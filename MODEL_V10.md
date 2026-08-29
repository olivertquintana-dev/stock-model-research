# V10 Independent Point-in-Time Validation

## Purpose
V10 is a hard validation gate, not another optimization stage.

## Required independent data
A historical dataset sourced independently from the current research dataset, containing:
- Date
- Ticker
- Value (appropriately adjusted price)
- UniverseDate or equivalent point-in-time membership information
- Liquidity measure

## Validation rules
1. Reconstruct the eligible universe as it existed on each rebalance date.
2. Apply liquidity constraints before ranking.
3. Keep the RS63 signal and Top 30 / Top 50 specifications frozen.
4. Apply realistic transaction-cost and turnover assumptions.
5. Compare against a tradeable benchmark.
6. Evaluate a fully untouched holdout period.

## Gate
No further claim of robustness should be made unless the independent dataset passes schema and coverage checks and the frozen model remains competitive after rerunning the pipeline.

Current status: BLOCKED_PENDING_INDEPENDENT_DATA.
