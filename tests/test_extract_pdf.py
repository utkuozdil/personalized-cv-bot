import os

from src.utility.pdf_extractor import extract_text_from_pdf2

def test_extract_text_from_sample_pdf():
    sample_pdf_path = "tests/example_cv.pdf"
    text = extract_text_from_pdf2(sample_pdf_path)
    print(text)

