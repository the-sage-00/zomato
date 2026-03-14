# DelhiFloodIQ
### AI-Powered Predictive Urban Flood Intelligence Platform for Delhi

**Hackathon:** India Innovates 2026  
**Domain:** Urban Solutions  
**Problem Statement:** Urban Flooding & Hydrology Engine — GIS-Integrated Predictive System for 2500+ Micro Flood Hotspots  
**Category:** Software Only

---


## 1. The Problem

Delhi drowns every monsoon. And every year, the city acts surprised.

India's capital has **3,800+ km of stormwater drains** — managed by **five separate agencies** (MCD, DJB, PWD, NDMC, and Cantonment Board) — with no unified system that knows which drains are cleared, which are silted, or where water will accumulate next. During the 2025 monsoon, entire neighbourhoods in Rohini, Dwarka, and East Delhi were submerged under 3–5 feet of water within hours. Citizens woke up to flooded streets with **zero advance warning**. Emergency services could not reach affected areas because no one knew which roads were passable.

This is not a new crisis. It happens every year. What makes it a solvable problem in 2026 is that all the data needed to predict it already exists — but lives in silos that never talk to each other.

### The Core Failures

**1. No Prediction — Only Reaction**  
Delhi has no ward-level flood prediction system. The existing Central Water Commission (CWC) system focuses on river flooding and major basins. Nobody predicts that *Patel Nagar's B-Block service road will flood if it rains 40mm/hr for 2 hours* — even though it happens every single year at that exact threshold. The city reacts after water is knee-deep. By then, the damage is done.

**2. Five Agencies, Zero Coordination**  
A single road in Delhi can have its drains managed by MCD, its stormwater outfall controlled by PWD, and its water supply pipes maintained by DJB — all independently, with no shared visibility. When one agency desilts only their section, the bottleneck simply moves to the next agency's territory. MCD spent **₹36 crore** on desilting in 2025, but without knowing which drains were the highest-risk, the money was spread uniformly rather than targeted where it mattered most.

**3. Citizens are Blind**  
There is no public-facing system that tells a citizen: *"Your ward has a high flood risk today. Avoid basement parking. Move vehicles to higher ground."* People learn about flooding only when their homes are already inundated. The MCD App allows complaint filing *after* the fact — which helps no one during the actual event.

**4. The ₹36 Crore Desilting Lottery**  
MCD cleans drains before every monsoon, but the prioritization is manual. Officers decide which drains to desilt based on past experience and political pressure, not data. A drain that caused 200 waterlogging complaints last year might be desilted at the same priority as one that caused 5. The budget is limited — but the intelligence to allocate it optimally does not exist.

### The Scale

| Metric | Number |
|---|---|
| Total drain length in Delhi | 3,800+ km |
| Agencies managing drains | 5 (MCD, DJB, PWD, NDMC, Cantonment Board) |
| Wards in Delhi | 250 |
| Estimated micro flood hotspots | 2,500+ |
| Desilting budget (2025) | ₹36 crore |
| Waterlogging complaints per monsoon season | Tens of thousands |
| Average citizen warning time before flooding | **0 hours** |

---

## 2. The Solution — DelhiFloodIQ

**DelhiFloodIQ** is an AI-powered geospatial intelligence platform that predicts urban flooding at the ward and street level, enables data-driven desilting prioritization, unifies drain visibility across all five agencies, and delivers hyper-local flood alerts to citizens — all before the first drop of monsoon rain causes damage.

It transforms Delhi's flood response from **reactive** ("the road is flooded, send a pump") to **predictive** ("this road will flood in 4 hours at current rainfall rate, reroute traffic and pre-position pumps").

### How It Works

#### Stage 1 — Geospatial Data Fusion

DelhiFloodIQ ingests and unifies geospatial data from multiple sources into a single spatial database:

- **Delhi's drain network maps** (KML data from MCD/PWD/DJB covering all major stormwater drains — Najafgarh, Barapulla, East Drain, and hundreds of smaller drains)
- **Ward boundary polygons** for all 250 Delhi wards
- **Road and elevation data** from OpenStreetMap
- **Historical waterlogging complaint locations** from the MCD App and data.gov.in
- **Desilting records** from MCD (which drains were cleaned, when, and to what extent)

All data is stored in **PostGIS** — an industry-standard geospatial database — enabling complex spatial queries like: *"Find all drain segments within 500m of a school that have not been desilted in 12 months and had >10 waterlogging complaints last monsoon."*

#### Stage 2 — Flood Risk Scoring (Pre-Monsoon Intelligence)

Before monsoon season even begins, DelhiFloodIQ generates a **static flood risk score** for every ward and every drain segment based on:

- **Historical flood frequency** — how many times this location flooded in the past 5 years
- **Drain capacity and condition** — drain diameter, gradient, silt level, last desilting date
- **Terrain and elevation** — low-lying areas, natural water accumulation points
- **Upstream dependencies** — if drain A feeds into drain B, and drain B is silted, drain A's entire catchment is at risk regardless of drain A's own condition
- **Population density and criticality** — hospitals, schools, and densely populated areas get higher weight

An **XGBoost gradient-boosted model** trained on 5+ years of historical flood-complaint correlation data computes a composite risk score (0–100) for each of Delhi's 2,500+ identified micro flood hotspots.

**Output:** A pre-monsoon **Flood Vulnerability Map** of Delhi — before a single drop of rain falls, the city knows exactly where it is weakest.

#### Stage 3 — Real-Time Rainfall Prediction & Flood Forecasting

Once monsoon begins, DelhiFloodIQ shifts into real-time mode:

- **IMD (India Meteorological Department) rainfall data** is ingested continuously — both observed rainfall from monitoring stations and forecast data
- An **LSTM (Long Short-Term Memory) neural network** trained on 10+ years of Delhi's hourly rainfall patterns generates hyper-local rainfall predictions for the next 6–48 hours
- The rainfall predictions are fed into the pre-computed drain capacity model to simulate **water flow and accumulation** across the drain network
- The system answers the critical question: *"If rainfall continues at X mm/hr for the next Y hours, which specific wards and streets will flood, and when?"*

**Output:** A dynamic, animated **flood propagation map** that visualizes how water will spread across Delhi over the coming hours — updated every 15 minutes.

#### Stage 4 — Intelligent Desilting Priority Engine

DelhiFloodIQ generates a ranked **Desilting Priority Queue** for MCD officers — answering the question: *"Given our limited budget and time before monsoon, which 100 drains should we desilt first for maximum flood prevention impact?"*

The ranking algorithm considers:
- **Flood risk reduction impact** — if we desilt this drain, how many fewer wards flood?
- **Upstream/downstream dependencies** — desilting downstream first prevents cascading backflow
- **Population at risk** — higher priority for drains protecting hospitals, schools, low-income housing
- **Cost efficiency** — shorter drains with high impact are prioritized over long drains with marginal benefit

This turns the ₹36 crore desilting budget from a **lottery** into a **precision instrument**.

#### Stage 5 — Citizen Alert System

When DelhiFloodIQ predicts flooding in a specific ward, it automatically triggers **hyper-local alerts**:

- **WhatsApp notifications** to subscribed citizens: *"⚠️ Flood Alert: Rohini Sector 7 — HIGH flood risk in next 3 hours. Expected waterlogging on main road. Avoid basement parking. Nearest shelter: Community Hall, Sector 5."*
- **SMS fallback** for citizens without smartphones
- Alerts include: risk level, expected timing, affected streets, nearest safe zones, emergency contacts

Citizens move from **0 hours warning** to **6–48 hours advance notice**.

#### Stage 6 — Cross-Agency Coordination Dashboard

A unified command dashboard for MCD, PWD, DJB, NDMC, and Cantonment Board officers showing:

- **All 5 agency drain networks on one map** — first time ever
- Real-time **incident feed** — citizen reports, sensor alerts, and AI predictions in one stream
- **Cross-agency drain handoff alerts** — when a drain crosses from MCD territory to PWD territory, both agencies see the flood risk for the entire stretch
- **Emergency corridor suggestions** — predicted flood zones overlaid with ambulance/fire routes, suggesting alternative corridors before roads become impassable

---

## 3. Innovation — What Makes DelhiFloodIQ Different

### Innovation 1: Micro-Hotspot Prediction (Not River-Level, Not City-Level — Street-Level)

Existing flood prediction systems in India (CWC, C-FLOOD) predict at the **river basin** or **district** level. They tell you "Delhi may experience flooding." That is useless for a citizen in Rajouri Garden who needs to know if *their street* will flood.

DelhiFloodIQ predicts at the **micro-hotspot level** — specific road segments, underpasses, and low-lying pockets — by correlating drain network topology with rainfall patterns. This is the difference between a weather forecast and an umbrella for your lane.

### Innovation 2: Drain Dependency Graph

We model Delhi's drain network as a **directed graph** where each drain segment is a node and water flow is an edge. This captures **upstream-downstream dependencies** that no current system accounts for:

- If Drain A (MCD territory) feeds into Drain B (PWD territory) and Drain B is silted, desilting only Drain A is wasted effort
- Our system identifies these **cascading failure chains** and recommends coordinated desilting across agencies

This is the first system that treats Delhi's drainage as a **connected network** rather than isolated segments managed by isolated agencies.

### Innovation 3: Predictive Budget Optimization

Instead of spreading desilting budget uniformly, DelhiFloodIQ answers: *"For every ₹1 lakh spent on desilting, which drain gives us the maximum reduction in flood risk?"*

This converts flood prevention from a **cost center** (spend money, hope it helps) to a **measurable investment** (spend ₹X on drain Y, reduce flood probability in 3 wards by Z%).

### Innovation 4: Citizen-Centric Warning System

No existing government system in Delhi provides **proactive, location-specific flood warnings** to individual citizens. DelhiFloodIQ is the first system where a citizen can subscribe to their ward and receive actionable, plain-language alerts hours before flooding occurs — via WhatsApp, requiring no app download.

### Innovation 5: Five-Agency Unification

For the first time in Delhi's civic infrastructure history, drain data from all five managing agencies is rendered on a **single unified map**. Officers from any agency can see the complete picture — not just their own slice. This directly addresses the "structural silos" problem identified by multiple government reports and the Delhi High Court.

---

## 4. System Architecture

```
┌──────────────────────────────────────────────────────┐
│                   DATA SOURCES                        │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌────────────┐  │
│  │Delhi GIS │ │  IMD     │ │ CPCB │ │MCD App     │  │
│  │Drain Maps│ │ Rainfall │ │Weather│ │Complaints  │  │
│  │(KML/SHP) │ │ (API)    │ │(API) │ │(data.gov)  │  │
│  └────┬─────┘ └────┬─────┘ └──┬───┘ └─────┬──────┘  │
│       │             │          │           │          │
└───────┼─────────────┼──────────┼───────────┼──────────┘
        │             │          │           │
        ▼             ▼          ▼           ▼
┌──────────────────────────────────────────────────────┐
│              GEOSPATIAL DATA ENGINE                   │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │         PostgreSQL + PostGIS                    │  │
│  │  • Unified drain network (all 5 agencies)      │  │
│  │  • Ward boundary polygons (250 wards)          │  │
│  │  • Historical flood complaint locations         │  │
│  │  • Drain dependency directed graph              │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│              AI / ML PREDICTION ENGINE                │
│                                                      │
│  ┌─────────────────┐  ┌──────────────────────────┐  │
│  │   XGBoost Model  │  │   LSTM Neural Network     │  │
│  │                  │  │                           │  │
│  │ Static Flood     │  │ Real-Time Rainfall        │  │
│  │ Risk Scoring     │  │ Forecasting (6-48 hrs)    │  │
│  │ (per hotspot)    │  │ (per ward)                │  │
│  └────────┬─────────┘  └──────────┬───────────────┘  │
│           │                       │                   │
│           ▼                       ▼                   │
│  ┌────────────────────────────────────────────────┐  │
│  │        Flood Propagation Simulator              │  │
│  │  • Drain capacity × rainfall rate               │  │
│  │  • Upstream dependency chain analysis            │  │
│  │  • Time-stepped ward-level flood prediction     │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────┘
                       │
        ┌──────────────┼───────────────┐
        ▼              ▼               ▼
┌──────────────┐ ┌────────────┐ ┌──────────────────┐
│ PUBLIC FLOOD │ │  OFFICER   │ │  CITIZEN ALERT   │
│  RISK MAP    │ │ COMMAND    │ │   SYSTEM         │
│              │ │ DASHBOARD  │ │                  │
│ • Interactive│ │            │ │ • WhatsApp push  │
│   GIS map    │ │ • Unified  │ │ • SMS fallback   │
│ • Ward-level │ │   5-agency │ │ • Ward subscribe │
│   risk scores│ │   drain map│ │ • Plain language │
│ • Historical │ │ • Desilting│ │ • Shelter info   │
│   flood data │ │   priority │ │ • Emergency      │
│ • Search by  │ │   queue    │ │   contacts       │
│   location   │ │ • Emergency│ │                  │
│              │ │   corridors│ │                  │
└──────────────┘ └────────────┘ └──────────────────┘
```

---

## 5. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js + Mapbox GL JS | Interactive GIS map rendering with 100K+ geospatial features |
| **Backend API** | Python, FastAPI | High-performance async API serving predictions and geospatial queries |
| **ML — Risk Scoring** | XGBoost (scikit-learn) | Gradient-boosted model for static flood risk scoring per hotspot |
| **ML — Forecasting** | LSTM (PyTorch) | Time-series rainfall prediction for 6–48 hour forecasting |
| **GIS Database** | PostgreSQL + PostGIS | Spatial queries, drain network graph, ward polygon intersections |
| **Map Tiles** | OpenStreetMap + Delhi Drain KML data | Base layer + drain overlay |
| **Citizen Alerts** | Twilio WhatsApp Business API + SMS | Hyper-local push notifications, no app download needed |
| **Deployment** | Docker containers | Portable, reproducible deployment on any cloud |
| **Data Sources** | IMD API, CPCB API, data.gov.in, opencity.in | Real-time rainfall, weather, historical complaints, GIS drain data |

---

## 6. Data Sources & Availability

| Source | Data | Format | Access |
|---|---|---|---|
| opencity.in / Delhi Open Data | Delhi stormwater drain network maps (Najafgarh, Barapulla, East, PWD drains) | KML | Free, public download |
| data.gov.in | MCD complaint data, CPCB air quality + weather data | CSV/API | Free, API key available |
| IMD (mausam.imd.gov.in) | Historical + real-time rainfall data for Delhi stations | API/CSV | Publicly available |
| waterhubdata.com | Barapullah sub-basin GIS, waterlogging points vectorized via ArcGIS | GIS/SHP | Free |
| OpenStreetMap | Road network, building footprints, elevation contours for Delhi | OSM/GeoJSON | Free |
| Delhi Master Plan 2041 | Ward boundaries, drainage zones, land use classification | PDF/GIS | Public document |
| MCD budgets / desilting reports | Desilting schedules, drain maintenance records | PDF | RTI / public records |

All primary data sources are **open, free, and publicly accessible** — no proprietary data or special government access is required.

---

## 7. Impact Potential

| Metric | Current (Without DelhiFloodIQ) | Projected (With DelhiFloodIQ) |
|---|---|---|
| **Citizen flood warning time** | 0 hours (no system exists) | 6–48 hours advance |
| **Desilting budget targeting** | Uniform / political (guesswork) | AI-optimized by flood risk impact |
| **Cross-agency drain visibility** | None (5 independent silos) | Unified real-time map |
| **Micro flood hotspot coverage** | 0 mapped hotspots | 2,500+ scored and monitored |
| **Emergency corridor planning** | Reactive (after roads flood) | Predictive (reroute before flooding) |
| **Citizen complaint resolution** | Post-facto (file complaint after flood) | Pre-emptive (prevent flood, reduce complaints) |
| **₹36 Cr desilting ROI** | Unknown / low | Measurable: ₹X → Y% risk reduction |

---

## 8. Feasibility & Deployability

- **100% software solution** — no hardware sensors, IoT devices, or physical infrastructure required
- **All data sources are openly available** — no dependency on proprietary or restricted government datasets
- **Cloud-agnostic** — runs on any infrastructure (AWS, Azure, NIC Cloud, or even a university server)
- **NIC Cloud compatible** — designed for government data residency compliance if adopted
- **Modular architecture** — each component (GIS engine, ML models, alert system, dashboard) can be deployed independently and upgraded individually
- **Low citizen barrier** — WhatsApp-based alerts require no app download, no registration, no smartphone — works on basic Android and even feature phones via SMS fallback

---

## 9. Alignment with Government Initiatives

DelhiFloodIQ directly supports and accelerates multiple active government mandates:

| Initiative | How DelhiFloodIQ Aligns |
|---|---|
| **Delhi Govt–IIT Kanpur MoU (Nov 2025)** | India's first AI-driven urban water management model — DelhiFloodIQ is exactly this concept, production-ready |
| **MCD 2026 Monsoon Desilting Plan** | ₹36 Cr desilting of 800 drains — our system tells MCD *which* 800 drains to prioritize |
| **Delhi Flood Safety Plan 2026** | Cross-departmental monitoring committee formed — our dashboard gives them the unified view they lack |
| **Central Water Commission C-FLOOD** | Village-level flood alerts nationally — DelhiFloodIQ extends this to *street-level* for India's capital |
| **Smart Cities Mission** | AI + IoT for urban intelligence — DelhiFloodIQ delivers the intelligence layer mission demands |
| **Delhi Master Plan 2041** | Sustainable drainage and climate resilience — our system enables evidence-based planning |

---

## 10. Why This Solution Wins

1. **Exact problem statement match** — The hackathon asks for a *"GIS-integrated predictive system for 2500+ micro flood hotspots."* DelhiFloodIQ is exactly this.

2. **Built for Delhi, by design** — This is not a generic smart city tool adapted for Delhi. Every data source, every drain map, every prediction model is Delhi-specific.

3. **Solves the real bottleneck** — Delhi's flood problem is not a lack of money (₹36 Cr was allocated) or effort (800 drains are desilted annually). The bottleneck is *intelligence* — knowing where to focus. DelhiFloodIQ provides that intelligence.

4. **First to unify five agencies** — No system in Delhi has ever shown all five agency drain networks on a single map. We break the structural silo.

5. **Citizen impact is immediate and measurable** — From zero warning to 6–48 hours. From no public risk map to ward-level transparency. These are concrete, auditable improvements.

6. **No hardware dependency** — Fully deployable with existing infrastructure. No sensors to install, no hardware to procure, no multi-year capex approval needed.

7. **Post-hackathon adoption path is clear** — The Delhi government has already signed an MoU with IIT Kanpur for exactly this type of system. DelhiFloodIQ can slot directly into that roadmap.

---

## 11. References

1. Delhi Open City Portal — Stormwater Drain KML Maps — opencity.in
2. Central Water Commission (CWC) — C-FLOOD Unified Flood Forecasting — cwc.gov.in
3. India Meteorological Department — Rainfall Monitoring & Forecasting — mausam.imd.gov.in
4. CPCB — Continuous Ambient Air Quality Monitoring System — cpcb.nic.in
5. Delhi Government & IIT Kanpur MoU (Nov 2025) — AI-Driven Urban Water Management Model
6. MCD Budget 2025–26 — ₹36 Crore Desilting Allocation — mcd.gov.in
7. Delhi Master Plan 2041 (Draft) — Drainage Master Plan for NCT of Delhi (2018)
8. XGBoost: A Scalable Tree Boosting System — Chen & Guestrin, KDD 2016
9. Long Short-Term Memory Networks — Hochreiter & Schmidhuber, Neural Computation 1997
10. PostGIS — Spatial and Geographic Objects for PostgreSQL — postgis.net
11. Delhi High Court Direction on MCD Financial Crunch Impeding Flood Prevention (Dec 2025)
12. WaterHub Data — Barapullah Sub-basin GIS Data — waterhubdata.com
13. data.gov.in — Open Government Data Platform India — CPGRAMS, CPCB, MCD Datasets
