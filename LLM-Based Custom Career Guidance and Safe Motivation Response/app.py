import streamlit as st
import json
import os
from modules.rag_engine import retrieve_context
from modules.llm_client import generate_career_advice
from modules.safety_check import check_safety

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Placement Coach", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_students():
    with open('data/student_input.json', 'r') as f:
        return json.load(f)

students = load_students()

# --- SIDEBAR ---
st.sidebar.title("⚙️ Control Panel")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
st.sidebar.info("Get key from: aistudio.google.com")

st.sidebar.markdown("---")
st.sidebar.header("Select Student Profile")
# Create a mapping of Name -> Student Object
student_names = [s['name'] for s in students]
selected_name = st.sidebar.selectbox("Choose a student to simulate:", student_names)

# Get the full student object
student = next(s for s in students if s['name'] == selected_name)

# --- MAIN LAYOUT ---
st.title("🎓 LLM-Based Personalized Career Guidance")
st.markdown(f"**Module 5 Prototype** | Target: {student['target_company']} | Days Left: {student['days_to_interview']}")

# Display Student "Card"
col1, col2, col3 = st.columns(3)
with col1:
    st.error(f"❤️ Emotion: {student['emotional_state']}")
with col2:
    st.warning(f"🛠 Tech Status: {student['technical_status']}")
with col3:
    st.info(f"📅 Recent Event: {student['recent_event']}")

st.markdown("---")

# --- GENERATION LOGIC ---
if st.button("Generate AI Guidance", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar to proceed.")
    else:
        with st.spinner("🤖 AI is thinking... (Retrieving RAG data + Generating + Checking Safety)"):
            
            # 1. RAG Retrieval
            rag_context = retrieve_context(student['target_company'], student['emotional_state'])
            
            # 2. LLM Generation
            raw_advice = generate_career_advice(student, rag_context, api_key)
            
            # 3. Safety Layer (Reflexion)
            is_safe, final_advice, safety_logs = check_safety(student, raw_advice)

        # --- DISPLAY RESULTS ---
        
        # Section A: The Final Output (User View)
        st.subheader("💬 AI Coach Response")
        st.success(final_advice)

        # Section B: The "Behind the Scenes" (For Project Demo)
        st.markdown("---")
        st.subheader("🧠 System Internals (Project Justification)")
        
        tab1, tab2, tab3 = st.tabs(["📚 RAG Retrieval", "🛡️ Safety Logs", "📝 Raw Prompt Data"])
        
        with tab1:
            st.write("The system retrieved this 'Secret Knowledge' to ground the advice:")
            st.json(rag_context['company_info'])
            st.write("**Few-Shot Examples Used for Tone Matching:**")
            st.json(rag_context['emotional_examples'])
            
        with tab2:
            st.write("Safety Layer Execution Trace:")
            for log in safety_logs:
                if "CRITICAL" in log:
                    st.error(log)
                elif "VIOLATION" in log:
                    st.warning(log)
                else:
                    st.success(log)
                    
        with tab3:
            st.write("The raw data injected into the LLM:")
            st.json(student)

else:
    st.info("Click the button above to generate advice based on the student's state.")