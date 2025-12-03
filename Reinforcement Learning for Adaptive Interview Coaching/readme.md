# Reinforcement Learning for Adaptive Interview Coaching

This project implements a **Reinforcement Learning (RL) agent** to simulate an **adaptive interview coaching system**.  
The RL-based AI coach interacts with a student and suggests actions such as:

- Increasing difficulty  
- Switching topics  
- Giving encouragement  
- Offering quick revision  

Decisions are made based on the student's **confidence**, **mastery**, and **burnout** levels.

---
## 1. Folder Structure

Assuming project root:

`Reinforcement Learning for Adaptive Interview Coaching/`

```bash
Reinforcement Learning for Adaptive Interview Coaching/
│
├── model/
│   └── q_table.pkl
├── Dashboard.py
├── QLearningAgent.py
├── Student.py
├── Trainer.py
├── requirements.txt
└── README.md
```
## 2. Features
### 2.1. Student Environment (`Student.py`)
This module defines a custom environment that models a student's dynamic learning state and responses to coaching actions.

**Key Features:**
- Simulates a student's state using the following attributes:
  - **Confidence:** `0–20`
  - **Mastery:** `0–20`
  - **Burnout:** `0.0–1.0` (Probability of exhaustion)
  - **Time left:** `30 days` (Total preparation timeline)
- Handles state transitions based on AI-driven actions.
- Incorporates stochastic (random) outcomes to mimic real-world uncertainty.
- Each action results in a reward and updates the student's confidence, mastery, and burnout levels, reflecting the variable nature of learning outcomes.

---

### 2.2. RL Agent (`QLearningAgent.py`)
This module implements the core decision-making intelligence using Reinforcement Learning.

**Key Features:**
- Q-Learning agent with epsilon-greedy exploration to balance exploration and exploitation.
- Learns optimal strategies to maximize student progress while proactively managing burnout.
- Supports saving and loading of trained Q-tables for seamless deployment and continuous learning.
- Adapts dynamically to the student's state to provide personalized coaching.

---

### 2.3. Trainer (`Trainer.py`)
This script manages the training lifecycle of the RL agent.

**Key Features:**
- Trains the agent across multiple simulations (episodes) to improve performance.
- Manages learning rate and exploration decay schedules for efficient training.
- Saves the optimized Q-table to disk for use by the `Dashboard.py` interface.
- Ensures the agent generalizes well across diverse student scenarios.

---

### 2.4. Dashboard (`Dashboard.py`)
This module provides an interactive interface for deploying and testing the trained AI coach.

**Key Features:**
- Loads the pre-trained Q-table for immediate use.
- Offers an interactive environment where users can input student parameters:
  - **Confidence**
  - **Mastery**
  - **Burnout**
- Generates personalized action strategies to optimize learning outcomes for individual students.
- Enables step-by-step guidance, making the AI coach practical for real-world educational scenarios.

### Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
