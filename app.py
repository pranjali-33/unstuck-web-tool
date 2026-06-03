import streamlit as st

# 1. Page Configuration (App Title)
st.set_page_config(page_title="Unstuck", page_icon="🎯", layout="centered")

# 2. Main Header
st.title("🎯 Unstuck")
st.subheader("Overcome choice paralysis. Get your next move.")

# 3. User Input Section
st.write("---")
raw_tasks = st.text_area(
    "Paste your messy notes-app text dump here:",
    placeholder="e.g., need to review Excel files, reply to team emails, go for a quick walk, draft the proposal summary...",
    height=150
)

# 4. Energy Scale Selector
energy_level = st.select_slider(
    "How is your mental energy right now?",
    options=["Fried", "Managing", "High Energy"]
)

# 5. The Execution Button
st.write("")
if st.button("Get My Next Move", type="primary"):
    if raw_tasks.strip() == "":
        st.warning("Please paste some text first so the engine can extract a task!")
    else:
        # Placeholder for the AI brain link tomorrow
        st.write("---")
        st.info("The logic engine is processing... (We will connect the AI API here next!)")
