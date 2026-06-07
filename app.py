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

# 2. Initialize official Google GenAI Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# 3. Clean, Human-Centric Title
st.title("⚡ UNSTUCK")
st.markdown("##### **Deconstruct the friction. Find your entry point.**")
st.write("---")

# 4. Step 1: Input Section
st.markdown("### **Step 1: What are you actively avoiding?**")
user_dump = st.text_area(
    "Be brutally honest. What is the actual task, and what is the current execution bottleneck?",
    placeholder="e.g., 'I need to build this slide deck but I'm completely overwhelmed by the raw data and don't know where to start...'",
    height=130,
    label_visibility="collapsed"
)

st.write(" ")

# 5. Step 2: Diagnostic Calibration
st.markdown("### **Step 2: Reality Check**")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Your actual energy level right now:**")
    current_capacity = st.selectbox(
        "Energy Selection",
        options=[
            "1 - Running on fumes (Fried / Exhausted)",
            "2 - Normal operational capacity (Standard day)",
            "3 - Highly focused (Locked in / Peak clarity)"
        ],
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**How heavy does the task feel?**")
    task_complexity = st.selectbox(
        "Complexity Selection",
        options=[
            "1 - Lightweight (Routine / Clear formatting)",
            "2 - Medium heavy (Messy / Needs thinking)",
            "3 - Intimidating (Ambiguous / High pressure)"
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

# --- INTERNAL MODEL MECHANICS (Processed automatically behind the scenes) ---
cap_score = int(current_capacity[0])
comp_score = int(task_complexity[0])
strategy_delta = cap_score - comp_score

# Grounded, direct status messaging matching your core behavioral model rules
if strategy_delta < 0:
    allocation_quadrant = "STRATEGIC DEEP WORK PARALYSIS"
    vibe_heading = "Friction Freeze"
    vibe_message = "You're trying to climb a mountain on an empty tank. Because the task complexity outpaces your current energy, your brain is actively hitting the brakes. We are overriding this freeze by aggressively slicing the task down into an absurdly simple, 5-minute physical action step."
    prompt_instruction = "The system flags a capacity deficit. Break this down into an absurdly simple micro-task executable in under 5 minutes."
elif strategy_delta > 0:
    allocation_quadrant = "QUICK WINS / EXCESS CAPACITY"
    vibe_heading = "High Velocity Lane"
    vibe_message = "You have plenty of fuel and a clear road ahead. Your energy outmatches the baseline friction of this task. Let's take immediate advantage of this cognitive window and get a high-momentum action item locked down right now."
    prompt_instruction = "The user has high energy relative to the task. Give them an immediate, high-momentum starting action."
else:
    allocation_quadrant = "BALANCED OPERATIONAL STATE"
    vibe_heading = "Clear Entry Point Needed"
    vibe_message = "You actually have exactly what it takes to execute this task right now—your energy matches the weight perfectly. You aren't stuck because you're tired; you're just stuck at the starting threshold. Let's isolate your exact opening sequence."
    prompt_instruction = "Energy and complexity match perfectly. Provide a clean, logical first step to initiate focus."

# 6. Dynamic Diagnostics Container
st.write("---")
with st.container(border=True):
    st.markdown(f"#### **System Diagnosis: {vibe_heading}**")
    st.write(vibe_message)

# 7. Optimization Action Trigger
st.write(" ")
if st.button("Give Me My First Action Step", type="primary", use_container_width=True):
    if not client:
        st.error("Authentication Error: API Key missing in dashboard settings.")
    elif not user_dump.strip():
        st.warning("Please dump your raw thoughts in Step 1 first so we can map out your action step.")
    else:
        with st.spinner("Cutting through the friction..."):
            try:
                system_instruction = (
                    "You are an operational language parser. Your single job is to translate messy human prose into clear execution steps. "
                    "You do not decide the strategy; the system code has already computed the allocation rules. "
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
                
                # Polished, Non-Truncated Action Roadmap Presentation
                st.write("---")
                st.markdown("### **⚡ Your Momentum Roadmap**")
                
                with st.container(border=True):
                    st.markdown("##### **The Reality Check**")
                    st.write(data['fact_assessment'])
                    st.write(" ")
                    
                    st.markdown("##### **Your Next 15-Minute Micro-Step**")
                    st.info(data['momentum_task'])
                    st.write(" ")
                    
                    st.markdown("##### **Why This Works Right Now**")
                    st.caption(data['task_rationale'])
            
            # DEFENSIVE OVERLOAD HANDLING: Catches rate caps beautifully
            except APIError as api_err:
                if "429" in str(api_err) or "RESOURCE_EXHAUSTED" in str(api_err):
                    st.write("---")
                    st.warning(
                        "**Server Traffic Intercept**\n\n"
                        "A few alpha testers are pushing momentum calculations at the exact same moment. "
                        "Because we are on the public tier, the server is cooling down. "
                        "Please wait exactly 60 seconds and click 'Give Me My First Action Step' again."
                    )
                else:
                    st.error(f"API Connection Error: {str(api_err)}")
            except Exception as e:
                st.error(f"System Error: {str(e)}")
