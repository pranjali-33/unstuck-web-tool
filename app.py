import streamlit as st
import os
import json
from google import genai
from google.genai import types

# 1. System & Page Configuration
st.set_page_config(
    page_title="Unstuck Engine",
    page_icon="⚡",
    layout="centered"
)

# Apply styling parameters cleanly using native HTML tags (Safe blocks only)
st.html("""
    <style>
    .main { background-color: #0f172a; }
    textarea { background-color: #1e293b !important; color: #f8fafc !important; border: 1px solid #334155 !important; }
    select { background-color: #1e293b !important; color: #f8fafc !important; }
    .metric-card {
        background-color: #1e293b;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        border-top: 4px solid #6366f1;
        margin-top: 20px;
    }
    .reframe-card {
        background-color: #0f172a; 
        padding: 20px; 
        border-radius: 8px; 
        border: 1px solid #1e293b;
    }
    h1, h2, h3, h4, p, label, span { color: #f8fafc !important; }
    </style>
""")

# 2. Initialize official Google GenAI Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# 3. Streamlit Native Header Section
st.title("⚡ UNSTUCK")
st.caption("STRUCTURAL TASK ALLOCATION ENGINE • MATRIX SYSTEM LOGIC")
st.write("---")

# 4. Structured Decision Inputs
user_dump = st.text_area(
    "Log Task Description and Perceived Execution Blocks:",
    placeholder="Describe the task and what is causing the initiation bottleneck...",
    height=120
)

col1, col2 = st.columns(2)
with col1:
    current_capacity = st.selectbox(
        "User Current Energy / Capacity Score:",
        ["1 - Low Energy (End of day / Fatigue)", "2 - Medium Energy (Standard operational focus)", "3 - High Energy (Peak cognitive state)"]
    )
with col2:
    task_complexity = st.selectbox(
        "Task Complexity Score:",
        ["1 - Low Complexity (Routine / Clear execution steps)", "2 - Medium Complexity (Multi-step / Disorganized)", "3 - High Complexity (Ambiguous / High strategic weight)"]
    )

# Pre-test Behavioral Signal Metric
st.write(" ")
pre_likelihood = st.slider("Pre-Intervention: How likely are you to initiate this task in the next 15 minutes? (Scale 1-10)", 1, 10, 5)

# --- THE PROPRIETARY MATHEMATICAL MODEL ---
cap_score = int(current_capacity[0])
comp_score = int(task_complexity[0])
strategy_delta = cap_score - comp_score

if strategy_delta < 0:
    allocation_quadrant = "STRATEGIC DEEP WORK PARALYSIS"
    system_directive = "COMPLEXITY MISMATCH: High friction detected. Task architecture must be aggressively stripped down to prevent executive freeze."
    q_marker = "[X] STRATEGIC DEEP WORK (Friction Freeze)"
    prompt_instruction = "The system has flagged a deficit in capacity. You must decompose this task into an absurdly simple, low-friction micro-task executable in under 5 minutes."
elif strategy_delta > 0:
    allocation_quadrant = "QUICK WINS / EXCESS CAPACITY"
    system_directive = "VELOCITY OPPORTUNITY: Low friction detected. Energy reserves exceed task complexity. Immediate acceleration recommended."
    q_marker = "[X] QUICK WINS (High Acceleration)"
else:
    allocation_quadrant = "BALANCED OPERATIONAL STATE"
    system_directive = "EQUILIBRIUM: Task complexity matches energy levels. Clear entry point required to initiate standard execution cycle."
    q_marker = "[X] OPERATIONAL MOMENTUM (Balanced)"

# 5. The Visual Matrix Grid Presentation (Using native st.code to completely eliminate TypeErrors)
st.markdown("### 📊 System Framework Mapping")
matrix_visual = f"""
         HIGH COMPLEXITY / HIGH VALUE
                     ▲
                     │
    [ ] QUICK WINS    │   {q_marker if strategy_delta < 0 else "[ ] STRATEGIC DEEP WORK"}
                     │
LOW CAPACITY ────────┼────────────────► HIGH CAPACITY
                     │
    {q_marker if strategy_delta >= 0 else "[ ] OPERATIONAL CHORES"} │   [ ] COMPLEX DISTRACTIONS
                     ▼
          LOW COMPLEXITY / ROUTINE
"""
st.code(matrix_visual, language="text")

# 6. AI Execution Protocol
if st.button("Optimize Task Allocation", type="primary"):
    if not client:
        st.error("Authentication Error: API Key missing in environment.")
    elif not user_dump.strip():
        st.warning("Input Required: Please provide task details for analysis.")
    else:
        with st.spinner("Calculating allocation vectors..."):
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
                st.write("---")
                
                # I. The Structural Resource Assessment
                st.markdown("#### ⚡ I. Structural Resource Assessment")
                st.markdown(f"""
                    <div class='reframe-card'>
                        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'><strong>CORE BLOCK:</strong> {system_directive}</p>
                        <p style='color: #f8fafc; font-size: 1rem; margin-top: 10px; margin-bottom: 0;'><strong>SCOPE ANALYSIS:</strong> {data['fact_assessment']}</p>
                    </div>
                """, unsafe_with_html=True)
                
                # II. The Target Action
                st.markdown("#### 🚀 II. Core Initialization Action")
                st.markdown(f"""
                    <div class='metric-card'>
                        <span style='font-size: 0.75rem; color: #6366f1; font-weight: bold; text-transform: uppercase;'>Calculated Next Micro-Step</span>
                        <h2 style='margin-top: 10px; margin-bottom: 15px;'>{data['momentum_task']}</h2>
                        <p style='color: #94a3b8; font-size: 0.85rem; margin: 0;'><strong>Reasoning:</strong> {data['task_rationale']}</p>
                    </div>
                """, unsafe_with_html=True)
                
            except Exception as e:
                st.error(f"Processing Fault. Trace: {str(e)}")
