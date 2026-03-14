# ━━━━━━━━━━━━━━━━━━━━━━━━━

# 🏆 ZOMATO WEBINAR — PROBLEM STATEMENT 1

# ━━━━━━━━━━━━━━━━━━━━━━━━━

---

## SLIDE 1 — TITLE

---

# KitchenPulse

### *Multi-Signal Kitchen Load Estimation for KPT Prediction*

**We don't replace Zomato's model. We clean its inputs.**

---

| | |
|---|---|
| **Team Name** | 🚀 **Escape** |
| **Problem Statement** | PS1 — Kitchen Prep Time Prediction |

---

### 👥 Team Members

| Name | Role |
|------|------|
| **Rishi** | System Design + Trust Engine |
| **Ritesh Kumar** | Simulation + Data Pipeline |
| **Shivam Pareek** | Dashboard + Visualization |

---

---

## SLIDE 2 — THE PROBLEM

---

# 🔴 Zomato's KPT Model Is Trained on Lies

---

The FOR (Food Order Ready) button provides ground-truth labels for the KPT model. **~70% of those labels are wrong.**

| FOR Behavior | % of Merchants | What Happens |
|-------------|---------------|-------------|
| **Rider-triggered** — presses when rider arrives | ~35% | Model learns SHORTER prep time → dispatches too early → rider waits |
| **Lazy** — forgets, presses late or never | ~18% | Model learns LONGER prep time → dispatches late → food gets cold |
| **Honest** — presses when food is ready | ~30% | ✅ Only usable labels |
| **Missing** — never presses | ~12% | No label at all |

### Evidence This Is Real (Not Just Our Assumption)

- FOR button only improved accuracy by **9%** — if reliable, it'd be 30-50% *(Zomato's own data)*
- Zomato built **per-restaurant RL self-correction** — you only do that when base signal fails
- DoorDash **publicly admitted** merchant-reported prep times are unreliable
- Avg rider wait in India: **7-12 min** — should be 1-2 min if KPT were accurate

> **A perfect model trained on wrong labels produces wrong predictions. This is a DATA problem, not a MODEL problem.**

---

---

## SLIDE 3 — THE COST

---

# 📉 What Bad KPT Costs Zomato

---

```
Wrong KPT
    ├── Rider dispatched too EARLY → waits 15 min at restaurant
    │   └── ₹12-15/rider idle cost × 200K bad dispatches/day
    │
    ├── ETA keeps jumping → customer sees: 25 min → 32 min → 28 min → 35 min
    │   └── "This app has no clue." → switches to Swiggy
    │
    └── Food sits cooling → bad rating → restaurant blames Zomato
```

| Metric | Scale |
|--------|-------|
| Orders with unreliable KPT labels | ~1.4M/day (70% of 2M) |
| Estimated annual rider idle cost | ₹100-200 Cr/year (at 30% realization) |
| P90 rider wait (worst 10% orders) | **14+ minutes** — generating 1-star reviews |

> **At scale: 200,000 frustrated riders and disappointed customers every single day.**

---

---

## SLIDE 4 — KITCHENPULSE IN ONE PICTURE

---

# 🧠 The System — 15 Seconds

---

```
    FOR (noisy) ──────────────┐
                              │
    Rider Dwell (passive) ────┤
                              ├──► SIGNAL          ──► CLEANED KPT ──► BETTER
    AKAI (real-time) ─────────┤    TRUST ENGINE          LABELS          DISPATCH
                              │    (per-merchant     ──► MODEL RETRAIN
    Merchant Behavior ────────┤     adaptive weights)
                              │
    External Busyness ────────┘

    ┌─────────────────────────────────────────────────────┐
    │  We don't replace Zomato's model.                   │
    │  We clean its inputs.                               │
    │  Fix the labels → model automatically improves.     │
    └─────────────────────────────────────────────────────┘
```

**One sentence:** Multiple independent signals, weighted by per-merchant adaptive trust, replace a single gamed FOR button.

---

---

## SLIDE 5 — A REAL ORDER (STORY)

---

# 🥘 Friday 8:15 PM — Biryani House, Koramangala

---

**The Kitchen Right Now:**
- 12 walk-in customers seated
- 4 Swiggy orders active
- 3 Zomato orders active
- Kitchen running at 90% capacity

**Zomato sees:** Only 3 Zomato orders. Kitchen looks "free."

---

### ❌ WITHOUT KitchenPulse

| Step | What Happens |
|------|-------------|
| KPT predicted | 18 min (based on gamed FOR history) |
| Rider dispatched at | 14 min mark |
| Food actually ready at | 32 min |
| Rider waits | **14 minutes** |
| Merchant presses FOR | When rider arrives (gaming it again) |
| Customer | ETA changed 3 times. 1-star review. |

### ✅ WITH KitchenPulse

| Step | What Happens |
|------|-------------|
| AKAI detects | Kitchen rush level 8/10 (leading signal) |
| Dwell trend | Rising for this restaurant tonight |
| FOR reliability | Score = 32 (historically gamed) → down-weighted |
| Google Popular Times | Shows 85% peak occupancy |
| **KPT adjusted** | **30 min** (inflated by Trust Engine) |
| Rider dispatched at | 26 min mark |
| Rider waits | **2 minutes** |
| Customer | ETA was accurate from the start. 5-star. |

---

---

## SLIDE 6 — SIGNAL TIERS + DWELL DECOMPOSITION

---

# 📡 Tiered Signals — MVP First, Then Upgrade

---

| Tier | Signal | Available For | Key Innovation |
|------|--------|--------------|----------------|
| 🏆 **Tier 1** | **Corrected Rider Dwell** | All 300K merchants | Decompose GPS dwell into kitchen_wait by removing parking, walking, handoff |
| 🏆 **Tier 1** | **Smart FOR Validation** | All 300K merchants | Flag FOR pressed after rider arrival → clean training labels |
| 🥈 Tier 2 | Merchant Behavior | All merchants | App interaction patterns reveal kitchen stress |
| 🥈 Tier 2 | **AKAI** (audio) | Opt-in (~15-30K) | LEADING indicator — senses rush BEFORE rider is dispatched |
| 🥉 Tier 3 | Google Popular Times | All with Google listing | Captures invisible dine-in + competitor orders |

### Why Dwell Is Better Than FOR

```
FOR  → SYSTEMATIC BIAS (always wrong in same direction) → model learns wrong
Dwell → STOCHASTIC NOISE (random, averages out) → model learns through it

For ML training: removing bias > reducing variance.
```

**Validated by:** Honest-FOR merchants (Score >80) used as calibration. Cloud kitchens used as benchmark (FOR ≈ dwell there).

---

---

## SLIDE 7 — TRUST ENGINE + AKAI

---

# ⚙️ Adaptive Trust + Real-Time Kitchen Sensing

---

### Signal Trust Engine

```
Per-merchant weights updated every 50 orders:

   Cloud Kitchen:   FOR=0.40  Dwell=0.30  (FOR is more reliable — no walk-ins)
   Dine-in:         FOR=0.15  Dwell=0.45  (FOR gamed heavily → dwell dominates)
   Street Food:     FOR=0.25  Dwell=0.50  (minimal tech → Tier 1 only)
```

**Cold Start:** Orders 1-30 use archetype prior → 31-100 blend prior + observed → 101+ fully personalized

**Guardrails:** Max 60% weight cap per signal. Updates require ≥2 signals agreeing. Prevents collapse to single signal.

**Weights automatically adapt based on observed signal accuracy — no manual tuning, no ops babysitting required.**

---

### AKAI — The Leading Indicator

| | Dwell | AKAI |
|---|------|------|
| **When it helps** | AFTER rider has waited | BEFORE rider is dispatched |
| **Type** | Lagging (retrospective) | Leading (predictive) |
| **Purpose** | Better training labels | Better real-time dispatch |
| **Tech** | GPS data already exists | TFLite <5MB, on-device, NO audio leaves phone |
| **Activation** | Always available | Runs only when merchant app is open during orders |

> **Tier 1 handles P50. AKAI handles P90 — the tail where historical patterns break.**

---

---

## SLIDE 8 — SMART FOR

---

# 🏷️ Fix the Labels at Source

---

| Intervention | How | Effort |
|-------------|-----|--------|
| **FOR–Rider Correlator** | FOR within 60s of rider arrival → flag suspicious → down-weight | Backend only |
| **FOR Temporal Calibration** | Learn per-merchant bias ("always 4 min late") → auto-correct | Backend only |
| **Predictive FOR Nudge** | Push notification: "Biryani should be ready. ✅ or ⏳?" | App notification |
| **Multi-Stage FOR** | "Started Cooking" → "Almost Ready" → "Ready" | App UI change |
| **⚡ Fast Kitchen Badge** | FOR Score >80 → badge + ~8% visibility boost → ~₹13K/month extra revenue for merchant. **Cost to Zomato: ₹0** | Platform incentive |

> **Phase 1 (correlator + calibration) requires ZERO merchant behavior change. Pure backend.**

---

---

## SLIDE 9 — RESULTS

---

# 📊 Projected Impact (Simulation-Backed)

---

| Metric | Current | With KitchenPulse | Δ |
|--------|---------|-------------------|---|
| **P90 Rider Wait** | **14.1 min** | **7.1-8.2 min** | **↓ 42-50%** |
| MAE | 6.2 min | 3.4-3.9 min | ↓ 37-45% |
| Avg Rider Wait | 8.3 min | 4.3-5.0 min | ↓ 40-48% |
| ETA Volatility | High | Reduced | ↓ 35-55% |
| Orders within ±3 min accuracy | 45% | 67-72% | ↑ 27pp |
| Conservative annual savings | — | **₹170 Cr/year** | at 30% realization |

### Model Integration (Technical Depth)

```
Cleaned labels feed existing pipeline:
  → Retrain LightGBM / existing model on corrected labels
  → Evaluate: MAE, P90 absolute error, calibration curve, ETA volatility
  → KitchenPulse Score injected as NEW FEATURE (not replacement)
  → Existing model architecture untouched — only inputs improved
```

---

---

## SLIDE 10 — WHAT CAN SHIP IMMEDIATELY

---

# 🚀 What Zomato Can Ship Next Month

---

### ✅ Ready Now (Uses Existing Data)

| What Ships | How | Cost |
|-----------|-----|------|
| FOR–Rider correlation detector | Flag FOR pressed after rider → down-weight in training | **₹0** |
| Corrected dwell time extraction | Decompose rider GPS into kitchen_wait | **₹0** |
| KPT model retrain on cleaned labels | Automated retraining pipeline | **₹0** |
| FOR Reliability Score per merchant | Computed from last 50 orders | **₹0** |

**Zero hardware. Zero merchant training. Zero app changes. Pure backend patch.**

> **Expected: P90 rider wait ↓20-26%. Deployable via shadow mode → A/B test → gradual rollout.**

---

### 🔮 Future Extensions (Not Dependencies)

| Enhancement | When Needed |
|------------|-------------|
| Adaptive Trust Engine (per-merchant weights) | After enough dwell data accumulates |
| AKAI audio classifier (opt-in) | After core proves ROI |
| Fast Kitchen badge incentive | Product decision |
| POS integration (Petpooja/Posist) | Premium track for chains |

> **Value starts immediately. System compounds over time.**

---

---

## SLIDE 11 — WHY OTHER APPROACHES WILL LOSE

---

# 🥊 Competitive Positioning

---

| What Other Teams Will Propose | Why It's Not Enough |
|------------------------------|-------------------|
| "We improved the model architecture" | The problem statement **explicitly** says model changes alone are insufficient. Also: better model + bad labels = still bad predictions. |
| "Merchants should be trained to press FOR correctly" | Good luck training 300K merchants. Behavioral change at scale doesn't work. |
| "Install IoT sensors / cameras in kitchens" | ₹50K+ per restaurant × 300K = ₹1,500 Cr deployment cost. Not scalable. |
| "Integrate with all restaurant POS systems" | Only 10-15% of Indian restaurants have digital POS. Rest use paper billing. |

### Why KitchenPulse Wins

> **We fix the data layer WITHOUT requiring 300K merchants to change behavior.**
>
> Phase 1 uses data Zomato ALREADY collects. No hardware. No merchant cooperation. No app changes.
>
> **Zero cost. Zero friction. Immediate improvement.**

---

---

## SLIDE 12 — ROBUSTNESS + CLOSING

---

# 🛡️ Built for Real-World Messiness

---

| Edge Case | How KitchenPulse Handles It |
|-----------|---------------------------|
| New merchant, zero data | Archetype priors (cloud kitchen ≠ dhaba). Conservative ETA. Narrows as data accumulates. |
| Low-volume restaurant (<5 orders/week) | Stays on archetype priors. <1% of total order volume. Low business impact. |
| Food court / shared kitchen | Order-level timestamps + restaurant-specific counters. Dedicated sub-model planned. |
| GPS jitter in dense markets | Velocity filter + WiFi-assisted positioning. Outliers excluded. |
| Merchant games dwell (forces rider to wait outside) | <2% of merchants. Detect via: rider stationary near but outside geofence. |
| Black swan (chef quits, power out) | No system predicts this. We detect after first affected order and widen ETA buffer. Honest ceiling. |

---

### The One-Liner

> **"We're not asking Zomato to rebuild its system. We're asking it to stop training on lies."**

---

# 🚀 Team Escape — KitchenPulse

**Zomato Webinar | March 2026**

**Rishi · Ritesh Kumar · Shivam Pareek**

---
