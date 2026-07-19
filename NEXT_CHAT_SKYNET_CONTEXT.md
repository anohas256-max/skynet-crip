# SKYNET handoff context — 2026-07-18

Path: `/root/skynet`. Real trading is prohibited:

- `REAL_TRADING_ENABLED=false`
- `REAL_TRADING_ARMED=false`
- `LIVE_DRY_RUN=true`

Closed research: V19 anomaly/direction (`NO_VALIDATION_EDGE`), V20 Binance lead/context (`STOP_NO_VALIDATION_EDGE`), and V21 slow cross-sectional trend/momentum (`STOP_NO_VALIDATION_EDGE`). Do not retest, tune, or derive live/shadow/recorder work from these branches.

V21 recovery facts: MEXC 1h public history failed continuity; allowed Binance USD-M monthly fallback was feasibility-only. Technical recovery expanded the omitted old-symbol registry and used official monthly funding archives after the live Binance funding API returned HTTP 451. The fixed shared split was 2022-01-01--2026-06-30. Universe: BTC, ETH, DOGE, BNB, AVAX, ADA, ETC, LINK, BCH, DOT, ATOM. All eight fixed 12h/24h configurations failed validation at severe cost; untouched final was never opened.

V22 is also closed: the preregistered basis-only cross-sectional convergence audit used official Binance USD-M monthly executable, mark, index, and actual funding archives over the same fixed universe/split. Actual mark/index gaps were not interpolated; symbols were made unavailable at affected decisions. All four fixed configurations (INSTANT_BASIS or MEAN_24H_BASIS, HOLD_24H or HOLD_72H) failed severe-cost validation. No frozen candidate exists and untouched final was not opened. Decision: `STOP_NO_VALIDATION_EDGE`. Do not reopen, tune, or derive live/shadow/recorder work from V22.

Meta-audit conclusion: V19--V22 are closed without a validation edge. Global status: `STOP_RESEARCH_NO_EVIDENCE`. Do not start V23 or change trading configuration unless a new external data source or a fundamentally different market hypothesis is introduced. `REAL_TRADING_ENABLED=false`, `REAL_TRADING_ARMED=false`, `LIVE_DRY_RUN=true`.

V24 Binance USD-M launch momentum is a separate preregistered branch. The official Binance CMS catalogue became rate-limited (HTTP 429) after one request and two allowed retries before an event record was accepted. No kline/funding data was downloaded and no validation/final evaluation was opened. Current V24 decision: `STOP_SOURCE_RATE_LIMITED`; do not infer an edge or start any trading/shadow work.
