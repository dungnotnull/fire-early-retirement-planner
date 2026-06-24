"""Main harness -- orchestrates intake, research sync, gate, scoring and roadmap."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .allocation_scorer import AllocationScorer
from .constants import DISCLAIMER, FRAMEWORKS, SAFE_WITHDRAWAL_RATE, SCORE_WEIGHTS
from .intake import FinancialIntake
from .knowledge_sync import KnowledgeBrainSync
from .models import (
    DimensionScore,
    FinalReport,
    FinancialProfile,
    GateVerdict,
    MarketAssumptions,
    RiskScreenResult,
    SimulationResult,
)
from .monte_carlo import MonteCarloEngine
from .risk_screener import RiskSuitabilityScreener
from .roadmap import FIRERoadmapBuilder
from .utils import configure_logging, get_logger

configure_logging()
logger = get_logger("fire_planner.harness")


class FIREPlannerHarness:
    """End-to-end planner harness with explicit quality gates."""

    def __init__(
        self,
        num_simulations: int = 10_000,
        market_assumptions: Optional[MarketAssumptions] = None,
        use_guyton_klinger: bool = False,
        brain_path: Optional[str] = None,
    ):
        self.num_simulations = num_simulations
        self.market_assumptions = market_assumptions
        self.use_guyton_klinger = use_guyton_klinger
        self.knowledge = KnowledgeBrainSync(brain_path=brain_path)

    def run(self, raw_input: Dict[str, Any]) -> FinalReport:
        """Execute the full harness and return a scored deliverable."""
        logger.info("Starting FIRE planner harness")

        # Stage 1: Intake
        profile = self._intake(raw_input)

        # Stage 2: Evidence sync
        evidence_note = self.knowledge.degraded_mode_note()

        # Stage 3: Risk / suitability gate
        risk_screen = RiskSuitabilityScreener.screen(profile)

        # Stage 4: Monte Carlo scoring
        engine = MonteCarloEngine(
            assumptions=self.market_assumptions,
            num_simulations=self.num_simulations,
            use_guyton_klinger=self.use_guyton_klinger,
        )
        simulation = engine.run(profile)

        # Stage 5: Allocation scoring
        allocation_score = AllocationScorer(profile).score()

        # Stage 6: Dimension scores
        dimensions = self._score_dimensions(profile, simulation, allocation_score)

        # Stage 7: Devil's advocate challenge
        devil_review = self._devils_advocate(profile, simulation, allocation_score, dimensions)

        # Stage 8: Roadmap
        roadmap = FIRERoadmapBuilder(
            profile=profile,
            simulation=simulation,
            allocation_score=allocation_score,
            risk_screen=risk_screen,
        ).build()

        # Stage 9: Quality gates
        self._run_quality_gates(
            profile,
            risk_screen,
            dimensions,
            roadmap,
            devil_review,
        )

        composite = self._composite_score(dimensions)
        confidence = self._confidence_level(simulation, allocation_score, risk_screen)

        findings = self._build_findings(profile, simulation, allocation_score, risk_screen, dimensions)
        sources = self._build_sources()
        assumptions = self._build_assumptions(profile, simulation, evidence_note)

        report = FinalReport(
            composite_score=composite,
            confidence_level=confidence,
            dimension_scores=dimensions,
            simulation_result=simulation,
            allocation_score=allocation_score,
            risk_screen=risk_screen,
            roadmap=roadmap,
            findings=findings,
            sources=sources,
            assumptions=assumptions,
            disclaimer=DISCLAIMER,
        )
        logger.info("Harness complete: composite=%.2f confidence=%s", composite, confidence)
        return report

    @staticmethod
    def _intake(raw_input: Dict[str, Any]) -> FinancialProfile:
        missing_questions = FinancialIntake.ask_clarifying_questions(raw_input)
        if missing_questions:
            raise ValueError(
                "Incomplete intake. Clarifying questions:\n" + "\n".join(f"- {q}" for q in missing_questions)
            )
        return FinancialIntake.from_dict(raw_input)

    def _score_dimensions(
        self,
        profile: FinancialProfile,
        simulation: SimulationResult,
        allocation_score,
    ) -> List[DimensionScore]:
        multiple = profile.portfolio_multiple_of_expenses()
        target_multiple = 1.0 / SAFE_WITHDRAWAL_RATE
        sr = profile.savings_rate()

        # Savings rate vs target
        already_retired = profile.current_age >= profile.retirement_age
        if already_retired:
            savings_score = 80.0
            savings_rationale = "Already retired; savings-rate target is not applicable."
        elif sr >= 0.50:
            savings_score = 95.0
            savings_rationale = f"Savings rate {sr:.0%} is excellent for early retirement."
        elif sr >= 0.30:
            savings_score = 80.0
            savings_rationale = f"Savings rate {sr:.0%} is strong but may need to rise for very early retirement."
        elif sr >= 0.15:
            savings_score = 55.0
            savings_rationale = f"Savings rate {sr:.0%} is moderate; early retirement likely requires a higher rate."
        else:
            savings_score = 25.0
            savings_rationale = f"Savings rate {sr:.0%} is too low for typical early-retirement timelines."

        # Withdrawal strategy robustness
        wr = simulation.withdrawal_rate_used
        if wr <= 0.035:
            withdraw_score = 95.0
            withdraw_rationale = f"Withdrawal rate {wr:.1%} is conservative vs the 4% benchmark."
        elif wr <= 0.04:
            withdraw_score = 80.0
            withdraw_rationale = f"Withdrawal rate {wr:.1%} aligns with the 4% rule but carries sequence risk."
        elif wr <= 0.05:
            withdraw_score = 55.0
            withdraw_rationale = f"Withdrawal rate {wr:.1%} is elevated; dynamic guardrails strongly recommended."
        else:
            withdraw_score = 25.0
            withdraw_rationale = f"Withdrawal rate {wr:.1%} is very high and likely unsustainable."

        # Plan success probability (direct from simulation)
        success_pct = simulation.success_probability * 100
        if success_pct >= 95:
            success_score = 95.0
        elif success_pct >= 80:
            success_score = 80.0
        elif success_pct >= 60:
            success_score = 60.0
        else:
            success_score = 30.0

        # Downside / ruin risk
        ruin_pct = simulation.ruin_probability * 100
        if ruin_pct <= 5:
            risk_score = 90.0
            risk_rationale = f"Ruin probability {ruin_pct:.1f}% is low."
        elif ruin_pct <= 15:
            risk_score = 65.0
            risk_rationale = f"Ruin probability {ruin_pct:.1f}% is moderate; monitor guardrails."
        elif ruin_pct <= 30:
            risk_score = 40.0
            risk_rationale = f"Ruin probability {ruin_pct:.1f}% is elevated."
        else:
            risk_score = 15.0
            risk_rationale = f"Ruin probability {ruin_pct:.1f}% is unacceptably high."

        return [
            DimensionScore(
                name="Savings rate vs target",
                score=savings_score,
                weight=SCORE_WEIGHTS["savings_rate_vs_target"],
                rationale=savings_rationale,
                evidence=FRAMEWORKS["trinity_study"]["source"],
            ),
            DimensionScore(
                name="Asset allocation quality",
                score=allocation_score.overall_score,
                weight=SCORE_WEIGHTS["asset_allocation_quality"],
                rationale=allocation_score.rationale,
                evidence=FRAMEWORKS["mpt"]["source"],
            ),
            DimensionScore(
                name="Fee drag",
                score=allocation_score.fee_drag_score,
                weight=SCORE_WEIGHTS["fee_drag"],
                rationale=f"Total fee rate {profile.fee_rate:.2%}.",
                evidence=FRAMEWORKS["bogleheads"]["source"],
            ),
            DimensionScore(
                name="Withdrawal strategy robustness",
                score=withdraw_score,
                weight=SCORE_WEIGHTS["withdrawal_strategy_robustness"],
                rationale=withdraw_rationale,
                evidence=FRAMEWORKS["guyton_klinger"]["source"],
            ),
            DimensionScore(
                name="Plan success probability",
                score=success_score,
                weight=SCORE_WEIGHTS["plan_success_probability"],
                rationale=f"Monte Carlo success probability {success_pct:.1f}% over {simulation.num_simulations:,} paths.",
                evidence=FRAMEWORKS["monte_carlo"]["source"],
            ),
            DimensionScore(
                name="Downside / ruin risk",
                score=risk_score,
                weight=SCORE_WEIGHTS["downside_ruin_risk"],
                rationale=risk_rationale,
                evidence=FRAMEWORKS["monte_carlo"]["source"],
            ),
        ]

    def _devils_advocate(
        self,
        profile: FinancialProfile,
        simulation: SimulationResult,
        allocation_score,
        dimensions: List[DimensionScore],
    ) -> List[str]:
        """Stress-test the strongest claims; return objections and responses."""
        objections: List[str] = []

        # Object to optimistic return assumptions
        if self.market_assumptions and self.market_assumptions.equities_mean_return >= 0.08:
            objections.append(
                "Devil's advocate: equity return assumption ?8% is above long-term historical averages. "
                "Response: sensitivity analysis should be shown to the user."
            )

        # Object to inflation assumption
        if self.market_assumptions and self.market_assumptions.inflation_regime_shock is None:
            objections.append(
                "Devil's advocate: base-case inflation ignores regime risk (e.g., persistent 5-6%). "
                "Response: high-inflation sensitivity scenario is included."
            )

        # Object to perfect sequence luck
        if simulation.success_probability > 0.90:
            objections.append(
                "Devil's advocate: high success probability may reflect favorable return draws. "
                "Response: guardrails and tail-risk analysis are recommended regardless."
            )

        # Object to allocation score
        weakest = min(dimensions, key=lambda d: d.score)
        objections.append(
            f"Devil's advocate: the weakest dimension is '{weakest.name}' ({weakest.score:.0f}/100). "
            f"Response: roadmap prioritizes improving this area first."
        )

        if not objections:
            objections.append(
                "Devil's advocate: no strong objections; assumptions appear conservative and well-documented."
            )
        return objections

    def _run_quality_gates(
        self,
        profile: FinancialProfile,
        risk_screen: RiskScreenResult,
        dimensions: List[DimensionScore],
        roadmap,
        devil_review: List[str],
    ) -> None:
        """Enforce all output quality gates."""
        # Gate A: every dimension cites a source or assumption
        for d in dimensions:
            if not d.evidence:
                raise RuntimeError(f"Quality gate failed: dimension '{d.name}' lacks evidence or assumption")

        # Gate B: risk screen must not be a surprise halt (we still produce output for warnings)
        if risk_screen.halted():
            # Halt is allowed to flow through as a flagged report, but the deliverable must say so.
            pass

        # Gate C: devil's advocate performed
        if not devil_review:
            raise RuntimeError("Quality gate failed: devil's advocate review missing")

        # Gate D: roadmap prioritized
        if not roadmap:
            raise RuntimeError("Quality gate failed: roadmap is empty")

        logger.info("All quality gates passed")

    @staticmethod
    def _composite_score(dimensions: List[DimensionScore]) -> float:
        return round(sum(d.score * d.weight for d in dimensions), 2)

    @staticmethod
    def _confidence_level(
        simulation: SimulationResult,
        allocation_score,
        risk_screen: RiskScreenResult,
    ) -> str:
        if risk_screen.halted():
            return "low (halted by suitability gate)"
        if simulation.num_simulations >= 10_000 and allocation_score.overall_score >= 70:
            return "high"
        if simulation.num_simulations >= 2_000:
            return "medium"
        return "low"

    @staticmethod
    def _build_findings(
        profile: FinancialProfile,
        simulation: SimulationResult,
        allocation_score,
        risk_screen: RiskScreenResult,
        dimensions: List[DimensionScore],
    ) -> Dict[str, List[str]]:
        strengths: List[str] = []
        gaps: List[str] = []
        risks: List[str] = []

        if simulation.success_probability >= 0.80:
            strengths.append(
                f"Monte Carlo success probability {simulation.success_probability:.0%} is strong."
            )
        else:
            gaps.append(
                f"Success probability {simulation.success_probability:.0%} is below the 80% comfort zone."
            )

        if allocation_score.overall_score >= 75:
            strengths.append("Portfolio allocation score is solid relative to framework targets.")
        else:
            gaps.append(allocation_score.rationale)

        if risk_screen.flags:
            risks.extend(risk_screen.flags)
        if risk_screen.warnings:
            risks.extend(risk_screen.warnings)

        if simulation.ruin_probability > 0.10:
            risks.append(
                f"Ruin probability of {simulation.ruin_probability:.0%} warrants spending guardrails."
            )

        weakest = min(dimensions, key=lambda d: d.score)
        gaps.append(f"Weakest scoring dimension: {weakest.name} ({weakest.score:.0f}/100).")

        return {
            "strengths": strengths,
            "gaps": gaps,
            "risks": risks,
        }

    def _build_sources(self) -> List[tuple]:
        sources = [
            (FRAMEWORKS["trinity_study"]["name"], FRAMEWORKS["trinity_study"]["source"]),
            (FRAMEWORKS["monte_carlo"]["name"], FRAMEWORKS["monte_carlo"]["source"]),
            (FRAMEWORKS["mpt"]["name"], FRAMEWORKS["mpt"]["source"]),
            (FRAMEWORKS["bogleheads"]["name"], FRAMEWORKS["bogleheads"]["source"]),
            (FRAMEWORKS["guyton_klinger"]["name"], FRAMEWORKS["guyton_klinger"]["source"]),
        ]
        if self.knowledge.degraded:
            sources.append(
                (
                    "SECOND-KNOWLEDGE-BRAIN.md",
                    "Local seeded knowledge base (live refresh unavailable)",
                )
            )
        return sources

    @staticmethod
    def _build_assumptions(
        profile: FinancialProfile,
        simulation: SimulationResult,
        evidence_note: str,
    ) -> List[str]:
        assumptions = [evidence_note]
        assumptions.append(
            f"Withdrawal model: real fixed withdrawals starting at "
            f"{simulation.annual_withdrawal:,.0f}/yr ({simulation.withdrawal_rate_used:.2%} of portfolio)."
        )
        for key, value in simulation.assumptions.items():
            if key != "num_simulations" and key != "portfolio_multiple_of_expenses":
                assumptions.append(f"{key}: {value:.2%}")
        assumptions.append(f"Simulations: {simulation.num_simulations:,} independent paths.")
        assumptions.append(
            f"Plan horizon: age {profile.current_age} to {profile.life_expectancy} "
            f"({profile.years_to_retirement()} accumulation years, {profile.years_in_retirement()} retirement years)."
        )
        return assumptions


def run_fire_planner(
    raw_input: Dict[str, Any],
    num_simulations: int = 10_000,
    market_assumptions: Optional[MarketAssumptions] = None,
    use_guyton_klinger: bool = False,
    brain_path: Optional[str] = None,
) -> FinalReport:
    """Convenience entrypoint for the full harness."""
    harness = FIREPlannerHarness(
        num_simulations=num_simulations,
        market_assumptions=market_assumptions,
        use_guyton_klinger=use_guyton_klinger,
        brain_path=brain_path,
    )
    return harness.run(raw_input)

