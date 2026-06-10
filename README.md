# Awaaz AI: Intelligent Workplace Compliance Portal

Awaaz AI is an agentic workplace reporting portal that utilizes AI-driven knowledge retrieval to ensure safe, anonymous, and policy-compliant misconduct reporting.

## 🚀 Features
- **Agentic Knowledge Retrieval:** Uses an integrated policy knowledge base to ground AI responses (Simulated Foundry IQ).
- **Multi-lingual Support:** Handles English, Urdu, and Roman Urdu.
- **Smart Anonymization:** Automatically scrubs Personally Identifiable Information (PII) using AI reasoning.
- **Severity Matrix:** AI-driven categorization for actionable HR reporting.

## 🤖 GitHub Copilot Usage
This project was developed using **GitHub Copilot Agent Mode**. Copilot assisted in:
- Architecting the agentic logic for compliance routing.
- Scaffolding the responsive UI components and CSS styling.
- Debugging JSON-based storage for anonymous history.

## 🛠️ Setup Guide
1. **Clone the repository:**
   `git clone https://github.com/Laveeza-Khan/Awaaz-ai.git`
2. **Install dependencies:**
   `pip install -r requirements.txt`
3. **Configure API:**
   Add `GOOGLE_GEMINI_API_KEY` to your Streamlit secrets/environment variables.
4. **Run:**
   `streamlit run app.py`

## 🧠 Microsoft IQ Integration
Awaaz AI incorporates the principles of **Foundry IQ** by leveraging an agentic knowledge retrieval layer. The system cross-references complaints against a structured `policy_kb.json` knowledge graph, ensuring compliance decisions are grounded in actual company policies rather than generic hallucinations.
