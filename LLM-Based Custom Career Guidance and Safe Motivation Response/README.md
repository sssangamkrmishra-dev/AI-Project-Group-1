Module 5: LLM-Based Custom Career Guidance

This module acts as the "Voice" of the AI placement system. It takes data from the Bayesian Network (simulated via JSON) and generates personalized, safe, and company-specific advice.

Features

RAG (Retrieval Augmented Generation): Retrieves specific interview secrets (Amazon Leadership Principles, etc.) based on the user's target.

Safety Guardrails: Detects "Burnout" and forces a mental health break override.

Reflexion: Checks for toxic positivity or false promises.

Few-Shot Prompting: Adapts tone based on emotional state.

Setup

Install dependencies:

pip install -r requirements.txt


Run the app:

streamlit run app.py


Enter your Google Gemini API Key in the sidebar.

Project Structure

data/: Contains synthetic student profiles and company knowledge base.

modules/rag_engine.py: Handles context retrieval.

modules/safety_check.py: Implements the "Circuit Breaker" safety logic.

modules/llm_client.py: Manages Prompt Engineering and API calls.