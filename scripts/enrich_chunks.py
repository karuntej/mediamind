#!/usr/bin/env python
"""
Usage: python scripts/enrich_chunks.py
Adds NER entities to pdf_chunks.json → all_chunks.json
"""
import json, spacy, pathlib, tqdm, os
IN_FILE  = pathlib.Path("data/processed/pdf_chunks.json")
OUT_FILE = pathlib.Path("data/processed/all_chunks.json")

nlp = spacy.load("en_core_web_sm")          # run `python -m spacy download en_core_web_sm` once
chunks = json.load(open(IN_FILE))

for c in tqdm.tqdm(chunks, desc="spaCy NER"):
    doc = nlp(c["text"][:5000])
    c["ents"] = [{"text": e.text, "label": e.label_} for e in doc.ents]

json.dump(chunks, open(OUT_FILE, "w"))
print("✔ ner-enriched chunks →", OUT_FILE)
