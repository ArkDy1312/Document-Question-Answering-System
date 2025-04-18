from app.ingest import parser
import os

def test_pdf_extraction():
    path = "data/uploads/sample.pdf"
    assert os.path.exists(path)
    text = parser.extract_text(path)
    assert isinstance(text, str)
    assert len(text) > 20

def test_txt_extraction():
    path = "data/uploads/sample.txt"
    assert os.path.exists(path)
    text = parser.extract_text(path)
    assert isinstance(text, str)
    assert len(text) > 20
