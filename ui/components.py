import streamlit as st
from typing import List, Dict, Any


def render_header():
    st.title("📘 AI Knowledge & Decision Support System")
    st.caption("Upload documents → Ask questions → Get grounded answers")


def render_document_uploader() -> Any:
    st.subheader("📄 Upload Document")
    return st.file_uploader("Choose a file", type=["pdf", "txt", "csv", "xlsx"])


def render_uploaded_documents(documents: Dict[str, str]):
    st.subheader("📁 Uploaded Documents")
    if not documents:
        st.info("No documents uploaded yet.")
        return

    for doc_id, filename in documents.items():
        st.write(f"**{filename}** — `{doc_id}`")


def render_query_box() -> str:
    st.subheader("🔍 Ask a Question")
    return st.text_input("Enter your question")


def render_sources(sources: List[Dict[str, Any]]):
    st.subheader("📚 Sources")
    if not sources:
        st.warning("No sources returned.")
        return

    for idx, src in enumerate(sources):
        st.markdown(f"### Source {idx+1}")
        st.write(src.get("text", ""))
        st.caption(str(src.get("metadata", {})))
        st.divider()