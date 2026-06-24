# PROJECT-detail.md -- FIRE Early Retirement Planner (Monte Carlo)

## Executive Summary
`fire-early-retirement-planner` is a harness skill in the **Finance, Investment & Insurance** cluster (idea #191). Builds a personalized Financial-Independence/Retire-Early plan stress-tested with Monte Carlo simulation against withdrawal-rate research. It executes a research-first, framework-grounded workflow that ends in a multi-dimensional score and a prioritized, effort/impact-ranked improvement roadmap.

> **Disclaimer:** This skill provides informational analysis only and is **not** professional legal, financial, tax or accounting advice. Verify with a licensed professional before acting.

## Problem Statement
Aspiring early retirees rely on naive '4% rule' rules of thumb that ignore sequence-of-returns risk, inflation regimes and longevity. This skill builds a personalized FIRE plan, runs Monte Carlo simulations across return/inflation scenarios, and reports success probability with sensitivity analysis.

## Target Users & Use Cases
- Practitioners, learners and small teams who need an expert-grade, evidence-based analysis without hiring a specialist.
- Trigger examples:
  - "Can I retire at 45 with 25x expenses?" -> the skill runs its full harness and returns a scored deliverable.
  - "My FIRE portfolio is 80% crypto" -> the skill runs its full harness and returns a scored deliverable.
  - "Can I stop saving now and coast?" -> the skill runs its full harness and returns a scored deliverable.
  - "What if inflation stays at 6%?" -> the skill runs its full harness and returns a scored deliverable.
  - "What if I live to 100?" -> the skill runs its full harness and returns a scored deliverable.

## Harness Architecture
```
User input
   │
   ▼
[Stage 1 Intake]  sub-financial-intake
   │
   ▼
[Stage 2 Research]  SECOND-KNOWLEDGE-BRAIN.md + WebSearch/WebFetch
   │
   ▼
[Stage 3 Gate]  sub-risk-suitability-screener
   │
   ▼
[Stage 4 Scoring]  sub-montecarlo-engine  -> score vs frameworks
   │
   ▼
[Stage 5 Challenge]  devil's-advocate review
   │
   ▼
[Stage 6 Synthesis]  sub-fire-roadmap  -> scored report + roadmap
```

## Full Sub-Skill Catalog
### `sub-financial-intake`
- **Purpose:** Capture income, savings rate, current assets, expenses, target retirement age, risk tolerance and longevity assumptions.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-risk-suitability-screener`
- **Purpose:** Establish risk capacity vs tolerance and flag unsuitable assumptions (e.g., 100% crypto, no emergency fund) before modeling.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-montecarlo-engine`
- **Purpose:** Run stochastic simulations across return/inflation regimes and report success probability, percentile outcomes and ruin risk.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-allocation-scoring`
- **Purpose:** Score the portfolio against MPT/Bogleheads principles (diversification, fee drag, glide path).
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.
### `sub-fire-roadmap`
- **Purpose:** Produce a prioritized savings-rate, allocation and withdrawal-guardrail action plan with milestones.
- **Inputs:** structured fields from prior stages / user.
- **Outputs:** structured record consumed by the next stage.
- **Tools:** Read, WebSearch/WebFetch (as needed).
- **Quality gate:** outputs are complete, evidence-linked, and assumptions are explicit.

## Evaluation Frameworks
1. **Trinity Study / Bengen Safe Withdrawal Rate** -- Foundational research on sustainable withdrawal rates and the origin and limits of the '4% rule'.
2. **Monte Carlo simulation (sequence-of-returns risk)** -- Stochastic modeling of portfolio paths to estimate probability of plan success rather than a single deterministic path.
3. **Modern Portfolio Theory (Markowitz) & asset allocation** -- Efficient-frontier basis for risk-adjusted allocation across equities, bonds and cash.
4. **Bogleheads low-cost index philosophy** -- Evidence on fee drag, diversification and behavioral discipline for long-horizon investors.
5. **Guyton-Klinger guardrails / dynamic withdrawal** -- Rule-based dynamic spending adjustments that materially raise plan survival vs fixed withdrawals.

## Scoring Dimensions
- Savings rate vs target
- Asset allocation quality
- Fee drag
- Withdrawal strategy robustness
- Plan success probability
- Downside / ruin risk

Each dimension is scored 0-100 (or 1-5) with an explicit rationale and at least one cited source or stated assumption. The composite score is a transparent weighted aggregate; weights are disclosed.

## Skill File Format Specification
- Frontmatter: `name` (= `fire-early-retirement-planner`), `description` (one line).
- Required sections: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates.

## E2E Execution Flow
1. Parse request; classify the task and detect missing inputs (ask targeted questions).
2. Run intake sub-skill -> structured profile.
3. Sync evidence from the knowledge brain; refresh via WebSearch/WebFetch when available; otherwise signal degraded mode.
4. Run the compliance gate -- **halt and route out** on red flags.
5. Score against frameworks; record evidence per dimension.
6. Devil's-advocate pass: challenge weakest assumptions, seek disconfirming evidence.
7. Synthesize the deliverable: scored report + prioritized roadmap (effort x impact).
8. Run quality gates; only then present output.

## SECOND-KNOWLEDGE-BRAIN Integration
- Sources: ArXiv (q-fin.PM, q-fin.RM, econ.GN) + the authoritative domain sources listed in `CLAUDE.md`.
- Crawl config and append format are defined in `tools/knowledge_updater.py` and `SECOND-KNOWLEDGE-BRAIN.md`.

## Supporting Tools Spec -- `knowledge_updater.py`
- **Inputs:** crawl query list (below), source URLs, last-run timestamp.
- **Outputs:** appended, de-duplicated, date-stamped entries in `SECOND-KNOWLEDGE-BRAIN.md`.
- **Schedule:** weekly cron.
- **Crawl queries:** `safe withdrawal rate research 2026`, `sequence of returns risk early retirement`, `dynamic withdrawal guardrails Guyton Klinger`, `Monte Carlo retirement success probability study`

## Quality Gates (must all pass before output)
- Every scored dimension cites a source or states an assumption.
- The applicable safety/compliance gate has passed.
- The devil's-advocate review has been performed and its objections addressed.
- The roadmap items are prioritized by effort x impact and are actionable.
- Evidence hierarchy respected (systematic review > meta-analysis > RCT/standard > expert opinion > blog).

## Test Scenarios
1. **Classic 4% check** -- *User:* "Can I retire at 45 with 25x expenses?" -> *Skill:* Runs Monte Carlo across regimes, reports success probability and sequence-risk caveat vs naive 4% rule. (**Gate:** Output states probability not certainty; non-advice disclaimer required.)
2. **Aggressive crypto allocation** -- *User:* "My FIRE portfolio is 80% crypto" -> *Skill:* Risk screener flags concentration; models high-variance outcomes and ruin probability. (**Gate:** Suitability warning before projections.)
3. **Coast-FIRE question** -- *User:* "Can I stop saving now and coast?" -> *Skill:* Models coast scenarios and required compounding horizon. (**Gate:** Assumptions and date-stamped return inputs disclosed.)
4. **High inflation worry** -- *User:* "What if inflation stays at 6%?" -> *Skill:* Runs inflation-regime sensitivity and guardrail adjustment. (**Gate:** Inflation series cited to source.)
5. **Longevity tail** -- *User:* "What if I live to 100?" -> *Skill:* Extends horizon, applies actuarial longevity and reports tail-risk depletion. (**Gate:** Longevity assumption explicitly disclosed.)

## Key Design Decisions
1. Research-first: no scored claim without a citation or explicit assumption.
2. Framework-grounded: scoring uses only the named world-renowned frameworks above.
3. Composable sub-skills (≥3) with explicit gates between stages.
4. Self-improving knowledge brain via the crawl pipeline.
5. Graceful degradation when WebSearch/WebFetch are unavailable.
