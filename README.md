# Media Mind

# Install requirements.txt dependencies using
pip install -r requirements.txt

or 

pip install fastapi pydantic faiss-cpu numpy sentence-transformers requests PyMuPDF tqdm spacy streamlit uvicorn urllib3

## Run the application

Use the convenience script below to launch Ollama, the FastAPI server and the
Streamlit UI in one go:

```bash
python scripts/run_app.py
```

Any existing instances of these processes will be terminated automatically so
you don't need to clear the ports manually.
