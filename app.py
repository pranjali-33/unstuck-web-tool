import streamlit as st
import os
import json
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. Page Configuration
st.set_page_config(
    page_title="Unstuck Engine",
    page_icon="⚡",
    layout="centered"
)

# 2. Server Shield Connection
@st.cache_resource
def get_genai_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return None

client = get_genai_client()

# 3. Interface Header
st.title("⚡ UNSTUCK")
st.write("---")

# 4. Step 1: Input Box
st.markdown("### **Step 1: What task is on your plate right now?**")
user_dump = st.text_area(
    "Task Input Box",
    placeholder="What project, file, or decision are you trying to tackle? Jot down the details or your raw thoughts here...",
    height=130,
    label_visibility="collapsed"
)

st.write(" ")

# 5. Step 2: Reality Check Matrix
st.markdown("### **Step 2: Reality Check**")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Your mental battery right now:**")
    current_capacity = st.selectbox(
        "Energy Selection",
        options=[
            "1 - Running on fumes (Tired / Exhausted)",
            "2 - Normal capacity (Standard operational focus)",
            "3 - Highly focused (Ready to work but directionless)"
        ],
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**Perceived task weight:**")
    task_complexity = st.selectbox(
        "Complexity Selection",
        options=[
            "1 - Lightweight (Straightforward / Routine steps)",
            "2 - Medium heavy (Messy scope / Needs thinking)",
            "3 - Intimidating (Vague / High stakes project)"
        ],
        label_visibility="collapsed"
    )

st.write(" ")
st.markdown("**Honesty check: What are the odds you actually start this in the next 15 minutes?**")
pre_likelihood = st.slider(
    "Probability Slider",
    min_value=1,
    max_value=10,
    value=5,
    label_visibility="collapsed"
)

# =====================================================================
# 🧠 THE STRATEGIC INTERVIEW EMPOWERMENT LAYER (70% HARDCODED FRAMEWORK)
# =====================================================================
cap_score = int(current_capacity[0])
comp_score = int(task_complexity[0])

# Explicit Matrix Rules engineered by YOU. No LLM black box logic here.
if cap_score == 1 and comp_score == 3:
    chosen_strategy = "MICRO-TASK DECOMPOSITION"
    framework_directive = "Break the task down into a tiny, absurdly simple micro-action that takes under 5 minutes to beat procrastination."
elif cap_score == 3 and comp_score == 1:
    chosen_strategy = "HIGH-VELOCITY MOMENTUM SPRINT"
    framework_directive = "Leverage peak energy to run a rapid 10-minute sprint and completely clear this off the plate."
elif cap_score >= comp_score:
    chosen_strategy = "IMMEDIATE PROGRESSIVE INITIALIZATION"
    framework_directive = "Isolate the absolute first structural step or row of data and execute it immediately."
else:
    chosen_strategy = "SCOPE RE-ANCHORING"
    framework_directive = "Energy is low relative to complexity. Reduce the operational scope by half and outline just one milestone."

# 6. Action Optimization Button
st.write(" ")
if st.button("Give Me My First Action Step", type="primary", use_container_width=True):
    if not client:
        st.error("Authentication Error: API Key missing in dashboard settings.")
    elif not user_dump.strip():
        st.warning("Please enter your task details in Step 1 first.")
    else:
        with st.spinner("Operationalizing framework matrix..."):
            try:
                # The LLM is strictly used as a 30% linguistic translator
                system_instruction = (
                    "You are a behavioral linguistics optimizer. Your single job is to translate raw user tasks into natural, actionable phrases based on strict structural rules. "
                    "Output strictly raw JSON matching the schema requested. No filler conversational prose."
                )
                
                prompt_content = f"""
                Raw User Input: "{user_dump}"
                
                Our hardcoded behavioral framework has already evaluated the user's capacity metrics and determined the following:
                - Selected Strategy Group: {chosen_strategy}
                - Execution Rule: {framework_directive}
                
                Generate a response that maps the Raw User Input directly onto our Execution Rule.
                
                Return this exact JSON schema:
                {{
                  "fact_assessment": "A clear 1-sentence statement contextualizing their input against their current energy state.",
                  "momentum_task": "A single, hyper-specific physical action step that executing the template directive exactly.",
                  "task_rationale": "An explainable behavioral science reason why this specific action fits a strategy of {chosen_strategy}."
                }}
                """
                
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.1
                    ),
                )
                
                data = json.loads(response.text)
                
                # Render Response Dashboard
                st.write("---")
                st.markdown(f"### **⚡ Framework Assessment: {chosen_strategy}**")
                
                with st.container(border=True):
                    out_col1, out_col2 = st.columns([1, 2])
                    
                    with out_col1:
                        st.markdown("**THE REALITY CHECK**")
                    with out_col2:
                        st.write(data['fact_assessment'])
                        
                    st.write("---")
                    
                    with out_col1:
                        st.markdown("**THE 15-MIN ACTION**")
                    with out_col2:
                        st.info(f"**{data['momentum_task']}**")
                        
                    st.write("---")
                    
                    with out_col1:
                        st.markdown("**METHODOLOGY WHY**")
                    with out_col2:
                        st.write(data['task_rationale'])
            
            except APIError as api_err:
                st.error("The network is exceptionally busy right now. Please click the button once more.")
            except Exception as e:
                st.error("System structural optimization processing. Please retry.")
