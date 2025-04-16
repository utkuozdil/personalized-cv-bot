import pytest
import boto3
from botocore.exceptions import ClientError
from unittest.mock import MagicMock, patch
from src.services.s3 import S3Service

@pytest.fixture
def mock_s3_client():
    with patch('boto3.client') as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3

@pytest.fixture
def s3_service(mock_s3_client):
    return S3Service(bucket_name="test-bucket")

def test_get_file_content_success(s3_service, mock_s3_client):
    # Setup mock response
    mock_response = {
        'Body': MagicMock()
    }
    mock_response['Body'].read.return_value = b"test content"
    mock_s3_client.get_object.return_value = mock_response

    # Test the method
    result = s3_service.get_file_content("test-key")
    
    # Verify the result
    assert result == "test content"
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="test-key"
    )

def test_get_file_content_error(s3_service, mock_s3_client):
    # Setup mock to raise an error
    mock_s3_client.get_object.side_effect = ClientError(
        {'Error': {'Code': 'NoSuchKey', 'Message': 'Not found'}},
        'GetObject'
    )

    # Test the method
    result = s3_service.get_file_content("non-existent-key")
    
    # Verify the result
    assert result is None

def test_upload_file_success(s3_service, mock_s3_client):
    # Test data
    test_key = "test-key"
    test_content = b"test content"
    
    # Test the method
    result = s3_service.upload_file(test_key, test_content)
    
    # Verify the result
    assert result["success"] is True
    assert result["key"] == test_key
    mock_s3_client.put_object.assert_called_once_with(
        Bucket="test-bucket",
        Key=test_key,
        Body=test_content,
        ContentType="application/pdf"
    )

def test_upload_file_error(s3_service, mock_s3_client):
    # Setup mock to raise an error
    mock_s3_client.put_object.side_effect = ClientError(
        {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
        'PutObject'
    )

    # Test the method
    result = s3_service.upload_file("test-key", b"test content")
    
    # Verify the result
    assert result["success"] is False
    assert "error" in result

def test_get_presigned_upload_url_success(s3_service, mock_s3_client):
    # Setup mock response
    mock_s3_client.generate_presigned_url.return_value = "https://test-url.com"
    
    # Test the method
    result = s3_service.get_presigned_upload_url("test-key")
    
    # Verify the result
    assert result == "https://test-url.com"
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        'put_object',
        Params={
            'Bucket': "test-bucket",
            'Key': "test-key",
            'ContentType': "application/pdf"
        },
        ExpiresIn=3600
    )

def test_get_presigned_upload_url_error(s3_service, mock_s3_client):
    # Setup mock to raise an error
    mock_s3_client.generate_presigned_url.side_effect = ClientError(
        {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
        'GeneratePresignedUrl'
    )

    # Test the method
    result = s3_service.get_presigned_upload_url("test-key")
    
    # Verify the result
    assert result is None 