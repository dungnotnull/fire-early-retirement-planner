---
name: fire-early-retirement-planner__sub-risk-suitability-screener
description: Sub-skill of fire-early-retirement-planner -- Establish risk capacity vs tolerance and flag unsuitable assumptions (e.g., 80%+ crypto, no emergency fund) before modeling.
---

## Purpose
Establish risk capacity vs tolerance and flag unsuitable assumptions before the Monte Carlo engine runs. The gate returns a verdict (`pass`, `warning`, or `halt`) plus specific flags, warnings and suggestions.

## Inputs
- `FinancialProfile` from `sub-financial-intake`.
- Relevant entries from `SECOND-KNOWLEDGE-BRAIN.md`.

## Procedure
1. Compute the portfolio multiple of annual expenses (`current_portfolio / annual_expenses`).
2. Compare to the implied 25x target for a 4% safe withdrawal rate.
3. Check concentration risk:
   - Crypto/speculative ? 75% ? `halt`.
   - Crypto/speculative ? 20% ? `warning`.
   - Single asset class ? 90% ? `warning`.
   - Equity-only (>95%) ? `warning`.
4. Check withdrawal-rate sustainability:
   - ? 8% ? `halt`.
   - ? 6% ? `warning`.
5. Check fee drag:
   - ? 3% ? `halt`.
   - ? 1.5% ? `warning`.
6. Check emergency fund adequacy:
   - Missing or < 3 months ? `warning`.
7. Check cash-flow capacity:
   - Expenses ? 90% of gross income ? `warning`.
   - Expenses > gross income ? `halt`.
8. Check age / allocation consistency:
   - Retirement < 5 years away with equity > 80% ? `warning`.
   - Long horizon (>60 years) with equity < 40% ? `warning`.
9. Aggregate verdict: any flag ? `halt`; any warning without flags ? `warning`; else `pass`.

## Outputs
- `RiskScreenResult` with `verdict`, `flags`, `warnings`, `suggestions`.

## Quality Gate
- Output is complete and structured.
- Each flag/warning links to a named framework or explicit threshold.
- Halts are surfaced in the final report, not hidden.

## Implementation
The production implementation lives in `src/fire_planner/risk_screener.py` (`RiskSuitabilityScreener`).
