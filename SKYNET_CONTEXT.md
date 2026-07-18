# SKYNET context — 2026-07-18

Real trading is blocked: `REAL_TRADING_ENABLED=false`, `REAL_TRADING_ARMED=false`, and `LIVE_DRY_RUN=true`.

V19 directional anomaly research is closed. The sequence ridge failed all three models and five OOS folds; the opportunity/direction classifier reported `NO_VALIDATION_EDGE`. Do not reopen or tune V19 hypotheses.

V20 Binance lead/context is closed: official daily Binance aggTrades and exact recorded MEXC bid/ask snapshots were audited under the fixed 30-rule family. No validation candidate met the hard gates at exact 15-second MEXC entry and 300-second exit. Untouched final was not opened. Decision: `STOP_NO_VALIDATION_EDGE`. Do not reopen or tune V20 hypotheses.

V21 slow cross-sectional 12--24h trend/momentum recovery is closed. MEXC public 1h history was not continuous enough (only one seed candidate reached 2023 continuously), so the allowed official Binance USD-M monthly archive fallback was used solely for signal feasibility, not MEXC execution proof. Recovery corrected an incomplete fallback candidate registry and replaced an HTTP-451 live funding endpoint with official monthly funding archives. The conservative shared 2022-01-01--2026-06-30 split was fixed before PnL. Corrected train-only universe: BTC, ETH, DOGE, BNB, AVAX, ADA, ETC, LINK, BCH, DOT, ATOM. All eight preregistered configurations failed validation at severe cost; final was not opened. Decision: `STOP_NO_VALIDATION_EDGE`.

V22 cross-sectional perpetual basis convergence is closed. It used only official Binance USD-M monthly executable 1h klines, markPriceKlines, indexPriceKlines, and actual fundingRate archives for the fixed V21 universe and 2022-01-01--2026-06-30 split. Mark/index gaps were never interpolated and data availability was enforced per decision. All four preregistered basis-only configurations (instant/24h mean by 24h/72h hold) failed severe-cost validation; no validation candidate froze and untouched final was not opened. Decision: `STOP_NO_VALIDATION_EDGE`. This is Binance signal feasibility only, not MEXC execution proof; do not reopen or tune V22.

Next permissible work is a newly preregistered, bounded research question with independent data-quality validation. Do not create live, shadow, recorder, timer, or real-trading infrastructure from V19/V20/V21 results.
