from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import json, sqlite3, io, fitz, pathlib
import faiss
from sentence_transformers import SentenceTransformer
from src.storage import download_pdf
from .ollama_client import ollama_generate

app = FastAPI()

DATA_DIR = pathlib.Path("data")

model = SentenceTransformer("all-MiniLM-L12-v2")
index = faiss.read_index(str(DATA_DIR / "faiss.index"))

class Query(BaseModel):
    question: str
    top_k:    int

def dense_search(q: str, k: int):
    """Return top-k passages using the FAISS index."""
    emb = model.encode([q], normalize_embeddings=True)
    scores, ids = index.search(emb, k)
    con = sqlite3.connect(DATA_DIR / "meta.db")
    cur = con.cursor()
    results = []
    for idx, score in zip(ids[0], scores[0]):
        row = cur.execute(
            "SELECT chunk_id, doc_path, loc, text FROM meta WHERE id=?",
            (int(idx),),
        ).fetchone()
        if row:
            results.append({
                "chunk_id": row[0],
                "doc_path": row[1],
                "loc": json.loads(row[2]),
                "text": row[3],
                "score": float(score),
            })
    con.close()
    return results

def synthesize_answer(q: str, passages: list):
    """Use Ollama to generate an answer from passages."""
    context = "\n\n".join(p["text"] for p in passages)
    prompt = (
        "Answer the question using the context below.\n\n" + context +
        f"\n\nQuestion: {q}\nAnswer:"
    )
    return ollama_generate(prompt)

@app.post("/chat")
def chat(q: Query):
    passages = dense_search(q.question, q.top_k)
    answer   = synthesize_answer(q.question, passages)
    return JSONResponse({"answer": answer, "passages": passages})

@app.get("/preview")
def preview(key: str, page: int = 1):
    """
    Render page N of the PDF as PNG.
    """
    try:
        data = download_pdf(key)
        doc  = fitz.open(stream=data, filetype="pdf")
        pix  = doc.load_page(page-1).get_pixmap()
        img  = pix.tobytes("png")
        return StreamingResponse(io.BytesIO(img), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
