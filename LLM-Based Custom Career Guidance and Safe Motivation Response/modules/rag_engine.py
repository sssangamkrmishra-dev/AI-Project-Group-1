import json
import os
import random

def load_knowledge_base():
    """Loads the synthetic knowledge base from the JSON file."""

    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, 'data', 'knowledge_base.json')
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"company_protocols": {}, "emotional_scenarios": []}

def retrieve_context(target_company, emotional_state):
    """
    RAG LOGIC:
    1. Fetches specific interview protocols for the Target Company.
    2. Fetches 'Few-Shot' examples of how to reply to the specific Emotional State.
    """
    kb = load_knowledge_base()
    
    # 1. Company Context Retrieval
    # Default to generic if company not found
    company_data = kb.get("company_protocols", {}).get(target_company, {
        "focus_areas": ["General Coding", "Soft Skills"],
        "secret_tip": "Focus on fundamentals and clarity.",
        "hiring_bar": "Standard industry bar."
    })

    # 2. Emotional Context Retrieval (Few-Shot Learning)
    # We find examples where the emotion matches the student's current state
    all_scenarios = kb.get("emotional_scenarios", [])
    relevant_scenarios = [
        s for s in all_scenarios 
        if s["emotion_label"].lower() in emotional_state.lower()
    ]
    
    # If no exact match pick random generic ones 
    if not relevant_scenarios:
        relevant_scenarios = random.sample(all_scenarios, min(3, len(all_scenarios)))
    else:
        # Limit to top 3 relevant examples 
        relevant_scenarios = relevant_scenarios[:3]

    return {
        "company_info": company_data,
        "emotional_examples": relevant_scenarios
    }