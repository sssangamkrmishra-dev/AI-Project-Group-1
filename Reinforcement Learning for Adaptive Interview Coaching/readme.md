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
## Features

- **Student Environment (`Student.py`)**  
  - Simulates a student's state with attributes:
    - Confidence: 0–20
    - Mastery: 0–20
    - Burnout: 0.0–1.0
    - Time left: 30 days  
  - Handles state transitions based on AI actions.

- **RL Agent (`QLearningAgent.py`)**  
  - Q-Learning agent with epsilon-greedy exploration.
  - Learns optimal actions to maximize student progress while managing burnout.
  - Can save and load trained Q-tables.

- **Trainer (`trainer.py`)**  
  - Trains the agent through multiple simulations.
  - Saves the learned Q-table for future use.

- **Serve (`serve.py`)**  
  - Interactive interface to test the trained AI coach.
  - Users can input student parameters and see step-by-step recommendations.

---

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
