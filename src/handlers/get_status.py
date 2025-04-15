from src.services.dynamodb import DynamodbService
from src.utility.response_util import response
from decimal import Decimal

dynamodb = DynamodbService()

def convert_decimal_to_float(obj):
    if isinstance(obj, list):
        return [convert_decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

def handler(event, context):
    uuid = event["pathParameters"].get("uuid")
    if not uuid:
        return response(400, {"error": "Missing UUID in path"})

    try:
        item = dynamodb.get_by_uuid(uuid)
        if item:
            return response(200, convert_decimal_to_float(item))
        else:
            return response(404, {"status": "not_found", "message": f"Status for UUID {uuid} not found"})
    except Exception as e:
        return response(500, {"status": "error", "message": str(e)})
