"""Tests for the main planner harness."""
from __future__ import annotations

import pytest

from fire_planner.harness import FIREPlannerHarness, run_fire_planner


def test_harness_runs_classic_4pct():
    raw = {
        "current_age": 45,
        "retirement_age": 45,
        "life_expectancy": 95,
        "current_portfolio": 1_250_000,
        "annual_gross_income": 0,
        "annual_expenses": 50_000,
        "annual_savings": 0,
        "allocation": {"equities": 0.60, "bonds": 0.30, "cash": 0.10},
        "risk_tolerance": "moderate",
        "target_withdrawal_rate": 0.04,
        "emergency_fund_months": 12,
        "fee_rate": 0.001,
    }
    report = run_fire_planner(raw, num_simulations=500)
    assert report.composite_score > 0
    assert report.roadmap
    assert report.dimension_scores
    assert report.sources
    assert report.disclaimer


def test_harness_incomplete_input_raises():
    with pytest.raises(ValueError) as exc_info:
        run_fire_planner({"current_age": 45})
    assert "Incomplete intake" in str(exc_info.value)


def test_harness_crypto_halts():
    raw = {
        "current_age": 35,
        "retirement_age": 45,
        "life_expectancy": 90,
        "current_portfolio": 500_000,
        "annual_gross_income": 150_000,
        "annual_expenses": 60_000,
        "annual_savings": 60_000,
        "allocation": {"equities": 0.10, "bonds": 0.05, "cash": 0.05, "alternatives": 0.80, "crypto": 0.80},
        "risk_tolerance": "aggressive",
        "emergency_fund_months": 3,
        "fee_rate": 0.005,
    }
    report = run_fire_planner(raw, num_simulations=500)
    assert report.risk_screen.halted()
    assert report.roadmap


def test_harness_with_high_inflation_assumptions(high_inflation_assumptions):
    raw = {
        "current_age": 45,
        "retirement_age": 45,
        "life_expectancy": 85,
        "current_portfolio": 1_250_000,
        "annual_gross_income": 0,
        "annual_expenses": 50_000,
        "annual_savings": 0,
        "allocation": {"equities": 0.60, "bonds": 0.30, "cash": 0.10},
        "risk_tolerance": "moderate",
        "target_withdrawal_rate": 0.04,
    }
    harness = FIREPlannerHarness(
        num_simulations=500,
        market_assumptions=high_inflation_assumptions,
    )
    report = harness.run(raw)
    assert report.simulation_result.success_probability < 1.0
    assert report.assumptions
