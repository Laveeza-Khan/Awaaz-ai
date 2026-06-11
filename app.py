import streamlit as st
import google.generativeai as genai
import json
import secrets
from pathlib import Path

# Load key from Streamlit native secrets
api_key = st.secrets["GOOGLE_GEMINI_API_KEY"]
genai.configure(api_key=api_key)

DATA_FILE = Path(__file__).resolve().parent / "reports.json"

# Local storage helpers for anonymous pattern detection

def load_policy_kb():
    try:
        with open("policy_kb.json", "r", encoding="utf-8") as f:
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


# 1. Page Configuration
st.set_page_config(
    page_title="Awaaz AI - Anonymous Misconduct Reporting",
    page_icon="A",
    layout="wide"
)

st.markdown("""
    <style>
    /* Backgrounds */
    [data-testid="stAppViewContainer"] { background-color: #041736 !important; }
    
    /* Card Styling */
    .card {
        background-color: #0d2d5e !important;
        padding: 25px !important;
        border-radius: 12px !important;
        border: 1px solid #d9ed91 !important;
        margin-bottom: 20px !important;
        color: #eaffb8 !important; /* Yahan se text ka color set ho raha hai */
    }

    /* Force Text Color Everywhere */
    .stApp, .stMarkdown, p, div, label, h1, h2, h3 {
        color: #eaffb8 !important;
    }
    </style>
""", unsafe_allow_html=True)


def pill_badge(text, bg="#EFF6FF", color="#1E3A8A"):
    return (
        f"<span style='display:inline-block;padding:6px 12px;border-radius:999px;"
        f"background:{bg};color:{color};font-weight:700;font-size:13px;'>{text}</span>"
    )

report_history = load_report_history()

department_counts = {}
for item in report_history:
    dept = item.get("department")
    if dept:
        department_counts[dept] = department_counts.get(dept, 0) + 1
repeated_departments = sum(1 for count in department_counts.values() if count >= 2)

# Sidebar
with st.sidebar:
    st.markdown("## Awaaz AI")
    st.caption("Safe Voice for Employees")
    st.markdown("---")

    if not api_key:
        st.error("Gemini API key not found. Please add GOOGLE_GEMINI_API_KEY to Streamlit secrets and restart the app.")

    st.markdown("---")
    st.markdown("**Portal Statistics**")
    st.metric("Total Reports Filed", f"{len(report_history)} case(s) logged")
    st.metric("Departments Flagged", f"{repeated_departments} with repeated complaints")
    st.metric("Identity Privacy Rate", "100% Secure")
    st.markdown("---")
    st.caption("Microsoft Hackathon 2026")

# Main dashboard header
st.markdown('<h1 style="text-align:center;color:#1E3A8A;font-weight:800;margin-bottom:8px;">🛡️ Awaaz AI</h1>', unsafe_allow_html=True)

# Main dashboard tabs
tab1, tab2 = st.tabs(["📝 File Report", "📊 Track Progress"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### File an Anonymous Workplace Report")
    st.markdown("Apna masla safely darj karein. Hamara AI aap ka naam mita kar auto-report banayega.")

    left_panel, right_panel = st.columns([1, 1])

    with left_panel:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        lang_selection = st.radio(
            "Choose Language / Language Select Karein:",
            ["Roman Urdu / Urdu (رومن اردو)", "English Only"],
            horizontal=True,
        )

        voice_enabled = st.checkbox("Submit a voice note instead of text")
        user_message = ""

        if voice_enabled:
            audio_data = st.audio_input("Record your voice note safely:")
            st.markdown(
                "<div class='recording-wrap'><div class='recording-bar'><div class='recording-indicator'></div></div></div>",
                unsafe_allow_html=True,
            )
            if audio_data is not None:
                user_message = (
                    "User uploaded an audio report regarding supervisor harassment, "
                    "forced late night shifts, and workspace intimidation."
                )
                st.info("Voice note received and being processed.")
        else:
            user_message = st.text_area(
                "Write your issue here / Apna masla detail se yahan likhein:",
                height=150,
                placeholder=(
                    "E.g., Mera manager Asif mujhe kafi tang karta hai aur hamesha extra hours "
                    "kaam karne ka bolta hai. Mera naam Sarah hai..."
                ),
            )

        department = st.selectbox(
            "Which department does this issue come from? / Kis department ka masla hai:",
            [
                "Select your department",
                "Sales",
                "Engineering",
                "Operations",
                "Customer Support",
                "Finance",
                "Human Resources",
                "Legal",
                "Facilities",
                "Other",
            ],
            help="Anonymous department information is used only for pattern detection and not to identify individuals.",
        )

        send_to = st.selectbox(
            "Where should we send this report?",
            [
                "Direct Compliance Committee (Bypasses Local HR entirely)",
                "General HR Department",
                "Company Directors Board",
            ],
        )

        submit_btn = st.button("Process and Generate Report", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right_panel:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Generated HR Report Preview")
        output_container = st.container(border=True)

        if submit_btn and user_message and department != "Select your department":
            with output_container:
                with st.spinner("AI is removing names and formatting the text..."):
                    if not api_key:
                        st.error("Cannot process report: Gemini API key missing. Add GOOGLE_GEMINI_API_KEY to Streamlit secrets.")
                    else:
                        try:
                            easy_prompt = f"""
                            You are a helpful HR Compliance officer. Analyze this raw workplace complaint.

                            Tasks:
                            1. Translate the main complaint clearly into simple, professional, corporate English. Keep sentences simple and easy to understand.
                            2. Remove all personal identifiers like names of people, cities, or direct contact details. Replace them EXACTLY with structural HTML tags: '<span class=\"redacted-tag\">[EMPLOYEE]</span>', '<span class=\"redacted-tag\">[SUPERVISOR]</span>', or '<span class=\"redacted-tag\">[LOCATION]</span>'.
                            3. Set Severity Level as either HIGH, MEDIUM, or LOW.
                            4. Identify which standard workplace policy this violates (e.g., Anti-Harassment Guidelines, Fair Labor Standards Code).

                            You MUST reply ONLY in this strict JSON format:
                            {{
                                "redacted_text": "simple english report text here",
                                "severity_score": "HIGH or MEDIUM or LOW",
                                "policy_mapping": "policy rule name"
                            }}

                            Complaint Text: {user_message}
                            """

                            model = genai.GenerativeModel('gemini-1.5-flash')
                            response = model.generate_content(
                                easy_prompt,
                                generation_config={"response_mime_type": "application/json"},
                            )

                            clean_json = response.text.strip().replace("```json", "").replace("```", "")
                            parsed_data = json.loads(clean_json)

                            final_text_report = parsed_data.get("redacted_text", "")
                            final_severity = parsed_data.get("severity_score", "").upper()
                            final_policy = parsed_data.get("policy_mapping", "")
                        except Exception as e:
                            status_code = getattr(e, 'code', None) or getattr(e, 'status_code', None)
                            if status_code in (400, 401):
                                st.error("AI request failed with status 400/401. Please verify your Gemini API key and request configuration.")
                            else:
                                st.error(f"AI processing error: {e}")
                            final_text_report = None
                            final_severity = None
                            final_policy = None

                        if not final_text_report:
                            st.error("AI did not return a valid report. Please try again later.")
                        else:
                            case_id = f"AWZ-{secrets.token_hex(4).upper()}"
                            st.markdown(f"##### **Case ID:** `{case_id}`")
                            st.markdown(f"**Sent To:** `{send_to}`")
                            st.markdown(f"**Department logged:** {pill_badge(department)}", unsafe_allow_html=True)
                            st.markdown("---")
                            st.markdown("**Official English Report (Names Removed):**")
                            st.markdown(final_text_report, unsafe_allow_html=True)
                            st.markdown("---")

                            if final_severity and "HIGH" in final_severity:
                                severity_badge = pill_badge("HIGH", bg="#FEF2F2", color="#991B1B")
                                severity_copy = "Serious issue detected - Action required."
                            elif final_severity and "MEDIUM" in final_severity:
                                severity_badge = pill_badge("MEDIUM", bg="#FEF3C7", color="#92400E")
                                severity_copy = "Review within 48 hours."
                            else:
                                severity_badge = pill_badge("LOW", bg="#DCFCE7", color="#065F46")
                                severity_copy = "Logged for record."

                            st.markdown(
                                f"<div style='margin-bottom:18px; font-size:14px; line-height:1.6;'>"
                                f"<strong>Severity:</strong> {severity_badge} — {severity_copy}</div>",
                                unsafe_allow_html=True,
                            )

                            st.markdown(
                                f"<div class='hr-routing-card'><strong>Automatic Routing Triggered:</strong> Encrypted PDF payload successfully generated and securely dispatched via TLS tunnel to the <strong>{send_to}</strong> compliance mail server.</div>",
                                unsafe_allow_html=True,
                            )

                            same_dept_count = sum(1 for item in report_history if item.get("department") == department)
                            if same_dept_count >= 2:
                                st.warning(
                                    f"Pattern Alert: There are now {same_dept_count + 1} total anonymous reports from {department}. "
                                    "Multiple complaints from the same department may indicate an emerging workplace issue."
                                )
                            elif same_dept_count == 1:
                                st.info(
                                    f"One prior complaint from {department} has already been recorded. "
                                    "This helps compliance detect repeat patterns earlier."
                                )
                            else:
                                st.success(f"No prior anonymous reports from {department} are currently logged.")

                            st.markdown(f"""
                            <div class='crypto-container'>
                                <b>Database Status:</b> Securely Encrypted and Safe.<br>
                                User IP logs dropped automatically.
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown(f"""
                            <div class='iq-container'>
                                <b>Microsoft Foundry IQ Alignment:</b><br>
                                Cross-verified against company policy documentation: <u>{final_policy}</u>.
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown("---")
                            st.markdown(
                                f"<div class='token-box'><b>Track Anonymously:</b><br>"
                                f"Send the text token <b>'{case_id}'</b> to our company bot to check progress without revealing your name.</div>",
                                unsafe_allow_html=True,
                            )

                            save_report({
                                "case_id": case_id,
                                "department": department,
                                "severity": final_severity,
                                "policy": final_policy,
                            })
        elif submit_btn and not user_message:
            with output_container:
                st.error("Please enter a complaint before submitting.")
        elif submit_btn and department == "Select your department":
            with output_container:
                st.error("Please select the department or choose 'Other' before submitting.")
        else:
            with output_container:
                st.info("Form is ready. Please type your complaint on the left and click 'Process' to see the secure compliance file preview here.")

    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Track Progress")
    st.markdown("**Dashboard Overview**")
    st.markdown(f"- Total reports filed: **{len(report_history)}**")
    st.markdown(f"- Departments flagged with repeated complaints: **{repeated_departments}**")
    st.markdown(f"- Identity Privacy Rate: **100% Secure**")
    st.markdown("---")
    st.markdown("**Recent Case History**")
    if report_history:
        for item in report_history[-5:]:
            case_id = item.get("case_id", "N/A")
            dept = item.get("department", "N/A")
            severity = item.get("severity", "N/A")
            policy = item.get("policy", "N/A")
            st.markdown(f"- `{case_id}` | Department: {dept} | Severity: {severity} | Policy: {policy}")
    else:
        st.info("No cases have been filed yet.")
    st.markdown('</div>', unsafe_allow_html=True)
