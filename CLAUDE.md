# CLAUDE.md -- FIRE Early Retirement Planner (Monte Carlo)

**Skill name:** `fire-early-retirement-planner`
**Source idea:** #191 (ideas.md)
**Cluster:** Finance, Investment & Insurance (`finance-insurance`)
**Tagline:** Builds a personalized Financial-Independence/Retire-Early plan stress-tested with Monte Carlo simulation against withdrawal-rate research.
**Current phase:** Phase 5 -- Integration & Cross-Skill Wiring complete.

## Problem This Skill Solves
Aspiring early retirees rely on naive '4% rule' rules of thumb that ignore sequence-of-returns risk, inflation regimes and longevity. This skill builds a personalized FIRE plan, runs Monte Carlo simulations across return/inflation scenarios, and reports success probability with sensitivity analysis.

## Harness Flow Summary
1. **Intake** ? `sub-financial-intake` gathers structured inputs.
2. **Research / evidence sync** ? consult `SECOND-KNOWLEDGE-BRAIN.md`; refresh via WebSearch/WebFetch when available.
3. **Gate** ? compliance check (`sub-risk-suitability-screener`) runs before analysis.
4. **Analysis / scoring** ? `sub-montecarlo-engine` + `sub-allocation-scoring` score against the named frameworks.
5. **Challenge** ? devil's-advocate review stress-tests assumptions and evidence.
6. **Synthesize** ? `sub-fire-roadmap` produces the scored deliverable + prioritized roadmap.
7. **Render** ? `src/fire_planner/report.py` emits the final markdown report.

**Compliance gate:** `sub-risk-suitability-screener` MUST run before the final deliverable is emitted. Output is informational, not professional/legal/financial advice.

## Sub-skills
- `skills/sub-financial-intake.md` -- Capture income, savings rate, current assets, expenses, target retirement age, risk tolerance and longevity assumptions.
- `skills/sub-risk-suitability-screener.md` -- Establish risk capacity vs tolerance and flag unsuitable assumptions (e.g., 80%+ crypto, no emergency fund) before modeling.
- `skills/sub-montecarlo-engine.md` -- Run stochastic simulations across return/inflation regimes and report success probability, percentile outcomes and ruin risk.
- `skills/sub-allocation-scoring.md` -- Score the portfolio against MPT/Bogleheads principles (diversification, fee drag, glide path, tax efficiency).
- `skills/sub-fire-roadmap.md` -- Produce a prioritized savings-rate, allocation and withdrawal-guardrail action plan with milestones.

## Evaluation Frameworks (world-renowned, citable)
- **Trinity Study / Bengen Safe Withdrawal Rate** -- Foundational research on sustainable withdrawal rates and the origin and limits of the '4% rule'.
- **Monte Carlo simulation (sequence-of-returns risk)** -- Stochastic modeling of portfolio paths to estimate probability of plan success rather than a single deterministic path.
- **Modern Portfolio Theory (Markowitz) & asset allocation** -- Efficient-frontier basis for risk-adjusted allocation across equities, bonds and cash.
- **Bogleheads low-cost index philosophy** -- Evidence on fee drag, diversification and behavioral discipline for long-horizon investors.
- **Guyton-Klinger guardrails / dynamic withdrawal** -- Rule-based dynamic spending adjustments that materially raise plan survival vs fixed withdrawals.

## Tools Required
- `WebSearch`, `WebFetch` -- live evidence and trend updates (graceful degradation to the knowledge brain when unavailable).
- `Read`, `Write` -- load the knowledge brain; emit the deliverable.
- `Bash` -- run `python tools/knowledge_updater.py` (crawl4ai pipeline).
- `Python` -- `src/fire_planner` package implements the full harness and all sub-skills.

## Knowledge Sources
- **ArXiv / academic categories:** q-fin.PM, q-fin.RM, econ.GN
- [SSRN Financial Planning eJournal](https://www.ssrn.com/) -- Working papers on withdrawal rates and retirement modeling.
- [Bogleheads wiki](https://www.bogleheads.org/wiki/) -- Reference on low-cost investing and safe-withdrawal methods.
- [Morningstar retirement research](https://www.morningstar.com/retirement) -- Annual state-of-retirement and withdrawal-rate studies.
- [FRED economic data](https://fred.stlouisfed.org/) -- Historical inflation and return series for simulation inputs.
- [Social Security / pension actuarial tables](https://www.ssa.gov/oact/) -- Longevity assumptions for plan horizon.

## Supporting Tools
- `tools/knowledge_updater.py` -- crawl4ai + WebSearch pipeline that grows `SECOND-KNOWLEDGE-BRAIN.md` (recommended weekly cron).
- `src/fire_planner/harness.py` -- main orchestration entry point (`run_fire_planner`).
- `src/fire_planner/report.py` -- markdown report renderer.

## Active Development Tasks
- [x] Scaffold all required deliverables
- [x] Define frameworks, sub-skills and scoring dimensions
- [x] Author knowledge brain v1 and crawl pipeline
- [x] Implement production-grade Python harness and all sub-skills
- [x] Build comprehensive pytest scenario suite (7 scenarios + adversarial cases)
- [x] Expand knowledge brain with foundational papers and authoritative sources
- [x] Complete Phase 0-5 integration and cross-skill wiring

## Related Root Docs
- `README.md` -- project overview, quick start and structure
- `PROJECT-detail.md` -- full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` -- phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` -- living domain knowledge base
