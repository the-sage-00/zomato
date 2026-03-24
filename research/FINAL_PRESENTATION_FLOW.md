# 🎤 KitchenPulse — FINAL Presentation Flow (7:30)

> **3 Presenters** | **PPT (10 slides) → Terminal → Dashboard** | Smooth handoffs  
> Matches your actual PDF exactly.

---

## 👥 Role Assignment

| Person | Time | Coverage |
|--------|------|----------|
| **Rishi** | 0:00 – 2:40 | PPT Slides 1–7 (Title → Problem → FOR Pie → Why This Matters → Impact → Can't Zomato → Our Approach + Signals) |
| **Ritesh Kumar** | 2:40 – 4:30 | PPT Slide 8 (Trust Engine intro) → Terminal Demo → PPT Slide 9 (Simulation Dashboard transition) |
| **Shivam Pareek** | 4:30 – 7:30 | Dashboard Deep-Dive (Trust Engine visualization, Results, Biryani Story, Science, Business Impact, Close) |

---

## 🔴 PART 1 — RISHI (0:00 – 2:40) | PPT Only

> **Where:** PPT fullscreen  
> **Role:** Storyteller. Hook the judges. Build the problem. Set up the solution.

---

### 📌 Slide 1 — Title (0:00 – 0:15) ⏱️ 15 sec

> **On screen:** "KitchenPulse — Multi-Signal Kitchen Load Estimation for KPT Prediction"

**Say:**
> "Good [morning/afternoon], judges. We are Team Escape. Our project is **KitchenPulse**. And our thesis is one line: we don't replace Zomato's model — **we clean the data it trains on.**"

➡️ *Next Slide*

---

### 📌 Slide 2 — THE PROBLEM (0:15 – 0:30) ⏱️ 15 sec

> **On screen:** Bold "THE PROBLEM" with Zomato rider illustration

**Say:**
> "Imagine you order biryani. App says 25 minutes. Then 32. Then 28. Then 35. You close the app frustrated. This happens to **millions** of orders every day. The obvious fix — build a better model. But we discovered something different."

➡️ *Next Slide*

---

### 📌 Slide 3 — FOR Button: 70% of data is a lie (0:30 – 1:10) ⏱️ 40 sec

> **On screen:** Big pie chart — Rider-Triggered 35%, Lazy Press 18%, Missing 12%, Other 5%, Honest 30%

**Say:**
> "Zomato trains its model on the **FOR button** — Food Order Ready. Restaurants press this when food is supposedly ready. But look at this data."
>
> *(Point at chart)*
>
> "Only **30% are honest**. 35% press it only when the rider arrives — that's **rider-triggered fraud**. The system thinks food took less time than it actually did. 18% press it late because they forget. 12% never press it at all."
>
> "So **70% of the ground truth Zomato trains on is a lie.** That's 1.4 million wrong training labels. Every. Single. Day."

➡️ *Next Slide*

---

### 📌 Slide 4 — WHY THIS MATTERS? (1:10 – 1:20) ⏱️ 10 sec

> **On screen:** Bold "WHY THIS MATTERS?" — visual transition slide

**Say:**
> "So what happens when you train on lies?"

➡️ *Next Slide (immediately — this is a transition)*

---

### 📌 Slide 5 — The Problem Details (1:20 – 2:00) ⏱️ 40 sec

> **On screen:** "Zomato's ML model is **fine**. The **data it trains on** is broken." + 3 impact cards + quote at bottom

**Say:**
> "The model is fine. The data is broken. And that causes three real-world disasters."
>
> *(Point to each card:)*
>
> "**KPT Underestimated** — model thinks food takes 10 minutes, actually takes 25. Rider arrives too early, waits 15 minutes doing nothing. That costs **₹12-15 per idle rider.**"
>
> "**KPT Overestimated** — model thinks 30 minutes, actually 15. Rider dispatched late, food sits cooling. Customer gets cold food. **1-star review.**"
>
> "**ETA Volatility** — customer sees 25→32→28→35 minutes. Trust erodes completely. Cancellations rise. **2 lakh orders per day affected.**"
>
> *(Point to the quote at the bottom)*
> "**A perfect model trained on wrong labels produces wrong predictions. This is a data problem, not a model problem.**"

➡️ *Next Slide*

---

### 📌 Slide 6 — CAN'T ZOMATO SOLVE THIS!! (2:00 – 2:20) ⏱️ 20 sec

> **On screen:** Bold "CAN'T ZOMATO SOLVE THIS !!" with neural network visuals

**Say:**
> "The natural question — can't Zomato already solve this? They've tried. Multiple model architectures, bigger neural nets, more parameters. But here's the truth — **no model architecture can fix wrong labels.** The problem isn't the model complexity. It's the data quality. And the hackathon itself says: **improve signals, not models.** That's exactly what we do."

➡️ *Next Slide*

---

### 📌 Slide 7 — Our Solution: 5 Signals > 1 Button (2:20 – 2:35) ⏱️ 15 sec

> **On screen:** "KitchenPulse: **5 Signals > 1 Button**" — 3 tier cards + Dwell Decomposition + ₹0 cost badge

**Say:**
> "KitchenPulse uses **5 independent signals** instead of one unreliable button. **Tier 1 — zero cost** — Corrected Dwell Time from rider GPS plus Smart FOR Validation. **Tier 2** — Merchant Behavior patterns and AKAI audio sensing. **Tier 3** — External busyness from Google."
>
> *(Point at Dwell Decomposition bar)*
> "We decompose the raw GPS dwell time, subtract parking, approach, and handoff — and extract the pure **kitchen wait**. Phase 1 costs **₹0** — it uses data Zomato already collects."

🔁 **HANDOFF to Ritesh:**
> "Now Ritesh will explain the brain behind this — the Trust Engine — and show you our live simulation."

---

## 🟡 PART 2 — RITESH KUMAR (2:35 – 4:30) | PPT → Terminal → PPT

> **Where:** PPT Slide 8 → Alt-Tab to Terminal → PPT Slide 9  
> **Role:** Technical credibility. Show the system works.

---

### 📌 Slide 8 — THE TRUST ENGINE (2:35 – 3:15) ⏱️ 40 sec

> **On screen:** Bold "THE TRUST ENGINE" — visual transition slide

**Say:**
> "This is the brain of KitchenPulse — **the Adaptive Trust Engine**. Every restaurant gets **its own signal weights.** These weights update automatically every 50 orders."
>
> "If a restaurant presses FOR honestly — the system trusts it, weight stays high. If a restaurant always games the button — the system detects it and **stops believing it.** FOR weight drops from 0.40 to 0.15. Dwell Time takes over."
>
> "**The system figures out the restaurant lies — and stops believing it.** No human touches this. Fully automated, per-restaurant learning."
>
> *(Pause)*
> "For new restaurants with no history, we use **peer learning** — we start with weights from similar restaurant types. After 200 orders, the system has its own personalized weights."
>
> "Shivam will show you the exact visualization of this on our dashboard. But first — let me prove the system works."

---

### 💻 Terminal Demo (3:15 – 3:55) ⏱️ 40 sec

> ➡️ **ALT-TAB to Terminal** (pre-typed command ready)

**Say:**
> "Let me run our full simulation live. 3 lakh orders, 1,000 merchants, all 4 restaurant archetypes."

*(Run:)*
```
python simulation/run_demo.py
```

*(While it runs, narrate over the scrolling output:)*
> "The system is generating realistic order data using M/D/1 queueing models, decomposing dwell times, running the Trust Engine to catch FOR fraud across all merchants, and evaluating 4 model variants — Baseline, Dwell-Corrected, KP-Lite, and KP-Full."

*(When results appear:)*
> "Results are in. You can see MAE dropping 16%, P90 worst-case error dropping 31%. The simulation proves our approach mathematically. Now let me show you where all of this comes alive."

---

### 📌 Slide 9 — SIMULATION DASHBOARD (3:55 – 4:00) ⏱️ 5 sec

> ➡️ **ALT-TAB back to PPT** → Show Slide 9

**On screen:** Bold "SIMULATION DASHBOARD"

**Say:**
> "And now — Shivam will walk you through our interactive dashboard."

🔁 **HANDOFF to Shivam:**
> "Shivam, take it from here."

---

## 🟢 PART 3 — SHIVAM PAREEK (4:00 – 7:30) | Dashboard Only

> **Where:** Dashboard fullscreen in browser  
> **Role:** Visual proof. Walk through every key chart. Close strong.

---

### ➡️ ALT-TAB to Dashboard (already open, pre-scrolled to Trust Engine section)

---

### 🧠 Trust Engine Visualization (4:00 – 4:50) ⏱️ 50 sec

> **On screen:** Trust Weight Evolution Chart (Dashboard Ch 4)

**Say:**
> "This is the Trust Engine in action — live visualization."

*(Click on a Dine-in / gaming merchant button)*
> "Watch this dine-in restaurant. At order 1, default weights — FOR at 40%, Dwell at 20%. These are archetype priors."
>
> "By order 50, the system detects FOR is being pressed 8 seconds after rider arrival. **That's not food ready — that's rider-triggered.** FOR weight starts dropping."
>
> "By order 200 — **stable.** FOR is at 15%, Dwell has risen to 47%. The system **healed its own data source.**"

*(Click on an honest Cloud Kitchen merchant for contrast)*
> "Compare this cloud kitchen — FOR stays high at 35% because they're honest. **Each restaurant gets its own trust profile.**"

*(Point at Stacked Bar — Signal Weights by Archetype)*
> "And here — the average weight distribution per type. Cloud kitchens trust FOR. Dine-in trusts Dwell. Street food relies heavily on behavioral signals. One-size-fits-all doesn't work."

---

### 📊 Results (4:50 – 5:25) ⏱️ 35 sec

> **Scroll to:** Results section (Dashboard Ch 5)

**Say:**
> "Now the proof. 3 lakh orders. 1,000 merchants."

*(Point at P90 bar chart — THE hero metric)*
> "P90 — the worst 10% of orders. Baseline with just FOR: **23 minutes of error.** With Dwell Correction: **16 minutes. That's a 31% reduction.** These are the orders that cause refunds and 1-star reviews."

*(Point at MAE bar chart)*
> "Average error: 7.2 down to 6.0 — **16% improvement.**"

*(Point at P95/Tail Risk quickly)*
> "And P95 — the absolute worst — drops from **31 to 24 minutes.** Seven minutes saved on the worst orders."

---

### 🍗 Biryani Story (5:25 – 6:05) ⏱️ 40 sec

> **Scroll to:** Biryani Story section (Dashboard Ch 6)

**Say:**
> "Let me make this real with ONE order."
>
> "Friday night, 8:15 PM. Customer orders biryani from a busy dine-in restaurant. Kitchen has 12 walk-in customers, 4 Swiggy orders, 3 Zomato orders. But Zomato only sees its 3."

*(Point at LEFT panel — WITHOUT KitchenPulse)*
> "**Without KitchenPulse:** System predicts 20 minutes, dispatches rider early. Rider arrives and **waits 25 minutes.** ETA changes 3 times. 1-star review. Prediction error: **25 minutes.**"

*(Point at RIGHT panel — WITH KitchenPulse)*
> "**With KitchenPulse:** Trust Engine knows this merchant's FOR is unreliable. Uses dwell + behavior instead. Predicts **43 minutes.** Actual: 45 minutes. Rider waits just **2 minutes.** That's **92% error reduction** on a single order."

*(Point at Rider Wait bar chart)*
> "Across ALL orders — rider wait drops **40%.** From 1.4 minutes to 0.86 minutes average."

---

### 🔬 The Science (6:05 – 6:25) ⏱️ 20 sec

> **Scroll to:** Label Noise Experiment (Dashboard Ch 7)

**Say:**
> "Here's the mathematical proof. Same ML model, trained on data with increasing label noise — 0% to 80%. As noise increases, error rises linearly. **Bad FOR data = bad predictions.** No model can overcome wrong training labels. You have to **fix the data.**"

---

### 💰 Business Impact + Close (6:25 – 7:00) ⏱️ 35 sec

> **Scroll to:** Business Impact (Dashboard Ch 8) *OR* stay on dashboard and summarize

**Say:**
> "Three things make this **practical.**"
>
> "**Zero cost.** Everything we need already exists — rider GPS, FOR timestamps, merchant behavior. Zero hardware. Zero merchant training. Zero app changes. **Pure backend patch.**"
>
> "**Real impact.** Worst-case rider wait drops **31%.** Estimated annual savings: **₹170 crore.**"
>
> "**Easy deployment.** Shadow mode first, then 5% A/B test, then full rollout. We don't replace Zomato's model. We give it **cleaner data.** The model improves automatically."

---

### 🎬 Final Line (7:00 – 7:15) ⏱️ 15 sec

> ➡️ **ALT-TAB to PPT Slide 10** (Q n A / THANK YOU)

*(Pause. Look at judges.)*

> "We are not building Zomato a new brain."

*(Pause)*

> "We are cleaning the lies that the current brain is learning from."

*(Final line — SLOWLY)*

> **"Fix the labels — and the model fixes itself."**
>
> "Thank you. We're Team Escape. Ready for questions."

---

## ⏱️ Complete Timeline

| Time | Slide | Presenter | What Happens |
|------|-------|-----------|-------------|
| 0:00 | Slide 1 — Title | Rishi | Brand intro, thesis statement |
| 0:15 | Slide 2 — THE PROBLEM | Rishi | Biryani ETA story hook |
| 0:30 | Slide 3 — FOR Pie Chart | Rishi | 70% lie, pie chart walkthrough |
| 1:10 | Slide 4 — WHY THIS MATTERS | Rishi | 2-sec transition |
| 1:20 | Slide 5 — Impact Details | Rishi | 3 cards: underestimated, overestimated, volatility |
| 2:00 | Slide 6 — CAN'T ZOMATO SOLVE | Rishi | Neural nets won't fix bad data |
| 2:20 | Slide 7 — Our Solution (5 Signals) | Rishi | Signal tiers + dwell decomposition |
| 2:35 | **HANDOFF → Ritesh** | — | — |
| 2:35 | Slide 8 — THE TRUST ENGINE | Ritesh | Trust Engine mechanics + peer learning |
| 3:15 | **TERMINAL** | Ritesh | `python simulation/run_demo.py` |
| 3:55 | Slide 9 — SIMULATION DASHBOARD | Ritesh | Transition slide |
| 4:00 | **HANDOFF → Shivam** | — | — |
| 4:00 | Dashboard: Trust Engine | Shivam | Weight evolution chart, archetype bars |
| 4:50 | Dashboard: Results | Shivam | P90, MAE, P95 bar charts |
| 5:25 | Dashboard: Biryani Story | Shivam | Before/after timeline, rider wait |
| 6:05 | Dashboard: Science | Shivam | Label noise experiment |
| 6:25 | Dashboard: Business Impact | Shivam | ₹0 cost, ₹170Cr savings, deployment |
| 7:00 | Slide 10 — Q n A | Shivam | Final line + thank you |
| **~7:15** | | | **END → Q&A begins** |

---

## 🔁 Transition Choreography

### Transition 1: Rishi → Ritesh (at ~2:35)
- **Rishi says:** "Now Ritesh will explain the brain behind this — the Trust Engine — and show you our live simulation."
- **Ritesh:** Steps forward, clicks to Slide 8
- **Screen:** PPT stays fullscreen

### Transition 2: Ritesh → Shivam (at ~4:00)
- **Ritesh:** Quickly shows Slide 9 ("SIMULATION DASHBOARD") as a bridge
- **Ritesh says:** "Shivam, take it from here."
- **Shivam:** Takes over, ALT-TABs to pre-opened Dashboard
- **Screen:** Terminal → PPT Slide 9 (2 sec) → Dashboard (fullscreen)

### Transition 3: Shivam → Close (at ~7:00)
- **Shivam:** ALT-TABs back to PPT Slide 10 (Q n A)
- Delivers the final line

---

## 🖥️ Screen Flow

```
PPT Slide 1 → 2 → 3 → 4 → 5 → 6 → 7          [RISHI]
                                    ↓
                              PPT Slide 8        [RITESH]
                                    ↓
                              TERMINAL            [RITESH]
                                    ↓
                              PPT Slide 9         [RITESH → handoff]
                                    ↓
                              DASHBOARD            [SHIVAM]
                              (Ch4 → Ch5 → Ch6 → Ch7 → Ch8)
                                    ↓
                              PPT Slide 10         [SHIVAM → close]
```

---

## ✅ Pre-Presentation Checklist

- [ ] PPT open fullscreen, on Slide 1
- [ ] Terminal open with `python simulation/run_demo.py` typed (NOT yet entered)
- [ ] Dashboard open in Chrome, scrolled to Trust Weight Evolution chart (Ch 4)
- [ ] All 3 presenters know their handoff cues
- [ ] Timer visible (phone on table or watch)
- [ ] Practice the full ALT-TAB sequence: PPT → Terminal → PPT → Dashboard → PPT at least 3x
- [ ] Test audio/projector connection

---

## 🔑 Three Lines Judges Will Remember

1. **"The model isn't broken. The data is."** — Rishi (Slide 5)
2. **"The system figured out the restaurant lies — and stopped believing it."** — Ritesh (Slide 8)
3. **"Fix the labels. The model fixes itself."** — Shivam (Closing)
