# 🎤 KitchenPulse — Stage Script
> **What you actually say on stage. Natural, spoken English.**
> Total time: ~7:30 minutes

---

## ⏱️ 0:00 – 1:15 | The Hook — The Problem

*(Start confidently)*

Imagine you open Zomato and order biryani.
The app says 25 minutes.
After five minutes it changes to 32 minutes.
Then 28. Then 35.
At that point you just close the app, frustrated.

*(Pause)*

This is not rare.
This happens to millions of orders every day.

The obvious idea would be:
build a better machine learning model.

More data.
More features.
Bigger model.

*(Pause)*

But when we studied the system carefully,
we discovered something surprising.

*(Speak slowly)*

**The model is not broken.
The data is broken.**

Zomato trains its kitchen preparation model using one signal —
the **FOR button**.

FOR means Food Order Ready.

Restaurants press this button when the food is ready.

And the system treats that timestamp as the ground truth.

*(Pause)*

But the problem is —
most restaurants press this button incorrectly.

*(Show slide)*

Around **35%** press it only when the rider arrives.
So the system thinks the food took less time than it actually did.

Around **18%** press it late because they forget.

**12%** never press it at all.

Only about **30%** press it correctly.

*(Pause)*

So the system is learning from wrong answers.

And if your training data is wrong,
your predictions will also be wrong.

*(Speak slowly)*

**Bad data in.
Bad predictions out.**

---

## ⏱️ 1:15 – 2:15 | Why This Matters

Zomato processes around **2 million orders** every day.

If 70% of those labels are wrong,
that means **1.4 million wrong training examples** every single day.

**First problem — riders wait**

If the system predicts food will be ready earlier,
it sends the rider too soon.

The rider arrives at the restaurant
and waits 7 to 12 minutes doing nothing.

Multiply that across thousands of orders —
and it costs Zomato **hundreds of crores** every year.

**Second problem — ETA keeps changing**

Customers see the delivery time changing again and again.

25 minutes. 32 minutes. 28 minutes.

Customers lose trust.

And when trust breaks,
they switch to Swiggy.

**Third problem — food gets cold**

If the system predicts too late,
the rider arrives late.

The food waits on the counter.

Customer receives cold food
and leaves a **1-star review**.

*(Pause)*

Today, in the worst 10% of orders,
riders wait more than **14 minutes**.

These are exactly the orders that create bad experiences.

---

## ⏱️ 2:15 – 4:00 | The Solution — KitchenPulse

So our approach is simple.

*(Speak clearly)*

**We don't replace Zomato's model.
We clean the data that goes into it.**

Instead of trusting only one button,
our system looks at **five different signals**.

Then it learns which signals are reliable
for each restaurant.

We call this system **KitchenPulse**.

---

### Signal 1 — Rider Dwell Time

When the rider reaches the restaurant,
the GPS shows how long they stayed there.

That time tells us how long the rider waited for food.

But raw dwell time also includes:
parking, walking to the restaurant, and handing over the order.

So we subtract those parts.

After removing that noise,
we get a good estimate of how long food was actually not ready.

*(Pause)*

And unlike the FOR button,
**GPS cannot be gamed easily**.

*(Say this clearly)*

The FOR button has **systematic bias**.
It is wrong in the same direction again and again.

GPS dwell time has **random noise**.

Random noise cancels out across many orders.
**Bias does not.**

---

### Signal 2 — FOR Trust Score

We do not completely ignore the FOR button.

Instead, we **score how trustworthy** it is.

If the FOR button is pressed within two minutes of rider arrival,
it is probably rider-triggered. We flag that.

Over time each restaurant gets a **trust score**.

---

### Signal 3 — Merchant Behavior

We also look at how fast the merchant accepts the order.

If they take longer to tap Accept Order,
their kitchen is probably busy.

That signal already exists in Zomato's data.

---

### Signal 4 — AKAI

AKAI stands for **Ambient Kitchen Activity Index**.

The restaurant tablet measures how loud the kitchen is.

Not speech. Only noise level.

A louder kitchen usually means the kitchen is busy.

And this signal tells us **before** we even send the rider.

---

### Signal 5 — External Busyness

Finally we use **Google Popular Times**.

This tells us if the restaurant is crowded.

Zomato might see only 3 orders.
But the restaurant might have 20 dine-in customers.

Google data helps us see that **hidden demand**.

---

### The Trust Engine

*(Now explain the key innovation)*

KitchenPulse learns **which signals to trust**.

Every restaurant gets its own trust weights.

These weights update automatically
as more orders happen.

If a restaurant presses the FOR button honestly,
the system trusts it.

If a restaurant always games the button,
the system slowly stops believing it.

*(Speak slowly)*

**The system figures out the restaurant lies —
and stops believing it.**

---

### Handling New Restaurants

For brand new restaurants with no history,
we use **peer learning**.

We look at similar restaurants
and use their average prep time as a starting point.

Then as more orders happen,
the system learns the real pattern.

---

## ⏱️ 4:00 – 4:45 | The Breakthrough

One big challenge was restaurants that **always** game the FOR button.

Their own data can never teach us the truth.

So instead we learn from honest restaurants of the same type.

That single change reduced our prediction error by **16%**
and reduced worst-case rider wait by **30%**.

---

## ⏱️ 4:45 – 6:15 | Demo Story

Let me show you one example.

**Friday night. 8:15 PM.**
A customer orders biryani from a dine-in restaurant.

The kitchen currently has:
- 12 dine-in customers
- 4 Swiggy orders
- 3 Zomato orders

But Zomato only sees the 3 Zomato orders.
So the kitchen looks empty.

---

### ❌ Without KitchenPulse

The current system predicts **18 minutes**.

So the rider is sent early.

The rider arrives at minute 14
and **waits 14 minutes** outside.

The ETA keeps changing.
Customer leaves a **1-star review**.

---

### ✅ With KitchenPulse

Our system knows this restaurant's FOR trust score is very low.
So it ignores that signal.

It uses dwell time and behavior signals instead.

The prediction becomes **30 minutes**.

The rider arrives at minute 28.
Waits only **2 minutes**.

The food is hot.
The ETA stays stable.

---

## ⏱️ 6:15 – 7:30 | Business Impact

Three things make this system practical.

### First — Zero Cost

Everything we need already exists.

Zomato already collects:
rider GPS, FOR timestamps, merchant app behavior.

So this is just a **backend improvement**.

### Second — Real Impact

In our simulation:

- Worst-case rider wait dropped from **23 minutes to 16 minutes**
- Prediction accuracy improved significantly
- This could save around **₹170 crore per year**

### Third — Easy Deployment

We don't replace Zomato's model.

KitchenPulse simply provides **cleaner data**.

The existing model becomes better automatically.

---

## 🎬 Final Line

*(Pause. Look at judges.)*

We are not building Zomato a new brain.

*(Pause)*

We are cleaning the lies that the current brain is learning from.

*(Final line)*

**Fix the labels —
and the model fixes itself.**

Thank you.

---

## ⭐ Delivery Tips

- **Speak slower** than you think you need to
- **Pause** after every important line
- **Eye contact** with the judges during key moments

### 🔑 Three Lines the Judges Will Remember

1. **"The model isn't broken. The data is."**
2. **"The system figured out the restaurant lies — and stopped believing it."**
3. **"Fix the labels. The model fixes itself."**
