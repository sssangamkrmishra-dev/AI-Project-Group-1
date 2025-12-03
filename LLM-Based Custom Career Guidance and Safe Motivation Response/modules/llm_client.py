import google.generativeai as genai
import os

def generate_career_advice(student_profile, rag_context, api_key):
    """
    Constructs the prompt and calls the Gemini API.
    """
    if not api_key:
        return "Error: Please enter a valid Gemini API Key in the sidebar."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-pro")

        # --- PARSE RAG DATA ---
        company_info = rag_context['company_info']
        examples = rag_context['emotional_examples']
        
        examples_text = ""
        for ex in examples:
            examples_text += f"- User: \"{ex['user_text']}\" -> AI: \"{ex['sample_reply']}\"\n"

        # ---  PROMPT ENGINEERING  ---
        prompt = f"""
        ROLE:
        You are an elite AI Career Coach for engineering students. Your goal is to provide specific, high-value advice.

        CONTEXT - THE STUDENT:
        - Name: {student_profile['name']}
        - Target Company: {student_profile['target_company']}
        - Days to Interview: {student_profile['days_to_interview']}
        - Technical Status: {student_profile['technical_status']}
        - Recent Event: {student_profile['recent_event']}
        - DETECTED EMOTION: {student_profile['emotional_state']}

        CONTEXT - KNOWLEDGE BASE (RAG DATA):
        - Company Focus Areas: {', '.join(company_info['focus_areas'])}
        - Insider Secret: "{company_info['secret_tip']}"
        - Hiring Bar: "{company_info['hiring_bar']}"

        FEW-SHOT EXAMPLES (How to match tone):
        {examples_text}

        INSTRUCTIONS:
        1. Acknowledge the student's recent event and emotion (validate them).
        2. Provide specific advice that connects their '{student_profile['technical_status']}' to the '{student_profile['target_company']}' requirements.
        3. Use the "Insider Secret" to give them an edge.
        4. Keep it under 100 words.
        5. DO NOT be generic. Be specific to the company data provided.

        OUTPUT:
        Write the advice directly.
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"API Error: {str(e)}"