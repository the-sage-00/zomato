import numpy as np
import pandas as pd
from simulation.config import GAMING


def detect_gaming(orders_df: pd.DataFrame, for_scores: pd.DataFrame) -> pd.DataFrame:
    window = GAMING["for_rider_window_sec"] / 60.0
    min_orders = GAMING["min_orders_to_detect"]

    results = []
    for mid, group in orders_df.groupby("merchant_id"):
        if len(group) < min_orders:
            results.append({
                "merchant_id": mid,
                "gaming_detected": False,
                "gaming_patterns": [],
            })
            continue

        tail = group.tail(50)
        patterns = []

        diff = (tail["for_timestamp"] - tail["rider_arrival_time"]).dropna().abs()
        if len(diff) > 5:
            pct_near_rider = (diff < window).mean()
            if pct_near_rider > 0.6:
                patterns.append("for_rider_correlation")

        median_dwell = group["raw_dwell_time"].median()
        recent_dwell = tail["raw_dwell_time"].median()
        if median_dwell > 0 and recent_dwell > GAMING["dwell_multiplier_threshold"] * median_dwell:
            patterns.append("dwell_always_high")

        akai_vals = tail["akai_score"].dropna()
        ack_vals = tail["ack_latency"]
        if len(akai_vals) > 5:
            high_akai = akai_vals > GAMING["ack_anomaly_min_akai"]
            low_ack = ack_vals.loc[akai_vals.index] < GAMING["ack_anomaly_max_sec"]
            if (high_akai & low_ack).sum() > 5:
                patterns.append("ack_anomaly")

        results.append({
            "merchant_id": mid,
            "gaming_detected": len(patterns) > 0,
            "gaming_patterns": patterns,
        })

    return pd.DataFrame(results)


def run(orders_df: pd.DataFrame, for_scores: pd.DataFrame):
    gaming = detect_gaming(orders_df, for_scores)
    n_gaming = gaming["gaming_detected"].sum()
    print(f"  Gaming detection: {n_gaming} merchants flagged")
    return gaming
