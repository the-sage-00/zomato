import numpy as np
import pandas as pd
from simulation.config import (
    SEED, NUM_MERCHANTS, ORDERS_PER_MERCHANT, ARCHETYPES, TIME_SLOTS,
    COMPLEXITY, DWELL_NOISE, T_HANDOFF_MU, T_HANDOFF_SIGMA,
    GPS_JITTER_SIGMA, FOR_NOISE, DISPATCH, KPT_BOUNDS, AKAI, EXTERNAL,
    BEHAVIOR, SIGNAL_NAMES,
)
from simulation.queue_model import queue_factor_vectorized


def create_merchants(rng: np.random.Generator) -> pd.DataFrame:
    records = []
    mid = 0
    for arch_name, arch_cfg in ARCHETYPES.items():
        n = arch_cfg["count"]
        fp = arch_cfg["for_profile"]
        behaviors = rng.choice(
            list(fp.keys()),
            size=n,
            p=list(fp.values()),
        )
        venues = rng.choice(
            arch_cfg["venue_types"],
            size=n,
            p=arch_cfg["venue_weights"],
        )
        akai_flags = rng.random(n) < arch_cfg["akai_opt_in_rate"]
        lats = 19.0 + rng.random(n) * 0.15
        lons = 72.8 + rng.random(n) * 0.15
        for i in range(n):
            records.append({
                "merchant_id": mid,
                "archetype": arch_name,
                "venue_type": venues[i],
                "for_behavior": behaviors[i],
                "kitchen_capacity": arch_cfg["kitchen_capacity"],
                "base_kpt_mu": arch_cfg["base_kpt_mu"],
                "base_kpt_sigma": arch_cfg["base_kpt_sigma"],
                "walkin_base_lambda": arch_cfg["walkin_base_lambda"],
                "akai_opted_in": bool(akai_flags[i]),
                "lat": lats[i],
                "lon": lons[i],
                "neighborhood_id": int(lats[i] * 100) * 1000 + int(lons[i] * 100),
            })
            mid += 1
    return pd.DataFrame(records)


def _generate_orders_for_merchant(merchant: dict, rng: np.random.Generator) -> pd.DataFrame:
    n_orders = rng.integers(ORDERS_PER_MERCHANT[0], ORDERS_PER_MERCHANT[1] + 1)

    ts_names = list(TIME_SLOTS.keys())
    ts_probs = [TIME_SLOTS[t]["prob"] for t in ts_names]
    time_slots = rng.choice(ts_names, size=n_orders, p=ts_probs)

    cx_names = list(COMPLEXITY.keys())
    cx_probs = [COMPLEXITY[c]["probability"] for c in cx_names]
    complexities = rng.choice(cx_names, size=n_orders, p=cx_probs)

    kpt_mults = np.array([TIME_SLOTS[t]["kpt_mult"] for t in time_slots])
    cx_mults = np.array([COMPLEXITY[c]["multiplier"] for c in complexities])
    walkin_mults = np.array([TIME_SLOTS[t]["walkin_mult"] for t in time_slots])

    walkin_load = rng.poisson(
        lam=np.maximum(merchant["walkin_base_lambda"] * walkin_mults, 0.1)
    )
    concurrent_zomato = rng.poisson(lam=np.clip(kpt_mults * 3, 1, 15))
    active_orders = walkin_load + concurrent_zomato

    qf = queue_factor_vectorized(
        active_orders.astype(np.float64),
        np.full(n_orders, merchant["kitchen_capacity"], dtype=np.float64),
    )

    base_kpt_raw = np.exp(
        rng.normal(merchant["base_kpt_mu"], merchant["base_kpt_sigma"], size=n_orders)
    )
    true_kpt = base_kpt_raw * kpt_mults * cx_mults * qf
    true_kpt = np.clip(true_kpt, KPT_BOUNDS["min"], KPT_BOUNDS["max"])

    hist_for_avg = np.mean(true_kpt[:20]) if n_orders >= 20 else np.mean(true_kpt)
    running_avg = np.full(n_orders, hist_for_avg)
    for i in range(20, n_orders):
        running_avg[i] = np.mean(true_kpt[max(0, i - 20):i])

    dispatch_time = np.maximum(running_avg - DISPATCH["early_dispatch_minutes"], 0)
    rider_travel = rng.uniform(DISPATCH["rider_travel_min"], DISPATCH["rider_travel_max"], size=n_orders)
    rider_arrival = dispatch_time + rider_travel

    behavior = merchant["for_behavior"]
    for_timestamp = np.full(n_orders, np.nan)
    if behavior == "honest":
        for_timestamp = true_kpt + rng.normal(0, FOR_NOISE["honest_sigma"], n_orders)
    elif behavior == "rider_triggered":
        for_timestamp = rider_arrival + rng.uniform(
            FOR_NOISE["rider_triggered_low"],
            FOR_NOISE["rider_triggered_high"],
            n_orders,
        )
    elif behavior == "lazy":
        delay = rng.exponential(FOR_NOISE["lazy_exp_mean"], n_orders)
        for_timestamp = true_kpt + delay
    for_timestamp = np.maximum(for_timestamp, 0)
    if behavior == "missing":
        for_timestamp[:] = np.nan

    venue = merchant["venue_type"]
    dn = DWELL_NOISE[venue]
    t_approach = np.abs(rng.normal(dn["t_approach_mu"], dn["t_approach_sigma"], n_orders))
    t_park = np.abs(rng.normal(dn["t_park_mu"], dn["t_park_sigma"], n_orders))
    t_handoff = np.abs(rng.normal(T_HANDOFF_MU, T_HANDOFF_SIGMA, n_orders))
    gps_jitter = rng.normal(0, GPS_JITTER_SIGMA, n_orders)

    kitchen_wait = np.maximum(true_kpt - rider_arrival, 0)
    raw_dwell = kitchen_wait + t_approach + t_park + t_handoff + gps_jitter
    raw_dwell = np.maximum(raw_dwell, 0.1)

    is_batched = rng.random(n_orders) < 0.12

    rush_factor = 1 + walkin_load / BEHAVIOR["rush_scaling"]
    ack_latency = BEHAVIOR["base_latency_sec"] * rush_factor + rng.normal(0, BEHAVIOR["noise_sigma_sec"], n_orders)
    ack_latency = np.clip(ack_latency, BEHAVIOR["min_sec"], BEHAVIOR["max_sec"])

    akai_score = np.full(n_orders, np.nan)
    if merchant["akai_opted_in"]:
        raw_rush = (walkin_load + concurrent_zomato) * AKAI["correlation_factor"]
        akai_score = raw_rush + rng.normal(0, AKAI["noise_sigma"], n_orders)
        akai_score = np.clip(akai_score, AKAI["min_score"], AKAI["max_score"])

    walkin_lagged = np.roll(walkin_load, 2)
    walkin_lagged[:2] = walkin_load[:2]
    google_busyness = np.clip(walkin_lagged / EXTERNAL["normalization_max_walkins"], 0, 1)

    hours = np.zeros(n_orders)
    for i, ts in enumerate(time_slots):
        slot = TIME_SLOTS[ts]
        h_low, h_high = slot["hours"]
        if h_low < h_high:
            hours[i] = rng.uniform(h_low, h_high)
        else:
            hours[i] = rng.uniform(h_low, h_high + 24) % 24

    df = pd.DataFrame({
        "merchant_id": merchant["merchant_id"],
        "archetype": merchant["archetype"],
        "venue_type": merchant["venue_type"],
        "for_behavior": merchant["for_behavior"],
        "time_slot": time_slots,
        "hour": hours,
        "complexity": complexities,
        "walkin_load": walkin_load,
        "concurrent_zomato": concurrent_zomato,
        "active_orders": active_orders,
        "queue_factor": qf,
        "true_kpt": true_kpt,
        "for_timestamp": for_timestamp,
        "rider_arrival_time": rider_arrival,
        "raw_dwell_time": raw_dwell,
        "kitchen_wait_true": kitchen_wait,
        "t_approach": t_approach,
        "t_park": t_park,
        "t_handoff": t_handoff,
        "gps_jitter": gps_jitter,
        "is_batched": is_batched,
        "ack_latency": ack_latency,
        "akai_score": akai_score,
        "google_busyness": google_busyness,
    })
    return df


def generate_all_orders(merchants_df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    frames = []
    for _, m in merchants_df.iterrows():
        frames.append(_generate_orders_for_merchant(m.to_dict(), rng))
    df = pd.concat(frames, ignore_index=True)
    df.insert(0, "order_id", np.arange(len(df)))
    return df


def run(seed: int = SEED):
    rng = np.random.default_rng(seed)
    print("  Creating 1,000 merchants across 4 archetypes...")
    merchants = create_merchants(rng)
    print(f"  Merchants created: {len(merchants)}")
    print(f"    Cloud Kitchen: {(merchants.archetype == 'cloud_kitchen').sum()}")
    print(f"    QSR Chain:     {(merchants.archetype == 'qsr_chain').sum()}")
    print(f"    Dine-in:       {(merchants.archetype == 'dine_in').sum()}")
    print(f"    Street Food:   {(merchants.archetype == 'street_food').sum()}")

    print("\n  Generating orders...")
    orders = generate_all_orders(merchants, rng)
    print(f"  Generated {len(orders):,} orders")
    print(f"    KPT range: {orders.true_kpt.min():.1f} – {orders.true_kpt.max():.1f} min")
    print(f"    FOR missing: {orders.for_timestamp.isna().sum():,} ({orders.for_timestamp.isna().mean()*100:.1f}%)")
    print(f"    AKAI available: {orders.akai_score.notna().sum():,} ({orders.akai_score.notna().mean()*100:.1f}%)")
    print(f"    Batched orders: {orders.is_batched.sum():,} ({orders.is_batched.mean()*100:.1f}%)")

    return merchants, orders


if __name__ == "__main__":
    merchants, orders = run()
    print(f"\nSample order:\n{orders.iloc[0].to_dict()}")
