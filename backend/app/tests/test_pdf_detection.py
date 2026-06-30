from pathlib import Path

from reportlab.pdfgen import canvas

from app.models import TextExtractionStatus
from app.services.pdf_detection import detect_pdf_text


def make_pdf(path: Path, text: str | None) -> None:
    pdf = canvas.Canvas(str(path))
    if text:
        pdf.drawString(72, 720, text)
    pdf.showPage()
    pdf.save()


def test_text_based_pdf_detects_text(tmp_path):
    pdf_path = tmp_path / "statement.pdf"
    make_pdf(pdf_path, "2026-06-30 KROGER #4481 -42.10 " * 5)
    result = detect_pdf_text(pdf_path, threshold=20)
    assert result.status == TextExtractionStatus.text_found


def test_empty_pdf_detects_scanned_or_empty(tmp_path):
    pdf_path = tmp_path / "empty.pdf"
    make_pdf(pdf_path, None)
    result = detect_pdf_text(pdf_path, threshold=20)
    assert result.status == TextExtractionStatus.scanned_or_empty
