from src.services.dynamodb import DynamodbService
from src.utility.response_util import response
from src.utility.decimal_util import clean_decimals

dynamodb = DynamodbService()



def handler(event, context):
    uuid = event["pathParameters"].get("uuid")
    if not uuid:
        return response(400, {"error": "Missing UUID in path"})

    try:
        item = dynamodb.get_by_uuid(uuid)
        if item:
            return response(200, clean_decimals(item, to_decimal=False))
        else:
            return response(404, {"status": "not_found", "message": f"Status for UUID {uuid} not found"})
    except Exception as e:
        return response(500, {"status": "error", "message": str(e)})
