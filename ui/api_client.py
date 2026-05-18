import requests
from typing import List, Dict, Any
import logging
logger = logging.getLogger(__name__)


class APIClient:
    """
    Handles communication with the FastAPI backend.
    """

    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url.rstrip("/")

    # -------------------------
    # Safe Request
    # -------------------------
    def _safe_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return {"ok": True, "data": response.json()}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: Backend is not reachable. Please ensure the FastAPI server is running.")
            return {"ok": False, "error": "Backend is not reachable. Please ensure the FastAPI server is running."}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            return {"ok": False, "error": f"HTTP error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"ok": False, "error": f"Unexpected error: {str(e)}"}

    # -------------------------
    # Document Upload
    # -------------------------
    def upload_documents(self, files_list) -> Dict[str, Any]:
        url = f"{self.base_url}/documents/"
        logger.info(f"Uploading {len(files_list)} files to {url}")
        files = [
            ("files", (f.name, f.getvalue()))
            for f in files_list
        ]
        return self._safe_request("POST", url, files=files)



    # -------------------------
    # Query
    # -------------------------
    def query(self, query: str, document_ids: List[str]) -> Dict[str, Any]:
        url = f"{self.base_url}/query"
        payload = {"query": query, "document_ids": document_ids}
        return self._safe_request("POST", url, json=payload)

    # -------------------------
    # Health Check
    # -------------------------
    def health(self) -> Dict[str, Any]:
        url = f"{self.base_url}/health/"
        return self._safe_request("GET", url)

    # -------------------------
    # Delete Document from Vector Store
    # -------------------------
    def delete_document(self, doc_id: str):
        url = f"{self.base_url}/documents/{doc_id}"
        logger.info(f"Deleting {url}")
        return self._safe_request("DELETE", url)
