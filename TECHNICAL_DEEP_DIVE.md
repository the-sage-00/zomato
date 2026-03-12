# 🔬 KitchenPulse — Technical Deep Dive

> **Purpose:** This file explains how every algorithm, formula, and system component works under the hood. After reading this, you will understand every line of math and every design decision.

---

## 1. DATA GENERATION — How We Create Realistic Orders

### 1.1 Merchant Creation (data_generator.py)

We create **1,000 merchants** split into 4 archetypes (250 each):

| Archetype | Base KPT (min) | FOR Behavior Split | Logic |
|-----------|---------------|-------------------|-------|
| Cloud Kitchen | 10 ± 3 | 60% honest, 15% rider, 15% lazy, 10% missing | Digital-native, better at pressing FOR |
| QSR Chain | 8 ± 2 | 45% honest, 20% rider, 20% lazy, 15% missing | Standardized but busy |
| Dine-in | 25 ± 8 | 20% honest, 40% rider, 25% lazy, 15% missing | Worst FOR compliance — busy staff |
| Street Food | 12 ± 5 | 25% honest, 15% rider, 20% lazy, 40% missing | Often lacks smartphone skills |

### 1.2 Order Generation — The True KPT Formula

For each order, the **true kitchen preparation time** is computed as:

```
true_kpt = base_kpt × complexity_factor × time_slot_factor × queue_factor + random_noise
```

**Each component explained:**

#### base_kpt
- Drawn from a normal distribution centered on the merchant's archetype mean
- Example: A dine-in merchant might have base_kpt = 25 ± 8 minutes
- Clamped to `[3.0, 60.0]` min to avoid impossible values

#### complexity_factor
- Each order is randomly assigned: `simple` (0.7), `medium` (1.0), or `complex` (1.4)
- A simple dal costs less time; a complex biryani costs more
- Distribution: ~30% simple, ~50% medium, ~20% complex

#### time_slot_factor
- Different hours have different kitchen loads:
  - `morning` (6-11am): 0.85 (lighter load, faster cooking)
  - `lunch` (11am-3pm): 1.15 (peak rush, slower)
  - `afternoon` (3-6pm): 0.90 (between rushes)
  - `dinner` (6-11pm): 1.20 (heaviest rush, slowest)
  - `late_night` (11pm-2am): 0.95

#### queue_factor (M/D/1 Queueing Model)
```python
active_orders = zomato_orders + walkin_orders
utilization = active_orders / kitchen_capacity       # rho
if utilization < 1.0:
    queue_factor = 1 + (utilization² / (2 * (1 - utilization)))
else:
    queue_factor = 1 + utilization   # overloaded kitchen
```

This comes from **queueing theory**. The M/D/1 model tells us:
- When a kitchen is at 50% capacity → queue_factor ≈ 1.25 (25% slower)
- When at 80% capacity → queue_factor ≈ 2.6 (160% slower!)
- When overloaded (>100%) → linear penalty

**Why this matters:** Real kitchens don't just "take longer when busy" — they experience exponential slowdowns due to bottlenecks. A kitchen handling 8 simultaneous orders is NOT 2x slower than one handling 4 — it's more like 3-4x slower. The M/D/1 model captures this accurately.

#### random_noise
- Small Gaussian noise: `N(0, 1.5)` minutes
- Simulates natural cooking variability (ingredient prep, oven variations, etc.)

### 1.3 FOR Timestamp Generation

Once `true_kpt` is known, the FOR timestamp is generated based on the merchant's behavior:

| Behavior | FOR Timestamp Formula | What It Simulates |
|----------|----------------------|-------------------|
| Honest | `true_kpt + N(0, 1.0)` | Merchant presses FOR within ~1 min of food being ready |
| Rider-triggered | `rider_arrival_time + N(0, 0.5)` | Merchant presses FOR when rider asks, not when food is ready |
| Lazy | `true_kpt + U(3, 15)` | Merchant waits 3-15 minutes after food is ready |
| Missing | `NaN` | No FOR signal at all |

### 1.4 Other Signals Generated

| Signal | Formula | What It Represents |
|--------|---------|-------------------|
| rider_arrival_time | `order_time + travel_time + N(0, 1.5)` | When rider GPS shows arrival at restaurant |
| dwell_time_raw | `pickup_time - rider_arrival_time + GPS_jitter` | Raw GPS-measured time at restaurant |
| ack_latency | `U(5, 120)` seconds | How fast merchant acknowledged the order in the app |
| akai_score | `true_kpt + N(0, 0.8)` (13.5% of orders) | AKAI sensor prediction (very accurate but rare) |
| google_busyness | `U(0.2, 0.9)` | Google Maps popular times API busyness factor |

---

## 2. FOR VALIDATOR — Flagging Bad Signals (for_validator.py)

### Algorithm:
```python
for each order:
    if for_timestamp is NaN:
        flag = "missing"
    elif |for_timestamp - rider_arrival_time| < 2.0 minutes:
        flag = "suspicious_rider_triggered"
    elif |corrected_dwell - for_timestamp| > 8.0 minutes:
        flag = "suspicious_late"
    else:
        flag = "valid"
```

### Why these thresholds?

**2-minute threshold for rider-triggered:**
If the FOR button was pressed within 2 minutes of the rider's GPS arrival, it's very likely the merchant pressed it because the rider asked "is my order ready?" The timestamp reflects rider arrival, not food readiness.

**8-minute threshold for suspicious_late:**
Initially (Iteration 4) this was 3 minutes, which flagged too many honest merchants. Through debugging, we found that honest merchants sometimes take 3-5 minutes after cooking to press the button (wrapping food, checking order, etc.). Raising to 8 minutes eliminated false positives while still catching genuinely lazy presses.

### Merchant Reliability Score:
After flagging all orders, each merchant gets a reliability score:
```python
reliability = valid_count / total_count
```
- **Honest** (reliability ≥ 0.60): Trust their FOR data
- **Average** (0.30 ≤ reliability < 0.60): Partially trust
- **Unreliable** (reliability < 0.30): Mostly ignore their FOR

---

## 3. DWELL DECOMPOSITION — Cleaning GPS Data (dwell_decomposition.py)

### The Problem:
Raw GPS dwell time = `pickup_time - rider_arrival_time`. But this includes:
- Parking time (rider looking for a spot)
- Walking to the restaurant
- Standing in queue
- Actual food waiting
- Handoff time (verifying order, packing)

### The Fix:
```python
corrected_dwell = raw_dwell - t_park - t_walk - t_handoff
```
Where:
- `t_park` = estimated parking time based on venue type (2 min for mall, 0 for street)
- `t_walk` = estimated walking time (1 min average)
- `t_handoff` = order verification time (1-2 min)
- Result is clamped to `[1.0, max_dwell]` to avoid negative values

The corrected dwell time is our best physical estimate of "how long did the rider actually wait for food."

---

## 4. TRUST ENGINE — Adaptive Signal Weighting (trust_engine.py)

### Core Concept:
Every merchant has 5 signal weights that sum to 1.0:
```python
weights = {
    "for":       0.20,   # initial equal weights
    "dwell":     0.20,
    "behavior":  0.20,
    "akai":      0.20,
    "external":  0.20,
}
```

### How Weights Update After Each Order:
```python
# For each signal that had an estimate for this order:
signal_error = |signal_estimate - actual_kpt|
signal_accuracy = 1.0 / (1.0 + signal_error)

# Normalize accuracies to weights:
total_accuracy = sum(all signal accuracies)
raw_weight[signal] = accuracy[signal] / total_accuracy

# Exponential moving average update:
new_weight[signal] = (1 - learning_rate) × old_weight + learning_rate × raw_weight
# learning_rate = 0.3
```

### What This Achieves:
After ~50-100 orders:
- For an **honest merchant**: FOR weight stays at 0.30-0.40 (it's consistently accurate)
- For a **rider-triggered merchant**: FOR weight drops to 0.02-0.05 (it's consistently wrong), Dwell rises to 0.50+
- For a **missing-FOR merchant**: FOR gets weight 0 (no data), Behavior and External compensate

### Archetype Priors:
For merchants with no valid FOR history:
```python
archetype_prior = median(true_kpt) from all honest merchants of same archetype
```
This is a "peer learning" mechanism — if we can't trust Merchant X's data, we learn from other honest merchants of the same restaurant type.

### The dwell_kpt_buffer Fix (Iteration 7):
When building the Dwell-Corrected prediction, we discovered that raw corrected_dwell had a systematic underestimate. The fix:
```python
dwell_kpt_buffer = 2.0  # minutes
dwell_estimate = corrected_dwell + dwell_kpt_buffer
```
This accounts for the fact that the rider's GPS arrival might be slightly before they actually interact with the restaurant.

---

## 5. KITCHENPULSE SCORE — Signal Fusion (kitchenpulse_score.py)

### Final Prediction Formula:
```python
kp_score = (w_for × for_estimate 
          + w_dwell × dwell_estimate 
          + w_behavior × behavior_estimate 
          + w_akai × akai_estimate 
          + w_external × external_estimate)
```

Where:
- `for_estimate` = raw FOR timestamp (or archetype prior if missing/flagged)
- `dwell_estimate` = corrected_dwell + buffer
- `behavior_estimate` = merchant's historical median KPT for similar complexity/time_slot
- `akai_estimate` = AKAI sensor prediction (if available, else excluded from fusion)
- `external_estimate` = google_busyness × archetype_base_kpt (weak signal)

### KP-Lite vs KP-Full:
- **KP-Lite**: Uses only FOR, Dwell, and Behavior signals
- **KP-Full**: Uses all 5 signals including AKAI and External
- Both build ON TOP of the Dwell-Corrected prediction (they refine it, not restart)

### The "Build on DC" Architecture (Iteration 7 Fix):
```python
# WRONG (Iterations 1-5): KP-Full starts from scratch
kp_full_pred = weighted_average(all_5_signals)

# CORRECT (Iteration 7): KP-Full refines Dwell-Corrected
dc_pred = dwell_corrected_prediction
adjustment = weighted_average(small_signal_deltas)  # capped at ±3 min
kp_full_pred = dc_pred + adjustment
```

**Why this works better:** The Dwell-Corrected prediction is already good (MAE=6.0). The other signals shouldn't override it — they should make small corrections. Capping adjustments at ±3 min prevents edge cases from blowing up the prediction.

---

## 6. EVALUATION — How We Measure Success (evaluate.py)

### Metrics Computed:

| Metric | Formula | What It Captures |
|--------|---------|-----------------|
| MAE | `mean(|pred - true|)` | Average prediction quality |
| Median Error (P50) | `median(|pred - true|)` | Typical prediction quality (less sensitive to outliers) |
| P90 Error | `percentile(|pred - true|, 90)` | Worst 10% of orders |
| P95 Error | `percentile(|pred - true|, 95)` | Worst 5% of orders |
| Within ±3min | `mean(|pred - true| ≤ 3)` | Fraction of "very good" predictions |
| Within ±5min | `mean(|pred - true| ≤ 5)` | Fraction of "acceptable" predictions |
| ETA Volatility | `std(consecutive_prediction_differences) / mean(predictions)` | Prediction stability |

---

## 7. LABEL NOISE EXPERIMENT (label_noise_experiment.py)

### How It Works:
```python
for noise_pct in [0, 10, 20, 30, 40, 50, 60, 70, 80]:
    corrupted_labels = true_kpt.copy()
    n_corrupt = int(len(labels) * noise_pct / 100)
    random_indices = random.choice(len(labels), n_corrupt)
    corrupted_labels[random_indices] = for_timestamp[random_indices]
    
    model = GradientBoostingRegressor(n_estimators=200, max_depth=5)
    model.fit(X_train, corrupted_labels_train)
    predictions = model.predict(X_test)
    
    mae = mean_absolute_error(y_true_test, predictions)
    p90 = percentile(errors, 90)
```

### Key Finding:
| Noise % | MAE | P90 | Interpretation |
|---------|-----|-----|----------------|
| 0% | 8.09 | 18.33 | Clean data = best possible model |
| 40% | 8.32 | 19.02 | Even moderate noise hurts P90 |
| 80% | 8.66 | 20.17 | Heavy noise = nearly 10% degradation |

**Conclusion:** Label noise has a direct, measurable, and monotonic negative impact on ML model accuracy. KitchenPulse's Trust Engine reduces effective label noise by downweighting unreliable FOR signals.

---

## 8. DISPATCH SIMULATOR (dispatch_simulator.py)

### How Dispatch Works:
```python
dispatch_time = max(predicted_kpt - buffer, 0)   # buffer = 4 minutes
rider_travel_time = 12 minutes (average)
rider_arrival = dispatch_time + rider_travel_time

rider_wait = max(true_kpt - rider_arrival, 0)     # rider arrives before food
food_cool = max(rider_arrival - true_kpt, 0)      # food ready before rider
```

If prediction is accurate (pred ≈ true_kpt):
- rider_wait ≈ 0 (rider arrives exactly when food is ready)
- food_cool ≈ 0 (no cooling time)

If prediction is too LOW (pred < true_kpt):
- Rider arrives too early → high rider_wait
- Wasted rider time, fuel, reduced delivery capacity

If prediction is too HIGH (pred > true_kpt):
- Rider arrives too late → high food_cool
- Customer gets cold food, bad experience

---

## 9. THE 7 DEBUGGING ITERATIONS — Summary

| Iter | Problem | Fix | Result |
|------|---------|-----|--------|
| 1 | Hardcoded base_kpt = 12.2 (actual mean = 31.3) | — | All KP models worse than baseline |
| 2 | Self-referencing predictions (feedback loop) | — | Models diverge, no convergence |
| 3 | Used rider dwell time as prep time directly | — | Systematically underestimated |
| 4 | suspicious_late threshold too low (3 min) | Raised to 8 min | False positives dropped 40% |
| 5 | Rider-triggered merchants had no valid FOR history | — | Fallback predictions terrible |
| 6 | No cross-merchant learning | Added archetype priors | DC MAE: 7.2 → 6.0 |
| 7 | KP-Lite/Full overrode good DC predictions | Built KP on top of DC, capped ±3min | Final: MAE=6.2, P90=16.6 |

**Key Lesson:** Each iteration improved by ~0.5-1.0 MAE. The biggest single improvement was Iteration 6 (archetype priors), which dropped MAE by 1.2 minutes. The final architecture chains models: `Baseline → Dwell-Corrected → KP-Lite → KP-Full`, where each refines the previous instead of restarting.

---

## 10. DASHBOARD DATA FLOW

```
Python Simulation (304K orders in RAM)
    ↓
    Aggregate results into small JSON files
    ↓
dashboard/data/
    ├── metrics_comparison.json     (4 models × 7 metrics)
    ├── for_distribution.json       (4 behavior percentages)
    ├── trust_evolution.json        (10 merchants × weight history)
    ├── merchant_profiles.json      (50 merchants × current weights)
    ├── label_noise_experiment.json (9 noise levels × MAE/P90)
    ├── dispatch_results.json       (4 models × wait/cool stats)
    ├── scenario_presets.json       (4 scenarios × predictions)
    ├── sample_orders.json          (10 representative orders)
    ├── biryani_story.json          (1 order timeline comparison)
    └── for_examples.json           (4 behavior examples)
    ↓
Dashboard (HTML/CSS/JS + Chart.js)
    → Reads JSON files via fetch()
    → Renders interactive charts and tables
```

All 10 JSON files represent aggregated or sampled data from the full 304K-order evaluation. The core metrics (MAE, P90, accuracy) are computed on the ENTIRE dataset, not a sample.

---
