# V24 repaired Binance launch momentum audit

**V24_DECISION=STOP_DATA_UNAVAILABLE**

CMS source quality: requests=7/30, minimum spacing=3 seconds, source_stop=none.
Exact official launch events=0; continuous executable 1m windows=0.

## Validation metrics
- 15m/24h: base={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; severe={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; quarters=[0, 0, 0, 0]; delayed={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; pass=False; final=None
- 15m/72h: base={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; severe={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; quarters=[0, 0, 0, 0]; delayed={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; pass=False; final=None
- 60m/24h: base={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; severe={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; quarters=[0, 0, 0, 0]; delayed={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; pass=False; final=None
- 60m/72h: base={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; severe={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; quarters=[0, 0, 0, 0]; delayed={'trades': 0, 'pnl': 0, 'pf': 0, 'leave_best_event': 0, 'price': 0, 'funding': 0}; pass=False; final=None

```json
{
  "cms_limit": 30,
  "cms_requests": 7,
  "continuous_events": 0,
  "decision": "STOP_DATA_UNAVAILABLE",
  "exact_events": 0,
  "exclusions": [
    {
      "launch": null,
      "reason": "excluded_article_http_202",
      "symbol": null,
      "url": "https://www.binance.com/en/support/announcement/6fe9f6dc91544df88dc24ad41211feff"
    },
    {
      "launch": null,
      "reason": "excluded_article_http_202",
      "symbol": null,
      "url": "https://www.binance.com/en/support/announcement/98d978c5630041c49a6bd317daa791e8"
    },
    {
      "launch": null,
      "reason": "excluded_article_http_202",
      "symbol": null,
      "url": "https://www.binance.com/en/support/announcement/a444dd2f67da43e0bafdd730fddc3887"
    },
    {
      "launch": null,
      "reason": "excluded_article_http_202",
      "symbol": null,
      "url": "https://www.binance.com/en/support/announcement/a6b7d5a8a14a44c1b6a6a34813c6d93f"
    },
    {
      "launch": null,
      "reason": "excluded_article_http_202",
      "symbol": null,
      "url": "https://www.binance.com/en/support/announcement/7fa4e8b3ced94b4c8c189a4593dbce9b"
    }
  ],
  "final_opened": false,
  "requests": [
    {
      "bytes": 31766,
      "status": 200,
      "url": "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo=1&pageSize=20"
    },
    {
      "bytes": 31897,
      "status": 200,
      "url": "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo=2&pageSize=20"
    },
    {
      "bytes": 0,
      "status": 202,
      "url": "https://www.binance.com/en/support/announcement/6fe9f6dc91544df88dc24ad41211feff"
    },
    {
      "bytes": 0,
      "status": 202,
      "url": "https://www.binance.com/en/support/announcement/98d978c5630041c49a6bd317daa791e8"
    },
    {
      "bytes": 0,
      "status": 202,
      "url": "https://www.binance.com/en/support/announcement/a444dd2f67da43e0bafdd730fddc3887"
    },
    {
      "bytes": 0,
      "status": 202,
      "url": "https://www.binance.com/en/support/announcement/a6b7d5a8a14a44c1b6a6a34813c6d93f"
    },
    {
      "bytes": 0,
      "status": 202,
      "url": "https://www.binance.com/en/support/announcement/7fa4e8b3ced94b4c8c189a4593dbce9b"
    }
  ],
  "results": [
    {
      "hold_hours": 24,
      "signal_minutes": 15,
      "validation_base": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      },
      "validation_delayed_5m": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      },
      "validation_pass": false,
      "validation_quarters": [
        0,
        0,
        0,
        0
      ],
      "validation_severe": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      }
    },
    {
      "hold_hours": 72,
      "signal_minutes": 15,
      "validation_base": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      },
      "validation_delayed_5m": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      },
      "validation_pass": false,
      "validation_quarters": [
        0,
        0,
        0,
        0
      ],
      "validation_severe": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      }
    },
    {
      "hold_hours": 24,
      "signal_minutes": 60,
      "validation_base": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      },
      "validation_delayed_5m": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      },
      "validation_pass": false,
      "validation_quarters": [
        0,
        0,
        0,
        0
      ],
      "validation_severe": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      }
    },
    {
      "hold_hours": 72,
      "signal_minutes": 60,
      "validation_base": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      },
      "validation_delayed_5m": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      },
      "validation_pass": false,
      "validation_quarters": [
        0,
        0,
        0,
        0
      ],
      "validation_severe": {
        "funding": 0,
        "leave_best_event": 0,
        "pf": 0,
        "pnl": 0,
        "price": 0,
        "trades": 0
      }
    }
  ],
  "self_tests": [
    "launch_time_parsing",
    "no_lookahead",
    "entry_timing",
    "funding_sign_boundary",
    "no_overlap",
    "cost_arithmetic",
    "final_gate"
  ],
  "source_stop": null
}
```
