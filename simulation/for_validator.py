import numpy as np
import pandas as pd
from simulation.config import FOR_SCORE


def flag_orders(orders_df: pd.DataFrame) -> pd.Series:
    for_ts = orders_df["for_timestamp"].values
    rider_arr = orders_df["rider_arrival_time"].values
    window = FOR_SCORE["rider_triggered_window_sec"] / 60.0

    flags = np.full(len(orders_df), "valid", dtype=object)
    is_missing = np.isnan(for_ts)
    flags[is_missing] = "missing"

    diff = for_ts - rider_arr
    is_rider_triggered = (~is_missing) & (np.abs(diff) <= window)
    flags[is_rider_triggered] = "suspicious_rider_triggered"

    is_very_late = (~is_missing) & (~is_rider_triggered) & (diff > 8.0)
    flags[is_very_late] = "suspicious_late"

    return pd.Series(flags, index=orders_df.index, name="for_flag")


def compute_merchant_scores(orders_df: pd.DataFrame, for_flags: pd.Series) -> pd.DataFrame:
    df = orders_df[["merchant_id", "for_timestamp", "rider_arrival_time"]].copy()
    df["for_flag"] = for_flags.values
    window = FOR_SCORE["window_size"]

    results = []
    for mid, group in df.groupby("merchant_id"):
        if len(group) < 10:
            results.append({"merchant_id": mid, "for_score": 50, "tier": "average"})
            continue

        tail = group.tail(window)
        n = len(tail)

        pct_rt = (tail["for_flag"] == "suspicious_rider_triggered").sum() / n
        pct_missing = (tail["for_flag"] == "missing").sum() / n
        pct_late = (tail["for_flag"] == "suspicious_late").sum() / n
        pct_valid = (tail["for_flag"] == "valid").sum() / n

        score = FOR_SCORE["base_score"]
        score -= pct_rt * FOR_SCORE["penalty_rider_triggered_max"]
        score -= pct_missing * FOR_SCORE["penalty_missing_max"]
        score -= pct_late * 15

        if pct_valid > 0.7:
            score += 10
        if pct_rt < 0.05 and pct_missing < 0.05:
            score += 10

        score = np.clip(score, 0, 100)

        if score >= 75:
            tier = "honest"
        elif score >= 45:
            tier = "average"
        else:
            tier = "unreliable"

        results.append({"merchant_id": mid, "for_score": round(score, 1), "tier": tier})

    return pd.DataFrame(results)


def run(orders_df: pd.DataFrame):
    flags = flag_orders(orders_df)
    scores = compute_merchant_scores(orders_df, flags)
    tier_counts = scores["tier"].value_counts()
    print(f"  FOR validation: {tier_counts.get('honest', 0)} honest, "
          f"{tier_counts.get('average', 0)} average, "
          f"{tier_counts.get('unreliable', 0)} unreliable")
    return flags, scores
