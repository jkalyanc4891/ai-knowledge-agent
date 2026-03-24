import streamlit as st
from typing import List, Dict, Any
from api_client import APIClient

api = APIClient(base_url="http://localhost:8000/api")


# -----------------------------
# Header
# -----------------------------
def render_header():
    st.title("📘 AI Knowledge & Decision Support System")
    st.caption("Upload documents → Ask questions → Get grounded answers")


# -----------------------------
# Document Upload
# -----------------------------
def render_document_uploader():
    st.subheader("📄 Upload Document")
    return st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "csv", "xlsx"],
        accept_multiple_files=True
    )


def handle_uploads(uploaded_files):
    """Ingest only NEW files, never re-ingest on rerun."""
    if "documents" not in st.session_state:
        st.session_state.documents = {}  # {doc_id: filename}

    if not uploaded_files:
        return

    for file in uploaded_files:
        if file.name not in st.session_state.documents:
            with st.spinner(f"Uploading {file.name}..."):
                doc_id = api.upload_document(file)
                st.session_state.documents[file.name] = doc_id["document_id"]
                st.success(f"Uploaded: {file.name} ({doc_id['chunks']} chunks)")


def render_uploaded_documents():
    st.subheader("📁 Uploaded Documents")

    if "documents" not in st.session_state or not st.session_state.documents:
        st.info("No documents uploaded yet.")
        return

    for filename, doc_id in st.session_state.documents.items():
        st.write(f"**{filename}** — `{doc_id}`")


# -----------------------------
# Query
# -----------------------------
def render_query_box():
    st.subheader("🔍 Ask a Question")
    return st.text_input("Enter your question")


def handle_query(query):
    if not query:
        return

    if "documents" not in st.session_state or not st.session_state.documents:
        st.warning("Please upload at least one document before querying.")
        return
    #st.write("DEBUG DOCS:", st.session_state.documents)
    doc_ids = list(st.session_state.documents.values())
    #st.write("DEBUG DOC IDS:", doc_ids)

    with st.spinner("Thinking..."):
        response = api.query(query, doc_ids)

    st.subheader("🧠 Answer")
    st.write(response["answer"])

    render_sources(response.get("sources", []))


# -----------------------------
# Sources
# -----------------------------
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


# -----------------------------
# Main
# -----------------------------
def main():
    render_header()

    uploaded_files = render_document_uploader()
    handle_uploads(uploaded_files)

    render_uploaded_documents()

    query = render_query_box()
    handle_query(query)


if __name__ == "__main__":
    main()