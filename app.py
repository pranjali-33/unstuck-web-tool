import streamlit as st
import os
import json
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(
    page_title="Unstuck Engine",
    page_icon="⚡",
    layout="centered"
)

# 2. Initialize official Google GenAI Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# 3. Clean, Highly Readable Header (Zero styling code to prevent font clipping)
st.title("⚡ UNSTUCK")
st.subheader("Task Allocation Engine")
st.write("---")

# 4. User-Friendly Input Layout
st.markdown("### Step 1: Log Operational Constraints")
user_dump = st.text_area(
    "What specific task or deadline is causing an execution bottleneck right now?",
    placeholder="Paste your raw mental dump, disorganized notes, or timeline pressure here...",
    height=130
)

st.write(" ")

st.markdown("### Step 2: Calibrate Execution Metrics")
col1, col2 = st.columns(2)

with col1:
    current_capacity = st.selectbox(
        "Current Capacity / Energy Score:",
        options=[
            "1 - Low Energy (Fatigued / End of day)",
            "2 - Medium Energy (Standard operational focus)",
            "3 - High Energy (Peak cognitive focus)"
        ]
    )

with col2:
    task_complexity = st.selectbox(
        "Task Complexity Score:",
        options=[
            "1 - Low Complexity (Routine / Clear steps)",
            "2 - Medium Complexity (Multi-step Process)",
            "3 - High Complexity (Ambiguous / Strategic project)"
        ]
    )

st.write(" ")

# FIX 3: Behavior Validation Signal Metric
pre_likelihood = st.slider(
    "Pre-Intervention: How likely are you to initiate this task in the next 15 minutes?",
    min_value=1,
    max_value=10,
    value=5
)

# --- THE PROPRIETARY DECISION MODEL MECHANICS ---
cap_score = int(current_capacity[0])
comp_score = int(task_complexity[0])
strategy_delta = cap_score - comp_score

if strategy_delta < 0:
    allocation_quadrant = "STRATEGIC DEEP WORK PARALYSIS"
    system_directive = "COMPLEXITY MISMATCH: High friction detected. Task architecture must be reduced."
    q_label = "STRATEGIC DEEP WORK (Friction Freeze)"
    prompt_instruction = "The system flags a capacity deficit. Decompose this task into an absurdly simple micro-task executable in under 5 minutes."
elif strategy_delta > 0:
    allocation_quadrant = "QUICK WINS / EXCESS CAPACITY"
    system_directive = "VELOCITY OPPORTUNITY: Energy reserves exceed complexity. Immediate acceleration recommended."
    q_label = "QUICK WINS (High Acceleration)"
else:
    allocation_quadrant = "BALANCED OPERATIONAL STATE"
    system_directive = "EQUILIBRIUM: Complexity matches energy. Provide a clear entry point."
    q_label = "OPERATIONAL MOMENTUM (Balanced State)"

# 5. Clean, Professional Metric Grid Layout
st.write("---")
st.markdown("### 📊 Active Framework Mapping")

# Render metrics in an elegant, structured grid layout instead of an ugly raw code block
m_col1, m_col2 = st.columns(2)
with m_col1:
    st.metric(label="Calculated Allocation Quadrant", value=q_label)
with m_col2:
    st.metric(label="Calculated Model Delta Score", value=f"{strategy_delta} (Cap vs Comp)")

# 6. Action Execution Protocol Button
st.write(" ")
if st.button("Optimize Task Allocation", type="primary", use_container_width=True):
    if not client:
        st.error("Authentication Error: API Key missing in environment.")
    elif not user_dump.strip():
        st.warning("Input Verification Failed: Please provide constraint data to analyze.")
    else:
        with st.spinner("Processing allocation formulas..."):
            try:
                system_instruction = (
                    "You are an operational language parser. Your single job is to translate messy human prose into clear execution steps. "
                    "You do not decide the strategy; the system code has already computed the allocation rules. "
                    "Output strictly raw JSON matching the schema requested. No conversational filler."
                )
                
                prompt_content = f"""
                User Input Task: "{user_dump}"
                System Computed Quadrant: {allocation_quadrant}
                System Directive: {system_directive}
                Target Strategy Rule: {prompt_instruction}
                
                Return this exact JSON schema:
                {{
                  "fact_assessment": "A concise, 1-sentence statement clarifying the actual, objective scope of the task compared to available time.",
                  "momentum_task": "A single, hyper-specific physical action step that aligns perfectly with the Target Strategy Rule.",
                  "task_rationale": "A clear, grounded explanation of why this starting point matches their current capacity score of {cap_score}."
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
                
                # Cleaned, Professional Output Cockpit using native styling parameters
                st.write("---")
                st.markdown("### ⚡ I. System Allocation Assessment")
                st.warning(f"**Model Diagnostic:** {system_directive}")
                st.info(f"**Scope Analysis:** {data['fact_assessment']}")
                
                st.markdown("### 🚀 II. Core Initialization Action")
                st.success(f"**Target Micro-Step (Execute Within 15 Minutes):**\n\n### {data['momentum_task']}")
                st.markdown(f"**Behavioral Rationale:** {data['task_rationale']}")
                
            except Exception as e:
                st.error(f"Processing Error. Technical Trace: {str(e)}")
