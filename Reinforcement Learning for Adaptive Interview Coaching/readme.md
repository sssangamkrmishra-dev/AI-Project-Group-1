## Author: Debargha Nath (22CS01070)


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

## 3. Installation/ How To Use
### 3.1. Clone the repo
```bash
git clone https://github.com/sssangamkrmishra-dev/AI-Project-Group-1.git
cd Reinforcement\ Learning\ for\ Adaptive\ Interview\ Coaching
```
### 3.2. Create & activate a Python virtual environment (recommended)
- macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
- Windows (cmd):
```bash
python -m venv .venv
.venv\Scripts\activate
```
### 3.3. Install dependencies
```bash
pip install -r requirement.txt
```
### 3.4. Interact With The Agent
- This command starts the trained RL agent and collects three required inputs from the user (described in the Example section below)
```bash
python3 Dashboard.py
```
## 4. Description of The Agent and The Environment

### The Agent / Placement Guide

#### Purpose  
The agent functions as a personalized placement-preparation guide. Based on the student's Confidence Level, Mastery Level, Burnout Probability.
It dynamically generates a tailored **30-day improvement plan**. The Agent interactes with the Student(Environment) and every day observes what 
are the effect of the suggested action on the state of the student and dynamically changes its strategy.

The objective is to help the student improve efficiently while maintaining a healthy balance between:

- **Skill growth/ Increase The Mastery to maximum level within 30 days**  
- **Confidence building/ Increase The confidence to maximum level within 30 days**  
- **Burnout prevention/ Keep The Burnout Probability as low as possible**

The Action Suggested by the Agents are:
* Increase difficult
* Offer Ouick Revision
* Give Encouragement
* Switch Topic
Impact of these actions are discussed in student/environment part below
---

### Input Assumptions

Before generating the plan, the student provides the following input values:

| **Parameter** | **Range** | **Meaning** |
|---------------|-----------:|------------|
| **Mastery Level** | `0 – 20` | Represents the student’s current understanding and preparedness in relevant technical and aptitude topics. |
| **Confidence Level** | `0 – 20` | Measures how confident the student feels about performing well in placement activities (interviews, coding tests, assessments). |
| **Burnout Probability** | `0.0 – 1.0` | Indicates the likelihood of mental fatigue or emotional strain. Higher values imply the need for pacing, rest days, or lighter strategies. |

---

### Output 

The agent generates a personalized **30-day adaptive plan**. Each day consists of:

- A recommended **action**  
- An **observation phase**, where the agent observes the impact of the completed action on the student's:
  - **Mastery level**
  - **Confidence level**
  - **Burnout probability**
- A **state update and prediction step**, where the agent uses the newly observed values to:
  - Update its own internal student state
  - Dynamically adjust future recommendations
  - Predict the next optimal action based on progress.
This makes the plan responsive and personalized, evolving each day based on the student's performance and well-being.
---

### The Environment/ Student

The student represents the learning environment in which the agent operates.  
Their state is defined by three evolving attributes:

- **Mastery:** Reflects current technical understanding and preparedness level.
- **Confidence:** Indicates self-belief and readiness to face placement challenges.
- **Burnout Probability:** Measures emotional strain, fatigue, or risk of losing motivation.

As the student progresses through the 30-day plan, these values change based on the recommended actions, forming the feedback loop the agent learns from.
#### Action Impact Summary

| Action | Name | Primary Effects on Student State |
|--------|-------|----------------------------------|
| `0` | **Increase Difficulty** | - Success improves **Mastery (+2)** and **Confidence (+2)**, but slightly increases **Burnout (+0.1)**. <br> - Failure reduces **Confidence (−2)** and increases **Burnout (+0.15)**. |
| `1` | **Switch Topic** | - Reduces **Burnout (−0.2)**. <br> - Slight increase in **Confidence (+1)**. |
| `2` | **Give Encouragement** | - Strong reduction in **Burnout (−0.4)**. <br> - Boosts **Confidence (+3)**. |
| `3` | **Offer Quick Revision** | - Gradually improves **Mastery (+1)**. <br> - Slightly reduces **Burnout (−0.1)**. |

### Reward:

The reward system evaluates how effective each action is in improving the student’s state. The reward is calculated using several factors:

---

*  Positive Contributions

| Component | Description | Impact on Reward |
|-----------|-------------|------------------|
| **Mastery Gain** | Increase in technical understanding | `+5.0 × mastery_gain` |
| **Confidence Gain** | Growth in self-belief | `+1.5 × confidence_gain` |
| **Burnout Reduction** | Lower stress or fatigue | `+25.0 × burn_reduction` |

---

* Special Conditions

| Condition | Action Effect | Reward Outcome |
|----------|--------------|----------------|
| Burnout was **high (> 0.7)** and agent chooses **Encouragement (action 2)** | Smart recovery step | `+50.0 bonus` |
| Burnout was **high (> 0.7)** but agent chooses any action **other than 2** | Poor decision | `−20.0 penalty` |
| Burnout becomes **extreme (> 0.9)** | Risky exhaustion | `−30.0 penalty` |
| Burnout reaches **1.0 or more** | Critical failure | `−1000.0 penalty` |

---

* Time-Based Penalty

- A small penalty is applied each step to discourage unnecessary actions:  
  `reward -= 0.05 × steps_used`

---

* End-of-Plan Bonus
When time runs out:
| Final Mastery | Outcome |
|---------------|---------|
| **≥ 16** | `+50.0 bonus` |
| **< 10** | `−50.0 penalty` |

---

## 5. Exmaple and different cases

### 5.1 Case: Low Confidence, High Mastery, Low Burnout
- Student Enter his details as input:
<img width="365" height="67" alt="Screenshot 2025-12-03 at 7 52 42 PM" src="https://github.com/user-attachments/assets/220ff645-710d-4bbb-83bc-713020ef7f65" />


- The agent outputs a recommended daily action strategy, along with a second column describing the predicted effects of that action on the student's confidence, mastery, and burnout levels.

- The updated (post-action) confidence, mastery, and burnout values will then be used to generate the strategy for the following day.
<img width="365" height="302" alt="Screenshot 2025-12-03 at 7 54 45 PM" src="https://github.com/user-attachments/assets/c1eb38ef-e481-4305-906e-df0f9a23e36f" />

* Analysis
Since the student already demonstrates strong mastery but currently has low confidence, a suitable strategy is to introduce a "topic switch" action. Because of the student's existing skill level, they are likely to perform well in the new topic, which can help build confidence through successful attempts. This approach can also continue strengthening mastery while keeping burnout low, as the change in topic may provide novelty and prevent mental fatigue.

### 5.2. Case: Low Confidence, High Mastery, High Burnout
- Student Enter his details as input:
<img width="365" height="63" alt="Screenshot 2025-12-03 at 8 07 00 PM" src="https://github.com/user-attachments/assets/72df9725-e2d7-4325-b347-1acd8f1b1ec4" />

- Output Plan:
<img width="365" height="312" alt="Screenshot 2025-12-03 at 8 05 34 PM" src="https://github.com/user-attachments/assets/6f780671-a4fe-47b2-a574-1aa8aadf0685" />

* Analysis
Since the student already demonstrates strong mastery but currently has low confidence, but also have high burnout probability .
a suitable strategy is to introduce a "topic switch", beacause new topic will lower burnout.
In output there is a series of "topic switch" action right at the beginning of a days plan, which is reasonable as we first want to lower burnout and
then increase the student's mastery and confidence.


### 5.3. Case: High Confidence, Low Mastery, Low Burnout
- Student Enter his details as input:
<img width="365" height="64" alt="Screenshot 2025-12-03 at 8 10 57 PM" src="https://github.com/user-attachments/assets/e857122b-b0b9-4957-ae69-21f11fb58262" />

- Output Plan:
<img width="365" height="268" alt="Screenshot 2025-12-03 at 8 10 36 PM" src="https://github.com/user-attachments/assets/1d7d3a44-4831-4c37-89ff-e2d8115ed5a8" />

* Analysis
Since the student Have Low Mastery agent push the student to quickly "increase difficulty".
But doing so increases burnout rapidly so the agent also provide "encouragment" to the student and suggest "switch topic".

### 5.4. Case: Low Confidence, Low Mastery, High Burnout
- Student Enter his details as input:
<img width="365" height="62" alt="Screenshot 2025-12-03 at 8 15 39 PM" src="https://github.com/user-attachments/assets/f418807d-2d08-4ffd-ac2a-4d653616e8d0" />

- Output Plan:
<img width="365" height="300" alt="Screenshot 2025-12-03 at 8 16 01 PM" src="https://github.com/user-attachments/assets/5bc3fdfc-6403-4cc3-b336-d0413530c1a4" />

* Analysis
Since the student Have Low Mastery & Low Confidence agent push the student to quickly "increase difficulty". However since he also have high burnout the agent
Now, instead of wasting a day in giving encouragement it provides the student with quick revision which increases mastery and confidence
and lower burnout.


### 5.5. Case: High Confidence, High Mastery, High Burnout
- Student Enter his details as input:
<img width="365" height="61" alt="Screenshot 2025-12-03 at 8 18 00 PM" src="https://github.com/user-attachments/assets/a5d5e43b-a004-46e8-af06-4da0ddf8d19e" />

- Output Plan:
<img width="365" height="271" alt="Screenshot 2025-12-03 at 8 18 22 PM" src="https://github.com/user-attachments/assets/18dc91a2-3a59-430b-8874-049f8178c63c" />


* Analysis
Since the student Have High Mastery and high Confidence agent suggest "increase difficulty".
But doing so increases burnout rapidly, but since the student have good mastery we can spend a day in encouraging him to reduce his high burnout. 





