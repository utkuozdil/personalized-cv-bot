from src.services.dynamodb import DynamodbService
from src.utility.response_util import response
from decimal import Decimal

dynamodb = DynamodbService()

def clean_decimals(obj):
    if isinstance(obj, dict):
        return {k: clean_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_decimals(x) for x in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj

def handler(event, context):
    try:
        email = (event.get("queryStringParameters") or {}).get("email")
        if not email:
            return response(400, {"error": "Missing email"})

        uploads = dynamodb.get_by_email(email)
        confirmed = [u for u in uploads if u.get("confirmed")]

        resumes = [
            {
                "uuid": u["uuid"],
                "name": u.get("name"),
                "filename": u.get("filename"),
                "created_at": u.get("created_at"),
                "updated_at": u.get("updated_at"),
                "status": u.get("status"),
                "score_feedback": u.get("score_feedback", {}),
                "summary": u.get("summary"),
                "conversation": u.get("conversation", [])
            }
            for u in confirmed
        ]

        return response(200, {
            "hasPrevious": len(confirmed) > 0,
            "resumes": clean_decimals(resumes)
        })

    except Exception as e:
        return response(500, {"error": str(e)})
