"""Typed domain models for the FIRE early-retirement planner."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple


class RiskTolerance(Enum):
    """Investor risk-tolerance buckets used to tune allocations and guardrails."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class SimulationStatus(Enum):
    """Terminal status of a single Monte Carlo path."""

    SUCCESS = "success"
    DEPLETED = "depleted"
    INSUFFICIENT_AT_RETIREMENT = "insufficient_at_retirement"


class GateVerdict(Enum):
    """Verdict returned by compliance / suitability gates."""

    PASS = "pass"
    WARNING = "warning"
    HALT = "halt"


class Priority(Enum):
    """Priority buckets for roadmap actions."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class AssetAllocation:
    """Portfolio allocation expressed as fractions summing to 1.0."""

    equities: float = 0.0
    bonds: float = 0.0
    cash: float = 0.0
    alternatives: float = 0.0
    # Optional breakdowns for deeper scoring
    us_equities: Optional[float] = None
    international_equities: Optional[float] = None
    crypto: Optional[float] = None
    real_estate: Optional[float] = None

    def __post_init__(self) -> None:
        total = round(
            self.equities + self.bonds + self.cash + self.alternatives, 6
        )
        if total < 0.0 or total > 1.0:
            raise ValueError(
                f"Allocation fractions must be between 0 and 1; got {total}"
            )

    def total(self) -> float:
        return self.equities + self.bonds + self.cash + self.alternatives

    def has_shortfall(self) -> bool:
        return self.total() < 0.999999


@dataclass(frozen=True)
class TaxStatus:
    """Tax characteristics of the portfolio / accounts."""

    tax_deferred_ratio: float = 0.0
    taxable_ratio: float = 0.0
    tax_free_ratio: float = 0.0
    marginal_tax_rate: float = 0.0
    effective_tax_rate: float = 0.0


@dataclass(frozen=True)
class FinancialProfile:
    """Complete financial snapshot used by the planner."""

    current_age: int
    retirement_age: int
    life_expectancy: int
    current_portfolio: float
    annual_gross_income: float
    annual_expenses: float
    annual_savings: float
    allocation: AssetAllocation
    risk_tolerance: RiskTolerance
    # Optional fields allow progressive disclosure during intake
    target_withdrawal_rate: Optional[float] = None
    monthly_expenses: Optional[float] = None
    emergency_fund_months: Optional[float] = None
    desired_legacy: Optional[float] = None
    pension_income: float = 0.0
    social_security_annual: float = 0.0
    fee_rate: float = 0.001
    inflation_assumption: Optional[float] = None
    expected_return_override: Optional[float] = None
    tax_status: Optional[TaxStatus] = None
    notes: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.retirement_age < self.current_age:
            raise ValueError("retirement_age must be greater than or equal to current_age")
        if self.life_expectancy <= self.retirement_age:
            raise ValueError("life_expectancy must be greater than retirement_age")
        if self.annual_expenses <= 0:
            raise ValueError("annual_expenses must be positive")
        if self.current_portfolio < 0:
            raise ValueError("current_portfolio cannot be negative")
        if self.fee_rate < 0 or self.fee_rate > 0.5:
            raise ValueError("fee_rate must be between 0 and 0.5")

    def years_to_retirement(self) -> int:
        return self.retirement_age - self.current_age

    def years_in_retirement(self) -> int:
        return self.life_expectancy - self.retirement_age

    def savings_rate(self) -> float:
        """Gross savings rate relative to gross income."""
        if self.annual_gross_income <= 0:
            return 0.0
        return self.annual_savings / self.annual_gross_income

    def portfolio_multiple_of_expenses(self) -> float:
        if self.annual_expenses == 0:
            return float("inf")
        return self.current_portfolio / self.annual_expenses


@dataclass(frozen=True)
class MarketAssumptions:
    """Stochastic assumptions for Monte Carlo simulation."""

    equities_mean_return: float = 0.07
    equities_volatility: float = 0.16
    bonds_mean_return: float = 0.035
    bonds_volatility: float = 0.05
    cash_mean_return: float = 0.02
    cash_volatility: float = 0.01
    alternatives_mean_return: float = 0.05
    alternatives_volatility: float = 0.25
    correlation_equities_bonds: float = 0.0
    inflation_mean: float = 0.025
    inflation_volatility: float = 0.01
    inflation_regime_shock: Optional[float] = None  # e.g. 0.06 fixed inflation
    sequence_risk_model: str = "lognormal"
    seed: Optional[int] = None

    def blended_return(self, allocation: AssetAllocation) -> float:
        return (
            allocation.equities * self.equities_mean_return
            + allocation.bonds * self.bonds_mean_return
            + allocation.cash * self.cash_mean_return
            + allocation.alternatives * self.alternatives_mean_return
        )

    def blended_volatility(self, allocation: AssetAllocation) -> float:
        eq_w = allocation.equities
        b_w = allocation.bonds
        c_w = allocation.cash
        alt_w = allocation.alternatives
        var = (
            (eq_w * self.equities_volatility) ** 2
            + (b_w * self.bonds_volatility) ** 2
            + (c_w * self.cash_volatility) ** 2
            + (alt_w * self.alternatives_volatility) ** 2
            + 2
            * eq_w
            * b_w
            * self.equities_volatility
            * self.bonds_volatility
            * self.correlation_equities_bonds
        )
        return var ** 0.5


@dataclass
class SinglePathResult:
    """Outcome of one simulated lifetime."""

    portfolio_values: List[float]
    withdrawals: List[float]
    inflation_series: List[float]
    depleted: bool
    depleted_age: Optional[int]
    final_balance: float
    reason: SimulationStatus


@dataclass
class SimulationResult:
    """Aggregate Monte Carlo results across all simulated paths."""

    success_probability: float
    median_final_balance: float
    mean_final_balance: float
    percentile_05: float
    percentile_25: float
    percentile_75: float
    percentile_95: float
    ruin_probability: float
    median_depletion_age: Optional[float]
    paths: List[SinglePathResult]
    withdrawal_rate_used: float
    annual_withdrawal: float
    assumptions: Dict[str, float]
    num_simulations: int


@dataclass
class RiskScreenResult:
    """Output of the suitability / compliance gate."""

    verdict: GateVerdict
    flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def halted(self) -> bool:
        return self.verdict == GateVerdict.HALT

    def warned(self) -> bool:
        return self.verdict == GateVerdict.WARNING


@dataclass
class DimensionScore:
    """Score for a single scoring dimension (0-100)."""

    name: str
    score: float
    weight: float
    rationale: str
    evidence: str
    assumption: Optional[str] = None


@dataclass
class AllocationScore:
    """Multi-dimensional allocation scoring output."""

    diversification_score: float
    fee_drag_score: float
    glide_path_score: float
    tax_efficiency_score: float
    overall_score: float
    rationale: str
    evidence: str
    dimensions: List[DimensionScore] = field(default_factory=list)


@dataclass
class RoadmapItem:
    """Actionable improvement item ranked by effort -- impact."""

    title: str
    description: str
    impact: int  # 1-5
    effort: int  # 1-5
    priority: Priority
    rationale: str
    evidence: str
    milestone: Optional[str] = None
    savings_delta: Optional[float] = None
    success_delta: Optional[float] = None

    def impact_x_effort(self) -> float:
        if self.effort == 0:
            return float("inf")
        return self.impact / self.effort


@dataclass
class FinalReport:
    """Top-level deliverable emitted by the harness."""

    composite_score: float
    confidence_level: str
    dimension_scores: List[DimensionScore]
    simulation_result: SimulationResult
    allocation_score: AllocationScore
    risk_screen: RiskScreenResult
    roadmap: List[RoadmapItem]
    findings: Dict[str, List[str]]
    sources: List[Tuple[str, str]]
    assumptions: List[str]
    disclaimer: str

    def to_dict(self) -> Dict:
        return {
            "composite_score": round(self.composite_score, 2),
            "confidence_level": self.confidence_level,
            "dimension_scores": [
                {
                    "name": d.name,
                    "score": round(d.score, 2),
                    "weight": round(d.weight, 2),
                    "rationale": d.rationale,
                    "evidence": d.evidence,
                    "assumption": d.assumption,
                }
                for d in self.dimension_scores
            ],
            "simulation": {
                "success_probability": round(self.simulation_result.success_probability, 4),
                "ruin_probability": round(self.simulation_result.ruin_probability, 4),
                "median_final_balance": round(self.simulation_result.median_final_balance, 2),
                "withdrawal_rate_used": round(self.simulation_result.withdrawal_rate_used, 4),
                "annual_withdrawal": round(self.simulation_result.annual_withdrawal, 2),
                "num_simulations": self.simulation_result.num_simulations,
            },
            "allocation_score": {
                "overall": round(self.allocation_score.overall_score, 2),
                "diversification": round(self.allocation_score.diversification_score, 2),
                "fee_drag": round(self.allocation_score.fee_drag_score, 2),
                "glide_path": round(self.allocation_score.glide_path_score, 2),
                "tax_efficiency": round(self.allocation_score.tax_efficiency_score, 2),
            },
            "risk_screen": {
                "verdict": self.risk_screen.verdict.value,
                "flags": self.risk_screen.flags,
                "warnings": self.risk_screen.warnings,
                "suggestions": self.risk_screen.suggestions,
            },
            "roadmap": [
                {
                    "title": r.title,
                    "priority": r.priority.value,
                    "impact": r.impact,
                    "effort": r.effort,
                    "impact_x_effort": round(r.impact_x_effort(), 2),
                    "rationale": r.rationale,
                    "evidence": r.evidence,
                }
                for r in self.roadmap
            ],
            "findings": self.findings,
            "sources": self.sources,
            "assumptions": self.assumptions,
            "disclaimer": self.disclaimer,
        }

