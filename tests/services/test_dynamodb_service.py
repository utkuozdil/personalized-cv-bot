import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from src.services.dynamodb import DynamodbService

@pytest.fixture
def mock_dynamodb():
    with patch('boto3.resource') as mock_resource:
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        yield mock_table

@pytest.fixture
def dynamodb_service(mock_dynamodb):
    return DynamodbService()

def test_create_upload(dynamodb_service, mock_dynamodb):
    # Test data
    email = "test@example.com"
    uuid = "test-uuid"
    filename = "test.pdf"
    token = "test-token"
    
    # Test the method
    dynamodb_service.create_upload(email, uuid, filename, token)
    
    # Verify the call
    mock_dynamodb.put_item.assert_called_once()
    call_args = mock_dynamodb.put_item.call_args[1]['Item']
    assert call_args['email'] == email
    assert call_args['uuid'] == uuid
    assert call_args['filename'] == filename
    assert call_args['secure_token'] == token
    assert call_args['status'] == "created"
    assert call_args['confirmed'] is False
    assert isinstance(call_args['created_at'], str)
    assert isinstance(call_args['updated_at'], str)

def test_get_by_email(dynamodb_service, mock_dynamodb):
    # Setup mock response
    mock_items = [
        {'email': 'test@example.com', 'uuid': 'test-uuid-1'},
        {'email': 'test@example.com', 'uuid': 'test-uuid-2'}
    ]
    mock_dynamodb.query.return_value = {'Items': mock_items}
    
    # Test the method
    result = dynamodb_service.get_by_email('test@example.com')
    
    # Verify the result
    assert result == mock_items
    mock_dynamodb.query.assert_called_once()

def test_get_by_uuid(dynamodb_service, mock_dynamodb):
    # Setup mock response
    mock_items = [{'email': 'test@example.com', 'uuid': 'test-uuid'}]
    mock_dynamodb.query.return_value = {'Items': mock_items}
    
    # Test the method
    result = dynamodb_service.get_by_uuid('test-uuid')
    
    # Verify the result
    assert result == mock_items[0]
    mock_dynamodb.query.assert_called_once()

def test_get_by_uuid_not_found(dynamodb_service, mock_dynamodb):
    # Setup mock response with no items
    mock_dynamodb.query.return_value = {'Items': []}
    
    # Test the method
    result = dynamodb_service.get_by_uuid('non-existent-uuid')
    
    # Verify the result
    assert result is None

def test_get_by_token(dynamodb_service, mock_dynamodb):
    # Setup mock response
    mock_items = [{'email': 'test@example.com', 'token': 'test-token'}]
    mock_dynamodb.query.return_value = {'Items': mock_items}
    
    # Test the method
    result = dynamodb_service.get_by_token('test-token')
    
    # Verify the result
    assert result == mock_items[0]
    mock_dynamodb.query.assert_called_once()

def test_append_message(dynamodb_service, mock_dynamodb):
    # Setup mock response for get_by_uuid
    mock_item = {
        'email': 'test@example.com',
        'uuid': 'test-uuid',
        'conversation': []
    }
    mock_dynamodb.query.return_value = {'Items': [mock_item]}
    
    # Test data
    message = {'role': 'user', 'content': 'test message'}
    
    # Test the method
    dynamodb_service.append_message('test-uuid', message)
    
    # Verify the update call
    mock_dynamodb.update_item.assert_called_once()
    call_args = mock_dynamodb.update_item.call_args[1]
    assert call_args['Key'] == {'email': 'test@example.com', 'uuid': 'test-uuid'}
    assert 'conversation' in call_args['UpdateExpression']
    assert 'updated_at' in call_args['UpdateExpression']

def test_update_status(dynamodb_service, mock_dynamodb):
    # Setup mock response for get_by_uuid
    mock_item = {
        'email': 'test@example.com',
        'uuid': 'test-uuid'
    }
    mock_dynamodb.query.return_value = {'Items': [mock_item]}

    # Test the method
    dynamodb_service.update_status('test-uuid', 'processing')

    # Verify the update call
    mock_dynamodb.update_item.assert_called_once()
    call_args = mock_dynamodb.update_item.call_args[1]
    assert call_args['Key'] == {'email': 'test@example.com', 'uuid': 'test-uuid'}
    assert '#s' in call_args['ExpressionAttributeNames']
    assert call_args['ExpressionAttributeNames']['#s'] == 'status' 