# tests/test-scenarios.md -- FIRE Early Retirement Planner (Monte Carlo)

Scenario-based tests for `fire-early-retirement-planner` (idea #191). Minimum 5; 7 provided (incl. degraded-mode and insufficient-input edge cases), plus 3 adversarial edge cases.

### Scenario 1: Classic 4% check
- **User input:** "Can I retire at 45 with 25x expenses?"
- **Expected harness behavior:** Runs Monte Carlo across regimes, reports success probability and sequence-risk caveat vs naive 4% rule.
- **Frameworks exercised:** Trinity Study / Bengen Safe Withdrawal Rate, Monte Carlo simulation (sequence-of-returns risk), Modern Portfolio Theory (Markowitz) & asset allocation
- **Quality gate under test:** Output states probability not certainty; non-advice disclaimer required.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.

### Scenario 2: Aggressive crypto allocation
- **User input:** "My FIRE portfolio is 80% crypto"
- **Expected harness behavior:** Risk screener flags concentration; models high-variance outcomes and ruin probability.
- **Frameworks exercised:** Trinity Study / Bengen Safe Withdrawal Rate, Monte Carlo simulation (sequence-of-returns risk), Modern Portfolio Theory (Markowitz) & asset allocation
- **Quality gate under test:** Suitability warning before projections.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.

### Scenario 3: Coast-FIRE question
- **User input:** "Can I stop saving now and coast?"
- **Expected harness behavior:** Models coast scenarios and required compounding horizon.
- **Frameworks exercised:** Trinity Study / Bengen Safe Withdrawal Rate, Monte Carlo simulation (sequence-of-returns risk), Modern Portfolio Theory (Markowitz) & asset allocation
- **Quality gate under test:** Assumptions and date-stamped return inputs disclosed.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.

### Scenario 4: High inflation worry
- **User input:** "What if inflation stays at 6%?"
- **Expected harness behavior:** Runs inflation-regime sensitivity and guardrail adjustment.
- **Frameworks exercised:** Trinity Study / Bengen Safe Withdrawal Rate, Monte Carlo simulation (sequence-of-returns risk), Modern Portfolio Theory (Markowitz) & asset allocation
- **Quality gate under test:** Inflation series cited to source.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.

### Scenario 5: Longevity tail
- **User input:** "What if I live to 100?"
- **Expected harness behavior:** Extends horizon, applies actuarial longevity and reports tail-risk depletion.
- **Frameworks exercised:** Trinity Study / Bengen Safe Withdrawal Rate, Monte Carlo simulation (sequence-of-returns risk), Modern Portfolio Theory (Markowitz) & asset allocation
- **Quality gate under test:** Longevity assumption explicitly disclosed.
- **Pass criteria:** scored output produced, gate enforced, every dimension evidence-linked or assumption-marked, prioritized roadmap included.

### Scenario 6: Degraded mode (offline)
- **User input:** any of the above with WebSearch/WebFetch unavailable.
- **Expected behavior:** skill falls back to `SECOND-KNOWLEDGE-BRAIN.md`, explicitly signals degraded mode, and still enforces all gates.
- **Pass criteria:** no fabricated live data; degradation disclosed.

### Scenario 7: Insufficient input
- **User input:** a vague one-line request missing key fields.
- **Expected behavior:** intake sub-skill asks targeted clarifying questions instead of assuming.
- **Pass criteria:** no scored output until required inputs are gathered.

## Adversarial / Edge Cases
1. **Zero expenses** -- must raise a validation error (division by zero / meaningless plan).
2. **Negative portfolio** -- must raise a validation error.
3. **Very high withdrawal rate (15%)** -- risk screen halts/warns and ruin probability is very high.

## Regression Checklist
- [x] All gates enforced on every path (compliance).
- [x] Scores trace to citations or explicit assumptions.
- [x] Devil's-advocate review present.
- [x] Roadmap prioritized by impact x effort.
- [x] Disclaimer present where applicable.
