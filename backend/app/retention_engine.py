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


def calculate_policy_health_score(lead_data: dict, touchpoints: list = None, life_events: list = None) -> dict:
    """
    Calculate policy health score (0-100) and predict churn risk using AI analysis
    
    Args:
        lead_data: Lead information
        touchpoints: List of customer interactions (emails, calls, SMS)
        life_events: List of life events
    
    Returns:
        Dict with health_score, churn_risk, and contributing factors
    """
    
    print("\n🤖 AI-POWERED Policy Health Score Calculation")
    
    # Prepare data for AI analysis
    touchpoint_count = len(touchpoints) if touchpoints else 0
    life_event_count = len(life_events) if life_events else 0
    
    # Get recent touchpoint sentiments and intents
    recent_sentiments = []
    recent_intents = []
    customer_responses = []
    
    if touchpoints:
        for tp in touchpoints[-5:]:  # Last 5 touchpoints
            if tp.get('sentiment'):
                recent_sentiments.append(tp['sentiment'])
            if tp.get('intent'):
                recent_intents.append(tp['intent'])
            if tp.get('content'):
                customer_responses.append(tp['content'][:200])  # First 200 chars
    
    # Get life event outcomes
    life_event_outcomes = []
    unaddressed_events = 0
    if life_events:
        for event in life_events:
            outcome = event.get('outcome') or 'pending'  # Handle None values
            life_event_outcomes.append(outcome)
            if outcome == 'pending' or outcome is None:
                unaddressed_events += 1
    
    # Build AI prompt with REAL data
    prompt = f"""You are an insurance policy health analyst. Analyze this customer's data and predict their churn risk.

CUSTOMER DATA:
- Name: {lead_data.get('full_name')}
- Policy Type: {lead_data.get('insurance_type')}
- Account Age: {lead_data.get('created_at', 'Unknown')}

ENGAGEMENT DATA:
- Total Touchpoints: {touchpoint_count}
- Recent Sentiments: {', '.join(recent_sentiments) if recent_sentiments else 'No data'}
- Recent Intents: {', '.join(recent_intents) if recent_intents else 'No data'}
- Customer Responses: {len(customer_responses)} interactions recorded

LIFE EVENTS:
- Total Life Events: {life_event_count}
- Unaddressed Events: {unaddressed_events}
- Event Outcomes: {', '.join(life_event_outcomes) if life_event_outcomes else 'None'}

RECENT INTERACTIONS (Last 5):
{chr(10).join([f"- {resp}" for resp in customer_responses]) if customer_responses else "No recent interactions"}

Based on this REAL data, provide a policy health score analysis. Return ONLY valid JSON:
{{
    "health_score": <0-100>,
    "churn_risk": "<low/medium/high>",
    "churn_probability": <0-100>,
    "days_to_predicted_churn": <number>,
    "engagement_score": <0-100>,
    "satisfaction_score": <0-100>,
    "usage_score": <0-100>,
    "payment_score": <0-100>,
    "reasoning": "<brief explanation>",
    "retention_actions": ["<action1>", "<action2>"],
    "priority": "<low/medium/high>"
}}

SCORING GUIDELINES:
- Engagement: Based on touchpoint count and recency (more = better)
- Satisfaction: Based on sentiment analysis (positive = higher)
- Usage: Based on intent patterns (interested/ready = good, objecting/lost = bad)
- Payment: Assume good unless data suggests otherwise
- Health Score: Weighted average (Engagement 25%, Satisfaction 30%, Usage 20%, Payment 25%)
- Churn Risk: Low (80-100), Medium (50-79), High (0-49)
- Unaddressed life events = higher churn risk
- Negative sentiment = lower satisfaction score
- "Lost" or "objecting" intent = lower health score

Return ONLY the JSON, no other text."""

    # Use AI to calculate score
    if client:
        try:
            print("📊 Analyzing customer data with AI...")
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for consistent scoring
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse AI response
            result = json.loads(response.choices[0].message.content)
            print(f"✅ AI Health Score: {result['health_score']} ({result['churn_risk']} risk)")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in AI calculation: {e}")
            # Fall through to rule-based backup
    
    # Fallback: Rule-based calculation using real data
    print("⚠️ Using rule-based calculation (AI not available)")
    
    # Calculate engagement score from real data
    engagement_score = min(100, (touchpoint_count * 10) + 50)  # More touchpoints = more engaged
    
    # Calculate satisfaction from sentiment
    satisfaction_score = 75  # Default
    if recent_sentiments:
        positive_count = sum(1 for s in recent_sentiments if s == 'positive')
        negative_count = sum(1 for s in recent_sentiments if s == 'negative')
        sentiment_ratio = (positive_count - negative_count) / len(recent_sentiments)
        satisfaction_score = max(0, min(100, 75 + (sentiment_ratio * 25)))
    
    # Calculate usage score from intent
    usage_score = 75  # Default
    if recent_intents:
        good_intents = sum(1 for i in recent_intents if i in ['interested', 'ready'])
        bad_intents = sum(1 for i in recent_intents if i in ['objecting', 'lost'])
        intent_ratio = (good_intents - bad_intents) / len(recent_intents)
        usage_score = max(0, min(100, 75 + (intent_ratio * 25)))
    
    # Payment score (assume good unless we have data)
    payment_score = 90
    
    # Calculate overall health score
    health_score = int(
        engagement_score * 0.25 +
        satisfaction_score * 0.30 +
        usage_score * 0.20 +
        payment_score * 0.25
    )
    
    # Adjust for unaddressed life events
    if unaddressed_events > 0:
        health_score = max(0, health_score - (unaddressed_events * 10))
    
    # Determine churn risk
    if health_score >= 80:
        churn_risk = "low"
        churn_probability = 15
    elif health_score >= 50:
        churn_risk = "medium"
        churn_probability = 35
    else:
        churn_risk = "high"
        churn_probability = 65
    
    return {
        "health_score": health_score,
        "churn_risk": churn_risk,
        "churn_probability": churn_probability,
        "days_to_predicted_churn": 90,
        "engagement_score": int(engagement_score),
        "satisfaction_score": int(satisfaction_score),
        "usage_score": int(usage_score),
        "payment_score": payment_score,
        "reasoning": f"Based on {touchpoint_count} interactions, {len(recent_sentiments)} sentiment data points, and {unaddressed_events} unaddressed life events",
        "retention_actions": [
            "Increase engagement through personalized outreach" if engagement_score < 70 else "Maintain current engagement level",
            "Address unaddressed life events" if unaddressed_events > 0 else "Monitor for new life events",
            "Improve satisfaction through proactive support" if satisfaction_score < 70 else "Continue excellent service"
        ],
        "priority": "high" if health_score < 70 else "medium" if health_score < 85 else "low"
    }


def analyze_life_event(event_type: str, lead_data: dict) -> dict:
    """
    Analyze a life event and determine upsell/retention opportunity
    
    Args:
        event_type: Type of life event (new_baby, home_reno, teen_driver, job_change)
        lead_data: Lead information
    
    Returns:
        Dict with opportunity analysis and recommended action
    """
    
    print(f"\n🎯 Analyzing life event: {event_type}")
    
    first_name = lead_data.get('full_name', '').split()[0] if lead_data.get('full_name') else 'there'
    
    # Define opportunities for each life event type (EXACT SPEC)
    opportunities = {
        "new_baby": {
            "opportunity_type": "upsell",
            "recommended_product": "umbrella_insurance",
            "estimated_value": 25,  # $25/month
            "message": f"🎉 Congrats on the new baby, {first_name}! As your family grows, have you thought about umbrella insurance? It adds an extra layer of liability protection beyond your regular policies. Would love to send you a quick quote — just let me know!"
        },
        "home_reno": {
            "opportunity_type": "upsell",
            "recommended_product": "flood_coverage",
            "estimated_value": 35,  # $35/month
            "message": f"🏡 Congrats on the new home, {first_name}! Have you thought about adding flood coverage? It's not included in standard policies but can be a lifesaver. Want me to send over a quote?"
        },
        "teen_driver": {
            "opportunity_type": "upsell",
            "recommended_product": "auto_upgrade",
            "estimated_value": 75,  # $75/month
            "message": f"🚗 Hey {first_name}, congrats on the teen driver! That's a big milestone. We have great coverage options for young drivers, including accident forgiveness. Want to review your policy to make sure you're covered?"
        },
        "job_change": {
            "opportunity_type": "retention",
            "recommended_product": "policy_review",
            "estimated_value": 0,
            "message": f"💼 Congrats on the new job, {first_name}! Life changes can affect your insurance needs. Want to do a quick policy review to make sure everything still fits?"
        }
    }
    
    return opportunities.get(event_type, {
        "opportunity_type": "retention",
        "recommended_product": "policy_review",
        "estimated_value": 0,
        "message": f"Hi {first_name}, I wanted to check in and see how things are going. Let me know if there's anything I can help with!"
    })


def generate_retention_action(life_event_data: dict, lead_data: dict, policy_health: dict) -> dict:
    """
    Generate automated retention action (SMS, email, etc.)
    
    Args:
        life_event_data: Life event details
        lead_data: Lead information
        policy_health: Policy health score data
    
    Returns:
        Dict with action details
    """
    
    # Analyze the life event
    analysis = analyze_life_event(life_event_data['event_type'], lead_data)
    
    # Generate action
    action = {
        "action_type": "sms",  # Start with SMS for immediate engagement
        "content": analysis.get('message', ''),
        "recommended_product": analysis.get('recommended_product'),
        "estimated_value": analysis.get('estimated_value'),
        "quote_details": analysis.get('quote_details'),
        "priority": "high" if policy_health.get('churn_risk') == 'high' else "medium",
        "timing": "immediate"
    }
    
    return action


def process_customer_response(response_text: str, life_event_id: int, lead_data: dict) -> dict:
    """
    Process customer response to retention outreach
    
    Args:
        response_text: Customer's response
        life_event_id: ID of the life event
        lead_data: Lead information
    
    Returns:
        Dict with intent analysis and next action
    """
    
    # Demo mode - robust intent detection
    if DEMO_MODE or not client:
        print(f"\n🎭 DEMO MODE - Processing customer response: {response_text}")
        
        # Clean and normalize response
        response_lower = response_text.lower().strip()
        # Remove punctuation for better matching
        import re
        response_clean = re.sub(r'[^\w\s]', '', response_lower)
        
        # Positive intent - very flexible matching
        positive_patterns = [
            'yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'great', 'perfect', 
            'awesome', 'sounds good', 'interested', 'lets do it', 'let do it',
            'do it', 'go ahead', 'sign me up', 'im in', 'count me in',
            'absolutely', 'definitely', 'for sure', 'love to', 'would love'
        ]
        
        if any(pattern in response_clean for pattern in positive_patterns):
            return {
                "intent": "positive",
                "confidence": 0.95,
                "outcome": "converted",
                "next_action": "confirm_and_process",
                "response_message": f"That's wonderful, {lead_data.get('full_name', '').split()[0]}! I'm so glad this feels right for you and your family. I'll get everything set up for you today, and you'll receive a confirmation email with all the details shortly. Thank you for trusting us with your family's protection. If you have any questions at all, I'm always here. 💙"
            }
        
        # Negative intent
        negative_patterns = [
            'no', 'nope', 'not interested', 'no thanks', 'maybe later',
            'not now', 'not right now', 'pass', 'decline', 'not for me'
        ]
        
        if any(pattern in response_clean for pattern in negative_patterns):
            return {
                "intent": "negative",
                "confidence": 0.90,
                "outcome": "declined",
                "next_action": "acknowledge_and_follow_up",
                "response_message": f"I completely understand, {lead_data.get('full_name', '').split()[0]}. You have a lot on your plate right now! Please know there's absolutely no pressure - I just wanted you to know the option is there if you ever need it. Wishing you and your family all the best. Take care! 😊"
            }
        
        # Needs more info
        info_patterns = [
            'tell me more', 'more info', 'details', 'how much', 'what',
            'explain', 'cost', 'price', 'coverage', 'learn more', 'info'
        ]
        
        if any(pattern in response_clean for pattern in info_patterns):
            return {
                "intent": "curious",
                "confidence": 0.85,
                "outcome": "pending",
                "next_action": "provide_details",
                "response_message": f"I'm happy to explain, {lead_data.get('full_name', '').split()[0]}! Umbrella insurance is like an extra safety net - it provides additional liability coverage (typically $1M) beyond your regular auto/home policies. It helps protect your family's assets if there's ever a lawsuit or major claim. Many parents find it gives them peace of mind, especially with little ones. It's usually around $25/month. Would you like me to send you more detailed information? No rush at all - just let me know what works for you. 😊"
            }
        
        # Unclear - default to friendly clarification
        return {
            "intent": "unclear",
            "confidence": 0.50,
            "outcome": "pending",
            "next_action": "clarify",
            "response_message": f"Thanks for getting back to me, {lead_data.get('full_name', '').split()[0]}! I just want to make sure I'm being helpful and not overwhelming you during this busy time. Would you like to learn more about the coverage options, or would you prefer I check back with you later? Whatever works best for you! 😊"
        }
    
    # If we get here, no real AI is configured, use demo logic
    print(f"\n⚠️ No AI client configured - using demo logic")
    
    # Clean and normalize response
    response_lower = response_text.lower().strip()
    import re
    response_clean = re.sub(r'[^\w\s]', '', response_lower)
    
    # Positive intent - very flexible matching
    positive_patterns = [
        'yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'great', 'perfect', 
        'awesome', 'sounds good', 'interested', 'lets do it', 'let do it',
        'do it', 'go ahead', 'sign me up', 'im in', 'count me in',
        'absolutely', 'definitely', 'for sure', 'love to', 'would love'
    ]
    
    if any(pattern in response_clean for pattern in positive_patterns):
        return {
            "intent": "positive",
            "confidence": 0.95,
            "outcome": "converted",
            "next_action": "confirm_and_process",
            "response_message": f"That's wonderful, {lead_data.get('full_name', '').split()[0]}! I'm so glad this feels right for you and your family. I'll get everything set up for you today, and you'll receive a confirmation email with all the details shortly. Thank you for trusting us with your family's protection. If you have any questions at all, I'm always here. 💙"
        }
    
    # Default to pending
    return {
        "intent": "unclear",
        "confidence": 0.50,
        "outcome": "pending",
        "next_action": "clarify",
        "response_message": f"Thanks for getting back to me, {lead_data.get('full_name', '').split()[0]}! I just want to make sure I'm being helpful. Would you like to learn more? 😊"
    }
