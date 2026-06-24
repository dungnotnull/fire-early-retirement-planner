---
name: fire-early-retirement-planner__sub-fire-roadmap
description: Sub-skill of fire-early-retirement-planner -- Produce a prioritized savings-rate, allocation and withdrawal-guardrail action plan with milestones.
---

## Purpose
Produce a prioritized savings-rate, allocation and withdrawal-guardrail action plan with milestones, ranked by impact x effort.

## Inputs
- `FinancialProfile` from `sub-financial-intake`.
- `SimulationResult` from `sub-montecarlo-engine`.
- `AllocationScore` from `sub-allocation-scoring`.
- `RiskScreenResult` from `sub-risk-suitability-screener`.

## Procedure
1. **Savings actions**
   - Compute target portfolio (25x annual expenses for 4% rule).
   - Compute required annual savings to close the gap over years to retirement.
   - If savings rate < 30%, recommend raising it.
2. **Allocation actions**
   - If equity deviates ? 10% from age-based glide path, recommend rebalancing.
   - If crypto > 10%, recommend reducing to ? 5%.
   - If bonds+cash < 10%, recommend adding fixed-income ballast.
   - If fee drag score < 70, recommend switching to low-cost index funds.
3. **Withdrawal actions**
   - If effective withdrawal rate > 4%, recommend lowering it or increasing the portfolio.
   - If ? 4%, recommend adopting Guyton-Klinger dynamic guardrails.
   - If ruin probability > 10%, recommend a flexible spending floor/ceiling plan.
4. **Risk-mitigation actions**
   - Convert the top risk-screen warnings into explicit roadmap items.
5. **Tax actions**
   - If `tax_status` missing, recommend documenting account tax placement.
6. **Prioritize**
   - Assign impact (1-5) and effort (1-5) to each item.
   - Bucket into Critical/High/Medium/Low.
   - Sort by priority class then by impact/effort ratio descending.

## Outputs
- Ordered list of `RoadmapItem` objects, each with title, description, impact, effort, priority, rationale, evidence and optional milestone/savings_delta/success_delta.

## Quality Gate
- Output is complete and structured.
- Every item is actionable and cites a framework or explicit assumption.
- Items are prioritized by impact x effort.

## Implementation
The production implementation lives in `src/fire_planner/roadmap.py` (`FIRERoadmapBuilder`).
