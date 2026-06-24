"""Monte Carlo simulation sub-skill -- sequence-of-returns risk engine."""
from __future__ import annotations

import math
import random
from typing import Dict, List, Optional

import numpy as np

from .constants import DEFAULT_MARKET_ASSUMPTIONS, DEFAULT_NUM_SIMULATIONS, DEFAULT_SEED
from .models import AssetAllocation, FinancialProfile, MarketAssumptions, SinglePathResult, SimulationResult, SimulationStatus
from .utils import configure_logging, get_logger, percentile

configure_logging()
logger = get_logger("fire_planner.monte_carlo")


class MonteCarloEngine:
    """Run stochastic lifetime portfolio simulations."""

    def __init__(
        self,
        assumptions: Optional[MarketAssumptions] = None,
        num_simulations: int = DEFAULT_NUM_SIMULATIONS,
        use_guyton_klinger: bool = False,
    ):
        self.assumptions = assumptions or MarketAssumptions(**DEFAULT_MARKET_ASSUMPTIONS)
        self.num_simulations = self._validate_sim_count(num_simulations)
        self.use_guyton_klinger = use_guyton_klinger
        self._rng = random.Random(self.assumptions.seed or DEFAULT_SEED)

    @staticmethod
    def _validate_sim_count(n: int) -> int:
        if not isinstance(n, int) or n < 100:
            raise ValueError("num_simulations must be an integer >= 100")
        return n

    def run(self, profile: FinancialProfile) -> SimulationResult:
        """Run the full simulation and return aggregate results."""
        logger.info(
            "Running Monte Carlo: age %d -> %d, %d simulations",
            profile.current_age,
            profile.life_expectancy,
            self.num_simulations,
        )

        annual_withdrawal = self._initial_annual_withdrawal(profile)
        paths: List[SinglePathResult] = []
        for _ in range(self.num_simulations):
            path = self._simulate_path(profile, annual_withdrawal)
            paths.append(path)

        return self._aggregate(paths, profile, annual_withdrawal)

    def _initial_annual_withdrawal(self, profile: FinancialProfile) -> float:
        """Compute the first-year retirement withdrawal amount."""
        net_expenses = max(0.0, profile.annual_expenses - profile.social_security_annual - profile.pension_income)
        if profile.target_withdrawal_rate is not None:
            return profile.target_withdrawal_rate * profile.current_portfolio
        # Otherwise use current expenses (naive 4% check scenario)
        return net_expenses

    def _simulate_path(
        self,
        profile: FinancialProfile,
        annual_withdrawal: float,
    ) -> SinglePathResult:
        """Simulate a single lifetime portfolio path."""
        portfolio = profile.current_portfolio
        current_age = profile.current_age
        retirement_age = profile.retirement_age
        life_expectancy = profile.life_expectancy

        portfolio_values: List[float] = []
        withdrawals: List[float] = []
        inflation_series: List[float] = []
        real_annual_withdrawal = annual_withdrawal

        while current_age < life_expectancy and portfolio >= 0:
            # Annual inflation draw
            inflation = self._draw_inflation()
            inflation_series.append(inflation)

            if current_age < retirement_age:
                # Accumulation phase
                contribution = profile.annual_savings
                portfolio = portfolio * (1.0 + self._draw_return(profile.allocation, inflation))
                portfolio = portfolio * (1.0 - profile.fee_rate)
                portfolio += contribution
                withdrawals.append(0.0)
            else:
                # Retirement phase
                portfolio = portfolio * (1.0 + self._draw_return(profile.allocation, inflation))
                portfolio = portfolio * (1.0 - profile.fee_rate)

                # Adjust withdrawal for inflation
                real_annual_withdrawal *= (1.0 + inflation)

                # Guyton-Klinger guardrails: cut/raise withdrawal if portfolio changes materially
                if self.use_guyton_klinger and portfolio > 0:
                    real_annual_withdrawal = self._apply_guardrails(
                        portfolio, real_annual_withdrawal, annual_withdrawal
                    )

                withdrawal = min(real_annual_withdrawal, portfolio)
                portfolio -= withdrawal
                withdrawals.append(withdrawal)

                if portfolio <= 0:
                    depleted_age = current_age
                    break

            portfolio_values.append(portfolio)
            current_age += 1
        else:
            depleted_age = None

        if portfolio <= 0:
            status = SimulationStatus.DEPLETED
        elif current_age >= life_expectancy:
            status = SimulationStatus.SUCCESS
        else:
            status = SimulationStatus.INSUFFICIENT_AT_RETIREMENT

        return SinglePathResult(
            portfolio_values=portfolio_values,
            withdrawals=withdrawals,
            inflation_series=inflation_series,
            depleted=portfolio <= 0,
            depleted_age=depleted_age,
            final_balance=portfolio,
            reason=status,
        )

    def _draw_inflation(self) -> float:
        """Draw a random annual inflation rate."""
        if self.assumptions.inflation_regime_shock is not None:
            # Fixed regime shock: mean shifted but still stochastic around it
            mean = self.assumptions.inflation_regime_shock
            sigma = self.assumptions.inflation_volatility
            return max(-0.02, np.random.normal(mean, sigma))
        mean = self.assumptions.inflation_mean
        sigma = self.assumptions.inflation_volatility
        return max(-0.02, np.random.normal(mean, sigma))

    def _draw_return(self, allocation: AssetAllocation, inflation: float) -> float:
        """Draw a single annual portfolio return from correlated normals."""
        # Nominal mean return for this allocation
        mean = self.assumptions.blended_return(allocation)
        sigma = self.assumptions.blended_volatility(allocation)

        # Real vs nominal: our simulation applies nominal returns and separately
        # inflates withdrawals. We approximate by keeping nominal return draw.
        raw_return = np.random.normal(mean, sigma)

        # Floor to prevent absurd single-year crashes breaking all paths
        return max(-0.50, raw_return)

    def _apply_guardrails(
        self,
        portfolio: float,
        current_withdrawal: float,
        initial_withdrawal: float,
    ) -> float:
        """Apply Guyton-Klinger guardrails to adjust spending."""
        # Guardrails at +/-20% of initial withdrawal in real terms
        upper = initial_withdrawal * 1.20
        lower = initial_withdrawal * 0.80
        if current_withdrawal > upper:
            return upper
        if current_withdrawal < lower:
            return lower
        return current_withdrawal

    def _aggregate(
        self,
        paths: List[SinglePathResult],
        profile: FinancialProfile,
        annual_withdrawal: float,
    ) -> SimulationResult:
        """Aggregate path results into summary statistics."""
        success_count = sum(1 for p in paths if not p.depleted)
        depleted_count = len(paths) - success_count

        success_probability = success_count / len(paths)
        ruin_probability = depleted_count / len(paths)

        final_balances = [p.final_balance for p in paths]
        median_final = percentile(final_balances, 50)
        mean_final = sum(final_balances) / len(final_balances)

        depleted_ages = [
            p.depleted_age for p in paths if p.depleted and p.depleted_age is not None
        ]
        median_depletion_age = (
            percentile(depleted_ages, 50) if depleted_ages else None
        )

        portfolio_multiple = (
            profile.current_portfolio / profile.annual_expenses
            if profile.annual_expenses > 0 else 0.0
        )
        withdrawal_rate_used = (
            annual_withdrawal / profile.current_portfolio
            if profile.current_portfolio > 0 else 0.0
        )

        assumptions = {
            "equities_mean_return": self.assumptions.equities_mean_return,
            "equities_volatility": self.assumptions.equities_volatility,
            "bonds_mean_return": self.assumptions.bonds_mean_return,
            "bonds_volatility": self.assumptions.bonds_volatility,
            "cash_mean_return": self.assumptions.cash_mean_return,
            "inflation_mean": self.assumptions.inflation_mean,
            "inflation_volatility": self.assumptions.inflation_volatility,
            "num_simulations": float(self.num_simulations),
            "portfolio_multiple_of_expenses": portfolio_multiple,
        }

        return SimulationResult(
            success_probability=success_probability,
            median_final_balance=median_final,
            mean_final_balance=mean_final,
            percentile_05=percentile(final_balances, 5),
            percentile_25=percentile(final_balances, 25),
            percentile_75=percentile(final_balances, 75),
            percentile_95=percentile(final_balances, 95),
            ruin_probability=ruin_probability,
            median_depletion_age=median_depletion_age,
            paths=paths,
            withdrawal_rate_used=withdrawal_rate_used,
            annual_withdrawal=annual_withdrawal,
            assumptions=assumptions,
            num_simulations=self.num_simulations,
        )

    @classmethod
    def sensitivity_analysis(
        cls,
        profile: FinancialProfile,
        assumptions: Optional[MarketAssumptions] = None,
        num_simulations: int = 2_000,
    ) -> List[Dict[str, float]]:
        """Run simulations across inflation and return regimes for sensitivity."""
        scenarios = [
            {"name": "base", "inflation_shock": None, "equity_premium": 0.0},
            {"name": "high_inflation", "inflation_shock": 0.06, "equity_premium": 0.0},
            {"name": "low_return", "inflation_shock": None, "equity_premium": -0.015},
            {"name": "stagflation", "inflation_shock": 0.06, "equity_premium": -0.015},
        ]
        results: List[Dict[str, float]] = []
        base = assumptions or MarketAssumptions(**DEFAULT_MARKET_ASSUMPTIONS)

        for scenario in scenarios:
            sa = MarketAssumptions(
                equities_mean_return=base.equities_mean_return + scenario["equity_premium"],
                equities_volatility=base.equities_volatility,
                bonds_mean_return=base.bonds_mean_return,
                bonds_volatility=base.bonds_volatility,
                cash_mean_return=base.cash_mean_return,
                cash_volatility=base.cash_volatility,
                alternatives_mean_return=base.alternatives_mean_return,
                alternatives_volatility=base.alternatives_volatility,
                correlation_equities_bonds=base.correlation_equities_bonds,
                inflation_mean=base.inflation_mean,
                inflation_volatility=base.inflation_volatility,
                inflation_regime_shock=scenario["inflation_shock"],
            )
            engine = cls(assumptions=sa, num_simulations=num_simulations)
            res = engine.run(profile)
            results.append(
                {
                    "scenario": scenario["name"],
                    "success_probability": round(res.success_probability, 4),
                    "ruin_probability": round(res.ruin_probability, 4),
                    "median_final_balance": round(res.median_final_balance, 2),
                    "withdrawal_rate_used": round(res.withdrawal_rate_used, 4),
                }
            )
        return results

