import json
import pytest
from unittest.mock import patch, MagicMock
from src.handlers.confirm_resume import handler

@pytest.fixture
def valid_token():
    return "valid_token_123"

@pytest.fixture
def valid_item():
    return {
        "email": "test@example.com",
        "uuid": "test-uuid-123",
        "confirmed": False
    }

@pytest.fixture
def event_with_token(valid_token):
    return {
        "queryStringParameters": {
            "token": valid_token
        }
    }

@pytest.fixture
def event_without_token():
    return {
        "queryStringParameters": {}
    }

def test_successful_confirmation(event_with_token, valid_token, valid_item):
    with patch('src.handlers.confirm_resume.dynamodb') as mock_dynamodb, \
         patch('src.handlers.confirm_resume.extract_and_upload') as mock_extract, \
         patch('src.handlers.confirm_resume.get_confirm_response') as mock_get_response:
        
        # Setup mocks
        mock_dynamodb.get_by_token.return_value = valid_item
        mock_dynamodb.table.update_item.return_value = None
        mock_extract.return_value = "extracted_key_123"
        mock_get_response.return_value = {"statusCode": 200, "body": "Success"}
        
        # Call the handler
        result = handler(event_with_token, None)
        
        # Verify the result
        assert result["statusCode"] == 200
        
        # Verify the mocks were called correctly
        mock_dynamodb.get_by_token.assert_called_once_with(valid_token)
        mock_dynamodb.table.update_item.assert_called_once()
        mock_extract.assert_called_once_with(valid_item["uuid"], f"uploads/{valid_item['uuid']}")
        mock_get_response.assert_called_once_with(valid_item)

def test_missing_token(event_without_token):
    result = handler(event_without_token, None)
    
    assert result["statusCode"] == 400
    assert "Missing token" in json.loads(result["body"])["error"]

def test_invalid_token(event_with_token, valid_token):
    with patch('src.handlers.confirm_resume.dynamodb') as mock_dynamodb:
        # Setup mock to return None (invalid token)
        mock_dynamodb.get_by_token.return_value = None
        
        # Call the handler
        result = handler(event_with_token, None)
        
        # Verify the result
        assert result["statusCode"] == 404
        assert "Invalid or expired token" in json.loads(result["body"])["error"]
        
        # Verify the mock was called
        mock_dynamodb.get_by_token.assert_called_once_with(valid_token)

def test_error_handling(event_with_token, valid_token):
    with patch('src.handlers.confirm_resume.dynamodb') as mock_dynamodb:
        # Setup mock to raise an exception
        mock_dynamodb.get_by_token.side_effect = Exception("Test error")
        
        # Call the handler
        result = handler(event_with_token, None)
        
        # Verify the result
        assert result["statusCode"] == 500
        assert "Error confirming resume" in json.loads(result["body"])["error"] 