def check_safety(student_profile, advice_draft):
    """
    Implements Safety Guardrails and Reflexion.
    Returns: (is_safe (bool), modified_advice (str), log (str))
    """
    logs = []
    
    # --- LAYER 1: THE BURNOUT CASE---
    # If the student is in a critical state  we override the LLM entirely.
    critical_states = ["burnout", "depression", "hopeless", "panic"]
    state = student_profile.get("emotional_state", "").lower()
    
    for flag in critical_states:
        if flag in state:
            logs.append(f" CRITICAL STATE DETECTED: '{flag}'. Activating Mental Health Protocol.")
            safe_reply = (
                f"I hear that you are feeling {state}. Please pause your preparation right now. "
                "Your mental health is more important than any job. Take the rest of the day off "
                "to sleep or do something non-technical. We can reassess tomorrow."
            )
            return False, safe_reply, logs

    # --- LAYER 2: TOXIC POSITIVITY and FALSE PROMISES FILTER ---
    # We scan the draft for dangerous phrases.
    unsafe_phrases = [
        "guaranteed job", "you will definitely get placed", 
        "just work harder", "don't be lazy", "100% success"
    ]
    
    for phrase in unsafe_phrases:
        if phrase in advice_draft.lower():
            logs.append(f" SAFETY VIOLATION: Found banned phrase '{phrase}'. Rewriting...")
            # Simple rule-based rewrite for the demo
            advice_draft = advice_draft.replace(phrase, "this improves your chances")
            advice_draft += " (Revised for realism)."
            return True, advice_draft, logs

    logs.append(" Safety Check Passed. No toxic content found.")
    return True, advice_draft, logs