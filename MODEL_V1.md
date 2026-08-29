# Model V1.0 Specification

## Name
RS63 Technical Selector V1.0

## Purpose
Cross-sectional technical stock selection.

## Signal
63-session trailing return:

`RS63 = Price[t] / Price[t-63] - 1`

Stocks are ranked cross-sectionally by RS63.

## Selection
Select the top 10% of the available universe.

## Research evidence
- Horizon tested: 126 sessions.
- Strongest historical candidate in S2/S3/S4.
- Temporal holdout used: 2023-2026.
- S5 showed top-decile utility but weak full-universe monotonicity.

## Operational interpretation
This is a research selector, not an execution-ready trading strategy.

## Known limitations
- Universe is not point-in-time reconstructed.
- No liquidity screen.
- No transaction costs or slippage.
- No corporate-action audit beyond source data.
- No position sizing or portfolio construction layer.
