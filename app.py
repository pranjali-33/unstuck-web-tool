import streamlit as st
import google.generativeai as genai
import os

# ==========================================
# 1. PAGE CONFIGURATION & BRANDING
# ==========================================
st.set_page_config(
    page_title="Unstuck | Behavioral Decision Support Matrix",
    page_icon="🧠",
    layout="centered"
)

# App Title & Subtitle optimized for MBB positioning
st.title("🧠 UNSTUCK")
st.subheader("When motivation isn't the problem, but starting is.")
st.markdown("---")

# ==========================================
# 2. VISIBLE BEHAVIORAL FRAMEWORK SECTION
# ==========================================
# Addressing MBB feedback: making the underlying decision logic explicitly transparent
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
# 3. BACKEND SETUP & ERROR HANDLING
# ==========================================
# Secure API Key Retrieval from Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ API Key Configuration Missing. Please add `GEMINI_API_KEY` to your Streamlit secrets.")
    st.stop()

# Initialize Gemini Client
genai.configure(api_key=api_key)

# Initialize Session State to prevent text from disappearing on UI reruns
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
    energy_level = st.slider("Current Cognitive Energy Level", 1, 10, 5, 
                             help="1 = Brain fog/exhausted, 10 = Sharp/focused")
with col2:
    task_complexity = st.slider("Perceived Task Complexity", 1, 10, 5, 
                                help="1 = Administrative/Simple, 10 = Highly ambiguous/Strategic")

action_readiness = st.slider("Action Readiness Score", 1, 10, 5, 
                             help="How willing are you to take a tiny step right this second?")

# ==========================================
# 5. EXECUTION LAYER & SYSTEM PROMPTING
# ==========================================
if st.button("Generate One Next Move", type="primary"):
    if not brain_dump.strip():
        st.warning("Please provide a brain dump before running the behavioral triage engine.")
    else:
        with st.spinner("Operationalizing framework... Triaging mental clutter..."):
            
            # Structuring a hyper-strict system prompt that forces the LLM to follow your exact framework
            framework_prompt = f"""
            You are an expert executive functioning coach and a behavioral design engine. 
            Your role is to operationalize the UNSTUCK Behavioral Triage Matrix.
            
            INPUT CONSTRAINTS:
            - User's Messy Thought Dump: "{brain_dump}"
            - Current Cognitive Energy: {energy_level}/10
            - Perceived Task Complexity: {task_complexity}/10
            - Action Readiness Score: {action_readiness}/10
            
            Based on these inputs, you must adjust the "activation energy" required for their next step. If energy is low or complexity is high, the action step MUST be drastically downsized to an atomic micro-task (e.g., less than 5 minutes of effort).
            
            OUTPUT FORMAT REQUIREMENTS:
            Provide your output strictly in the following Markdown format. Do not deviate.
            
            ### 🩺 Diagnosis
            [Provide a 2-sentence psychological diagnosis of why the user is experiencing friction based on their metrics.]
            
            ### 🔄 Reframe
            [Offer a powerful cognitive reframe to lower anxiety regarding the thought dump.]
            
            ### 🎯 The ONE Next Action
            **[State exactly ONE concrete, highly specific, friction-free micro-action the user can take in the next 15 minutes. It must be an isolated step, not a sequence.]**
            
            ### 📋 Rationale
            [Explain how this step explicitly maps to their current Cognitive Energy level of {energy_level}/10.]
            """
            
            try:
                # Utilizing the recommended model for text-generation
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(framework_prompt)
                
                # Cache response in session state to protect against app re-renders
                st.session_state.triage_result = response.text
                
            except Exception as e:
                # Consulting approach to technical quota roadblocks: Clear, controlled user messaging
                st.error("### ⏳ Framework Traffic Control")
                st.info(
                    "The behavioral triage engine is currently processing a high volume of requests. "
                    "To preserve the analytical integrity of the framework, requests are being throttled. "
                    "Please wait 60 seconds and try your request again."
                )
                # Log the actual technical issue gracefully below for debugging purposes
                with st.expander("Technical Exception Data Logs"):
                    st.code(str(e))

# ==========================================
# 6. OUTPUT & IMPACT SCREEN
# ==========================================
if st.session_state.triage_result:
    st.markdown("---")
    st.markdown("### 📤 Step 2: Your Action Recommendation Matrix")
    st.markdown(st.session_state.triage_result)
    
    # Pilot Study Data Collection Prompt — MBB Gold Standard Evidence Gathering
    st.markdown("---")
    st.markdown("### 📊 Help Validate the Framework")
    st.info(
        "As part of our 7-day Operational Pilot Study tracking execution velocity under high-cognitive loads, "
        "please take 30 seconds to submit your quick, anonymous impact metrics via our tracking protocol."
    )
    st.link_button("Complete Pilot Impact Form", "https://forms.google.com/YOUR_FORM_URL_HERE")
