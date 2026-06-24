"""Tests for the FIRE roadmap builder."""
from __future__ import annotations

from fire_planner.allocation_scorer import AllocationScorer
from fire_planner.monte_carlo import MonteCarloEngine
from fire_planner.risk_screener import RiskSuitabilityScreener
from fire_planner.roadmap import FIRERoadmapBuilder


def test_roadmap_prioritized(classic_4pct_profile):
    sim = MonteCarloEngine(num_simulations=500).run(classic_4pct_profile)
    alloc = AllocationScorer(classic_4pct_profile).score()
    screen = RiskSuitabilityScreener.screen(classic_4pct_profile)
    roadmap = FIRERoadmapBuilder(classic_4pct_profile, sim, alloc, screen).build()
    assert len(roadmap) > 0
    # Verify impact--effort sorting within priority classes
    for i in range(len(roadmap) - 1):
        if roadmap[i].priority == roadmap[i + 1].priority:
            assert roadmap[i].impact_x_effort() >= roadmap[i + 1].impact_x_effort()


def test_crypto_roadmap_has_reduce_crypto(crypto_profile):
    sim = MonteCarloEngine(num_simulations=500).run(crypto_profile)
    alloc = AllocationScorer(crypto_profile).score()
    screen = RiskSuitabilityScreener.screen(crypto_profile)
    roadmap = FIRERoadmapBuilder(crypto_profile, sim, alloc, screen).build()
    titles = [item.title.lower() for item in roadmap]
    assert any("crypto" in t for t in titles)


def test_coast_roadmap_suggests_savings(coast_profile):
    sim = MonteCarloEngine(num_simulations=500).run(coast_profile)
    alloc = AllocationScorer(coast_profile).score()
    screen = RiskSuitabilityScreener.screen(coast_profile)
    roadmap = FIRERoadmapBuilder(coast_profile, sim, alloc, screen).build()
    titles = [item.title.lower() for item in roadmap]
    assert any("savings" in t or "coast" in t for t in titles)
