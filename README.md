# 🏦 AvataarFlow: Enterprise Multi-Agent Orchestration

AvataarFlow is an enterprise-grade, LangGraph-powered multi-agent system built for the ET AI Hackathon 2026 (Problem Statement 2). It automates and self-heals the complex "Contract-to-Payment" procurement workflow using 7 specialized ReAct AI agents.

## 🌟 Key Features
- **Multi-Agent Architecture**: Uses `LangGraph` to orchestrate 7 specialized agents.
- **Self-Healing & ReAct**: Automatic exception handling for common SME vendor errors (e.g., missing PAN, incorrect GST).
- **Human-in-the-Loop Constraint**: Fully autonomous except for high-value Purchase Orders (> ₹1M) which dynamically stall for human approval.
- **Secure Audit Trails**: Every agent decision and tool-call is logged to an SQLite Database, encrypted at rest using AES-256 (Fernet).
- **Mock ERP Integration**: Fully functional asynchronous FastAPI mock ERP.
- **Dynamic Frontend**: Modern Streamlit app with live Mermaid graph tracking, real-time reasoning traces, and audit PDF exports.

## 🛠 Project Structure
- `/app`: Streamlit UI (`dashboard.py`)
- `/agents`: LangGraph node logic and `GraphState` definition
- `/tools`: Sourcing tools, Indian Validation Tools (GST, TDS), PDF Parsers, Async ERP Client
- `/db`: SQLite DB + AES-256 Encryption Wrappers
- `/mock_erp`: FastAPI endpoints for Mock PR, PO, Invoice
- `/tests`: Scenarios, PDFs, and Pytests for self-healing logic

## 🚀 Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Setup Encryption Key**
   Make sure to generate a `.env` file with a secure Fernet key.
   ```bash
   python -c "from cryptography.fernet import Fernet; open('.env', 'w').write(f'FERNET_KEY={Fernet.generate_key().decode()}\n')"
   ```
3. **Run Mock ERP (Backend)**
   ```bash
   python mock_erp/main.py
   ```
4. **Run Streamlit Dashboard (Frontend)**
   ```bash
   streamlit run app/dashboard.py
   ```

## ⚠️ Disclaimer
**Demo only - Not legal or financial advice.** This system was developed for technology demonstration purposes during the ET AI Hackathon 2026.
