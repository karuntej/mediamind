import streamlit as st, requests, textwrap, re, html
from src.storage import presigned_url
from highlight_utils import highlight_terms  # your existing helper

st.set_page_config(page_title="MediaMind PDF Chat (S3)")
st.title("MediaMind · PDF Chat")

query = st.text_input("Ask a question about your PDFs and press ↵")
top_k = st.slider("Top-k passages", 1, 10, 5)

if query:
    with st.spinner("Searching…"):
        try:
            resp = requests.post(
                "http://localhost:8001/chat",
                json={"question": query, "top_k": top_k},
                timeout=60
            )
            resp.raise_for_status()
            payload = resp.json()
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

    # 1. Show answer
    if "answer" in payload:
        st.subheader("💡 LLM-Synthesised Answer")
        st.success(payload["answer"])
        st.markdown("---")

    # 2. Show passages
    for idx, p in enumerate(payload["passages"]):
        key    = p["doc_path"]
        page   = p["loc"]["page"]
        score  = p["score"]

        col1, col2 = st.columns([1, 3])
        with col1:
            # embed our preview endpoint
            url = f"http://localhost:8001/preview?key={key}&page={page}"
            st.image(url, use_column_width=True)

        with col2:
            st.markdown(f"**{idx+1}.** {key.split('/')[-1]} · page {page} · score {score:.3f}")
            st.markdown(highlight_terms(query, p["text"]), unsafe_allow_html=True)

        st.divider()
else:
    st.info("Enter a question to get started.")
