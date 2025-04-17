import pytest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os


# Assuming extract_util.py is in src/utility
from src.utility.extract_util import extract_and_upload

# Constants for testing
TEST_UUID = "test-uuid"
TEST_S3_KEY = "uploads/test-uuid.pdf"
MIN_TEXT_LENGTH = 200

@pytest.fixture(autouse=True)
def mock_tempfile_fixture(): # Renamed to avoid conflict with standard library
    # Mock tempfile creation to avoid actual file system operations
    with patch('tempfile.NamedTemporaryFile', MagicMock()) as mock_temp:
        # Ensure the context manager returns the mock object itself
        mock_file = MagicMock()
        mock_file.name = "dummy_temp_file.pdf"
        mock_temp.return_value.__enter__.return_value = mock_file
        yield mock_temp

def test_extract_and_upload_success():
    """Test successful extraction and upload."""
    with patch('src.utility.extract_util.s3', MagicMock()) as mock_s3, \
         patch('src.utility.extract_util.extract_text_from_pdf') as mock_extract_pdf, \
         patch('src.utility.extract_util.update_status') as mock_update_status:

        # Mock S3 download success
        mock_s3.download_file.return_value = {"success": True}
        # Mock PDF extraction success (long enough text)
        mock_extract_pdf.return_value = "a" * MIN_TEXT_LENGTH
        # Mock S3 upload success
        mock_s3.upload_file.return_value = {"success": True}

        expected_key = f"extracted/{TEST_UUID}.txt"
        result_key = extract_and_upload(TEST_UUID, TEST_S3_KEY)

        assert result_key == expected_key
        mock_s3.download_file.assert_called_once_with(TEST_S3_KEY, "dummy_temp_file.pdf")
        mock_extract_pdf.assert_called_once_with("dummy_temp_file.pdf")
        mock_s3.upload_file.assert_called_once_with(
            key=expected_key,
            file_bytes=("a" * MIN_TEXT_LENGTH).encode("utf-8"),
            content_type="text/plain"
        )
        mock_update_status.assert_called_once_with(TEST_UUID, "extracted")

def test_extract_and_upload_extraction_failed_empty():
    """Test extraction failing due to empty text."""
    with patch('src.utility.extract_util.s3', MagicMock()) as mock_s3, \
         patch('src.utility.extract_util.extract_text_from_pdf') as mock_extract_pdf, \
         patch('src.utility.extract_util.update_status') as mock_update_status:

        mock_s3.download_file.return_value = {"success": True}
        mock_extract_pdf.return_value = "" # Empty string

        with pytest.raises(Exception, match="Failed to extract text from PDF."):
            extract_and_upload(TEST_UUID, TEST_S3_KEY)

        mock_s3.download_file.assert_called_once()
        mock_extract_pdf.assert_called_once()
        mock_update_status.assert_called_once_with(TEST_UUID, "extraction_failed")
        mock_s3.upload_file.assert_not_called()

def test_extract_and_upload_extraction_failed_none():
    """Test extraction failing due to None text."""
    with patch('src.utility.extract_util.s3', MagicMock()) as mock_s3, \
         patch('src.utility.extract_util.extract_text_from_pdf') as mock_extract_pdf, \
         patch('src.utility.extract_util.update_status') as mock_update_status:

        mock_s3.download_file.return_value = {"success": True}
        mock_extract_pdf.return_value = None # None value

        with pytest.raises(Exception, match="Failed to extract text from PDF."):
            extract_and_upload(TEST_UUID, TEST_S3_KEY)

        mock_s3.download_file.assert_called_once()
        mock_extract_pdf.assert_called_once()
        mock_update_status.assert_called_once_with(TEST_UUID, "extraction_failed")
        mock_s3.upload_file.assert_not_called()

def test_extract_and_upload_extraction_insufficient():
    """Test extraction yielding insufficient text."""
    with patch('src.utility.extract_util.s3', MagicMock()) as mock_s3, \
         patch('src.utility.extract_util.extract_text_from_pdf') as mock_extract_pdf, \
         patch('src.utility.extract_util.update_status') as mock_update_status:

        mock_s3.download_file.return_value = {"success": True}
        short_text = "a" * (MIN_TEXT_LENGTH - 1)
        mock_extract_pdf.return_value = short_text

        with pytest.raises(Exception, match="Extracted text is too short"):
            extract_and_upload(TEST_UUID, TEST_S3_KEY)

        mock_s3.download_file.assert_called_once()
        mock_extract_pdf.assert_called_once()
        mock_update_status.assert_called_once_with(TEST_UUID, "extraction_insufficient")
        mock_s3.upload_file.assert_not_called()

def test_extract_and_upload_s3_download_error():
    """Test failure during S3 download."""
    with patch('src.utility.extract_util.s3', MagicMock()) as mock_s3, \
         patch('src.utility.extract_util.extract_text_from_pdf') as mock_extract_pdf, \
         patch('src.utility.extract_util.update_status') as mock_update_status:

        mock_s3.download_file.return_value = {"success": False, "error": "Download failed"}

        with pytest.raises(Exception, match="Download failed"):
            extract_and_upload(TEST_UUID, TEST_S3_KEY)

        mock_s3.download_file.assert_called_once()
        mock_extract_pdf.assert_not_called()
        mock_update_status.assert_not_called()
        mock_s3.upload_file.assert_not_called()

def test_extract_and_upload_pdf_extraction_error():
    """Test failure during PDF text extraction itself."""
    with patch('src.utility.extract_util.s3', MagicMock()) as mock_s3, \
         patch('src.utility.extract_util.extract_text_from_pdf') as mock_extract_pdf, \
         patch('src.utility.extract_util.update_status') as mock_update_status:

        mock_s3.download_file.return_value = {"success": True}
        mock_extract_pdf.side_effect = Exception("PDF parsing error")

        with pytest.raises(Exception, match="Failed to process resume: PDF parsing error"):
             extract_and_upload(TEST_UUID, TEST_S3_KEY)

        mock_s3.download_file.assert_called_once()
        mock_extract_pdf.assert_called_once()
        # Note: update_status is not called because the error happens *before* the checks
        mock_update_status.assert_not_called()
        mock_s3.upload_file.assert_not_called()

def test_extract_and_upload_s3_upload_error():
    """Test failure during S3 upload."""
    with patch('src.utility.extract_util.s3', MagicMock()) as mock_s3, \
         patch('src.utility.extract_util.extract_text_from_pdf') as mock_extract_pdf, \
         patch('src.utility.extract_util.update_status') as mock_update_status:

        mock_s3.download_file.return_value = {"success": True}
        mock_extract_pdf.return_value = "a" * MIN_TEXT_LENGTH
        # Mock S3 upload failure
        mock_s3.upload_file.side_effect = Exception("Upload failed")

        with pytest.raises(Exception, match="Failed to process resume: Upload failed"):
            extract_and_upload(TEST_UUID, TEST_S3_KEY)

        mock_s3.download_file.assert_called_once()
        mock_extract_pdf.assert_called_once()
        mock_s3.upload_file.assert_called_once()
        # Status is updated before the upload attempt fails in this case
        mock_update_status.assert_not_called() # Status should only be 'extracted' on *successful* upload

# Removed commented out directory creation helper
# Note: This assumes a standard project structure. Adjust if necessary.
# import os
# test_dir = os.path.dirname(__file__)
# utility_dir = os.path.join(test_dir, '..', 'src', 'utility')
# if not os.path.exists(test_dir):
#     os.makedirs(test_dir) 