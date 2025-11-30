# 🎯 Placement Planner

> A  planner backend (GraphPlan + POP with temporal scheduling & repair) paired with a polished React frontend (Tailwind + Framer Motion) that visualizes plans, schedules, intermediate algorithm traces, and supports simulation & repair flows.

![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![React](https://img.shields.io/badge/react-18+-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Data \& How It's Used](#-data--how-its-used)
- [Inputs and Outputs](#-inputs-and-outputs)
  - [Input Fields](#input-fields-client--backend)
  - [Output Plan/Schedule](#output-planschedule-backend--client)
- [How the Planners Work](#%EF%B8%8F-how-the-planners-work)
  - [GraphPlan](#graphplan)
  - [POP (Partial-Order Planner)](#pop-partial-order-planner--scheduling)
- [Getting Started](#-getting-started)
  - [Backend Setup](#backend-python--fastapi)
  - [Frontend Setup](#frontend-react)
- [Features Implemented](#-features-implemented)
- [Future Work](#-future-work)


---

## 🌟 Overview

Placement Planner helps students create optimized preparation schedules for placements using AI planning algorithms. It combines **GraphPlan** and **Partial-Order Planning (POP)** with temporal scheduling to generate actionable, resource-aware study plans.

---

## 📊 Data & How It's Used

Only **two operational data sources** are used by the planning algorithm:

| Data Source | Purpose |
|-------------|---------|
| **LeetCode Practice / DSA Metrics** | Estimate duration/effort/benefit for DSA-related actions |
| **Mock Interviews** | Estimate benefit for confidence/communication improvements |

### What the planner computes from this data:

- ⏱️ **Action durations** (weeks)
- 💪 **Effort estimates** (hours)
- 📈 **Estimated benefit probabilities** (used to order/score candidates in heuristics)

> **Note:** `dataset_skeleton` and `estimates.json` provide data-driven heuristics (durations, benefits, burnout risk). See `/data` for raw dataset skeletons.

---

## 📥 Inputs and Outputs

### Input Fields (Client → Backend)

| Field | Type | Description | Real-World Meaning |
|-------|------|-------------|-------------------|
| `init_state` | `List[str]` | Facts/fluents describing the student now | Current skill-level tags, resource/health flags |
| `goals` | `List[str]` | Desired target fluents | Outcomes you want to reach |
| `max_parallel_major_actions_per_week` | `int` | Resource constraint | How many large-time commitments a student can handle concurrently |
| `executed_actions` *(repair endpoint)* | `List[{name, status}]` | Actions that have been executed | Runtime observations used to replan |

#### Example `init_state`:

```text
DSA_LOW, ML_LOW, RESUME_LOW, NOT_BURNOUT
```

#### Example `goals`:

```text
DSA_HIGH, RESUME_HIGH, CONF_HIGH
```

---

### Output Plan/Schedule (Backend → Client)

Each action in the plan/schedule contains:

| Field | Description |
|-------|-------------|
| `name` | Action identifier (e.g., `DSA_Practice_intense`) |
| `duration` / `duration_weeks` | Planned temporal length (weeks) |
| `effort_hours` / `effort` | Total effort estimate (hours) |
| `preconds` / `preconditions` | Facts required before executing action |
| `adds` | Facts that the action adds on success (effects) |
| `dels` / `deletes` | Facts removed (if any) |
| `est` | Earliest scheduled start week (POP output) |
| `order` | Sequence index (GraphPlan returns linear order) |
| `trace` *(optional)* | Ordered list of trace-step objects for trace viewer |

#### Example Schedule Item:

```json
{
  "name": "DSA_Practice_intense",
  "duration": 2,
  "effort_hours": 20,
  "preconds": ["DSA_LOW"],
  "adds": ["DSA_HIGH", "BURNOUT"],
  "dels": [],
  "est": 0
}
```

---

## ⚙️ How the Planners Work

### GraphPlan

```text
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Facts L0   │───▶│  Actions    │───▶│  Facts L1   │───▶ ...
│  (Initial)  │    │  Layer      │    │  (Effects)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

**What it does:**

1. Builds a planning graph alternating layers of facts (states) and actions
2. Performs backward search from goals to initial facts
3. Extracts a linear action sequence (plan)

**Output:** An ordered list of actions (sequence)

**Best for:** Finding minimal action sets when concurrency and durations are not the main concern

**Frontend Visualization:** Action Sequence list (GraphPlan tab) with trace viewer showing graph construction, mutex checks, levels, and extraction steps

---

### POP (Partial-Order Planner) + Scheduling

**What it does:**

1. Produces **partial-order plans** (constraints between actions rather than a single total order)
2. Schedules actions over time with `est` (Earliest Start Time) values
3. Respects `max_parallel_major_actions_per_week` and resource limits
4. **Supports repair:** When an action is executed/failed, POP can re-schedule or re-plan

**Frontend Visualization:**

- 📊 POP Schedule
- 📅 Gantt/Timeline chart
- 🗓️ Schedule cards with "Week X"
- 🔧 Repair UI (mark actions done/failed → rerun repair planner)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm 

### Backend (Python / FastAPI)

```bash
# Navigate to project root
cd Planning Placement Strategy using GraphPlan and POP

# Create and activate virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --reload
```

> The API will be available at `http://localhost:8000`

### Frontend (React)

```bash
# Navigate to client directory from Planning Placement Strategy using GraphPlan and POP (directory)
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

> The frontend will be available at `http://localhost:5173`

---

## Images :

<img width="1193" height="952" alt="image" src="https://github.com/user-attachments/assets/90e3392e-6df6-4460-b9b7-a4702f652e64" />
<img width="1193" height="952" alt="image" src="https://github.com/user-attachments/assets/24cf9e68-7906-4a15-ad64-f9efc76e15af" />
<img width="802" height="923" alt="image" src="https://github.com/user-attachments/assets/8fb3d1ad-d538-4826-84a4-54dd506f12f8" />
<img width="787" height="796" alt="image" src="https://github.com/user-attachments/assets/40886f07-2683-4e94-9e4f-ceb7972d3ac6" />
<img width="782" height="622" alt="image" src="https://github.com/user-attachments/assets/0f9b2011-1d63-488f-82b9-cec9ffe3b437" />
<img width="947" height="511" alt="image" src="https://github.com/user-attachments/assets/423626b8-1f0b-42d7-a861-00a1dbf03ed1" />
<img width="965" height="547" alt="image" src="https://github.com/user-attachments/assets/ed197f2c-1bcd-41d8-9faf-40d56f6770d8" />



## 🧪 Running the Interactive Planner via Terminal

This section explains how to run the backend planner directly from your terminal without using the frontend UI.

---

### Step 1 — Run the Script

```bash
python3 run_example.py
```

> **Note:** If `estimates.json` exists, the script automatically loads probability-based heuristics.

---

### Step 2 — Provide Inputs

When you run the script, you'll see the following prompts:

```text
Planner example (interactive).
Press Enter to use defaults or provide comma-separated values.

Initial state [DSA_LOW, ML_LOW, RESUME_LOW, NOT_BURNOUT]:
Goals [DSA_HIGH, RESUME_HIGH, CONF_HIGH]:
```

#### ✅ Option A: Enter Custom Values

You can provide your own comma-separated values:

```text
Initial state [DSA_LOW, ML_LOW, RESUME_LOW, NOT_BURNOUT]: 
DSA_LOW, ML_HIGH, RESUME_LOW, BURN_OUT

Goals [DSA_HIGH, RESUME_HIGH, CONF_HIGH]:
DSA_HIGH, RESUME_HIGH, CONF_HIGH
```

#### ✅ Option B: Use Defaults

Simply press `Enter` to use the default values:

| Field | Default Value |
|-------|---------------|
| Initial State | `DSA_LOW, ML_LOW, RESUME_LOW, NOT_BURNOUT` |
| Goals | `DSA_HIGH, RESUME_HIGH, CONF_HIGH` |

---

### 🎯 Example Input (Copy & Paste Ready)

**Initial State:**

```text
DSA_LOW, ML_HIGH, RESUME_LOW, BURN_OUT
```

**Goal State:**

```text
DSA_HIGH, RESUME_HIGH, CONF_HIGH
```

---

## 📤 Script Output Explained

After running, the script outputs the following sections:

---

### 1️⃣ GraphPlan Construction Levels

Shows how GraphPlan expands the planning graph layer by layer:

```text
Graph construction levels:
Level 0: ['BURN_OUT', 'DSA_LOW', 'ML_HIGH', 'RESUME_LOW']
Level 1: [...]
Level 2: [...]
...
```

> This helps visualize the state-space exploration during planning.

---

### 2️⃣ GraphPlan Final Plan (Ordered Sequence)

The extracted linear action sequence:

```text
1. DSA_Practice_light
2. Resume_Optimize_quick
3. Resume_Optimize_deep
4. DSA_Review
5. DSA_Keep_practice
6. MockInterview_full
```

---

### 3️⃣ GraphPlan Step-by-Step State Evolution

Shows how the world state changes after each action:

```text
Step 1: Apply DSA_Practice_light
  before: ['BURN_OUT', 'DSA_LOW', ...]
  after : ['DSA_MED', 'NOT_BURNOUT', ...]
```

> 💡 **Tip:** This is perfect for understanding how planning works at the conceptual level.

---

### 4️⃣ POP Scheduled Plan

The Partial-Order Planner output includes:

| Attribute | Description |
|-----------|-------------|
| Start week | When the action begins |
| Duration | How long the action takes |
| Effort | Estimated hours required |
| Expected benefit | Probability-based benefit score |
| Burnout risk | Risk level indicator |
| Adds/Deletes | State changes (effects) |

**Example Output:**

```text
- Resume_Optimize_quick: week 0
- DSA_Practice_intense: week 0
- Resume_Optimize_deep: week 1
- MockInterview_full: week 2
```

---

### 5️⃣ POP Step-by-Step World State Progression

Shows how the plan unfolds over time with state transitions:

```text
Week 0: Action Resume_Optimize_quick
  before: [...]
  after : [...]

Week 0: Action DSA_Practice_intense
  before: [...]
  after : [...]

Week 2: Action MockInterview_full
  before: [...]
  after : [...]
```

> This visualization helps track how your preparation state evolves week by week.

---

### 📋 Quick Reference

| Output Section | What It Shows |
|----------------|---------------|
| Construction Levels | GraphPlan layer-by-layer expansion |
| Final Plan | Ordered action sequence |
| State Evolution | Before/after states per action |
| POP Schedule | Time-based action scheduling |
| World Progression | Weekly state changes |



### Images :
<img width="1239" height="219" alt="image" src="https://github.com/user-attachments/assets/5a941909-b633-4f24-a10a-f54febbdb4b0" />
<img width="1797" height="761" alt="image" src="https://github.com/user-attachments/assets/197a7b90-4ea0-48d8-9c78-4c1abcd1513c" />
<img width="1781" height="223" alt="image" src="https://github.com/user-attachments/assets/61631860-8792-4f03-99b5-a51f1f968118" />
<img width="1093" height="757" alt="image" src="https://github.com/user-attachments/assets/d84e9dbe-5c49-421d-a486-ed17f9de315b" />





## ✅ Features Implemented

### 🎨 UI/UX

- [x] Glass design with animated orbs and particles
- [x] Gradient buttons with Framer Motion transitions
- [x] Action details modal (preconditions/effects/duration/effort)

### 📊 Visualization

- [x] Gantt chart / timeline visualization (positioned by `est` and `duration`)
- [x] Trace viewer modal with step-by-step playback (copyable JSON)

### 🔧 Planning Features

- [x] Temporal scheduling with resource constraints (parallelism limit)
- [x] Plan repair flow (mark action Done/Failed → regenerate schedule)
- [x] Simulation endpoint + UI modal for single action state changes
- [x] Data-driven heuristics via `estimates.json`

### 🎓 Extra Features 

- [x] Temporal scheduling + resource constraints
- [x] Repair flow supporting executed actions
- [x] Interactive UI + pedagogical trace viewer (great for teaching theory!)
- [x] Simulation endpoint for step-wise verification

---

## 🔮 Future Work

| Category | Enhancement |
|----------|-------------|
| **User Experience** | User profiles with persisted preferences & history (localStorage / backend DB) |
| **Security** | Authentication for multi-user scenarios |
| **Export** | Export/print plan as PDF or shareable link |
| **Interactivity** | Interactive timeline editing (drag actions to reschedule with conflict warnings) |
| **Modeling** | More realistic effort modeling (daily calendars, working hours, availability slots) |
| **AI Planning** | Action success probabilities and expected utility-based planning |
| **Visualization** | Visualization of mutex/conflicts (in GraphPlan trace) |
| **Testing** | Unit tests for planner + E2E tests for frontend–backend flow |
| **Data Integration** | Connect actual LeetCode + mock interview logs to auto-update estimates |

---



---



