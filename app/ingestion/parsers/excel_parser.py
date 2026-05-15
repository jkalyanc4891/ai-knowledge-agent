from .base_parser import BaseParser
import pandas as pd
import io

class ExcelParser(BaseParser):
    def parse(self, file_bytes: bytes) -> str:
        df = pd.read_excel(io.BytesIO(file_bytes))
        return df.to_csv(index=False)