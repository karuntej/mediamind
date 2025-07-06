#!/usr/bin/env python
import fitz, uuid, json, pathlib, tqdm
from src.storage import list_pdfs, download_pdf

OUT_DIR = pathlib.Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

chunks, skipped = [], []

for key in tqdm.tqdm(list_pdfs(), desc="extracting from S3"):
    try:
        data = download_pdf(key)
        doc  = fitz.open(stream=data, filetype="pdf")
        if doc.needs_pass:
            raise ValueError("encrypted")

        for page_no, page in enumerate(doc, start=1):
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "source"  : "s3",
                "doc_path": key,              # record the S3 key
                "loc"     : {"page": page_no},
                "text"    : page.get_text(),
            })

    except Exception as e:
        skipped.append((key, str(e)))

# write out exactly as before
json.dump(chunks, open(OUT_DIR/"all_chunks.json", "w"), indent=2)
print(f"✅ extracted {len(chunks):,} chunks")
if skipped:
    json.dump(skipped, open(OUT_DIR/"skipped_pdfs.json", "w"), indent=2)
    print(f"🚫 skipped {len(skipped)} PDFs")
