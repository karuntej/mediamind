from fastapi import FastAPI
from pydantic import BaseModel
import faiss, sqlite3, json, numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from api.ollama_client import ollama_generate

DATA = Path(__file__).resolve().parents[1] / "data"
index = faiss.read_index(str(DATA / "faiss.index"))
con   = sqlite3.connect(str(DATA / "meta.db"), check_same_thread=False)
model = SentenceTransformer("all-MiniLM-L12-v2")

app = FastAPI(title="MediaMind PDF API", version="0.1")

@app.get("/ping")
def ping():
    return {"status": "ok", "routes": ["/chat (POST)", "/docs"]}

class Query(BaseModel):
    question: str
    top_k:   int = 5

@app.get("/")
def root(): return {"status":"alive","docs":"/docs","chat":"/chat"}

def dense_search(q: str, k: int):
    vec = model.encode([q], normalize_embeddings=True).astype("float32")
    D,I = index.search(vec, k)
    rows=[]
    for rank, idx in enumerate(I[0]):
        chunk_id, source, path, loc, text = con.execute(
            "SELECT chunk_id, source, doc_path, loc, text FROM meta WHERE id=?",
            (int(idx),)).fetchone()
        rows.append({"rank":rank,"score":float(D[0][rank]),"doc_path":path,
                     "loc":json.loads(loc),"text":text})
    return rows

@app.post("/chat")
def chat(q: Query):
    # 1. retrieve evidence chunks
    passages = dense_search(q.question, q.top_k)

    # 2. synthesize answer using Llama-3
    answer = synthesize_answer(q.question, passages)

    # 3. include both answer and passages in the response
    return {
        "question": q.question,
        "answer"  : answer,
        "passages": passages
    }


def synthesize_answer(question: str, passages: list[dict]) -> str:
    ctx = "\n".join(f"[{i}] {p['text']}" for i, p in enumerate(passages))
    prompt = (
        "Answer the user question using only the numbered context. "
        "Cite passages like [0], [1].\n\n### Context\n"
        f"{ctx}\n\n### Question\n{question}\n### Answer:\n"
    )
    return ollama_generate(prompt, model="llama3.2:latest")