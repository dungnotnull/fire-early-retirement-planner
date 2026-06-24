"""Tests for the Monte Carlo engine."""
from __future__ import annotations

import pytest

from fire_planner.monte_carlo import MonteCarloEngine
from fire_planner.models import AssetAllocation, FinancialProfile, MarketAssumptions, RiskTolerance


def test_classic_4pct_success_probability(classic_4pct_profile):
    engine = MonteCarloEngine(num_simulations=1_000, use_guyton_klinger=False)
    result = engine.run(classic_4pct_profile)
    assert 0.0 <= result.success_probability <= 1.0
    assert result.num_simulations == 1_000
    assert result.withdrawal_rate_used == 0.04
    assert result.annual_withdrawal == 50_000


def test_coast_scenario_requires_compounding(coast_profile):
    engine = MonteCarloEngine(num_simulations=1_000, use_guyton_klinger=False)
    result = engine.run(coast_profile)
    assert result.ruin_probability > result.success_probability or result.success_probability < 0.80


def test_high_inflation_regime(high_inflation_assumptions):
    profile = FinancialProfile(
        current_age=45,
        retirement_age=45,
        life_expectancy=85,
        current_portfolio=1_250_000,
        annual_gross_income=0,
        annual_expenses=50_000,
        annual_savings=0,
        allocation=AssetAllocation(equities=0.60, bonds=0.30, cash=0.10),
        risk_tolerance=RiskTolerance.MODERATE,
        target_withdrawal_rate=0.04,
    )
    engine = MonteCarloEngine(assumptions=high_inflation_assumptions, num_simulations=500)
    result = engine.run(profile)
    # High fixed inflation should lower success vs base case
    assert result.ruin_probability > 0.0


def test_sensitivity_analysis(classic_4pct_profile):
    results = MonteCarloEngine.sensitivity_analysis(
        classic_4pct_profile, num_simulations=500
    )
    assert len(results) == 4
    names = {r["scenario"] for r in results}
    assert names == {"base", "high_inflation", "low_return", "stagflation"}


def test_simulation_paths_populated(classic_4pct_profile):
    engine = MonteCarloEngine(num_simulations=100)
    result = engine.run(classic_4pct_profile)
    assert len(result.paths) == 100


def test_invalid_sim_count():
    with pytest.raises(ValueError):
        MonteCarloEngine(num_simulations=50)

