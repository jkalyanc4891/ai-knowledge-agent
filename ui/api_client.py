import requests
from typing import List, Dict, Any


class APIClient:
    """
    Handles communication with the FastAPI backend.
    """

    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url.rstrip("/")

    # -------------------------
    # D
    # -------------------------
    def _safe_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return {"ok": True, "data": response.json()}
        except requests.exceptions.ConnectionError:
            return {"ok": False, "error": "Backend is not reachable. Please ensure the FastAPI server is running."}
        except requests.exceptions.HTTPError as e:
            return {"ok": False, "error": f"HTTP error: {str(e)}"}
        except Exception as e:
            return {"ok": False, "error": f"Unexpected error: {str(e)}"}

    # -------------------------
    # Document Upload
    # -------------------------
    def upload_document(self, file) -> Dict[str, Any]:
        #url = f"{self.base_url}/documents/"
        #files = {"file": (file.name, file.getvalue())}
        #response = requests.post(url, files=files)
        #response.raise_for_status()
        #return response.json()
        url = f"{self.base_url}/documents/"
        files = {"file": (file.name, file.getvalue())}
        return self._safe_request("POST", url, files=files)

    # -------------------------
    # Query
    # -------------------------
    def query(self, query: str, document_ids: List[str]) -> Dict[str, Any]:
        #url = f"{self.base_url}/query/"
        #payload = {"query": query, "document_ids": document_ids}
        #response = requests.post(url, json=payload)
        #response.raise_for_status()
        #return response.json()
        url = f"{self.base_url}/query"
        payload = {"query": query, "document_ids": document_ids}
        return self._safe_request("POST", url, json=payload)

    # -------------------------
    # Health Check
    # -------------------------
    def health(self) -> Dict[str, Any]:
        #url = f"{self.base_url}/health/"
        #response = requests.get(url)
        #response.raise_for_status()
        #return response.json()
        url = f"{self.base_url}/health/"
        return self._safe_request("GET", url)

    # -------------------------
    # Delete Document from Vector Store
    # -------------------------
    def delete_document(self, doc_id: str):
        #url = f"{self.base_url}/documents/{doc_id}"
        #response = requests.delete(url)
        #response.raise_for_status()
        #return response.json()
        url = f"{self.base_url}/documents/{doc_id}"
        return self._safe_request("DELETE", url)
