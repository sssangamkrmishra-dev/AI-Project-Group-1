# Module 5: LLM-Based Custom Career Guidance & Safe Motivation Response

**Author:** Utkarsh Singh (22CS01075)  
**Live Demo:** *Click Here to Launch AI Coach*  
**Tech Stack:** Python, Streamlit, Google Gemini 2.5 Pro, RAG (Retrieval Augmented Generation)

---

## 📌 Project Overview

This module serves as the **“Voice”** of the AI Placement System.  
While upstream mathematical models (Bayesian Networks, RL) estimate readiness, risks, and weaknesses,  
**Module-5 converts those numbers into empathetic, actionable, and psychologically safe career advice.**  

A specialized **Safety-First Architecture** ensures:

- Burnout detection  
- Prevention of toxic positivity  
- Tone adaptation based on emotional state  
- Company-specific guidance through RAG  
- Realistic, evidence-based coaching

---

## 🏗️ System Architecture

The system follows a **7-step pipeline**:

1. **Input Reception**  
   Receives student metadata (emotion, target company, weaknesses).

2. **RAG Retrieval**  
   Pulls relevant insights from `knowledge_base.json`  
   (Amazon LPs, Google bar-raiser patterns, anxiety protocols, etc.).

3. **Prompt Augmentation**  
   Injects retrieved snippets into a dynamic hybrid system prompt.

4. **LLM Inference**  
   Uses **Google Gemini 2.5 Pro** to generate tailored guidance.

5. **Safety Reflexion**  
   `safety_check.py` scans for unsafe patterns  
   (burnout triggers, unrealistic promises, harmful motivation).

6. **Tone Controller**  
   Adjusts output tone (Consoling, Neutral, Challenging).

7. **Output Delivery**  
   Final validated response is displayed on the Streamlit dashboard.

> For detailed diagrams, refer to **Module_5_Report.pdf**

---

## 📂 Project Structure

```plaintext
placement_ai_system/
│
├── data/
│   ├── knowledge_base.json       # Synthetic Knowledge (Company Secrets, Interview Tips)
│   └── student_input.json        # Simulated Student Profiles (Edge Cases)
│
├── modules/
│   ├── __init__.py
│   ├── rag_engine.py             # Logic to retrieve specific tips based on metadata
│   ├── llm_client.py             # Gemini 2.5 Pro Client & Prompt Engineering
│   └── safety_check.py           # Reflexion Logic (Burnout Circuit Breaker)
│
├── app.py                        # Streamlit Frontend Dashboard
├── requirements.txt              # Project Dependencies
└── README.md                     # Documentation


modules/safety_check.py: Implements the "Circuit Breaker" safety logic.

modules/llm_client.py: Manages Prompt Engineering and API calls.
