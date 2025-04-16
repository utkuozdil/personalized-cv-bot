import openai
import numpy as np
import json
import os
import pytest
from unittest.mock import patch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock embedding response
MOCK_EMBEDDING = [0.1] * 1536  # OpenAI embeddings are 1536-dimensional

class MockEmbeddingResponse:
    class Data:
        def __init__(self, embedding):
            self.embedding = embedding

    def __init__(self, embedding):
        self.data = [self.Data(embedding)]

def mock_create(*args, **kwargs):
    return MockEmbeddingResponse(MOCK_EMBEDDING)

# --- Core Functions ---

def load_embeddings(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_query_embedding(query):
    response = openai.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    vec1, vec2 = np.array(vec1), np.array(vec2)
    # Ensure vectors have the same shape
    min_len = min(len(vec1), len(vec2))
    vec1 = vec1[:min_len]
    vec2 = vec2[:min_len]
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def find_most_similar_chunk(query, embeddings):
    query_vec = get_query_embedding(query)
    scored_chunks = []

    for chunk in embeddings["chunks"]:
        if not chunk.get("embedding"):
            continue
        similarity = cosine_similarity(query_vec, chunk["embedding"])
        scored_chunks.append((similarity, chunk["text"]))

    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    return scored_chunks[0] if scored_chunks else (0.0, "")

# --- Pytest Fixtures & Tests ---

@pytest.fixture
def embeddings():
    file_path = "test_embeddings.json"
    assert os.path.exists(file_path), f"{file_path} does not exist"
    return load_embeddings(file_path)

@pytest.mark.parametrize("query", [
    "What cloud platforms or tools has this person used?",
    "Which programming languages does this person know?",
    "Tell me about this person's experience with AWS.",
])
@patch('openai.embeddings.create', side_effect=mock_create)
def test_find_most_relevant_chunk(mock_embeddings, query, embeddings):
    similarity, text = find_most_similar_chunk(query, embeddings)
    assert similarity > 0.05  # Lower threshold since we're using mock embeddings
    assert len(text.strip()) > 0
    mock_embeddings.assert_called_once()
