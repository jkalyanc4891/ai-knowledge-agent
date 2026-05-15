import streamlit as st
from typing import List, Dict, Any
from api_client import APIClient

# -----------------------------------
# Config & API Client
# -----------------------------------
API_BASE_URL = "http://localhost:8000/api"
MAX_UPLOAD_MB = 30
MAX_FILES = 10
api = APIClient(base_url=API_BASE_URL)


# -----------------------------------
# State Initialization
# -----------------------------------
def init_session_state():
    if "documents" not in st.session_state:
        st.session_state.documents = {}  # {filename: {"id": str, "chunks": int}}

    if "answer" not in st.session_state:
        st.session_state.answer = ""

    if "sources" not in st.session_state:
        st.session_state.sources = []

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Key used to reset the uploader widget
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0


# -----------------------------------
# Header
# -----------------------------------
def render_header():
    st.title("📘 AI Knowledge & Decision Support System")
    st.caption("Upload documents → Ask questions → Get grounded answers")


# -----------------------------------
# Document Upload
# -----------------------------------
def render_document_uploader():
    st.subheader("📄 Upload Document")

    uploaded_files = st.file_uploader(
        "Choose files (max 30 MB each)",
        type=["pdf", "txt", "csv", "xlsx"],
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
        max_upload_size=MAX_UPLOAD_MB# 🔥 resets when key changes
    )

    if not uploaded_files:
        return

    if len(uploaded_files) > MAX_FILES:
        st.error(f"⚠️ You selected {len(uploaded_files)} files. Limit is {MAX_FILES}.")
        return

    # Filter oversized files
    valid_files = []
    for file in uploaded_files:
        size_mb = file.size / (1024 * 1024)
        if size_mb > MAX_UPLOAD_MB:
            st.warning(f"⚠️ {file.name} is {size_mb:.2f} MB (limit: {MAX_UPLOAD_MB} MB). Skipping.")
            continue
        if file.name in st.session_state.documents:
            continue
        valid_files.append(file)

    if not valid_files:
        return

    with st.spinner("Uploading documents..."):
        result = api.upload_documents(valid_files)

    if not result["ok"]:
        st.error(result["error"])
        return

    for item in result["data"]["results"]:
        if "error" in item:
            st.error(f"{item['filename']}: {item['error']}")
        else:
            st.session_state.documents[item["filename"]] = {
                "id": item["document_id"],
                "chunks": item["chunks"],
            }
            st.success(f"Uploaded: {item['filename']} ({item['chunks']} chunks)")


def render_uploaded_documents():
    st.subheader("📁 Uploaded Documents")

    if not st.session_state.documents:
        st.info("No documents uploaded yet.")
        return

    # Iterate over a copy to avoid mutation issues
    for filename, meta in list(st.session_state.documents.items()):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{filename}** — `{meta['id']}` ({meta['chunks']} chunks)")
        with col2:
            if st.button("❌ Remove", key=f"remove_{filename}"):
                # Delete from Chroma
                delete_result = api.delete_document(meta["id"])
                if not delete_result["ok"]:
                    st.error(delete_result["error"])
                    return

                # Remove from session state
                del st.session_state.documents[filename]

                # Reset uploader so file doesn't re-upload on rerun
                st.session_state.uploader_key += 1

                st.success(f"Removed {filename}")
                st.rerun()

# -----------------------------------
# Chat & Query Handling
# -----------------------------------
def render_chat_history():
    if not st.session_state.chat_history:
        return

    st.subheader("💬 Chat History")
    for i, turn in enumerate(st.session_state.chat_history):
        with st.expander(f"Turn {i+1}", expanded=False):
            with st.chat_message("user"):
                st.write(turn["user"])
            with st.chat_message("assistant"):
                st.write(turn["ai"])


def handle_query(query: str):
    if not query:
        return

    if not st.session_state.documents:
        st.warning("Please upload at least one document before querying.")
        return

    doc_ids = [meta["id"] for meta in st.session_state.documents.values()]

    with st.spinner("Thinking..."):
        result = api.query(query, doc_ids)

        if not result["ok"]:
            st.error(result["error"])
            return

        response = result["data"]

    # Always overwrite state to avoid stale UI
    st.session_state.answer = response.get("answer", "I don’t know")
    st.session_state.sources = response.get("sources", [])

    # Append to chat history
    st.session_state.chat_history.append(
        {
            "user": query,
            "ai": st.session_state.answer,
        }
    )


def render_chat_input():
    st.subheader("🔍 Ask a Question")
    query = st.chat_input("Type your question...")
    if query:
        handle_query(query)


# -----------------------------------
# Sources Rendering
# -----------------------------------
def render_sources():
    st.subheader("📚 Sources")
    sources: List[Dict[str, Any]] = st.session_state.sources

    if not sources:
        st.info("No sources returned for this answer.")
        return

    for idx, src in enumerate(sources):
        with st.expander(f"Source {idx + 1}", expanded=False):
            st.write(src.get("text", ""))
            st.caption(str(src.get("metadata", {})))


# -----------------------------------
# Main
# -----------------------------------
def main():
    st.set_page_config(page_title="AI Knowledge & Decision Support", layout="wide")
    init_session_state()

    render_header()

    col_left, col_right = st.columns([1, 2])

    with col_left:
        render_document_uploader()
        render_uploaded_documents()

        # 🔄 Refresh / Reset button
        if st.button("🔄 Refresh / Reset"):
            # Delete all documents from Chroma
            for filename, meta in st.session_state.documents.items():
                #api.delete_document(meta["id"])
                delete_result = api.delete_document(meta["id"])
                if not delete_result["ok"]:
                    st.error(delete_result["error"])
                    return

            # Clear session state
            st.session_state.documents = {}
            st.session_state.answer = ""
            st.session_state.sources = []
            st.session_state.chat_history = []

            # Reset uploader widget
            st.session_state.uploader_key += 1

            st.rerun()

        st.markdown(
            """
            ---
            **ℹ️ Note**

            - **Refresh / Reset** will delete *all* uploaded documents from **VectorDB** and clear the UI.
            - **Remove** will remove the file from the **uploaded list** in the UI (and also deletes it from VectorDB for that single file).
            """
        )

    with col_right:
        render_chat_history()
        render_chat_input()

        if st.session_state.answer:
            st.subheader("🧠 Latest Answer")
            st.write(st.session_state.answer)
            render_sources()


if __name__ == "__main__":
    main()
