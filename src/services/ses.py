import boto3
import os

from src.utility.email_format_util import get_mail_template

class EmailService:
    def __init__(self, region="us-east-1"):
        self.client = boto3.client("ses", region_name=region)
        self.sender = os.getenv("NOTIFY_FROM_EMAIL", "utkuozdil@gmail.com")
        self.recipient = os.getenv("NOTIFY_TO_EMAIL", "utkuozdil1@gmail.com")

    def send_confirmation_email(self, email, filename, token, base_url):
        confirm_link = f"{base_url}/confirm?token={token}"

        subject = "📄 New Resume Uploaded — Confirmation Required"
        body_text = (
            f"A new resume has been uploaded.\n\n"
            f"Email: {email}\n"
            f"Filename: {filename}\n"
            f"Click below to confirm:\n{confirm_link}"
        )
        
        body_html = get_mail_template(email, filename, confirm_link)
        
        return self.client.send_email(
            Source=self.sender,
            Destination={"ToAddresses": [self.recipient]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            }
        )
