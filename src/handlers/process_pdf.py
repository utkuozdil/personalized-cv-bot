import json
import os
import traceback
import uuid
import secrets
from datetime import datetime, timezone

from src.constants.status import STATUS_CREATED
from src.services.ses import EmailService
from src.services.s3 import S3Service
from src.utility.status_util import write_status
from src.utility.response_util import response

s3 = S3Service()
email_service = EmailService()

def handler(event, context):
    try:
        # ✅ Parse the request body
        body = json.loads(event.get("body", "{}"))
        filename_from_client = body.get("filename", "resume.pdf")
        email = body.get("email", "").strip()

        if not email:
            raise ValueError("Email is required")

        # ✅ Generate UUID + use original filename extension if needed
        uuid_str = str(uuid.uuid4())
        s3_key = f"uploads/{uuid_str}"

        token = secrets.token_hex(16)
        write_status(uuid=uuid_str, status=STATUS_CREATED, 
                     extra={"token": token, "email": email, "filename": filename_from_client, "conversation": [], "created_at": datetime.now(timezone.utc).isoformat()
                            })

        # ✅ Generate presigned S3 URL
        presigned_url = s3.get_presigned_upload_url(key=s3_key)
        if not presigned_url:
            raise Exception("Could not generate presigned URL")
        
        email_service.send_confirmation_email(
            email=email,
            filename=filename_from_client,
            token=token,
            base_url=os.getenv("API_GATEWAY", "")  # this will be used in the confirmation link
        )
        
        return response(status_code=200, body={
                "upload_url": presigned_url,
                "uuid": uuid_str,
                "message": "Upload your file using this URL via HTTP PUT"
            })

    except Exception as e:
        traceback.print_exc()
        return response(status_code=500, body={"error": str(e)})
