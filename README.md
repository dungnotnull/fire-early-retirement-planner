<div align="center">

  <img src="https://img.icons8.com/color/96/fire.png" alt="FIRE" width="80" height="80"/>

  # 🔥 FIRE Early Retirement Planner

  **A production-grade, framework-grounded Monte Carlo retirement planning harness**

  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
  [![pytest](https://img.shields.io/badge/tests-38%20passed-brightgreen.svg?style=for-the-badge&logo=pytest)](./tests)
  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)

  *Stress-test your Financial Independence / Retire Early plan against sequence-of-returns risk, inflation regimes, and longevity tails.*

  [Quick Start](#-quick-start) • [Features](#-features) • [Frameworks](#-frameworks) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

> :warning: **Disclaimer:** This tool provides **informational and educational analysis only**. It is **not** professional legal, tax, accounting, or investment advice. Always verify with a licensed fiduciary or financial planner before acting.

---

## 🎯 Why this exists

Most FIRE calculators give you a single deterministic number:

> *"You need 25x expenses, then you can withdraw 4% forever."*

That advice is a useful rule of thumb, but it quietly ignores the risks that destroy real retirement plans:

<div align="center">

| Risk | Why it matters |
|------|----------------|
| 🎲 **Sequence-of-returns risk** | Bad returns in your first decade of retirement can permanently impair a portfolio |
| 💹 **Inflation regimes** | Sustained 5-6% inflation changes everything |
| 👴 **Longevity tails** | Living to 100 is expensive |
| 📊 **Portfolio construction** | 80% crypto, 2% fees, or zero bonds are not compatible with sustainable withdrawals |

</div>

This planner treats retirement as a **stochastic problem**, not a deterministic one. It runs thousands of simulated lifetime paths, scores each dimension against named research frameworks, challenges its own assumptions, and returns a prioritized improvement roadmap.

---

## ✨ Features

<details>
<summary><b>🔍 Evidence-based intake</b></summary>

Structured financial profile with validation, clarifying questions, and no hidden assumptions. Captures:
- Current portfolio composition and value
- Income, expenses, and savings rate
- Risk tolerance and time horizon
- Target retirement age and longevity assumptions
- Emergency fund status and fee structure

</details>

<details>
<summary><b>🛡️ Suitability gate</b></summary>

Halts/warns on red flags before running simulations:
- Excessive crypto or concentrated positions
- High fee ratios (>1%)
- Low portfolio multiples relative to expenses
- Missing or inadequate emergency funds
- Unrealistic withdrawal rates (>6%)

</details>

<details>
<summary><b>🎲 Monte Carlo engine</b></summary>

Thousands of correlated return/inflation paths with:
- Percentile outcomes (10th, 25th, 50th, 75th, 90th)
- Ruin probability and median ruin age
- Regime sensitivity analysis
- Sequence-of-returns risk quantification

</details>

<details>
<summary><b>📈 Regime sensitivity</b></summary>

Four built-in economic scenarios:
- **Base:** Historical average returns and inflation
- **High inflation:** Elevated CPI with reduced real returns
- **Low return:** Secular stagnation scenario
- **Stagflation:** High inflation + low returns

</details>

<details>
<summary><b>⚖️ Framework-grounded scoring</b></summary>

Six dimensions scored 0-100 against citable frameworks:
- Savings rate vs target (Trinity/Bengen + Bogleheads)
- Asset allocation quality (Markowitz MPT + Bogleheads)
- Fee drag (Bogleheads low-cost philosophy)
- Withdrawal strategy robustness (Guyton-Klinger + Trinity)
- Plan success probability (Monte Carlo)
- Downside/ruin risk (Monte Carlo)

</details>

<details>
<summary><b>📝 Devil's-advocate review</b></summary>

Built-in challenge pass that surfaces:
- Weakest assumptions in your plan
- Hidden risks not captured by the model
- Suggested stress tests and sensitivity analyses

</details>

<details>
<summary><b>🎯 Prioritized roadmap</b></summary>

Action items ranked by impact × effort with:
- Specific, achievable milestones
- Cited sources for each recommendation
- Timeline estimates for implementation
- Expected improvement in plan success probability

</details>

<details>
<summary><b>🧠 Self-updating knowledge brain</b></summary>

`SECOND-KNOWLEDGE-BRAIN.md` grown by a crawl4ai/WebSearch pipeline:
- Continuous learning from academic sources
- Automatic citation management
- Graceful degradation in offline mode
- Weekly cron recommended for updates

</details>

---

## 📚 Frameworks we score against

Every scored dimension cites one of these named, citable frameworks:

<div align="center">

| Framework | Core Contribution |
|-----------|-------------------|
| **Trinity Study / Bengen** | Origin, limits, and evidence behind the 4% rule |
| **Monte Carlo Simulation** | Quantifying sequence-of-returns risk and plan survival probability |
| **Modern Portfolio Theory (Markowitz)** | Efficient-frontier allocation and age-based glide paths |
| **Bogleheads Philosophy** | Fee drag, diversification, and behavioral discipline |
| **Guyton-Klinger Guardrails** | Dynamic spending rules that materially improve plan survival |

</div>

---

## 🚀 Quick start

### Installation

```bash
# Clone the repository
git clone https://github.com/dungnotnull/fire-early-retirement-planner.git
cd fire-early-retirement-planner

# Install with pip
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

### Run your first plan

```python
from fire_planner.harness import run_fire_planner
from fire_planner.report import ReportRenderer

# Define your financial profile
profile = {
    # Demographics
    "current_age": 45,
    "retirement_age": 45,
    "life_expectancy": 95,

    # Financials
    "current_portfolio": 1_250_000,
    "annual_gross_income": 0,
    "annual_expenses": 50_000,
    "annual_savings": 0,

    # Portfolio allocation (must sum to 1.0)
    "allocation": {
        "equities": 0.60,
        "bonds": 0.30,
        "cash": 0.10
    },

    # Risk & strategy
    "risk_tolerance": "moderate",
    "target_withdrawal_rate": 0.04,

    # Safety nets
    "emergency_fund_months": 12,
    "fee_rate": 0.001,
}

# Run the full analysis
report = run_fire_planner(profile, num_simulations=10_000)

# Render and print the report
print(ReportRenderer(report).render())
```

### Run the test suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fire_planner

# Run specific scenario tests
pytest tests/test_scenarios.py -v
```

Expected output: **38 passed** ✅

---

## 🏗️ Architecture

The harness follows a disciplined pipeline from intake to deliverable:

```
                          User input
                              |
                              v
                 +---------------------------+
                 | 1. sub-financial-intake   |
                 |   validate + normalize    |
                 +---------------------------+
                              |
                              v
                 +---------------------------+
                 | 2. SECOND-KNOWLEDGE-BRAIN |
                 |   evidence sync (live or  |
                 |   degraded offline mode)  |
                 +---------------------------+
                              |
                              v
                 +---------------------------+
                 | 3. sub-risk-suitability   |
                 |   screener gate           |
                 +---------------------------+
                              |
                              v
        +--------------------+--------------------+
        |                                         |
        v                                         v
+-----------------------+             +-----------------------+
| 4a. sub-montecarlo-   |             | 4b. sub-allocation-   |
|    engine             |             |    scoring            |
| success probability,  |             | diversification, fees,|
| ruin risk, percentiles|             | glide path, tax eff.  |
+-----------------------+             +-----------------------+
        |                                         |
        +--------------------+--------------------+
                             |
                             v
                 +---------------------------+
                 | 5. Devil's-advocate review |
                 | challenge weakest assumptions|
                 +---------------------------+
                             |
                             v
                 +---------------------------+
                 | 6. sub-fire-roadmap        |
                 | prioritized action plan    |
                 +---------------------------+
                             |
                             v
                 +---------------------------+
                 | 7. report.py renderer      |
                 | professional markdown      |
                 +---------------------------+
```

### Pipeline stages

<details>
<summary><b>1. Financial Intake</b></summary>

- Validates all numeric inputs are non-negative
- Ensures allocation sums to 1.0
- Checks age logic (retirement ≥ current, life_expectancy ≥ retirement)
- Derives missing values (savings rate = savings / income)
- Returns normalized `FinancialProfile` dataclass

</details>

<details>
<summary><b>2. Knowledge Sync</b></summary>

- Loads `SECOND-KNOWLEDGE-BRAIN.md` with framework definitions
- Gracefully degrades if file is missing
- Supports optional live refresh via crawl4ai pipeline

</details>

<details>
<summary><b>3. Risk Suitability Screener</b></summary>

- Checks portfolio multiple (assets / expenses) ≥ 15x
- Flags crypto allocation > 20%
- Warns if fee_rate > 0.01 (1%)
- Requires emergency_fund_months ≥ 3
- Validates withdrawal_rate ≤ 0.08 (8%)

</details>

<details>
<summary><b>4a. Monte Carlo Engine</b></summary>

- Generates correlated return/inflation paths
- Models equities (μ=7%, σ=15%), bonds (μ=4%, σ=5%), cash (μ=2%, σ=1%)
- Supports regime shifts (high inflation, low return, stagflation)
- Calculates success probability and ruin age distribution
- Returns percentile outcomes (10th, 25th, 50th, 75th, 90th)

</details>

<details>
<summary><b>4b. Allocation Scorer</b></summary>

- Scores diversification (penalizes concentration)
- Evaluates fee drag (0.5% fee → 50% score)
- Checks glide path appropriateness for age
- Assesses tax efficiency (location optimization)

</details>

<details>
<summary><b>5. Devil's Advocate Review</b></summary>

- Identifies weakest assumption (lowest-scoring dimension)
- Suggests stress tests (high-inflation, long-lived, bear-market-first)
- Flags hidden risks (concentration, sequence, longevity)

</details>

<details>
<summary><b>6. FIRE Roadmap</b></summary>

- Ranks actions by impact × effort matrix
- Provides specific milestones (e.g., "Increase savings to 30%")
- Cites framework sources for each recommendation
- Estimates timeline for measurable improvement

</details>

<details>
<summary><b>7. Report Renderer</b></summary>

- Generates professional markdown report
- Includes all scores, percentiles, and recommendations
- Format ready for GitHub, Notion, or print

</details>

---

## 📊 Scoring dimensions

<div align="center">

| Dimension | Weight | Framework | What it measures |
|-----------|--------|-----------|------------------|
| 💰 Savings rate vs target | 15% | Trinity/Bengen + Bogleheads | Gross savings rate vs early-retirement targets |
| 📈 Asset allocation quality | 20% | Markowitz MPT + Bogleheads | Diversification, concentration, age-based glide path |
| 💸 Fee drag | 10% | Bogleheads | Total expense ratio vs low-cost benchmarks |
| 🎯 Withdrawal strategy robustness | 15% | Guyton-Klinger + Trinity | Initial withdrawal rate and dynamic guardrails |
| ✅ Plan success probability | 25% | Monte Carlo | Probability portfolio survives the full horizon |
| ⚠️ Downside / ruin risk | 15% | Monte Carlo | Tail depletion probability and median ruin age |

</div>

The composite score is a transparent weighted aggregate. Every dimension includes a cited source or an explicit assumption.

---

## 📁 Project structure

```
fire-early-retirement-planner/
├── src/fire_planner/                 # Core Python package
│   ├── __init__.py
│   ├── constants.py                   # Frameworks, defaults, thresholds
│   ├── models.py                      # Typed dataclasses
│   ├── utils.py                       # Validation & statistics helpers
│   ├── intake.py                      # Financial intake sub-skill
│   ├── risk_screener.py               # Suitability gate sub-skill
│   ├── monte_carlo.py                 # Stochastic simulation engine
│   ├── allocation_scorer.py           # MPT/Bogleheads scoring
│   ├── roadmap.py                     # Prioritized action-plan builder
│   ├── knowledge_sync.py              # Knowledge-brain loader
│   ├── harness.py                     # End-to-end orchestration
│   └── report.py                      # Markdown report renderer
│
├── skills/                            # Codex skill definitions
│   ├── main.md
│   ├── sub-financial-intake.md
│   ├── sub-risk-suitability-screener.md
│   ├── sub-montecarlo-engine.md
│   ├── sub-allocation-scoring.md
│   └── sub-fire-roadmap.md
│
├── tools/
│   └── knowledge_updater.py           # Crawl4ai + WebSearch pipeline
│
├── tests/                             # pytest suite: 38 tests
│   ├── conftest.py
│   ├── test_intake.py
│   ├── test_risk_screener.py
│   ├── test_monte_carlo.py
│   ├── test_allocation_scorer.py
│   ├── test_roadmap.py
│   ├── test_harness.py
│   ├── test_scenarios.py
│   └── test-scenarios.md
│
├── SECOND-KNOWLEDGE-BRAIN.md          # Living domain knowledge base
├── PROJECT-detail.md                  # Full technical specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md
├── CLAUDE.md                          # Agent context
├── pyproject.toml
├── requirements.txt
├── LICENSE
└── README.md                          # You are here
```

---

## 💡 Example use cases

These map directly to the test scenarios in `tests/test-scenarios.md`:

<details>
<summary><b>1. Classic 4% check</b></summary>

*"Can I retire at 45 with 25x expenses?"*

```python
profile = {
    "current_age": 45,
    "retirement_age": 45,
    "current_portfolio": 1_250_000,
    "annual_expenses": 50_000,
    ...
}
# Expected: ~85% success probability under base assumptions
```

</details>

<details>
<summary><b>2. Aggressive crypto allocation</b></summary>

*"My FIRE portfolio is 80% crypto."*

```python
profile = {
    "allocation": {"crypto": 0.80, "equities": 0.15, "bonds": 0.05},
    ...
}
# Expected: suitability gate warning, low allocation-quality score
```

</details>

<details>
<summary><b>3. Coast-FIRE</b></summary>

*"Can I stop saving now and coast?"*

```python
profile = {
    "current_age": 35,
    "retirement_age": 45,
    "current_portfolio": 500_000,
    "annual_savings": 0,  # Stop saving, just let it grow
    ...
}
# Expected: analysis of coast-to-FIRE viability
```

</details>

<details>
<summary><b>4. High inflation worry</b></summary>

*"What if inflation stays at 6%?"*

```python
report = run_fire_planner(profile, regime="high_inflation")
# Expected: reduced success probability, inflation-risk commentary
```

</details>

<details>
<summary><b>5. Longevity tail</b></summary>

*"What if I live to 100?"*

```python
profile = {
    "life_expectancy": 100,
    ...
}
# Expected: extended horizon analysis, longevity-risk commentary
```

</details>

<details>
<summary><b>6. Degraded mode</b></summary>

Works offline with the seeded knowledge brain.

```python
# No network access required
report = run_fire_planner(profile)
# Expected: full functionality using local SECOND-KNOWLEDGE-BRAIN.md
```

</details>

<details>
<summary><b>7. Insufficient input</b></summary>

Asks clarifying questions instead of assuming.

```python
profile = {
    "current_age": 45,
    # Missing: retirement_age, expenses, etc.
}
# Expected: intake raises ValidationError with specific missing fields
```

</details>

---

## 🧠 Knowledge brain

`SECOND-KNOWLEDGE-BRAIN.md` is the living domain knowledge base. It is seeded with:

- Five core frameworks (Trinity/Bengen, Monte Carlo, MPT, Bogleheads, Guyton-Klinger)
- Five foundational research papers with summaries
- Authoritative sources for ongoing updates

### Refresh the knowledge brain

Optional, but recommended for staying current with research:

```bash
# Install crawl dependencies
pip install -e .[crawl]

# Run the knowledge updater
python tools/knowledge_updater.py
```

Recommended schedule: **weekly cron**.

The pipeline gracefully degrades if crawl4ai or network access is unavailable.

---

## 🧪 Testing & validation

### Run the full suite

```bash
pytest -v
```

### Run with coverage

```bash
pytest --cov=fire_planner --cov-report=html
```

### Run specific scenario tests

```bash
pytest tests/test_scenarios.py -v
```

### Test suite composition

- ✅ Unit tests for every sub-skill
- ✅ End-to-end harness tests
- ✅ All 7 named scenarios from `tests/test-scenarios.md`
- ✅ 3 adversarial edge cases (zero expenses, negative portfolio, 15% withdrawal rate)

Current status: **38 passed** 🎉

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Open an issue** to discuss large changes before implementing
2. **Add tests** for any new behavior or bug fix
3. **Ensure `pytest` passes** before submitting a PR
4. **Follow the existing code style** (black, ruff, mypy)
5. **Cite your sources** for any framework or scoring changes

### Development setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/fire-early-retirement-planner.git
cd fire-early-retirement-planner

# Install in development mode
pip install -e .[dev]

# Run pre-commit checks
pytest
ruff check src/
mypy src/
black --check src/
```

---

## 📜 License

MIT License — see [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

- **William Bengen**, **Cooley, Hubbard, & Walz**, and the **Trinity Study** for safe-withdrawal-rate foundations
- **Harry Markowitz** for Modern Portfolio Theory
- The **Bogleheads community** for low-cost, disciplined investing education
- **Jonathan Guyton & William Klinger** for dynamic withdrawal guardrails
- The open-source Python ecosystem: **NumPy**, **pytest**, and **crawl4ai**

---

## 📚 References & Further Reading

- [The Trinity Study: An Update (Cooley, Hubbard, Walz)](https://advisorone.com/c/content/dam/advisorone/RIC/TrinityStudyUpdate.pdf)
- [Bengen: Determining Safe Withdrawal Rates](https://www.afjournal.com/articles/determining-safe-withdrawal-rates-expanding-the-data/)
- [Guyton-Klinger: Decision Rules for Portfolio Withdrawals](https://www.relevantinvestor.com/images/2006_IJWM_Klinger_Guyton.pdf)
- [Bogleheads Wiki: Safe Withdrawal Rates](https://www.bogleheads.org/wiki/Safe_withdrawal_rates)
- [Morningstar Retirement Research](https://www.morningstar.com/retirement)

---

<div align="center">

  **Built for evidence-first retirement planning.**

  :star: Star this repo if you find it useful!

  [Report Bug](https://github.com/dungnotnull/fire-early-retirement-planner/issues) •
  [Request Feature](https://github.com/dungnotnull/fire-early-retirement-planner/issues) •
  [Visit Documentation](https://github.com/dungnotnull/fire-early-retirement-planner/wiki)

</div>
