import streamlit as st
import os
from google import genai
from google.genai import types

# 1. Page Configuration
st.set_page_config(page_title="Unstuck", page_icon="🎯", layout="centered")

# 2. Initialize the AI Client
# The app looks for an environment variable named GEMINI_API_KEY to authenticate securely
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# 3. User Interface Layout
st.title("🎯 Unstuck")
st.subheader("Overcome choice paralysis. Get your next move.")
st.write("---")

raw_tasks = st.text_area(
    "Paste your messy notes-app text dump here:",
    placeholder="e.g., need to review Excel files, reply to team emails, go for a quick walk, draft the proposal summary...",
    height=150
)

energy_level = st.select_slider(
    "How is your mental energy right now?",
    options=["Fried", "Managing", "High Energy"]
)

st.write("")

# 4. Core Execution Logic
if st.button("Get My Next Move", type="primary"):
    if not api_key:
        st.error("API Key missing! Please set the GEMINI_API_KEY hosting variable.")
    elif raw_tasks.strip() == "":
        st.warning("Please paste some text first so the engine can extract a task!")
    else:
        with st.spinner("Applying behavioral sorting matrix..."):
            try:
                # Constructing the strict behavioral prompt constraint
                behavioral_prompt = f"""
                You are a behavioral psychology framework engine designed to minimize task-initiation latency and eliminate choice paralysis.
                
                The user has provided a chaotic, unfiltered text dump of their mind/to-do items:
                ---
                {raw_tasks}
                ---
                
                The user's current cognitive state and mental energy level is: **{energy_level}**
                
                Execute the following three-step logical protocol:
                1. ANALYZE & EXTRACT: Parse the raw text dump and isolate all distinct, actionable tasks hidden within the emotional or conversational noise.
                2. CLASSIFY BY NEUROLOGICAL DEMAND: Evaluate each task based on cognitive weight. 
                   - If energy is 'Fried', immediately filter out all heavy analytical, creative, or decision-heavy tasks. Isolate a low-friction operational or physical momentum task.
                   - If energy is 'High Energy', isolate the highest-leverage, most strategically important task that maximizes their current cognitive bandwidth.
                3. ISOLATE THE SINGLE NEXT MOVE: Select exactly ONE task. Do not give choices. 
                
                Output your response in a clean, professional, highly encouraging format using these exact Markdown sections:
                ### 🎯 Your Next Move
                [State the single chosen task clearly and concisely here]
                
                ### ⚡ The 5-Minute Kickstart
                [Provide an ultra-low-friction, immediate step the user can take in under 5 minutes to break inertia and build momentum for this task]
                """

                # Call the lightweight, ultra-fast Gemini 2.5 Flash model
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=behavioral_prompt,
                )
                
                st.write("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"An error occurred while calling the brain engine: {e}")
