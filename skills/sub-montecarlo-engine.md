---
name: fire-early-retirement-planner__sub-montecarlo-engine
description: Sub-skill of fire-early-retirement-planner -- Run stochastic simulations across return/inflation regimes and report success probability, percentile outcomes and ruin risk.
---

## Purpose
Run stochastic simulations across return/inflation regimes and report success probability, percentile outcomes and ruin risk.

## Inputs
- `FinancialProfile` from `sub-financial-intake`.
- `MarketAssumptions` (mean return, volatility, inflation, correlation) from harness defaults or user override.
- Optional `use_guyton_klinger` flag for dynamic guardrails.

## Procedure
1. Validate simulation count (? 100).
2. Seed the random number generator for reproducibility.
3. For each simulation path:
   - Initialize portfolio to `current_portfolio`.
   - For each year from `current_age` to `life_expectancy`:
     - Draw annual inflation from a normal distribution (or fixed regime shock).
     - Draw annual portfolio return from a normal distribution with blended mean/volatility for the allocation.
     - Accumulation phase: compound portfolio, subtract fee drag, add annual savings.
     - Retirement phase: compound portfolio, subtract fee drag, inflate the annual withdrawal, optionally apply Guyton-Klinger guardrails, subtract withdrawal.
     - If portfolio reaches ? 0, mark path as `depleted` and record depletion age.
4. Aggregate paths into success probability, ruin probability, median/mean/percentile final balances, and median depletion age.
5. Optionally run sensitivity analysis across base, high-inflation, low-return and stagflation regimes.

## Outputs
- `SimulationResult` with `success_probability`, `ruin_probability`, percentile balances, `withdrawal_rate_used`, `annual_withdrawal`, `assumptions`, and full `paths`.

## Quality Gate
- Output is complete and structured.
- Assumptions are explicit (returns, volatility, inflation, simulation count).
- No output presents probability as certainty; tail risk is quantified.
- Sensitivity analysis is available for regime-stress questions.

## Implementation
The production implementation lives in `src/fire_planner/monte_carlo.py` (`MonteCarloEngine`).
