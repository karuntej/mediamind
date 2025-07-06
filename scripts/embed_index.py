#!/usr/bin/env python
import json, sqlite3, pathlib
import numpy as np, faiss
from sentence_transformers import SentenceTransformer

DATA_DIR = pathlib.Path("data")
chunks   = json.load(open(DATA_DIR/"processed"/"all_chunks.json"))
model    = SentenceTransformer("all-MiniLM-L12-v2")

# encode texts (first 512 chars)
texts = [c["text"][:512] for c in chunks]
embs  = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
ids   = np.arange(len(embs)).astype("int64")

# build & write FAISS index
index = faiss.IndexFlatIP(embs.shape[1])
index.add(embs)
faiss.write_index(index, str(DATA_DIR/"faiss.index"))
print("✔️ FAISS index written")

# write SQLite metadata
con = sqlite3.connect(DATA_DIR/"meta.db")
cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS meta (
  id        INTEGER PRIMARY KEY,
  chunk_id  TEXT,
  doc_path  TEXT,
  loc       TEXT,
  text      TEXT
)
""")
entries = [
    (i, c["chunk_id"], c["doc_path"], json.dumps(c["loc"]), c["text"])
    for i, c in enumerate(chunks)
]
cur.executemany("INSERT OR REPLACE INTO meta VALUES (?,?,?,?,?)", entries)
con.commit()
con.close()
print("✔️ SQLite meta written")
