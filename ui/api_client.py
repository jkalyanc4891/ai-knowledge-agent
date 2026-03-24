import requests
from typing import List, Dict, Any


class APIClient:
    """
    Handles communication with the FastAPI backend.
    """

    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url.rstrip("/")

    # -------------------------
    # Document Upload
    # -------------------------
    def upload_document(self, file) -> Dict[str, Any]:
        url = f"{self.base_url}/documents/"
        files = {"file": (file.name, file.getvalue())}
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()

    # -------------------------
    # Query
    # -------------------------
    def query(self, query: str, document_ids: List[str]) -> Dict[str, Any]:
        url = f"{self.base_url}/query/"
        payload = {"query": query, "document_ids": document_ids}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    # -------------------------
    # Health Check
    # -------------------------
    def health(self) -> Dict[str, Any]:
        url = f"{self.base_url}/health/"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()