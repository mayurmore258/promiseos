"""Parser for CSV tabular files."""

import csv
import io
from typing import Tuple
from app.core.exceptions import MalformedFileError
from app.utils.text import clean_text


class CSVParser:
    """Extracts tabular records from CSV files, normalizing headers and row content."""

    def parse(self, content_bytes: bytes, filename: str) -> Tuple[str, dict]:
        try:
            try:
                decoded = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                decoded = content_bytes.decode("latin-1")

            f = io.StringIO(decoded)
            reader = csv.reader(f)
            rows = list(reader)

            if not rows:
                return "", {"format": "csv", "row_count": 0, "column_count": 0}

            headers = [h.strip() for h in rows[0]]
            lines = [", ".join(headers)]

            for row in rows[1:]:
                if not any(row):
                    continue
                # Format as structured row: "Header: Value"
                row_items = []
                for idx, cell in enumerate(row):
                    h = headers[idx] if idx < len(headers) else f"col_{idx}"
                    row_items.append(f"{h}: {cell.strip()}")
                lines.append(" | ".join(row_items))

            full_text = clean_text("\n".join(lines))
            metadata = {
                "format": "csv",
                "row_count": len(rows),
                "column_count": len(headers),
                "headers": headers,
                "character_count": len(full_text),
            }
            return full_text, metadata
        except Exception as e:
            raise MalformedFileError(filename, f"Failed to parse CSV content: {str(e)}")
