import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Check if we're in demo mode
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not DEMO_MODE and groq_api_key:
    client = Groq(api_key=groq_api_key)
else:
    client = None


def analyze_touchpoint(content: str, lead_data: dict) -> dict:
    """
    Analyze a touchpoint (call transcript, email, text)
    Returns: sentiment, intent, objections, key_points, urgency
    """
    
    # Demo mode - return mock analysis
    if DEMO_MODE or not client:
        print("\n🎭 DEMO MODE - Using mock conversation analysis")
        return {
            "sentiment": "neutral",
            "intent": "interested_but_objecting",
            "objections": ["too expensive", "busy this week"],
            "key_points": [
                "Currently paying $180/month with Geico",
                "Quote is $220/month ($40 more)",
                "Has clean driving record",
                "Interested in accident forgiveness",
                "Needs time to think"
            ],
            "urgency": "medium"
        }
    
    # Real AI analysis
    try:
        prompt = f"""Analyze this conversation with an insurance prospect:

PROSPECT INFO:
- Name: {lead_data.get('full_name', 'Unknown')}
- Insurance Type: {lead_data.get('insurance_type', 'Unknown')}
- Current Provider: {lead_data.get('current_provider', 'Unknown')}

CONVERSATION:
{content}

Analyze and return ONLY valid JSON with these exact fields:
{{
  "sentiment": "positive/neutral/negative",
  "intent": "browsing/interested/ready/objecting/lost",
  "objections": ["list", "of", "objections"],
  "key_points": ["important", "things", "mentioned"],
  "urgency": "low/medium/high"
}}

Return ONLY the JSON, no other text."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON response
        analysis = json.loads(response.choices[0].message.content)
        print(f"✅ AI analyzed conversation: {analysis['intent']}")
        
        return analysis
    
    except Exception as e:
        print(f"❌ Error analyzing touchpoint: {e}")
        # Fallback to demo mode
        return {
            "sentiment": "neutral",
            "intent": "interested",
            "objections": [],
            "key_points": [],
            "urgency": "medium"
        }


def detect_intent_shift(previous_touchpoints: list, current_intent: str) -> dict:
    """
    Detect if there's been a shift in the lead's intent over time.
    
    Args:
        previous_touchpoints: List of previous touchpoint dicts with intent
        current_intent: Current intent from latest analysis
    
    Returns:
        Dict with shift_detected, previous_intent, current_intent, shift_type, significance
    """
    if not previous_touchpoints or len(previous_touchpoints) == 0:
        return {
            "shift_detected": False,
            "previous_intent": None,
            "current_intent": current_intent,
            "shift_type": "initial",
            "significance": "low",
            "message": "First touchpoint - establishing baseline intent"
        }
    
    # Get the most recent previous intent
    previous_intent = None
    for tp in reversed(previous_touchpoints):
        if tp.get('intent'):
            previous_intent = tp.get('intent')
            break
    
    if not previous_intent:
        return {
            "shift_detected": False,
            "previous_intent": None,
            "current_intent": current_intent,
            "shift_type": "initial",
            "significance": "low",
            "message": "No previous intent data available"
        }
    
    # Check if intent has changed
    if previous_intent == current_intent:
        return {
            "shift_detected": False,
            "previous_intent": previous_intent,
            "current_intent": current_intent,
            "shift_type": "stable",
            "significance": "low",
            "message": f"Intent remains stable: {current_intent}"
        }
    
    # Define intent progression levels (lower = earlier stage, higher = closer to conversion)
    intent_levels = {
        "browsing": 1,
        "interested": 2,
        "interested_but_objecting": 2.5,
        "objecting": 2,
        "ready": 3,
        "lost": 0
    }
    
    prev_level = intent_levels.get(previous_intent, 1)
    curr_level = intent_levels.get(current_intent, 1)
    
    # Determine shift type and significance
    if curr_level > prev_level:
        # Positive shift (moving toward conversion)
        shift_type = "positive"
        if curr_level - prev_level >= 2:
            significance = "high"
            message = f"🚀 MAJOR POSITIVE SHIFT: {previous_intent} → {current_intent}! Lead is moving toward conversion!"
        else:
            significance = "medium"
            message = f"✅ Positive shift: {previous_intent} → {current_intent}. Lead is warming up!"
    
    elif curr_level < prev_level:
        # Negative shift (moving away from conversion)
        shift_type = "negative"
        if prev_level - curr_level >= 2:
            significance = "high"
            message = f"⚠️ MAJOR NEGATIVE SHIFT: {previous_intent} → {current_intent}. Immediate action needed!"
        else:
            significance = "medium"
            message = f"⚠️ Negative shift: {previous_intent} → {current_intent}. Need to re-engage."
    
    else:
        # Lateral shift (same level but different intent)
        shift_type = "lateral"
        significance = "low"
        message = f"↔️ Lateral shift: {previous_intent} → {current_intent}. Intent changed but level similar."
    
    return {
        "shift_detected": True,
        "previous_intent": previous_intent,
        "current_intent": current_intent,
        "shift_type": shift_type,
        "significance": significance,
        "message": message,
        "previous_level": prev_level,
        "current_level": curr_level
    }


def generate_followup_actions(lead_data: dict, touchpoint_data: dict, analysis: dict, intent_shift: dict = None) -> list:
    """
    Generate recommended follow-up actions based on conversation analysis
    Returns: list of actions with type, priority, content, reasoning, timing
    """
    
    # Demo mode - return mock actions
    if DEMO_MODE or not client:
        print("\n🎭 DEMO MODE - Generating mock follow-up actions")
        
        actions = []
        
        # Action 1: SMS
        actions.append({
            "action_type": "sms",
            "priority": "high",
            "content": f"Hi {lead_data.get('full_name', 'there').split()[0]}! Quick follow-up - I found a way to get you closer to your current rate. Can we chat for 5 mins tomorrow? 📞 - Alex @ Solisa",
            "reasoning": "Prospect mentioned price as main objection. Quick SMS shows we're addressing their concern.",
            "timing": "immediate"
        })
        
        # Action 2: Email
        calendly_link = lead_data.get('calendly_link', 'https://calendly.com/solisa-demo/30min')
        email_content = f"""Subject: Accident Forgiveness: Worth the Extra $40?

Hi {lead_data.get('full_name', 'there').split()[0]},

Great talking with you today! I know the $40/month difference gave you pause.

Here's something to consider: With your clean driving record, you're a perfect candidate for accident forgiveness. Here's what that means:

• One accident won't raise your rates
• Average rate increase after accident: $500-$1,200/year
• Your protection: $0 increase

So that $40/month ($480/year) could save you $500-$1,200 if something happens.

Plus, I'm working on getting you a better rate. Let's schedule a quick 15-minute call to discuss your options:

📅 Book your call here: {calendly_link}

Looking forward to finding you the best coverage!

Best,
Alex
Solisa Insurance"""
        
        actions.append({
            "action_type": "email",
            "priority": "medium",
            "content": email_content,
            "reasoning": "Provide ROI case study addressing price objection with concrete numbers.",
            "timing": "1hour"
        })
        
        # Action 3: Call script
        call_script = f"""CALL SCRIPT - Follow-up with {lead_data.get('full_name', 'Prospect')}

OBJECTIVE: Address price objection, present revised quote

OPENING:
"Hi {lead_data.get('full_name', 'there').split()[0]}, it's Alex from Solisa. Do you have 5 minutes? I found some options that might work better for you."

KEY POINTS TO COVER:
1. Acknowledge their concern about the $40 difference
2. Present revised quote (aim for $200-210/month)
3. Emphasize accident forgiveness value with their clean record
4. Offer flexible payment options

OBJECTION HANDLING:
- If still too expensive: "What monthly rate would work for your budget?"
- If needs time: "I understand. Can I check back next week?"
- If comparing: "What would make this an easy yes for you?"

CLOSE:
"Does this feel more in line with what you're looking for?"

NEXT STEP: Book follow-up or close deal"""
        
        actions.append({
            "action_type": "call",
            "priority": "medium",
            "content": call_script,
            "reasoning": "Prepare for tomorrow's call with specific talking points addressing their objections.",
            "timing": "1day"
        })
        
        return actions
    
    # Real AI generation
    try:
        objections_str = ", ".join(analysis.get('objections', []))
        key_points_str = ", ".join(analysis.get('key_points', []))
        
        # Build intent shift context
        intent_shift_context = ""
        if intent_shift and intent_shift.get('shift_detected'):
            intent_shift_context = f"""
INTENT SHIFT DETECTED:
- Previous Intent: {intent_shift.get('previous_intent')}
- Current Intent: {intent_shift.get('current_intent')}
- Shift Type: {intent_shift.get('shift_type')} ({intent_shift.get('significance')} significance)
- Message: {intent_shift.get('message')}

⚠️ IMPORTANT: Adjust your follow-up strategy based on this intent shift!
"""
        
        calendly_link = lead_data.get('calendly_link', 'https://calendly.com/solisa-demo/30min')
        
        prompt = f"""Based on this conversation analysis, recommend 2-3 specific follow-up actions:

LEAD INFO:
- Name: {lead_data.get('full_name', 'Unknown')}
- Email: {lead_data.get('email', 'Unknown')}
- Phone: {lead_data.get('phone', 'Unknown')}
- Insurance: {lead_data.get('insurance_type', 'Unknown')}
- Calendly Booking Link: {calendly_link}

ANALYSIS:
- Sentiment: {analysis.get('sentiment', 'neutral')}
- Intent: {analysis.get('intent', 'interested')}
- Objections: {objections_str}
- Key Points: {key_points_str}
- Urgency: {analysis.get('urgency', 'medium')}
{intent_shift_context}
CONVERSATION:
{touchpoint_data.get('content', '')}

Generate specific, actionable follow-ups. Return ONLY valid JSON array:
[
  {{
    "action_type": "sms/email/call/escalate",
    "priority": "high/medium/low",
    "content": "exact message or script to use",
    "reasoning": "why this action makes sense",
    "timing": "immediate/1hour/1day"
  }}
]

IMPORTANT: For email actions, ALWAYS include the Calendly booking link ({calendly_link}) with a clear call-to-action to book a follow-up call.
Make messages personal, natural, and address their specific objections.
Return ONLY the JSON array, no other text."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON response
        actions = json.loads(response.choices[0].message.content)
        print(f"✅ Generated {len(actions)} follow-up actions")
        
        return actions
    
    except Exception as e:
        print(f"❌ Error generating actions: {e}")
        # Fallback to simple action
        return [{
            "action_type": "email",
            "priority": "medium",
            "content": f"Hi {lead_data.get('full_name', 'there')},\n\nThanks for your time today. Let me know if you have any questions!\n\nBest,\nAlex",
            "reasoning": "General follow-up",
            "timing": "1hour"
        }]
