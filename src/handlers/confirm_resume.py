from datetime import datetime
from src.utility.response_util import response
from src.services.dynamodb import DynamodbService
from src.utility.email_format_util import get_confirm_response
from src.utility.extract_util import extract_and_upload

dynamodb = DynamodbService()

def handler(event, context):
    token = (event.get("queryStringParameters") or {}).get("token")

    if not token:
        return response(400, {"error": "Missing token"})

    try:
        item = dynamodb.get_by_token(token)
        if not item:
            return response(404, {"error": "Invalid or expired token"})

        dynamodb.table.update_item(
            Key={"email": item["email"], "uuid": item["uuid"]},
            UpdateExpression="SET confirmed = :c",
            ExpressionAttributeValues={":c": True}
        )

        s3_key = f"uploads/{item['uuid']}"
        extracted_key = extract_and_upload(item["uuid"], s3_key)

        print(f"[✅] Confirmed and extracted resume for {item['uuid']}: {extracted_key}")
        return get_confirm_response(item)

    except Exception as e:
        return response(500, {"error": f"Error confirming resume: {str(e)}"})

