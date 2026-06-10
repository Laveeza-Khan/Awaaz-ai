import streamlit as st
import google.generativeai as genai
import json
import secrets
from pathlib import Path

# 1. Config and Setup
st.set_page_config(page_title="Awaaz AI", page_icon="A", layout="wide")
api_key = st.secrets.get("GOOGLE_GEMINI_API_KEY", None)
if api_key:
    genai.configure(api_key=api_key)

DATA_FILE = Path(__file__).resolve().parent / "reports.json"

# --- FUNCTIONS ---
def load_policy_kb():
    try:
        with open("policy_kb.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"General": "Follow standard company conduct."}

def load_report_history():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return []
    return []

def save_report(report_entry):
    try:
        history = load_report_history()
        history.append(report_entry)
        with DATA_FILE.open("w", encoding="utf-8") as fh:
            json.dump(history, fh, indent=2)
        return True
    except OSError:
        return False

# CSS Injection
st.markdown("""<style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] { background-color: #041736 !important; }
    .stApp, p, div, label, h1, h2, h3, .stMetric, .stSidebar, span, li { color: #eaffb8 !important; }
    .card { background-color: #0d2d5e !important; padding: 25px !important; border-radius: 12px !important; border: 1px solid #d9ed91 !important; margin-bottom: 20px !important; }
    button { background-color: #d9ed91 !important; color: #041736 !important; font-weight: bold !important; }
</style>""", unsafe_allow_html=True)

report_history = load_report_history()

# Tabs and UI
tab1, tab2 = st.tabs(["📝 File Report", "📊 Track Progress"])

with tab1:
    left_panel, right_panel = st.columns([1, 1])
    with left_panel:
        user_message = st.text_area("Write your issue:")
        department = st.selectbox("Department:", ["Select your department", "Sales", "Engineering", "Other"])
        send_to = st.selectbox("Send to:", ["Compliance Committee", "HR", "Directors"])
        submit_btn = st.button("Process and Generate Report")

    with right_panel:
        output_container = st.container(border=True)
        if submit_btn and user_message and department != "Select your department":
            with output_container:
                with st.spinner("AI is processing..."):
                    if not api_key:
                        st.error("Gemini API key missing.")
                    else:
                        try:
                            policy_kb = load_policy_kb()
                            policy_context = json.dumps(policy_kb)
                            prompt = f"Analyze this complaint: {user_message}. Use this KB: {policy_context}. Output JSON with keys: redacted_text, severity_score, policy_mapping."
                            
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                            
                            parsed_data = json.loads(response.text.strip())
                            st.write(f"**Report:** {parsed_data.get('redacted_text')}")
                            
                            save_report({
                                "case_id": f"AWZ-{secrets.token_hex(4).upper()}",
                                "department": department,
                                "severity": parsed_data.get("severity_score"),
                                "policy": parsed_data.get("policy_mapping")
                            })
                        except Exception as e:
                            st.error(f"Error: {e}")
