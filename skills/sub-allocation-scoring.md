---
name: fire-early-retirement-planner__sub-allocation-scoring
description: Sub-skill of fire-early-retirement-planner -- Score the portfolio against MPT/Bogleheads principles (diversification, fee drag, glide path, tax efficiency).
---

## Purpose
Score the portfolio against Modern Portfolio Theory and Bogleheads principles across diversification, fee drag, glide path and tax efficiency.

## Inputs
- `FinancialProfile` from `sub-financial-intake`.
- `SECOND-KNOWLEDGE-BRAIN.md` framework guidance.

## Procedure
1. **Diversification**
   - Penalize portfolios with bonds+cash < 10% (low ballast).
   - Penalize single asset-class dominance ? 90% or ? 75%.
   - Penalize crypto/speculative > 5% and strongly penalize > 20%.
   - Reward international equity diversification when data is provided.
   - Penalize allocation shortfall (sum < 100%).
2. **Fee drag**
   - Compare `fee_rate` to thresholds: ? 0.05% excellent, ? 0.15% good, ? 0.5% fair, > 0.5% poor.
3. **Glide path**
   - Interpolate age-based equity target from the built-in glide-path table.
   - Score based on deviation from target: ? 5% ? excellent, ? 15% ? good, ? 30% ? fair, > 30% ? poor.
4. **Tax efficiency**
   - If `tax_status` provided, score tax-free/tax-deferred/taxable placement.
   - If missing, assume average efficiency and note the assumption.
5. Compute weighted overall score: 35% diversification, 25% fee drag, 25% glide path, 15% tax efficiency.

## Outputs
- `AllocationScore` with sub-scores, overall score, rationale, evidence and per-dimension `DimensionScore` list.

## Quality Gate
- Output is complete and structured.
- Each sub-score links to MPT, Bogleheads or an explicit assumption.
- Rationale identifies the weakest dimension.

## Implementation
The production implementation lives in `src/fire_planner/allocation_scorer.py` (`AllocationScorer`).
