#!/usr/bin/env python3
"""
Test SendGrid Email Integration
"""

import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load environment variables
load_dotenv('backend/.env')

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

def test_sendgrid():
    """Test sending an email via SendGrid"""
    
    print("🧪 Testing SendGrid Email Integration\n")
    print(f"API Key: {SENDGRID_API_KEY[:20]}..." if SENDGRID_API_KEY else "❌ No API Key")
    print(f"From Email: {SENDGRID_FROM_EMAIL}\n")
    
    if not SENDGRID_API_KEY:
        print("❌ ERROR: SENDGRID_API_KEY not found in .env file")
        return
    
    if not SENDGRID_FROM_EMAIL:
        print("❌ ERROR: SENDGRID_FROM_EMAIL not found in .env file")
        return
    
    # Create test email
    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails='ckinjal03@gmail.com',  # Recipient email
        subject='Solisa AI SDR - Test Email',
        html_content='''
        <html>
            <body>
                <h2>🎉 SendGrid Integration Working!</h2>
                <p>This is a test email from your Solisa AI SDR system.</p>
                <p><strong>If you're seeing this, SendGrid is configured correctly!</strong></p>
                <hr>
                <p style="color: #666;">Sent via SendGrid API</p>
            </body>
        </html>
        '''
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print("✅ Email sent successfully!")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
        
        if response.status_code == 202:
            print("\n🎉 SUCCESS! SendGrid accepted the email.")
            print("Check your inbox (might take a few seconds)")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        if "401" in str(e):
            print("\n💡 TIP: Your API key might be invalid. Check:")
            print("   1. API key is correct in .env file")
            print("   2. API key has 'Mail Send' permissions in SendGrid")
        elif "403" in str(e):
            print("\n💡 TIP: Your sender email might not be verified. Check:")
            print("   1. Go to https://app.sendgrid.com/settings/sender_auth")
            print("   2. Verify your sender email")

if __name__ == "__main__":
    test_sendgrid()
