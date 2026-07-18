# V21 universe recovery — final summary

Classification: `A) TECHNICAL_IMPLEMENTATION_ERROR`.

The initial Binance fallback used an incomplete 10-symbol registry and omitted old required USD-M contracts including DOT, LINK, TRX, XLM, AVAX, ATOM, FIL, and NEAR. It also attempted the geographically unavailable live Binance funding endpoint (HTTP 451), despite official monthly `fundingRate` archives being available. The recovery used those archives and documented all candidate quality results in the ignored operational report `v21_universe_recovery_audit.txt`.

Before PnL, V21 fixed the conservative common calendar: every symbol needs continuous 2022-01-01 through 2026-06-30 data, preserving the original 30-month train, 12-month validation, and 12-month final split. Later starts were not used to alter a cross-sectional split.

Corrected train-only universe at the unchanged $1M average hourly volume threshold: BTC, ETH, DOGE, BNB, AVAX, ADA, ETC, LINK, BCH, DOT, ATOM. XRP, SOL, LTC, TRX, XLM, FIL, and NEAR were excluded because official monthly archives have two real gaps (72h and 48h) in 2022; no prices were interpolated.

All eight fixed validation configurations failed severe-cost gates. No untouched final data was opened. Decision: `STOP_NO_VALIDATION_EDGE`.
