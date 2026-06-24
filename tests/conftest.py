"""Shared fixtures for the FIRE planner test suite."""
from __future__ import annotations

import pytest

from fire_planner.models import AssetAllocation, FinancialProfile, MarketAssumptions, RiskTolerance


@pytest.fixture
def classic_4pct_profile():
    """A user asking the classic 'Can I retire at 45 with 25x expenses?' scenario."""
    return FinancialProfile(
        current_age=45,
        retirement_age=45,
        life_expectancy=95,
        current_portfolio=1_250_000,
        annual_gross_income=0,
        annual_expenses=50_000,
        annual_savings=0,
        allocation=AssetAllocation(equities=0.60, bonds=0.30, cash=0.10),
        risk_tolerance=RiskTolerance.MODERATE,
        target_withdrawal_rate=0.04,
        emergency_fund_months=12,
        fee_rate=0.001,
    )


@pytest.fixture
def crypto_profile():
    """Aggressive crypto allocation profile."""
    return FinancialProfile(
        current_age=35,
        retirement_age=45,
        life_expectancy=90,
        current_portfolio=500_000,
        annual_gross_income=150_000,
        annual_expenses=60_000,
        annual_savings=60_000,
        allocation=AssetAllocation(equities=0.10, bonds=0.05, cash=0.05, alternatives=0.80, crypto=0.80),
        risk_tolerance=RiskTolerance.AGGRESSIVE,
        emergency_fund_months=3,
        fee_rate=0.005,
    )


@pytest.fixture
def coast_profile():
    """Coast-FIRE profile with no further savings."""
    return FinancialProfile(
        current_age=35,
        retirement_age=50,
        life_expectancy=90,
        current_portfolio=600_000,
        annual_gross_income=100_000,
        annual_expenses=50_000,
        annual_savings=0,
        allocation=AssetAllocation(equities=0.70, bonds=0.25, cash=0.05),
        risk_tolerance=RiskTolerance.MODERATE,
        emergency_fund_months=6,
        fee_rate=0.0015,
    )


@pytest.fixture
def high_inflation_assumptions():
    return MarketAssumptions(
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
