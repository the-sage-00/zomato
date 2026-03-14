import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from simulation.config import VIZ_COLORS as C


plt.rcParams.update({
    "figure.facecolor": C["background"],
    "axes.facecolor": C["card"],
    "axes.edgecolor": C["muted"],
    "axes.labelcolor": C["text"],
    "text.color": C["text"],
    "xtick.color": C["text"],
    "ytick.color": C["text"],
    "grid.color": "#2a2a4a",
    "font.family": "sans-serif",
    "font.size": 12,
})

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
DASH_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "data")


def _ensure_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DASH_DIR, exist_ok=True)


def chart_p90_comparison(model_results: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    names = list(model_results.keys())
    p90s = [model_results[n]["metrics"]["p90_error"] for n in names]
    colors = [C["danger"], C["warning"], C["secondary"], C["success"]]
    bars = ax.bar(names, p90s, color=colors[:len(names)], width=0.6, edgecolor="none")
    baseline = p90s[0]
    for bar, val in zip(bars, p90s):
        pct = (1 - val / baseline) * 100
        label = f"{val:.1f} min" if pct == 0 else f"{val:.1f} min\n↓{pct:.0f}%"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, label,
                ha="center", va="bottom", fontsize=11, fontweight="bold", color=C["text"])
    ax.set_ylabel("P90 Rider Wait Error (minutes)", fontsize=13)
    ax.set_title("Worst-Case Rider Wait — KitchenPulse Cuts P90 by 50%", fontsize=15, fontweight="bold", pad=15)
    ax.set_ylim(0, max(p90s) * 1.3)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "p90_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_mae_comparison(model_results: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    names = list(model_results.keys())
    maes = [model_results[n]["metrics"]["mae"] for n in names]
    colors = [C["danger"], C["warning"], C["secondary"], C["success"]]
    bars = ax.bar(names, maes, color=colors[:len(names)], width=0.6)
    baseline = maes[0]
    for bar, val in zip(bars, maes):
        pct = (1 - val / baseline) * 100
        label = f"{val:.1f}" if pct == 0 else f"{val:.1f}\n↓{pct:.0f}%"
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15, label,
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_ylabel("Mean Absolute Error (minutes)")
    ax.set_title("KPT Prediction Accuracy — MAE Comparison", fontsize=15, fontweight="bold", pad=15)
    ax.set_ylim(0, max(maes) * 1.3)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "mae_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_for_breakdown(orders_df):
    flags = orders_df.get("for_flag", pd.Series(dtype=str))
    if flags.empty:
        return
    counts = flags.value_counts()
    labels_map = {
        "valid": "Honest (~30%)",
        "suspicious_rider_triggered": "Rider-Triggered (~35%)",
        "suspicious_late": "Lazy/Late (~20%)",
        "missing": "Missing (~15%)",
    }
    color_map = {
        "valid": C["success"],
        "suspicious_rider_triggered": C["danger"],
        "suspicious_late": C["warning"],
        "missing": C["muted"],
    }
    labels = [labels_map.get(k, k) for k in counts.index]
    clrs = [color_map.get(k, C["muted"]) for k in counts.index]

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        counts.values, labels=labels, colors=clrs, autopct="%1.0f%%",
        startangle=90, pctdistance=0.78, wedgeprops={"width": 0.4, "edgecolor": C["background"]},
        textprops={"fontsize": 11},
    )
    for t in autotexts:
        t.set_fontweight("bold")
    ax.text(0, 0, "FOR\nReliability", ha="center", va="center", fontsize=14, fontweight="bold", color=C["text"])
    ax.set_title("70% of FOR Button Data is Unreliable", fontsize=15, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "for_breakdown_pie.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_trust_evolution(trust_profiles: dict, orders_df: pd.DataFrame):
    candidates = []
    for mid, prof in trust_profiles.items():
        if prof["archetype"] == "dine_in" and len(prof["weight_history"]) >= 4:
            beh = orders_df[orders_df["merchant_id"] == mid]["for_behavior"].iloc[0]
            if beh == "rider_triggered":
                candidates.append((mid, prof))
    if not candidates:
        for mid, prof in trust_profiles.items():
            if len(prof["weight_history"]) >= 4:
                candidates.append((mid, prof))
                break
    if not candidates:
        return
    mid, prof = candidates[0]
    hist = prof["weight_history"]
    orders_at = [h["at_order"] for h in hist]
    signal_colors = {"for": C["danger"], "dwell": C["secondary"], "behavior": C["warning"],
                     "akai": C["success"], "external": C["muted"]}

    fig, ax = plt.subplots(figsize=(12, 6))
    for sig in ["for", "dwell", "behavior", "akai", "external"]:
        vals = [h["weights"].get(sig, 0) for h in hist]
        ax.plot(orders_at, vals, marker="o", markersize=5, linewidth=2.5,
                label=sig.upper(), color=signal_colors[sig])
    ax.set_xlabel("Orders Processed", fontsize=13)
    ax.set_ylabel("Signal Weight", fontsize=13)
    ax.set_title(f"Trust Weight Evolution — Merchant #{mid} (Dine-in, Rider-Triggered FOR)",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="center right", fontsize=10, facecolor=C["card"], edgecolor=C["muted"])
    ax.set_ylim(0, 0.65)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "trust_weight_evolution.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_rider_wait_distribution(model_results: dict, orders_df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(12, 6))
    true_kpt = orders_df["true_kpt"].values
    colors = [C["danger"], C["warning"], C["secondary"], C["success"]]
    for i, (name, data) in enumerate(model_results.items()):
        preds = data["predictions"]
        rider_arrival = np.maximum(preds - 4, 0) + 12
        wait = np.maximum(true_kpt - rider_arrival, 0)
        wait_clipped = np.clip(wait, 0, 25)
        ax.hist(wait_clipped, bins=50, alpha=0.5, color=colors[i], label=name, density=True)
    ax.set_xlabel("Rider Wait Time (minutes)", fontsize=13)
    ax.set_ylabel("Density", fontsize=13)
    ax.set_title("Rider Wait Distribution — Tail Compression with KitchenPulse", fontsize=14, fontweight="bold", pad=15)
    ax.legend(fontsize=10, facecolor=C["card"], edgecolor=C["muted"])
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "rider_wait_distribution.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_eta_volatility(model_results: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    names = list(model_results.keys())
    vols = [model_results[n]["metrics"].get("avg_eta_volatility", 0) for n in names]
    colors = [C["danger"], C["warning"], C["secondary"], C["success"]]
    bars = ax.bar(names, vols, color=colors[:len(names)], width=0.6)
    for bar, val in zip(bars, vols):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03, f"{val:.2f}",
                ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_ylabel("Avg ETA Changes per Order (>3min shifts)")
    ax.set_title("ETA Stability — Fewer Surprises = More Customer Trust", fontsize=14, fontweight="bold", pad=15)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "eta_volatility.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_archetype_heatmap(trust_profiles: dict):
    from simulation.config import SIGNAL_NAMES
    archetypes = ["cloud_kitchen", "qsr_chain", "dine_in", "street_food"]
    arch_labels = ["Cloud Kitchen", "QSR Chain", "Dine-in", "Street Food"]
    sig_labels = [s.upper() for s in SIGNAL_NAMES]
    matrix = np.zeros((4, 5))
    counts = np.zeros(4)
    for prof in trust_profiles.values():
        try:
            ai = archetypes.index(prof["archetype"])
        except ValueError:
            continue
        for j, s in enumerate(SIGNAL_NAMES):
            matrix[ai, j] += prof["current_weights"].get(s, 0)
        counts[ai] += 1
    for i in range(4):
        if counts[i] > 0:
            matrix[i] /= counts[i]

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(matrix, cmap="YlGnBu", aspect="auto", vmin=0, vmax=0.6)
    ax.set_xticks(range(5))
    ax.set_xticklabels(sig_labels, fontsize=11)
    ax.set_yticks(range(4))
    ax.set_yticklabels(arch_labels, fontsize=11)
    for i in range(4):
        for j in range(5):
            color = "white" if matrix[i, j] > 0.3 else C["text"]
            ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", fontsize=12, fontweight="bold", color=color)
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Average Weight", fontsize=11)
    ax.set_title("Signal Trust by Restaurant Type — Cloud Kitchen ≠ Dhaba", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "merchant_archetype_heatmap.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_biryani_story(model_results: dict, orders_df: pd.DataFrame):
    dine_in = orders_df[orders_df["archetype"] == "dine_in"]
    sample = dine_in[(dine_in["true_kpt"] > 20) & (dine_in["true_kpt"] < 30)].head(1)
    if len(sample) == 0:
        sample = dine_in.head(1)
    row = sample.iloc[0]
    true = row["true_kpt"]
    bl_pred = model_results["Baseline"]["predictions"][sample.index[0]]
    kp_pred = model_results["KP-Full"]["predictions"][sample.index[0]]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for ax, title, pred, color in [
        (axes[0], "WITHOUT KitchenPulse", bl_pred, C["danger"]),
        (axes[1], "WITH KitchenPulse", kp_pred, C["success"]),
    ]:
        events = [
            (0, "Order Placed", C["secondary"]),
            (max(pred - 4, 0), f"Rider Dispatched\n(est {pred:.0f}min)", C["warning"]),
            (max(pred - 4, 0) + 12, f"Rider Arrives", color),
            (true, f"Food Ready\n(actual {true:.0f}min)", C["success"]),
        ]
        events.sort(key=lambda x: x[0])
        y_pos = list(range(len(events)))
        times = [e[0] for e in events]
        labels = [e[1] for e in events]
        clrs = [e[2] for e in events]
        ax.barh(y_pos, times, color=clrs, height=0.4, alpha=0.8, edgecolor="none")
        for yp, t, l in zip(y_pos, times, labels):
            ax.text(t + 0.5, yp, f"  {l} ({t:.0f}min)", va="center", fontsize=10, color=C["text"])
        rider_arr = max(pred - 4, 0) + 12
        wait = max(true - rider_arr, 0)
        cool = max(rider_arr - true, 0)
        ax.set_title(f"{title}\nRider Wait: {wait:.0f}min | Food Cooling: {cool:.0f}min",
                     fontsize=13, fontweight="bold", color=color, pad=10)
        ax.set_yticks([])
        ax.set_xlabel("Time (minutes)")
        ax.grid(axis="x", alpha=0.3)
    fig.suptitle("Biryani House Story — One Order, Two Outcomes", fontsize=16, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "biryani_story_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_label_noise(noise_results: pd.DataFrame):
    if noise_results is None or len(noise_results) == 0:
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(noise_results["noise_pct"] * 100, noise_results["mae"], "o-",
            color=C["danger"], linewidth=2.5, markersize=8, label="MAE")
    ax.plot(noise_results["noise_pct"] * 100, noise_results["p90_error"], "s--",
            color=C["warning"], linewidth=2, markersize=7, label="P90 Error")
    ax.axvline(x=70, color=C["primary"], linestyle=":", linewidth=2, alpha=0.7)
    ax.text(71, ax.get_ylim()[1] * 0.9, "Current FOR\nnoise (~70%)", fontsize=10, color=C["primary"])
    ax.axvline(x=20, color=C["success"], linestyle=":", linewidth=2, alpha=0.7)
    ax.text(21, ax.get_ylim()[1] * 0.8, "After\nKitchenPulse\n(~20%)", fontsize=10, color=C["success"])
    ax.set_xlabel("Training Label Noise (%)", fontsize=13)
    ax.set_ylabel("Error (minutes)", fontsize=13)
    ax.set_title("Label Noise Directly Destroys Model Accuracy", fontsize=15, fontweight="bold", pad=15)
    ax.legend(fontsize=11, facecolor=C["card"], edgecolor=C["muted"])
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "label_noise_vs_mae.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_dispatch_comparison(dispatch_results: dict):
    if not dispatch_results:
        return
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    names = list(dispatch_results.keys())
    colors = [C["danger"], C["warning"], C["secondary"], C["success"]]

    rw = [dispatch_results[n]["avg_rider_wait"] for n in names]
    bars = axes[0].bar(names, rw, color=colors[:len(names)], width=0.6)
    for bar, val in zip(bars, rw):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f"{val:.1f}",
                     ha="center", va="bottom", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Avg Rider Wait (min)")
    axes[0].set_title("Rider Wait After Dispatch", fontsize=13, fontweight="bold")
    axes[0].grid(axis="y", alpha=0.3)

    fc = [dispatch_results[n]["avg_food_cool"] for n in names]
    bars = axes[1].bar(names, fc, color=colors[:len(names)], width=0.6)
    for bar, val in zip(bars, fc):
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, f"{val:.1f}",
                     ha="center", va="bottom", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Avg Food Cooling Time (min)")
    axes[1].set_title("Food Cooling Before Pickup", fontsize=13, fontweight="bold")
    axes[1].grid(axis="y", alpha=0.3)

    fig.suptitle("Dispatch Simulation — Logistics Impact", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "dispatch_timing_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()


def chart_tail_risk(model_results: dict):
    fig, ax = plt.subplots(figsize=(10, 6))
    names = list(model_results.keys())
    colors = [C["danger"], C["warning"], C["secondary"], C["success"]]
    x = np.arange(len(names))
    w = 0.25
    p90s = [model_results[n]["metrics"]["p90_error"] for n in names]
    p95s = [model_results[n]["metrics"]["p95_error"] for n in names]
    p99s = [model_results[n]["metrics"]["p99_error"] for n in names]
    bars1 = ax.bar(x - w, p90s, w, label="P90", color=[c + "CC" for c in colors])
    bars2 = ax.bar(x, p95s, w, label="P95", color=[c + "99" for c in colors])
    bars3 = ax.bar(x + w, p99s, w, label="P99", color=[c + "66" for c in colors])
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Error (minutes)")
    ax.set_title("Tail Risk Analysis — P90 / P95 / P99 Error", fontsize=14, fontweight="bold", pad=15)
    ax.legend(fontsize=11, facecolor=C["card"], edgecolor=C["muted"])
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "tail_risk_analysis.png"), dpi=150, bbox_inches="tight")
    plt.close()


def _export_sample_orders(orders_df, model_results):
    archetypes = ["cloud_kitchen", "qsr_chain", "dine_in", "street_food"]
    behaviors = ["honest", "rider_triggered", "lazy", "missing"]
    samples = []
    for arch in archetypes:
        for beh in behaviors:
            row = orders_df[(orders_df["archetype"] == arch) & (orders_df["for_behavior"] == beh)]
            if len(row) > 0:
                samples.append(row.iloc[0])
            if len(samples) >= 10:
                break
        if len(samples) >= 10:
            break
    while len(samples) < 10:
        samples.append(orders_df.sample(1, random_state=99).iloc[0])
    bl_preds = model_results["Baseline"]["predictions"]
    kp_preds = model_results["KP-Full"]["predictions"]
    rows = []
    for s in samples:
        idx = s.name
        for_ts = s["for_timestamp"]
        true = s["true_kpt"]
        gap = abs(for_ts - true) if not np.isnan(for_ts) else None
        rows.append({
            "order_id": int(s["order_id"]),
            "merchant_id": int(s["merchant_id"]),
            "archetype": s["archetype"],
            "for_behavior": s["for_behavior"],
            "complexity": s["complexity"],
            "time_slot": s["time_slot"],
            "true_kpt": round(true, 1),
            "for_timestamp": round(for_ts, 1) if not np.isnan(for_ts) else None,
            "for_gap": round(gap, 1) if gap is not None else None,
            "rider_arrival": round(s["rider_arrival_time"], 1),
            "ack_latency": round(s["ack_latency"], 1),
            "google_busyness": round(s["google_busyness"], 2),
            "baseline_pred": round(float(bl_preds[idx]), 1),
            "kp_pred": round(float(kp_preds[idx]), 1),
        })
    with open(os.path.join(DASH_DIR, "sample_orders.json"), "w") as f:
        json.dump(rows, f, indent=2)


def _export_biryani_story(orders_df, model_results):
    dine_in = orders_df[orders_df["archetype"] == "dine_in"]
    candidates = dine_in[(dine_in["true_kpt"] > 25) & (dine_in["true_kpt"] < 45)
                         & (dine_in["for_behavior"] == "rider_triggered")]
    if len(candidates) == 0:
        candidates = dine_in[(dine_in["true_kpt"] > 20) & (dine_in["true_kpt"] < 40)]
    row = candidates.iloc[0]
    idx = row.name
    true_kpt = float(row["true_kpt"])
    bl_pred = float(model_results["Baseline"]["predictions"][idx])
    kp_pred = float(model_results["KP-Full"]["predictions"][idx])

    def make_timeline(pred, label):
        dispatch = max(pred - 4, 0)
        rider_travel = 12
        rider_arr = dispatch + rider_travel
        rider_wait = max(true_kpt - rider_arr, 0)
        food_cool = max(rider_arr - true_kpt, 0)
        return {
            "label": label,
            "prediction": round(pred, 1),
            "events": [
                {"time": 0, "label": "Order Placed", "type": "neutral"},
                {"time": round(dispatch, 1), "label": f"Rider Dispatched (est {pred:.0f}min)", "type": "dispatch"},
                {"time": round(rider_arr, 1), "label": "Rider Arrives", "type": "rider"},
                {"time": round(true_kpt, 1), "label": f"Food Ready ({true_kpt:.0f}min)", "type": "food"},
            ],
            "rider_wait": round(rider_wait, 1),
            "food_cool": round(food_cool, 1),
        }

    story = {
        "archetype": row["archetype"],
        "merchant_id": int(row["merchant_id"]),
        "true_kpt": round(true_kpt, 1),
        "for_behavior": row["for_behavior"],
        "without_kp": make_timeline(bl_pred, "WITHOUT KitchenPulse"),
        "with_kp": make_timeline(kp_pred, "WITH KitchenPulse"),
    }
    with open(os.path.join(DASH_DIR, "biryani_story.json"), "w") as f:
        json.dump(story, f, indent=2)


def _export_for_examples(orders_df):
    examples = []
    for beh in ["honest", "rider_triggered", "lazy", "missing"]:
        subset = orders_df[orders_df["for_behavior"] == beh]
        if beh == "missing":
            row = subset.iloc[0]
            examples.append({
                "behavior": beh,
                "true_kpt": round(float(row["true_kpt"]), 1),
                "for_timestamp": None,
                "gap": None,
                "rider_arrival": round(float(row["rider_arrival_time"]), 1),
                "verdict": "No data at all",
            })
        else:
            row = subset.iloc[5]
            for_ts = float(row["for_timestamp"])
            true = float(row["true_kpt"])
            gap = round(for_ts - true, 1)
            if beh == "honest":
                verdict = f"FOR is {abs(gap):.1f}min off — reliable ✅"
            elif beh == "rider_triggered":
                verdict = f"FOR is {abs(gap):.1f}min EARLY — tracks rider, not food ❌"
            else:
                verdict = f"FOR is {abs(gap):.1f}min LATE — merchant pressed lazily ⚠️"
            examples.append({
                "behavior": beh,
                "true_kpt": round(true, 1),
                "for_timestamp": round(for_ts, 1),
                "gap": gap,
                "rider_arrival": round(float(row["rider_arrival_time"]), 1),
                "verdict": verdict,
            })
    with open(os.path.join(DASH_DIR, "for_examples.json"), "w") as f:
        json.dump(examples, f, indent=2)


def export_dashboard_json(model_results, orders_df, trust_profiles, noise_results,
                          dispatch_results, scenario_results, for_scores):
    _ensure_dirs()

    _export_sample_orders(orders_df, model_results)
    _export_biryani_story(orders_df, model_results)
    _export_for_examples(orders_df)

    metrics_data = {
        "models": list(model_results.keys()),
        "mae": [model_results[n]["metrics"]["mae"] for n in model_results],
        "p50_error": [model_results[n]["metrics"]["p50_error"] for n in model_results],
        "p90_error": [model_results[n]["metrics"]["p90_error"] for n in model_results],
        "p95_error": [model_results[n]["metrics"]["p95_error"] for n in model_results],
        "within_3min": [model_results[n]["metrics"]["within_3min"] for n in model_results],
        "within_5min": [model_results[n]["metrics"]["within_5min"] for n in model_results],
        "avg_eta_volatility": [model_results[n]["metrics"].get("avg_eta_volatility", 0) for n in model_results],
    }
    with open(os.path.join(DASH_DIR, "metrics_comparison.json"), "w") as f:
        json.dump(metrics_data, f, indent=2)

    sample_profiles = []
    # Sample from all 4 archetypes to ensure Signal Weights chart has data for all types
    archetypes_for_profiles = ["cloud_kitchen", "qsr_chain", "dine_in", "street_food"]
    per_arch_profiles = 13
    for arch in archetypes_for_profiles:
        count = 0
        for mid, p in trust_profiles.items():
            if p["archetype"] == arch:
                sample_profiles.append({
                    "merchant_id": mid,
                    "archetype": p["archetype"],
                    "order_count": p["order_count"],
                    "for_score": p["for_score"],
                    "gaming_detected": p["gaming_detected"],
                    "current_weights": p["current_weights"],
                    "weight_history": p["weight_history"],
                })
                count += 1
                if count >= per_arch_profiles:
                    break
    with open(os.path.join(DASH_DIR, "merchant_profiles.json"), "w") as f:
        json.dump(sample_profiles, f, indent=2)

    trust_evol = []
    # Sample merchants from all 4 archetypes for dashboard variety
    archetypes_needed = ["cloud_kitchen", "qsr_chain", "dine_in", "street_food"]
    per_arch = 3
    for arch in archetypes_needed:
        count = 0
        for mid, prof in trust_profiles.items():
            if prof["archetype"] == arch and len(prof["weight_history"]) >= 4:
                beh = orders_df[orders_df["merchant_id"] == mid]["for_behavior"].iloc[0]
                trust_evol.append({
                    "merchant_id": mid,
                    "archetype": prof["archetype"],
                    "for_behavior": beh,
                    "weight_history": prof["weight_history"],
                })
                count += 1
                if count >= per_arch:
                    break
    with open(os.path.join(DASH_DIR, "trust_evolution.json"), "w") as f:
        json.dump(trust_evol, f, indent=2)

    if "for_flag" in orders_df.columns:
        fc = orders_df["for_flag"].value_counts().to_dict()
        total = sum(fc.values())
        for_dist = {
            "honest_count": fc.get("valid", 0),
            "rider_triggered_count": fc.get("suspicious_rider_triggered", 0),
            "lazy_count": fc.get("suspicious_late", 0),
            "missing_count": fc.get("missing", 0),
            "honest_pct": round(fc.get("valid", 0) / total * 100, 1),
            "rider_triggered_pct": round(fc.get("suspicious_rider_triggered", 0) / total * 100, 1),
            "lazy_pct": round(fc.get("suspicious_late", 0) / total * 100, 1),
            "missing_pct": round(fc.get("missing", 0) / total * 100, 1),
        }
    else:
        for_dist = {}
    with open(os.path.join(DASH_DIR, "for_distribution.json"), "w") as f:
        json.dump(for_dist, f, indent=2)

    if noise_results is not None:
        with open(os.path.join(DASH_DIR, "label_noise_experiment.json"), "w") as f:
            json.dump(noise_results.to_dict("records"), f, indent=2)

    if dispatch_results:
        with open(os.path.join(DASH_DIR, "dispatch_results.json"), "w") as f:
            json.dump(dispatch_results, f, indent=2)

    if scenario_results:
        with open(os.path.join(DASH_DIR, "scenario_presets.json"), "w") as f:
            json.dump(scenario_results, f, indent=2, default=str)


def generate_all_charts(model_results, orders_df, trust_profiles, noise_results=None, dispatch_results=None):
    _ensure_dirs()
    chart_p90_comparison(model_results)
    chart_mae_comparison(model_results)
    chart_for_breakdown(orders_df)
    chart_trust_evolution(trust_profiles, orders_df)
    chart_rider_wait_distribution(model_results, orders_df)
    chart_eta_volatility(model_results)
    chart_archetype_heatmap(trust_profiles)
    chart_biryani_story(model_results, orders_df)
    if noise_results is not None:
        chart_label_noise(noise_results)
    if dispatch_results:
        chart_dispatch_comparison(dispatch_results)
    chart_tail_risk(model_results)
    n_charts = 8 + (1 if noise_results is not None else 0) + (1 if dispatch_results else 0) + 1
    print(f"  {n_charts} charts saved to output/")
