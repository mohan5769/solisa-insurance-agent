import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if we're in demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Initialize Twilio client
twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")

if not DEMO_MODE and twilio_account_sid and twilio_auth_token:
    twilio_client = Client(twilio_account_sid, twilio_auth_token)
else:
    twilio_client = None

# Initialize SendGrid client
sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
sendgrid_from_email = os.getenv("SENDGRID_FROM_EMAIL", "alex@solisa.com")

if not DEMO_MODE and sendgrid_api_key:
    sendgrid_client = SendGridAPIClient(sendgrid_api_key)
else:
    sendgrid_client = None


def send_sms(to_phone: str, message: str) -> dict:
    """
    Send an SMS message to the lead.
    
    Args:
        to_phone: Phone number to send to (E.164 format)
        message: SMS message content
    
    Returns:
        Dictionary with success status and message_id or error
    """
    # In demo mode, just print to console
    if DEMO_MODE:
        print(f"\n{'='*60}")
        print(f"📱 DEMO MODE - SMS would be sent to: {to_phone}")
        print(f"{'='*60}")
        print(f"Message: {message}")
        print(f"{'='*60}\n")
        return {
            "success": True,
            "message_id": f"demo_sms_{to_phone}",
            "status": "demo"
        }
    
    # Send actual SMS via Twilio
    try:
        if not twilio_client:
            raise Exception("Twilio client not initialized. Check your credentials.")
        
        message_obj = twilio_client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=to_phone
        )
        
        print(f"✅ SMS sent successfully to {to_phone}")
        return {
            "success": True,
            "message_id": message_obj.sid,
            "status": message_obj.status
        }
    
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def send_email(to_email: str, subject: str, body: str) -> dict:
    """
    Send an email to the lead.
    
    Args:
        to_email: Email address to send to
        subject: Email subject line
        body: Email body content (plain text)
    
    Returns:
        Dictionary with success status and message_id or error
    """
    # In demo mode, just print to console
    if DEMO_MODE:
        print(f"\n{'='*60}")
        print(f"📧 DEMO MODE - Email would be sent to: {to_email}")
        print(f"{'='*60}")
        print(f"Subject: {subject}")
        print(f"{'='*60}")
        print(f"Body:\n{body}")
        print(f"{'='*60}\n")
        return {
            "success": True,
            "message_id": f"demo_email_{to_email}",
            "status": "demo"
        }
    
    # Send actual email via SendGrid
    try:
        if not sendgrid_client:
            raise Exception("SendGrid client not initialized. Check your API key.")
        
        # Convert plain text to HTML (replace newlines with <br>)
        html_body = body.replace("\n", "<br>")
        
        message = Mail(
            from_email=sendgrid_from_email,
            to_emails=to_email,
            subject=subject,
            html_content=f"<html><body><pre style='font-family: Arial, sans-serif; white-space: pre-wrap;'>{html_body}</pre></body></html>"
        )
        
        response = sendgrid_client.send(message)
        
        print(f"✅ Email sent successfully to {to_email}")
        return {
            "success": True,
            "message_id": response.headers.get("X-Message-Id", "unknown"),
            "status_code": response.status_code
        }
    
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return {
            "success": False,
            "error": str(e)
        }
