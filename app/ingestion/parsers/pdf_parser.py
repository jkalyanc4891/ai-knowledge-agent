from .base_parser import BaseParser
from pypdf import PdfReader
import io

class PDFParser(BaseParser):
    def parse(self, file_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)