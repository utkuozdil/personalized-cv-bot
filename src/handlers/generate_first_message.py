from datetime import datetime, timezone
import json
import traceback
from src.utility.prompt_util import get_first_message_prompt
from src.integrations.openai import OpenAIIntegration
from src.services.dynamodb import DynamodbService
from src.utility.decimal_util import clean_decimals

dynamodb = DynamodbService()
openai = OpenAIIntegration()

def handler(event, context):
    for record in event["Records"]:
        try:
            payload = json.loads(record["Sns"]["Message"])
            uuid = payload["uuid"]

            item = dynamodb.get_by_uuid(uuid)
            if not item:
                print(f"[⚠️] UUID not found: {uuid}")
                continue
                
            # Convert Decimal values to float for JSON serialization
            item = clean_decimals(item, to_decimal=False)

            prompt = get_first_message_prompt(
                summary=item.get("summary", ""),
                score=item.get("score_feedback", {}).get("overall_score"),
                category_scores=item.get("score_feedback", {}).get("category_scores", {}),
                feedback=item.get("score_feedback", {}).get("feedback", {})
            )

            first_msg = openai.stream_to_string(prompt, stream=True)

            dynamodb.append_message(uuid, {
                "role": "assistant",
                "content": first_msg,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

            print(f"[✅] First message generated for {uuid}")

        except Exception as e:
            print(f"[❌] Error generating first message: {e}")
            print(traceback.format_exc())

