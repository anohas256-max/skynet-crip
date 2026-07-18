# V19--V22 meta-audit

Read-only synthesis of the final reports and the two context handoffs. No data
were downloaded and no backtest was run.

| Signal family | Validation trades or pairs (best full validation candidate) | Best full-candidate severe PF | Closure reason |
|---|---:|---:|---|
| V19 directional anomaly / opportunity classifier | 9 trades | 2.19 | `NO_VALIDATION_EDGE`: only the 0.45 threshold traded (the other frozen thresholds had zero trades), and no threshold passed; the separate fixed sequence-ridge audit also had 0/5 positive folds and 0/2 positive halves. |
| V20 Binance lead/context | 39 trades | 1.29 | `STOP_NO_VALIDATION_EDGE`: no candidate met the hard validation gates; final remained closed. |
| V21 slow cross-sectional trend/momentum | 574 positions | 0.80 | `STOP_NO_VALIDATION_EDGE`: all eight fixed configurations failed severe-cost gates; final remained closed. |
| V22 cross-sectional perpetual basis convergence | 220 positions / 110 pairs | 0.88 | `STOP_NO_VALIDATION_EDGE`: all four fixed configurations had negative severe PnL and negative delayed-entry PnL; no candidate froze and final remained closed. |

## Verified closure and final gates

- V19: classifier decision `NO_VALIDATION_EDGE`; final was not opened because no validation threshold passed. The V19 sequence-ridge audit separately reported `NO_WALK_FORWARD_EDGE` and real decision blocked.
- V20: `BINANCE_LEAD_DECISION=STOP_NO_VALIDATION_EDGE`; `FINAL_UNTOUCHED_TEST=NOT_OPENED`.
- V21: `V21_TREND_DECISION=STOP_NO_VALIDATION_EDGE`; untouched final not opened.
- V22: `V22_BASIS_DECISION=STOP_NO_VALIDATION_EDGE`; validation passed 0; untouched final not opened.

## Common report-grounded failure evidence

- V19's sequence model had no positive walk-forward folds or halves; the classifier's only non-zero validation threshold had nine trades and no threshold passed.
- V20's 30 fixed validation configurations produced no hard-gate winner; even the best full hard-PF candidate had a negative leave-best result.
- V21's best severe PF was 0.80 across the fixed configurations, all of which failed severe-cost gates.
- V22's best severe PF was 0.88; all four severe PnLs and all delayed-entry severe PnLs were negative.

## Verdict

There is no report-based evidence to continue seeking alpha on this same dataset under severe costs. `STOP_RESEARCH_NO_EVIDENCE`.

Safety remains unchanged: `REAL_TRADING_ENABLED=false`,
`REAL_TRADING_ARMED=false`, `LIVE_DRY_RUN=true`.
