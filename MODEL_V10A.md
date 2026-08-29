# V10-A Point-in-Time Data Adapter

Canonical schema:
| Column | Meaning |
|---|---|
| Date | Observation/trading date |
| Ticker | Security identifier |
| Value | Adjusted price |
| UniverseDate | Date on which membership/eligibility is known point-in-time |
| Liquidity | Liquidity measure supplied by provider |

The adapter accepts common aliases such as symbol/ticker, close/price, membership_date/universe_date and dollar_volume/liquidity.

## Workflow
1. Place an independently sourced parquet file at `data/raw_point_in_time.parquet`, or set `PIT_SOURCE`.
2. Run the adapter.
3. Inspect `outputs/v10a_adapter_status.json`.
4. If READY, V10 can consume `data/point_in_time_universe.parquet`.

No synthetic point-in-time membership is generated: missing source data remains blocked rather than being silently fabricated.
