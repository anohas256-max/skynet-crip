# V22 perpetual basis audit

**V22_BASIS_DECISION=STOP_NO_VALIDATION_EDGE**

Source/range: official Binance USD-M monthly executable klines, markPriceKlines, indexPriceKlines, and fundingRate archives; V21 parsed official executable/funding cache reused where present; 2022-01-01 through 2026-06-30 UTC.

Self-tests: PASS (basis_sign, opposite_side, funding_sign, timestamp_no_lookahead, entry_delay, exit_funding_boundary, cost_once, max_two_positions, pair_atomicity, final_gate).

Universe: BTCUSDT, ETHUSDT, DOGEUSDT, BNBUSDT, AVAXUSDT, ADAUSDT, ETCUSDT, LINKUSDT, BCHUSDT, DOTUSDT, ATOMUSDT.

Data-quality valid symbols: 11/11; invalid: none.

## Validation
- INSTANT_BASIS / HOLD_24H: positions=546 pairs=273 severe_pnl=$-34.38 PF=0.73 funding=$+0.65 price=$-2.26; delay severe PnL=$-35.80; pass=False; skips={'insufficient_lookback': 3, 'active_pair': 819}
- INSTANT_BASIS / HOLD_72H: positions=220 pairs=110 severe_pnl=$-17.56 PF=0.79 funding=$+0.41 price=$-4.76; delay severe PnL=$-20.06; pass=False; skips={'insufficient_lookback': 3, 'active_pair': 982}
- MEAN_24H_BASIS / HOLD_24H: positions=546 pairs=273 severe_pnl=$-33.42 PF=0.71 funding=$+0.88 price=$-1.55; delay severe PnL=$-34.48; pass=False; skips={'insufficient_lookback': 3, 'active_pair': 819}
- MEAN_24H_BASIS / HOLD_72H: positions=220 pairs=110 severe_pnl=$-8.91 PF=0.88 funding=$+0.97 price=$+3.33; delay severe PnL=$-11.15; pass=False; skips={'insufficient_lookback': 3, 'active_pair': 982}

## Full machine-readable report
```json
{
  "data_quality": {
    "ADAUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 3,
          "hours": 39336,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 15405316.340431437
    },
    "ATOMUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 3,
          "hours": 39336,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 8607843.091055779
    },
    "AVAXUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 10,
          "hours": 39072,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 16155312.821449012
    },
    "BCHUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 3,
          "hours": 39336,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 10414619.857423626
    },
    "BNBUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 9,
          "hours": 39096,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 20295079.20360875
    },
    "BTCUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 9,
          "hours": 39096,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 547939922.6315746
    },
    "DOGEUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 3,
          "hours": 39336,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 28415051.577877626
    },
    "DOTUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 8,
          "hours": 39168,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 9509519.776745472
    },
    "ETCUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 3,
          "hours": 39336,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 14600213.201592525
    },
    "ETHUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 3,
          "hours": 39336,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 288725365.8815376
    },
    "LINKUSDT": {
      "funding": {
        "duplicates": 0,
        "first": "2022-01-01T00:00Z",
        "last": "2026-06-30T16:00Z",
        "missing_intervals_over_24h": 0,
        "settlements": 4926
      },
      "sources": [
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 0,
          "hours": 39408,
          "kind": "exec",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 4,
          "hours": 39312,
          "kind": "mark",
          "last": "2026-06-30T23:00Z"
        },
        {
          "bad_timestamp": 0,
          "coverage": true,
          "duplicates": 0,
          "first": "2022-01-01T00:00Z",
          "gaps": 5,
          "hours": 39288,
          "kind": "index",
          "last": "2026-06-30T23:00Z"
        }
      ],
      "train_average_hourly_volume_usdt": 13272611.019207502
    }
  },
  "decision": "STOP_NO_VALIDATION_EDGE",
  "final": null,
  "final_opened": false,
  "frozen_candidate": null,
  "range": "2022-01-01 through 2026-06-30 UTC",
  "self_tests": "PASS",
  "source": "official Binance USD-M monthly executable klines, markPriceKlines, indexPriceKlines, and fundingRate archives; V21 parsed official executable/funding cache reused where present",
  "universe": [
    "BTCUSDT",
    "ETHUSDT",
    "DOGEUSDT",
    "BNBUSDT",
    "AVAXUSDT",
    "ADAUSDT",
    "ETCUSDT",
    "LINKUSDT",
    "BCHUSDT",
    "DOTUSDT",
    "ATOMUSDT"
  ],
  "validation": [
    {
      "base": {
        "avg": -0.04615789261499193,
        "best_symbol_share": 0.357199157258444,
        "funding": 0.64992252,
        "leave_best_pair": -27.89723836083344,
        "leave_best_symbol": -27.45881408396098,
        "leave_best_trade": -28.990792279279948,
        "long_pf": 1.0620428616812643,
        "long_pnl": 3.4467549007468063,
        "mdd": -27.233539249644064,
        "pairs": 273,
        "pf": 0.7898395379776644,
        "pnl": -25.202209367785596,
        "positions": 546,
        "price": -2.2649318877855924,
        "short_pf": 0.5548947724362736,
        "short_pnl": -28.648964268532403,
        "symbols": 11,
        "wr": 0.4542124542124542
      },
      "delay_severe": {
        "avg": -0.06555869016097085,
        "best_symbol_share": 0.7296244654922456,
        "funding": 0.64992252,
        "leave_best_pair": -38.161841088517214,
        "leave_best_symbol": -38.118610076171024,
        "leave_best_trade": -38.80902398198676,
        "long_pf": 0.9105366110420268,
        "long_pnl": -5.387373660041503,
        "mdd": -36.051729533958095,
        "pairs": 273,
        "pf": 0.7145606552048865,
        "pnl": -35.79504482789009,
        "positions": 546,
        "price": -3.68496734789009,
        "short_pf": 0.533514345529146,
        "short_pnl": -30.407671167848587,
        "symbols": 11,
        "wr": 0.4267399267399267
      },
      "hold_hours": 24,
      "quarters": [
        -10.733790301480532,
        -5.830301181143747,
        -14.61480819337444,
        -3.196109691786875
      ],
      "severe": {
        "avg": -0.06295789261499193,
        "best_symbol_share": 0.3851656606203886,
        "funding": 0.64992252,
        "leave_best_pair": -37.036438360833436,
        "leave_best_symbol": -36.16121408396098,
        "leave_best_trade": -38.14679227927994,
        "long_pf": 0.9803818917475294,
        "long_pnl": -1.1396450992531924,
        "mdd": -34.84393924964411,
        "pairs": 273,
        "pf": 0.7251308971962704,
        "pnl": -34.375009367785594,
        "positions": 546,
        "price": -2.2649318877855924,
        "short_pf": 0.5037132966858345,
        "short_pnl": -33.2353642685324,
        "symbols": 11,
        "wr": 0.43223443223443225
      },
      "signal": "INSTANT_BASIS",
      "skips": {
        "active_pair": 819,
        "insufficient_lookback": 3
      },
      "validation_pass": false
    },
    {
      "base": {
        "avg": -0.06300392413732699,
        "best_symbol_share": 0.5253620032746054,
        "funding": 0.40656324,
        "leave_best_pair": -16.445174864088347,
        "leave_best_symbol": -20.94394255943749,
        "leave_best_trade": -19.068141180811697,
        "long_pf": 1.2090239426962186,
        "long_pnl": 7.487852333512736,
        "mdd": -16.014581145783577,
        "pairs": 110,
        "pf": 0.8286377093900109,
        "pnl": -13.860863310211936,
        "positions": 220,
        "price": -4.763426550211937,
        "short_pf": 0.5262512284075407,
        "short_pnl": -21.348715643724674,
        "symbols": 11,
        "wr": 0.4954545454545455
      },
      "delay_severe": {
        "avg": -0.0912043473664006,
        "best_symbol_share": 0.42359883566047646,
        "funding": 0.40656324,
        "leave_best_pair": -22.249611425163856,
        "leave_best_symbol": -23.746193665883414,
        "leave_best_trade": -24.15084626290082,
        "long_pf": 1.0338941700052726,
        "long_pnl": 1.25388996139089,
        "mdd": -21.351600364641307,
        "pairs": 110,
        "pf": 0.7583062472394612,
        "pnl": -20.06495642060813,
        "positions": 220,
        "price": -7.271519660608129,
        "short_pf": 0.5367868284295075,
        "short_pnl": -21.31884638199902,
        "symbols": 11,
        "wr": 0.4636363636363636
      },
      "hold_hours": 72,
      "quarters": [
        -3.048844320755686,
        -5.554011978412077,
        -5.53377346030494,
        -3.420233550739236
      ],
      "severe": {
        "avg": -0.079803924137327,
        "best_symbol_share": 0.5580385361717368,
        "funding": 0.40656324,
        "leave_best_pair": -20.10757486408835,
        "leave_best_symbol": -24.236742559437495,
        "leave_best_trade": -22.7473411808117,
        "long_pf": 1.153698214689185,
        "long_pnl": 5.639852333512734,
        "mdd": -19.54258114578358,
        "pairs": 110,
        "pf": 0.7878927152444929,
        "pnl": -17.556863310211938,
        "positions": 220,
        "price": -4.763426550211937,
        "short_pf": 0.49659008371724955,
        "short_pnl": -23.196715643724673,
        "symbols": 11,
        "wr": 0.4863636363636364
      },
      "signal": "INSTANT_BASIS",
      "skips": {
        "active_pair": 982,
        "insufficient_lookback": 3
      },
      "validation_pass": false
    },
    {
      "base": {
        "avg": -0.04441637886379611,
        "best_symbol_share": 0.4937030882482064,
        "funding": 0.88141488,
        "leave_best_pair": -26.08349894394593,
        "leave_best_symbol": -27.366429514852268,
        "leave_best_trade": -26.54786604618577,
        "long_pf": 1.005521151274709,
        "long_pnl": 0.2981794957470563,
        "mdd": -26.403433848908847,
        "pairs": 273,
        "pf": 0.7773585935382472,
        "pnl": -24.251342859632675,
        "positions": 546,
        "price": -1.5455577396326707,
        "short_pf": 0.5529851947386275,
        "short_pnl": -24.549522355379732,
        "symbols": 11,
        "wr": 0.43956043956043955
      },
      "delay_severe": {
        "avg": -0.06315025079536758,
        "best_symbol_share": 0.4216920559162925,
        "funding": 0.88141488,
        "leave_best_pair": -36.16962178817118,
        "leave_best_symbol": -36.62590221774833,
        "leave_best_trade": -36.7131040258212,
        "long_pf": 0.8911062340831133,
        "long_pnl": -6.285166604336807,
        "mdd": -36.368983435034586,
        "pairs": 273,
        "pf": 0.7047222678777509,
        "pnl": -34.4800369342707,
        "positions": 546,
        "price": -2.6014518142706966,
        "short_pf": 0.5225514533967612,
        "short_pnl": -28.19487032993389,
        "symbols": 11,
        "wr": 0.43223443223443225
      },
      "hold_hours": 24,
      "quarters": [
        -10.784657400348564,
        -3.906006477517086,
        -12.550324289898418,
        -6.183154691868603
      ],
      "severe": {
        "avg": -0.061216378863796106,
        "best_symbol_share": 0.5486789474718691,
        "funding": 0.88141488,
        "leave_best_pair": -35.22269894394593,
        "leave_best_symbol": -34.77522951485227,
        "leave_best_trade": -35.70386604618577,
        "long_pf": 0.924153769277661,
        "long_pnl": -4.288220504252942,
        "mdd": -35.35783384890885,
        "pairs": 273,
        "pf": 0.7073391828564691,
        "pnl": -33.424142859632674,
        "positions": 546,
        "price": -1.5455577396326707,
        "short_pf": 0.49477704760958097,
        "short_pnl": -29.13592235537973,
        "symbols": 11,
        "wr": 0.4175824175824176
      },
      "signal": "MEAN_24H_BASIS",
      "skips": {
        "active_pair": 819,
        "insufficient_lookback": 3
      },
      "validation_pass": false
    },
    {
      "base": {
        "avg": -0.023687060582000534,
        "best_symbol_share": 0.6484768782484335,
        "funding": 0.96520032,
        "leave_best_pair": -7.287679191289974,
        "leave_best_symbol": -17.576187671148368,
        "leave_best_trade": -8.83189515225332,
        "long_pf": 1.2181170246956938,
        "long_pnl": 7.795915203001288,
        "mdd": -10.413311743796193,
        "pairs": 110,
        "pf": 0.9260887166920161,
        "pnl": -5.211153328040117,
        "positions": 220,
        "price": 3.3276463519598836,
        "short_pf": 0.625842581080169,
        "short_pnl": -13.007068531041405,
        "symbols": 11,
        "wr": 0.4636363636363636
      },
      "delay_severe": {
        "avg": -0.050699116757002366,
        "best_symbol_share": 0.7536126554748217,
        "funding": 0.96520032,
        "leave_best_pair": -13.338460691096248,
        "leave_best_symbol": -21.41445124837973,
        "leave_best_trade": -14.613100617345529,
        "long_pf": 1.103611898131235,
        "long_pnl": 3.7460832861871918,
        "mdd": -12.698140669874924,
        "pairs": 110,
        "pf": 0.8441956523194907,
        "pnl": -11.15380568654052,
        "positions": 220,
        "price": 1.0809939934594799,
        "short_pf": 0.5794981431244651,
        "short_pnl": -14.899888972727712,
        "symbols": 11,
        "wr": 0.4318181818181818
      },
      "hold_hours": 72,
      "quarters": [
        -2.4471368140529206,
        -2.479322829847269,
        -3.0743039425162513,
        -0.906389741623677
      ],
      "severe": {
        "avg": -0.040487060582000536,
        "best_symbol_share": 0.664450083238023,
        "funding": 0.96520032,
        "leave_best_pair": -10.950079191289975,
        "leave_best_symbol": -20.549787671148373,
        "leave_best_trade": -12.511095152253322,
        "long_pf": 1.162006393234254,
        "long_pnl": 5.947915203001287,
        "mdd": -11.48851174379619,
        "pairs": 110,
        "pf": 0.8771695576502686,
        "pnl": -8.907153328040119,
        "positions": 220,
        "price": 3.3276463519598836,
        "short_pf": 0.5850744432997612,
        "short_pnl": -14.855068531041406,
        "symbols": 11,
        "wr": 0.45
      },
      "signal": "MEAN_24H_BASIS",
      "skips": {
        "active_pair": 982,
        "insufficient_lookback": 3
      },
      "validation_pass": false
    }
  ],
  "validation_passed": 0
}
```
