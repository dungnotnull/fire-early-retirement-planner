"""Framework-grounded constants and defaults for the FIRE planner."""
from __future__ import annotations

from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# World-renowned frameworks and citations used for scoring
# ---------------------------------------------------------------------------
FRAMEWORKS: Dict[str, Dict[str, str]] = {
    "trinity_study": {
        "name": "Trinity Study / Bengen Safe Withdrawal Rate",
        "authors": "Cooley, Hubbard, Walz (1998); Bengen (1994)",
        "summary": (
            "Foundational research on sustainable withdrawal rates and the "
            "origin and limits of the '4% rule'."
        ),
        "source": "Journal of Financial Planning, 1998",
    },
    "monte_carlo": {
        "name": "Monte Carlo simulation (sequence-of-returns risk)",
        "authors": "Standard actuarial / quantitative finance practice",
        "summary": (
            "Stochastic modeling of portfolio paths to estimate probability of "
            "plan success rather than a single deterministic path."
        ),
        "source": "Quantitative finance literature",
    },
    "mpt": {
        "name": "Modern Portfolio Theory (Markowitz)",
        "authors": "Harry Markowitz (1952)",
        "summary": (
            "Efficient-frontier basis for risk-adjusted allocation across "
            "equities, bonds and cash."
        ),
        "source": "Journal of Finance, 1952",
    },
    "bogleheads": {
        "name": "Bogleheads low-cost index philosophy",
        "authors": "Bogleheads community; Jack Bogle (Vanguard)",
        "summary": (
            "Evidence on fee drag, diversification and behavioral discipline for "
            "long-horizon investors."
        ),
        "source": "https://www.bogleheads.org/wiki/",
    },
    "guyton_klinger": {
        "name": "Guyton-Klinger guardrails / dynamic withdrawal",
        "authors": "Guyton & Klinger (2006)",
        "summary": (
            "Rule-based dynamic spending adjustments that materially raise plan "
            "survival vs fixed withdrawals."
        ),
        "source": "Journal of Financial Planning, 2006",
    },
}


# ---------------------------------------------------------------------------
# Default market assumptions -- grounded in long-term historical data
# Sources: FRED, Dimson-Marsh-Staunton (Credit Suisse Yearbook), Morningstar
# ---------------------------------------------------------------------------
DEFAULT_MARKET_ASSUMPTIONS: Dict[str, float] = {
    "equities_mean_return": 0.070,
    "equities_volatility": 0.160,
    "bonds_mean_return": 0.035,
    "bonds_volatility": 0.050,
    "cash_mean_return": 0.020,
    "cash_volatility": 0.010,
    "alternatives_mean_return": 0.050,
    "alternatives_volatility": 0.250,
    "correlation_equities_bonds": 0.0,
    "inflation_mean": 0.025,
    "inflation_volatility": 0.010,
}

# ---------------------------------------------------------------------------
# Guardrails and thresholds
# ---------------------------------------------------------------------------
SAFE_WITHDRAWAL_RATE: float = 0.04
MAX_RECOMMENDED_CRYPTO_RATIO: float = 0.05
MIN_EMERGENCY_FUND_MONTHS: int = 3
TARGET_EMERGENCY_FUND_MONTHS: int = 6

# Age-based glide-path targets (equity fraction)
GLIDE_PATH: Dict[int, float] = {
    25: 0.90,
    35: 0.80,
    45: 0.70,
    55: 0.60,
    65: 0.50,
    75: 0.40,
    85: 0.30,
}

# ---------------------------------------------------------------------------
# Score weights for composite FIRE score (must sum to 1.0)
# ---------------------------------------------------------------------------
SCORE_WEIGHTS: Dict[str, float] = {
    "savings_rate_vs_target": 0.15,
    "asset_allocation_quality": 0.20,
    "fee_drag": 0.10,
    "withdrawal_strategy_robustness": 0.15,
    "plan_success_probability": 0.25,
    "downside_ruin_risk": 0.15,
}

# Sanity check
assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-9, "Score weights must sum to 1.0"


# ---------------------------------------------------------------------------
# Simulation defaults
# ---------------------------------------------------------------------------
DEFAULT_NUM_SIMULATIONS: int = 10_000
DEFAULT_SEED: int = 191
MAX_AGE_CEILING: int = 120


# ---------------------------------------------------------------------------
# Knowledge-brain configuration
# ---------------------------------------------------------------------------
ARXIV_CATEGORIES: List[str] = ["q-fin.PM", "q-fin.RM", "econ.GN"]
DOMAIN_SOURCES: List[str] = [
    "https://www.ssrn.com/",
    "https://www.bogleheads.org/wiki/",
    "https://www.morningstar.com/retirement",
    "https://fred.stlouisfed.org/",
    "https://www.ssa.gov/oact/",
]
SEARCH_QUERIES: List[str] = [
    "safe withdrawal rate research 2026",
    "sequence of returns risk early retirement",
    "dynamic withdrawal guardrails Guyton Klinger",
    "Monte Carlo retirement success probability study",
]


# ---------------------------------------------------------------------------
# Standard disclaimer
# ---------------------------------------------------------------------------
DISCLAIMER: str = (
    "This analysis is provided for informational and educational purposes only "
    "and is not professional legal, tax, accounting, or investment advice. "
    "Consult a licensed financial planner or fiduciary before acting."
)
