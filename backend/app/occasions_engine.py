import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Check if we're in demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not DEMO_MODE and groq_api_key:
    client = Groq(api_key=groq_api_key)
else:
    client = None


def detect_occasions(lead_data: dict) -> list:
    """
    Detect upcoming occasions for a customer
    
    Args:
        lead_data: Lead information including dates
    
    Returns:
        List of detected occasions
    """
    occasions = []
    today = datetime.now()
    
    # Check for policy anniversary
    if lead_data.get('created_at'):
        try:
            policy_start = datetime.fromisoformat(lead_data['created_at'].replace('Z', '+00:00'))
            years_with_company = (today - policy_start).days // 365
            
            if years_with_company > 0:
                # Calculate next anniversary
                next_anniversary = policy_start.replace(year=today.year)
                if next_anniversary < today:
                    next_anniversary = next_anniversary.replace(year=today.year + 1)
                
                days_until = (next_anniversary - today).days
                
                if 0 <= days_until <= 30:  # Within 30 days
                    occasions.append({
                        'type': 'policy_anniversary',
                        'years': years_with_company,
                        'date': next_anniversary.isoformat(),
                        'days_until': days_until,
                        'priority': 'medium'
                    })
        except:
            pass
    
    # Check for birthday (if we had birth date)
    # For demo, we'll simulate this
    
    # Check for renewal date
    if lead_data.get('renewal_date'):
        try:
            renewal_date = datetime.strptime(lead_data['renewal_date'], '%Y-%m-%d')
            days_until = (renewal_date - today).days
            
            if 0 <= days_until <= 60:  # Within 60 days
                occasions.append({
                    'type': 'policy_renewal',
                    'date': renewal_date.isoformat(),
                    'days_until': days_until,
                    'priority': 'high' if days_until <= 30 else 'medium'
                })
        except:
            pass
    
    return occasions


def generate_occasion_message(occasion_type: str, lead_data: dict, occasion_data: dict = None) -> dict:
    """
    Generate personalized message for an occasion
    
    Args:
        occasion_type: Type of occasion
        lead_data: Lead information
        occasion_data: Additional occasion details
    
    Returns:
        Dict with message and offer details
    """
    
    first_name = lead_data.get('full_name', '').split()[0]
    
    print(f"\n🎉 Generating occasion message: {occasion_type}")
    
    # Always use detailed, empathetic messages
    occasion_messages = {
            "policy_anniversary": {
                "message": f"🎉 Happy {occasion_data.get('years', 2)}-year anniversary with Solisa, {first_name}! We're so grateful to have you as part of our family. As a thank you for your loyalty, here's a special gift: $50 off your next renewal! You've been an amazing customer, and we look forward to many more years together. Cheers to you! 🥳",
                "offer_type": "loyalty_discount",
                "offer_value": 50,
                "offer_description": "$50 off next renewal",
                "action_required": False
            },
            "birthday": {
                "message": f"🎂 Happy Birthday, {first_name}! We hope your day is filled with joy and celebration. As a birthday gift from us, enjoy free roadside assistance for the entire month! It's our way of saying thank you for being such a valued customer. Have a wonderful day! 🎈",
                "offer_type": "free_service",
                "offer_value": 0,
                "offer_description": "Free roadside assistance for 1 month",
                "action_required": False
            },
            "policy_renewal": {
                "message": f"Hi {first_name}, your policy renewal is coming up in {occasion_data.get('days_until', 30)} days. Before you renew, I wanted to check in - are you still happy with your coverage? Sometimes life changes, and your insurance should too. I'm here if you'd like to review your policy or explore any updates. No pressure, just want to make sure you're getting the best value! 😊",
                "offer_type": "policy_review",
                "offer_value": 0,
                "offer_description": "Complimentary policy review",
                "action_required": True
            },
            "usage_based_savings": {
                "message": f"Hi {first_name}, I noticed something interesting - you're driving about 40% less than the average policyholder! That's great for the environment and your wallet. Have you considered switching to our pay-per-mile plan? Based on your driving, you could save around $340 per year. Want to learn more? No obligation, just thought you'd like to know! 🚗",
                "offer_type": "plan_switch",
                "offer_value": 340,
                "offer_description": "Save $340/year with pay-per-mile",
                "action_required": True
            },
            "holiday_season": {
                "message": f"Happy Holidays, {first_name}! 🎄 As we wrap up the year, I wanted to reach out and say thank you for being such a wonderful customer. If you're planning any holiday travel, remember you have 24/7 roadside assistance. Safe travels and warm wishes to you and your family! ❄️",
                "offer_type": "reminder",
                "offer_value": 0,
                "offer_description": "Holiday travel reminder",
                "action_required": False
            }
        }
    
    return occasion_messages.get(occasion_type, {
        "message": f"Hi {first_name}, just checking in to see how everything is going with your policy. I'm here if you need anything!",
        "offer_type": "check_in",
        "offer_value": 0,
        "offer_description": "Customer check-in",
        "action_required": False
    })


def analyze_usage_patterns(lead_data: dict) -> dict:
    """
    Analyze customer usage patterns for upsell opportunities
    
    Args:
        lead_data: Lead information
    
    Returns:
        Dict with usage analysis and recommendations
    """
    
    # Demo mode - simulate usage analysis
    if DEMO_MODE or not client:
        print("\n🎭 DEMO MODE - Analyzing usage patterns")
        
        # Simulate different usage patterns
        import random
        
        patterns = [
            {
                "pattern_type": "low_mileage",
                "current_usage": "60% below average",
                "recommendation": "pay_per_mile",
                "potential_savings": 340,
                "confidence": 0.85,
                "message": "Customer drives significantly less than average - perfect candidate for pay-per-mile"
            },
            {
                "pattern_type": "high_engagement",
                "current_usage": "Uses app regularly, no claims",
                "recommendation": "safe_driver_discount",
                "potential_savings": 120,
                "confidence": 0.90,
                "message": "Excellent driving record and high engagement - eligible for safe driver discount"
            },
            {
                "pattern_type": "bundle_opportunity",
                "current_usage": "Auto only, owns home",
                "recommendation": "home_auto_bundle",
                "potential_savings": 400,
                "confidence": 0.75,
                "message": "Customer owns home but only has auto insurance - bundle opportunity"
            }
        ]
        
        return random.choice(patterns)
    
    # Real AI analysis would go here
    return {
        "pattern_type": "standard",
        "current_usage": "Average",
        "recommendation": None,
        "potential_savings": 0,
        "confidence": 0.5,
        "message": "Standard usage pattern"
    }


def generate_occasion_action(occasion_type: str, lead_data: dict, occasion_data: dict = None) -> dict:
    """
    Generate automated action for an occasion
    
    Args:
        occasion_type: Type of occasion
        lead_data: Lead information
        occasion_data: Additional occasion details
    
    Returns:
        Dict with action details
    """
    
    message_data = generate_occasion_message(occasion_type, lead_data, occasion_data)
    
    # Determine action type based on occasion
    action_type = "sms"  # Default to SMS for most occasions
    
    if occasion_type in ['policy_renewal', 'usage_based_savings']:
        action_type = "email"  # More detailed info needed
    
    return {
        "action_type": action_type,
        "content": message_data['message'],
        "offer_type": message_data['offer_type'],
        "offer_value": message_data['offer_value'],
        "offer_description": message_data['offer_description'],
        "action_required": message_data['action_required'],
        "priority": "high" if message_data['action_required'] else "medium",
        "timing": "immediate"
    }
