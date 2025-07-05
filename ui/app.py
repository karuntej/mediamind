# ui/app.py
"""
Streamlit front-end for MediaMind PDF Chat (LLM + Retrieval)
-----------------------------------------------------------
• Ask a question about your PDF corpus
• See a concise LLM answer (via Ollama / Llama-3)
• Inspect the top-k supporting passages, with highlighted keywords
• View a thumbnail of each cited PDF page
"""

import streamlit as st
import requests, textwrap, re, html
import fitz                           # PyMuPDF
import functools
from pathlib import Path
from src.utils_pdf import render_page_png   # already imported earlier


###############################################################################
# CONFIG
###############################################################################
API_URL   = "http://localhost:8001/chat"   # FastAPI endpoint
TOP_K_MAX = 10
PAGE_ZOOM = 1.4                           # thumbnail DPI scale

###############################################################################
# UTILS
###############################################################################
@functools.lru_cache(maxsize=256)
def render_page_png(pdf_path: str, page_no: int, zoom: float = PAGE_ZOOM) -> bytes:
    """
    Return raw PNG bytes for a single PDF page.
    Cached for speed so repeated renders don't hit the disk.
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_no - 1)
    pix  = page.get_pixmap(dpi=72 * zoom)
    return pix.tobytes("png")


def highlight_terms(query: str, text: str, max_chars: int = 400) -> str:
    """
    Simple case-insensitive highlight of each 4+ char token from the query.
    """
    snippet = textwrap.shorten(text.replace("\n", " "), max_chars, placeholder=" …")
    tokens  = [re.escape(w) for w in query.split() if len(w) >= 4]
    if not tokens:
        return html.escape(snippet)

    pattern = re.compile("(" + "|".join(tokens) + ")", re.I)
    return pattern.sub(r"<mark>\1</mark>", html.escape(snippet))


###############################################################################
# STREAMLIT LAYOUT
###############################################################################
st.set_page_config(page_title="MediaMind PDF Chat", layout="wide")
st.title("📚 MediaMind · PDF Chat")

with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Top-k passages", 1, TOP_K_MAX, 5)
    st.markdown("---")
    st.write("🔌 **API**:", API_URL)

query = st.text_input("Ask a question about your PDFs and press ↵", key="query")

###############################################################################
# MAIN LOGIC
###############################################################################
if query:
    with st.spinner("Searching…"):
        try:
            res = requests.post(API_URL, json={"question": query, "top_k": top_k}, timeout=120)
            res.raise_for_status()
            payload = res.json()
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

    # ── 1. Show the LLM answer ──────────────────────────────────────────────
    if "answer" in payload and payload["answer"]:
        st.subheader("💡 LLM-Synthesised Answer")
        st.success(payload["answer"])

    st.markdown("---")

    # ── 2. Show supporting passages ─────────────────────────────────────────
    for idx, p in enumerate(payload["passages"]):
        pdf_name = Path(p["doc_path"]).name
        page_no  = p["loc"].get("page", "?")
        score    = p["score"]

        col1, col2 = st.columns([1, 3])
        with col1:
            pdf_path = Path(p["doc_path"]).expanduser().resolve()
            print("UI got path →", pdf_path)          # <-- add this once for debugging
            if pdf_path.exists():
                st.image(render_page_png(str(pdf_path), page_no), use_column_width=True)
            else:
                st.caption(":grey[Preview unavailable]")



        with col2:
            st.markdown(f"**{idx+1}. {pdf_name}  ·  page {page_no}  ·  score {score:.3f}**")
            st.write(highlight_terms(query, p["text"]), unsafe_allow_html=True)

        st.divider()

else:
    st.info("Enter a question in the box above to get started!")
