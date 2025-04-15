import boto3
import json
from botocore.exceptions import ClientError

class ApiGatewayService:
    def __init__(self):
        self.clients = {}

    def get_client(self, domain, stage):
        key = f"{domain}/{stage}"
        if key not in self.clients:
            self.clients[key] = boto3.client(
                "apigatewaymanagementapi",
                endpoint_url=f"https://{domain}/{stage}"
            )
        return self.clients[key]

    def send_response(self, domain, stage, connection_id, message: dict):
        try:
            client = self.get_client(domain, stage)
            client.post_to_connection(
                ConnectionId=connection_id,
                Data=json.dumps(message).encode("utf-8")
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'GoneException':
                print(f"⚠️ Connection {connection_id} is gone (disconnected).")
            else:
                print(f"❌ Failed to send message to {connection_id}: {e}")
