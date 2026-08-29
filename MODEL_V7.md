# V7 Walk-Forward Robustness

Evaluates fixed portfolio constructions (Top 20, 30, 50, 100) independently across:
- 2016-2019 development window
- 2020-2022 test window
- 2023-2026 holdout

No parameter is re-optimized within each period. The objective is to test temporal stability and reduce confidence driven by a single full-sample result.

Remaining caveat: the underlying universe is still not point-in-time reconstructed.
