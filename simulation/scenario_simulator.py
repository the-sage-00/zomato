import numpy as np
from simulation.config import ARCHETYPES, TIME_SLOTS, COMPLEXITY, ARCHETYPE_PRIOR_WEIGHTS, AKAI, EXTERNAL


def run_scenario(archetype: str, time_slot: str, for_reliability: int,
                 rush_level: int, complexity: str) -> dict:
    arch = ARCHETYPES.get(archetype, ARCHETYPES["dine_in"])
    ts = TIME_SLOTS.get(time_slot, TIME_SLOTS["lunch"])
    cx = COMPLEXITY.get(complexity, COMPLEXITY["medium"])

    base_kpt = np.exp(arch["base_kpt_mu"])
    true_kpt = base_kpt * ts["kpt_mult"] * cx["multiplier"] * (1 + rush_level * 0.08)
    true_kpt = np.clip(true_kpt, 3, 60)

    if for_reliability > 70:
        for_est = true_kpt + np.random.normal(0, 1)
    elif for_reliability > 30:
        for_est = true_kpt + np.random.normal(0, 3)
    else:
        for_est = true_kpt * 0.7

    priors = ARCHETYPE_PRIOR_WEIGHTS.get(archetype, ARCHETYPE_PRIOR_WEIGHTS["dine_in"])
    for_w = priors["for"] * (for_reliability / 100)
    dwell_w = priors["dwell"] * (1 + (100 - for_reliability) / 200)
    total = for_w + dwell_w + priors["behavior"] + priors["akai"] + priors["external"]
    weights = {
        "for": for_w / total,
        "dwell": dwell_w / total,
        "behavior": priors["behavior"] / total,
        "akai": priors["akai"] / total,
        "external": priors["external"] / total,
    }

    dwell_est = true_kpt + np.random.normal(0, 2)
    behavior_est = 5 + (rush_level * 8) * 0.18
    akai_est = base_kpt * (1 + rush_level * AKAI["kpt_impact_per_level"])
    ext_busyness = np.clip(rush_level / 10, 0, 1)
    ext_est = base_kpt * (1 + ext_busyness * EXTERNAL["kpt_impact_at_full"])

    estimates = {"for": for_est, "dwell": dwell_est, "behavior": behavior_est, "akai": akai_est, "external": ext_est}
    kp_score = sum(weights[s] * estimates[s] for s in weights)

    baseline_dispatch = max(for_est - 4, 0) + 12
    kp_dispatch = max(kp_score - 4, 0) + 12
    baseline_wait = max(true_kpt - baseline_dispatch, 0)
    kp_wait = max(true_kpt - kp_dispatch, 0)

    return {
        "archetype": archetype,
        "time_slot": time_slot,
        "for_reliability": for_reliability,
        "rush_level": rush_level,
        "complexity": complexity,
        "true_kpt": round(true_kpt, 1),
        "baseline_prediction": round(for_est, 1),
        "kp_prediction": round(kp_score, 1),
        "baseline_error": round(abs(for_est - true_kpt), 1),
        "kp_error": round(abs(kp_score - true_kpt), 1),
        "baseline_rider_wait": round(baseline_wait, 1),
        "kp_rider_wait": round(kp_wait, 1),
        "weights": {k: round(v, 3) for k, v in weights.items()},
        "estimates": {k: round(v, 1) for k, v in estimates.items()},
    }


def get_presets():
    return [
        {"name": "Honest Cloud Kitchen", "params": {"archetype": "cloud_kitchen", "time_slot": "dinner", "for_reliability": 90, "rush_level": 3, "complexity": "medium"}},
        {"name": "Gaming Dine-in Rush", "params": {"archetype": "dine_in", "time_slot": "lunch", "for_reliability": 15, "rush_level": 9, "complexity": "complex"}},
        {"name": "Missing FOR Street Food", "params": {"archetype": "street_food", "time_slot": "lunch", "for_reliability": 5, "rush_level": 7, "complexity": "medium"}},
        {"name": "Quiet QSR Morning", "params": {"archetype": "qsr_chain", "time_slot": "morning", "for_reliability": 75, "rush_level": 2, "complexity": "simple"}},
    ]


def run():
    presets = get_presets()
    print("  Scenario simulations:")
    for p in presets:
        result = run_scenario(**p["params"])
        print(f"    {p['name']}: True={result['true_kpt']}min, "
              f"Baseline={result['baseline_prediction']}min (err={result['baseline_error']}), "
              f"KP={result['kp_prediction']}min (err={result['kp_error']})")
    return [{"name": p["name"], "result": run_scenario(**p["params"])} for p in presets]
