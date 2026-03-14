import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error


def run_noise_experiment(orders_df: pd.DataFrame, noise_levels=None):
    if noise_levels is None:
        noise_levels = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]

    df = orders_df.copy()
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["cx_num"] = df["complexity"].map({"simple": 0, "medium": 1, "complex": 2})
    df["arch_num"] = df["archetype"].map({"cloud_kitchen": 0, "qsr_chain": 1, "dine_in": 2, "street_food": 3})

    features = ["arch_num", "cx_num", "hour_sin", "hour_cos",
                "walkin_load", "ack_latency", "google_busyness", "queue_factor"]
    available = [f for f in features if f in df.columns]
    df = df.dropna(subset=available + ["true_kpt"]).copy()
    df = df.sample(min(30000, len(df)), random_state=42).reset_index(drop=True)

    X = df[available].fillna(0).values
    y_clean = df["true_kpt"].values

    n = len(df)
    split = int(0.8 * n)
    X_train, X_test = X[:split], X[split:]
    y_train_clean, y_test = y_clean[:split], y_clean[split:]

    rng = np.random.default_rng(42)
    results = []

    for noise_pct in noise_levels:
        n_corrupt = int(len(y_train_clean) * noise_pct)
        y_noisy = y_train_clean.copy()
        if n_corrupt > 0:
            corrupt_idx = rng.choice(len(y_train_clean), size=n_corrupt, replace=False)
            for idx in corrupt_idx:
                mode = rng.choice(["rider_triggered", "lazy"], p=[0.6, 0.4])
                if mode == "rider_triggered":
                    y_noisy[idx] = y_train_clean[idx] * rng.uniform(0.40, 0.75)
                else:
                    y_noisy[idx] = y_train_clean[idx] + rng.exponential(7.0)

        model = GradientBoostingRegressor(
            n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
        )
        model.fit(X_train, y_noisy)
        preds = model.predict(X_test)
        preds = np.clip(preds, 3, 60)
        mae = mean_absolute_error(y_test, preds)
        errors = np.abs(y_test - preds)
        p90 = np.percentile(errors, 90)

        results.append({
            "noise_pct": noise_pct,
            "noise_pct_label": f"{int(noise_pct*100)}%",
            "mae": round(mae, 2),
            "p90_error": round(p90, 2),
        })

    return pd.DataFrame(results)


def run(orders_df: pd.DataFrame):
    print("  Running label noise experiment...")
    results = run_noise_experiment(orders_df)
    print("  Noise Level → MAE → P90")
    for _, row in results.iterrows():
        print(f"    {row['noise_pct_label']:>5s} → MAE={row['mae']:.2f} → P90={row['p90_error']:.2f}")
    return results
