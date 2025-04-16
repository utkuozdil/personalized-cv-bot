import json
import re
import traceback
from datetime import datetime, timezone

from src.services.dynamodb import DynamodbService
from src.services.api_gateway import ApiGatewayService
from src.integrations.openai import OpenAIIntegration
from src.services.s3 import S3Service
from src.utility.embed_utils import find_top_chunks, combine_chunks, rerank_chunks
from src.utility.prompt_util import get_resume_prompt

s3 = S3Service()
dynamodb = DynamodbService()
api_gateway = ApiGatewayService()
openai_integration = OpenAIIntegration()

cached_embeddings = {}
name_cache = {}
text_cache = {}
chat_cache = {}  # 🧠 per-connection chat history


def handler(event, context):
    connection_id = event['requestContext']['connectionId']
    domain = event['requestContext']['domainName']
    stage = event['requestContext']['stage']

    try:
        body = json.loads(event.get("body", "{}"))
        question = body.get("question", "").strip()
        embedding_key = body.get("embeddingKey")
        uuid_str = embedding_key.split("/")[-1].replace(".json", "")

        if not question or not embedding_key:
            raise ValueError("Missing question or embeddingKey")

        # 👋 Early typing signal
        api_gateway.send_response(domain, stage, connection_id, {
            "type": "typing",
            "message": "Finding the most relevant information..."
        })

        # Append user message to chat cache and DynamoDB
        user_msg = {
            "role": "user",
            "content": question,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        chat_cache.setdefault(connection_id, []).append(user_msg)
        dynamodb.append_message(uuid_str, user_msg)

        # Load embeddings
        if embedding_key not in cached_embeddings:
            embedding_json = s3.get_file_content(embedding_key)
            cached_embeddings[embedding_key] = json.loads(embedding_json)
        embeddings = cached_embeddings[embedding_key]

        # Load full resume text
        if embedding_key in text_cache:
            full_text = text_cache[embedding_key]
        else:
            extracted_key = get_extracted_key_from_embedding_key(embedding_key)
            full_text = s3.get_file_content(extracted_key)
            text_cache[embedding_key] = full_text

        # Load name from DynamoDB
        if embedding_key in name_cache:
            name = name_cache[embedding_key]
        else:
            item = dynamodb.get_by_uuid(uuid_str)
            if not item:
                raise Exception(f"Missing status entry for UUID {uuid_str}")
            name = item.get("name", "This person")
            name_cache[embedding_key] = name

        # RAG retrieval
        top_chunks = rerank_chunks(
            openai_integration,
            question,
            [chunk for chunk in find_top_chunks(openai_integration, question, embeddings, 10, 0.4) if len(chunk) == 3]
        )
        similarity = top_chunks[0][0] if top_chunks else 0.0
        context_text = combine_chunks(top_chunks) if similarity >= 0.4 else full_text

        # Build message thread for LLM
        message_history = get_resume_prompt(
            prompt=question,
            history=chat_cache[connection_id],
            context=context_text
        )

        # 🔄 Stream and cache assistant reply
        _, finish_reason = stream_response(message_history, connection_id, domain, stage, uuid_str)

        api_gateway.send_response(domain, stage, connection_id, {
            "type": "stream_end",
            "similarity": similarity,
            "finish_reason": finish_reason or "unknown"
        })

    except Exception as e:
        print(traceback.format_exc())
        api_gateway.send_response(domain, stage, connection_id, {
            "type": "error",
            "message": str(e),
        })

    return {"statusCode": 200}


def get_extracted_key_from_embedding_key(embedding_key: str) -> str:
    return embedding_key.replace("embeddings/", "extracted/").replace(".json", ".txt")


def stream_response(messages: list, connection_id: str, domain: str, stage: str, uuid_str: str) -> tuple:
    tokens_sent = 0
    finish_reason = None
    buffer = ""
    full_response = ""
    buffer_size = 300

    for token, reason in openai_integration.chat(messages):
        if token:
            buffer += token
            full_response += token
            tokens_sent += 1

            if len(buffer) >= buffer_size or buffer.endswith(('.', '!', '?', '\n')):
                api_gateway.send_response(domain, stage, connection_id, {
                    "type": "stream",
                    "token": fix_punctuation_spacing(buffer)
                })
                buffer = ""

        if reason:
            finish_reason = reason

    if buffer.strip():
        api_gateway.send_response(domain, stage, connection_id, {
            "type": "stream",
            "token": fix_punctuation_spacing(buffer.strip())
        })

    if tokens_sent == 0:
        api_gateway.send_response(domain, stage, connection_id, {
            "type": "stream",
            "token": "🤔 Sorry, I couldn't find a good answer based on this resume."
        })

    if tokens_sent > 0:
        assistant_msg = {
            "role": "assistant",
            "content": fix_punctuation_spacing(full_response),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        chat_cache.setdefault(connection_id, []).append({
            "role": "assistant",
            "content": assistant_msg["content"]
        })

        dynamodb.append_message(uuid_str, assistant_msg)

    return tokens_sent, finish_reason


def fix_punctuation_spacing(text: str) -> str:
    return re.sub(r'([.!?])(?=\w)', r'\1 ', text)
