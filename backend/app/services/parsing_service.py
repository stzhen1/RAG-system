import io
from typing import Dict, Any
from app.config import settings


class ParsingService:
    def parse(self, content: bytes, filename: str) -> Dict[str, Any]:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        if ext == "pdf":
            return self.parse_pdf(content, filename)
        elif ext in ("txt", "md"):
            return self.parse_text(content, filename)
        else:
            return {"error": f"Unsupported file type: .{ext}"}

    def parse_pdf(self, content: bytes, filename: str) -> Dict[str, Any]:
        from PyPDF2 import PdfReader
        try:
            reader = PdfReader(io.BytesIO(content))
            if len(reader.pages) > settings.max_pdf_pages:
                return {"error": f"PDF exceeds max pages ({settings.max_pdf_pages})"}

            full_text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"

            return {
                "text": full_text.strip(),
                "page_count": len(reader.pages),
                "file_type": "pdf",
            }
        except Exception as e:
            return {"error": str(e)}

    def parse_pdf_text_only(self, content: bytes, filename: str) -> Dict[str, Any]:
        return self.parse_pdf(content, filename)

    def parse_text(self, content: bytes, filename: str) -> Dict[str, Any]:
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("latin-1")
            except Exception as e:
                return {"error": f"Failed to decode text file: {e}"}

        return {
            "text": text.strip(),
            "page_count": 1,
            "file_type": filename.rsplit(".", 1)[-1].lower(),
        }
