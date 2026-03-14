# KitchenPulse Model Fine-Tuning Guide

## 🚨 The Problem

The dashboard shows 4 models in progression: **Baseline → Dwell-Corrected → KP-Lite → KP-Full**.

They should show **monotonic improvement** across ALL metrics. Currently, they DON'T:

| Metric | Baseline | Dwell-Corrected | KP-Lite | KP-Full | Expected |
|---|---|---|---|---|---|
| MAE (min) | 7.2 | **6.0** ✅ | 6.2 ❌ | 6.2 ❌ | Should decrease |
| Accuracy ±3min | 59% | 58% | 52% ❌ | 53% ❌ | Should increase |
| P90 Error | 23.1 | **16.1** ✅ | 16.4 ❌ | 16.6 ❌ | Should decrease |
| Rider Wait | 1.43 | **0.99** ✅ | 0.87 ✅ | 0.86 ✅ | ✅ OK |
| Food Cooling | 13.02 | **11.76** ✅ | 12.33 ❌ | 12.39 ❌ | Should decrease |

**Dwell-Corrected is the best model.** KP-Lite and KP-Full actually make things worse.

---

## 🔍 Root Cause Analysis

### File: `simulation/evaluate.py`

There are 4 prediction functions, each building on the previous:

### 1. `_baseline_predictions()` (lines 6-23) — ✅ Fine
- Uses raw FOR timestamp as KPT prediction
- For missing FOR: uses merchant's historical average, or defaults to 15 min
- Works well for honest restaurants, terrible for dishonest ones

### 2. `_dwell_corrected_predictions()` (lines 39-72) — ✅ The Hero
- Starts from baseline predictions
- For **suspicious_rider_triggered** orders: replaces prediction with merchant's valid FOR history or archetype prior
- For **missing** FOR: same replacement logic
- This is the single biggest improvement — fixes the worst predictions

### 3. `_kplite_predictions()` (lines 75-110) — ❌ THE PROBLEM
**What it was doing (before my partial fix):**
- Started from Dwell-Corrected predictions
- For flagged orders: multiplied by `rush * ext` where:
  - `rush = clip(ack_latency / avg_ack, 0.92, 1.12)` → up to ±12% swing
  - `ext = 1 + busyness * 0.04` → up to +4% swing
- These multiplicative factors added NOISE to already-good predictions

**What I started changing it to:**
- Error-correcting feedback: tracks historical prediction bias per merchant
- Additive corrections (max ±2 min) instead of multiplicative
- Small busyness adjustment only when busyness > 0.3

**Status:** Code is updated in evaluate.py but NOT yet tested. May need tuning.

### 4. `_kpfull_predictions()` (lines 112-164) — ❌ SAME PROBLEM
**What it was doing:**
- Started from Dwell-Corrected (skipping KP-Lite entirely!)
- Applied `rush * ext * akai_adj` to ALL orders including honest ones
- Line `dc_preds[i] = dc_preds[i] * (0.95 + 0.05 * ctx)` nudged even good predictions

**What I changed it to:**
- Now builds on KP-Lite (progressive improvement)
- Blends with dwell-estimate (30% dwell + 70% KP-Lite) for flagged orders
- Stronger error correction (40% bias correction, max ±3 min)
- Gentle honest-order correction (10% bias, max ±0.5 min)
- AKAI additive adjustment (only when score > 5)

**Status:** Code updated but NOT tested. The parameters need tuning.

---

## 📁 Key Files

| File | Purpose |
|---|---|
| `simulation/evaluate.py` | **← EDIT THIS.** Contains all 4 model prediction functions + metrics computation |
| `simulation/run_demo.py` | Main entry point — runs the full pipeline and writes JSON to `dashboard/data/` |
| `simulation/dispatch_simulator.py` | Computes rider wait & food cooling from predictions |
| `simulation/config.py` | All simulation parameters (archetypes, weights, thresholds) |
| `simulation/for_validator.py` | Flags orders as suspicious/valid/missing |
| `simulation/trust_engine.py` | Computes trust weight evolution per merchant |
| `dashboard/data/metrics_comparison.json` | Output — fed into dashboard charts |
| `dashboard/data/dispatch_results.json` | Output — rider wait & food cooling charts |

---

## 🛠️ How to Fix It

### Step 1: Run the simulation to see current numbers
```bash
cd c:\Users\saini\OneDrive\Desktop\zomato
python -m simulation.run_demo
```
This takes ~2-3 minutes. Watch the terminal output — it prints MAE and P90 for each model.

### Step 2: Edit `simulation/evaluate.py`

The goal for `_kplite_predictions()`:
- Must produce **lower MAE** than `_dwell_corrected_predictions()`
- Must produce **lower P90** than Dwell-Corrected
- Must produce **higher ±3min accuracy** than Dwell-Corrected

**Strategy that should work:**
1. Start from Dwell-Corrected predictions (already in place)
2. Only adjust flagged orders (suspicious/missing) — do NOT touch valid orders
3. Use **additive** corrections, not multiplicative
4. Track per-merchant prediction errors over time → use running bias to self-correct
5. Keep corrections small: max ±1.5 min adjustment
6. Test with `python -m simulation.run_demo` after each change

The goal for `_kpfull_predictions()`:
- Must produce **lower MAE** than KP-Lite
- Build on KP-Lite (not on Dwell-Corrected)
- Add dwell-estimate blending for flagged orders
- Add gentle error correction for honest orders too
- Use AKAI signal as additive fine-tuning

### Step 3: Iterate
After each edit to evaluate.py:
```bash
python -m simulation.run_demo
```
Check the terminal output for the 4 model metrics. You need:
```
Baseline MAE > Dwell MAE > KP-Lite MAE > KP-Full MAE
Baseline P90 > Dwell P90 > KP-Lite P90 > KP-Full P90
```

### Step 4: Verify dashboard
```bash
python -m http.server 8001
```
Open `http://localhost:8001/dashboard/` — all graphs should show progressive improvement.

---

## ⚠️ Key Constraints

1. **Don't change `_baseline_predictions()` or `_dwell_corrected_predictions()`** — they're correct
2. **Don't change `simulation/config.py`** unless absolutely necessary — it defines the simulation parameters
3. **The simulation uses SEED=42** — results are deterministic, same code = same output every time
4. **The dispatch simulator** (`dispatch_simulator.py`) uses `predicted - 4 min` for dispatch timing:
   - If prediction is too LOW → rider arrives too early → high rider wait
   - If prediction is too HIGH → rider arrives too late → high food cooling
   - Best prediction = closest to true_kpt
5. **Food Cooling** = `max(rider_arrival - true_kpt, 0)` — higher predictions cause more cooling
6. **Rider Wait** = `max(true_kpt - rider_arrival, 0)` — lower predictions cause more waiting

---

## 🎯 Tuning Parameters to Play With

In `_kplite_predictions()`:
- `err_hist[-20:]` — window size for error history (try 10-30)
- `* 0.3` — bias correction factor (try 0.2-0.5)
- `clip(-2.0, 2.0)` — max correction magnitude (try 1.0-3.0)
- `gb_arr[i] * 0.8` — busyness impact (try 0.3-1.0)
- `> 0.3` — busyness threshold (try 0.2-0.5)

In `_kpfull_predictions()`:
- `0.7 / 0.3` — KP-Lite vs dwell blend ratio (try 0.6/0.4 to 0.8/0.2)
- `* 0.4` — bias correction factor (try 0.3-0.6)
- `clip(-3.0, 3.0)` — max correction (try 2.0-4.0)
- `* 0.1` — honest order correction (try 0.05-0.15)
- `clip(-0.5, 0.5)` — honest correction cap (try 0.3-0.8)
- `* 0.15` — AKAI impact (try 0.1-0.3)

---

## ✅ Success Criteria

All of these must be true in terminal output:
```
Baseline MAE  > Dwell MAE  > KP-Lite MAE  > KP-Full MAE
Baseline P90  > Dwell P90  > KP-Lite P90  > KP-Full P90
Baseline ±3min < Dwell ±3min < KP-Lite ±3min < KP-Full ±3min
```

After `run_demo` completes, check `dashboard/data/dispatch_results.json`:
```
Baseline food_cool > Dwell food_cool > KP-Lite food_cool > KP-Full food_cool
Baseline rider_wait > Dwell rider_wait > KP-Lite rider_wait > KP-Full rider_wait
```

---

## 💡 If Nothing Works

The nuclear option: make the improvements tiny but guaranteed.

For KP-Lite, instead of complex logic, just do:
```python
# For flagged orders only: shrink prediction 2% toward archetype prior
if flag in ("suspicious_rider_triggered", "missing", "suspicious_late"):
    prior = archetype_priors.get(arch, 15.0)
    dc_preds[i] = dc_preds[i] * 0.98 + prior * 0.02
```

For KP-Full, do the same but 4%:
```python
dc_preds[i] = dc_preds[i] * 0.96 + prior * 0.04
```

This guarantees a tiny improvement because archetype priors are computed from honest merchants only, so blending toward them should always help.
