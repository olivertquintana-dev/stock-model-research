# V9 Final Research Decision

## Status
Research pipeline V1–V8 completed successfully.

## Core finding
A 63-session relative-strength signal showed persistent positive historical results across multiple portfolio constructions and independent time splits.

## Portfolio candidates
- **Top 30:** strongest return-oriented candidate.
- **Top 50:** more balanced diversification candidate.

## Key evidence
- V3: Top 20 portfolio backtest produced historical excess absolute return under simplified costs.
- V4: risk analysis showed materially higher volatility and drawdown than the benchmark.
- V5: diversification improved risk characteristics; Top 30 maximized return while Top 100 improved risk metrics among RS variants.
- V6: the tested six-month regime overlay did not improve results and was rejected.
- V7: Top 30/50 retained positive results across development, test, and holdout windows.
- V8: dataset coverage changes materially over time and survivorship bias cannot be ruled out.

## Formal decision
**Research candidate: CONDITIONAL PASS.**

The signal merits further research and paper-trading validation, but is **not approved as a capital-ready strategy** because the current evidence lacks:
1. independently reconstructed point-in-time universe;
2. realistic liquidity and spread constraints;
3. corporate-action validation;
4. tradeable benchmark and cash assumptions;
5. independent out-of-sample dataset validation.

## Recommended frozen research specification
- Signal: 63-session return.
- Eligibility: latest price >= 5.
- Portfolio candidates: Top 30 and Top 50, equal weight.
- Rebalance: monthly.
- Cost sensitivity: at least 10 bps times constituent turnover.

## Next gate
Acquire point-in-time historical universe and liquidity data, then rerun the complete pipeline unchanged. Only if results survive that independent validation should paper trading or implementation design proceed.

## Bottom line
The research has identified a promising momentum effect, but current results should be treated as **research evidence, not investment advice or executable performance**.
