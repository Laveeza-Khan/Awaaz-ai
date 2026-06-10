import streamlit as st
import google.generativeai as genai
import json
import secrets
from pathlib import Path

# --- 1. CONFIG & SETUP ---
api_key = st.secrets.get("GOOGLE_GEMINI_API_KEY", None)
if api_key:
    genai.configure(api_key=api_key)

DATA_FILE = Path(__file__).resolve().parent / "reports.json"
POLICY_FILE = Path(__file__).resolve().parent / "policy_kb.json"

def load_report_history():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except: return []
    return []

def load_policy_kb():
    try:
        with open(POLICY_FILE, "r") as f:
            return json.load(f)
    except: return {"General": "Follow standard company conduct."}

policy_kb = load_policy_kb()
report_history = load_report_history()

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Awaaz AI", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] { background-color: #041736 !important; }
    .stApp, p, div, label, h1, h2, h3, .stMetric, .stSidebar, span, li { color: #eaffb8 !important; }
    .card { background-color: #0d2d5e !important; padding: 25px !important; border-radius: 12px !important; border: 1px solid #d9ed91 !important; margin-bottom: 20px !important; }
    button { background-color: #d9ed91 !important; color: #041736 !important; font-weight: bold !important; }
    label { color: #d9ed91 !important; font-weight: 600 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. UI LOGIC ---
st.markdown('<h1 style="text-align:center;">🛡️ Awaaz AI</h1>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📝 File Report", "📊 Track Progress"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        user_message = st.text_area("Write your issue:", height=150)
        department = st.selectbox("Department:", ["Select", "Sales", "Engineering", "HR", "Legal", "Other"])
        send_to = st.selectbox("Send to:", ["Compliance Committee", "HR", "Board"])
        submit_btn = st.button("Process Report")
    
    with col2:
        if submit_btn and user_message and department != "Select":
            with st.spinner("AI analyzing compliance..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"""
                    You are a Foundry IQ Compliance Agent. 
                    Grounding Knowledge: {json.dumps(policy_kb)}.
                    Output JSON ONLY: {{"redacted_text": "...", "severity_score": "...", "policy_mapping": "..."}}
                    Complaint: {user_message}
                    """
                    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    parsed = json.loads(response.text)
                    
                    st.success("Report Generated!")
                    st.write(f"**Policy Mapped:** {parsed['policy_mapping']}")
                    st.write(f"**Severity:** {parsed['severity_score']}")
                    
                    # Save logic
                    new_report = {"case_id": f"AWZ-{secrets.token_hex(4).upper()}", "department": department, "severity": parsed['severity_score'], "policy": parsed['policy_mapping']}
                    # (Add save logic here as per your previous code)
                except Exception as e:
                    st.error(f"Error: {e}")

# (Baaki ka tab2 ka code yahan waise hi rehne do)
