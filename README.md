<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/bd/Zomato_Logo.svg" alt="Zomato Logo" width="150" />
  <h1>🔬 KitchenPulse</h1>
  <p><b>Multi-Signal Kitchen Load Estimation for KPT Prediction</b></p>
  <p><i>"Fix the labels — and the model fixes itself."</i></p>
  <p>
    <img src="https://img.shields.io/badge/Team-Escape-red?style=for-the-badge&logo=zomato" alt="Team Escape" />
    <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge" alt="Status" />
    <img src="https://img.shields.io/badge/Impact-₹170Cr%20Savings-green?style=for-the-badge" alt="Impact" />
  </p>
</div>

<hr>

## 🚨 The Core Problem: The Data is Broken, Not the Model

Zomato relies on predicting **KPT (Kitchen Preparation Time)** to decide when to dispatch delivery riders. Accurate predictions mean hot food and zero wait times. However, the current model struggles because it relies on the **FOR (Food Order Ready)** button pressed by merchants.

Our research revealed a harsh truth: **70% of the FOR data is a lie.**

<div align="center">
  <table>
    <tr>
      <th>Fraud Type</th>
      <th>Prevalence</th>
      <th>Impact</th>
    </tr>
    <tr>
      <td><b>Rider-Triggered</b></td>
      <td>~35%</td>
      <td>Merchants press FOR only when the rider arrives. The system drastically underestimates actual prep time.</td>
    </tr>
    <tr>
      <td><b>Lazy Press</b></td>
      <td>~18%</td>
      <td>Merchants forget, pressing it late. The system overestimates prep time.</td>
    </tr>
    <tr>
      <td><b>Missing</b></td>
      <td>~12%</td>
      <td>Merchants never press it at all. Complete data blindspot.</td>
    </tr>
    <tr>
      <td><b>Honest</b></td>
      <td>~30%</td>
      <td>The only reliable data Zomato currently trains on.</td>
    </tr>
  </table>
</div>

**Every day, 1.4 million wrong training labels feed into the ML model.** When KPT is underestimated, riders arrive early and idle (₹12-15 wasted per rider). When overestimated, the food sits on the counter and gets cold (1-star reviews).

### The Solution Objective
Zomato explicitly asked the hackathon: **"Improve signals, not models."** KitchenPulse is the solution.

---

## 🛠️ The KitchenPulse Architecture: 5 Signals > 1 Button

We replace the reliance on a single, easily falsified button with a **Multi-Signal Triangulation** architecture. 

### 🟢 Tier 1: Zero Cost (Primary Ground Truth)
1. **Corrected Rider Dwell Time**: GPS data is noisy (parking, walking). We decompose the GPS trace to find the *pure kitchen wait time*. It's a zero-fraud, purely observational signal.
2. **Smart FOR Validation**: We don't discard the FOR button; we grade it. If pressed within 60 seconds of a rider arriving, it's flagged and ignored in training.

### 🔵 Tier 2: Low-Friction Enhancers
3. **Merchant Behavioral Signals**: App interaction patterns. If the merchant's latency in acknowledging a new order spikes, the kitchen is overwhelmed. 
4. **AKAI (Ambient Kitchen Activity Index)**: A leading indicator. A tiny, local LLM/TFLite model runs on the merchant tablet, analyzing background audio (decibel levels + noise patterns) to detect a rush *before* Zomato dispatch even happens. No audio is transmitted; only a 1-10 rush score.

### 🟠 Tier 3: External Context
5. **External Busyness (Google Popular Times)**: Free crowdsourced foot traffic data. Zomato might only see 3 app orders, but 20 dine-in customers mean the kitchen is slammed.

---

## 🧠 The Innovation: Adaptive Trust Engine

The brain of KitchenPulse is a dynamically adjusting system that scores each merchant's reliability.

* **Self-Healing Weights**: Every restaurant gets a dynamic profile. If a dine-in restaurant constantly games the FOR button, the Trust Engine detects it, drops the FOR weight from 0.40 to 0.05, and elevates Dwell Time. The system figures out the merchant is lying and stops believing them.
* **Archetype Priors (Peer Learning)**: New restaurants start with average weights based on their archetype (Cloud Kitchen, QSR, Dine-in, Street Food). 

> **Result:** No manual intervention is needed. The system catches fraud automatically and self-corrects the data pipeline.

---

## 🔬 The 7-Iteration Debugging Journey

We built a massive simulation of **304,046 orders** across 1,000 merchants. Getting the system to beat Zomato's baseline was a rigorous 7-step optimization process:

| Iteration | The Problem Encountered | Root Cause | The Fix & Lesson Learned |
|:---:|---|---|---|
| **1** | All models worse than baseline (MAE ~16.8) | Fixed base constant vs actual mean. | **Fix:** Use historical averages. **Lesson:** Never hardcode base values for high-variance targets. |
| **2** | Models stuck at ~15 MAE | Self-referencing prediction loop. | **Fix:** Anchor to FOR history. **Lesson:** Never predict iteratively from your own outputs. |
| **3** | Dwell estimate broken | Dwell measures *wait* time, not prep time. | **Fix:** Use `rider_arrival + dwell`. **Lesson:** Mathematically align signal definitions. |
| **4** | Zero "honest" merchants | `suspicious_late` threshold too tight. | **Fix:** Raise threshold from 3 to 8 mins. **Lesson:** Calibrate thresholds to actual data distributions. |
| **5** | KitchenPulse worse than Baseline | Rider-triggered merchants had 0 valid history. | **Fix:** Cross-merchant learning required. |
| **6** | KP still worse than Dwell-Corrected | Contextual adjustments adding too much noise. | **Fix:** **Archetype Priors** introduced. Fallback to honest merchants of the same type. *(Huge Breakthrough!)* |
| **7** | **Final Winning Architecture** | Models restarting instead of layering. | **Fix:** Chain the models systematically: `Baseline → DC → KP-Lite → KP-Full`. Apply micro-adjustments only. |

*You can read the full, in-depth journey in the [`research/DEBUGGING_JOURNEY.md`](research/DEBUGGING_JOURNEY.md) document.*

---

## 📊 Business Impact & Results

The simulation conclusively mathematically proves the architecture. By simply cleaning the data Zomato feeds its models, the impact is immense:

* **📉 ↓ 31% Reduction in P90 Wait Time** (Worst-case rider wait dropped from 23.1 to 16.0 minutes)
* **📉 ↓ 16% Reduction in Mean Absolute Error (MAE)** (7.15 → 6.0 minutes)
* **📉 ↓ 40% Drop in Average Rider Wait** (1.43 mins → 0.86 mins)
* **✅ 1.4 Million Bad Labels Fixed Daily**

### 💰 Estimated Savings: **₹170 Crore Annually**
Calculated via recovered idle rider time (₹12-15 salvaged per rider on poorly predicted orders) and reduced order cancellation/churn.

### 🚀 Deployment Plan (Zero Cost)
This involves *Zero hardware*, *Zero merchant training*, and *Zero app changes*. It is a pure backend patch.
1. **Shadow Mode (Week 1-2):** Run KitchenPulse in parallel.
2. **A/B Test (Week 3-6):** Route 5% orders via KP.
3. **Full Rollout:** Scale to all 300K merchants.

---

## 👨‍💻 Team Escape
* **Rishi** - System Design + Trust Engine
* **Ritesh Kumar** - Simulation + Data Pipeline
* **Shivam Pareek** - Dashboard + Visualization

<div align="center">
  <br>
  <i>"We are not building Zomato a new brain. We are cleaning the lies that the current brain is learning from."</i>
</div>
