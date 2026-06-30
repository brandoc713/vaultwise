from dataclasses import dataclass
from pathlib import Path

from app.models import TextExtractionStatus
from app.services.pdf_text import extract_text_pdfplumber, extract_text_pymupdf


@dataclass(frozen=True)
class PdfDetectionResult:
    status: TextExtractionStatus
    text_preview: str
    message: str


def detect_pdf_text(path: Path, threshold: int = 80) -> PdfDetectionResult:
    try:
        text = extract_text_pdfplumber(path)
        if len(text.strip()) >= threshold:
            return PdfDetectionResult(TextExtractionStatus.text_found, text[:1000], "Text extracted with pdfplumber.")
        text = extract_text_pymupdf(path)
        if len(text.strip()) >= threshold:
            return PdfDetectionResult(TextExtractionStatus.text_found, text[:1000], "Text extracted with PyMuPDF.")
        return PdfDetectionResult(
            TextExtractionStatus.scanned_or_empty,
            text[:1000],
            "This PDF appears scanned or empty. OCR is planned but not included in this slice.",
        )
    except Exception as exc:  # pragma: no cover - defensive boundary around third-party PDF libs
        return PdfDetectionResult(TextExtractionStatus.failed, "", f"PDF text detection failed: {exc}")
