from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import json, sqlite3, io, fitz
from src.storage import download_pdf

app = FastAPI()

class Query(BaseModel):
    question: str
    top_k:    int

def dense_search(q: str, k: int):
    # your existing FAISS lookup logic…
    # returns list of {"doc_path": key, "loc":{…}, "score":float, "text": str}
    raise NotImplementedError

def synthesize_answer(q: str, passages: list):
    # your existing LLM synthesis call…
    raise NotImplementedError

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
