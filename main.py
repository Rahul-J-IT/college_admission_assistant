"""
main.py
─────────────────────────────────────────────────────────────────
FastAPI Entry Point for TN Admissions AI.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import os

from data_loader import build_documents, load_raw_data
from vectorstore import build_vectorstore
from rag_chain import build_rag_chain
from agent import process
from rag_chain import ask

# Globals to hold pipeline state
chain = None
data = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chain, data
    print("⚙️ Building RAG engine — this runs only once…")
    try:
        docs = build_documents()
        vectorstore = build_vectorstore(docs)
        chain = build_rag_chain(vectorstore)
        data = load_raw_data()
        print("✅ Pipeline initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing pipeline: {e}")
    yield
    print("Shutting down...")

app = FastAPI(title="TN Admissions AI", lifespan=lifespan)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class ChatRequest(BaseModel):
    query: str
    
@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    global chain
    if chain is None:
        return JSONResponse(status_code=503, content={"error": "Pipeline not initialized yet."})
    
    try:
        augmented_query, intent = process(req.query)
        result = ask(chain, augmented_query)
        answer = result.get("answer", "")
        
        # Extract sources
        sources_list = []
        for src in result.get("source_documents", []):
            m = src.metadata
            label = m.get("college_name", m.get("exam_key", m.get("doc_type", "Reference")))
            course = m.get("course_name", "")
            if course:
                label += f" → {course}"
            sources_list.append(label)
            
        return dict(
            answer=answer,
            intent=intent,
            sources=list(set(sources_list)) # deduplicate
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/data")
async def data_endpoint():
    global data
    if data is None:
        return JSONResponse(status_code=503, content={"error": "Data not initialized yet."})
    return data

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
