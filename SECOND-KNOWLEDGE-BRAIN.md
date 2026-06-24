# SECOND-KNOWLEDGE-BRAIN.md -- FIRE Early Retirement Planner (Monte Carlo)

> Self-improving domain knowledge base for `fire-early-retirement-planner` (idea #191). Grown by `tools/knowledge_updater.py`.

## Core Concepts & Frameworks
### Trinity Study / Bengen Safe Withdrawal Rate
Foundational research on sustainable withdrawal rates and the origin and limits of the '4% rule'. The classic Trinity Study (Cooley, Hubbard & Walz, 1998) tested 3-6% withdrawals over 15-30 year horizons using US historical returns. Bengen (1994) introduced the 4% rule-of-thumb based on 50/50 stock/bond portfolios.

### Monte Carlo simulation (sequence-of-returns risk)
Stochastic modeling of portfolio paths to estimate probability of plan success rather than a single deterministic path. Sequence-of-returns risk is especially severe in the first decade of retirement because early withdrawals lock in losses and reduce the base from which future growth compounds.

### Modern Portfolio Theory (Markowitz) & asset allocation
Efficient-frontier basis for risk-adjusted allocation across equities, bonds and cash. The mean-variance framework shows that diversification can improve expected return per unit of risk and that the asset mix should align with the investor's horizon and risk tolerance.

### Bogleheads low-cost index philosophy
Evidence on fee drag, diversification and behavioral discipline for long-horizon investors. Keeping total costs below ~0.15% per year materially increases terminal wealth versus higher-cost active strategies.

### Guyton-Klinger guardrails / dynamic withdrawal
Rule-based dynamic spending adjustments that materially raise plan survival vs fixed withdrawals. The guardrails approach raises spending after strong portfolio performance and cuts it after poor performance, keeping withdrawals within a defined corridor.


## Key Research Papers
| Title | Authors | Year | Venue | Link | Relevance |
|-------|---------|------|-------|------|-----------|
| Determining Withdrawal Rates Using Historical Data | William P. Bengen | 1994 | Journal of Financial Planning | https://www.journalfp.com/ | Foundational safe-withdrawal-rate research |
| Retirement Savings: Choosing a Withdrawal Rate That Is Sustainable | Cooley, Hubbard, Walz | 1998 | Journal of Financial Planning | https://www.journalfp.com/ | Trinity Study; tested 3-6% over 15-30 years |
| Portfolio Construction for Taxable Investors | Reichenstein & Meyer | 2013 | CFA Institute Research Foundation | https://www.cfainstitute.org/ | Tax-efficient asset location |
| Optimal Asset Location and Allocation with Taxable and Tax-Deferred Investing | Dammon, Spatt, Zhang | 2004 | Review of Financial Studies | https://academic.oup.com/rfs | Tax-efficient withdrawal sequencing |
| Decision Rules and Maximum Initial Withdrawal Rates | Guyton & Klinger | 2006 | Journal of Financial Planning | https://www.journalfp.com/ | Dynamic guardrails methodology |


## State-of-the-Art Methods & Tools
- Apply the frameworks above as the scoring backbone.
- Prefer the highest available evidence tier (systematic review > meta-analysis > RCT/standard > expert opinion > blog).
- Refresh trend-sensitive figures (prices, thresholds, benchmarks) at analysis time via WebSearch when available.
- Use Monte Carlo rather than deterministic projections for early-retirement planning because long horizons magnify tail risk.
- Implement Guyton-Klinger guardrails (or similar rule-based dynamic spending) to improve plan survival materially above fixed real withdrawals.

## Authoritative Data Sources
| Source | Why it matters |
|--------|----------------|
| [SSRN Financial Planning eJournal](https://www.ssrn.com/) | Working papers on withdrawal rates and retirement modeling. |
| [Bogleheads wiki](https://www.bogleheads.org/wiki/) | Reference on low-cost investing and safe-withdrawal methods. |
| [Morningstar retirement research](https://www.morningstar.com/retirement) | Annual state-of-retirement and withdrawal-rate studies. |
| [FRED economic data](https://fred.stlouisfed.org/) | Historical inflation and return series for simulation inputs. |
| [Social Security / pension actuarial tables](https://www.ssa.gov/oact/) | Longevity assumptions for plan horizon. |
| [ArXiv q-fin.PM](https://arxiv.org/list/q-fin.PM/recent) | Recent portfolio-management and retirement-quant preprints. |
| [ArXiv q-fin.RM](https://arxiv.org/list/q-fin.RM/recent) | Recent risk-management preprints. |
| [ArXiv econ.GN](https://arxiv.org/list/econ.GN/recent) | Recent general-economics preprints. |

## Analytical Frameworks (used for scoring)
- **Trinity Study / Bengen Safe Withdrawal Rate**
- **Monte Carlo simulation (sequence-of-returns risk)**
- **Modern Portfolio Theory (Markowitz) & asset allocation**
- **Bogleheads low-cost index philosophy**
- **Guyton-Klinger guardrails / dynamic withdrawal**

Scoring dimensions derived from these frameworks:
1. Savings rate vs target
2. Asset allocation quality
3. Fee drag
4. Withdrawal strategy robustness
5. Plan success probability
6. Downside / ruin risk

## Self-Update Protocol
- **Crawl sources:** ArXiv (q-fin.PM, q-fin.RM, econ.GN) + the authoritative domain sources above.
- **Search queries:**
  - `safe withdrawal rate research 2026`
  - `sequence of returns risk early retirement`
  - `dynamic withdrawal guardrails Guyton Klinger`
  - `Monte Carlo retirement success probability study`
- **Frequency:** weekly (cron).
- **Append format:** `### [YYYY-MM-DD] <title>` with Authors, Venue, Link, Key finding, Relevance score (0-1), Source-hash (dedupe).
- **Dedupe:** skip entries whose DOI/URL hash already exists.

## Knowledge Update Log
- **2026-06-18** -- Knowledge brain v1 seeded with core frameworks, sources and crawl config for idea #191.
- **2026-06-24** -- Seeded with five foundational papers, authoritative data sources, state-of-the-art methods and scoring dimensions. Pipeline ready for scheduled crawls.
