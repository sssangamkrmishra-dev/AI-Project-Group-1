📘 Module 2 — Search-Based Recommendation System
### *AI-Driven Personalized Placement Preparation – State-Space Search Module*

This module implements **search-based reasoning** to recommend the **next best placement preparation activity** for a student, modeled as a **state-space problem**.  
It uses both an **uninformed search (UCS)** and an **informed search (A\\*)**, compares them empirically across multiple student profiles, and outputs CSV, JSON, and visualization results.

---

# 🚀 1. Project Overview

Final-year students often struggle with choosing the right next step in their preparation (DSA, System Design, Resume, HR, Breaks, etc.).  
We model this decision-making as a **search problem**, where:

- **State** = student skill levels + burnout  
- **Action** = preparation activity  
- **Transition** = effects of the activity on the student's state  
- **Goal** = readiness ≥ 0.75  
- **Search algorithm** = finds optimal next action & full plan  

This project implements:

### ✔ Uninformed Search
- **Uniform-Cost Search (UCS)**

### ✔ Informed Search
- **A\\* Search (admissible heuristic)**

### ✔ Additional Algorithm
- **BFS (Breadth-First Search)** for comparison

---

# 📂 2. Project Structure

```
module2_project/
├── module2_core.py
├── run_recommendation.py
├── experiments.py
├── generate_report.py
├── tests/
│   └── test_searches.py
├── results/
│   ├── experiment_results.csv
│   ├── experiment_results.json
│   ├── experiment_first_actions.png
│   └── recommendation_summary.json
├── requirements.txt
└── README.md
```

---

# ⚙️ 3. Installation & Setup

## Step 1 — Create Virtual Environment

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```powershell
python -m venv venv
venv\\Scripts\\activate
```

---

## Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ 4. How to Run the Code

## A) Run Recommendation for a Single Student

```bash
python run_recommendation.py
```

Output saved at:
```
results/recommendation_summary.json
```

### **Your Actual Output Included:**

- UCS next action: **Quick Revision**
- A* next action: **Quick Revision**
- UCS expansions: **718**
- A\* expansions: **87**
- Both total cost = **177.0**

---

## B) Run Multi-Profile Experiments

```bash
python experiments.py
```

Outputs:
- experiment_results.csv  
- experiment_results.json  
- experiment_first_actions.png  

### Example CSV Output (Your Run)

```
profile,start_readiness,bfs_first,bfs_cost,ucs_first,ucs_cost,astar_first,astar_cost
balanced_mid,0.3948,Solve DSA Problem,9,Quick Revision,177.0,Quick Revision,177.0
dsastrong,0.4312,Revise Resume,8,Quick Revision,174.0,Quick Revision,174.0
resume_weak,0.3772,,,Quick Revision,184.0,Quick Revision,184.0
burned_out,0.2808,,,Take a Break,200.0,Take a Break,200.0
```

---

# 📊 5. Algorithms Implemented

## A) Readiness Function

\\[
\\text{Readiness} =
(\\sum w_i \\cdot \\text{Skill}_i) \\cdot (1 - 0.8 \\cdot \\text{burnout})
\\]

Goal:
```
R >= 0.75
```

---

## B) State Transition Model

Each action changes:
- Skills  
- Burnout  
- Time cost  

Example:
```
Quick Revision:
+0.05 all skills
+0.01 burnout
20 minutes
```

---

## C) BFS (Breadth-First Search)

- Ignores cost  
- Expands by depth  
- **Not optimal**  
- Included for comparison  

---

## D) Uniform-Cost Search (UCS)

- Uninformed  
- Expands by cumulative cost  
- Guarantees **optimal plan**

---

## E) A* Search

Heuristic:

\\[
h = \\frac{\\text{Readiness Deficit}}{\\max(\\text{readiness gain per minute})}
\\]

- Admissible  
- Consistent  
- Optimal  
- Much fewer expansions  

---

# 📈 6. Results & Interpretation

## Result 1 — UCS & A* Always Agree

| Profile | UCS | A\* | Interpretation |
|---------|------|------|----------------|
| balanced_mid | Quick Revision | Quick Revision | Same optimal action |
| dsastrong | Quick Revision | Quick Revision | Same |
| resume_weak | Quick Revision | Quick Revision | Same |
| burned_out | Take a Break | Take a Break | Same |

---

## Result 2 — BFS Gives Unrealistic Suggestions

- Suggests **Solve DSA Problem** for balanced_mid  
- Suggests **Revise Resume** for dsastrong  
- Fails for deeper states  

BFS ignores burnout & time cost → **not strategic**.

---

## Result 3 — A\* is 8× More Efficient

| Algorithm | Expansions |
|----------|------------|
| UCS | 718 |
| A\* | 87 |

---

# 🧠 7. Why A\* is More Strategic  
### *(Use this section in your official report)*

- ✔ Faster  
- ✔ Still optimal  
- ✔ Uses domain knowledge  
- ✔ Avoids high-burnout sequences  
- ✔ Better suited for real-time student guidance  

UCS is reliable but slow; A\* is preferred for deployment.

---

# 📦 8. Sample Output (recommendation_summary.json)

UCS path:
```
["Quick Revision","Quick Revision","Quick Revision","Quick Revision",
 "Quick Revision","Take a Break","Take a Break","Take a Break","Quick Revision"]
```

A* path:
```
["Quick Revision","Quick Revision","Take a Break","Quick Revision",
 "Take a Break","Take a Break","Quick Revision","Quick Revision","Quick Revision"]
```

Both:
- Cost = **177**
- Final burnout low  
- Readiness threshold exceeded

---

# 🎯 9. Conclusion

This project:
- Successfully models placement preparation as a search problem  
- Implements BFS, UCS, and A\*  
- Produces correct CSV/JSON/visual outputs  
- Shows A\* as the most strategic real-world choice  

Everything is reproducible, validated, and ready for academic submission.

---

# 👨‍💻 Authors
**Devanshu Dangi**
