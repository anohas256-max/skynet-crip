# V28A L2 source / implementation feasibility

**V28A_DECISION=STOP_SOURCE_OR_IMPLEMENTATION_INVALID**

Probe-only bounded stop: confirmed bookDepth schema is ('timestamp', 'percentage', 'depth', 'notional'); it has no executable bid/ask prices and no sequence field.
Self-tests: PASS (confirmed_headers, signed_aggressor_mapping, first_observation_no_interpolation, archive_cap).

```json
{
  "decision": "STOP_SOURCE_OR_IMPLEMENTATION_INVALID",
  "probe": [
    {
      "get_bytes": 520918,
      "head_bytes": 520918,
      "head_status": 200,
      "schema": {
        "bad_rows": 0,
        "depth_levels_per_snapshot": {
          "12": 2628
        },
        "duplicate_timestamp_percentage": 0,
        "first_ms": 1780272007000,
        "gap_count_over_10s": 2627,
        "has_bid_ask_prices": false,
        "has_sequence_field": false,
        "header": [
          "timestamp",
          "percentage",
          "depth",
          "notional"
        ],
        "last_ms": 1780358370000,
        "max_gap_ms": 240000,
        "snapshots": 2628
      },
      "url": "https://data.binance.vision/data/futures/um/daily/bookDepth/BTCUSDT/BTCUSDT-bookDepth-2026-06-01.zip"
    },
    {
      "get_bytes": 20035428,
      "head_bytes": 20035428,
      "head_status": 200,
      "schema": {
        "bad_rows": 0,
        "duplicate_agg_trade_id": 0,
        "first_ms": 1780272000093,
        "header": [
          "agg_trade_id",
          "price",
          "quantity",
          "first_trade_id",
          "last_trade_id",
          "transact_time",
          "is_buyer_maker"
        ],
        "last_ms": 1780358399294,
        "max_intertrade_gap_ms": 6234,
        "nonmonotonic_agg_trade_id": 0,
        "signed_flow_available": true
      },
      "url": "https://data.binance.vision/data/futures/um/daily/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2026-06-01.zip"
    }
  ],
  "reason": "bookDepth_schema_lacks_executable_bid_ask_prices_and_sequence",
  "replay_feasibility": {
    "forward_labels_1_5_15_60s": "POSSIBLE_FROM_AGGTRADES_ONLY",
    "sequence_gap_replay": "NO_BOOKDEPTH_HAS_NO_SEQUENCE",
    "signed_aggressive_trade_flow": "YES_FROM_is_buyer_maker",
    "spread": "NO_BOOKDEPTH_HAS_NO_BID_ASK_PRICES",
    "top_of_book_depth_imbalance": "PARTIAL_PERCENTAGE_BUCKETS_ONLY"
  },
  "self_tests": [
    "confirmed_headers",
    "signed_aggressor_mapping",
    "first_observation_no_interpolation",
    "archive_cap"
  ],
  "source": "official Binance Data Vision probes only"
}
```
