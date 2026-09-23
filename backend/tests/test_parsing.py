import io
import pytest
from app.core.parsing import extract_text, get_extension, MAX_FILE_BYTES


def create_sample_docx_bytes(text: str) -> bytes:
    from docx import Document
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def create_sample_pdf_bytes(text: str) -> bytes:
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, ArrayObject, DecodedStreamObject

    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    # Add a simple text stream content to the PDF page
    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 12 Tf 72 712 Td ({text}) Tj ET".encode("latin1"))
    page[NameObject("/Contents")] = stream

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_get_extension():
    assert get_extension("resume.pdf") == ".pdf"
    assert get_extension("My_CV.DOCX") == ".docx"
    assert get_extension("file.tar.gz") == ".gz"
    assert get_extension("") == ""


def test_unsupported_file_extension():
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text("cv.txt", b"plain text")

    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text("cv.png", b"\x89PNG\r\n\x1a\n")


def test_empty_file():
    with pytest.raises(ValueError, match="uploaded file is empty"):
        extract_text("cv.pdf", b"")


def test_docx_extraction():
    sample_text = "Jane Doe - Senior Software Engineer"
    docx_bytes = create_sample_docx_bytes(sample_text)
    extracted = extract_text("resume.docx", docx_bytes)
    assert sample_text in extracted


def test_pdf_extraction_scanned_or_empty():
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)
    empty_pdf_bytes = buf.getvalue()

    with pytest.raises(ValueError, match="Could not extract any text from the PDF"):
        extract_text("empty.pdf", empty_pdf_bytes)
