"""Allocation-scoring sub-skill -- MPT, Bogleheads and glide-path scoring."""
from __future__ import annotations

from typing import List

from .constants import FRAMEWORKS, GLIDE_PATH
from .models import AllocationScore, AssetAllocation, DimensionScore, FinancialProfile
from .utils import clamp, configure_logging, get_logger, interpolate_glide_equity

configure_logging()
logger = get_logger("fire_planner.allocation_scorer")


class AllocationScorer:
    """Score a portfolio allocation against named frameworks."""

    # Fee drag thresholds from Bogleheads research
    EXCELLENT_FEE: float = 0.0005
    GOOD_FEE: float = 0.0015
    FAIR_FEE: float = 0.005

    def __init__(self, profile: FinancialProfile):
        self.profile = profile
        self.allocation = profile.allocation

    def score(self) -> AllocationScore:
        """Compute all allocation sub-scores and the overall score."""
        div_score, div_rationale, div_evidence = self._diversification()
        fee_score, fee_rationale, fee_evidence = self._fee_drag()
        glide_score, glide_rationale, glide_evidence = self._glide_path()
        tax_score, tax_rationale, tax_evidence = self._tax_efficiency()

        overall = round(
            0.35 * div_score + 0.25 * fee_score + 0.25 * glide_score + 0.15 * tax_score,
            2,
        )

        dimensions = [
            DimensionScore(
                name="diversification",
                score=div_score,
                weight=0.35,
                rationale=div_rationale,
                evidence=div_evidence,
            ),
            DimensionScore(
                name="fee_drag",
                score=fee_score,
                weight=0.25,
                rationale=fee_rationale,
                evidence=fee_evidence,
            ),
            DimensionScore(
                name="glide_path",
                score=glide_score,
                weight=0.25,
                rationale=glide_rationale,
                evidence=glide_evidence,
            ),
            DimensionScore(
                name="tax_efficiency",
                score=tax_score,
                weight=0.15,
                rationale=tax_rationale,
                evidence=tax_evidence,
            ),
        ]

        score = AllocationScore(
            diversification_score=div_score,
            fee_drag_score=fee_score,
            glide_path_score=glide_score,
            tax_efficiency_score=tax_score,
            overall_score=overall,
            rationale=self._summary_rationale(dimensions),
            evidence="Frameworks: Markowitz MPT, Bogleheads low-cost index philosophy.",
            dimensions=dimensions,
        )
        logger.info("Allocation overall_score=%s", overall)
        return score

    def _diversification(self) -> tuple:
        a = self.allocation
        score = 100.0
        rationale_parts: List[str] = []

        # Penalize missing bonds/cash (ballast)
        if a.bonds + a.cash < 0.10:
            score -= 20
            rationale_parts.append("Minimal bonds/cash reduces portfolio ballast.")
        elif a.bonds + a.cash > 0.50:
            score -= 10
            rationale_parts.append("Very high fixed-income allocation may stunt long-term growth.")

        # Penalize single asset-class dominance
        max_core = max(a.equities, a.bonds, a.cash, a.alternatives)
        if max_core >= 0.90:
            score -= 25
            rationale_parts.append("Portfolio dominated by a single asset class.")
        elif max_core >= 0.75:
            score -= 10
            rationale_parts.append("Portfolio is moderately concentrated.")

        # Crypto/speculative concentration
        crypto = a.crypto or 0.0
        if crypto > 0.20:
            score -= 30
            rationale_parts.append(f"Crypto allocation {crypto:.0%} is excessive for retirement capital.")
        elif crypto > 0.05:
            score -= 10
            rationale_parts.append(f"Crypto allocation {crypto:.0%} exceeds prudent 5% limit.")

        # Geographic diversification (when data provided)
        if a.us_equities is not None and a.international_equities is not None:
            total_equity = a.us_equities + a.international_equities
            if total_equity > 0 and (a.international_equities / total_equity) < 0.15:
                score -= 10
                rationale_parts.append("International equity diversification appears low.")

        if a.has_shortfall():
            score -= 5
            rationale_parts.append("Allocation does not sum to 100%; some assets are unspecified.")

        rationale = " ".join(rationale_parts) or "Allocation is well diversified across major asset classes."
        return clamp(score, 0, 100), rationale, FRAMEWORKS["mpt"]["source"]

    def _fee_drag(self) -> tuple:
        fee = self.profile.fee_rate
        if fee <= self.EXCELLENT_FEE:
            score = 95.0
            rationale = f"Fee rate {fee:.2%} is very low, minimizing drag."
        elif fee <= self.GOOD_FEE:
            score = 80.0
            rationale = f"Fee rate {fee:.2%} is reasonable for index-oriented portfolios."
        elif fee <= self.FAIR_FEE:
            score = 55.0
            rationale = f"Fee rate {fee:.2%} is moderate; fee drag will reduce terminal wealth."
        else:
            score = 25.0
            rationale = f"Fee rate {fee:.2%} is high and materially harmful to compounding."
        return score, rationale, FRAMEWORKS["bogleheads"]["source"]

    def _glide_path(self) -> tuple:
        a = self.allocation
        target_equity = interpolate_glide_equity(self.profile.current_age, GLIDE_PATH)
        deviation = abs(a.equities - target_equity)

        if deviation <= 0.05:
            score = 95.0
            rationale = (
                f"Equity allocation {a.equities:.0%} is within 5% of age-based target "
                f"{target_equity:.0%}."
            )
        elif deviation <= 0.15:
            score = 75.0
            rationale = (
                f"Equity allocation {a.equities:.0%} deviates moderately from age-based target "
                f"{target_equity:.0%}."
            )
        elif deviation <= 0.30:
            score = 50.0
            rationale = (
                f"Equity allocation {a.equities:.0%} deviates materially from age-based target "
                f"{target_equity:.0%}."
            )
        else:
            score = 25.0
            rationale = (
                f"Equity allocation {a.equities:.0%} is far from age-based target "
                f"{target_equity:.0%}; consider rebalancing toward the glide path."
            )
        return clamp(score, 0, 100), rationale, FRAMEWORKS["mpt"]["source"]

    def _tax_efficiency(self) -> tuple:
        tax = self.profile.tax_status
        if tax is None:
            return 70.0, "Tax status not provided; assuming average tax efficiency.", "Assumption"
        score = 80.0
        rationale_parts: List[str] = []
        if tax.tax_free_ratio > 0.3:
            score += 10
            rationale_parts.append("Substantial Roth/tax-free assets improve tax flexibility.")
        if tax.tax_deferred_ratio > 0.7 and tax.marginal_tax_rate > 0.25:
            score -= 10
            rationale_parts.append("Heavy tax-deferred exposure with high marginal rate creates future tax risk.")
        if tax.effective_tax_rate > 0.20:
            score -= 10
            rationale_parts.append("High effective tax rate reduces net retirement cash flow.")
        rationale = " ".join(rationale_parts) or "Tax placement is reasonably efficient."
        return clamp(score, 0, 100), rationale, "Assumption"

    @staticmethod
    def _summary_rationale(dimensions: List[DimensionScore]) -> str:
        weakest = min(dimensions, key=lambda d: d.score)
        return (
            f"Overall allocation score driven primarily by {weakest.name} "
            f"(score {weakest.score:.0f}/100). {weakest.rationale}"
        )
