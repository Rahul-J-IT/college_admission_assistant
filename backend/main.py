"""
main.py
─────────────────────────────────────────────────────────────────
FastAPI Entry Point for TN Admissions AI Backend.
This module orchestrates the server, handling REST endpoints and
delivering the static HTML/CSS SPA (Single Page Application).

It explicitly handles data loading and RAG pipeline initialization logic.
"""

import os
import uvicorn
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Internal logic modules
from data_loader import build_documents, load_raw_data
from vectorstore import build_vectorstore
from rag_chain import build_rag_chain, ask
from agent import process

# ── Global State ────────────────────────────────────────────────
chain = None
data = None
startup_error = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    Executes exactly once when the server boots.
    Initializes the RAG elements, embeddings, and dataset variables.
    """
    global chain, data, startup_error
    print("⚙️ Building RAG engine — this runs only once…")
    try:
        # Load and embed datasets into memory
        docs = build_documents()
        vectorstore = build_vectorstore(docs)
        
        # Build conversational chain connecting Groq & FAISS
        chain = build_rag_chain(vectorstore)
        data = load_raw_data()
        
        print("✅ Pipeline initialized successfully.")
    except Exception as e:
        # Log error to console but keep the server up to allow rendering informative errors
        print(f"❌ Error initializing pipeline: {e}")
        startup_error = str(e)
        traceback.print_exc()
        
    yield
    print("🛑 Shutting down server...")

# Initialize the API
app = FastAPI(title="TN Admissions AI", lifespan=lifespan)

# ── Mount Static Files ───────────────────────────────────────────
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ── Data Models ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str

# ── Endpoints ────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    """
    Serves the main application interface. 
    Ensure index.html exists in the static directory.
    """
    index_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse("<html><body><h1>Error: index.html not found!</h1></body></html>", status_code=404)
        
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Primary agentic endpoint for interacting with the AI.
    It takes user text, routes it to the intent-detector, retrieves data,
    and returns a formatted answer.
    """
    global chain, startup_error
    
    # 1. Defensive validation
    if chain is None:
        error_msg = startup_error if startup_error else "Pipeline not initialized yet."
        raise HTTPException(status_code=503, detail=error_msg)
    
    try:
        # 2. Agentic intent recognition
        augmented_query, intent = process(req.query.strip())
        
        # 3. RAG Retrieval & LLM invocation
        result = ask(chain, augmented_query)
        answer = result.get("answer", "")
        
        # 4. Synthesize source metadata specifically
        sources_list = []
        for src in result.get("source_documents", []):
            m = src.metadata
            label = m.get("college_name", m.get("exam_key", m.get("doc_type", "Reference")))
            course = m.get("course_name", "")
            if course:
                label += f" → {course}"
            sources_list.append(label)
            
        return JSONResponse({
            "answer": answer,
            "intent": intent,
            "sources": list(set(sources_list)) # Deduplicate reference docs
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI internal failure: {str(e)}")

@app.get("/api/data")
async def data_endpoint():
    """
    Secondary endpoint providing static JSON representations
    for frontend dynamic rendering (Checklists, College listings).
    """
    global data, startup_error
    if data is None:
        error_msg = startup_error if startup_error else "Data not initialized yet."
        raise HTTPException(status_code=503, detail=error_msg)
        
    return JSONResponse(data)

# ── Local Runner Support ─────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
