import numpy as np
import pandas as pd
from simulation.config import DWELL_NOISE, T_HANDOFF_MU, KPT_BOUNDS


def decompose(orders_df: pd.DataFrame, merchants_df: pd.DataFrame) -> pd.Series:
    venue_map = merchants_df.set_index("merchant_id")["venue_type"]
    venues = orders_df["merchant_id"].map(venue_map)

    t_approach_est = venues.map(lambda v: DWELL_NOISE[v]["t_approach_mu"]).astype(np.float64)
    t_park_est = venues.map(lambda v: DWELL_NOISE[v]["t_park_mu"]).astype(np.float64)

    corrected = (
        orders_df["raw_dwell_time"].values
        - t_approach_est.values
        - t_park_est.values
        - T_HANDOFF_MU
    )

    mask_batched = orders_df["is_batched"].values
    mask_outlier = (corrected < 0) | (corrected > KPT_BOUNDS["max"])
    mask_invalid = mask_batched | mask_outlier

    result = np.where(mask_invalid, np.nan, np.maximum(corrected, 0.0))
    return pd.Series(result, index=orders_df.index, name="corrected_dwell")


def run(orders_df: pd.DataFrame, merchants_df: pd.DataFrame):
    corrected = decompose(orders_df, merchants_df)
    valid = corrected.notna().sum()
    filtered = corrected.isna().sum()
    print(f"  Dwell decomposition: {valid:,} valid, {filtered:,} filtered")
    return corrected
