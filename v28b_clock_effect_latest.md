# V28B quarter-hour / clock-time effect audit

**V28B_DECISION=STOP_SOURCE_OR_IMPLEMENTATION_INVALID**

Reason: projected_full_raw_exceeds_2GB_cap. Official Data Vision only; no live Binance API.
Observed one-day five-symbol compressed raw=32,665,067 bytes; fixed 912-day projection=29,790,541,104; cap=2,000,000,000.
Self-tests: PASS (buyer_maker_sign, utc_boundary, cost, no_overlap, train_validation_split).

| symbol | official archive HEAD | compressed bytes |
|---|---:|---:|
| BTCUSDT | 200 | 10,064,410 |
| ETHUSDT | 200 | 7,130,159 |
| SOLUSDT | 200 | 12,474,691 |
| XRPUSDT | 200 | 1,569,243 |
| DOGEUSDT | 200 | 1,426,564 |

The article documents periodic activity and order-flow predictability, but does not establish a net-of-cost trading edge; V28B makes no such claim.

```json
{
  "days": 912,
  "decision": "STOP_SOURCE_OR_IMPLEMENTATION_INVALID",
  "no_pnl_or_signal_result": true,
  "observed_one_day_five_symbol_bytes": 32665067,
  "paper_methodology": {
    "aggtrades_observable": [
      "trade count",
      "notional volume",
      "absolute return",
      "signed aggressive notional flow",
      "volume-normalized imbalance",
      "first 10-second quarter-hour return"
    ],
    "methodology_used": [
      "aggregate trades into UTC calendar-time bins",
      "buyer-initiated = isBuyerMaker false; seller-initiated = true",
      "quarter-hour peak window is first 10 seconds at minutes 00/15/30/45",
      "separate periodic activity/volatility diagnostics from net-of-cost trading evidence"
    ],
    "not_observable_or_not_claimed": [
      "queue position",
      "spread",
      "algorithmic trader identity",
      "article's technical-indicator model",
      "a volatility burst as an edge"
    ],
    "url": "https://arxiv.org/html/2607.09426v1"
  },
  "probes": [
    {
      "compressed_bytes": 10064410,
      "status": 200,
      "symbol": "BTCUSDT",
      "url": "https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2024-01-01.zip"
    },
    {
      "compressed_bytes": 7130159,
      "status": 200,
      "symbol": "ETHUSDT",
      "url": "https://data.binance.vision/data/futures/um/daily/aggTrades/ETHUSDT/ETHUSDT-aggTrades-2024-01-01.zip"
    },
    {
      "compressed_bytes": 12474691,
      "status": 200,
      "symbol": "SOLUSDT",
      "url": "https://data.binance.vision/data/futures/um/daily/aggTrades/SOLUSDT/SOLUSDT-aggTrades-2024-01-01.zip"
    },
    {
      "compressed_bytes": 1569243,
      "status": 200,
      "symbol": "XRPUSDT",
      "url": "https://data.binance.vision/data/futures/um/daily/aggTrades/XRPUSDT/XRPUSDT-aggTrades-2024-01-01.zip"
    },
    {
      "compressed_bytes": 1426564,
      "status": 200,
      "symbol": "DOGEUSDT",
      "url": "https://data.binance.vision/data/futures/um/daily/aggTrades/DOGEUSDT/DOGEUSDT-aggTrades-2024-01-01.zip"
    }
  ],
  "projected_raw_bytes_from_observed_day": 29790541104,
  "raw_cap_bytes": 2000000000,
  "reason": "projected_full_raw_exceeds_2GB_cap",
  "self_tests": [
    "buyer_maker_sign",
    "utc_boundary",
    "cost",
    "no_overlap",
    "train_validation_split"
  ]
}
```
