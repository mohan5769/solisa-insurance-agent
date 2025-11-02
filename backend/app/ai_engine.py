import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Check if we're in demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
CALENDLY_LINK = os.getenv("CALENDLY_LINK", "https://calendly.com/solisa-demo/30min")


def generate_personalized_sms(lead_info: dict) -> str:
    """
    Generate a personalized SMS message for the lead.
    
    Args:
        lead_info: Dictionary with enriched lead information
    
    Returns:
        Personalized SMS message under 160 characters
    """
    first_name = lead_info.get("full_name", "").split()[0]
    insurance_type = lead_info.get("insurance_type", "insurance")
    current_provider = lead_info.get("current_provider", "your current provider")
    savings = lead_info.get("estimated_savings", 500)
    
    # In demo mode, return a quick template
    if DEMO_MODE:
        return f"Hi {first_name}! 👋 Noticed you're with {current_provider} for {insurance_type.lower()}. We could save you ${savings}/yr. Book a quick chat? {CALENDLY_LINK} - Alex @ Solisa"
    
    # Use Groq Llama to generate personalized SMS
    try:
        prompt = f"""Generate a casual, friendly SMS message (under 160 characters) for an insurance lead:

Lead Info:
- Name: {first_name}
- Insurance Type: {insurance_type}
- Current Provider: {current_provider}
- Estimated Savings: ${savings}/year
- Life Stage: {lead_info.get('life_stage', 'N/A')}

Requirements:
- Use first name only
- Mention the insurance type and current provider
- Highlight the savings opportunity
- Include this booking link: {CALENDLY_LINK}
- Sign as "Alex @ Solisa"
- Include one relevant emoji
- Keep it under 160 characters
- Sound helpful, not salesy

Generate only the SMS text, no quotes or explanations."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        sms_text = response.choices[0].message.content.strip()
        
        # Ensure it's under 160 characters
        if len(sms_text) > 160:
            sms_text = sms_text[:157] + "..."
        
        return sms_text
    
    except Exception as e:
        print(f"Error generating SMS with Groq: {e}")
        # Fallback message
        return f"Hi {first_name}! We can save you ${savings}/yr on {insurance_type.lower()}. Book a chat? {CALENDLY_LINK} - Alex @ Solisa"


def generate_personalized_email(lead_info: dict) -> dict:
    """
    Generate a personalized email for the lead.
    
    Args:
        lead_info: Dictionary with enriched lead information
    
    Returns:
        Dictionary with 'subject' and 'body' keys
    """
    first_name = lead_info.get("full_name", "").split()[0]
    full_name = lead_info.get("full_name", "there")
    insurance_type = lead_info.get("insurance_type", "insurance")
    current_provider = lead_info.get("current_provider", "your current provider")
    savings = lead_info.get("estimated_savings", 500)
    life_stage = lead_info.get("life_stage", "")
    pain_points = lead_info.get("pain_points", [])
    renewal_date = lead_info.get("renewal_date", "soon")
    
    # In demo mode, return a template email
    if DEMO_MODE:
        subject = f"{first_name}, save ${savings}/year on your {insurance_type} insurance"
        
        pain_points_text = "\n".join([f"• {point}" for point in pain_points[:2]]) if pain_points else "• High premiums\n• Poor customer service"
        
        body = f"""Hi {full_name},

I noticed you're currently with {current_provider} for your {insurance_type.lower()} insurance. As a {life_stage.lower()}, you deserve coverage that actually works for you.

Here's what caught my attention:
{pain_points_text}

The good news? We can likely save you ${savings} per year while addressing these concerns. With your renewal coming up in {renewal_date}, now's the perfect time to explore better options.

I'd love to show you a personalized quote that fits your needs. It takes just 15 minutes, and there's zero pressure.

Book a quick call: {CALENDLY_LINK}

Looking forward to helping you get the coverage you deserve!

Best,
Alex
Solisa Insurance
alex@solisa.com"""
        
        return {"subject": subject, "body": body}
    
    # Use Groq Llama to generate personalized email
    try:
        pain_points_list = "\n".join([f"- {point}" for point in pain_points[:2]]) if pain_points else "- High premiums"
        
        prompt = f"""Generate a professional but friendly email for an insurance lead:

Lead Info:
- Full Name: {full_name}
- First Name: {first_name}
- Insurance Type: {insurance_type}
- Current Provider: {current_provider}
- Estimated Savings: ${savings}/year
- Life Stage: {life_stage}
- Renewal Date: {renewal_date}
- Pain Points:
{pain_points_list}

Requirements:
- Write a compelling subject line (under 60 characters)
- Personalized greeting with full name
- Acknowledge their life stage
- Address their specific pain points
- Highlight the savings opportunity (${savings}/year)
- Mention their upcoming renewal date
- Include a clear call-to-action with this link: {CALENDLY_LINK}
- Professional but warm tone
- Sign as "Alex" from "Solisa Insurance"
- Email signature: alex@solisa.com
- Keep it concise (under 300 words)

Generate the email in this format:
SUBJECT: [subject line]
BODY:
[email body]

Do not include any other text or explanations."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        email_text = response.choices[0].message.content.strip()
        
        # Parse subject and body
        if "SUBJECT:" in email_text and "BODY:" in email_text:
            parts = email_text.split("BODY:", 1)
            subject = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip()
        else:
            # Fallback if format is not as expected
            lines = email_text.split("\n", 1)
            subject = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else email_text
        
        return {"subject": subject, "body": body}
    
    except Exception as e:
        print(f"Error generating email with Groq: {e}")
        # Fallback email
        subject = f"{first_name}, save ${savings}/year on your {insurance_type} insurance"
        body = f"""Hi {full_name},

I noticed you're with {current_provider} for {insurance_type.lower()} insurance. We can save you ${savings}/year with better coverage.

Your renewal is coming up in {renewal_date} - let's chat about your options.

Book a quick call: {CALENDLY_LINK}

Best,
Alex
Solisa Insurance
alex@solisa.com"""
        
        return {"subject": subject, "body": body}
