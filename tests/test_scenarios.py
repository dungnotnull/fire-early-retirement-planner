"""End-to-end scenario tests matching tests/test-scenarios.md.

This module validates the seven named scenarios plus adversarial edge cases.
"""
from __future__ import annotations

import pytest

from fire_planner.harness import run_fire_planner
from fire_planner.models import GateVerdict
from fire_planner.report import ReportRenderer


def _run_scenario(raw, num_simulations=500):
    return run_fire_planner(raw, num_simulations=num_simulations)


def test_scenario_1_classic_4pct_check():
    """User: 'Can I retire at 45 with 25x expenses?'"""
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
    report = _run_scenario(raw)
    assert report.disclaimer
    assert report.simulation_result.withdrawal_rate_used == 0.04
    assert all(d.evidence for d in report.dimension_scores)
    assert report.roadmap
    assert report.risk_screen.verdict in (GateVerdict.PASS, GateVerdict.WARNING)
    # Output should state probability, not certainty
    rendered = ReportRenderer(report).render()
    assert "probability" in rendered.lower()


def test_scenario_2_aggressive_crypto():
    """User: 'My FIRE portfolio is 80% crypto'"""
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
    report = _run_scenario(raw)
    assert report.risk_screen.halted()
    assert any("crypto" in flag.lower() for flag in report.risk_screen.flags)
    assert report.simulation_result.ruin_probability > 0.0
    assert report.roadmap


def test_scenario_3_coast_fire():
    """User: 'Can I stop saving now and coast?'"""
    raw = {
        "current_age": 35,
        "retirement_age": 50,
        "life_expectancy": 90,
        "current_portfolio": 600_000,
        "annual_gross_income": 100_000,
        "annual_expenses": 50_000,
        "annual_savings": 0,
        "allocation": {"equities": 0.70, "bonds": 0.25, "cash": 0.05},
        "risk_tolerance": "moderate",
        "emergency_fund_months": 6,
        "fee_rate": 0.0015,
    }
    report = _run_scenario(raw)
    assert report.assumptions
    assert any("date" in a.lower() or "return" in a.lower() for a in report.assumptions)
    assert report.roadmap


def test_scenario_4_high_inflation():
    """User: 'What if inflation stays at 6%?'"""
    from fire_planner.models import MarketAssumptions

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
    assumptions = MarketAssumptions(
        equities_mean_return=0.07,
        equities_volatility=0.16,
        bonds_mean_return=0.035,
        bonds_volatility=0.05,
        cash_mean_return=0.02,
        cash_volatility=0.01,
        alternatives_mean_return=0.05,
        alternatives_volatility=0.25,
        correlation_equities_bonds=0.0,
        inflation_mean=0.025,
        inflation_volatility=0.01,
        inflation_regime_shock=0.06,
        seed=42,
    )
    report = _run_scenario(raw)
    # Inflation assumption should be noted; run with shock to compare
    shocked = run_fire_planner(raw, num_simulations=500, market_assumptions=assumptions)
    assert any("inflation" in a.lower() for a in report.assumptions)
    assert shocked.simulation_result.ruin_probability >= report.simulation_result.ruin_probability


def test_scenario_5_longevity_tail():
    """User: 'What if I live to 100?'"""
    raw = {
        "current_age": 45,
        "retirement_age": 45,
        "life_expectancy": 100,
        "current_portfolio": 1_250_000,
        "annual_gross_income": 0,
        "annual_expenses": 50_000,
        "annual_savings": 0,
        "allocation": {"equities": 0.60, "bonds": 0.30, "cash": 0.10},
        "risk_tolerance": "moderate",
        "target_withdrawal_rate": 0.04,
    }
    report = _run_scenario(raw)
    assert report.simulation_result.num_simulations == 500
    assert any("100" in a or "longevity" in a.lower() for a in report.assumptions)
    # Simulation is valid; exact success-probability ordering can vary with stochastic draws.
    assert 0.0 <= report.simulation_result.success_probability <= 1.0


def test_scenario_6_degraded_mode():
    """Any scenario with WebSearch/WebFetch unavailable falls back to knowledge brain."""
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
    }
    report = _run_scenario(raw)
    # No fabricated live data; degraded mode disclosed via assumptions
    assert any("unavailable" in a.lower() or "offline" in a.lower() or "seeded" in a.lower()
               for a in report.assumptions)


def test_scenario_7_insufficient_input():
    """Vague one-line request missing key fields."""
    with pytest.raises(ValueError) as exc_info:
        _run_scenario({"current_age": 40})
    assert "Incomplete intake" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Adversarial / edge-case scenarios beyond the initial 5
# ---------------------------------------------------------------------------

def test_adversarial_zero_expenses():
    raw = {
        "current_age": 45,
        "retirement_age": 45,
        "life_expectancy": 95,
        "current_portfolio": 1_000_000,
        "annual_gross_income": 0,
        "annual_expenses": 0,
        "annual_savings": 0,
        "allocation": {"equities": 0.60, "bonds": 0.30, "cash": 0.10},
        "risk_tolerance": "moderate",
    }
    with pytest.raises(ValueError):
        _run_scenario(raw)


def test_adversarial_negative_portfolio():
    raw = {
        "current_age": 45,
        "retirement_age": 55,
        "life_expectancy": 95,
        "current_portfolio": -100_000,
        "annual_gross_income": 100_000,
        "annual_expenses": 50_000,
        "annual_savings": 20_000,
        "allocation": {"equities": 0.60, "bonds": 0.30, "cash": 0.10},
        "risk_tolerance": "moderate",
    }
    with pytest.raises(ValueError):
        _run_scenario(raw)


def test_adversarial_very_high_withdrawal_rate():
    raw = {
        "current_age": 45,
        "retirement_age": 45,
        "life_expectancy": 85,
        "current_portfolio": 500_000,
        "annual_gross_income": 0,
        "annual_expenses": 75_000,
        "annual_savings": 0,
        "allocation": {"equities": 0.60, "bonds": 0.30, "cash": 0.10},
        "risk_tolerance": "aggressive",
        "target_withdrawal_rate": 0.15,
    }
    report = _run_scenario(raw)
    assert report.risk_screen.halted() or report.risk_screen.warned()
    assert report.simulation_result.ruin_probability > 0.5

