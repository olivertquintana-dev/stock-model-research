# V6 Regime Filter & Defensive Overlay

Tests a Top 30 RS63 portfolio with a simple, lagged market regime overlay.

Risk-on:
- Prior six-month equal-weight universe return is positive.
- Hold the Top 30 portfolio.

Risk-off:
- Prior six-month universe return is non-positive.
- Hold a 0% cash-return proxy.

The regime signal is shifted one month to avoid using same-month information.

This is a research overlay only. A real implementation requires a tradeable benchmark, cash yield, taxes, execution assumptions and out-of-sample validation.
