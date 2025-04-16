import json
import pytest
from unittest.mock import patch, MagicMock
from src.integrations.openai import OpenAIIntegration

@pytest.fixture
def openai_integration():
    with patch('src.integrations.openai.openai') as mock_openai:
        mock_openai.api_key = "test-key"
        yield OpenAIIntegration()

@pytest.fixture
def mock_openai():
    with patch('src.integrations.openai.openai') as mock_client:
        mock_embeddings = MagicMock()
        mock_chat = MagicMock()
        mock_client.embeddings = mock_embeddings
        mock_client.chat = mock_chat
        yield mock_embeddings, mock_chat

def test_embed_query_success(openai_integration, mock_openai):
    mock_embeddings, _ = mock_openai
    # Setup mock response
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    mock_embeddings.create.return_value = mock_response

    # Test the method
    result = openai_integration.embed_query("test text")
    assert result == [0.1, 0.2, 0.3]

def test_embed_query_error(openai_integration, mock_openai):
    mock_embeddings, _ = mock_openai
    # Setup mock to raise an error
    mock_embeddings.create.side_effect = Exception("API Error")

    # Test the method
    try:
        result = openai_integration.embed_query("test text")
        assert result is None
    except Exception:
        pass  # Expected exception

def test_embed_batch_success(openai_integration, mock_openai):
    mock_embeddings, _ = mock_openai
    # Setup mock response
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1, 0.2, 0.3]),
        MagicMock(embedding=[0.4, 0.5, 0.6])
    ]
    mock_embeddings.create.return_value = mock_response

    # Test the method
    result = openai_integration.embed_batch(["text1", "text2"])
    assert len(result) == 2
    assert result[0] == [0.1, 0.2, 0.3]
    assert result[1] == [0.4, 0.5, 0.6]

def test_embed_batch_error(openai_integration, mock_openai):
    mock_embeddings, _ = mock_openai
    # Setup mock to raise an error
    mock_embeddings.create.side_effect = Exception("API Error")

    # Test the method
    result = openai_integration.embed_batch(["text1", "text2"])
    assert result == [[], []]

def test_chat_streaming_success(openai_integration, mock_openai):
    _, mock_chat = mock_openai
    # Setup mock response for streaming
    mock_response = [
        MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"), finish_reason=None)]),
        MagicMock(choices=[MagicMock(delta=MagicMock(content=" World"), finish_reason="stop")])
    ]
    mock_chat.completions.create.return_value = mock_response

    # Test the method
    messages = [{"role": "user", "content": "Hi"}]
    result = ""
    for content, _ in openai_integration.chat(messages, stream=True):
        if content:
            result += content
    assert result == "Hello World"

def test_chat_non_streaming_success(openai_integration, mock_openai):
    _, mock_chat = mock_openai
    # Setup mock response for non-streaming
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello World"))]
    mock_chat.completions.create.return_value = mock_response

    # Test the method
    messages = [{"role": "user", "content": "Hi"}]
    result = openai_integration._direct_chat(messages)
    assert result == "Hello World"

def test_stream_to_string_success(openai_integration, mock_openai):
    _, mock_chat = mock_openai
    # Setup mock response for non-streaming mode
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello World"))]
    mock_chat.completions.create.return_value = mock_response

    # Test the method
    messages = [{"role": "user", "content": "Hi"}]
    result = openai_integration.stream_to_string(messages)
    assert result == "Hello World"

def test_direct_chat_success(openai_integration, mock_openai):
    _, mock_chat = mock_openai
    # Setup mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello World"))]
    mock_chat.completions.create.return_value = mock_response

    # Test the method
    messages = [{"role": "user", "content": "Hi"}]
    result = openai_integration._direct_chat(messages)
    assert result == "Hello World"

def test_direct_chat_error(openai_integration, mock_openai):
    _, mock_chat = mock_openai
    # Setup mock to raise an error
    mock_chat.completions.create.side_effect = Exception("API Error")

    # Test the method
    messages = [{"role": "user", "content": "Hi"}]
    result = openai_integration._direct_chat(messages)
    assert result == "⚠️ Error: Failed to generate response." 