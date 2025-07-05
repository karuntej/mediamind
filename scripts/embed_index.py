#!/usr/bin/env python
"""
Usage: python scripts/embed_index.py
Creates data/faiss.index  and  data/meta.db
"""
import json, sqlite3, numpy as np, faiss, pathlib, os, tqdm, json
from sentence_transformers import SentenceTransformer

DATA_DIR = pathlib.Path("data")
chunks   = json.load(open(DATA_DIR/"processed"/"all_chunks.json"))
model    = SentenceTransformer("all-MiniLM-L12-v2")

texts = [c["text"][:512] for c in chunks]
embs  = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
ids   = np.arange(len(texts)).astype("int64")

index = faiss.IndexFlatIP(embs.shape[1])
index = faiss.IndexIDMap2(index)
index.add_with_ids(embs, ids)

FAISS_PATH = DATA_DIR / "faiss.index"
faiss.write_index(index, str(FAISS_PATH))      # ← Path ➜ str
print(f"✔️  FAISS index written to {FAISS_PATH}")


con = sqlite3.connect(DATA_DIR/"meta.db")
con.execute("""CREATE TABLE IF NOT EXISTS meta
               (id INTEGER PRIMARY KEY, chunk_id TEXT, source TEXT,
                doc_path TEXT, loc TEXT, text TEXT)""")
con.executemany("INSERT OR REPLACE INTO meta VALUES (?,?,?,?,?,?)",
                [(i,c["chunk_id"],c["source"],c["doc_path"],
                  json.dumps(c["loc"]),c["text"]) for i,c in enumerate(chunks)])
con.commit(); con.close()
print("✔ FAISS index & SQLite meta written")
