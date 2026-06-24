"""FIRE Early Retirement Planner -- production-grade Monte Carlo planning harness.

A financial-planning skill in the Finance, Investment & Insurance cluster that builds
personalized Financial-Independence/Retire-Early plans stress-tested with Monte Carlo
simulation against safe-withdrawal-rate research.
"""

__version__ = "1.0.0"
__author__ = "fire-early-retirement-planner contributors"

from .harness import run_fire_planner, FIREPlannerHarness
from .models import FinancialProfile, AssetAllocation, FinalReport
from .intake import FinancialIntake
from .risk_screener import RiskSuitabilityScreener
from .monte_carlo import MonteCarloEngine
from .allocation_scorer import AllocationScorer
from .roadmap import FIRERoadmapBuilder

__all__ = [
    "run_fire_planner",
    "FIREPlannerHarness",
    "FinancialProfile",
    "AssetAllocation",
    "FinalReport",
    "FinancialIntake",
    "RiskSuitabilityScreener",
    "MonteCarloEngine",
    "AllocationScorer",
    "FIRERoadmapBuilder",
]
