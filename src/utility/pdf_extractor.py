import logging
import pdfplumber


def extract_text_from_pdf(file_path):
    try:
        full_text = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    full_text.append(text.strip())
                else:
                    logging.warning(f"No text found on page {i} in {file_path}")
        return "\n\n".join(full_text)
    except Exception as e:
        logging.error(f"Error extracting text from {file_path}: {e}")
        return None
