import numpy as np
import pandas as pd
from simulation.config import AKAI, EXTERNAL, SIGNAL_NAMES


def _for_estimate(row):
    return row["for_timestamp"]


def _dwell_estimate(row, merchant_dwell_history):
    mid = row["merchant_id"]
    vals = merchant_dwell_history.get(mid, [])
    if len(vals) == 0:
        return np.nan
    return np.mean(vals[-10:])


def _behavior_estimate(row):
    return 5.0 + row["ack_latency"] * 0.18


def _akai_estimate(row, base_kpt):
    akai = row["akai_score"]
    if np.isnan(akai):
        return np.nan
    return base_kpt * (1.0 + akai * AKAI["kpt_impact_per_level"])


def _external_estimate(row, base_kpt):
    gb = row["google_busyness"]
    return base_kpt * (1.0 + gb * EXTERNAL["kpt_impact_at_full"])


def compute_kp_scores(
    orders_df: pd.DataFrame,
    trust_profiles: dict,
    merchants_df: pd.DataFrame,
) -> pd.DataFrame:
    base_kpt_map = merchants_df.set_index("merchant_id")["base_kpt_mu"].to_dict()

    kp_scores = np.full(len(orders_df), np.nan)
    contributions_list = []

    dwell_history = {}
    for _, row in orders_df.iterrows():
        mid = int(row["merchant_id"])
        cd = row.get("corrected_dwell", np.nan)
        if not np.isnan(cd):
            dwell_history.setdefault(mid, []).append(cd)

    for idx, row in orders_df.iterrows():
        mid = int(row["merchant_id"])
        profile = trust_profiles.get(mid)
        if profile is None:
            contributions_list.append({})
            continue

        weights = profile["current_weights"]
        base = np.exp(base_kpt_map.get(mid, 2.5))

        estimates = {}
        f_val = _for_estimate(row)
        if not np.isnan(f_val):
            estimates["for"] = f_val

        d_val = _dwell_estimate(row, dwell_history)
        if not np.isnan(d_val):
            estimates["dwell"] = d_val

        estimates["behavior"] = _behavior_estimate(row)

        a_val = _akai_estimate(row, base)
        if not np.isnan(a_val):
            estimates["akai"] = a_val

        estimates["external"] = _external_estimate(row, base)

        active_w = {s: weights.get(s, 0) for s in estimates}
        total_w = sum(active_w.values())
        if total_w <= 0:
            contributions_list.append({})
            continue

        score = 0.0
        contribs = {}
        for s, est in estimates.items():
            eff_w = active_w[s] / total_w
            c = eff_w * est
            score += c
            contribs[s] = {"weight": round(eff_w, 3), "estimate": round(est, 1), "contribution": round(c, 2)}

        kp_scores[idx] = score
        contributions_list.append(contribs)

    orders_df = orders_df.copy()
    orders_df["kp_score"] = kp_scores
    return orders_df, contributions_list


def compute_kp_scores_fast(
    orders_df: pd.DataFrame,
    trust_profiles: dict,
    merchants_df: pd.DataFrame,
) -> pd.Series:
    n = len(orders_df)
    mid_arr = orders_df["merchant_id"].values
    for_arr = orders_df["for_timestamp"].values
    cd_arr = orders_df["corrected_dwell"].values if "corrected_dwell" in orders_df.columns else np.full(n, np.nan)
    ack_arr = orders_df["ack_latency"].values
    akai_arr = orders_df["akai_score"].values if "akai_score" in orders_df.columns else np.full(n, np.nan)
    gb_arr = orders_df["google_busyness"].values

    base_map = merchants_df.set_index("merchant_id")["base_kpt_mu"].to_dict()

    weight_arrays = {s: np.zeros(n) for s in SIGNAL_NAMES}
    for i in range(n):
        mid = int(mid_arr[i])
        p = trust_profiles.get(mid)
        if p:
            for s in SIGNAL_NAMES:
                weight_arrays[s][i] = p["current_weights"].get(s, 0)

    base_kpts = np.array([np.exp(base_map.get(int(m), 2.5)) for m in mid_arr])

    est_for = for_arr.copy()
    est_behavior = 5.0 + ack_arr * 0.18
    est_akai = base_kpts * (1.0 + akai_arr * AKAI["kpt_impact_per_level"])
    est_external = base_kpts * (1.0 + gb_arr * EXTERNAL["kpt_impact_at_full"])

    dwell_rolling = np.full(n, np.nan)
    from collections import defaultdict
    buf = defaultdict(list)
    for i in range(n):
        mid = int(mid_arr[i])
        vals = buf[mid]
        if len(vals) > 0:
            dwell_rolling[i] = np.mean(vals[-10:])
        v = cd_arr[i]
        if not np.isnan(v):
            vals.append(v)

    signals = {
        "for": est_for,
        "dwell": dwell_rolling,
        "behavior": est_behavior,
        "akai": est_akai,
        "external": est_external,
    }

    numerator = np.zeros(n)
    denominator = np.zeros(n)
    for s in SIGNAL_NAMES:
        est = signals[s]
        w = weight_arrays[s]
        valid = ~np.isnan(est)
        numerator += np.where(valid, w * est, 0)
        denominator += np.where(valid, w, 0)

    denominator = np.where(denominator > 0, denominator, 1.0)
    kp_scores = numerator / denominator

    return pd.Series(kp_scores, index=orders_df.index, name="kp_score")


def run(orders_df, trust_profiles, merchants_df):
    scores = compute_kp_scores_fast(orders_df, trust_profiles, merchants_df)
    valid = scores.notna().sum()
    print(f"  KitchenPulse scores computed: {valid:,}")
    return scores
