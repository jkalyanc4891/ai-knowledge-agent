from .base_parser import BaseParser

class TXTParser(BaseParser):
    def parse(self, file_bytes: bytes) -> str:
        return file_bytes.decode("utf-8", errors="ignore")