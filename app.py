import streamlit as st
import os
import json
import time
from google import genai
from google.genai import types

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Unstuck Engine",
    page_icon="⚡",
    layout="centered"
)

# ----------------------------
# SESSION STATE (ANTI-SPAM LOCK)
# ----------------------------
if "used_api" not in st.session_state:
    st.session_state.used_api = False

# ----------------------------
# STYLING
# ----------------------------
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    .stTextArea textarea { background-color: #1e293b; color: #f8fafc; border: 1px solid #334155; }
    .stSelectbox div { background-color: #1e293b; color: #f8fafc; }
    h1, h2, h3 { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# GEMINI CLIENT
# ----------------------------
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# ----------------------------
# HEADER
# ----------------------------
st.title("⚡ UNSTUCK")
st.markdown("#### Your cognitive momentum engine")

st.write("---")

# ----------------------------
# INPUTS
# ----------------------------
user_dump = st.text_area("Paste your mental dump:")

task_category = st.selectbox(
    "Context",
    ["Professional", "Academic", "Personal"]
)

cognitive_weight = st.selectbox(
    "Complexity",
    ["Low", "Medium", "High"]
)

# ----------------------------
# FRAMEWORK BUTTON
# ----------------------------
if st.button("Execute Framework Optimization", type="primary"):

    # Prevent repeated clicks
    if st.session_state.used_api:
        st.warning("Please wait before running again.")
        st.stop()

    if not client:
        st.error("Missing API key.")
        st.stop()

    if not user_dump.strip():
        st.warning("Please enter input.")
        st.stop()

    st.session_state.used_api = True

    # ----------------------------
    # PROMPT
    # ----------------------------
    system_instruction = (
        "You are a behavioral analyst. Return strict JSON only."
    )

    prompt_content = f"""
User Input: {user_dump}
Context: {task_category}
Complexity: {cognitive_weight}

Return JSON:
{{
  "fact_assessment": "",
  "cognitive_shift": "",
  "momentum_task": "",
  "clinical_rationale": ""
}}
"""

    # ----------------------------
    # CACHED API CALL
    # ----------------------------
    @st.cache_data(show_spinner=False)
    def call_gemini(prompt_content):
        return client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt_content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.1
            ),
        )

    # ----------------------------
    # API EXECUTION WITH ERROR HANDLING
    # ----------------------------
    try:
        with st.spinner("Analyzing..."):
            response = call_gemini(prompt_content)
            data = json.loads(response.text)

        st.write("---")

        st.markdown("### Insight")
        st.write(data["fact_assessment"])

        st.markdown("### Next Action")
        st.success(data["momentum_task"])

        st.markdown("### Why this works")
        st.info(data["clinical_rationale"])

        # release lock
        st.session_state.used_api = False

    except Exception as e:

        st.session_state.used_api = False

        if "429" in str(e):
            st.error("Rate limit reached. Wait 60–90 seconds and try again.")
        else:
            st.error(f"Error: {str(e)}")
