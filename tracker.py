import boto3
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes

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

def send_mail_with_attachments_and_record(to_email, subject, body, from_email, attachments=None):
    """
    Send email with optional attachments.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: HTML body of the email
        from_email: Sender email address (must be verified in SES)
        attachments: List of file paths to attach (supports images, videos, docs)
                     Example: ['path/to/image.png', 'path/to/document.pdf']
    
    Returns:
        message_id: The SES message ID
    """
    # Create a multipart message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    
    # Attach the HTML body
    msg.attach(MIMEText(body, 'html'))
    
    # Attach files if provided
    if attachments:
        for file_path in attachments:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue
            
            # Guess the content type
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            main_type, sub_type = content_type.split('/', 1)
            
            # Read and attach the file
            with open(file_path, 'rb') as f:
                attachment = MIMEBase(main_type, sub_type)
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                
                # Add header with filename
                filename = os.path.basename(file_path)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{filename}"'
                )
                msg.attach(attachment)
    
    # Send the raw email
    r = ses.send_raw_email(
        Source=from_email,
        Destinations=[to_email],
        RawMessage={'Data': msg.as_string()},
        ConfigurationSetName="email-marketing"
    )
    
    msg_id = r["MessageId"]
    
    # Record in DynamoDB
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
