# V27 V18 offline microstructure replay

**V27_DECISION=STOP_NO_VALIDATION_EDGE**

Source: read-only `/root/skynet/data/v18_micro_paths.sqlite3`; rows=267076; range=2026-06-17T11:09:00Z--2026-07-18T17:42:34Z; chronological 70/30 split=2026-07-09T08:32:30Z.
Self-tests: PASS (parser_path_json, no_overlap, direction_sign, cost, chronological_split).

## Fixed validation configurations
- continuation / confirm / 60s: {'trades': 11545, 'severe_pnl': -46.674061799999336, 'pf': 0.1112865521622023, 'win_rate': 0.0887830229536596, 'gross_pnl': -0.49406179999999683}; leave_best_symbol=-46.730345; pass=False; skips={'structure_not_selected': 76090, 'symbol_cooldown': 3646, 'missing_horizon_path': 19, 'invalid_path_json': 0}
- continuation / confirm / 300s: {'trades': 11538, 'severe_pnl': -47.79456749999989, 'pf': 0.26843332242823176, 'win_rate': 0.16970012133818685, 'gross_pnl': -1.6425674999999946}; leave_best_symbol=-47.956901; pass=False; skips={'structure_not_selected': 76000, 'symbol_cooldown': 3645, 'missing_horizon_path': 117, 'invalid_path_json': 0}
- continuation / contradict / 60s: {'trades': 12339, 'severe_pnl': -51.909292399999146, 'pf': 0.1049250443910482, 'win_rate': 0.07593808250263392, 'gross_pnl': -2.5532923999999957}; leave_best_symbol=-52.034775; pass=False; skips={'structure_not_selected': 74982, 'symbol_cooldown': 3960, 'missing_horizon_path': 19, 'invalid_path_json': 0}
- continuation / contradict / 300s: {'trades': 12324, 'severe_pnl': -52.70675089999963, 'pf': 0.2502053231815633, 'win_rate': 0.15546900357026938, 'gross_pnl': -3.410750899999978}; leave_best_symbol=-53.006439; pass=False; skips={'structure_not_selected': 74905, 'symbol_cooldown': 3954, 'missing_horizon_path': 117, 'invalid_path_json': 0}
- fade / confirm / 60s: {'trades': 11545, 'severe_pnl': -45.685938199999384, 'pf': 0.09713055762559883, 'win_rate': 0.09181463837158943, 'gross_pnl': 0.49406179999999683}; leave_best_symbol=-45.721707; pass=False; skips={'structure_not_selected': 76090, 'symbol_cooldown': 3646, 'missing_horizon_path': 19, 'invalid_path_json': 0}
- fade / confirm / 300s: {'trades': 11538, 'severe_pnl': -44.509432499999946, 'pf': 0.27277010187263184, 'win_rate': 0.19457444964465245, 'gross_pnl': 1.6425674999999946}; leave_best_symbol=-44.603263; pass=False; skips={'structure_not_selected': 76000, 'symbol_cooldown': 3645, 'missing_horizon_path': 117, 'invalid_path_json': 0}
- fade / contradict / 60s: {'trades': 12339, 'severe_pnl': -46.80270759999924, 'pf': 0.10929535699086998, 'win_rate': 0.09222789529135263, 'gross_pnl': 2.5532923999999957}; leave_best_symbol=-46.827244; pass=False; skips={'structure_not_selected': 74982, 'symbol_cooldown': 3960, 'missing_horizon_path': 19, 'invalid_path_json': 0}
- fade / contradict / 300s: {'trades': 12324, 'severe_pnl': -45.88524909999991, 'pf': 0.279916956051855, 'win_rate': 0.19133398247322297, 'gross_pnl': 3.410750899999978}; leave_best_symbol=-46.009652; pass=False; skips={'structure_not_selected': 74905, 'symbol_cooldown': 3954, 'missing_horizon_path': 117, 'invalid_path_json': 0}

## Full compact audit
```json
{
  "configs": [
    {
      "direction": "continuation",
      "horizon_seconds": 60,
      "leave_best_symbol": -46.73034549999934,
      "structure": "confirm",
      "validation": {
        "gross_pnl": -0.49406179999999683,
        "pf": 0.1112865521622023,
        "severe_pnl": -46.674061799999336,
        "trades": 11545,
        "win_rate": 0.0887830229536596
      },
      "validation_by_symbol": {
        "0G_USDT": {
          "gross_pnl": 0.0026093000000000006,
          "pf": 0.15196648015842276,
          "severe_pnl": -0.08539070000000001,
          "trades": 22,
          "win_rate": 0.18181818181818182
        },
        "1000000BABYDOGE_USDT": {
          "gross_pnl": -0.006099899999999998,
          "pf": 0.0,
          "severe_pnl": -0.0260999,
          "trades": 5,
          "win_rate": 0.0
        },
        "1000BONK_USDT": {
          "gross_pnl": -0.022657700000000006,
          "pf": 0.018547484092260997,
          "severe_pnl": -0.21465769999999998,
          "trades": 48,
          "win_rate": 0.041666666666666664
        },
        "1INCH_USDT": {
          "gross_pnl": -0.0001337,
          "pf": 0.0,
          "severe_pnl": -0.0041337,
          "trades": 1,
          "win_rate": 0.0
        },
        "2Z_USDT": {
          "gross_pnl": -0.043768600000000005,
          "pf": 0.0,
          "severe_pnl": -0.051768600000000005,
          "trades": 2,
          "win_rate": 0.0
        },
        "4_USDT": {
          "gross_pnl": -0.014276599999999999,
          "pf": 0.0,
          "severe_pnl": -0.0382766,
          "trades": 6,
          "win_rate": 0.0
        },
        "AAVE_USDT": {
          "gross_pnl": 0.012892699999999998,
          "pf": 0.0038700172564493326,
          "severe_pnl": -0.15510730000000003,
          "trades": 42,
          "win_rate": 0.023809523809523808
        },
        "ACE_USDT": {
          "gross_pnl": 0.060283699999999996,
          "pf": 999,
          "severe_pnl": 0.05628369999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "ACT_USDT": {
          "gross_pnl": 0.00351,
          "pf": 0.0,
          "severe_pnl": -0.008490000000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "ACU_USDT": {
          "gross_pnl": 0.0029502,
          "pf": 0.0,
          "severe_pnl": -0.0130498,
          "trades": 4,
          "win_rate": 0.0
        },
        "ADA_USDT": {
          "gross_pnl": -0.012154900000000007,
          "pf": 0.014165724158507897,
          "severe_pnl": -0.2841549,
          "trades": 68,
          "win_rate": 0.014705882352941176
        },
        "AERGO_USDT": {
          "gross_pnl": 0.0018270999999999995,
          "pf": 0.09351957358233096,
          "severe_pnl": -0.0261729,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "AERO_USDT": {
          "gross_pnl": -0.004884699999999996,
          "pf": 0.01628908142149347,
          "severe_pnl": -0.17688469999999998,
          "trades": 43,
          "win_rate": 0.046511627906976744
        },
        "AEVO_USDT": {
          "gross_pnl": 0.0005249,
          "pf": 0.0,
          "severe_pnl": -0.0034751,
          "trades": 1,
          "win_rate": 0.0
        },
        "AGI_USDT": {
          "gross_pnl": -0.005363699999999999,
          "pf": 0.0,
          "severe_pnl": -0.0173637,
          "trades": 3,
          "win_rate": 0.0
        },
        "AGLD_USDT": {
          "gross_pnl": 0.024051499999999996,
          "pf": 0.4957126028242217,
          "severe_pnl": -0.019948500000000004,
          "trades": 11,
          "win_rate": 0.5454545454545454
        },
        "AGT_USDT": {
          "gross_pnl": 0.0021845,
          "pf": 0.0,
          "severe_pnl": -0.0058155,
          "trades": 2,
          "win_rate": 0.0
        },
        "AIGENSYN_USDT": {
          "gross_pnl": -0.009084499999999999,
          "pf": 0.0,
          "severe_pnl": -0.08908450000000001,
          "trades": 20,
          "win_rate": 0.0
        },
        "AIOT_USDT": {
          "gross_pnl": 0.0031781000000000127,
          "pf": 0.27950076730948903,
          "severe_pnl": -0.17282190000000003,
          "trades": 44,
          "win_rate": 0.20454545454545456
        },
        "AIOZ_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "AIO_USDT": {
          "gross_pnl": -0.0049713,
          "pf": 0.0,
          "severe_pnl": -0.0129713,
          "trades": 2,
          "win_rate": 0.0
        },
        "AKE_USDT": {
          "gross_pnl": 0.019655699999999977,
          "pf": 0.6175341682435013,
          "severe_pnl": -0.2683443,
          "trades": 72,
          "win_rate": 0.3472222222222222
        },
        "AKT_USDT": {
          "gross_pnl": 0.0005260999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0034739000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "ALCH_USDT": {
          "gross_pnl": -0.06868509999999999,
          "pf": 0.03382582827783397,
          "severe_pnl": -0.2006851,
          "trades": 33,
          "win_rate": 0.09090909090909091
        },
        "ALGO_USDT": {
          "gross_pnl": -0.010796000000000002,
          "pf": 0.0,
          "severe_pnl": -0.17079600000000006,
          "trades": 40,
          "win_rate": 0.0
        },
        "ALLO_USDT": {
          "gross_pnl": 0.08319759999999998,
          "pf": 0.14552957799180313,
          "severe_pnl": -0.6088023999999997,
          "trades": 173,
          "win_rate": 0.1791907514450867
        },
        "ALPINE_USDT": {
          "gross_pnl": -0.0068451,
          "pf": 0.0,
          "severe_pnl": -0.0108451,
          "trades": 1,
          "win_rate": 0.0
        },
        "ALT_USDT": {
          "gross_pnl": -0.0076839000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0396839,
          "trades": 8,
          "win_rate": 0.0
        },
        "ANKR_USDT": {
          "gross_pnl": 0.0051752,
          "pf": 0.36026287328538414,
          "severe_pnl": -0.0108248,
          "trades": 4,
          "win_rate": 0.25
        },
        "ANSEM_USDT": {
          "gross_pnl": -0.04151099999999998,
          "pf": 0.27568167001530974,
          "severe_pnl": -0.629511,
          "trades": 147,
          "win_rate": 0.2585034013605442
        },
        "ANTHROPIC_USDT": {
          "gross_pnl": -0.0028715000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0588715,
          "trades": 14,
          "win_rate": 0.0
        },
        "APE_USDT": {
          "gross_pnl": -0.012606299999999997,
          "pf": 0.0,
          "severe_pnl": -0.2246063000000001,
          "trades": 53,
          "win_rate": 0.0
        },
        "APR_USDT": {
          "gross_pnl": 0.0028382000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0011617999999999997,
          "trades": 1,
          "win_rate": 0.0
        },
        "APT_USDT": {
          "gross_pnl": -0.0154725,
          "pf": 0.0,
          "severe_pnl": -0.2834725000000001,
          "trades": 67,
          "win_rate": 0.0
        },
        "ARB_USDT": {
          "gross_pnl": 0.06351879999999999,
          "pf": 0.024255393737949212,
          "severe_pnl": -0.5204812,
          "trades": 146,
          "win_rate": 0.0547945205479452
        },
        "ARCSOL_USDT": {
          "gross_pnl": -0.0080153,
          "pf": 0.0,
          "severe_pnl": -0.0160153,
          "trades": 2,
          "win_rate": 0.0
        },
        "ARKK_USDT": {
          "gross_pnl": -0.011346699999999998,
          "pf": 0.0,
          "severe_pnl": -0.019346699999999998,
          "trades": 2,
          "win_rate": 0.0
        },
        "ARKM_USDT": {
          "gross_pnl": 0.0009834999999999993,
          "pf": 0.0,
          "severe_pnl": -0.06301650000000002,
          "trades": 16,
          "win_rate": 0.0
        },
        "ARX_USDT": {
          "gross_pnl": 0.001978499999999997,
          "pf": 0.04788816954808457,
          "severe_pnl": -0.15002150000000006,
          "trades": 38,
          "win_rate": 0.10526315789473684
        },
        "AR_USDT": {
          "gross_pnl": -0.0035207000000000003,
          "pf": 0.0,
          "severe_pnl": -0.039520700000000006,
          "trades": 9,
          "win_rate": 0.0
        },
        "ASTEROID_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "ASTER_USDT": {
          "gross_pnl": -0.010347599999999998,
          "pf": 0.00040452352116483145,
          "severe_pnl": -0.16234760000000004,
          "trades": 38,
          "win_rate": 0.02631578947368421
        },
        "ATH_USDT": {
          "gross_pnl": -0.007964699999999998,
          "pf": 0.0,
          "severe_pnl": -0.0159647,
          "trades": 2,
          "win_rate": 0.0
        },
        "ATOM_USDT": {
          "gross_pnl": -0.002076399999999999,
          "pf": 0.0,
          "severe_pnl": -0.15807640000000006,
          "trades": 39,
          "win_rate": 0.0
        },
        "AVAAI_USDT": {
          "gross_pnl": 0.0229756,
          "pf": 2.4228949086161884,
          "severe_pnl": 0.0069756,
          "trades": 4,
          "win_rate": 0.5
        },
        "AVAX_USDT": {
          "gross_pnl": 0.0020798,
          "pf": 0.0,
          "severe_pnl": -0.057920200000000005,
          "trades": 15,
          "win_rate": 0.0
        },
        "AVNT_USDT": {
          "gross_pnl": -0.012328799999999997,
          "pf": 0.0,
          "severe_pnl": -0.07632879999999999,
          "trades": 16,
          "win_rate": 0.0
        },
        "AWE_USDT": {
          "gross_pnl": 0.0118921,
          "pf": 0.9877528319447911,
          "severe_pnl": -0.00010790000000000018,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "AXL_USDT": {
          "gross_pnl": -0.0020969,
          "pf": 0.0,
          "severe_pnl": -0.006096900000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "AXS_USDT": {
          "gross_pnl": -0.009121200000000001,
          "pf": 0.0,
          "severe_pnl": -0.061121199999999994,
          "trades": 13,
          "win_rate": 0.0
        },
        "A_USDT": {
          "gross_pnl": -0.0062028,
          "pf": 0.0,
          "severe_pnl": -0.022202799999999998,
          "trades": 4,
          "win_rate": 0.0
        },
        "B2_USDT": {
          "gross_pnl": -0.012146,
          "pf": 0.0,
          "severe_pnl": -0.024146,
          "trades": 3,
          "win_rate": 0.0
        },
        "B3_USDT": {
          "gross_pnl": -0.029503999999999996,
          "pf": 0.1785909996626786,
          "severe_pnl": -0.06550399999999999,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "BABY_USDT": {
          "gross_pnl": -0.0037097999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0277098,
          "trades": 6,
          "win_rate": 0.0
        },
        "BANANAS31_USDT": {
          "gross_pnl": 0.0037824000000000004,
          "pf": 0.002585296580854257,
          "severe_pnl": -0.0082176,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "BANANA_USDT": {
          "gross_pnl": 0.0029471000000000002,
          "pf": 0.0,
          "severe_pnl": -0.005052900000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "BAND_USDT": {
          "gross_pnl": -0.0135884,
          "pf": 0.0,
          "severe_pnl": -0.0255884,
          "trades": 3,
          "win_rate": 0.0
        },
        "BANK_USDT": {
          "gross_pnl": 0.1769879000000001,
          "pf": 0.6380031806074088,
          "severe_pnl": -0.13901210000000008,
          "trades": 79,
          "win_rate": 0.35443037974683544
        },
        "BAN_USDT": {
          "gross_pnl": 0.00022579999999999953,
          "pf": 0.0,
          "severe_pnl": -0.015774200000000002,
          "trades": 4,
          "win_rate": 0.0
        },
        "BASED_USDT": {
          "gross_pnl": -0.021379899999999997,
          "pf": 0.0010813809086068558,
          "severe_pnl": -0.12137990000000001,
          "trades": 25,
          "win_rate": 0.04
        },
        "BAS_USDT": {
          "gross_pnl": 0.0046061999999999995,
          "pf": 0.0,
          "severe_pnl": -0.007393800000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "BAT_USDT": {
          "gross_pnl": -0.0012002000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0332002,
          "trades": 8,
          "win_rate": 0.0
        },
        "BCH_USDT": {
          "gross_pnl": -0.007056999999999997,
          "pf": 0.0030169271550135037,
          "severe_pnl": -0.239057,
          "trades": 58,
          "win_rate": 0.017241379310344827
        },
        "BEAT_USDT": {
          "gross_pnl": 0.15903650000000005,
          "pf": 0.11994257890121846,
          "severe_pnl": -0.6209635000000001,
          "trades": 195,
          "win_rate": 0.1282051282051282
        },
        "BERA_USDT": {
          "gross_pnl": -0.0010447,
          "pf": 0.0,
          "severe_pnl": -0.0170447,
          "trades": 4,
          "win_rate": 0.0
        },
        "BIANRENSHENG_USDT": {
          "gross_pnl": 0.0011056,
          "pf": 0.0,
          "severe_pnl": -0.010894399999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "BICO_USDT": {
          "gross_pnl": -0.0023202000000000006,
          "pf": 0.0,
          "severe_pnl": -0.0423202,
          "trades": 10,
          "win_rate": 0.0
        },
        "BIGTIME_USDT": {
          "gross_pnl": 0.0002939,
          "pf": 0.0,
          "severe_pnl": -0.0037061,
          "trades": 1,
          "win_rate": 0.0
        },
        "BILL_USDT": {
          "gross_pnl": 0.11282130000000004,
          "pf": 0.19389842227211984,
          "severe_pnl": -0.5311787000000003,
          "trades": 161,
          "win_rate": 0.14906832298136646
        },
        "BIO_USDT": {
          "gross_pnl": -0.0017724000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0057724000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "BLAST_USDT": {
          "gross_pnl": -0.11356719999999998,
          "pf": 0.16183251926490677,
          "severe_pnl": -0.22956720000000003,
          "trades": 29,
          "win_rate": 0.3448275862068966
        },
        "BLEND_USDT": {
          "gross_pnl": -0.014409700000000001,
          "pf": 0.0,
          "severe_pnl": -0.04240970000000001,
          "trades": 7,
          "win_rate": 0.0
        },
        "BLESS_USDT": {
          "gross_pnl": -0.044799999999999986,
          "pf": 0.007623988388177596,
          "severe_pnl": -0.23280000000000003,
          "trades": 47,
          "win_rate": 0.0425531914893617
        },
        "BLUAI_USDT": {
          "gross_pnl": 0.0812524,
          "pf": 2.5491111557157433,
          "severe_pnl": 0.05325239999999999,
          "trades": 7,
          "win_rate": 0.5714285714285714
        },
        "BLUR_USDT": {
          "gross_pnl": -0.0024798999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0144799,
          "trades": 3,
          "win_rate": 0.0
        },
        "BNB_USDT": {
          "gross_pnl": -0.0009035999999999996,
          "pf": 0.0,
          "severe_pnl": -0.09290360000000003,
          "trades": 23,
          "win_rate": 0.0
        },
        "BRETT_USDT": {
          "gross_pnl": -0.04018630000000001,
          "pf": 0.0063071426729430615,
          "severe_pnl": -0.10018630000000002,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "BREV_USDT": {
          "gross_pnl": -0.0112306,
          "pf": 0.0,
          "severe_pnl": -0.0312306,
          "trades": 5,
          "win_rate": 0.0
        },
        "BSB_USDT": {
          "gross_pnl": -0.04983050000000004,
          "pf": 0.12907400530562965,
          "severe_pnl": -0.6658304999999997,
          "trades": 154,
          "win_rate": 0.14285714285714285
        },
        "BSV_USDT": {
          "gross_pnl": 0.004123399999999999,
          "pf": 0.08608831025852008,
          "severe_pnl": -0.0318766,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "BTW_USDT": {
          "gross_pnl": 0.003041500000000005,
          "pf": 0.12865146960437268,
          "severe_pnl": -0.1449585,
          "trades": 37,
          "win_rate": 0.10810810810810811
        },
        "BUILDONBOB_USDT": {
          "gross_pnl": -0.018845099999999997,
          "pf": 0.07034829049525006,
          "severe_pnl": -0.0308451,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "BULLA_USDT": {
          "gross_pnl": 0.040789399999999996,
          "pf": 0.49787335422930756,
          "severe_pnl": -0.0472106,
          "trades": 22,
          "win_rate": 0.4090909090909091
        },
        "CAKE_USDT": {
          "gross_pnl": -0.007701,
          "pf": 0.0,
          "severe_pnl": -0.043701000000000004,
          "trades": 9,
          "win_rate": 0.0
        },
        "CAP_USDT": {
          "gross_pnl": 0.014687299999999992,
          "pf": 0.16123388263733263,
          "severe_pnl": -0.18931270000000003,
          "trades": 51,
          "win_rate": 0.058823529411764705
        },
        "CARV_USDT": {
          "gross_pnl": -0.0092365,
          "pf": 0.0,
          "severe_pnl": -0.0132365,
          "trades": 1,
          "win_rate": 0.0
        },
        "CASHCAT_USDT": {
          "gross_pnl": -0.0914976,
          "pf": 0.17082335458332595,
          "severe_pnl": -0.1914976,
          "trades": 25,
          "win_rate": 0.24
        },
        "CATI_USDT": {
          "gross_pnl": -0.0026976,
          "pf": 0.0,
          "severe_pnl": -0.010697600000000002,
          "trades": 2,
          "win_rate": 0.0
        },
        "CC_USDT": {
          "gross_pnl": 0.0078279,
          "pf": 0.10070976799062108,
          "severe_pnl": -0.048172099999999995,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "CFX_USDT": {
          "gross_pnl": -0.0034093,
          "pf": 0.0,
          "severe_pnl": -0.031409299999999994,
          "trades": 7,
          "win_rate": 0.0
        },
        "CHEEMS_USDT": {
          "gross_pnl": 0.0021964,
          "pf": 0.0,
          "severe_pnl": -0.0018036000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "CHIP_USDT": {
          "gross_pnl": 0.013146300000000001,
          "pf": 0.010013382989141645,
          "severe_pnl": -0.1348537,
          "trades": 37,
          "win_rate": 0.05405405405405406
        },
        "CHR_USDT": {
          "gross_pnl": -0.0022531,
          "pf": 0.0,
          "severe_pnl": -0.014253100000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "CHZ_USDT": {
          "gross_pnl": -0.004489000000000002,
          "pf": 0.018732118730408476,
          "severe_pnl": -0.120489,
          "trades": 29,
          "win_rate": 0.034482758620689655
        },
        "CKB_USDT": {
          "gross_pnl": -0.0010741000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0090741,
          "trades": 2,
          "win_rate": 0.0
        },
        "CLO_USDT": {
          "gross_pnl": 0.0123319,
          "pf": 0.8724263376088589,
          "severe_pnl": -0.0036681000000000005,
          "trades": 4,
          "win_rate": 0.25
        },
        "COAI_USDT": {
          "gross_pnl": 0.0039026999999999985,
          "pf": 0.0,
          "severe_pnl": -0.07209729999999999,
          "trades": 19,
          "win_rate": 0.0
        },
        "COLLECT_USDT": {
          "gross_pnl": -0.020727199999999998,
          "pf": 0.010663510164504314,
          "severe_pnl": -0.07672720000000001,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "COMP_USDT": {
          "gross_pnl": -0.0017801,
          "pf": 0.0,
          "severe_pnl": -0.0097801,
          "trades": 2,
          "win_rate": 0.0
        },
        "COTI_USDT": {
          "gross_pnl": -0.0026076,
          "pf": 0.0,
          "severe_pnl": -0.0066076,
          "trades": 1,
          "win_rate": 0.0
        },
        "CROSS_USDT": {
          "gross_pnl": -0.0041578,
          "pf": 0.0,
          "severe_pnl": -0.0201578,
          "trades": 4,
          "win_rate": 0.0
        },
        "CRO_USDT": {
          "gross_pnl": 0.027606099999999998,
          "pf": 0.39174561101099,
          "severe_pnl": -0.0883939,
          "trades": 29,
          "win_rate": 0.10344827586206896
        },
        "CRV_USDT": {
          "gross_pnl": 0.026287199999999993,
          "pf": 0.04630583833075382,
          "severe_pnl": -0.2257128,
          "trades": 63,
          "win_rate": 0.06349206349206349
        },
        "CTC_USDT": {
          "gross_pnl": -0.008405200000000002,
          "pf": 0.0,
          "severe_pnl": -0.044405200000000006,
          "trades": 9,
          "win_rate": 0.0
        },
        "CVX_USDT": {
          "gross_pnl": -0.0063884000000000015,
          "pf": 0.0018290032577775671,
          "severe_pnl": -0.04638840000000001,
          "trades": 10,
          "win_rate": 0.1
        },
        "CYS_USDT": {
          "gross_pnl": -0.015928299999999996,
          "pf": 0.0,
          "severe_pnl": -0.0719283,
          "trades": 14,
          "win_rate": 0.0
        },
        "DASH_USDT": {
          "gross_pnl": 0.0107401,
          "pf": 0.012087346752551398,
          "severe_pnl": -0.27325990000000006,
          "trades": 71,
          "win_rate": 0.028169014084507043
        },
        "DEEP_USDT": {
          "gross_pnl": -0.0005455999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0085456,
          "trades": 2,
          "win_rate": 0.0
        },
        "DEXE_USDT": {
          "gross_pnl": -0.07544299999999998,
          "pf": 0.125941561267845,
          "severe_pnl": -0.599443,
          "trades": 131,
          "win_rate": 0.15267175572519084
        },
        "DODO_USDT": {
          "gross_pnl": -0.033315000000000025,
          "pf": 0.24388968735201283,
          "severe_pnl": -0.36531500000000017,
          "trades": 83,
          "win_rate": 0.2289156626506024
        },
        "DOGE_USDT": {
          "gross_pnl": 0.005354299999999999,
          "pf": 0.004229688088602286,
          "severe_pnl": -0.27464570000000005,
          "trades": 70,
          "win_rate": 0.014285714285714285
        },
        "DOGS_USDT": {
          "gross_pnl": -0.0027630999999999997,
          "pf": 0.0,
          "severe_pnl": -0.026763099999999998,
          "trades": 6,
          "win_rate": 0.0
        },
        "DOT_USDT": {
          "gross_pnl": -0.04747969999999999,
          "pf": 0.0012376205209768101,
          "severe_pnl": -0.4194797000000002,
          "trades": 93,
          "win_rate": 0.010752688172043012
        },
        "DRAM_USDT": {
          "gross_pnl": -0.004782999999999998,
          "pf": 0.025877849974209263,
          "severe_pnl": -0.19678300000000004,
          "trades": 48,
          "win_rate": 0.08333333333333333
        },
        "DUSK_USDT": {
          "gross_pnl": -0.0002803,
          "pf": 0.0,
          "severe_pnl": -0.0042803,
          "trades": 1,
          "win_rate": 0.0
        },
        "DYDX_USDT": {
          "gross_pnl": 0.0041562000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0318438,
          "trades": 9,
          "win_rate": 0.0
        },
        "EDEN_USDT": {
          "gross_pnl": -0.0068441000000000005,
          "pf": 0.0,
          "severe_pnl": -0.018844100000000003,
          "trades": 3,
          "win_rate": 0.0
        },
        "EDGE_USDT": {
          "gross_pnl": -0.06081669999999999,
          "pf": 0.07832829707795451,
          "severe_pnl": -0.4288167000000001,
          "trades": 92,
          "win_rate": 0.09782608695652174
        },
        "EDU_USDT": {
          "gross_pnl": -0.0034088000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0234088,
          "trades": 5,
          "win_rate": 0.0
        },
        "EGLD_USDT": {
          "gross_pnl": -0.018168899999999988,
          "pf": 0.025850359616091327,
          "severe_pnl": -0.3061689,
          "trades": 72,
          "win_rate": 0.041666666666666664
        },
        "EIGEN_USDT": {
          "gross_pnl": 0.027347400000000004,
          "pf": 0.045292530338433695,
          "severe_pnl": -0.31665260000000006,
          "trades": 86,
          "win_rate": 0.05813953488372093
        },
        "ELSA_USDT": {
          "gross_pnl": -0.0388873,
          "pf": 0.010150473856499316,
          "severe_pnl": -0.06688730000000001,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "ENA_USDT": {
          "gross_pnl": -0.01865569999999999,
          "pf": 0.00552718540095819,
          "severe_pnl": -0.2986557000000001,
          "trades": 70,
          "win_rate": 0.014285714285714285
        },
        "ENJ_USDT": {
          "gross_pnl": -0.010458,
          "pf": 0.017259126805903857,
          "severe_pnl": -0.070458,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "ENSO_USDT": {
          "gross_pnl": 0.0013173999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0106826,
          "trades": 3,
          "win_rate": 0.0
        },
        "ENS_USDT": {
          "gross_pnl": -0.012385299999999998,
          "pf": 0.0,
          "severe_pnl": -0.0803853,
          "trades": 17,
          "win_rate": 0.0
        },
        "EPIC_USDT": {
          "gross_pnl": 0.0024971999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0015028000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "ERA_USDT": {
          "gross_pnl": -0.0011718,
          "pf": 0.0,
          "severe_pnl": -0.0051718,
          "trades": 1,
          "win_rate": 0.0
        },
        "ESPORTS_USDT": {
          "gross_pnl": 0.020788600000000063,
          "pf": 0.37141264074140395,
          "severe_pnl": -0.4232114000000002,
          "trades": 111,
          "win_rate": 0.3783783783783784
        },
        "ESP_USDT": {
          "gross_pnl": -0.0068547,
          "pf": 0.0,
          "severe_pnl": -0.0148547,
          "trades": 2,
          "win_rate": 0.0
        },
        "ETC_USDT": {
          "gross_pnl": 0.001701,
          "pf": 0.0,
          "severe_pnl": -0.08629900000000001,
          "trades": 22,
          "win_rate": 0.0
        },
        "ETHFI_USDT": {
          "gross_pnl": 0.020358899999999996,
          "pf": 0.017241966070304544,
          "severe_pnl": -0.3436411000000001,
          "trades": 91,
          "win_rate": 0.03296703296703297
        },
        "ETH_USDT": {
          "gross_pnl": -0.004922499999999999,
          "pf": 0.0,
          "severe_pnl": -0.3009225000000001,
          "trades": 74,
          "win_rate": 0.0
        },
        "EUL_USDT": {
          "gross_pnl": -0.0062296,
          "pf": 0.0,
          "severe_pnl": -0.0142296,
          "trades": 2,
          "win_rate": 0.0
        },
        "EVAA_USDT": {
          "gross_pnl": 0.08613679999999997,
          "pf": 0.5395366869746335,
          "severe_pnl": -0.2098632,
          "trades": 74,
          "win_rate": 0.3108108108108108
        },
        "EWY_USDT": {
          "gross_pnl": -0.009884400000000002,
          "pf": 0.0,
          "severe_pnl": -0.3018844000000001,
          "trades": 73,
          "win_rate": 0.0
        },
        "FET_USDT": {
          "gross_pnl": 0.008018700000000004,
          "pf": 0.0012836003859384513,
          "severe_pnl": -0.2559813,
          "trades": 66,
          "win_rate": 0.015151515151515152
        },
        "FF_USDT": {
          "gross_pnl": -0.0130884,
          "pf": 0.008567156259208127,
          "severe_pnl": -0.0810884,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "FHE_USDT": {
          "gross_pnl": -0.008489199999999999,
          "pf": 0.07161176169010211,
          "severe_pnl": -0.14848919999999996,
          "trades": 35,
          "win_rate": 0.11428571428571428
        },
        "FIGHT_USDT": {
          "gross_pnl": 0.00096,
          "pf": 0.0,
          "severe_pnl": -0.00304,
          "trades": 1,
          "win_rate": 0.0
        },
        "FILECOIN_USDT": {
          "gross_pnl": -0.012834400000000003,
          "pf": 0.0,
          "severe_pnl": -0.14483440000000003,
          "trades": 33,
          "win_rate": 0.0
        },
        "FLOCK_USDT": {
          "gross_pnl": 0.0141884,
          "pf": 0.17753825998928124,
          "severe_pnl": -0.0138116,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "FLOKI_USDT": {
          "gross_pnl": -0.0026198,
          "pf": 0.0,
          "severe_pnl": -0.1106198,
          "trades": 27,
          "win_rate": 0.0
        },
        "FLOW_USDT": {
          "gross_pnl": 0.0003274,
          "pf": 0.0,
          "severe_pnl": -0.0076726,
          "trades": 2,
          "win_rate": 0.0
        },
        "FLR_USDT": {
          "gross_pnl": -0.0015198,
          "pf": 0.0,
          "severe_pnl": -0.0055198,
          "trades": 1,
          "win_rate": 0.0
        },
        "FOGO_USDT": {
          "gross_pnl": -0.0154357,
          "pf": 0.0,
          "severe_pnl": -0.039435700000000004,
          "trades": 6,
          "win_rate": 0.0
        },
        "FOLKS_USDT": {
          "gross_pnl": -0.0223451,
          "pf": 0.11061587989851368,
          "severe_pnl": -0.1903451,
          "trades": 42,
          "win_rate": 0.09523809523809523
        },
        "FORM_USDT": {
          "gross_pnl": -0.00046699999999999997,
          "pf": 0.0,
          "severe_pnl": -0.008467,
          "trades": 2,
          "win_rate": 0.0
        },
        "FRAX_USDT": {
          "gross_pnl": -0.00041050000000000006,
          "pf": 0.0,
          "severe_pnl": -0.0044105,
          "trades": 1,
          "win_rate": 0.0
        },
        "F_USDT": {
          "gross_pnl": 0.0021887,
          "pf": 0.0,
          "severe_pnl": -0.0058113,
          "trades": 2,
          "win_rate": 0.0
        },
        "GALA_USDT": {
          "gross_pnl": -0.026280400000000002,
          "pf": 0.0005037189055779637,
          "severe_pnl": -0.34228040000000004,
          "trades": 79,
          "win_rate": 0.012658227848101266
        },
        "GAS_USDT": {
          "gross_pnl": -0.0093868,
          "pf": 0.0,
          "severe_pnl": -0.0173868,
          "trades": 2,
          "win_rate": 0.0
        },
        "GENIUS_USDT": {
          "gross_pnl": 0.0022413,
          "pf": 0.0,
          "severe_pnl": -0.009758699999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "GIGGLE_USDT": {
          "gross_pnl": 0.004544,
          "pf": 0.31435297579636584,
          "severe_pnl": -0.007455999999999999,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "GLM_USDT": {
          "gross_pnl": -0.0029771,
          "pf": 0.0,
          "severe_pnl": -0.0149771,
          "trades": 3,
          "win_rate": 0.0
        },
        "GOAT_USDT": {
          "gross_pnl": -0.0045147,
          "pf": 0.0,
          "severe_pnl": -0.0085147,
          "trades": 1,
          "win_rate": 0.0
        },
        "GPS_USDT": {
          "gross_pnl": -0.0078478,
          "pf": 0.01095748265220277,
          "severe_pnl": -0.047847799999999996,
          "trades": 10,
          "win_rate": 0.1
        },
        "GRAM_USDT": {
          "gross_pnl": -0.0008893000000000006,
          "pf": 0.0024434394416161546,
          "severe_pnl": -0.1368893,
          "trades": 34,
          "win_rate": 0.029411764705882353
        },
        "GRASS_USDT": {
          "gross_pnl": -0.017284400000000002,
          "pf": 0.0,
          "severe_pnl": -0.0932844,
          "trades": 19,
          "win_rate": 0.0
        },
        "GRT_USDT": {
          "gross_pnl": -0.0022806000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0342806,
          "trades": 8,
          "win_rate": 0.0
        },
        "GUA_USDT": {
          "gross_pnl": 0.0009440999999999981,
          "pf": 0.4060502197247262,
          "severe_pnl": -0.011055900000000002,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "GUN_USDT": {
          "gross_pnl": 0.0170608,
          "pf": 0.3956720813947975,
          "severe_pnl": -0.0229392,
          "trades": 10,
          "win_rate": 0.2
        },
        "G_USDT": {
          "gross_pnl": -0.006926799999999999,
          "pf": 0.19665616497207505,
          "severe_pnl": -0.0269268,
          "trades": 5,
          "win_rate": 0.2
        },
        "HBAR_USDT": {
          "gross_pnl": -0.003055800000000001,
          "pf": 0.0,
          "severe_pnl": -0.1910558,
          "trades": 47,
          "win_rate": 0.0
        },
        "HEI_USDT": {
          "gross_pnl": -0.018042699999999988,
          "pf": 0.12491446510035627,
          "severe_pnl": -0.21804270000000003,
          "trades": 50,
          "win_rate": 0.12
        },
        "HIGH_USDT": {
          "gross_pnl": 0.022349899999999995,
          "pf": 0.36446790210796065,
          "severe_pnl": -0.0216501,
          "trades": 11,
          "win_rate": 0.2727272727272727
        },
        "HK50_USDT": {
          "gross_pnl": 0.001959899999999999,
          "pf": 0.0,
          "severe_pnl": -0.034040100000000004,
          "trades": 9,
          "win_rate": 0.0
        },
        "HMSTR_USDT": {
          "gross_pnl": 0.006356100000000003,
          "pf": 0.2555336816128943,
          "severe_pnl": -0.0456439,
          "trades": 13,
          "win_rate": 0.3076923076923077
        },
        "HNT_USDT": {
          "gross_pnl": -0.005732299999999999,
          "pf": 0.0,
          "severe_pnl": -0.0297323,
          "trades": 6,
          "win_rate": 0.0
        },
        "HOLO_USDT": {
          "gross_pnl": -0.0027397000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0227397,
          "trades": 5,
          "win_rate": 0.0
        },
        "HOME_USDT": {
          "gross_pnl": 0.0758274,
          "pf": 0.47670065141051915,
          "severe_pnl": -0.08017260000000002,
          "trades": 39,
          "win_rate": 0.28205128205128205
        },
        "HOT_USDT": {
          "gross_pnl": -0.0158505,
          "pf": 0.0,
          "severe_pnl": -0.0278505,
          "trades": 3,
          "win_rate": 0.0
        },
        "HYPE_USDT": {
          "gross_pnl": -0.009259499999999997,
          "pf": 0.0,
          "severe_pnl": -0.1772595,
          "trades": 42,
          "win_rate": 0.0
        },
        "ICNT_USDT": {
          "gross_pnl": -0.0012706,
          "pf": 0.0,
          "severe_pnl": -0.0052706,
          "trades": 1,
          "win_rate": 0.0
        },
        "ICP_USDT": {
          "gross_pnl": 0.0022340999999999984,
          "pf": 0.0005349733203182936,
          "severe_pnl": -0.2897659,
          "trades": 73,
          "win_rate": 0.0136986301369863
        },
        "ICX_USDT": {
          "gross_pnl": 0.0025437999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0054562000000000005,
          "trades": 2,
          "win_rate": 0.0
        },
        "ID_USDT": {
          "gross_pnl": 0.0002511,
          "pf": 0.0,
          "severe_pnl": -0.0157489,
          "trades": 4,
          "win_rate": 0.0
        },
        "IMX_USDT": {
          "gross_pnl": -0.0044754,
          "pf": 0.0,
          "severe_pnl": -0.028475399999999998,
          "trades": 6,
          "win_rate": 0.0
        },
        "INDA_USDT": {
          "gross_pnl": -0.021539099999999995,
          "pf": 0.0,
          "severe_pnl": -0.0455391,
          "trades": 6,
          "win_rate": 0.0
        },
        "INJ_USDT": {
          "gross_pnl": -0.03120070000000002,
          "pf": 0.0,
          "severe_pnl": -0.43920070000000005,
          "trades": 102,
          "win_rate": 0.0
        },
        "INTW_USDT": {
          "gross_pnl": 0.011330600000000001,
          "pf": 1.421195067973443,
          "severe_pnl": 0.0033306000000000013,
          "trades": 2,
          "win_rate": 0.5
        },
        "INX_USDT": {
          "gross_pnl": -0.0013262999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0053263,
          "trades": 1,
          "win_rate": 0.0
        },
        "IN_USDT": {
          "gross_pnl": -0.0022024,
          "pf": 0.0,
          "severe_pnl": -0.0102024,
          "trades": 2,
          "win_rate": 0.0
        },
        "IOST_USDT": {
          "gross_pnl": -0.0008939,
          "pf": 0.0,
          "severe_pnl": -0.0048939,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTA_USDT": {
          "gross_pnl": -0.0043,
          "pf": 0.0,
          "severe_pnl": -0.0083,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTX_USDT": {
          "gross_pnl": -0.0029252,
          "pf": 0.0,
          "severe_pnl": -0.0069252,
          "trades": 1,
          "win_rate": 0.0
        },
        "IRYS_USDT": {
          "gross_pnl": -0.0153257,
          "pf": 0.0,
          "severe_pnl": -0.0193257,
          "trades": 1,
          "win_rate": 0.0
        },
        "IWM_USDT": {
          "gross_pnl": -0.0010398,
          "pf": 0.0,
          "severe_pnl": -0.0050398000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "JASMY_USDT": {
          "gross_pnl": 0.0006285999999999998,
          "pf": 0.0011085112015882326,
          "severe_pnl": -0.16337139999999997,
          "trades": 41,
          "win_rate": 0.024390243902439025
        },
        "JCT_USDT": {
          "gross_pnl": -0.0074515999999999975,
          "pf": 0.25851975125125165,
          "severe_pnl": -0.0834516,
          "trades": 19,
          "win_rate": 0.05263157894736842
        },
        "JP225_USDT": {
          "gross_pnl": -0.00026669999999999906,
          "pf": 0.010958123111064798,
          "severe_pnl": -0.032266699999999995,
          "trades": 8,
          "win_rate": 0.125
        },
        "JST_USDT": {
          "gross_pnl": 0.006655399999999999,
          "pf": 0.13694949653173874,
          "severe_pnl": -0.025344600000000002,
          "trades": 8,
          "win_rate": 0.125
        },
        "JTO_USDT": {
          "gross_pnl": -0.021084300000000007,
          "pf": 0.010322774972622864,
          "severe_pnl": -0.2930843000000001,
          "trades": 68,
          "win_rate": 0.029411764705882353
        },
        "JUP_USDT": {
          "gross_pnl": -0.0187737,
          "pf": 0.0013861543507560797,
          "severe_pnl": -0.43477370000000004,
          "trades": 104,
          "win_rate": 0.019230769230769232
        },
        "KAIA_USDT": {
          "gross_pnl": -0.0031938,
          "pf": 0.0,
          "severe_pnl": -0.0231938,
          "trades": 5,
          "win_rate": 0.0
        },
        "KAITO_USDT": {
          "gross_pnl": 0.013238599999999994,
          "pf": 0.09014932453408024,
          "severe_pnl": -0.23476139999999995,
          "trades": 62,
          "win_rate": 0.12903225806451613
        },
        "KAS_USDT": {
          "gross_pnl": -0.0120766,
          "pf": 0.0,
          "severe_pnl": -0.1280766,
          "trades": 29,
          "win_rate": 0.0
        },
        "KAT_USDT": {
          "gross_pnl": 0.0040649,
          "pf": 0.5278833853934255,
          "severe_pnl": -0.0079351,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "KITE_USDT": {
          "gross_pnl": 0.0361963,
          "pf": 0.06006407906678611,
          "severe_pnl": -0.19180369999999997,
          "trades": 57,
          "win_rate": 0.08771929824561403
        },
        "KMNO_USDT": {
          "gross_pnl": 0.0010892999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0069107000000000005,
          "trades": 2,
          "win_rate": 0.0
        },
        "KORU_USDT": {
          "gross_pnl": 0.027824400000000006,
          "pf": 0.16640832808846295,
          "severe_pnl": -0.27217559999999996,
          "trades": 75,
          "win_rate": 0.24
        },
        "KSM_USDT": {
          "gross_pnl": -0.0064638000000000004,
          "pf": 0.0,
          "severe_pnl": -0.014463800000000002,
          "trades": 2,
          "win_rate": 0.0
        },
        "KSTR_USDT": {
          "gross_pnl": -0.00040419999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0044042000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "LAB_USDT": {
          "gross_pnl": 0.09294439999999998,
          "pf": 0.6356082788273703,
          "severe_pnl": -0.15105560000000004,
          "trades": 61,
          "win_rate": 0.29508196721311475
        },
        "LDO_USDT": {
          "gross_pnl": -0.031072000000000013,
          "pf": 0.011287082712725978,
          "severe_pnl": -0.46307200000000015,
          "trades": 108,
          "win_rate": 0.027777777777777776
        },
        "LEAD_USDT": {
          "gross_pnl": 0.0017280999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0142719,
          "trades": 4,
          "win_rate": 0.0
        },
        "LIGHT_USDT": {
          "gross_pnl": -0.0024217,
          "pf": 0.0,
          "severe_pnl": -0.046421699999999996,
          "trades": 11,
          "win_rate": 0.0
        },
        "LINEA_USDT": {
          "gross_pnl": 0.004116000000000001,
          "pf": 0.0,
          "severe_pnl": -0.023884,
          "trades": 7,
          "win_rate": 0.0
        },
        "LINK_USDT": {
          "gross_pnl": 0.0036579999999999994,
          "pf": 0.01095419590825741,
          "severe_pnl": -0.21634199999999998,
          "trades": 55,
          "win_rate": 0.01818181818181818
        },
        "LIT_USDT": {
          "gross_pnl": 0.052508699999999985,
          "pf": 0.025228762049270746,
          "severe_pnl": -0.6634913,
          "trades": 179,
          "win_rate": 0.05027932960893855
        },
        "LRC_USDT": {
          "gross_pnl": 0.0025427000000000023,
          "pf": 0.23425312523082994,
          "severe_pnl": -0.0694573,
          "trades": 18,
          "win_rate": 0.3333333333333333
        },
        "LTC_USDT": {
          "gross_pnl": -0.0006857000000000007,
          "pf": 0.0,
          "severe_pnl": -0.15268570000000004,
          "trades": 38,
          "win_rate": 0.0
        },
        "LUMIA_USDT": {
          "gross_pnl": -0.0588217,
          "pf": 0.07350989437781777,
          "severe_pnl": -0.13082170000000004,
          "trades": 18,
          "win_rate": 0.1111111111111111
        },
        "LUNANEW_USDT": {
          "gross_pnl": -0.0008573,
          "pf": 0.0,
          "severe_pnl": -0.0048573,
          "trades": 1,
          "win_rate": 0.0
        },
        "LUNC_USDT": {
          "gross_pnl": -0.010508700000000003,
          "pf": 0.0,
          "severe_pnl": -0.08250869999999999,
          "trades": 18,
          "win_rate": 0.0
        },
        "MAGMA_USDT": {
          "gross_pnl": 0.0247645,
          "pf": 0.2342911263024914,
          "severe_pnl": -0.25523550000000017,
          "trades": 70,
          "win_rate": 0.18571428571428572
        },
        "MANA_USDT": {
          "gross_pnl": -0.006789900000000001,
          "pf": 0.0,
          "severe_pnl": -0.0587899,
          "trades": 13,
          "win_rate": 0.0
        },
        "MANTA_USDT": {
          "gross_pnl": -0.0038989999999999997,
          "pf": 0.0,
          "severe_pnl": -0.067899,
          "trades": 16,
          "win_rate": 0.0
        },
        "MANTRA_USDT": {
          "gross_pnl": -0.016911799999999994,
          "pf": 0.1077916313744768,
          "severe_pnl": -0.1009118,
          "trades": 21,
          "win_rate": 0.23809523809523808
        },
        "MASK_USDT": {
          "gross_pnl": -0.0005013,
          "pf": 0.0,
          "severe_pnl": -0.0085013,
          "trades": 2,
          "win_rate": 0.0
        },
        "MAV_USDT": {
          "gross_pnl": -0.0060965,
          "pf": 0.0,
          "severe_pnl": -0.0220965,
          "trades": 4,
          "win_rate": 0.0
        },
        "MEGA_USDT": {
          "gross_pnl": 0.0065346,
          "pf": 0.0,
          "severe_pnl": -0.0254654,
          "trades": 8,
          "win_rate": 0.0
        },
        "MEME_USDT": {
          "gross_pnl": -0.0058989,
          "pf": 0.0,
          "severe_pnl": -0.0298989,
          "trades": 6,
          "win_rate": 0.0
        },
        "MERL_USDT": {
          "gross_pnl": -0.023436100000000005,
          "pf": 0.0,
          "severe_pnl": -0.08343610000000001,
          "trades": 15,
          "win_rate": 0.0
        },
        "MET_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "MINA_USDT": {
          "gross_pnl": -0.0027003,
          "pf": 0.0,
          "severe_pnl": -0.0107003,
          "trades": 2,
          "win_rate": 0.0
        },
        "MITO_USDT": {
          "gross_pnl": 0.0021331,
          "pf": 0.0,
          "severe_pnl": -0.0058668999999999995,
          "trades": 2,
          "win_rate": 0.0
        },
        "MMT_USDT": {
          "gross_pnl": -0.032449099999999995,
          "pf": 0.09764250858931578,
          "severe_pnl": -0.29244909999999996,
          "trades": 65,
          "win_rate": 0.09230769230769231
        },
        "MNT_USDT": {
          "gross_pnl": -0.0013816000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0373816,
          "trades": 9,
          "win_rate": 0.0
        },
        "MONAD_USDT": {
          "gross_pnl": 0.011519500000000002,
          "pf": 0.06455099376178733,
          "severe_pnl": -0.0644805,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "MOODENG_USDT": {
          "gross_pnl": -0.0009005,
          "pf": 0.0,
          "severe_pnl": -0.0049005,
          "trades": 1,
          "win_rate": 0.0
        },
        "MORPHO_USDT": {
          "gross_pnl": -0.0226903,
          "pf": 0.0,
          "severe_pnl": -0.15469030000000006,
          "trades": 33,
          "win_rate": 0.0
        },
        "MOVE_USDT": {
          "gross_pnl": -0.003637800000000001,
          "pf": 0.0,
          "severe_pnl": -0.0276378,
          "trades": 6,
          "win_rate": 0.0
        },
        "MOVR_USDT": {
          "gross_pnl": -0.0014545,
          "pf": 0.0,
          "severe_pnl": -0.0054545,
          "trades": 1,
          "win_rate": 0.0
        },
        "MSTU_USDT": {
          "gross_pnl": -0.015674399999999998,
          "pf": 0.10559857655680448,
          "severe_pnl": -0.051674399999999995,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "MUBARAK_USDT": {
          "gross_pnl": 0.0081845,
          "pf": 999,
          "severe_pnl": 0.004184500000000001,
          "trades": 1,
          "win_rate": 1.0
        },
        "MUU_USDT": {
          "gross_pnl": 0.0075694,
          "pf": 0.0,
          "severe_pnl": -0.0084306,
          "trades": 4,
          "win_rate": 0.0
        },
        "MVLL_USDT": {
          "gross_pnl": 0.019601999999999987,
          "pf": 0.3313339388072165,
          "severe_pnl": -0.08039799999999998,
          "trades": 25,
          "win_rate": 0.32
        },
        "MYX_USDT": {
          "gross_pnl": 0.004309500000000002,
          "pf": 0.12068445591905572,
          "severe_pnl": -0.3956904999999999,
          "trades": 100,
          "win_rate": 0.1
        },
        "M_USDT": {
          "gross_pnl": 0.028519100000000002,
          "pf": 999,
          "severe_pnl": 0.024519100000000002,
          "trades": 1,
          "win_rate": 1.0
        },
        "NAORIS_USDT": {
          "gross_pnl": -0.012673199999999999,
          "pf": 0.08283272101413297,
          "severe_pnl": -0.08867320000000001,
          "trades": 19,
          "win_rate": 0.15789473684210525
        },
        "NEAR_USDT": {
          "gross_pnl": -0.014470600000000004,
          "pf": 0.007869569858817602,
          "severe_pnl": -0.5464705999999998,
          "trades": 133,
          "win_rate": 0.015037593984962405
        },
        "NEIROCTO_USDT": {
          "gross_pnl": -0.0010076,
          "pf": 0.0,
          "severe_pnl": -0.0050076,
          "trades": 1,
          "win_rate": 0.0
        },
        "NEO_USDT": {
          "gross_pnl": -0.004627200000000001,
          "pf": 0.0,
          "severe_pnl": -0.008627200000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "NES_USDT": {
          "gross_pnl": -0.0129419,
          "pf": 0.046402966015831465,
          "severe_pnl": -0.08894190000000002,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "NEX_USDT": {
          "gross_pnl": 0.0418283,
          "pf": 999,
          "severe_pnl": 0.037828299999999995,
          "trades": 1,
          "win_rate": 1.0
        },
        "NGAS_USDT": {
          "gross_pnl": 0.012890100000000002,
          "pf": 0.04318161498706285,
          "severe_pnl": -0.21510990000000008,
          "trades": 57,
          "win_rate": 0.017543859649122806
        },
        "NICKEL_USDT": {
          "gross_pnl": 0.00036969999999999993,
          "pf": 0.0,
          "severe_pnl": -0.0156303,
          "trades": 4,
          "win_rate": 0.0
        },
        "NIGHT_USDT": {
          "gross_pnl": -0.0019924000000000005,
          "pf": 0.0,
          "severe_pnl": -0.05799240000000001,
          "trades": 14,
          "win_rate": 0.0
        },
        "NIL_USDT": {
          "gross_pnl": -0.008372899999999999,
          "pf": 0.0,
          "severe_pnl": -0.032372899999999996,
          "trades": 6,
          "win_rate": 0.0
        },
        "NOM_USDT": {
          "gross_pnl": -0.019973599999999998,
          "pf": 0.0,
          "severe_pnl": -0.0479736,
          "trades": 7,
          "win_rate": 0.0
        },
        "NOT_USDT": {
          "gross_pnl": 0.0010673000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0109327,
          "trades": 3,
          "win_rate": 0.0
        },
        "OFC_USDT": {
          "gross_pnl": -0.0039879,
          "pf": 0.009358530101973989,
          "severe_pnl": -0.0279879,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "OGN_USDT": {
          "gross_pnl": -0.049839499999999995,
          "pf": 0.022746846170275795,
          "severe_pnl": -0.1418395,
          "trades": 23,
          "win_rate": 0.08695652173913043
        },
        "OG_USDT": {
          "gross_pnl": 0.0047319,
          "pf": 999,
          "severe_pnl": 0.0007318999999999997,
          "trades": 1,
          "win_rate": 1.0
        },
        "OKB_USDT": {
          "gross_pnl": -0.00024369999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0082437,
          "trades": 2,
          "win_rate": 0.0
        },
        "OL_USDT": {
          "gross_pnl": 0.0010138,
          "pf": 0.0,
          "severe_pnl": -0.0029862,
          "trades": 1,
          "win_rate": 0.0
        },
        "ONDO_USDT": {
          "gross_pnl": -0.00023629999999999832,
          "pf": 0.020339212886290845,
          "severe_pnl": -0.40023629999999993,
          "trades": 100,
          "win_rate": 0.02
        },
        "ONE_USDT": {
          "gross_pnl": 0.018176799999999996,
          "pf": 4.2208121024147855,
          "severe_pnl": 0.010176799999999998,
          "trades": 2,
          "win_rate": 0.5
        },
        "ONG_USDT": {
          "gross_pnl": -0.0010328,
          "pf": 0.0,
          "severe_pnl": -0.0050328000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "ONT_USDT": {
          "gross_pnl": -0.0002327,
          "pf": 0.0,
          "severe_pnl": -0.008232699999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "OPENAI_USDT": {
          "gross_pnl": -0.06252070000000001,
          "pf": 0.0,
          "severe_pnl": -0.4465206999999999,
          "trades": 96,
          "win_rate": 0.0
        },
        "OPENLEDGER_USDT": {
          "gross_pnl": -0.0013324,
          "pf": 0.0,
          "severe_pnl": -0.0053324,
          "trades": 1,
          "win_rate": 0.0
        },
        "OPG_USDT": {
          "gross_pnl": -0.022381399999999996,
          "pf": 0.0,
          "severe_pnl": -0.1143814,
          "trades": 23,
          "win_rate": 0.0
        },
        "OPN_USDT": {
          "gross_pnl": 0.0200092,
          "pf": 0.07874690858628464,
          "severe_pnl": -0.15999079999999996,
          "trades": 45,
          "win_rate": 0.08888888888888889
        },
        "OP_USDT": {
          "gross_pnl": -0.009005200000000001,
          "pf": 0.0,
          "severe_pnl": -0.38500520000000016,
          "trades": 94,
          "win_rate": 0.0
        },
        "ORCA_USDT": {
          "gross_pnl": -0.0040973,
          "pf": 0.0,
          "severe_pnl": -0.016097300000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "ORDI_USDT": {
          "gross_pnl": -0.0339748,
          "pf": 0.009222270266084113,
          "severe_pnl": -0.5219748000000002,
          "trades": 122,
          "win_rate": 0.01639344262295082
        },
        "O_USDT": {
          "gross_pnl": 0.0347409,
          "pf": 0.4103305462672765,
          "severe_pnl": -0.1012591,
          "trades": 34,
          "win_rate": 0.058823529411764705
        },
        "PARTI_USDT": {
          "gross_pnl": -0.04424229999999999,
          "pf": 0.20737311163312414,
          "severe_pnl": -0.11624229999999999,
          "trades": 18,
          "win_rate": 0.16666666666666666
        },
        "PAXG_USDT": {
          "gross_pnl": -0.00033509999999999963,
          "pf": 0.0,
          "severe_pnl": -0.07633509999999999,
          "trades": 19,
          "win_rate": 0.0
        },
        "PENDLE_USDT": {
          "gross_pnl": 0.0079459,
          "pf": 0.0,
          "severe_pnl": -0.14805410000000002,
          "trades": 39,
          "win_rate": 0.0
        },
        "PEOPLE_USDT": {
          "gross_pnl": -0.0012870000000000002,
          "pf": 0.0,
          "severe_pnl": -0.005287,
          "trades": 1,
          "win_rate": 0.0
        },
        "PEPE_USDT": {
          "gross_pnl": -0.0052287,
          "pf": 0.0,
          "severe_pnl": -0.04122870000000001,
          "trades": 9,
          "win_rate": 0.0
        },
        "PHAROS_USDT": {
          "gross_pnl": 0.0002428,
          "pf": 0.0,
          "severe_pnl": -0.0037572,
          "trades": 1,
          "win_rate": 0.0
        },
        "PHA_USDT": {
          "gross_pnl": -0.00038380000000000017,
          "pf": 0.0,
          "severe_pnl": -0.0203838,
          "trades": 5,
          "win_rate": 0.0
        },
        "PIEVERSE_USDT": {
          "gross_pnl": -0.005217,
          "pf": 0.03518806888398305,
          "severe_pnl": -0.025217000000000003,
          "trades": 5,
          "win_rate": 0.2
        },
        "PIPPIN_USDT": {
          "gross_pnl": -0.0339492,
          "pf": 0.007556061352261141,
          "severe_pnl": -0.28594920000000007,
          "trades": 63,
          "win_rate": 0.047619047619047616
        },
        "PI_USDT": {
          "gross_pnl": 0.06068309999999999,
          "pf": 0.1691689833125195,
          "severe_pnl": -0.5553169000000003,
          "trades": 154,
          "win_rate": 0.045454545454545456
        },
        "PLUME_USDT": {
          "gross_pnl": -0.0009458000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0169458,
          "trades": 4,
          "win_rate": 0.0
        },
        "PNUT_USDT": {
          "gross_pnl": -0.0002346,
          "pf": 0.0,
          "severe_pnl": -0.0042346,
          "trades": 1,
          "win_rate": 0.0
        },
        "POL_USDT": {
          "gross_pnl": -0.030421300000000002,
          "pf": 0.0,
          "severe_pnl": -0.2824213000000001,
          "trades": 63,
          "win_rate": 0.0
        },
        "PONS_USDT": {
          "gross_pnl": -0.0169122,
          "pf": 0.0,
          "severe_pnl": -0.0209122,
          "trades": 1,
          "win_rate": 0.0
        },
        "POPCAT_USDT": {
          "gross_pnl": -0.0046815,
          "pf": 0.0,
          "severe_pnl": -0.0166815,
          "trades": 3,
          "win_rate": 0.0
        },
        "PORTAL_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "POWER_USDT": {
          "gross_pnl": -0.0058257000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0258257,
          "trades": 5,
          "win_rate": 0.0
        },
        "POWR_USDT": {
          "gross_pnl": 0.029211,
          "pf": 2.9822252957778064,
          "severe_pnl": 0.021210999999999997,
          "trades": 2,
          "win_rate": 0.5
        },
        "PRL_USDT": {
          "gross_pnl": -0.0017699,
          "pf": 0.0,
          "severe_pnl": -0.0057699,
          "trades": 1,
          "win_rate": 0.0
        },
        "PROM_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "PTB_USDT": {
          "gross_pnl": 0.0009311,
          "pf": 0.0,
          "severe_pnl": -0.0030689000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "PUMPFUN_USDT": {
          "gross_pnl": -0.019466100000000007,
          "pf": 0.021582548908618698,
          "severe_pnl": -0.4834661000000002,
          "trades": 116,
          "win_rate": 0.04310344827586207
        },
        "PUNDIX_USDT": {
          "gross_pnl": -0.0012245000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0092245,
          "trades": 2,
          "win_rate": 0.0
        },
        "PYTH_USDT": {
          "gross_pnl": -0.022821899999999992,
          "pf": 0.01370579370590038,
          "severe_pnl": -0.4068219,
          "trades": 96,
          "win_rate": 0.041666666666666664
        },
        "QNT_USDT": {
          "gross_pnl": 0.0025758,
          "pf": 0.0,
          "severe_pnl": -0.0134242,
          "trades": 4,
          "win_rate": 0.0
        },
        "QTUM_USDT": {
          "gross_pnl": -0.0038018999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0158019,
          "trades": 3,
          "win_rate": 0.0
        },
        "RAM_USDT": {
          "gross_pnl": -0.0102103,
          "pf": 0.025899394886326012,
          "severe_pnl": -0.06621030000000001,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "RARE_USDT": {
          "gross_pnl": -0.0088255,
          "pf": 0.0,
          "severe_pnl": -0.0168255,
          "trades": 2,
          "win_rate": 0.0
        },
        "RAVE_USDT": {
          "gross_pnl": 0.06800939999999997,
          "pf": 0.17271989525583972,
          "severe_pnl": -0.4719905999999999,
          "trades": 135,
          "win_rate": 0.1111111111111111
        },
        "RAY_USDT": {
          "gross_pnl": 0.0002904,
          "pf": 0.0,
          "severe_pnl": -0.0037096,
          "trades": 1,
          "win_rate": 0.0
        },
        "RED_USDT": {
          "gross_pnl": -0.0008849999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0048850000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "RENDER_USDT": {
          "gross_pnl": -0.0007687000000000006,
          "pf": 0.0,
          "severe_pnl": -0.1447687,
          "trades": 36,
          "win_rate": 0.0
        },
        "RESOLV_USDT": {
          "gross_pnl": -0.004634000000000005,
          "pf": 0.033172394977538176,
          "severe_pnl": -0.15663400000000002,
          "trades": 38,
          "win_rate": 0.10526315789473684
        },
        "REZ_USDT": {
          "gross_pnl": -0.0033278,
          "pf": 0.0,
          "severe_pnl": -0.007327800000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "RE_USDT": {
          "gross_pnl": 0.0130264,
          "pf": 0.019617847820629003,
          "severe_pnl": -0.3869736,
          "trades": 100,
          "win_rate": 0.06
        },
        "RIF_USDT": {
          "gross_pnl": -0.032519700000000006,
          "pf": 0.04703541311199297,
          "severe_pnl": -0.10851970000000001,
          "trades": 19,
          "win_rate": 0.05263157894736842
        },
        "RLC_USDT": {
          "gross_pnl": 0.0108165,
          "pf": 0.26457811730970876,
          "severe_pnl": -0.0171835,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "ROAM_USDT": {
          "gross_pnl": 0.06238259999999999,
          "pf": 0.8433744073974888,
          "severe_pnl": -0.025617399999999988,
          "trades": 22,
          "win_rate": 0.4090909090909091
        },
        "ROBO_USDT": {
          "gross_pnl": -0.0060479,
          "pf": 0.0,
          "severe_pnl": -0.0220479,
          "trades": 4,
          "win_rate": 0.0
        },
        "ROSE_USDT": {
          "gross_pnl": 0.0024519000000000003,
          "pf": 0.0,
          "severe_pnl": -0.017548099999999997,
          "trades": 5,
          "win_rate": 0.0
        },
        "RPL_USDT": {
          "gross_pnl": -0.0087765,
          "pf": 0.0,
          "severe_pnl": -0.0287765,
          "trades": 5,
          "win_rate": 0.0
        },
        "RSR_USDT": {
          "gross_pnl": -0.0023861000000000004,
          "pf": 0.0,
          "severe_pnl": -0.026386100000000003,
          "trades": 6,
          "win_rate": 0.0
        },
        "RUNE_USDT": {
          "gross_pnl": 0.0011861000000000003,
          "pf": 0.0,
          "severe_pnl": -0.014813899999999998,
          "trades": 4,
          "win_rate": 0.0
        },
        "RVN_USDT": {
          "gross_pnl": -0.006082499999999999,
          "pf": 0.1054162002223615,
          "severe_pnl": -0.0700825,
          "trades": 16,
          "win_rate": 0.0625
        },
        "SAFE_USDT": {
          "gross_pnl": 0.00040510000000000014,
          "pf": 0.0,
          "severe_pnl": -0.015594899999999998,
          "trades": 4,
          "win_rate": 0.0
        },
        "SAGA_USDT": {
          "gross_pnl": -0.0014921,
          "pf": 0.0,
          "severe_pnl": -0.0094921,
          "trades": 2,
          "win_rate": 0.0
        },
        "SAHARA_USDT": {
          "gross_pnl": -0.016097300000000002,
          "pf": 0.0027316859382917847,
          "severe_pnl": -0.08009730000000001,
          "trades": 16,
          "win_rate": 0.0625
        },
        "SAND_USDT": {
          "gross_pnl": 0.0022278,
          "pf": 0.0,
          "severe_pnl": -0.0057722,
          "trades": 2,
          "win_rate": 0.0
        },
        "SANTOS_USDT": {
          "gross_pnl": -0.00037400000000000063,
          "pf": 0.014653227019708127,
          "severe_pnl": -0.016374,
          "trades": 4,
          "win_rate": 0.25
        },
        "SAPIEN_USDT": {
          "gross_pnl": 0.0001371,
          "pf": 0.0,
          "severe_pnl": -0.0038629000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "SEI_USDT": {
          "gross_pnl": 0.0050418999999999985,
          "pf": 0.007667473571858482,
          "severe_pnl": -0.2029581,
          "trades": 52,
          "win_rate": 0.019230769230769232
        },
        "SENT_USDT": {
          "gross_pnl": -0.0268964,
          "pf": 0.03461617848497927,
          "severe_pnl": -0.1028964,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "SHIB_USDT": {
          "gross_pnl": -0.0086563,
          "pf": 0.0,
          "severe_pnl": -0.10465630000000001,
          "trades": 24,
          "win_rate": 0.0
        },
        "SHLD_USDT": {
          "gross_pnl": 0.0026187,
          "pf": 0.0,
          "severe_pnl": -0.0053813,
          "trades": 2,
          "win_rate": 0.0
        },
        "SIGN_USDT": {
          "gross_pnl": -0.0011727,
          "pf": 0.0,
          "severe_pnl": -0.0051727000000000006,
          "trades": 1,
          "win_rate": 0.0
        },
        "SIREN_USDT": {
          "gross_pnl": -0.0098468,
          "pf": 0.0,
          "severe_pnl": -0.0138468,
          "trades": 1,
          "win_rate": 0.0
        },
        "SKL_USDT": {
          "gross_pnl": -0.0766771,
          "pf": 0.11624505888879902,
          "severe_pnl": -0.24467709999999998,
          "trades": 42,
          "win_rate": 0.11904761904761904
        },
        "SKR_USDT": {
          "gross_pnl": -0.0136872,
          "pf": 0.0,
          "severe_pnl": -0.0296872,
          "trades": 4,
          "win_rate": 0.0
        },
        "SKYAI_USDT": {
          "gross_pnl": -0.023037200000000015,
          "pf": 0.0687595084400791,
          "severe_pnl": -0.6870371999999997,
          "trades": 166,
          "win_rate": 0.08433734939759036
        },
        "SKY_USDT": {
          "gross_pnl": 0.0033218999999999983,
          "pf": 0.020389644957119014,
          "severe_pnl": -0.056678099999999995,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "SLX_USDT": {
          "gross_pnl": -0.05361190000000001,
          "pf": 0.05313663151364765,
          "severe_pnl": -0.6496118999999999,
          "trades": 149,
          "win_rate": 0.12080536912751678
        },
        "SMH_USDT": {
          "gross_pnl": 0.000169,
          "pf": 0.0,
          "severe_pnl": -0.003831,
          "trades": 1,
          "win_rate": 0.0
        },
        "SNT_USDT": {
          "gross_pnl": 0.0005340000000000001,
          "pf": 0.0,
          "severe_pnl": -0.011466,
          "trades": 3,
          "win_rate": 0.0
        },
        "SNXX_USDT": {
          "gross_pnl": -0.0393825,
          "pf": 0.0,
          "severe_pnl": -0.0673825,
          "trades": 7,
          "win_rate": 0.0
        },
        "SNX_USDT": {
          "gross_pnl": 0.0074863,
          "pf": 0.10381040875025169,
          "severe_pnl": -0.04851370000000001,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "SOL_USDT": {
          "gross_pnl": -0.0034867000000000006,
          "pf": 0.007740113842590939,
          "severe_pnl": -0.21148670000000006,
          "trades": 52,
          "win_rate": 0.019230769230769232
        },
        "SOXL_USDT": {
          "gross_pnl": 0.022819099999999988,
          "pf": 0.12413240670453281,
          "severe_pnl": -0.4491809000000002,
          "trades": 118,
          "win_rate": 0.1694915254237288
        },
        "SOXS_USDT": {
          "gross_pnl": 0.012364099999999998,
          "pf": 0.15994257578410545,
          "severe_pnl": -0.09163590000000002,
          "trades": 26,
          "win_rate": 0.19230769230769232
        },
        "SOXX_USDT": {
          "gross_pnl": -0.0143148,
          "pf": 0.0,
          "severe_pnl": -0.04631480000000001,
          "trades": 8,
          "win_rate": 0.0
        },
        "SPELL_USDT": {
          "gross_pnl": -0.0291114,
          "pf": 0.0,
          "severe_pnl": -0.0491114,
          "trades": 5,
          "win_rate": 0.0
        },
        "SPK_USDT": {
          "gross_pnl": 0.0010946999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0029053000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "SPY_USDT": {
          "gross_pnl": 0.0020889,
          "pf": 0.0,
          "severe_pnl": -0.0019111000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "SQD_USDT": {
          "gross_pnl": 0.0042818000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0077182,
          "trades": 3,
          "win_rate": 0.0
        },
        "SQQQ_USDT": {
          "gross_pnl": 0.0021403999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0058595999999999995,
          "trades": 2,
          "win_rate": 0.0
        },
        "STABLE_USDT": {
          "gross_pnl": -0.0010201999999999993,
          "pf": 0.04746401883699222,
          "severe_pnl": -0.04102020000000001,
          "trades": 10,
          "win_rate": 0.1
        },
        "STAR_USDT": {
          "gross_pnl": -0.031211000000000003,
          "pf": 0.0,
          "severe_pnl": -0.035211000000000006,
          "trades": 1,
          "win_rate": 0.0
        },
        "STEEM_USDT": {
          "gross_pnl": -0.0016294,
          "pf": 0.0,
          "severe_pnl": -0.0056294,
          "trades": 1,
          "win_rate": 0.0
        },
        "STG_USDT": {
          "gross_pnl": -0.0108791,
          "pf": 0.0,
          "severe_pnl": -0.06687910000000001,
          "trades": 14,
          "win_rate": 0.0
        },
        "STORJ_USDT": {
          "gross_pnl": 0.0173053,
          "pf": 999,
          "severe_pnl": 0.013305299999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "STO_USDT": {
          "gross_pnl": 0.002469,
          "pf": 0.0,
          "severe_pnl": -0.005531,
          "trades": 2,
          "win_rate": 0.0
        },
        "STRK_USDT": {
          "gross_pnl": -0.013827299999999997,
          "pf": 0.0,
          "severe_pnl": -0.0938273,
          "trades": 20,
          "win_rate": 0.0
        },
        "STX_USDT": {
          "gross_pnl": -0.0250197,
          "pf": 0.0,
          "severe_pnl": -0.08901970000000002,
          "trades": 16,
          "win_rate": 0.0
        },
        "SUI_USDT": {
          "gross_pnl": -5.2800000000003235e-05,
          "pf": 0.006606261010763453,
          "severe_pnl": -0.25205279999999997,
          "trades": 63,
          "win_rate": 0.031746031746031744
        },
        "SUPER_USDT": {
          "gross_pnl": 0.004648000000000001,
          "pf": 0.4214986583993643,
          "severe_pnl": -0.007351999999999999,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "SUSHI_USDT": {
          "gross_pnl": -0.007349,
          "pf": 0.0,
          "severe_pnl": -0.023349,
          "trades": 4,
          "win_rate": 0.0
        },
        "SXT_USDT": {
          "gross_pnl": -0.021617100000000042,
          "pf": 0.23428905745779047,
          "severe_pnl": -0.3616171,
          "trades": 85,
          "win_rate": 0.2
        },
        "SYN_USDT": {
          "gross_pnl": -0.01672300000000004,
          "pf": 0.14270763653480037,
          "severe_pnl": -0.6327229999999998,
          "trades": 154,
          "win_rate": 0.2012987012987013
        },
        "SYRUP_USDT": {
          "gross_pnl": 0.0008547999999999994,
          "pf": 0.01431940177582356,
          "severe_pnl": -0.29514520000000005,
          "trades": 74,
          "win_rate": 0.04054054054054054
        },
        "S_USDT": {
          "gross_pnl": 0.0007026000000000003,
          "pf": 0.023740039769394733,
          "severe_pnl": -0.0272974,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "TAC_USDT": {
          "gross_pnl": -0.0748576,
          "pf": 0.22421382180675883,
          "severe_pnl": -0.35085760000000005,
          "trades": 69,
          "win_rate": 0.15942028985507245
        },
        "TAG_USDT": {
          "gross_pnl": 0.0684401,
          "pf": 0.5605692837674523,
          "severe_pnl": -0.0515599,
          "trades": 30,
          "win_rate": 0.3
        },
        "TAIKO_USDT": {
          "gross_pnl": 0.0055277,
          "pf": 0.0018814095149973637,
          "severe_pnl": -0.006472299999999999,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "TAO_USDT": {
          "gross_pnl": -0.014651399999999998,
          "pf": 0.0,
          "severe_pnl": -0.15065140000000002,
          "trades": 34,
          "win_rate": 0.0
        },
        "TENDIES_USDT": {
          "gross_pnl": 0.0392548,
          "pf": 999,
          "severe_pnl": 0.0352548,
          "trades": 1,
          "win_rate": 1.0
        },
        "THETA_USDT": {
          "gross_pnl": -0.03949890000000001,
          "pf": 0.004215426852717286,
          "severe_pnl": -0.1954989,
          "trades": 39,
          "win_rate": 0.02564102564102564
        },
        "THE_USDT": {
          "gross_pnl": 0.0212235,
          "pf": 0.45671800571988774,
          "severe_pnl": -0.0227765,
          "trades": 11,
          "win_rate": 0.36363636363636365
        },
        "TIA_USDT": {
          "gross_pnl": -0.02361580000000001,
          "pf": 0.006406917990715004,
          "severe_pnl": -0.35161580000000026,
          "trades": 82,
          "win_rate": 0.024390243902439025
        },
        "TLM_USDT": {
          "gross_pnl": -0.004337399999999999,
          "pf": 0.06828945336709204,
          "severe_pnl": -0.30833739999999993,
          "trades": 76,
          "win_rate": 0.06578947368421052
        },
        "TNSR_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "TOSHI_USDT": {
          "gross_pnl": -0.0249733,
          "pf": 0.0,
          "severe_pnl": -0.0369733,
          "trades": 3,
          "win_rate": 0.0
        },
        "TOWNS_USDT": {
          "gross_pnl": 0.006660299999999999,
          "pf": 0.19596071774206336,
          "severe_pnl": -0.0253397,
          "trades": 8,
          "win_rate": 0.125
        },
        "TQQQ_USDT": {
          "gross_pnl": 0.0119583,
          "pf": 0.0,
          "severe_pnl": -0.052041699999999996,
          "trades": 16,
          "win_rate": 0.0
        },
        "TRADOOR_USDT": {
          "gross_pnl": 0.0033661999999999937,
          "pf": 0.14253869668983288,
          "severe_pnl": -0.14863379999999998,
          "trades": 38,
          "win_rate": 0.21052631578947367
        },
        "TRB_USDT": {
          "gross_pnl": 0.0130594,
          "pf": 0.0,
          "severe_pnl": -0.06294060000000001,
          "trades": 19,
          "win_rate": 0.0
        },
        "TRIA_USDT": {
          "gross_pnl": -0.012284100000000001,
          "pf": 0.15342868490808775,
          "severe_pnl": -0.5882841000000002,
          "trades": 144,
          "win_rate": 0.1875
        },
        "TRX_USDT": {
          "gross_pnl": -0.0007744000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0487744,
          "trades": 12,
          "win_rate": 0.0
        },
        "TRY_USDT": {
          "gross_pnl": -0.0004684,
          "pf": 0.0,
          "severe_pnl": -0.0164684,
          "trades": 4,
          "win_rate": 0.0
        },
        "TSLL_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "TURBO_USDT": {
          "gross_pnl": -0.0071278,
          "pf": 0.0,
          "severe_pnl": -0.0271278,
          "trades": 5,
          "win_rate": 0.0
        },
        "TUT_USDT": {
          "gross_pnl": 5.569999999999989e-05,
          "pf": 0.0,
          "severe_pnl": -0.007944300000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "TWT_USDT": {
          "gross_pnl": -0.0086063,
          "pf": 0.0,
          "severe_pnl": -0.0126063,
          "trades": 1,
          "win_rate": 0.0
        },
        "T_USDT": {
          "gross_pnl": 0.08785679999999998,
          "pf": 0.3458747858670814,
          "severe_pnl": -0.2241432000000001,
          "trades": 78,
          "win_rate": 0.21794871794871795
        },
        "UAI_USDT": {
          "gross_pnl": -0.049202199999999995,
          "pf": 0.03527072759448321,
          "severe_pnl": -0.2892022,
          "trades": 60,
          "win_rate": 0.05
        },
        "UMA_USDT": {
          "gross_pnl": 0.00148,
          "pf": 0.0,
          "severe_pnl": -0.00652,
          "trades": 2,
          "win_rate": 0.0
        },
        "UNI_USDT": {
          "gross_pnl": -0.005304299999999998,
          "pf": 0.0023346623177704856,
          "severe_pnl": -0.38130430000000015,
          "trades": 94,
          "win_rate": 0.02127659574468085
        },
        "UP_USDT": {
          "gross_pnl": -0.0024848999999999995,
          "pf": 0.0,
          "severe_pnl": -0.014484900000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "URNM_USDT": {
          "gross_pnl": 0.0015041,
          "pf": 0.0,
          "severe_pnl": -0.006495900000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "USELESS_USDT": {
          "gross_pnl": -0.0247632,
          "pf": 0.04009010704918237,
          "severe_pnl": -0.24476320000000007,
          "trades": 55,
          "win_rate": 0.03636363636363636
        },
        "USO_USDT": {
          "gross_pnl": -0.0013599,
          "pf": 0.0,
          "severe_pnl": -0.0053599,
          "trades": 1,
          "win_rate": 0.0
        },
        "USUAL_USDT": {
          "gross_pnl": 0.0016453999999999996,
          "pf": 0.0005196350911086335,
          "severe_pnl": -0.0463546,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "UVXY_USDT": {
          "gross_pnl": -0.0005467000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0165467,
          "trades": 4,
          "win_rate": 0.0
        },
        "VANRY_USDT": {
          "gross_pnl": 0.07287660000000001,
          "pf": 0.4211985412102952,
          "severe_pnl": -0.13512340000000003,
          "trades": 52,
          "win_rate": 0.28846153846153844
        },
        "VELO_USDT": {
          "gross_pnl": -0.012998800000000001,
          "pf": 0.0,
          "severe_pnl": -0.0329988,
          "trades": 5,
          "win_rate": 0.0
        },
        "VELVET_USDT": {
          "gross_pnl": 0.05358939999999998,
          "pf": 0.24250344306640498,
          "severe_pnl": -0.5384106000000003,
          "trades": 148,
          "win_rate": 0.20270270270270271
        },
        "VET_USDT": {
          "gross_pnl": 0.0023320000000000007,
          "pf": 0.0,
          "severe_pnl": -0.04166800000000001,
          "trades": 11,
          "win_rate": 0.0
        },
        "VINE_USDT": {
          "gross_pnl": -0.0370347,
          "pf": 0.0,
          "severe_pnl": -0.0690347,
          "trades": 8,
          "win_rate": 0.0
        },
        "VIRTUAL_USDT": {
          "gross_pnl": -0.012009800000000004,
          "pf": 0.013999946980467881,
          "severe_pnl": -0.4240098000000001,
          "trades": 103,
          "win_rate": 0.05825242718446602
        },
        "VVV_USDT": {
          "gross_pnl": 0.024661,
          "pf": 0.03463406574752257,
          "severe_pnl": -0.2553390000000001,
          "trades": 70,
          "win_rate": 0.02857142857142857
        },
        "WIF_USDT": {
          "gross_pnl": 0.011303699999999996,
          "pf": 0.03717688932164027,
          "severe_pnl": -0.29269629999999996,
          "trades": 76,
          "win_rate": 0.06578947368421052
        },
        "WLD_USDT": {
          "gross_pnl": -0.01898140000000001,
          "pf": 0.0015021366808926815,
          "severe_pnl": -0.5749814,
          "trades": 139,
          "win_rate": 0.007194244604316547
        },
        "WLFI_USDT": {
          "gross_pnl": -0.0013677999999999987,
          "pf": 0.0,
          "severe_pnl": -0.09336780000000001,
          "trades": 23,
          "win_rate": 0.0
        },
        "WOO_USDT": {
          "gross_pnl": -0.0015911,
          "pf": 0.0,
          "severe_pnl": -0.0055911,
          "trades": 1,
          "win_rate": 0.0
        },
        "W_USDT": {
          "gross_pnl": 0.0020462,
          "pf": 0.0,
          "severe_pnl": -0.0139538,
          "trades": 4,
          "win_rate": 0.0
        },
        "XAI_USDT": {
          "gross_pnl": -0.0169123,
          "pf": 0.0,
          "severe_pnl": -0.0369123,
          "trades": 5,
          "win_rate": 0.0
        },
        "XAN_USDT": {
          "gross_pnl": 0.0051126,
          "pf": 0.005250605989522244,
          "severe_pnl": -0.05088739999999999,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "XBI_USDT": {
          "gross_pnl": 0.008714900000000001,
          "pf": 0.005319954562665665,
          "severe_pnl": -0.0472851,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "XDC_USDT": {
          "gross_pnl": 0.0003685000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0076315,
          "trades": 2,
          "win_rate": 0.0
        },
        "XEC_USDT": {
          "gross_pnl": 0.0322374,
          "pf": 0.22467457274705446,
          "severe_pnl": -0.31576259999999995,
          "trades": 87,
          "win_rate": 0.1839080459770115
        },
        "XLM_USDT": {
          "gross_pnl": 0.018051300000000006,
          "pf": 0.011927465799205466,
          "severe_pnl": -0.26194870000000003,
          "trades": 70,
          "win_rate": 0.04285714285714286
        },
        "XLU_USDT": {
          "gross_pnl": 0.0156344,
          "pf": 0.6037720436743844,
          "severe_pnl": -0.004365599999999999,
          "trades": 5,
          "win_rate": 0.6
        },
        "XMR_USDT": {
          "gross_pnl": 0.009141799999999999,
          "pf": 0.0,
          "severe_pnl": -0.2948582,
          "trades": 76,
          "win_rate": 0.0
        },
        "XPIN_USDT": {
          "gross_pnl": 0.051641099999999995,
          "pf": 0.9036396941425744,
          "severe_pnl": -0.008358899999999996,
          "trades": 15,
          "win_rate": 0.2
        },
        "XPL_USDT": {
          "gross_pnl": 0.0250119,
          "pf": 0.04024379300118799,
          "severe_pnl": -0.3229881,
          "trades": 87,
          "win_rate": 0.034482758620689655
        },
        "XPT_USDT": {
          "gross_pnl": 0.008747099999999999,
          "pf": 0.0,
          "severe_pnl": -0.09125290000000001,
          "trades": 25,
          "win_rate": 0.0
        },
        "XRP_USDT": {
          "gross_pnl": 0.0034845000000000006,
          "pf": 0.0,
          "severe_pnl": -0.10451550000000003,
          "trades": 27,
          "win_rate": 0.0
        },
        "XTZ_USDT": {
          "gross_pnl": -0.0004706999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0164707,
          "trades": 4,
          "win_rate": 0.0
        },
        "XVS_USDT": {
          "gross_pnl": 0.0069364000000000006,
          "pf": 999,
          "severe_pnl": 0.0029364000000000005,
          "trades": 1,
          "win_rate": 1.0
        },
        "YFI_USDT": {
          "gross_pnl": -0.0013945999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0173946,
          "trades": 4,
          "win_rate": 0.0
        },
        "ZAMA_USDT": {
          "gross_pnl": 0.0002729000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0077271,
          "trades": 2,
          "win_rate": 0.0
        },
        "ZBT_USDT": {
          "gross_pnl": -0.021025300000000004,
          "pf": 0.08242848878004945,
          "severe_pnl": -0.3010253,
          "trades": 70,
          "win_rate": 0.08571428571428572
        },
        "ZEC_USDT": {
          "gross_pnl": 0.0270611,
          "pf": 0.036802643290066,
          "severe_pnl": -0.38893890000000014,
          "trades": 104,
          "win_rate": 0.057692307692307696
        },
        "ZEN_USDT": {
          "gross_pnl": 0.0042919,
          "pf": 0.02575149279585889,
          "severe_pnl": -0.0717081,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "ZEST_USDT": {
          "gross_pnl": -0.006893099999999999,
          "pf": 0.0,
          "severe_pnl": -0.0308931,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZETA_USDT": {
          "gross_pnl": -0.0005775,
          "pf": 0.0,
          "severe_pnl": -0.0045775,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZINC_USDT": {
          "gross_pnl": -0.0010873,
          "pf": 0.0,
          "severe_pnl": -0.0210873,
          "trades": 5,
          "win_rate": 0.0
        },
        "ZKC_USDT": {
          "gross_pnl": 0.00022429999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0037757,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZKP_USDT": {
          "gross_pnl": 0.0082413,
          "pf": 0.13110578115954016,
          "severe_pnl": -0.0157587,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "ZKSYNC_USDT": {
          "gross_pnl": -0.0306726,
          "pf": 0.0,
          "severe_pnl": -0.10667260000000002,
          "trades": 19,
          "win_rate": 0.0
        },
        "ZORA_USDT": {
          "gross_pnl": -0.0029619,
          "pf": 0.07463558731195018,
          "severe_pnl": -0.0229619,
          "trades": 5,
          "win_rate": 0.2
        },
        "ZRO_USDT": {
          "gross_pnl": -0.007300999999999998,
          "pf": 0.02338774234936763,
          "severe_pnl": -0.21130100000000002,
          "trades": 51,
          "win_rate": 0.058823529411764705
        },
        "ZRX_USDT": {
          "gross_pnl": 5.200000000000126e-06,
          "pf": 0.0,
          "severe_pnl": -0.0199948,
          "trades": 5,
          "win_rate": 0.0
        }
      },
      "validation_depth_quartiles": [
        {
          "gross_pnl": 0.2212654999999995,
          "pf": 0.2324491945306567,
          "quartile": 1,
          "severe_pnl": -10.854734499999987,
          "trades": 2769,
          "upper": 8976.76524,
          "win_rate": 0.15890213073311665
        },
        {
          "gross_pnl": -0.5634687999999997,
          "pf": 0.08460506614369895,
          "quartile": 2,
          "severe_pnl": -12.68346879999992,
          "trades": 3030,
          "upper": 106972.33601999999,
          "win_rate": 0.08811881188118811
        },
        {
          "gross_pnl": -0.01861409999999986,
          "pf": 0.08417530148881101,
          "quartile": 3,
          "severe_pnl": -11.798614099999947,
          "trades": 2945,
          "upper": 1071304.435,
          "win_rate": 0.07402376910016978
        },
        {
          "gross_pnl": -0.1332443999999998,
          "pf": 0.02583100722597517,
          "quartile": 4,
          "severe_pnl": -11.337244399999904,
          "trades": 2801,
          "upper": null,
          "win_rate": 0.03570153516601214
        }
      ],
      "validation_pass": false,
      "validation_skips": {
        "invalid_path_json": 0,
        "missing_horizon_path": 19,
        "structure_not_selected": 76090,
        "symbol_cooldown": 3646
      },
      "validation_spread_quartiles": [
        {
          "gross_pnl": -0.0004797000000001908,
          "pf": 0.058713988624608277,
          "quartile": 1,
          "severe_pnl": -12.104479699999965,
          "trades": 3026,
          "upper": 2.148689299527946,
          "win_rate": 0.05386649041639128
        },
        {
          "gross_pnl": -0.005208899999999998,
          "pf": 0.08755681618401577,
          "quartile": 2,
          "severe_pnl": -11.353208899999958,
          "trades": 2837,
          "upper": 4.268032437045758,
          "win_rate": 0.07966161438138879
        },
        {
          "gross_pnl": 0.11163040000000014,
          "pf": 0.10456552561286737,
          "quartile": 3,
          "severe_pnl": -11.484369599999924,
          "trades": 2899,
          "upper": 7.482229704451622,
          "win_rate": 0.0921007243877199
        },
        {
          "gross_pnl": -0.6000035999999982,
          "pf": 0.18477100448988162,
          "quartile": 4,
          "severe_pnl": -11.7320035999999,
          "trades": 2783,
          "upper": null,
          "win_rate": 0.1325907294286741
        }
      ]
    },
    {
      "direction": "continuation",
      "horizon_seconds": 300,
      "leave_best_symbol": -47.956901499999894,
      "structure": "confirm",
      "validation": {
        "gross_pnl": -1.6425674999999946,
        "pf": 0.26843332242823176,
        "severe_pnl": -47.79456749999989,
        "trades": 11538,
        "win_rate": 0.16970012133818685
      },
      "validation_by_symbol": {
        "0G_USDT": {
          "gross_pnl": -0.021992600000000005,
          "pf": 0.16997992725516528,
          "severe_pnl": -0.10999260000000002,
          "trades": 22,
          "win_rate": 0.18181818181818182
        },
        "1000000BABYDOGE_USDT": {
          "gross_pnl": -0.025412900000000002,
          "pf": 0.0,
          "severe_pnl": -0.0454129,
          "trades": 5,
          "win_rate": 0.0
        },
        "1000BONK_USDT": {
          "gross_pnl": -0.03242269999999999,
          "pf": 0.09599126374405445,
          "severe_pnl": -0.22442270000000003,
          "trades": 48,
          "win_rate": 0.125
        },
        "1INCH_USDT": {
          "gross_pnl": -0.0044112000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0084112,
          "trades": 1,
          "win_rate": 0.0
        },
        "2Z_USDT": {
          "gross_pnl": -0.016876000000000002,
          "pf": 0.0,
          "severe_pnl": -0.024876000000000002,
          "trades": 2,
          "win_rate": 0.0
        },
        "4_USDT": {
          "gross_pnl": -0.013268899999999998,
          "pf": 0.0,
          "severe_pnl": -0.0372689,
          "trades": 6,
          "win_rate": 0.0
        },
        "AAVE_USDT": {
          "gross_pnl": 0.0024524000000000017,
          "pf": 0.022789320239917407,
          "severe_pnl": -0.16554760000000004,
          "trades": 42,
          "win_rate": 0.07142857142857142
        },
        "ACE_USDT": {
          "gross_pnl": 0.0857396,
          "pf": 999,
          "severe_pnl": 0.0817396,
          "trades": 1,
          "win_rate": 1.0
        },
        "ACT_USDT": {
          "gross_pnl": -0.0048378,
          "pf": 0.0,
          "severe_pnl": -0.0168378,
          "trades": 3,
          "win_rate": 0.0
        },
        "ACU_USDT": {
          "gross_pnl": 0.0199946,
          "pf": 2.423389395667046,
          "severe_pnl": 0.003994599999999999,
          "trades": 4,
          "win_rate": 0.75
        },
        "ADA_USDT": {
          "gross_pnl": -0.01704770000000001,
          "pf": 0.024672062140744595,
          "severe_pnl": -0.2890477000000001,
          "trades": 68,
          "win_rate": 0.04411764705882353
        },
        "AERGO_USDT": {
          "gross_pnl": 0.1213724,
          "pf": 21.265306565382524,
          "severe_pnl": 0.09337239999999998,
          "trades": 7,
          "win_rate": 0.7142857142857143
        },
        "AERO_USDT": {
          "gross_pnl": -0.007168200000000002,
          "pf": 0.11503565429093725,
          "severe_pnl": -0.1791682,
          "trades": 43,
          "win_rate": 0.18604651162790697
        },
        "AEVO_USDT": {
          "gross_pnl": 0.0099738,
          "pf": 999,
          "severe_pnl": 0.0059738,
          "trades": 1,
          "win_rate": 1.0
        },
        "AGI_USDT": {
          "gross_pnl": -0.0048714,
          "pf": 0.0,
          "severe_pnl": -0.0168714,
          "trades": 3,
          "win_rate": 0.0
        },
        "AGLD_USDT": {
          "gross_pnl": 0.032169100000000006,
          "pf": 0.7709937110326953,
          "severe_pnl": -0.011830899999999997,
          "trades": 11,
          "win_rate": 0.2727272727272727
        },
        "AGT_USDT": {
          "gross_pnl": -0.018707699999999997,
          "pf": 0.0,
          "severe_pnl": -0.026707699999999997,
          "trades": 2,
          "win_rate": 0.0
        },
        "AIGENSYN_USDT": {
          "gross_pnl": 0.0502963,
          "pf": 0.5789092414364068,
          "severe_pnl": -0.029703700000000006,
          "trades": 20,
          "win_rate": 0.4
        },
        "AIOT_USDT": {
          "gross_pnl": 0.07989770000000003,
          "pf": 0.6739264088858187,
          "severe_pnl": -0.0961023,
          "trades": 44,
          "win_rate": 0.29545454545454547
        },
        "AIOZ_USDT": {
          "gross_pnl": -0.0011874,
          "pf": 0.0,
          "severe_pnl": -0.0051874,
          "trades": 1,
          "win_rate": 0.0
        },
        "AIO_USDT": {
          "gross_pnl": -0.022553000000000004,
          "pf": 0.0,
          "severe_pnl": -0.030553000000000004,
          "trades": 2,
          "win_rate": 0.0
        },
        "AKE_USDT": {
          "gross_pnl": 0.09721220000000003,
          "pf": 0.8331395249175,
          "severe_pnl": -0.19078780000000012,
          "trades": 72,
          "win_rate": 0.375
        },
        "AKT_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "ALCH_USDT": {
          "gross_pnl": -0.09244709999999998,
          "pf": 0.14734339616620576,
          "severe_pnl": -0.2244471,
          "trades": 33,
          "win_rate": 0.15151515151515152
        },
        "ALGO_USDT": {
          "gross_pnl": -0.015350299999999999,
          "pf": 0.02353099719951284,
          "severe_pnl": -0.17535030000000007,
          "trades": 40,
          "win_rate": 0.025
        },
        "ALLO_USDT": {
          "gross_pnl": -0.010064699999999921,
          "pf": 0.26786487968138933,
          "severe_pnl": -0.6980646999999998,
          "trades": 172,
          "win_rate": 0.23255813953488372
        },
        "ALPINE_USDT": {
          "gross_pnl": 0.007778500000000001,
          "pf": 999,
          "severe_pnl": 0.0037785000000000006,
          "trades": 1,
          "win_rate": 1.0
        },
        "ALT_USDT": {
          "gross_pnl": -0.012739,
          "pf": 0.0,
          "severe_pnl": -0.044739,
          "trades": 8,
          "win_rate": 0.0
        },
        "ANKR_USDT": {
          "gross_pnl": 0.005862099999999999,
          "pf": 0.0,
          "severe_pnl": -0.010137900000000002,
          "trades": 4,
          "win_rate": 0.0
        },
        "ANSEM_USDT": {
          "gross_pnl": -0.21949529999999992,
          "pf": 0.41129699572354883,
          "severe_pnl": -0.8074952999999999,
          "trades": 147,
          "win_rate": 0.38095238095238093
        },
        "ANTHROPIC_USDT": {
          "gross_pnl": -0.0063089,
          "pf": 0.0,
          "severe_pnl": -0.06230890000000001,
          "trades": 14,
          "win_rate": 0.0
        },
        "APE_USDT": {
          "gross_pnl": -0.029989099999999998,
          "pf": 0.002937757852115824,
          "severe_pnl": -0.2419891,
          "trades": 53,
          "win_rate": 0.03773584905660377
        },
        "APR_USDT": {
          "gross_pnl": -0.0037843,
          "pf": 0.0,
          "severe_pnl": -0.0077843,
          "trades": 1,
          "win_rate": 0.0
        },
        "APT_USDT": {
          "gross_pnl": -0.05891539999999999,
          "pf": 0.0,
          "severe_pnl": -0.3269153999999999,
          "trades": 67,
          "win_rate": 0.0
        },
        "ARB_USDT": {
          "gross_pnl": 0.0220278,
          "pf": 0.13626626939097458,
          "severe_pnl": -0.5619722,
          "trades": 146,
          "win_rate": 0.1643835616438356
        },
        "ARCSOL_USDT": {
          "gross_pnl": -0.0198683,
          "pf": 0.0,
          "severe_pnl": -0.0278683,
          "trades": 2,
          "win_rate": 0.0
        },
        "ARKK_USDT": {
          "gross_pnl": -0.0156774,
          "pf": 0.0,
          "severe_pnl": -0.0236774,
          "trades": 2,
          "win_rate": 0.0
        },
        "ARKM_USDT": {
          "gross_pnl": 0.0199449,
          "pf": 0.07103787112010798,
          "severe_pnl": -0.0440551,
          "trades": 16,
          "win_rate": 0.1875
        },
        "ARX_USDT": {
          "gross_pnl": -0.028649300000000006,
          "pf": 0.1675511901552697,
          "severe_pnl": -0.18064930000000004,
          "trades": 38,
          "win_rate": 0.18421052631578946
        },
        "AR_USDT": {
          "gross_pnl": -0.0009320000000000014,
          "pf": 0.010682867766026968,
          "severe_pnl": -0.036932,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "ASTEROID_USDT": {
          "gross_pnl": 0.0416667,
          "pf": 999,
          "severe_pnl": 0.0376667,
          "trades": 1,
          "win_rate": 1.0
        },
        "ASTER_USDT": {
          "gross_pnl": -0.0252722,
          "pf": 0.0,
          "severe_pnl": -0.17727220000000002,
          "trades": 38,
          "win_rate": 0.0
        },
        "ATH_USDT": {
          "gross_pnl": -0.0121953,
          "pf": 0.0,
          "severe_pnl": -0.0201953,
          "trades": 2,
          "win_rate": 0.0
        },
        "ATOM_USDT": {
          "gross_pnl": -0.011717199999999999,
          "pf": 0.0025928736414174668,
          "severe_pnl": -0.1677172,
          "trades": 39,
          "win_rate": 0.02564102564102564
        },
        "AVAAI_USDT": {
          "gross_pnl": 0.056195499999999995,
          "pf": 2.488347379178577,
          "severe_pnl": 0.0401955,
          "trades": 4,
          "win_rate": 0.5
        },
        "AVAX_USDT": {
          "gross_pnl": 0.0165764,
          "pf": 0.15756431721223849,
          "severe_pnl": -0.04342359999999999,
          "trades": 15,
          "win_rate": 0.2
        },
        "AVNT_USDT": {
          "gross_pnl": -0.015057000000000001,
          "pf": 0.016204740714193273,
          "severe_pnl": -0.07905700000000002,
          "trades": 16,
          "win_rate": 0.0625
        },
        "AWE_USDT": {
          "gross_pnl": 0.008846800000000002,
          "pf": 0.7880885495772794,
          "severe_pnl": -0.0031531999999999992,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "AXL_USDT": {
          "gross_pnl": 0.0046598,
          "pf": 999,
          "severe_pnl": 0.0006598000000000003,
          "trades": 1,
          "win_rate": 1.0
        },
        "AXS_USDT": {
          "gross_pnl": 0.0023566000000000004,
          "pf": 0.1418733329991409,
          "severe_pnl": -0.049643400000000004,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "A_USDT": {
          "gross_pnl": -0.0008489999999999999,
          "pf": 0.0,
          "severe_pnl": -0.016849,
          "trades": 4,
          "win_rate": 0.0
        },
        "B2_USDT": {
          "gross_pnl": -0.0252587,
          "pf": 0.0,
          "severe_pnl": -0.0372587,
          "trades": 3,
          "win_rate": 0.0
        },
        "B3_USDT": {
          "gross_pnl": -0.061549099999999995,
          "pf": 0.33443931367813173,
          "severe_pnl": -0.09754909999999999,
          "trades": 9,
          "win_rate": 0.3333333333333333
        },
        "BABY_USDT": {
          "gross_pnl": 0.008914,
          "pf": 0.07437631149452088,
          "severe_pnl": -0.015086,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "BANANAS31_USDT": {
          "gross_pnl": 0.0059343,
          "pf": 0.41737585246374026,
          "severe_pnl": -0.006065699999999999,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "BANANA_USDT": {
          "gross_pnl": -0.0060489,
          "pf": 0.0,
          "severe_pnl": -0.0140489,
          "trades": 2,
          "win_rate": 0.0
        },
        "BAND_USDT": {
          "gross_pnl": -0.0254934,
          "pf": 0.0,
          "severe_pnl": -0.037493399999999996,
          "trades": 3,
          "win_rate": 0.0
        },
        "BANK_USDT": {
          "gross_pnl": 0.46339960000000013,
          "pf": 1.2151958776884053,
          "severe_pnl": 0.14739960000000002,
          "trades": 79,
          "win_rate": 0.4430379746835443
        },
        "BAN_USDT": {
          "gross_pnl": 0.0011243999999999994,
          "pf": 0.00847180840781991,
          "severe_pnl": -0.014875600000000001,
          "trades": 4,
          "win_rate": 0.25
        },
        "BASED_USDT": {
          "gross_pnl": 0.009404499999999998,
          "pf": 0.27734096124807656,
          "severe_pnl": -0.0905955,
          "trades": 25,
          "win_rate": 0.2
        },
        "BAS_USDT": {
          "gross_pnl": -0.0168091,
          "pf": 0.3264416726090972,
          "severe_pnl": -0.028809099999999997,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "BAT_USDT": {
          "gross_pnl": 0.0038788999999999994,
          "pf": 0.03664510736259369,
          "severe_pnl": -0.0281211,
          "trades": 8,
          "win_rate": 0.125
        },
        "BCH_USDT": {
          "gross_pnl": 0.007552800000000001,
          "pf": 0.06060344791505353,
          "severe_pnl": -0.22444720000000007,
          "trades": 58,
          "win_rate": 0.06896551724137931
        },
        "BEAT_USDT": {
          "gross_pnl": 0.20459980000000003,
          "pf": 0.32616015413290644,
          "severe_pnl": -0.5754002,
          "trades": 195,
          "win_rate": 0.26666666666666666
        },
        "BERA_USDT": {
          "gross_pnl": 0.0008866999999999998,
          "pf": 0.0,
          "severe_pnl": -0.015113300000000001,
          "trades": 4,
          "win_rate": 0.0
        },
        "BIANRENSHENG_USDT": {
          "gross_pnl": -0.0018465999999999997,
          "pf": 0.22241128538616622,
          "severe_pnl": -0.0138466,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "BICO_USDT": {
          "gross_pnl": -0.0006420000000000002,
          "pf": 0.10722640933324254,
          "severe_pnl": -0.040642,
          "trades": 10,
          "win_rate": 0.2
        },
        "BIGTIME_USDT": {
          "gross_pnl": -0.00044080000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0044408,
          "trades": 1,
          "win_rate": 0.0
        },
        "BILL_USDT": {
          "gross_pnl": 0.03408579999999998,
          "pf": 0.4225361500617404,
          "severe_pnl": -0.6099142000000002,
          "trades": 161,
          "win_rate": 0.2608695652173913
        },
        "BIO_USDT": {
          "gross_pnl": -0.006026200000000001,
          "pf": 0.0,
          "severe_pnl": -0.0100262,
          "trades": 1,
          "win_rate": 0.0
        },
        "BLAST_USDT": {
          "gross_pnl": -0.0430397,
          "pf": 0.49766726268255157,
          "severe_pnl": -0.1590397,
          "trades": 29,
          "win_rate": 0.3793103448275862
        },
        "BLEND_USDT": {
          "gross_pnl": -0.014131,
          "pf": 0.0,
          "severe_pnl": -0.042131,
          "trades": 7,
          "win_rate": 0.0
        },
        "BLESS_USDT": {
          "gross_pnl": -0.06334899999999999,
          "pf": 0.08288912784178709,
          "severe_pnl": -0.25134899999999993,
          "trades": 47,
          "win_rate": 0.1702127659574468
        },
        "BLUAI_USDT": {
          "gross_pnl": 0.1666063,
          "pf": 6.032433394087704,
          "severe_pnl": 0.13860630000000002,
          "trades": 7,
          "win_rate": 0.7142857142857143
        },
        "BLUR_USDT": {
          "gross_pnl": 0.0011806,
          "pf": 0.0,
          "severe_pnl": -0.0108194,
          "trades": 3,
          "win_rate": 0.0
        },
        "BNB_USDT": {
          "gross_pnl": 0.0023318000000000032,
          "pf": 0.0,
          "severe_pnl": -0.08966820000000002,
          "trades": 23,
          "win_rate": 0.0
        },
        "BRETT_USDT": {
          "gross_pnl": -0.027615799999999996,
          "pf": 0.04079708962879191,
          "severe_pnl": -0.08761580000000002,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "BREV_USDT": {
          "gross_pnl": -0.0070123,
          "pf": 0.0,
          "severe_pnl": -0.0270123,
          "trades": 5,
          "win_rate": 0.0
        },
        "BSB_USDT": {
          "gross_pnl": -0.23528580000000002,
          "pf": 0.17857314820541823,
          "severe_pnl": -0.8512858000000001,
          "trades": 154,
          "win_rate": 0.18831168831168832
        },
        "BSV_USDT": {
          "gross_pnl": -0.004493599999999999,
          "pf": 0.09998021866158131,
          "severe_pnl": -0.040493600000000005,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "BTW_USDT": {
          "gross_pnl": -0.0313114,
          "pf": 0.23349085740544806,
          "severe_pnl": -0.1793114000000001,
          "trades": 37,
          "win_rate": 0.13513513513513514
        },
        "BUILDONBOB_USDT": {
          "gross_pnl": -0.030953899999999996,
          "pf": 0.0,
          "severe_pnl": -0.042953899999999996,
          "trades": 3,
          "win_rate": 0.0
        },
        "BULLA_USDT": {
          "gross_pnl": 0.08074989999999999,
          "pf": 0.9568027312213634,
          "severe_pnl": -0.007250099999999996,
          "trades": 22,
          "win_rate": 0.2727272727272727
        },
        "CAKE_USDT": {
          "gross_pnl": -0.0064434,
          "pf": 0.09736568435424496,
          "severe_pnl": -0.042443400000000006,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "CAP_USDT": {
          "gross_pnl": -0.012923400000000002,
          "pf": 0.19240683710789977,
          "severe_pnl": -0.21692340000000002,
          "trades": 51,
          "win_rate": 0.21568627450980393
        },
        "CARV_USDT": {
          "gross_pnl": -0.0098522,
          "pf": 0.0,
          "severe_pnl": -0.0138522,
          "trades": 1,
          "win_rate": 0.0
        },
        "CASHCAT_USDT": {
          "gross_pnl": -0.1727264,
          "pf": 0.3709222604840178,
          "severe_pnl": -0.2727264,
          "trades": 25,
          "win_rate": 0.32
        },
        "CATI_USDT": {
          "gross_pnl": -0.0159088,
          "pf": 0.0,
          "severe_pnl": -0.0239088,
          "trades": 2,
          "win_rate": 0.0
        },
        "CC_USDT": {
          "gross_pnl": 0.023295200000000005,
          "pf": 0.5076587717964505,
          "severe_pnl": -0.032704800000000006,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "CFX_USDT": {
          "gross_pnl": -0.0003235999999999994,
          "pf": 0.0,
          "severe_pnl": -0.028323599999999997,
          "trades": 7,
          "win_rate": 0.0
        },
        "CHEEMS_USDT": {
          "gross_pnl": 0.0017571000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0022429,
          "trades": 1,
          "win_rate": 0.0
        },
        "CHIP_USDT": {
          "gross_pnl": -0.0023191,
          "pf": 0.03982219485491851,
          "severe_pnl": -0.1503191,
          "trades": 37,
          "win_rate": 0.08108108108108109
        },
        "CHR_USDT": {
          "gross_pnl": 0.08054510000000001,
          "pf": 9.522224018102472,
          "severe_pnl": 0.0685451,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "CHZ_USDT": {
          "gross_pnl": -0.006335,
          "pf": 0.017505563600121118,
          "severe_pnl": -0.12233499999999997,
          "trades": 29,
          "win_rate": 0.10344827586206896
        },
        "CKB_USDT": {
          "gross_pnl": 0.0064623,
          "pf": 0.47127187704157053,
          "severe_pnl": -0.0015377000000000004,
          "trades": 2,
          "win_rate": 0.5
        },
        "CLO_USDT": {
          "gross_pnl": -0.0035674999999999873,
          "pf": 0.7435559714402543,
          "severe_pnl": -0.019567499999999988,
          "trades": 4,
          "win_rate": 0.25
        },
        "COAI_USDT": {
          "gross_pnl": 0.0043144,
          "pf": 0.1267895578621171,
          "severe_pnl": -0.0716856,
          "trades": 19,
          "win_rate": 0.2631578947368421
        },
        "COLLECT_USDT": {
          "gross_pnl": -0.0389857,
          "pf": 0.06692711505440141,
          "severe_pnl": -0.09498570000000002,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "COMP_USDT": {
          "gross_pnl": -0.0011765999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0091766,
          "trades": 2,
          "win_rate": 0.0
        },
        "COTI_USDT": {
          "gross_pnl": -0.0026076,
          "pf": 0.0,
          "severe_pnl": -0.0066076,
          "trades": 1,
          "win_rate": 0.0
        },
        "CROSS_USDT": {
          "gross_pnl": -0.0037559,
          "pf": 0.0,
          "severe_pnl": -0.0197559,
          "trades": 4,
          "win_rate": 0.0
        },
        "CRO_USDT": {
          "gross_pnl": 0.05007789999999999,
          "pf": 0.44526966928455364,
          "severe_pnl": -0.0659221,
          "trades": 29,
          "win_rate": 0.27586206896551724
        },
        "CRV_USDT": {
          "gross_pnl": 0.012978999999999992,
          "pf": 0.09482828810712653,
          "severe_pnl": -0.239021,
          "trades": 63,
          "win_rate": 0.15873015873015872
        },
        "CTC_USDT": {
          "gross_pnl": -0.0028973000000000007,
          "pf": 0.0,
          "severe_pnl": -0.038897299999999996,
          "trades": 9,
          "win_rate": 0.0
        },
        "CVX_USDT": {
          "gross_pnl": -0.0006053999999999999,
          "pf": 0.003360144125393011,
          "severe_pnl": -0.0406054,
          "trades": 10,
          "win_rate": 0.2
        },
        "CYS_USDT": {
          "gross_pnl": -0.0102117,
          "pf": 0.12061630981773942,
          "severe_pnl": -0.0662117,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "DASH_USDT": {
          "gross_pnl": -0.012046100000000004,
          "pf": 0.021811851018710224,
          "severe_pnl": -0.2960460999999999,
          "trades": 71,
          "win_rate": 0.07042253521126761
        },
        "DEEP_USDT": {
          "gross_pnl": 9.399999999999903e-06,
          "pf": 0.0,
          "severe_pnl": -0.0079906,
          "trades": 2,
          "win_rate": 0.0
        },
        "DEXE_USDT": {
          "gross_pnl": -0.17690519999999987,
          "pf": 0.27225362141728526,
          "severe_pnl": -0.7009051999999998,
          "trades": 131,
          "win_rate": 0.2595419847328244
        },
        "DODO_USDT": {
          "gross_pnl": 0.2090999000000001,
          "pf": 0.8180652072123095,
          "severe_pnl": -0.12290009999999998,
          "trades": 83,
          "win_rate": 0.40963855421686746
        },
        "DOGE_USDT": {
          "gross_pnl": 0.009012599999999996,
          "pf": 0.03170024905398789,
          "severe_pnl": -0.27098740000000004,
          "trades": 70,
          "win_rate": 0.08571428571428572
        },
        "DOGS_USDT": {
          "gross_pnl": 0.0019606,
          "pf": 0.0,
          "severe_pnl": -0.0220394,
          "trades": 6,
          "win_rate": 0.0
        },
        "DOT_USDT": {
          "gross_pnl": -0.04166159999999999,
          "pf": 0.0,
          "severe_pnl": -0.41366160000000013,
          "trades": 93,
          "win_rate": 0.0
        },
        "DRAM_USDT": {
          "gross_pnl": 0.005098399999999994,
          "pf": 0.11318870224414952,
          "severe_pnl": -0.18690160000000006,
          "trades": 48,
          "win_rate": 0.1875
        },
        "DUSK_USDT": {
          "gross_pnl": -0.001822,
          "pf": 0.0,
          "severe_pnl": -0.005822,
          "trades": 1,
          "win_rate": 0.0
        },
        "DYDX_USDT": {
          "gross_pnl": -0.005420899999999999,
          "pf": 0.0,
          "severe_pnl": -0.0414209,
          "trades": 9,
          "win_rate": 0.0
        },
        "EDEN_USDT": {
          "gross_pnl": -0.011693399999999998,
          "pf": 0.02709294877059279,
          "severe_pnl": -0.0236934,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "EDGE_USDT": {
          "gross_pnl": -0.11006769999999999,
          "pf": 0.1608016825123373,
          "severe_pnl": -0.4780677000000002,
          "trades": 92,
          "win_rate": 0.13043478260869565
        },
        "EDU_USDT": {
          "gross_pnl": 0.0028529999999999996,
          "pf": 0.0,
          "severe_pnl": -0.017147000000000003,
          "trades": 5,
          "win_rate": 0.0
        },
        "EGLD_USDT": {
          "gross_pnl": -0.04302969999999998,
          "pf": 0.07292486128027392,
          "severe_pnl": -0.3310297,
          "trades": 72,
          "win_rate": 0.16666666666666666
        },
        "EIGEN_USDT": {
          "gross_pnl": -0.03179100000000001,
          "pf": 0.06445203533856916,
          "severe_pnl": -0.375791,
          "trades": 86,
          "win_rate": 0.12790697674418605
        },
        "ELSA_USDT": {
          "gross_pnl": -0.05016799999999999,
          "pf": 0.15862892939599915,
          "severe_pnl": -0.078168,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "ENA_USDT": {
          "gross_pnl": -0.03620140000000002,
          "pf": 0.03829087831148714,
          "severe_pnl": -0.3162014,
          "trades": 70,
          "win_rate": 0.02857142857142857
        },
        "ENJ_USDT": {
          "gross_pnl": -0.014108800000000001,
          "pf": 0.0066377137955069354,
          "severe_pnl": -0.0741088,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "ENSO_USDT": {
          "gross_pnl": -0.0008935999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0128936,
          "trades": 3,
          "win_rate": 0.0
        },
        "ENS_USDT": {
          "gross_pnl": 0.0161113,
          "pf": 0.1241837015432239,
          "severe_pnl": -0.05188870000000001,
          "trades": 17,
          "win_rate": 0.17647058823529413
        },
        "EPIC_USDT": {
          "gross_pnl": -0.008046600000000001,
          "pf": 0.0,
          "severe_pnl": -0.012046600000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "ERA_USDT": {
          "gross_pnl": -0.0011718,
          "pf": 0.0,
          "severe_pnl": -0.0051718,
          "trades": 1,
          "win_rate": 0.0
        },
        "ESPORTS_USDT": {
          "gross_pnl": -0.001393899999999941,
          "pf": 0.6780124609582951,
          "severe_pnl": -0.4453939000000003,
          "trades": 111,
          "win_rate": 0.3783783783783784
        },
        "ESP_USDT": {
          "gross_pnl": -0.0048017,
          "pf": 0.0,
          "severe_pnl": -0.0128017,
          "trades": 2,
          "win_rate": 0.0
        },
        "ETC_USDT": {
          "gross_pnl": -0.0005571999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0885572,
          "trades": 22,
          "win_rate": 0.0
        },
        "ETHFI_USDT": {
          "gross_pnl": 0.004396499999999994,
          "pf": 0.08582915456481932,
          "severe_pnl": -0.3556035000000002,
          "trades": 90,
          "win_rate": 0.13333333333333333
        },
        "ETH_USDT": {
          "gross_pnl": 0.027804500000000006,
          "pf": 0.05052146080538516,
          "severe_pnl": -0.2681955,
          "trades": 74,
          "win_rate": 0.08108108108108109
        },
        "EUL_USDT": {
          "gross_pnl": -0.0062574,
          "pf": 0.0,
          "severe_pnl": -0.0142574,
          "trades": 2,
          "win_rate": 0.0
        },
        "EVAA_USDT": {
          "gross_pnl": 0.40019439999999995,
          "pf": 1.1788990762679854,
          "severe_pnl": 0.10419439999999995,
          "trades": 74,
          "win_rate": 0.47297297297297297
        },
        "EWY_USDT": {
          "gross_pnl": 0.016724200000000012,
          "pf": 0.023766789903449746,
          "severe_pnl": -0.27527579999999996,
          "trades": 73,
          "win_rate": 0.0821917808219178
        },
        "FET_USDT": {
          "gross_pnl": -0.0116708,
          "pf": 0.02591303383022802,
          "severe_pnl": -0.27567080000000005,
          "trades": 66,
          "win_rate": 0.045454545454545456
        },
        "FF_USDT": {
          "gross_pnl": -0.014091,
          "pf": 0.12402442329731585,
          "severe_pnl": -0.08209100000000001,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "FHE_USDT": {
          "gross_pnl": 0.02147960000000001,
          "pf": 0.3529288442513938,
          "severe_pnl": -0.1185204,
          "trades": 35,
          "win_rate": 0.34285714285714286
        },
        "FIGHT_USDT": {
          "gross_pnl": -0.0048,
          "pf": 0.0,
          "severe_pnl": -0.008799999999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "FILECOIN_USDT": {
          "gross_pnl": -0.025927900000000004,
          "pf": 0.007217929028936467,
          "severe_pnl": -0.15792789999999998,
          "trades": 33,
          "win_rate": 0.030303030303030304
        },
        "FLOCK_USDT": {
          "gross_pnl": -0.0028316000000000036,
          "pf": 0.23415163656506388,
          "severe_pnl": -0.030831600000000008,
          "trades": 7,
          "win_rate": 0.42857142857142855
        },
        "FLOKI_USDT": {
          "gross_pnl": -0.0036544000000000004,
          "pf": 0.04392873717938838,
          "severe_pnl": -0.11165439999999999,
          "trades": 27,
          "win_rate": 0.1111111111111111
        },
        "FLOW_USDT": {
          "gross_pnl": -0.0127841,
          "pf": 0.0,
          "severe_pnl": -0.0207841,
          "trades": 2,
          "win_rate": 0.0
        },
        "FLR_USDT": {
          "gross_pnl": -0.0015198,
          "pf": 0.0,
          "severe_pnl": -0.0055198,
          "trades": 1,
          "win_rate": 0.0
        },
        "FOGO_USDT": {
          "gross_pnl": -0.038189299999999995,
          "pf": 0.0,
          "severe_pnl": -0.0621893,
          "trades": 6,
          "win_rate": 0.0
        },
        "FOLKS_USDT": {
          "gross_pnl": 0.002311799999999996,
          "pf": 0.20968988254687818,
          "severe_pnl": -0.16568820000000004,
          "trades": 42,
          "win_rate": 0.23809523809523808
        },
        "FORM_USDT": {
          "gross_pnl": -0.0024907,
          "pf": 0.0,
          "severe_pnl": -0.0104907,
          "trades": 2,
          "win_rate": 0.0
        },
        "FRAX_USDT": {
          "gross_pnl": 0.0049261,
          "pf": 999,
          "severe_pnl": 0.0009261,
          "trades": 1,
          "win_rate": 1.0
        },
        "F_USDT": {
          "gross_pnl": 0.0027466,
          "pf": 0.0,
          "severe_pnl": -0.0052534,
          "trades": 2,
          "win_rate": 0.0
        },
        "GALA_USDT": {
          "gross_pnl": -0.04210189999999999,
          "pf": 0.014595792420655576,
          "severe_pnl": -0.3581018999999998,
          "trades": 79,
          "win_rate": 0.05063291139240506
        },
        "GAS_USDT": {
          "gross_pnl": -0.0039977,
          "pf": 0.0,
          "severe_pnl": -0.0119977,
          "trades": 2,
          "win_rate": 0.0
        },
        "GENIUS_USDT": {
          "gross_pnl": 0.0028708000000000015,
          "pf": 0.5020671750062724,
          "severe_pnl": -0.009129199999999999,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "GIGGLE_USDT": {
          "gross_pnl": 0.0031449,
          "pf": 0.27851875992993036,
          "severe_pnl": -0.0088551,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "GLM_USDT": {
          "gross_pnl": -0.0019919,
          "pf": 0.0,
          "severe_pnl": -0.013991900000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "GOAT_USDT": {
          "gross_pnl": -0.0082769,
          "pf": 0.0,
          "severe_pnl": -0.0122769,
          "trades": 1,
          "win_rate": 0.0
        },
        "GPS_USDT": {
          "gross_pnl": -0.0178325,
          "pf": 0.022196184650344144,
          "severe_pnl": -0.057832499999999995,
          "trades": 10,
          "win_rate": 0.2
        },
        "GRAM_USDT": {
          "gross_pnl": -0.025200100000000003,
          "pf": 0.03523369833236777,
          "severe_pnl": -0.16120009999999999,
          "trades": 34,
          "win_rate": 0.08823529411764706
        },
        "GRASS_USDT": {
          "gross_pnl": -0.008485000000000001,
          "pf": 0.12119289340101522,
          "severe_pnl": -0.084485,
          "trades": 19,
          "win_rate": 0.2631578947368421
        },
        "GRT_USDT": {
          "gross_pnl": -0.0028883000000000003,
          "pf": 0.015250390927104082,
          "severe_pnl": -0.0348883,
          "trades": 8,
          "win_rate": 0.125
        },
        "GUA_USDT": {
          "gross_pnl": 0.0031747000000000025,
          "pf": 0.6126196119743658,
          "severe_pnl": -0.008825300000000001,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "GUN_USDT": {
          "gross_pnl": 0.009234,
          "pf": 0.4522786709844422,
          "severe_pnl": -0.030765999999999998,
          "trades": 10,
          "win_rate": 0.2
        },
        "G_USDT": {
          "gross_pnl": -0.1138305,
          "pf": 0.13766118452422374,
          "severe_pnl": -0.13383050000000002,
          "trades": 5,
          "win_rate": 0.2
        },
        "HBAR_USDT": {
          "gross_pnl": -0.025853499999999998,
          "pf": 0.0006098586810228781,
          "severe_pnl": -0.2138535,
          "trades": 47,
          "win_rate": 0.02127659574468085
        },
        "HEI_USDT": {
          "gross_pnl": 0.006599299999999997,
          "pf": 0.25017563040848606,
          "severe_pnl": -0.19340070000000004,
          "trades": 50,
          "win_rate": 0.22
        },
        "HIGH_USDT": {
          "gross_pnl": 0.024645499999999997,
          "pf": 0.5671112343743359,
          "severe_pnl": -0.0193545,
          "trades": 11,
          "win_rate": 0.36363636363636365
        },
        "HK50_USDT": {
          "gross_pnl": 0.003820200000000002,
          "pf": 0.06978666820835981,
          "severe_pnl": -0.0321798,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "HMSTR_USDT": {
          "gross_pnl": -0.029583800000000004,
          "pf": 0.2716349952459389,
          "severe_pnl": -0.08158380000000001,
          "trades": 13,
          "win_rate": 0.15384615384615385
        },
        "HNT_USDT": {
          "gross_pnl": -0.006541100000000001,
          "pf": 0.0,
          "severe_pnl": -0.0305411,
          "trades": 6,
          "win_rate": 0.0
        },
        "HOLO_USDT": {
          "gross_pnl": -0.0061683,
          "pf": 0.0,
          "severe_pnl": -0.026168300000000002,
          "trades": 5,
          "win_rate": 0.0
        },
        "HOME_USDT": {
          "gross_pnl": 0.0779163,
          "pf": 0.574372067746203,
          "severe_pnl": -0.0780837,
          "trades": 39,
          "win_rate": 0.38461538461538464
        },
        "HOT_USDT": {
          "gross_pnl": -0.006722500000000001,
          "pf": 0.0,
          "severe_pnl": -0.018722500000000003,
          "trades": 3,
          "win_rate": 0.0
        },
        "HYPE_USDT": {
          "gross_pnl": -0.027180999999999997,
          "pf": 0.0,
          "severe_pnl": -0.191181,
          "trades": 41,
          "win_rate": 0.0
        },
        "ICNT_USDT": {
          "gross_pnl": -0.010165200000000001,
          "pf": 0.0,
          "severe_pnl": -0.014165200000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "ICP_USDT": {
          "gross_pnl": 0.016158200000000008,
          "pf": 0.025115206640369724,
          "severe_pnl": -0.2758418,
          "trades": 73,
          "win_rate": 0.0684931506849315
        },
        "ICX_USDT": {
          "gross_pnl": 0.0034204,
          "pf": 0.0,
          "severe_pnl": -0.0045796,
          "trades": 2,
          "win_rate": 0.0
        },
        "ID_USDT": {
          "gross_pnl": 0.004014900000000001,
          "pf": 0.035466529318031875,
          "severe_pnl": -0.011985099999999999,
          "trades": 4,
          "win_rate": 0.25
        },
        "IMX_USDT": {
          "gross_pnl": -0.012926700000000001,
          "pf": 0.011373037227420573,
          "severe_pnl": -0.03692670000000001,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "INDA_USDT": {
          "gross_pnl": -0.0081903,
          "pf": 0.08943997827575086,
          "severe_pnl": -0.032190300000000005,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "INJ_USDT": {
          "gross_pnl": -0.03359400000000002,
          "pf": 0.01872775524924454,
          "severe_pnl": -0.44159399999999976,
          "trades": 102,
          "win_rate": 0.0392156862745098
        },
        "INTW_USDT": {
          "gross_pnl": 0.0275292,
          "pf": 3.575765968952373,
          "severe_pnl": 0.019529199999999997,
          "trades": 2,
          "win_rate": 0.5
        },
        "INX_USDT": {
          "gross_pnl": 0.0013262999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0026737,
          "trades": 1,
          "win_rate": 0.0
        },
        "IN_USDT": {
          "gross_pnl": 0.0072495,
          "pf": 0.812375,
          "severe_pnl": -0.0007505000000000003,
          "trades": 2,
          "win_rate": 0.5
        },
        "IOST_USDT": {
          "gross_pnl": -0.0016389,
          "pf": 0.0,
          "severe_pnl": -0.0056389000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTA_USDT": {
          "gross_pnl": 0.0038223000000000003,
          "pf": 0.0,
          "severe_pnl": -0.00017769999999999982,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTX_USDT": {
          "gross_pnl": -0.0054325,
          "pf": 0.0,
          "severe_pnl": -0.0094325,
          "trades": 1,
          "win_rate": 0.0
        },
        "IRYS_USDT": {
          "gross_pnl": -0.0137931,
          "pf": 0.0,
          "severe_pnl": -0.0177931,
          "trades": 1,
          "win_rate": 0.0
        },
        "IWM_USDT": {
          "gross_pnl": -0.001241,
          "pf": 0.0,
          "severe_pnl": -0.005241,
          "trades": 1,
          "win_rate": 0.0
        },
        "JASMY_USDT": {
          "gross_pnl": -0.0006153000000000015,
          "pf": 0.05061055754432042,
          "severe_pnl": -0.16461530000000002,
          "trades": 41,
          "win_rate": 0.0975609756097561
        },
        "JCT_USDT": {
          "gross_pnl": 0.0028106000000000173,
          "pf": 0.44741948294528816,
          "severe_pnl": -0.07318939999999999,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "JP225_USDT": {
          "gross_pnl": -0.009593,
          "pf": 0.0,
          "severe_pnl": -0.041593,
          "trades": 8,
          "win_rate": 0.0
        },
        "JST_USDT": {
          "gross_pnl": -0.0040003999999999994,
          "pf": 0.0,
          "severe_pnl": -0.0360004,
          "trades": 8,
          "win_rate": 0.0
        },
        "JTO_USDT": {
          "gross_pnl": 0.015709300000000006,
          "pf": 0.1332441181563369,
          "severe_pnl": -0.2562907,
          "trades": 68,
          "win_rate": 0.1323529411764706
        },
        "JUP_USDT": {
          "gross_pnl": -0.02758279999999999,
          "pf": 0.03304894801848001,
          "severe_pnl": -0.44358280000000017,
          "trades": 104,
          "win_rate": 0.04807692307692308
        },
        "KAIA_USDT": {
          "gross_pnl": -0.0034669,
          "pf": 0.0,
          "severe_pnl": -0.0234669,
          "trades": 5,
          "win_rate": 0.0
        },
        "KAITO_USDT": {
          "gross_pnl": -0.026211599999999995,
          "pf": 0.2170335679087572,
          "severe_pnl": -0.27421160000000006,
          "trades": 62,
          "win_rate": 0.1774193548387097
        },
        "KAS_USDT": {
          "gross_pnl": 0.0011449999999999984,
          "pf": 0.018622713815157066,
          "severe_pnl": -0.11485500000000004,
          "trades": 29,
          "win_rate": 0.06896551724137931
        },
        "KAT_USDT": {
          "gross_pnl": 0.014879999999999999,
          "pf": 1.1726028875024723,
          "severe_pnl": 0.0028800000000000006,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "KITE_USDT": {
          "gross_pnl": -0.010833799999999994,
          "pf": 0.15961175898486463,
          "severe_pnl": -0.23883379999999993,
          "trades": 57,
          "win_rate": 0.22807017543859648
        },
        "KMNO_USDT": {
          "gross_pnl": -0.0059783,
          "pf": 0.0,
          "severe_pnl": -0.013978299999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "KORU_USDT": {
          "gross_pnl": 0.01799430000000002,
          "pf": 0.37021765909722304,
          "severe_pnl": -0.2820056999999999,
          "trades": 75,
          "win_rate": 0.26666666666666666
        },
        "KSM_USDT": {
          "gross_pnl": -0.0029203999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0109204,
          "trades": 2,
          "win_rate": 0.0
        },
        "KSTR_USDT": {
          "gross_pnl": 0.00040419999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0035958,
          "trades": 1,
          "win_rate": 0.0
        },
        "LAB_USDT": {
          "gross_pnl": 0.11762480000000004,
          "pf": 0.8133354563699001,
          "severe_pnl": -0.12637520000000005,
          "trades": 61,
          "win_rate": 0.5081967213114754
        },
        "LDO_USDT": {
          "gross_pnl": -0.08169510000000002,
          "pf": 0.02415194727900686,
          "severe_pnl": -0.5136951000000002,
          "trades": 108,
          "win_rate": 0.08333333333333333
        },
        "LEAD_USDT": {
          "gross_pnl": 0.0007605000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0152395,
          "trades": 4,
          "win_rate": 0.0
        },
        "LIGHT_USDT": {
          "gross_pnl": 0.0203702,
          "pf": 0.32769231206949034,
          "severe_pnl": -0.023629800000000003,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "LINEA_USDT": {
          "gross_pnl": 0.0012756,
          "pf": 0.0,
          "severe_pnl": -0.026724400000000002,
          "trades": 7,
          "win_rate": 0.0
        },
        "LINK_USDT": {
          "gross_pnl": -0.005448300000000001,
          "pf": 0.03450581056728403,
          "severe_pnl": -0.22544830000000002,
          "trades": 55,
          "win_rate": 0.05454545454545454
        },
        "LIT_USDT": {
          "gross_pnl": 0.031003799999999984,
          "pf": 0.1459853295673363,
          "severe_pnl": -0.6849962000000003,
          "trades": 179,
          "win_rate": 0.19553072625698323
        },
        "LRC_USDT": {
          "gross_pnl": 0.05425290000000002,
          "pf": 0.8923252031139178,
          "severe_pnl": -0.017747099999999988,
          "trades": 18,
          "win_rate": 0.5
        },
        "LTC_USDT": {
          "gross_pnl": 0.0007156999999999997,
          "pf": 0.013820976568483976,
          "severe_pnl": -0.1512843,
          "trades": 38,
          "win_rate": 0.07894736842105263
        },
        "LUMIA_USDT": {
          "gross_pnl": -0.1052948,
          "pf": 0.2426082721734747,
          "severe_pnl": -0.1772948,
          "trades": 18,
          "win_rate": 0.2222222222222222
        },
        "LUNANEW_USDT": {
          "gross_pnl": -0.0023575,
          "pf": 0.0,
          "severe_pnl": -0.0063575,
          "trades": 1,
          "win_rate": 0.0
        },
        "LUNC_USDT": {
          "gross_pnl": -0.005146999999999999,
          "pf": 0.01987638400996041,
          "severe_pnl": -0.07714700000000001,
          "trades": 18,
          "win_rate": 0.1111111111111111
        },
        "MAGMA_USDT": {
          "gross_pnl": 0.1160387,
          "pf": 0.6404539594595099,
          "severe_pnl": -0.16396130000000006,
          "trades": 70,
          "win_rate": 0.35714285714285715
        },
        "MANA_USDT": {
          "gross_pnl": -0.0213707,
          "pf": 0.023129391182552042,
          "severe_pnl": -0.07337069999999998,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "MANTA_USDT": {
          "gross_pnl": -0.008099199999999999,
          "pf": 0.013071134953411235,
          "severe_pnl": -0.0720992,
          "trades": 16,
          "win_rate": 0.0625
        },
        "MANTRA_USDT": {
          "gross_pnl": 0.10590049999999998,
          "pf": 1.2816951227982618,
          "severe_pnl": 0.02190050000000001,
          "trades": 21,
          "win_rate": 0.38095238095238093
        },
        "MASK_USDT": {
          "gross_pnl": 0.0010046,
          "pf": 0.0,
          "severe_pnl": -0.006995400000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "MAV_USDT": {
          "gross_pnl": -0.0059723000000000016,
          "pf": 0.0,
          "severe_pnl": -0.0219723,
          "trades": 4,
          "win_rate": 0.0
        },
        "MEGA_USDT": {
          "gross_pnl": 0.009788599999999998,
          "pf": 0.0,
          "severe_pnl": -0.022211400000000003,
          "trades": 8,
          "win_rate": 0.0
        },
        "MEME_USDT": {
          "gross_pnl": -0.0051286000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0291286,
          "trades": 6,
          "win_rate": 0.0
        },
        "MERL_USDT": {
          "gross_pnl": 0.00012600000000000068,
          "pf": 0.11241498313004394,
          "severe_pnl": -0.059874,
          "trades": 15,
          "win_rate": 0.13333333333333333
        },
        "MET_USDT": {
          "gross_pnl": -0.0177253,
          "pf": 0.0,
          "severe_pnl": -0.0217253,
          "trades": 1,
          "win_rate": 0.0
        },
        "MINA_USDT": {
          "gross_pnl": -0.005412,
          "pf": 0.0,
          "severe_pnl": -0.013412,
          "trades": 2,
          "win_rate": 0.0
        },
        "MITO_USDT": {
          "gross_pnl": -0.0030261999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0110262,
          "trades": 2,
          "win_rate": 0.0
        },
        "MMT_USDT": {
          "gross_pnl": -0.0328985,
          "pf": 0.2200101833265071,
          "severe_pnl": -0.29289850000000006,
          "trades": 65,
          "win_rate": 0.2153846153846154
        },
        "MNT_USDT": {
          "gross_pnl": 0.008060399999999999,
          "pf": 0.08846040912205146,
          "severe_pnl": -0.027939600000000002,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "MONAD_USDT": {
          "gross_pnl": 0.013652899999999999,
          "pf": 0.18090870155838215,
          "severe_pnl": -0.06234710000000001,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "MOODENG_USDT": {
          "gross_pnl": 0.0049527,
          "pf": 999,
          "severe_pnl": 0.0009526999999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "MORPHO_USDT": {
          "gross_pnl": -0.040070100000000004,
          "pf": 0.04921564618708455,
          "severe_pnl": -0.1720701,
          "trades": 33,
          "win_rate": 0.09090909090909091
        },
        "MOVE_USDT": {
          "gross_pnl": -0.0017877000000000006,
          "pf": 0.0,
          "severe_pnl": -0.0257877,
          "trades": 6,
          "win_rate": 0.0
        },
        "MOVR_USDT": {
          "gross_pnl": -0.0109091,
          "pf": 0.0,
          "severe_pnl": -0.0149091,
          "trades": 1,
          "win_rate": 0.0
        },
        "MSTU_USDT": {
          "gross_pnl": -0.0586279,
          "pf": 0.15050940941902455,
          "severe_pnl": -0.09462790000000001,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "MUBARAK_USDT": {
          "gross_pnl": 0.0022321,
          "pf": 0.0,
          "severe_pnl": -0.0017679000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "MUU_USDT": {
          "gross_pnl": 0.013997299999999999,
          "pf": 0.8184052083711144,
          "severe_pnl": -0.0020027000000000014,
          "trades": 4,
          "win_rate": 0.25
        },
        "MVLL_USDT": {
          "gross_pnl": 0.007136399999999986,
          "pf": 0.4494711013174596,
          "severe_pnl": -0.09286360000000002,
          "trades": 25,
          "win_rate": 0.36
        },
        "MYX_USDT": {
          "gross_pnl": -0.015631499999999996,
          "pf": 0.21460634559803782,
          "severe_pnl": -0.41563150000000004,
          "trades": 100,
          "win_rate": 0.18
        },
        "M_USDT": {
          "gross_pnl": 0.023340999999999997,
          "pf": 999,
          "severe_pnl": 0.019340999999999997,
          "trades": 1,
          "win_rate": 1.0
        },
        "NAORIS_USDT": {
          "gross_pnl": 0.0109442,
          "pf": 0.3023282250367304,
          "severe_pnl": -0.0650558,
          "trades": 19,
          "win_rate": 0.3157894736842105
        },
        "NEAR_USDT": {
          "gross_pnl": 0.041411600000000014,
          "pf": 0.08399870718652305,
          "severe_pnl": -0.4905883999999999,
          "trades": 133,
          "win_rate": 0.12030075187969924
        },
        "NEIROCTO_USDT": {
          "gross_pnl": -0.0025189,
          "pf": 0.0,
          "severe_pnl": -0.0065189,
          "trades": 1,
          "win_rate": 0.0
        },
        "NEO_USDT": {
          "gross_pnl": -0.0077120999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0117121,
          "trades": 1,
          "win_rate": 0.0
        },
        "NES_USDT": {
          "gross_pnl": -0.0288952,
          "pf": 0.04846777251442783,
          "severe_pnl": -0.10489520000000001,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "NEX_USDT": {
          "gross_pnl": 0.0390582,
          "pf": 999,
          "severe_pnl": 0.0350582,
          "trades": 1,
          "win_rate": 1.0
        },
        "NGAS_USDT": {
          "gross_pnl": 0.007156000000000006,
          "pf": 0.07771886136006859,
          "severe_pnl": -0.220844,
          "trades": 57,
          "win_rate": 0.07017543859649122
        },
        "NICKEL_USDT": {
          "gross_pnl": -0.0025233,
          "pf": 0.0,
          "severe_pnl": -0.0185233,
          "trades": 4,
          "win_rate": 0.0
        },
        "NIGHT_USDT": {
          "gross_pnl": 0.021425,
          "pf": 0.32621515124350575,
          "severe_pnl": -0.034574999999999995,
          "trades": 14,
          "win_rate": 0.21428571428571427
        },
        "NIL_USDT": {
          "gross_pnl": -0.014689800000000003,
          "pf": 0.0,
          "severe_pnl": -0.038689799999999996,
          "trades": 6,
          "win_rate": 0.0
        },
        "NOM_USDT": {
          "gross_pnl": -0.008725799999999999,
          "pf": 0.009960830617355837,
          "severe_pnl": -0.036725799999999996,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "NOT_USDT": {
          "gross_pnl": -0.0007251999999999988,
          "pf": 0.039788719109602,
          "severe_pnl": -0.012725199999999999,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "OFC_USDT": {
          "gross_pnl": 0.0104373,
          "pf": 0.043641056016246425,
          "severe_pnl": -0.0135627,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "OGN_USDT": {
          "gross_pnl": -0.01199549999999999,
          "pf": 0.43418682327312075,
          "severe_pnl": -0.1039955,
          "trades": 23,
          "win_rate": 0.21739130434782608
        },
        "OG_USDT": {
          "gross_pnl": 0.0051262,
          "pf": 999,
          "severe_pnl": 0.0011262,
          "trades": 1,
          "win_rate": 1.0
        },
        "OKB_USDT": {
          "gross_pnl": -0.0025978999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0105979,
          "trades": 2,
          "win_rate": 0.0
        },
        "OL_USDT": {
          "gross_pnl": -0.0176399,
          "pf": 0.0,
          "severe_pnl": -0.0216399,
          "trades": 1,
          "win_rate": 0.0
        },
        "ONDO_USDT": {
          "gross_pnl": 0.026223599999999993,
          "pf": 0.15977229239336346,
          "severe_pnl": -0.3697763999999999,
          "trades": 99,
          "win_rate": 0.13131313131313133
        },
        "ONE_USDT": {
          "gross_pnl": 0.0333585,
          "pf": 999,
          "severe_pnl": 0.0253585,
          "trades": 2,
          "win_rate": 1.0
        },
        "ONG_USDT": {
          "gross_pnl": 0.0008263,
          "pf": 0.0,
          "severe_pnl": -0.0031737000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "ONT_USDT": {
          "gross_pnl": -0.0020609,
          "pf": 0.0,
          "severe_pnl": -0.010060900000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "OPENAI_USDT": {
          "gross_pnl": -0.05489190000000002,
          "pf": 0.0,
          "severe_pnl": -0.4388919,
          "trades": 96,
          "win_rate": 0.0
        },
        "OPENLEDGER_USDT": {
          "gross_pnl": -0.0053298,
          "pf": 0.0,
          "severe_pnl": -0.0093298,
          "trades": 1,
          "win_rate": 0.0
        },
        "OPG_USDT": {
          "gross_pnl": -0.0513175,
          "pf": 0.012661602668588292,
          "severe_pnl": -0.1433175,
          "trades": 23,
          "win_rate": 0.08695652173913043
        },
        "OPN_USDT": {
          "gross_pnl": 0.07472039999999999,
          "pf": 0.3933819144381761,
          "severe_pnl": -0.10527960000000001,
          "trades": 45,
          "win_rate": 0.17777777777777778
        },
        "OP_USDT": {
          "gross_pnl": 0.016519600000000023,
          "pf": 0.059492993298620296,
          "severe_pnl": -0.35948040000000014,
          "trades": 94,
          "win_rate": 0.09574468085106383
        },
        "ORCA_USDT": {
          "gross_pnl": -0.003326,
          "pf": 0.0,
          "severe_pnl": -0.015326,
          "trades": 3,
          "win_rate": 0.0
        },
        "ORDI_USDT": {
          "gross_pnl": -0.0515853,
          "pf": 0.03627102454539545,
          "severe_pnl": -0.5395852999999999,
          "trades": 122,
          "win_rate": 0.09836065573770492
        },
        "O_USDT": {
          "gross_pnl": 0.0379911,
          "pf": 0.45687629153341486,
          "severe_pnl": -0.09800889999999998,
          "trades": 34,
          "win_rate": 0.2647058823529412
        },
        "PARTI_USDT": {
          "gross_pnl": -0.04492260000000001,
          "pf": 0.5037906630519845,
          "severe_pnl": -0.11692260000000002,
          "trades": 18,
          "win_rate": 0.2777777777777778
        },
        "PAXG_USDT": {
          "gross_pnl": -0.0016939999999999998,
          "pf": 0.0,
          "severe_pnl": -0.07769399999999999,
          "trades": 19,
          "win_rate": 0.0
        },
        "PENDLE_USDT": {
          "gross_pnl": -0.021015699999999995,
          "pf": 0.01163045851254085,
          "severe_pnl": -0.17701570000000003,
          "trades": 39,
          "win_rate": 0.05128205128205128
        },
        "PEOPLE_USDT": {
          "gross_pnl": -0.0018386,
          "pf": 0.0,
          "severe_pnl": -0.0058386,
          "trades": 1,
          "win_rate": 0.0
        },
        "PEPE_USDT": {
          "gross_pnl": -0.005042800000000003,
          "pf": 0.0,
          "severe_pnl": -0.041042800000000004,
          "trades": 9,
          "win_rate": 0.0
        },
        "PHAROS_USDT": {
          "gross_pnl": -0.0009711,
          "pf": 0.0,
          "severe_pnl": -0.0049711,
          "trades": 1,
          "win_rate": 0.0
        },
        "PHA_USDT": {
          "gross_pnl": 0.0129454,
          "pf": 0.2158157423772523,
          "severe_pnl": -0.007054600000000001,
          "trades": 5,
          "win_rate": 0.4
        },
        "PIEVERSE_USDT": {
          "gross_pnl": -0.0101157,
          "pf": 0.0,
          "severe_pnl": -0.030115700000000002,
          "trades": 5,
          "win_rate": 0.0
        },
        "PIPPIN_USDT": {
          "gross_pnl": -0.06525549999999998,
          "pf": 0.07735512472721018,
          "severe_pnl": -0.31725549999999997,
          "trades": 63,
          "win_rate": 0.1111111111111111
        },
        "PI_USDT": {
          "gross_pnl": -0.03328400000000001,
          "pf": 0.13500767361555188,
          "severe_pnl": -0.6492839999999999,
          "trades": 154,
          "win_rate": 0.14935064935064934
        },
        "PLUME_USDT": {
          "gross_pnl": -0.0072633,
          "pf": 0.0,
          "severe_pnl": -0.0232633,
          "trades": 4,
          "win_rate": 0.0
        },
        "PNUT_USDT": {
          "gross_pnl": 0.0023463,
          "pf": 0.0,
          "severe_pnl": -0.0016537000000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "POL_USDT": {
          "gross_pnl": -0.058878600000000024,
          "pf": 0.024688162651424532,
          "severe_pnl": -0.31087859999999995,
          "trades": 63,
          "win_rate": 0.031746031746031744
        },
        "PONS_USDT": {
          "gross_pnl": 0.09438079999999999,
          "pf": 999,
          "severe_pnl": 0.09038079999999998,
          "trades": 1,
          "win_rate": 1.0
        },
        "POPCAT_USDT": {
          "gross_pnl": -0.0070121,
          "pf": 0.0,
          "severe_pnl": -0.0190121,
          "trades": 3,
          "win_rate": 0.0
        },
        "PORTAL_USDT": {
          "gross_pnl": -0.0017778,
          "pf": 0.0,
          "severe_pnl": -0.0057778,
          "trades": 1,
          "win_rate": 0.0
        },
        "POWER_USDT": {
          "gross_pnl": 0.007675299999999999,
          "pf": 0.12990652886027332,
          "severe_pnl": -0.012324700000000003,
          "trades": 5,
          "win_rate": 0.2
        },
        "POWR_USDT": {
          "gross_pnl": -0.0156682,
          "pf": 0.0,
          "severe_pnl": -0.0236682,
          "trades": 2,
          "win_rate": 0.0
        },
        "PRL_USDT": {
          "gross_pnl": -0.0035398,
          "pf": 0.0,
          "severe_pnl": -0.0075398,
          "trades": 1,
          "win_rate": 0.0
        },
        "PROM_USDT": {
          "gross_pnl": 0.0007530000000000001,
          "pf": 0.0,
          "severe_pnl": -0.003247,
          "trades": 1,
          "win_rate": 0.0
        },
        "PTB_USDT": {
          "gross_pnl": -0.0046555,
          "pf": 0.0,
          "severe_pnl": -0.0086555,
          "trades": 1,
          "win_rate": 0.0
        },
        "PUMPFUN_USDT": {
          "gross_pnl": 0.019944200000000006,
          "pf": 0.17695138099100396,
          "severe_pnl": -0.44405579999999995,
          "trades": 116,
          "win_rate": 0.1724137931034483
        },
        "PUNDIX_USDT": {
          "gross_pnl": -0.0022357,
          "pf": 0.0,
          "severe_pnl": -0.0102357,
          "trades": 2,
          "win_rate": 0.0
        },
        "PYTH_USDT": {
          "gross_pnl": -0.02140739999999998,
          "pf": 0.05011419007162821,
          "severe_pnl": -0.40140739999999997,
          "trades": 95,
          "win_rate": 0.1368421052631579
        },
        "QNT_USDT": {
          "gross_pnl": 0.0065766,
          "pf": 0.16854309310369167,
          "severe_pnl": -0.009423399999999998,
          "trades": 4,
          "win_rate": 0.25
        },
        "QTUM_USDT": {
          "gross_pnl": -0.0036577000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0156577,
          "trades": 3,
          "win_rate": 0.0
        },
        "RAM_USDT": {
          "gross_pnl": -0.016244300000000003,
          "pf": 0.0,
          "severe_pnl": -0.0722443,
          "trades": 14,
          "win_rate": 0.0
        },
        "RARE_USDT": {
          "gross_pnl": -0.0418405,
          "pf": 0.0,
          "severe_pnl": -0.049840499999999996,
          "trades": 2,
          "win_rate": 0.0
        },
        "RAVE_USDT": {
          "gross_pnl": -0.1136961,
          "pf": 0.1978799215274755,
          "severe_pnl": -0.6536961000000003,
          "trades": 135,
          "win_rate": 0.2
        },
        "RAY_USDT": {
          "gross_pnl": 0.001307,
          "pf": 0.0,
          "severe_pnl": -0.002693,
          "trades": 1,
          "win_rate": 0.0
        },
        "RED_USDT": {
          "gross_pnl": 0.0088496,
          "pf": 999,
          "severe_pnl": 0.004849599999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "RENDER_USDT": {
          "gross_pnl": 0.010494300000000002,
          "pf": 0.0,
          "severe_pnl": -0.1335057,
          "trades": 36,
          "win_rate": 0.0
        },
        "RESOLV_USDT": {
          "gross_pnl": -0.022868299999999994,
          "pf": 0.12963952879529037,
          "severe_pnl": -0.17486829999999998,
          "trades": 38,
          "win_rate": 0.23684210526315788
        },
        "REZ_USDT": {
          "gross_pnl": -0.0033278,
          "pf": 0.0,
          "severe_pnl": -0.007327800000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "RE_USDT": {
          "gross_pnl": 0.004300099999999994,
          "pf": 0.07539683944735294,
          "severe_pnl": -0.39169990000000016,
          "trades": 99,
          "win_rate": 0.15151515151515152
        },
        "RIF_USDT": {
          "gross_pnl": -0.05644019999999998,
          "pf": 0.056783082514263256,
          "severe_pnl": -0.1324402,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "RLC_USDT": {
          "gross_pnl": -0.029556399999999997,
          "pf": 0.10395322081711,
          "severe_pnl": -0.057556399999999994,
          "trades": 7,
          "win_rate": 0.42857142857142855
        },
        "ROAM_USDT": {
          "gross_pnl": -0.02348399999999992,
          "pf": 0.8607482029880604,
          "severe_pnl": -0.11148400000000006,
          "trades": 22,
          "win_rate": 0.2727272727272727
        },
        "ROBO_USDT": {
          "gross_pnl": -0.0130103,
          "pf": 0.0,
          "severe_pnl": -0.0290103,
          "trades": 4,
          "win_rate": 0.0
        },
        "ROSE_USDT": {
          "gross_pnl": 0.013892799999999999,
          "pf": 0.47564179617068764,
          "severe_pnl": -0.006107200000000002,
          "trades": 5,
          "win_rate": 0.4
        },
        "RPL_USDT": {
          "gross_pnl": -0.0126329,
          "pf": 0.0,
          "severe_pnl": -0.032632900000000006,
          "trades": 5,
          "win_rate": 0.0
        },
        "RSR_USDT": {
          "gross_pnl": 0.0031369000000000006,
          "pf": 0.0,
          "severe_pnl": -0.0208631,
          "trades": 6,
          "win_rate": 0.0
        },
        "RUNE_USDT": {
          "gross_pnl": -0.0020590999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0180591,
          "trades": 4,
          "win_rate": 0.0
        },
        "RVN_USDT": {
          "gross_pnl": -0.009579500000000001,
          "pf": 0.15583730196517545,
          "severe_pnl": -0.0735795,
          "trades": 16,
          "win_rate": 0.25
        },
        "SAFE_USDT": {
          "gross_pnl": 0.0029044000000000006,
          "pf": 0.2991683524387503,
          "severe_pnl": -0.013095599999999999,
          "trades": 4,
          "win_rate": 0.25
        },
        "SAGA_USDT": {
          "gross_pnl": -0.0014921,
          "pf": 0.0,
          "severe_pnl": -0.0094921,
          "trades": 2,
          "win_rate": 0.0
        },
        "SAHARA_USDT": {
          "gross_pnl": -0.0279113,
          "pf": 0.0,
          "severe_pnl": -0.09191130000000002,
          "trades": 16,
          "win_rate": 0.0
        },
        "SAND_USDT": {
          "gross_pnl": -0.0031025000000000002,
          "pf": 0.0,
          "severe_pnl": -0.011102500000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "SANTOS_USDT": {
          "gross_pnl": 0.0203065,
          "pf": 1.3945379421545903,
          "severe_pnl": 0.004306500000000001,
          "trades": 4,
          "win_rate": 0.5
        },
        "SAPIEN_USDT": {
          "gross_pnl": -0.0013705999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0053706,
          "trades": 1,
          "win_rate": 0.0
        },
        "SEI_USDT": {
          "gross_pnl": -0.014763900000000007,
          "pf": 0.0014187709901900833,
          "severe_pnl": -0.22276390000000007,
          "trades": 52,
          "win_rate": 0.019230769230769232
        },
        "SENT_USDT": {
          "gross_pnl": -0.006126099999999999,
          "pf": 0.2954135791824419,
          "severe_pnl": -0.08212610000000001,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "SHIB_USDT": {
          "gross_pnl": -0.010411,
          "pf": 0.0,
          "severe_pnl": -0.10641100000000005,
          "trades": 24,
          "win_rate": 0.0
        },
        "SHLD_USDT": {
          "gross_pnl": 0.0057349,
          "pf": 0.433725,
          "severe_pnl": -0.0022651,
          "trades": 2,
          "win_rate": 0.5
        },
        "SIGN_USDT": {
          "gross_pnl": -0.0015246,
          "pf": 0.0,
          "severe_pnl": -0.0055246,
          "trades": 1,
          "win_rate": 0.0
        },
        "SIREN_USDT": {
          "gross_pnl": -0.0175055,
          "pf": 0.0,
          "severe_pnl": -0.0215055,
          "trades": 1,
          "win_rate": 0.0
        },
        "SKL_USDT": {
          "gross_pnl": 0.0352447,
          "pf": 0.6159508691314066,
          "severe_pnl": -0.13275530000000005,
          "trades": 42,
          "win_rate": 0.30952380952380953
        },
        "SKR_USDT": {
          "gross_pnl": 0.0045412,
          "pf": 0.11128001489110875,
          "severe_pnl": -0.011458800000000002,
          "trades": 4,
          "win_rate": 0.25
        },
        "SKYAI_USDT": {
          "gross_pnl": -0.17275039999999994,
          "pf": 0.15576392759318322,
          "severe_pnl": -0.8367504,
          "trades": 166,
          "win_rate": 0.18674698795180722
        },
        "SKY_USDT": {
          "gross_pnl": 0.0139341,
          "pf": 0.15490609028101368,
          "severe_pnl": -0.0460659,
          "trades": 15,
          "win_rate": 0.2
        },
        "SLX_USDT": {
          "gross_pnl": -0.12489730000000004,
          "pf": 0.16487632037266872,
          "severe_pnl": -0.7208973000000002,
          "trades": 149,
          "win_rate": 0.174496644295302
        },
        "SMH_USDT": {
          "gross_pnl": -0.0013353999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0053354,
          "trades": 1,
          "win_rate": 0.0
        },
        "SNT_USDT": {
          "gross_pnl": -0.0074249,
          "pf": 0.0,
          "severe_pnl": -0.019424900000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "SNXX_USDT": {
          "gross_pnl": -0.0393834,
          "pf": 0.0,
          "severe_pnl": -0.06738340000000001,
          "trades": 7,
          "win_rate": 0.0
        },
        "SNX_USDT": {
          "gross_pnl": 0.016124499999999996,
          "pf": 0.21609698847406714,
          "severe_pnl": -0.0398755,
          "trades": 14,
          "win_rate": 0.2857142857142857
        },
        "SOL_USDT": {
          "gross_pnl": -0.012747699999999997,
          "pf": 0.004078021543719964,
          "severe_pnl": -0.22074770000000005,
          "trades": 52,
          "win_rate": 0.038461538461538464
        },
        "SOXL_USDT": {
          "gross_pnl": 0.127025,
          "pf": 0.47674834837677077,
          "severe_pnl": -0.34497500000000003,
          "trades": 118,
          "win_rate": 0.3813559322033898
        },
        "SOXS_USDT": {
          "gross_pnl": 0.027033300000000014,
          "pf": 0.47104832723973933,
          "severe_pnl": -0.07696669999999999,
          "trades": 26,
          "win_rate": 0.23076923076923078
        },
        "SOXX_USDT": {
          "gross_pnl": -0.0106388,
          "pf": 0.0,
          "severe_pnl": -0.0426388,
          "trades": 8,
          "win_rate": 0.0
        },
        "SPELL_USDT": {
          "gross_pnl": -0.034939899999999996,
          "pf": 0.0,
          "severe_pnl": -0.0549399,
          "trades": 5,
          "win_rate": 0.0
        },
        "SPK_USDT": {
          "gross_pnl": 0.0098522,
          "pf": 999,
          "severe_pnl": 0.0058522,
          "trades": 1,
          "win_rate": 1.0
        },
        "SPY_USDT": {
          "gross_pnl": -1.33e-05,
          "pf": 0.0,
          "severe_pnl": -0.0040133,
          "trades": 1,
          "win_rate": 0.0
        },
        "SQD_USDT": {
          "gross_pnl": 0.0026153,
          "pf": 0.0,
          "severe_pnl": -0.009384700000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "SQQQ_USDT": {
          "gross_pnl": 0.0077564999999999995,
          "pf": 0.9187439516801814,
          "severe_pnl": -0.00024350000000000023,
          "trades": 2,
          "win_rate": 0.5
        },
        "STABLE_USDT": {
          "gross_pnl": -0.012023600000000002,
          "pf": 0.03288915988756858,
          "severe_pnl": -0.0520236,
          "trades": 10,
          "win_rate": 0.1
        },
        "STAR_USDT": {
          "gross_pnl": 0.038290899999999996,
          "pf": 999,
          "severe_pnl": 0.0342909,
          "trades": 1,
          "win_rate": 1.0
        },
        "STEEM_USDT": {
          "gross_pnl": -0.0027933000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0067933,
          "trades": 1,
          "win_rate": 0.0
        },
        "STG_USDT": {
          "gross_pnl": -0.0251264,
          "pf": 0.0,
          "severe_pnl": -0.08112640000000002,
          "trades": 14,
          "win_rate": 0.0
        },
        "STORJ_USDT": {
          "gross_pnl": 0.0383189,
          "pf": 999,
          "severe_pnl": 0.0343189,
          "trades": 1,
          "win_rate": 1.0
        },
        "STO_USDT": {
          "gross_pnl": 0.0022549,
          "pf": 0.0,
          "severe_pnl": -0.0057451,
          "trades": 2,
          "win_rate": 0.0
        },
        "STRK_USDT": {
          "gross_pnl": -0.004308999999999999,
          "pf": 0.11262744751325393,
          "severe_pnl": -0.08430900000000001,
          "trades": 20,
          "win_rate": 0.15
        },
        "STX_USDT": {
          "gross_pnl": -0.036649,
          "pf": 0.021066012805536945,
          "severe_pnl": -0.10064899999999999,
          "trades": 16,
          "win_rate": 0.125
        },
        "SUI_USDT": {
          "gross_pnl": -0.014078399999999996,
          "pf": 0.01636493494394932,
          "severe_pnl": -0.26607840000000005,
          "trades": 63,
          "win_rate": 0.031746031746031744
        },
        "SUPER_USDT": {
          "gross_pnl": 0.0011407000000000014,
          "pf": 0.3303342377898372,
          "severe_pnl": -0.010859299999999999,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "SUSHI_USDT": {
          "gross_pnl": -0.0213169,
          "pf": 0.0,
          "severe_pnl": -0.0373169,
          "trades": 4,
          "win_rate": 0.0
        },
        "SXT_USDT": {
          "gross_pnl": -0.07948449999999996,
          "pf": 0.34735429904817544,
          "severe_pnl": -0.4194845,
          "trades": 85,
          "win_rate": 0.24705882352941178
        },
        "SYN_USDT": {
          "gross_pnl": 0.0585983,
          "pf": 0.4481420442799812,
          "severe_pnl": -0.5574016999999997,
          "trades": 154,
          "win_rate": 0.34415584415584416
        },
        "SYRUP_USDT": {
          "gross_pnl": 0.03693249999999999,
          "pf": 0.0816189073403488,
          "severe_pnl": -0.25906750000000006,
          "trades": 74,
          "win_rate": 0.16216216216216217
        },
        "S_USDT": {
          "gross_pnl": 0.0004713999999999992,
          "pf": 0.12053696935619904,
          "severe_pnl": -0.0275286,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "TAC_USDT": {
          "gross_pnl": -0.28504319999999994,
          "pf": 0.33029006830992785,
          "severe_pnl": -0.5610432,
          "trades": 69,
          "win_rate": 0.21739130434782608
        },
        "TAG_USDT": {
          "gross_pnl": -0.14162120000000003,
          "pf": 0.10768569616022157,
          "severe_pnl": -0.2616212,
          "trades": 30,
          "win_rate": 0.23333333333333334
        },
        "TAIKO_USDT": {
          "gross_pnl": 0.0166486,
          "pf": 1.2534360467335066,
          "severe_pnl": 0.004648599999999999,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "TAO_USDT": {
          "gross_pnl": 0.0027102999999999997,
          "pf": 0.03760490231259825,
          "severe_pnl": -0.13328969999999998,
          "trades": 34,
          "win_rate": 0.11764705882352941
        },
        "TENDIES_USDT": {
          "gross_pnl": 0.166334,
          "pf": 999,
          "severe_pnl": 0.162334,
          "trades": 1,
          "win_rate": 1.0
        },
        "THETA_USDT": {
          "gross_pnl": -0.03859560000000001,
          "pf": 0.05648010635930302,
          "severe_pnl": -0.1945956,
          "trades": 39,
          "win_rate": 0.10256410256410256
        },
        "THE_USDT": {
          "gross_pnl": -0.040600399999999995,
          "pf": 0.31405229394098605,
          "severe_pnl": -0.08460039999999999,
          "trades": 11,
          "win_rate": 0.2727272727272727
        },
        "TIA_USDT": {
          "gross_pnl": -0.04332949999999999,
          "pf": 0.08557775419189766,
          "severe_pnl": -0.3713295,
          "trades": 82,
          "win_rate": 0.07317073170731707
        },
        "TLM_USDT": {
          "gross_pnl": -0.14717679999999997,
          "pf": 0.11970037055652157,
          "severe_pnl": -0.45117680000000004,
          "trades": 76,
          "win_rate": 0.18421052631578946
        },
        "TNSR_USDT": {
          "gross_pnl": -0.0006418,
          "pf": 0.0,
          "severe_pnl": -0.0046418,
          "trades": 1,
          "win_rate": 0.0
        },
        "TOSHI_USDT": {
          "gross_pnl": -0.0529519,
          "pf": 0.0,
          "severe_pnl": -0.0649519,
          "trades": 3,
          "win_rate": 0.0
        },
        "TOWNS_USDT": {
          "gross_pnl": 0.0111452,
          "pf": 0.4187447218281496,
          "severe_pnl": -0.020854800000000003,
          "trades": 8,
          "win_rate": 0.375
        },
        "TQQQ_USDT": {
          "gross_pnl": 0.0151483,
          "pf": 0.11051449983886036,
          "severe_pnl": -0.0488517,
          "trades": 16,
          "win_rate": 0.25
        },
        "TRADOOR_USDT": {
          "gross_pnl": -0.1484286,
          "pf": 0.3284089501777848,
          "severe_pnl": -0.30042860000000005,
          "trades": 38,
          "win_rate": 0.18421052631578946
        },
        "TRB_USDT": {
          "gross_pnl": 0.0018333999999999985,
          "pf": 0.058687203803499385,
          "severe_pnl": -0.07416660000000001,
          "trades": 19,
          "win_rate": 0.05263157894736842
        },
        "TRIA_USDT": {
          "gross_pnl": 0.0598355,
          "pf": 0.41447483276729824,
          "severe_pnl": -0.5161645,
          "trades": 144,
          "win_rate": 0.3402777777777778
        },
        "TRX_USDT": {
          "gross_pnl": 0.0016552999999999993,
          "pf": 0.0,
          "severe_pnl": -0.0463447,
          "trades": 12,
          "win_rate": 0.0
        },
        "TRY_USDT": {
          "gross_pnl": 0.0018777000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0141223,
          "trades": 4,
          "win_rate": 0.0
        },
        "TSLL_USDT": {
          "gross_pnl": -0.0008834,
          "pf": 0.0,
          "severe_pnl": -0.0048834,
          "trades": 1,
          "win_rate": 0.0
        },
        "TURBO_USDT": {
          "gross_pnl": -0.0023255000000000007,
          "pf": 0.0,
          "severe_pnl": -0.0223255,
          "trades": 5,
          "win_rate": 0.0
        },
        "TUT_USDT": {
          "gross_pnl": 0.0002787999999999983,
          "pf": 0.332324481378034,
          "severe_pnl": -0.007721200000000001,
          "trades": 2,
          "win_rate": 0.5
        },
        "TWT_USDT": {
          "gross_pnl": -0.0163798,
          "pf": 0.0,
          "severe_pnl": -0.0203798,
          "trades": 1,
          "win_rate": 0.0
        },
        "T_USDT": {
          "gross_pnl": -0.022562099999999967,
          "pf": 0.3971319619685205,
          "severe_pnl": -0.33456210000000003,
          "trades": 78,
          "win_rate": 0.2948717948717949
        },
        "UAI_USDT": {
          "gross_pnl": -0.11106269999999999,
          "pf": 0.09640115300241095,
          "severe_pnl": -0.3510627000000001,
          "trades": 60,
          "win_rate": 0.1
        },
        "UMA_USDT": {
          "gross_pnl": 0.018135400000000003,
          "pf": 999,
          "severe_pnl": 0.010135400000000001,
          "trades": 2,
          "win_rate": 1.0
        },
        "UNI_USDT": {
          "gross_pnl": -0.039702600000000005,
          "pf": 0.011145888490685516,
          "severe_pnl": -0.41570260000000003,
          "trades": 94,
          "win_rate": 0.0851063829787234
        },
        "UP_USDT": {
          "gross_pnl": -0.0064876000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0184876,
          "trades": 3,
          "win_rate": 0.0
        },
        "URNM_USDT": {
          "gross_pnl": 0.0009347000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0070653,
          "trades": 2,
          "win_rate": 0.0
        },
        "USELESS_USDT": {
          "gross_pnl": -0.0005622000000000058,
          "pf": 0.17591757464529612,
          "severe_pnl": -0.2205622,
          "trades": 55,
          "win_rate": 0.21818181818181817
        },
        "USO_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "USUAL_USDT": {
          "gross_pnl": 0.0024769999999999983,
          "pf": 0.20797746572971051,
          "severe_pnl": -0.045522999999999994,
          "trades": 12,
          "win_rate": 0.25
        },
        "UVXY_USDT": {
          "gross_pnl": -0.0017143000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0177143,
          "trades": 4,
          "win_rate": 0.0
        },
        "VANRY_USDT": {
          "gross_pnl": -0.09271449999999999,
          "pf": 0.3190434459676726,
          "severe_pnl": -0.3007145,
          "trades": 52,
          "win_rate": 0.28846153846153844
        },
        "VELO_USDT": {
          "gross_pnl": -0.0150782,
          "pf": 0.0,
          "severe_pnl": -0.035078200000000004,
          "trades": 5,
          "win_rate": 0.0
        },
        "VELVET_USDT": {
          "gross_pnl": -0.07177570000000003,
          "pf": 0.4104458641947236,
          "severe_pnl": -0.6637757000000002,
          "trades": 148,
          "win_rate": 0.3310810810810811
        },
        "VET_USDT": {
          "gross_pnl": -0.0031617,
          "pf": 0.0007013484536432046,
          "severe_pnl": -0.0471617,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "VINE_USDT": {
          "gross_pnl": -0.04414950000000001,
          "pf": 0.0,
          "severe_pnl": -0.0761495,
          "trades": 8,
          "win_rate": 0.0
        },
        "VIRTUAL_USDT": {
          "gross_pnl": -0.0003913000000000076,
          "pf": 0.1434852412165923,
          "severe_pnl": -0.4123913000000002,
          "trades": 103,
          "win_rate": 0.1553398058252427
        },
        "VVV_USDT": {
          "gross_pnl": 0.0550742,
          "pf": 0.20830741884673928,
          "severe_pnl": -0.2249258,
          "trades": 70,
          "win_rate": 0.11428571428571428
        },
        "WIF_USDT": {
          "gross_pnl": 0.024135800000000002,
          "pf": 0.10019236290646433,
          "severe_pnl": -0.2798642,
          "trades": 76,
          "win_rate": 0.07894736842105263
        },
        "WLD_USDT": {
          "gross_pnl": -0.0346393,
          "pf": 0.05312184481786235,
          "severe_pnl": -0.5906392999999999,
          "trades": 139,
          "win_rate": 0.07194244604316546
        },
        "WLFI_USDT": {
          "gross_pnl": 0.003429200000000001,
          "pf": 0.0,
          "severe_pnl": -0.08857079999999999,
          "trades": 23,
          "win_rate": 0.0
        },
        "WOO_USDT": {
          "gross_pnl": -0.0015911,
          "pf": 0.0,
          "severe_pnl": -0.0055911,
          "trades": 1,
          "win_rate": 0.0
        },
        "W_USDT": {
          "gross_pnl": 0.001006,
          "pf": 0.0,
          "severe_pnl": -0.014994,
          "trades": 4,
          "win_rate": 0.0
        },
        "XAI_USDT": {
          "gross_pnl": -0.0327637,
          "pf": 0.0,
          "severe_pnl": -0.052763700000000004,
          "trades": 5,
          "win_rate": 0.0
        },
        "XAN_USDT": {
          "gross_pnl": 0.032020700000000006,
          "pf": 0.4741231657920072,
          "severe_pnl": -0.023979299999999995,
          "trades": 14,
          "win_rate": 0.35714285714285715
        },
        "XBI_USDT": {
          "gross_pnl": 0.032106899999999994,
          "pf": 0.2749714001341235,
          "severe_pnl": -0.023893100000000004,
          "trades": 14,
          "win_rate": 0.35714285714285715
        },
        "XDC_USDT": {
          "gross_pnl": -0.00036909999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0083691,
          "trades": 2,
          "win_rate": 0.0
        },
        "XEC_USDT": {
          "gross_pnl": -0.07058020000000004,
          "pf": 0.3803523927656199,
          "severe_pnl": -0.41858019999999996,
          "trades": 87,
          "win_rate": 0.20689655172413793
        },
        "XLM_USDT": {
          "gross_pnl": -0.0223748,
          "pf": 0.007324593680674864,
          "severe_pnl": -0.2983748,
          "trades": 69,
          "win_rate": 0.028985507246376812
        },
        "XLU_USDT": {
          "gross_pnl": 0.028909999999999998,
          "pf": 2.1541600279796373,
          "severe_pnl": 0.008910000000000001,
          "trades": 5,
          "win_rate": 0.8
        },
        "XMR_USDT": {
          "gross_pnl": 0.019658399999999996,
          "pf": 0.028588061341343094,
          "severe_pnl": -0.2843416000000001,
          "trades": 76,
          "win_rate": 0.05263157894736842
        },
        "XPIN_USDT": {
          "gross_pnl": 0.004584800000000005,
          "pf": 0.5693799684505817,
          "severe_pnl": -0.0554152,
          "trades": 15,
          "win_rate": 0.3333333333333333
        },
        "XPL_USDT": {
          "gross_pnl": -0.04136539999999998,
          "pf": 0.06499464977648167,
          "severe_pnl": -0.3893654000000001,
          "trades": 87,
          "win_rate": 0.08045977011494253
        },
        "XPT_USDT": {
          "gross_pnl": 0.018015999999999997,
          "pf": 0.18540193852558784,
          "severe_pnl": -0.08198399999999999,
          "trades": 25,
          "win_rate": 0.08
        },
        "XRP_USDT": {
          "gross_pnl": 0.002958900000000001,
          "pf": 0.0,
          "severe_pnl": -0.1050411,
          "trades": 27,
          "win_rate": 0.0
        },
        "XTZ_USDT": {
          "gross_pnl": 0.0029098,
          "pf": 0.0,
          "severe_pnl": -0.0130902,
          "trades": 4,
          "win_rate": 0.0
        },
        "XVS_USDT": {
          "gross_pnl": 0.0084778,
          "pf": 999,
          "severe_pnl": 0.0044778000000000005,
          "trades": 1,
          "win_rate": 1.0
        },
        "YFI_USDT": {
          "gross_pnl": -0.0022881999999999998,
          "pf": 0.10301835339356309,
          "severe_pnl": -0.0182882,
          "trades": 4,
          "win_rate": 0.25
        },
        "ZAMA_USDT": {
          "gross_pnl": -0.0045709999999999995,
          "pf": 0.0,
          "severe_pnl": -0.012570999999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "ZBT_USDT": {
          "gross_pnl": 0.0292778,
          "pf": 0.313440478615852,
          "severe_pnl": -0.2507222,
          "trades": 70,
          "win_rate": 0.2571428571428571
        },
        "ZEC_USDT": {
          "gross_pnl": -0.05324979999999999,
          "pf": 0.09057120098917984,
          "severe_pnl": -0.46924980000000005,
          "trades": 104,
          "win_rate": 0.11538461538461539
        },
        "ZEN_USDT": {
          "gross_pnl": -0.0064352,
          "pf": 0.000824210454867199,
          "severe_pnl": -0.0824352,
          "trades": 19,
          "win_rate": 0.05263157894736842
        },
        "ZEST_USDT": {
          "gross_pnl": -0.0127625,
          "pf": 0.0,
          "severe_pnl": -0.0367625,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZETA_USDT": {
          "gross_pnl": 0.00028879999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0037112,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZINC_USDT": {
          "gross_pnl": -0.0017284999999999998,
          "pf": 0.0,
          "severe_pnl": -0.021728499999999998,
          "trades": 5,
          "win_rate": 0.0
        },
        "ZKC_USDT": {
          "gross_pnl": -0.00022429999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0042243,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZKP_USDT": {
          "gross_pnl": 0.0039591,
          "pf": 0.0,
          "severe_pnl": -0.0200409,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZKSYNC_USDT": {
          "gross_pnl": -0.029088700000000002,
          "pf": 0.03500879696458808,
          "severe_pnl": -0.10508870000000003,
          "trades": 19,
          "win_rate": 0.05263157894736842
        },
        "ZORA_USDT": {
          "gross_pnl": -0.007284199999999999,
          "pf": 0.045302653356147374,
          "severe_pnl": -0.0272842,
          "trades": 5,
          "win_rate": 0.2
        },
        "ZRO_USDT": {
          "gross_pnl": -0.005481400000000003,
          "pf": 0.04264252296833676,
          "severe_pnl": -0.20948139999999996,
          "trades": 51,
          "win_rate": 0.0784313725490196
        },
        "ZRX_USDT": {
          "gross_pnl": 9.100000000000167e-06,
          "pf": 0.0,
          "severe_pnl": -0.0199909,
          "trades": 5,
          "win_rate": 0.0
        }
      },
      "validation_depth_quartiles": [
        {
          "gross_pnl": 0.03367720000000097,
          "pf": 0.46406990184614216,
          "quartile": 1,
          "severe_pnl": -11.038322799999978,
          "trades": 2768,
          "upper": 8976.76524,
          "win_rate": 0.2536127167630058
        },
        {
          "gross_pnl": -1.2900148000000027,
          "pf": 0.21720500862274175,
          "quartile": 2,
          "severe_pnl": -13.398014799999952,
          "trades": 3027,
          "upper": 106972.33601999999,
          "win_rate": 0.1658407664354146
        },
        {
          "gross_pnl": -0.3034029000000008,
          "pf": 0.20606093308943002,
          "quartile": 3,
          "severe_pnl": -12.075402899999947,
          "trades": 2943,
          "upper": 1071304.435,
          "win_rate": 0.16445803601766903
        },
        {
          "gross_pnl": -0.08282700000000005,
          "pf": 0.09083755112989106,
          "quartile": 4,
          "severe_pnl": -11.282826999999953,
          "trades": 2800,
          "upper": null,
          "win_rate": 0.09642857142857143
        }
      ],
      "validation_pass": false,
      "validation_skips": {
        "invalid_path_json": 0,
        "missing_horizon_path": 117,
        "structure_not_selected": 76000,
        "symbol_cooldown": 3645
      },
      "validation_spread_quartiles": [
        {
          "gross_pnl": -0.18798280000000006,
          "pf": 0.17411746159788807,
          "quartile": 1,
          "severe_pnl": -12.275982800000003,
          "trades": 3022,
          "upper": 2.148689299527946,
          "win_rate": 0.12806088682991396
        },
        {
          "gross_pnl": -0.1234510000000017,
          "pf": 0.24789865220525836,
          "quartile": 2,
          "severe_pnl": -11.459450999999936,
          "trades": 2834,
          "upper": 4.268032437045758,
          "win_rate": 0.16937191249117856
        },
        {
          "gross_pnl": -0.44184460000000014,
          "pf": 0.24946698874038856,
          "quartile": 3,
          "severe_pnl": -12.037844599999987,
          "trades": 2899,
          "upper": 7.482229704451622,
          "win_rate": 0.17281821317695756
        },
        {
          "gross_pnl": -0.8892891000000015,
          "pf": 0.3736328847822097,
          "quartile": 4,
          "severe_pnl": -12.021289099999924,
          "trades": 2783,
          "upper": null,
          "win_rate": 0.21200143729787999
        }
      ]
    },
    {
      "direction": "continuation",
      "horizon_seconds": 60,
      "leave_best_symbol": -52.034774599999146,
      "structure": "contradict",
      "validation": {
        "gross_pnl": -2.5532923999999957,
        "pf": 0.1049250443910482,
        "severe_pnl": -51.909292399999146,
        "trades": 12339,
        "win_rate": 0.07593808250263392
      },
      "validation_by_symbol": {
        "0G_USDT": {
          "gross_pnl": 0.002456499999999999,
          "pf": 0.134147734162804,
          "severe_pnl": -0.0735435,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "1000000BABYDOGE_USDT": {
          "gross_pnl": -0.0037342999999999994,
          "pf": 0.09564049804548769,
          "severe_pnl": -0.019734299999999996,
          "trades": 4,
          "win_rate": 0.25
        },
        "1000BONK_USDT": {
          "gross_pnl": -0.03628329999999999,
          "pf": 0.0072552958098576975,
          "severe_pnl": -0.2802833,
          "trades": 61,
          "win_rate": 0.01639344262295082
        },
        "1000BTT_USDT": {
          "gross_pnl": -0.0040605,
          "pf": 0.0,
          "severe_pnl": -0.0080605,
          "trades": 1,
          "win_rate": 0.0
        },
        "2Z_USDT": {
          "gross_pnl": 0.00028209999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0037179,
          "trades": 1,
          "win_rate": 0.0
        },
        "4_USDT": {
          "gross_pnl": -0.0010232000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0290232,
          "trades": 7,
          "win_rate": 0.0
        },
        "AAVE_USDT": {
          "gross_pnl": -0.011003399999999995,
          "pf": 0.0032072688855473547,
          "severe_pnl": -0.18700340000000001,
          "trades": 44,
          "win_rate": 0.022727272727272728
        },
        "ACE_USDT": {
          "gross_pnl": 0.0044551,
          "pf": 0.7584510449246032,
          "severe_pnl": -0.0035449,
          "trades": 2,
          "win_rate": 0.5
        },
        "ACH_USDT": {
          "gross_pnl": 0.0002737000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0077263,
          "trades": 2,
          "win_rate": 0.0
        },
        "ACU_USDT": {
          "gross_pnl": -0.0003985,
          "pf": 0.0,
          "severe_pnl": -0.0043985,
          "trades": 1,
          "win_rate": 0.0
        },
        "ACX_USDT": {
          "gross_pnl": 0.00023720000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0037628,
          "trades": 1,
          "win_rate": 0.0
        },
        "ADA_USDT": {
          "gross_pnl": -0.0200446,
          "pf": 0.0,
          "severe_pnl": -0.4000446000000001,
          "trades": 95,
          "win_rate": 0.0
        },
        "AERGO_USDT": {
          "gross_pnl": -0.044199899999999986,
          "pf": 0.016767368233300634,
          "severe_pnl": -0.08819990000000001,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "AERO_USDT": {
          "gross_pnl": -0.017890600000000003,
          "pf": 0.0,
          "severe_pnl": -0.23389059999999998,
          "trades": 54,
          "win_rate": 0.0
        },
        "AGI_USDT": {
          "gross_pnl": -0.0043412,
          "pf": 0.0,
          "severe_pnl": -0.0123412,
          "trades": 2,
          "win_rate": 0.0
        },
        "AGLD_USDT": {
          "gross_pnl": 0.002498000000000002,
          "pf": 0.16000236296640896,
          "severe_pnl": -0.045502,
          "trades": 12,
          "win_rate": 0.25
        },
        "AIGENSYN_USDT": {
          "gross_pnl": -0.014679600000000003,
          "pf": 0.010568674562075412,
          "severe_pnl": -0.0906796,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "AIOT_USDT": {
          "gross_pnl": 0.13859210000000005,
          "pf": 0.757452103245925,
          "severe_pnl": -0.07740790000000004,
          "trades": 54,
          "win_rate": 0.18518518518518517
        },
        "AIOZ_USDT": {
          "gross_pnl": -0.004721400000000001,
          "pf": 0.0,
          "severe_pnl": -0.0127214,
          "trades": 2,
          "win_rate": 0.0
        },
        "AIO_USDT": {
          "gross_pnl": 0.0079943,
          "pf": 0.9989885188011286,
          "severe_pnl": -5.699999999999976e-06,
          "trades": 2,
          "win_rate": 0.5
        },
        "AKE_USDT": {
          "gross_pnl": -0.12907559999999996,
          "pf": 0.43663415870170585,
          "severe_pnl": -0.36507560000000006,
          "trades": 59,
          "win_rate": 0.3050847457627119
        },
        "AKT_USDT": {
          "gross_pnl": -0.0050357,
          "pf": 0.0,
          "severe_pnl": -0.0090357,
          "trades": 1,
          "win_rate": 0.0
        },
        "ALCH_USDT": {
          "gross_pnl": 0.05725909999999999,
          "pf": 0.14574698102307226,
          "severe_pnl": -0.1947409,
          "trades": 63,
          "win_rate": 0.1111111111111111
        },
        "ALGO_USDT": {
          "gross_pnl": -0.0071902,
          "pf": 0.0,
          "severe_pnl": -0.13919020000000004,
          "trades": 33,
          "win_rate": 0.0
        },
        "ALLO_USDT": {
          "gross_pnl": -0.011228600000000017,
          "pf": 0.11400875849487982,
          "severe_pnl": -0.7992285999999998,
          "trades": 197,
          "win_rate": 0.16751269035532995
        },
        "ALT_USDT": {
          "gross_pnl": -0.0204865,
          "pf": 0.0,
          "severe_pnl": -0.056486499999999995,
          "trades": 9,
          "win_rate": 0.0
        },
        "ANKR_USDT": {
          "gross_pnl": 0.008956699999999998,
          "pf": 0.49762727712935595,
          "severe_pnl": -0.015043300000000003,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "ANSEM_USDT": {
          "gross_pnl": -0.007807500000000035,
          "pf": 0.3693320954703075,
          "severe_pnl": -0.6918075000000001,
          "trades": 171,
          "win_rate": 0.27485380116959063
        },
        "ANTHROPIC_USDT": {
          "gross_pnl": -0.010293700000000003,
          "pf": 0.0,
          "severe_pnl": -0.0822937,
          "trades": 18,
          "win_rate": 0.0
        },
        "APE_USDT": {
          "gross_pnl": -0.023686,
          "pf": 0.01234774086812631,
          "severe_pnl": -0.2956860000000001,
          "trades": 68,
          "win_rate": 0.029411764705882353
        },
        "APT_USDT": {
          "gross_pnl": -0.017533899999999995,
          "pf": 0.0,
          "severe_pnl": -0.3935339,
          "trades": 94,
          "win_rate": 0.0
        },
        "ARB_USDT": {
          "gross_pnl": -0.0593466,
          "pf": 0.015640372235693208,
          "severe_pnl": -0.8193465999999997,
          "trades": 190,
          "win_rate": 0.010526315789473684
        },
        "ARKK_USDT": {
          "gross_pnl": -0.0405368,
          "pf": 0.0,
          "severe_pnl": -0.056536800000000005,
          "trades": 4,
          "win_rate": 0.0
        },
        "ARKM_USDT": {
          "gross_pnl": -0.0027248,
          "pf": 0.0,
          "severe_pnl": -0.038724800000000004,
          "trades": 9,
          "win_rate": 0.0
        },
        "ARX_USDT": {
          "gross_pnl": -0.014426400000000002,
          "pf": 0.009940037135158036,
          "severe_pnl": -0.1264264,
          "trades": 28,
          "win_rate": 0.03571428571428571
        },
        "AR_USDT": {
          "gross_pnl": -0.0108396,
          "pf": 0.0,
          "severe_pnl": -0.0748396,
          "trades": 16,
          "win_rate": 0.0
        },
        "ASP_USDT": {
          "gross_pnl": -0.0058252,
          "pf": 0.0,
          "severe_pnl": -0.0098252,
          "trades": 1,
          "win_rate": 0.0
        },
        "ASTER_USDT": {
          "gross_pnl": -0.010139500000000003,
          "pf": 0.0,
          "severe_pnl": -0.1461395,
          "trades": 34,
          "win_rate": 0.0
        },
        "ATH_USDT": {
          "gross_pnl": -0.0117735,
          "pf": 0.0,
          "severe_pnl": -0.0397735,
          "trades": 7,
          "win_rate": 0.0
        },
        "ATOM_USDT": {
          "gross_pnl": -0.0241087,
          "pf": 0.0,
          "severe_pnl": -0.2081087,
          "trades": 46,
          "win_rate": 0.0
        },
        "AT_USDT": {
          "gross_pnl": -0.010006000000000001,
          "pf": 0.0,
          "severe_pnl": -0.026006,
          "trades": 4,
          "win_rate": 0.0
        },
        "AVAAI_USDT": {
          "gross_pnl": -0.0019253999999999999,
          "pf": 0.37320688304849015,
          "severe_pnl": -0.0139254,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "AVAX_USDT": {
          "gross_pnl": -0.0140489,
          "pf": 0.0,
          "severe_pnl": -0.1740489,
          "trades": 40,
          "win_rate": 0.0
        },
        "AVNT_USDT": {
          "gross_pnl": -0.0087383,
          "pf": 0.0,
          "severe_pnl": -0.1207383,
          "trades": 28,
          "win_rate": 0.0
        },
        "AWE_USDT": {
          "gross_pnl": -0.0023399,
          "pf": 0.0,
          "severe_pnl": -0.010339899999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "AXS_USDT": {
          "gross_pnl": -0.0030264000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0390264,
          "trades": 9,
          "win_rate": 0.0
        },
        "A_USDT": {
          "gross_pnl": 0.0015012000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0104988,
          "trades": 3,
          "win_rate": 0.0
        },
        "B2_USDT": {
          "gross_pnl": -0.005148700000000001,
          "pf": 0.0,
          "severe_pnl": -0.013148700000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "B3_USDT": {
          "gross_pnl": -0.020834000000000002,
          "pf": 0.1678330227493707,
          "severe_pnl": -0.07283400000000001,
          "trades": 13,
          "win_rate": 0.15384615384615385
        },
        "BANANAS31_USDT": {
          "gross_pnl": -0.0019371999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0099372,
          "trades": 2,
          "win_rate": 0.0
        },
        "BAND_USDT": {
          "gross_pnl": 0.0005865,
          "pf": 0.0,
          "severe_pnl": -0.0034135,
          "trades": 1,
          "win_rate": 0.0
        },
        "BANK_USDT": {
          "gross_pnl": 0.007697800000000008,
          "pf": 0.22035369060194082,
          "severe_pnl": -0.3283022,
          "trades": 84,
          "win_rate": 0.17857142857142858
        },
        "BAN_USDT": {
          "gross_pnl": -0.0007657,
          "pf": 0.0,
          "severe_pnl": -0.0047657,
          "trades": 1,
          "win_rate": 0.0
        },
        "BASED_USDT": {
          "gross_pnl": -0.004136100000000002,
          "pf": 0.07759880445564868,
          "severe_pnl": -0.12813609999999998,
          "trades": 31,
          "win_rate": 0.03225806451612903
        },
        "BAS_USDT": {
          "gross_pnl": -0.006554,
          "pf": 0.23885033551468035,
          "severe_pnl": -0.026554,
          "trades": 5,
          "win_rate": 0.2
        },
        "BAT_USDT": {
          "gross_pnl": -0.0025351,
          "pf": 0.0,
          "severe_pnl": -0.014535100000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "BCH_USDT": {
          "gross_pnl": 0.014813400000000011,
          "pf": 0.024092326505911654,
          "severe_pnl": -0.23318660000000005,
          "trades": 62,
          "win_rate": 0.03225806451612903
        },
        "BEAT_USDT": {
          "gross_pnl": -0.04598509999999998,
          "pf": 0.06200526026842823,
          "severe_pnl": -0.6859851,
          "trades": 160,
          "win_rate": 0.08125
        },
        "BERA_USDT": {
          "gross_pnl": -0.007249699999999999,
          "pf": 0.0,
          "severe_pnl": -0.039249700000000005,
          "trades": 8,
          "win_rate": 0.0
        },
        "BIANRENSHENG_USDT": {
          "gross_pnl": -0.011175799999999998,
          "pf": 0.0,
          "severe_pnl": -0.0471758,
          "trades": 9,
          "win_rate": 0.0
        },
        "BICO_USDT": {
          "gross_pnl": -0.011481599999999998,
          "pf": 0.0,
          "severe_pnl": -0.0434816,
          "trades": 8,
          "win_rate": 0.0
        },
        "BIGTIME_USDT": {
          "gross_pnl": -0.0010289,
          "pf": 0.0,
          "severe_pnl": -0.0090289,
          "trades": 2,
          "win_rate": 0.0
        },
        "BILL_USDT": {
          "gross_pnl": 0.009712999999999989,
          "pf": 0.2129292646636903,
          "severe_pnl": -0.5782869999999999,
          "trades": 147,
          "win_rate": 0.10884353741496598
        },
        "BLAST_USDT": {
          "gross_pnl": 0.0836675,
          "pf": 0.8713194808350989,
          "severe_pnl": -0.020332500000000007,
          "trades": 26,
          "win_rate": 0.38461538461538464
        },
        "BLESS_USDT": {
          "gross_pnl": -0.0665093,
          "pf": 0.0,
          "severe_pnl": -0.21850929999999996,
          "trades": 38,
          "win_rate": 0.0
        },
        "BLUAI_USDT": {
          "gross_pnl": 0.0249975,
          "pf": 1.0152706229954915,
          "severe_pnl": 0.000997499999999991,
          "trades": 6,
          "win_rate": 0.3333333333333333
        },
        "BLUR_USDT": {
          "gross_pnl": -0.03486,
          "pf": 0.0,
          "severe_pnl": -0.07886,
          "trades": 11,
          "win_rate": 0.0
        },
        "BNB_USDT": {
          "gross_pnl": -0.0021260000000000003,
          "pf": 0.0,
          "severe_pnl": -0.062126,
          "trades": 15,
          "win_rate": 0.0
        },
        "BOBA_USDT": {
          "gross_pnl": -0.0058871,
          "pf": 0.0,
          "severe_pnl": -0.013887100000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "BRETT_USDT": {
          "gross_pnl": -0.0329712,
          "pf": 0.01998514739291262,
          "severe_pnl": -0.12497120000000005,
          "trades": 23,
          "win_rate": 0.043478260869565216
        },
        "BREV_USDT": {
          "gross_pnl": -0.0015725000000000001,
          "pf": 0.0,
          "severe_pnl": -0.017572499999999998,
          "trades": 4,
          "win_rate": 0.0
        },
        "BR_USDT": {
          "gross_pnl": 0.0004898,
          "pf": 0.0,
          "severe_pnl": -0.0035102,
          "trades": 1,
          "win_rate": 0.0
        },
        "BSB_USDT": {
          "gross_pnl": -0.000501300000000004,
          "pf": 0.12735793159928108,
          "severe_pnl": -0.7445013000000003,
          "trades": 186,
          "win_rate": 0.13978494623655913
        },
        "BSV_USDT": {
          "gross_pnl": 0.013854100000000001,
          "pf": 0.16718480248195547,
          "severe_pnl": -0.026145900000000003,
          "trades": 10,
          "win_rate": 0.2
        },
        "BTW_USDT": {
          "gross_pnl": -0.034187699999999994,
          "pf": 0.09098813020912347,
          "severe_pnl": -0.15818770000000001,
          "trades": 31,
          "win_rate": 0.0967741935483871
        },
        "BUILDONBOB_USDT": {
          "gross_pnl": -0.0227663,
          "pf": 0.0,
          "severe_pnl": -0.0387663,
          "trades": 4,
          "win_rate": 0.0
        },
        "BULLA_USDT": {
          "gross_pnl": 0.023437200000000002,
          "pf": 0.4700904469236209,
          "severe_pnl": -0.016562799999999996,
          "trades": 10,
          "win_rate": 0.3
        },
        "CAKE_USDT": {
          "gross_pnl": -0.0035234,
          "pf": 0.0,
          "severe_pnl": -0.0475234,
          "trades": 11,
          "win_rate": 0.0
        },
        "CAP_USDT": {
          "gross_pnl": -0.0451674,
          "pf": 0.039800628391326705,
          "severe_pnl": -0.29316740000000013,
          "trades": 62,
          "win_rate": 0.06451612903225806
        },
        "CASHCAT_USDT": {
          "gross_pnl": -0.013116600000000008,
          "pf": 0.338690069165134,
          "severe_pnl": -0.11711660000000002,
          "trades": 26,
          "win_rate": 0.2692307692307692
        },
        "CC_USDT": {
          "gross_pnl": 0.0248156,
          "pf": 0.41712590506838293,
          "severe_pnl": -0.0231844,
          "trades": 12,
          "win_rate": 0.3333333333333333
        },
        "CFX_USDT": {
          "gross_pnl": -7.319999999999948e-05,
          "pf": 0.0,
          "severe_pnl": -0.04807320000000001,
          "trades": 12,
          "win_rate": 0.0
        },
        "CHIP_USDT": {
          "gross_pnl": 0.0036745999999999992,
          "pf": 0.010233738331215316,
          "severe_pnl": -0.18832540000000003,
          "trades": 48,
          "win_rate": 0.041666666666666664
        },
        "CHR_USDT": {
          "gross_pnl": -0.0022949,
          "pf": 0.0,
          "severe_pnl": -0.0102949,
          "trades": 2,
          "win_rate": 0.0
        },
        "CHZ_USDT": {
          "gross_pnl": -0.0095509,
          "pf": 0.0,
          "severe_pnl": -0.07755090000000002,
          "trades": 17,
          "win_rate": 0.0
        },
        "CLO_USDT": {
          "gross_pnl": -0.0052516,
          "pf": 0.00401819735353206,
          "severe_pnl": -0.017251600000000002,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "COAI_USDT": {
          "gross_pnl": -0.0035784999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0715785,
          "trades": 17,
          "win_rate": 0.0
        },
        "COLLECT_USDT": {
          "gross_pnl": -0.0188843,
          "pf": 0.09999055299714309,
          "severe_pnl": -0.0828843,
          "trades": 16,
          "win_rate": 0.125
        },
        "COMP_USDT": {
          "gross_pnl": -0.0029025,
          "pf": 0.0,
          "severe_pnl": -0.018902500000000003,
          "trades": 4,
          "win_rate": 0.0
        },
        "COOKIE_USDT": {
          "gross_pnl": -0.0022700999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0062701,
          "trades": 1,
          "win_rate": 0.0
        },
        "CORE_USDT": {
          "gross_pnl": -0.0053462,
          "pf": 0.0,
          "severe_pnl": -0.021346200000000003,
          "trades": 4,
          "win_rate": 0.0
        },
        "COW_USDT": {
          "gross_pnl": 0.0026864,
          "pf": 0.0,
          "severe_pnl": -0.0013136000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "CROSS_USDT": {
          "gross_pnl": -0.0026462,
          "pf": 0.0,
          "severe_pnl": -0.0146462,
          "trades": 3,
          "win_rate": 0.0
        },
        "CRO_USDT": {
          "gross_pnl": -0.0023346999999999973,
          "pf": 0.06882919906868042,
          "severe_pnl": -0.15833470000000002,
          "trades": 39,
          "win_rate": 0.05128205128205128
        },
        "CRV_USDT": {
          "gross_pnl": -0.015534599999999997,
          "pf": 0.0,
          "severe_pnl": -0.2995346,
          "trades": 71,
          "win_rate": 0.0
        },
        "CTC_USDT": {
          "gross_pnl": -0.0345353,
          "pf": 0.0,
          "severe_pnl": -0.1305353,
          "trades": 24,
          "win_rate": 0.0
        },
        "CTR_USDT": {
          "gross_pnl": 0.017094,
          "pf": 999,
          "severe_pnl": 0.013094000000000001,
          "trades": 1,
          "win_rate": 1.0
        },
        "CVX_USDT": {
          "gross_pnl": -0.0123026,
          "pf": 0.0,
          "severe_pnl": -0.0443026,
          "trades": 8,
          "win_rate": 0.0
        },
        "CYS_USDT": {
          "gross_pnl": -0.0221453,
          "pf": 0.0,
          "severe_pnl": -0.058145300000000004,
          "trades": 9,
          "win_rate": 0.0
        },
        "C_USDT": {
          "gross_pnl": -0.004016700000000001,
          "pf": 0.0,
          "severe_pnl": -0.008016700000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "DASH_USDT": {
          "gross_pnl": 0.0055941,
          "pf": 0.0,
          "severe_pnl": -0.3584059000000001,
          "trades": 91,
          "win_rate": 0.0
        },
        "DEEP_USDT": {
          "gross_pnl": 0.0020227,
          "pf": 0.0,
          "severe_pnl": -0.0179773,
          "trades": 5,
          "win_rate": 0.0
        },
        "DEXE_USDT": {
          "gross_pnl": -0.056946699999999996,
          "pf": 0.11550233873851534,
          "severe_pnl": -0.5649466999999998,
          "trades": 127,
          "win_rate": 0.12598425196850394
        },
        "DODO_USDT": {
          "gross_pnl": 0.09193209999999999,
          "pf": 0.44806623550374053,
          "severe_pnl": -0.36006790000000005,
          "trades": 113,
          "win_rate": 0.25663716814159293
        },
        "DOGE_USDT": {
          "gross_pnl": -0.010898000000000003,
          "pf": 0.0,
          "severe_pnl": -0.154898,
          "trades": 36,
          "win_rate": 0.0
        },
        "DOGS_USDT": {
          "gross_pnl": -0.0033039,
          "pf": 0.0,
          "severe_pnl": -0.0313039,
          "trades": 7,
          "win_rate": 0.0
        },
        "DOT_USDT": {
          "gross_pnl": -0.0492904,
          "pf": 0.0,
          "severe_pnl": -0.37729040000000014,
          "trades": 82,
          "win_rate": 0.0
        },
        "DRAM_USDT": {
          "gross_pnl": 0.01661850000000001,
          "pf": 0.02075494095819744,
          "severe_pnl": -0.1913815,
          "trades": 52,
          "win_rate": 0.038461538461538464
        },
        "DYDX_USDT": {
          "gross_pnl": -0.004492899999999999,
          "pf": 0.0,
          "severe_pnl": -0.0684929,
          "trades": 16,
          "win_rate": 0.0
        },
        "EDEN_USDT": {
          "gross_pnl": -0.0037198,
          "pf": 0.0,
          "severe_pnl": -0.0237198,
          "trades": 5,
          "win_rate": 0.0
        },
        "EDGE_USDT": {
          "gross_pnl": 0.027842799999999997,
          "pf": 0.1733083799252586,
          "severe_pnl": -0.2921572,
          "trades": 80,
          "win_rate": 0.1
        },
        "EDU_USDT": {
          "gross_pnl": -0.006984799999999999,
          "pf": 0.0,
          "severe_pnl": -0.0309848,
          "trades": 6,
          "win_rate": 0.0
        },
        "EGLD_USDT": {
          "gross_pnl": 0.015038000000000006,
          "pf": 0.0342548969158311,
          "severe_pnl": -0.49696200000000024,
          "trades": 128,
          "win_rate": 0.0703125
        },
        "EIGEN_USDT": {
          "gross_pnl": 0.0320177,
          "pf": 0.03264302680176277,
          "severe_pnl": -0.8079823000000003,
          "trades": 210,
          "win_rate": 0.0380952380952381
        },
        "ELSA_USDT": {
          "gross_pnl": -0.0076329,
          "pf": 0.016299058538540204,
          "severe_pnl": -0.0876329,
          "trades": 20,
          "win_rate": 0.05
        },
        "ENA_USDT": {
          "gross_pnl": 0.015837499999999997,
          "pf": 0.020977419502587826,
          "severe_pnl": -0.2201625,
          "trades": 59,
          "win_rate": 0.05084745762711865
        },
        "ENJ_USDT": {
          "gross_pnl": -0.0037207999999999994,
          "pf": 0.0,
          "severe_pnl": -0.0517208,
          "trades": 12,
          "win_rate": 0.0
        },
        "ENSO_USDT": {
          "gross_pnl": -0.00014230000000000015,
          "pf": 0.0,
          "severe_pnl": -0.0121423,
          "trades": 3,
          "win_rate": 0.0
        },
        "ENS_USDT": {
          "gross_pnl": -0.008507700000000003,
          "pf": 0.0354979967882585,
          "severe_pnl": -0.20450770000000007,
          "trades": 49,
          "win_rate": 0.02040816326530612
        },
        "EPIC_USDT": {
          "gross_pnl": 0.0002543,
          "pf": 0.0,
          "severe_pnl": -0.0037457000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "ERA_USDT": {
          "gross_pnl": -0.0009322,
          "pf": 0.0,
          "severe_pnl": -0.0049322,
          "trades": 1,
          "win_rate": 0.0
        },
        "ESPORTS_USDT": {
          "gross_pnl": 0.14546730000000008,
          "pf": 0.632135438857347,
          "severe_pnl": -0.25453270000000006,
          "trades": 100,
          "win_rate": 0.33
        },
        "ESP_USDT": {
          "gross_pnl": -0.00025599999999999993,
          "pf": 0.0,
          "severe_pnl": -0.012256,
          "trades": 3,
          "win_rate": 0.0
        },
        "ETC_USDT": {
          "gross_pnl": 0.002588,
          "pf": 0.0,
          "severe_pnl": -0.073412,
          "trades": 19,
          "win_rate": 0.0
        },
        "ETHFI_USDT": {
          "gross_pnl": -0.017382599999999998,
          "pf": 0.01977367859458342,
          "severe_pnl": -0.6133826,
          "trades": 149,
          "win_rate": 0.040268456375838924
        },
        "ETH_USDT": {
          "gross_pnl": 0.004827600000000003,
          "pf": 0.0,
          "severe_pnl": -0.3391724000000001,
          "trades": 86,
          "win_rate": 0.0
        },
        "EUL_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "EVAA_USDT": {
          "gross_pnl": 0.04705629999999998,
          "pf": 0.6279896956654658,
          "severe_pnl": -0.14894370000000004,
          "trades": 49,
          "win_rate": 0.2653061224489796
        },
        "EWJ_USDT": {
          "gross_pnl": 0.0009682,
          "pf": 0.0,
          "severe_pnl": -0.0030318000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "EWY_USDT": {
          "gross_pnl": -0.017682799999999995,
          "pf": 0.0,
          "severe_pnl": -0.24168279999999998,
          "trades": 56,
          "win_rate": 0.0
        },
        "FET_USDT": {
          "gross_pnl": -0.0063797,
          "pf": 0.0,
          "severe_pnl": -0.3023797,
          "trades": 74,
          "win_rate": 0.0
        },
        "FF_USDT": {
          "gross_pnl": -0.0011436000000000016,
          "pf": 0.07168373006237849,
          "severe_pnl": -0.0531436,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "FHE_USDT": {
          "gross_pnl": 0.007599399999999999,
          "pf": 0.11368730451821986,
          "severe_pnl": -0.17640059999999996,
          "trades": 46,
          "win_rate": 0.10869565217391304
        },
        "FILECOIN_USDT": {
          "gross_pnl": 0.004052699999999999,
          "pf": 0.0,
          "severe_pnl": -0.0799473,
          "trades": 21,
          "win_rate": 0.0
        },
        "FLOCK_USDT": {
          "gross_pnl": -0.020023100000000002,
          "pf": 0.0,
          "severe_pnl": -0.0560231,
          "trades": 9,
          "win_rate": 0.0
        },
        "FLOKI_USDT": {
          "gross_pnl": -0.007069300000000001,
          "pf": 0.0,
          "severe_pnl": -0.10306930000000002,
          "trades": 24,
          "win_rate": 0.0
        },
        "FLOW_USDT": {
          "gross_pnl": 0.0011823,
          "pf": 0.0,
          "severe_pnl": -0.0108177,
          "trades": 3,
          "win_rate": 0.0
        },
        "FLUID_USDT": {
          "gross_pnl": 0.005602200000000001,
          "pf": 999,
          "severe_pnl": 0.0016022000000000007,
          "trades": 1,
          "win_rate": 1.0
        },
        "FOGO_USDT": {
          "gross_pnl": 0.0040964999999999994,
          "pf": 0.2371953960096143,
          "severe_pnl": -0.0039035000000000007,
          "trades": 2,
          "win_rate": 0.5
        },
        "FOLKS_USDT": {
          "gross_pnl": -0.0018398000000000004,
          "pf": 0.03988538409971346,
          "severe_pnl": -0.16183979999999998,
          "trades": 40,
          "win_rate": 0.125
        },
        "FORM_USDT": {
          "gross_pnl": -0.0004796,
          "pf": 0.0,
          "severe_pnl": -0.0044796,
          "trades": 1,
          "win_rate": 0.0
        },
        "FRAX_USDT": {
          "gross_pnl": -0.0057036000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0137036,
          "trades": 2,
          "win_rate": 0.0
        },
        "GALA_USDT": {
          "gross_pnl": -0.004994500000000005,
          "pf": 0.011999698572165051,
          "severe_pnl": -0.4129945000000001,
          "trades": 102,
          "win_rate": 0.0196078431372549
        },
        "GAS_USDT": {
          "gross_pnl": -0.0048544,
          "pf": 0.0,
          "severe_pnl": -0.0088544,
          "trades": 1,
          "win_rate": 0.0
        },
        "GENIUS_USDT": {
          "gross_pnl": 0.0025363999999999986,
          "pf": 0.24132917847664012,
          "severe_pnl": -0.013463600000000003,
          "trades": 4,
          "win_rate": 0.25
        },
        "GIGGLE_USDT": {
          "gross_pnl": -0.0018748,
          "pf": 0.0,
          "severe_pnl": -0.0058748,
          "trades": 1,
          "win_rate": 0.0
        },
        "GLM_USDT": {
          "gross_pnl": -0.0029595999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0149596,
          "trades": 3,
          "win_rate": 0.0
        },
        "GMT_USDT": {
          "gross_pnl": -0.0026991,
          "pf": 0.0,
          "severe_pnl": -0.0106991,
          "trades": 2,
          "win_rate": 0.0
        },
        "GPS_USDT": {
          "gross_pnl": 0.0042167,
          "pf": 0.10799648308046082,
          "severe_pnl": -0.019783299999999997,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "GRAM_USDT": {
          "gross_pnl": 0.010875799999999996,
          "pf": 0.0,
          "severe_pnl": -0.1011242,
          "trades": 28,
          "win_rate": 0.0
        },
        "GRASS_USDT": {
          "gross_pnl": 0.0037325,
          "pf": 0.054784838863396634,
          "severe_pnl": -0.0882675,
          "trades": 23,
          "win_rate": 0.08695652173913043
        },
        "GRIFFAIN_USDT": {
          "gross_pnl": 0.0099379,
          "pf": 999,
          "severe_pnl": 0.005937899999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "GRT_USDT": {
          "gross_pnl": 0.0005420000000000003,
          "pf": 0.0,
          "severe_pnl": -0.035458,
          "trades": 9,
          "win_rate": 0.0
        },
        "GUA_USDT": {
          "gross_pnl": 0.0119486,
          "pf": 0.3465303140978816,
          "severe_pnl": -0.0080514,
          "trades": 5,
          "win_rate": 0.4
        },
        "GUN_USDT": {
          "gross_pnl": -0.0178677,
          "pf": 0.0,
          "severe_pnl": -0.07386770000000001,
          "trades": 14,
          "win_rate": 0.0
        },
        "G_USDT": {
          "gross_pnl": 0.0042035,
          "pf": 0.41542159121881117,
          "severe_pnl": -0.011796500000000001,
          "trades": 4,
          "win_rate": 0.25
        },
        "HBAR_USDT": {
          "gross_pnl": 0.007659100000000004,
          "pf": 0.005305100346303489,
          "severe_pnl": -0.24834090000000006,
          "trades": 64,
          "win_rate": 0.015625
        },
        "HEI_USDT": {
          "gross_pnl": -0.019508800000000007,
          "pf": 0.09718457090733228,
          "severe_pnl": -0.2115088000000001,
          "trades": 48,
          "win_rate": 0.14583333333333334
        },
        "HIGH_USDT": {
          "gross_pnl": -0.020382500000000005,
          "pf": 0.04069183721094304,
          "severe_pnl": -0.08838249999999999,
          "trades": 17,
          "win_rate": 0.11764705882352941
        },
        "HK50_USDT": {
          "gross_pnl": -0.0032072999999999997,
          "pf": 0.0,
          "severe_pnl": -0.051207300000000004,
          "trades": 12,
          "win_rate": 0.0
        },
        "HMSTR_USDT": {
          "gross_pnl": 0.006356500000000001,
          "pf": 0.01366980910730837,
          "severe_pnl": -0.025643500000000007,
          "trades": 8,
          "win_rate": 0.125
        },
        "HNT_USDT": {
          "gross_pnl": -0.001404,
          "pf": 0.0,
          "severe_pnl": -0.009404,
          "trades": 2,
          "win_rate": 0.0
        },
        "HOLO_USDT": {
          "gross_pnl": -0.0004238,
          "pf": 0.0,
          "severe_pnl": -0.0044238,
          "trades": 1,
          "win_rate": 0.0
        },
        "HOME_USDT": {
          "gross_pnl": 0.02140119999999999,
          "pf": 0.257945745268348,
          "severe_pnl": -0.1985988,
          "trades": 55,
          "win_rate": 0.23636363636363636
        },
        "HOT_USDT": {
          "gross_pnl": -0.013121800000000003,
          "pf": 0.1866032692054866,
          "severe_pnl": -0.0371218,
          "trades": 6,
          "win_rate": 0.3333333333333333
        },
        "HYPE_USDT": {
          "gross_pnl": 0.002926299999999998,
          "pf": 0.014305912881214813,
          "severe_pnl": -0.2090737,
          "trades": 53,
          "win_rate": 0.018867924528301886
        },
        "ICP_USDT": {
          "gross_pnl": -0.0020784000000000015,
          "pf": 0.012226650342521541,
          "severe_pnl": -0.29407839999999996,
          "trades": 73,
          "win_rate": 0.0136986301369863
        },
        "ICX_USDT": {
          "gross_pnl": -0.0008452999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0048453,
          "trades": 1,
          "win_rate": 0.0
        },
        "ID_USDT": {
          "gross_pnl": -0.0085682,
          "pf": 0.0,
          "severe_pnl": -0.028568200000000002,
          "trades": 5,
          "win_rate": 0.0
        },
        "IMX_USDT": {
          "gross_pnl": -0.0022914999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0302915,
          "trades": 7,
          "win_rate": 0.0
        },
        "INDA_USDT": {
          "gross_pnl": -0.0231991,
          "pf": 0.005692262972726448,
          "severe_pnl": -0.09919910000000001,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "INJ_USDT": {
          "gross_pnl": -0.019656100000000006,
          "pf": 0.0,
          "severe_pnl": -0.3716561000000001,
          "trades": 88,
          "win_rate": 0.0
        },
        "INTW_USDT": {
          "gross_pnl": -0.004784,
          "pf": 0.0,
          "severe_pnl": -0.024784,
          "trades": 5,
          "win_rate": 0.0
        },
        "IN_USDT": {
          "gross_pnl": -0.0020773,
          "pf": 0.0,
          "severe_pnl": -0.0060773,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTA_USDT": {
          "gross_pnl": 0.007137999999999999,
          "pf": 0.8182776430905448,
          "severe_pnl": -0.0008620000000000008,
          "trades": 2,
          "win_rate": 0.5
        },
        "IOTX_USDT": {
          "gross_pnl": 0.0007779,
          "pf": 0.0,
          "severe_pnl": -0.0032221000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "IO_USDT": {
          "gross_pnl": -0.002381,
          "pf": 0.0,
          "severe_pnl": -0.010381,
          "trades": 2,
          "win_rate": 0.0
        },
        "JASMY_USDT": {
          "gross_pnl": -0.017830999999999996,
          "pf": 0.0021498801214459716,
          "severe_pnl": -0.25783100000000003,
          "trades": 60,
          "win_rate": 0.03333333333333333
        },
        "JCT_USDT": {
          "gross_pnl": 0.014580099999999999,
          "pf": 0.31465754311042093,
          "severe_pnl": -0.0254199,
          "trades": 10,
          "win_rate": 0.3
        },
        "JP225_USDT": {
          "gross_pnl": -0.00029239999999999995,
          "pf": 0.03314141314338923,
          "severe_pnl": -0.0322924,
          "trades": 8,
          "win_rate": 0.125
        },
        "JST_USDT": {
          "gross_pnl": 0.0022494,
          "pf": 0.0,
          "severe_pnl": -0.021750600000000002,
          "trades": 6,
          "win_rate": 0.0
        },
        "JTO_USDT": {
          "gross_pnl": -0.0016018999999999983,
          "pf": 0.04938310427007164,
          "severe_pnl": -0.34160190000000007,
          "trades": 85,
          "win_rate": 0.011764705882352941
        },
        "JUP_USDT": {
          "gross_pnl": -0.023095700000000004,
          "pf": 0.008848327371177014,
          "severe_pnl": -0.5910957000000001,
          "trades": 142,
          "win_rate": 0.02112676056338028
        },
        "KAIA_USDT": {
          "gross_pnl": 0.0011522000000000001,
          "pf": 0.0,
          "severe_pnl": -0.018847799999999998,
          "trades": 5,
          "win_rate": 0.0
        },
        "KAITO_USDT": {
          "gross_pnl": -0.027259899999999993,
          "pf": 0.05044931633195315,
          "severe_pnl": -0.2392599,
          "trades": 53,
          "win_rate": 0.09433962264150944
        },
        "KAS_USDT": {
          "gross_pnl": -0.010229299999999997,
          "pf": 0.0,
          "severe_pnl": -0.12222930000000001,
          "trades": 28,
          "win_rate": 0.0
        },
        "KERNEL_USDT": {
          "gross_pnl": -0.0019642,
          "pf": 0.0,
          "severe_pnl": -0.0059642,
          "trades": 1,
          "win_rate": 0.0
        },
        "KITE_USDT": {
          "gross_pnl": 2.350000000000095e-05,
          "pf": 0.020666278545287367,
          "severe_pnl": -0.12397650000000002,
          "trades": 31,
          "win_rate": 0.0967741935483871
        },
        "KMNO_USDT": {
          "gross_pnl": 0.0050477000000000005,
          "pf": 0.0,
          "severe_pnl": -0.022952300000000002,
          "trades": 7,
          "win_rate": 0.0
        },
        "KORU_USDT": {
          "gross_pnl": 0.027810400000000002,
          "pf": 0.18731724357061508,
          "severe_pnl": -0.25218960000000007,
          "trades": 70,
          "win_rate": 0.22857142857142856
        },
        "KSM_USDT": {
          "gross_pnl": -0.0005858000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0125858,
          "trades": 3,
          "win_rate": 0.0
        },
        "KSTR_USDT": {
          "gross_pnl": 0.0007822,
          "pf": 0.0,
          "severe_pnl": -0.0072178,
          "trades": 2,
          "win_rate": 0.0
        },
        "LAB_USDT": {
          "gross_pnl": -0.1503517,
          "pf": 0.33023420897271466,
          "severe_pnl": -0.3783516999999998,
          "trades": 57,
          "win_rate": 0.2807017543859649
        },
        "LAYER_USDT": {
          "gross_pnl": -0.0016103,
          "pf": 0.0,
          "severe_pnl": -0.0056103,
          "trades": 1,
          "win_rate": 0.0
        },
        "LDO_USDT": {
          "gross_pnl": 0.002985499999999999,
          "pf": 0.005144468496894251,
          "severe_pnl": -0.6490144999999998,
          "trades": 163,
          "win_rate": 0.024539877300613498
        },
        "LEAD_USDT": {
          "gross_pnl": 0.0005056,
          "pf": 0.0,
          "severe_pnl": -0.0234944,
          "trades": 6,
          "win_rate": 0.0
        },
        "LIGHT_USDT": {
          "gross_pnl": 0.008376399999999999,
          "pf": 0.20295556530247313,
          "severe_pnl": -0.023623599999999998,
          "trades": 8,
          "win_rate": 0.125
        },
        "LINEA_USDT": {
          "gross_pnl": -0.005570900000000001,
          "pf": 0.0,
          "severe_pnl": -0.0335709,
          "trades": 7,
          "win_rate": 0.0
        },
        "LINK_USDT": {
          "gross_pnl": -0.020451000000000007,
          "pf": 0.0,
          "severe_pnl": -0.24845099999999995,
          "trades": 57,
          "win_rate": 0.0
        },
        "LIT_USDT": {
          "gross_pnl": -0.001127199999999998,
          "pf": 0.009895545436547212,
          "severe_pnl": -0.6251272000000004,
          "trades": 156,
          "win_rate": 0.019230769230769232
        },
        "LRC_USDT": {
          "gross_pnl": -0.13672280000000003,
          "pf": 0.06694150417827298,
          "severe_pnl": -0.28472279999999994,
          "trades": 37,
          "win_rate": 0.1891891891891892
        },
        "LTC_USDT": {
          "gross_pnl": -0.0123804,
          "pf": 0.0,
          "severe_pnl": -0.20038040000000004,
          "trades": 47,
          "win_rate": 0.0
        },
        "LUMIA_USDT": {
          "gross_pnl": -0.014398000000000003,
          "pf": 0.12140485219389845,
          "severe_pnl": -0.098398,
          "trades": 21,
          "win_rate": 0.19047619047619047
        },
        "LUNANEW_USDT": {
          "gross_pnl": 0.0012958,
          "pf": 0.0,
          "severe_pnl": -0.0067042000000000004,
          "trades": 2,
          "win_rate": 0.0
        },
        "LUNC_USDT": {
          "gross_pnl": -0.005323699999999999,
          "pf": 0.0,
          "severe_pnl": -0.18932369999999998,
          "trades": 46,
          "win_rate": 0.0
        },
        "LYN_USDT": {
          "gross_pnl": -0.0209598,
          "pf": 0.0,
          "severe_pnl": -0.0289598,
          "trades": 2,
          "win_rate": 0.0
        },
        "MAGMA_USDT": {
          "gross_pnl": -0.123553,
          "pf": 0.15915507289117453,
          "severe_pnl": -0.48755299999999996,
          "trades": 91,
          "win_rate": 0.16483516483516483
        },
        "MANA_USDT": {
          "gross_pnl": -0.0085954,
          "pf": 0.0,
          "severe_pnl": -0.0685954,
          "trades": 15,
          "win_rate": 0.0
        },
        "MANTA_USDT": {
          "gross_pnl": 0.008454399999999999,
          "pf": 0.019519108834572446,
          "severe_pnl": -0.03154560000000001,
          "trades": 10,
          "win_rate": 0.2
        },
        "MANTRA_USDT": {
          "gross_pnl": -0.030410300000000005,
          "pf": 0.07028003937669935,
          "severe_pnl": -0.09841029999999999,
          "trades": 17,
          "win_rate": 0.17647058823529413
        },
        "MASK_USDT": {
          "gross_pnl": -0.0005086,
          "pf": 0.0,
          "severe_pnl": -0.0045086,
          "trades": 1,
          "win_rate": 0.0
        },
        "MAV_USDT": {
          "gross_pnl": -0.0020182,
          "pf": 0.0,
          "severe_pnl": -0.0140182,
          "trades": 3,
          "win_rate": 0.0
        },
        "MEGA_USDT": {
          "gross_pnl": -0.00014729999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0081473,
          "trades": 2,
          "win_rate": 0.0
        },
        "MEME_USDT": {
          "gross_pnl": -0.0003488999999999992,
          "pf": 0.0,
          "severe_pnl": -0.0243489,
          "trades": 6,
          "win_rate": 0.0
        },
        "MERL_USDT": {
          "gross_pnl": -0.0073925,
          "pf": 0.0,
          "severe_pnl": -0.0513925,
          "trades": 11,
          "win_rate": 0.0
        },
        "METIS_USDT": {
          "gross_pnl": 1.1400000000000006e-05,
          "pf": 0.0,
          "severe_pnl": -0.0079886,
          "trades": 2,
          "win_rate": 0.0
        },
        "MET_USDT": {
          "gross_pnl": -0.009194299999999999,
          "pf": 0.0,
          "severe_pnl": -0.0211943,
          "trades": 3,
          "win_rate": 0.0
        },
        "MEW_USDT": {
          "gross_pnl": -0.0054659999999999995,
          "pf": 0.0,
          "severe_pnl": -0.009465999999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "ME_USDT": {
          "gross_pnl": -0.0028754,
          "pf": 0.0,
          "severe_pnl": -0.0068754,
          "trades": 1,
          "win_rate": 0.0
        },
        "MINA_USDT": {
          "gross_pnl": 0.0021821,
          "pf": 0.0,
          "severe_pnl": -0.005817899999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "MIRA_USDT": {
          "gross_pnl": 0.0026718,
          "pf": 0.11093108148035186,
          "severe_pnl": -0.0093282,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "MITO_USDT": {
          "gross_pnl": -0.037441800000000004,
          "pf": 0.0,
          "severe_pnl": -0.061441800000000005,
          "trades": 6,
          "win_rate": 0.0
        },
        "MMT_USDT": {
          "gross_pnl": -0.026805699999999995,
          "pf": 0.05131677500598774,
          "severe_pnl": -0.24280569999999996,
          "trades": 54,
          "win_rate": 0.09259259259259259
        },
        "MNT_USDT": {
          "gross_pnl": -0.0017173000000000008,
          "pf": 0.0,
          "severe_pnl": -0.045717299999999995,
          "trades": 11,
          "win_rate": 0.0
        },
        "MOCA_USDT": {
          "gross_pnl": -0.0044743,
          "pf": 0.0,
          "severe_pnl": -0.0084743,
          "trades": 1,
          "win_rate": 0.0
        },
        "MONAD_USDT": {
          "gross_pnl": -0.029624500000000005,
          "pf": 0.0,
          "severe_pnl": -0.16562449999999998,
          "trades": 34,
          "win_rate": 0.0
        },
        "MOODENG_USDT": {
          "gross_pnl": 0.024295900000000002,
          "pf": 999,
          "severe_pnl": 0.020295900000000002,
          "trades": 1,
          "win_rate": 1.0
        },
        "MORPHO_USDT": {
          "gross_pnl": -0.015895900000000004,
          "pf": 0.0,
          "severe_pnl": -0.1078959,
          "trades": 23,
          "win_rate": 0.0
        },
        "MOVE_USDT": {
          "gross_pnl": -0.0018034,
          "pf": 0.0,
          "severe_pnl": -0.0138034,
          "trades": 3,
          "win_rate": 0.0
        },
        "MSTU_USDT": {
          "gross_pnl": -0.035344299999999995,
          "pf": 0.0,
          "severe_pnl": -0.06334429999999999,
          "trades": 7,
          "win_rate": 0.0
        },
        "MUBARAK_USDT": {
          "gross_pnl": -0.0014482,
          "pf": 0.0,
          "severe_pnl": -0.0054482,
          "trades": 1,
          "win_rate": 0.0
        },
        "MUU_USDT": {
          "gross_pnl": -0.0013679000000000002,
          "pf": 0.0,
          "severe_pnl": -0.013367900000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "MVLL_USDT": {
          "gross_pnl": 0.014116000000000004,
          "pf": 0.24068241851918354,
          "severe_pnl": -0.09388400000000001,
          "trades": 27,
          "win_rate": 0.25925925925925924
        },
        "MYX_USDT": {
          "gross_pnl": -0.04769809999999999,
          "pf": 0.05559588342380636,
          "severe_pnl": -0.3716981000000001,
          "trades": 81,
          "win_rate": 0.09876543209876543
        },
        "NAORIS_USDT": {
          "gross_pnl": -0.028931599999999995,
          "pf": 0.0051900042386232,
          "severe_pnl": -0.09693160000000002,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "NEAR_USDT": {
          "gross_pnl": -0.03546039999999999,
          "pf": 0.0004322204961486884,
          "severe_pnl": -0.3954603999999998,
          "trades": 90,
          "win_rate": 0.011111111111111112
        },
        "NEO_USDT": {
          "gross_pnl": 0.00197,
          "pf": 0.0,
          "severe_pnl": -0.006030000000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "NES_USDT": {
          "gross_pnl": -0.003133300000000001,
          "pf": 0.0006552531646207641,
          "severe_pnl": -0.09913330000000002,
          "trades": 24,
          "win_rate": 0.041666666666666664
        },
        "NEX_USDT": {
          "gross_pnl": 0.007327200000000001,
          "pf": 999,
          "severe_pnl": 0.0033272000000000006,
          "trades": 1,
          "win_rate": 1.0
        },
        "NGAS_USDT": {
          "gross_pnl": -0.0106228,
          "pf": 0.0,
          "severe_pnl": -0.20662279999999997,
          "trades": 49,
          "win_rate": 0.0
        },
        "NICKEL_USDT": {
          "gross_pnl": 0.0013926000000000001,
          "pf": 0.0,
          "severe_pnl": -0.042607400000000004,
          "trades": 11,
          "win_rate": 0.0
        },
        "NIGHT_USDT": {
          "gross_pnl": -0.0032165000000000006,
          "pf": 0.0,
          "severe_pnl": -0.059216500000000005,
          "trades": 14,
          "win_rate": 0.0
        },
        "NIL_USDT": {
          "gross_pnl": -0.0045055,
          "pf": 0.0,
          "severe_pnl": -0.044505499999999996,
          "trades": 10,
          "win_rate": 0.0
        },
        "NOM_USDT": {
          "gross_pnl": 0.0007783999999999998,
          "pf": 0.0,
          "severe_pnl": -0.011221600000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "NOT_USDT": {
          "gross_pnl": -0.0034424000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0194424,
          "trades": 4,
          "win_rate": 0.0
        },
        "OFC_USDT": {
          "gross_pnl": 0.0056544,
          "pf": 0.0,
          "severe_pnl": -0.0143456,
          "trades": 5,
          "win_rate": 0.0
        },
        "OGN_USDT": {
          "gross_pnl": 0.0010858999999999999,
          "pf": 0.01852816113281107,
          "severe_pnl": -0.0669141,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "OG_USDT": {
          "gross_pnl": -0.010534800000000002,
          "pf": 0.0,
          "severe_pnl": -0.0265348,
          "trades": 4,
          "win_rate": 0.0
        },
        "OKB_USDT": {
          "gross_pnl": -0.0002468,
          "pf": 0.0,
          "severe_pnl": -0.0042468,
          "trades": 1,
          "win_rate": 0.0
        },
        "OL_USDT": {
          "gross_pnl": 0.0018363000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0061637,
          "trades": 2,
          "win_rate": 0.0
        },
        "ONDO_USDT": {
          "gross_pnl": -0.037518,
          "pf": 0.012878814531472079,
          "severe_pnl": -0.5415180000000002,
          "trades": 126,
          "win_rate": 0.03968253968253968
        },
        "ONE_USDT": {
          "gross_pnl": -0.0018022,
          "pf": 0.0,
          "severe_pnl": -0.0218022,
          "trades": 5,
          "win_rate": 0.0
        },
        "ONT_USDT": {
          "gross_pnl": -0.0006586000000000001,
          "pf": 0.0,
          "severe_pnl": -0.004658600000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "OPENAI_USDT": {
          "gross_pnl": -0.0638776,
          "pf": 0.0,
          "severe_pnl": -0.4238776,
          "trades": 90,
          "win_rate": 0.0
        },
        "OPG_USDT": {
          "gross_pnl": -0.004203799999999996,
          "pf": 0.07870180245263052,
          "severe_pnl": -0.09220380000000002,
          "trades": 22,
          "win_rate": 0.045454545454545456
        },
        "OPN_USDT": {
          "gross_pnl": -0.018578200000000003,
          "pf": 0.03554122624181479,
          "severe_pnl": -0.20257819999999993,
          "trades": 46,
          "win_rate": 0.08695652173913043
        },
        "OP_USDT": {
          "gross_pnl": -0.07439470000000002,
          "pf": 0.0034412816681866085,
          "severe_pnl": -0.7703947000000004,
          "trades": 174,
          "win_rate": 0.005747126436781609
        },
        "ORCA_USDT": {
          "gross_pnl": 0.0008403,
          "pf": 0.0,
          "severe_pnl": -0.0031597,
          "trades": 1,
          "win_rate": 0.0
        },
        "ORDI_USDT": {
          "gross_pnl": -0.015501499999999994,
          "pf": 0.01588712680657509,
          "severe_pnl": -0.5235015000000001,
          "trades": 127,
          "win_rate": 0.023622047244094488
        },
        "O_USDT": {
          "gross_pnl": -0.012988399999999999,
          "pf": 0.128998152993749,
          "severe_pnl": -0.22498839999999995,
          "trades": 53,
          "win_rate": 0.09433962264150944
        },
        "PARTI_USDT": {
          "gross_pnl": -0.009243399999999999,
          "pf": 0.039822016663514405,
          "severe_pnl": -0.04924339999999999,
          "trades": 10,
          "win_rate": 0.1
        },
        "PAXG_USDT": {
          "gross_pnl": -0.0047583,
          "pf": 0.0,
          "severe_pnl": -0.024758300000000004,
          "trades": 5,
          "win_rate": 0.0
        },
        "PENDLE_USDT": {
          "gross_pnl": -0.0050967999999999986,
          "pf": 0.0032114644263242635,
          "severe_pnl": -0.13709680000000002,
          "trades": 33,
          "win_rate": 0.030303030303030304
        },
        "PEOPLE_USDT": {
          "gross_pnl": 0.0001819,
          "pf": 0.0,
          "severe_pnl": -0.0038181,
          "trades": 1,
          "win_rate": 0.0
        },
        "PEPE_USDT": {
          "gross_pnl": -0.0026333999999999997,
          "pf": 0.0,
          "severe_pnl": -0.022633399999999998,
          "trades": 5,
          "win_rate": 0.0
        },
        "PHA_USDT": {
          "gross_pnl": -0.0033521000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0153521,
          "trades": 3,
          "win_rate": 0.0
        },
        "PIEVERSE_USDT": {
          "gross_pnl": -0.0026851,
          "pf": 0.0,
          "severe_pnl": -0.0226851,
          "trades": 5,
          "win_rate": 0.0
        },
        "PIPPIN_USDT": {
          "gross_pnl": -0.10566249999999998,
          "pf": 0.03605565959406181,
          "severe_pnl": -0.37766249999999985,
          "trades": 68,
          "win_rate": 0.058823529411764705
        },
        "PIXEL_USDT": {
          "gross_pnl": -0.0090257,
          "pf": 0.0,
          "severe_pnl": -0.0170257,
          "trades": 2,
          "win_rate": 0.0
        },
        "PI_USDT": {
          "gross_pnl": -0.02332830000000001,
          "pf": 0.14228822687811055,
          "severe_pnl": -0.7753283000000002,
          "trades": 188,
          "win_rate": 0.0425531914893617
        },
        "PLUME_USDT": {
          "gross_pnl": -0.0039843,
          "pf": 0.0,
          "severe_pnl": -0.0159843,
          "trades": 3,
          "win_rate": 0.0
        },
        "PNUT_USDT": {
          "gross_pnl": -0.0018713,
          "pf": 0.0,
          "severe_pnl": -0.0098713,
          "trades": 2,
          "win_rate": 0.0
        },
        "POL_USDT": {
          "gross_pnl": -0.010866899999999999,
          "pf": 0.0,
          "severe_pnl": -0.2188669,
          "trades": 52,
          "win_rate": 0.0
        },
        "POPCAT_USDT": {
          "gross_pnl": -0.0011364,
          "pf": 0.0,
          "severe_pnl": -0.0131364,
          "trades": 3,
          "win_rate": 0.0
        },
        "PORTAL_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "POWER_USDT": {
          "gross_pnl": -0.0033298,
          "pf": 0.0,
          "severe_pnl": -0.011329800000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "POWR_USDT": {
          "gross_pnl": -0.0064905,
          "pf": 0.0,
          "severe_pnl": -0.0104905,
          "trades": 1,
          "win_rate": 0.0
        },
        "PROMPT_USDT": {
          "gross_pnl": 0.0012146,
          "pf": 0.0,
          "severe_pnl": -0.0027854000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "PROM_USDT": {
          "gross_pnl": -0.0038033000000000003,
          "pf": 0.0,
          "severe_pnl": -0.019803300000000003,
          "trades": 4,
          "win_rate": 0.0
        },
        "PTB_USDT": {
          "gross_pnl": -0.00016549999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0041655,
          "trades": 1,
          "win_rate": 0.0
        },
        "PUMPFUN_USDT": {
          "gross_pnl": -0.051099799999999994,
          "pf": 0.015383363079688009,
          "severe_pnl": -0.4910998000000003,
          "trades": 110,
          "win_rate": 0.045454545454545456
        },
        "PUNDIX_USDT": {
          "gross_pnl": -0.0040516,
          "pf": 0.0,
          "severe_pnl": -0.008051599999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "PYTH_USDT": {
          "gross_pnl": -0.018924599999999996,
          "pf": 0.018726799248330515,
          "severe_pnl": -0.5349245999999996,
          "trades": 129,
          "win_rate": 0.046511627906976744
        },
        "QNT_USDT": {
          "gross_pnl": -0.000759,
          "pf": 0.0,
          "severe_pnl": -0.008759,
          "trades": 2,
          "win_rate": 0.0
        },
        "QTUM_USDT": {
          "gross_pnl": -0.0004743000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0124743,
          "trades": 3,
          "win_rate": 0.0
        },
        "Q_USDT": {
          "gross_pnl": 0.0019825,
          "pf": 0.0,
          "severe_pnl": -0.0020175,
          "trades": 1,
          "win_rate": 0.0
        },
        "RAM_USDT": {
          "gross_pnl": -0.022860299999999997,
          "pf": 0.033669825557392986,
          "severe_pnl": -0.08286030000000001,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "RARE_USDT": {
          "gross_pnl": -0.006383,
          "pf": 0.0,
          "severe_pnl": -0.010383,
          "trades": 1,
          "win_rate": 0.0
        },
        "RAVE_USDT": {
          "gross_pnl": -0.008659599999999991,
          "pf": 0.08201036801448364,
          "severe_pnl": -0.39265959999999994,
          "trades": 96,
          "win_rate": 0.0625
        },
        "RAY_USDT": {
          "gross_pnl": 0.005141000000000001,
          "pf": 0.06541291905151268,
          "severe_pnl": -0.014859,
          "trades": 5,
          "win_rate": 0.2
        },
        "RENDER_USDT": {
          "gross_pnl": -0.0254168,
          "pf": 0.0,
          "severe_pnl": -0.2894168000000001,
          "trades": 66,
          "win_rate": 0.0
        },
        "RESOLV_USDT": {
          "gross_pnl": -0.06372489999999999,
          "pf": 0.0,
          "severe_pnl": -0.2557249,
          "trades": 48,
          "win_rate": 0.0
        },
        "REZ_USDT": {
          "gross_pnl": 0.0014366000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0065634,
          "trades": 2,
          "win_rate": 0.0
        },
        "RE_USDT": {
          "gross_pnl": -0.06115679999999999,
          "pf": 0.01612566154749867,
          "severe_pnl": -0.5051568000000004,
          "trades": 111,
          "win_rate": 0.036036036036036036
        },
        "RIF_USDT": {
          "gross_pnl": -0.026521000000000003,
          "pf": 0.0,
          "severe_pnl": -0.08252099999999998,
          "trades": 14,
          "win_rate": 0.0
        },
        "RLC_USDT": {
          "gross_pnl": 0.004045,
          "pf": 0.0,
          "severe_pnl": -0.027955,
          "trades": 8,
          "win_rate": 0.0
        },
        "ROAM_USDT": {
          "gross_pnl": 0.19348220000000002,
          "pf": 1.5735618581652282,
          "severe_pnl": 0.12548220000000002,
          "trades": 17,
          "win_rate": 0.47058823529411764
        },
        "ROBO_USDT": {
          "gross_pnl": -0.0010319,
          "pf": 0.0,
          "severe_pnl": -0.009031899999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "ROSE_USDT": {
          "gross_pnl": 0.0075542000000000005,
          "pf": 0.096241461477363,
          "severe_pnl": -0.028445799999999997,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "RPL_USDT": {
          "gross_pnl": 0.0017836,
          "pf": 0.0,
          "severe_pnl": -0.0062164,
          "trades": 2,
          "win_rate": 0.0
        },
        "RSR_USDT": {
          "gross_pnl": -0.0087493,
          "pf": 0.0,
          "severe_pnl": -0.0367493,
          "trades": 7,
          "win_rate": 0.0
        },
        "RUNE_USDT": {
          "gross_pnl": 0.0056979000000000005,
          "pf": 0.0,
          "severe_pnl": -0.030302100000000002,
          "trades": 9,
          "win_rate": 0.0
        },
        "RVN_USDT": {
          "gross_pnl": -0.013773599999999995,
          "pf": 0.06359085989394954,
          "severe_pnl": -0.06177360000000001,
          "trades": 12,
          "win_rate": 0.16666666666666666
        },
        "SAFE_USDT": {
          "gross_pnl": -0.0069355,
          "pf": 0.0,
          "severe_pnl": -0.0189355,
          "trades": 3,
          "win_rate": 0.0
        },
        "SAGA_USDT": {
          "gross_pnl": 0.0016022999999999996,
          "pf": 0.0,
          "severe_pnl": -0.010397700000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "SAHARA_USDT": {
          "gross_pnl": 0.0064823,
          "pf": 0.0,
          "severe_pnl": -0.041517700000000005,
          "trades": 12,
          "win_rate": 0.0
        },
        "SAND_USDT": {
          "gross_pnl": 0.0010110000000000002,
          "pf": 0.0,
          "severe_pnl": -0.042989000000000006,
          "trades": 11,
          "win_rate": 0.0
        },
        "SANTOS_USDT": {
          "gross_pnl": -0.006432499999999999,
          "pf": 0.0,
          "severe_pnl": -0.0144325,
          "trades": 2,
          "win_rate": 0.0
        },
        "SEI_USDT": {
          "gross_pnl": -0.023821899999999997,
          "pf": 0.0,
          "severe_pnl": -0.3198219000000001,
          "trades": 74,
          "win_rate": 0.0
        },
        "SENT_USDT": {
          "gross_pnl": 0.03433699999999999,
          "pf": 0.44968990948709353,
          "severe_pnl": -0.065663,
          "trades": 25,
          "win_rate": 0.24
        },
        "SFP_USDT": {
          "gross_pnl": -0.0004662,
          "pf": 0.0,
          "severe_pnl": -0.0044662,
          "trades": 1,
          "win_rate": 0.0
        },
        "SHIB_USDT": {
          "gross_pnl": -0.0007669999999999999,
          "pf": 0.0,
          "severe_pnl": -0.11276700000000003,
          "trades": 28,
          "win_rate": 0.0
        },
        "SIGN_USDT": {
          "gross_pnl": -0.0001149,
          "pf": 0.0,
          "severe_pnl": -0.0041149,
          "trades": 1,
          "win_rate": 0.0
        },
        "SKL_USDT": {
          "gross_pnl": -0.0411889,
          "pf": 0.3008070955763985,
          "severe_pnl": -0.19718890000000003,
          "trades": 39,
          "win_rate": 0.3076923076923077
        },
        "SKYAI_USDT": {
          "gross_pnl": 0.009054600000000001,
          "pf": 0.06741201273722826,
          "severe_pnl": -0.5789454000000002,
          "trades": 147,
          "win_rate": 0.07482993197278912
        },
        "SKY_USDT": {
          "gross_pnl": -0.006238599999999999,
          "pf": 0.0,
          "severe_pnl": -0.05423860000000001,
          "trades": 12,
          "win_rate": 0.0
        },
        "SLX_USDT": {
          "gross_pnl": -0.15694460000000002,
          "pf": 0.03694058853040842,
          "severe_pnl": -0.7129446000000002,
          "trades": 139,
          "win_rate": 0.02877697841726619
        },
        "SMH_USDT": {
          "gross_pnl": 0.002046,
          "pf": 0.0,
          "severe_pnl": -0.001954,
          "trades": 1,
          "win_rate": 0.0
        },
        "SNT_USDT": {
          "gross_pnl": -0.0057766,
          "pf": 0.0,
          "severe_pnl": -0.0177766,
          "trades": 3,
          "win_rate": 0.0
        },
        "SNXX_USDT": {
          "gross_pnl": 0.0032695999999999966,
          "pf": 0.3073670259552848,
          "severe_pnl": -0.1047304,
          "trades": 27,
          "win_rate": 0.2222222222222222
        },
        "SNX_USDT": {
          "gross_pnl": 0.0013723000000000008,
          "pf": 0.0,
          "severe_pnl": -0.0266277,
          "trades": 7,
          "win_rate": 0.0
        },
        "SOL_USDT": {
          "gross_pnl": 0.007086100000000001,
          "pf": 0.0065886356438252915,
          "severe_pnl": -0.1289139,
          "trades": 34,
          "win_rate": 0.029411764705882353
        },
        "SOONNETWORK_USDT": {
          "gross_pnl": -8.999999999999677e-07,
          "pf": 0.0,
          "severe_pnl": -0.0120009,
          "trades": 3,
          "win_rate": 0.0
        },
        "SOXL_USDT": {
          "gross_pnl": -0.103005,
          "pf": 0.08174845284958812,
          "severe_pnl": -0.5630050000000002,
          "trades": 115,
          "win_rate": 0.12173913043478261
        },
        "SOXS_USDT": {
          "gross_pnl": -0.021949400000000008,
          "pf": 0.02610529502887971,
          "severe_pnl": -0.12994940000000002,
          "trades": 27,
          "win_rate": 0.07407407407407407
        },
        "SOXX_USDT": {
          "gross_pnl": -0.006848099999999999,
          "pf": 0.0,
          "severe_pnl": -0.054848100000000004,
          "trades": 12,
          "win_rate": 0.0
        },
        "SPACE_USDT": {
          "gross_pnl": -0.0007081,
          "pf": 0.0,
          "severe_pnl": -0.0047081,
          "trades": 1,
          "win_rate": 0.0
        },
        "SPELL_USDT": {
          "gross_pnl": -0.0391165,
          "pf": 0.0,
          "severe_pnl": -0.0591165,
          "trades": 5,
          "win_rate": 0.0
        },
        "SPORTFUN_USDT": {
          "gross_pnl": 0.038268,
          "pf": 7.803020767778477,
          "severe_pnl": 0.030268000000000003,
          "trades": 2,
          "win_rate": 0.5
        },
        "SPY_USDT": {
          "gross_pnl": 0.00045809999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0035419,
          "trades": 1,
          "win_rate": 0.0
        },
        "SQD_USDT": {
          "gross_pnl": -0.017135400000000002,
          "pf": 0.0,
          "severe_pnl": -0.0451354,
          "trades": 7,
          "win_rate": 0.0
        },
        "SQQQ_USDT": {
          "gross_pnl": -0.0055834000000000005,
          "pf": 0.0,
          "severe_pnl": -0.025583399999999996,
          "trades": 5,
          "win_rate": 0.0
        },
        "STABLE_USDT": {
          "gross_pnl": -0.0238851,
          "pf": 0.0,
          "severe_pnl": -0.0598851,
          "trades": 9,
          "win_rate": 0.0
        },
        "STAR_USDT": {
          "gross_pnl": -0.008553999999999999,
          "pf": 0.0,
          "severe_pnl": -0.020554,
          "trades": 3,
          "win_rate": 0.0
        },
        "STG_USDT": {
          "gross_pnl": -0.006367500000000002,
          "pf": 0.0,
          "severe_pnl": -0.0743675,
          "trades": 17,
          "win_rate": 0.0
        },
        "STO_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "STRK_USDT": {
          "gross_pnl": -0.011214,
          "pf": 0.0,
          "severe_pnl": -0.055214,
          "trades": 11,
          "win_rate": 0.0
        },
        "STX_USDT": {
          "gross_pnl": -0.0182679,
          "pf": 0.0,
          "severe_pnl": -0.0982679,
          "trades": 20,
          "win_rate": 0.0
        },
        "SUI_USDT": {
          "gross_pnl": -0.008872899999999998,
          "pf": 0.0,
          "severe_pnl": -0.2568728999999999,
          "trades": 62,
          "win_rate": 0.0
        },
        "SUPER_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "SUSHI_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "SXT_USDT": {
          "gross_pnl": 0.024068099999999995,
          "pf": 0.22857970687271884,
          "severe_pnl": -0.3799319,
          "trades": 101,
          "win_rate": 0.18811881188118812
        },
        "SYN_USDT": {
          "gross_pnl": -0.10236560000000001,
          "pf": 0.09825904591093539,
          "severe_pnl": -0.8263656000000003,
          "trades": 181,
          "win_rate": 0.13259668508287292
        },
        "SYRUP_USDT": {
          "gross_pnl": -0.039063200000000006,
          "pf": 0.03978412462038916,
          "severe_pnl": -0.2950632000000001,
          "trades": 64,
          "win_rate": 0.046875
        },
        "S_USDT": {
          "gross_pnl": 0.0051106,
          "pf": 0.0,
          "severe_pnl": -0.0228894,
          "trades": 7,
          "win_rate": 0.0
        },
        "TAC_USDT": {
          "gross_pnl": -0.11227320000000003,
          "pf": 0.14723371997134618,
          "severe_pnl": -0.3842731999999998,
          "trades": 68,
          "win_rate": 0.1323529411764706
        },
        "TAG_USDT": {
          "gross_pnl": 0.015560599999999996,
          "pf": 0.346301085990167,
          "severe_pnl": -0.10043940000000001,
          "trades": 29,
          "win_rate": 0.2413793103448276
        },
        "TAIKO_USDT": {
          "gross_pnl": -0.007016700000000001,
          "pf": 0.0,
          "severe_pnl": -0.0230167,
          "trades": 4,
          "win_rate": 0.0
        },
        "TAO_USDT": {
          "gross_pnl": -0.006400800000000001,
          "pf": 0.0,
          "severe_pnl": -0.0944008,
          "trades": 22,
          "win_rate": 0.0
        },
        "THETA_USDT": {
          "gross_pnl": -0.0053894999999999985,
          "pf": 0.004402218144868075,
          "severe_pnl": -0.16538950000000002,
          "trades": 40,
          "win_rate": 0.05
        },
        "THE_USDT": {
          "gross_pnl": -0.014790099999999994,
          "pf": 0.0,
          "severe_pnl": -0.0707901,
          "trades": 14,
          "win_rate": 0.0
        },
        "TIA_USDT": {
          "gross_pnl": -0.017857799999999997,
          "pf": 0.008951208822422079,
          "severe_pnl": -0.4298578000000002,
          "trades": 103,
          "win_rate": 0.04854368932038835
        },
        "TLM_USDT": {
          "gross_pnl": -0.0032044000000000026,
          "pf": 0.06650375361481915,
          "severe_pnl": -0.2512044,
          "trades": 62,
          "win_rate": 0.06451612903225806
        },
        "TOSHI_USDT": {
          "gross_pnl": -0.0179583,
          "pf": 0.0607329390132472,
          "severe_pnl": -0.049958300000000004,
          "trades": 8,
          "win_rate": 0.375
        },
        "TOWNS_USDT": {
          "gross_pnl": -0.0067607,
          "pf": 0.14649385068611667,
          "severe_pnl": -0.04676070000000001,
          "trades": 10,
          "win_rate": 0.1
        },
        "TQQQ_USDT": {
          "gross_pnl": -0.0021234999999999995,
          "pf": 0.0019969161982012255,
          "severe_pnl": -0.0581235,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "TRADOOR_USDT": {
          "gross_pnl": 0.039408800000000015,
          "pf": 0.43252542201501404,
          "severe_pnl": -0.12459119999999999,
          "trades": 41,
          "win_rate": 0.34146341463414637
        },
        "TRB_USDT": {
          "gross_pnl": -0.0066188,
          "pf": 0.0,
          "severe_pnl": -0.0666188,
          "trades": 15,
          "win_rate": 0.0
        },
        "TRIA_USDT": {
          "gross_pnl": 0.005503299999999994,
          "pf": 0.1540645036118964,
          "severe_pnl": -0.5144967,
          "trades": 130,
          "win_rate": 0.15384615384615385
        },
        "TRUST_USDT": {
          "gross_pnl": -0.00041430000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0044143,
          "trades": 1,
          "win_rate": 0.0
        },
        "TRX_USDT": {
          "gross_pnl": -0.0022528000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0262528,
          "trades": 6,
          "win_rate": 0.0
        },
        "TRY_USDT": {
          "gross_pnl": 0.00046929999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0035307000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "TURBO_USDT": {
          "gross_pnl": -0.004655699999999999,
          "pf": 0.0,
          "severe_pnl": -0.0286557,
          "trades": 6,
          "win_rate": 0.0
        },
        "TUT_USDT": {
          "gross_pnl": -0.0023504,
          "pf": 0.0,
          "severe_pnl": -0.0103504,
          "trades": 2,
          "win_rate": 0.0
        },
        "TWT_USDT": {
          "gross_pnl": -0.0009164000000000004,
          "pf": 0.0,
          "severe_pnl": -0.028916400000000002,
          "trades": 7,
          "win_rate": 0.0
        },
        "T_USDT": {
          "gross_pnl": 0.15398819999999994,
          "pf": 0.3977202273560041,
          "severe_pnl": -0.1900118,
          "trades": 86,
          "win_rate": 0.2441860465116279
        },
        "UAI_USDT": {
          "gross_pnl": -0.0761283,
          "pf": 0.03957356068347066,
          "severe_pnl": -0.2921283000000002,
          "trades": 54,
          "win_rate": 0.09259259259259259
        },
        "UMA_USDT": {
          "gross_pnl": 0.0114356,
          "pf": 0.9192699393523287,
          "severe_pnl": -0.0005644000000000001,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "UNI_USDT": {
          "gross_pnl": -0.02840769999999999,
          "pf": 0.005097578606179504,
          "severe_pnl": -0.4524077000000001,
          "trades": 106,
          "win_rate": 0.018867924528301886
        },
        "USELESS_USDT": {
          "gross_pnl": 0.005970099999999999,
          "pf": 0.002424616258693828,
          "severe_pnl": -0.25002989999999997,
          "trades": 64,
          "win_rate": 0.046875
        },
        "USO_USDT": {
          "gross_pnl": -0.006378,
          "pf": 0.0,
          "severe_pnl": -0.030378000000000002,
          "trades": 6,
          "win_rate": 0.0
        },
        "USUAL_USDT": {
          "gross_pnl": -0.0089454,
          "pf": 0.006060309538953304,
          "severe_pnl": -0.0609454,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "UVXY_USDT": {
          "gross_pnl": 0.035503200000000006,
          "pf": 1.639450336868788,
          "severe_pnl": 0.011503200000000005,
          "trades": 6,
          "win_rate": 0.3333333333333333
        },
        "VANA_USDT": {
          "gross_pnl": -0.0023426999999999996,
          "pf": 0.0022845083139784914,
          "severe_pnl": -0.0183427,
          "trades": 4,
          "win_rate": 0.25
        },
        "VANRY_USDT": {
          "gross_pnl": -0.048993300000000004,
          "pf": 0.14985331756246534,
          "severe_pnl": -0.2289933,
          "trades": 45,
          "win_rate": 0.2
        },
        "VELO_USDT": {
          "gross_pnl": 0.000986,
          "pf": 0.0,
          "severe_pnl": -0.011014000000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "VELVET_USDT": {
          "gross_pnl": 0.04164349999999997,
          "pf": 0.2782602849880931,
          "severe_pnl": -0.5303565000000003,
          "trades": 143,
          "win_rate": 0.25874125874125875
        },
        "VET_USDT": {
          "gross_pnl": 0.006443,
          "pf": 0.0,
          "severe_pnl": -0.06555699999999999,
          "trades": 18,
          "win_rate": 0.0
        },
        "VINE_USDT": {
          "gross_pnl": -0.019158500000000002,
          "pf": 0.0,
          "severe_pnl": -0.047158500000000006,
          "trades": 7,
          "win_rate": 0.0
        },
        "VIRTUAL_USDT": {
          "gross_pnl": -0.006426300000000003,
          "pf": 0.009716572176824935,
          "severe_pnl": -0.5224262999999998,
          "trades": 129,
          "win_rate": 0.023255813953488372
        },
        "VVV_USDT": {
          "gross_pnl": 0.025698300000000004,
          "pf": 0.07976089870814834,
          "severe_pnl": -0.3343016999999999,
          "trades": 90,
          "win_rate": 0.05555555555555555
        },
        "WAL_USDT": {
          "gross_pnl": -0.0016617000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0056617,
          "trades": 1,
          "win_rate": 0.0
        },
        "WET_USDT": {
          "gross_pnl": -0.0038247,
          "pf": 0.0,
          "severe_pnl": -0.0078247,
          "trades": 1,
          "win_rate": 0.0
        },
        "WIF_USDT": {
          "gross_pnl": -0.0014425000000000002,
          "pf": 0.0032467956674549544,
          "severe_pnl": -0.3814425000000002,
          "trades": 95,
          "win_rate": 0.010526315789473684
        },
        "WLD_USDT": {
          "gross_pnl": -0.013511800000000003,
          "pf": 0.007006123706860235,
          "severe_pnl": -0.3135118000000002,
          "trades": 75,
          "win_rate": 0.02666666666666667
        },
        "WLFI_USDT": {
          "gross_pnl": -0.0010243999999999993,
          "pf": 0.0,
          "severe_pnl": -0.1010244,
          "trades": 25,
          "win_rate": 0.0
        },
        "WOO_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "W_USDT": {
          "gross_pnl": 0.0043028,
          "pf": 0.0,
          "severe_pnl": -0.03169720000000001,
          "trades": 9,
          "win_rate": 0.0
        },
        "XAI_USDT": {
          "gross_pnl": 0.0017142999999999998,
          "pf": 0.0,
          "severe_pnl": -0.018285700000000002,
          "trades": 5,
          "win_rate": 0.0
        },
        "XAN_USDT": {
          "gross_pnl": -0.0333179,
          "pf": 0.03364342073523585,
          "severe_pnl": -0.0773179,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "XBI_USDT": {
          "gross_pnl": -0.0037867000000000013,
          "pf": 0.0,
          "severe_pnl": -0.0557867,
          "trades": 13,
          "win_rate": 0.0
        },
        "XDC_USDT": {
          "gross_pnl": -0.0029407000000000005,
          "pf": 0.0,
          "severe_pnl": -0.034940700000000005,
          "trades": 8,
          "win_rate": 0.0
        },
        "XEC_USDT": {
          "gross_pnl": 0.07118719999999988,
          "pf": 0.2745111374940092,
          "severe_pnl": -0.36481279999999994,
          "trades": 109,
          "win_rate": 0.22935779816513763
        },
        "XLM_USDT": {
          "gross_pnl": -0.0016219999999999987,
          "pf": 0.0,
          "severe_pnl": -0.209622,
          "trades": 52,
          "win_rate": 0.0
        },
        "XLU_USDT": {
          "gross_pnl": -0.0014227999999999999,
          "pf": 0.0,
          "severe_pnl": -0.013422800000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "XMR_USDT": {
          "gross_pnl": -0.009010999999999996,
          "pf": 0.004238889327145274,
          "severe_pnl": -0.3610110000000001,
          "trades": 88,
          "win_rate": 0.022727272727272728
        },
        "XPIN_USDT": {
          "gross_pnl": 0.0016621000000000084,
          "pf": 0.3002227226002252,
          "severe_pnl": -0.07433789999999998,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "XPL_USDT": {
          "gross_pnl": 0.024644400000000004,
          "pf": 0.006467602174353498,
          "severe_pnl": -0.28735560000000004,
          "trades": 78,
          "win_rate": 0.02564102564102564
        },
        "XPT_USDT": {
          "gross_pnl": -0.00826,
          "pf": 0.006287576299967872,
          "severe_pnl": -0.10825999999999998,
          "trades": 25,
          "win_rate": 0.04
        },
        "XRP_USDT": {
          "gross_pnl": 0.0057425,
          "pf": 0.009256804961578888,
          "severe_pnl": -0.1502575,
          "trades": 39,
          "win_rate": 0.02564102564102564
        },
        "XTZ_USDT": {
          "gross_pnl": -0.00012049999999999989,
          "pf": 0.0,
          "severe_pnl": -0.0201205,
          "trades": 5,
          "win_rate": 0.0
        },
        "YFI_USDT": {
          "gross_pnl": -0.008152799999999998,
          "pf": 0.0,
          "severe_pnl": -0.0641528,
          "trades": 14,
          "win_rate": 0.0
        },
        "ZAMA_USDT": {
          "gross_pnl": -0.0046388,
          "pf": 0.0,
          "severe_pnl": -0.028638800000000002,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZBT_USDT": {
          "gross_pnl": -0.06552730000000002,
          "pf": 0.053363541495634624,
          "severe_pnl": -0.42952729999999995,
          "trades": 91,
          "win_rate": 0.06593406593406594
        },
        "ZEC_USDT": {
          "gross_pnl": -0.0337152,
          "pf": 0.008937532858576685,
          "severe_pnl": -0.27371520000000005,
          "trades": 60,
          "win_rate": 0.016666666666666666
        },
        "ZEN_USDT": {
          "gross_pnl": -0.005018999999999997,
          "pf": 0.038104832566501115,
          "severe_pnl": -0.10101900000000001,
          "trades": 24,
          "win_rate": 0.08333333333333333
        },
        "ZEST_USDT": {
          "gross_pnl": 0.009555400000000002,
          "pf": 0.23053241454969314,
          "severe_pnl": -0.022444600000000002,
          "trades": 8,
          "win_rate": 0.25
        },
        "ZETA_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZIL_USDT": {
          "gross_pnl": 0.002905799999999999,
          "pf": 0.27750042548363296,
          "severe_pnl": -0.005094200000000001,
          "trades": 2,
          "win_rate": 0.5
        },
        "ZINC_USDT": {
          "gross_pnl": -2.959999999999996e-05,
          "pf": 0.0,
          "severe_pnl": -0.024029599999999998,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZKP_USDT": {
          "gross_pnl": 0.0033761999999999998,
          "pf": 0.0,
          "severe_pnl": -0.024623799999999998,
          "trades": 7,
          "win_rate": 0.0
        },
        "ZKSYNC_USDT": {
          "gross_pnl": -0.0065009,
          "pf": 0.0,
          "severe_pnl": -0.058500900000000015,
          "trades": 13,
          "win_rate": 0.0
        },
        "ZORA_USDT": {
          "gross_pnl": 0.0046602,
          "pf": 0.01952241975320949,
          "severe_pnl": -0.0393398,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "ZRO_USDT": {
          "gross_pnl": -0.0012819,
          "pf": 0.00012968659708090905,
          "severe_pnl": -0.1572819,
          "trades": 39,
          "win_rate": 0.02564102564102564
        }
      },
      "validation_depth_quartiles": [
        {
          "gross_pnl": -0.4083084999999999,
          "pf": 0.22434186845166354,
          "quartile": 1,
          "severe_pnl": -11.560308499999975,
          "trades": 2788,
          "upper": 8976.76524,
          "win_rate": 0.1441893830703013
        },
        {
          "gross_pnl": -1.0464373999999985,
          "pf": 0.089931408761293,
          "quartile": 2,
          "severe_pnl": -13.826437399999957,
          "trades": 3195,
          "upper": 106972.33601999999,
          "win_rate": 0.07793427230046948
        },
        {
          "gross_pnl": -0.45913929999999953,
          "pf": 0.07081519187342726,
          "quartile": 3,
          "severe_pnl": -13.85913929999992,
          "trades": 3350,
          "upper": 1071304.435,
          "win_rate": 0.05880597014925373
        },
        {
          "gross_pnl": -0.6394072000000008,
          "pf": 0.024568558585919484,
          "quartile": 4,
          "severe_pnl": -12.663407199999916,
          "trades": 3006,
          "upper": null,
          "win_rate": 0.029607451763140388
        }
      ],
      "validation_pass": false,
      "validation_skips": {
        "invalid_path_json": 0,
        "missing_horizon_path": 19,
        "structure_not_selected": 74982,
        "symbol_cooldown": 3960
      },
      "validation_spread_quartiles": [
        {
          "gross_pnl": -0.3253715000000001,
          "pf": 0.04728181721360382,
          "quartile": 1,
          "severe_pnl": -12.245371499999996,
          "trades": 2980,
          "upper": 2.148689299527946,
          "win_rate": 0.046308724832214765
        },
        {
          "gross_pnl": -0.31225510000000023,
          "pf": 0.08225398403575554,
          "quartile": 2,
          "severe_pnl": -12.916255099999965,
          "trades": 3151,
          "upper": 4.268032437045758,
          "win_rate": 0.06918438590923516
        },
        {
          "gross_pnl": -1.1884600000000005,
          "pf": 0.075249244282897,
          "quartile": 3,
          "severe_pnl": -14.188459999999903,
          "trades": 3250,
          "upper": 7.482229704451622,
          "win_rate": 0.06923076923076923
        },
        {
          "gross_pnl": -0.7272057999999995,
          "pf": 0.20129011758955012,
          "quartile": 4,
          "severe_pnl": -12.559205799999901,
          "trades": 2958,
          "upper": null,
          "win_rate": 0.12035158891142664
        }
      ]
    },
    {
      "direction": "continuation",
      "horizon_seconds": 300,
      "leave_best_symbol": -53.00643949999964,
      "structure": "contradict",
      "validation": {
        "gross_pnl": -3.410750899999978,
        "pf": 0.2502053231815633,
        "severe_pnl": -52.70675089999963,
        "trades": 12324,
        "win_rate": 0.15546900357026938
      },
      "validation_by_symbol": {
        "0G_USDT": {
          "gross_pnl": -0.008360499999999998,
          "pf": 0.1789420717672009,
          "severe_pnl": -0.0843605,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "1000000BABYDOGE_USDT": {
          "gross_pnl": -0.012833500000000001,
          "pf": 0.0,
          "severe_pnl": -0.028833500000000005,
          "trades": 4,
          "win_rate": 0.0
        },
        "1000BONK_USDT": {
          "gross_pnl": -0.029705,
          "pf": 0.030947508550306965,
          "severe_pnl": -0.273705,
          "trades": 61,
          "win_rate": 0.09836065573770492
        },
        "1000BTT_USDT": {
          "gross_pnl": -0.0025840000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0065840000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "2Z_USDT": {
          "gross_pnl": -0.00042320000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0044232,
          "trades": 1,
          "win_rate": 0.0
        },
        "4_USDT": {
          "gross_pnl": -0.0054284,
          "pf": 0.0,
          "severe_pnl": -0.033428400000000004,
          "trades": 7,
          "win_rate": 0.0
        },
        "AAVE_USDT": {
          "gross_pnl": -0.030472799999999994,
          "pf": 0.022463111467142378,
          "severe_pnl": -0.2064728,
          "trades": 44,
          "win_rate": 0.045454545454545456
        },
        "ACE_USDT": {
          "gross_pnl": -0.1160565,
          "pf": 0.0,
          "severe_pnl": -0.1240565,
          "trades": 2,
          "win_rate": 0.0
        },
        "ACH_USDT": {
          "gross_pnl": 0.0030055999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0049943999999999995,
          "trades": 2,
          "win_rate": 0.0
        },
        "ACU_USDT": {
          "gross_pnl": -0.001594,
          "pf": 0.0,
          "severe_pnl": -0.005594,
          "trades": 1,
          "win_rate": 0.0
        },
        "ACX_USDT": {
          "gross_pnl": 0.000949,
          "pf": 0.0,
          "severe_pnl": -0.003051,
          "trades": 1,
          "win_rate": 0.0
        },
        "ADA_USDT": {
          "gross_pnl": -0.044018599999999984,
          "pf": 0.03867442646068601,
          "severe_pnl": -0.4240185999999999,
          "trades": 95,
          "win_rate": 0.05263157894736842
        },
        "AERGO_USDT": {
          "gross_pnl": -0.026947799999999994,
          "pf": 0.39328496565689736,
          "severe_pnl": -0.07094779999999999,
          "trades": 11,
          "win_rate": 0.2727272727272727
        },
        "AERO_USDT": {
          "gross_pnl": -0.010624900000000012,
          "pf": 0.02661607573520853,
          "severe_pnl": -0.22662490000000005,
          "trades": 54,
          "win_rate": 0.07407407407407407
        },
        "AGI_USDT": {
          "gross_pnl": -0.0012563999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0092564,
          "trades": 2,
          "win_rate": 0.0
        },
        "AGLD_USDT": {
          "gross_pnl": -0.0333059,
          "pf": 0.02160731154070624,
          "severe_pnl": -0.08130589999999999,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "AIGENSYN_USDT": {
          "gross_pnl": -0.0062844999999999976,
          "pf": 0.12431344628944392,
          "severe_pnl": -0.0822845,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "AIOT_USDT": {
          "gross_pnl": 0.10084699999999996,
          "pf": 0.73511531787174,
          "severe_pnl": -0.11515300000000003,
          "trades": 54,
          "win_rate": 0.2962962962962963
        },
        "AIOZ_USDT": {
          "gross_pnl": -0.0033461000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0113461,
          "trades": 2,
          "win_rate": 0.0
        },
        "AIO_USDT": {
          "gross_pnl": -0.0443824,
          "pf": 0.0,
          "severe_pnl": -0.05238240000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "AKE_USDT": {
          "gross_pnl": -0.3604033,
          "pf": 0.4890381556332845,
          "severe_pnl": -0.5964033000000002,
          "trades": 59,
          "win_rate": 0.3050847457627119
        },
        "AKT_USDT": {
          "gross_pnl": 0.004386,
          "pf": 999,
          "severe_pnl": 0.00038600000000000006,
          "trades": 1,
          "win_rate": 1.0
        },
        "ALCH_USDT": {
          "gross_pnl": 0.0656627,
          "pf": 0.5036614620596775,
          "severe_pnl": -0.18633730000000004,
          "trades": 63,
          "win_rate": 0.31746031746031744
        },
        "ALGO_USDT": {
          "gross_pnl": -0.0036835999999999982,
          "pf": 0.0,
          "severe_pnl": -0.13568360000000002,
          "trades": 33,
          "win_rate": 0.0
        },
        "ALLO_USDT": {
          "gross_pnl": -0.15669229999999995,
          "pf": 0.2307188491126127,
          "severe_pnl": -0.9406923,
          "trades": 196,
          "win_rate": 0.1989795918367347
        },
        "ALT_USDT": {
          "gross_pnl": -0.0492248,
          "pf": 0.0,
          "severe_pnl": -0.0852248,
          "trades": 9,
          "win_rate": 0.0
        },
        "ANKR_USDT": {
          "gross_pnl": 0.05157609999999999,
          "pf": 1.7787790812609081,
          "severe_pnl": 0.027576099999999992,
          "trades": 6,
          "win_rate": 0.6666666666666666
        },
        "ANSEM_USDT": {
          "gross_pnl": -0.15277930000000006,
          "pf": 0.48403843145529485,
          "severe_pnl": -0.8367793000000001,
          "trades": 171,
          "win_rate": 0.3333333333333333
        },
        "ANTHROPIC_USDT": {
          "gross_pnl": -0.008325800000000001,
          "pf": 0.0,
          "severe_pnl": -0.08032579999999999,
          "trades": 18,
          "win_rate": 0.0
        },
        "APE_USDT": {
          "gross_pnl": -0.036417700000000004,
          "pf": 0.021329912203988322,
          "severe_pnl": -0.3084177,
          "trades": 68,
          "win_rate": 0.07352941176470588
        },
        "APT_USDT": {
          "gross_pnl": 0.013778599999999981,
          "pf": 0.023815395047085592,
          "severe_pnl": -0.3622214,
          "trades": 94,
          "win_rate": 0.02127659574468085
        },
        "ARB_USDT": {
          "gross_pnl": -0.10719320000000003,
          "pf": 0.07784085888227948,
          "severe_pnl": -0.8671932000000002,
          "trades": 190,
          "win_rate": 0.07894736842105263
        },
        "ARKK_USDT": {
          "gross_pnl": -0.0385778,
          "pf": 0.0,
          "severe_pnl": -0.054577799999999996,
          "trades": 4,
          "win_rate": 0.0
        },
        "ARKM_USDT": {
          "gross_pnl": -0.0053904,
          "pf": 0.0,
          "severe_pnl": -0.0413904,
          "trades": 9,
          "win_rate": 0.0
        },
        "ARX_USDT": {
          "gross_pnl": -0.003317200000000004,
          "pf": 0.1012329898835596,
          "severe_pnl": -0.11531720000000001,
          "trades": 28,
          "win_rate": 0.14285714285714285
        },
        "AR_USDT": {
          "gross_pnl": -0.013082399999999998,
          "pf": 0.0,
          "severe_pnl": -0.07708240000000002,
          "trades": 16,
          "win_rate": 0.0
        },
        "ASP_USDT": {
          "gross_pnl": -0.0194175,
          "pf": 0.0,
          "severe_pnl": -0.0234175,
          "trades": 1,
          "win_rate": 0.0
        },
        "ASTER_USDT": {
          "gross_pnl": -0.010115699999999998,
          "pf": 0.0,
          "severe_pnl": -0.1461157,
          "trades": 34,
          "win_rate": 0.0
        },
        "ATH_USDT": {
          "gross_pnl": -0.020175300000000004,
          "pf": 0.0,
          "severe_pnl": -0.0481753,
          "trades": 7,
          "win_rate": 0.0
        },
        "ATOM_USDT": {
          "gross_pnl": -0.030131999999999996,
          "pf": 0.0,
          "severe_pnl": -0.21413200000000007,
          "trades": 46,
          "win_rate": 0.0
        },
        "AT_USDT": {
          "gross_pnl": -0.0092408,
          "pf": 0.0,
          "severe_pnl": -0.025240800000000004,
          "trades": 4,
          "win_rate": 0.0
        },
        "AVAAI_USDT": {
          "gross_pnl": 0.06589119999999998,
          "pf": 4.044941407794966,
          "severe_pnl": 0.05389119999999999,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "AVAX_USDT": {
          "gross_pnl": 0.009532000000000002,
          "pf": 0.010855946052903189,
          "severe_pnl": -0.15046799999999996,
          "trades": 40,
          "win_rate": 0.075
        },
        "AVNT_USDT": {
          "gross_pnl": 0.0016736000000000001,
          "pf": 0.0656425917598048,
          "severe_pnl": -0.11032640000000002,
          "trades": 28,
          "win_rate": 0.07142857142857142
        },
        "AWE_USDT": {
          "gross_pnl": -0.0144246,
          "pf": 0.0,
          "severe_pnl": -0.0224246,
          "trades": 2,
          "win_rate": 0.0
        },
        "AXS_USDT": {
          "gross_pnl": -0.002066,
          "pf": 0.0,
          "severe_pnl": -0.03806600000000001,
          "trades": 9,
          "win_rate": 0.0
        },
        "A_USDT": {
          "gross_pnl": 0.0016041000000000002,
          "pf": 0.18440500847298064,
          "severe_pnl": -0.0103959,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "B2_USDT": {
          "gross_pnl": -0.0028130000000000004,
          "pf": 0.0,
          "severe_pnl": -0.010813,
          "trades": 2,
          "win_rate": 0.0
        },
        "B3_USDT": {
          "gross_pnl": -0.14567739999999998,
          "pf": 0.0324904057789,
          "severe_pnl": -0.1976774,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "BANANAS31_USDT": {
          "gross_pnl": -0.013309699999999999,
          "pf": 0.0,
          "severe_pnl": -0.0213097,
          "trades": 2,
          "win_rate": 0.0
        },
        "BAND_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "BANK_USDT": {
          "gross_pnl": 0.13319159999999997,
          "pf": 0.6808373423727534,
          "severe_pnl": -0.20280840000000014,
          "trades": 84,
          "win_rate": 0.36904761904761907
        },
        "BAN_USDT": {
          "gross_pnl": -0.0022971,
          "pf": 0.0,
          "severe_pnl": -0.0062971,
          "trades": 1,
          "win_rate": 0.0
        },
        "BASED_USDT": {
          "gross_pnl": -0.025985200000000003,
          "pf": 0.1915294107500545,
          "severe_pnl": -0.14998519999999999,
          "trades": 31,
          "win_rate": 0.16129032258064516
        },
        "BAS_USDT": {
          "gross_pnl": -0.0056609,
          "pf": 0.16901499671309356,
          "severe_pnl": -0.0256609,
          "trades": 5,
          "win_rate": 0.2
        },
        "BAT_USDT": {
          "gross_pnl": -0.002543,
          "pf": 0.0,
          "severe_pnl": -0.014543,
          "trades": 3,
          "win_rate": 0.0
        },
        "BCH_USDT": {
          "gross_pnl": 0.020971700000000006,
          "pf": 0.04551525871089991,
          "severe_pnl": -0.22702830000000002,
          "trades": 62,
          "win_rate": 0.08064516129032258
        },
        "BEAT_USDT": {
          "gross_pnl": -0.03233390000000001,
          "pf": 0.23872634684745778,
          "severe_pnl": -0.6723339,
          "trades": 160,
          "win_rate": 0.2375
        },
        "BERA_USDT": {
          "gross_pnl": -0.0062844,
          "pf": 0.0,
          "severe_pnl": -0.0382844,
          "trades": 8,
          "win_rate": 0.0
        },
        "BIANRENSHENG_USDT": {
          "gross_pnl": -0.012962000000000001,
          "pf": 0.003983091187970176,
          "severe_pnl": -0.048962,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "BICO_USDT": {
          "gross_pnl": -0.017403499999999995,
          "pf": 0.12036913390986029,
          "severe_pnl": -0.049403499999999996,
          "trades": 8,
          "win_rate": 0.125
        },
        "BIGTIME_USDT": {
          "gross_pnl": -0.0016168999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0096169,
          "trades": 2,
          "win_rate": 0.0
        },
        "BILL_USDT": {
          "gross_pnl": 0.13063520000000006,
          "pf": 0.4844155596736847,
          "severe_pnl": -0.4573648000000002,
          "trades": 147,
          "win_rate": 0.2857142857142857
        },
        "BLAST_USDT": {
          "gross_pnl": 0.25234619999999996,
          "pf": 1.771179651772407,
          "severe_pnl": 0.14834619999999996,
          "trades": 26,
          "win_rate": 0.5384615384615384
        },
        "BLESS_USDT": {
          "gross_pnl": -0.0482996,
          "pf": 0.09203756605745875,
          "severe_pnl": -0.20029960000000002,
          "trades": 38,
          "win_rate": 0.10526315789473684
        },
        "BLUAI_USDT": {
          "gross_pnl": -0.057224699999999996,
          "pf": 0.20476623124866608,
          "severe_pnl": -0.0812247,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "BLUR_USDT": {
          "gross_pnl": -0.0958665,
          "pf": 0.0,
          "severe_pnl": -0.1398665,
          "trades": 11,
          "win_rate": 0.0
        },
        "BNB_USDT": {
          "gross_pnl": -0.0009191,
          "pf": 0.0,
          "severe_pnl": -0.060919100000000004,
          "trades": 15,
          "win_rate": 0.0
        },
        "BOBA_USDT": {
          "gross_pnl": -0.00044800000000000005,
          "pf": 0.0,
          "severe_pnl": -0.008448,
          "trades": 2,
          "win_rate": 0.0
        },
        "BRETT_USDT": {
          "gross_pnl": -0.034249100000000005,
          "pf": 0.0,
          "severe_pnl": -0.12624910000000003,
          "trades": 23,
          "win_rate": 0.0
        },
        "BREV_USDT": {
          "gross_pnl": 0.00040299999999999993,
          "pf": 0.0,
          "severe_pnl": -0.015597,
          "trades": 4,
          "win_rate": 0.0
        },
        "BR_USDT": {
          "gross_pnl": -0.0018193,
          "pf": 0.0,
          "severe_pnl": -0.0058193,
          "trades": 1,
          "win_rate": 0.0
        },
        "BSB_USDT": {
          "gross_pnl": 0.013371500000000012,
          "pf": 0.31390876920165867,
          "severe_pnl": -0.7306285000000001,
          "trades": 186,
          "win_rate": 0.23655913978494625
        },
        "BSV_USDT": {
          "gross_pnl": -0.004396200000000003,
          "pf": 0.12728223434870808,
          "severe_pnl": -0.0443962,
          "trades": 10,
          "win_rate": 0.3
        },
        "BTW_USDT": {
          "gross_pnl": 0.061691300000000025,
          "pf": 0.6549879124201406,
          "severe_pnl": -0.062308699999999974,
          "trades": 31,
          "win_rate": 0.3548387096774194
        },
        "BUILDONBOB_USDT": {
          "gross_pnl": 0.007497500000000001,
          "pf": 0.6332426055411532,
          "severe_pnl": -0.0085025,
          "trades": 4,
          "win_rate": 0.25
        },
        "BULLA_USDT": {
          "gross_pnl": 0.039161299999999996,
          "pf": 0.9840255225941621,
          "severe_pnl": -0.0008386999999999995,
          "trades": 10,
          "win_rate": 0.2
        },
        "CAKE_USDT": {
          "gross_pnl": 0.0021558999999999997,
          "pf": 0.013557539981894975,
          "severe_pnl": -0.0418441,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "CAP_USDT": {
          "gross_pnl": -0.0493084,
          "pf": 0.19000748670211315,
          "severe_pnl": -0.2973084000000001,
          "trades": 62,
          "win_rate": 0.1774193548387097
        },
        "CASHCAT_USDT": {
          "gross_pnl": 0.12467470000000003,
          "pf": 1.088498836763828,
          "severe_pnl": 0.020674699999999983,
          "trades": 26,
          "win_rate": 0.46153846153846156
        },
        "CC_USDT": {
          "gross_pnl": 0.019434299999999998,
          "pf": 0.34184812535567904,
          "severe_pnl": -0.028565700000000003,
          "trades": 12,
          "win_rate": 0.3333333333333333
        },
        "CFX_USDT": {
          "gross_pnl": -0.0064627999999999994,
          "pf": 0.012766667089624064,
          "severe_pnl": -0.0544628,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "CHIP_USDT": {
          "gross_pnl": -0.028819400000000002,
          "pf": 0.017323929308720523,
          "severe_pnl": -0.22081940000000005,
          "trades": 48,
          "win_rate": 0.041666666666666664
        },
        "CHR_USDT": {
          "gross_pnl": -0.0018214,
          "pf": 0.0,
          "severe_pnl": -0.009821400000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "CHZ_USDT": {
          "gross_pnl": -0.0098949,
          "pf": 0.021333561159349635,
          "severe_pnl": -0.0778949,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "CLO_USDT": {
          "gross_pnl": -0.0691099,
          "pf": 0.0,
          "severe_pnl": -0.0811099,
          "trades": 3,
          "win_rate": 0.0
        },
        "COAI_USDT": {
          "gross_pnl": 0.014966800000000002,
          "pf": 0.22026397389960636,
          "severe_pnl": -0.0530332,
          "trades": 17,
          "win_rate": 0.17647058823529413
        },
        "COLLECT_USDT": {
          "gross_pnl": -0.0048618,
          "pf": 0.3254153837714035,
          "severe_pnl": -0.06886179999999999,
          "trades": 16,
          "win_rate": 0.375
        },
        "COMP_USDT": {
          "gross_pnl": 0.004694,
          "pf": 0.05596098929543596,
          "severe_pnl": -0.011306,
          "trades": 4,
          "win_rate": 0.25
        },
        "COOKIE_USDT": {
          "gross_pnl": -0.0011351,
          "pf": 0.0,
          "severe_pnl": -0.0051351,
          "trades": 1,
          "win_rate": 0.0
        },
        "CORE_USDT": {
          "gross_pnl": -0.0078783,
          "pf": 0.0,
          "severe_pnl": -0.0238783,
          "trades": 4,
          "win_rate": 0.0
        },
        "COW_USDT": {
          "gross_pnl": 0.0040295999999999995,
          "pf": 999,
          "severe_pnl": 2.959999999999942e-05,
          "trades": 1,
          "win_rate": 1.0
        },
        "CROSS_USDT": {
          "gross_pnl": -0.0109139,
          "pf": 0.0,
          "severe_pnl": -0.0229139,
          "trades": 3,
          "win_rate": 0.0
        },
        "CRO_USDT": {
          "gross_pnl": 0.06599989999999999,
          "pf": 0.38555244235805597,
          "severe_pnl": -0.09000009999999999,
          "trades": 39,
          "win_rate": 0.20512820512820512
        },
        "CRV_USDT": {
          "gross_pnl": -0.005080100000000005,
          "pf": 0.019170414161833436,
          "severe_pnl": -0.28908009999999995,
          "trades": 71,
          "win_rate": 0.08450704225352113
        },
        "CTC_USDT": {
          "gross_pnl": -0.0259687,
          "pf": 0.0,
          "severe_pnl": -0.1219687,
          "trades": 24,
          "win_rate": 0.0
        },
        "CTR_USDT": {
          "gross_pnl": 0.002442,
          "pf": 0.0,
          "severe_pnl": -0.001558,
          "trades": 1,
          "win_rate": 0.0
        },
        "CVX_USDT": {
          "gross_pnl": -0.002459899999999998,
          "pf": 0.19968275202170105,
          "severe_pnl": -0.0344599,
          "trades": 8,
          "win_rate": 0.25
        },
        "CYS_USDT": {
          "gross_pnl": -0.019901099999999998,
          "pf": 0.10227013589339225,
          "severe_pnl": -0.0559011,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "C_USDT": {
          "gross_pnl": -0.008033400000000001,
          "pf": 0.0,
          "severe_pnl": -0.012033400000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "DASH_USDT": {
          "gross_pnl": -0.017119400000000003,
          "pf": 0.00559249636707913,
          "severe_pnl": -0.3771194,
          "trades": 90,
          "win_rate": 0.044444444444444446
        },
        "DEEP_USDT": {
          "gross_pnl": 0.0031478,
          "pf": 0.0,
          "severe_pnl": -0.0168522,
          "trades": 5,
          "win_rate": 0.0
        },
        "DEXE_USDT": {
          "gross_pnl": 0.03539789999999998,
          "pf": 0.39892962636761636,
          "severe_pnl": -0.47260209999999997,
          "trades": 127,
          "win_rate": 0.2755905511811024
        },
        "DODO_USDT": {
          "gross_pnl": 0.018270599999999967,
          "pf": 0.6253178146926968,
          "severe_pnl": -0.43372940000000004,
          "trades": 113,
          "win_rate": 0.2743362831858407
        },
        "DOGE_USDT": {
          "gross_pnl": -0.019358500000000004,
          "pf": 0.00037449585331511423,
          "severe_pnl": -0.1633585,
          "trades": 36,
          "win_rate": 0.027777777777777776
        },
        "DOGS_USDT": {
          "gross_pnl": -0.011275400000000001,
          "pf": 0.0,
          "severe_pnl": -0.0392754,
          "trades": 7,
          "win_rate": 0.0
        },
        "DOT_USDT": {
          "gross_pnl": -0.0615284,
          "pf": 0.0,
          "severe_pnl": -0.38552840000000016,
          "trades": 81,
          "win_rate": 0.0
        },
        "DRAM_USDT": {
          "gross_pnl": 0.0755561,
          "pf": 0.32439680062028786,
          "severe_pnl": -0.1324439,
          "trades": 52,
          "win_rate": 0.34615384615384615
        },
        "DYDX_USDT": {
          "gross_pnl": 0.009406799999999998,
          "pf": 0.0,
          "severe_pnl": -0.054593200000000015,
          "trades": 16,
          "win_rate": 0.0
        },
        "EDEN_USDT": {
          "gross_pnl": -0.0036303000000000004,
          "pf": 0.041907403127648096,
          "severe_pnl": -0.023630300000000003,
          "trades": 5,
          "win_rate": 0.2
        },
        "EDGE_USDT": {
          "gross_pnl": 0.02004540000000003,
          "pf": 0.2905872697902896,
          "severe_pnl": -0.29995460000000007,
          "trades": 80,
          "win_rate": 0.2375
        },
        "EDU_USDT": {
          "gross_pnl": 0.001764299999999999,
          "pf": 0.27166511079447747,
          "severe_pnl": -0.022235699999999997,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "EGLD_USDT": {
          "gross_pnl": 0.038971199999999984,
          "pf": 0.13843770928723997,
          "severe_pnl": -0.47302879999999997,
          "trades": 128,
          "win_rate": 0.171875
        },
        "EIGEN_USDT": {
          "gross_pnl": 0.03859060000000003,
          "pf": 0.1108523557365438,
          "severe_pnl": -0.8014093999999997,
          "trades": 210,
          "win_rate": 0.12857142857142856
        },
        "ELSA_USDT": {
          "gross_pnl": -0.14731509999999998,
          "pf": 0.030937183066528377,
          "severe_pnl": -0.2273151,
          "trades": 20,
          "win_rate": 0.1
        },
        "ENA_USDT": {
          "gross_pnl": 0.0013168000000000014,
          "pf": 0.02384330461222341,
          "severe_pnl": -0.2346832000000001,
          "trades": 59,
          "win_rate": 0.0847457627118644
        },
        "ENJ_USDT": {
          "gross_pnl": -0.0038188,
          "pf": 0.004045797271921778,
          "severe_pnl": -0.051818800000000005,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "ENSO_USDT": {
          "gross_pnl": -0.0004077,
          "pf": 0.0,
          "severe_pnl": -0.012407699999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "ENS_USDT": {
          "gross_pnl": -0.02818649999999999,
          "pf": 0.04575745115916376,
          "severe_pnl": -0.22418650000000007,
          "trades": 49,
          "win_rate": 0.10204081632653061
        },
        "EPIC_USDT": {
          "gross_pnl": 0.0038149,
          "pf": 0.0,
          "severe_pnl": -0.0001851000000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "ERA_USDT": {
          "gross_pnl": -0.0025302999999999997,
          "pf": 0.0,
          "severe_pnl": -0.006530299999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "ESPORTS_USDT": {
          "gross_pnl": 0.08377590000000013,
          "pf": 0.7396366585636709,
          "severe_pnl": -0.31222410000000006,
          "trades": 99,
          "win_rate": 0.35353535353535354
        },
        "ESP_USDT": {
          "gross_pnl": -0.0068005999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0188006,
          "trades": 3,
          "win_rate": 0.0
        },
        "ETC_USDT": {
          "gross_pnl": -0.008722699999999998,
          "pf": 0.0,
          "severe_pnl": -0.08472270000000001,
          "trades": 19,
          "win_rate": 0.0
        },
        "ETHFI_USDT": {
          "gross_pnl": -0.05824619999999997,
          "pf": 0.0397055463771397,
          "severe_pnl": -0.6502462,
          "trades": 148,
          "win_rate": 0.10810810810810811
        },
        "ETH_USDT": {
          "gross_pnl": 0.015305000000000003,
          "pf": 0.07238472433998476,
          "severe_pnl": -0.3286950000000001,
          "trades": 86,
          "win_rate": 0.10465116279069768
        },
        "EUL_USDT": {
          "gross_pnl": -0.0010256,
          "pf": 0.0,
          "severe_pnl": -0.0050256,
          "trades": 1,
          "win_rate": 0.0
        },
        "EVAA_USDT": {
          "gross_pnl": -0.10169550000000005,
          "pf": 0.5668087231519573,
          "severe_pnl": -0.2976955000000001,
          "trades": 49,
          "win_rate": 0.30612244897959184
        },
        "EWJ_USDT": {
          "gross_pnl": 0.0003227,
          "pf": 0.0,
          "severe_pnl": -0.0036773,
          "trades": 1,
          "win_rate": 0.0
        },
        "EWY_USDT": {
          "gross_pnl": -0.0003126999999999966,
          "pf": 0.022136051841728403,
          "severe_pnl": -0.22431270000000003,
          "trades": 56,
          "win_rate": 0.07142857142857142
        },
        "FET_USDT": {
          "gross_pnl": -0.002735899999999998,
          "pf": 0.009966093673724434,
          "severe_pnl": -0.29873589999999994,
          "trades": 74,
          "win_rate": 0.04054054054054054
        },
        "FF_USDT": {
          "gross_pnl": 0.004535200000000003,
          "pf": 0.2912062312590345,
          "severe_pnl": -0.0474648,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "FHE_USDT": {
          "gross_pnl": 0.0022645999999999964,
          "pf": 0.24578226651195148,
          "severe_pnl": -0.18173540000000002,
          "trades": 46,
          "win_rate": 0.1956521739130435
        },
        "FILECOIN_USDT": {
          "gross_pnl": 0.007431400000000001,
          "pf": 0.033968786666834894,
          "severe_pnl": -0.0765686,
          "trades": 21,
          "win_rate": 0.09523809523809523
        },
        "FLOCK_USDT": {
          "gross_pnl": -0.0560827,
          "pf": 0.0,
          "severe_pnl": -0.0920827,
          "trades": 9,
          "win_rate": 0.0
        },
        "FLOKI_USDT": {
          "gross_pnl": -0.024943100000000006,
          "pf": 0.0,
          "severe_pnl": -0.12094310000000001,
          "trades": 24,
          "win_rate": 0.0
        },
        "FLOW_USDT": {
          "gross_pnl": 0.0038233,
          "pf": 0.0,
          "severe_pnl": -0.0081767,
          "trades": 3,
          "win_rate": 0.0
        },
        "FLUID_USDT": {
          "gross_pnl": 0.0037348,
          "pf": 0.0,
          "severe_pnl": -0.00026520000000000016,
          "trades": 1,
          "win_rate": 0.0
        },
        "FOGO_USDT": {
          "gross_pnl": -0.0048421,
          "pf": 0.0863551960386741,
          "severe_pnl": -0.0128421,
          "trades": 2,
          "win_rate": 0.5
        },
        "FOLKS_USDT": {
          "gross_pnl": -0.013668000000000003,
          "pf": 0.09252799207422471,
          "severe_pnl": -0.17366799999999993,
          "trades": 40,
          "win_rate": 0.175
        },
        "FORM_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "FRAX_USDT": {
          "gross_pnl": -0.0040048,
          "pf": 0.0,
          "severe_pnl": -0.0120048,
          "trades": 2,
          "win_rate": 0.0
        },
        "GALA_USDT": {
          "gross_pnl": -0.0249074,
          "pf": 0.05749118413355222,
          "severe_pnl": -0.43290740000000016,
          "trades": 102,
          "win_rate": 0.0784313725490196
        },
        "GAS_USDT": {
          "gross_pnl": -0.0058252,
          "pf": 0.0,
          "severe_pnl": -0.0098252,
          "trades": 1,
          "win_rate": 0.0
        },
        "GENIUS_USDT": {
          "gross_pnl": 0.0150682,
          "pf": 0.9083919933933697,
          "severe_pnl": -0.0009318000000000009,
          "trades": 4,
          "win_rate": 0.5
        },
        "GIGGLE_USDT": {
          "gross_pnl": -0.0041245,
          "pf": 0.0,
          "severe_pnl": -0.0081245,
          "trades": 1,
          "win_rate": 0.0
        },
        "GLM_USDT": {
          "gross_pnl": -0.0019684999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0139685,
          "trades": 3,
          "win_rate": 0.0
        },
        "GMT_USDT": {
          "gross_pnl": -0.0013494999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0093495,
          "trades": 2,
          "win_rate": 0.0
        },
        "GPS_USDT": {
          "gross_pnl": -0.015872,
          "pf": 0.06927887319998412,
          "severe_pnl": -0.039872,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "GRAM_USDT": {
          "gross_pnl": 0.018758199999999996,
          "pf": 0.0787548610452433,
          "severe_pnl": -0.09324179999999999,
          "trades": 28,
          "win_rate": 0.17857142857142858
        },
        "GRASS_USDT": {
          "gross_pnl": 0.0040208,
          "pf": 0.059546893740018696,
          "severe_pnl": -0.08797919999999998,
          "trades": 23,
          "win_rate": 0.17391304347826086
        },
        "GRIFFAIN_USDT": {
          "gross_pnl": 0.0012422,
          "pf": 0.0,
          "severe_pnl": -0.0027578000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "GRT_USDT": {
          "gross_pnl": 0.007365,
          "pf": 0.015617426338894354,
          "severe_pnl": -0.028635,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "GUA_USDT": {
          "gross_pnl": 0.028931900000000007,
          "pf": 1.6373918876487885,
          "severe_pnl": 0.008931900000000003,
          "trades": 5,
          "win_rate": 0.6
        },
        "GUN_USDT": {
          "gross_pnl": -0.04242699999999999,
          "pf": 0.021117767805995794,
          "severe_pnl": -0.09842700000000003,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "G_USDT": {
          "gross_pnl": -0.047589099999999995,
          "pf": 0.4645245661989717,
          "severe_pnl": -0.06358910000000001,
          "trades": 4,
          "win_rate": 0.25
        },
        "HBAR_USDT": {
          "gross_pnl": 0.008859999999999998,
          "pf": 0.0022914113252883624,
          "severe_pnl": -0.24714000000000005,
          "trades": 64,
          "win_rate": 0.03125
        },
        "HEI_USDT": {
          "gross_pnl": -0.021795,
          "pf": 0.22765298193250952,
          "severe_pnl": -0.21379500000000004,
          "trades": 48,
          "win_rate": 0.16666666666666666
        },
        "HIGH_USDT": {
          "gross_pnl": -0.012263400000000006,
          "pf": 0.2393745812520315,
          "severe_pnl": -0.0802634,
          "trades": 17,
          "win_rate": 0.23529411764705882
        },
        "HK50_USDT": {
          "gross_pnl": -0.004957499999999999,
          "pf": 0.015954333368638756,
          "severe_pnl": -0.0529575,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "HMSTR_USDT": {
          "gross_pnl": -0.027722000000000004,
          "pf": 0.0,
          "severe_pnl": -0.059722,
          "trades": 8,
          "win_rate": 0.0
        },
        "HNT_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.008,
          "trades": 2,
          "win_rate": 0.0
        },
        "HOLO_USDT": {
          "gross_pnl": 0.0011301,
          "pf": 0.0,
          "severe_pnl": -0.0028699,
          "trades": 1,
          "win_rate": 0.0
        },
        "HOME_USDT": {
          "gross_pnl": 0.03914440000000001,
          "pf": 0.5615196625127284,
          "severe_pnl": -0.1808556,
          "trades": 55,
          "win_rate": 0.38181818181818183
        },
        "HOT_USDT": {
          "gross_pnl": -0.0239389,
          "pf": 0.23535107027785754,
          "severe_pnl": -0.0479389,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "HYPE_USDT": {
          "gross_pnl": 0.011224699999999994,
          "pf": 0.03773689167606392,
          "severe_pnl": -0.19677530000000001,
          "trades": 52,
          "win_rate": 0.11538461538461539
        },
        "ICP_USDT": {
          "gross_pnl": 0.023919399999999997,
          "pf": 0.05222307072249798,
          "severe_pnl": -0.2680806,
          "trades": 73,
          "win_rate": 0.0821917808219178
        },
        "ICX_USDT": {
          "gross_pnl": -0.0021133,
          "pf": 0.0,
          "severe_pnl": -0.0061133,
          "trades": 1,
          "win_rate": 0.0
        },
        "ID_USDT": {
          "gross_pnl": -0.015428,
          "pf": 0.0,
          "severe_pnl": -0.035428,
          "trades": 5,
          "win_rate": 0.0
        },
        "IMX_USDT": {
          "gross_pnl": -0.0007429999999999997,
          "pf": 0.0,
          "severe_pnl": -0.028742999999999998,
          "trades": 7,
          "win_rate": 0.0
        },
        "INDA_USDT": {
          "gross_pnl": -0.018995199999999997,
          "pf": 0.0575227867780632,
          "severe_pnl": -0.0949952,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "INJ_USDT": {
          "gross_pnl": -0.0023499000000000037,
          "pf": 0.04955613306700691,
          "severe_pnl": -0.35434990000000005,
          "trades": 88,
          "win_rate": 0.06818181818181818
        },
        "INTW_USDT": {
          "gross_pnl": -0.0291572,
          "pf": 0.03029609610794388,
          "severe_pnl": -0.04915720000000001,
          "trades": 5,
          "win_rate": 0.2
        },
        "IN_USDT": {
          "gross_pnl": -0.014956400000000002,
          "pf": 0.0,
          "severe_pnl": -0.0189564,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTA_USDT": {
          "gross_pnl": 0.013166899999999999,
          "pf": 999,
          "severe_pnl": 0.0051668999999999994,
          "trades": 2,
          "win_rate": 1.0
        },
        "IOTX_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "IO_USDT": {
          "gross_pnl": -0.004796,
          "pf": 0.0,
          "severe_pnl": -0.012795999999999998,
          "trades": 2,
          "win_rate": 0.0
        },
        "JASMY_USDT": {
          "gross_pnl": -0.004833599999999994,
          "pf": 0.09578022202049138,
          "severe_pnl": -0.24483359999999998,
          "trades": 60,
          "win_rate": 0.06666666666666667
        },
        "JCT_USDT": {
          "gross_pnl": 0.0178162,
          "pf": 0.5884648919395231,
          "severe_pnl": -0.0221838,
          "trades": 10,
          "win_rate": 0.3
        },
        "JP225_USDT": {
          "gross_pnl": -0.012246400000000001,
          "pf": 0.0,
          "severe_pnl": -0.0442464,
          "trades": 8,
          "win_rate": 0.0
        },
        "JST_USDT": {
          "gross_pnl": -0.0034276999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0274277,
          "trades": 6,
          "win_rate": 0.0
        },
        "JTO_USDT": {
          "gross_pnl": -0.0956259,
          "pf": 0.015997670700474937,
          "severe_pnl": -0.4356259,
          "trades": 85,
          "win_rate": 0.023529411764705882
        },
        "JUP_USDT": {
          "gross_pnl": -0.06393689999999998,
          "pf": 0.026731666537295296,
          "severe_pnl": -0.6319368999999999,
          "trades": 142,
          "win_rate": 0.04929577464788732
        },
        "KAIA_USDT": {
          "gross_pnl": 0.0036013,
          "pf": 0.0,
          "severe_pnl": -0.016398700000000002,
          "trades": 5,
          "win_rate": 0.0
        },
        "KAITO_USDT": {
          "gross_pnl": -0.10362939999999998,
          "pf": 0.08312115297523584,
          "severe_pnl": -0.3156293999999999,
          "trades": 53,
          "win_rate": 0.20754716981132076
        },
        "KAS_USDT": {
          "gross_pnl": -0.016892299999999996,
          "pf": 0.0,
          "severe_pnl": -0.12489230000000004,
          "trades": 27,
          "win_rate": 0.0
        },
        "KERNEL_USDT": {
          "gross_pnl": -0.0014731,
          "pf": 0.0,
          "severe_pnl": -0.0054731,
          "trades": 1,
          "win_rate": 0.0
        },
        "KITE_USDT": {
          "gross_pnl": 0.0456776,
          "pf": 0.3700204222310342,
          "severe_pnl": -0.07832239999999999,
          "trades": 31,
          "win_rate": 0.25806451612903225
        },
        "KMNO_USDT": {
          "gross_pnl": 0.008393699999999999,
          "pf": 0.0,
          "severe_pnl": -0.0196063,
          "trades": 7,
          "win_rate": 0.0
        },
        "KORU_USDT": {
          "gross_pnl": -0.021680999999999992,
          "pf": 0.3876414734716563,
          "severe_pnl": -0.301681,
          "trades": 70,
          "win_rate": 0.32857142857142857
        },
        "KSM_USDT": {
          "gross_pnl": 0.0047940000000000005,
          "pf": 0.0,
          "severe_pnl": -0.007205999999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "KSTR_USDT": {
          "gross_pnl": 0.0024673000000000004,
          "pf": 0.07435043750313701,
          "severe_pnl": -0.0055327,
          "trades": 2,
          "win_rate": 0.5
        },
        "LAB_USDT": {
          "gross_pnl": 0.08045929999999998,
          "pf": 0.7787473053982011,
          "severe_pnl": -0.14754070000000002,
          "trades": 57,
          "win_rate": 0.3333333333333333
        },
        "LAYER_USDT": {
          "gross_pnl": -0.0020495,
          "pf": 0.0,
          "severe_pnl": -0.0060495,
          "trades": 1,
          "win_rate": 0.0
        },
        "LDO_USDT": {
          "gross_pnl": -0.11787979999999991,
          "pf": 0.04689088118419891,
          "severe_pnl": -0.7698798,
          "trades": 163,
          "win_rate": 0.07975460122699386
        },
        "LEAD_USDT": {
          "gross_pnl": -0.0010641,
          "pf": 0.0,
          "severe_pnl": -0.0250641,
          "trades": 6,
          "win_rate": 0.0
        },
        "LIGHT_USDT": {
          "gross_pnl": 0.015304800000000004,
          "pf": 0.5127878879848717,
          "severe_pnl": -0.016695199999999997,
          "trades": 8,
          "win_rate": 0.125
        },
        "LINEA_USDT": {
          "gross_pnl": 0.0066116000000000005,
          "pf": 0.14066228997083094,
          "severe_pnl": -0.0213884,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "LINK_USDT": {
          "gross_pnl": -0.006828899999999998,
          "pf": 0.02812342472318584,
          "severe_pnl": -0.2348289000000001,
          "trades": 57,
          "win_rate": 0.05263157894736842
        },
        "LIT_USDT": {
          "gross_pnl": 0.08419530000000003,
          "pf": 0.1521304696179328,
          "severe_pnl": -0.5398046999999999,
          "trades": 156,
          "win_rate": 0.20512820512820512
        },
        "LRC_USDT": {
          "gross_pnl": -0.16840339999999998,
          "pf": 0.3331325445947012,
          "severe_pnl": -0.3164034000000001,
          "trades": 37,
          "win_rate": 0.2972972972972973
        },
        "LTC_USDT": {
          "gross_pnl": -0.0015195000000000005,
          "pf": 0.0021492388945898886,
          "severe_pnl": -0.1895195,
          "trades": 47,
          "win_rate": 0.0425531914893617
        },
        "LUMIA_USDT": {
          "gross_pnl": -0.0359409,
          "pf": 0.2920052204926176,
          "severe_pnl": -0.1199409,
          "trades": 21,
          "win_rate": 0.2857142857142857
        },
        "LUNANEW_USDT": {
          "gross_pnl": 0.0038916000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0041084,
          "trades": 2,
          "win_rate": 0.0
        },
        "LUNC_USDT": {
          "gross_pnl": -0.00032809999999999665,
          "pf": 0.02480573155402059,
          "severe_pnl": -0.18432810000000005,
          "trades": 46,
          "win_rate": 0.043478260869565216
        },
        "LYN_USDT": {
          "gross_pnl": -0.0259888,
          "pf": 0.0,
          "severe_pnl": -0.0339888,
          "trades": 2,
          "win_rate": 0.0
        },
        "MAGMA_USDT": {
          "gross_pnl": -0.22400910000000007,
          "pf": 0.3236660871525577,
          "severe_pnl": -0.5880090999999997,
          "trades": 91,
          "win_rate": 0.2857142857142857
        },
        "MANA_USDT": {
          "gross_pnl": -0.0078239,
          "pf": 0.036648433827007235,
          "severe_pnl": -0.06782389999999998,
          "trades": 15,
          "win_rate": 0.2
        },
        "MANTA_USDT": {
          "gross_pnl": 0.011781500000000002,
          "pf": 0.34064303572680327,
          "severe_pnl": -0.0282185,
          "trades": 10,
          "win_rate": 0.2
        },
        "MANTRA_USDT": {
          "gross_pnl": 0.0378847,
          "pf": 0.7454973379531818,
          "severe_pnl": -0.030115300000000005,
          "trades": 17,
          "win_rate": 0.29411764705882354
        },
        "MASK_USDT": {
          "gross_pnl": -0.0027976,
          "pf": 0.0,
          "severe_pnl": -0.0067976,
          "trades": 1,
          "win_rate": 0.0
        },
        "MAV_USDT": {
          "gross_pnl": -0.020191399999999998,
          "pf": 0.0,
          "severe_pnl": -0.0321914,
          "trades": 3,
          "win_rate": 0.0
        },
        "MEGA_USDT": {
          "gross_pnl": -0.0001926,
          "pf": 0.0,
          "severe_pnl": -0.0081926,
          "trades": 2,
          "win_rate": 0.0
        },
        "MEME_USDT": {
          "gross_pnl": 0.00011300000000000025,
          "pf": 0.006868394575132417,
          "severe_pnl": -0.023887,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "MERL_USDT": {
          "gross_pnl": 0.0029157000000000002,
          "pf": 0.13842659777037739,
          "severe_pnl": -0.041084300000000004,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "METIS_USDT": {
          "gross_pnl": 0.0015055,
          "pf": 0.0,
          "severe_pnl": -0.0064945,
          "trades": 2,
          "win_rate": 0.0
        },
        "MET_USDT": {
          "gross_pnl": -0.0088403,
          "pf": 0.0,
          "severe_pnl": -0.0208403,
          "trades": 3,
          "win_rate": 0.0
        },
        "MEW_USDT": {
          "gross_pnl": -0.0032795999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0072796,
          "trades": 1,
          "win_rate": 0.0
        },
        "ME_USDT": {
          "gross_pnl": -0.0052715999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0092716,
          "trades": 1,
          "win_rate": 0.0
        },
        "MINA_USDT": {
          "gross_pnl": 0.0037091,
          "pf": 0.0,
          "severe_pnl": -0.0042909,
          "trades": 2,
          "win_rate": 0.0
        },
        "MIRA_USDT": {
          "gross_pnl": 0.0062966,
          "pf": 0.16948436794664568,
          "severe_pnl": -0.005703400000000001,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "MITO_USDT": {
          "gross_pnl": -0.0998494,
          "pf": 0.0,
          "severe_pnl": -0.1238494,
          "trades": 6,
          "win_rate": 0.0
        },
        "MMT_USDT": {
          "gross_pnl": -0.05693490000000001,
          "pf": 0.22593938012381634,
          "severe_pnl": -0.2689349000000001,
          "trades": 53,
          "win_rate": 0.22641509433962265
        },
        "MNT_USDT": {
          "gross_pnl": -0.005274600000000001,
          "pf": 0.0,
          "severe_pnl": -0.0492746,
          "trades": 11,
          "win_rate": 0.0
        },
        "MOCA_USDT": {
          "gross_pnl": -0.006711399999999999,
          "pf": 0.0,
          "severe_pnl": -0.0107114,
          "trades": 1,
          "win_rate": 0.0
        },
        "MONAD_USDT": {
          "gross_pnl": -0.030447600000000005,
          "pf": 0.0,
          "severe_pnl": -0.16644760000000006,
          "trades": 34,
          "win_rate": 0.0
        },
        "MOODENG_USDT": {
          "gross_pnl": 0.0417115,
          "pf": 999,
          "severe_pnl": 0.037711499999999995,
          "trades": 1,
          "win_rate": 1.0
        },
        "MORPHO_USDT": {
          "gross_pnl": -0.012918100000000004,
          "pf": 0.03584937216961711,
          "severe_pnl": -0.1049181,
          "trades": 23,
          "win_rate": 0.13043478260869565
        },
        "MOVE_USDT": {
          "gross_pnl": -0.0008976,
          "pf": 0.0,
          "severe_pnl": -0.0128976,
          "trades": 3,
          "win_rate": 0.0
        },
        "MSTU_USDT": {
          "gross_pnl": -0.0422371,
          "pf": 0.09656619237863465,
          "severe_pnl": -0.0702371,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "MUBARAK_USDT": {
          "gross_pnl": 0.0021723000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0018276999999999998,
          "trades": 1,
          "win_rate": 0.0
        },
        "MUU_USDT": {
          "gross_pnl": -0.00508,
          "pf": 0.0,
          "severe_pnl": -0.017079999999999998,
          "trades": 3,
          "win_rate": 0.0
        },
        "MVLL_USDT": {
          "gross_pnl": 0.0240161,
          "pf": 0.6491812660300592,
          "severe_pnl": -0.08398390000000003,
          "trades": 27,
          "win_rate": 0.4444444444444444
        },
        "MYX_USDT": {
          "gross_pnl": -0.19028879999999995,
          "pf": 0.08006242761124946,
          "severe_pnl": -0.5142888000000001,
          "trades": 81,
          "win_rate": 0.13580246913580246
        },
        "NAORIS_USDT": {
          "gross_pnl": -0.0873863,
          "pf": 0.05709106973165381,
          "severe_pnl": -0.1553863,
          "trades": 17,
          "win_rate": 0.11764705882352941
        },
        "NEAR_USDT": {
          "gross_pnl": -0.08515340000000002,
          "pf": 0.022643582364290874,
          "severe_pnl": -0.44515340000000003,
          "trades": 90,
          "win_rate": 0.044444444444444446
        },
        "NEO_USDT": {
          "gross_pnl": 0.0079313,
          "pf": 0.9862890671775836,
          "severe_pnl": -6.869999999999966e-05,
          "trades": 2,
          "win_rate": 0.5
        },
        "NES_USDT": {
          "gross_pnl": -0.039093900000000015,
          "pf": 0.0798540232492087,
          "severe_pnl": -0.1350939,
          "trades": 24,
          "win_rate": 0.16666666666666666
        },
        "NEX_USDT": {
          "gross_pnl": -0.0528831,
          "pf": 0.0,
          "severe_pnl": -0.056883100000000006,
          "trades": 1,
          "win_rate": 0.0
        },
        "NGAS_USDT": {
          "gross_pnl": -0.008406200000000004,
          "pf": 0.002477139167786648,
          "severe_pnl": -0.20440619999999998,
          "trades": 49,
          "win_rate": 0.02040816326530612
        },
        "NICKEL_USDT": {
          "gross_pnl": 0.0042958,
          "pf": 0.022661034638939755,
          "severe_pnl": -0.039704199999999995,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "NIGHT_USDT": {
          "gross_pnl": 0.017866200000000002,
          "pf": 0.2656083596369428,
          "severe_pnl": -0.03813380000000001,
          "trades": 14,
          "win_rate": 0.2857142857142857
        },
        "NIL_USDT": {
          "gross_pnl": -0.005114900000000001,
          "pf": 0.0,
          "severe_pnl": -0.045114900000000006,
          "trades": 10,
          "win_rate": 0.0
        },
        "NOM_USDT": {
          "gross_pnl": -0.0017853999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0137854,
          "trades": 3,
          "win_rate": 0.0
        },
        "NOT_USDT": {
          "gross_pnl": 0.006584999999999999,
          "pf": 0.023785823897805917,
          "severe_pnl": -0.009415000000000001,
          "trades": 4,
          "win_rate": 0.25
        },
        "OFC_USDT": {
          "gross_pnl": 0.0040152,
          "pf": 0.30187319570069054,
          "severe_pnl": -0.0159848,
          "trades": 5,
          "win_rate": 0.2
        },
        "OGN_USDT": {
          "gross_pnl": -0.007182600000000001,
          "pf": 0.39444614035186626,
          "severe_pnl": -0.0751826,
          "trades": 17,
          "win_rate": 0.29411764705882354
        },
        "OG_USDT": {
          "gross_pnl": -0.012393000000000001,
          "pf": 0.0,
          "severe_pnl": -0.028393,
          "trades": 4,
          "win_rate": 0.0
        },
        "OKB_USDT": {
          "gross_pnl": 0.0009872,
          "pf": 0.0,
          "severe_pnl": -0.0030128000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "OL_USDT": {
          "gross_pnl": -0.0021853999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0101854,
          "trades": 2,
          "win_rate": 0.0
        },
        "ONDO_USDT": {
          "gross_pnl": -0.07259510000000001,
          "pf": 0.05273511428155479,
          "severe_pnl": -0.5725951000000001,
          "trades": 125,
          "win_rate": 0.064
        },
        "ONE_USDT": {
          "gross_pnl": 0.0089851,
          "pf": 0.2016279255184211,
          "severe_pnl": -0.011014900000000001,
          "trades": 5,
          "win_rate": 0.4
        },
        "ONT_USDT": {
          "gross_pnl": 0.0008782,
          "pf": 0.0,
          "severe_pnl": -0.0031218,
          "trades": 1,
          "win_rate": 0.0
        },
        "OPENAI_USDT": {
          "gross_pnl": -0.060879,
          "pf": 0.0,
          "severe_pnl": -0.4208790000000001,
          "trades": 90,
          "win_rate": 0.0
        },
        "OPG_USDT": {
          "gross_pnl": 0.0334007,
          "pf": 0.3173013802942645,
          "severe_pnl": -0.05459929999999999,
          "trades": 22,
          "win_rate": 0.2727272727272727
        },
        "OPN_USDT": {
          "gross_pnl": -0.029161700000000013,
          "pf": 0.18576459250165311,
          "severe_pnl": -0.21316169999999995,
          "trades": 46,
          "win_rate": 0.21739130434782608
        },
        "OP_USDT": {
          "gross_pnl": -0.1812308,
          "pf": 0.014572794230827394,
          "severe_pnl": -0.8732307999999999,
          "trades": 173,
          "win_rate": 0.028901734104046242
        },
        "ORCA_USDT": {
          "gross_pnl": -0.002521,
          "pf": 0.0,
          "severe_pnl": -0.006521,
          "trades": 1,
          "win_rate": 0.0
        },
        "ORDI_USDT": {
          "gross_pnl": -0.027061199999999994,
          "pf": 0.04254154491782814,
          "severe_pnl": -0.5350612000000001,
          "trades": 127,
          "win_rate": 0.07874015748031496
        },
        "O_USDT": {
          "gross_pnl": 0.04317419999999999,
          "pf": 0.35848561905036935,
          "severe_pnl": -0.16882580000000005,
          "trades": 53,
          "win_rate": 0.18867924528301888
        },
        "PARTI_USDT": {
          "gross_pnl": 0.0117541,
          "pf": 0.763786421894365,
          "severe_pnl": -0.0282459,
          "trades": 10,
          "win_rate": 0.4
        },
        "PAXG_USDT": {
          "gross_pnl": -0.0077526999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0277527,
          "trades": 5,
          "win_rate": 0.0
        },
        "PENDLE_USDT": {
          "gross_pnl": -0.008127800000000003,
          "pf": 0.029269242252840087,
          "severe_pnl": -0.1401278,
          "trades": 33,
          "win_rate": 0.06060606060606061
        },
        "PEOPLE_USDT": {
          "gross_pnl": -0.0023645,
          "pf": 0.0,
          "severe_pnl": -0.0063645,
          "trades": 1,
          "win_rate": 0.0
        },
        "PEPE_USDT": {
          "gross_pnl": -0.0011914000000000009,
          "pf": 0.15337688020614845,
          "severe_pnl": -0.0211914,
          "trades": 5,
          "win_rate": 0.2
        },
        "PHA_USDT": {
          "gross_pnl": -0.0141825,
          "pf": 0.0,
          "severe_pnl": -0.026182499999999997,
          "trades": 3,
          "win_rate": 0.0
        },
        "PIEVERSE_USDT": {
          "gross_pnl": -0.0005064000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0205064,
          "trades": 5,
          "win_rate": 0.0
        },
        "PIPPIN_USDT": {
          "gross_pnl": -0.10960170000000001,
          "pf": 0.027079003841440064,
          "severe_pnl": -0.3816017000000001,
          "trades": 68,
          "win_rate": 0.1323529411764706
        },
        "PIXEL_USDT": {
          "gross_pnl": -0.010740900000000001,
          "pf": 0.0,
          "severe_pnl": -0.0187409,
          "trades": 2,
          "win_rate": 0.0
        },
        "PI_USDT": {
          "gross_pnl": -0.0016881999999999939,
          "pf": 0.20359586797469054,
          "severe_pnl": -0.7536882000000001,
          "trades": 188,
          "win_rate": 0.16489361702127658
        },
        "PLUME_USDT": {
          "gross_pnl": -0.006978399999999999,
          "pf": 0.0,
          "severe_pnl": -0.0189784,
          "trades": 3,
          "win_rate": 0.0
        },
        "PNUT_USDT": {
          "gross_pnl": -0.0049173,
          "pf": 0.0,
          "severe_pnl": -0.0129173,
          "trades": 2,
          "win_rate": 0.0
        },
        "POL_USDT": {
          "gross_pnl": -0.020553199999999994,
          "pf": 0.0005374413854355552,
          "severe_pnl": -0.22855320000000004,
          "trades": 52,
          "win_rate": 0.019230769230769232
        },
        "POPCAT_USDT": {
          "gross_pnl": 0.0016254999999999998,
          "pf": 0.13878835170673393,
          "severe_pnl": -0.0103745,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "PORTAL_USDT": {
          "gross_pnl": 0.0008795,
          "pf": 0.0,
          "severe_pnl": -0.0031205,
          "trades": 1,
          "win_rate": 0.0
        },
        "POWER_USDT": {
          "gross_pnl": -0.0072770000000000005,
          "pf": 0.0,
          "severe_pnl": -0.015277,
          "trades": 2,
          "win_rate": 0.0
        },
        "POWR_USDT": {
          "gross_pnl": 0.0122856,
          "pf": 999,
          "severe_pnl": 0.0082856,
          "trades": 1,
          "win_rate": 1.0
        },
        "PROMPT_USDT": {
          "gross_pnl": 0.010526299999999999,
          "pf": 999,
          "severe_pnl": 0.006526299999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "PROM_USDT": {
          "gross_pnl": -0.0074091999999999995,
          "pf": 0.0,
          "severe_pnl": -0.023409199999999998,
          "trades": 4,
          "win_rate": 0.0
        },
        "PTB_USDT": {
          "gross_pnl": -0.0258193,
          "pf": 0.0,
          "severe_pnl": -0.0298193,
          "trades": 1,
          "win_rate": 0.0
        },
        "PUMPFUN_USDT": {
          "gross_pnl": -0.07657739999999999,
          "pf": 0.09281556112409388,
          "severe_pnl": -0.5165774000000001,
          "trades": 110,
          "win_rate": 0.13636363636363635
        },
        "PUNDIX_USDT": {
          "gross_pnl": -0.0007463,
          "pf": 0.0,
          "severe_pnl": -0.0047463,
          "trades": 1,
          "win_rate": 0.0
        },
        "PYTH_USDT": {
          "gross_pnl": -0.025940199999999983,
          "pf": 0.0725425355480449,
          "severe_pnl": -0.5419402000000003,
          "trades": 129,
          "win_rate": 0.14728682170542637
        },
        "QNT_USDT": {
          "gross_pnl": -0.0013696,
          "pf": 0.0,
          "severe_pnl": -0.0093696,
          "trades": 2,
          "win_rate": 0.0
        },
        "QTUM_USDT": {
          "gross_pnl": 0.0120144,
          "pf": 1.003908264350658,
          "severe_pnl": 1.4399999999999483e-05,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "Q_USDT": {
          "gross_pnl": -0.0020726,
          "pf": 0.0,
          "severe_pnl": -0.0060726,
          "trades": 1,
          "win_rate": 0.0
        },
        "RAM_USDT": {
          "gross_pnl": -0.035502900000000004,
          "pf": 0.0,
          "severe_pnl": -0.0955029,
          "trades": 15,
          "win_rate": 0.0
        },
        "RARE_USDT": {
          "gross_pnl": -0.0049645,
          "pf": 0.0,
          "severe_pnl": -0.0089645,
          "trades": 1,
          "win_rate": 0.0
        },
        "RAVE_USDT": {
          "gross_pnl": -0.2244604,
          "pf": 0.11173534559904465,
          "severe_pnl": -0.6084603999999999,
          "trades": 96,
          "win_rate": 0.13541666666666666
        },
        "RAY_USDT": {
          "gross_pnl": 0.0034391,
          "pf": 0.20049338849757894,
          "severe_pnl": -0.0165609,
          "trades": 5,
          "win_rate": 0.2
        },
        "RENDER_USDT": {
          "gross_pnl": -0.007343300000000007,
          "pf": 0.008819477954410043,
          "severe_pnl": -0.27134330000000006,
          "trades": 66,
          "win_rate": 0.030303030303030304
        },
        "RESOLV_USDT": {
          "gross_pnl": -0.03952249999999999,
          "pf": 0.03992845985072442,
          "severe_pnl": -0.23152250000000002,
          "trades": 48,
          "win_rate": 0.10416666666666667
        },
        "REZ_USDT": {
          "gross_pnl": -0.005294,
          "pf": 0.0,
          "severe_pnl": -0.013294,
          "trades": 2,
          "win_rate": 0.0
        },
        "RE_USDT": {
          "gross_pnl": -0.03109420000000005,
          "pf": 0.11882994916749649,
          "severe_pnl": -0.4750941999999999,
          "trades": 111,
          "win_rate": 0.14414414414414414
        },
        "RIF_USDT": {
          "gross_pnl": -0.041993499999999996,
          "pf": 0.001206785313504268,
          "severe_pnl": -0.09799349999999998,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "RLC_USDT": {
          "gross_pnl": 0.010854500000000003,
          "pf": 0.4598988531582846,
          "severe_pnl": -0.0211455,
          "trades": 8,
          "win_rate": 0.5
        },
        "ROAM_USDT": {
          "gross_pnl": 0.3676885999999999,
          "pf": 1.5159963222887212,
          "severe_pnl": 0.29968859999999986,
          "trades": 17,
          "win_rate": 0.4117647058823529
        },
        "ROBO_USDT": {
          "gross_pnl": 0.0014747000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0065252999999999995,
          "trades": 2,
          "win_rate": 0.0
        },
        "ROSE_USDT": {
          "gross_pnl": 0.0222775,
          "pf": 0.4691201844587328,
          "severe_pnl": -0.013722499999999999,
          "trades": 9,
          "win_rate": 0.3333333333333333
        },
        "RPL_USDT": {
          "gross_pnl": 0.0029107,
          "pf": 0.0,
          "severe_pnl": -0.0050893,
          "trades": 2,
          "win_rate": 0.0
        },
        "RSR_USDT": {
          "gross_pnl": -0.0063269,
          "pf": 0.0,
          "severe_pnl": -0.0343269,
          "trades": 7,
          "win_rate": 0.0
        },
        "RUNE_USDT": {
          "gross_pnl": 0.011330099999999997,
          "pf": 0.2164952710041732,
          "severe_pnl": -0.0246699,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "RVN_USDT": {
          "gross_pnl": 0.0026087999999999997,
          "pf": 0.26398417421337245,
          "severe_pnl": -0.0453912,
          "trades": 12,
          "win_rate": 0.16666666666666666
        },
        "SAFE_USDT": {
          "gross_pnl": -0.006941499999999999,
          "pf": 0.0,
          "severe_pnl": -0.0189415,
          "trades": 3,
          "win_rate": 0.0
        },
        "SAGA_USDT": {
          "gross_pnl": 0.0110289,
          "pf": 0.8246510536104439,
          "severe_pnl": -0.0009711000000000003,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "SAHARA_USDT": {
          "gross_pnl": -0.0033035,
          "pf": 0.0,
          "severe_pnl": -0.051303500000000016,
          "trades": 12,
          "win_rate": 0.0
        },
        "SAND_USDT": {
          "gross_pnl": -4.3399999999999917e-05,
          "pf": 0.0,
          "severe_pnl": -0.04404340000000001,
          "trades": 11,
          "win_rate": 0.0
        },
        "SANTOS_USDT": {
          "gross_pnl": -0.0086369,
          "pf": 0.0,
          "severe_pnl": -0.0166369,
          "trades": 2,
          "win_rate": 0.0
        },
        "SEI_USDT": {
          "gross_pnl": -0.011857999999999999,
          "pf": 0.00722480348173354,
          "severe_pnl": -0.307858,
          "trades": 74,
          "win_rate": 0.02702702702702703
        },
        "SENT_USDT": {
          "gross_pnl": 0.025377699999999996,
          "pf": 0.630291115716503,
          "severe_pnl": -0.07462230000000003,
          "trades": 25,
          "win_rate": 0.32
        },
        "SFP_USDT": {
          "gross_pnl": -0.0004662,
          "pf": 0.0,
          "severe_pnl": -0.0044662,
          "trades": 1,
          "win_rate": 0.0
        },
        "SHIB_USDT": {
          "gross_pnl": 0.0030496000000000026,
          "pf": 0.005464221489926877,
          "severe_pnl": -0.1089504,
          "trades": 28,
          "win_rate": 0.07142857142857142
        },
        "SIGN_USDT": {
          "gross_pnl": -0.0008042,
          "pf": 0.0,
          "severe_pnl": -0.0048042,
          "trades": 1,
          "win_rate": 0.0
        },
        "SKL_USDT": {
          "gross_pnl": -0.04582390000000002,
          "pf": 0.4621537525123613,
          "severe_pnl": -0.20182390000000003,
          "trades": 39,
          "win_rate": 0.28205128205128205
        },
        "SKYAI_USDT": {
          "gross_pnl": 0.012810200000000032,
          "pf": 0.27019168363836066,
          "severe_pnl": -0.5671898000000001,
          "trades": 145,
          "win_rate": 0.21379310344827587
        },
        "SKY_USDT": {
          "gross_pnl": 8.520000000000055e-05,
          "pf": 0.002236465634643971,
          "severe_pnl": -0.047914799999999994,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "SLX_USDT": {
          "gross_pnl": -0.21574100000000004,
          "pf": 0.12847003968599036,
          "severe_pnl": -0.771741,
          "trades": 139,
          "win_rate": 0.1510791366906475
        },
        "SMH_USDT": {
          "gross_pnl": 0.0021644,
          "pf": 0.0,
          "severe_pnl": -0.0018356000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "SNT_USDT": {
          "gross_pnl": -0.0035262999999999996,
          "pf": 0.0,
          "severe_pnl": -0.015526300000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "SNXX_USDT": {
          "gross_pnl": -0.06273569999999999,
          "pf": 0.2706872004814935,
          "severe_pnl": -0.17073570000000002,
          "trades": 27,
          "win_rate": 0.2962962962962963
        },
        "SNX_USDT": {
          "gross_pnl": 0.0068901,
          "pf": 0.012115794990827721,
          "severe_pnl": -0.0211099,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "SOL_USDT": {
          "gross_pnl": 0.019904300000000003,
          "pf": 0.020671265717500862,
          "severe_pnl": -0.1160957,
          "trades": 34,
          "win_rate": 0.08823529411764706
        },
        "SOONNETWORK_USDT": {
          "gross_pnl": 0.0029942000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0090058,
          "trades": 3,
          "win_rate": 0.0
        },
        "SOXL_USDT": {
          "gross_pnl": -0.02001190000000002,
          "pf": 0.3388623728770605,
          "severe_pnl": -0.48001190000000005,
          "trades": 115,
          "win_rate": 0.26956521739130435
        },
        "SOXS_USDT": {
          "gross_pnl": 0.0421545,
          "pf": 0.5129486116422481,
          "severe_pnl": -0.0658455,
          "trades": 27,
          "win_rate": 0.4074074074074074
        },
        "SOXX_USDT": {
          "gross_pnl": -0.0025073999999999995,
          "pf": 0.03195424593576184,
          "severe_pnl": -0.05050739999999999,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "SPACE_USDT": {
          "gross_pnl": -0.0061958000000000004,
          "pf": 0.0,
          "severe_pnl": -0.010195800000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "SPELL_USDT": {
          "gross_pnl": -0.0568256,
          "pf": 0.0,
          "severe_pnl": -0.07682560000000001,
          "trades": 5,
          "win_rate": 0.0
        },
        "SPORTFUN_USDT": {
          "gross_pnl": -0.0593283,
          "pf": 0.0,
          "severe_pnl": -0.06732830000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "SPY_USDT": {
          "gross_pnl": -0.0005659,
          "pf": 0.0,
          "severe_pnl": -0.0045659,
          "trades": 1,
          "win_rate": 0.0
        },
        "SQD_USDT": {
          "gross_pnl": 0.002191000000000001,
          "pf": 0.24668789604415556,
          "severe_pnl": -0.025809,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "SQQQ_USDT": {
          "gross_pnl": -0.0080774,
          "pf": 0.06404298867280472,
          "severe_pnl": -0.028077400000000002,
          "trades": 5,
          "win_rate": 0.2
        },
        "STABLE_USDT": {
          "gross_pnl": -0.014750599999999999,
          "pf": 0.0,
          "severe_pnl": -0.0507506,
          "trades": 9,
          "win_rate": 0.0
        },
        "STAR_USDT": {
          "gross_pnl": -0.11019969999999998,
          "pf": 0.0,
          "severe_pnl": -0.1221997,
          "trades": 3,
          "win_rate": 0.0
        },
        "STG_USDT": {
          "gross_pnl": -0.018294199999999997,
          "pf": 0.0791189254313652,
          "severe_pnl": -0.0862942,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "STO_USDT": {
          "gross_pnl": 0.0019139,
          "pf": 0.0,
          "severe_pnl": -0.0020861,
          "trades": 1,
          "win_rate": 0.0
        },
        "STRK_USDT": {
          "gross_pnl": -0.007318099999999999,
          "pf": 0.14759367348904887,
          "severe_pnl": -0.0513181,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "STX_USDT": {
          "gross_pnl": -0.0188446,
          "pf": 0.01772562986754223,
          "severe_pnl": -0.09884460000000002,
          "trades": 20,
          "win_rate": 0.05
        },
        "SUI_USDT": {
          "gross_pnl": 0.009574000000000001,
          "pf": 0.020057744969888082,
          "severe_pnl": -0.23442600000000008,
          "trades": 61,
          "win_rate": 0.08196721311475409
        },
        "SUPER_USDT": {
          "gross_pnl": 0.0035336,
          "pf": 0.0,
          "severe_pnl": -0.00046640000000000006,
          "trades": 1,
          "win_rate": 0.0
        },
        "SUSHI_USDT": {
          "gross_pnl": 0.0011933,
          "pf": 0.0,
          "severe_pnl": -0.0028067,
          "trades": 1,
          "win_rate": 0.0
        },
        "SXT_USDT": {
          "gross_pnl": 0.07203699999999996,
          "pf": 0.5236678791531247,
          "severe_pnl": -0.33196300000000006,
          "trades": 101,
          "win_rate": 0.3069306930693069
        },
        "SYN_USDT": {
          "gross_pnl": -0.025163699999999997,
          "pf": 0.3341827092238025,
          "severe_pnl": -0.7491637000000001,
          "trades": 181,
          "win_rate": 0.3259668508287293
        },
        "SYRUP_USDT": {
          "gross_pnl": -0.05140490000000001,
          "pf": 0.0774649958465579,
          "severe_pnl": -0.3074049000000001,
          "trades": 64,
          "win_rate": 0.09375
        },
        "S_USDT": {
          "gross_pnl": -0.002031299999999999,
          "pf": 0.0,
          "severe_pnl": -0.030031299999999997,
          "trades": 7,
          "win_rate": 0.0
        },
        "TAC_USDT": {
          "gross_pnl": -0.01658749999999999,
          "pf": 0.457242858607145,
          "severe_pnl": -0.2885875,
          "trades": 68,
          "win_rate": 0.3382352941176471
        },
        "TAG_USDT": {
          "gross_pnl": 0.22392320000000002,
          "pf": 1.4752073466497815,
          "severe_pnl": 0.10792320000000004,
          "trades": 29,
          "win_rate": 0.41379310344827586
        },
        "TAIKO_USDT": {
          "gross_pnl": -0.0088827,
          "pf": 0.05863236545918851,
          "severe_pnl": -0.0248827,
          "trades": 4,
          "win_rate": 0.25
        },
        "TAO_USDT": {
          "gross_pnl": -0.0165526,
          "pf": 0.0,
          "severe_pnl": -0.10455260000000002,
          "trades": 22,
          "win_rate": 0.0
        },
        "THETA_USDT": {
          "gross_pnl": 0.014918299999999995,
          "pf": 0.045534597649653195,
          "severe_pnl": -0.1450817,
          "trades": 40,
          "win_rate": 0.075
        },
        "THE_USDT": {
          "gross_pnl": -0.009464400000000003,
          "pf": 0.1328586850697733,
          "severe_pnl": -0.06546439999999999,
          "trades": 14,
          "win_rate": 0.2857142857142857
        },
        "TIA_USDT": {
          "gross_pnl": -0.05972409999999998,
          "pf": 0.024225967543156722,
          "severe_pnl": -0.47172409999999987,
          "trades": 103,
          "win_rate": 0.05825242718446602
        },
        "TLM_USDT": {
          "gross_pnl": 0.04356959999999997,
          "pf": 0.3794358502210051,
          "severe_pnl": -0.20443040000000004,
          "trades": 62,
          "win_rate": 0.22580645161290322
        },
        "TOSHI_USDT": {
          "gross_pnl": 0.012448799999999998,
          "pf": 0.6614833219347075,
          "severe_pnl": -0.019551200000000005,
          "trades": 8,
          "win_rate": 0.375
        },
        "TOWNS_USDT": {
          "gross_pnl": 0.0449746,
          "pf": 1.0891118905420947,
          "severe_pnl": 0.004974599999999992,
          "trades": 10,
          "win_rate": 0.3
        },
        "TQQQ_USDT": {
          "gross_pnl": -0.008057400000000001,
          "pf": 0.12176268806914309,
          "severe_pnl": -0.0640574,
          "trades": 14,
          "win_rate": 0.21428571428571427
        },
        "TRADOOR_USDT": {
          "gross_pnl": -0.021979499999999985,
          "pf": 0.49198046476892265,
          "severe_pnl": -0.18597949999999994,
          "trades": 41,
          "win_rate": 0.2682926829268293
        },
        "TRB_USDT": {
          "gross_pnl": -0.0004978999999999995,
          "pf": 0.0,
          "severe_pnl": -0.06049790000000001,
          "trades": 15,
          "win_rate": 0.0
        },
        "TRIA_USDT": {
          "gross_pnl": 0.0022922000000000047,
          "pf": 0.3597640326368258,
          "severe_pnl": -0.5177077999999998,
          "trades": 130,
          "win_rate": 0.2230769230769231
        },
        "TRUST_USDT": {
          "gross_pnl": -0.0037283,
          "pf": 0.0,
          "severe_pnl": -0.0077283000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "TRX_USDT": {
          "gross_pnl": -0.0013499000000000002,
          "pf": 0.0,
          "severe_pnl": -0.025349899999999998,
          "trades": 6,
          "win_rate": 0.0
        },
        "TRY_USDT": {
          "gross_pnl": -0.00046929999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0044693,
          "trades": 1,
          "win_rate": 0.0
        },
        "TURBO_USDT": {
          "gross_pnl": -0.0037806999999999997,
          "pf": 0.018367166657832897,
          "severe_pnl": -0.027780700000000002,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "TUT_USDT": {
          "gross_pnl": 0.0123552,
          "pf": 2.0888,
          "severe_pnl": 0.0043552,
          "trades": 2,
          "win_rate": 0.5
        },
        "TWT_USDT": {
          "gross_pnl": -0.0011604000000000007,
          "pf": 0.0,
          "severe_pnl": -0.029160400000000003,
          "trades": 7,
          "win_rate": 0.0
        },
        "T_USDT": {
          "gross_pnl": 0.1300901,
          "pf": 0.6180676187216413,
          "severe_pnl": -0.21390989999999996,
          "trades": 86,
          "win_rate": 0.32558139534883723
        },
        "UAI_USDT": {
          "gross_pnl": -0.08280499999999998,
          "pf": 0.1050824655104613,
          "severe_pnl": -0.29880500000000004,
          "trades": 54,
          "win_rate": 0.1111111111111111
        },
        "UMA_USDT": {
          "gross_pnl": 0.0092415,
          "pf": 0.6316056571268314,
          "severe_pnl": -0.0027584999999999997,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "UNI_USDT": {
          "gross_pnl": 0.009308499999999997,
          "pf": 0.06486100938450491,
          "severe_pnl": -0.4146915,
          "trades": 106,
          "win_rate": 0.14150943396226415
        },
        "USELESS_USDT": {
          "gross_pnl": 0.0748872,
          "pf": 0.25428334735999547,
          "severe_pnl": -0.1811128,
          "trades": 64,
          "win_rate": 0.25
        },
        "USO_USDT": {
          "gross_pnl": -0.0114353,
          "pf": 0.0,
          "severe_pnl": -0.035435299999999996,
          "trades": 6,
          "win_rate": 0.0
        },
        "USUAL_USDT": {
          "gross_pnl": 0.004284199999999997,
          "pf": 0.13792125341239425,
          "severe_pnl": -0.04771580000000001,
          "trades": 13,
          "win_rate": 0.23076923076923078
        },
        "UVXY_USDT": {
          "gross_pnl": 0.0021808999999999995,
          "pf": 0.2037522260823869,
          "severe_pnl": -0.0218191,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "VANA_USDT": {
          "gross_pnl": 0.0224928,
          "pf": 2.0207681544484095,
          "severe_pnl": 0.0064928,
          "trades": 4,
          "win_rate": 0.5
        },
        "VANRY_USDT": {
          "gross_pnl": -0.07856189999999998,
          "pf": 0.35212798184688765,
          "severe_pnl": -0.2585619,
          "trades": 45,
          "win_rate": 0.28888888888888886
        },
        "VELO_USDT": {
          "gross_pnl": 0.0025877999999999995,
          "pf": 0.0,
          "severe_pnl": -0.009412199999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "VELVET_USDT": {
          "gross_pnl": 0.026682500000000015,
          "pf": 0.5532187983569007,
          "severe_pnl": -0.5453175000000005,
          "trades": 143,
          "win_rate": 0.3076923076923077
        },
        "VET_USDT": {
          "gross_pnl": -0.0152233,
          "pf": 0.0,
          "severe_pnl": -0.08722329999999999,
          "trades": 18,
          "win_rate": 0.0
        },
        "VINE_USDT": {
          "gross_pnl": -0.0146517,
          "pf": 0.0,
          "severe_pnl": -0.0426517,
          "trades": 7,
          "win_rate": 0.0
        },
        "VIRTUAL_USDT": {
          "gross_pnl": 0.02069270000000001,
          "pf": 0.07029368480869586,
          "severe_pnl": -0.4913072999999999,
          "trades": 128,
          "win_rate": 0.1171875
        },
        "VVV_USDT": {
          "gross_pnl": 0.06428819999999999,
          "pf": 0.2314438921850034,
          "severe_pnl": -0.2957118000000001,
          "trades": 90,
          "win_rate": 0.17777777777777778
        },
        "WAL_USDT": {
          "gross_pnl": -0.0053174,
          "pf": 0.0,
          "severe_pnl": -0.0093174,
          "trades": 1,
          "win_rate": 0.0
        },
        "WET_USDT": {
          "gross_pnl": -0.010199199999999999,
          "pf": 0.0,
          "severe_pnl": -0.014199199999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "WIF_USDT": {
          "gross_pnl": -0.018237800000000005,
          "pf": 0.018537093656979975,
          "severe_pnl": -0.3982377999999999,
          "trades": 95,
          "win_rate": 0.031578947368421054
        },
        "WLD_USDT": {
          "gross_pnl": 0.0013118999999999917,
          "pf": 0.07188818463791011,
          "severe_pnl": -0.2986881,
          "trades": 75,
          "win_rate": 0.12
        },
        "WLFI_USDT": {
          "gross_pnl": -0.0029970000000000005,
          "pf": 0.0,
          "severe_pnl": -0.10299700000000002,
          "trades": 25,
          "win_rate": 0.0
        },
        "WOO_USDT": {
          "gross_pnl": 0.0071146,
          "pf": 999,
          "severe_pnl": 0.0031145999999999995,
          "trades": 1,
          "win_rate": 1.0
        },
        "W_USDT": {
          "gross_pnl": -0.0132161,
          "pf": 0.0,
          "severe_pnl": -0.049216100000000006,
          "trades": 9,
          "win_rate": 0.0
        },
        "XAI_USDT": {
          "gross_pnl": 0.0009247000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0190753,
          "trades": 5,
          "win_rate": 0.0
        },
        "XAN_USDT": {
          "gross_pnl": -0.0505175,
          "pf": 0.04493820024897742,
          "severe_pnl": -0.09451749999999999,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "XBI_USDT": {
          "gross_pnl": -0.0080151,
          "pf": 0.05138013173014761,
          "severe_pnl": -0.0600151,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "XDC_USDT": {
          "gross_pnl": 0.0036855000000000004,
          "pf": 0.0637110961205243,
          "severe_pnl": -0.028314500000000003,
          "trades": 8,
          "win_rate": 0.25
        },
        "XEC_USDT": {
          "gross_pnl": 0.04595019999999993,
          "pf": 0.5350927389446353,
          "severe_pnl": -0.3900498,
          "trades": 109,
          "win_rate": 0.30275229357798167
        },
        "XLM_USDT": {
          "gross_pnl": -0.0020933,
          "pf": 0.04033858263400517,
          "severe_pnl": -0.21009329999999993,
          "trades": 52,
          "win_rate": 0.07692307692307693
        },
        "XLU_USDT": {
          "gross_pnl": -0.0028139999999999997,
          "pf": 0.0,
          "severe_pnl": -0.014814,
          "trades": 3,
          "win_rate": 0.0
        },
        "XMR_USDT": {
          "gross_pnl": -0.0091918,
          "pf": 0.005439915587136952,
          "severe_pnl": -0.36119179999999995,
          "trades": 88,
          "win_rate": 0.022727272727272728
        },
        "XPIN_USDT": {
          "gross_pnl": 0.0364066,
          "pf": 0.6328627753524549,
          "severe_pnl": -0.0395934,
          "trades": 19,
          "win_rate": 0.3684210526315789
        },
        "XPL_USDT": {
          "gross_pnl": -0.0002297000000000013,
          "pf": 0.034610049860337874,
          "severe_pnl": -0.31222970000000005,
          "trades": 78,
          "win_rate": 0.0641025641025641
        },
        "XPT_USDT": {
          "gross_pnl": -0.0204206,
          "pf": 0.0,
          "severe_pnl": -0.12042059999999999,
          "trades": 25,
          "win_rate": 0.0
        },
        "XRP_USDT": {
          "gross_pnl": -0.012168200000000006,
          "pf": 0.017178168268701176,
          "severe_pnl": -0.16416820000000004,
          "trades": 38,
          "win_rate": 0.02631578947368421
        },
        "XTZ_USDT": {
          "gross_pnl": 0.003806,
          "pf": 0.0,
          "severe_pnl": -0.016194,
          "trades": 5,
          "win_rate": 0.0
        },
        "YFI_USDT": {
          "gross_pnl": -0.0318971,
          "pf": 0.0,
          "severe_pnl": -0.0878971,
          "trades": 14,
          "win_rate": 0.0
        },
        "ZAMA_USDT": {
          "gross_pnl": -0.0164933,
          "pf": 0.0,
          "severe_pnl": -0.040493299999999996,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZBT_USDT": {
          "gross_pnl": -0.018245899999999995,
          "pf": 0.21255447801226635,
          "severe_pnl": -0.3822458999999999,
          "trades": 91,
          "win_rate": 0.24175824175824176
        },
        "ZEC_USDT": {
          "gross_pnl": -0.03365739999999999,
          "pf": 0.026405003854784035,
          "severe_pnl": -0.2736574,
          "trades": 60,
          "win_rate": 0.08333333333333333
        },
        "ZEN_USDT": {
          "gross_pnl": 0.016364100000000003,
          "pf": 0.15045706354938193,
          "severe_pnl": -0.07963590000000001,
          "trades": 24,
          "win_rate": 0.16666666666666666
        },
        "ZEST_USDT": {
          "gross_pnl": 0.005411000000000001,
          "pf": 0.4194351343384609,
          "severe_pnl": -0.026589,
          "trades": 8,
          "win_rate": 0.25
        },
        "ZETA_USDT": {
          "gross_pnl": -0.0008671,
          "pf": 0.0,
          "severe_pnl": -0.0048671,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZIL_USDT": {
          "gross_pnl": 0.006905,
          "pf": 0.0,
          "severe_pnl": -0.001095,
          "trades": 2,
          "win_rate": 0.0
        },
        "ZINC_USDT": {
          "gross_pnl": 0.0025061,
          "pf": 0.0,
          "severe_pnl": -0.021493900000000003,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZKP_USDT": {
          "gross_pnl": -0.0071923,
          "pf": 0.0,
          "severe_pnl": -0.035192299999999996,
          "trades": 7,
          "win_rate": 0.0
        },
        "ZKSYNC_USDT": {
          "gross_pnl": 0.004721299999999999,
          "pf": 0.0,
          "severe_pnl": -0.04727869999999999,
          "trades": 13,
          "win_rate": 0.0
        },
        "ZORA_USDT": {
          "gross_pnl": 0.0028426999999999992,
          "pf": 0.24214474585509208,
          "severe_pnl": -0.04115730000000001,
          "trades": 11,
          "win_rate": 0.2727272727272727
        },
        "ZRO_USDT": {
          "gross_pnl": 0.02899419999999999,
          "pf": 0.14326978079500935,
          "severe_pnl": -0.1270058,
          "trades": 39,
          "win_rate": 0.1282051282051282
        }
      },
      "validation_depth_quartiles": [
        {
          "gross_pnl": -0.9114932000000032,
          "pf": 0.431695686541174,
          "quartile": 1,
          "severe_pnl": -12.047493199999982,
          "trades": 2784,
          "upper": 8976.76524,
          "win_rate": 0.2377873563218391
        },
        {
          "gross_pnl": -1.0044583000000007,
          "pf": 0.23834357933359412,
          "quartile": 2,
          "severe_pnl": -13.776458299999979,
          "trades": 3193,
          "upper": 106972.33601999999,
          "win_rate": 0.15659254619480112
        },
        {
          "gross_pnl": -0.8067818000000007,
          "pf": 0.17411239689090105,
          "quartile": 3,
          "severe_pnl": -14.194781799999948,
          "trades": 3347,
          "upper": 1071304.435,
          "win_rate": 0.14580221093516582
        },
        {
          "gross_pnl": -0.6880175999999999,
          "pf": 0.0819815860145418,
          "quartile": 4,
          "severe_pnl": -12.688017599999919,
          "trades": 3000,
          "upper": null,
          "win_rate": 0.08866666666666667
        }
      ],
      "validation_pass": false,
      "validation_skips": {
        "invalid_path_json": 0,
        "missing_horizon_path": 117,
        "structure_not_selected": 74905,
        "symbol_cooldown": 3954
      },
      "validation_spread_quartiles": [
        {
          "gross_pnl": -0.5830321000000004,
          "pf": 0.14672782823111424,
          "quartile": 1,
          "severe_pnl": -12.483032099999994,
          "trades": 2975,
          "upper": 2.148689299527946,
          "win_rate": 0.12705882352941175
        },
        {
          "gross_pnl": -0.5154656999999994,
          "pf": 0.21771374587892356,
          "quartile": 2,
          "severe_pnl": -13.099465699999946,
          "trades": 3146,
          "upper": 4.268032437045758,
          "win_rate": 0.1519389701207883
        },
        {
          "gross_pnl": -1.4221167000000012,
          "pf": 0.19709639981498495,
          "quartile": 3,
          "severe_pnl": -14.410116699999964,
          "trades": 3247,
          "upper": 7.482229704451622,
          "win_rate": 0.14567292885740685
        },
        {
          "gross_pnl": -0.8901363999999994,
          "pf": 0.39377683166739286,
          "quartile": 4,
          "severe_pnl": -12.714136399999955,
          "trades": 2956,
          "upper": null,
          "win_rate": 0.19857916102841677
        }
      ]
    },
    {
      "direction": "fade",
      "horizon_seconds": 60,
      "leave_best_symbol": -45.72170679999938,
      "structure": "confirm",
      "validation": {
        "gross_pnl": 0.49406179999999683,
        "pf": 0.09713055762559883,
        "severe_pnl": -45.685938199999384,
        "trades": 11545,
        "win_rate": 0.09181463837158943
      },
      "validation_by_symbol": {
        "0G_USDT": {
          "gross_pnl": -0.0026093000000000006,
          "pf": 0.05289053019098081,
          "severe_pnl": -0.09060929999999999,
          "trades": 22,
          "win_rate": 0.09090909090909091
        },
        "1000000BABYDOGE_USDT": {
          "gross_pnl": 0.006099899999999998,
          "pf": 0.11617452566254635,
          "severe_pnl": -0.013900100000000002,
          "trades": 5,
          "win_rate": 0.2
        },
        "1000BONK_USDT": {
          "gross_pnl": 0.022657700000000006,
          "pf": 0.028928745302834895,
          "severe_pnl": -0.16934230000000003,
          "trades": 48,
          "win_rate": 0.0625
        },
        "1INCH_USDT": {
          "gross_pnl": 0.0001337,
          "pf": 0.0,
          "severe_pnl": -0.0038663,
          "trades": 1,
          "win_rate": 0.0
        },
        "2Z_USDT": {
          "gross_pnl": 0.043768600000000005,
          "pf": 9.091894215324752,
          "severe_pnl": 0.0357686,
          "trades": 2,
          "win_rate": 0.5
        },
        "4_USDT": {
          "gross_pnl": 0.014276599999999999,
          "pf": 0.13229637958575396,
          "severe_pnl": -0.009723399999999998,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "AAVE_USDT": {
          "gross_pnl": -0.012892699999999998,
          "pf": 0.0033377686316966807,
          "severe_pnl": -0.18089270000000005,
          "trades": 42,
          "win_rate": 0.023809523809523808
        },
        "ACE_USDT": {
          "gross_pnl": -0.060283699999999996,
          "pf": 0.0,
          "severe_pnl": -0.0642837,
          "trades": 1,
          "win_rate": 0.0
        },
        "ACT_USDT": {
          "gross_pnl": -0.00351,
          "pf": 0.0,
          "severe_pnl": -0.01551,
          "trades": 3,
          "win_rate": 0.0
        },
        "ACU_USDT": {
          "gross_pnl": -0.0029502,
          "pf": 0.0,
          "severe_pnl": -0.0189502,
          "trades": 4,
          "win_rate": 0.0
        },
        "ADA_USDT": {
          "gross_pnl": 0.012154900000000007,
          "pf": 0.001441087756095706,
          "severe_pnl": -0.25984510000000005,
          "trades": 68,
          "win_rate": 0.014705882352941176
        },
        "AERGO_USDT": {
          "gross_pnl": -0.0018270999999999995,
          "pf": 0.10777445408315883,
          "severe_pnl": -0.029827100000000002,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "AERO_USDT": {
          "gross_pnl": 0.004884699999999996,
          "pf": 0.026176042627557218,
          "severe_pnl": -0.1671153,
          "trades": 43,
          "win_rate": 0.046511627906976744
        },
        "AEVO_USDT": {
          "gross_pnl": -0.0005249,
          "pf": 0.0,
          "severe_pnl": -0.0045249,
          "trades": 1,
          "win_rate": 0.0
        },
        "AGI_USDT": {
          "gross_pnl": 0.005363699999999999,
          "pf": 0.055398192299480356,
          "severe_pnl": -0.006636300000000001,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "AGLD_USDT": {
          "gross_pnl": -0.024051499999999996,
          "pf": 0.11681989492919141,
          "severe_pnl": -0.0680515,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "AGT_USDT": {
          "gross_pnl": -0.0021845,
          "pf": 0.0,
          "severe_pnl": -0.010184499999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "AIGENSYN_USDT": {
          "gross_pnl": 0.009084499999999999,
          "pf": 0.0010015974845956864,
          "severe_pnl": -0.0709155,
          "trades": 20,
          "win_rate": 0.05
        },
        "AIOT_USDT": {
          "gross_pnl": -0.0031781000000000127,
          "pf": 0.26229062055858676,
          "severe_pnl": -0.17917809999999998,
          "trades": 44,
          "win_rate": 0.20454545454545456
        },
        "AIOZ_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "AIO_USDT": {
          "gross_pnl": 0.0049713,
          "pf": 0.5381812082583635,
          "severe_pnl": -0.0030287000000000005,
          "trades": 2,
          "win_rate": 0.5
        },
        "AKE_USDT": {
          "gross_pnl": -0.019655699999999977,
          "pf": 0.562356966709873,
          "severe_pnl": -0.3076557000000001,
          "trades": 72,
          "win_rate": 0.4027777777777778
        },
        "AKT_USDT": {
          "gross_pnl": -0.0005260999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0045261,
          "trades": 1,
          "win_rate": 0.0
        },
        "ALCH_USDT": {
          "gross_pnl": 0.06868509999999999,
          "pf": 0.3658928641176816,
          "severe_pnl": -0.06331490000000001,
          "trades": 33,
          "win_rate": 0.21212121212121213
        },
        "ALGO_USDT": {
          "gross_pnl": 0.010796000000000002,
          "pf": 0.0,
          "severe_pnl": -0.14920400000000006,
          "trades": 40,
          "win_rate": 0.0
        },
        "ALLO_USDT": {
          "gross_pnl": -0.08319759999999998,
          "pf": 0.0657616867826201,
          "severe_pnl": -0.7751976,
          "trades": 173,
          "win_rate": 0.12716763005780346
        },
        "ALPINE_USDT": {
          "gross_pnl": 0.0068451,
          "pf": 999,
          "severe_pnl": 0.0028450999999999997,
          "trades": 1,
          "win_rate": 1.0
        },
        "ALT_USDT": {
          "gross_pnl": 0.0076839000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0243161,
          "trades": 8,
          "win_rate": 0.0
        },
        "ANKR_USDT": {
          "gross_pnl": -0.0051752,
          "pf": 0.018175748358618644,
          "severe_pnl": -0.021175199999999998,
          "trades": 4,
          "win_rate": 0.25
        },
        "ANSEM_USDT": {
          "gross_pnl": 0.04151099999999998,
          "pf": 0.3401049308617704,
          "severe_pnl": -0.5464890000000003,
          "trades": 147,
          "win_rate": 0.2585034013605442
        },
        "ANTHROPIC_USDT": {
          "gross_pnl": 0.0028715000000000004,
          "pf": 0.0,
          "severe_pnl": -0.05312849999999999,
          "trades": 14,
          "win_rate": 0.0
        },
        "APE_USDT": {
          "gross_pnl": 0.012606299999999997,
          "pf": 0.037375069640438074,
          "severe_pnl": -0.19939370000000006,
          "trades": 53,
          "win_rate": 0.018867924528301886
        },
        "APR_USDT": {
          "gross_pnl": -0.0028382000000000004,
          "pf": 0.0,
          "severe_pnl": -0.006838200000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "APT_USDT": {
          "gross_pnl": 0.0154725,
          "pf": 0.0,
          "severe_pnl": -0.25252750000000007,
          "trades": 67,
          "win_rate": 0.0
        },
        "ARB_USDT": {
          "gross_pnl": -0.06351879999999999,
          "pf": 0.0024405987955686535,
          "severe_pnl": -0.6475188000000002,
          "trades": 146,
          "win_rate": 0.02054794520547945
        },
        "ARCSOL_USDT": {
          "gross_pnl": 0.0080153,
          "pf": 1.0021500843170321,
          "severe_pnl": 1.530000000000021e-05,
          "trades": 2,
          "win_rate": 0.5
        },
        "ARKK_USDT": {
          "gross_pnl": 0.011346699999999998,
          "pf": 1.9277576026390926,
          "severe_pnl": 0.0033466999999999985,
          "trades": 2,
          "win_rate": 0.5
        },
        "ARKM_USDT": {
          "gross_pnl": -0.0009834999999999993,
          "pf": 0.0,
          "severe_pnl": -0.06498350000000001,
          "trades": 16,
          "win_rate": 0.0
        },
        "ARX_USDT": {
          "gross_pnl": -0.001978499999999997,
          "pf": 0.004692174236802577,
          "severe_pnl": -0.15397850000000002,
          "trades": 38,
          "win_rate": 0.07894736842105263
        },
        "AR_USDT": {
          "gross_pnl": 0.0035207000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0324793,
          "trades": 9,
          "win_rate": 0.0
        },
        "ASTEROID_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "ASTER_USDT": {
          "gross_pnl": 0.010347599999999998,
          "pf": 0.04977765911845815,
          "severe_pnl": -0.1416524,
          "trades": 38,
          "win_rate": 0.02631578947368421
        },
        "ATH_USDT": {
          "gross_pnl": 0.007964699999999998,
          "pf": 0.9257779646761962,
          "severe_pnl": -3.530000000000113e-05,
          "trades": 2,
          "win_rate": 0.5
        },
        "ATOM_USDT": {
          "gross_pnl": 0.002076399999999999,
          "pf": 0.0,
          "severe_pnl": -0.15392360000000002,
          "trades": 39,
          "win_rate": 0.0
        },
        "AVAAI_USDT": {
          "gross_pnl": -0.0229756,
          "pf": 0.0,
          "severe_pnl": -0.038975600000000006,
          "trades": 4,
          "win_rate": 0.0
        },
        "AVAX_USDT": {
          "gross_pnl": -0.0020798,
          "pf": 0.0,
          "severe_pnl": -0.062079800000000004,
          "trades": 15,
          "win_rate": 0.0
        },
        "AVNT_USDT": {
          "gross_pnl": 0.012328799999999997,
          "pf": 0.0038288175393003114,
          "severe_pnl": -0.0516712,
          "trades": 16,
          "win_rate": 0.125
        },
        "AWE_USDT": {
          "gross_pnl": -0.0118921,
          "pf": 0.0,
          "severe_pnl": -0.0238921,
          "trades": 3,
          "win_rate": 0.0
        },
        "AXL_USDT": {
          "gross_pnl": 0.0020969,
          "pf": 0.0,
          "severe_pnl": -0.0019031,
          "trades": 1,
          "win_rate": 0.0
        },
        "AXS_USDT": {
          "gross_pnl": 0.009121200000000001,
          "pf": 0.0,
          "severe_pnl": -0.0428788,
          "trades": 13,
          "win_rate": 0.0
        },
        "A_USDT": {
          "gross_pnl": 0.0062028,
          "pf": 0.09533131417596218,
          "severe_pnl": -0.009797200000000002,
          "trades": 4,
          "win_rate": 0.25
        },
        "B2_USDT": {
          "gross_pnl": 0.012146,
          "pf": 1.0518502734569217,
          "severe_pnl": 0.0001460000000000003,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "B3_USDT": {
          "gross_pnl": 0.029503999999999996,
          "pf": 0.8510153250553876,
          "severe_pnl": -0.006496000000000004,
          "trades": 9,
          "win_rate": 0.4444444444444444
        },
        "BABY_USDT": {
          "gross_pnl": 0.0037097999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0202902,
          "trades": 6,
          "win_rate": 0.0
        },
        "BANANAS31_USDT": {
          "gross_pnl": -0.0037824000000000004,
          "pf": 0.0,
          "severe_pnl": -0.015782400000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "BANANA_USDT": {
          "gross_pnl": -0.0029471000000000002,
          "pf": 0.0,
          "severe_pnl": -0.010947100000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "BAND_USDT": {
          "gross_pnl": 0.0135884,
          "pf": 1.3971000000000002,
          "severe_pnl": 0.001588400000000001,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "BANK_USDT": {
          "gross_pnl": -0.1769879000000001,
          "pf": 0.16067364998789507,
          "severe_pnl": -0.49298790000000003,
          "trades": 79,
          "win_rate": 0.24050632911392406
        },
        "BAN_USDT": {
          "gross_pnl": -0.00022579999999999953,
          "pf": 0.0,
          "severe_pnl": -0.0162258,
          "trades": 4,
          "win_rate": 0.0
        },
        "BASED_USDT": {
          "gross_pnl": 0.021379899999999997,
          "pf": 0.05452072487453955,
          "severe_pnl": -0.0786201,
          "trades": 25,
          "win_rate": 0.12
        },
        "BAS_USDT": {
          "gross_pnl": -0.0046061999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0166062,
          "trades": 3,
          "win_rate": 0.0
        },
        "BAT_USDT": {
          "gross_pnl": 0.0012002000000000004,
          "pf": 0.0,
          "severe_pnl": -0.030799800000000002,
          "trades": 8,
          "win_rate": 0.0
        },
        "BCH_USDT": {
          "gross_pnl": 0.007056999999999997,
          "pf": 0.0020523003865032608,
          "severe_pnl": -0.2249430000000001,
          "trades": 58,
          "win_rate": 0.017241379310344827
        },
        "BEAT_USDT": {
          "gross_pnl": -0.15903650000000005,
          "pf": 0.020331964146586848,
          "severe_pnl": -0.9390365000000005,
          "trades": 195,
          "win_rate": 0.06666666666666667
        },
        "BERA_USDT": {
          "gross_pnl": 0.0010447,
          "pf": 0.0,
          "severe_pnl": -0.014955300000000001,
          "trades": 4,
          "win_rate": 0.0
        },
        "BIANRENSHENG_USDT": {
          "gross_pnl": -0.0011056,
          "pf": 0.0,
          "severe_pnl": -0.0131056,
          "trades": 3,
          "win_rate": 0.0
        },
        "BICO_USDT": {
          "gross_pnl": 0.0023202000000000006,
          "pf": 0.0,
          "severe_pnl": -0.0376798,
          "trades": 10,
          "win_rate": 0.0
        },
        "BIGTIME_USDT": {
          "gross_pnl": -0.0002939,
          "pf": 0.0,
          "severe_pnl": -0.0042939,
          "trades": 1,
          "win_rate": 0.0
        },
        "BILL_USDT": {
          "gross_pnl": -0.11282130000000004,
          "pf": 0.05289557015884076,
          "severe_pnl": -0.7568212999999999,
          "trades": 161,
          "win_rate": 0.10559006211180125
        },
        "BIO_USDT": {
          "gross_pnl": 0.0017724000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0022275999999999997,
          "trades": 1,
          "win_rate": 0.0
        },
        "BLAST_USDT": {
          "gross_pnl": 0.11356719999999998,
          "pf": 0.9835814539537666,
          "severe_pnl": -0.002432800000000004,
          "trades": 29,
          "win_rate": 0.4482758620689655
        },
        "BLEND_USDT": {
          "gross_pnl": 0.014409700000000001,
          "pf": 0.29941129165291985,
          "severe_pnl": -0.0135903,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "BLESS_USDT": {
          "gross_pnl": 0.044799999999999986,
          "pf": 0.13204861982396107,
          "severe_pnl": -0.14320000000000002,
          "trades": 47,
          "win_rate": 0.23404255319148937
        },
        "BLUAI_USDT": {
          "gross_pnl": -0.0812524,
          "pf": 0.11046300503014995,
          "severe_pnl": -0.1092524,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "BLUR_USDT": {
          "gross_pnl": 0.0024798999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0095201,
          "trades": 3,
          "win_rate": 0.0
        },
        "BNB_USDT": {
          "gross_pnl": 0.0009035999999999996,
          "pf": 0.0,
          "severe_pnl": -0.09109640000000002,
          "trades": 23,
          "win_rate": 0.0
        },
        "BRETT_USDT": {
          "gross_pnl": 0.04018630000000001,
          "pf": 0.46018188555050626,
          "severe_pnl": -0.019813700000000004,
          "trades": 15,
          "win_rate": 0.2
        },
        "BREV_USDT": {
          "gross_pnl": 0.0112306,
          "pf": 0.34309642236471505,
          "severe_pnl": -0.0087694,
          "trades": 5,
          "win_rate": 0.2
        },
        "BSB_USDT": {
          "gross_pnl": 0.04983050000000004,
          "pf": 0.14548514291104608,
          "severe_pnl": -0.5661695000000002,
          "trades": 154,
          "win_rate": 0.16883116883116883
        },
        "BSV_USDT": {
          "gross_pnl": -0.004123399999999999,
          "pf": 0.038308601998480414,
          "severe_pnl": -0.040123400000000004,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "BTW_USDT": {
          "gross_pnl": -0.003041500000000005,
          "pf": 0.06556103210431659,
          "severe_pnl": -0.15104149999999997,
          "trades": 37,
          "win_rate": 0.10810810810810811
        },
        "BUILDONBOB_USDT": {
          "gross_pnl": 0.018845099999999997,
          "pf": 1.6623798879437974,
          "severe_pnl": 0.006845099999999998,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "BULLA_USDT": {
          "gross_pnl": -0.040789399999999996,
          "pf": 0.1690330955935773,
          "severe_pnl": -0.12878940000000003,
          "trades": 22,
          "win_rate": 0.13636363636363635
        },
        "CAKE_USDT": {
          "gross_pnl": 0.007701,
          "pf": 0.009121308146150997,
          "severe_pnl": -0.028298999999999998,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "CAP_USDT": {
          "gross_pnl": -0.014687299999999992,
          "pf": 0.033167764197719156,
          "severe_pnl": -0.21868730000000006,
          "trades": 51,
          "win_rate": 0.09803921568627451
        },
        "CARV_USDT": {
          "gross_pnl": 0.0092365,
          "pf": 999,
          "severe_pnl": 0.0052365,
          "trades": 1,
          "win_rate": 1.0
        },
        "CASHCAT_USDT": {
          "gross_pnl": 0.0914976,
          "pf": 0.9226258999025361,
          "severe_pnl": -0.008502399999999986,
          "trades": 25,
          "win_rate": 0.36
        },
        "CATI_USDT": {
          "gross_pnl": 0.0026976,
          "pf": 0.0,
          "severe_pnl": -0.0053024,
          "trades": 2,
          "win_rate": 0.0
        },
        "CC_USDT": {
          "gross_pnl": -0.0078279,
          "pf": 0.0,
          "severe_pnl": -0.0638279,
          "trades": 14,
          "win_rate": 0.0
        },
        "CFX_USDT": {
          "gross_pnl": 0.0034093,
          "pf": 0.08392348240728666,
          "severe_pnl": -0.0245907,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "CHEEMS_USDT": {
          "gross_pnl": -0.0021964,
          "pf": 0.0,
          "severe_pnl": -0.0061963999999999995,
          "trades": 1,
          "win_rate": 0.0
        },
        "CHIP_USDT": {
          "gross_pnl": -0.013146300000000001,
          "pf": 0.0,
          "severe_pnl": -0.1611463,
          "trades": 37,
          "win_rate": 0.0
        },
        "CHR_USDT": {
          "gross_pnl": 0.0022531,
          "pf": 0.004402451481103157,
          "severe_pnl": -0.0097469,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "CHZ_USDT": {
          "gross_pnl": 0.004489000000000002,
          "pf": 0.0,
          "severe_pnl": -0.11151100000000001,
          "trades": 29,
          "win_rate": 0.0
        },
        "CKB_USDT": {
          "gross_pnl": 0.0010741000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0069259000000000005,
          "trades": 2,
          "win_rate": 0.0
        },
        "CLO_USDT": {
          "gross_pnl": -0.0123319,
          "pf": 0.2360218634639083,
          "severe_pnl": -0.028331899999999997,
          "trades": 4,
          "win_rate": 0.5
        },
        "COAI_USDT": {
          "gross_pnl": -0.0039026999999999985,
          "pf": 0.01669349439817275,
          "severe_pnl": -0.0799027,
          "trades": 19,
          "win_rate": 0.05263157894736842
        },
        "COLLECT_USDT": {
          "gross_pnl": 0.020727199999999998,
          "pf": 0.10099094690482016,
          "severe_pnl": -0.0352728,
          "trades": 14,
          "win_rate": 0.21428571428571427
        },
        "COMP_USDT": {
          "gross_pnl": 0.0017801,
          "pf": 0.0,
          "severe_pnl": -0.0062199,
          "trades": 2,
          "win_rate": 0.0
        },
        "COTI_USDT": {
          "gross_pnl": 0.0026076,
          "pf": 0.0,
          "severe_pnl": -0.0013924000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "CROSS_USDT": {
          "gross_pnl": 0.0041578,
          "pf": 0.0,
          "severe_pnl": -0.0118422,
          "trades": 4,
          "win_rate": 0.0
        },
        "CRO_USDT": {
          "gross_pnl": -0.027606099999999998,
          "pf": 0.10024172144767214,
          "severe_pnl": -0.1436061,
          "trades": 29,
          "win_rate": 0.10344827586206896
        },
        "CRV_USDT": {
          "gross_pnl": -0.026287199999999993,
          "pf": 0.0,
          "severe_pnl": -0.27828720000000007,
          "trades": 63,
          "win_rate": 0.0
        },
        "CTC_USDT": {
          "gross_pnl": 0.008405200000000002,
          "pf": 0.0,
          "severe_pnl": -0.027594799999999996,
          "trades": 9,
          "win_rate": 0.0
        },
        "CVX_USDT": {
          "gross_pnl": 0.0063884000000000015,
          "pf": 0.04641721303801384,
          "severe_pnl": -0.033611600000000005,
          "trades": 10,
          "win_rate": 0.1
        },
        "CYS_USDT": {
          "gross_pnl": 0.015928299999999996,
          "pf": 0.1130262517154367,
          "severe_pnl": -0.0400717,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "DASH_USDT": {
          "gross_pnl": -0.0107401,
          "pf": 0.0,
          "severe_pnl": -0.2947401000000001,
          "trades": 71,
          "win_rate": 0.0
        },
        "DEEP_USDT": {
          "gross_pnl": 0.0005455999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0074544,
          "trades": 2,
          "win_rate": 0.0
        },
        "DEXE_USDT": {
          "gross_pnl": 0.07544299999999998,
          "pf": 0.2023422727813485,
          "severe_pnl": -0.44855700000000004,
          "trades": 131,
          "win_rate": 0.20610687022900764
        },
        "DODO_USDT": {
          "gross_pnl": 0.033315000000000025,
          "pf": 0.31570166668346766,
          "severe_pnl": -0.29868500000000003,
          "trades": 83,
          "win_rate": 0.20481927710843373
        },
        "DOGE_USDT": {
          "gross_pnl": -0.005354299999999999,
          "pf": 0.0,
          "severe_pnl": -0.28535430000000006,
          "trades": 70,
          "win_rate": 0.0
        },
        "DOGS_USDT": {
          "gross_pnl": 0.0027630999999999997,
          "pf": 0.0,
          "severe_pnl": -0.021236900000000003,
          "trades": 6,
          "win_rate": 0.0
        },
        "DOT_USDT": {
          "gross_pnl": 0.04747969999999999,
          "pf": 0.001838409439034441,
          "severe_pnl": -0.3245203000000001,
          "trades": 93,
          "win_rate": 0.010752688172043012
        },
        "DRAM_USDT": {
          "gross_pnl": 0.004782999999999998,
          "pf": 0.05877922886228706,
          "severe_pnl": -0.18721700000000008,
          "trades": 48,
          "win_rate": 0.10416666666666667
        },
        "DUSK_USDT": {
          "gross_pnl": 0.0002803,
          "pf": 0.0,
          "severe_pnl": -0.0037197000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "DYDX_USDT": {
          "gross_pnl": -0.0041562000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0401562,
          "trades": 9,
          "win_rate": 0.0
        },
        "EDEN_USDT": {
          "gross_pnl": 0.0068441000000000005,
          "pf": 0.33493711705901325,
          "severe_pnl": -0.0051559,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "EDGE_USDT": {
          "gross_pnl": 0.06081669999999999,
          "pf": 0.1419829984967127,
          "severe_pnl": -0.3071833,
          "trades": 92,
          "win_rate": 0.13043478260869565
        },
        "EDU_USDT": {
          "gross_pnl": 0.0034088000000000005,
          "pf": 0.02030115146147033,
          "severe_pnl": -0.0165912,
          "trades": 5,
          "win_rate": 0.2
        },
        "EGLD_USDT": {
          "gross_pnl": 0.018168899999999988,
          "pf": 0.035417682495241985,
          "severe_pnl": -0.2698311,
          "trades": 72,
          "win_rate": 0.06944444444444445
        },
        "EIGEN_USDT": {
          "gross_pnl": -0.027347400000000004,
          "pf": 0.003977412780023513,
          "severe_pnl": -0.37134740000000005,
          "trades": 86,
          "win_rate": 0.011627906976744186
        },
        "ELSA_USDT": {
          "gross_pnl": 0.0388873,
          "pf": 1.5940093297323839,
          "severe_pnl": 0.010887299999999999,
          "trades": 7,
          "win_rate": 0.42857142857142855
        },
        "ENA_USDT": {
          "gross_pnl": 0.01865569999999999,
          "pf": 0.0,
          "severe_pnl": -0.26134430000000003,
          "trades": 70,
          "win_rate": 0.0
        },
        "ENJ_USDT": {
          "gross_pnl": 0.010458,
          "pf": 0.1021486668696446,
          "severe_pnl": -0.049542,
          "trades": 15,
          "win_rate": 0.13333333333333333
        },
        "ENSO_USDT": {
          "gross_pnl": -0.0013173999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0133174,
          "trades": 3,
          "win_rate": 0.0
        },
        "ENS_USDT": {
          "gross_pnl": 0.012385299999999998,
          "pf": 0.001086659769520357,
          "severe_pnl": -0.05561470000000001,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "EPIC_USDT": {
          "gross_pnl": -0.0024971999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0064972,
          "trades": 1,
          "win_rate": 0.0
        },
        "ERA_USDT": {
          "gross_pnl": 0.0011718,
          "pf": 0.0,
          "severe_pnl": -0.0028282000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "ESPORTS_USDT": {
          "gross_pnl": -0.020788600000000063,
          "pf": 0.35068468961324284,
          "severe_pnl": -0.4647886000000001,
          "trades": 111,
          "win_rate": 0.3153153153153153
        },
        "ESP_USDT": {
          "gross_pnl": 0.0068547,
          "pf": 0.0,
          "severe_pnl": -0.0011453000000000006,
          "trades": 2,
          "win_rate": 0.0
        },
        "ETC_USDT": {
          "gross_pnl": -0.001701,
          "pf": 0.0,
          "severe_pnl": -0.08970100000000002,
          "trades": 22,
          "win_rate": 0.0
        },
        "ETHFI_USDT": {
          "gross_pnl": -0.020358899999999996,
          "pf": 0.0076871164186996105,
          "severe_pnl": -0.3843589,
          "trades": 91,
          "win_rate": 0.02197802197802198
        },
        "ETH_USDT": {
          "gross_pnl": 0.004922499999999999,
          "pf": 0.0,
          "severe_pnl": -0.29107749999999993,
          "trades": 74,
          "win_rate": 0.0
        },
        "EUL_USDT": {
          "gross_pnl": 0.0062296,
          "pf": 0.40456731577708266,
          "severe_pnl": -0.0017704,
          "trades": 2,
          "win_rate": 0.5
        },
        "EVAA_USDT": {
          "gross_pnl": -0.08613679999999997,
          "pf": 0.2909864877376224,
          "severe_pnl": -0.3821368000000001,
          "trades": 74,
          "win_rate": 0.25675675675675674
        },
        "EWY_USDT": {
          "gross_pnl": 0.009884400000000002,
          "pf": 0.005922205469204496,
          "severe_pnl": -0.2821156,
          "trades": 73,
          "win_rate": 0.0410958904109589
        },
        "FET_USDT": {
          "gross_pnl": -0.008018700000000004,
          "pf": 0.0,
          "severe_pnl": -0.27201870000000006,
          "trades": 66,
          "win_rate": 0.0
        },
        "FF_USDT": {
          "gross_pnl": 0.0130884,
          "pf": 0.05237253737937127,
          "severe_pnl": -0.054911600000000005,
          "trades": 17,
          "win_rate": 0.11764705882352941
        },
        "FHE_USDT": {
          "gross_pnl": 0.008489199999999999,
          "pf": 0.058821340314420885,
          "severe_pnl": -0.1315108,
          "trades": 35,
          "win_rate": 0.17142857142857143
        },
        "FIGHT_USDT": {
          "gross_pnl": -0.00096,
          "pf": 0.0,
          "severe_pnl": -0.00496,
          "trades": 1,
          "win_rate": 0.0
        },
        "FILECOIN_USDT": {
          "gross_pnl": 0.012834400000000003,
          "pf": 0.005672307823245617,
          "severe_pnl": -0.11916560000000001,
          "trades": 33,
          "win_rate": 0.030303030303030304
        },
        "FLOCK_USDT": {
          "gross_pnl": -0.0141884,
          "pf": 0.0,
          "severe_pnl": -0.0421884,
          "trades": 7,
          "win_rate": 0.0
        },
        "FLOKI_USDT": {
          "gross_pnl": 0.0026198,
          "pf": 0.0011639479446082033,
          "severe_pnl": -0.10538020000000001,
          "trades": 27,
          "win_rate": 0.037037037037037035
        },
        "FLOW_USDT": {
          "gross_pnl": -0.0003274,
          "pf": 0.0,
          "severe_pnl": -0.0083274,
          "trades": 2,
          "win_rate": 0.0
        },
        "FLR_USDT": {
          "gross_pnl": 0.0015198,
          "pf": 0.0,
          "severe_pnl": -0.0024802,
          "trades": 1,
          "win_rate": 0.0
        },
        "FOGO_USDT": {
          "gross_pnl": 0.0154357,
          "pf": 0.42630440170682526,
          "severe_pnl": -0.0085643,
          "trades": 6,
          "win_rate": 0.3333333333333333
        },
        "FOLKS_USDT": {
          "gross_pnl": 0.0223451,
          "pf": 0.16038692956941084,
          "severe_pnl": -0.1456549,
          "trades": 42,
          "win_rate": 0.16666666666666666
        },
        "FORM_USDT": {
          "gross_pnl": 0.00046699999999999997,
          "pf": 0.0,
          "severe_pnl": -0.007533,
          "trades": 2,
          "win_rate": 0.0
        },
        "FRAX_USDT": {
          "gross_pnl": 0.00041050000000000006,
          "pf": 0.0,
          "severe_pnl": -0.0035895,
          "trades": 1,
          "win_rate": 0.0
        },
        "F_USDT": {
          "gross_pnl": -0.0021887,
          "pf": 0.0,
          "severe_pnl": -0.0101887,
          "trades": 2,
          "win_rate": 0.0
        },
        "GALA_USDT": {
          "gross_pnl": 0.026280400000000002,
          "pf": 0.006777590139891928,
          "severe_pnl": -0.28971959999999997,
          "trades": 79,
          "win_rate": 0.012658227848101266
        },
        "GAS_USDT": {
          "gross_pnl": 0.0093868,
          "pf": 13.305235137533298,
          "severe_pnl": 0.001386800000000001,
          "trades": 2,
          "win_rate": 0.5
        },
        "GENIUS_USDT": {
          "gross_pnl": -0.0022413,
          "pf": 0.0,
          "severe_pnl": -0.014241300000000002,
          "trades": 3,
          "win_rate": 0.0
        },
        "GIGGLE_USDT": {
          "gross_pnl": -0.004544,
          "pf": 0.0,
          "severe_pnl": -0.016544,
          "trades": 3,
          "win_rate": 0.0
        },
        "GLM_USDT": {
          "gross_pnl": 0.0029771,
          "pf": 0.0,
          "severe_pnl": -0.0090229,
          "trades": 3,
          "win_rate": 0.0
        },
        "GOAT_USDT": {
          "gross_pnl": 0.0045147,
          "pf": 999,
          "severe_pnl": 0.0005146999999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "GPS_USDT": {
          "gross_pnl": 0.0078478,
          "pf": 0.02421836589762733,
          "severe_pnl": -0.032152200000000006,
          "trades": 10,
          "win_rate": 0.1
        },
        "GRAM_USDT": {
          "gross_pnl": 0.0008893000000000006,
          "pf": 0.004289837043675127,
          "severe_pnl": -0.1351107,
          "trades": 34,
          "win_rate": 0.029411764705882353
        },
        "GRASS_USDT": {
          "gross_pnl": 0.017284400000000002,
          "pf": 0.0,
          "severe_pnl": -0.05871559999999999,
          "trades": 19,
          "win_rate": 0.0
        },
        "GRT_USDT": {
          "gross_pnl": 0.0022806000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0297194,
          "trades": 8,
          "win_rate": 0.0
        },
        "GUA_USDT": {
          "gross_pnl": -0.0009440999999999981,
          "pf": 0.3069979601998041,
          "severe_pnl": -0.0129441,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "GUN_USDT": {
          "gross_pnl": -0.0170608,
          "pf": 0.03467900058703417,
          "severe_pnl": -0.05706079999999999,
          "trades": 10,
          "win_rate": 0.1
        },
        "G_USDT": {
          "gross_pnl": 0.006926799999999999,
          "pf": 0.4470863890510146,
          "severe_pnl": -0.0130732,
          "trades": 5,
          "win_rate": 0.2
        },
        "HBAR_USDT": {
          "gross_pnl": 0.003055800000000001,
          "pf": 0.0,
          "severe_pnl": -0.1849442,
          "trades": 47,
          "win_rate": 0.0
        },
        "HEI_USDT": {
          "gross_pnl": 0.018042699999999988,
          "pf": 0.10235283148343376,
          "severe_pnl": -0.1819573,
          "trades": 50,
          "win_rate": 0.22
        },
        "HIGH_USDT": {
          "gross_pnl": -0.022349899999999995,
          "pf": 0.010388328083237879,
          "severe_pnl": -0.06634989999999999,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "HK50_USDT": {
          "gross_pnl": -0.001959899999999999,
          "pf": 0.0,
          "severe_pnl": -0.0379599,
          "trades": 9,
          "win_rate": 0.0
        },
        "HMSTR_USDT": {
          "gross_pnl": -0.006356100000000003,
          "pf": 0.053768235555461875,
          "severe_pnl": -0.0583561,
          "trades": 13,
          "win_rate": 0.15384615384615385
        },
        "HNT_USDT": {
          "gross_pnl": 0.005732299999999999,
          "pf": 0.0,
          "severe_pnl": -0.0182677,
          "trades": 6,
          "win_rate": 0.0
        },
        "HOLO_USDT": {
          "gross_pnl": 0.0027397000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0172603,
          "trades": 5,
          "win_rate": 0.0
        },
        "HOME_USDT": {
          "gross_pnl": -0.0758274,
          "pf": 0.11031141560432188,
          "severe_pnl": -0.23182740000000004,
          "trades": 39,
          "win_rate": 0.15384615384615385
        },
        "HOT_USDT": {
          "gross_pnl": 0.0158505,
          "pf": 1.8104268395352752,
          "severe_pnl": 0.0038505000000000006,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "HYPE_USDT": {
          "gross_pnl": 0.009259499999999997,
          "pf": 0.0010622411652433138,
          "severe_pnl": -0.15874050000000003,
          "trades": 42,
          "win_rate": 0.023809523809523808
        },
        "ICNT_USDT": {
          "gross_pnl": 0.0012706,
          "pf": 0.0,
          "severe_pnl": -0.0027294,
          "trades": 1,
          "win_rate": 0.0
        },
        "ICP_USDT": {
          "gross_pnl": -0.0022340999999999984,
          "pf": 0.0,
          "severe_pnl": -0.29423409999999994,
          "trades": 73,
          "win_rate": 0.0
        },
        "ICX_USDT": {
          "gross_pnl": -0.0025437999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0105438,
          "trades": 2,
          "win_rate": 0.0
        },
        "ID_USDT": {
          "gross_pnl": -0.0002511,
          "pf": 0.0,
          "severe_pnl": -0.0162511,
          "trades": 4,
          "win_rate": 0.0
        },
        "IMX_USDT": {
          "gross_pnl": 0.0044754,
          "pf": 0.0,
          "severe_pnl": -0.019524600000000003,
          "trades": 6,
          "win_rate": 0.0
        },
        "INDA_USDT": {
          "gross_pnl": 0.021539099999999995,
          "pf": 0.6814740030287734,
          "severe_pnl": -0.0024609000000000002,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "INJ_USDT": {
          "gross_pnl": 0.03120070000000002,
          "pf": 0.0,
          "severe_pnl": -0.37679929999999984,
          "trades": 102,
          "win_rate": 0.0
        },
        "INTW_USDT": {
          "gross_pnl": -0.011330600000000001,
          "pf": 0.0,
          "severe_pnl": -0.019330600000000003,
          "trades": 2,
          "win_rate": 0.0
        },
        "INX_USDT": {
          "gross_pnl": 0.0013262999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0026737,
          "trades": 1,
          "win_rate": 0.0
        },
        "IN_USDT": {
          "gross_pnl": 0.0022024,
          "pf": 0.05456443038387528,
          "severe_pnl": -0.0057976,
          "trades": 2,
          "win_rate": 0.5
        },
        "IOST_USDT": {
          "gross_pnl": 0.0008939,
          "pf": 0.0,
          "severe_pnl": -0.0031061,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTA_USDT": {
          "gross_pnl": 0.0043,
          "pf": 999,
          "severe_pnl": 0.0002999999999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "IOTX_USDT": {
          "gross_pnl": 0.0029252,
          "pf": 0.0,
          "severe_pnl": -0.0010747999999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "IRYS_USDT": {
          "gross_pnl": 0.0153257,
          "pf": 999,
          "severe_pnl": 0.0113257,
          "trades": 1,
          "win_rate": 1.0
        },
        "IWM_USDT": {
          "gross_pnl": 0.0010398,
          "pf": 0.0,
          "severe_pnl": -0.0029602,
          "trades": 1,
          "win_rate": 0.0
        },
        "JASMY_USDT": {
          "gross_pnl": -0.0006285999999999998,
          "pf": 0.010614514395882563,
          "severe_pnl": -0.1646286,
          "trades": 41,
          "win_rate": 0.024390243902439025
        },
        "JCT_USDT": {
          "gross_pnl": 0.0074515999999999975,
          "pf": 0.08751416016729961,
          "severe_pnl": -0.06854840000000001,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "JP225_USDT": {
          "gross_pnl": 0.00026669999999999906,
          "pf": 0.0,
          "severe_pnl": -0.031733300000000006,
          "trades": 8,
          "win_rate": 0.0
        },
        "JST_USDT": {
          "gross_pnl": -0.006655399999999999,
          "pf": 0.0,
          "severe_pnl": -0.038655400000000006,
          "trades": 8,
          "win_rate": 0.0
        },
        "JTO_USDT": {
          "gross_pnl": 0.021084300000000007,
          "pf": 0.008251275773873301,
          "severe_pnl": -0.2509157,
          "trades": 68,
          "win_rate": 0.04411764705882353
        },
        "JUP_USDT": {
          "gross_pnl": 0.0187737,
          "pf": 0.003720751283264166,
          "severe_pnl": -0.3972263000000002,
          "trades": 104,
          "win_rate": 0.009615384615384616
        },
        "KAIA_USDT": {
          "gross_pnl": 0.0031938,
          "pf": 0.0,
          "severe_pnl": -0.0168062,
          "trades": 5,
          "win_rate": 0.0
        },
        "KAITO_USDT": {
          "gross_pnl": -0.013238599999999994,
          "pf": 0.055889446967402646,
          "severe_pnl": -0.2612386,
          "trades": 62,
          "win_rate": 0.08064516129032258
        },
        "KAS_USDT": {
          "gross_pnl": 0.0120766,
          "pf": 0.06441480574548628,
          "severe_pnl": -0.10392340000000004,
          "trades": 29,
          "win_rate": 0.034482758620689655
        },
        "KAT_USDT": {
          "gross_pnl": -0.0040649,
          "pf": 0.11115475907247464,
          "severe_pnl": -0.0160649,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "KITE_USDT": {
          "gross_pnl": -0.0361963,
          "pf": 0.011350543259632636,
          "severe_pnl": -0.2641963,
          "trades": 57,
          "win_rate": 0.017543859649122806
        },
        "KMNO_USDT": {
          "gross_pnl": -0.0010892999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0090893,
          "trades": 2,
          "win_rate": 0.0
        },
        "KORU_USDT": {
          "gross_pnl": -0.027824400000000006,
          "pf": 0.09992726921291233,
          "severe_pnl": -0.32782439999999996,
          "trades": 75,
          "win_rate": 0.21333333333333335
        },
        "KSM_USDT": {
          "gross_pnl": 0.0064638000000000004,
          "pf": 0.5842039733665351,
          "severe_pnl": -0.0015361999999999997,
          "trades": 2,
          "win_rate": 0.5
        },
        "KSTR_USDT": {
          "gross_pnl": 0.00040419999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0035958,
          "trades": 1,
          "win_rate": 0.0
        },
        "LAB_USDT": {
          "gross_pnl": -0.09294439999999998,
          "pf": 0.33254797384978735,
          "severe_pnl": -0.3369444,
          "trades": 61,
          "win_rate": 0.29508196721311475
        },
        "LDO_USDT": {
          "gross_pnl": 0.031072000000000013,
          "pf": 0.020291428893984064,
          "severe_pnl": -0.4009280000000001,
          "trades": 108,
          "win_rate": 0.027777777777777776
        },
        "LEAD_USDT": {
          "gross_pnl": -0.0017280999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0177281,
          "trades": 4,
          "win_rate": 0.0
        },
        "LIGHT_USDT": {
          "gross_pnl": 0.0024217,
          "pf": 0.0,
          "severe_pnl": -0.0415783,
          "trades": 11,
          "win_rate": 0.0
        },
        "LINEA_USDT": {
          "gross_pnl": -0.004116000000000001,
          "pf": 0.0,
          "severe_pnl": -0.032116,
          "trades": 7,
          "win_rate": 0.0
        },
        "LINK_USDT": {
          "gross_pnl": -0.0036579999999999994,
          "pf": 0.0,
          "severe_pnl": -0.22365799999999997,
          "trades": 55,
          "win_rate": 0.0
        },
        "LIT_USDT": {
          "gross_pnl": -0.052508699999999985,
          "pf": 0.014885507533957546,
          "severe_pnl": -0.7685086999999997,
          "trades": 179,
          "win_rate": 0.0335195530726257
        },
        "LRC_USDT": {
          "gross_pnl": -0.0025427000000000023,
          "pf": 0.1968645019210339,
          "severe_pnl": -0.0745427,
          "trades": 18,
          "win_rate": 0.16666666666666666
        },
        "LTC_USDT": {
          "gross_pnl": 0.0006857000000000007,
          "pf": 0.0,
          "severe_pnl": -0.15131430000000004,
          "trades": 38,
          "win_rate": 0.0
        },
        "LUMIA_USDT": {
          "gross_pnl": 0.0588217,
          "pf": 0.8321079539880778,
          "severe_pnl": -0.013178300000000009,
          "trades": 18,
          "win_rate": 0.2777777777777778
        },
        "LUNANEW_USDT": {
          "gross_pnl": 0.0008573,
          "pf": 0.0,
          "severe_pnl": -0.0031427,
          "trades": 1,
          "win_rate": 0.0
        },
        "LUNC_USDT": {
          "gross_pnl": 0.010508700000000003,
          "pf": 0.0,
          "severe_pnl": -0.0614913,
          "trades": 18,
          "win_rate": 0.0
        },
        "MAGMA_USDT": {
          "gross_pnl": -0.0247645,
          "pf": 0.15975478965231085,
          "severe_pnl": -0.3047645,
          "trades": 70,
          "win_rate": 0.17142857142857143
        },
        "MANA_USDT": {
          "gross_pnl": 0.006789900000000001,
          "pf": 0.0008729358933559546,
          "severe_pnl": -0.0452101,
          "trades": 13,
          "win_rate": 0.15384615384615385
        },
        "MANTA_USDT": {
          "gross_pnl": 0.0038989999999999997,
          "pf": 0.01662707061187357,
          "severe_pnl": -0.060101,
          "trades": 16,
          "win_rate": 0.0625
        },
        "MANTRA_USDT": {
          "gross_pnl": 0.016911799999999994,
          "pf": 0.3111733776614587,
          "severe_pnl": -0.06708820000000001,
          "trades": 21,
          "win_rate": 0.23809523809523808
        },
        "MASK_USDT": {
          "gross_pnl": 0.0005013,
          "pf": 0.0,
          "severe_pnl": -0.0074987000000000005,
          "trades": 2,
          "win_rate": 0.0
        },
        "MAV_USDT": {
          "gross_pnl": 0.0060965,
          "pf": 0.09590104071572031,
          "severe_pnl": -0.009903499999999999,
          "trades": 4,
          "win_rate": 0.25
        },
        "MEGA_USDT": {
          "gross_pnl": -0.0065346,
          "pf": 0.0,
          "severe_pnl": -0.03853460000000001,
          "trades": 8,
          "win_rate": 0.0
        },
        "MEME_USDT": {
          "gross_pnl": 0.0058989,
          "pf": 0.0,
          "severe_pnl": -0.0181011,
          "trades": 6,
          "win_rate": 0.0
        },
        "MERL_USDT": {
          "gross_pnl": 0.023436100000000005,
          "pf": 0.10091939382464386,
          "severe_pnl": -0.0365639,
          "trades": 15,
          "win_rate": 0.13333333333333333
        },
        "MET_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "MINA_USDT": {
          "gross_pnl": 0.0027003,
          "pf": 0.0,
          "severe_pnl": -0.0052997,
          "trades": 2,
          "win_rate": 0.0
        },
        "MITO_USDT": {
          "gross_pnl": -0.0021331,
          "pf": 0.0,
          "severe_pnl": -0.0101331,
          "trades": 2,
          "win_rate": 0.0
        },
        "MMT_USDT": {
          "gross_pnl": 0.032449099999999995,
          "pf": 0.1439523700067378,
          "severe_pnl": -0.22755090000000003,
          "trades": 65,
          "win_rate": 0.18461538461538463
        },
        "MNT_USDT": {
          "gross_pnl": 0.0013816000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0346184,
          "trades": 9,
          "win_rate": 0.0
        },
        "MONAD_USDT": {
          "gross_pnl": -0.011519500000000002,
          "pf": 0.0,
          "severe_pnl": -0.08751950000000001,
          "trades": 19,
          "win_rate": 0.0
        },
        "MOODENG_USDT": {
          "gross_pnl": 0.0009005,
          "pf": 0.0,
          "severe_pnl": -0.0030995,
          "trades": 1,
          "win_rate": 0.0
        },
        "MORPHO_USDT": {
          "gross_pnl": 0.0226903,
          "pf": 0.09813827044375414,
          "severe_pnl": -0.10930970000000004,
          "trades": 33,
          "win_rate": 0.09090909090909091
        },
        "MOVE_USDT": {
          "gross_pnl": 0.003637800000000001,
          "pf": 0.02920184794061418,
          "severe_pnl": -0.0203622,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "MOVR_USDT": {
          "gross_pnl": 0.0014545,
          "pf": 0.0,
          "severe_pnl": -0.0025455,
          "trades": 1,
          "win_rate": 0.0
        },
        "MSTU_USDT": {
          "gross_pnl": 0.015674399999999998,
          "pf": 0.2922594797869006,
          "severe_pnl": -0.020325600000000003,
          "trades": 9,
          "win_rate": 0.3333333333333333
        },
        "MUBARAK_USDT": {
          "gross_pnl": -0.0081845,
          "pf": 0.0,
          "severe_pnl": -0.012184500000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "MUU_USDT": {
          "gross_pnl": -0.0075694,
          "pf": 0.0,
          "severe_pnl": -0.023569399999999997,
          "trades": 4,
          "win_rate": 0.0
        },
        "MVLL_USDT": {
          "gross_pnl": -0.019601999999999987,
          "pf": 0.16529354167146473,
          "severe_pnl": -0.11960199999999999,
          "trades": 25,
          "win_rate": 0.24
        },
        "MYX_USDT": {
          "gross_pnl": -0.004309500000000002,
          "pf": 0.06910731492236791,
          "severe_pnl": -0.4043095000000003,
          "trades": 100,
          "win_rate": 0.12
        },
        "M_USDT": {
          "gross_pnl": -0.028519100000000002,
          "pf": 0.0,
          "severe_pnl": -0.0325191,
          "trades": 1,
          "win_rate": 0.0
        },
        "NAORIS_USDT": {
          "gross_pnl": 0.012673199999999999,
          "pf": 0.16053618108837547,
          "severe_pnl": -0.0633268,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "NEAR_USDT": {
          "gross_pnl": 0.014470600000000004,
          "pf": 0.016086780208554943,
          "severe_pnl": -0.5175294,
          "trades": 133,
          "win_rate": 0.015037593984962405
        },
        "NEIROCTO_USDT": {
          "gross_pnl": 0.0010076,
          "pf": 0.0,
          "severe_pnl": -0.0029924,
          "trades": 1,
          "win_rate": 0.0
        },
        "NEO_USDT": {
          "gross_pnl": 0.004627200000000001,
          "pf": 999,
          "severe_pnl": 0.0006272000000000005,
          "trades": 1,
          "win_rate": 1.0
        },
        "NES_USDT": {
          "gross_pnl": 0.0129419,
          "pf": 0.03146675923252257,
          "severe_pnl": -0.06305810000000002,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "NEX_USDT": {
          "gross_pnl": -0.0418283,
          "pf": 0.0,
          "severe_pnl": -0.0458283,
          "trades": 1,
          "win_rate": 0.0
        },
        "NGAS_USDT": {
          "gross_pnl": -0.012890100000000002,
          "pf": 0.0,
          "severe_pnl": -0.2408901,
          "trades": 57,
          "win_rate": 0.0
        },
        "NICKEL_USDT": {
          "gross_pnl": -0.00036969999999999993,
          "pf": 0.0,
          "severe_pnl": -0.0163697,
          "trades": 4,
          "win_rate": 0.0
        },
        "NIGHT_USDT": {
          "gross_pnl": 0.0019924000000000005,
          "pf": 0.016427000014569402,
          "severe_pnl": -0.0540076,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "NIL_USDT": {
          "gross_pnl": 0.008372899999999999,
          "pf": 0.2216416795337949,
          "severe_pnl": -0.015627099999999998,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "NOM_USDT": {
          "gross_pnl": 0.019973599999999998,
          "pf": 0.4894991922455572,
          "severe_pnl": -0.008026400000000003,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "NOT_USDT": {
          "gross_pnl": -0.0010673000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0130673,
          "trades": 3,
          "win_rate": 0.0
        },
        "OFC_USDT": {
          "gross_pnl": 0.0039879,
          "pf": 0.08573373475811717,
          "severe_pnl": -0.020012099999999998,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "OGN_USDT": {
          "gross_pnl": 0.049839499999999995,
          "pf": 0.4847378622741171,
          "severe_pnl": -0.04216050000000001,
          "trades": 23,
          "win_rate": 0.21739130434782608
        },
        "OG_USDT": {
          "gross_pnl": -0.0047319,
          "pf": 0.0,
          "severe_pnl": -0.0087319,
          "trades": 1,
          "win_rate": 0.0
        },
        "OKB_USDT": {
          "gross_pnl": 0.00024369999999999996,
          "pf": 0.0,
          "severe_pnl": -0.007756300000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "OL_USDT": {
          "gross_pnl": -0.0010138,
          "pf": 0.0,
          "severe_pnl": -0.0050138000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "ONDO_USDT": {
          "gross_pnl": 0.00023629999999999832,
          "pf": 0.008754155155219191,
          "severe_pnl": -0.3997637,
          "trades": 100,
          "win_rate": 0.02
        },
        "ONE_USDT": {
          "gross_pnl": -0.018176799999999996,
          "pf": 0.0,
          "severe_pnl": -0.0261768,
          "trades": 2,
          "win_rate": 0.0
        },
        "ONG_USDT": {
          "gross_pnl": 0.0010328,
          "pf": 0.0,
          "severe_pnl": -0.0029672,
          "trades": 1,
          "win_rate": 0.0
        },
        "ONT_USDT": {
          "gross_pnl": 0.0002327,
          "pf": 0.0,
          "severe_pnl": -0.0077672999999999996,
          "trades": 2,
          "win_rate": 0.0
        },
        "OPENAI_USDT": {
          "gross_pnl": 0.06252070000000001,
          "pf": 0.0,
          "severe_pnl": -0.32147930000000013,
          "trades": 96,
          "win_rate": 0.0
        },
        "OPENLEDGER_USDT": {
          "gross_pnl": 0.0013324,
          "pf": 0.0,
          "severe_pnl": -0.0026676,
          "trades": 1,
          "win_rate": 0.0
        },
        "OPG_USDT": {
          "gross_pnl": 0.022381399999999996,
          "pf": 0.1345943002901318,
          "severe_pnl": -0.06961859999999999,
          "trades": 23,
          "win_rate": 0.08695652173913043
        },
        "OPN_USDT": {
          "gross_pnl": -0.0200092,
          "pf": 0.021557042068176727,
          "severe_pnl": -0.20000920000000003,
          "trades": 45,
          "win_rate": 0.06666666666666667
        },
        "OP_USDT": {
          "gross_pnl": 0.009005200000000001,
          "pf": 0.005194476392822007,
          "severe_pnl": -0.3669948000000001,
          "trades": 94,
          "win_rate": 0.02127659574468085
        },
        "ORCA_USDT": {
          "gross_pnl": 0.0040973,
          "pf": 0.0,
          "severe_pnl": -0.0079027,
          "trades": 3,
          "win_rate": 0.0
        },
        "ORDI_USDT": {
          "gross_pnl": 0.0339748,
          "pf": 0.012511910642073054,
          "severe_pnl": -0.45402519999999985,
          "trades": 122,
          "win_rate": 0.03278688524590164
        },
        "O_USDT": {
          "gross_pnl": -0.0347409,
          "pf": 0.12114622023834037,
          "severe_pnl": -0.17074089999999997,
          "trades": 34,
          "win_rate": 0.08823529411764706
        },
        "PARTI_USDT": {
          "gross_pnl": 0.04424229999999999,
          "pf": 0.7166468459547886,
          "severe_pnl": -0.027757699999999996,
          "trades": 18,
          "win_rate": 0.2777777777777778
        },
        "PAXG_USDT": {
          "gross_pnl": 0.00033509999999999963,
          "pf": 0.0,
          "severe_pnl": -0.07566490000000001,
          "trades": 19,
          "win_rate": 0.0
        },
        "PENDLE_USDT": {
          "gross_pnl": -0.0079459,
          "pf": 0.014448504172542844,
          "severe_pnl": -0.16394590000000006,
          "trades": 39,
          "win_rate": 0.05128205128205128
        },
        "PEOPLE_USDT": {
          "gross_pnl": 0.0012870000000000002,
          "pf": 0.0,
          "severe_pnl": -0.002713,
          "trades": 1,
          "win_rate": 0.0
        },
        "PEPE_USDT": {
          "gross_pnl": 0.0052287,
          "pf": 0.0,
          "severe_pnl": -0.030771299999999998,
          "trades": 9,
          "win_rate": 0.0
        },
        "PHAROS_USDT": {
          "gross_pnl": -0.0002428,
          "pf": 0.0,
          "severe_pnl": -0.0042428,
          "trades": 1,
          "win_rate": 0.0
        },
        "PHA_USDT": {
          "gross_pnl": 0.00038380000000000017,
          "pf": 0.0,
          "severe_pnl": -0.0196162,
          "trades": 5,
          "win_rate": 0.0
        },
        "PIEVERSE_USDT": {
          "gross_pnl": 0.005217,
          "pf": 0.09753000500592166,
          "severe_pnl": -0.014782999999999998,
          "trades": 5,
          "win_rate": 0.2
        },
        "PIPPIN_USDT": {
          "gross_pnl": 0.0339492,
          "pf": 0.04498224431196051,
          "severe_pnl": -0.2180508,
          "trades": 63,
          "win_rate": 0.09523809523809523
        },
        "PI_USDT": {
          "gross_pnl": -0.06068309999999999,
          "pf": 0.015928912431046403,
          "severe_pnl": -0.6766831000000001,
          "trades": 154,
          "win_rate": 0.03896103896103896
        },
        "PLUME_USDT": {
          "gross_pnl": 0.0009458000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0150542,
          "trades": 4,
          "win_rate": 0.0
        },
        "PNUT_USDT": {
          "gross_pnl": 0.0002346,
          "pf": 0.0,
          "severe_pnl": -0.0037654,
          "trades": 1,
          "win_rate": 0.0
        },
        "POL_USDT": {
          "gross_pnl": 0.030421300000000002,
          "pf": 0.021726298092227057,
          "severe_pnl": -0.22157870000000002,
          "trades": 63,
          "win_rate": 0.031746031746031744
        },
        "PONS_USDT": {
          "gross_pnl": 0.0169122,
          "pf": 999,
          "severe_pnl": 0.012912199999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "POPCAT_USDT": {
          "gross_pnl": 0.0046815,
          "pf": 0.0,
          "severe_pnl": -0.0073185,
          "trades": 3,
          "win_rate": 0.0
        },
        "PORTAL_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "POWER_USDT": {
          "gross_pnl": 0.0058257000000000005,
          "pf": 0.03625361210266871,
          "severe_pnl": -0.0141743,
          "trades": 5,
          "win_rate": 0.2
        },
        "POWR_USDT": {
          "gross_pnl": -0.029211,
          "pf": 0.06766453863037311,
          "severe_pnl": -0.03721100000000001,
          "trades": 2,
          "win_rate": 0.5
        },
        "PRL_USDT": {
          "gross_pnl": 0.0017699,
          "pf": 0.0,
          "severe_pnl": -0.0022301,
          "trades": 1,
          "win_rate": 0.0
        },
        "PROM_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "PTB_USDT": {
          "gross_pnl": -0.0009311,
          "pf": 0.0,
          "severe_pnl": -0.0049311,
          "trades": 1,
          "win_rate": 0.0
        },
        "PUMPFUN_USDT": {
          "gross_pnl": 0.019466100000000007,
          "pf": 0.02816404127003699,
          "severe_pnl": -0.4445339,
          "trades": 116,
          "win_rate": 0.07758620689655173
        },
        "PUNDIX_USDT": {
          "gross_pnl": 0.0012245000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0067755,
          "trades": 2,
          "win_rate": 0.0
        },
        "PYTH_USDT": {
          "gross_pnl": 0.022821899999999992,
          "pf": 0.013817494933630693,
          "severe_pnl": -0.3611781000000001,
          "trades": 96,
          "win_rate": 0.052083333333333336
        },
        "QNT_USDT": {
          "gross_pnl": -0.0025758,
          "pf": 0.0,
          "severe_pnl": -0.018575800000000003,
          "trades": 4,
          "win_rate": 0.0
        },
        "QTUM_USDT": {
          "gross_pnl": 0.0038018999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0081981,
          "trades": 3,
          "win_rate": 0.0
        },
        "RAM_USDT": {
          "gross_pnl": 0.0102103,
          "pf": 0.0021965330515030315,
          "severe_pnl": -0.045789699999999996,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "RARE_USDT": {
          "gross_pnl": 0.0088255,
          "pf": 1.206375,
          "severe_pnl": 0.0008254999999999998,
          "trades": 2,
          "win_rate": 0.5
        },
        "RAVE_USDT": {
          "gross_pnl": -0.06800939999999997,
          "pf": 0.05080517952618423,
          "severe_pnl": -0.6080094000000004,
          "trades": 135,
          "win_rate": 0.0962962962962963
        },
        "RAY_USDT": {
          "gross_pnl": -0.0002904,
          "pf": 0.0,
          "severe_pnl": -0.0042904,
          "trades": 1,
          "win_rate": 0.0
        },
        "RED_USDT": {
          "gross_pnl": 0.0008849999999999999,
          "pf": 0.0,
          "severe_pnl": -0.003115,
          "trades": 1,
          "win_rate": 0.0
        },
        "RENDER_USDT": {
          "gross_pnl": 0.0007687000000000006,
          "pf": 0.0,
          "severe_pnl": -0.14323130000000003,
          "trades": 36,
          "win_rate": 0.0
        },
        "RESOLV_USDT": {
          "gross_pnl": 0.004634000000000005,
          "pf": 0.019150937179894214,
          "severe_pnl": -0.147366,
          "trades": 38,
          "win_rate": 0.05263157894736842
        },
        "REZ_USDT": {
          "gross_pnl": 0.0033278,
          "pf": 0.0,
          "severe_pnl": -0.0006722,
          "trades": 1,
          "win_rate": 0.0
        },
        "RE_USDT": {
          "gross_pnl": -0.0130264,
          "pf": 0.013256399328006057,
          "severe_pnl": -0.41302639999999996,
          "trades": 100,
          "win_rate": 0.02
        },
        "RIF_USDT": {
          "gross_pnl": 0.032519700000000006,
          "pf": 0.2527643061651675,
          "severe_pnl": -0.04348030000000001,
          "trades": 19,
          "win_rate": 0.2631578947368421
        },
        "RLC_USDT": {
          "gross_pnl": -0.0108165,
          "pf": 0.0,
          "severe_pnl": -0.038816500000000004,
          "trades": 7,
          "win_rate": 0.0
        },
        "ROAM_USDT": {
          "gross_pnl": -0.06238259999999999,
          "pf": 0.35113992966129814,
          "severe_pnl": -0.15038260000000003,
          "trades": 22,
          "win_rate": 0.2727272727272727
        },
        "ROBO_USDT": {
          "gross_pnl": 0.0060479,
          "pf": 0.17081035143557013,
          "severe_pnl": -0.009952100000000002,
          "trades": 4,
          "win_rate": 0.25
        },
        "ROSE_USDT": {
          "gross_pnl": -0.0024519000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0224519,
          "trades": 5,
          "win_rate": 0.0
        },
        "RPL_USDT": {
          "gross_pnl": 0.0087765,
          "pf": 0.12343114207389937,
          "severe_pnl": -0.0112235,
          "trades": 5,
          "win_rate": 0.2
        },
        "RSR_USDT": {
          "gross_pnl": 0.0023861000000000004,
          "pf": 0.0,
          "severe_pnl": -0.021613900000000002,
          "trades": 6,
          "win_rate": 0.0
        },
        "RUNE_USDT": {
          "gross_pnl": -0.0011861000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0171861,
          "trades": 4,
          "win_rate": 0.0
        },
        "RVN_USDT": {
          "gross_pnl": 0.006082499999999999,
          "pf": 0.24090110186807723,
          "severe_pnl": -0.0579175,
          "trades": 16,
          "win_rate": 0.1875
        },
        "SAFE_USDT": {
          "gross_pnl": -0.00040510000000000014,
          "pf": 0.012775765161818302,
          "severe_pnl": -0.016405100000000002,
          "trades": 4,
          "win_rate": 0.25
        },
        "SAGA_USDT": {
          "gross_pnl": 0.0014921,
          "pf": 0.0,
          "severe_pnl": -0.0065079000000000005,
          "trades": 2,
          "win_rate": 0.0
        },
        "SAHARA_USDT": {
          "gross_pnl": 0.016097300000000002,
          "pf": 0.0,
          "severe_pnl": -0.0479027,
          "trades": 16,
          "win_rate": 0.0
        },
        "SAND_USDT": {
          "gross_pnl": -0.0022278,
          "pf": 0.0,
          "severe_pnl": -0.0102278,
          "trades": 2,
          "win_rate": 0.0
        },
        "SANTOS_USDT": {
          "gross_pnl": 0.00037400000000000063,
          "pf": 0.0,
          "severe_pnl": -0.015626,
          "trades": 4,
          "win_rate": 0.0
        },
        "SAPIEN_USDT": {
          "gross_pnl": -0.0001371,
          "pf": 0.0,
          "severe_pnl": -0.0041371,
          "trades": 1,
          "win_rate": 0.0
        },
        "SEI_USDT": {
          "gross_pnl": -0.0050418999999999985,
          "pf": 0.0,
          "severe_pnl": -0.21304190000000006,
          "trades": 52,
          "win_rate": 0.0
        },
        "SENT_USDT": {
          "gross_pnl": 0.0268964,
          "pf": 0.30827042248759273,
          "severe_pnl": -0.0491036,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "SHIB_USDT": {
          "gross_pnl": 0.0086563,
          "pf": 0.0,
          "severe_pnl": -0.0873437,
          "trades": 24,
          "win_rate": 0.0
        },
        "SHLD_USDT": {
          "gross_pnl": -0.0026187,
          "pf": 0.0,
          "severe_pnl": -0.0106187,
          "trades": 2,
          "win_rate": 0.0
        },
        "SIGN_USDT": {
          "gross_pnl": 0.0011727,
          "pf": 0.0,
          "severe_pnl": -0.0028273,
          "trades": 1,
          "win_rate": 0.0
        },
        "SIREN_USDT": {
          "gross_pnl": 0.0098468,
          "pf": 999,
          "severe_pnl": 0.005846799999999999,
          "trades": 1,
          "win_rate": 1.0
        },
        "SKL_USDT": {
          "gross_pnl": 0.0766771,
          "pf": 0.43660530309573453,
          "severe_pnl": -0.09132290000000003,
          "trades": 42,
          "win_rate": 0.3333333333333333
        },
        "SKR_USDT": {
          "gross_pnl": 0.0136872,
          "pf": 0.6707148653843413,
          "severe_pnl": -0.002312800000000001,
          "trades": 4,
          "win_rate": 0.5
        },
        "SKYAI_USDT": {
          "gross_pnl": 0.023037200000000015,
          "pf": 0.08200505170000755,
          "severe_pnl": -0.6409628000000005,
          "trades": 166,
          "win_rate": 0.12650602409638553
        },
        "SKY_USDT": {
          "gross_pnl": -0.0033218999999999983,
          "pf": 0.065036484926159,
          "severe_pnl": -0.06332190000000001,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "SLX_USDT": {
          "gross_pnl": 0.05361190000000001,
          "pf": 0.10012222612480136,
          "severe_pnl": -0.5423881000000002,
          "trades": 149,
          "win_rate": 0.12751677852348994
        },
        "SMH_USDT": {
          "gross_pnl": -0.000169,
          "pf": 0.0,
          "severe_pnl": -0.004169,
          "trades": 1,
          "win_rate": 0.0
        },
        "SNT_USDT": {
          "gross_pnl": -0.0005340000000000001,
          "pf": 0.0,
          "severe_pnl": -0.012534,
          "trades": 3,
          "win_rate": 0.0
        },
        "SNXX_USDT": {
          "gross_pnl": 0.0393825,
          "pf": 1.7424886824698962,
          "severe_pnl": 0.0113825,
          "trades": 7,
          "win_rate": 0.42857142857142855
        },
        "SNX_USDT": {
          "gross_pnl": -0.0074863,
          "pf": 0.029372778351106528,
          "severe_pnl": -0.0634863,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "SOL_USDT": {
          "gross_pnl": 0.0034867000000000006,
          "pf": 0.0,
          "severe_pnl": -0.2045133,
          "trades": 52,
          "win_rate": 0.0
        },
        "SOXL_USDT": {
          "gross_pnl": -0.022819099999999988,
          "pf": 0.09854107018064187,
          "severe_pnl": -0.49481910000000007,
          "trades": 118,
          "win_rate": 0.1271186440677966
        },
        "SOXS_USDT": {
          "gross_pnl": -0.012364099999999998,
          "pf": 0.1292875614325992,
          "severe_pnl": -0.11636410000000001,
          "trades": 26,
          "win_rate": 0.15384615384615385
        },
        "SOXX_USDT": {
          "gross_pnl": 0.0143148,
          "pf": 6.784874253662772e-05,
          "severe_pnl": -0.017685199999999998,
          "trades": 8,
          "win_rate": 0.125
        },
        "SPELL_USDT": {
          "gross_pnl": 0.0291114,
          "pf": 1.7222270662745625,
          "severe_pnl": 0.009111399999999999,
          "trades": 5,
          "win_rate": 0.2
        },
        "SPK_USDT": {
          "gross_pnl": -0.0010946999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0050947,
          "trades": 1,
          "win_rate": 0.0
        },
        "SPY_USDT": {
          "gross_pnl": -0.0020889,
          "pf": 0.0,
          "severe_pnl": -0.0060888999999999995,
          "trades": 1,
          "win_rate": 0.0
        },
        "SQD_USDT": {
          "gross_pnl": -0.0042818000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0162818,
          "trades": 3,
          "win_rate": 0.0
        },
        "SQQQ_USDT": {
          "gross_pnl": -0.0021403999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0101404,
          "trades": 2,
          "win_rate": 0.0
        },
        "STABLE_USDT": {
          "gross_pnl": 0.0010201999999999993,
          "pf": 0.04289793723558631,
          "severe_pnl": -0.03897980000000001,
          "trades": 10,
          "win_rate": 0.1
        },
        "STAR_USDT": {
          "gross_pnl": 0.031211000000000003,
          "pf": 999,
          "severe_pnl": 0.027211000000000003,
          "trades": 1,
          "win_rate": 1.0
        },
        "STEEM_USDT": {
          "gross_pnl": 0.0016294,
          "pf": 0.0,
          "severe_pnl": -0.0023706,
          "trades": 1,
          "win_rate": 0.0
        },
        "STG_USDT": {
          "gross_pnl": 0.0108791,
          "pf": 0.005494796143724295,
          "severe_pnl": -0.045120900000000005,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "STORJ_USDT": {
          "gross_pnl": -0.0173053,
          "pf": 0.0,
          "severe_pnl": -0.0213053,
          "trades": 1,
          "win_rate": 0.0
        },
        "STO_USDT": {
          "gross_pnl": -0.002469,
          "pf": 0.0,
          "severe_pnl": -0.010469,
          "trades": 2,
          "win_rate": 0.0
        },
        "STRK_USDT": {
          "gross_pnl": 0.013827299999999997,
          "pf": 0.030669553396692948,
          "severe_pnl": -0.0661727,
          "trades": 20,
          "win_rate": 0.1
        },
        "STX_USDT": {
          "gross_pnl": 0.0250197,
          "pf": 0.14533379523249892,
          "severe_pnl": -0.03898030000000002,
          "trades": 16,
          "win_rate": 0.1875
        },
        "SUI_USDT": {
          "gross_pnl": 5.2800000000003235e-05,
          "pf": 0.007670893614205569,
          "severe_pnl": -0.2519471999999999,
          "trades": 63,
          "win_rate": 0.015873015873015872
        },
        "SUPER_USDT": {
          "gross_pnl": -0.004648000000000001,
          "pf": 0.0,
          "severe_pnl": -0.016648000000000003,
          "trades": 3,
          "win_rate": 0.0
        },
        "SUSHI_USDT": {
          "gross_pnl": 0.007349,
          "pf": 0.026698018743741794,
          "severe_pnl": -0.008651,
          "trades": 4,
          "win_rate": 0.25
        },
        "SXT_USDT": {
          "gross_pnl": 0.021617100000000042,
          "pf": 0.2380378804540715,
          "severe_pnl": -0.31838289999999997,
          "trades": 85,
          "win_rate": 0.21176470588235294
        },
        "SYN_USDT": {
          "gross_pnl": 0.01672300000000004,
          "pf": 0.18907014589178522,
          "severe_pnl": -0.599277,
          "trades": 154,
          "win_rate": 0.16883116883116883
        },
        "SYRUP_USDT": {
          "gross_pnl": -0.0008547999999999994,
          "pf": 0.0039321980211840055,
          "severe_pnl": -0.2968548,
          "trades": 74,
          "win_rate": 0.02702702702702703
        },
        "S_USDT": {
          "gross_pnl": -0.0007026000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0287026,
          "trades": 7,
          "win_rate": 0.0
        },
        "TAC_USDT": {
          "gross_pnl": 0.0748576,
          "pf": 0.36022005572005217,
          "severe_pnl": -0.20114240000000003,
          "trades": 69,
          "win_rate": 0.2753623188405797
        },
        "TAG_USDT": {
          "gross_pnl": -0.0684401,
          "pf": 0.050956899243545954,
          "severe_pnl": -0.18844010000000005,
          "trades": 30,
          "win_rate": 0.16666666666666666
        },
        "TAIKO_USDT": {
          "gross_pnl": -0.0055277,
          "pf": 0.0,
          "severe_pnl": -0.0175277,
          "trades": 3,
          "win_rate": 0.0
        },
        "TAO_USDT": {
          "gross_pnl": 0.014651399999999998,
          "pf": 0.0,
          "severe_pnl": -0.12134860000000003,
          "trades": 34,
          "win_rate": 0.0
        },
        "TENDIES_USDT": {
          "gross_pnl": -0.0392548,
          "pf": 0.0,
          "severe_pnl": -0.043254799999999996,
          "trades": 1,
          "win_rate": 0.0
        },
        "THETA_USDT": {
          "gross_pnl": 0.03949890000000001,
          "pf": 0.11369814137027819,
          "severe_pnl": -0.11650110000000002,
          "trades": 39,
          "win_rate": 0.10256410256410256
        },
        "THE_USDT": {
          "gross_pnl": -0.0212235,
          "pf": 0.1012729216845888,
          "severe_pnl": -0.0652235,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "TIA_USDT": {
          "gross_pnl": 0.02361580000000001,
          "pf": 0.015021380064214622,
          "severe_pnl": -0.3043841999999998,
          "trades": 82,
          "win_rate": 0.04878048780487805
        },
        "TLM_USDT": {
          "gross_pnl": 0.004337399999999999,
          "pf": 0.036980761956731674,
          "severe_pnl": -0.2996626,
          "trades": 76,
          "win_rate": 0.10526315789473684
        },
        "TNSR_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "TOSHI_USDT": {
          "gross_pnl": 0.0249733,
          "pf": 4.243325,
          "severe_pnl": 0.0129733,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "TOWNS_USDT": {
          "gross_pnl": -0.006660299999999999,
          "pf": 0.0,
          "severe_pnl": -0.0386603,
          "trades": 8,
          "win_rate": 0.0
        },
        "TQQQ_USDT": {
          "gross_pnl": -0.0119583,
          "pf": 0.0,
          "severe_pnl": -0.07595829999999999,
          "trades": 16,
          "win_rate": 0.0
        },
        "TRADOOR_USDT": {
          "gross_pnl": -0.0033661999999999937,
          "pf": 0.10458673508789522,
          "severe_pnl": -0.1553662,
          "trades": 38,
          "win_rate": 0.15789473684210525
        },
        "TRB_USDT": {
          "gross_pnl": -0.0130594,
          "pf": 0.0,
          "severe_pnl": -0.0890594,
          "trades": 19,
          "win_rate": 0.0
        },
        "TRIA_USDT": {
          "gross_pnl": 0.012284100000000001,
          "pf": 0.13416580295601008,
          "severe_pnl": -0.5637159,
          "trades": 144,
          "win_rate": 0.18055555555555555
        },
        "TRX_USDT": {
          "gross_pnl": 0.0007744000000000002,
          "pf": 0.0,
          "severe_pnl": -0.04722559999999999,
          "trades": 12,
          "win_rate": 0.0
        },
        "TRY_USDT": {
          "gross_pnl": 0.0004684,
          "pf": 0.0,
          "severe_pnl": -0.0155316,
          "trades": 4,
          "win_rate": 0.0
        },
        "TSLL_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "TURBO_USDT": {
          "gross_pnl": 0.0071278,
          "pf": 0.0,
          "severe_pnl": -0.0128722,
          "trades": 5,
          "win_rate": 0.0
        },
        "TUT_USDT": {
          "gross_pnl": -5.569999999999989e-05,
          "pf": 0.0,
          "severe_pnl": -0.008055699999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "TWT_USDT": {
          "gross_pnl": 0.0086063,
          "pf": 999,
          "severe_pnl": 0.004606300000000001,
          "trades": 1,
          "win_rate": 1.0
        },
        "T_USDT": {
          "gross_pnl": -0.08785679999999998,
          "pf": 0.08868597293111759,
          "severe_pnl": -0.3998568,
          "trades": 78,
          "win_rate": 0.16666666666666666
        },
        "UAI_USDT": {
          "gross_pnl": 0.049202199999999995,
          "pf": 0.1591817704275354,
          "severe_pnl": -0.19079780000000007,
          "trades": 60,
          "win_rate": 0.11666666666666667
        },
        "UMA_USDT": {
          "gross_pnl": -0.00148,
          "pf": 0.0,
          "severe_pnl": -0.00948,
          "trades": 2,
          "win_rate": 0.0
        },
        "UNI_USDT": {
          "gross_pnl": 0.005304299999999998,
          "pf": 0.018806990982024922,
          "severe_pnl": -0.37069570000000013,
          "trades": 94,
          "win_rate": 0.02127659574468085
        },
        "UP_USDT": {
          "gross_pnl": 0.0024848999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0095151,
          "trades": 3,
          "win_rate": 0.0
        },
        "URNM_USDT": {
          "gross_pnl": -0.0015041,
          "pf": 0.0,
          "severe_pnl": -0.0095041,
          "trades": 2,
          "win_rate": 0.0
        },
        "USELESS_USDT": {
          "gross_pnl": 0.0247632,
          "pf": 0.039581745850983174,
          "severe_pnl": -0.19523680000000002,
          "trades": 55,
          "win_rate": 0.05454545454545454
        },
        "USO_USDT": {
          "gross_pnl": 0.0013599,
          "pf": 0.0,
          "severe_pnl": -0.0026401000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "USUAL_USDT": {
          "gross_pnl": -0.0016453999999999996,
          "pf": 0.008872065769877306,
          "severe_pnl": -0.04964539999999999,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "UVXY_USDT": {
          "gross_pnl": 0.0005467000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0154533,
          "trades": 4,
          "win_rate": 0.0
        },
        "VANRY_USDT": {
          "gross_pnl": -0.07287660000000001,
          "pf": 0.15242195461322747,
          "severe_pnl": -0.2808766,
          "trades": 52,
          "win_rate": 0.17307692307692307
        },
        "VELO_USDT": {
          "gross_pnl": 0.012998800000000001,
          "pf": 0.5719857679093254,
          "severe_pnl": -0.007001200000000001,
          "trades": 5,
          "win_rate": 0.2
        },
        "VELVET_USDT": {
          "gross_pnl": -0.05358939999999998,
          "pf": 0.17349576576055256,
          "severe_pnl": -0.6455894,
          "trades": 148,
          "win_rate": 0.17567567567567569
        },
        "VET_USDT": {
          "gross_pnl": -0.0023320000000000007,
          "pf": 0.0,
          "severe_pnl": -0.046332000000000005,
          "trades": 11,
          "win_rate": 0.0
        },
        "VINE_USDT": {
          "gross_pnl": 0.0370347,
          "pf": 1.4356256597504629,
          "severe_pnl": 0.0050347000000000005,
          "trades": 8,
          "win_rate": 0.5
        },
        "VIRTUAL_USDT": {
          "gross_pnl": 0.012009800000000004,
          "pf": 0.004042193790250131,
          "severe_pnl": -0.3999902000000001,
          "trades": 103,
          "win_rate": 0.02912621359223301
        },
        "VVV_USDT": {
          "gross_pnl": -0.024661,
          "pf": 0.009143907178690774,
          "severe_pnl": -0.30466100000000007,
          "trades": 70,
          "win_rate": 0.04285714285714286
        },
        "WIF_USDT": {
          "gross_pnl": -0.011303699999999996,
          "pf": 0.0,
          "severe_pnl": -0.3153036999999999,
          "trades": 76,
          "win_rate": 0.0
        },
        "WLD_USDT": {
          "gross_pnl": 0.01898140000000001,
          "pf": 0.004347901054520353,
          "severe_pnl": -0.5370186000000002,
          "trades": 139,
          "win_rate": 0.014388489208633094
        },
        "WLFI_USDT": {
          "gross_pnl": 0.0013677999999999987,
          "pf": 0.016668384534846488,
          "severe_pnl": -0.09063220000000002,
          "trades": 23,
          "win_rate": 0.043478260869565216
        },
        "WOO_USDT": {
          "gross_pnl": 0.0015911,
          "pf": 0.0,
          "severe_pnl": -0.0024089000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "W_USDT": {
          "gross_pnl": -0.0020462,
          "pf": 0.0,
          "severe_pnl": -0.0180462,
          "trades": 4,
          "win_rate": 0.0
        },
        "XAI_USDT": {
          "gross_pnl": 0.0169123,
          "pf": 0.6635832734087295,
          "severe_pnl": -0.0030876999999999988,
          "trades": 5,
          "win_rate": 0.4
        },
        "XAN_USDT": {
          "gross_pnl": -0.0051126,
          "pf": 0.04226786836484106,
          "severe_pnl": -0.0611126,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "XBI_USDT": {
          "gross_pnl": -0.008714900000000001,
          "pf": 0.0,
          "severe_pnl": -0.0647149,
          "trades": 14,
          "win_rate": 0.0
        },
        "XDC_USDT": {
          "gross_pnl": -0.0003685000000000001,
          "pf": 0.0,
          "severe_pnl": -0.008368500000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "XEC_USDT": {
          "gross_pnl": -0.0322374,
          "pf": 0.09716554009453897,
          "severe_pnl": -0.3802374,
          "trades": 87,
          "win_rate": 0.1839080459770115
        },
        "XLM_USDT": {
          "gross_pnl": -0.018051300000000006,
          "pf": 0.0,
          "severe_pnl": -0.2980513000000001,
          "trades": 70,
          "win_rate": 0.0
        },
        "XLU_USDT": {
          "gross_pnl": -0.0156344,
          "pf": 0.0,
          "severe_pnl": -0.0356344,
          "trades": 5,
          "win_rate": 0.0
        },
        "XMR_USDT": {
          "gross_pnl": -0.009141799999999999,
          "pf": 0.0,
          "severe_pnl": -0.3131417999999999,
          "trades": 76,
          "win_rate": 0.0
        },
        "XPIN_USDT": {
          "gross_pnl": -0.051641099999999995,
          "pf": 0.13402740771595384,
          "severe_pnl": -0.11164110000000002,
          "trades": 15,
          "win_rate": 0.26666666666666666
        },
        "XPL_USDT": {
          "gross_pnl": -0.0250119,
          "pf": 0.003995373132016866,
          "severe_pnl": -0.3730119,
          "trades": 87,
          "win_rate": 0.011494252873563218
        },
        "XPT_USDT": {
          "gross_pnl": -0.008747099999999999,
          "pf": 0.0,
          "severe_pnl": -0.1087471,
          "trades": 25,
          "win_rate": 0.0
        },
        "XRP_USDT": {
          "gross_pnl": -0.0034845000000000006,
          "pf": 0.0,
          "severe_pnl": -0.1114845,
          "trades": 27,
          "win_rate": 0.0
        },
        "XTZ_USDT": {
          "gross_pnl": 0.0004706999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0155293,
          "trades": 4,
          "win_rate": 0.0
        },
        "XVS_USDT": {
          "gross_pnl": -0.0069364000000000006,
          "pf": 0.0,
          "severe_pnl": -0.0109364,
          "trades": 1,
          "win_rate": 0.0
        },
        "YFI_USDT": {
          "gross_pnl": 0.0013945999999999997,
          "pf": 0.0,
          "severe_pnl": -0.014605400000000001,
          "trades": 4,
          "win_rate": 0.0
        },
        "ZAMA_USDT": {
          "gross_pnl": -0.0002729000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0082729,
          "trades": 2,
          "win_rate": 0.0
        },
        "ZBT_USDT": {
          "gross_pnl": 0.021025300000000004,
          "pf": 0.09446049399033665,
          "severe_pnl": -0.25897470000000006,
          "trades": 70,
          "win_rate": 0.08571428571428572
        },
        "ZEC_USDT": {
          "gross_pnl": -0.0270611,
          "pf": 0.01808382546109899,
          "severe_pnl": -0.4430610999999999,
          "trades": 104,
          "win_rate": 0.038461538461538464
        },
        "ZEN_USDT": {
          "gross_pnl": -0.0042919,
          "pf": 0.0,
          "severe_pnl": -0.08029190000000001,
          "trades": 19,
          "win_rate": 0.0
        },
        "ZEST_USDT": {
          "gross_pnl": 0.006893099999999999,
          "pf": 0.023400392765801945,
          "severe_pnl": -0.017106899999999998,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "ZETA_USDT": {
          "gross_pnl": 0.0005775,
          "pf": 0.0,
          "severe_pnl": -0.0034225,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZINC_USDT": {
          "gross_pnl": 0.0010873,
          "pf": 0.0,
          "severe_pnl": -0.0189127,
          "trades": 5,
          "win_rate": 0.0
        },
        "ZKC_USDT": {
          "gross_pnl": -0.00022429999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0042243,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZKP_USDT": {
          "gross_pnl": -0.0082413,
          "pf": 0.0,
          "severe_pnl": -0.0322413,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZKSYNC_USDT": {
          "gross_pnl": 0.0306726,
          "pf": 0.14591663306413621,
          "severe_pnl": -0.045327400000000004,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "ZORA_USDT": {
          "gross_pnl": 0.0029619,
          "pf": 0.0484379014152155,
          "severe_pnl": -0.0170381,
          "trades": 5,
          "win_rate": 0.2
        },
        "ZRO_USDT": {
          "gross_pnl": 0.007300999999999998,
          "pf": 0.0,
          "severe_pnl": -0.19669899999999998,
          "trades": 51,
          "win_rate": 0.0
        },
        "ZRX_USDT": {
          "gross_pnl": -5.200000000000126e-06,
          "pf": 0.0,
          "severe_pnl": -0.0200052,
          "trades": 5,
          "win_rate": 0.0
        }
      },
      "validation_depth_quartiles": [
        {
          "gross_pnl": -0.2212654999999995,
          "pf": 0.1877553060828738,
          "quartile": 1,
          "severe_pnl": -11.297265499999963,
          "trades": 2769,
          "upper": 8976.76524,
          "win_rate": 0.16540267244492596
        },
        {
          "gross_pnl": 0.5634687999999997,
          "pf": 0.10049874335970228,
          "quartile": 2,
          "severe_pnl": -11.556531199999936,
          "trades": 3030,
          "upper": 106972.33601999999,
          "win_rate": 0.0933993399339934
        },
        {
          "gross_pnl": 0.01861409999999986,
          "pf": 0.06249994818850139,
          "quartile": 3,
          "severe_pnl": -11.761385899999947,
          "trades": 2945,
          "upper": 1071304.435,
          "win_rate": 0.07775891341256366
        },
        {
          "gross_pnl": 0.1332443999999998,
          "pf": 0.020195186808589078,
          "quartile": 4,
          "severe_pnl": -11.07075559999989,
          "trades": 2801,
          "upper": null,
          "win_rate": 0.03213138164941092
        }
      ],
      "validation_pass": false,
      "validation_skips": {
        "invalid_path_json": 0,
        "missing_horizon_path": 19,
        "structure_not_selected": 76090,
        "symbol_cooldown": 3646
      },
      "validation_spread_quartiles": [
        {
          "gross_pnl": 0.0004797000000001908,
          "pf": 0.048204382209558735,
          "quartile": 1,
          "severe_pnl": -12.103520299999964,
          "trades": 3026,
          "upper": 2.148689299527946,
          "win_rate": 0.05584930601454065
        },
        {
          "gross_pnl": 0.005208899999999998,
          "pf": 0.07235468988053159,
          "quartile": 2,
          "severe_pnl": -11.342791099999971,
          "trades": 2837,
          "upper": 4.268032437045758,
          "win_rate": 0.07966161438138879
        },
        {
          "gross_pnl": -0.11163040000000014,
          "pf": 0.07549123975026782,
          "quartile": 3,
          "severe_pnl": -11.707630399999907,
          "trades": 2899,
          "upper": 7.482229704451622,
          "win_rate": 0.08451190065539842
        },
        {
          "gross_pnl": 0.6000035999999982,
          "pf": 0.1894212448008034,
          "quartile": 4,
          "severe_pnl": -10.531996399999906,
          "trades": 2783,
          "upper": null,
          "win_rate": 0.15091627739849084
        }
      ]
    },
    {
      "direction": "fade",
      "horizon_seconds": 300,
      "leave_best_symbol": -44.60326299999995,
      "structure": "confirm",
      "validation": {
        "gross_pnl": 1.6425674999999946,
        "pf": 0.27277010187263184,
        "severe_pnl": -44.509432499999946,
        "trades": 11538,
        "win_rate": 0.19457444964465245
      },
      "validation_by_symbol": {
        "0G_USDT": {
          "gross_pnl": 0.021992600000000005,
          "pf": 0.2696373602784804,
          "severe_pnl": -0.06600740000000001,
          "trades": 22,
          "win_rate": 0.2727272727272727
        },
        "1000000BABYDOGE_USDT": {
          "gross_pnl": 0.025412900000000002,
          "pf": 2.260984019009458,
          "severe_pnl": 0.005412899999999999,
          "trades": 5,
          "win_rate": 0.8
        },
        "1000BONK_USDT": {
          "gross_pnl": 0.03242269999999999,
          "pf": 0.13742373005954567,
          "severe_pnl": -0.15957730000000003,
          "trades": 48,
          "win_rate": 0.20833333333333334
        },
        "1INCH_USDT": {
          "gross_pnl": 0.0044112000000000005,
          "pf": 999,
          "severe_pnl": 0.00041120000000000045,
          "trades": 1,
          "win_rate": 1.0
        },
        "2Z_USDT": {
          "gross_pnl": 0.016876000000000002,
          "pf": 2.4546765655473064,
          "severe_pnl": 0.008876,
          "trades": 2,
          "win_rate": 0.5
        },
        "4_USDT": {
          "gross_pnl": 0.013268899999999998,
          "pf": 0.19375657400450783,
          "severe_pnl": -0.010731100000000002,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "AAVE_USDT": {
          "gross_pnl": -0.0024524000000000017,
          "pf": 0.014725442037827764,
          "severe_pnl": -0.17045240000000003,
          "trades": 42,
          "win_rate": 0.047619047619047616
        },
        "ACE_USDT": {
          "gross_pnl": -0.0857396,
          "pf": 0.0,
          "severe_pnl": -0.0897396,
          "trades": 1,
          "win_rate": 0.0
        },
        "ACT_USDT": {
          "gross_pnl": 0.0048378,
          "pf": 0.09356451306713914,
          "severe_pnl": -0.0071622000000000005,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "ACU_USDT": {
          "gross_pnl": -0.0199946,
          "pf": 0.0,
          "severe_pnl": -0.0359946,
          "trades": 4,
          "win_rate": 0.0
        },
        "ADA_USDT": {
          "gross_pnl": 0.01704770000000001,
          "pf": 0.02143722112939595,
          "severe_pnl": -0.2549523000000001,
          "trades": 68,
          "win_rate": 0.07352941176470588
        },
        "AERGO_USDT": {
          "gross_pnl": -0.1213724,
          "pf": 0.0,
          "severe_pnl": -0.1493724,
          "trades": 7,
          "win_rate": 0.0
        },
        "AERO_USDT": {
          "gross_pnl": 0.007168200000000002,
          "pf": 0.10475788046695682,
          "severe_pnl": -0.16483180000000006,
          "trades": 43,
          "win_rate": 0.13953488372093023
        },
        "AEVO_USDT": {
          "gross_pnl": -0.0099738,
          "pf": 0.0,
          "severe_pnl": -0.0139738,
          "trades": 1,
          "win_rate": 0.0
        },
        "AGI_USDT": {
          "gross_pnl": 0.0048714,
          "pf": 0.0,
          "severe_pnl": -0.0071286,
          "trades": 3,
          "win_rate": 0.0
        },
        "AGLD_USDT": {
          "gross_pnl": -0.032169100000000006,
          "pf": 0.11021044700275105,
          "severe_pnl": -0.0761691,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "AGT_USDT": {
          "gross_pnl": 0.018707699999999997,
          "pf": 12.500053699924814,
          "severe_pnl": 0.010707699999999997,
          "trades": 2,
          "win_rate": 0.5
        },
        "AIGENSYN_USDT": {
          "gross_pnl": -0.0502963,
          "pf": 0.03590772272421886,
          "severe_pnl": -0.1302963,
          "trades": 20,
          "win_rate": 0.15
        },
        "AIOT_USDT": {
          "gross_pnl": -0.07989770000000003,
          "pf": 0.28567723933405204,
          "severe_pnl": -0.2558976999999999,
          "trades": 44,
          "win_rate": 0.3409090909090909
        },
        "AIOZ_USDT": {
          "gross_pnl": 0.0011874,
          "pf": 0.0,
          "severe_pnl": -0.0028126,
          "trades": 1,
          "win_rate": 0.0
        },
        "AIO_USDT": {
          "gross_pnl": 0.022553000000000004,
          "pf": 3.6802585778219794,
          "severe_pnl": 0.014553000000000003,
          "trades": 2,
          "win_rate": 0.5
        },
        "AKE_USDT": {
          "gross_pnl": -0.09721220000000003,
          "pf": 0.6845673915736797,
          "severe_pnl": -0.3852121999999999,
          "trades": 72,
          "win_rate": 0.4444444444444444
        },
        "AKT_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "ALCH_USDT": {
          "gross_pnl": 0.09244709999999998,
          "pf": 0.7219241298726498,
          "severe_pnl": -0.03955290000000003,
          "trades": 33,
          "win_rate": 0.36363636363636365
        },
        "ALGO_USDT": {
          "gross_pnl": 0.015350299999999999,
          "pf": 0.012568024749677113,
          "severe_pnl": -0.14464970000000002,
          "trades": 40,
          "win_rate": 0.025
        },
        "ALLO_USDT": {
          "gross_pnl": 0.010064699999999921,
          "pf": 0.2818636421271873,
          "severe_pnl": -0.6779353,
          "trades": 172,
          "win_rate": 0.27906976744186046
        },
        "ALPINE_USDT": {
          "gross_pnl": -0.007778500000000001,
          "pf": 0.0,
          "severe_pnl": -0.0117785,
          "trades": 1,
          "win_rate": 0.0
        },
        "ALT_USDT": {
          "gross_pnl": 0.012739,
          "pf": 0.04792739711130664,
          "severe_pnl": -0.019261,
          "trades": 8,
          "win_rate": 0.25
        },
        "ANKR_USDT": {
          "gross_pnl": -0.005862099999999999,
          "pf": 0.0,
          "severe_pnl": -0.021862100000000002,
          "trades": 4,
          "win_rate": 0.0
        },
        "ANSEM_USDT": {
          "gross_pnl": 0.21949529999999992,
          "pf": 0.675353743176459,
          "severe_pnl": -0.36850469999999996,
          "trades": 147,
          "win_rate": 0.42857142857142855
        },
        "ANTHROPIC_USDT": {
          "gross_pnl": 0.0063089,
          "pf": 0.0,
          "severe_pnl": -0.0496911,
          "trades": 14,
          "win_rate": 0.0
        },
        "APE_USDT": {
          "gross_pnl": 0.029989099999999998,
          "pf": 0.0930540572188823,
          "severe_pnl": -0.1820109,
          "trades": 53,
          "win_rate": 0.11320754716981132
        },
        "APR_USDT": {
          "gross_pnl": 0.0037843,
          "pf": 0.0,
          "severe_pnl": -0.0002157000000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "APT_USDT": {
          "gross_pnl": 0.05891539999999999,
          "pf": 0.05342156039850675,
          "severe_pnl": -0.2090846,
          "trades": 67,
          "win_rate": 0.07462686567164178
        },
        "ARB_USDT": {
          "gross_pnl": -0.0220278,
          "pf": 0.07245947821045538,
          "severe_pnl": -0.6060277999999999,
          "trades": 146,
          "win_rate": 0.11643835616438356
        },
        "ARCSOL_USDT": {
          "gross_pnl": 0.0198683,
          "pf": 4.794820143884892,
          "severe_pnl": 0.0118683,
          "trades": 2,
          "win_rate": 0.5
        },
        "ARKK_USDT": {
          "gross_pnl": 0.0156774,
          "pf": 3.128295400992432,
          "severe_pnl": 0.0076774,
          "trades": 2,
          "win_rate": 0.5
        },
        "ARKM_USDT": {
          "gross_pnl": -0.0199449,
          "pf": 0.0,
          "severe_pnl": -0.08394490000000002,
          "trades": 16,
          "win_rate": 0.0
        },
        "ARX_USDT": {
          "gross_pnl": 0.028649300000000006,
          "pf": 0.21770110072984553,
          "severe_pnl": -0.12335070000000002,
          "trades": 38,
          "win_rate": 0.2894736842105263
        },
        "AR_USDT": {
          "gross_pnl": 0.0009320000000000014,
          "pf": 0.0,
          "severe_pnl": -0.035068,
          "trades": 9,
          "win_rate": 0.0
        },
        "ASTEROID_USDT": {
          "gross_pnl": -0.0416667,
          "pf": 0.0,
          "severe_pnl": -0.045666700000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "ASTER_USDT": {
          "gross_pnl": 0.0252722,
          "pf": 0.07789865222285365,
          "severe_pnl": -0.12672779999999997,
          "trades": 38,
          "win_rate": 0.02631578947368421
        },
        "ATH_USDT": {
          "gross_pnl": 0.0121953,
          "pf": 999,
          "severe_pnl": 0.004195299999999999,
          "trades": 2,
          "win_rate": 1.0
        },
        "ATOM_USDT": {
          "gross_pnl": 0.011717199999999999,
          "pf": 5.544359030513514e-05,
          "severe_pnl": -0.14428280000000002,
          "trades": 39,
          "win_rate": 0.02564102564102564
        },
        "AVAAI_USDT": {
          "gross_pnl": -0.056195499999999995,
          "pf": 0.1447520396329075,
          "severe_pnl": -0.07219550000000001,
          "trades": 4,
          "win_rate": 0.25
        },
        "AVAX_USDT": {
          "gross_pnl": -0.0165764,
          "pf": 0.03578515809938251,
          "severe_pnl": -0.0765764,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "AVNT_USDT": {
          "gross_pnl": 0.015057000000000001,
          "pf": 0.10220710706083487,
          "severe_pnl": -0.048943,
          "trades": 16,
          "win_rate": 0.1875
        },
        "AWE_USDT": {
          "gross_pnl": -0.008846800000000002,
          "pf": 0.17149011596944572,
          "severe_pnl": -0.020846800000000002,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "AXL_USDT": {
          "gross_pnl": -0.0046598,
          "pf": 0.0,
          "severe_pnl": -0.0086598,
          "trades": 1,
          "win_rate": 0.0
        },
        "AXS_USDT": {
          "gross_pnl": -0.0023566000000000004,
          "pf": 0.0,
          "severe_pnl": -0.054356600000000005,
          "trades": 13,
          "win_rate": 0.0
        },
        "A_USDT": {
          "gross_pnl": 0.0008489999999999999,
          "pf": 0.0,
          "severe_pnl": -0.015151000000000001,
          "trades": 4,
          "win_rate": 0.0
        },
        "B2_USDT": {
          "gross_pnl": 0.0252587,
          "pf": 999,
          "severe_pnl": 0.013258699999999998,
          "trades": 3,
          "win_rate": 1.0
        },
        "B3_USDT": {
          "gross_pnl": 0.061549099999999995,
          "pf": 1.3479770313449135,
          "severe_pnl": 0.025549099999999995,
          "trades": 9,
          "win_rate": 0.5555555555555556
        },
        "BABY_USDT": {
          "gross_pnl": -0.008914,
          "pf": 0.0,
          "severe_pnl": -0.032914,
          "trades": 6,
          "win_rate": 0.0
        },
        "BANANAS31_USDT": {
          "gross_pnl": -0.0059343,
          "pf": 0.11850402795731692,
          "severe_pnl": -0.0179343,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "BANANA_USDT": {
          "gross_pnl": 0.0060489,
          "pf": 0.4746492905032446,
          "severe_pnl": -0.0019510999999999999,
          "trades": 2,
          "win_rate": 0.5
        },
        "BAND_USDT": {
          "gross_pnl": 0.0254934,
          "pf": 4.373349999999999,
          "severe_pnl": 0.013493400000000001,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "BANK_USDT": {
          "gross_pnl": -0.46339960000000013,
          "pf": 0.32741735293460283,
          "severe_pnl": -0.7793996,
          "trades": 79,
          "win_rate": 0.35443037974683544
        },
        "BAN_USDT": {
          "gross_pnl": -0.0011243999999999994,
          "pf": 0.07917986331055175,
          "severe_pnl": -0.017124399999999998,
          "trades": 4,
          "win_rate": 0.25
        },
        "BASED_USDT": {
          "gross_pnl": -0.009404499999999998,
          "pf": 0.14718019793336118,
          "severe_pnl": -0.10940450000000002,
          "trades": 25,
          "win_rate": 0.16
        },
        "BAS_USDT": {
          "gross_pnl": 0.0168091,
          "pf": 1.1620458665516522,
          "severe_pnl": 0.004809100000000004,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "BAT_USDT": {
          "gross_pnl": -0.0038788999999999994,
          "pf": 0.0,
          "severe_pnl": -0.0358789,
          "trades": 8,
          "win_rate": 0.0
        },
        "BCH_USDT": {
          "gross_pnl": -0.007552800000000001,
          "pf": 0.007779859347035239,
          "severe_pnl": -0.23955279999999998,
          "trades": 58,
          "win_rate": 0.06896551724137931
        },
        "BEAT_USDT": {
          "gross_pnl": -0.20459980000000003,
          "pf": 0.13231808242081017,
          "severe_pnl": -0.9845997999999999,
          "trades": 195,
          "win_rate": 0.1641025641025641
        },
        "BERA_USDT": {
          "gross_pnl": -0.0008866999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0168867,
          "trades": 4,
          "win_rate": 0.0
        },
        "BIANRENSHENG_USDT": {
          "gross_pnl": 0.0018465999999999997,
          "pf": 0.37938411510861725,
          "severe_pnl": -0.0101534,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "BICO_USDT": {
          "gross_pnl": 0.0006420000000000002,
          "pf": 0.02597290107034583,
          "severe_pnl": -0.039358000000000004,
          "trades": 10,
          "win_rate": 0.2
        },
        "BIGTIME_USDT": {
          "gross_pnl": 0.00044080000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0035592,
          "trades": 1,
          "win_rate": 0.0
        },
        "BILL_USDT": {
          "gross_pnl": -0.03408579999999998,
          "pf": 0.3617340188961184,
          "severe_pnl": -0.6780858,
          "trades": 161,
          "win_rate": 0.32298136645962733
        },
        "BIO_USDT": {
          "gross_pnl": 0.006026200000000001,
          "pf": 999,
          "severe_pnl": 0.0020262000000000006,
          "trades": 1,
          "win_rate": 1.0
        },
        "BLAST_USDT": {
          "gross_pnl": 0.0430397,
          "pf": 0.7320696542589036,
          "severe_pnl": -0.07296029999999999,
          "trades": 29,
          "win_rate": 0.4482758620689655
        },
        "BLEND_USDT": {
          "gross_pnl": 0.014131,
          "pf": 0.2727015291674533,
          "severe_pnl": -0.013869000000000001,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "BLESS_USDT": {
          "gross_pnl": 0.06334899999999999,
          "pf": 0.28570814607079587,
          "severe_pnl": -0.12465100000000001,
          "trades": 47,
          "win_rate": 0.2765957446808511
        },
        "BLUAI_USDT": {
          "gross_pnl": -0.1666063,
          "pf": 0.07395993983313735,
          "severe_pnl": -0.1946063,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "BLUR_USDT": {
          "gross_pnl": -0.0011806,
          "pf": 0.0,
          "severe_pnl": -0.013180599999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "BNB_USDT": {
          "gross_pnl": -0.0023318000000000032,
          "pf": 0.0,
          "severe_pnl": -0.09433180000000001,
          "trades": 23,
          "win_rate": 0.0
        },
        "BRETT_USDT": {
          "gross_pnl": 0.027615799999999996,
          "pf": 0.30170647875418855,
          "severe_pnl": -0.0323842,
          "trades": 15,
          "win_rate": 0.26666666666666666
        },
        "BREV_USDT": {
          "gross_pnl": 0.0070123,
          "pf": 0.2607141434092862,
          "severe_pnl": -0.012987700000000001,
          "trades": 5,
          "win_rate": 0.2
        },
        "BSB_USDT": {
          "gross_pnl": 0.23528580000000002,
          "pf": 0.4637655969797338,
          "severe_pnl": -0.38071420000000006,
          "trades": 154,
          "win_rate": 0.34415584415584416
        },
        "BSV_USDT": {
          "gross_pnl": 0.004493599999999999,
          "pf": 0.13297944065142672,
          "severe_pnl": -0.031506400000000004,
          "trades": 9,
          "win_rate": 0.3333333333333333
        },
        "BTW_USDT": {
          "gross_pnl": 0.0313114,
          "pf": 0.3372364661199327,
          "severe_pnl": -0.11668859999999999,
          "trades": 37,
          "win_rate": 0.32432432432432434
        },
        "BUILDONBOB_USDT": {
          "gross_pnl": 0.030953899999999996,
          "pf": 3.3916593059936897,
          "severe_pnl": 0.018953899999999996,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "BULLA_USDT": {
          "gross_pnl": -0.08074989999999999,
          "pf": 0.3048244593178913,
          "severe_pnl": -0.16874989999999998,
          "trades": 22,
          "win_rate": 0.36363636363636365
        },
        "CAKE_USDT": {
          "gross_pnl": 0.0064434,
          "pf": 0.0,
          "severe_pnl": -0.029556600000000002,
          "trades": 9,
          "win_rate": 0.0
        },
        "CAP_USDT": {
          "gross_pnl": 0.012923400000000002,
          "pf": 0.23653768393663963,
          "severe_pnl": -0.19107660000000004,
          "trades": 51,
          "win_rate": 0.19607843137254902
        },
        "CARV_USDT": {
          "gross_pnl": 0.0098522,
          "pf": 999,
          "severe_pnl": 0.0058522,
          "trades": 1,
          "win_rate": 1.0
        },
        "CASHCAT_USDT": {
          "gross_pnl": 0.1727264,
          "pf": 1.302723312680418,
          "severe_pnl": 0.07272640000000001,
          "trades": 25,
          "win_rate": 0.52
        },
        "CATI_USDT": {
          "gross_pnl": 0.0159088,
          "pf": 999,
          "severe_pnl": 0.0079088,
          "trades": 2,
          "win_rate": 1.0
        },
        "CC_USDT": {
          "gross_pnl": -0.023295200000000005,
          "pf": 0.08473257683575323,
          "severe_pnl": -0.0792952,
          "trades": 14,
          "win_rate": 0.21428571428571427
        },
        "CFX_USDT": {
          "gross_pnl": 0.0003235999999999994,
          "pf": 0.054095805763657225,
          "severe_pnl": -0.0276764,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "CHEEMS_USDT": {
          "gross_pnl": -0.0017571000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0057571,
          "trades": 1,
          "win_rate": 0.0
        },
        "CHIP_USDT": {
          "gross_pnl": 0.0023191,
          "pf": 0.04217796654744372,
          "severe_pnl": -0.1456809,
          "trades": 37,
          "win_rate": 0.08108108108108109
        },
        "CHR_USDT": {
          "gross_pnl": -0.08054510000000001,
          "pf": 0.00046550208341883636,
          "severe_pnl": -0.0925451,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "CHZ_USDT": {
          "gross_pnl": 0.006335,
          "pf": 0.07669653276037133,
          "severe_pnl": -0.109665,
          "trades": 29,
          "win_rate": 0.10344827586206896
        },
        "CKB_USDT": {
          "gross_pnl": -0.0064623,
          "pf": 0.0,
          "severe_pnl": -0.0144623,
          "trades": 2,
          "win_rate": 0.0
        },
        "CLO_USDT": {
          "gross_pnl": 0.0035674999999999873,
          "pf": 0.8170781947497431,
          "severe_pnl": -0.012432500000000013,
          "trades": 4,
          "win_rate": 0.5
        },
        "COAI_USDT": {
          "gross_pnl": -0.0043144,
          "pf": 0.06912182813483374,
          "severe_pnl": -0.08031440000000001,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "COLLECT_USDT": {
          "gross_pnl": 0.0389857,
          "pf": 0.648235938679099,
          "severe_pnl": -0.017014300000000003,
          "trades": 14,
          "win_rate": 0.35714285714285715
        },
        "COMP_USDT": {
          "gross_pnl": 0.0011765999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0068234,
          "trades": 2,
          "win_rate": 0.0
        },
        "COTI_USDT": {
          "gross_pnl": 0.0026076,
          "pf": 0.0,
          "severe_pnl": -0.0013924000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "CROSS_USDT": {
          "gross_pnl": 0.0037559,
          "pf": 0.0,
          "severe_pnl": -0.0122441,
          "trades": 4,
          "win_rate": 0.0
        },
        "CRO_USDT": {
          "gross_pnl": -0.05007789999999999,
          "pf": 0.09005790215368838,
          "severe_pnl": -0.1660779,
          "trades": 29,
          "win_rate": 0.1724137931034483
        },
        "CRV_USDT": {
          "gross_pnl": -0.012978999999999992,
          "pf": 0.04202308943477413,
          "severe_pnl": -0.264979,
          "trades": 63,
          "win_rate": 0.09523809523809523
        },
        "CTC_USDT": {
          "gross_pnl": 0.0028973000000000007,
          "pf": 0.0,
          "severe_pnl": -0.0331027,
          "trades": 9,
          "win_rate": 0.0
        },
        "CVX_USDT": {
          "gross_pnl": 0.0006053999999999999,
          "pf": 0.10975270783005243,
          "severe_pnl": -0.0393946,
          "trades": 10,
          "win_rate": 0.1
        },
        "CYS_USDT": {
          "gross_pnl": 0.0102117,
          "pf": 0.21319726301391512,
          "severe_pnl": -0.0457883,
          "trades": 14,
          "win_rate": 0.21428571428571427
        },
        "DASH_USDT": {
          "gross_pnl": 0.012046100000000004,
          "pf": 0.044768606899555474,
          "severe_pnl": -0.2719539000000001,
          "trades": 71,
          "win_rate": 0.08450704225352113
        },
        "DEEP_USDT": {
          "gross_pnl": -9.399999999999903e-06,
          "pf": 0.0,
          "severe_pnl": -0.0080094,
          "trades": 2,
          "win_rate": 0.0
        },
        "DEXE_USDT": {
          "gross_pnl": 0.17690519999999987,
          "pf": 0.5191639783452926,
          "severe_pnl": -0.3470948000000001,
          "trades": 131,
          "win_rate": 0.366412213740458
        },
        "DODO_USDT": {
          "gross_pnl": -0.2090999000000001,
          "pf": 0.39633613563128034,
          "severe_pnl": -0.5410999000000003,
          "trades": 83,
          "win_rate": 0.3493975903614458
        },
        "DOGE_USDT": {
          "gross_pnl": -0.009012599999999996,
          "pf": 0.0010006840600189206,
          "severe_pnl": -0.2890126,
          "trades": 70,
          "win_rate": 0.014285714285714285
        },
        "DOGS_USDT": {
          "gross_pnl": -0.0019606,
          "pf": 0.0,
          "severe_pnl": -0.0259606,
          "trades": 6,
          "win_rate": 0.0
        },
        "DOT_USDT": {
          "gross_pnl": 0.04166159999999999,
          "pf": 0.004260413960074973,
          "severe_pnl": -0.33033840000000003,
          "trades": 93,
          "win_rate": 0.021505376344086023
        },
        "DRAM_USDT": {
          "gross_pnl": -0.005098399999999994,
          "pf": 0.15809850882700943,
          "severe_pnl": -0.19709839999999998,
          "trades": 48,
          "win_rate": 0.20833333333333334
        },
        "DUSK_USDT": {
          "gross_pnl": 0.001822,
          "pf": 0.0,
          "severe_pnl": -0.0021780000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "DYDX_USDT": {
          "gross_pnl": 0.005420899999999999,
          "pf": 0.0,
          "severe_pnl": -0.0305791,
          "trades": 9,
          "win_rate": 0.0
        },
        "EDEN_USDT": {
          "gross_pnl": 0.011693399999999998,
          "pf": 0.9737919597904039,
          "severe_pnl": -0.0003066000000000019,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "EDGE_USDT": {
          "gross_pnl": 0.11006769999999999,
          "pf": 0.3021032768628182,
          "severe_pnl": -0.2579323,
          "trades": 92,
          "win_rate": 0.2826086956521739
        },
        "EDU_USDT": {
          "gross_pnl": -0.0028529999999999996,
          "pf": 0.052827467298861085,
          "severe_pnl": -0.022853,
          "trades": 5,
          "win_rate": 0.2
        },
        "EGLD_USDT": {
          "gross_pnl": 0.04302969999999998,
          "pf": 0.18759644316448656,
          "severe_pnl": -0.24497030000000006,
          "trades": 72,
          "win_rate": 0.2222222222222222
        },
        "EIGEN_USDT": {
          "gross_pnl": 0.03179100000000001,
          "pf": 0.13163838036591405,
          "severe_pnl": -0.31220899999999996,
          "trades": 86,
          "win_rate": 0.22093023255813954
        },
        "ELSA_USDT": {
          "gross_pnl": 0.05016799999999999,
          "pf": 1.5248081211736688,
          "severe_pnl": 0.022167999999999993,
          "trades": 7,
          "win_rate": 0.42857142857142855
        },
        "ENA_USDT": {
          "gross_pnl": 0.03620140000000002,
          "pf": 0.047427668751423686,
          "severe_pnl": -0.24379859999999995,
          "trades": 70,
          "win_rate": 0.1
        },
        "ENJ_USDT": {
          "gross_pnl": 0.014108800000000001,
          "pf": 0.18526882407663847,
          "severe_pnl": -0.0458912,
          "trades": 15,
          "win_rate": 0.13333333333333333
        },
        "ENSO_USDT": {
          "gross_pnl": 0.0008935999999999998,
          "pf": 0.0,
          "severe_pnl": -0.011106399999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "ENS_USDT": {
          "gross_pnl": -0.0161113,
          "pf": 0.04596665982335174,
          "severe_pnl": -0.0841113,
          "trades": 17,
          "win_rate": 0.11764705882352941
        },
        "EPIC_USDT": {
          "gross_pnl": 0.008046600000000001,
          "pf": 999,
          "severe_pnl": 0.004046600000000001,
          "trades": 1,
          "win_rate": 1.0
        },
        "ERA_USDT": {
          "gross_pnl": 0.0011718,
          "pf": 0.0,
          "severe_pnl": -0.0028282000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "ESPORTS_USDT": {
          "gross_pnl": 0.001393899999999941,
          "pf": 0.6699742604348885,
          "severe_pnl": -0.4426061000000002,
          "trades": 111,
          "win_rate": 0.46846846846846846
        },
        "ESP_USDT": {
          "gross_pnl": 0.0048017,
          "pf": 0.2979564062602893,
          "severe_pnl": -0.0031983000000000003,
          "trades": 2,
          "win_rate": 0.5
        },
        "ETC_USDT": {
          "gross_pnl": 0.0005571999999999997,
          "pf": 0.0,
          "severe_pnl": -0.08744280000000001,
          "trades": 22,
          "win_rate": 0.0
        },
        "ETHFI_USDT": {
          "gross_pnl": -0.004396499999999994,
          "pf": 0.06685041319922551,
          "severe_pnl": -0.3643965,
          "trades": 90,
          "win_rate": 0.07777777777777778
        },
        "ETH_USDT": {
          "gross_pnl": -0.027804500000000006,
          "pf": 0.0008747624102095724,
          "severe_pnl": -0.3238045,
          "trades": 74,
          "win_rate": 0.013513513513513514
        },
        "EUL_USDT": {
          "gross_pnl": 0.0062574,
          "pf": 0.6533312113314897,
          "severe_pnl": -0.0017426000000000004,
          "trades": 2,
          "win_rate": 0.5
        },
        "EVAA_USDT": {
          "gross_pnl": -0.40019439999999995,
          "pf": 0.329897965990075,
          "severe_pnl": -0.6961944000000002,
          "trades": 74,
          "win_rate": 0.28378378378378377
        },
        "EWY_USDT": {
          "gross_pnl": -0.016724200000000012,
          "pf": 0.027075252524615866,
          "severe_pnl": -0.3087242000000001,
          "trades": 73,
          "win_rate": 0.0410958904109589
        },
        "FET_USDT": {
          "gross_pnl": 0.0116708,
          "pf": 0.0017580949909325979,
          "severe_pnl": -0.25232920000000003,
          "trades": 66,
          "win_rate": 0.015151515151515152
        },
        "FF_USDT": {
          "gross_pnl": 0.014091,
          "pf": 0.15170464737890604,
          "severe_pnl": -0.053909,
          "trades": 17,
          "win_rate": 0.23529411764705882
        },
        "FHE_USDT": {
          "gross_pnl": -0.02147960000000001,
          "pf": 0.1849046470342681,
          "severe_pnl": -0.1614796,
          "trades": 35,
          "win_rate": 0.34285714285714286
        },
        "FIGHT_USDT": {
          "gross_pnl": 0.0048,
          "pf": 999,
          "severe_pnl": 0.0007999999999999995,
          "trades": 1,
          "win_rate": 1.0
        },
        "FILECOIN_USDT": {
          "gross_pnl": 0.025927900000000004,
          "pf": 0.014957820561872467,
          "severe_pnl": -0.1060721,
          "trades": 33,
          "win_rate": 0.09090909090909091
        },
        "FLOCK_USDT": {
          "gross_pnl": 0.0028316000000000036,
          "pf": 0.350600158941491,
          "severe_pnl": -0.0251684,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "FLOKI_USDT": {
          "gross_pnl": 0.0036544000000000004,
          "pf": 0.0042408626777364275,
          "severe_pnl": -0.10434559999999997,
          "trades": 27,
          "win_rate": 0.037037037037037035
        },
        "FLOW_USDT": {
          "gross_pnl": 0.0127841,
          "pf": 2.1960249999999997,
          "severe_pnl": 0.0047840999999999995,
          "trades": 2,
          "win_rate": 0.5
        },
        "FLR_USDT": {
          "gross_pnl": 0.0015198,
          "pf": 0.0,
          "severe_pnl": -0.0024802,
          "trades": 1,
          "win_rate": 0.0
        },
        "FOGO_USDT": {
          "gross_pnl": 0.038189299999999995,
          "pf": 2.8069096373268136,
          "severe_pnl": 0.0141893,
          "trades": 6,
          "win_rate": 0.5
        },
        "FOLKS_USDT": {
          "gross_pnl": -0.002311799999999996,
          "pf": 0.1958132300570304,
          "severe_pnl": -0.1703118,
          "trades": 42,
          "win_rate": 0.23809523809523808
        },
        "FORM_USDT": {
          "gross_pnl": 0.0024907,
          "pf": 0.0,
          "severe_pnl": -0.0055093,
          "trades": 2,
          "win_rate": 0.0
        },
        "FRAX_USDT": {
          "gross_pnl": -0.0049261,
          "pf": 0.0,
          "severe_pnl": -0.0089261,
          "trades": 1,
          "win_rate": 0.0
        },
        "F_USDT": {
          "gross_pnl": -0.0027466,
          "pf": 0.0,
          "severe_pnl": -0.0107466,
          "trades": 2,
          "win_rate": 0.0
        },
        "GALA_USDT": {
          "gross_pnl": 0.04210189999999999,
          "pf": 0.08659316897676715,
          "severe_pnl": -0.2738981,
          "trades": 79,
          "win_rate": 0.11392405063291139
        },
        "GAS_USDT": {
          "gross_pnl": 0.0039977,
          "pf": 0.313875745731331,
          "severe_pnl": -0.0040023,
          "trades": 2,
          "win_rate": 0.5
        },
        "GENIUS_USDT": {
          "gross_pnl": -0.0028708000000000015,
          "pf": 0.13566986341179885,
          "severe_pnl": -0.0148708,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "GIGGLE_USDT": {
          "gross_pnl": -0.0031449,
          "pf": 0.017738546152648804,
          "severe_pnl": -0.0151449,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "GLM_USDT": {
          "gross_pnl": 0.0019919,
          "pf": 0.0,
          "severe_pnl": -0.010008099999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "GOAT_USDT": {
          "gross_pnl": 0.0082769,
          "pf": 999,
          "severe_pnl": 0.0042769,
          "trades": 1,
          "win_rate": 1.0
        },
        "GPS_USDT": {
          "gross_pnl": 0.0178325,
          "pf": 0.3096408918066278,
          "severe_pnl": -0.022167500000000003,
          "trades": 10,
          "win_rate": 0.2
        },
        "GRAM_USDT": {
          "gross_pnl": 0.025200100000000003,
          "pf": 0.15321865091101683,
          "severe_pnl": -0.11079989999999999,
          "trades": 34,
          "win_rate": 0.11764705882352941
        },
        "GRASS_USDT": {
          "gross_pnl": 0.008485000000000001,
          "pf": 0.16451654817812264,
          "severe_pnl": -0.067515,
          "trades": 19,
          "win_rate": 0.2631578947368421
        },
        "GRT_USDT": {
          "gross_pnl": 0.0028883000000000003,
          "pf": 0.0,
          "severe_pnl": -0.029111699999999997,
          "trades": 8,
          "win_rate": 0.0
        },
        "GUA_USDT": {
          "gross_pnl": -0.0031747000000000025,
          "pf": 0.30888066057285474,
          "severe_pnl": -0.015174700000000003,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "GUN_USDT": {
          "gross_pnl": -0.009234,
          "pf": 0.13768582998220513,
          "severe_pnl": -0.049234,
          "trades": 10,
          "win_rate": 0.2
        },
        "G_USDT": {
          "gross_pnl": 0.1138305,
          "pf": 3.4931116301191154,
          "severe_pnl": 0.09383050000000001,
          "trades": 5,
          "win_rate": 0.4
        },
        "HBAR_USDT": {
          "gross_pnl": 0.025853499999999998,
          "pf": 0.02662185168554434,
          "severe_pnl": -0.1621465,
          "trades": 47,
          "win_rate": 0.0425531914893617
        },
        "HEI_USDT": {
          "gross_pnl": -0.006599299999999997,
          "pf": 0.21157372478487074,
          "severe_pnl": -0.2065993,
          "trades": 50,
          "win_rate": 0.2
        },
        "HIGH_USDT": {
          "gross_pnl": -0.024645499999999997,
          "pf": 0.05591183715233892,
          "severe_pnl": -0.0686455,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "HK50_USDT": {
          "gross_pnl": -0.003820200000000002,
          "pf": 0.01587638955479874,
          "severe_pnl": -0.03982020000000001,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "HMSTR_USDT": {
          "gross_pnl": 0.029583800000000004,
          "pf": 0.5680686582809225,
          "severe_pnl": -0.0224162,
          "trades": 13,
          "win_rate": 0.5384615384615384
        },
        "HNT_USDT": {
          "gross_pnl": 0.006541100000000001,
          "pf": 0.08760771976399641,
          "severe_pnl": -0.0174589,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "HOLO_USDT": {
          "gross_pnl": 0.0061683,
          "pf": 0.0,
          "severe_pnl": -0.013831700000000002,
          "trades": 5,
          "win_rate": 0.0
        },
        "HOME_USDT": {
          "gross_pnl": -0.0779163,
          "pf": 0.19981917652455636,
          "severe_pnl": -0.23391630000000002,
          "trades": 39,
          "win_rate": 0.23076923076923078
        },
        "HOT_USDT": {
          "gross_pnl": 0.006722500000000001,
          "pf": 0.4395237943522266,
          "severe_pnl": -0.005277499999999999,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "HYPE_USDT": {
          "gross_pnl": 0.027180999999999997,
          "pf": 0.03392650105420134,
          "severe_pnl": -0.13681900000000002,
          "trades": 41,
          "win_rate": 0.04878048780487805
        },
        "ICNT_USDT": {
          "gross_pnl": 0.010165200000000001,
          "pf": 999,
          "severe_pnl": 0.006165200000000001,
          "trades": 1,
          "win_rate": 1.0
        },
        "ICP_USDT": {
          "gross_pnl": -0.016158200000000008,
          "pf": 0.007399452546162829,
          "severe_pnl": -0.30815819999999994,
          "trades": 73,
          "win_rate": 0.0136986301369863
        },
        "ICX_USDT": {
          "gross_pnl": -0.0034204,
          "pf": 0.0,
          "severe_pnl": -0.0114204,
          "trades": 2,
          "win_rate": 0.0
        },
        "ID_USDT": {
          "gross_pnl": -0.004014900000000001,
          "pf": 0.0,
          "severe_pnl": -0.020014900000000002,
          "trades": 4,
          "win_rate": 0.0
        },
        "IMX_USDT": {
          "gross_pnl": 0.012926700000000001,
          "pf": 0.30879140085641876,
          "severe_pnl": -0.0110733,
          "trades": 6,
          "win_rate": 0.3333333333333333
        },
        "INDA_USDT": {
          "gross_pnl": 0.0081903,
          "pf": 0.08802644254342194,
          "severe_pnl": -0.0158097,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "INJ_USDT": {
          "gross_pnl": 0.03359400000000002,
          "pf": 0.004350048319096441,
          "severe_pnl": -0.374406,
          "trades": 102,
          "win_rate": 0.049019607843137254
        },
        "INTW_USDT": {
          "gross_pnl": -0.0275292,
          "pf": 0.0,
          "severe_pnl": -0.0355292,
          "trades": 2,
          "win_rate": 0.0
        },
        "INX_USDT": {
          "gross_pnl": -0.0013262999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0053263,
          "trades": 1,
          "win_rate": 0.0
        },
        "IN_USDT": {
          "gross_pnl": -0.0072495,
          "pf": 0.0,
          "severe_pnl": -0.0152495,
          "trades": 2,
          "win_rate": 0.0
        },
        "IOST_USDT": {
          "gross_pnl": 0.0016389,
          "pf": 0.0,
          "severe_pnl": -0.0023611,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTA_USDT": {
          "gross_pnl": -0.0038223000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0078223,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTX_USDT": {
          "gross_pnl": 0.0054325,
          "pf": 999,
          "severe_pnl": 0.0014324999999999997,
          "trades": 1,
          "win_rate": 1.0
        },
        "IRYS_USDT": {
          "gross_pnl": 0.0137931,
          "pf": 999,
          "severe_pnl": 0.0097931,
          "trades": 1,
          "win_rate": 1.0
        },
        "IWM_USDT": {
          "gross_pnl": 0.001241,
          "pf": 0.0,
          "severe_pnl": -0.002759,
          "trades": 1,
          "win_rate": 0.0
        },
        "JASMY_USDT": {
          "gross_pnl": 0.0006153000000000015,
          "pf": 0.04482493930211905,
          "severe_pnl": -0.16338470000000002,
          "trades": 41,
          "win_rate": 0.12195121951219512
        },
        "JCT_USDT": {
          "gross_pnl": -0.0028106000000000173,
          "pf": 0.3279909546787453,
          "severe_pnl": -0.07881060000000001,
          "trades": 19,
          "win_rate": 0.3684210526315789
        },
        "JP225_USDT": {
          "gross_pnl": 0.009593,
          "pf": 0.0,
          "severe_pnl": -0.022407000000000003,
          "trades": 8,
          "win_rate": 0.0
        },
        "JST_USDT": {
          "gross_pnl": 0.0040003999999999994,
          "pf": 0.0,
          "severe_pnl": -0.0279996,
          "trades": 8,
          "win_rate": 0.0
        },
        "JTO_USDT": {
          "gross_pnl": -0.015709300000000006,
          "pf": 0.03758611519491009,
          "severe_pnl": -0.28770930000000006,
          "trades": 68,
          "win_rate": 0.10294117647058823
        },
        "JUP_USDT": {
          "gross_pnl": 0.02758279999999999,
          "pf": 0.03424907363872818,
          "severe_pnl": -0.3884171999999999,
          "trades": 104,
          "win_rate": 0.07692307692307693
        },
        "KAIA_USDT": {
          "gross_pnl": 0.0034669,
          "pf": 0.0,
          "severe_pnl": -0.0165331,
          "trades": 5,
          "win_rate": 0.0
        },
        "KAITO_USDT": {
          "gross_pnl": 0.026211599999999995,
          "pf": 0.2777588904129038,
          "severe_pnl": -0.22178840000000005,
          "trades": 62,
          "win_rate": 0.22580645161290322
        },
        "KAS_USDT": {
          "gross_pnl": -0.0011449999999999984,
          "pf": 0.04930669060205842,
          "severe_pnl": -0.11714500000000003,
          "trades": 29,
          "win_rate": 0.034482758620689655
        },
        "KAT_USDT": {
          "gross_pnl": -0.014879999999999999,
          "pf": 0.24421563472671703,
          "severe_pnl": -0.02688,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "KITE_USDT": {
          "gross_pnl": 0.010833799999999994,
          "pf": 0.18205991778648742,
          "severe_pnl": -0.2171662000000001,
          "trades": 57,
          "win_rate": 0.2807017543859649
        },
        "KMNO_USDT": {
          "gross_pnl": 0.0059783,
          "pf": 0.49457499999999993,
          "severe_pnl": -0.0020217000000000004,
          "trades": 2,
          "win_rate": 0.5
        },
        "KORU_USDT": {
          "gross_pnl": -0.01799430000000002,
          "pf": 0.31654445560393085,
          "severe_pnl": -0.31799430000000006,
          "trades": 75,
          "win_rate": 0.25333333333333335
        },
        "KSM_USDT": {
          "gross_pnl": 0.0029203999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0050796,
          "trades": 2,
          "win_rate": 0.0
        },
        "KSTR_USDT": {
          "gross_pnl": -0.00040419999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0044042000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "LAB_USDT": {
          "gross_pnl": -0.11762480000000004,
          "pf": 0.5564140448621586,
          "severe_pnl": -0.36162479999999997,
          "trades": 61,
          "win_rate": 0.4262295081967213
        },
        "LDO_USDT": {
          "gross_pnl": 0.08169510000000002,
          "pf": 0.11009515980338529,
          "severe_pnl": -0.35030490000000014,
          "trades": 108,
          "win_rate": 0.1388888888888889
        },
        "LEAD_USDT": {
          "gross_pnl": -0.0007605000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0167605,
          "trades": 4,
          "win_rate": 0.0
        },
        "LIGHT_USDT": {
          "gross_pnl": -0.0203702,
          "pf": 0.0,
          "severe_pnl": -0.0643702,
          "trades": 11,
          "win_rate": 0.0
        },
        "LINEA_USDT": {
          "gross_pnl": -0.0012756,
          "pf": 0.0,
          "severe_pnl": -0.029275600000000006,
          "trades": 7,
          "win_rate": 0.0
        },
        "LINK_USDT": {
          "gross_pnl": 0.005448300000000001,
          "pf": 0.008592896951314467,
          "severe_pnl": -0.21455169999999998,
          "trades": 55,
          "win_rate": 0.01818181818181818
        },
        "LIT_USDT": {
          "gross_pnl": -0.031003799999999984,
          "pf": 0.11655940072992872,
          "severe_pnl": -0.7470038000000002,
          "trades": 179,
          "win_rate": 0.1787709497206704
        },
        "LRC_USDT": {
          "gross_pnl": -0.05425290000000002,
          "pf": 0.4384414784951378,
          "severe_pnl": -0.1262529,
          "trades": 18,
          "win_rate": 0.3888888888888889
        },
        "LTC_USDT": {
          "gross_pnl": -0.0007156999999999997,
          "pf": 0.0,
          "severe_pnl": -0.1527157,
          "trades": 38,
          "win_rate": 0.0
        },
        "LUMIA_USDT": {
          "gross_pnl": 0.1052948,
          "pf": 1.3378748916703371,
          "severe_pnl": 0.0332948,
          "trades": 18,
          "win_rate": 0.5555555555555556
        },
        "LUNANEW_USDT": {
          "gross_pnl": 0.0023575,
          "pf": 0.0,
          "severe_pnl": -0.0016425000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "LUNC_USDT": {
          "gross_pnl": 0.005146999999999999,
          "pf": 0.03425810226148256,
          "severe_pnl": -0.066853,
          "trades": 18,
          "win_rate": 0.05555555555555555
        },
        "MAGMA_USDT": {
          "gross_pnl": -0.1160387,
          "pf": 0.31965556633998415,
          "severe_pnl": -0.3960386999999999,
          "trades": 70,
          "win_rate": 0.32857142857142857
        },
        "MANA_USDT": {
          "gross_pnl": 0.0213707,
          "pf": 0.22923440063615408,
          "severe_pnl": -0.030629299999999998,
          "trades": 13,
          "win_rate": 0.15384615384615385
        },
        "MANTA_USDT": {
          "gross_pnl": 0.008099199999999999,
          "pf": 0.07312123201814598,
          "severe_pnl": -0.05590080000000001,
          "trades": 16,
          "win_rate": 0.0625
        },
        "MANTRA_USDT": {
          "gross_pnl": -0.10590049999999998,
          "pf": 0.0863834446765498,
          "severe_pnl": -0.1899005,
          "trades": 21,
          "win_rate": 0.19047619047619047
        },
        "MASK_USDT": {
          "gross_pnl": -0.0010046,
          "pf": 0.0,
          "severe_pnl": -0.0090046,
          "trades": 2,
          "win_rate": 0.0
        },
        "MAV_USDT": {
          "gross_pnl": 0.0059723000000000016,
          "pf": 0.28924407272211794,
          "severe_pnl": -0.010027699999999999,
          "trades": 4,
          "win_rate": 0.25
        },
        "MEGA_USDT": {
          "gross_pnl": -0.009788599999999998,
          "pf": 0.0,
          "severe_pnl": -0.041788599999999995,
          "trades": 8,
          "win_rate": 0.0
        },
        "MEME_USDT": {
          "gross_pnl": 0.0051286000000000005,
          "pf": 0.04265378800945608,
          "severe_pnl": -0.0188714,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "MERL_USDT": {
          "gross_pnl": -0.00012600000000000068,
          "pf": 0.15366511455066525,
          "severe_pnl": -0.060126,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "MET_USDT": {
          "gross_pnl": 0.0177253,
          "pf": 999,
          "severe_pnl": 0.0137253,
          "trades": 1,
          "win_rate": 1.0
        },
        "MINA_USDT": {
          "gross_pnl": 0.005412,
          "pf": 0.0,
          "severe_pnl": -0.0025880000000000005,
          "trades": 2,
          "win_rate": 0.0
        },
        "MITO_USDT": {
          "gross_pnl": 0.0030261999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0049738000000000004,
          "trades": 2,
          "win_rate": 0.0
        },
        "MMT_USDT": {
          "gross_pnl": 0.0328985,
          "pf": 0.306412057539016,
          "severe_pnl": -0.2271015,
          "trades": 65,
          "win_rate": 0.3076923076923077
        },
        "MNT_USDT": {
          "gross_pnl": -0.008060399999999999,
          "pf": 0.0,
          "severe_pnl": -0.0440604,
          "trades": 9,
          "win_rate": 0.0
        },
        "MONAD_USDT": {
          "gross_pnl": -0.013652899999999999,
          "pf": 0.021366593057767527,
          "severe_pnl": -0.08965290000000001,
          "trades": 19,
          "win_rate": 0.05263157894736842
        },
        "MOODENG_USDT": {
          "gross_pnl": -0.0049527,
          "pf": 0.0,
          "severe_pnl": -0.008952700000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "MORPHO_USDT": {
          "gross_pnl": 0.040070100000000004,
          "pf": 0.21485348840983104,
          "severe_pnl": -0.09192990000000001,
          "trades": 33,
          "win_rate": 0.21212121212121213
        },
        "MOVE_USDT": {
          "gross_pnl": 0.0017877000000000006,
          "pf": 0.0,
          "severe_pnl": -0.022212300000000004,
          "trades": 6,
          "win_rate": 0.0
        },
        "MOVR_USDT": {
          "gross_pnl": 0.0109091,
          "pf": 999,
          "severe_pnl": 0.0069091,
          "trades": 1,
          "win_rate": 1.0
        },
        "MSTU_USDT": {
          "gross_pnl": 0.0586279,
          "pf": 1.5877651422663914,
          "severe_pnl": 0.022627899999999996,
          "trades": 9,
          "win_rate": 0.5555555555555556
        },
        "MUBARAK_USDT": {
          "gross_pnl": -0.0022321,
          "pf": 0.0,
          "severe_pnl": -0.0062321,
          "trades": 1,
          "win_rate": 0.0
        },
        "MUU_USDT": {
          "gross_pnl": -0.013997299999999999,
          "pf": 0.0,
          "severe_pnl": -0.029997299999999998,
          "trades": 4,
          "win_rate": 0.0
        },
        "MVLL_USDT": {
          "gross_pnl": -0.007136399999999986,
          "pf": 0.39404305187683847,
          "severe_pnl": -0.1071364,
          "trades": 25,
          "win_rate": 0.44
        },
        "MYX_USDT": {
          "gross_pnl": 0.015631499999999996,
          "pf": 0.16972841802804708,
          "severe_pnl": -0.3843685000000001,
          "trades": 100,
          "win_rate": 0.28
        },
        "M_USDT": {
          "gross_pnl": -0.023340999999999997,
          "pf": 0.0,
          "severe_pnl": -0.027340999999999997,
          "trades": 1,
          "win_rate": 0.0
        },
        "NAORIS_USDT": {
          "gross_pnl": -0.0109442,
          "pf": 0.23730347960188,
          "severe_pnl": -0.0869442,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "NEAR_USDT": {
          "gross_pnl": -0.041411600000000014,
          "pf": 0.010010535042742717,
          "severe_pnl": -0.5734115999999998,
          "trades": 133,
          "win_rate": 0.045112781954887216
        },
        "NEIROCTO_USDT": {
          "gross_pnl": 0.0025189,
          "pf": 0.0,
          "severe_pnl": -0.0014811,
          "trades": 1,
          "win_rate": 0.0
        },
        "NEO_USDT": {
          "gross_pnl": 0.0077120999999999995,
          "pf": 999,
          "severe_pnl": 0.0037120999999999994,
          "trades": 1,
          "win_rate": 1.0
        },
        "NES_USDT": {
          "gross_pnl": 0.0288952,
          "pf": 0.31053298712247845,
          "severe_pnl": -0.047104799999999995,
          "trades": 19,
          "win_rate": 0.3157894736842105
        },
        "NEX_USDT": {
          "gross_pnl": -0.0390582,
          "pf": 0.0,
          "severe_pnl": -0.043058200000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "NGAS_USDT": {
          "gross_pnl": -0.007156000000000006,
          "pf": 0.013371071678661292,
          "severe_pnl": -0.235156,
          "trades": 57,
          "win_rate": 0.05263157894736842
        },
        "NICKEL_USDT": {
          "gross_pnl": 0.0025233,
          "pf": 0.0,
          "severe_pnl": -0.0134767,
          "trades": 4,
          "win_rate": 0.0
        },
        "NIGHT_USDT": {
          "gross_pnl": -0.021425,
          "pf": 0.054890218342636944,
          "severe_pnl": -0.077425,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "NIL_USDT": {
          "gross_pnl": 0.014689800000000003,
          "pf": 0.3881711244003417,
          "severe_pnl": -0.009310200000000001,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "NOM_USDT": {
          "gross_pnl": 0.008725799999999999,
          "pf": 0.28678527552878136,
          "severe_pnl": -0.019274200000000002,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "NOT_USDT": {
          "gross_pnl": 0.0007251999999999988,
          "pf": 0.0,
          "severe_pnl": -0.011274800000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "OFC_USDT": {
          "gross_pnl": -0.0104373,
          "pf": 0.022808595645425356,
          "severe_pnl": -0.034437300000000004,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "OGN_USDT": {
          "gross_pnl": 0.01199549999999999,
          "pf": 0.4821195653932918,
          "severe_pnl": -0.0800045,
          "trades": 23,
          "win_rate": 0.30434782608695654
        },
        "OG_USDT": {
          "gross_pnl": -0.0051262,
          "pf": 0.0,
          "severe_pnl": -0.009126200000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "OKB_USDT": {
          "gross_pnl": 0.0025978999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0054021,
          "trades": 2,
          "win_rate": 0.0
        },
        "OL_USDT": {
          "gross_pnl": 0.0176399,
          "pf": 999,
          "severe_pnl": 0.0136399,
          "trades": 1,
          "win_rate": 1.0
        },
        "ONDO_USDT": {
          "gross_pnl": -0.026223599999999993,
          "pf": 0.0644753599862449,
          "severe_pnl": -0.4222236,
          "trades": 99,
          "win_rate": 0.13131313131313133
        },
        "ONE_USDT": {
          "gross_pnl": -0.0333585,
          "pf": 0.0,
          "severe_pnl": -0.0413585,
          "trades": 2,
          "win_rate": 0.0
        },
        "ONG_USDT": {
          "gross_pnl": -0.0008263,
          "pf": 0.0,
          "severe_pnl": -0.0048263,
          "trades": 1,
          "win_rate": 0.0
        },
        "ONT_USDT": {
          "gross_pnl": 0.0020609,
          "pf": 0.0,
          "severe_pnl": -0.005939100000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "OPENAI_USDT": {
          "gross_pnl": 0.05489190000000002,
          "pf": 0.0,
          "severe_pnl": -0.3291081,
          "trades": 96,
          "win_rate": 0.0
        },
        "OPENLEDGER_USDT": {
          "gross_pnl": 0.0053298,
          "pf": 999,
          "severe_pnl": 0.0013298,
          "trades": 1,
          "win_rate": 1.0
        },
        "OPG_USDT": {
          "gross_pnl": 0.0513175,
          "pf": 0.35574112139764535,
          "severe_pnl": -0.04068250000000001,
          "trades": 23,
          "win_rate": 0.30434782608695654
        },
        "OPN_USDT": {
          "gross_pnl": -0.07472039999999999,
          "pf": 0.040504999747620674,
          "severe_pnl": -0.2547204,
          "trades": 45,
          "win_rate": 0.13333333333333333
        },
        "OP_USDT": {
          "gross_pnl": -0.016519600000000023,
          "pf": 0.028665675996372215,
          "severe_pnl": -0.3925196,
          "trades": 94,
          "win_rate": 0.06382978723404255
        },
        "ORCA_USDT": {
          "gross_pnl": 0.003326,
          "pf": 0.0,
          "severe_pnl": -0.008674000000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "ORDI_USDT": {
          "gross_pnl": 0.0515853,
          "pf": 0.07804535297906594,
          "severe_pnl": -0.43641469999999993,
          "trades": 122,
          "win_rate": 0.13934426229508196
        },
        "O_USDT": {
          "gross_pnl": -0.0379911,
          "pf": 0.18999310993379945,
          "severe_pnl": -0.1739911,
          "trades": 34,
          "win_rate": 0.3235294117647059
        },
        "PARTI_USDT": {
          "gross_pnl": 0.04492260000000001,
          "pf": 0.8394779806430273,
          "severe_pnl": -0.02707739999999997,
          "trades": 18,
          "win_rate": 0.5
        },
        "PAXG_USDT": {
          "gross_pnl": 0.0016939999999999998,
          "pf": 0.0,
          "severe_pnl": -0.07430600000000001,
          "trades": 19,
          "win_rate": 0.0
        },
        "PENDLE_USDT": {
          "gross_pnl": 0.021015699999999995,
          "pf": 0.07972925894590152,
          "severe_pnl": -0.1349843,
          "trades": 39,
          "win_rate": 0.1282051282051282
        },
        "PEOPLE_USDT": {
          "gross_pnl": 0.0018386,
          "pf": 0.0,
          "severe_pnl": -0.0021614,
          "trades": 1,
          "win_rate": 0.0
        },
        "PEPE_USDT": {
          "gross_pnl": 0.005042800000000003,
          "pf": 0.21603128054740958,
          "severe_pnl": -0.0309572,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "PHAROS_USDT": {
          "gross_pnl": 0.0009711,
          "pf": 0.0,
          "severe_pnl": -0.0030289,
          "trades": 1,
          "win_rate": 0.0
        },
        "PHA_USDT": {
          "gross_pnl": -0.0129454,
          "pf": 0.0,
          "severe_pnl": -0.0329454,
          "trades": 5,
          "win_rate": 0.0
        },
        "PIEVERSE_USDT": {
          "gross_pnl": 0.0101157,
          "pf": 0.33260185547798143,
          "severe_pnl": -0.009884299999999999,
          "trades": 5,
          "win_rate": 0.2
        },
        "PIPPIN_USDT": {
          "gross_pnl": 0.06525549999999998,
          "pf": 0.19415919740638915,
          "severe_pnl": -0.1867445000000001,
          "trades": 63,
          "win_rate": 0.23809523809523808
        },
        "PI_USDT": {
          "gross_pnl": 0.03328400000000001,
          "pf": 0.15373117767991312,
          "severe_pnl": -0.5827160000000001,
          "trades": 154,
          "win_rate": 0.17532467532467533
        },
        "PLUME_USDT": {
          "gross_pnl": 0.0072633,
          "pf": 0.32643841213793956,
          "severe_pnl": -0.0087367,
          "trades": 4,
          "win_rate": 0.25
        },
        "PNUT_USDT": {
          "gross_pnl": -0.0023463,
          "pf": 0.0,
          "severe_pnl": -0.0063463,
          "trades": 1,
          "win_rate": 0.0
        },
        "POL_USDT": {
          "gross_pnl": 0.058878600000000024,
          "pf": 0.06691114654297724,
          "severe_pnl": -0.19312140000000008,
          "trades": 63,
          "win_rate": 0.1111111111111111
        },
        "PONS_USDT": {
          "gross_pnl": -0.09438079999999999,
          "pf": 0.0,
          "severe_pnl": -0.09838079999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "POPCAT_USDT": {
          "gross_pnl": 0.0070121,
          "pf": 0.006077634305754851,
          "severe_pnl": -0.0049879,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "PORTAL_USDT": {
          "gross_pnl": 0.0017778,
          "pf": 0.0,
          "severe_pnl": -0.0022222,
          "trades": 1,
          "win_rate": 0.0
        },
        "POWER_USDT": {
          "gross_pnl": -0.007675299999999999,
          "pf": 0.018902103975751997,
          "severe_pnl": -0.027675299999999996,
          "trades": 5,
          "win_rate": 0.2
        },
        "POWR_USDT": {
          "gross_pnl": 0.0156682,
          "pf": 107.35506241331439,
          "severe_pnl": 0.007668199999999998,
          "trades": 2,
          "win_rate": 0.5
        },
        "PRL_USDT": {
          "gross_pnl": 0.0035398,
          "pf": 0.0,
          "severe_pnl": -0.0004602,
          "trades": 1,
          "win_rate": 0.0
        },
        "PROM_USDT": {
          "gross_pnl": -0.0007530000000000001,
          "pf": 0.0,
          "severe_pnl": -0.004753,
          "trades": 1,
          "win_rate": 0.0
        },
        "PTB_USDT": {
          "gross_pnl": 0.0046555,
          "pf": 999,
          "severe_pnl": 0.0006554999999999998,
          "trades": 1,
          "win_rate": 1.0
        },
        "PUMPFUN_USDT": {
          "gross_pnl": -0.019944200000000006,
          "pf": 0.09596300941539801,
          "severe_pnl": -0.4839442000000001,
          "trades": 116,
          "win_rate": 0.14655172413793102
        },
        "PUNDIX_USDT": {
          "gross_pnl": 0.0022357,
          "pf": 0.0,
          "severe_pnl": -0.0057643,
          "trades": 2,
          "win_rate": 0.0
        },
        "PYTH_USDT": {
          "gross_pnl": 0.02140739999999998,
          "pf": 0.08766183460082087,
          "severe_pnl": -0.35859260000000015,
          "trades": 95,
          "win_rate": 0.18947368421052632
        },
        "QNT_USDT": {
          "gross_pnl": -0.0065766,
          "pf": 0.0,
          "severe_pnl": -0.0225766,
          "trades": 4,
          "win_rate": 0.0
        },
        "QTUM_USDT": {
          "gross_pnl": 0.0036577000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0083423,
          "trades": 3,
          "win_rate": 0.0
        },
        "RAM_USDT": {
          "gross_pnl": 0.016244300000000003,
          "pf": 0.09544991217452241,
          "severe_pnl": -0.0397557,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "RARE_USDT": {
          "gross_pnl": 0.0418405,
          "pf": 999,
          "severe_pnl": 0.033840499999999996,
          "trades": 2,
          "win_rate": 1.0
        },
        "RAVE_USDT": {
          "gross_pnl": 0.1136961,
          "pf": 0.3135499144320344,
          "severe_pnl": -0.4263039,
          "trades": 135,
          "win_rate": 0.25925925925925924
        },
        "RAY_USDT": {
          "gross_pnl": -0.001307,
          "pf": 0.0,
          "severe_pnl": -0.005307,
          "trades": 1,
          "win_rate": 0.0
        },
        "RED_USDT": {
          "gross_pnl": -0.0088496,
          "pf": 0.0,
          "severe_pnl": -0.0128496,
          "trades": 1,
          "win_rate": 0.0
        },
        "RENDER_USDT": {
          "gross_pnl": -0.010494300000000002,
          "pf": 0.00045676605749429296,
          "severe_pnl": -0.15449430000000003,
          "trades": 36,
          "win_rate": 0.027777777777777776
        },
        "RESOLV_USDT": {
          "gross_pnl": 0.022868299999999994,
          "pf": 0.3201773527750329,
          "severe_pnl": -0.1291317,
          "trades": 38,
          "win_rate": 0.2631578947368421
        },
        "REZ_USDT": {
          "gross_pnl": 0.0033278,
          "pf": 0.0,
          "severe_pnl": -0.0006722,
          "trades": 1,
          "win_rate": 0.0
        },
        "RE_USDT": {
          "gross_pnl": -0.004300099999999994,
          "pf": 0.06049932230638791,
          "severe_pnl": -0.40030009999999994,
          "trades": 99,
          "win_rate": 0.10101010101010101
        },
        "RIF_USDT": {
          "gross_pnl": 0.05644019999999998,
          "pf": 0.5682268200992912,
          "severe_pnl": -0.019559800000000002,
          "trades": 19,
          "win_rate": 0.5789473684210527
        },
        "RLC_USDT": {
          "gross_pnl": 0.029556399999999997,
          "pf": 1.0507345822481116,
          "severe_pnl": 0.0015563999999999995,
          "trades": 7,
          "win_rate": 0.5714285714285714
        },
        "ROAM_USDT": {
          "gross_pnl": 0.02348399999999992,
          "pf": 0.91372939061654,
          "severe_pnl": -0.06451600000000005,
          "trades": 22,
          "win_rate": 0.5909090909090909
        },
        "ROBO_USDT": {
          "gross_pnl": 0.0130103,
          "pf": 0.6290694789081884,
          "severe_pnl": -0.0029897000000000005,
          "trades": 4,
          "win_rate": 0.25
        },
        "ROSE_USDT": {
          "gross_pnl": -0.013892799999999999,
          "pf": 0.0,
          "severe_pnl": -0.0338928,
          "trades": 5,
          "win_rate": 0.0
        },
        "RPL_USDT": {
          "gross_pnl": 0.0126329,
          "pf": 0.4339966195451751,
          "severe_pnl": -0.0073671000000000006,
          "trades": 5,
          "win_rate": 0.4
        },
        "RSR_USDT": {
          "gross_pnl": -0.0031369000000000006,
          "pf": 0.0,
          "severe_pnl": -0.027136900000000002,
          "trades": 6,
          "win_rate": 0.0
        },
        "RUNE_USDT": {
          "gross_pnl": 0.0020590999999999995,
          "pf": 0.17228337667581012,
          "severe_pnl": -0.013940899999999999,
          "trades": 4,
          "win_rate": 0.25
        },
        "RVN_USDT": {
          "gross_pnl": 0.009579500000000001,
          "pf": 0.28638024227705816,
          "severe_pnl": -0.0544205,
          "trades": 16,
          "win_rate": 0.1875
        },
        "SAFE_USDT": {
          "gross_pnl": -0.0029044000000000006,
          "pf": 0.12439903289455398,
          "severe_pnl": -0.018904400000000002,
          "trades": 4,
          "win_rate": 0.25
        },
        "SAGA_USDT": {
          "gross_pnl": 0.0014921,
          "pf": 0.0,
          "severe_pnl": -0.0065079000000000005,
          "trades": 2,
          "win_rate": 0.0
        },
        "SAHARA_USDT": {
          "gross_pnl": 0.0279113,
          "pf": 0.22426760614847563,
          "severe_pnl": -0.03608870000000001,
          "trades": 16,
          "win_rate": 0.1875
        },
        "SAND_USDT": {
          "gross_pnl": 0.0031025000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0048975,
          "trades": 2,
          "win_rate": 0.0
        },
        "SANTOS_USDT": {
          "gross_pnl": -0.0203065,
          "pf": 0.049426223284626224,
          "severe_pnl": -0.0363065,
          "trades": 4,
          "win_rate": 0.25
        },
        "SAPIEN_USDT": {
          "gross_pnl": 0.0013705999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0026294000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "SEI_USDT": {
          "gross_pnl": 0.014763900000000007,
          "pf": 0.006111887191113875,
          "severe_pnl": -0.19323610000000005,
          "trades": 52,
          "win_rate": 0.038461538461538464
        },
        "SENT_USDT": {
          "gross_pnl": 0.006126099999999999,
          "pf": 0.316775658350184,
          "severe_pnl": -0.0698739,
          "trades": 19,
          "win_rate": 0.42105263157894735
        },
        "SHIB_USDT": {
          "gross_pnl": 0.010411,
          "pf": 0.014244613928118145,
          "severe_pnl": -0.08558900000000001,
          "trades": 24,
          "win_rate": 0.041666666666666664
        },
        "SHLD_USDT": {
          "gross_pnl": -0.0057349,
          "pf": 0.0,
          "severe_pnl": -0.013734900000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "SIGN_USDT": {
          "gross_pnl": 0.0015246,
          "pf": 0.0,
          "severe_pnl": -0.0024754,
          "trades": 1,
          "win_rate": 0.0
        },
        "SIREN_USDT": {
          "gross_pnl": 0.0175055,
          "pf": 999,
          "severe_pnl": 0.0135055,
          "trades": 1,
          "win_rate": 1.0
        },
        "SKL_USDT": {
          "gross_pnl": -0.0352447,
          "pf": 0.468375286352439,
          "severe_pnl": -0.20324469999999997,
          "trades": 42,
          "win_rate": 0.3333333333333333
        },
        "SKR_USDT": {
          "gross_pnl": -0.0045412,
          "pf": 0.0,
          "severe_pnl": -0.020541200000000003,
          "trades": 4,
          "win_rate": 0.0
        },
        "SKYAI_USDT": {
          "gross_pnl": 0.17275039999999994,
          "pf": 0.3190687653088365,
          "severe_pnl": -0.4912495999999999,
          "trades": 166,
          "win_rate": 0.30120481927710846
        },
        "SKY_USDT": {
          "gross_pnl": -0.0139341,
          "pf": 0.06780453854281457,
          "severe_pnl": -0.07393409999999999,
          "trades": 15,
          "win_rate": 0.13333333333333333
        },
        "SLX_USDT": {
          "gross_pnl": 0.12489730000000004,
          "pf": 0.28903937712298466,
          "severe_pnl": -0.47110270000000004,
          "trades": 149,
          "win_rate": 0.2348993288590604
        },
        "SMH_USDT": {
          "gross_pnl": 0.0013353999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0026646000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "SNT_USDT": {
          "gross_pnl": 0.0074249,
          "pf": 0.2501679914775055,
          "severe_pnl": -0.0045750999999999995,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "SNXX_USDT": {
          "gross_pnl": 0.0393834,
          "pf": 1.7242362162643625,
          "severe_pnl": 0.011383399999999998,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "SNX_USDT": {
          "gross_pnl": -0.016124499999999996,
          "pf": 0.06952217294042064,
          "severe_pnl": -0.0721245,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "SOL_USDT": {
          "gross_pnl": 0.012747699999999997,
          "pf": 0.028936119420800176,
          "severe_pnl": -0.19525229999999996,
          "trades": 52,
          "win_rate": 0.019230769230769232
        },
        "SOXL_USDT": {
          "gross_pnl": -0.127025,
          "pf": 0.28645740769240663,
          "severe_pnl": -0.5990250000000003,
          "trades": 118,
          "win_rate": 0.2288135593220339
        },
        "SOXS_USDT": {
          "gross_pnl": -0.027033300000000014,
          "pf": 0.24394123858266356,
          "severe_pnl": -0.13103330000000005,
          "trades": 26,
          "win_rate": 0.2692307692307692
        },
        "SOXX_USDT": {
          "gross_pnl": 0.0106388,
          "pf": 0.11679483999007688,
          "severe_pnl": -0.021361200000000004,
          "trades": 8,
          "win_rate": 0.125
        },
        "SPELL_USDT": {
          "gross_pnl": 0.034939899999999996,
          "pf": 2.889763082333,
          "severe_pnl": 0.014939899999999999,
          "trades": 5,
          "win_rate": 0.2
        },
        "SPK_USDT": {
          "gross_pnl": -0.0098522,
          "pf": 0.0,
          "severe_pnl": -0.0138522,
          "trades": 1,
          "win_rate": 0.0
        },
        "SPY_USDT": {
          "gross_pnl": 1.33e-05,
          "pf": 0.0,
          "severe_pnl": -0.0039867,
          "trades": 1,
          "win_rate": 0.0
        },
        "SQD_USDT": {
          "gross_pnl": -0.0026153,
          "pf": 0.0,
          "severe_pnl": -0.014615300000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "SQQQ_USDT": {
          "gross_pnl": -0.0077564999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0157565,
          "trades": 2,
          "win_rate": 0.0
        },
        "STABLE_USDT": {
          "gross_pnl": 0.012023600000000002,
          "pf": 0.1796354508773576,
          "severe_pnl": -0.0279764,
          "trades": 10,
          "win_rate": 0.2
        },
        "STAR_USDT": {
          "gross_pnl": -0.038290899999999996,
          "pf": 0.0,
          "severe_pnl": -0.04229089999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "STEEM_USDT": {
          "gross_pnl": 0.0027933000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0012066999999999998,
          "trades": 1,
          "win_rate": 0.0
        },
        "STG_USDT": {
          "gross_pnl": 0.0251264,
          "pf": 0.08013812706140333,
          "severe_pnl": -0.030873600000000008,
          "trades": 14,
          "win_rate": 0.21428571428571427
        },
        "STORJ_USDT": {
          "gross_pnl": -0.0383189,
          "pf": 0.0,
          "severe_pnl": -0.042318900000000007,
          "trades": 1,
          "win_rate": 0.0
        },
        "STO_USDT": {
          "gross_pnl": -0.0022549,
          "pf": 0.0,
          "severe_pnl": -0.0102549,
          "trades": 2,
          "win_rate": 0.0
        },
        "STRK_USDT": {
          "gross_pnl": 0.004308999999999999,
          "pf": 0.08926723619299723,
          "severe_pnl": -0.075691,
          "trades": 20,
          "win_rate": 0.15
        },
        "STX_USDT": {
          "gross_pnl": 0.036649,
          "pf": 0.3815978384978012,
          "severe_pnl": -0.027351,
          "trades": 16,
          "win_rate": 0.3125
        },
        "SUI_USDT": {
          "gross_pnl": 0.014078399999999996,
          "pf": 0.01707466001472395,
          "severe_pnl": -0.2379216,
          "trades": 63,
          "win_rate": 0.06349206349206349
        },
        "SUPER_USDT": {
          "gross_pnl": -0.0011407000000000014,
          "pf": 0.24290331687475145,
          "severe_pnl": -0.013140700000000003,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "SUSHI_USDT": {
          "gross_pnl": 0.0213169,
          "pf": 2.3868485575669047,
          "severe_pnl": 0.005316899999999999,
          "trades": 4,
          "win_rate": 0.5
        },
        "SXT_USDT": {
          "gross_pnl": 0.07948449999999996,
          "pf": 0.5023535081799237,
          "severe_pnl": -0.2605155000000001,
          "trades": 85,
          "win_rate": 0.35294117647058826
        },
        "SYN_USDT": {
          "gross_pnl": -0.0585983,
          "pf": 0.39362898953310727,
          "severe_pnl": -0.6745983000000001,
          "trades": 154,
          "win_rate": 0.2792207792207792
        },
        "SYRUP_USDT": {
          "gross_pnl": -0.03693249999999999,
          "pf": 0.08874719486617057,
          "severe_pnl": -0.33293249999999996,
          "trades": 74,
          "win_rate": 0.0945945945945946
        },
        "S_USDT": {
          "gross_pnl": -0.0004713999999999992,
          "pf": 0.04824400125691135,
          "severe_pnl": -0.0284714,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "TAC_USDT": {
          "gross_pnl": 0.28504319999999994,
          "pf": 1.0192715420195781,
          "severe_pnl": 0.009043199999999939,
          "trades": 69,
          "win_rate": 0.463768115942029
        },
        "TAG_USDT": {
          "gross_pnl": 0.14162120000000003,
          "pf": 1.1514972308796159,
          "severe_pnl": 0.021621199999999997,
          "trades": 30,
          "win_rate": 0.3
        },
        "TAIKO_USDT": {
          "gross_pnl": -0.0166486,
          "pf": 0.22769645504785013,
          "severe_pnl": -0.0286486,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "TAO_USDT": {
          "gross_pnl": -0.0027102999999999997,
          "pf": 0.0,
          "severe_pnl": -0.13871029999999998,
          "trades": 34,
          "win_rate": 0.0
        },
        "TENDIES_USDT": {
          "gross_pnl": -0.166334,
          "pf": 0.0,
          "severe_pnl": -0.170334,
          "trades": 1,
          "win_rate": 0.0
        },
        "THETA_USDT": {
          "gross_pnl": 0.03859560000000001,
          "pf": 0.19779600320596263,
          "severe_pnl": -0.11740440000000003,
          "trades": 39,
          "win_rate": 0.23076923076923078
        },
        "THE_USDT": {
          "gross_pnl": 0.040600399999999995,
          "pf": 0.9522319440092514,
          "severe_pnl": -0.0033995999999999974,
          "trades": 11,
          "win_rate": 0.5454545454545454
        },
        "TIA_USDT": {
          "gross_pnl": 0.04332949999999999,
          "pf": 0.07229847775354996,
          "severe_pnl": -0.28467050000000005,
          "trades": 82,
          "win_rate": 0.13414634146341464
        },
        "TLM_USDT": {
          "gross_pnl": 0.14717679999999997,
          "pf": 0.49392836144175517,
          "severe_pnl": -0.15682320000000008,
          "trades": 76,
          "win_rate": 0.3026315789473684
        },
        "TNSR_USDT": {
          "gross_pnl": 0.0006418,
          "pf": 0.0,
          "severe_pnl": -0.0033582,
          "trades": 1,
          "win_rate": 0.0
        },
        "TOSHI_USDT": {
          "gross_pnl": 0.0529519,
          "pf": 14.032045570264767,
          "severe_pnl": 0.0409519,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "TOWNS_USDT": {
          "gross_pnl": -0.0111452,
          "pf": 0.1450640034874965,
          "severe_pnl": -0.04314520000000001,
          "trades": 8,
          "win_rate": 0.125
        },
        "TQQQ_USDT": {
          "gross_pnl": -0.0151483,
          "pf": 0.10163389234130699,
          "severe_pnl": -0.0791483,
          "trades": 16,
          "win_rate": 0.25
        },
        "TRADOOR_USDT": {
          "gross_pnl": 0.1484286,
          "pf": 0.9856264800531893,
          "severe_pnl": -0.003571400000000004,
          "trades": 38,
          "win_rate": 0.5526315789473685
        },
        "TRB_USDT": {
          "gross_pnl": -0.0018333999999999985,
          "pf": 0.006570667864737162,
          "severe_pnl": -0.0778334,
          "trades": 19,
          "win_rate": 0.05263157894736842
        },
        "TRIA_USDT": {
          "gross_pnl": -0.0598355,
          "pf": 0.3409853056634476,
          "severe_pnl": -0.6358354999999999,
          "trades": 144,
          "win_rate": 0.2847222222222222
        },
        "TRX_USDT": {
          "gross_pnl": -0.0016552999999999993,
          "pf": 0.0,
          "severe_pnl": -0.049655300000000006,
          "trades": 12,
          "win_rate": 0.0
        },
        "TRY_USDT": {
          "gross_pnl": -0.0018777000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0178777,
          "trades": 4,
          "win_rate": 0.0
        },
        "TSLL_USDT": {
          "gross_pnl": 0.0008834,
          "pf": 0.0,
          "severe_pnl": -0.0031166,
          "trades": 1,
          "win_rate": 0.0
        },
        "TURBO_USDT": {
          "gross_pnl": 0.0023255000000000007,
          "pf": 0.0,
          "severe_pnl": -0.017674500000000003,
          "trades": 5,
          "win_rate": 0.0
        },
        "TUT_USDT": {
          "gross_pnl": -0.0002787999999999983,
          "pf": 0.3009600526889075,
          "severe_pnl": -0.0082788,
          "trades": 2,
          "win_rate": 0.5
        },
        "TWT_USDT": {
          "gross_pnl": 0.0163798,
          "pf": 999,
          "severe_pnl": 0.0123798,
          "trades": 1,
          "win_rate": 1.0
        },
        "T_USDT": {
          "gross_pnl": 0.022562099999999967,
          "pf": 0.4483191949488362,
          "severe_pnl": -0.28943789999999997,
          "trades": 78,
          "win_rate": 0.2948717948717949
        },
        "UAI_USDT": {
          "gross_pnl": 0.11106269999999999,
          "pf": 0.4318423472708341,
          "severe_pnl": -0.12893729999999998,
          "trades": 60,
          "win_rate": 0.31666666666666665
        },
        "UMA_USDT": {
          "gross_pnl": -0.018135400000000003,
          "pf": 0.0,
          "severe_pnl": -0.026135400000000003,
          "trades": 2,
          "win_rate": 0.0
        },
        "UNI_USDT": {
          "gross_pnl": 0.039702600000000005,
          "pf": 0.09010197538413252,
          "severe_pnl": -0.3362974,
          "trades": 94,
          "win_rate": 0.1276595744680851
        },
        "UP_USDT": {
          "gross_pnl": 0.0064876000000000005,
          "pf": 0.18349330489394475,
          "severe_pnl": -0.005512400000000001,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "URNM_USDT": {
          "gross_pnl": -0.0009347000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0089347,
          "trades": 2,
          "win_rate": 0.0
        },
        "USELESS_USDT": {
          "gross_pnl": 0.0005622000000000058,
          "pf": 0.1299822140953493,
          "severe_pnl": -0.2194378,
          "trades": 55,
          "win_rate": 0.21818181818181817
        },
        "USO_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "USUAL_USDT": {
          "gross_pnl": -0.0024769999999999983,
          "pf": 0.11757816050962538,
          "severe_pnl": -0.050476999999999994,
          "trades": 12,
          "win_rate": 0.16666666666666666
        },
        "UVXY_USDT": {
          "gross_pnl": 0.0017143000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0142857,
          "trades": 4,
          "win_rate": 0.0
        },
        "VANRY_USDT": {
          "gross_pnl": 0.09271449999999999,
          "pf": 0.6594623909692129,
          "severe_pnl": -0.11528550000000001,
          "trades": 52,
          "win_rate": 0.34615384615384615
        },
        "VELO_USDT": {
          "gross_pnl": 0.0150782,
          "pf": 0.6566800828688817,
          "severe_pnl": -0.004921799999999999,
          "trades": 5,
          "win_rate": 0.4
        },
        "VELVET_USDT": {
          "gross_pnl": 0.07177570000000003,
          "pf": 0.5047132397905195,
          "severe_pnl": -0.5202243000000003,
          "trades": 148,
          "win_rate": 0.3310810810810811
        },
        "VET_USDT": {
          "gross_pnl": 0.0031617,
          "pf": 0.07119821327850656,
          "severe_pnl": -0.0408383,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "VINE_USDT": {
          "gross_pnl": 0.04414950000000001,
          "pf": 2.117185129332144,
          "severe_pnl": 0.012149499999999997,
          "trades": 8,
          "win_rate": 0.375
        },
        "VIRTUAL_USDT": {
          "gross_pnl": 0.0003913000000000076,
          "pf": 0.12303966435883537,
          "severe_pnl": -0.4116087000000001,
          "trades": 103,
          "win_rate": 0.17475728155339806
        },
        "VVV_USDT": {
          "gross_pnl": -0.0550742,
          "pf": 0.03873333683329042,
          "severe_pnl": -0.33507420000000004,
          "trades": 70,
          "win_rate": 0.07142857142857142
        },
        "WIF_USDT": {
          "gross_pnl": -0.024135800000000002,
          "pf": 0.02427973027742103,
          "severe_pnl": -0.32813580000000014,
          "trades": 76,
          "win_rate": 0.039473684210526314
        },
        "WLD_USDT": {
          "gross_pnl": 0.0346393,
          "pf": 0.0637611624459117,
          "severe_pnl": -0.5213607000000002,
          "trades": 139,
          "win_rate": 0.11510791366906475
        },
        "WLFI_USDT": {
          "gross_pnl": -0.003429200000000001,
          "pf": 0.011563447738685131,
          "severe_pnl": -0.09542919999999999,
          "trades": 23,
          "win_rate": 0.08695652173913043
        },
        "WOO_USDT": {
          "gross_pnl": 0.0015911,
          "pf": 0.0,
          "severe_pnl": -0.0024089000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "W_USDT": {
          "gross_pnl": -0.001006,
          "pf": 0.0,
          "severe_pnl": -0.017006,
          "trades": 4,
          "win_rate": 0.0
        },
        "XAI_USDT": {
          "gross_pnl": 0.0327637,
          "pf": 3.792932166301969,
          "severe_pnl": 0.0127637,
          "trades": 5,
          "win_rate": 0.8
        },
        "XAN_USDT": {
          "gross_pnl": -0.032020700000000006,
          "pf": 0.05540263115815816,
          "severe_pnl": -0.08802070000000001,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "XBI_USDT": {
          "gross_pnl": -0.032106899999999994,
          "pf": 0.0,
          "severe_pnl": -0.0881069,
          "trades": 14,
          "win_rate": 0.0
        },
        "XDC_USDT": {
          "gross_pnl": 0.00036909999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0076309,
          "trades": 2,
          "win_rate": 0.0
        },
        "XEC_USDT": {
          "gross_pnl": 0.07058020000000004,
          "pf": 0.49202830668900077,
          "severe_pnl": -0.2774198000000001,
          "trades": 87,
          "win_rate": 0.367816091954023
        },
        "XLM_USDT": {
          "gross_pnl": 0.0223748,
          "pf": 0.03507180696048903,
          "severe_pnl": -0.2536252,
          "trades": 69,
          "win_rate": 0.08695652173913043
        },
        "XLU_USDT": {
          "gross_pnl": -0.028909999999999998,
          "pf": 0.0,
          "severe_pnl": -0.04891,
          "trades": 5,
          "win_rate": 0.0
        },
        "XMR_USDT": {
          "gross_pnl": -0.019658399999999996,
          "pf": 0.0012876621110438076,
          "severe_pnl": -0.3236584,
          "trades": 76,
          "win_rate": 0.013157894736842105
        },
        "XPIN_USDT": {
          "gross_pnl": -0.004584800000000005,
          "pf": 0.510809785197983,
          "severe_pnl": -0.06458480000000003,
          "trades": 15,
          "win_rate": 0.4666666666666667
        },
        "XPL_USDT": {
          "gross_pnl": 0.04136539999999998,
          "pf": 0.11208836648485736,
          "severe_pnl": -0.3066346000000001,
          "trades": 87,
          "win_rate": 0.13793103448275862
        },
        "XPT_USDT": {
          "gross_pnl": -0.018015999999999997,
          "pf": 0.01652677684517896,
          "severe_pnl": -0.118016,
          "trades": 25,
          "win_rate": 0.04
        },
        "XRP_USDT": {
          "gross_pnl": -0.002958900000000001,
          "pf": 0.0,
          "severe_pnl": -0.11095890000000003,
          "trades": 27,
          "win_rate": 0.0
        },
        "XTZ_USDT": {
          "gross_pnl": -0.0029098,
          "pf": 0.0,
          "severe_pnl": -0.0189098,
          "trades": 4,
          "win_rate": 0.0
        },
        "XVS_USDT": {
          "gross_pnl": -0.0084778,
          "pf": 0.0,
          "severe_pnl": -0.0124778,
          "trades": 1,
          "win_rate": 0.0
        },
        "YFI_USDT": {
          "gross_pnl": 0.0022881999999999998,
          "pf": 0.07543238596136341,
          "severe_pnl": -0.013711800000000001,
          "trades": 4,
          "win_rate": 0.25
        },
        "ZAMA_USDT": {
          "gross_pnl": 0.0045709999999999995,
          "pf": 0.2947491824520268,
          "severe_pnl": -0.0034290000000000006,
          "trades": 2,
          "win_rate": 0.5
        },
        "ZBT_USDT": {
          "gross_pnl": -0.0292778,
          "pf": 0.22426827546196723,
          "severe_pnl": -0.30927780000000005,
          "trades": 70,
          "win_rate": 0.2
        },
        "ZEC_USDT": {
          "gross_pnl": 0.05324979999999999,
          "pf": 0.104486992912182,
          "severe_pnl": -0.36275020000000013,
          "trades": 104,
          "win_rate": 0.14423076923076922
        },
        "ZEN_USDT": {
          "gross_pnl": 0.0064352,
          "pf": 0.016928410023925033,
          "severe_pnl": -0.0695648,
          "trades": 19,
          "win_rate": 0.10526315789473684
        },
        "ZEST_USDT": {
          "gross_pnl": 0.0127625,
          "pf": 0.08862720290666073,
          "severe_pnl": -0.011237500000000001,
          "trades": 6,
          "win_rate": 0.3333333333333333
        },
        "ZETA_USDT": {
          "gross_pnl": -0.00028879999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0042888,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZINC_USDT": {
          "gross_pnl": 0.0017284999999999998,
          "pf": 0.0,
          "severe_pnl": -0.018271500000000003,
          "trades": 5,
          "win_rate": 0.0
        },
        "ZKC_USDT": {
          "gross_pnl": 0.00022429999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0037757,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZKP_USDT": {
          "gross_pnl": -0.0039591,
          "pf": 0.0,
          "severe_pnl": -0.0279591,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZKSYNC_USDT": {
          "gross_pnl": 0.029088700000000002,
          "pf": 0.2030426583762295,
          "severe_pnl": -0.04691130000000001,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "ZORA_USDT": {
          "gross_pnl": 0.007284199999999999,
          "pf": 0.3081004021090319,
          "severe_pnl": -0.012715800000000003,
          "trades": 5,
          "win_rate": 0.4
        },
        "ZRO_USDT": {
          "gross_pnl": 0.005481400000000003,
          "pf": 0.07981540555248084,
          "severe_pnl": -0.19851859999999993,
          "trades": 51,
          "win_rate": 0.09803921568627451
        },
        "ZRX_USDT": {
          "gross_pnl": -9.100000000000167e-06,
          "pf": 0.0,
          "severe_pnl": -0.020009100000000002,
          "trades": 5,
          "win_rate": 0.0
        }
      },
      "validation_depth_quartiles": [
        {
          "gross_pnl": -0.03367720000000097,
          "pf": 0.4392464404330406,
          "quartile": 1,
          "severe_pnl": -11.105677199999981,
          "trades": 2768,
          "upper": 8976.76524,
          "win_rate": 0.30346820809248554
        },
        {
          "gross_pnl": 1.2900148000000027,
          "pf": 0.2778289878145263,
          "quartile": 2,
          "severe_pnl": -10.817985199999963,
          "trades": 3027,
          "upper": 106972.33601999999,
          "win_rate": 0.2094482986455236
        },
        {
          "gross_pnl": 0.3034029000000008,
          "pf": 0.20319141629214785,
          "quartile": 3,
          "severe_pnl": -11.46859709999996,
          "trades": 2943,
          "upper": 1071304.435,
          "win_rate": 0.17974855589534489
        },
        {
          "gross_pnl": 0.08282700000000005,
          "pf": 0.0755858650539013,
          "quartile": 4,
          "severe_pnl": -11.117172999999967,
          "trades": 2800,
          "upper": null,
          "win_rate": 0.08642857142857142
        }
      ],
      "validation_pass": false,
      "validation_skips": {
        "invalid_path_json": 0,
        "missing_horizon_path": 117,
        "structure_not_selected": 76000,
        "symbol_cooldown": 3645
      },
      "validation_spread_quartiles": [
        {
          "gross_pnl": 0.18798280000000006,
          "pf": 0.16258538819452292,
          "quartile": 1,
          "severe_pnl": -11.900017200000029,
          "trades": 3022,
          "upper": 2.148689299527946,
          "win_rate": 0.1340172071475844
        },
        {
          "gross_pnl": 0.1234510000000017,
          "pf": 0.23006343556025194,
          "quartile": 2,
          "severe_pnl": -11.212548999999942,
          "trades": 2834,
          "upper": 4.268032437045758,
          "win_rate": 0.1961891319689485
        },
        {
          "gross_pnl": 0.44184460000000014,
          "pf": 0.2540945037060141,
          "quartile": 3,
          "severe_pnl": -11.154155399999924,
          "trades": 2899,
          "upper": 7.482229704451622,
          "win_rate": 0.19730941704035873
        },
        {
          "gross_pnl": 0.8892891000000015,
          "pf": 0.413927023838687,
          "quartile": 4,
          "severe_pnl": -10.242710899999956,
          "trades": 2783,
          "upper": null,
          "win_rate": 0.2558390226374416
        }
      ]
    },
    {
      "direction": "fade",
      "horizon_seconds": 60,
      "leave_best_symbol": -46.82724439999924,
      "structure": "contradict",
      "validation": {
        "gross_pnl": 2.5532923999999957,
        "pf": 0.10929535699086998,
        "severe_pnl": -46.80270759999924,
        "trades": 12339,
        "win_rate": 0.09222789529135263
      },
      "validation_by_symbol": {
        "0G_USDT": {
          "gross_pnl": -0.002456499999999999,
          "pf": 0.06775532416731724,
          "severe_pnl": -0.0784565,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "1000000BABYDOGE_USDT": {
          "gross_pnl": 0.0037342999999999994,
          "pf": 0.22556713788727323,
          "severe_pnl": -0.012265700000000001,
          "trades": 4,
          "win_rate": 0.5
        },
        "1000BONK_USDT": {
          "gross_pnl": 0.03628329999999999,
          "pf": 0.015353467743923356,
          "severe_pnl": -0.2077167000000001,
          "trades": 61,
          "win_rate": 0.06557377049180328
        },
        "1000BTT_USDT": {
          "gross_pnl": 0.0040605,
          "pf": 999,
          "severe_pnl": 6.049999999999979e-05,
          "trades": 1,
          "win_rate": 1.0
        },
        "2Z_USDT": {
          "gross_pnl": -0.00028209999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0042821000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "4_USDT": {
          "gross_pnl": 0.0010232000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0269768,
          "trades": 7,
          "win_rate": 0.0
        },
        "AAVE_USDT": {
          "gross_pnl": 0.011003399999999995,
          "pf": 0.0,
          "severe_pnl": -0.1649966,
          "trades": 44,
          "win_rate": 0.0
        },
        "ACE_USDT": {
          "gross_pnl": -0.0044551,
          "pf": 0.3489503836744935,
          "severe_pnl": -0.0124551,
          "trades": 2,
          "win_rate": 0.5
        },
        "ACH_USDT": {
          "gross_pnl": -0.0002737000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0082737,
          "trades": 2,
          "win_rate": 0.0
        },
        "ACU_USDT": {
          "gross_pnl": 0.0003985,
          "pf": 0.0,
          "severe_pnl": -0.0036015,
          "trades": 1,
          "win_rate": 0.0
        },
        "ACX_USDT": {
          "gross_pnl": -0.00023720000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0042372,
          "trades": 1,
          "win_rate": 0.0
        },
        "ADA_USDT": {
          "gross_pnl": 0.0200446,
          "pf": 0.0,
          "severe_pnl": -0.3599554,
          "trades": 95,
          "win_rate": 0.0
        },
        "AERGO_USDT": {
          "gross_pnl": 0.044199899999999986,
          "pf": 1.005204089336433,
          "severe_pnl": 0.00019989999999999938,
          "trades": 11,
          "win_rate": 0.36363636363636365
        },
        "AERO_USDT": {
          "gross_pnl": 0.017890600000000003,
          "pf": 0.005809789975364719,
          "severe_pnl": -0.19810940000000005,
          "trades": 54,
          "win_rate": 0.018518518518518517
        },
        "AGI_USDT": {
          "gross_pnl": 0.0043412,
          "pf": 0.025878594249201154,
          "severe_pnl": -0.0036588000000000007,
          "trades": 2,
          "win_rate": 0.5
        },
        "AGLD_USDT": {
          "gross_pnl": -0.002498000000000002,
          "pf": 0.1495589320058068,
          "severe_pnl": -0.05049800000000001,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "AIGENSYN_USDT": {
          "gross_pnl": 0.014679600000000003,
          "pf": 0.05822618396721936,
          "severe_pnl": -0.06132040000000001,
          "trades": 19,
          "win_rate": 0.05263157894736842
        },
        "AIOT_USDT": {
          "gross_pnl": -0.13859210000000005,
          "pf": 0.1565941724258662,
          "severe_pnl": -0.3545920999999998,
          "trades": 54,
          "win_rate": 0.25925925925925924
        },
        "AIOZ_USDT": {
          "gross_pnl": 0.004721400000000001,
          "pf": 0.0,
          "severe_pnl": -0.0032786,
          "trades": 2,
          "win_rate": 0.0
        },
        "AIO_USDT": {
          "gross_pnl": -0.0079943,
          "pf": 0.0,
          "severe_pnl": -0.0159943,
          "trades": 2,
          "win_rate": 0.0
        },
        "AKE_USDT": {
          "gross_pnl": 0.12907559999999996,
          "pf": 0.77837371303686,
          "severe_pnl": -0.10692440000000004,
          "trades": 59,
          "win_rate": 0.4745762711864407
        },
        "AKT_USDT": {
          "gross_pnl": 0.0050357,
          "pf": 999,
          "severe_pnl": 0.0010356999999999996,
          "trades": 1,
          "win_rate": 1.0
        },
        "ALCH_USDT": {
          "gross_pnl": -0.05725909999999999,
          "pf": 0.027673316650993575,
          "severe_pnl": -0.3092590999999998,
          "trades": 63,
          "win_rate": 0.06349206349206349
        },
        "ALGO_USDT": {
          "gross_pnl": 0.0071902,
          "pf": 0.0,
          "severe_pnl": -0.12480980000000001,
          "trades": 33,
          "win_rate": 0.0
        },
        "ALLO_USDT": {
          "gross_pnl": 0.011228600000000017,
          "pf": 0.09475601098079947,
          "severe_pnl": -0.7767714,
          "trades": 197,
          "win_rate": 0.14213197969543148
        },
        "ALT_USDT": {
          "gross_pnl": 0.0204865,
          "pf": 0.43269374933719496,
          "severe_pnl": -0.0155135,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "ANKR_USDT": {
          "gross_pnl": -0.008956699999999998,
          "pf": 0.07469445856063521,
          "severe_pnl": -0.0329567,
          "trades": 6,
          "win_rate": 0.5
        },
        "ANSEM_USDT": {
          "gross_pnl": 0.007807500000000035,
          "pf": 0.3479172804319494,
          "severe_pnl": -0.6761925000000001,
          "trades": 171,
          "win_rate": 0.3157894736842105
        },
        "ANTHROPIC_USDT": {
          "gross_pnl": 0.010293700000000003,
          "pf": 0.0,
          "severe_pnl": -0.06170630000000001,
          "trades": 18,
          "win_rate": 0.0
        },
        "APE_USDT": {
          "gross_pnl": 0.023686,
          "pf": 0.0,
          "severe_pnl": -0.24831400000000003,
          "trades": 68,
          "win_rate": 0.0
        },
        "APT_USDT": {
          "gross_pnl": 0.017533899999999995,
          "pf": 0.0,
          "severe_pnl": -0.3584661000000001,
          "trades": 94,
          "win_rate": 0.0
        },
        "ARB_USDT": {
          "gross_pnl": 0.0593466,
          "pf": 0.006420901972301304,
          "severe_pnl": -0.7006534000000004,
          "trades": 190,
          "win_rate": 0.021052631578947368
        },
        "ARKK_USDT": {
          "gross_pnl": 0.0405368,
          "pf": 13.011356961033876,
          "severe_pnl": 0.0245368,
          "trades": 4,
          "win_rate": 0.75
        },
        "ARKM_USDT": {
          "gross_pnl": 0.0027248,
          "pf": 0.0,
          "severe_pnl": -0.033275200000000005,
          "trades": 9,
          "win_rate": 0.0
        },
        "ARX_USDT": {
          "gross_pnl": 0.014426400000000002,
          "pf": 0.06615801895369915,
          "severe_pnl": -0.09757360000000001,
          "trades": 28,
          "win_rate": 0.14285714285714285
        },
        "AR_USDT": {
          "gross_pnl": 0.0108396,
          "pf": 0.010157170813635,
          "severe_pnl": -0.0531604,
          "trades": 16,
          "win_rate": 0.0625
        },
        "ASP_USDT": {
          "gross_pnl": 0.0058252,
          "pf": 999,
          "severe_pnl": 0.0018252,
          "trades": 1,
          "win_rate": 1.0
        },
        "ASTER_USDT": {
          "gross_pnl": 0.010139500000000003,
          "pf": 0.012994294900699904,
          "severe_pnl": -0.1258605,
          "trades": 34,
          "win_rate": 0.029411764705882353
        },
        "ATH_USDT": {
          "gross_pnl": 0.0117735,
          "pf": 0.23127759564912545,
          "severe_pnl": -0.0162265,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "ATOM_USDT": {
          "gross_pnl": 0.0241087,
          "pf": 0.0030378136720320987,
          "severe_pnl": -0.15989130000000007,
          "trades": 46,
          "win_rate": 0.021739130434782608
        },
        "AT_USDT": {
          "gross_pnl": 0.010006000000000001,
          "pf": 0.31968310898236224,
          "severe_pnl": -0.005993999999999999,
          "trades": 4,
          "win_rate": 0.25
        },
        "AVAAI_USDT": {
          "gross_pnl": 0.0019253999999999999,
          "pf": 0.3816039038762545,
          "severe_pnl": -0.010074600000000001,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "AVAX_USDT": {
          "gross_pnl": 0.0140489,
          "pf": 0.0,
          "severe_pnl": -0.14595110000000003,
          "trades": 40,
          "win_rate": 0.0
        },
        "AVNT_USDT": {
          "gross_pnl": 0.0087383,
          "pf": 0.015844771749510593,
          "severe_pnl": -0.10326170000000004,
          "trades": 28,
          "win_rate": 0.03571428571428571
        },
        "AWE_USDT": {
          "gross_pnl": 0.0023399,
          "pf": 0.0,
          "severe_pnl": -0.0056601,
          "trades": 2,
          "win_rate": 0.0
        },
        "AXS_USDT": {
          "gross_pnl": 0.0030264000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0329736,
          "trades": 9,
          "win_rate": 0.0
        },
        "A_USDT": {
          "gross_pnl": -0.0015012000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0135012,
          "trades": 3,
          "win_rate": 0.0
        },
        "B2_USDT": {
          "gross_pnl": 0.005148700000000001,
          "pf": 0.2871750000000002,
          "severe_pnl": -0.0028512999999999993,
          "trades": 2,
          "win_rate": 0.5
        },
        "B3_USDT": {
          "gross_pnl": 0.020834000000000002,
          "pf": 0.41837766821064265,
          "severe_pnl": -0.031166,
          "trades": 13,
          "win_rate": 0.3076923076923077
        },
        "BANANAS31_USDT": {
          "gross_pnl": 0.0019371999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0060628,
          "trades": 2,
          "win_rate": 0.0
        },
        "BAND_USDT": {
          "gross_pnl": -0.0005865,
          "pf": 0.0,
          "severe_pnl": -0.0045865,
          "trades": 1,
          "win_rate": 0.0
        },
        "BANK_USDT": {
          "gross_pnl": -0.007697800000000008,
          "pf": 0.1227691982564511,
          "severe_pnl": -0.34369780000000005,
          "trades": 84,
          "win_rate": 0.19047619047619047
        },
        "BAN_USDT": {
          "gross_pnl": 0.0007657,
          "pf": 0.0,
          "severe_pnl": -0.0032343,
          "trades": 1,
          "win_rate": 0.0
        },
        "BASED_USDT": {
          "gross_pnl": 0.004136100000000002,
          "pf": 0.004216945040977305,
          "severe_pnl": -0.1198639,
          "trades": 31,
          "win_rate": 0.06451612903225806
        },
        "BAS_USDT": {
          "gross_pnl": 0.006554,
          "pf": 0.4236704042793952,
          "severe_pnl": -0.013446,
          "trades": 5,
          "win_rate": 0.4
        },
        "BAT_USDT": {
          "gross_pnl": 0.0025351,
          "pf": 0.0,
          "severe_pnl": -0.0094649,
          "trades": 3,
          "win_rate": 0.0
        },
        "BCH_USDT": {
          "gross_pnl": -0.014813400000000011,
          "pf": 0.0,
          "severe_pnl": -0.26281340000000003,
          "trades": 62,
          "win_rate": 0.0
        },
        "BEAT_USDT": {
          "gross_pnl": 0.04598509999999998,
          "pf": 0.055149117270550135,
          "severe_pnl": -0.5940149000000001,
          "trades": 160,
          "win_rate": 0.0875
        },
        "BERA_USDT": {
          "gross_pnl": 0.007249699999999999,
          "pf": 0.02326379845144791,
          "severe_pnl": -0.024750300000000003,
          "trades": 8,
          "win_rate": 0.125
        },
        "BIANRENSHENG_USDT": {
          "gross_pnl": 0.011175799999999998,
          "pf": 0.007952619968669056,
          "severe_pnl": -0.0248242,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "BICO_USDT": {
          "gross_pnl": 0.011481599999999998,
          "pf": 0.014168824741871778,
          "severe_pnl": -0.0205184,
          "trades": 8,
          "win_rate": 0.125
        },
        "BIGTIME_USDT": {
          "gross_pnl": 0.0010289,
          "pf": 0.0,
          "severe_pnl": -0.0069711,
          "trades": 2,
          "win_rate": 0.0
        },
        "BILL_USDT": {
          "gross_pnl": -0.009712999999999989,
          "pf": 0.1342599365301915,
          "severe_pnl": -0.5977130000000003,
          "trades": 147,
          "win_rate": 0.14965986394557823
        },
        "BLAST_USDT": {
          "gross_pnl": -0.0836675,
          "pf": 0.25170956358779084,
          "severe_pnl": -0.1876675,
          "trades": 26,
          "win_rate": 0.34615384615384615
        },
        "BLESS_USDT": {
          "gross_pnl": 0.0665093,
          "pf": 0.18280101286344216,
          "severe_pnl": -0.0854907,
          "trades": 38,
          "win_rate": 0.23684210526315788
        },
        "BLUAI_USDT": {
          "gross_pnl": -0.0249975,
          "pf": 0.4550098826209356,
          "severe_pnl": -0.0489975,
          "trades": 6,
          "win_rate": 0.5
        },
        "BLUR_USDT": {
          "gross_pnl": 0.03486,
          "pf": 0.7201092615049178,
          "severe_pnl": -0.00914,
          "trades": 11,
          "win_rate": 0.2727272727272727
        },
        "BNB_USDT": {
          "gross_pnl": 0.0021260000000000003,
          "pf": 0.0,
          "severe_pnl": -0.05787400000000001,
          "trades": 15,
          "win_rate": 0.0
        },
        "BOBA_USDT": {
          "gross_pnl": 0.0058871,
          "pf": 0.0,
          "severe_pnl": -0.0021129,
          "trades": 2,
          "win_rate": 0.0
        },
        "BRETT_USDT": {
          "gross_pnl": 0.0329712,
          "pf": 0.23833216773291147,
          "severe_pnl": -0.059028800000000006,
          "trades": 23,
          "win_rate": 0.17391304347826086
        },
        "BREV_USDT": {
          "gross_pnl": 0.0015725000000000001,
          "pf": 0.0,
          "severe_pnl": -0.014427500000000003,
          "trades": 4,
          "win_rate": 0.0
        },
        "BR_USDT": {
          "gross_pnl": -0.0004898,
          "pf": 0.0,
          "severe_pnl": -0.0044898,
          "trades": 1,
          "win_rate": 0.0
        },
        "BSB_USDT": {
          "gross_pnl": 0.000501300000000004,
          "pf": 0.10498243366957245,
          "severe_pnl": -0.7434987000000001,
          "trades": 186,
          "win_rate": 0.14516129032258066
        },
        "BSV_USDT": {
          "gross_pnl": -0.013854100000000001,
          "pf": 0.0,
          "severe_pnl": -0.05385410000000001,
          "trades": 10,
          "win_rate": 0.0
        },
        "BTW_USDT": {
          "gross_pnl": 0.034187699999999994,
          "pf": 0.3095467079959378,
          "severe_pnl": -0.08981230000000001,
          "trades": 31,
          "win_rate": 0.16129032258064516
        },
        "BUILDONBOB_USDT": {
          "gross_pnl": 0.0227663,
          "pf": 2.3410298081496745,
          "severe_pnl": 0.006766299999999999,
          "trades": 4,
          "win_rate": 0.5
        },
        "BULLA_USDT": {
          "gross_pnl": -0.023437200000000002,
          "pf": 0.027800255014467177,
          "severe_pnl": -0.0634372,
          "trades": 10,
          "win_rate": 0.1
        },
        "CAKE_USDT": {
          "gross_pnl": 0.0035234,
          "pf": 0.0,
          "severe_pnl": -0.0404766,
          "trades": 11,
          "win_rate": 0.0
        },
        "CAP_USDT": {
          "gross_pnl": 0.0451674,
          "pf": 0.1939806228797209,
          "severe_pnl": -0.2028326,
          "trades": 62,
          "win_rate": 0.14516129032258066
        },
        "CASHCAT_USDT": {
          "gross_pnl": 0.013116600000000008,
          "pf": 0.4415526320640519,
          "severe_pnl": -0.09088340000000003,
          "trades": 26,
          "win_rate": 0.3076923076923077
        },
        "CC_USDT": {
          "gross_pnl": -0.0248156,
          "pf": 0.0,
          "severe_pnl": -0.07281560000000001,
          "trades": 12,
          "win_rate": 0.0
        },
        "CFX_USDT": {
          "gross_pnl": 7.319999999999948e-05,
          "pf": 0.0,
          "severe_pnl": -0.047926800000000006,
          "trades": 12,
          "win_rate": 0.0
        },
        "CHIP_USDT": {
          "gross_pnl": -0.0036745999999999992,
          "pf": 0.008581418596603406,
          "severe_pnl": -0.1956746,
          "trades": 48,
          "win_rate": 0.020833333333333332
        },
        "CHR_USDT": {
          "gross_pnl": 0.0022949,
          "pf": 0.0,
          "severe_pnl": -0.0057051,
          "trades": 2,
          "win_rate": 0.0
        },
        "CHZ_USDT": {
          "gross_pnl": 0.0095509,
          "pf": 0.0,
          "severe_pnl": -0.0584491,
          "trades": 17,
          "win_rate": 0.0
        },
        "CLO_USDT": {
          "gross_pnl": 0.0052516,
          "pf": 0.16372558738970952,
          "severe_pnl": -0.0067484,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "COAI_USDT": {
          "gross_pnl": 0.0035784999999999996,
          "pf": 0.04909406251153179,
          "severe_pnl": -0.0644215,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "COLLECT_USDT": {
          "gross_pnl": 0.0188843,
          "pf": 0.2189515779997576,
          "severe_pnl": -0.0451157,
          "trades": 16,
          "win_rate": 0.25
        },
        "COMP_USDT": {
          "gross_pnl": 0.0029025,
          "pf": 0.0,
          "severe_pnl": -0.013097500000000002,
          "trades": 4,
          "win_rate": 0.0
        },
        "COOKIE_USDT": {
          "gross_pnl": 0.0022700999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0017299000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "CORE_USDT": {
          "gross_pnl": 0.0053462,
          "pf": 0.0,
          "severe_pnl": -0.010653800000000001,
          "trades": 4,
          "win_rate": 0.0
        },
        "COW_USDT": {
          "gross_pnl": -0.0026864,
          "pf": 0.0,
          "severe_pnl": -0.0066864,
          "trades": 1,
          "win_rate": 0.0
        },
        "CROSS_USDT": {
          "gross_pnl": 0.0026462,
          "pf": 0.0,
          "severe_pnl": -0.0093538,
          "trades": 3,
          "win_rate": 0.0
        },
        "CRO_USDT": {
          "gross_pnl": 0.0023346999999999973,
          "pf": 0.020674364107162547,
          "severe_pnl": -0.1536653,
          "trades": 39,
          "win_rate": 0.02564102564102564
        },
        "CRV_USDT": {
          "gross_pnl": 0.015534599999999997,
          "pf": 0.0,
          "severe_pnl": -0.2684654,
          "trades": 71,
          "win_rate": 0.0
        },
        "CTC_USDT": {
          "gross_pnl": 0.0345353,
          "pf": 0.0,
          "severe_pnl": -0.06146470000000001,
          "trades": 24,
          "win_rate": 0.0
        },
        "CTR_USDT": {
          "gross_pnl": -0.017094,
          "pf": 0.0,
          "severe_pnl": -0.021094,
          "trades": 1,
          "win_rate": 0.0
        },
        "CVX_USDT": {
          "gross_pnl": 0.0123026,
          "pf": 0.18032350285260104,
          "severe_pnl": -0.0196974,
          "trades": 8,
          "win_rate": 0.125
        },
        "CYS_USDT": {
          "gross_pnl": 0.0221453,
          "pf": 0.3159490271009534,
          "severe_pnl": -0.013854700000000001,
          "trades": 9,
          "win_rate": 0.3333333333333333
        },
        "C_USDT": {
          "gross_pnl": 0.004016700000000001,
          "pf": 999,
          "severe_pnl": 1.670000000000057e-05,
          "trades": 1,
          "win_rate": 1.0
        },
        "DASH_USDT": {
          "gross_pnl": -0.0055941,
          "pf": 0.0006773114978561261,
          "severe_pnl": -0.3695941000000001,
          "trades": 91,
          "win_rate": 0.01098901098901099
        },
        "DEEP_USDT": {
          "gross_pnl": -0.0020227,
          "pf": 0.0,
          "severe_pnl": -0.0220227,
          "trades": 5,
          "win_rate": 0.0
        },
        "DEXE_USDT": {
          "gross_pnl": 0.056946699999999996,
          "pf": 0.1759041282324355,
          "severe_pnl": -0.4510533,
          "trades": 127,
          "win_rate": 0.16535433070866143
        },
        "DODO_USDT": {
          "gross_pnl": -0.09193209999999999,
          "pf": 0.262013251229295,
          "severe_pnl": -0.5439320999999998,
          "trades": 113,
          "win_rate": 0.2743362831858407
        },
        "DOGE_USDT": {
          "gross_pnl": 0.010898000000000003,
          "pf": 0.0,
          "severe_pnl": -0.13310200000000003,
          "trades": 36,
          "win_rate": 0.0
        },
        "DOGS_USDT": {
          "gross_pnl": 0.0033039,
          "pf": 0.0,
          "severe_pnl": -0.0246961,
          "trades": 7,
          "win_rate": 0.0
        },
        "DOT_USDT": {
          "gross_pnl": 0.0492904,
          "pf": 0.0,
          "severe_pnl": -0.27870960000000006,
          "trades": 82,
          "win_rate": 0.0
        },
        "DRAM_USDT": {
          "gross_pnl": -0.01661850000000001,
          "pf": 0.008336615059680325,
          "severe_pnl": -0.22461850000000003,
          "trades": 52,
          "win_rate": 0.019230769230769232
        },
        "DYDX_USDT": {
          "gross_pnl": 0.004492899999999999,
          "pf": 0.0,
          "severe_pnl": -0.0595071,
          "trades": 16,
          "win_rate": 0.0
        },
        "EDEN_USDT": {
          "gross_pnl": 0.0037198,
          "pf": 0.0,
          "severe_pnl": -0.0162802,
          "trades": 5,
          "win_rate": 0.0
        },
        "EDGE_USDT": {
          "gross_pnl": -0.027842799999999997,
          "pf": 0.041096819385875755,
          "severe_pnl": -0.3478428,
          "trades": 80,
          "win_rate": 0.1375
        },
        "EDU_USDT": {
          "gross_pnl": 0.006984799999999999,
          "pf": 0.08925369459446439,
          "severe_pnl": -0.017015200000000005,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "EGLD_USDT": {
          "gross_pnl": -0.015038000000000006,
          "pf": 0.018866926992580423,
          "severe_pnl": -0.5270379999999998,
          "trades": 128,
          "win_rate": 0.046875
        },
        "EIGEN_USDT": {
          "gross_pnl": -0.0320177,
          "pf": 0.011697098109172386,
          "severe_pnl": -0.8720176999999999,
          "trades": 210,
          "win_rate": 0.023809523809523808
        },
        "ELSA_USDT": {
          "gross_pnl": 0.0076329,
          "pf": 0.12602759578515144,
          "severe_pnl": -0.0723671,
          "trades": 20,
          "win_rate": 0.2
        },
        "ENA_USDT": {
          "gross_pnl": -0.015837499999999997,
          "pf": 0.004125265391941736,
          "severe_pnl": -0.2518374999999999,
          "trades": 59,
          "win_rate": 0.01694915254237288
        },
        "ENJ_USDT": {
          "gross_pnl": 0.0037207999999999994,
          "pf": 0.032531391952036456,
          "severe_pnl": -0.044279200000000005,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "ENSO_USDT": {
          "gross_pnl": 0.00014230000000000015,
          "pf": 0.0,
          "severe_pnl": -0.0118577,
          "trades": 3,
          "win_rate": 0.0
        },
        "ENS_USDT": {
          "gross_pnl": 0.008507700000000003,
          "pf": 0.0018616709788013357,
          "severe_pnl": -0.18749230000000003,
          "trades": 49,
          "win_rate": 0.02040816326530612
        },
        "EPIC_USDT": {
          "gross_pnl": -0.0002543,
          "pf": 0.0,
          "severe_pnl": -0.0042543,
          "trades": 1,
          "win_rate": 0.0
        },
        "ERA_USDT": {
          "gross_pnl": 0.0009322,
          "pf": 0.0,
          "severe_pnl": -0.0030678,
          "trades": 1,
          "win_rate": 0.0
        },
        "ESPORTS_USDT": {
          "gross_pnl": -0.14546730000000008,
          "pf": 0.34645129937583846,
          "severe_pnl": -0.5454673000000001,
          "trades": 100,
          "win_rate": 0.32
        },
        "ESP_USDT": {
          "gross_pnl": 0.00025599999999999993,
          "pf": 0.0,
          "severe_pnl": -0.011744000000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "ETC_USDT": {
          "gross_pnl": -0.002588,
          "pf": 0.0,
          "severe_pnl": -0.078588,
          "trades": 19,
          "win_rate": 0.0
        },
        "ETHFI_USDT": {
          "gross_pnl": 0.017382599999999998,
          "pf": 0.000578113457054565,
          "severe_pnl": -0.5786174000000002,
          "trades": 149,
          "win_rate": 0.013422818791946308
        },
        "ETH_USDT": {
          "gross_pnl": -0.004827600000000003,
          "pf": 0.0,
          "severe_pnl": -0.3488276000000001,
          "trades": 86,
          "win_rate": 0.0
        },
        "EUL_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "EVAA_USDT": {
          "gross_pnl": -0.04705629999999998,
          "pf": 0.4013867862236576,
          "severe_pnl": -0.24305629999999992,
          "trades": 49,
          "win_rate": 0.42857142857142855
        },
        "EWJ_USDT": {
          "gross_pnl": -0.0009682,
          "pf": 0.0,
          "severe_pnl": -0.0049682,
          "trades": 1,
          "win_rate": 0.0
        },
        "EWY_USDT": {
          "gross_pnl": 0.017682799999999995,
          "pf": 0.0,
          "severe_pnl": -0.20631720000000006,
          "trades": 56,
          "win_rate": 0.0
        },
        "FET_USDT": {
          "gross_pnl": 0.0063797,
          "pf": 0.0,
          "severe_pnl": -0.28962030000000005,
          "trades": 74,
          "win_rate": 0.0
        },
        "FF_USDT": {
          "gross_pnl": 0.0011436000000000016,
          "pf": 0.1299176562572177,
          "severe_pnl": -0.0508564,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "FHE_USDT": {
          "gross_pnl": -0.007599399999999999,
          "pf": 0.07837005674583764,
          "severe_pnl": -0.19159940000000006,
          "trades": 46,
          "win_rate": 0.10869565217391304
        },
        "FILECOIN_USDT": {
          "gross_pnl": -0.004052699999999999,
          "pf": 0.0,
          "severe_pnl": -0.08805270000000001,
          "trades": 21,
          "win_rate": 0.0
        },
        "FLOCK_USDT": {
          "gross_pnl": 0.020023100000000002,
          "pf": 0.14462314355773043,
          "severe_pnl": -0.015976900000000002,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "FLOKI_USDT": {
          "gross_pnl": 0.007069300000000001,
          "pf": 0.0,
          "severe_pnl": -0.0889307,
          "trades": 24,
          "win_rate": 0.0
        },
        "FLOW_USDT": {
          "gross_pnl": -0.0011823,
          "pf": 0.0,
          "severe_pnl": -0.013182300000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "FLUID_USDT": {
          "gross_pnl": -0.005602200000000001,
          "pf": 0.0,
          "severe_pnl": -0.009602200000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "FOGO_USDT": {
          "gross_pnl": -0.0040964999999999994,
          "pf": 0.0,
          "severe_pnl": -0.0120965,
          "trades": 2,
          "win_rate": 0.0
        },
        "FOLKS_USDT": {
          "gross_pnl": 0.0018398000000000004,
          "pf": 0.02417351624092567,
          "severe_pnl": -0.15816020000000006,
          "trades": 40,
          "win_rate": 0.05
        },
        "FORM_USDT": {
          "gross_pnl": 0.0004796,
          "pf": 0.0,
          "severe_pnl": -0.0035204,
          "trades": 1,
          "win_rate": 0.0
        },
        "FRAX_USDT": {
          "gross_pnl": 0.0057036000000000005,
          "pf": 0.36294282464560157,
          "severe_pnl": -0.0022964,
          "trades": 2,
          "win_rate": 0.5
        },
        "GALA_USDT": {
          "gross_pnl": 0.004994500000000005,
          "pf": 0.001428953011307239,
          "severe_pnl": -0.40300549999999996,
          "trades": 102,
          "win_rate": 0.00980392156862745
        },
        "GAS_USDT": {
          "gross_pnl": 0.0048544,
          "pf": 999,
          "severe_pnl": 0.0008544,
          "trades": 1,
          "win_rate": 1.0
        },
        "GENIUS_USDT": {
          "gross_pnl": -0.0025363999999999986,
          "pf": 0.0,
          "severe_pnl": -0.018536399999999998,
          "trades": 4,
          "win_rate": 0.0
        },
        "GIGGLE_USDT": {
          "gross_pnl": 0.0018748,
          "pf": 0.0,
          "severe_pnl": -0.0021252,
          "trades": 1,
          "win_rate": 0.0
        },
        "GLM_USDT": {
          "gross_pnl": 0.0029595999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0090404,
          "trades": 3,
          "win_rate": 0.0
        },
        "GMT_USDT": {
          "gross_pnl": 0.0026991,
          "pf": 0.0,
          "severe_pnl": -0.005300900000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "GPS_USDT": {
          "gross_pnl": -0.0042167,
          "pf": 0.0,
          "severe_pnl": -0.0282167,
          "trades": 6,
          "win_rate": 0.0
        },
        "GRAM_USDT": {
          "gross_pnl": -0.010875799999999996,
          "pf": 0.0,
          "severe_pnl": -0.1228758,
          "trades": 28,
          "win_rate": 0.0
        },
        "GRASS_USDT": {
          "gross_pnl": -0.0037325,
          "pf": 0.027313359892786777,
          "severe_pnl": -0.09573250000000003,
          "trades": 23,
          "win_rate": 0.08695652173913043
        },
        "GRIFFAIN_USDT": {
          "gross_pnl": -0.0099379,
          "pf": 0.0,
          "severe_pnl": -0.0139379,
          "trades": 1,
          "win_rate": 0.0
        },
        "GRT_USDT": {
          "gross_pnl": -0.0005420000000000003,
          "pf": 0.0,
          "severe_pnl": -0.036542000000000005,
          "trades": 9,
          "win_rate": 0.0
        },
        "GUA_USDT": {
          "gross_pnl": -0.0119486,
          "pf": 0.0,
          "severe_pnl": -0.0319486,
          "trades": 5,
          "win_rate": 0.0
        },
        "GUN_USDT": {
          "gross_pnl": 0.0178677,
          "pf": 0.0035330241066178943,
          "severe_pnl": -0.0381323,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "G_USDT": {
          "gross_pnl": -0.0042035,
          "pf": 0.14803132340104327,
          "severe_pnl": -0.020203500000000003,
          "trades": 4,
          "win_rate": 0.25
        },
        "HBAR_USDT": {
          "gross_pnl": -0.007659100000000004,
          "pf": 0.0,
          "severe_pnl": -0.2636590999999999,
          "trades": 64,
          "win_rate": 0.0
        },
        "HEI_USDT": {
          "gross_pnl": 0.019508800000000007,
          "pf": 0.10005546028120395,
          "severe_pnl": -0.17249120000000004,
          "trades": 48,
          "win_rate": 0.1875
        },
        "HIGH_USDT": {
          "gross_pnl": 0.020382500000000005,
          "pf": 0.2416701968066301,
          "severe_pnl": -0.04761750000000001,
          "trades": 17,
          "win_rate": 0.29411764705882354
        },
        "HK50_USDT": {
          "gross_pnl": 0.0032072999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0447927,
          "trades": 12,
          "win_rate": 0.0
        },
        "HMSTR_USDT": {
          "gross_pnl": -0.006356500000000001,
          "pf": 0.0294407894736842,
          "severe_pnl": -0.0383565,
          "trades": 8,
          "win_rate": 0.125
        },
        "HNT_USDT": {
          "gross_pnl": 0.001404,
          "pf": 0.0,
          "severe_pnl": -0.006596,
          "trades": 2,
          "win_rate": 0.0
        },
        "HOLO_USDT": {
          "gross_pnl": 0.0004238,
          "pf": 0.0,
          "severe_pnl": -0.0035762,
          "trades": 1,
          "win_rate": 0.0
        },
        "HOME_USDT": {
          "gross_pnl": -0.02140119999999999,
          "pf": 0.1970636757936191,
          "severe_pnl": -0.2414012,
          "trades": 55,
          "win_rate": 0.21818181818181817
        },
        "HOT_USDT": {
          "gross_pnl": 0.013121800000000003,
          "pf": 0.614626767324295,
          "severe_pnl": -0.010878199999999998,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "HYPE_USDT": {
          "gross_pnl": -0.002926299999999998,
          "pf": 0.0,
          "severe_pnl": -0.21492630000000001,
          "trades": 53,
          "win_rate": 0.0
        },
        "ICP_USDT": {
          "gross_pnl": 0.0020784000000000015,
          "pf": 0.008680833370945263,
          "severe_pnl": -0.2899216,
          "trades": 73,
          "win_rate": 0.0136986301369863
        },
        "ICX_USDT": {
          "gross_pnl": 0.0008452999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0031547000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "ID_USDT": {
          "gross_pnl": 0.0085682,
          "pf": 0.013726285275517837,
          "severe_pnl": -0.0114318,
          "trades": 5,
          "win_rate": 0.2
        },
        "IMX_USDT": {
          "gross_pnl": 0.0022914999999999997,
          "pf": 0.0,
          "severe_pnl": -0.025708500000000002,
          "trades": 7,
          "win_rate": 0.0
        },
        "INDA_USDT": {
          "gross_pnl": 0.0231991,
          "pf": 0.21437286299669978,
          "severe_pnl": -0.05280090000000001,
          "trades": 19,
          "win_rate": 0.2631578947368421
        },
        "INJ_USDT": {
          "gross_pnl": 0.019656100000000006,
          "pf": 0.0,
          "severe_pnl": -0.3323439000000001,
          "trades": 88,
          "win_rate": 0.0
        },
        "INTW_USDT": {
          "gross_pnl": 0.004784,
          "pf": 0.3801859930833058,
          "severe_pnl": -0.015216,
          "trades": 5,
          "win_rate": 0.2
        },
        "IN_USDT": {
          "gross_pnl": 0.0020773,
          "pf": 0.0,
          "severe_pnl": -0.0019227000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "IOTA_USDT": {
          "gross_pnl": -0.007137999999999999,
          "pf": 0.0,
          "severe_pnl": -0.015137999999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "IOTX_USDT": {
          "gross_pnl": -0.0007779,
          "pf": 0.0,
          "severe_pnl": -0.0047779,
          "trades": 1,
          "win_rate": 0.0
        },
        "IO_USDT": {
          "gross_pnl": 0.002381,
          "pf": 0.0,
          "severe_pnl": -0.005619,
          "trades": 2,
          "win_rate": 0.0
        },
        "JASMY_USDT": {
          "gross_pnl": 0.017830999999999996,
          "pf": 0.040559921333937356,
          "severe_pnl": -0.22216899999999995,
          "trades": 60,
          "win_rate": 0.06666666666666667
        },
        "JCT_USDT": {
          "gross_pnl": -0.014580099999999999,
          "pf": 0.040801872699984885,
          "severe_pnl": -0.054580100000000006,
          "trades": 10,
          "win_rate": 0.1
        },
        "JP225_USDT": {
          "gross_pnl": 0.00029239999999999995,
          "pf": 0.006093661839383109,
          "severe_pnl": -0.0317076,
          "trades": 8,
          "win_rate": 0.125
        },
        "JST_USDT": {
          "gross_pnl": -0.0022494,
          "pf": 0.0,
          "severe_pnl": -0.026249400000000003,
          "trades": 6,
          "win_rate": 0.0
        },
        "JTO_USDT": {
          "gross_pnl": 0.0016018999999999983,
          "pf": 0.0044274395930603725,
          "severe_pnl": -0.33839810000000003,
          "trades": 85,
          "win_rate": 0.023529411764705882
        },
        "JUP_USDT": {
          "gross_pnl": 0.023095700000000004,
          "pf": 0.001666502080654229,
          "severe_pnl": -0.5449043000000005,
          "trades": 142,
          "win_rate": 0.02112676056338028
        },
        "KAIA_USDT": {
          "gross_pnl": -0.0011522000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0211522,
          "trades": 5,
          "win_rate": 0.0
        },
        "KAITO_USDT": {
          "gross_pnl": 0.027259899999999993,
          "pf": 0.1702280277183394,
          "severe_pnl": -0.18474010000000002,
          "trades": 53,
          "win_rate": 0.18867924528301888
        },
        "KAS_USDT": {
          "gross_pnl": 0.010229299999999997,
          "pf": 0.0,
          "severe_pnl": -0.1017707,
          "trades": 28,
          "win_rate": 0.0
        },
        "KERNEL_USDT": {
          "gross_pnl": 0.0019642,
          "pf": 0.0,
          "severe_pnl": -0.0020358,
          "trades": 1,
          "win_rate": 0.0
        },
        "KITE_USDT": {
          "gross_pnl": -2.350000000000095e-05,
          "pf": 0.034195462046011864,
          "severe_pnl": -0.12402349999999998,
          "trades": 31,
          "win_rate": 0.06451612903225806
        },
        "KMNO_USDT": {
          "gross_pnl": -0.0050477000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0330477,
          "trades": 7,
          "win_rate": 0.0
        },
        "KORU_USDT": {
          "gross_pnl": -0.027810400000000002,
          "pf": 0.14579494443137062,
          "severe_pnl": -0.3078104,
          "trades": 70,
          "win_rate": 0.17142857142857143
        },
        "KSM_USDT": {
          "gross_pnl": 0.0005858000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0114142,
          "trades": 3,
          "win_rate": 0.0
        },
        "KSTR_USDT": {
          "gross_pnl": -0.0007822,
          "pf": 0.0,
          "severe_pnl": -0.0087822,
          "trades": 2,
          "win_rate": 0.0
        },
        "LAB_USDT": {
          "gross_pnl": 0.1503517,
          "pf": 0.8089050945072979,
          "severe_pnl": -0.07764830000000003,
          "trades": 57,
          "win_rate": 0.3333333333333333
        },
        "LAYER_USDT": {
          "gross_pnl": 0.0016103,
          "pf": 0.0,
          "severe_pnl": -0.0023897,
          "trades": 1,
          "win_rate": 0.0
        },
        "LDO_USDT": {
          "gross_pnl": -0.002985499999999999,
          "pf": 0.0022265312772346774,
          "severe_pnl": -0.6549855,
          "trades": 163,
          "win_rate": 0.018404907975460124
        },
        "LEAD_USDT": {
          "gross_pnl": -0.0005056,
          "pf": 0.0,
          "severe_pnl": -0.024505600000000002,
          "trades": 6,
          "win_rate": 0.0
        },
        "LIGHT_USDT": {
          "gross_pnl": -0.008376399999999999,
          "pf": 0.0,
          "severe_pnl": -0.04037640000000001,
          "trades": 8,
          "win_rate": 0.0
        },
        "LINEA_USDT": {
          "gross_pnl": 0.005570900000000001,
          "pf": 0.0,
          "severe_pnl": -0.0224291,
          "trades": 7,
          "win_rate": 0.0
        },
        "LINK_USDT": {
          "gross_pnl": 0.020451000000000007,
          "pf": 0.0,
          "severe_pnl": -0.2075490000000001,
          "trades": 57,
          "win_rate": 0.0
        },
        "LIT_USDT": {
          "gross_pnl": 0.001127199999999998,
          "pf": 0.006441741669314568,
          "severe_pnl": -0.6228728000000001,
          "trades": 156,
          "win_rate": 0.02564102564102564
        },
        "LRC_USDT": {
          "gross_pnl": 0.13672280000000003,
          "pf": 0.9176667625512703,
          "severe_pnl": -0.011277200000000013,
          "trades": 37,
          "win_rate": 0.3783783783783784
        },
        "LTC_USDT": {
          "gross_pnl": 0.0123804,
          "pf": 0.0,
          "severe_pnl": -0.17561959999999996,
          "trades": 47,
          "win_rate": 0.0
        },
        "LUMIA_USDT": {
          "gross_pnl": 0.014398000000000003,
          "pf": 0.32903258147296244,
          "severe_pnl": -0.069602,
          "trades": 21,
          "win_rate": 0.19047619047619047
        },
        "LUNANEW_USDT": {
          "gross_pnl": -0.0012958,
          "pf": 0.0,
          "severe_pnl": -0.0092958,
          "trades": 2,
          "win_rate": 0.0
        },
        "LUNC_USDT": {
          "gross_pnl": 0.005323699999999999,
          "pf": 0.0,
          "severe_pnl": -0.1786763,
          "trades": 46,
          "win_rate": 0.0
        },
        "LYN_USDT": {
          "gross_pnl": 0.0209598,
          "pf": 4.758206704558637,
          "severe_pnl": 0.0129598,
          "trades": 2,
          "win_rate": 0.5
        },
        "MAGMA_USDT": {
          "gross_pnl": 0.123553,
          "pf": 0.41848099875955563,
          "severe_pnl": -0.240447,
          "trades": 91,
          "win_rate": 0.27472527472527475
        },
        "MANA_USDT": {
          "gross_pnl": 0.0085954,
          "pf": 0.0884319240167827,
          "severe_pnl": -0.0514046,
          "trades": 15,
          "win_rate": 0.13333333333333333
        },
        "MANTA_USDT": {
          "gross_pnl": -0.008454399999999999,
          "pf": 0.0,
          "severe_pnl": -0.0484544,
          "trades": 10,
          "win_rate": 0.0
        },
        "MANTRA_USDT": {
          "gross_pnl": 0.030410300000000005,
          "pf": 0.47594324694716034,
          "severe_pnl": -0.037589700000000004,
          "trades": 17,
          "win_rate": 0.29411764705882354
        },
        "MASK_USDT": {
          "gross_pnl": 0.0005086,
          "pf": 0.0,
          "severe_pnl": -0.0034914,
          "trades": 1,
          "win_rate": 0.0
        },
        "MAV_USDT": {
          "gross_pnl": 0.0020182,
          "pf": 0.0,
          "severe_pnl": -0.0099818,
          "trades": 3,
          "win_rate": 0.0
        },
        "MEGA_USDT": {
          "gross_pnl": 0.00014729999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0078527,
          "trades": 2,
          "win_rate": 0.0
        },
        "MEME_USDT": {
          "gross_pnl": 0.0003488999999999992,
          "pf": 0.0,
          "severe_pnl": -0.0236511,
          "trades": 6,
          "win_rate": 0.0
        },
        "MERL_USDT": {
          "gross_pnl": 0.0073925,
          "pf": 0.0,
          "severe_pnl": -0.0366075,
          "trades": 11,
          "win_rate": 0.0
        },
        "METIS_USDT": {
          "gross_pnl": -1.1400000000000006e-05,
          "pf": 0.0,
          "severe_pnl": -0.0080114,
          "trades": 2,
          "win_rate": 0.0
        },
        "MET_USDT": {
          "gross_pnl": 0.009194299999999999,
          "pf": 0.1605481255422912,
          "severe_pnl": -0.0028057000000000004,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "MEW_USDT": {
          "gross_pnl": 0.0054659999999999995,
          "pf": 999,
          "severe_pnl": 0.0014659999999999994,
          "trades": 1,
          "win_rate": 1.0
        },
        "ME_USDT": {
          "gross_pnl": 0.0028754,
          "pf": 0.0,
          "severe_pnl": -0.0011246,
          "trades": 1,
          "win_rate": 0.0
        },
        "MINA_USDT": {
          "gross_pnl": -0.0021821,
          "pf": 0.0,
          "severe_pnl": -0.0101821,
          "trades": 2,
          "win_rate": 0.0
        },
        "MIRA_USDT": {
          "gross_pnl": -0.0026718,
          "pf": 0.0,
          "severe_pnl": -0.014671799999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "MITO_USDT": {
          "gross_pnl": 0.037441800000000004,
          "pf": 2.580886071483176,
          "severe_pnl": 0.0134418,
          "trades": 6,
          "win_rate": 0.6666666666666666
        },
        "MMT_USDT": {
          "gross_pnl": 0.026805699999999995,
          "pf": 0.06475713848585946,
          "severe_pnl": -0.18919430000000004,
          "trades": 54,
          "win_rate": 0.12962962962962962
        },
        "MNT_USDT": {
          "gross_pnl": 0.0017173000000000008,
          "pf": 0.00711739593949158,
          "severe_pnl": -0.042282700000000006,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "MOCA_USDT": {
          "gross_pnl": 0.0044743,
          "pf": 999,
          "severe_pnl": 0.00047429999999999955,
          "trades": 1,
          "win_rate": 1.0
        },
        "MONAD_USDT": {
          "gross_pnl": 0.029624500000000005,
          "pf": 0.003188843638898831,
          "severe_pnl": -0.10637550000000003,
          "trades": 34,
          "win_rate": 0.029411764705882353
        },
        "MOODENG_USDT": {
          "gross_pnl": -0.024295900000000002,
          "pf": 0.0,
          "severe_pnl": -0.028295900000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "MORPHO_USDT": {
          "gross_pnl": 0.015895900000000004,
          "pf": 0.0731219856774005,
          "severe_pnl": -0.0761041,
          "trades": 23,
          "win_rate": 0.08695652173913043
        },
        "MOVE_USDT": {
          "gross_pnl": 0.0018034,
          "pf": 0.0,
          "severe_pnl": -0.0101966,
          "trades": 3,
          "win_rate": 0.0
        },
        "MSTU_USDT": {
          "gross_pnl": 0.035344299999999995,
          "pf": 1.4403691178586846,
          "severe_pnl": 0.0073443,
          "trades": 7,
          "win_rate": 0.42857142857142855
        },
        "MUBARAK_USDT": {
          "gross_pnl": 0.0014482,
          "pf": 0.0,
          "severe_pnl": -0.0025518,
          "trades": 1,
          "win_rate": 0.0
        },
        "MUU_USDT": {
          "gross_pnl": 0.0013679000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0106321,
          "trades": 3,
          "win_rate": 0.0
        },
        "MVLL_USDT": {
          "gross_pnl": -0.014116000000000004,
          "pf": 0.11394829792976946,
          "severe_pnl": -0.12211600000000003,
          "trades": 27,
          "win_rate": 0.14814814814814814
        },
        "MYX_USDT": {
          "gross_pnl": 0.04769809999999999,
          "pf": 0.16645378149232404,
          "severe_pnl": -0.2763019000000001,
          "trades": 81,
          "win_rate": 0.1728395061728395
        },
        "NAORIS_USDT": {
          "gross_pnl": 0.028931599999999995,
          "pf": 0.18594780434442879,
          "severe_pnl": -0.039068399999999996,
          "trades": 17,
          "win_rate": 0.29411764705882354
        },
        "NEAR_USDT": {
          "gross_pnl": 0.03546039999999999,
          "pf": 0.0007383473212894638,
          "severe_pnl": -0.32453959999999993,
          "trades": 90,
          "win_rate": 0.03333333333333333
        },
        "NEO_USDT": {
          "gross_pnl": -0.00197,
          "pf": 0.0,
          "severe_pnl": -0.00997,
          "trades": 2,
          "win_rate": 0.0
        },
        "NES_USDT": {
          "gross_pnl": 0.003133300000000001,
          "pf": 0.018809893604657308,
          "severe_pnl": -0.09286670000000001,
          "trades": 24,
          "win_rate": 0.041666666666666664
        },
        "NEX_USDT": {
          "gross_pnl": -0.007327200000000001,
          "pf": 0.0,
          "severe_pnl": -0.0113272,
          "trades": 1,
          "win_rate": 0.0
        },
        "NGAS_USDT": {
          "gross_pnl": 0.0106228,
          "pf": 0.004355807725731277,
          "severe_pnl": -0.1853772,
          "trades": 49,
          "win_rate": 0.02040816326530612
        },
        "NICKEL_USDT": {
          "gross_pnl": -0.0013926000000000001,
          "pf": 0.0,
          "severe_pnl": -0.045392600000000005,
          "trades": 11,
          "win_rate": 0.0
        },
        "NIGHT_USDT": {
          "gross_pnl": 0.0032165000000000006,
          "pf": 0.023970133025639894,
          "severe_pnl": -0.0527835,
          "trades": 14,
          "win_rate": 0.07142857142857142
        },
        "NIL_USDT": {
          "gross_pnl": 0.0045055,
          "pf": 0.0,
          "severe_pnl": -0.0354945,
          "trades": 10,
          "win_rate": 0.0
        },
        "NOM_USDT": {
          "gross_pnl": -0.0007783999999999998,
          "pf": 0.0,
          "severe_pnl": -0.012778399999999999,
          "trades": 3,
          "win_rate": 0.0
        },
        "NOT_USDT": {
          "gross_pnl": 0.0034424000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0125576,
          "trades": 4,
          "win_rate": 0.0
        },
        "OFC_USDT": {
          "gross_pnl": -0.0056544,
          "pf": 0.0,
          "severe_pnl": -0.0256544,
          "trades": 5,
          "win_rate": 0.0
        },
        "OGN_USDT": {
          "gross_pnl": -0.0010858999999999999,
          "pf": 0.017127662904148258,
          "severe_pnl": -0.0690859,
          "trades": 17,
          "win_rate": 0.11764705882352941
        },
        "OG_USDT": {
          "gross_pnl": 0.010534800000000002,
          "pf": 0.2831114317570671,
          "severe_pnl": -0.005465199999999999,
          "trades": 4,
          "win_rate": 0.5
        },
        "OKB_USDT": {
          "gross_pnl": 0.0002468,
          "pf": 0.0,
          "severe_pnl": -0.0037532,
          "trades": 1,
          "win_rate": 0.0
        },
        "OL_USDT": {
          "gross_pnl": -0.0018363000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0098363,
          "trades": 2,
          "win_rate": 0.0
        },
        "ONDO_USDT": {
          "gross_pnl": 0.037518,
          "pf": 0.02161342486267452,
          "severe_pnl": -0.4664820000000001,
          "trades": 126,
          "win_rate": 0.03968253968253968
        },
        "ONE_USDT": {
          "gross_pnl": 0.0018022,
          "pf": 0.0,
          "severe_pnl": -0.0181978,
          "trades": 5,
          "win_rate": 0.0
        },
        "ONT_USDT": {
          "gross_pnl": 0.0006586000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0033414,
          "trades": 1,
          "win_rate": 0.0
        },
        "OPENAI_USDT": {
          "gross_pnl": 0.0638776,
          "pf": 0.0030968653286080777,
          "severe_pnl": -0.29612240000000006,
          "trades": 90,
          "win_rate": 0.011111111111111112
        },
        "OPG_USDT": {
          "gross_pnl": 0.004203799999999996,
          "pf": 0.02309813179446823,
          "severe_pnl": -0.08379620000000002,
          "trades": 22,
          "win_rate": 0.09090909090909091
        },
        "OPN_USDT": {
          "gross_pnl": 0.018578200000000003,
          "pf": 0.03838847241340823,
          "severe_pnl": -0.16542179999999998,
          "trades": 46,
          "win_rate": 0.06521739130434782
        },
        "OP_USDT": {
          "gross_pnl": 0.07439470000000002,
          "pf": 0.016657048464979316,
          "severe_pnl": -0.6216052999999997,
          "trades": 174,
          "win_rate": 0.028735632183908046
        },
        "ORCA_USDT": {
          "gross_pnl": -0.0008403,
          "pf": 0.0,
          "severe_pnl": -0.0048403000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "ORDI_USDT": {
          "gross_pnl": 0.015501499999999994,
          "pf": 2.334977969990502e-05,
          "severe_pnl": -0.49249850000000023,
          "trades": 127,
          "win_rate": 0.007874015748031496
        },
        "O_USDT": {
          "gross_pnl": 0.012988399999999999,
          "pf": 0.1273878144838164,
          "severe_pnl": -0.1990116,
          "trades": 53,
          "win_rate": 0.11320754716981132
        },
        "PARTI_USDT": {
          "gross_pnl": 0.009243399999999999,
          "pf": 0.28623246423225535,
          "severe_pnl": -0.0307566,
          "trades": 10,
          "win_rate": 0.1
        },
        "PAXG_USDT": {
          "gross_pnl": 0.0047583,
          "pf": 0.0,
          "severe_pnl": -0.0152417,
          "trades": 5,
          "win_rate": 0.0
        },
        "PENDLE_USDT": {
          "gross_pnl": 0.0050967999999999986,
          "pf": 0.0,
          "severe_pnl": -0.12690320000000002,
          "trades": 33,
          "win_rate": 0.0
        },
        "PEOPLE_USDT": {
          "gross_pnl": -0.0001819,
          "pf": 0.0,
          "severe_pnl": -0.0041819,
          "trades": 1,
          "win_rate": 0.0
        },
        "PEPE_USDT": {
          "gross_pnl": 0.0026333999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0173666,
          "trades": 5,
          "win_rate": 0.0
        },
        "PHA_USDT": {
          "gross_pnl": 0.0033521000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0086479,
          "trades": 3,
          "win_rate": 0.0
        },
        "PIEVERSE_USDT": {
          "gross_pnl": 0.0026851,
          "pf": 0.0,
          "severe_pnl": -0.0173149,
          "trades": 5,
          "win_rate": 0.0
        },
        "PIPPIN_USDT": {
          "gross_pnl": 0.10566249999999998,
          "pf": 0.3731236578712716,
          "severe_pnl": -0.16633750000000003,
          "trades": 68,
          "win_rate": 0.07352941176470588
        },
        "PIXEL_USDT": {
          "gross_pnl": 0.0090257,
          "pf": 2.067214649880344,
          "severe_pnl": 0.0010256999999999992,
          "trades": 2,
          "win_rate": 0.5
        },
        "PI_USDT": {
          "gross_pnl": 0.02332830000000001,
          "pf": 0.06705291092205048,
          "severe_pnl": -0.7286717,
          "trades": 188,
          "win_rate": 0.10638297872340426
        },
        "PLUME_USDT": {
          "gross_pnl": 0.0039843,
          "pf": 0.0,
          "severe_pnl": -0.0080157,
          "trades": 3,
          "win_rate": 0.0
        },
        "PNUT_USDT": {
          "gross_pnl": 0.0018713,
          "pf": 0.0,
          "severe_pnl": -0.0061287,
          "trades": 2,
          "win_rate": 0.0
        },
        "POL_USDT": {
          "gross_pnl": 0.010866899999999999,
          "pf": 0.001223055663218907,
          "severe_pnl": -0.19713309999999998,
          "trades": 52,
          "win_rate": 0.019230769230769232
        },
        "POPCAT_USDT": {
          "gross_pnl": 0.0011364,
          "pf": 0.0,
          "severe_pnl": -0.010863600000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "PORTAL_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "POWER_USDT": {
          "gross_pnl": 0.0033298,
          "pf": 0.0,
          "severe_pnl": -0.0046702,
          "trades": 2,
          "win_rate": 0.0
        },
        "POWR_USDT": {
          "gross_pnl": 0.0064905,
          "pf": 999,
          "severe_pnl": 0.0024904999999999997,
          "trades": 1,
          "win_rate": 1.0
        },
        "PROMPT_USDT": {
          "gross_pnl": -0.0012146,
          "pf": 0.0,
          "severe_pnl": -0.0052146,
          "trades": 1,
          "win_rate": 0.0
        },
        "PROM_USDT": {
          "gross_pnl": 0.0038033000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0121967,
          "trades": 4,
          "win_rate": 0.0
        },
        "PTB_USDT": {
          "gross_pnl": 0.00016549999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0038345000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "PUMPFUN_USDT": {
          "gross_pnl": 0.051099799999999994,
          "pf": 0.08353949167456497,
          "severe_pnl": -0.38890020000000014,
          "trades": 110,
          "win_rate": 0.08181818181818182
        },
        "PUNDIX_USDT": {
          "gross_pnl": 0.0040516,
          "pf": 999,
          "severe_pnl": 5.1599999999999736e-05,
          "trades": 1,
          "win_rate": 1.0
        },
        "PYTH_USDT": {
          "gross_pnl": 0.018924599999999996,
          "pf": 0.007377838129280907,
          "severe_pnl": -0.49707539999999995,
          "trades": 129,
          "win_rate": 0.03875968992248062
        },
        "QNT_USDT": {
          "gross_pnl": 0.000759,
          "pf": 0.0,
          "severe_pnl": -0.007241000000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "QTUM_USDT": {
          "gross_pnl": 0.0004743000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0115257,
          "trades": 3,
          "win_rate": 0.0
        },
        "Q_USDT": {
          "gross_pnl": -0.0019825,
          "pf": 0.0,
          "severe_pnl": -0.0059825,
          "trades": 1,
          "win_rate": 0.0
        },
        "RAM_USDT": {
          "gross_pnl": 0.022860299999999997,
          "pf": 0.25106926152896836,
          "severe_pnl": -0.037139700000000005,
          "trades": 15,
          "win_rate": 0.2
        },
        "RARE_USDT": {
          "gross_pnl": 0.006383,
          "pf": 999,
          "severe_pnl": 0.0023829999999999997,
          "trades": 1,
          "win_rate": 1.0
        },
        "RAVE_USDT": {
          "gross_pnl": 0.008659599999999991,
          "pf": 0.034045895510096506,
          "severe_pnl": -0.3753404000000002,
          "trades": 96,
          "win_rate": 0.09375
        },
        "RAY_USDT": {
          "gross_pnl": -0.005141000000000001,
          "pf": 0.0,
          "severe_pnl": -0.025141,
          "trades": 5,
          "win_rate": 0.0
        },
        "RENDER_USDT": {
          "gross_pnl": 0.0254168,
          "pf": 0.02234544614879015,
          "severe_pnl": -0.23858320000000008,
          "trades": 66,
          "win_rate": 0.015151515151515152
        },
        "RESOLV_USDT": {
          "gross_pnl": 0.06372489999999999,
          "pf": 0.10355495827541647,
          "severe_pnl": -0.1282751,
          "trades": 48,
          "win_rate": 0.0625
        },
        "REZ_USDT": {
          "gross_pnl": -0.0014366000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0094366,
          "trades": 2,
          "win_rate": 0.0
        },
        "RE_USDT": {
          "gross_pnl": 0.06115679999999999,
          "pf": 0.007930220897193207,
          "severe_pnl": -0.3828431999999999,
          "trades": 111,
          "win_rate": 0.04504504504504504
        },
        "RIF_USDT": {
          "gross_pnl": 0.026521000000000003,
          "pf": 0.14057398078178937,
          "severe_pnl": -0.029478999999999998,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "RLC_USDT": {
          "gross_pnl": -0.004045,
          "pf": 0.0,
          "severe_pnl": -0.036045,
          "trades": 8,
          "win_rate": 0.0
        },
        "ROAM_USDT": {
          "gross_pnl": -0.19348220000000002,
          "pf": 0.3657336535525092,
          "severe_pnl": -0.26148220000000005,
          "trades": 17,
          "win_rate": 0.47058823529411764
        },
        "ROBO_USDT": {
          "gross_pnl": 0.0010319,
          "pf": 0.0,
          "severe_pnl": -0.0069681,
          "trades": 2,
          "win_rate": 0.0
        },
        "ROSE_USDT": {
          "gross_pnl": -0.0075542000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0435542,
          "trades": 9,
          "win_rate": 0.0
        },
        "RPL_USDT": {
          "gross_pnl": -0.0017836,
          "pf": 0.0,
          "severe_pnl": -0.0097836,
          "trades": 2,
          "win_rate": 0.0
        },
        "RSR_USDT": {
          "gross_pnl": 0.0087493,
          "pf": 0.0,
          "severe_pnl": -0.0192507,
          "trades": 7,
          "win_rate": 0.0
        },
        "RUNE_USDT": {
          "gross_pnl": -0.0056979000000000005,
          "pf": 0.0,
          "severe_pnl": -0.04169790000000001,
          "trades": 9,
          "win_rate": 0.0
        },
        "RVN_USDT": {
          "gross_pnl": 0.013773599999999995,
          "pf": 0.21375736246772462,
          "severe_pnl": -0.0342264,
          "trades": 12,
          "win_rate": 0.16666666666666666
        },
        "SAFE_USDT": {
          "gross_pnl": 0.0069355,
          "pf": 0.06296255180580224,
          "severe_pnl": -0.0050645,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "SAGA_USDT": {
          "gross_pnl": -0.0016022999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0136023,
          "trades": 3,
          "win_rate": 0.0
        },
        "SAHARA_USDT": {
          "gross_pnl": -0.0064823,
          "pf": 0.0,
          "severe_pnl": -0.05448230000000002,
          "trades": 12,
          "win_rate": 0.0
        },
        "SAND_USDT": {
          "gross_pnl": -0.0010110000000000002,
          "pf": 0.0,
          "severe_pnl": -0.045011,
          "trades": 11,
          "win_rate": 0.0
        },
        "SANTOS_USDT": {
          "gross_pnl": 0.006432499999999999,
          "pf": 0.545639004029102,
          "severe_pnl": -0.0015675000000000008,
          "trades": 2,
          "win_rate": 0.5
        },
        "SEI_USDT": {
          "gross_pnl": 0.023821899999999997,
          "pf": 0.023953785764644204,
          "severe_pnl": -0.27217810000000003,
          "trades": 74,
          "win_rate": 0.02702702702702703
        },
        "SENT_USDT": {
          "gross_pnl": -0.03433699999999999,
          "pf": 0.1775007071668142,
          "severe_pnl": -0.134337,
          "trades": 25,
          "win_rate": 0.16
        },
        "SFP_USDT": {
          "gross_pnl": 0.0004662,
          "pf": 0.0,
          "severe_pnl": -0.0035338,
          "trades": 1,
          "win_rate": 0.0
        },
        "SHIB_USDT": {
          "gross_pnl": 0.0007669999999999999,
          "pf": 0.0,
          "severe_pnl": -0.11123300000000004,
          "trades": 28,
          "win_rate": 0.0
        },
        "SIGN_USDT": {
          "gross_pnl": 0.0001149,
          "pf": 0.0,
          "severe_pnl": -0.0038851000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "SKL_USDT": {
          "gross_pnl": 0.0411889,
          "pf": 0.5051783168379987,
          "severe_pnl": -0.11481109999999999,
          "trades": 39,
          "win_rate": 0.38461538461538464
        },
        "SKYAI_USDT": {
          "gross_pnl": -0.009054600000000001,
          "pf": 0.03796267829900287,
          "severe_pnl": -0.5970545999999999,
          "trades": 147,
          "win_rate": 0.08163265306122448
        },
        "SKY_USDT": {
          "gross_pnl": 0.006238599999999999,
          "pf": 0.0,
          "severe_pnl": -0.0417614,
          "trades": 12,
          "win_rate": 0.0
        },
        "SLX_USDT": {
          "gross_pnl": 0.15694460000000002,
          "pf": 0.16730105066175768,
          "severe_pnl": -0.39905540000000006,
          "trades": 139,
          "win_rate": 0.12949640287769784
        },
        "SMH_USDT": {
          "gross_pnl": -0.002046,
          "pf": 0.0,
          "severe_pnl": -0.006046,
          "trades": 1,
          "win_rate": 0.0
        },
        "SNT_USDT": {
          "gross_pnl": 0.0057766,
          "pf": 0.0,
          "severe_pnl": -0.0062234000000000005,
          "trades": 3,
          "win_rate": 0.0
        },
        "SNXX_USDT": {
          "gross_pnl": -0.0032695999999999966,
          "pf": 0.2223167314680144,
          "severe_pnl": -0.11126960000000001,
          "trades": 27,
          "win_rate": 0.2962962962962963
        },
        "SNX_USDT": {
          "gross_pnl": -0.0013723000000000008,
          "pf": 0.10809514121480258,
          "severe_pnl": -0.0293723,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "SOL_USDT": {
          "gross_pnl": -0.007086100000000001,
          "pf": 0.0,
          "severe_pnl": -0.1430861,
          "trades": 34,
          "win_rate": 0.0
        },
        "SOONNETWORK_USDT": {
          "gross_pnl": 8.999999999999677e-07,
          "pf": 0.0,
          "severe_pnl": -0.0119991,
          "trades": 3,
          "win_rate": 0.0
        },
        "SOXL_USDT": {
          "gross_pnl": 0.103005,
          "pf": 0.20326118468463547,
          "severe_pnl": -0.356995,
          "trades": 115,
          "win_rate": 0.19130434782608696
        },
        "SOXS_USDT": {
          "gross_pnl": 0.021949400000000008,
          "pf": 0.23885736525304166,
          "severe_pnl": -0.0860506,
          "trades": 27,
          "win_rate": 0.18518518518518517
        },
        "SOXX_USDT": {
          "gross_pnl": 0.006848099999999999,
          "pf": 0.0,
          "severe_pnl": -0.0411519,
          "trades": 12,
          "win_rate": 0.0
        },
        "SPACE_USDT": {
          "gross_pnl": 0.0007081,
          "pf": 0.0,
          "severe_pnl": -0.0032919,
          "trades": 1,
          "win_rate": 0.0
        },
        "SPELL_USDT": {
          "gross_pnl": 0.0391165,
          "pf": 2.2490607460453327,
          "severe_pnl": 0.0191165,
          "trades": 5,
          "win_rate": 0.4
        },
        "SPORTFUN_USDT": {
          "gross_pnl": -0.038268,
          "pf": 0.0,
          "severe_pnl": -0.046268,
          "trades": 2,
          "win_rate": 0.0
        },
        "SPY_USDT": {
          "gross_pnl": -0.00045809999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0044581,
          "trades": 1,
          "win_rate": 0.0
        },
        "SQD_USDT": {
          "gross_pnl": 0.017135400000000002,
          "pf": 0.3668463533319736,
          "severe_pnl": -0.0108646,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "SQQQ_USDT": {
          "gross_pnl": 0.0055834000000000005,
          "pf": 0.1325647721392556,
          "severe_pnl": -0.0144166,
          "trades": 5,
          "win_rate": 0.2
        },
        "STABLE_USDT": {
          "gross_pnl": 0.0238851,
          "pf": 0.3655791788856304,
          "severe_pnl": -0.012114900000000003,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "STAR_USDT": {
          "gross_pnl": 0.008553999999999999,
          "pf": 0.5706881945482633,
          "severe_pnl": -0.003446000000000001,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "STG_USDT": {
          "gross_pnl": 0.006367500000000002,
          "pf": 0.004223356421230528,
          "severe_pnl": -0.06163250000000001,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "STO_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "STRK_USDT": {
          "gross_pnl": 0.011214,
          "pf": 0.015411781664424374,
          "severe_pnl": -0.032786,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "STX_USDT": {
          "gross_pnl": 0.0182679,
          "pf": 0.0,
          "severe_pnl": -0.06173210000000001,
          "trades": 20,
          "win_rate": 0.0
        },
        "SUI_USDT": {
          "gross_pnl": 0.008872899999999998,
          "pf": 0.0,
          "severe_pnl": -0.2391271000000001,
          "trades": 62,
          "win_rate": 0.0
        },
        "SUPER_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "SUSHI_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "SXT_USDT": {
          "gross_pnl": -0.024068099999999995,
          "pf": 0.15739187347141645,
          "severe_pnl": -0.4280680999999999,
          "trades": 101,
          "win_rate": 0.18811881188118812
        },
        "SYN_USDT": {
          "gross_pnl": 0.10236560000000001,
          "pf": 0.20055680143706633,
          "severe_pnl": -0.6216343999999996,
          "trades": 181,
          "win_rate": 0.15469613259668508
        },
        "SYRUP_USDT": {
          "gross_pnl": 0.039063200000000006,
          "pf": 0.03660116902760742,
          "severe_pnl": -0.21693679999999999,
          "trades": 64,
          "win_rate": 0.0625
        },
        "S_USDT": {
          "gross_pnl": -0.0051106,
          "pf": 0.0,
          "severe_pnl": -0.033110600000000004,
          "trades": 7,
          "win_rate": 0.0
        },
        "TAC_USDT": {
          "gross_pnl": 0.11227320000000003,
          "pf": 0.5128371938396598,
          "severe_pnl": -0.1597268,
          "trades": 68,
          "win_rate": 0.27941176470588236
        },
        "TAG_USDT": {
          "gross_pnl": -0.015560599999999996,
          "pf": 0.21888327416798917,
          "severe_pnl": -0.13156060000000003,
          "trades": 29,
          "win_rate": 0.2413793103448276
        },
        "TAIKO_USDT": {
          "gross_pnl": 0.007016700000000001,
          "pf": 0.3673019495154384,
          "severe_pnl": -0.0089833,
          "trades": 4,
          "win_rate": 0.25
        },
        "TAO_USDT": {
          "gross_pnl": 0.006400800000000001,
          "pf": 0.0,
          "severe_pnl": -0.08159919999999998,
          "trades": 22,
          "win_rate": 0.0
        },
        "THETA_USDT": {
          "gross_pnl": 0.0053894999999999985,
          "pf": 0.0030673264287860544,
          "severe_pnl": -0.15461050000000004,
          "trades": 40,
          "win_rate": 0.025
        },
        "THE_USDT": {
          "gross_pnl": 0.014790099999999994,
          "pf": 0.27873388698794965,
          "severe_pnl": -0.041209899999999994,
          "trades": 14,
          "win_rate": 0.2857142857142857
        },
        "TIA_USDT": {
          "gross_pnl": 0.017857799999999997,
          "pf": 0.0,
          "severe_pnl": -0.3941421999999997,
          "trades": 103,
          "win_rate": 0.0
        },
        "TLM_USDT": {
          "gross_pnl": 0.0032044000000000026,
          "pf": 0.050630829921799736,
          "severe_pnl": -0.24479559999999997,
          "trades": 62,
          "win_rate": 0.08064516129032258
        },
        "TOSHI_USDT": {
          "gross_pnl": 0.0179583,
          "pf": 0.5932535774288858,
          "severe_pnl": -0.014041700000000004,
          "trades": 8,
          "win_rate": 0.25
        },
        "TOWNS_USDT": {
          "gross_pnl": 0.0067607,
          "pf": 0.09768253718337463,
          "severe_pnl": -0.0332393,
          "trades": 10,
          "win_rate": 0.3
        },
        "TQQQ_USDT": {
          "gross_pnl": 0.0021234999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0538765,
          "trades": 14,
          "win_rate": 0.0
        },
        "TRADOOR_USDT": {
          "gross_pnl": -0.039408800000000015,
          "pf": 0.26406563353284224,
          "severe_pnl": -0.20340880000000003,
          "trades": 41,
          "win_rate": 0.2682926829268293
        },
        "TRB_USDT": {
          "gross_pnl": 0.0066188,
          "pf": 0.00020227749475576953,
          "severe_pnl": -0.05338119999999999,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "TRIA_USDT": {
          "gross_pnl": -0.005503299999999994,
          "pf": 0.10662465533863644,
          "severe_pnl": -0.5255033000000002,
          "trades": 130,
          "win_rate": 0.1
        },
        "TRUST_USDT": {
          "gross_pnl": 0.00041430000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0035857,
          "trades": 1,
          "win_rate": 0.0
        },
        "TRX_USDT": {
          "gross_pnl": 0.0022528000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0217472,
          "trades": 6,
          "win_rate": 0.0
        },
        "TRY_USDT": {
          "gross_pnl": -0.00046929999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0044693,
          "trades": 1,
          "win_rate": 0.0
        },
        "TURBO_USDT": {
          "gross_pnl": 0.004655699999999999,
          "pf": 0.1413943248749439,
          "severe_pnl": -0.019344300000000002,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "TUT_USDT": {
          "gross_pnl": 0.0023504,
          "pf": 0.0,
          "severe_pnl": -0.0056496,
          "trades": 2,
          "win_rate": 0.0
        },
        "TWT_USDT": {
          "gross_pnl": 0.0009164000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0270836,
          "trades": 7,
          "win_rate": 0.0
        },
        "T_USDT": {
          "gross_pnl": -0.15398819999999994,
          "pf": 0.039179447522808906,
          "severe_pnl": -0.49798820000000016,
          "trades": 86,
          "win_rate": 0.11627906976744186
        },
        "UAI_USDT": {
          "gross_pnl": 0.0761283,
          "pf": 0.25229688590008487,
          "severe_pnl": -0.1398717,
          "trades": 54,
          "win_rate": 0.16666666666666666
        },
        "UMA_USDT": {
          "gross_pnl": -0.0114356,
          "pf": 0.0,
          "severe_pnl": -0.023435599999999997,
          "trades": 3,
          "win_rate": 0.0
        },
        "UNI_USDT": {
          "gross_pnl": 0.02840769999999999,
          "pf": 0.0,
          "severe_pnl": -0.39559230000000006,
          "trades": 106,
          "win_rate": 0.0
        },
        "USELESS_USDT": {
          "gross_pnl": -0.005970099999999999,
          "pf": 0.012495617920349809,
          "severe_pnl": -0.2619701,
          "trades": 64,
          "win_rate": 0.046875
        },
        "USO_USDT": {
          "gross_pnl": 0.006378,
          "pf": 0.0,
          "severe_pnl": -0.017622,
          "trades": 6,
          "win_rate": 0.0
        },
        "USUAL_USDT": {
          "gross_pnl": 0.0089454,
          "pf": 0.08032664674431966,
          "severe_pnl": -0.043054600000000005,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "UVXY_USDT": {
          "gross_pnl": -0.035503200000000006,
          "pf": 0.0,
          "severe_pnl": -0.0595032,
          "trades": 6,
          "win_rate": 0.0
        },
        "VANA_USDT": {
          "gross_pnl": 0.0023426999999999996,
          "pf": 0.14865353447201096,
          "severe_pnl": -0.0136573,
          "trades": 4,
          "win_rate": 0.25
        },
        "VANRY_USDT": {
          "gross_pnl": 0.048993300000000004,
          "pf": 0.3668399632109335,
          "severe_pnl": -0.1310067,
          "trades": 45,
          "win_rate": 0.26666666666666666
        },
        "VELO_USDT": {
          "gross_pnl": -0.000986,
          "pf": 0.0,
          "severe_pnl": -0.012986000000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "VELVET_USDT": {
          "gross_pnl": -0.04164349999999997,
          "pf": 0.2010038565497351,
          "severe_pnl": -0.6136435,
          "trades": 143,
          "win_rate": 0.21678321678321677
        },
        "VET_USDT": {
          "gross_pnl": -0.006443,
          "pf": 0.0,
          "severe_pnl": -0.078443,
          "trades": 18,
          "win_rate": 0.0
        },
        "VINE_USDT": {
          "gross_pnl": 0.019158500000000002,
          "pf": 0.5635077360558458,
          "severe_pnl": -0.0088415,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "VIRTUAL_USDT": {
          "gross_pnl": 0.006426300000000003,
          "pf": 0.014304922404423166,
          "severe_pnl": -0.5095737000000001,
          "trades": 129,
          "win_rate": 0.03875968992248062
        },
        "VVV_USDT": {
          "gross_pnl": -0.025698300000000004,
          "pf": 0.0038508295554655035,
          "severe_pnl": -0.38569830000000016,
          "trades": 90,
          "win_rate": 0.03333333333333333
        },
        "WAL_USDT": {
          "gross_pnl": 0.0016617000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0023382999999999998,
          "trades": 1,
          "win_rate": 0.0
        },
        "WET_USDT": {
          "gross_pnl": 0.0038247,
          "pf": 0.0,
          "severe_pnl": -0.0001753000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "WIF_USDT": {
          "gross_pnl": 0.0014425000000000002,
          "pf": 0.0,
          "severe_pnl": -0.3785575,
          "trades": 95,
          "win_rate": 0.0
        },
        "WLD_USDT": {
          "gross_pnl": 0.013511800000000003,
          "pf": 0.0,
          "severe_pnl": -0.2864882,
          "trades": 75,
          "win_rate": 0.0
        },
        "WLFI_USDT": {
          "gross_pnl": 0.0010243999999999993,
          "pf": 0.0,
          "severe_pnl": -0.09897560000000001,
          "trades": 25,
          "win_rate": 0.0
        },
        "WOO_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "W_USDT": {
          "gross_pnl": -0.0043028,
          "pf": 0.0,
          "severe_pnl": -0.0403028,
          "trades": 9,
          "win_rate": 0.0
        },
        "XAI_USDT": {
          "gross_pnl": -0.0017142999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0217143,
          "trades": 5,
          "win_rate": 0.0
        },
        "XAN_USDT": {
          "gross_pnl": 0.0333179,
          "pf": 0.5917627186009539,
          "severe_pnl": -0.010682100000000003,
          "trades": 11,
          "win_rate": 0.36363636363636365
        },
        "XBI_USDT": {
          "gross_pnl": 0.0037867000000000013,
          "pf": 0.024273111973237647,
          "severe_pnl": -0.04821330000000001,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "XDC_USDT": {
          "gross_pnl": 0.0029407000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0290593,
          "trades": 8,
          "win_rate": 0.0
        },
        "XEC_USDT": {
          "gross_pnl": -0.07118719999999988,
          "pf": 0.11991816698204309,
          "severe_pnl": -0.5071872000000001,
          "trades": 109,
          "win_rate": 0.1834862385321101
        },
        "XLM_USDT": {
          "gross_pnl": 0.0016219999999999987,
          "pf": 0.0,
          "severe_pnl": -0.206378,
          "trades": 52,
          "win_rate": 0.0
        },
        "XLU_USDT": {
          "gross_pnl": 0.0014227999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0105772,
          "trades": 3,
          "win_rate": 0.0
        },
        "XMR_USDT": {
          "gross_pnl": 0.009010999999999996,
          "pf": 0.0,
          "severe_pnl": -0.34298899999999993,
          "trades": 88,
          "win_rate": 0.0
        },
        "XPIN_USDT": {
          "gross_pnl": -0.0016621000000000084,
          "pf": 0.15692624009691938,
          "severe_pnl": -0.07766209999999998,
          "trades": 19,
          "win_rate": 0.2631578947368421
        },
        "XPL_USDT": {
          "gross_pnl": -0.024644400000000004,
          "pf": 0.0012096052806079523,
          "severe_pnl": -0.33664439999999995,
          "trades": 78,
          "win_rate": 0.01282051282051282
        },
        "XPT_USDT": {
          "gross_pnl": 0.00826,
          "pf": 0.0067494267209738884,
          "severe_pnl": -0.09174,
          "trades": 25,
          "win_rate": 0.04
        },
        "XRP_USDT": {
          "gross_pnl": -0.0057425,
          "pf": 0.0,
          "severe_pnl": -0.16174249999999998,
          "trades": 39,
          "win_rate": 0.0
        },
        "XTZ_USDT": {
          "gross_pnl": 0.00012049999999999989,
          "pf": 0.0,
          "severe_pnl": -0.0198795,
          "trades": 5,
          "win_rate": 0.0
        },
        "YFI_USDT": {
          "gross_pnl": 0.008152799999999998,
          "pf": 0.0384269875179112,
          "severe_pnl": -0.047847200000000006,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "ZAMA_USDT": {
          "gross_pnl": 0.0046388,
          "pf": 0.0,
          "severe_pnl": -0.0193612,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZBT_USDT": {
          "gross_pnl": 0.06552730000000002,
          "pf": 0.07676425300148662,
          "severe_pnl": -0.2984726999999999,
          "trades": 91,
          "win_rate": 0.13186813186813187
        },
        "ZEC_USDT": {
          "gross_pnl": 0.0337152,
          "pf": 0.02840122308948789,
          "severe_pnl": -0.20628479999999996,
          "trades": 60,
          "win_rate": 0.03333333333333333
        },
        "ZEN_USDT": {
          "gross_pnl": 0.005018999999999997,
          "pf": 0.11160910449072853,
          "severe_pnl": -0.090981,
          "trades": 24,
          "win_rate": 0.041666666666666664
        },
        "ZEST_USDT": {
          "gross_pnl": -0.009555400000000002,
          "pf": 0.025292198425189462,
          "severe_pnl": -0.0415554,
          "trades": 8,
          "win_rate": 0.125
        },
        "ZETA_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZIL_USDT": {
          "gross_pnl": -0.002905799999999999,
          "pf": 0.0,
          "severe_pnl": -0.0109058,
          "trades": 2,
          "win_rate": 0.0
        },
        "ZINC_USDT": {
          "gross_pnl": 2.959999999999996e-05,
          "pf": 0.0,
          "severe_pnl": -0.023970400000000003,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZKP_USDT": {
          "gross_pnl": -0.0033761999999999998,
          "pf": 0.0,
          "severe_pnl": -0.03137620000000001,
          "trades": 7,
          "win_rate": 0.0
        },
        "ZKSYNC_USDT": {
          "gross_pnl": 0.0065009,
          "pf": 0.015324451600616346,
          "severe_pnl": -0.0454991,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "ZORA_USDT": {
          "gross_pnl": -0.0046602,
          "pf": 0.0,
          "severe_pnl": -0.0486602,
          "trades": 11,
          "win_rate": 0.0
        },
        "ZRO_USDT": {
          "gross_pnl": 0.0012819,
          "pf": 0.017339671079123167,
          "severe_pnl": -0.1547181,
          "trades": 39,
          "win_rate": 0.02564102564102564
        }
      },
      "validation_depth_quartiles": [
        {
          "gross_pnl": 0.4083084999999999,
          "pf": 0.2176346385752736,
          "quartile": 1,
          "severe_pnl": -10.743691500000008,
          "trades": 2788,
          "upper": 8976.76524,
          "win_rate": 0.17647058823529413
        },
        {
          "gross_pnl": 1.0464373999999985,
          "pf": 0.12441537119176423,
          "quartile": 2,
          "severe_pnl": -11.733562599999933,
          "trades": 3195,
          "upper": 106972.33601999999,
          "win_rate": 0.09953051643192488
        },
        {
          "gross_pnl": 0.45913929999999953,
          "pf": 0.05651889578379003,
          "quartile": 3,
          "severe_pnl": -12.94086069999995,
          "trades": 3350,
          "upper": 1071304.435,
          "win_rate": 0.06985074626865671
        },
        {
          "gross_pnl": 0.6394072000000008,
          "pf": 0.026664989694805196,
          "quartile": 4,
          "severe_pnl": -11.384592799999924,
          "trades": 3006,
          "upper": null,
          "win_rate": 0.03127079174983367
        }
      ],
      "validation_pass": false,
      "validation_skips": {
        "invalid_path_json": 0,
        "missing_horizon_path": 19,
        "structure_not_selected": 74982,
        "symbol_cooldown": 3960
      },
      "validation_spread_quartiles": [
        {
          "gross_pnl": 0.3253715000000001,
          "pf": 0.04168717490138066,
          "quartile": 1,
          "severe_pnl": -11.594628499999958,
          "trades": 2980,
          "upper": 2.148689299527946,
          "win_rate": 0.04798657718120805
        },
        {
          "gross_pnl": 0.31225510000000023,
          "pf": 0.07277268882627039,
          "quartile": 2,
          "severe_pnl": -12.291744899999973,
          "trades": 3151,
          "upper": 4.268032437045758,
          "win_rate": 0.07045382418279911
        },
        {
          "gross_pnl": 1.1884600000000005,
          "pf": 0.10543007972328115,
          "quartile": 3,
          "severe_pnl": -11.811539999999908,
          "trades": 3250,
          "upper": 7.482229704451622,
          "win_rate": 0.088
        },
        {
          "gross_pnl": 0.7272057999999995,
          "pf": 0.20604384212064128,
          "quartile": 4,
          "severe_pnl": -11.104794199999946,
          "trades": 2958,
          "upper": null,
          "win_rate": 0.16463826910074375
        }
      ]
    },
    {
      "direction": "fade",
      "horizon_seconds": 300,
      "leave_best_symbol": -46.00965239999991,
      "structure": "contradict",
      "validation": {
        "gross_pnl": 3.410750899999978,
        "pf": 0.279916956051855,
        "severe_pnl": -45.88524909999991,
        "trades": 12324,
        "win_rate": 0.19133398247322297
      },
      "validation_by_symbol": {
        "0G_USDT": {
          "gross_pnl": 0.008360499999999998,
          "pf": 0.28996346916923854,
          "severe_pnl": -0.0676395,
          "trades": 19,
          "win_rate": 0.15789473684210525
        },
        "1000000BABYDOGE_USDT": {
          "gross_pnl": 0.012833500000000001,
          "pf": 0.617466204380444,
          "severe_pnl": -0.003166499999999999,
          "trades": 4,
          "win_rate": 0.5
        },
        "1000BONK_USDT": {
          "gross_pnl": 0.029705,
          "pf": 0.09973814918144835,
          "severe_pnl": -0.21429499999999999,
          "trades": 61,
          "win_rate": 0.16393442622950818
        },
        "1000BTT_USDT": {
          "gross_pnl": 0.0025840000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0014159999999999997,
          "trades": 1,
          "win_rate": 0.0
        },
        "2Z_USDT": {
          "gross_pnl": 0.00042320000000000004,
          "pf": 0.0,
          "severe_pnl": -0.0035768,
          "trades": 1,
          "win_rate": 0.0
        },
        "4_USDT": {
          "gross_pnl": 0.0054284,
          "pf": 0.017844632903571103,
          "severe_pnl": -0.0225716,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "AAVE_USDT": {
          "gross_pnl": 0.030472799999999994,
          "pf": 0.038891530617636186,
          "severe_pnl": -0.1455272,
          "trades": 44,
          "win_rate": 0.11363636363636363
        },
        "ACE_USDT": {
          "gross_pnl": 0.1160565,
          "pf": 999,
          "severe_pnl": 0.1080565,
          "trades": 2,
          "win_rate": 1.0
        },
        "ACH_USDT": {
          "gross_pnl": -0.0030055999999999998,
          "pf": 0.0,
          "severe_pnl": -0.011005599999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "ACU_USDT": {
          "gross_pnl": 0.001594,
          "pf": 0.0,
          "severe_pnl": -0.002406,
          "trades": 1,
          "win_rate": 0.0
        },
        "ACX_USDT": {
          "gross_pnl": -0.000949,
          "pf": 0.0,
          "severe_pnl": -0.004949,
          "trades": 1,
          "win_rate": 0.0
        },
        "ADA_USDT": {
          "gross_pnl": 0.044018599999999984,
          "pf": 0.03743965400915685,
          "severe_pnl": -0.3359814000000001,
          "trades": 95,
          "win_rate": 0.06315789473684211
        },
        "AERGO_USDT": {
          "gross_pnl": 0.026947799999999994,
          "pf": 0.7933567619970914,
          "severe_pnl": -0.017052200000000017,
          "trades": 11,
          "win_rate": 0.5454545454545454
        },
        "AERO_USDT": {
          "gross_pnl": 0.010624900000000012,
          "pf": 0.01898873849775305,
          "severe_pnl": -0.2053751,
          "trades": 54,
          "win_rate": 0.05555555555555555
        },
        "AGI_USDT": {
          "gross_pnl": 0.0012563999999999995,
          "pf": 0.119668942469616,
          "severe_pnl": -0.006743600000000001,
          "trades": 2,
          "win_rate": 0.5
        },
        "AGLD_USDT": {
          "gross_pnl": 0.0333059,
          "pf": 0.5048173322864047,
          "severe_pnl": -0.014694100000000002,
          "trades": 12,
          "win_rate": 0.3333333333333333
        },
        "AIGENSYN_USDT": {
          "gross_pnl": 0.0062844999999999976,
          "pf": 0.16582909161395928,
          "severe_pnl": -0.0697155,
          "trades": 19,
          "win_rate": 0.21052631578947367
        },
        "AIOT_USDT": {
          "gross_pnl": -0.10084699999999996,
          "pf": 0.3906902121248891,
          "severe_pnl": -0.31684700000000016,
          "trades": 54,
          "win_rate": 0.3888888888888889
        },
        "AIOZ_USDT": {
          "gross_pnl": 0.0033461000000000003,
          "pf": 0.0,
          "severe_pnl": -0.004653899999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "AIO_USDT": {
          "gross_pnl": 0.0443824,
          "pf": 999,
          "severe_pnl": 0.0363824,
          "trades": 2,
          "win_rate": 1.0
        },
        "AKE_USDT": {
          "gross_pnl": 0.3604033,
          "pf": 1.1657572466906059,
          "severe_pnl": 0.12440329999999997,
          "trades": 59,
          "win_rate": 0.5423728813559322
        },
        "AKT_USDT": {
          "gross_pnl": -0.004386,
          "pf": 0.0,
          "severe_pnl": -0.008386000000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "ALCH_USDT": {
          "gross_pnl": -0.0656627,
          "pf": 0.31818812061395585,
          "severe_pnl": -0.3176627,
          "trades": 63,
          "win_rate": 0.25396825396825395
        },
        "ALGO_USDT": {
          "gross_pnl": 0.0036835999999999982,
          "pf": 0.005471147235787919,
          "severe_pnl": -0.12831640000000005,
          "trades": 33,
          "win_rate": 0.030303030303030304
        },
        "ALLO_USDT": {
          "gross_pnl": 0.15669229999999995,
          "pf": 0.3469010298077252,
          "severe_pnl": -0.6273076999999995,
          "trades": 196,
          "win_rate": 0.2857142857142857
        },
        "ALT_USDT": {
          "gross_pnl": 0.0492248,
          "pf": 1.664078937457631,
          "severe_pnl": 0.013224799999999997,
          "trades": 9,
          "win_rate": 0.3333333333333333
        },
        "ANKR_USDT": {
          "gross_pnl": -0.05157609999999999,
          "pf": 0.20434066252217445,
          "severe_pnl": -0.07557610000000001,
          "trades": 6,
          "win_rate": 0.3333333333333333
        },
        "ANSEM_USDT": {
          "gross_pnl": 0.15277930000000006,
          "pf": 0.6217344806275714,
          "severe_pnl": -0.5312207,
          "trades": 171,
          "win_rate": 0.42105263157894735
        },
        "ANTHROPIC_USDT": {
          "gross_pnl": 0.008325800000000001,
          "pf": 0.0,
          "severe_pnl": -0.06367420000000001,
          "trades": 18,
          "win_rate": 0.0
        },
        "APE_USDT": {
          "gross_pnl": 0.036417700000000004,
          "pf": 0.052419688948275776,
          "severe_pnl": -0.2355823,
          "trades": 68,
          "win_rate": 0.11764705882352941
        },
        "APT_USDT": {
          "gross_pnl": -0.013778599999999981,
          "pf": 0.00661562018317199,
          "severe_pnl": -0.3897786000000001,
          "trades": 94,
          "win_rate": 0.02127659574468085
        },
        "ARB_USDT": {
          "gross_pnl": 0.10719320000000003,
          "pf": 0.09827797474348228,
          "severe_pnl": -0.6528067999999997,
          "trades": 190,
          "win_rate": 0.14210526315789473
        },
        "ARKK_USDT": {
          "gross_pnl": 0.0385778,
          "pf": 9.37704066488572,
          "severe_pnl": 0.022577799999999995,
          "trades": 4,
          "win_rate": 0.75
        },
        "ARKM_USDT": {
          "gross_pnl": 0.0053904,
          "pf": 0.0,
          "severe_pnl": -0.0306096,
          "trades": 9,
          "win_rate": 0.0
        },
        "ARX_USDT": {
          "gross_pnl": 0.003317200000000004,
          "pf": 0.16616439365110544,
          "severe_pnl": -0.10868279999999998,
          "trades": 28,
          "win_rate": 0.21428571428571427
        },
        "AR_USDT": {
          "gross_pnl": 0.013082399999999998,
          "pf": 0.07185446458680812,
          "severe_pnl": -0.05091759999999999,
          "trades": 16,
          "win_rate": 0.1875
        },
        "ASP_USDT": {
          "gross_pnl": 0.0194175,
          "pf": 999,
          "severe_pnl": 0.0154175,
          "trades": 1,
          "win_rate": 1.0
        },
        "ASTER_USDT": {
          "gross_pnl": 0.010115699999999998,
          "pf": 0.0,
          "severe_pnl": -0.1258843,
          "trades": 34,
          "win_rate": 0.0
        },
        "ATH_USDT": {
          "gross_pnl": 0.020175300000000004,
          "pf": 0.44120461621961315,
          "severe_pnl": -0.0078247,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "ATOM_USDT": {
          "gross_pnl": 0.030131999999999996,
          "pf": 0.04363164888823143,
          "severe_pnl": -0.153868,
          "trades": 46,
          "win_rate": 0.08695652173913043
        },
        "AT_USDT": {
          "gross_pnl": 0.0092408,
          "pf": 0.10245923407871672,
          "severe_pnl": -0.0067592,
          "trades": 4,
          "win_rate": 0.25
        },
        "AVAAI_USDT": {
          "gross_pnl": -0.06589119999999998,
          "pf": 0.11072750480078732,
          "severe_pnl": -0.0778912,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "AVAX_USDT": {
          "gross_pnl": -0.009532000000000002,
          "pf": 0.008221723274134275,
          "severe_pnl": -0.16953200000000002,
          "trades": 40,
          "win_rate": 0.025
        },
        "AVNT_USDT": {
          "gross_pnl": -0.0016736000000000001,
          "pf": 0.05438979002910694,
          "severe_pnl": -0.1136736,
          "trades": 28,
          "win_rate": 0.10714285714285714
        },
        "AWE_USDT": {
          "gross_pnl": 0.0144246,
          "pf": 2.846043330843055,
          "severe_pnl": 0.0064246,
          "trades": 2,
          "win_rate": 0.5
        },
        "AXS_USDT": {
          "gross_pnl": 0.002066,
          "pf": 0.0,
          "severe_pnl": -0.033934,
          "trades": 9,
          "win_rate": 0.0
        },
        "A_USDT": {
          "gross_pnl": -0.0016041000000000002,
          "pf": 0.0,
          "severe_pnl": -0.013604100000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "B2_USDT": {
          "gross_pnl": 0.0028130000000000004,
          "pf": 0.3065415313038945,
          "severe_pnl": -0.005187,
          "trades": 2,
          "win_rate": 0.5
        },
        "B3_USDT": {
          "gross_pnl": 0.14567739999999998,
          "pf": 5.5163800459943015,
          "severe_pnl": 0.09367740000000001,
          "trades": 13,
          "win_rate": 0.8461538461538461
        },
        "BANANAS31_USDT": {
          "gross_pnl": 0.013309699999999999,
          "pf": 999,
          "severe_pnl": 0.005309699999999999,
          "trades": 2,
          "win_rate": 1.0
        },
        "BAND_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "BANK_USDT": {
          "gross_pnl": -0.13319159999999997,
          "pf": 0.3995626403541058,
          "severe_pnl": -0.4691915999999999,
          "trades": 84,
          "win_rate": 0.3333333333333333
        },
        "BAN_USDT": {
          "gross_pnl": 0.0022971,
          "pf": 0.0,
          "severe_pnl": -0.0017029000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "BASED_USDT": {
          "gross_pnl": 0.025985200000000003,
          "pf": 0.20274798927613938,
          "severe_pnl": -0.0980148,
          "trades": 31,
          "win_rate": 0.22580645161290322
        },
        "BAS_USDT": {
          "gross_pnl": 0.0056609,
          "pf": 0.3375267962743938,
          "severe_pnl": -0.0143391,
          "trades": 5,
          "win_rate": 0.4
        },
        "BAT_USDT": {
          "gross_pnl": 0.002543,
          "pf": 0.0,
          "severe_pnl": -0.009457,
          "trades": 3,
          "win_rate": 0.0
        },
        "BCH_USDT": {
          "gross_pnl": -0.020971700000000006,
          "pf": 0.0,
          "severe_pnl": -0.2689716999999999,
          "trades": 62,
          "win_rate": 0.0
        },
        "BEAT_USDT": {
          "gross_pnl": 0.03233390000000001,
          "pf": 0.26867363188486454,
          "severe_pnl": -0.6076660999999997,
          "trades": 160,
          "win_rate": 0.23125
        },
        "BERA_USDT": {
          "gross_pnl": 0.0062844,
          "pf": 0.009315262699654063,
          "severe_pnl": -0.025715599999999998,
          "trades": 8,
          "win_rate": 0.125
        },
        "BIANRENSHENG_USDT": {
          "gross_pnl": 0.012962000000000001,
          "pf": 0.2638958117659088,
          "severe_pnl": -0.023038,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "BICO_USDT": {
          "gross_pnl": 0.017403499999999995,
          "pf": 0.35410573080990665,
          "severe_pnl": -0.014596500000000004,
          "trades": 8,
          "win_rate": 0.625
        },
        "BIGTIME_USDT": {
          "gross_pnl": 0.0016168999999999999,
          "pf": 0.0,
          "severe_pnl": -0.0063831,
          "trades": 2,
          "win_rate": 0.0
        },
        "BILL_USDT": {
          "gross_pnl": -0.13063520000000006,
          "pf": 0.2906578209534706,
          "severe_pnl": -0.7186352000000003,
          "trades": 147,
          "win_rate": 0.2925170068027211
        },
        "BLAST_USDT": {
          "gross_pnl": -0.25234619999999996,
          "pf": 0.2376587541497607,
          "severe_pnl": -0.35634619999999995,
          "trades": 26,
          "win_rate": 0.2692307692307692
        },
        "BLESS_USDT": {
          "gross_pnl": 0.0482996,
          "pf": 0.23520435894958633,
          "severe_pnl": -0.10370039999999998,
          "trades": 38,
          "win_rate": 0.23684210526315788
        },
        "BLUAI_USDT": {
          "gross_pnl": 0.057224699999999996,
          "pf": 2.149059129093506,
          "severe_pnl": 0.033224699999999996,
          "trades": 6,
          "win_rate": 0.8333333333333334
        },
        "BLUR_USDT": {
          "gross_pnl": 0.0958665,
          "pf": 2.745500498075007,
          "severe_pnl": 0.051866499999999996,
          "trades": 11,
          "win_rate": 0.18181818181818182
        },
        "BNB_USDT": {
          "gross_pnl": 0.0009191,
          "pf": 0.0,
          "severe_pnl": -0.0590809,
          "trades": 15,
          "win_rate": 0.0
        },
        "BOBA_USDT": {
          "gross_pnl": 0.00044800000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0075520000000000006,
          "trades": 2,
          "win_rate": 0.0
        },
        "BRETT_USDT": {
          "gross_pnl": 0.034249100000000005,
          "pf": 0.26721448139261333,
          "severe_pnl": -0.0577509,
          "trades": 23,
          "win_rate": 0.17391304347826086
        },
        "BREV_USDT": {
          "gross_pnl": -0.00040299999999999993,
          "pf": 0.0,
          "severe_pnl": -0.016403,
          "trades": 4,
          "win_rate": 0.0
        },
        "BR_USDT": {
          "gross_pnl": 0.0018193,
          "pf": 0.0,
          "severe_pnl": -0.0021807,
          "trades": 1,
          "win_rate": 0.0
        },
        "BSB_USDT": {
          "gross_pnl": -0.013371500000000012,
          "pf": 0.27296065421028165,
          "severe_pnl": -0.7573714999999996,
          "trades": 186,
          "win_rate": 0.25806451612903225
        },
        "BSV_USDT": {
          "gross_pnl": 0.004396200000000003,
          "pf": 0.22232560984133642,
          "severe_pnl": -0.035603800000000005,
          "trades": 10,
          "win_rate": 0.2
        },
        "BTW_USDT": {
          "gross_pnl": -0.061691300000000025,
          "pf": 0.2716860062637154,
          "severe_pnl": -0.18569130000000003,
          "trades": 31,
          "win_rate": 0.16129032258064516
        },
        "BUILDONBOB_USDT": {
          "gross_pnl": -0.007497500000000001,
          "pf": 0.1311349324616642,
          "severe_pnl": -0.0234975,
          "trades": 4,
          "win_rate": 0.25
        },
        "BULLA_USDT": {
          "gross_pnl": -0.039161299999999996,
          "pf": 0.08879498684322605,
          "severe_pnl": -0.07916129999999999,
          "trades": 10,
          "win_rate": 0.5
        },
        "CAKE_USDT": {
          "gross_pnl": -0.0021558999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0461559,
          "trades": 11,
          "win_rate": 0.0
        },
        "CAP_USDT": {
          "gross_pnl": 0.0493084,
          "pf": 0.326990221807929,
          "severe_pnl": -0.19869160000000002,
          "trades": 62,
          "win_rate": 0.2903225806451613
        },
        "CASHCAT_USDT": {
          "gross_pnl": -0.12467470000000003,
          "pf": 0.3925202387258462,
          "severe_pnl": -0.2286747,
          "trades": 26,
          "win_rate": 0.34615384615384615
        },
        "CC_USDT": {
          "gross_pnl": -0.019434299999999998,
          "pf": 0.017857454952199522,
          "severe_pnl": -0.0674343,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "CFX_USDT": {
          "gross_pnl": 0.0064627999999999994,
          "pf": 0.03726726789368897,
          "severe_pnl": -0.041537199999999996,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "CHIP_USDT": {
          "gross_pnl": 0.028819400000000002,
          "pf": 0.1024776651524677,
          "severe_pnl": -0.1631806,
          "trades": 48,
          "win_rate": 0.08333333333333333
        },
        "CHR_USDT": {
          "gross_pnl": 0.0018214,
          "pf": 0.0,
          "severe_pnl": -0.0061786,
          "trades": 2,
          "win_rate": 0.0
        },
        "CHZ_USDT": {
          "gross_pnl": 0.0098949,
          "pf": 0.008558748402486398,
          "severe_pnl": -0.05810510000000001,
          "trades": 17,
          "win_rate": 0.058823529411764705
        },
        "CLO_USDT": {
          "gross_pnl": 0.0691099,
          "pf": 10.762709836233716,
          "severe_pnl": 0.05710989999999999,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "COAI_USDT": {
          "gross_pnl": -0.014966800000000002,
          "pf": 0.09298740825121403,
          "severe_pnl": -0.08296680000000001,
          "trades": 17,
          "win_rate": 0.11764705882352941
        },
        "COLLECT_USDT": {
          "gross_pnl": 0.0048618,
          "pf": 0.3965963898754893,
          "severe_pnl": -0.059138199999999995,
          "trades": 16,
          "win_rate": 0.375
        },
        "COMP_USDT": {
          "gross_pnl": -0.004694,
          "pf": 0.0,
          "severe_pnl": -0.020694,
          "trades": 4,
          "win_rate": 0.0
        },
        "COOKIE_USDT": {
          "gross_pnl": 0.0011351,
          "pf": 0.0,
          "severe_pnl": -0.0028649,
          "trades": 1,
          "win_rate": 0.0
        },
        "CORE_USDT": {
          "gross_pnl": 0.0078783,
          "pf": 0.15053864658508526,
          "severe_pnl": -0.008121699999999999,
          "trades": 4,
          "win_rate": 0.25
        },
        "COW_USDT": {
          "gross_pnl": -0.0040295999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0080296,
          "trades": 1,
          "win_rate": 0.0
        },
        "CROSS_USDT": {
          "gross_pnl": 0.0109139,
          "pf": 0.7465876478685923,
          "severe_pnl": -0.0010861000000000004,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "CRO_USDT": {
          "gross_pnl": -0.06599989999999999,
          "pf": 0.02143671668067659,
          "severe_pnl": -0.22199989999999997,
          "trades": 39,
          "win_rate": 0.05128205128205128
        },
        "CRV_USDT": {
          "gross_pnl": 0.005080100000000005,
          "pf": 0.06418294136277988,
          "severe_pnl": -0.27891990000000005,
          "trades": 71,
          "win_rate": 0.11267605633802817
        },
        "CTC_USDT": {
          "gross_pnl": 0.0259687,
          "pf": 0.0033188879163731236,
          "severe_pnl": -0.0700313,
          "trades": 24,
          "win_rate": 0.041666666666666664
        },
        "CTR_USDT": {
          "gross_pnl": -0.002442,
          "pf": 0.0,
          "severe_pnl": -0.006442,
          "trades": 1,
          "win_rate": 0.0
        },
        "CVX_USDT": {
          "gross_pnl": 0.002459899999999998,
          "pf": 0.17158785934428342,
          "severe_pnl": -0.0295401,
          "trades": 8,
          "win_rate": 0.25
        },
        "CYS_USDT": {
          "gross_pnl": 0.019901099999999998,
          "pf": 0.4710416591369833,
          "severe_pnl": -0.0160989,
          "trades": 9,
          "win_rate": 0.4444444444444444
        },
        "C_USDT": {
          "gross_pnl": 0.008033400000000001,
          "pf": 999,
          "severe_pnl": 0.004033400000000001,
          "trades": 1,
          "win_rate": 1.0
        },
        "DASH_USDT": {
          "gross_pnl": 0.017119400000000003,
          "pf": 0.022681402048409217,
          "severe_pnl": -0.3428806000000001,
          "trades": 90,
          "win_rate": 0.03333333333333333
        },
        "DEEP_USDT": {
          "gross_pnl": -0.0031478,
          "pf": 0.0,
          "severe_pnl": -0.0231478,
          "trades": 5,
          "win_rate": 0.0
        },
        "DEXE_USDT": {
          "gross_pnl": -0.03539789999999998,
          "pf": 0.35062400207648176,
          "severe_pnl": -0.5433978999999999,
          "trades": 127,
          "win_rate": 0.2755905511811024
        },
        "DODO_USDT": {
          "gross_pnl": -0.018270599999999967,
          "pf": 0.561664793628894,
          "severe_pnl": -0.47027060000000004,
          "trades": 113,
          "win_rate": 0.46017699115044247
        },
        "DOGE_USDT": {
          "gross_pnl": 0.019358500000000004,
          "pf": 0.0,
          "severe_pnl": -0.12464150000000002,
          "trades": 36,
          "win_rate": 0.0
        },
        "DOGS_USDT": {
          "gross_pnl": 0.011275400000000001,
          "pf": 0.058697059237371625,
          "severe_pnl": -0.0167246,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "DOT_USDT": {
          "gross_pnl": 0.0615284,
          "pf": 0.03997922473134796,
          "severe_pnl": -0.2624716,
          "trades": 81,
          "win_rate": 0.037037037037037035
        },
        "DRAM_USDT": {
          "gross_pnl": -0.0755561,
          "pf": 0.09775447358423209,
          "severe_pnl": -0.2835561,
          "trades": 52,
          "win_rate": 0.17307692307692307
        },
        "DYDX_USDT": {
          "gross_pnl": -0.009406799999999998,
          "pf": 0.0,
          "severe_pnl": -0.07340680000000001,
          "trades": 16,
          "win_rate": 0.0
        },
        "EDEN_USDT": {
          "gross_pnl": 0.0036303000000000004,
          "pf": 0.13544274381806468,
          "severe_pnl": -0.0163697,
          "trades": 5,
          "win_rate": 0.4
        },
        "EDGE_USDT": {
          "gross_pnl": -0.02004540000000003,
          "pf": 0.2259613414757398,
          "severe_pnl": -0.34004539999999994,
          "trades": 80,
          "win_rate": 0.275
        },
        "EDU_USDT": {
          "gross_pnl": -0.001764299999999999,
          "pf": 0.24320362825645714,
          "severe_pnl": -0.025764299999999997,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "EGLD_USDT": {
          "gross_pnl": -0.038971199999999984,
          "pf": 0.10464718898960733,
          "severe_pnl": -0.5509712000000001,
          "trades": 128,
          "win_rate": 0.1484375
        },
        "EIGEN_USDT": {
          "gross_pnl": -0.03859060000000003,
          "pf": 0.06825720024518692,
          "severe_pnl": -0.8785906000000002,
          "trades": 210,
          "win_rate": 0.11904761904761904
        },
        "ELSA_USDT": {
          "gross_pnl": 0.14731509999999998,
          "pf": 2.0027857186483753,
          "severe_pnl": 0.0673151,
          "trades": 20,
          "win_rate": 0.3
        },
        "ENA_USDT": {
          "gross_pnl": -0.0013168000000000014,
          "pf": 0.05868614898995408,
          "severe_pnl": -0.23731680000000002,
          "trades": 59,
          "win_rate": 0.06779661016949153
        },
        "ENJ_USDT": {
          "gross_pnl": 0.0038188,
          "pf": 0.00356343822170901,
          "severe_pnl": -0.044181200000000004,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "ENSO_USDT": {
          "gross_pnl": 0.0004077,
          "pf": 0.0,
          "severe_pnl": -0.0115923,
          "trades": 3,
          "win_rate": 0.0
        },
        "ENS_USDT": {
          "gross_pnl": 0.02818649999999999,
          "pf": 0.10119668337192304,
          "severe_pnl": -0.16781350000000003,
          "trades": 49,
          "win_rate": 0.1836734693877551
        },
        "EPIC_USDT": {
          "gross_pnl": -0.0038149,
          "pf": 0.0,
          "severe_pnl": -0.0078149,
          "trades": 1,
          "win_rate": 0.0
        },
        "ERA_USDT": {
          "gross_pnl": 0.0025302999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0014697000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "ESPORTS_USDT": {
          "gross_pnl": -0.08377590000000013,
          "pf": 0.6250912215755758,
          "severe_pnl": -0.47977590000000025,
          "trades": 99,
          "win_rate": 0.3939393939393939
        },
        "ESP_USDT": {
          "gross_pnl": 0.0068005999999999995,
          "pf": 0.0,
          "severe_pnl": -0.005199400000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "ETC_USDT": {
          "gross_pnl": 0.008722699999999998,
          "pf": 0.0,
          "severe_pnl": -0.0672773,
          "trades": 19,
          "win_rate": 0.0
        },
        "ETHFI_USDT": {
          "gross_pnl": 0.05824619999999997,
          "pf": 0.06575350665940158,
          "severe_pnl": -0.5337538000000003,
          "trades": 148,
          "win_rate": 0.13513513513513514
        },
        "ETH_USDT": {
          "gross_pnl": -0.015305000000000003,
          "pf": 0.025287641942376936,
          "severe_pnl": -0.35930499999999993,
          "trades": 86,
          "win_rate": 0.03488372093023256
        },
        "EUL_USDT": {
          "gross_pnl": 0.0010256,
          "pf": 0.0,
          "severe_pnl": -0.0029744000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "EVAA_USDT": {
          "gross_pnl": 0.10169550000000005,
          "pf": 0.8266223958979678,
          "severe_pnl": -0.09430449999999999,
          "trades": 49,
          "win_rate": 0.46938775510204084
        },
        "EWJ_USDT": {
          "gross_pnl": -0.0003227,
          "pf": 0.0,
          "severe_pnl": -0.0043227000000000005,
          "trades": 1,
          "win_rate": 0.0
        },
        "EWY_USDT": {
          "gross_pnl": 0.0003126999999999966,
          "pf": 0.05049593922828996,
          "severe_pnl": -0.22368729999999998,
          "trades": 56,
          "win_rate": 0.08928571428571429
        },
        "FET_USDT": {
          "gross_pnl": 0.002735899999999998,
          "pf": 0.013691290968099953,
          "severe_pnl": -0.2932641000000001,
          "trades": 74,
          "win_rate": 0.02702702702702703
        },
        "FF_USDT": {
          "gross_pnl": -0.004535200000000003,
          "pf": 0.19266338030582572,
          "severe_pnl": -0.05653520000000001,
          "trades": 13,
          "win_rate": 0.23076923076923078
        },
        "FHE_USDT": {
          "gross_pnl": -0.0022645999999999964,
          "pf": 0.15920497946363965,
          "severe_pnl": -0.18626460000000006,
          "trades": 46,
          "win_rate": 0.2391304347826087
        },
        "FILECOIN_USDT": {
          "gross_pnl": -0.007431400000000001,
          "pf": 0.0,
          "severe_pnl": -0.0914314,
          "trades": 21,
          "win_rate": 0.0
        },
        "FLOCK_USDT": {
          "gross_pnl": 0.0560827,
          "pf": 6.36798353469475,
          "severe_pnl": 0.020082700000000002,
          "trades": 9,
          "win_rate": 0.6666666666666666
        },
        "FLOKI_USDT": {
          "gross_pnl": 0.024943100000000006,
          "pf": 0.015331893081386242,
          "severe_pnl": -0.07105689999999999,
          "trades": 24,
          "win_rate": 0.041666666666666664
        },
        "FLOW_USDT": {
          "gross_pnl": -0.0038233,
          "pf": 0.0,
          "severe_pnl": -0.0158233,
          "trades": 3,
          "win_rate": 0.0
        },
        "FLUID_USDT": {
          "gross_pnl": -0.0037348,
          "pf": 0.0,
          "severe_pnl": -0.0077348,
          "trades": 1,
          "win_rate": 0.0
        },
        "FOGO_USDT": {
          "gross_pnl": 0.0048421,
          "pf": 0.6572641038442336,
          "severe_pnl": -0.0031579,
          "trades": 2,
          "win_rate": 0.5
        },
        "FOLKS_USDT": {
          "gross_pnl": 0.013668000000000003,
          "pf": 0.13603448021373013,
          "severe_pnl": -0.14633199999999993,
          "trades": 40,
          "win_rate": 0.2
        },
        "FORM_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "FRAX_USDT": {
          "gross_pnl": 0.0040048,
          "pf": 0.0,
          "severe_pnl": -0.003995200000000001,
          "trades": 2,
          "win_rate": 0.0
        },
        "GALA_USDT": {
          "gross_pnl": 0.0249074,
          "pf": 0.03304300505043495,
          "severe_pnl": -0.38309259999999984,
          "trades": 102,
          "win_rate": 0.0784313725490196
        },
        "GAS_USDT": {
          "gross_pnl": 0.0058252,
          "pf": 999,
          "severe_pnl": 0.0018252,
          "trades": 1,
          "win_rate": 1.0
        },
        "GENIUS_USDT": {
          "gross_pnl": -0.0150682,
          "pf": 0.0,
          "severe_pnl": -0.0310682,
          "trades": 4,
          "win_rate": 0.0
        },
        "GIGGLE_USDT": {
          "gross_pnl": 0.0041245,
          "pf": 999,
          "severe_pnl": 0.0001244999999999996,
          "trades": 1,
          "win_rate": 1.0
        },
        "GLM_USDT": {
          "gross_pnl": 0.0019684999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0100315,
          "trades": 3,
          "win_rate": 0.0
        },
        "GMT_USDT": {
          "gross_pnl": 0.0013494999999999998,
          "pf": 0.0,
          "severe_pnl": -0.0066505,
          "trades": 2,
          "win_rate": 0.0
        },
        "GPS_USDT": {
          "gross_pnl": 0.015872,
          "pf": 0.5768011204773483,
          "severe_pnl": -0.008128,
          "trades": 6,
          "win_rate": 0.5
        },
        "GRAM_USDT": {
          "gross_pnl": -0.018758199999999996,
          "pf": 0.0,
          "severe_pnl": -0.1307582,
          "trades": 28,
          "win_rate": 0.0
        },
        "GRASS_USDT": {
          "gross_pnl": -0.0040208,
          "pf": 0.09928680844198177,
          "severe_pnl": -0.0960208,
          "trades": 23,
          "win_rate": 0.13043478260869565
        },
        "GRIFFAIN_USDT": {
          "gross_pnl": -0.0012422,
          "pf": 0.0,
          "severe_pnl": -0.0052422,
          "trades": 1,
          "win_rate": 0.0
        },
        "GRT_USDT": {
          "gross_pnl": -0.007365,
          "pf": 0.0,
          "severe_pnl": -0.043365,
          "trades": 9,
          "win_rate": 0.0
        },
        "GUA_USDT": {
          "gross_pnl": -0.028931900000000007,
          "pf": 0.02522794596629766,
          "severe_pnl": -0.0489319,
          "trades": 5,
          "win_rate": 0.2
        },
        "GUN_USDT": {
          "gross_pnl": 0.04242699999999999,
          "pf": 0.666217459091781,
          "severe_pnl": -0.013573000000000002,
          "trades": 14,
          "win_rate": 0.2857142857142857
        },
        "G_USDT": {
          "gross_pnl": 0.047589099999999995,
          "pf": 1.4516270617956082,
          "severe_pnl": 0.031589099999999995,
          "trades": 4,
          "win_rate": 0.5
        },
        "HBAR_USDT": {
          "gross_pnl": -0.008859999999999998,
          "pf": 0.004828195156775442,
          "severe_pnl": -0.2648599999999999,
          "trades": 64,
          "win_rate": 0.015625
        },
        "HEI_USDT": {
          "gross_pnl": 0.021795,
          "pf": 0.27804410842763294,
          "severe_pnl": -0.17020500000000005,
          "trades": 48,
          "win_rate": 0.3125
        },
        "HIGH_USDT": {
          "gross_pnl": 0.012263400000000006,
          "pf": 0.37479977565900163,
          "severe_pnl": -0.055736600000000004,
          "trades": 17,
          "win_rate": 0.35294117647058826
        },
        "HK50_USDT": {
          "gross_pnl": 0.004957499999999999,
          "pf": 0.0,
          "severe_pnl": -0.043042500000000004,
          "trades": 12,
          "win_rate": 0.0
        },
        "HMSTR_USDT": {
          "gross_pnl": 0.027722000000000004,
          "pf": 0.8432053833551406,
          "severe_pnl": -0.004278000000000001,
          "trades": 8,
          "win_rate": 0.25
        },
        "HNT_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.008,
          "trades": 2,
          "win_rate": 0.0
        },
        "HOLO_USDT": {
          "gross_pnl": -0.0011301,
          "pf": 0.0,
          "severe_pnl": -0.0051301,
          "trades": 1,
          "win_rate": 0.0
        },
        "HOME_USDT": {
          "gross_pnl": -0.03914440000000001,
          "pf": 0.4325973981899215,
          "severe_pnl": -0.25914440000000005,
          "trades": 55,
          "win_rate": 0.34545454545454546
        },
        "HOT_USDT": {
          "gross_pnl": 0.0239389,
          "pf": 0.9973163972083503,
          "severe_pnl": -6.110000000000143e-05,
          "trades": 6,
          "win_rate": 0.6666666666666666
        },
        "HYPE_USDT": {
          "gross_pnl": -0.011224699999999994,
          "pf": 0.020464708531720503,
          "severe_pnl": -0.2192247,
          "trades": 52,
          "win_rate": 0.07692307692307693
        },
        "ICP_USDT": {
          "gross_pnl": -0.023919399999999997,
          "pf": 0.009462671985160721,
          "severe_pnl": -0.31591940000000013,
          "trades": 73,
          "win_rate": 0.0273972602739726
        },
        "ICX_USDT": {
          "gross_pnl": 0.0021133,
          "pf": 0.0,
          "severe_pnl": -0.0018867000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "ID_USDT": {
          "gross_pnl": 0.015428,
          "pf": 0.6496363789628563,
          "severe_pnl": -0.0045720000000000005,
          "trades": 5,
          "win_rate": 0.2
        },
        "IMX_USDT": {
          "gross_pnl": 0.0007429999999999997,
          "pf": 0.0,
          "severe_pnl": -0.027257,
          "trades": 7,
          "win_rate": 0.0
        },
        "INDA_USDT": {
          "gross_pnl": 0.018995199999999997,
          "pf": 0.26244805225050843,
          "severe_pnl": -0.0570048,
          "trades": 19,
          "win_rate": 0.3157894736842105
        },
        "INJ_USDT": {
          "gross_pnl": 0.0023499000000000037,
          "pf": 0.02214649480240178,
          "severe_pnl": -0.34965009999999996,
          "trades": 88,
          "win_rate": 0.045454545454545456
        },
        "INTW_USDT": {
          "gross_pnl": 0.0291572,
          "pf": 1.410769396397043,
          "severe_pnl": 0.0091572,
          "trades": 5,
          "win_rate": 0.4
        },
        "IN_USDT": {
          "gross_pnl": 0.014956400000000002,
          "pf": 999,
          "severe_pnl": 0.010956400000000002,
          "trades": 1,
          "win_rate": 1.0
        },
        "IOTA_USDT": {
          "gross_pnl": -0.013166899999999999,
          "pf": 0.0,
          "severe_pnl": -0.021166900000000002,
          "trades": 2,
          "win_rate": 0.0
        },
        "IOTX_USDT": {
          "gross_pnl": 0.0,
          "pf": 0.0,
          "severe_pnl": -0.004,
          "trades": 1,
          "win_rate": 0.0
        },
        "IO_USDT": {
          "gross_pnl": 0.004796,
          "pf": 0.05503450716687295,
          "severe_pnl": -0.0032040000000000007,
          "trades": 2,
          "win_rate": 0.5
        },
        "JASMY_USDT": {
          "gross_pnl": 0.004833599999999994,
          "pf": 0.024028433383328583,
          "severe_pnl": -0.23516640000000003,
          "trades": 60,
          "win_rate": 0.06666666666666667
        },
        "JCT_USDT": {
          "gross_pnl": -0.0178162,
          "pf": 0.10270386039625165,
          "severe_pnl": -0.057816200000000005,
          "trades": 10,
          "win_rate": 0.4
        },
        "JP225_USDT": {
          "gross_pnl": 0.012246400000000001,
          "pf": 0.10835466121395135,
          "severe_pnl": -0.0197536,
          "trades": 8,
          "win_rate": 0.125
        },
        "JST_USDT": {
          "gross_pnl": 0.0034276999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0205723,
          "trades": 6,
          "win_rate": 0.0
        },
        "JTO_USDT": {
          "gross_pnl": 0.0956259,
          "pf": 0.11626185433988902,
          "severe_pnl": -0.24437410000000004,
          "trades": 85,
          "win_rate": 0.1411764705882353
        },
        "JUP_USDT": {
          "gross_pnl": 0.06393689999999998,
          "pf": 0.05455509537575887,
          "severe_pnl": -0.5040631000000001,
          "trades": 142,
          "win_rate": 0.1056338028169014
        },
        "KAIA_USDT": {
          "gross_pnl": -0.0036013,
          "pf": 0.0,
          "severe_pnl": -0.0236013,
          "trades": 5,
          "win_rate": 0.0
        },
        "KAITO_USDT": {
          "gross_pnl": 0.10362939999999998,
          "pf": 0.5265136885152788,
          "severe_pnl": -0.10837059999999998,
          "trades": 53,
          "win_rate": 0.2830188679245283
        },
        "KAS_USDT": {
          "gross_pnl": 0.016892299999999996,
          "pf": 0.0,
          "severe_pnl": -0.09110769999999999,
          "trades": 27,
          "win_rate": 0.0
        },
        "KERNEL_USDT": {
          "gross_pnl": 0.0014731,
          "pf": 0.0,
          "severe_pnl": -0.0025269000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "KITE_USDT": {
          "gross_pnl": -0.0456776,
          "pf": 0.05432365461592223,
          "severe_pnl": -0.16967760000000004,
          "trades": 31,
          "win_rate": 0.12903225806451613
        },
        "KMNO_USDT": {
          "gross_pnl": -0.008393699999999999,
          "pf": 0.0,
          "severe_pnl": -0.036393699999999994,
          "trades": 7,
          "win_rate": 0.0
        },
        "KORU_USDT": {
          "gross_pnl": 0.021680999999999992,
          "pf": 0.45807058787988386,
          "severe_pnl": -0.2583190000000001,
          "trades": 70,
          "win_rate": 0.35714285714285715
        },
        "KSM_USDT": {
          "gross_pnl": -0.0047940000000000005,
          "pf": 0.0,
          "severe_pnl": -0.016794000000000003,
          "trades": 3,
          "win_rate": 0.0
        },
        "KSTR_USDT": {
          "gross_pnl": -0.0024673000000000004,
          "pf": 0.0,
          "severe_pnl": -0.010467300000000002,
          "trades": 2,
          "win_rate": 0.0
        },
        "LAB_USDT": {
          "gross_pnl": -0.08045929999999998,
          "pf": 0.5826993969109185,
          "severe_pnl": -0.3084593,
          "trades": 57,
          "win_rate": 0.3684210526315789
        },
        "LAYER_USDT": {
          "gross_pnl": 0.0020495,
          "pf": 0.0,
          "severe_pnl": -0.0019505,
          "trades": 1,
          "win_rate": 0.0
        },
        "LDO_USDT": {
          "gross_pnl": 0.11787979999999991,
          "pf": 0.14031642755995263,
          "severe_pnl": -0.5341202,
          "trades": 163,
          "win_rate": 0.18404907975460122
        },
        "LEAD_USDT": {
          "gross_pnl": 0.0010641,
          "pf": 0.0,
          "severe_pnl": -0.022935900000000002,
          "trades": 6,
          "win_rate": 0.0
        },
        "LIGHT_USDT": {
          "gross_pnl": -0.015304800000000004,
          "pf": 0.009145102573447776,
          "severe_pnl": -0.04730480000000001,
          "trades": 8,
          "win_rate": 0.125
        },
        "LINEA_USDT": {
          "gross_pnl": -0.0066116000000000005,
          "pf": 0.0,
          "severe_pnl": -0.0346116,
          "trades": 7,
          "win_rate": 0.0
        },
        "LINK_USDT": {
          "gross_pnl": 0.006828899999999998,
          "pf": 0.005436637540859096,
          "severe_pnl": -0.22117110000000006,
          "trades": 57,
          "win_rate": 0.017543859649122806
        },
        "LIT_USDT": {
          "gross_pnl": -0.08419530000000003,
          "pf": 0.07219441756559072,
          "severe_pnl": -0.7081953000000003,
          "trades": 156,
          "win_rate": 0.11538461538461539
        },
        "LRC_USDT": {
          "gross_pnl": 0.16840339999999998,
          "pf": 1.0740204088147969,
          "severe_pnl": 0.02040340000000001,
          "trades": 37,
          "win_rate": 0.5405405405405406
        },
        "LTC_USDT": {
          "gross_pnl": 0.0015195000000000005,
          "pf": 0.0,
          "severe_pnl": -0.1864805,
          "trades": 47,
          "win_rate": 0.0
        },
        "LUMIA_USDT": {
          "gross_pnl": 0.0359409,
          "pf": 0.6082513303075359,
          "severe_pnl": -0.048059100000000014,
          "trades": 21,
          "win_rate": 0.38095238095238093
        },
        "LUNANEW_USDT": {
          "gross_pnl": -0.0038916000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0118916,
          "trades": 2,
          "win_rate": 0.0
        },
        "LUNC_USDT": {
          "gross_pnl": 0.00032809999999999665,
          "pf": 0.010718408030942265,
          "severe_pnl": -0.18367190000000003,
          "trades": 46,
          "win_rate": 0.021739130434782608
        },
        "LYN_USDT": {
          "gross_pnl": 0.0259888,
          "pf": 999,
          "severe_pnl": 0.0179888,
          "trades": 2,
          "win_rate": 1.0
        },
        "MAGMA_USDT": {
          "gross_pnl": 0.22400910000000007,
          "pf": 0.7696457250049361,
          "severe_pnl": -0.1399908999999999,
          "trades": 91,
          "win_rate": 0.4175824175824176
        },
        "MANA_USDT": {
          "gross_pnl": 0.0078239,
          "pf": 0.16574302069009628,
          "severe_pnl": -0.052176099999999996,
          "trades": 15,
          "win_rate": 0.2
        },
        "MANTA_USDT": {
          "gross_pnl": -0.011781500000000002,
          "pf": 0.062032999976451855,
          "severe_pnl": -0.0517815,
          "trades": 10,
          "win_rate": 0.2
        },
        "MANTRA_USDT": {
          "gross_pnl": -0.0378847,
          "pf": 0.31304189298254265,
          "severe_pnl": -0.1058847,
          "trades": 17,
          "win_rate": 0.29411764705882354
        },
        "MASK_USDT": {
          "gross_pnl": 0.0027976,
          "pf": 0.0,
          "severe_pnl": -0.0012024000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "MAV_USDT": {
          "gross_pnl": 0.020191399999999998,
          "pf": 13.218675417661093,
          "severe_pnl": 0.0081914,
          "trades": 3,
          "win_rate": 0.6666666666666666
        },
        "MEGA_USDT": {
          "gross_pnl": 0.0001926,
          "pf": 0.0,
          "severe_pnl": -0.0078074,
          "trades": 2,
          "win_rate": 0.0
        },
        "MEME_USDT": {
          "gross_pnl": -0.00011300000000000025,
          "pf": 0.12091317408930494,
          "severe_pnl": -0.024113000000000002,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "MERL_USDT": {
          "gross_pnl": -0.0029157000000000002,
          "pf": 0.0749165435935254,
          "severe_pnl": -0.0469157,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "METIS_USDT": {
          "gross_pnl": -0.0015055,
          "pf": 0.0,
          "severe_pnl": -0.0095055,
          "trades": 2,
          "win_rate": 0.0
        },
        "MET_USDT": {
          "gross_pnl": 0.0088403,
          "pf": 0.18436201244224165,
          "severe_pnl": -0.0031597,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "MEW_USDT": {
          "gross_pnl": 0.0032795999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0007204000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "ME_USDT": {
          "gross_pnl": 0.0052715999999999996,
          "pf": 999,
          "severe_pnl": 0.0012715999999999995,
          "trades": 1,
          "win_rate": 1.0
        },
        "MINA_USDT": {
          "gross_pnl": -0.0037091,
          "pf": 0.0,
          "severe_pnl": -0.0117091,
          "trades": 2,
          "win_rate": 0.0
        },
        "MIRA_USDT": {
          "gross_pnl": -0.0062966,
          "pf": 0.0,
          "severe_pnl": -0.0182966,
          "trades": 3,
          "win_rate": 0.0
        },
        "MITO_USDT": {
          "gross_pnl": 0.0998494,
          "pf": 999,
          "severe_pnl": 0.07584940000000001,
          "trades": 6,
          "win_rate": 1.0
        },
        "MMT_USDT": {
          "gross_pnl": 0.05693490000000001,
          "pf": 0.40630416396584645,
          "severe_pnl": -0.15506510000000004,
          "trades": 53,
          "win_rate": 0.2830188679245283
        },
        "MNT_USDT": {
          "gross_pnl": 0.005274600000000001,
          "pf": 0.03725157742431096,
          "severe_pnl": -0.0387254,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "MOCA_USDT": {
          "gross_pnl": 0.006711399999999999,
          "pf": 999,
          "severe_pnl": 0.0027113999999999992,
          "trades": 1,
          "win_rate": 1.0
        },
        "MONAD_USDT": {
          "gross_pnl": 0.030447600000000005,
          "pf": 0.08635106173027587,
          "severe_pnl": -0.10555239999999999,
          "trades": 34,
          "win_rate": 0.11764705882352941
        },
        "MOODENG_USDT": {
          "gross_pnl": -0.0417115,
          "pf": 0.0,
          "severe_pnl": -0.0457115,
          "trades": 1,
          "win_rate": 0.0
        },
        "MORPHO_USDT": {
          "gross_pnl": 0.012918100000000004,
          "pf": 0.1383771416119631,
          "severe_pnl": -0.0790819,
          "trades": 23,
          "win_rate": 0.17391304347826086
        },
        "MOVE_USDT": {
          "gross_pnl": 0.0008976,
          "pf": 0.0,
          "severe_pnl": -0.0111024,
          "trades": 3,
          "win_rate": 0.0
        },
        "MSTU_USDT": {
          "gross_pnl": 0.0422371,
          "pf": 1.6072915422546026,
          "severe_pnl": 0.014237100000000004,
          "trades": 7,
          "win_rate": 0.5714285714285714
        },
        "MUBARAK_USDT": {
          "gross_pnl": -0.0021723000000000003,
          "pf": 0.0,
          "severe_pnl": -0.0061723,
          "trades": 1,
          "win_rate": 0.0
        },
        "MUU_USDT": {
          "gross_pnl": 0.00508,
          "pf": 0.13681269334397766,
          "severe_pnl": -0.006920000000000001,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "MVLL_USDT": {
          "gross_pnl": -0.0240161,
          "pf": 0.48652606457002967,
          "severe_pnl": -0.1320161,
          "trades": 27,
          "win_rate": 0.4444444444444444
        },
        "MYX_USDT": {
          "gross_pnl": 0.19028879999999995,
          "pf": 0.5502958818692267,
          "severe_pnl": -0.13371119999999997,
          "trades": 81,
          "win_rate": 0.37037037037037035
        },
        "NAORIS_USDT": {
          "gross_pnl": 0.0873863,
          "pf": 1.351583880275445,
          "severe_pnl": 0.019386299999999995,
          "trades": 17,
          "win_rate": 0.4117647058823529
        },
        "NEAR_USDT": {
          "gross_pnl": 0.08515340000000002,
          "pf": 0.05377750052329489,
          "severe_pnl": -0.27484660000000005,
          "trades": 90,
          "win_rate": 0.1111111111111111
        },
        "NEO_USDT": {
          "gross_pnl": -0.0079313,
          "pf": 0.0,
          "severe_pnl": -0.015931300000000002,
          "trades": 2,
          "win_rate": 0.0
        },
        "NES_USDT": {
          "gross_pnl": 0.039093900000000015,
          "pf": 0.2931121222623453,
          "severe_pnl": -0.0569061,
          "trades": 24,
          "win_rate": 0.375
        },
        "NEX_USDT": {
          "gross_pnl": 0.0528831,
          "pf": 999,
          "severe_pnl": 0.0488831,
          "trades": 1,
          "win_rate": 1.0
        },
        "NGAS_USDT": {
          "gross_pnl": 0.008406200000000004,
          "pf": 0.008646620514717533,
          "severe_pnl": -0.18759380000000003,
          "trades": 49,
          "win_rate": 0.04081632653061224
        },
        "NICKEL_USDT": {
          "gross_pnl": -0.0042958,
          "pf": 0.0,
          "severe_pnl": -0.04829580000000001,
          "trades": 11,
          "win_rate": 0.0
        },
        "NIGHT_USDT": {
          "gross_pnl": -0.017866200000000002,
          "pf": 0.047152080390601314,
          "severe_pnl": -0.0738662,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "NIL_USDT": {
          "gross_pnl": 0.005114900000000001,
          "pf": 0.0,
          "severe_pnl": -0.0348851,
          "trades": 10,
          "win_rate": 0.0
        },
        "NOM_USDT": {
          "gross_pnl": 0.0017853999999999995,
          "pf": 0.08739546851547418,
          "severe_pnl": -0.0102146,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "NOT_USDT": {
          "gross_pnl": -0.006584999999999999,
          "pf": 0.0,
          "severe_pnl": -0.022585,
          "trades": 4,
          "win_rate": 0.0
        },
        "OFC_USDT": {
          "gross_pnl": -0.0040152,
          "pf": 0.10780547609317531,
          "severe_pnl": -0.0240152,
          "trades": 5,
          "win_rate": 0.2
        },
        "OGN_USDT": {
          "gross_pnl": 0.007182600000000001,
          "pf": 0.49704682246035825,
          "severe_pnl": -0.0608174,
          "trades": 17,
          "win_rate": 0.29411764705882354
        },
        "OG_USDT": {
          "gross_pnl": 0.012393000000000001,
          "pf": 0.44334701688323713,
          "severe_pnl": -0.003607,
          "trades": 4,
          "win_rate": 0.5
        },
        "OKB_USDT": {
          "gross_pnl": -0.0009872,
          "pf": 0.0,
          "severe_pnl": -0.0049872,
          "trades": 1,
          "win_rate": 0.0
        },
        "OL_USDT": {
          "gross_pnl": 0.0021853999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0058146,
          "trades": 2,
          "win_rate": 0.0
        },
        "ONDO_USDT": {
          "gross_pnl": 0.07259510000000001,
          "pf": 0.0771039101281394,
          "severe_pnl": -0.4274049000000002,
          "trades": 125,
          "win_rate": 0.152
        },
        "ONE_USDT": {
          "gross_pnl": -0.0089851,
          "pf": 0.0,
          "severe_pnl": -0.0289851,
          "trades": 5,
          "win_rate": 0.0
        },
        "ONT_USDT": {
          "gross_pnl": -0.0008782,
          "pf": 0.0,
          "severe_pnl": -0.0048782,
          "trades": 1,
          "win_rate": 0.0
        },
        "OPENAI_USDT": {
          "gross_pnl": 0.060879,
          "pf": 0.0,
          "severe_pnl": -0.2991210000000001,
          "trades": 90,
          "win_rate": 0.0
        },
        "OPG_USDT": {
          "gross_pnl": -0.0334007,
          "pf": 0.02775059303668418,
          "severe_pnl": -0.1214007,
          "trades": 22,
          "win_rate": 0.13636363636363635
        },
        "OPN_USDT": {
          "gross_pnl": 0.029161700000000013,
          "pf": 0.2878676313336164,
          "severe_pnl": -0.1548383,
          "trades": 46,
          "win_rate": 0.2826086956521739
        },
        "OP_USDT": {
          "gross_pnl": 0.1812308,
          "pf": 0.07600130467510384,
          "severe_pnl": -0.5107692000000001,
          "trades": 173,
          "win_rate": 0.11560693641618497
        },
        "ORCA_USDT": {
          "gross_pnl": 0.002521,
          "pf": 0.0,
          "severe_pnl": -0.0014790000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "ORDI_USDT": {
          "gross_pnl": 0.027061199999999994,
          "pf": 0.06557542037942074,
          "severe_pnl": -0.48093880000000006,
          "trades": 127,
          "win_rate": 0.12598425196850394
        },
        "O_USDT": {
          "gross_pnl": -0.04317419999999999,
          "pf": 0.15045492877515645,
          "severe_pnl": -0.2551742,
          "trades": 53,
          "win_rate": 0.16981132075471697
        },
        "PARTI_USDT": {
          "gross_pnl": -0.0117541,
          "pf": 0.6235301563008055,
          "severe_pnl": -0.051754100000000004,
          "trades": 10,
          "win_rate": 0.3
        },
        "PAXG_USDT": {
          "gross_pnl": 0.0077526999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0122473,
          "trades": 5,
          "win_rate": 0.0
        },
        "PENDLE_USDT": {
          "gross_pnl": 0.008127800000000003,
          "pf": 0.033639091245254875,
          "severe_pnl": -0.12387220000000002,
          "trades": 33,
          "win_rate": 0.15151515151515152
        },
        "PEOPLE_USDT": {
          "gross_pnl": 0.0023645,
          "pf": 0.0,
          "severe_pnl": -0.0016355000000000002,
          "trades": 1,
          "win_rate": 0.0
        },
        "PEPE_USDT": {
          "gross_pnl": 0.0011914000000000009,
          "pf": 0.0,
          "severe_pnl": -0.0188086,
          "trades": 5,
          "win_rate": 0.0
        },
        "PHA_USDT": {
          "gross_pnl": 0.0141825,
          "pf": 999,
          "severe_pnl": 0.0021824999999999995,
          "trades": 3,
          "win_rate": 1.0
        },
        "PIEVERSE_USDT": {
          "gross_pnl": 0.0005064000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0194936,
          "trades": 5,
          "win_rate": 0.0
        },
        "PIPPIN_USDT": {
          "gross_pnl": 0.10960170000000001,
          "pf": 0.40811898682322023,
          "severe_pnl": -0.16239830000000005,
          "trades": 68,
          "win_rate": 0.16176470588235295
        },
        "PIXEL_USDT": {
          "gross_pnl": 0.010740900000000001,
          "pf": 999,
          "severe_pnl": 0.0027409,
          "trades": 2,
          "win_rate": 1.0
        },
        "PI_USDT": {
          "gross_pnl": 0.0016881999999999939,
          "pf": 0.171634646170016,
          "severe_pnl": -0.7503117999999994,
          "trades": 188,
          "win_rate": 0.19148936170212766
        },
        "PLUME_USDT": {
          "gross_pnl": 0.006978399999999999,
          "pf": 0.0,
          "severe_pnl": -0.005021600000000001,
          "trades": 3,
          "win_rate": 0.0
        },
        "PNUT_USDT": {
          "gross_pnl": 0.0049173,
          "pf": 0.18037276328733617,
          "severe_pnl": -0.0030827,
          "trades": 2,
          "win_rate": 0.5
        },
        "POL_USDT": {
          "gross_pnl": 0.020553199999999994,
          "pf": 0.04356265090486792,
          "severe_pnl": -0.1874468,
          "trades": 52,
          "win_rate": 0.07692307692307693
        },
        "POPCAT_USDT": {
          "gross_pnl": -0.0016254999999999998,
          "pf": 0.034946065203379846,
          "severe_pnl": -0.013625500000000002,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "PORTAL_USDT": {
          "gross_pnl": -0.0008795,
          "pf": 0.0,
          "severe_pnl": -0.0048795,
          "trades": 1,
          "win_rate": 0.0
        },
        "POWER_USDT": {
          "gross_pnl": 0.0072770000000000005,
          "pf": 0.6144000000000002,
          "severe_pnl": -0.0007229999999999997,
          "trades": 2,
          "win_rate": 0.5
        },
        "POWR_USDT": {
          "gross_pnl": -0.0122856,
          "pf": 0.0,
          "severe_pnl": -0.0162856,
          "trades": 1,
          "win_rate": 0.0
        },
        "PROMPT_USDT": {
          "gross_pnl": -0.010526299999999999,
          "pf": 0.0,
          "severe_pnl": -0.014526299999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "PROM_USDT": {
          "gross_pnl": 0.0074091999999999995,
          "pf": 0.3288332630197346,
          "severe_pnl": -0.008590800000000003,
          "trades": 4,
          "win_rate": 0.25
        },
        "PTB_USDT": {
          "gross_pnl": 0.0258193,
          "pf": 999,
          "severe_pnl": 0.0218193,
          "trades": 1,
          "win_rate": 1.0
        },
        "PUMPFUN_USDT": {
          "gross_pnl": 0.07657739999999999,
          "pf": 0.2071050662268272,
          "severe_pnl": -0.3634226000000001,
          "trades": 110,
          "win_rate": 0.16363636363636364
        },
        "PUNDIX_USDT": {
          "gross_pnl": 0.0007463,
          "pf": 0.0,
          "severe_pnl": -0.0032537,
          "trades": 1,
          "win_rate": 0.0
        },
        "PYTH_USDT": {
          "gross_pnl": 0.025940199999999983,
          "pf": 0.07072159333974522,
          "severe_pnl": -0.4900598,
          "trades": 129,
          "win_rate": 0.12403100775193798
        },
        "QNT_USDT": {
          "gross_pnl": 0.0013696,
          "pf": 0.0,
          "severe_pnl": -0.0066304,
          "trades": 2,
          "win_rate": 0.0
        },
        "QTUM_USDT": {
          "gross_pnl": -0.0120144,
          "pf": 0.0,
          "severe_pnl": -0.024014399999999998,
          "trades": 3,
          "win_rate": 0.0
        },
        "Q_USDT": {
          "gross_pnl": 0.0020726,
          "pf": 0.0,
          "severe_pnl": -0.0019274000000000001,
          "trades": 1,
          "win_rate": 0.0
        },
        "RAM_USDT": {
          "gross_pnl": 0.035502900000000004,
          "pf": 0.38806510758839124,
          "severe_pnl": -0.0244971,
          "trades": 15,
          "win_rate": 0.2
        },
        "RARE_USDT": {
          "gross_pnl": 0.0049645,
          "pf": 999,
          "severe_pnl": 0.0009645000000000001,
          "trades": 1,
          "win_rate": 1.0
        },
        "RAVE_USDT": {
          "gross_pnl": 0.2244604,
          "pf": 0.601851740935953,
          "severe_pnl": -0.15953959999999998,
          "trades": 96,
          "win_rate": 0.2604166666666667
        },
        "RAY_USDT": {
          "gross_pnl": -0.0034391,
          "pf": 0.0,
          "severe_pnl": -0.0234391,
          "trades": 5,
          "win_rate": 0.0
        },
        "RENDER_USDT": {
          "gross_pnl": 0.007343300000000007,
          "pf": 0.038149232319590706,
          "severe_pnl": -0.25665669999999996,
          "trades": 66,
          "win_rate": 0.015151515151515152
        },
        "RESOLV_USDT": {
          "gross_pnl": 0.03952249999999999,
          "pf": 0.15008388934410236,
          "severe_pnl": -0.15247750000000002,
          "trades": 48,
          "win_rate": 0.20833333333333334
        },
        "REZ_USDT": {
          "gross_pnl": 0.005294,
          "pf": 0.0,
          "severe_pnl": -0.002706,
          "trades": 2,
          "win_rate": 0.0
        },
        "RE_USDT": {
          "gross_pnl": 0.03109420000000005,
          "pf": 0.08920463468994126,
          "severe_pnl": -0.4129058000000001,
          "trades": 111,
          "win_rate": 0.1891891891891892
        },
        "RIF_USDT": {
          "gross_pnl": 0.041993499999999996,
          "pf": 0.589089522244877,
          "severe_pnl": -0.014006499999999998,
          "trades": 14,
          "win_rate": 0.14285714285714285
        },
        "RLC_USDT": {
          "gross_pnl": -0.010854500000000003,
          "pf": 0.24413538873994645,
          "severe_pnl": -0.0428545,
          "trades": 8,
          "win_rate": 0.25
        },
        "ROAM_USDT": {
          "gross_pnl": -0.3676885999999999,
          "pf": 0.5410668005967868,
          "severe_pnl": -0.43568859999999987,
          "trades": 17,
          "win_rate": 0.4117647058823529
        },
        "ROBO_USDT": {
          "gross_pnl": -0.0014747000000000002,
          "pf": 0.0,
          "severe_pnl": -0.009474699999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "ROSE_USDT": {
          "gross_pnl": -0.0222775,
          "pf": 0.0,
          "severe_pnl": -0.058277499999999996,
          "trades": 9,
          "win_rate": 0.0
        },
        "RPL_USDT": {
          "gross_pnl": -0.0029107,
          "pf": 0.0,
          "severe_pnl": -0.010910699999999999,
          "trades": 2,
          "win_rate": 0.0
        },
        "RSR_USDT": {
          "gross_pnl": 0.0063269,
          "pf": 0.0,
          "severe_pnl": -0.0216731,
          "trades": 7,
          "win_rate": 0.0
        },
        "RUNE_USDT": {
          "gross_pnl": -0.011330099999999997,
          "pf": 0.0,
          "severe_pnl": -0.0473301,
          "trades": 9,
          "win_rate": 0.0
        },
        "RVN_USDT": {
          "gross_pnl": -0.0026087999999999997,
          "pf": 0.12430462670890959,
          "severe_pnl": -0.0506088,
          "trades": 12,
          "win_rate": 0.16666666666666666
        },
        "SAFE_USDT": {
          "gross_pnl": 0.006941499999999999,
          "pf": 0.29102019649889965,
          "severe_pnl": -0.0050585000000000005,
          "trades": 3,
          "win_rate": 0.3333333333333333
        },
        "SAGA_USDT": {
          "gross_pnl": -0.0110289,
          "pf": 0.0,
          "severe_pnl": -0.023028899999999998,
          "trades": 3,
          "win_rate": 0.0
        },
        "SAHARA_USDT": {
          "gross_pnl": 0.0033035,
          "pf": 0.054170440405955596,
          "severe_pnl": -0.0446965,
          "trades": 12,
          "win_rate": 0.16666666666666666
        },
        "SAND_USDT": {
          "gross_pnl": 4.3399999999999917e-05,
          "pf": 0.0,
          "severe_pnl": -0.0439566,
          "trades": 11,
          "win_rate": 0.0
        },
        "SANTOS_USDT": {
          "gross_pnl": 0.0086369,
          "pf": 1.2196282630435529,
          "severe_pnl": 0.0006368999999999993,
          "trades": 2,
          "win_rate": 0.5
        },
        "SEI_USDT": {
          "gross_pnl": 0.011857999999999999,
          "pf": 0.03336095722922798,
          "severe_pnl": -0.284142,
          "trades": 74,
          "win_rate": 0.06756756756756757
        },
        "SENT_USDT": {
          "gross_pnl": -0.025377699999999996,
          "pf": 0.4110960962442009,
          "severe_pnl": -0.12537770000000004,
          "trades": 25,
          "win_rate": 0.36
        },
        "SFP_USDT": {
          "gross_pnl": 0.0004662,
          "pf": 0.0,
          "severe_pnl": -0.0035338,
          "trades": 1,
          "win_rate": 0.0
        },
        "SHIB_USDT": {
          "gross_pnl": -0.0030496000000000026,
          "pf": 0.004653617389423597,
          "severe_pnl": -0.11504960000000002,
          "trades": 28,
          "win_rate": 0.03571428571428571
        },
        "SIGN_USDT": {
          "gross_pnl": 0.0008042,
          "pf": 0.0,
          "severe_pnl": -0.0031958,
          "trades": 1,
          "win_rate": 0.0
        },
        "SKL_USDT": {
          "gross_pnl": 0.04582390000000002,
          "pf": 0.6408032364715316,
          "severe_pnl": -0.1101761,
          "trades": 39,
          "win_rate": 0.358974358974359
        },
        "SKYAI_USDT": {
          "gross_pnl": -0.012810200000000032,
          "pf": 0.24797086926754147,
          "severe_pnl": -0.5928102000000001,
          "trades": 145,
          "win_rate": 0.2620689655172414
        },
        "SKY_USDT": {
          "gross_pnl": -8.520000000000055e-05,
          "pf": 0.002671423238063635,
          "severe_pnl": -0.0480852,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "SLX_USDT": {
          "gross_pnl": 0.21574100000000004,
          "pf": 0.4012429884373005,
          "severe_pnl": -0.3402589999999999,
          "trades": 139,
          "win_rate": 0.33093525179856115
        },
        "SMH_USDT": {
          "gross_pnl": -0.0021644,
          "pf": 0.0,
          "severe_pnl": -0.0061644000000000004,
          "trades": 1,
          "win_rate": 0.0
        },
        "SNT_USDT": {
          "gross_pnl": 0.0035262999999999996,
          "pf": 0.0,
          "severe_pnl": -0.0084737,
          "trades": 3,
          "win_rate": 0.0
        },
        "SNXX_USDT": {
          "gross_pnl": 0.06273569999999999,
          "pf": 0.7049569177640649,
          "severe_pnl": -0.04526429999999999,
          "trades": 27,
          "win_rate": 0.37037037037037035
        },
        "SNX_USDT": {
          "gross_pnl": -0.0068901,
          "pf": 0.0,
          "severe_pnl": -0.0348901,
          "trades": 7,
          "win_rate": 0.0
        },
        "SOL_USDT": {
          "gross_pnl": -0.019904300000000003,
          "pf": 0.0,
          "severe_pnl": -0.15590430000000005,
          "trades": 34,
          "win_rate": 0.0
        },
        "SOONNETWORK_USDT": {
          "gross_pnl": -0.0029942000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0149942,
          "trades": 3,
          "win_rate": 0.0
        },
        "SOXL_USDT": {
          "gross_pnl": 0.02001190000000002,
          "pf": 0.3584538962294441,
          "severe_pnl": -0.43998809999999994,
          "trades": 115,
          "win_rate": 0.2956521739130435
        },
        "SOXS_USDT": {
          "gross_pnl": -0.0421545,
          "pf": 0.2036255035863623,
          "severe_pnl": -0.15015449999999997,
          "trades": 27,
          "win_rate": 0.2962962962962963
        },
        "SOXX_USDT": {
          "gross_pnl": 0.0025073999999999995,
          "pf": 0.024588652512682406,
          "severe_pnl": -0.0454926,
          "trades": 12,
          "win_rate": 0.08333333333333333
        },
        "SPACE_USDT": {
          "gross_pnl": 0.0061958000000000004,
          "pf": 999,
          "severe_pnl": 0.0021958000000000004,
          "trades": 1,
          "win_rate": 1.0
        },
        "SPELL_USDT": {
          "gross_pnl": 0.0568256,
          "pf": 9.215965374146625,
          "severe_pnl": 0.03682560000000001,
          "trades": 5,
          "win_rate": 0.6
        },
        "SPORTFUN_USDT": {
          "gross_pnl": 0.0593283,
          "pf": 11.478370929876494,
          "severe_pnl": 0.05132830000000001,
          "trades": 2,
          "win_rate": 0.5
        },
        "SPY_USDT": {
          "gross_pnl": 0.0005659,
          "pf": 0.0,
          "severe_pnl": -0.0034341,
          "trades": 1,
          "win_rate": 0.0
        },
        "SQD_USDT": {
          "gross_pnl": -0.002191000000000001,
          "pf": 0.12743531125452667,
          "severe_pnl": -0.030191000000000003,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "SQQQ_USDT": {
          "gross_pnl": 0.0080774,
          "pf": 0.44494155000721597,
          "severe_pnl": -0.0119226,
          "trades": 5,
          "win_rate": 0.4
        },
        "STABLE_USDT": {
          "gross_pnl": 0.014750599999999999,
          "pf": 0.09395812902400545,
          "severe_pnl": -0.0212494,
          "trades": 9,
          "win_rate": 0.2222222222222222
        },
        "STAR_USDT": {
          "gross_pnl": 0.11019969999999998,
          "pf": 999,
          "severe_pnl": 0.09819969999999999,
          "trades": 3,
          "win_rate": 1.0
        },
        "STG_USDT": {
          "gross_pnl": 0.018294199999999997,
          "pf": 0.2656261542507454,
          "severe_pnl": -0.04970579999999999,
          "trades": 17,
          "win_rate": 0.17647058823529413
        },
        "STO_USDT": {
          "gross_pnl": -0.0019139,
          "pf": 0.0,
          "severe_pnl": -0.0059139,
          "trades": 1,
          "win_rate": 0.0
        },
        "STRK_USDT": {
          "gross_pnl": 0.007318099999999999,
          "pf": 0.11366404098004154,
          "severe_pnl": -0.036681899999999996,
          "trades": 11,
          "win_rate": 0.09090909090909091
        },
        "STX_USDT": {
          "gross_pnl": 0.0188446,
          "pf": 0.03451901505954193,
          "severe_pnl": -0.0611554,
          "trades": 20,
          "win_rate": 0.15
        },
        "SUI_USDT": {
          "gross_pnl": -0.009574000000000001,
          "pf": 0.0,
          "severe_pnl": -0.2535739999999999,
          "trades": 61,
          "win_rate": 0.0
        },
        "SUPER_USDT": {
          "gross_pnl": -0.0035336,
          "pf": 0.0,
          "severe_pnl": -0.0075336,
          "trades": 1,
          "win_rate": 0.0
        },
        "SUSHI_USDT": {
          "gross_pnl": -0.0011933,
          "pf": 0.0,
          "severe_pnl": -0.0051933,
          "trades": 1,
          "win_rate": 0.0
        },
        "SXT_USDT": {
          "gross_pnl": -0.07203699999999996,
          "pf": 0.3554332147341388,
          "severe_pnl": -0.476037,
          "trades": 101,
          "win_rate": 0.3465346534653465
        },
        "SYN_USDT": {
          "gross_pnl": 0.025163699999999997,
          "pf": 0.37915157491682316,
          "severe_pnl": -0.6988362999999999,
          "trades": 181,
          "win_rate": 0.281767955801105
        },
        "SYRUP_USDT": {
          "gross_pnl": 0.05140490000000001,
          "pf": 0.20389029143138196,
          "severe_pnl": -0.2045951,
          "trades": 64,
          "win_rate": 0.234375
        },
        "S_USDT": {
          "gross_pnl": 0.002031299999999999,
          "pf": 0.02939978247300532,
          "severe_pnl": -0.0259687,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "TAC_USDT": {
          "gross_pnl": 0.01658749999999999,
          "pf": 0.5050661384530065,
          "severe_pnl": -0.25541249999999993,
          "trades": 68,
          "win_rate": 0.3382352941176471
        },
        "TAG_USDT": {
          "gross_pnl": -0.22392320000000002,
          "pf": 0.2782949986008499,
          "severe_pnl": -0.33992320000000004,
          "trades": 29,
          "win_rate": 0.3103448275862069
        },
        "TAIKO_USDT": {
          "gross_pnl": 0.0088827,
          "pf": 0.5588085792214232,
          "severe_pnl": -0.0071173,
          "trades": 4,
          "win_rate": 0.5
        },
        "TAO_USDT": {
          "gross_pnl": 0.0165526,
          "pf": 0.0001175551879623425,
          "severe_pnl": -0.07144740000000001,
          "trades": 22,
          "win_rate": 0.045454545454545456
        },
        "THETA_USDT": {
          "gross_pnl": -0.014918299999999995,
          "pf": 0.012490212029873988,
          "severe_pnl": -0.17491830000000003,
          "trades": 40,
          "win_rate": 0.075
        },
        "THE_USDT": {
          "gross_pnl": 0.009464400000000003,
          "pf": 0.21628212469264707,
          "severe_pnl": -0.0465356,
          "trades": 14,
          "win_rate": 0.2857142857142857
        },
        "TIA_USDT": {
          "gross_pnl": 0.05972409999999998,
          "pf": 0.05137672883810069,
          "severe_pnl": -0.35227590000000003,
          "trades": 103,
          "win_rate": 0.11650485436893204
        },
        "TLM_USDT": {
          "gross_pnl": -0.04356959999999997,
          "pf": 0.22649278448919194,
          "severe_pnl": -0.2915695999999999,
          "trades": 62,
          "win_rate": 0.22580645161290322
        },
        "TOSHI_USDT": {
          "gross_pnl": -0.012448799999999998,
          "pf": 0.425550943181642,
          "severe_pnl": -0.0444488,
          "trades": 8,
          "win_rate": 0.375
        },
        "TOWNS_USDT": {
          "gross_pnl": -0.0449746,
          "pf": 0.13213736754755526,
          "severe_pnl": -0.08497460000000001,
          "trades": 10,
          "win_rate": 0.4
        },
        "TQQQ_USDT": {
          "gross_pnl": 0.008057400000000001,
          "pf": 0.16746806977329756,
          "severe_pnl": -0.0479426,
          "trades": 14,
          "win_rate": 0.21428571428571427
        },
        "TRADOOR_USDT": {
          "gross_pnl": 0.021979499999999985,
          "pf": 0.5586610216579146,
          "severe_pnl": -0.14202050000000005,
          "trades": 41,
          "win_rate": 0.3902439024390244
        },
        "TRB_USDT": {
          "gross_pnl": 0.0004978999999999995,
          "pf": 0.08572802674804167,
          "severe_pnl": -0.0595021,
          "trades": 15,
          "win_rate": 0.06666666666666667
        },
        "TRIA_USDT": {
          "gross_pnl": -0.0022922000000000047,
          "pf": 0.3088058758333195,
          "severe_pnl": -0.5222922,
          "trades": 130,
          "win_rate": 0.3384615384615385
        },
        "TRUST_USDT": {
          "gross_pnl": 0.0037283,
          "pf": 0.0,
          "severe_pnl": -0.00027170000000000015,
          "trades": 1,
          "win_rate": 0.0
        },
        "TRX_USDT": {
          "gross_pnl": 0.0013499000000000002,
          "pf": 0.0,
          "severe_pnl": -0.0226501,
          "trades": 6,
          "win_rate": 0.0
        },
        "TRY_USDT": {
          "gross_pnl": 0.00046929999999999997,
          "pf": 0.0,
          "severe_pnl": -0.0035307000000000003,
          "trades": 1,
          "win_rate": 0.0
        },
        "TURBO_USDT": {
          "gross_pnl": 0.0037806999999999997,
          "pf": 0.1361082508363633,
          "severe_pnl": -0.020219300000000003,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "TUT_USDT": {
          "gross_pnl": -0.0123552,
          "pf": 0.0,
          "severe_pnl": -0.0203552,
          "trades": 2,
          "win_rate": 0.0
        },
        "TWT_USDT": {
          "gross_pnl": 0.0011604000000000007,
          "pf": 0.004440026261809482,
          "severe_pnl": -0.026839599999999998,
          "trades": 7,
          "win_rate": 0.14285714285714285
        },
        "T_USDT": {
          "gross_pnl": -0.1300901,
          "pf": 0.30843920176959244,
          "severe_pnl": -0.47409010000000007,
          "trades": 86,
          "win_rate": 0.3372093023255814
        },
        "UAI_USDT": {
          "gross_pnl": 0.08280499999999998,
          "pf": 0.35664006669555126,
          "severe_pnl": -0.13319500000000004,
          "trades": 54,
          "win_rate": 0.2962962962962963
        },
        "UMA_USDT": {
          "gross_pnl": -0.0092415,
          "pf": 0.0,
          "severe_pnl": -0.0212415,
          "trades": 3,
          "win_rate": 0.0
        },
        "UNI_USDT": {
          "gross_pnl": -0.009308499999999997,
          "pf": 0.024310472593299458,
          "severe_pnl": -0.4333085000000001,
          "trades": 106,
          "win_rate": 0.11320754716981132
        },
        "USELESS_USDT": {
          "gross_pnl": -0.0748872,
          "pf": 0.0761621918781213,
          "severe_pnl": -0.33088719999999994,
          "trades": 64,
          "win_rate": 0.140625
        },
        "USO_USDT": {
          "gross_pnl": 0.0114353,
          "pf": 0.0,
          "severe_pnl": -0.012564700000000002,
          "trades": 6,
          "win_rate": 0.0
        },
        "USUAL_USDT": {
          "gross_pnl": -0.004284199999999997,
          "pf": 0.05533466149500431,
          "severe_pnl": -0.05628419999999999,
          "trades": 13,
          "win_rate": 0.15384615384615385
        },
        "UVXY_USDT": {
          "gross_pnl": -0.0021808999999999995,
          "pf": 0.09235286776126027,
          "severe_pnl": -0.0261809,
          "trades": 6,
          "win_rate": 0.16666666666666666
        },
        "VANA_USDT": {
          "gross_pnl": -0.0224928,
          "pf": 0.0,
          "severe_pnl": -0.03849280000000001,
          "trades": 4,
          "win_rate": 0.0
        },
        "VANRY_USDT": {
          "gross_pnl": 0.07856189999999998,
          "pf": 0.6464774463093248,
          "severe_pnl": -0.10143809999999998,
          "trades": 45,
          "win_rate": 0.4222222222222222
        },
        "VELO_USDT": {
          "gross_pnl": -0.0025877999999999995,
          "pf": 0.0,
          "severe_pnl": -0.0145878,
          "trades": 3,
          "win_rate": 0.0
        },
        "VELVET_USDT": {
          "gross_pnl": -0.026682500000000015,
          "pf": 0.5018109912012609,
          "severe_pnl": -0.5986824999999996,
          "trades": 143,
          "win_rate": 0.36363636363636365
        },
        "VET_USDT": {
          "gross_pnl": 0.0152233,
          "pf": 0.02446538351838298,
          "severe_pnl": -0.0567767,
          "trades": 18,
          "win_rate": 0.05555555555555555
        },
        "VINE_USDT": {
          "gross_pnl": 0.0146517,
          "pf": 0.06624554923646232,
          "severe_pnl": -0.0133483,
          "trades": 7,
          "win_rate": 0.2857142857142857
        },
        "VIRTUAL_USDT": {
          "gross_pnl": -0.02069270000000001,
          "pf": 0.07234663469843797,
          "severe_pnl": -0.5326927000000004,
          "trades": 128,
          "win_rate": 0.09375
        },
        "VVV_USDT": {
          "gross_pnl": -0.06428819999999999,
          "pf": 0.07135976803265717,
          "severe_pnl": -0.42428820000000006,
          "trades": 90,
          "win_rate": 0.13333333333333333
        },
        "WAL_USDT": {
          "gross_pnl": 0.0053174,
          "pf": 999,
          "severe_pnl": 0.0013173999999999998,
          "trades": 1,
          "win_rate": 1.0
        },
        "WET_USDT": {
          "gross_pnl": 0.010199199999999999,
          "pf": 999,
          "severe_pnl": 0.0061991999999999985,
          "trades": 1,
          "win_rate": 1.0
        },
        "WIF_USDT": {
          "gross_pnl": 0.018237800000000005,
          "pf": 0.020330934184165612,
          "severe_pnl": -0.3617622000000001,
          "trades": 95,
          "win_rate": 0.042105263157894736
        },
        "WLD_USDT": {
          "gross_pnl": -0.0013118999999999917,
          "pf": 0.07181919641138132,
          "severe_pnl": -0.30131189999999997,
          "trades": 75,
          "win_rate": 0.08
        },
        "WLFI_USDT": {
          "gross_pnl": 0.0029970000000000005,
          "pf": 0.0,
          "severe_pnl": -0.09700300000000002,
          "trades": 25,
          "win_rate": 0.0
        },
        "WOO_USDT": {
          "gross_pnl": -0.0071146,
          "pf": 0.0,
          "severe_pnl": -0.011114599999999999,
          "trades": 1,
          "win_rate": 0.0
        },
        "W_USDT": {
          "gross_pnl": 0.0132161,
          "pf": 0.23901723775137693,
          "severe_pnl": -0.022783900000000003,
          "trades": 9,
          "win_rate": 0.1111111111111111
        },
        "XAI_USDT": {
          "gross_pnl": -0.0009247000000000001,
          "pf": 0.0,
          "severe_pnl": -0.0209247,
          "trades": 5,
          "win_rate": 0.0
        },
        "XAN_USDT": {
          "gross_pnl": 0.0505175,
          "pf": 1.1690376460518976,
          "severe_pnl": 0.006517499999999998,
          "trades": 11,
          "win_rate": 0.45454545454545453
        },
        "XBI_USDT": {
          "gross_pnl": 0.0080151,
          "pf": 0.08255080033206379,
          "severe_pnl": -0.04398489999999999,
          "trades": 13,
          "win_rate": 0.3076923076923077
        },
        "XDC_USDT": {
          "gross_pnl": -0.0036855000000000004,
          "pf": 0.0,
          "severe_pnl": -0.035685499999999995,
          "trades": 8,
          "win_rate": 0.0
        },
        "XEC_USDT": {
          "gross_pnl": -0.04595019999999993,
          "pf": 0.43062406034401896,
          "severe_pnl": -0.48195020000000016,
          "trades": 109,
          "win_rate": 0.3761467889908257
        },
        "XLM_USDT": {
          "gross_pnl": 0.0020933,
          "pf": 0.029816962243250283,
          "severe_pnl": -0.2059067,
          "trades": 52,
          "win_rate": 0.07692307692307693
        },
        "XLU_USDT": {
          "gross_pnl": 0.0028139999999999997,
          "pf": 0.0,
          "severe_pnl": -0.009186,
          "trades": 3,
          "win_rate": 0.0
        },
        "XMR_USDT": {
          "gross_pnl": 0.0091918,
          "pf": 0.0009486098275978122,
          "severe_pnl": -0.3428082,
          "trades": 88,
          "win_rate": 0.011363636363636364
        },
        "XPIN_USDT": {
          "gross_pnl": -0.0364066,
          "pf": 0.24973785751329397,
          "severe_pnl": -0.1124066,
          "trades": 19,
          "win_rate": 0.3157894736842105
        },
        "XPL_USDT": {
          "gross_pnl": 0.0002297000000000013,
          "pf": 0.048489248857498474,
          "severe_pnl": -0.31177029999999994,
          "trades": 78,
          "win_rate": 0.10256410256410256
        },
        "XPT_USDT": {
          "gross_pnl": 0.0204206,
          "pf": 0.054696854509170376,
          "severe_pnl": -0.07957940000000002,
          "trades": 25,
          "win_rate": 0.08
        },
        "XRP_USDT": {
          "gross_pnl": 0.012168200000000006,
          "pf": 0.03624294663392385,
          "severe_pnl": -0.13983179999999998,
          "trades": 38,
          "win_rate": 0.05263157894736842
        },
        "XTZ_USDT": {
          "gross_pnl": -0.003806,
          "pf": 0.0,
          "severe_pnl": -0.023806,
          "trades": 5,
          "win_rate": 0.0
        },
        "YFI_USDT": {
          "gross_pnl": 0.0318971,
          "pf": 0.30671257345517616,
          "severe_pnl": -0.024102899999999997,
          "trades": 14,
          "win_rate": 0.2857142857142857
        },
        "ZAMA_USDT": {
          "gross_pnl": 0.0164933,
          "pf": 0.23977395866036072,
          "severe_pnl": -0.007506700000000001,
          "trades": 6,
          "win_rate": 0.3333333333333333
        },
        "ZBT_USDT": {
          "gross_pnl": 0.018245899999999995,
          "pf": 0.23414081142677154,
          "severe_pnl": -0.3457541,
          "trades": 91,
          "win_rate": 0.25274725274725274
        },
        "ZEC_USDT": {
          "gross_pnl": 0.03365739999999999,
          "pf": 0.08679336802772598,
          "severe_pnl": -0.20634260000000001,
          "trades": 60,
          "win_rate": 0.13333333333333333
        },
        "ZEN_USDT": {
          "gross_pnl": -0.016364100000000003,
          "pf": 0.10382948178573566,
          "severe_pnl": -0.11236409999999998,
          "trades": 24,
          "win_rate": 0.041666666666666664
        },
        "ZEST_USDT": {
          "gross_pnl": -0.005411000000000001,
          "pf": 0.20212164707036545,
          "severe_pnl": -0.03741099999999999,
          "trades": 8,
          "win_rate": 0.375
        },
        "ZETA_USDT": {
          "gross_pnl": 0.0008671,
          "pf": 0.0,
          "severe_pnl": -0.0031329,
          "trades": 1,
          "win_rate": 0.0
        },
        "ZIL_USDT": {
          "gross_pnl": -0.006905,
          "pf": 0.0,
          "severe_pnl": -0.014905000000000002,
          "trades": 2,
          "win_rate": 0.0
        },
        "ZINC_USDT": {
          "gross_pnl": -0.0025061,
          "pf": 0.0,
          "severe_pnl": -0.0265061,
          "trades": 6,
          "win_rate": 0.0
        },
        "ZKP_USDT": {
          "gross_pnl": 0.0071923,
          "pf": 0.0,
          "severe_pnl": -0.0208077,
          "trades": 7,
          "win_rate": 0.0
        },
        "ZKSYNC_USDT": {
          "gross_pnl": -0.004721299999999999,
          "pf": 0.02826232204348049,
          "severe_pnl": -0.056721299999999995,
          "trades": 13,
          "win_rate": 0.07692307692307693
        },
        "ZORA_USDT": {
          "gross_pnl": -0.0028426999999999992,
          "pf": 0.14898298064066043,
          "severe_pnl": -0.0468427,
          "trades": 11,
          "win_rate": 0.2727272727272727
        },
        "ZRO_USDT": {
          "gross_pnl": -0.02899419999999999,
          "pf": 0.05910481951793122,
          "severe_pnl": -0.1849942,
          "trades": 39,
          "win_rate": 0.07692307692307693
        }
      },
      "validation_depth_quartiles": [
        {
          "gross_pnl": 0.9114932000000032,
          "pf": 0.4710588554016116,
          "quartile": 1,
          "severe_pnl": -10.224506799999999,
          "trades": 2784,
          "upper": 8976.76524,
          "win_rate": 0.30495689655172414
        },
        {
          "gross_pnl": 1.0044583000000007,
          "pf": 0.2745900122725934,
          "quartile": 2,
          "severe_pnl": -11.767541699999969,
          "trades": 3193,
          "upper": 106972.33601999999,
          "win_rate": 0.20388349514563106
        },
        {
          "gross_pnl": 0.8067818000000007,
          "pf": 0.19452660196059426,
          "quartile": 3,
          "severe_pnl": -12.581218199999938,
          "trades": 3347,
          "upper": 1071304.435,
          "win_rate": 0.17060053779504034
        },
        {
          "gross_pnl": 0.6880175999999999,
          "pf": 0.09867890200274745,
          "quartile": 4,
          "severe_pnl": -11.311982399999946,
          "trades": 3000,
          "upper": null,
          "win_rate": 0.09566666666666666
        }
      ],
      "validation_pass": false,
      "validation_skips": {
        "invalid_path_json": 0,
        "missing_horizon_path": 117,
        "structure_not_selected": 74905,
        "symbol_cooldown": 3954
      },
      "validation_spread_quartiles": [
        {
          "gross_pnl": 0.5830321000000004,
          "pf": 0.16902828416343899,
          "quartile": 1,
          "severe_pnl": -11.31696789999999,
          "trades": 2975,
          "upper": 2.148689299527946,
          "win_rate": 0.13277310924369748
        },
        {
          "gross_pnl": 0.5154656999999994,
          "pf": 0.22422082722000955,
          "quartile": 2,
          "severe_pnl": -12.06853429999997,
          "trades": 3146,
          "upper": 4.268032437045758,
          "win_rate": 0.18054672600127145
        },
        {
          "gross_pnl": 1.4221167000000012,
          "pf": 0.2583805383649926,
          "quartile": 3,
          "severe_pnl": -11.565883299999935,
          "trades": 3247,
          "upper": 7.482229704451622,
          "win_rate": 0.18324607329842932
        },
        {
          "gross_pnl": 0.8901363999999994,
          "pf": 0.4230486740605059,
          "quartile": 4,
          "severe_pnl": -10.933863599999958,
          "trades": 2956,
          "upper": null,
          "win_rate": 0.2706359945872801
        }
      ]
    }
  ],
  "decision": "STOP_NO_VALIDATION_EDGE",
  "final_opened": false,
  "self_tests": [
    "parser_path_json",
    "no_overlap",
    "direction_sign",
    "cost",
    "chronological_split"
  ],
  "source": "/root/skynet/data/v18_micro_paths.sqlite3",
  "source_rows": 267076,
  "split_utc": "2026-07-09T08:32:30Z",
  "time_range": [
    "2026-06-17T11:09:00Z",
    "2026-07-18T17:42:34Z"
  ]
}
```
