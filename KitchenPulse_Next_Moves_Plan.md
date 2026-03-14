# 🗺️ Team Escape — Next Moves Action Plan (Agla Kadam)

> **Deadline:** Sunday, March 15th, 12:00 PM | Humare paas aaj (March 10) se gine toh **5 din** bache hain.
> **Format:** 5-8 min presentation chalegi + 5-7 min ka Q&A Zoom call pe.

---

## ⏰ Timeline (Kaise badhna hai aage)

```
Aaj (Mon Mar 10)     Tue Mar 11      Wed Mar 12      Thu Mar 13      Fri Mar 14      Sat Mar 15 (D-Day)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│ Guide padh lo    │ Demo Build +  │ Demo Finish + │ PPT bana lo + │ REHEARSE +    │ PRESENT       │
│ Team ki Call     │ Coding        │ Slides Draft  │ Demo Polish   │ Mock Q&A      │ 12:00-12:15   │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Day 1: Monday, March 10 (AAJ KA KAAM)

### [ ] 1. Team Sync Call — Guide ko acche se dimaag me dalo
- **Kya karna hai:** Sabko `KitchenPulse_Deep_Understanding_Guide.md` acche se padhni hai dhyan laga ke.
- **Goal:** Har kisi ko uthake neend me bhi pooche ki FOR fraud kya hai ya Dwell kaise circular nahi hai, toh concept clear hona chahiye zubaan pe.
- **Action:** 1 ghante ki call/meet lo jahan sab ek dusre ko kisi ek topic par explain karenge:
  - **Rishi:** Trust engine kya hai, aur 'circularity defense' ko judge ko kaise samjhana hai.
  - **Ritesh:** Simulation model ka data pipeline, aur Dwell noise kaise filter hota hai.
  - **Shivam:** Signal tiers, aur merchant type (archetypes) kaun kaun se hote hain.

### [ ] 2. Faisla len (Decide): Demo ka kya scene karna hai?
> [!IMPORTANT]
> Email walo ne specifically likha hai: "judges may ask you to show the results or demonstrate the implementation." Humare paas dikhane ke liye koi working mechanism (demo) hona bohot hi zaroori hai tabhi weightge milega.

**Options:**

| Option | Mehnat/Effort | Asar (Impact) | Apna Suggestion |
|--------|--------|--------|----------------|
| **A) Python Simulation Live Demo** (Best option) | 2 days | HIGH | Python code chalake dikhayenge jo 300,000 fake orders generate kare usme noise laye, and Graphs generate karke proof de! |
| **B) Dashboard website UI** | 2-3 days | HIGH | Ek UI front-end banalo jo system ke graph and dashboard metrics show kare par engine back pe kuch lamba nahi karta. |
| **C) Dono karein (A+B)** | 3-4 days | VERY HIGH | Simulation as a proof + Dashboard as UI... (Agar kaafi hard work krle). |
| **D) Bas slide slide khelo bina Demo** | 0 days | LOW | Bhadak jayenge email rules ke according. "Risk Factor max". |

**🎯 Result/Sifarsih: Option A karna hi padega (Python Simulation Demo). Option B (UI Dashboard) agar end mein time mila to karna hai warna skip.** *(Agar aapko Option A ka Python code chahiye, toh main apke liye puri script likh sakta hoon!)*

### [ ] 3. Kaam ka Batwara (Roles Define Karo)
| Kis banda ka kaam hai | Karna kya hai (Task) | Akhiri Delivery ka roop |
|--------|-----------|-------------|
| **Ritesh Kumar** (Data + Simulation) | Python Code for Simulating Orders | Ek aisi Python script jo 3 lakh orders ka data generate kare, unme FOR bias laaye aur hamara KPT corrections output print kare. |
| **Shivam Pareek** (Charts + Dash / PPT) | Result Analysis + UI + Charts | Python generate wale matplotlib/plotly data ko Pie Chart ya Bar Chart me sundar se present/plot karna + PPT banana. |
| **Rishi** (Trust Engine AI) | Adaptive Algorithm and Logic Core Code | Weight scores (0-100) wali formula update loop likhna jisse auto-update Trust machine chalega simulate orders me. |

---

## Day 2: Tuesday, March 11

### [ ] 4. Python Simulation Code Likhna Shuru (Ritesh + Rishi)

**Backend me kya codes run karne wali file banani hai:**
1. **Data Generator (`data_generator.py`):** Fake 1000 restaurants, har kisi me random Order KPT time (true cooking) lagayenge normal distribution se. Phir uspe 70% Fake FOR button ki noise set karni h.
2. **FOR Validator (`for_validator.py`):** Algorithm banani hai pakadne ko ki - "Are in bewakoofon ne to rider aane k 60 sec window me button hit kiya h!" (Flag it as suspicious and assign them reliability scores 1-100).
3. **Trust Engine Setup (`trust_engine.py`):** 60% Guard-rail limit rules (Koi single condition pe game haavi na jaye), and Archetypes ke weight distribution calculation wala code.

### [ ] 5. Slides PPT me Shape Dena Shuru (Shivam)

**Time limit = 5-8 minute max bolne ko milega Zoom per.** Slides to be sharp, to the point!

**Rough Outline for The Presentation Deck:**
1. Title intro: Team Escape - KitchenPulse.
2. The Truth Reality problem: Machine sahi h data ghatiya hai (70% FOR buttons fail).
3. "Fix Data, not model" (Apan Zomato ka KPT architecture chedenge nhi inputs sudharenge).
4. The Cost/Nuksaan slide - ₹100-200 Crore waste hote per year.
5. Our System Diagram Dashboard: Multi-layer model ki photo .
6. Aam Zindagi (Biryani Story): Bina pulses wala wait ETA and bad experiences of customer drop vs Zomato's future view.
7. Charts Show Results: Option A wale simulaion graph bar lagane - baseline drop.
8. Implementation Zero-Day Start-UP (1st Phase No cash spend Pure App/ML).
9. Failure acceptance point. (Honest point rakho ki hum kahan gadbad karenge, black swan events like current load unexpected!).
10. One liner Punch! Ending Team escape banner show... 

---

## Day 3: Wednesday, March 12

### [ ] 6. Demo code finish karke uski Photos(Graphs) Output me lau
- **Charts / Visualizations required:**
  - Bar graph (P-90 Rider worst wait cases pre-app testing aur our new ML backend wala output score).
  - FOR fraud percentage wala bada clear Pie chart dikhao.

### [ ] 7. PPT Slide Deck ke andar sab plot kar dena

---

## Day 4: Thursday, March 13

### [ ] 8. Touch Ups Dena! + Recording/Backup Set Rakhiyo 
- Slides color aur font professional + Zomato theme standard related lage bas cool red touch ke sath.
- Python code itna optimize rakho module wala ki VS Code script run 30 Sec me execution display output print kardya meeting live mein.
- **BAHOT ZAROORI:** Ek full proper recording/video laptop pe Mobile se Screen Record / MP4 rakh lena Shivam apni folder per offline! Zoom internet issues kar jae to "Video chala diyo as an Output showcase fail backup" !! 

### [ ] 9. Pehli baar Pura Presentation Drill/Rehearsal
- Zoom timer ke sath First dry run karo koun aake konsi slide handle karega.. Team combination or 8 Min switch limit check mark pe aana chiye!!

---

## Day 5: Friday, March 14 (Sabse Zaroori MOCK Q&A)

### [ ] 10. Q&A MOCK BATTLE BHAINKAR!
Ek banda pura senior judge / chid-chida observer banega jo cross question fekega rough ho kar.  

**Kaun kya jawab dega fix raho dimag k andar ki tu cross question mat dena agar line ka part nhi to:**
- **Rishi (System, Backend Arch, Algorithm Logic):** Pura dimaag system kaise bna, Circularity error kya hoti? Q safe hai Data.. Trust system? 
- **Ritesh (Data and Math Testing validation):** Bhai Simulation code ka proof or test points kya h? Mathematical data? P-90 or Rider ETA par impact. Standard Deviation stats puchte hain wo.
- **Shivam (Consumer side, Impact, UI and Delivery Metrics):** Customer ETA me Jump kyu thehrega .. Volatility rukna and business per 170% budget calculation kaise saving karta usper bat krni hui to.

---

## Day 6: Saturday, March 15 (GAME DAY/ PRESENTATION DAY 🔥)

### [ ] 11. Pre-Fight Check
- 11:57 AM (3 minute time bacha ke meeting pe) baith jayiye setup fix the tables.. 
- Screen share VS Code/Terminal script aur deck ek page se dur nhi hona chahiye bg p khulla ho .
- Wired LAN Ethernet connection/ Wifi is great (Mobile Hotspot backup standby phone unlock condition ma rkho us point).
- Full Light on Camera Face per (Smile k sth start)! 

### [ ] 12. Creative Bomb 💣 Phekne ke liye suggestions jo wow factory raise karte:
1. **Rider waali story (Hooking Intro):** "Sir Good afternoon, mai apko Rahul jo pichle 2 saal se apna zomato partner unki story duga phelay. Wo us dhoop ke temperature mai over 14 minute bina wajah ek dhaba point par wait karre on system's fault ETA . Jisse us ghante lagbhag 32 rupees earning rate loss huye us ek glitch wajah. Yahi nhi ulte uski rating per bhi strike laga kyunki gusse me insaan late aane pr unko rating star kaat dete customer... Aise desh me lag bhag >3+ Lakh log sadre in loop glitches per daily!! Tab hum machine ko sudharenge model layer par!"
2. **"Decision Slide":** Pitch ko aise end karo jaisa koi real Business/Shark-tank chalra ho: "Hum nahi maangte 1500 cr IOT set par... humko zero rupee funding chahiye... Please hamein Zomato shadow tests mein backend implement ka mauka do sir testing P-90 live results layegi and prove hogi model input signal error data me. Boom!"
