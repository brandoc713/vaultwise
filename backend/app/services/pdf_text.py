from pathlib import Path

import fitz
import pdfplumber


def extract_text_pdfplumber(path: Path) -> str:
    parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def extract_text_pymupdf(path: Path) -> str:
    parts: list[str] = []
    with fitz.open(path) as document:
        for page in document:
            parts.append(page.get_text("text") or "")
    return "\n".join(parts).strip()


def extract_pdf_text(path: Path) -> str:
    text = extract_text_pdfplumber(path)
    if text:
        return text
    return extract_text_pymupdf(path)
