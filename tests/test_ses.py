import pytest
import os
from botocore.exceptions import ClientError
import boto3
from dotenv import load_dotenv
load_dotenv()

@pytest.fixture(scope="module")
def ses_client():
    return boto3.client("ses", region_name="us-east-1")  # Adjust region if needed

def test_send_email_sandbox(ses_client):
    sender = os.getenv("SES_SANDBOX_SENDER")      # Must be verified in SES
    recipient = os.getenv("SES_SANDBOX_RECIPIENT")  # Must be verified in SES

    if not sender or not recipient:
        pytest.skip("Set SES_SANDBOX_SENDER and SES_SANDBOX_RECIPIENT in env.")

    subject = "📄 Sandbox Test Email"
    body_text = "This is a plain text email from SES sandbox test."
    body_html = "<html><body><h1>Sandbox Test</h1><p>This is a test email from SES.</p></body></html>"

    try:
        response = ses_client.send_email(
            Source=sender,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            }
        )

        status_code = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        message_id = response.get("MessageId")

        assert status_code == 200, f"SES returned HTTP {status_code}"
        assert message_id, "No MessageId returned"

        print(f"[✅] Email accepted by SES. MessageId: {message_id}")

    except ClientError as e:
        print(f"[❌] SES ClientError: {e}")
        pytest.fail("SES send_email failed")

