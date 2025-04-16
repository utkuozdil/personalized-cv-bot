import json
import pytest
from unittest.mock import patch, MagicMock
from src.handlers.process_pdf import handler
from src.services import dynamodb, s3, ses

@pytest.fixture
def valid_email():
    return "test@example.com"

@pytest.fixture
def valid_uuid():
    return "test-uuid-123"

@pytest.fixture
def valid_presigned_url():
    return "https://example.com/presigned-url"

@pytest.fixture
def event_with_email(valid_email):
    return {
        "body": json.dumps({
            "email": valid_email
        })
    }

@pytest.fixture
def event_without_email():
    return {
        "body": json.dumps({})
    }

def test_successful_processing(event_with_email, valid_email, valid_uuid, valid_presigned_url):
    with patch('uuid.uuid4', return_value=valid_uuid), \
         patch.object(s3.S3Service, 'get_presigned_upload_url', return_value=valid_presigned_url), \
         patch('src.utility.status_util.write_status'), \
         patch.object(ses.EmailService, 'send_confirmation_email') as mock_send_email:
        
        # Call the handler
        result = handler(event_with_email, None)
        
        # Verify the result
        assert result["statusCode"] == 200
        response_body = json.loads(result["body"])
        assert response_body["upload_url"] == valid_presigned_url

def test_missing_email(event_without_email):
    result = handler(event_without_email, None)
    
    assert result["statusCode"] == 500
    response_body = json.loads(result["body"])
    assert "Email is required" in response_body["error"]

def test_error_generating_presigned_url(event_with_email, valid_uuid):
    with patch('uuid.uuid4', return_value=valid_uuid), \
         patch.object(s3.S3Service, 'get_presigned_upload_url', side_effect=Exception("Test error")):
        
        # Call the handler
        result = handler(event_with_email, None)
        
        # Verify the result
        assert result["statusCode"] == 500
        response_body = json.loads(result["body"])
        assert "Test error" in response_body["error"]

def test_error_sending_email(event_with_email, valid_uuid, valid_presigned_url):
    with patch('uuid.uuid4', return_value=valid_uuid), \
         patch.object(s3.S3Service, 'get_presigned_upload_url', return_value=valid_presigned_url), \
         patch('src.utility.status_util.write_status'), \
         patch.object(ses.EmailService, 'send_confirmation_email', side_effect=Exception("Test error")):
        
        # Call the handler
        result = handler(event_with_email, None)
        
        # Verify the result
        assert result["statusCode"] == 500
        response_body = json.loads(result["body"])
        assert "Test error" in response_body["error"] 