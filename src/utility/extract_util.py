import tempfile
from src.services.s3 import S3Service
from src.utility.pdf_extractor import extract_text_from_pdf
from src.utility.status_util import update_status

s3 = S3Service()

def extract_and_upload(uuid: str, s3_key: str) -> str:
    """Extract text from S3 PDF and upload extracted text back to S3."""
    try:
        file_name_without_extension = uuid  # already extracted earlier

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            result = s3.download_file(s3_key, tmp_file.name)
            if not result["success"]:
                raise Exception(result["error"])

            extracted_text = extract_text_from_pdf(tmp_file.name)
            if not extracted_text:
                raise Exception("Failed to extract text from PDF.")

            extracted_key = f"extracted/{file_name_without_extension}.txt"
            s3.upload_file(
                key=extracted_key,
                file_bytes=extracted_text.encode("utf-8"),
                content_type="text/plain"
            )

            update_status(file_name_without_extension, "extracted")
            return extracted_key

    except Exception as e:
        raise Exception(f"[❌] Failed to process resume: {e}")
