import json
from typing import List, Tuple
import numpy as np

from src.utility.prompt_util import get_rerank_prompt


def find_top_chunks(
    openai_integration,
    query: str,
    embeddings: List[dict],
    top_n: int = 3,
    min_similarity: float = 0.0,
    with_metadata: bool = True
) -> List[Tuple[float, str]]:
    query_vec = openai_integration.embed_query(query)
    scored = []

    for i, chunk in enumerate(embeddings):
        vec = chunk.get("embedding")
        text = chunk.get("text", "")
        if not vec:
            continue
        score = cosine_similarity(query_vec, vec)
        if score >= min_similarity:
            if with_metadata:
                scored.append((score, text, i))
            else:
                scored.append((score, text))

    scored.sort(reverse=True, key=lambda x: x[0])
    return scored[:top_n] if scored else [(0.0, "[No relevant resume content found]")]


def combine_chunks(chunks: List[Tuple[float, str]], separator: str = "\n\n---\n\n") -> str:
    return separator.join([chunk[1] for chunk in chunks])


def cosine_similarity(vec1, vec2) -> float:
    vec1, vec2 = np.array(vec1), np.array(vec2)
    norm1, norm2 = np.linalg.norm(vec1), np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(vec1, vec2) / (norm1 * norm2)


def rerank_chunks(openai_integration, question, top_chunks):
    # Pre-process the text chunks to replace newlines with spaces
    processed_chunks = []
    for i, (_, text, _) in enumerate(top_chunks):
        processed_text = text[:300].replace('\n', ' ')
        processed_chunks.append(f"[{i}] {processed_text}...")
    
    context = "\n\n".join(processed_chunks)

    messages = get_rerank_prompt(question, context)

    output = ""
    for token, _ in openai_integration.chat(messages, model="gpt-3.5-turbo"):
        output += token

    try:
        data = json.loads(output.strip())
        return [top_chunks[i] for i in data.get("chunks", [])]
    except Exception as e:
        print("Rerank parsing error:", e)
        return top_chunks[:3]  # fallback
