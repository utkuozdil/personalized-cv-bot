import json
import boto3
import os

from src.utility.email_format_util import get_mail_template

class SnsService:
    def __init__(self):
        self.sns = boto3.client("sns")

    def publish(self, uuid):
        self.sns.publish(
            TopicArn=os.getenv("GENERATE_FIRST_MESSAGE_TOPIC"),
            Message=json.dumps({ "uuid": uuid })
        )
