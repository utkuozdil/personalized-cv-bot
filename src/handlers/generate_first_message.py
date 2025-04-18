from datetime import datetime, timezone
import json
import traceback
from src.constants.status import STATUS_FIRST_MESSAGE_GENERATED
from src.utility.prompt_util import get_first_message_prompt
from src.integrations.openai import OpenAIIntegration
from src.services.dynamodb import DynamodbService
from src.utility.decimal_util import clean_decimals

dynamodb = DynamodbService()
openai = OpenAIIntegration()

def handler(event, context):
    for record in event["Records"]:
        try:
            message = json.loads(record["Sns"]["Message"])

            # 👇 Fix: unpack the actual payload from inside "uuid"
            payload = message["uuid"]
            uuid = payload["uuid"]

            summary = payload.get("summary", "")
            score_feedback = payload.get("score_feedback", {})

            prompt = get_first_message_prompt(
                summary=summary,
                score=score_feedback.get("overall_score"),
                category_scores=score_feedback.get("category_scores", {}),
                feedback=score_feedback.get("feedback", {})
            )

            first_msg = openai.stream_to_string(prompt)

            dynamodb.append_message(uuid, {
                "role": "assistant",
                "content": first_msg,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, status=STATUS_FIRST_MESSAGE_GENERATED)

            print(f"[✅] First message generated for {uuid}")

        except Exception as e:
            print(f"[❌] Error generating first message: {e}")
            print(traceback.format_exc())
