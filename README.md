# NextSteps USMLE Email Marketing Platform

This project is a comprehensive email marketing solution designed to send campaigns and track email deliverability metrics using AWS SES and DynamoDB. It consists of a user-friendly dashboard for managing campaigns and a webhook handler for processing real-time email events.

## Features

- **Email Campaign Management**: Send bulk emails via AWS SES with support for HTML bodies.
- **📎 File Attachments**: Attach images, videos, and documents (PDF, DOCX, etc.) to your emails.Max limit 5mb
- **Real-time Analytics**: Track delivery rates, open rates, click rates, bounces (permanent and transient), and complaints.
- **Interactive Dashboard**: Visualize email performance metrics through a Streamlit interface.
- **Automated Event Handling**: Process SES notifications (deliveries, bounces, complaints) via a FastAPI webhook.

## Components

### 1. Dashboard (dashboard.py)
A Streamlit-based web interface that allows users to:
- Upload CSV files containing recipient email addresses.
- Compose and send email campaigns.
- View detailed analytics and metrics on email performance.
- Refresh data to see the latest event statuses.

### 2. Tracker (tracker.py)
Contains the core logic for:
- Initializing AWS SES and DynamoDB clients.
- Sending emails using AWS SES.
- logging the initial "sent" status of each email into a DynamoDB table named `email_events`.

### 3. Webhook Handler (webhook/fastapiwebhook.py)
A FastAPI application that acts as an endpoint for AWS SNS notifications linked to SES. It handles:
- **Subscription Confirmation**: Automatically confirms SNS topic subscriptions.
- **Event Processing**: Updates the `email_events` DynamoDB table based on event types:
    - **Delivery**: Marks email as delivered.
    - **Open**: Increments open count.
    - **Click**: Increments click count.
    - **Complaint**: Records spam complaints.
    - **Bounce**: Records bounce types (permanent or transient).

## Prerequisites

- Python 3.8+
- AWS Account with SES and DynamoDB access.
- AWS Credentials configured locally or via environment variables.

### AWS Configuration
1. **SES**: Verify your "From Email" address in AWS SES. Set up a Configuration Set named `email-marketing` to publish events to an SNS topic.
2. **DynamoDB**: Create a table named `email_events` with `message_id` as the Primary Key (String).
3. **SNS**: Configure your SNS topic to send HTTP/HTTPS POST notifications to your deployed webhook URL (e.g., `https://your-domain.com/ses/webhook`).

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd email-marketing
   ```

2. Install dependencies:
   ```bash
   pip install streamlit pandas boto3 python-dotenv fastapi uvicorn requests
   ```

3. Create a `.env` file in the root directory with your AWS credentials:
   ```env
   AWS_ACCESS_KEY=your_access_key
   AWS_SECRET_KEY=your_secret_key
   ADMIN_PASSWORD=your_admin_password
   ```

## Usage

### Running the Dashboard
To start the campaign manager and analytics dashboard:

```bash
streamlit run dashboard.py
```
Access the dashboard in your browser at `http://localhost:8501`.

### Running the Webhook
To start the webhook server locally (for testing or development):

```bash
uvicorn webhook.fastapiwebhook:app --reload
```
The webhook will be available at `http://localhost:8000/ses/webhook`.

**Note**: For production, deploy the FastAPI app to a public-facing server (e.g., AWS Lambda, EC2, or a platform like Heroku/Vercel) so AWS SNS can reach it.

## Project Structure

- `dashboard.py`: Main application interface.
- `tracker.py`: AWS integration and email sending logic.
- `webhook/fastapiwebhook.py`: Endpoint for processing SES event notifications.
- `.env`: Configuration file for environment variables.
