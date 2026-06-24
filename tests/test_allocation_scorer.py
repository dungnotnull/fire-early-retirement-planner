"""Tests for the allocation scoring sub-skill."""
from __future__ import annotations

from dataclasses import replace

from fire_planner.allocation_scorer import AllocationScorer
from fire_planner.models import AssetAllocation


def test_classic_allocation_score(classic_4pct_profile):
    scorer = AllocationScorer(classic_4pct_profile)
    score = scorer.score()
    assert 0 <= score.overall_score <= 100
    assert 0 <= score.diversification_score <= 100
    assert 0 <= score.fee_drag_score <= 100
    assert 0 <= score.glide_path_score <= 100
    assert 0 <= score.tax_efficiency_score <= 100


def test_crypto_allocation_low_diversification(crypto_profile):
    score = AllocationScorer(crypto_profile).score()
    assert score.diversification_score <= 60
    assert score.overall_score < 60


def test_high_fee_penalty(classic_4pct_profile):
    profile = replace(classic_4pct_profile, fee_rate=0.03)
    score = AllocationScorer(profile).score()
    assert score.fee_drag_score < 50


def test_low_equity_for_age_penalty(classic_4pct_profile):
    profile = replace(
        classic_4pct_profile,
        allocation=AssetAllocation(equities=0.20, bonds=0.70, cash=0.10),
    )
    score = AllocationScorer(profile).score()
    assert score.glide_path_score < 70

