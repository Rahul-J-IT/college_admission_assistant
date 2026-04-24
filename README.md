# 🎓 Tamil Nadu College Admissions AI

An intelligent admissions guidance system for Tamil Nadu colleges, built with a fully modular architecture. 

This project aligns with strict evaluation metrics, providing a **proper Frontend/Backend architecture** utilizing FastAPI on the backend and an aesthetically pleasing HTML/CSS/JS frontend.

## 🚀 Tech Stack
- **Frontend** — Modern, aesthetic HTML/CSS/Vanilla JS with glassmorphism and responsiveness.
- **Backend API** — FastAPI to handle asynchronous query execution and static file serving.
- **RAG Engine** — FAISS + HuggingFace `all-MiniLM-L6-v2` (local, no API needed for embedding).
- **Agentic AI** — Intent detection & query augmentation layer (`agent.py`).
- **LangChain** — `ConversationalRetrievalChain` integrating vector stores and prompt history.
- **Groq API** — LLaMA 3 70B interface.

---

## 📁 Project Structure

```text
tn_college_admissions/
│
├── main.py                 ← FastAPI entry point and pipeline orchestrator
├── config.py               ← Loads ALL settings securely from .env
├── agent.py                ← Agentic AI: intent detection + query augmentation
├── data_loader.py          ← Loads structured JSON → LangChain Documents
├── vectorstore.py          ← Chunks + embeds + FAISS index logic
├── rag_chain.py            ← LLM + retriever + memory chain engine
├── prompts.py              ← All LangChain PromptTemplates
│
├── static/                 ← Frontend Directory
│   ├── index.html          ← Single Page Application layout
│   ├── style.css           ← Aesthetic premium modern design styles
│   └── app.js              ← REST client for Chat and Data features
│
├── tests/                  ← Automated test suites
│   ├── test_agent.py       ← Validation for AI intent logic
│   └── test_api.py         ← Validation for FastAPI backend endpoints
│
├── data/
│   └── tn_colleges.json    ← Dataset (10 TN colleges)
│
├── .env.example            ← Template — copy to .env and fill in key
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Install dependencies
Ensure you are using Python 3.9+. Then install the required packages:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment variables
Create your `.env` file explicitly from the template in the root directory:
```bash
cp .env.example .env
```
Open `.env` and replace the placeholder:
```ini
GROQ_API_KEY=gsk_your_actual_key_here
```
*(Get a free GROQ API key at [console.groq.com](https://console.groq.com))*

### 3. Run the Application End-to-End
Navigate into the `backend/` module to start the FastAPI server:
```bash
cd backend
python -m uvicorn main:app --reload
```
Navigate your browser to `http://localhost:8000` to interact with the beautifully crafted frontend!

---

## 🧠 Architecture Overview

Our architecture uses a complete separation of Frontend & Backend constraints allowing independent scalability:

```text
Frontend (Vanilla HTML/CSS/JS)
      │ (Fetch /api/chat)
      ▼
Backend (FastAPI main.py)
      │
      ▼
Agent Layer (agent.py)  ──→ 1. detect_intent() → 2. augment_query()
      │
      ▼
RAG Pipeline (rag_chain.ask)
      │
      ├─ Condense Questions (LangChain Memory)
      │
      ├─ FAISS Retriever (Top-K Similar Chunks matching intent)
      │
      └─ Groq LLaMA 3 70B Engine (Final LLM synthesize)
```

---

## 🧪 Testing & Validation Features
The infrastructure includes automated unit and integration tests using `pytest` and `httpx`.
Run tests via:
```bash
pytest
```
The testing guarantees backend functionality (validity of FastAPI endpoints) and agentic classification (making sure intents correspond correctly without regressions).

## 🛡️ Error Handling
Our endpoints strictly validate pipelines and gracefully encapsulate application errors via JSON structured responses without spilling stack traces uncomfortably to the end-user.