"""Tests for the risk-suitability screener gate."""
from __future__ import annotations

from fire_planner.models import GateVerdict
from fire_planner.risk_screener import RiskSuitabilityScreener


def test_classic_profile_passes(classic_4pct_profile):
    result = RiskSuitabilityScreener.screen(classic_4pct_profile)
    assert result.verdict in (GateVerdict.PASS, GateVerdict.WARNING)


def test_crypto_profile_halts(crypto_profile):
    result = RiskSuitabilityScreener.screen(crypto_profile)
    assert result.halted()
    assert any("crypto" in flag.lower() for flag in result.flags)


def test_low_multiple_flags():
    from fire_planner.models import AssetAllocation, FinancialProfile, RiskTolerance
    profile = FinancialProfile(
        current_age=45,
        retirement_age=45,
        life_expectancy=95,
        current_portfolio=100_000,
        annual_gross_income=0,
        annual_expenses=50_000,
        annual_savings=0,
        allocation=AssetAllocation(equities=0.60, bonds=0.30, cash=0.10),
        risk_tolerance=RiskTolerance.MODERATE,
    )
    result = RiskSuitabilityScreener.screen(profile)
    assert result.halted()


def test_high_fee_warns():
    from fire_planner.models import AssetAllocation, FinancialProfile, RiskTolerance
    profile = FinancialProfile(
        current_age=40,
        retirement_age=55,
        life_expectancy=95,
        current_portfolio=1_000_000,
        annual_gross_income=150_000,
        annual_expenses=60_000,
        annual_savings=50_000,
        allocation=AssetAllocation(equities=0.60, bonds=0.30, cash=0.10),
        risk_tolerance=RiskTolerance.MODERATE,
        fee_rate=0.02,
    )
    result = RiskSuitabilityScreener.screen(profile)
    assert result.warned() or result.halted()
    assert any("fee" in w.lower() for w in result.warnings + result.flags)


def test_emergency_fund_missing_warns(classic_4pct_profile):
    from dataclasses import replace
    profile = replace(classic_4pct_profile, emergency_fund_months=None)
    result = RiskSuitabilityScreener.screen(profile)
    assert any("emergency" in w.lower() for w in result.warnings + result.suggestions)
