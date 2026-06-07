import streamlit as st
import os
import json
from google import genai
from google.genai import types

# 1. Custom Premium Aesthetic Styling
st.set_page_config(
    page_title="Unstuck Engine",
    page_icon="⚡",
    layout="centered"
)

# Apply styling parameters cleanly without using multi-line triple quote blocks
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
    .matrix-display {
        font-family: monospace;
        background-color: #020617;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #1e293b;
        color: #94a3b8;
        line-height: 1.2;
    }
    h1, h2, h3, h4, p, label, span { color: #f8fafc !important; }
    </style>
""")

# 2. Initialize official Google GenAI Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# 3. Premium Header Section
st.markdown("<h1 style='text-align: center;'>⚡ UNSTUCK</h1>", unsafe_with_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; letter-spacing: 0.1em; text-transform: uppercase; font-size: 0.8rem;'>Cognitive Velocity Engine • Ver. 2.0</p>", unsafe_with_html=True)
st.write("---")

# 4. Structured Decision Inputs
user_dump = st.text_area(
    "Log Operational Constraints / Mental Dump:",
    placeholder="What exactly is the bottleneck? Paste raw notes or schedule conflict details...",
    height=150
)

col1, col2 = st.columns(2)
with col1:
    task_category = st.selectbox(
        "Context Domain:",
        ["Professional / Work", "Academic / Case Prep", "Personal Administration"]
    )
with col2:
    cognitive_weight = st.selectbox(
        "Perceived Complexity:",
        ["Low (Routine Execution)", "Medium (Multi-step Process)", "High (Strategic Ambiguity)"]
    )

# 5. The Visual Matrix (Interactive Framework Logic)
st.markdown("### 📊 Active Framework Mapping")

# Logic to highlight the current quadrant in the matrix
q1, q2, q3, q4 = "  ", "  ", "  ", "  "
if "High" in cognitive_weight:
    q2 = "▣" # Strategic Deep Work
elif "Low" in cognitive_weight:
    q1 = "▣" # Quick Wins
else:
    q3 = "▣" # Operational Momentum

matrix_visual = f"""
         HIGH VALUE / STRATEGIC IMPACT
                     ▲
                     │
    {q1} QUICK WINS    │   {q2} STRATEGIC DEEP WORK
    (Low Friction)   │   (High Friction)
                     │
LOW FRICTION ────────┼────────────────► HIGH FRICTION
                     │
    {q3} OPERATIONAL  │   {q4} COMPLEX
         MOMENTUM    │        DISTRACTIONS
                     ▼
          LOW VALUE / TACTICAL NOISE
"""
st.markdown(f"<div class='matrix-display'><pre>{matrix_visual}</pre></div>", unsafe_with_html=True)

# 6. AI Execution Protocol
if st.button("Execute Framework Optimization", type="primary"):
    if not client:
        st.error("Authentication Error: API Key missing in environment.")
    elif not user_dump.strip():
        st.warning("Input Required: Please provide task details for analysis.")
    else:
        with st.spinner("Decoding cognitive variables..."):
            try:
                system_instruction = (
                    "You are a behavioral data analyst for a performance consulting firm. "
                    "Analyze the user's unstructured input through the lens of cognitive friction. "
                    "Strip emotional noise. Output strictly raw JSON. No conversational text."
                )
                
                prompt_content = f"""
                User Input: "{user_dump}"
                Context: {task_category} | Perceived Load: {cognitive_weight}
                
                Return this JSON schema:
                {{
                  "fact_assessment": "One clinical, objective sentence summarizing the time/resource reality.",
                  "cognitive_shift": "A directive to shift focus to the immediate window of capacity.",
                  "momentum_task": "One single, hyper-specific micro-action to start within 15 minutes.",
                  "clinical_rationale": "Why this task specifically bypasses executive dysfunction given the load."
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
                
                # I. The Clinical Blueprint
                st.markdown("#### ⚡ I. System Reframe")
                st.markdown(f"""
                    <div style='background-color: #0f172a; padding: 20px; border-radius: 8px; border: 1px solid #1e293b;'>
                        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'><strong>ASSESSMENT:</strong> {data['fact_assessment']}</p>
                        <p style='color: #f8fafc; font-size: 1rem; margin-top: 10px; margin-bottom: 0;'><strong>DIRECTIVE:</strong> {data['cognitive_shift']}</p>
                    </div>
                """, unsafe_with_html=True)
                
                # II. The Target Action
                st.markdown("#### 🚀 II. Initialization Vector")
                st.markdown(f"""
                    <div class='metric-card'>
                        <span style='font-size: 0.75rem; color: #6366f1; font-weight: bold; text-transform: uppercase;'>Primary Momentum Task</span>
                        <h2 style='margin-top: 10px; margin-bottom: 15px; color: #ffffff !important;'>{data['momentum_task']}</h2>
                        <p style='color: #94a3b8; font-size: 0.85rem; font-style: italic; margin: 0;'><strong>Rationale:</strong> {data['clinical_rationale']}</p>
                    </div>
                """, unsafe_with_html=True)
                
            except Exception as e:
                st.error(f"Processing Fault. Trace: {str(e)}")
