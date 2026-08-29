# Model V2 Specification

## Name
V2 RS63 Operational Research Selector

## Core signal
RS63 = Price[t] / Price[t-63] - 1

## Eligibility
- Latest observed price must be at least 5.
- Positive price and a complete 63-session lookback are required.

## Selection
1. Rank the eligible universe by RS63.
2. Retain the top 10%.
3. Publish the top 20 as an equal-weight research basket.

## Risk controls currently implemented
- Minimum price filter: 5.
- Maximum published basket size: 20.
- Equal research weights: 5% each when 20 names are available.

## Important limitations
This remains a research model. Liquidity, point-in-time universe membership, corporate actions, transaction costs, sector caps, and execution constraints still require dedicated source data and validation.
