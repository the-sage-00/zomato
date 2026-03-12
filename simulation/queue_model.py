import numpy as np


def queue_factor(active_orders: int, kitchen_capacity: int) -> float:
    if kitchen_capacity <= 0:
        return 2.5
    rho = active_orders / kitchen_capacity
    if rho < 0.5:
        return 1.0
    if rho >= 1.0:
        return 2.5
    return 1.0 + (rho ** 2) / (2.0 * (1.0 - rho))


def queue_factor_vectorized(active_orders: np.ndarray, kitchen_capacity: np.ndarray) -> np.ndarray:
    cap = np.maximum(kitchen_capacity, 1)
    rho = active_orders / cap
    result = np.ones_like(rho, dtype=np.float64)
    mid = (rho >= 0.5) & (rho < 1.0)
    result[mid] = 1.0 + (rho[mid] ** 2) / (2.0 * (1.0 - rho[mid]))
    result[rho >= 1.0] = 2.5
    return result
