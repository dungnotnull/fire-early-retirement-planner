---
name: fire-early-retirement-planner__sub-financial-intake
description: Sub-skill of fire-early-retirement-planner -- Capture income, savings rate, current assets, expenses, target retirement age, risk tolerance and longevity assumptions.
---

## Purpose
Capture income, savings rate, current assets, expenses, target retirement age, risk tolerance and longevity assumptions in a structured, validated record that downstream stages can consume.

## Inputs
- Outputs from the prior harness stage and/or direct user input.
- Relevant entries from `SECOND-KNOWLEDGE-BRAIN.md` (framework defaults).

## Required Fields
| Field | Type | Description |
|-------|------|-------------|
| current_age | int | Today's age |
| retirement_age | int | Desired retirement age (must be > current_age) |
| life_expectancy | int | Planning horizon age (must be > retirement_age) |
| current_portfolio | float | Investable assets today |
| annual_gross_income | float | Pre-tax annual income |
| annual_expenses | float | Annual spending |
| annual_savings | float | Annual contributions to portfolio |
| allocation | dict / AssetAllocation | Equity/bond/cash/alternatives fractions |
| risk_tolerance | string / RiskTolerance | conservative / moderate / aggressive |

## Optional Fields
`target_withdrawal_rate`, `monthly_expenses`, `emergency_fund_months`, `desired_legacy`, `pension_income`, `social_security_annual`, `fee_rate`, `inflation_assumption`, `expected_return_override`, `tax_status`.

## Procedure
1. Validate that all required fields are present and non-null; if any are missing, emit targeted clarifying questions and stop short of producing a scored output.
2. Validate numeric ranges:
   - Ages: 18-120, with `current_age < retirement_age < life_expectancy`.
   - Financials: non-negative portfolio, positive expenses, savings ? income (warn if exceeded).
   - Allocation: each fraction ? 0, core classes (equities/bonds/cash/alternatives) sum ? 1.
   - fee_rate in [0, 0.5]; target_withdrawal_rate in [0, 1] if provided.
3. Normalize the allocation dict into an `AssetAllocation` object.
4. Map `risk_tolerance` string to `RiskTolerance` enum.
5. Parse optional fields with the same validation discipline.
6. Derive derived metrics (savings rate, portfolio multiple of expenses) and attach as notes.
7. Return a `FinancialProfile` dataclass instance.

## Outputs
- A `FinancialProfile` structured record the harness passes downstream.

## Quality Gate
- Output is complete and structured.
- Each material claim is evidence-linked or marked as an assumption.
- No required field is assumed; missing fields trigger clarifying questions.

## Implementation
The production implementation lives in `src/fire_planner/intake.py` (`FinancialIntake`).
