import json
import time
import traceback
from datetime import datetime, timezone

from src.constants.status import STATUS_EMBEDDED
from src.services.dynamodb import DynamodbService
from src.services.s3 import S3Service
from src.integrations.openai import OpenAIIntegration
from src.utility.text_divider import chunk_text
from src.utility.prompt_util import get_combined_first_message_prompt
from src.utility.decimal_util import clean_decimals
from src.utility.status_util import update_status

dynamodb = DynamodbService()
s3_service = S3Service()
openai = OpenAIIntegration()

def handler(event, context):
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    file_name = key.split("/")[-1]
    uuid = file_name.rsplit(".", 1)[0]

    print(f"[📄] Processing resume: {key}")
    s3_service.bucket_name = bucket
    text = s3_service.get_file_content(key)

    if not text:
        raise Exception(f"❌ Failed to load resume text from {key}")

    # 🧠 Run one LLM call to get full response
    try:
        prompt = get_combined_first_message_prompt(text)
        first_message = openai.stream_to_string(prompt)
    except Exception:
        print("[❌] Error during OpenAI completion:")
        print(traceback.format_exc())
        first_message = "Sorry, we couldn't generate feedback right now."

    # 💾 Save message to DB
    dynamodb.append_message(uuid, {
        "role": "assistant",
        "content": first_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, status=STATUS_EMBEDDED)

    print(f"[✅] Chatbot message saved for {uuid}")

    # ✨ Optionally generate embeddings here
    embeddings = generate_embeddings(text)
    output_key = key.replace("extracted/", "embeddings/").replace(".txt", ".json")
    s3_service.upload_file(
        key=output_key,
        file_bytes=json.dumps(embeddings).encode("utf-8"),
        content_type="application/json"
    )
    print(f"[📦] Embeddings saved to {output_key}")

    return {"status": "success"}

def generate_embeddings(text):
    chunks = chunk_text(text)
    vectors = openai.embed_batch(chunks)
    return [
        {
            "chunk_index": i,
            "text": chunks[i],
            "embedding": vectors[i]
        }
        for i in range(len(chunks))
    ]
