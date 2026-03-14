import numpy as np

SEED = 42
NUM_MERCHANTS = 1000
ORDERS_PER_MERCHANT = (100, 500)

ARCHETYPES = {
    "cloud_kitchen": {
        "count": 250,
        "base_kpt_mu": 2.35,
        "base_kpt_sigma": 0.45,
        "kitchen_capacity": 8,
        "walkin_base_lambda": 0,
        "venue_types": ["standalone"],
        "venue_weights": [1.0],
        "akai_opt_in_rate": 0.05,
        "for_profile": {
            "honest": 0.70,
            "rider_triggered": 0.10,
            "lazy": 0.15,
            "missing": 0.05,
        },
    },
    "qsr_chain": {
        "count": 250,
        "base_kpt_mu": 1.95,
        "base_kpt_sigma": 0.35,
        "kitchen_capacity": 12,
        "walkin_base_lambda": 5,
        "venue_types": ["mall", "standalone"],
        "venue_weights": [0.4, 0.6],
        "akai_opt_in_rate": 0.15,
        "for_profile": {
            "honest": 0.60,
            "rider_triggered": 0.10,
            "lazy": 0.20,
            "missing": 0.10,
        },
    },
    "dine_in": {
        "count": 250,
        "base_kpt_mu": 2.85,
        "base_kpt_sigma": 0.50,
        "kitchen_capacity": 6,
        "walkin_base_lambda": 15,
        "venue_types": ["mall", "standalone", "street"],
        "venue_weights": [0.25, 0.55, 0.20],
        "akai_opt_in_rate": 0.25,
        "for_profile": {
            "honest": 0.25,
            "rider_triggered": 0.40,
            "lazy": 0.20,
            "missing": 0.15,
        },
    },
    "street_food": {
        "count": 250,
        "base_kpt_mu": 2.15,
        "base_kpt_sigma": 0.55,
        "kitchen_capacity": 4,
        "walkin_base_lambda": 8,
        "venue_types": ["street"],
        "venue_weights": [1.0],
        "akai_opt_in_rate": 0.05,
        "for_profile": {
            "honest": 0.30,
            "rider_triggered": 0.30,
            "lazy": 0.25,
            "missing": 0.15,
        },
    },
}

TIME_SLOTS = {
    "morning":    {"hours": (6, 11),  "kpt_mult": 0.70, "walkin_mult": 0.3,  "prob": 0.10},
    "lunch":      {"hours": (11, 15), "kpt_mult": 1.40, "walkin_mult": 2.5,  "prob": 0.30},
    "afternoon":  {"hours": (15, 19), "kpt_mult": 0.90, "walkin_mult": 0.8,  "prob": 0.15},
    "dinner":     {"hours": (19, 23), "kpt_mult": 1.30, "walkin_mult": 2.0,  "prob": 0.30},
    "late_night": {"hours": (23, 6),  "kpt_mult": 0.80, "walkin_mult": 0.2,  "prob": 0.15},
}

COMPLEXITY = {
    "simple":  {"multiplier": 0.70, "probability": 0.30},
    "medium":  {"multiplier": 1.00, "probability": 0.50},
    "complex": {"multiplier": 1.50, "probability": 0.20},
}

DWELL_NOISE = {
    "street": {
        "t_approach_mu": 0.5, "t_approach_sigma": 0.3,
        "t_park_mu": 0.5, "t_park_sigma": 0.3,
    },
    "mall": {
        "t_approach_mu": 2.5, "t_approach_sigma": 1.0,
        "t_park_mu": 2.0, "t_park_sigma": 0.8,
    },
    "standalone": {
        "t_approach_mu": 1.0, "t_approach_sigma": 0.5,
        "t_park_mu": 1.0, "t_park_sigma": 0.5,
    },
}
T_HANDOFF_MU = 0.5
T_HANDOFF_SIGMA = 0.2
GPS_JITTER_SIGMA = 0.3

FOR_NOISE = {
    "honest_sigma": 1.0,
    "rider_triggered_low": -0.5,
    "rider_triggered_high": 1.0,
    "lazy_exp_mean": 5.0,
}

TRUST_ENGINE = {
    "alpha_new": 0.30,
    "alpha_stable": 0.10,
    "alpha_transition_orders": 200,
    "max_single_weight": 0.60,
    "min_signals_for_update": 2,
    "update_every_n_orders": 50,
    "cold_buffer_minutes": 5.0,
    "blended_start": 31,
    "blended_end": 100,
    "personalized_start": 101,
    "neighborhood_radius_km": 2.0,
    "neighborhood_top_n": 5,
    "neighborhood_min_orders": 200,
}

ARCHETYPE_PRIOR_WEIGHTS = {
    "cloud_kitchen": {"for": 0.40, "dwell": 0.30, "behavior": 0.15, "akai": 0.05, "external": 0.10},
    "qsr_chain":     {"for": 0.35, "dwell": 0.25, "behavior": 0.15, "akai": 0.05, "external": 0.20},
    "dine_in":       {"for": 0.15, "dwell": 0.40, "behavior": 0.20, "akai": 0.10, "external": 0.15},
    "street_food":   {"for": 0.25, "dwell": 0.50, "behavior": 0.15, "akai": 0.00, "external": 0.10},
}

SIGNAL_NAMES = ["for", "dwell", "behavior", "akai", "external"]

FOR_SCORE = {
    "base_score": 80,
    "penalty_rider_triggered_max": 30,
    "penalty_missing_max": 40,
    "penalty_high_variance": 20,
    "variance_threshold": 5.0,
    "bonus_early_max": 20,
    "bonus_low_variance": 15,
    "low_variance_threshold": 2.0,
    "rider_triggered_window_sec": 60,
    "window_size": 50,
}

AKAI = {
    "correlation_factor": 0.75,
    "noise_sigma": 0.8,
    "min_score": 1,
    "max_score": 10,
    "kpt_impact_per_level": 0.10,
}

EXTERNAL = {
    "lag_minutes": 30,
    "normalization_max_walkins": 50,
    "kpt_impact_at_full": 0.30,
}

BEHAVIOR = {
    "base_latency_sec": 15,
    "rush_scaling": 20,
    "noise_sigma_sec": 5,
    "min_sec": 5,
    "max_sec": 120,
}

DISPATCH = {
    "early_dispatch_minutes": 4,
    "rider_travel_min": 8,
    "rider_travel_max": 20,
}

KPT_BOUNDS = {"min": 3.0, "max": 60.0}

GAMING = {
    "for_rider_window_sec": 90,
    "dwell_multiplier_threshold": 3.0,
    "ack_anomaly_max_sec": 5,
    "ack_anomaly_min_akai": 7,
    "cap_weight": 0.10,
    "min_orders_to_detect": 30,
}

VIZ_COLORS = {
    "background": "#0f0f23",
    "card": "#1a1a2e",
    "primary": "#ff4757",
    "secondary": "#00d2ff",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "text": "#ffffff",
    "muted": "#8892b0",
}
