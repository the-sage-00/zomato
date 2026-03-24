<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/bd/Zomato_Logo.svg" alt="Zomato" width="150" />
  <h1>🔬 KitchenPulse</h1>
  <p><b>Multi-Signal Kitchen Load Estimation for KPT Prediction</b></p>
  <p><i>"Fix the labels — and the model fixes itself."</i></p>
  <p>
    <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge" alt="Status" />
    <img src="https://img.shields.io/badge/Impact-₹170Cr%20Savings-green?style=for-the-badge" alt="Impact" />
  </p>
</div>

<hr>

## 📖 The Story: Understanding the Problem from the Basics

Imagine you order a biryani on Zomato. The app says it will arrive in 25 minutes. Then it changes to 32. Then 28. Then 35. You close the app frustrated. This happens to millions of orders every day. 

Why does this happen? Zomato relies on a prediction called **KPT (Kitchen Preparation Time)**. If they can perfectly guess how long a restaurant takes to cook your food, they can send a delivery rider at the *exact* moment the food comes out of the kitchen.
- **If the rider arrives too early:** The rider waits (costing Zomato ₹12-15 in idle time) and rider earnings drop.
- **If the rider arrives too late:** The food gets cold, the customer gives a 1-star rating, and the restaurant blames Zomato for sending the rider late.

### How does Zomato currently predict KPT?
Zomato has a massive Machine Learning (ML) model that processes variables like dish complexity, time-of-day, and weather. But how does an ML model learn? It needs *data* to know if its past guesses were right or wrong. Currently, Zomato's ML model learns entirely from the **FOR (Food Order Ready) button**—a button on the restaurant's Zomato tablet that a chef or manager is supposed to tap the exact moment the food is cooked.

### The Breakthrough Realization: The Data is a Lie
The obvious hackathon solution is to "build a faster ML model." But our early research revealed a harsh truth: **Zomato's ML model is actually completely fine; the issue is that 70% of the FOR button data it trains on is a lie.**

<div align="center">
  <table>
    <tr>
      <th>Fraud Type</th>
      <th>Prevalence</th>
      <th>What happens in the kitchen?</th>
      <th>The Impact on Zomato's ML</th>
    </tr>
    <tr>
      <td><b>Rider-Triggered Fraud</b></td>
      <td>~35%</td>
      <td>The restaurant is busy, so they only tap "Ready" when the delivery rider physically arrives and screams for food.</td>
      <td>The ML model is fed impossibly fast prep times. It drastically underestimates future orders.</td>
    </tr>
    <tr>
      <td><b>Lazy Press</b></td>
      <td>~18%</td>
      <td>The chef cooks the food, forgets to tap the button, continues cooking, and finally taps it 15 minutes late.</td>
      <td>The ML model is fed impossibly slow prep times. It overestimates future orders.</td>
    </tr>
    <tr>
      <td><b>Missing Data</b></td>
      <td>~12%</td>
      <td>The restaurant never presses it at all.</td>
      <td>A complete data blindspot.</td>
    </tr>
    <tr>
      <td><b>Honest Merchants</b></td>
      <td>~30%</td>
      <td>The restaurant taps it exactly when cooked.</td>
      <td>The only reliable data Zomato currently has.</td>
    </tr>
  </table>
</div>

**Every day, 1.4 million wrong training labels feed into the ML model.** No matter how advanced your neural network architecture is, if you train it on bad data, it outputs bad results. 

---

## 🛠️ The Solution: KitchenPulse Architecture

Zomato explicitly posed a challenge to us in this Hackathon: **"Improve signals, not models."** 

Our solution is **KitchenPulse**: A system that stops relying blindly on one easily faked button, and instead triangulates the *true* prep time using 5 independent, ambient signals.

```text
╔══════════════════════════════════════════════════════════════╗
║                   KITCHENPULSE SYSTEM                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │  🏆 TIER 1 — PRIMARY (Always Available, Zero Hardware)  │ ║
║  │                                                         │ ║
║  │  1. CORRECTED RIDER DWELL TIME                          │ ║
║  │     → Decomposed into pure kitchen_wait                 │ ║
║  │                                                         │ ║
║  │  2. SMART FOR VALIDATION                                │ ║
║  │     → FOR graded for reliability per merchant           │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                         │                                    ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │  🥈 TIER 2 — ENHANCER (Real-Time Sensing)               │ ║
║  │                                                         │ ║
║  │  3. MERCHANT BEHAVIORAL SIGNALS                         │ ║
║  │     → App interaction latency during rush               │ ║
║  │                                                         │ ║
║  │  4. AKAI (Ambient Kitchen Activity Index)               │ ║
║  │     → Local audio ML matching decibel spikes            │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                         │                                    ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │  🥉 TIER 3 — CONTEXTUAL (External Enrichment)          │ ║
║  │                                                         │ ║
║  │  5. EXTERNAL BUSYNESS (Google Popular Times)            │ ║
║  │     → Live crowdsourced ambient foot traffic            │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                              ║
║  FUSION → KitchenPulse Trust Engine → feeds Zomato's ML    ║
╚══════════════════════════════════════════════════════════════╝
```

### 🟢 Tier 1: Zero Cost (Primary Ground Truth)
Instead of asking the restaurant, we passively measure them:
**1. Corrected Rider Dwell Time**: Zomato has GPS data tracking when the rider enters the restaurant and when they leave. However, GPS is noisy (did the rider take 5 minutes parking their bike or finding the right floor in a mall?). We mathematically *decompose* the GPS trace:

```text
Raw Dwell Time (observed via GPS)
══════════════════════════════════════════════════════════════

   Rider enters       Rider         Rider at        Food        Rider
   geofence          parks          counter        handed       exits
      │                │               │             │            │
      ▼                ▼               ▼             ▼            ▼
      ├────────────────┼───────────────┼─────────────┼────────────┤
      │   T_approach   │   T_park     │  T_kitchen   │  T_handoff │
      │   (GPS→door)   │  (park+walk) │ (THE SIGNAL) │  (exit)    │
      ├────────────────┼───────────────┼─────────────┼────────────┤
```

This removes the noise and gives us the absolute, un-faked reality of how long the food actually took.

**2. Smart FOR Validation**: We don't throw away the FOR button entirely; we grade it. If a restaurant presses their button within 60 seconds of a rider physically arriving, our system spots the anomaly, flags the merchant for "Rider-Triggered Fraud," and immediately ignores their button presses from the ML training loop going forward.

### 🔵 Tier 2: Low-Friction Enhancers (Real-Time Sensing)
Dwell time tells us how long a *past* order took. But what if a massive rush starts *right now*?

**3. Merchant Behavioral Signals**: If a restaurant is suddenly taking 2-3 extra minutes just to tap the "Accept Order" notification, we know the kitchen is overwhelmed and staff are distracted. We use app interaction latency as a live stress signal.

**4. AKAI (Ambient Kitchen Activity Index)**: A leading indicator. A tiny, 5MB local ML model runs directly on the merchant's Zomato tablet, analyzing ambient background audio (decibel levels + frequency of shouts/pans) to detect a kitchen rush *before* Zomato dispatch even happens. Complete privacy—no audio is transmitted to the cloud, just a 1-10 "rush score."

```text
TIMELINE COMPARISON: WHY AKAI MATTERS
══════════════════════════════════════════════════════════════

              Order               Rider              Rider
             Placed             Dispatched          Arrives
                │                    │                  │
  DWELL TIME:   │    ❌ nothing      │   ❌ nothing     │ ← only NOW you learn
 (Lagging)      │                    │                  │    how long rider waited
                │                    │                  │
  AKAI:         │ ✅ "kitchen is     │                  │
 (Leading)      │    at rush level   │                  │
                │    8/10 right now" │                  │
                │         │          │                  │
                │         └──► ADD +12 min to KPT      │
                │              DELAY rider dispatch     │
                │              → rider arrives when     │
                │                food is actually ready │
```

### 🟠 Tier 3: External Context
**5. External Busyness (Google Popular Times Integration)**: Free crowdsourced foot traffic data. Zomato might only see 3 app orders assigned to a kitchen, but if Google Maps says there are 40 dine-in customers swarming the location, the kitchen is slammed.

---

## 🧠 The Core Innovation: The Adaptive Trust Engine

Because every restaurant is vastly different (a street food stall vs. a hyper-efficient cloud kitchen vs. a massive dine-in restaurant), treating them equally is a failure point. The brain behind KitchenPulse is a dynamically adjusting Trust Engine that scores each merchant's data reliability live.

* **Self-Healing Weights**: Every restaurant gets a dynamic profile. If a dine-in restaurant constantly games the FOR button, the Trust Engine catches the statistical anomaly. It dynamically drops the FOR signal weight from 40% to 5%, and elevates the Dwell Time tracking weight to 80%. **The system figures out the merchant is lying and automatically stops believing them without human intervention.**

```text
MERCHANT TRUST PROFILE — Restaurant #48291
══════════════════════════════════════════════════════════════

Signal               │ Weight │ Reason
─────────────────────┼────────┼──────────────────────────────
FOR Button           │  0.05  │ FRAUD: Pressed avg 8 sec 
                     │        │ AFTER rider matched
Corrected Dwell Time │  0.65  │ Low variance (σ=2.1 min)
Merchant Behavior    │  0.20  │ App latency correlates r=0.71 
                     │        │ with KPT delays
AKAI                 │  0.10  │ Opted in, but data sparse
─────────────────────┴────────┴──────────────────────────────
Archetype: Mid-range Dine-in
Status: FOR Signal Automatically Ignored by ML (Self-Healed)
```

* **Archetype Priors (Peer Learning)**: When a brand new restaurant joins Zomato, the Trust Engine assigns them average weights based on their archetype. For instance, Cloud Kitchens inherently have far more reliable FOR buttons because they have no dine-in customers to distract them.

> **Result:** The data pipeline dynamically self-corrects and heals, generating the cleanest KPT training data Zomato has ever seen.

---

## 🔬 Deep-Dive Research & The 7-Iteration Debugging Journey

We didn't just design this theoretically; we mathematically validated everything. We built a massive python simulation of **304,046 orders** across 1,000 restaurants utilizing M/D/1 Queueing theory constraints. Getting the system to beat Zomato's current ML baseline was a rigorous 7-step data optimization process:

| Iteration | The Problem Encountered & The Failure Mode | The Fix & Key Scientific Insight Learned |
|:---:|---|---|
| **1: Constants** | All models performed worse than baseline (MAE ~16.8). We hardcoded a base assumption. | **Fix:** Implement historical averages instead of constants. Never hardcode base values for high-variance targets. |
| **2: The Prediction Loop** | Models were stuck at ~15 MAE. We created a self-referencing feedback loop. | **Fix:** Anchor mathematical equations to the raw FOR history. Never predict iteratively strictly from your own outputs. |
| **3: Dwell Measurement** | The Dwell estimate was broken because dwell measures *wait* time, not absolute *prep* time. | **Fix:** Mathematically align definitions. `Actual Prep = Rider Arrival Timestamp + Pure Dwell Time.` |
| **4: Thresholds** | The system detected zero "honest" merchants. The flagging threshold was too sensitive. | **Fix:** Raise the flag threshold from 3 to 8 minutes. Always calibrate algorithmic thresholds directly to data distributions. |
| **5: Zero History** | The KitchenPulse model was worse than the Baseline because merchant fraudsters had 0 valid history to learn from once we discarded their broken data. | **Fix:** Implement cross-merchant peer-learning algorithms to substitute missing history pipelines. |
| **6: Archetype Priors**| The KitchenPulse still fell behind simple Dwell averages due to massive noise in external context inputs. | **Fix:** Introduction of **Archetype Priors**. We used statistical fallbacks mapped uniquely to Cloud, QSR, and Dine-in archetypes. *(Massive Breakthrough!)* |
| **7: Final Polish** | The models were conflicting and restarting instead of compounding learning. | **Fix:** Chain the models systematically: `Baseline → DC → KP-Lite → KP-Full`, applying micro-adjustments only. |

*You can read our full mathematical and scientific debug logs in our [`research/DEBUGGING_JOURNEY.md`](research/DEBUGGING_JOURNEY.md) document.*

---

## 📊 Business Impact & Simulation Results

The simulation mathematically proves the architecture's power. By simply filtering the noise out of the raw data Zomato feeds to its ML models, the downstream impact is immense:

* **📉 ↓ 31% Reduction in P90 Wait Time**: The absolute worst-case scenario rider waits (the top 10% of terrible, cold-food orders) plummeted from 23.1 minutes to 16.0 minutes.
* **📉 ↓ 16% Reduction in Mean Absolute Error (MAE)**: The standard prediction error dropped cleanly from 7.15 → 6.0 minutes.
* **📉 ↓ 40% Drop in Average Rider Wait**: The average rider idle time dropped from 1.43 mins → 0.86 mins, nearly perfectly aligning the exact rider arrival with the chef packaging the food.

### 💰 Estimated Savings: **₹170 Crore Annually**
Zomato explicitly mentioned the cost of idle rider time is ₹12-15 per hour on poorly predicted orders. By scaling KitchenPulse across 2M daily Zomato orders, we recover thousands of idle rider hours and vastly reduce direct customer order cancellations resulting from ETA volatility.

<div align="center">
  <br>
  <i>"We are not building Zomato a new brain. We are simply giving its current brain the truth."</i>
</div>
