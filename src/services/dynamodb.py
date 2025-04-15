import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone

class DynamodbService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table("uploads")

    def create_upload(self, email: str, uuid: str, filename: str, token: str):
        self.table.put_item(
            Item={
                "email": email,
                "uuid": uuid,
                "filename": filename,
                "status": "created",
                "confirmed": False,
                "secure_token": token,
                "conversation": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        )

    def get_by_email(self, email: str):
        response = self.table.query(
            KeyConditionExpression=Key("email").eq(email)
        )
        return response.get("Items", [])

    def get_by_uuid(self, uuid: str):
        response = self.table.query(
            IndexName="uuid-index",
            KeyConditionExpression=Key("uuid").eq(uuid)
        )
        items = response.get("Items", [])
        return items[0] if items else None
    
    def get_by_token(self, token: str):
        response = self.table.query(
            IndexName="token-index",
            KeyConditionExpression=Key("secure_token").eq(token)
        )
        items = response.get("Items", [])
        return items[0] if items else None


    def append_message(self, uuid: str, message: dict):
        item = self.get_by_uuid(uuid)
        if not item:
            raise Exception(f"No upload found with uuid {uuid}")

        conversation = item.get("conversation", [])
        conversation.append(message)

        self.table.update_item(
            Key={
                "email": item["email"],
                "uuid": uuid
            },
            UpdateExpression="SET conversation = :c, updated_at = :t",
            ExpressionAttributeValues={
                ":c": conversation,
                ":t": datetime.now(timezone.utc).isoformat()
            }
        )

    def update_status(self, uuid: str, status: str):
        item = self.get_by_uuid(uuid)
        if not item:
            raise Exception(f"No upload found with uuid {uuid}")

        self.table.update_item(
            Key={
                "email": item["email"],
                "uuid": uuid
            },
            UpdateExpression="SET #s = :s, updated_at = :t",
            ExpressionAttributeNames={
                "#s": "status"
            },
            ExpressionAttributeValues={
                ":s": status,
                ":t": datetime.now(timezone.utc).isoformat()
            }
        )
