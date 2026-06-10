import streamlit as st
import google.generativeai as genai
import json
import secrets
from pathlib import Path

# --- 1. Page Configuration & Setup ---
st.set_page_config(page_title="Awaaz AI - Anonymous Misconduct Reporting", page_icon="🛡️", layout="wide")

# API Setup
api_key = st.secrets.get("GOOGLE_GEMINI_API_KEY", None)
if api_key:
    genai.configure(api_key=api_key)

DATA_FILE = Path(__file__).resolve().parent / "reports.json"

# --- 2. Helper Functions ---
def load_policy_kb():
    try:
        with open("policy_kb.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
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

def pill_badge(text, bg="#EFF6FF", color="#1E3A8A"):
    return f"<span style='display:inline-block;padding:6px 12px;border-radius:999px;background:{bg};color:{color};font-weight:700;font-size:13px;'>{text}</span>"

# --- 3. CSS Styling ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] { background-color: #041736 !important; }
    .stApp, p, div, label, h1 { color: #eaffb8 !important; }
    .card { background-color: #0d2d5e !important; padding: 25px !important; border-radius: 12px !important; border: 1px solid #d9ed91 !important; margin-bottom: 20px !important; }
    button { background-color: #d9ed91 !important; color: #041736 !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. Sidebar Stats ---
report_history = load_report_history()
department_counts = {item.get("department"): 0 for item in report_history}
for item in report_history:
    dept = item.get("department")
    if dept: department_counts[dept] += 1
repeated_depts = sum(1 for count in department_counts.values() if count >= 2)

with st.sidebar:
    st.markdown("## Awaaz AI")
    st.metric("Total Reports", len(report_history))
    st.metric("Flagged Depts", repeated_depts)

# --- 5. Main UI ---
st.markdown('<h1 style="text-align:center;">🛡️ Awaaz AI</h1>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📝 File Report", "📊 Track Progress"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        user_message = st.text_area("Write your issue:")
        department = st.selectbox("Select department:", ["Select your department", "Sales", "Engineering", "HR", "Other"])
        send_to = st.selectbox("Route to:", ["Compliance Committee", "General HR", "Directors"])
        submit_btn = st.button("Process and Generate Report", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        output_container = st.container(border=True)
        if submit_btn:
            if not user_message or department == "Select your department":
                output_container.error("Please fill in the form correctly.")
            elif not api_key:
                output_container.error("API Key not configured.")
            else:
                with output_container:
                    with st.spinner("AI is analyzing..."):
                        try:
                            policy_context = json.dumps(load_policy_kb())
                            prompt = f"Analyze: {user_message}. Use context: {policy_context}. Output JSON with: redacted_text, severity_score, policy_mapping."
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                            data = json.loads(response.text.strip())
                            
                            case_id = f"AWZ-{secrets.token_hex(4).upper()}"
                            st.success(f"Case ID: {case_id}")
                            st.write(data.get("redacted_text"))
                            
                            save_report({
                                "case_id": case_id, "department": department,
                                "severity": data.get("severity_score"), "policy": data.get("policy_mapping")
                            })
                        except Exception as e:
                            st.error(f"Error: {e}")

with tab2:
    st.markdown("### Recent History")
    for item in report_history[-5:]:
        st.write(f"- `{item['case_id']}` | {item['department']} | {item['severity']}")
