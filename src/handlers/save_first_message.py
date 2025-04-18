import json
import traceback
from src.services.dynamodb import DynamodbService

dynamodb = DynamodbService()

def handler(event, context):
    for record in event["Records"]:
        try:
            payload = json.loads(record["Sns"]["Message"])
            
            uuid = payload["uuid"]
            message = payload["message"]
            status = payload["status"]
            
            # Save the message to DynamoDB
            dynamodb.append_message(uuid, message, status=status)
            
            print(f"[✅] Message saved to DynamoDB for {uuid}")
        
        except Exception as e:
            print(f"[❌] Error saving message to DynamoDB: {e}")
            print(traceback.format_exc()) 