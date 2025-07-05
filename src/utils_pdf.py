import fitz      # PyMuPDF
import functools
from pathlib import Path
from typing import Union

@functools.lru_cache(maxsize=256)
def render_page_png(pdf_path: Union[str, Path], page_no: int, zoom: float = 1.5) -> bytes:
    """
    Returns raw PNG bytes for a single page; memoised for speed.
    """
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_no - 1)
    pix  = page.get_pixmap(dpi=72*zoom)
    return pix.tobytes("png")      # ready for st.image(...)
