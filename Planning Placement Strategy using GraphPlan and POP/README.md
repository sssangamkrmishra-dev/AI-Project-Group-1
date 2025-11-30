# 🎯 Placement Planner

> A powerful planner backend (GraphPlan + POP with temporal scheduling & repair) paired with a polished React frontend (Tailwind + Framer Motion) that visualizes plans, schedules, intermediate algorithm traces, and supports simulation & repair flows.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
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
- [Contributing](#-contributing)
- [License](#-license)

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
- npm or yarn

### Backend (Python / FastAPI)

```bash
# Navigate to project root
cd "Planning Placement Strategy using GraphPlan and POP"

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
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

> The frontend will be available at `http://localhost:5173`

---

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

### 🎓 Extra Features (Beyond Minimal Planner)

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for placement preparation**

[Report Bug](../../issues) · [Request Feature](../../issues)

</div>