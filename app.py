import streamlit as st
import os
import json
import time
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

# 3. Clean Main Header
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

# 5. Step 2: Realistic Resource Check
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

# --- INTERNAL MODEL MECHANICS ---
cap_score = int(current_capacity[0])
comp_score = int(task_complexity[0])
strategy_delta = cap_score - comp_score

if strategy_delta < 0:
    allocation_quadrant = "STRATEGIC DEEP WORK PARALYSIS"
    prompt_instruction = "The system flags a capacity deficit. Break this down into an absurdly simple micro-task executable in under 5 minutes."
elif strategy_delta > 0:
    allocation_quadrant = "QUICK WINS / EXCESS CAPACITY"
    prompt_instruction = "The user has high energy relative to the task. Give them an immediate, high-momentum starting action."
else:
    allocation_quadrant = "BALANCED OPERATIONAL STATE"
    prompt_instruction = "Energy and complexity match perfectly. Provide a clean, logical first step to initiate focus."

# 6. Action Optimization Button
st.write(" ")
if st.button("Give Me My First Action Step", type="primary", use_container_width=True):
    if not client:
        st.error("Authentication Error: API Key missing in dashboard settings.")
    elif not user_dump.strip():
        st.warning("Please enter your task details in Step 1 first so we can map out your entry point.")
    else:
        with st.spinner("Connecting to framework engine..."):
            
            system_instruction = (
                "You are an operational language parser. Your single job is to translate messy human prose into clear execution steps. "
                "Output strictly raw JSON matching the schema requested. No conversational filler."
            )
            
            prompt_content = f"""
            User Input Task: "{user_dump}"
            System Computed Quadrant: {allocation_quadrant}
            Target Strategy Rule: {prompt_instruction}
            
            Return this exact JSON schema:
            {{
              "fact_assessment": "A concise, 1-sentence statement clarifying the actual, objective scope of the task compared to available time.",
              "momentum_task": "A single, hyper-specific physical action step that aligns perfectly with the Target Strategy Rule.",
              "task_rationale": "A clear, grounded explanation of why this starting point matches their current capacity score of {cap_score}."
            }}
            """
            
            response_text = None
            max_retries = 3
            delay = 2  # Start with a 2-second pause if server is busy
            
            # Smart Retry Loop
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt_content,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            response_mime_type="application/json",
                            temperature=0.1
                        ),
                    )
                    response_text = response.text
                    break  # Success! Break out of the loop.
                except APIError as api_err:
                    if ("429" in str(api_err) or "RESOURCE_EXHAUSTED" in str(api_err)) and attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= 2  # Wait longer on the next try (2s, then 4s)
                    else:
                        st.error("The network is exceptionally busy right now. Please try clicking once more.")
                        st.stop()
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")
                    st.stop()
            
            if response_text:
                try:
                    data = json.loads(response_text)
                    
                    # Render Response Dashboard
                    st.write("---")
                    st.markdown("### **⚡ Your Action Roadmap**")
                    
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
                except Exception as parse_err:
                    st.error("Engine formatting anomaly. Please resubmit.")
