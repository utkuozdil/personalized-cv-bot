from datetime import datetime, timezone
from src.services.dynamodb import DynamodbService

dynamodb = DynamodbService()

def write_status(uuid: str, status: str, extra: dict = None):
    """Creates a new status record in DynamoDB if not already exists."""
    item = dynamodb.get_by_uuid(uuid)
    if item:
        return

    if not extra or "email" not in extra or "filename" not in extra:
        raise ValueError("Missing 'email' or 'filename' in extra data")

    dynamodb.create_upload(
        email=extra["email"],
        uuid=uuid,
        filename=extra["filename"],
        token=extra["token"]
    )

def update_status(uuid: str, status: str, extra: dict = None):
    """Updates the upload status and optionally appends conversation/messages."""
    item = dynamodb.get_by_uuid(uuid)
    if not item:
        raise Exception(f"No status found for uuid {uuid}")

    update_fields = {}
    if extra:
        # Update conversation (append messages if provided)
        if "conversation" in extra and isinstance(extra["conversation"], list):
            current_convo = item.get("conversation", [])
            current_convo.extend(extra["conversation"])
            update_fields["conversation"] = current_convo

        # Update other metadata if needed
        for key, value in extra.items():
            if key != "conversation":
                update_fields[key] = value

    update_fields["status"] = status
    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()

    dynamodb.table.update_item(
        Key={
            "email": item["email"],
            "uuid": uuid
        },
        UpdateExpression="SET " + ", ".join(f"#{k} = :{k}" for k in update_fields.keys()),
        ExpressionAttributeNames={f"#{k}": k for k in update_fields.keys()},
        ExpressionAttributeValues={f":{k}": v for k, v in update_fields.items()}
    )