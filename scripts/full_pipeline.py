#!/usr/bin/env python3
"""Run the entire MediaMind processing pipeline."""
import runpy
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def main():
    # sync local data to S3
    runpy.run_path(str(SCRIPT_DIR / 'sync_to_s3.py'))
    # extract PDFs from S3
    runpy.run_path(str(SCRIPT_DIR / 'extract_pdf.py'))
    # enrich chunks with spaCy NER
    runpy.run_path(str(SCRIPT_DIR / 'enrich_chunks.py'))
    # build embeddings and FAISS index
    runpy.run_path(str(SCRIPT_DIR / 'embed_index.py'))

if __name__ == '__main__':
    main()
