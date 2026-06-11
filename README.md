# Awaaz AI - Anonymous Workplace Reporting
A safe, anonymous, and secure platform for employees to report misconduct using AI. Built for the Microsoft Hackathon 2026.

## 🎥 Demo Video
[Click here to watch the Awaaz AI Demo]_https://drive.google.com/file/d/1nw6YhpufkjPjbScjd7As0SOpO71KR3Ne/view?usp=sharing

## 🛠️ Tech Stack
- Python / Streamlit
- Google Gemini API (GenAI)
- Microsoft Foundry IQ (Knowledge Base Grounding)

## 🤖 GitHub Copilot Usage
I leveraged GitHub Copilot during this development:
- **Code Generation:** Used Copilot suggestions for implementing the file-handling logic and CSS styling.
- **Debugging:** Used Copilot Chat to resolve errors in the JSON parsing process.
- **Documentation:** Copilot helped draft the initial project structure in the README.

## 🧠 Microsoft IQ Integration
- **Foundry IQ:** Used as the intelligence layer to ground AI analysis against company policy documents, ensuring reports are compliant and reducing hallucinations.

## 🚀 How to Run
1. Clone the repo.
2. Install requirements: `pip install -r requirements.txt`
3. Create a `.env` file and add your `GOOGLE_GEMINI_API_KEY`.
4. Run: `streamlit run app.py`
