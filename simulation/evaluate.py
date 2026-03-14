import numpy as np
import pandas as pd
from collections import defaultdict


def _baseline_predictions(orders_df):
    n = len(orders_df)
    preds = np.full(n, np.nan)
    mid_arr = orders_df["merchant_id"].values
    for_arr = orders_df["for_timestamp"].values
    merchant_avg = defaultdict(list)
    for i in range(n):
        mid = int(mid_arr[i])
        f = for_arr[i]
        hist = merchant_avg[mid]
        if not np.isnan(f):
            preds[i] = f
            hist.append(f)
        elif len(hist) > 0:
            preds[i] = np.mean(hist[-20:])
        else:
            preds[i] = 15.0
    return preds


def _build_archetype_kpt_priors(orders_df, for_scores):
    honest_mids = set(for_scores[for_scores["tier"] == "honest"]["merchant_id"].values)
    priors = {}
    for arch, grp in orders_df.groupby("archetype"):
        honest_orders = grp[grp["merchant_id"].isin(honest_mids)]
        valid_for = honest_orders["for_timestamp"].dropna()
        if len(valid_for) >= 50:
            priors[arch] = float(valid_for.median())
        else:
            priors[arch] = float(grp["for_timestamp"].dropna().median()) if grp["for_timestamp"].notna().sum() > 20 else 15.0
    return priors


def _dwell_corrected_predictions(orders_df, for_scores, archetype_priors):
    n = len(orders_df)
    preds = _baseline_predictions(orders_df).copy()
    mid_arr = orders_df["merchant_id"].values
    for_arr = orders_df["for_timestamp"].values
    flag_arr = orders_df["for_flag"].values if "for_flag" in orders_df.columns else np.full(n, "valid", dtype=object)
    arch_arr = orders_df["archetype"].values

    score_map = for_scores.set_index("merchant_id")["for_score"].to_dict()
    merchant_valid_for = defaultdict(list)

    for i in range(n):
        mid = int(mid_arr[i])
        f = for_arr[i]
        flag = flag_arr[i]
        arch = arch_arr[i]
        valid_hist = merchant_valid_for[mid]
        ms = score_map.get(mid, 50)

        if flag == "suspicious_rider_triggered":
            if len(valid_hist) >= 5:
                preds[i] = np.mean(valid_hist[-15:])
            else:
                preds[i] = archetype_priors.get(arch, 15.0)
        elif flag == "missing" or np.isnan(f):
            if len(valid_hist) >= 5:
                preds[i] = np.mean(valid_hist[-15:])
            elif ms < 50:
                preds[i] = archetype_priors.get(arch, 15.0)

        if flag == "valid" and not np.isnan(f):
            valid_hist.append(f)

    return preds


def _kplite_predictions(orders_df, for_scores, archetype_priors):
    dc_preds = _dwell_corrected_predictions(orders_df, for_scores, archetype_priors).copy()
    n = len(orders_df)
    mid_arr = orders_df["merchant_id"].values
    flag_arr = orders_df["for_flag"].values if "for_flag" in orders_df.columns else np.full(n, "valid", dtype=object)
    ack_arr = orders_df["ack_latency"].values
    gb_arr = orders_df["google_busyness"].values

    merchant_ack_hist = defaultdict(list)

    for i in range(n):
        mid = int(mid_arr[i])
        flag = flag_arr[i]
        ack_hist = merchant_ack_hist[mid]

        if flag in ("suspicious_rider_triggered", "missing", "suspicious_late"):
            avg_ack = np.mean(ack_hist[-30:]) if len(ack_hist) >= 5 else 30.0
            rush = np.clip(ack_arr[i] / max(avg_ack, 10), 0.92, 1.12)
            ext = 1 + gb_arr[i] * 0.04
            dc_preds[i] = dc_preds[i] * rush * ext

        ack_hist.append(ack_arr[i])

    return dc_preds


def _kpfull_predictions(orders_df, for_scores, archetype_priors):
    dc_preds = _dwell_corrected_predictions(orders_df, for_scores, archetype_priors).copy()
    n = len(orders_df)
    mid_arr = orders_df["merchant_id"].values
    for_arr = orders_df["for_timestamp"].values
    flag_arr = orders_df["for_flag"].values if "for_flag" in orders_df.columns else np.full(n, "valid", dtype=object)
    ack_arr = orders_df["ack_latency"].values
    akai_arr = orders_df["akai_score"].values if "akai_score" in orders_df.columns else np.full(n, np.nan)
    gb_arr = orders_df["google_busyness"].values

    merchant_ack_hist = defaultdict(list)

    for i in range(n):
        mid = int(mid_arr[i])
        flag = flag_arr[i]
        ack_hist = merchant_ack_hist[mid]

        avg_ack = np.mean(ack_hist[-30:]) if len(ack_hist) >= 5 else 30.0
        rush = np.clip(ack_arr[i] / max(avg_ack, 10), 0.93, 1.10)
        ext = 1 + gb_arr[i] * 0.03
        akai_adj = 1.0
        if not np.isnan(akai_arr[i]):
            akai_adj = 1 + np.clip((akai_arr[i] - 4) * 0.02, -0.05, 0.08)

        ctx = rush * ext * akai_adj

        if flag in ("suspicious_rider_triggered", "missing", "suspicious_late"):
            dc_preds[i] = dc_preds[i] * ctx
        elif flag == "valid":
            dc_preds[i] = dc_preds[i] * (0.95 + 0.05 * ctx)

        ack_hist.append(ack_arr[i])

    return dc_preds


def compute_metrics(true_kpt, preds):
    mask = ~(np.isnan(true_kpt) | np.isnan(preds))
    t = true_kpt[mask]
    p = preds[mask]
    errors = np.abs(t - p)
    return {
        "mae": round(float(np.mean(errors)), 2),
        "p50_error": round(float(np.median(errors)), 2),
        "p90_error": round(float(np.percentile(errors, 90)), 2),
        "p95_error": round(float(np.percentile(errors, 95)), 2),
        "p99_error": round(float(np.percentile(errors, 99)), 2),
        "within_3min": round(float((errors <= 3).mean()), 3),
        "within_5min": round(float((errors <= 5).mean()), 3),
        "n_orders": int(mask.sum()),
    }


def compute_eta_volatility(orders_df, predictions, rng):
    n = len(orders_df)
    true_kpt = orders_df["true_kpt"].values
    base_error = np.abs(true_kpt - predictions)
    avg_err = max(float(np.mean(base_error)), 1)
    volatility = np.zeros(n)
    current_eta = predictions.copy()
    for dt in [3, 6, 9]:
        noise = rng.normal(0, 1.5, n)
        new_eta = current_eta + noise
        change = np.abs(new_eta - current_eta)
        volatility += (change > 3).astype(float)
        current_eta = new_eta
    scale = base_error / avg_err
    volatility = volatility * np.clip(scale, 0.3, 3.0)
    return volatility


def run_all_models(orders_df, trust_profiles, merchants_df, seed=42, for_scores=None):
    rng = np.random.default_rng(seed)
    true_kpt = orders_df["true_kpt"].values

    archetype_priors = _build_archetype_kpt_priors(orders_df, for_scores) if for_scores is not None else {}
    print(f"  Archetype KPT priors: { {k: round(v,1) for k,v in archetype_priors.items()} }")

    print("\n  Running 4 prediction models...")
    models = {}

    bl = _baseline_predictions(orders_df)
    models["Baseline"] = {"predictions": bl, "metrics": compute_metrics(true_kpt, bl)}
    bl_mae = models["Baseline"]["metrics"]["mae"]
    print(f"    Baseline:         MAE={bl_mae:.1f}, P90={models['Baseline']['metrics']['p90_error']:.1f}")

    dc = _dwell_corrected_predictions(orders_df, for_scores, archetype_priors)
    models["Dwell-Corrected"] = {"predictions": dc, "metrics": compute_metrics(true_kpt, dc)}
    pct = (1 - models["Dwell-Corrected"]["metrics"]["mae"] / bl_mae) * 100
    print(f"    Dwell-Corrected:  MAE={models['Dwell-Corrected']['metrics']['mae']:.1f} (↓{pct:.0f}%), "
          f"P90={models['Dwell-Corrected']['metrics']['p90_error']:.1f}")

    kpl = _kplite_predictions(orders_df, for_scores, archetype_priors)
    models["KP-Lite"] = {"predictions": kpl, "metrics": compute_metrics(true_kpt, kpl)}
    pct = (1 - models["KP-Lite"]["metrics"]["mae"] / bl_mae) * 100
    print(f"    KP-Lite:          MAE={models['KP-Lite']['metrics']['mae']:.1f} (↓{pct:.0f}%), "
          f"P90={models['KP-Lite']['metrics']['p90_error']:.1f}")

    kpf = _kpfull_predictions(orders_df, for_scores, archetype_priors)
    models["KP-Full"] = {"predictions": kpf, "metrics": compute_metrics(true_kpt, kpf)}
    pct = (1 - models["KP-Full"]["metrics"]["mae"] / bl_mae) * 100
    print(f"    KP-Full:          MAE={models['KP-Full']['metrics']['mae']:.1f} (↓{pct:.0f}%), "
          f"P90={models['KP-Full']['metrics']['p90_error']:.1f}")

    for name, data in models.items():
        vol = compute_eta_volatility(orders_df, data["predictions"], rng)
        data["metrics"]["avg_eta_volatility"] = round(float(np.mean(vol)), 2)

    return models
