import streamlit as st
from openai import OpenAI
import os

# ==========================================
# 1. PAGE CONFIGURATION & BRANDING
# ==========================================
st.set_page_config(
    page_title="Unstuck | Behavioral Decision Support Matrix",
    page_icon="🧠",
    layout="centered"
)

# MBB-Optimized Positioning
st.title("🧠 UNSTUCK")
st.subheader("When motivation isn't the problem, but starting is.")
st.markdown("---")

# ==========================================
# 2. VISIBLE BEHAVIORAL FRAMEWORK SECTION
# ==========================================
with st.expander("🔬 View Underlying Behavioral Triage Engine", expanded=True):
    st.markdown("""
    **Unstuck** is an AI-operationalized behavioral framework designed to bypass executive dysfunction by neutralizing choice paralysis.
    
    ### The 4-Step Triage Process:
    1. **Capacity Assessment:** Quantifies your current neurological and cognitive energy limits.
    2. **Complexity Triage:** Deconstructs a high-friction mental thought-dump.
    3. **Size Matching:** Translates the workload down to a size smaller than or equal to your current energy.
    4. **Momentum Activation:** Recommends exactly **ONE** isolated micro-action to break inertia.
    """)

st.markdown("---")

# ==========================================
# 3. BACKEND SETUP & SDK INITIALIZATION
# ==========================================
# Secure API Key Retrieval from Streamlit Secrets or Environment Variables
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ API Key Configuration Missing. Please add `OPENAI_API_KEY` to your Streamlit secrets.")
    st.stop()

# Initialize the official OpenAI Client
client = OpenAI(api_key=api_key)

# Initialize Session State to lock results on screen
if "triage_result" not in st.session_state:
    st.session_state.triage_result = None

# ==========================================
# 4. USER INPUT LAYER (The Metrics Matrix)
# ==========================================
st.markdown("### 📥 Step 1: Input Your Current Cognitive Matrix")

brain_dump = st.text_area(
    "Mental Thought Dump / Messy Notes",
    placeholder="Type everything stressing you out right now. Don't organize it—let the tool handle the triage.",
    height=150
)

col1, col2 = st.columns(2)

with col1:
    energy_level = st.selectbox(
        "Current Cognitive Energy Level",
        ["1 - Total Burnout / Brain Fog", "2 - Low Capacity", "5 - Normal Focus", "8 - High Energy", "10 - Peak Performance"],
        index=2
    )
with col2:
    task_complexity = st.selectbox(
        "Perceived Task Complexity",
        ["1 - Lightweight / Routine", "5 - Moderate Effort", "10 - Highly Strategic / Ambiguous"],
        index=1
    )

action_readiness = st.slider("Honesty check: What are the odds you actually start this in the next 15 minutes? (1-10)", 1, 10, 5)

# ==========================================
# 5. EXECUTION LAYER & OPENAI INTERFACE
# ==========================================
if st.button("Give Me My First Action Step", type="primary"):
    if not brain_dump.strip():
        st.warning("Please provide a brain dump before running the behavioral triage engine.")
    else:
        with st.spinner("Operationalizing framework... Triaging mental clutter..."):
            
            framework_prompt = f"""
            You are an expert executive functioning coach and a behavioral design engine. 
            Your role is to operationalize the UNSTUCK Behavioral Triage Matrix.
            
            INPUT CONSTRAINTS:
            - User's Messy Thought Dump: "{brain_dump}"
            - Current Cognitive Energy: {energy_level}
            - Perceived Task Complexity: {task_complexity}
            - Action Readiness Score: {action_readiness}/10
            
            OUTPUT FORMAT REQUIREMENTS:
            Provide your output strictly in the following Markdown format:
            
            ### 🩺 Diagnosis
            [Provide a 2-sentence psychological diagnosis of why the user is experiencing friction.]
            
            ### 🔄 Reframe
            [Offer a powerful cognitive reframe to lower anxiety regarding the thought dump.]
            
            ### 🎯 The ONE Next Action
            **[State exactly ONE concrete, highly specific, friction-free micro-action the user can take in the next 15 minutes.]**
            
            ### 📋 Rationale
            [Explain how this step explicitly maps to their current energy level.]
            """
            
            try:
                # Production API Call using high-efficiency gpt-4o-mini
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a specialized behavioral design engine that outputs clean, structured markdown based precisely on the framework requirements requested."},
                        {"role": "user", "content": framework_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=600
                )
                
                # Direct extraction via SDK object structure
                output_text = response.choices[0].message.content
                st.session_state.triage_result = output_text
                
            except Exception as e:
                st.error("### ⏳ Framework Traffic Control")
                st.info(
                    "The behavioral triage engine encountered a processing interruption. "
                    "Please confirm your API balance status or click the execution button once more."
                )

# ==========================================
# 6. OUTPUT SCREEN
# ==========================================
if st.session_state.triage_result:
    st.markdown("---")
    st.markdown("### 📤 Step 2: Your Action Recommendation Matrix")
    st.markdown(st.session_state.triage_result)
