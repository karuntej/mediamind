# Media Mind

A media processing and storage system with MinIO S3-compatible storage.

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install fastapi pydantic faiss-cpu numpy sentence-transformers requests PyMuPDF pyyaml tqdm spacy streamlit uvicorn urllib3
```

### Configuration

The system uses `config.yaml` for S3/MinIO configuration. Make sure MinIO is running and accessible.

## Running Scripts

### Method 1: Using the helper script (Recommended)

```bash
./run_script.sh scripts/script_name.py
```

Examples:
```bash
./run_script.sh scripts/ingest_media.py
./run_script.sh scripts/extract_pdf.py
./run_script.sh scripts/test_minio_connection.py
```

### Method 2: Using PYTHONPATH

```bash
PYTHONPATH=. python scripts/script_name.py
```

### Method 3: Export PYTHONPATH (for multiple runs)

```bash
export PYTHONPATH="$PWD"
python scripts/script_name.py
```

## Available Scripts

- `scripts/ingest_media.py` - Upload files from `incoming/` directory to MinIO
- `scripts/extract_pdf.py` - Extract text from PDFs stored in MinIO
- `scripts/embed_index.py` - Create FAISS index from extracted text
- `scripts/enrich_chunks.py` - Add NER entities to text chunks
- `scripts/test_minio_connection.py` - Test MinIO connection
- `scripts/test_imports.py` - Test import functionality

## Project Structure

```
mediamind/
├── config.yaml          # S3/MinIO configuration
├── src/                 # Source code package
│   ├── __init__.py
│   ├── storage.py       # S3/MinIO storage utilities
│   └── utils_pdf.py
├── scripts/             # Scripts package
│   ├── __init__.py
│   ├── ingest_media.py
│   ├── extract_pdf.py
│   └── ...
├── data/                # Local data storage
├── incoming/            # Place new files here for ingestion
└── run_script.sh       # Helper script for running with correct PYTHONPATH
```
