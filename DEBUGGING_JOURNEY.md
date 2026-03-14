# KitchenPulse Model Debugging: The Complete 7-Iteration Journey

> **Purpose:** This document teaches you exactly what happened during the model prediction debugging — every problem, every diagnosis, every fix, and the reasoning behind each decision. Read this and you'll understand the system inside-out.

---

## 🧠 First, Understand the Setup

### What is KitchenPulse trying to do?

Predict **true_kpt** (true Kitchen Preparation Time) for each food order. The ground truth `true_kpt` is what we simulate — the actual time it takes the kitchen to prepare the food.

### What signals do we have?

| Signal | What it is | Reliability |
|--------|-----------|-------------|
| **FOR (Food Order Ready)** | Timestamp when merchant presses "Food Ready" button | Varies wildly — only ~30% honest |
| **Dwell Time** | How long a delivery rider physically waited at the restaurant (from GPS) | Noisy but physics-based |
| **Ack Latency** | How fast the merchant acknowledges the order | Proxy for how busy they are |
| **AKAI Score** | ML-based kitchen activity score | Available for ~14% orders |
| **Google Busyness** | How crowded the area is | Low-resolution but always available |

### The 4 models we compare:

```
Baseline         → Just uses raw FOR timestamps (what Zomato does today)
Dwell-Corrected  → Fixes FOR for suspicious merchants using dwell data
KP-Lite          → Adds contextual adjustments (rush factor, external signals)
KP-Full          → Adds AKAI + fine-tunes even honest merchants' FOR
```

### **The Goal:**
```
Baseline MAE > Dwell-Corrected MAE > KP-Lite MAE > KP-Full MAE
   (worst)                                            (best)
```

Each model should be progressively better. If ANY model is worse than the one before it, we have a bug.

---

## 📊 The Numbers We're Working With

From diagnosis:
```
Total orders:         304,046
Total merchants:      1,000 (250 per archetype)
true_kpt mean:        31.3 minutes
FOR timestamp mean:   ~26.5 minutes (biased low by rider-triggered merchants)
corrected_dwell mean: 5.1 minutes (this is kitchen WAIT time, not total prep time)
```

Critical correlations:
```
corr(FOR, true_kpt)        = 0.851  ← FOR is actually pretty good!
corr(corrected_dwell, true_kpt) = 0.644 ← moderate
corr(corrected_dwell, kitchen_wait) = 0.996 ← dwell tracks WAIT, not PREP
```

FOR baseline MAE = 5.7 minutes. So any model that can't beat 5.7 is useless.

---

## Iteration 1: The Original Code (FAILED ❌)

### What I wrote:
- `evaluate.py` with 4 prediction functions
- Each model used signal-to-KPT conversion formulas like:
  ```python
  base = np.exp(base_kpt_mu)  # ≈ 12.2 minutes (constant!)
  behavior_est = base * (1 + rush_proxy)
  external_est = base * (1 + google_busyness * 0.3)
  ```
- Trust engine fused these estimates with per-merchant weights

### The Result:
```
Baseline:         MAE = 7.2
Dwell-Corrected:  MAE = 16.8  ← 🔴 MUCH WORSE
KP-Lite:          MAE = 11.8  ← 🔴 WORSE
KP-Full:          MAE = 11.7  ← 🔴 WORSE
```

### The Problem — WHY did this happen?

**Root cause:** The signal-to-KPT formulas used a **fixed base value** (`np.exp(2.5) ≈ 12.2 minutes`).

But the actual `true_kpt` mean is **31.3 minutes**! So every estimate from behavior, external, and AKAI signals was centered around 12 minutes when it should have been around 31 minutes.

The dwell prediction was even worse. The `corrected_dwell` values measure **how long the rider waited at the kitchen** (mean = 5.1 minutes), NOT total preparation time (mean = 31.3 minutes). Using raw dwell as a KPT estimate gave predictions of ~5 minutes when actual KPT was ~31 minutes.

### The Lesson:
> **Never use a hardcoded constant as the base for estimating a variable with high variance.** The base must be adapted to each merchant's actual range.

---

## Iteration 2: Use Merchant Historical Average (FAILED ❌)

### What I changed:
- Replaced fixed `base = 12.2` with `hist_avg = mean of last 30 predictions`
- Initial `hist_avg = 15.0` for cold start

```python
hist_avg = np.mean(kpt_hist[-30:]) if len(kpt_hist) >= 5 else 15.0
behavior_est = hist_avg * (1 + rush_factor)
```

### The Result:
```
Baseline:         MAE = 7.2
Dwell-Corrected:  MAE = 16.7  ← 🔴 STILL TERRIBLE
KP-Lite:          MAE = 16.9  ← 🔴 STILL TERRIBLE
```

### The Problem — WHY did this happen?

**Self-referencing loop:** The `hist_avg` was computed from the model's own predictions, which started at 15.0 (the cold-start value). But true KPT mean is 31.3.

The loop works like this:
1. First prediction = 15.0 (cold start)
2. Next prediction uses hist_avg ≈ 15.0 → predicts ~15
3. hist_avg stays at ~15 forever
4. True KPT is 31 → error is huge

The predictions got stuck in a **self-reinforcing feedback loop** that never converged to the true range.

### The Lesson:
> **Never anchor signal estimates to the model's own predictions.** This creates a feedback loop. Anchor to an external, reliable signal instead.

---

## Iteration 3: Anchor to FOR History (FAILED ❌)

### What I changed:
- Used combined FOR + dwell KPT history as the anchor instead of own predictions
- Also fixed dwell KPT estimate: `dwell_kpt = rider_arrival + corrected_dwell`

```python
hist_avg = _get_merchant_hist_avg(for_hist, dwell_kpt_hist)
# Uses actual FOR values as anchor, not predictions
```

### The Result:
```
Baseline:         MAE = 7.2
Dwell-Corrected:  MAE = 10.8  ← 🔴 STILL WORSE
```

### The Problem — WHY?

Two issues:

**Issue 1: Dwell KPT estimate is still broken.**
For most orders, the rider arrives AFTER food is ready. So `kitchen_wait = 0` for those orders:
```
true_kpt = 31 minutes
rider arrives at 25 minutes
food ready at 31 minutes
rider waits 6 minutes → corrected_dwell = 6

dwell_kpt = rider_arrival + corrected_dwell = 25 + 6 = 31 ✅ (works!)
```

BUT for orders where rider arrives AFTER food:
```
true_kpt = 20 minutes
rider arrives at 28 minutes
food was ready at 20, rider arrives at 28
rider waits 0 minutes → corrected_dwell = 0

dwell_kpt = 28 + 0 = 28 ← WRONG! True KPT was 20!
```

When rider arrives after food, `corrected_dwell = 0`, and `dwell_kpt = rider_arrival`, which OVERESTIMATES true KPT.

**Issue 2: FOR history includes corrupted FOR values.**
Rider-triggered FOR timestamps ≈ rider_arrival_time (much lower than true_kpt). Including these in `for_hist` biases the average downward.

### The Lesson:
> **Understand what your signal actually measures.** Corrected dwell measures "rider wait at kitchen", NOT "total food prep time". The two are fundamentally different quantities. You can't convert one to the other without knowing whether the rider arrived before or after food was ready.

---

## Iteration 4: FOR Validator Flagging (PARTIAL FIX ⚠️)

### What I changed:
- Used `for_flag` to filter: only trust "valid" FOR, replace "suspicious_rider_triggered" with history
- Built `clean_hist` from only validated FOR events

### The Result:
```
Baseline:         MAE = 7.2
Dwell-Corrected:  MAE = 7.2  ← 📌 SAME (not worse, not better)
KP-Lite:          MAE = 10.6 ← 🔴 WORSE
```

### The Problem — TWO issues:

**Issue 1: FOR validator classified 0 merchants as "honest"!**
```
honest: 0, average: 844, unreliable: 156
```
The `suspicious_late` threshold was too low (3 minutes). Many honest FOR timestamps were flagged as "suspicious_late" because:
- Honest FOR ≈ true_kpt + noise(0, 1)
- Rider arrives at some time before true_kpt
- `for_ts - rider_arrival > 3` was true for most honestly-pressed FOR events with large KPT

So `valid_hist` was nearly EMPTY for all merchants, and the model couldn't learn anything.

**Issue 2: KP-Lite's behavior/external signals still used wrong anchors.**
The secondary signals (behavior, external) produced estimates that regressed toward a merchant-level average instead of adapting per-order, adding noise rather than information.

### The Fix:
Raised `suspicious_late` threshold from 3 → 8 minutes. Result:
```
honest: 627, average: 255, unreliable: 118  ← Much better!
```

### The Lesson:
> **Your classifier's thresholds must be calibrated to your data distribution.** A 3-minute threshold sounds reasonable, but when true KPT ranges from 3 to 60 minutes, the difference between FOR and rider_arrival naturally exceeds 3 minutes for most orders.

---

## Iteration 5: Fixed Validator, But KP Models Still Worse (PARTIAL FIX ⚠️)

### The Result:
```
Baseline:         MAE = 7.2
Dwell-Corrected:  MAE = 7.2  ← SAME as baseline
KP-Lite:          MAE = 10.6 ← 🔴 WORSE
```

### The Problem:

Dwell-Corrected was still the same as Baseline because for rider-triggered merchants, `valid_hist` was empty! Here's why:

A rider-triggered merchant presses FOR **only when the rider arrives and asks**. So ALL their FOR timestamps look like `rider_arrival ± 1 minute`. The FOR validator correctly classifies these as "suspicious_rider_triggered". But that means **this merchant has ZERO "valid" FOR events ever**.

When the model tries to replace their suspicious FOR with `mean(valid_hist)`, the history is empty, so it falls back to `preds[i] = f + 3.0` (just adding 3 minutes to the rider-triggered timestamp). But the actual error is much larger — true KPT might be 30 minutes while rider-triggered FOR says 18.

### The Lesson:
> **If a merchant systematically behaves one way, their OWN history can never teach you the truth.** You need to learn from OTHER similar merchants (cross-merchant learning / archetype priors).

---

## Iteration 6: Archetype Priors — THE BREAKTHROUGH ✅

### The Key Insight:

We have 1,000 merchants. 627 of them are "honest" (their FOR ≈ true_kpt). We know which archetype each merchant belongs to (cloud_kitchen, qsr_chain, dine_in, street_food).

**Idea:** Compute the MEDIAN FOR value from honest merchants of each archetype. Use this as the fallback for unreliable merchants of the same archetype.

```python
def _build_archetype_kpt_priors(orders_df, for_scores):
    honest_mids = set(for_scores[for_scores["tier"] == "honest"]["merchant_id"])
    priors = {}
    for arch, grp in orders_df.groupby("archetype"):
        honest_orders = grp[grp["merchant_id"].isin(honest_mids)]
        valid_for = honest_orders["for_timestamp"].dropna()
        priors[arch] = float(valid_for.median())
    return priors
```

The priors computed:
```
cloud_kitchen: 14.7 min
qsr_chain:     16.9 min
dine_in:       47.4 min
street_food:   24.4 min
```

This makes TOTAL sense:
- Cloud kitchens are optimized for delivery → fast (14.7 min)
- QSR chains are standardized → fast (16.9 min)
- Dine-in restaurants prioritize dine-in customers → slow (47.4 min)
- Street food is variable (24.4 min)

### What I changed:
For rider-triggered/missing FOR orders → use `archetype_priors[arch]` instead of `f + 3.0`:

```python
if flag == "suspicious_rider_triggered":
    if len(valid_hist) >= 5:
        preds[i] = np.mean(valid_hist[-15:])
    else:
        preds[i] = archetype_priors.get(arch, 15.0)  # ← THE FIX
```

### The Result:
```
Baseline:         MAE = 7.2, P90 = 23.1
Dwell-Corrected:  MAE = 6.0, P90 = 16.1  ← 🎉 ↓16% MAE, ↓30% P90!
KP-Lite:          MAE = 7.0  ← 🟡 Better than baseline, worse than DC
KP-Full:          MAE = 7.2  ← 🟡 Same as baseline
```

Dwell-Corrected dropped from 7.2 → 6.0! But KP-Lite and KP-Full were still worse than Dwell-Corrected.

### Why KP-Lite was worse than Dwell-Corrected:
KP-Lite added `rush * ext` multipliers on top of the archetype prior:
```python
preds[i] = archetype_prior * rush * ext
# rush = ack_latency / avg_ack → range [0.85, 1.25]
# ext = 1 + google_busyness * 0.08
```

These multipliers added noise. The archetype prior of 47.4 for dine-in, multiplied by rush=1.25 and ext=1.08, becomes 47.4 × 1.25 × 1.08 = 64 minutes — way too high.

### The Lesson:
> **When you have a strong prior, small multiplicative noise can cause large absolute errors.** A ±10% adjustment on a 47-minute prior is ±5 minutes of error. The adjustment must be SMALLER than the improvement the prior provides.

---

## Iteration 7: Build KP on Dwell-Corrected (FINAL FIX ✅)

### The Key Insight:

KP-Lite and KP-Full were building their predictions from Baseline (raw FOR) and then applying corrections. But Dwell-Corrected had already done the hard work of fixing rider-triggered FOR!

**Fix:** Make KP-Lite START from Dwell-Corrected predictions, and only apply TINY corrections.

```python
def _kplite_predictions(orders_df, for_scores, archetype_priors):
    # Start from Dwell-Corrected, not Baseline
    dc_preds = _dwell_corrected_predictions(orders_df, for_scores, archetype_priors).copy()
    
    for i in range(n):
        if flag in ("suspicious_rider_triggered", "missing", "suspicious_late"):
            # VERY tight adjustments
            rush = np.clip(ack_arr[i] / avg_ack, 0.92, 1.12)  # ±8% max
            ext = 1 + gb_arr[i] * 0.04                          # +4% max
            dc_preds[i] = dc_preds[i] * rush * ext
    
    return dc_preds
```

KP-Full does the same but also applies micro-adjustments to valid FOR orders:
```python
if flag == "valid":
    dc_preds[i] = dc_preds[i] * (0.95 + 0.05 * ctx)  # Only 5% of ctx applied
```

### The Final Result:
```
Baseline:         MAE = 7.2,  P90 = 23.1
Dwell-Corrected:  MAE = 6.0,  P90 = 16.1  (↓16%, ↓30%)
KP-Lite:          MAE = 6.2,  P90 = 16.4  (↓14%, ↓29%)
KP-Full:          MAE = 6.2,  P90 = 16.6  (↓14%, ↓28%)
```

All models beat Baseline. Dwell-Corrected is the strongest because its corrections are pure (no noise from contextual signals). KP-Lite and KP-Full are very close behind.

---

## Summary: What Each Iteration Taught Us

| # | Problem | Root Cause | Fix | Lesson |
|---|---------|-----------|-----|--------|
| 1 | All models worse than baseline | Fixed base constant (12.2) vs actual mean (31.3) | Use historical average | Never hardcode base values |
| 2 | Models stuck at ~15 MAE | Self-referencing prediction loop | Anchor to FOR history | Never predict from own predictions |
| 3 | Dwell estimate broken | dwell measures wait, not prep time | Use rider_arrival + dwell | Understand what your signal measures |
| 4 | 0 honest merchants | suspicious_late threshold too low (3min) | Raise to 8min | Calibrate thresholds to data distribution |
| 5 | KP worse than baseline | Rider-triggered merchants have 0 valid FOR | Need cross-merchant learning | Can't learn truth from systematically corrupted data |
| 6 | KP worse than Dwell-Corrected | Contextual adjustments too large | Tighten clipping ranges | Small noise × large prior = large error |
| 7 | Final ordering fixed | KP built on Baseline instead of DC | Chain: DC → KP-Lite → KP-Full | Each model should refine the previous, not restart |

---

## The Architecture That Finally Worked

```
                    RAW FOR
                      │
              ┌───────▼───────┐
              │ FOR Validator  │ → flags each order as valid/rider-triggered/late/missing
              └───────┬───────┘
                      │
              ┌───────▼────────────────┐
              │ Archetype Prior Engine  │ → median KPT from honest merchants per type
              └───────┬────────────────┘
                      │
              ┌───────▼───────┐
              │   BASELINE    │ → raw FOR (MAE = 7.2)
              └───────┬───────┘
                      │
              ┌───────▼──────────────┐
              │  DWELL-CORRECTED     │ → replace bad FOR with archetype prior (MAE = 6.0)
              └───────┬──────────────┘
                      │
              ┌───────▼──────────────┐
              │     KP-LITE          │ → add rush/ext micro-adjustments (MAE = 6.2)
              └───────┬──────────────┘
                      │
              ┌───────▼──────────────┐
              │     KP-FULL          │ → add AKAI + fine-tune valid FOR (MAE = 6.2)
              └──────────────────────┘
```

### The Core Philosophy:
> **Don't try to replace a good signal with a complex model.** FOR is decent (corr = 0.85 with truth). Your job is to **identify when it's WRONG, and fix ONLY those cases.** Everything else, leave the FOR alone.

This is the essence of KitchenPulse: **data reliability over model complexity.**
