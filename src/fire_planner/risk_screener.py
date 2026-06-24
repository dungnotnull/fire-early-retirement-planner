"""Risk-suitability screener sub-skill -- gate before Monte Carlo analysis."""
from __future__ import annotations

from typing import Dict, List

from .constants import MIN_EMERGENCY_FUND_MONTHS, SAFE_WITHDRAWAL_RATE
from .models import AssetAllocation, FinancialProfile, GateVerdict, RiskScreenResult
from .utils import configure_logging, get_logger

configure_logging()
logger = get_logger("fire_planner.risk_screener")


class RiskSuitabilityScreener:
    """Screen a financial profile for suitability and compliance red flags."""

    HALT_CRYPTO_RATIO: float = 0.75
    WARN_CRYPTO_RATIO: float = 0.20
    HALT_WITHDRAWAL_RATE: float = 0.08
    WARN_WITHDRAWAL_RATE: float = 0.06
    HALT_FEES: float = 0.03
    WARN_FEES: float = 0.015
    WARN_EXPENSE_TO_INCOME: float = 0.90
    HALT_EXPENSE_TO_INCOME: float = 1.05

    @classmethod
    def screen(cls, profile: FinancialProfile) -> RiskScreenResult:
        """Run the full gate and return a verdict plus flags/warnings."""
        flags: List[str] = []
        warnings: List[str] = []
        suggestions: List[str] = []

        cls._check_retirement_feasibility(profile, flags, warnings, suggestions)
        cls._check_concentration(profile.allocation, flags, warnings, suggestions)
        cls._check_withdrawal_rate(profile, flags, warnings, suggestions)
        cls._check_fees(profile.fee_rate, flags, warnings, suggestions)
        cls._check_emergency_fund(profile, flags, warnings, suggestions)
        cls._check_cash_flow(profile, flags, warnings, suggestions)
        cls._check_age_risk_consistency(profile, flags, warnings, suggestions)

        if flags:
            verdict = GateVerdict.HALT
        elif warnings:
            verdict = GateVerdict.WARNING
        else:
            verdict = GateVerdict.PASS

        result = RiskScreenResult(
            verdict=verdict,
            flags=flags,
            warnings=warnings,
            suggestions=suggestions,
        )
        logger.info("Risk screen verdict=%s flags=%d warnings=%d", verdict.value, len(flags), len(warnings))
        return result

    @classmethod
    def _check_retirement_feasibility(
        cls,
        profile: FinancialProfile,
        flags: List[str],
        warnings: List[str],
        suggestions: List[str],
    ) -> None:
        multiple = profile.portfolio_multiple_of_expenses()
        target_multiple = 1.0 / SAFE_WITHDRAWAL_RATE  # 25x
        if multiple < 10:
            flags.append(
                f"Portfolio is only {multiple:.1f}x annual expenses, far below the "
                f"{target_multiple:.0f}x implied by a {SAFE_WITHDRAWAL_RATE:.0%} withdrawal rate. "
                "Plan is not viable without substantial increases in savings, income, or return assumptions."
            )
        elif multiple < target_multiple * 0.8:
            warnings.append(
                f"Portfolio is {multiple:.1f}x annual expenses, below the {target_multiple:.0f}x target. "
                "Higher savings rate or longer working horizon may be needed."
            )
            suggestions.append(
                "Increase savings rate or delay retirement to close the funding gap."
            )
        else:
            suggestions.append(
                f"Portfolio multiple ({multiple:.1f}x) meets or exceeds the {target_multiple:.0f}x target."
            )

    @classmethod
    def _check_concentration(
        cls,
        allocation: AssetAllocation,
        flags: List[str],
        warnings: List[str],
        suggestions: List[str],
    ) -> None:
        crypto = allocation.crypto or 0.0
        alternatives = allocation.alternatives
        if crypto >= cls.HALT_CRYPTO_RATIO:
            flags.append(
                f"Crypto allocation is {crypto:.0%}. This concentration is incompatible with "
                "sustainable-withdrawal planning and is treated as a halt condition."
            )
        elif crypto >= cls.WARN_CRYPTO_RATIO:
            warnings.append(
                f"Crypto allocation is {crypto:.0%}, materially above the 5% "
                "ceiling suggested by prudent portfolio construction."
            )
            suggestions.append(
                "Reduce crypto exposure to ?5% and rebalance into broad-market index funds."
            )

        if allocation.equities > 0.95 and allocation.bonds + allocation.cash < 0.05:
            warnings.append(
                "Equity allocation exceeds 95% with minimal bonds/cash. Sequence-of-returns risk is elevated."
            )
            suggestions.append(
                "Add high-quality bonds or cash to dampen sequence-of-returns risk near retirement."
            )

        max_single = max(
            allocation.equities, allocation.bonds, allocation.cash, allocation.alternatives
        )
        if max_single >= 0.90:
            warnings.append(
                f"Portfolio is highly concentrated: one asset class represents {max_single:.0%}."
            )
            suggestions.append("Diversify across equities, bonds and cash per Modern Portfolio Theory.")

    @classmethod
    def _check_withdrawal_rate(
        cls,
        profile: FinancialProfile,
        flags: List[str],
        warnings: List[str],
        suggestions: List[str],
    ) -> None:
        wr = profile.target_withdrawal_rate
        if wr is None:
            return
        if wr >= cls.HALT_WITHDRAWAL_RATE:
            flags.append(
                f"Target withdrawal rate {wr:.1%} is double the 4% Trinity/Bengen benchmark "
                "and is treated as unsustainable."
            )
        elif wr >= cls.WARN_WITHDRAWAL_RATE:
            warnings.append(
                f"Target withdrawal rate {wr:.1%} exceeds the 4% safe-withdrawal benchmark. "
                "Dynamic guardrails (Guyton-Klinger) are strongly recommended."
            )
            suggestions.append(
                "Adopt Guyton-Klinger guardrails or reduce the withdrawal target to ?4%."
            )

    @classmethod
    def _check_fees(
        cls,
        fee_rate: float,
        flags: List[str],
        warnings: List[str],
        suggestions: List[str],
    ) -> None:
        if fee_rate >= cls.HALT_FEES:
            flags.append(
                f"Total fee rate {fee_rate:.2%} is extremely high and will materially erode "
                "long-term wealth accumulation."
            )
        elif fee_rate >= cls.WARN_FEES:
            warnings.append(
                f"Total fee rate {fee_rate:.2%} is high. Bogleheads research shows fee drag "
                "significantly reduces terminal wealth."
            )
            suggestions.append(
                "Switch to low-cost broad-market index funds (target expense ratio <0.15%)."
            )

    @classmethod
    def _check_emergency_fund(
        cls,
        profile: FinancialProfile,
        flags: List[str],
        warnings: List[str],
        suggestions: List[str],
    ) -> None:
        months = profile.emergency_fund_months
        if months is None:
            warnings.append(
                "Emergency fund size not disclosed; assuming less than 3 months."
            )
            suggestions.append(
                f"Maintain at least {MIN_EMERGENCY_FUND_MONTHS} months of expenses in liquid savings."
            )
        elif months < MIN_EMERGENCY_FUND_MONTHS:
            warnings.append(
                f"Emergency fund covers only {months:.1f} months, below the {MIN_EMERGENCY_FUND_MONTHS}-month minimum."
            )
            suggestions.append(
                "Build liquid emergency reserves before increasing retirement contributions."
            )

    @classmethod
    def _check_cash_flow(
        cls,
        profile: FinancialProfile,
        flags: List[str],
        warnings: List[str],
        suggestions: List[str],
    ) -> None:
        if profile.annual_gross_income <= 0:
            return
        ratio = profile.annual_expenses / profile.annual_gross_income
        if ratio >= cls.HALT_EXPENSE_TO_INCOME:
            flags.append(
                f"Annual expenses ({ratio:.0%} of gross income) exceed income. "
                "No capacity to save; plan is not viable without income increase or expense reduction."
            )
        elif ratio >= cls.WARN_EXPENSE_TO_INCOME:
            warnings.append(
                f"Annual expenses consume {ratio:.0%} of gross income, leaving limited room for savings."
            )
            suggestions.append(
                "Reduce discretionary spending or increase income to improve the savings rate."
            )

    @classmethod
    def _check_age_risk_consistency(
        cls,
        profile: FinancialProfile,
        flags: List[str],
        warnings: List[str],
        suggestions: List[str],
    ) -> None:
        horizon = profile.years_to_retirement()
        if horizon < 5 and profile.allocation.equities > 0.80:
            warnings.append(
                f"Retirement is only {horizon} years away, but equity allocation is {profile.allocation.equities:.0%}. "
                "High equity exposure close to retirement increases sequence risk."
            )
            suggestions.append(
                "Begin a glide-path shift toward a more conservative allocation."
            )
        if profile.life_expectancy - profile.current_age > 60 and profile.allocation.equities < 0.40:
            warnings.append(
                "Long retirement horizon with low equity allocation may not generate sufficient growth."
            )
            suggestions.append(
                "Consider a higher equity allocation given the extended time horizon, within risk tolerance."
            )
