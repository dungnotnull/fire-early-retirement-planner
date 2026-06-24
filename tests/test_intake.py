"""Tests for the financial intake sub-skill."""
from __future__ import annotations

import pytest

from fire_planner.intake import FinancialIntake
from fire_planner.models import AssetAllocation, FinancialProfile, RiskTolerance


def test_intake_from_dict_success():
    data = {
        "current_age": 40,
        "retirement_age": 55,
        "life_expectancy": 95,
        "current_portfolio": 800_000,
        "annual_gross_income": 120_000,
        "annual_expenses": 50_000,
        "annual_savings": 40_000,
        "allocation": {"equities": 0.70, "bonds": 0.25, "cash": 0.05},
        "risk_tolerance": "moderate",
    }
    profile = FinancialIntake.from_dict(data)
    assert isinstance(profile, FinancialProfile)
    assert profile.current_age == 40
    assert profile.savings_rate() == 40_000 / 120_000
    assert profile.allocation.equities == 0.70


def test_intake_missing_fields_raises():
    with pytest.raises(ValueError) as exc_info:
        FinancialIntake.from_dict({"current_age": 40})
    assert "Incomplete intake" in str(exc_info.value)


def test_intake_invalid_age_order():
    data = {
        "current_age": 50,
        "retirement_age": 45,
        "life_expectancy": 95,
        "current_portfolio": 800_000,
        "annual_gross_income": 120_000,
        "annual_expenses": 50_000,
        "annual_savings": 40_000,
        "allocation": {"equities": 0.70, "bonds": 0.25, "cash": 0.05},
        "risk_tolerance": "moderate",
    }
    with pytest.raises(ValueError):
        FinancialIntake.from_dict(data)


def test_intake_allocation_sum_exceeds_one():
    data = {
        "current_age": 40,
        "retirement_age": 55,
        "life_expectancy": 95,
        "current_portfolio": 800_000,
        "annual_gross_income": 120_000,
        "annual_expenses": 50_000,
        "annual_savings": 40_000,
        "allocation": {"equities": 0.70, "bonds": 0.25, "cash": 0.10, "alternatives": 0.10},
        "risk_tolerance": "moderate",
    }
    with pytest.raises(ValueError):
        FinancialIntake.from_dict(data)


def test_ask_clarifying_questions():
    questions = FinancialIntake.ask_clarifying_questions({"current_age": 40})
    assert len(questions) > 0
    assert any("retirement age" in q.lower() for q in questions)


def test_intake_accepts_asset_allocation_object():
    alloc = AssetAllocation(equities=0.60, bonds=0.30, cash=0.10)
    data = {
        "current_age": 40,
        "retirement_age": 55,
        "life_expectancy": 95,
        "current_portfolio": 800_000,
        "annual_gross_income": 120_000,
        "annual_expenses": 50_000,
        "annual_savings": 40_000,
        "allocation": alloc,
        "risk_tolerance": RiskTolerance.MODERATE,
    }
    profile = FinancialIntake.from_dict(data)
    assert profile.allocation == alloc
