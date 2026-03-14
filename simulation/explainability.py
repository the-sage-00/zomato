import numpy as np
import pandas as pd
from simulation.config import SIGNAL_NAMES, AKAI, EXTERNAL


def explain_order(order: dict, trust_profile: dict, base_kpt: float, dwell_avg: float = None):
    weights = trust_profile["current_weights"]
    estimates = {}
    for_ts = order.get("for_timestamp", np.nan)
    if not np.isnan(for_ts):
        estimates["for"] = for_ts
    if dwell_avg is not None and not np.isnan(dwell_avg):
        estimates["dwell"] = dwell_avg
    estimates["behavior"] = 5.0 + order.get("ack_latency", 15) * 0.18
    akai = order.get("akai_score", np.nan)
    if not np.isnan(akai):
        estimates["akai"] = base_kpt * (1 + akai * AKAI["kpt_impact_per_level"])
    estimates["external"] = base_kpt * (1 + order.get("google_busyness", 0) * EXTERNAL["kpt_impact_at_full"])

    active_w = {s: weights.get(s, 0) for s in estimates}
    total_w = sum(active_w.values())
    if total_w <= 0:
        return None

    breakdown = []
    total_score = 0
    for s, est in estimates.items():
        eff_w = active_w[s] / total_w
        contrib = eff_w * est
        total_score += contrib
        breakdown.append({
            "signal": s,
            "weight": round(eff_w, 3),
            "estimate_min": round(est, 1),
            "contribution_min": round(contrib, 2),
        })

    return {
        "prediction": round(total_score, 1),
        "true_kpt": round(order.get("true_kpt", 0), 1),
        "error": round(abs(total_score - order.get("true_kpt", 0)), 1),
        "for_score": trust_profile.get("for_score", 0),
        "phase": "personalized" if trust_profile["order_count"] > 100 else "blended" if trust_profile["order_count"] > 30 else "cold_start",
        "breakdown": breakdown,
    }


def explain_batch(orders_df: pd.DataFrame, trust_profiles: dict, merchants_df: pd.DataFrame, n_samples: int = 20):
    base_map = merchants_df.set_index("merchant_id")["base_kpt_mu"].to_dict()
    sample = orders_df.sample(min(n_samples, len(orders_df)), random_state=42)
    explanations = []
    for _, row in sample.iterrows():
        mid = int(row["merchant_id"])
        profile = trust_profiles.get(mid)
        if profile is None:
            continue
        base = np.exp(base_map.get(mid, 2.5))
        expl = explain_order(row.to_dict(), profile, base)
        if expl:
            explanations.append(expl)
    return explanations
