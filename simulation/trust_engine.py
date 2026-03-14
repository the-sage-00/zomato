import numpy as np
import pandas as pd
from simulation.config import (
    TRUST_ENGINE, ARCHETYPE_PRIOR_WEIGHTS, SIGNAL_NAMES,
)


def _get_alpha(order_count: int) -> float:
    if order_count < TRUST_ENGINE["alpha_transition_orders"]:
        return TRUST_ENGINE["alpha_new"]
    return TRUST_ENGINE["alpha_stable"]


def _normalize_weights(weights: dict) -> dict:
    total = sum(weights.values())
    if total == 0:
        n = len(weights)
        return {k: 1.0 / n for k in weights}
    return {k: v / total for k, v in weights.items()}


def _apply_cap(weights: dict, cap: float) -> dict:
    capped = {}
    excess = 0.0
    uncapped_keys = []
    for k, v in weights.items():
        if v > cap:
            capped[k] = cap
            excess += v - cap
        else:
            capped[k] = v
            uncapped_keys.append(k)
    if excess > 0 and uncapped_keys:
        share = excess / len(uncapped_keys)
        for k in uncapped_keys:
            capped[k] += share
    return _normalize_weights(capped)


def _signal_accuracy(predicted: float, actual: float) -> float:
    if actual <= 0:
        return 0.0
    error_ratio = abs(predicted - actual) / actual
    return max(0.0, 1.0 - error_ratio)


def build_trust_profiles(
    orders_df: pd.DataFrame,
    merchants_df: pd.DataFrame,
    corrected_dwell: pd.Series,
    for_scores: pd.DataFrame,
    gaming_results: pd.DataFrame,
) -> dict:
    orders_df = orders_df.copy()
    orders_df["corrected_dwell"] = corrected_dwell.values

    for_score_map = for_scores.set_index("merchant_id")["for_score"].to_dict()
    gaming_map = gaming_results.set_index("merchant_id")["gaming_detected"].to_dict()
    cap = TRUST_ENGINE["max_single_weight"]
    update_freq = TRUST_ENGINE["update_every_n_orders"]

    profiles = {}
    for mid, group in orders_df.groupby("merchant_id"):
        archetype = group["archetype"].iloc[0]
        prior = ARCHETYPE_PRIOR_WEIGHTS.get(archetype, ARCHETYPE_PRIOR_WEIGHTS["dine_in"]).copy()
        current_weights = prior.copy()
        history = [{"at_order": 0, "weights": prior.copy()}]

        sorted_group = group.sort_values("order_id")
        n_orders = len(sorted_group)
        rows = sorted_group.to_dict("records")
        true_kpts_so_far = []
        dwell_kpt_buffer = []

        for batch_start in range(0, n_orders, update_freq):
            batch_end = min(batch_start + update_freq, n_orders)
            batch = rows[batch_start:batch_end]
            if len(batch) < 10:
                for row in batch:
                    true_kpts_so_far.append(row["true_kpt"])
                    cd = row.get("corrected_dwell", np.nan)
                    if not np.isnan(cd):
                        dwell_kpt_buffer.append(row["rider_arrival_time"] + cd)
                continue

            order_count = batch_end
            alpha = _get_alpha(order_count)
            if order_count <= 30:
                for row in batch:
                    true_kpts_so_far.append(row["true_kpt"])
                    cd = row.get("corrected_dwell", np.nan)
                    if not np.isnan(cd):
                        dwell_kpt_buffer.append(row["rider_arrival_time"] + cd)
                continue

            if order_count <= TRUST_ENGINE["blended_end"]:
                blend_factor = 0.4
            else:
                blend_factor = 1.0

            hist_avg = np.mean(true_kpts_so_far[-30:]) if len(true_kpts_so_far) >= 5 else 15.0

            signal_accuracies = {s: [] for s in SIGNAL_NAMES}
            for row in batch:
                actual = row["true_kpt"]
                true_kpts_so_far.append(actual)
                if actual <= 0:
                    continue

                for_ts = row.get("for_timestamp", np.nan)
                if not np.isnan(for_ts):
                    signal_accuracies["for"].append(_signal_accuracy(for_ts, actual))

                cd = row.get("corrected_dwell", np.nan)
                ra = row.get("rider_arrival_time", 0)
                if not np.isnan(cd):
                    dwell_kpt = ra + cd
                    dwell_kpt_buffer.append(dwell_kpt)
                if len(dwell_kpt_buffer) >= 3:
                    dwell_est = np.mean(dwell_kpt_buffer[-10:])
                    signal_accuracies["dwell"].append(_signal_accuracy(dwell_est, actual))

                rush_proxy = row.get("ack_latency", 15) / 30.0
                behavior_est = hist_avg * (1 + np.clip(rush_proxy - 0.5, -0.2, 0.3))
                signal_accuracies["behavior"].append(_signal_accuracy(behavior_est, actual))

                akai = row.get("akai_score", np.nan)
                if not np.isnan(akai):
                    akai_est = hist_avg * (1 + np.clip(akai / 10 - 0.3, -0.15, 0.5))
                    signal_accuracies["akai"].append(_signal_accuracy(akai_est, actual))

                gb = row.get("google_busyness", 0.0)
                ext_est = hist_avg * (1 + gb * 0.25)
                signal_accuracies["external"].append(_signal_accuracy(ext_est, actual))

            mean_acc = {}
            for s in SIGNAL_NAMES:
                vals = signal_accuracies[s]
                if len(vals) >= 3:
                    mean_acc[s] = np.mean(vals)

            if len(mean_acc) < TRUST_ENGINE["min_signals_for_update"]:
                continue

            new_weights = {}
            for s in SIGNAL_NAMES:
                if s in mean_acc:
                    raw = alpha * mean_acc[s] + (1 - alpha) * current_weights[s]
                    if order_count <= TRUST_ENGINE["blended_end"]:
                        raw = (1 - blend_factor) * prior[s] + blend_factor * raw
                    new_weights[s] = raw
                else:
                    new_weights[s] = current_weights[s]

            new_weights = _apply_cap(new_weights, cap)
            current_weights = new_weights
            history.append({"at_order": order_count, "weights": current_weights.copy()})

        if gaming_map.get(mid, False):
            for s in SIGNAL_NAMES:
                if current_weights[s] > 0.10:
                    current_weights[s] = max(current_weights[s] * 0.5, 0.05)
            current_weights = _normalize_weights(current_weights)

        profiles[mid] = {
            "merchant_id": mid,
            "archetype": archetype,
            "order_count": n_orders,
            "for_score": for_score_map.get(mid, 50),
            "gaming_detected": gaming_map.get(mid, False),
            "current_weights": current_weights.copy(),
            "weight_history": history,
        }

    return profiles


def run(orders_df, merchants_df, corrected_dwell, for_scores, gaming_results):
    profiles = build_trust_profiles(
        orders_df, merchants_df, corrected_dwell, for_scores, gaming_results
    )
    total_updates = sum(len(p["weight_history"]) - 1 for p in profiles.values())
    print(f"  Trust Engine: {len(profiles)} profiles built, {total_updates:,} weight updates")
    return profiles
