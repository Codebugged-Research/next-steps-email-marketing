from fastapi import FastAPI, Request
import boto3
import json
import requests

app = FastAPI()

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table("email_events")

@app.post("/ses/webhook")
async def ses_webhook(request: Request):
    data = await request.json()

    # Step 1: Confirm SNS subscription
    if data.get("Type") == "SubscriptionConfirmation":
        subscribe_url = data["SubscribeURL"]
        requests.get(subscribe_url)
        return {"status": "SNS subscription confirmed"}

    # Step 2: Extract SES event from SNS message
    message = json.loads(data["Message"])
    event_type = message.get("eventType", "").lower()
    mail = message.get("mail", {})
    msg_id = mail.get("messageId")

    if not msg_id:
        return {"status": "no messageId found"}

    # Create item if not exists
    table.update_item(
        Key={"message_id": msg_id},
        UpdateExpression="SET sent = if_not_exists(sent, :zero)",
        ExpressionAttributeValues={":zero": 1}
    )

    # Handle each event type
    if event_type == "delivery":
        table.update_item(
            Key={"message_id": msg_id},
            UpdateExpression="SET delivered = :v",
            ExpressionAttributeValues={":v": 1}
        )

    elif event_type == "open":
        table.update_item(
            Key={"message_id": msg_id},
            UpdateExpression="SET opened = if_not_exists(opened, :zero) + :one",
            ExpressionAttributeValues={":one": 1, ":zero": 0}
        )

    elif event_type == "click":
        table.update_item(
            Key={"message_id": msg_id},
            UpdateExpression="SET clicked = if_not_exists(clicked, :zero) + :one",
            ExpressionAttributeValues={":one": 1, ":zero": 0}
        )

    elif event_type == "complaint":
        table.update_item(
            Key={"message_id": msg_id},
            UpdateExpression="SET complaint = :v",
            ExpressionAttributeValues={":v": 1}
        )

    elif event_type == "bounce":
        bounce_type = message.get("bounce", {}).get("bounceType", "unknown")
        table.update_item(
            Key={"message_id": msg_id},
            UpdateExpression="SET bounce = :b",
            ExpressionAttributeValues={":b": bounce_type}
        )

    return {"status": "ok"}
