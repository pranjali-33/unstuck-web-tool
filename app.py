import streamlit as st
import os
import time
from google import genai
from google.genai import types

# 1. Page Configuration (Upgraded Logo and Title)
st.set_page_config(
    page_title="Unstuck", 
    page_icon="⚡", 
    layout="centered"
)

# 2. Initialize the AI Client
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# 3. Main Header Interface
st.title("⚡ Unstuck")
st.subheader("Overcome choice paralysis. Get your next move.")
st.write("---")

# Visual Banner: Elegant Info Box
st.info("💡 **How it works:** Dump your unorganized tasks or messy thoughts below. Our logic engine will categorize them systematically to deliver a clear action plan.")

# 4. User Inputs
raw_tasks = st.text_area(
    "Paste your messy notes-app text dump here:",
    placeholder="e.g., need to review Excel files, reply to team emails, go for a quick walk, draft the proposal summary..."
)

# Interactive Energy Slider with Dynamic Emojis
st.write("#### How is your mental energy right now?")
energy_score = st.slider("Drag to match your current state:", 1, 4, 1, help="1 is lowest energy, 4 is highest energy")

# Dynamic state tracking mapping based on slider selection
if energy_score == 1:
    st.error("🔴 **Current State:** Fried / Completely Exhausted")
    energy_context = "The user is completely fried and exhausted. Give them micro-tasks that require almost zero decision-making."
elif energy_score == 2:
    st.warning("🟡 **Current State:** Drained / Low Focus")
    energy_context = "The user has low focus. Give them straightforward, highly structured tasks."
elif energy_score == 3:
    st.success("🟢 **Current State:** Charging / Balanced")
    energy_context = "The user is feeling balanced and focused. Give them regular analytical tasks."
else:
    st.info("⚡ **Current State:** Supercharged / High Cognitive Energy")
    energy_context = "The user is highly alert and ready. Give them their most complex strategic or deep-work task first."

st.write("") # Spacer

# 5. Execution Button & Dynamic AI Processing
if st.button("Get My Next Move", type="primary"):
    if not raw_tasks.strip():
        st.warning("Please paste some text or notes first to get started!")
    elif not client:
        st.error("AI Client configuration missing. Please verify your background credentials setup.")
    else:
        # Animated loading sequence to make the processing look fun
        with st.spinner("🧠 De-cluttering your brain... applying structural framework..."):
            
            # Formulating a clean prompt combining the user task dump and energy level
            prompt_content = f"""
            You are an elite productivity tool called Unstuck. 
            The user has dumped these raw thoughts/tasks:
            "{raw_tasks}"
            
            Context on user mental energy: {energy_context}
            
            Organize these tasks logically. Pick exactly ONE clear, highest-priority 'Next Move' that fits their current energy state perfectly, followed by a brief, categorized list of the remaining tasks.
            """
            
            try:
                # Simulating a small delay so the spinner feels like it's calculating
                time.sleep(1.2)
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_content,
                )
                
                # Dynamic Success Micro-Interaction!
                st.balloons()
                
                # Display Results in a Clean Container Block
                st.success("🎉 **Your Blueprint is Ready!**")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"An error occurred while generating your plan: {e}")
