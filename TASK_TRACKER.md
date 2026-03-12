# 🚀 KitchenPulse — Team Escape Task Tracker
### Hackathon Final Round: March 15, 2026 — 12:00 PM

> **Live Status Board.** Update this file as you finish each task.
> Mark: `[ ]` = todo | `[/]` = in progress | `[x]` = done
>
> **Legend:**
> - 🔴 **Ritesh** — Data + Simulation Engine
> - 🟣 **Rishi** — Trust Engine + Algorithm Core
> - 🟢 **Shivam** — Charts + Dashboard + PPT Slides

---

## ⏰ Timeline Overview

| Day | Date | Goal |
|-----|------|------|
| **Day 1** | Wed Mar 12 | Foundation + Data Generation |
| **Day 2** | Thu Mar 13 | Signal Processing + Trust Engine |
| **Day 3** | Fri Mar 14 | Evaluation + Charts + Dashboard |
| **Day 4** | Sat Mar 15 AM | Final polish + Rehearsal |
| **🎯 D-Day** | Sat Mar 15 12:00 PM | PRESENT |

---

## 📦 DAY 1 — Wednesday, March 12

### RITESH 🔴 — Foundation Files

- [ ] `simulation/config.py`
  - [ ] Merchant archetype settings (1000 restaurants, 4 types)
  - [ ] FOR noise profiles per archetype (honest/rider-triggered/lazy/missing %)
  - [ ] Time-of-day multipliers (5 time slots)
  - [ ] Order complexity settings (simple/medium/complex)
  - [ ] Dwell time noise params (T_approach, T_park, T_handoff per venue type)
  - [ ] Trust Engine alpha values + 60% cap + update frequency
  - [ ] Cold start prior weights per archetype
  - [ ] Kitchen capacity per archetype (for queue model)

- [ ] `simulation/queue_model.py` ← **[NEW — Critical]**
  - [ ] `queue_factor(active_orders, kitchen_capacity)` function
  - [ ] M/D/1 inspired formula: ρ < 0.5 → 1.0x, ρ = 0.9 → 1.8x, ρ ≥ 1.0 → 2.5x cap
  - [ ] Add docstring explaining queueing theory for judges

- [ ] `simulation/data_generator.py`
  - [ ] `create_merchants(N=1000)` — generates merchant profiles with permanent FOR behavior
  - [ ] `generate_true_kpt(merchant, order)` using lognormal × time_factor × complexity × queue_factor
  - [ ] FOR timestamp noise generation (all 4 behavior types)
  - [ ] Rider arrival time simulation (dispatch based on historical FOR average + travel)
  - [ ] Raw dwell time = kitchen_wait + GPS noise components
  - [ ] Secondary signals: ack_latency, akai_score (if opted-in), google_busyness
  - [ ] `neighborhood_id` field per merchant (for cold-start neighborhood learning)
  - [ ] Save output as `orders.parquet` + `dashboard/data/merchant_profiles.json`

- [ ] **Verify Test 1:**
  - [ ] `assert 250_000 <= len(df) <= 350_000`
  - [ ] `assert df.true_kpt.between(3, 60).all()`
  - [ ] Print 5 sample rows, check all fields populated

---

## 📦 DAY 2 — Thursday, March 13

### RITESH 🔴 — Signal Processing

- [ ] `simulation/dwell_decomposition.py`
  - [ ] `decompose_dwell(order, merchant)` → subtract T_approach + T_park + T_handoff
  - [ ] Filter batched orders (return None)
  - [ ] Outlier filter: corrected < 0 or > 60 → return None
  - [ ] `learn_approach_park_medians(merchant)` using orders where food ready before rider arrived

- [ ] `simulation/for_validator.py`
  - [ ] Per-order flagging: `flag_for(order)` → suspicious_rider_triggered / suspicious_late / valid / missing
  - [ ] Per-merchant scoring: `compute_for_score(last_50_orders)` → 0-100
  - [ ] Score tiers: 0-49 Unreliable, 50-79 Average, 80-100 Honest

- [ ] `simulation/gaming_detector.py` ← **[NEW — Critical]**
  - [ ] Detect Pattern 1: FOR always within 90 sec of rider arrival
  - [ ] Detect Pattern 2: Dwell consistently > 3× historical median
  - [ ] Detect Pattern 3: Ack latency implausibly low while AKAI is high
  - [ ] `classify_gaming(merchant)` → flag + cap affected signal weight at 10%

### RISHI 🟣 — Trust Engine

- [ ] `simulation/trust_engine.py`
  - [ ] Cold start Phase 1 (orders 1-30): Use archetype priors + ±5 min buffer
  - [ ] Cold start Phase 2 (orders 31-100): 60% prior + 40% observed
  - [ ] Phase 3 (orders 101+): Fully personalized
  - [ ] **[NEW]** `neighborhood_prior(new_merchant, all_merchants)` → find 5 nearest same-archetype/cuisine
  - [ ] Weight update formula: `w_new = α × accuracy + (1-α) × w_old`
  - [ ] Guardrail 1: 60% weight cap per signal
  - [ ] Guardrail 2: ≥2 signals must agree before update fires
  - [ ] Guardrail 3: Normalize after every update (`assert sum(weights) ≈ 1.0`)
  - [ ] Store weight_history log per merchant (every 50 orders)

- [ ] `simulation/kitchenpulse_score.py`
  - [ ] Signal → KPT estimate conversions (all 5 signals)
  - [ ] `compute_kp_score(order, trust_profile)` with renormalization if signal missing
  - [ ] Return both final score AND per-signal contributions dict

- [ ] **Verify Test 2:**
  - [ ] All merchant weights sum to 1.0
  - [ ] No single weight > 0.60
  - [ ] Rider-triggered merchants: FOR weight < 0.20 after 200 orders ✓
  - [ ] Honest merchants: FOR weight > 0.30 after 200 orders ✓

### RISHI 🟣 — Label Noise Experiment

- [ ] `simulation/label_noise_experiment.py` ← **[NEW — Scientific Proof]**
  - [ ] Train LinearRegression on clean labels (true_kpt)
  - [ ] Train same model on noisy FOR labels at noise levels: 0%, 20%, 40%, 60%, 80%
  - [ ] Compute MAE at each noise level against true_kpt
  - [ ] Show KitchenPulse connection: "We reduce noise from 70% → 20%"
  - [ ] Export results to `dashboard/data/label_noise_experiment.json`
  - [ ] **Verify Test 4:** MAE increases monotonically with noise level

---

## 📦 DAY 3 — Friday, March 14

### RITESH 🔴 — Dispatch Simulator

- [ ] `simulation/dispatch_simulator.py` ← **[NEW — Operations Impact]**
  - [ ] `simulate_dispatch(order, predicted_kpt)` → rider_wait, food_cool_time
  - [ ] Run for all 4 models across all orders
  - [ ] Compute summary: Avg rider wait, avg food cooling time, % orders with wait > 10 min
  - [ ] Export to `dashboard/data/dispatch_results.json`

- [ ] `simulation/explainability.py` ← **[NEW]**
  - [ ] Per-order signal contribution breakdown (weight × estimate for each signal)
  - [ ] `format_explanation(order, trust_profile, kp_score)` → dict with contributions

### RISHI 🟣 — Evaluation

- [ ] `simulation/evaluate.py`
  - [ ] Baseline model: FOR only (historical average if missing)
  - [ ] Dwell-Corrected model: Replace suspicious FOR with dwell
  - [ ] KP-Lite: Tier 1 + Behavior + External, no AKAI
  - [ ] KP-Full: All 5 signals + Trust Engine
  - [ ] Compute: MAE, P50, P90, Avg Rider Wait, Within ±3 min, ETA Volatility
  - [ ] ETA Volatility: Simulate ETA recalc at t=3, t=6, t=9 min per order
  - [ ] **Verify Test 3:** Ordering must be Baseline > Dwell > KP-Lite > KP-Full
  - [ ] If wrong ordering → tune `config.py` noise params

- [ ] `simulation/scenario_simulator.py` ← **[NEW — Dashboard Interactive]**
  - [ ] `run_scenario(archetype, time_slot, for_reliability, rush_level, complexity)` → predictions dict
  - [ ] 4 preset scenarios exported to `dashboard/data/scenario_presets.json`

- [ ] `simulation/run_demo.py`
  - [ ] Wire all modules in correct order
  - [ ] Print beautiful terminal summary table
  - [ ] **Verify Test 6:** Runs in < 30 seconds

### SHIVAM 🟢 — Charts + Dashboard

- [ ] `simulation/visualize.py` — all 11 charts:
  - [ ] Chart 1: P90 Rider Wait comparison (red → green gradient bars)
  - [ ] Chart 2: MAE comparison
  - [ ] Chart 3: FOR fraud breakdown donut
  - [ ] Chart 4: Trust weight evolution line chart (most dramatic dine-in example)
  - [ ] Chart 5: Rider wait distribution (KDE overlay)
  - [ ] Chart 6: ETA volatility bar chart ← secret weapon
  - [ ] Chart 7: Archetype × Signal heatmap
  - [ ] Chart 8: Biryani House before/after timeline
  - [ ] Chart 9: Label noise vs MAE line ← **[NEW]** scientific proof
  - [ ] Chart 10: Dispatch timing comparison ← **[NEW]** operations impact
  - [ ] Chart 11: Tail risk (P95/P99) analysis ← **[NEW]**

- [ ] `dashboard/index.html` + `style.css` + `app.js` — 7 sections:
  - [ ] Section 1: Hero banner with 4 count-up animations
  - [ ] Section 2: Model comparison interactive bar chart
  - [ ] Section 3: Trust Engine live view (merchant selector + donut + weight evolution)
  - [ ] Section 4: FOR fraud analysis
  - [ ] Section 5: Archetype heatmap
  - [ ] Section 6: **[NEW]** Scenario Simulator with sliders (interactive what-if)
  - [ ] Section 7: Biryani House before/after toggle
  - [ ] Dark mode glassmorphism cards, Inter font, Zomato red + cyan theme

- [ ] **Verify Test 5:** All 11 PNGs + 7 JSONs exist

---

## 📦 DAY 4 — Saturday, March 15 (Morning)

### ALL TEAM

- [ ] PPT Slides review + polish (Shivam leads)
  - [ ] Slide: Problem — Machine OK, data bad (70% FOR fails)
  - [ ] Slide: Cost — ₹100-200 Cr/year wasted
  - [ ] Slide: System diagram — 5 signals, 3 tiers
  - [ ] Slide: Label Noise Experiment chart (Chart 9) — scientific proof ← **[NEW]**
  - [ ] Slide: Simulation results — 4-model comparison
  - [ ] Slide: Biryani story (before/after)
  - [ ] Slide: Phase 1 = ₹0, day-1 deployable
  - [ ] Slide: Failure modes (honest acknowledgment builds credibility)

- [ ] Record a backup video of full demo (Shivam) ← **CRITICAL backup**
- [ ] Mock Q&A session — one person plays aggressive judge
  - [ ] Rishi defends: circularity, Trust Engine logic, system architecture
  - [ ] Ritesh defends: simulation math, P90 numbers, label noise proof
  - [ ] Shivam defends: business impact, ₹170 Cr, customer ETA volatility

- [ ] Pre-presentation setup:
  - [ ] Test `run_demo.py` on final machine — verify < 30 sec
  - [ ] Open `dashboard/index.html` in Chrome — verify all charts load
  - [ ] PPT + Terminal + Dashboard all pre-opened as browser tabs/windows
  - [ ] Wired LAN preferred, mobile hotspot as backup

---

## 🗂️ File Completion Checklist

| File | Owner | Status |
|------|-------|--------|
| `config.py` | Ritesh | `[ ]` |
| `queue_model.py` | Ritesh | `[ ]` |
| `data_generator.py` | Ritesh | `[ ]` |
| `dwell_decomposition.py` | Ritesh | `[ ]` |
| `for_validator.py` | Ritesh | `[ ]` |
| `gaming_detector.py` | Ritesh | `[ ]` |
| `trust_engine.py` | Rishi | `[ ]` |
| `kitchenpulse_score.py` | Rishi | `[ ]` |
| `label_noise_experiment.py` | Rishi | `[ ]` |
| `dispatch_simulator.py` | Ritesh | `[ ]` |
| `explainability.py` | Rishi | `[ ]` |
| `evaluate.py` | Rishi | `[ ]` |
| `scenario_simulator.py` | Rishi | `[ ]` |
| `visualize.py` (11 charts) | Shivam | `[ ]` |
| `run_demo.py` | All | `[ ]` |
| `dashboard/index.html` | Shivam | `[ ]` |
| `dashboard/style.css` | Shivam | `[ ]` |
| `dashboard/app.js` | Shivam | `[ ]` |
| PPT Slides | Shivam | `[ ]` |
| Backup Video | Shivam | `[ ]` |

---

## 🔑 Key Numbers — Memorize These

| Number | Context |
|--------|---------|
| **70%** | FOR button events unreliable (cite: FOR fail rate analysis) |
| **2 million** | Zomato orders per day |
| **300,000+** | Restaurants on Zomato |
| **7–12 min** | Current avg rider wait time (industry data) |
| **₹170 Cr/year** | Conservative annual savings (30% realization) |
| **9%** | How much FOR actually improved Zomato's model (their own blog) |
| **P90 ↓50%** | 14.1 min → 7.1 min — the hero number |
| **MAE ↓45%** | 6.2 min → 3.4 min |
| **₹0** | Cost of Phase 1 — pure backend, no hardware |
| **5 signals, 3 tiers** | KitchenPulse architecture |
| **60%** | Max weight cap per signal |
| **<5 MB** | AKAI TFLite model size |
| **100% on-device** | AKAI audio processing |
| **Phase 1 = 4 weeks** | Time to see impact after deployment |

---

## 🎤 Q&A Defense Assignments

| Question | Owner | Key Answer |
|----------|-------|------------|
| Why is FOR unreliable? | Ritesh | 70% failure modes, Zomato's own 9% improvement evidence |
| Isn't dwell circular logic? | Rishi | Calibrate on honest-FOR merchants first → breaks circularity |
| What if merchants game dwell? | Ritesh | gaming_detector.py + <2% will try + GPS anomaly detection |
| Why not just improve the ML model? | Rishi | Problem statement says "improve signals." Garbage in → garbage out. |
| What's the cost of Phase 1? | Shivam | ₹0. Pure backend. No merchant action needed. |
| What if all 5 signals fail? | Rishi | Trust Engine shows uncertainty buffer (20-35 min range), honest communication |
| IoT cameras are better? | Shivam | ₹1,500 Crore for 3L restaurants vs ₹0. India runs on cash, not IoT. |
| Why not add more signals? | Rishi | 5 is the right scope. Diminishing returns. Judges need to understand it in 10 sec. |
| How do you handle cold start? | Rishi | Neighborhood learning from nearby same-cuisine restaurants + archetype priors |

---

## 🏆 Core Message (Say This Every Time)

> *"The model isn't the problem. The training signal is. We don't fix the ML architecture — we fix the data it learns from. That's the highest-ROI intervention available to Zomato today."*
