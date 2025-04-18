import json
import time
from concurrent.futures import ThreadPoolExecutor
import traceback

from src.constants.status import STATUS_EMBEDDED
from src.services.sns import SnsService
from src.integrations.openai import OpenAIIntegration
from src.services.s3 import S3Service
from src.utility.text_divider import chunk_text
from src.utility.status_util import update_status
from src.utility.prompt_util import (
    get_score_and_feedback_prompt,
    get_summary_prompt
)
from src.utility.decimal_util import clean_decimals

s3_service = S3Service()
openai_integration = OpenAIIntegration()
sns_service = SnsService()

def handler(event, context):
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]
    
    file_name = key.split("/")[-1]
    uuid = file_name.rsplit(".", 1)[0]

    print(f"[🚀] Start embedding and metadata prep for: {key}")
    s3_service.bucket_name = bucket

    start_time = time.time()
    text = s3_service.get_file_content(key)
    if not text:
        raise Exception(f"Failed to load text from {key}")

    # 🚀 Run LLM calls in parallel
    summary, score_response = "", ""
    with ThreadPoolExecutor() as executor:
        summary_messages = get_summary_prompt(text)
        score_messages = get_score_and_feedback_prompt(text)

        summary_future = executor.submit(openai_integration.stream_to_string, summary_messages)
        score_future = executor.submit(openai_integration.stream_to_string, score_messages)

        try:
            summary = summary_future.result()
        except Exception:
            print("[❌] Error in summary generation:")
            print(traceback.format_exc())
            summary = "Summary generation failed."

        try:
            score_response = score_future.result()
        except Exception:
            print("[❌] Error in score/feedback generation:")
            print(traceback.format_exc())
            score_response = ""

    try:
        score_feedback = json.loads(score_response)
    except Exception:
        print(traceback.format_exc())
        score_feedback = {"error": "Failed to parse score feedback"}
    
    mid_time = time.time()
    payload = {
        "uuid": uuid,
        "name": score_feedback.get("name", "This person"),
        "summary": summary.strip(),
        "score_feedback": clean_decimals(score_feedback, to_decimal=False)
    }
    
    sns_service.publish(payload)
    
    update_status(
        uuid,
        STATUS_EMBEDDED,
        extra={
            "name": score_feedback.get("name", "This person"),
            "summary": summary.strip(),
            "score_feedback": clean_decimals(score_feedback)
        }
    )
    print(f"[✅] Status updated after {mid_time - start_time:.2f}s")
        
    # 🧠 Generate embeddings in the background
    embeddings = generate_embeddings(text)
    output_key = key.replace("extracted/", "embeddings/").replace(".txt", ".json")
    s3_service.upload_file(
        key=output_key,
        file_bytes=json.dumps(embeddings).encode("utf-8"),
        content_type="application/json"
    )

    end_time = time.time()
    print(f"[📦] Embeddings saved to {output_key} after {end_time - start_time:.2f}s")

    return {"status": "success", "chunks": len(embeddings)}

def generate_embeddings(text):
    chunks = chunk_text(text)
    vectors = openai_integration.embed_batch(chunks)
    return [
        {
            "chunk_index": i,
            "text": chunks[i],
            "embedding": vectors[i]
        }
        for i in range(len(chunks))
    ]
