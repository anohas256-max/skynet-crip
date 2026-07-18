# SKYNET research operating rules

- `REAL_TRADING_ENABLED` is always `false`.
- `REAL_TRADING_ARMED` is always `false`.
- `LIVE_DRY_RUN` is always `true`.
- Never enable, arm, or place real trades.
- Never read, print, or modify `.env` files or secrets.
- Do not use `systemctl`, restart services, modify `skynet.service` / `skynet-recorder.service`, or alter existing recorder/shadow processes.
- Preserve databases, historical reports, and research data; do not delete them.
- Never commit databases, Binance archives, logs, `.env`, or secrets.
- Do not tune parameters after inspecting an untouched test set.
- Stop and report honestly if a required gate fails.
- Avoid unbounded searches and strategy proliferation; use only bounded, predeclared rule families.
- Run long computations with `nohup`, a PID file, and a log file so they survive SSH disconnects.
