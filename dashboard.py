import streamlit as st
import pandas as pd
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

st.set_page_config(page_title="NextSteps USMLE Email Marketing", layout="centered")
st.title("NextSteps USMLE Email Marketing")

subject = st.text_input("Subject")
from_email = st.text_input("From Email (verified in SES)")
body = st.text_area("Email Body (HTML allowed)", height=250)

file = st.file_uploader("Upload CSV with 'email' column", type=["csv"])

def send_mail(to_email):
    return ses.send_email(
        Source=from_email,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Html": {"Data": body}}
        },
        ConfigurationSetName="email-marketing"
    )

if file:
    df = pd.read_csv(file)

    if st.button("Send Emails"):
        results = []
        for idx, row in df.iterrows():
            r = send_mail(row["email"])
            results.append({"email": row["email"], "message_id": r["MessageId"]})
        st.success("Emails Sent Successfully")
