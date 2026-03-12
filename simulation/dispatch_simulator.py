import numpy as np
import pandas as pd
from simulation.config import DISPATCH


def simulate_dispatch(orders_df: pd.DataFrame, prediction_column: str, rng: np.random.Generator) -> pd.DataFrame:
    predicted = orders_df[prediction_column].values
    true_kpt = orders_df["true_kpt"].values

    dispatch_time = np.maximum(predicted - DISPATCH["early_dispatch_minutes"], 0)
    travel = rng.uniform(DISPATCH["rider_travel_min"], DISPATCH["rider_travel_max"], size=len(orders_df))
    rider_arrival = dispatch_time + travel

    rider_wait = np.maximum(true_kpt - rider_arrival, 0)
    food_cool = np.maximum(rider_arrival - true_kpt, 0)

    return pd.DataFrame({
        "order_id": orders_df["order_id"].values,
        "predicted_kpt": predicted,
        "true_kpt": true_kpt,
        "rider_arrival": rider_arrival,
        "rider_wait": rider_wait,
        "food_cool_time": food_cool,
    })


def compute_dispatch_metrics(dispatch_df: pd.DataFrame) -> dict:
    rw = dispatch_df["rider_wait"]
    fc = dispatch_df["food_cool_time"]
    return {
        "avg_rider_wait": round(rw.mean(), 2),
        "p90_rider_wait": round(np.percentile(rw, 90), 2),
        "p95_rider_wait": round(np.percentile(rw, 95), 2),
        "pct_wait_over_10": round((rw > 10).mean() * 100, 1),
        "avg_food_cool": round(fc.mean(), 2),
        "pct_cool_over_5": round((fc > 5).mean() * 100, 1),
    }


def run(orders_df: pd.DataFrame, model_predictions: dict, seed: int = 42):
    rng = np.random.default_rng(seed)
    results = {}
    for model_name, pred_col in model_predictions.items():
        dispatch = simulate_dispatch(orders_df, pred_col, rng)
        metrics = compute_dispatch_metrics(dispatch)
        results[model_name] = metrics
    print("  Dispatch simulation complete")
    for name, m in results.items():
        print(f"    {name}: Rider Wait={m['avg_rider_wait']:.1f}min, "
              f"P90={m['p90_rider_wait']:.1f}min, "
              f"Food Cool={m['avg_food_cool']:.1f}min")
    return results
