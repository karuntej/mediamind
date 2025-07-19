import fitz, uuid, json, pathlib, tqdm, io, shutil
from typing import List

try:
    import pytesseract
    from PIL import Image
except Exception:  # optional OCR dependencies may be missing
    pytesseract = None
    Image = None

DATA_DIR = pathlib.Path("data")                  # adjust if needed
PDF_DIR  = DATA_DIR / "raw" / "pdf"
OUT_DIR  = DATA_DIR / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

chunks, skipped = [], []

for pdf in tqdm.tqdm(PDF_DIR.rglob("*.pdf"), desc="extract"):
    try:
        doc = fitz.open(pdf, filetype="pdf")     # strict=False by default
        if doc.needs_pass:
            raise ValueError("encrypted")

        for page_no, page in enumerate(doc, 1):
            text = page.get_text()

            # ── OCR images if pytesseract is available ──────────────────────
            if pytesseract and Image and shutil.which("tesseract"):
                for img in page.get_images(full=True):
                    xref = img[0]
                    base = doc.extract_image(xref)
                    img_bytes = base.get("image")
                    if img_bytes:
                        try:
                            im = Image.open(io.BytesIO(img_bytes))
                            text += "\n" + pytesseract.image_to_string(im)
                        except Exception:
                            pass

            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "source"  : "pdf",
                "doc_path": str(pdf),
                "loc"     : {"page": page_no},
                "text"    : text
            })

    except Exception as err:
        skipped.append((pdf.name, str(err)))
        continue

json.dump(chunks, open(OUT_DIR / "all_chunks.json", "w"))
print(f"✅ saved {len(chunks):,} chunks  |  🚫 skipped {len(skipped)} PDFs")
if skipped:
    json.dump(skipped, open(OUT_DIR / "skipped_pdfs.json", "w"))
    print("   → see processed/skipped_pdfs.json for details")

if pytesseract is None or Image is None or not shutil.which("tesseract"):
    print("ℹ️  Install 'pytesseract', 'Pillow' and the tesseract binary for OCR support")
