"""FIRE roadmap sub-skill -- build prioritized, effort--impact action plans."""
from __future__ import annotations

from typing import List, Optional

from .constants import (
    FRAMEWORKS,
    GLIDE_PATH,
    SAFE_WITHDRAWAL_RATE,
    SCORE_WEIGHTS,
)
from .models import (
    AllocationScore,
    FinancialProfile,
    Priority,
    RoadmapItem,
    RiskScreenResult,
    SimulationResult,
)
from .utils import configure_logging, get_logger, interpolate_glide_equity

configure_logging()
logger = get_logger("fire_planner.roadmap")


class FIRERoadmapBuilder:
    """Produce a prioritized savings/allocation/withdrawal action plan."""

    def __init__(
        self,
        profile: FinancialProfile,
        simulation: SimulationResult,
        allocation_score: AllocationScore,
        risk_screen: RiskScreenResult,
    ):
        self.profile = profile
        self.simulation = simulation
        self.allocation_score = allocation_score
        self.risk_screen = risk_screen

    def build(self) -> List[RoadmapItem]:
        """Build and sort roadmap by impact -- effort."""
        items: List[RoadmapItem] = []
        items.extend(self._savings_actions())
        items.extend(self._allocation_actions())
        items.extend(self._withdrawal_actions())
        items.extend(self._risk_mitigation_actions())
        items.extend(self._tax_actions())

        # Sort by priority class then impact/effort ratio descending
        priority_order = {
            Priority.CRITICAL: 0,
            Priority.HIGH: 1,
            Priority.MEDIUM: 2,
            Priority.LOW: 3,
        }
        items.sort(key=lambda x: (priority_order[x.priority], -x.impact_x_effort()))
        logger.info("Roadmap built with %d items", len(items))
        return items

    def _savings_actions(self) -> List[RoadmapItem]:
        items: List[RoadmapItem] = []
        sr = self.profile.savings_rate()
        target_multiple = 1.0 / SAFE_WITHDRAWAL_RATE
        current_multiple = self.profile.portfolio_multiple_of_expenses()
        gap = target_multiple * self.profile.annual_expenses - self.profile.current_portfolio
        years_to_retire = self.profile.years_to_retirement()

        if current_multiple < target_multiple and years_to_retire > 0:
            required_savings = max(0.0, gap / years_to_retire)
            savings_gap = required_savings - self.profile.annual_savings

            if savings_gap > 1000:
                items.append(
                    RoadmapItem(
                        title="Raise annual savings to close FIRE funding gap",
                        description=(
                            f"Current savings ${self.profile.annual_savings:,.0f}/yr likely insufficient. "
                            f"Target ?${required_savings:,.0f}/yr to reach {target_multiple:.0f}x expenses by retirement."
                        ),
                        impact=5,
                        effort=3,
                        priority=Priority.CRITICAL if current_multiple < 15 else Priority.HIGH,
                        rationale="Savings rate is the dominant lever for early retirement success.",
                        evidence=FRAMEWORKS["trinity_study"]["source"],
                        milestone=f"Reach {target_multiple:.0f}x annual expenses by age {self.profile.retirement_age}",
                        savings_delta=savings_gap,
                    )
                )
            else:
                items.append(
                    RoadmapItem(
                        title="Maintain current savings trajectory",
                        description=(
                            f"Savings trajectory is on track to reach approximately {current_multiple:.1f}x expenses. "
                            f"Continue saving ${self.profile.annual_savings:,.0f}/yr."
                        ),
                        impact=3,
                        effort=1,
                        priority=Priority.MEDIUM,
                        rationale="Steady savings supports compounding and reduces sequence risk.",
                        evidence=FRAMEWORKS["bogleheads"]["source"],
                    )
                )

        if sr < 0.30 and self.profile.annual_gross_income > 0:
            items.append(
                RoadmapItem(
                    title="Increase gross savings rate to at least 30%",
                    description=(
                        f"Current savings rate is {sr:.0%}. For early retirement, target ?30% "
                        "of gross income."
                    ),
                    impact=5,
                    effort=3,
                    priority=Priority.HIGH,
                    rationale="Higher savings rate shortens time to financial independence.",
                    evidence=FRAMEWORKS["bogleheads"]["source"],
                    savings_delta=self.profile.annual_gross_income * max(0.0, 0.30 - sr),
                )
            )
        return items

    def _allocation_actions(self) -> List[RoadmapItem]:
        items: List[RoadmapItem] = []
        a = self.profile.allocation
        score = self.allocation_score

        target_equity = interpolate_glide_equity(self.profile.current_age, GLIDE_PATH)
        equity_gap = target_equity - a.equities
        if abs(equity_gap) >= 0.10:
            direction = "increase" if equity_gap > 0 else "decrease"
            items.append(
                RoadmapItem(
                    title=f"{direction.capitalize()} equity allocation toward age-based glide path",
                    description=(
                        f"Current equity {a.equities:.0%} vs target {target_equity:.0%}. "
                        f"Rebalance {direction} by at least {abs(equity_gap):.0%}."
                    ),
                    impact=4,
                    effort=2,
                    priority=Priority.HIGH,
                    rationale="Age-appropriate equity exposure balances growth and sequence risk.",
                    evidence=FRAMEWORKS["mpt"]["source"],
                )
            )

        crypto = a.crypto or 0.0
        if crypto > 0.10:
            items.append(
                RoadmapItem(
                    title="Reduce crypto/speculative allocation to ?5%",
                    description=(
                        f"Crypto is {crypto:.0%} of the portfolio. Trim to ?5% and redirect "
                        "to broad-market index funds."
                    ),
                    impact=5,
                    effort=2,
                    priority=Priority.CRITICAL,
                    rationale="High crypto concentration is incompatible with sustainable withdrawal planning.",
                    evidence=FRAMEWORKS["mpt"]["source"],
                )
            )

        if a.bonds + a.cash < 0.10:
            items.append(
                RoadmapItem(
                    title="Add bonds/cash ballast to reduce sequence-of-returns risk",
                    description=(
                        "Fixed income is below 10%. Increase high-quality bonds or cash to "
                        "provide portfolio ballast near retirement."
                    ),
                    impact=4,
                    effort=2,
                    priority=Priority.HIGH,
                    rationale="Bonds/cash dampen sequence-of-returns risk in the first decade of retirement.",
                    evidence=FRAMEWORKS["monte_carlo"]["source"],
                )
            )

        if score.fee_drag_score < 70:
            items.append(
                RoadmapItem(
                    title="Lower investment fees to under 0.15% annually",
                    description=(
                        f"Current fee rate {self.profile.fee_rate:.2%} erodes compounding. "
                        "Switch to low-cost index funds or ETFs."
                    ),
                    impact=4,
                    effort=1,
                    priority=Priority.HIGH,
                    rationale="Fee drag is a deterministic headwind; Bogleheads research emphasizes minimizing it.",
                    evidence=FRAMEWORKS["bogleheads"]["source"],
                )
            )
        return items

    def _withdrawal_actions(self) -> List[RoadmapItem]:
        items: List[RoadmapItem] = []
        wr = self.simulation.withdrawal_rate_used

        if wr > SAFE_WITHDRAWAL_RATE:
            items.append(
                RoadmapItem(
                    title="Reduce initial withdrawal rate to ?4%",
                    description=(
                        f"Current effective withdrawal rate {wr:.1%} exceeds the Trinity/Bengen 4% benchmark. "
                        "Lower it or build a larger portfolio before retiring."
                    ),
                    impact=5,
                    effort=2,
                    priority=Priority.CRITICAL,
                    rationale="A lower withdrawal rate materially increases plan survival probability.",
                    evidence=FRAMEWORKS["trinity_study"]["source"],
                )
            )
        else:
            items.append(
                RoadmapItem(
                    title="Adopt Guyton-Klinger dynamic guardrails at retirement",
                    description=(
                        f"Withdrawal rate {wr:.1%} is at or below 4%. Add guardrails to raise/lower "
                        "spending when portfolio moves +/-20% in real terms."
                    ),
                    impact=4,
                    effort=2,
                    priority=Priority.HIGH,
                    rationale="Dynamic withdrawals materially improve survival vs fixed real withdrawals.",
                    evidence=FRAMEWORKS["guyton_klinger"]["source"],
                )
            )

        if self.simulation.ruin_probability > 0.10:
            items.append(
                RoadmapItem(
                    title="Build a flexible spending floor-and-ceiling plan",
                    description=(
                        f"Ruin probability is {self.simulation.ruin_probability:.0%}. Define discretionary "
                        "spending cuts (e.g., travel, dining) to activate in down markets."
                    ),
                    impact=5,
                    effort=2,
                    priority=Priority.CRITICAL,
                    rationale="Variable spending is one of the most effective levers to reduce ruin risk.",
                    evidence=FRAMEWORKS["guyton_klinger"]["source"],
                )
            )
        return items

    def _risk_mitigation_actions(self) -> List[RoadmapItem]:
        items: List[RoadmapItem] = []
        if self.risk_screen.warned() or self.risk_screen.halted():
            for warning in self.risk_screen.warnings[:3]:
                items.append(
                    RoadmapItem(
                        title=f"Address risk-screen warning: {warning[:60]}",
                        description=warning,
                        impact=4,
                        effort=2,
                        priority=Priority.HIGH,
                        rationale="Risk-screen warnings identify the most immediate threats to plan success.",
                        evidence="RiskSuitabilityScreener output",
                    )
                )
        return items

    def _tax_actions(self) -> List[RoadmapItem]:
        items: List[RoadmapItem] = []
        tax = self.profile.tax_status
        if tax is None:
            items.append(
                RoadmapItem(
                    title="Document account tax placement and marginal tax rate",
                    description=(
                        "Tax status is not provided. Map taxable, tax-deferred and tax-free buckets "
                        "to optimize withdrawal sequencing."
                    ),
                    impact=3,
                    effort=2,
                    priority=Priority.MEDIUM,
                    rationale="Tax-aware withdrawal sequencing can materially increase after-tax retirement income.",
                    evidence="Assumption: tax optimization best practice",
                )
            )
        return items
