import streamlit as st
import os
import json
from google import genai
from google.genai import types

# 1. Standard Page Setup
st.set_page_config(
    page_title="Unstuck Engine",
    page_icon="⚡",
    layout="centered"
)

# 2. Initialize official Google GenAI Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# 3. Clean & Welcoming Header
st.title("⚡ UNSTUCK")
st.markdown("##### *Your personal momentum generator when you're staring at a blank screen.*")
st.write("---")

# 4. Step 1: Getting the User's Problem
st.markdown("### ✍️ Step 1: Brain Dump")
user_dump = st.text_area(
    "What specific task, project, or deadline is keeping you stuck right now?",
    placeholder="Type or paste what you're working on, raw thoughts, or what you are avoiding...",
    height=130,
    label_visibility="collapsed"
)

st.write(" ")

# 5. Step 2: Checking the Vibe
st.markdown("### 📊 Step 2: Check Your Battery & Task")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Your Current Energy Level:**")
    current_capacity = st.selectbox(
        "Energy Selection",
        options=[
            "1 - Low Energy (Feeling fried / End of the day)",
            "2 - Medium Energy (Standard operational focus)",
            "3 - High Energy (Peak mental clarity / Locked in)"
        ],
        label_visibility="collapsed"
    )

with col2:
    st.markdown("**How Heavy is the Task?**")
    task_complexity = st.selectbox(
        "Complexity Selection",
        options=[
            "1 - Light (Routine / Clear next steps)",
            "2 - Medium (Multi-step project / A bit messy)",
            "3 - Heavy (Vague / Requires deep strategic focus)"
        ],
        label_visibility="collapsed"
    )

st.write(" ")
st.markdown("**Before we optimize, let's lock in a baseline:**")
pre_likelihood = st.slider(
    "On a scale of 1-10, how likely are you to actually start this task in the next 15 minutes?",
    min_value=1,
    max_value=10,
    value=5
)

# --- BACKEND BRAIN (Hidden from user, processed automatically) ---
cap_score = int(current_capacity[0])
comp_score = int(task_complexity[0])
strategy_delta = cap_score - comp_score

# Dynamic messaging with a supportive, clear personality
if strategy_delta < 0:
    allocation_quadrant = "STRATEGIC DEEP WORK PARALYSIS"
    vibe_heading = "🚨 Friction Freeze Alert!"
    vibe_message = "You are trying to climb a mountain on an empty tank. Because your energy is lower than the task weight, your brain is freezing up. We are forcing the system to chop this down into a tiny, 5-minute action step to get you moving."
    prompt_instruction = "The system flags a capacity deficit. Break this down into an absurdly simple micro-task executable in under 5 minutes."
elif strategy_delta > 0:
    allocation_quadrant = "QUICK WINS / EXCESS CAPACITY"
    vibe_heading = "🚀 Clear Skies Ahead!"
    vibe_message = "You've got plenty of fuel and a clear road. Your energy levels are higher than the friction of this task. Let’s strike while the iron is hot and get an immediate momentum step on the board."
    prompt_instruction = "The user has high energy relative to the task. Give them an immediate, high-momentum starting action."
else:
    allocation_quadrant = "BALANCED OPERATIONAL STATE"
    vibe_heading = "⚖️ Perfect Balance."
    vibe_message = "You are completely in sync. Your energy matches the complexity perfectly—you just need a clear, logical doorway to walk through. Let's find your exact starting point."
    prompt_instruction = "Energy and complexity match perfectly. Provide a clean, logical first step to initiate focus."

# 6. Step 3: Clean, Friendly Vibe Diagnostic Box
st.write("---")
with st.container(border=True):
    st.markdown(f"### {vibe_heading}")
    st.write(vibe_message)

# 7. Action Optimization Button
st.write(" ")
if st.button("Generate My Next Move", type="primary", use_container_width=True):
    if not client:
        st.error("Authentication Error: API Key missing in environment.")
    elif not user_dump.strip():
        st.warning("Please type something in Step 1 so we can build your action step!")
    else:
        with st.spinner("Analyzing your parameters..."):
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
                
                # Friendly, Motivational Output Design
                st.write("---")
                st.markdown("### ⚡ Your Custom Action Plan")
                
                with st.container(border=True):
                    st.markdown("#### **🔍 The Reality Check**")
                    st.info(data['fact_assessment'])
                    
                    st.markdown("#### **🏃‍♂️ Your Immediate 15-Minute Micro-Step**")
                    st.success(f"**{data['momentum_task']}**")
                    
                    st.markdown("#### **💡 Why This Works Right Now**")
                    st.write(data['task_rationale'])
                
            except Exception as e:
                st.error(f"Something went wrong under the hood. Details: {str(e)}")
