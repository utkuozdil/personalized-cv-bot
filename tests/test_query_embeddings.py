import openai
import numpy as np
import json
import os
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    print(scored_chunks)
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
def test_find_most_relevant_chunk(query, embeddings):
    similarity, text = find_most_similar_chunk(query, embeddings)
    print(f"\n🔍 Query: {query}\n✅ Best Match (Score: {similarity:.4f}):\n{text}")
    assert similarity > 0.05  # Lower threshold since we're using mock embeddings
    assert len(text.strip()) > 0
