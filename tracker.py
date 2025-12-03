import boto3
import os
from dotenv import load_dotenv
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = "ap-south-1"

ses = boto3.client(
    "ses",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

table = dynamodb.Table("email_events")

def send_mail_and_record(to_email, subject, body, from_email):
    r = ses.send_email(
        Source=from_email,
        Destination={"ToAddresses": [to_email]},
        Message={"Subject": {"Data": subject}, "Body": {"Html": {"Data": body}}},
        ConfigurationSetName="email-marketing"
    )
    msg_id = r["MessageId"]
    table.put_item(
        Item={
            "message_id": msg_id,
            "email": to_email,
            "sent": 1,
            "delivered": 0,
            "opened": 0,
            "clicked": 0,
            "bounce": "none",
            "complaint": 0
        }
    )
    return msg_id

def get_all_events():
    return table.scan().get("Items", [])
