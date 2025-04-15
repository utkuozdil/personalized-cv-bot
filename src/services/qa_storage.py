import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("QA_Answers")

class QAStorageService:
    def store_answer(self, embedding_key: str, question: str, answer: str, embedding: list, similarity: float):
        item = {
            "embedding_key": embedding_key,
            "question": question,
            "answer": answer,
            "embedding": embedding,
            "similarity": similarity,
            "timestamp": datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)

    def get_answers_by_resume(self, embedding_key: str) -> list:
        response = table.query(
            KeyConditionExpression=Key('embedding_key').eq(embedding_key)
        )
        return response.get("Items", [])
