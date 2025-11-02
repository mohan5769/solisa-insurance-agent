import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Import local modules
try:
    from .database import get_db, init_db
    from .models import Lead, Touchpoint, FollowUpAction, LifeEvent, PolicyHealth, Occasion
    from .enrichment import enrich_lead
    from .ai_engine import generate_personalized_sms, generate_personalized_email
    from .communications import send_sms, send_email
    from .followup_engine import analyze_touchpoint, generate_followup_actions, detect_intent_shift
    from .retention_engine import calculate_policy_health_score, analyze_life_event, generate_retention_action, process_customer_response
    from .occasions_engine import detect_occasions, generate_occasion_message, analyze_usage_patterns, generate_occasion_action
except ImportError:
    from database import get_db, init_db
    from models import Lead, Touchpoint, FollowUpAction, LifeEvent, PolicyHealth, Occasion
    from enrichment import enrich_lead
    from ai_engine import generate_personalized_sms, generate_personalized_email
    from communications import send_sms, send_email
    from followup_engine import analyze_touchpoint, generate_followup_actions, detect_intent_shift
    from retention_engine import calculate_policy_health_score, analyze_life_event, generate_retention_action, process_customer_response
    from occasions_engine import detect_occasions, generate_occasion_message, analyze_usage_patterns, generate_occasion_action

# Load environment variables
load_dotenv()

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Solisa AI SDR API",
    description="AI-powered insurance lead management and outreach",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class LeadCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    insurance_type: str
    current_provider: Optional[str] = None

class LeadResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    insurance_type: str
    current_provider: Optional[str]
    life_stage: Optional[str]
    estimated_age_range: Optional[str]
    pain_points: Optional[list]
    estimated_savings: Optional[int]
    renewal_date: Optional[str]
    sms_sent: bool
    sms_sent_at: Optional[str]
    sms_content: Optional[str]
    email_sent: bool
    email_sent_at: Optional[str]
    email_subject: Optional[str]
    email_content: Optional[str]
    booking_confirmed: bool
    booking_confirmed_at: Optional[str]
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_leads: int
    sms_sent: int
    emails_sent: int
    meetings_booked: int
    conversion_rate: float


# API Endpoints

@app.get("/")
def root():
    """Root endpoint - API status"""
    return {
        "status": "online",
        "service": "Solisa AI SDR API",
        "version": "1.0.0",
        "demo_mode": os.getenv("DEMO_MODE", "true").lower() == "true"
    }


@app.post("/api/leads", response_model=LeadResponse)
def create_lead(lead_data: LeadCreate, db: Session = Depends(get_db)):
    """
    Create a new lead, enrich data, and send personalized outreach.
    """
    # Convert to dict for enrichment
    lead_dict = lead_data.model_dump()
    
    # Enrich lead data
    enriched_data = enrich_lead(lead_dict)
    
    # Create lead in database
    new_lead = Lead(
        full_name=enriched_data["full_name"],
        email=enriched_data["email"],
        phone=enriched_data["phone"],
        insurance_type=enriched_data["insurance_type"],
        current_provider=enriched_data["current_provider"],
        life_stage=enriched_data["life_stage"],
        estimated_age_range=enriched_data["estimated_age_range"],
        pain_points=enriched_data["pain_points"],
        estimated_savings=enriched_data["estimated_savings"],
        renewal_date=enriched_data["renewal_date"],
        calendly_link=os.getenv("CALENDLY_LINK", "https://calendly.com/solisa-demo/30min"),
        status="enriched"
    )
    
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    
    # Generate personalized messages
    sms_message = generate_personalized_sms(enriched_data)
    email_data = generate_personalized_email(enriched_data)
    
    # Send SMS
    sms_result = send_sms(new_lead.phone, sms_message)
    if sms_result["success"]:
        new_lead.sms_sent = True
        new_lead.sms_sent_at = datetime.utcnow()
        new_lead.sms_content = sms_message
        new_lead.status = "contacted"
    
    # Send Email
    email_result = send_email(
        new_lead.email,
        email_data["subject"],
        email_data["body"]
    )
    if email_result["success"]:
        new_lead.email_sent = True
        new_lead.email_sent_at = datetime.utcnow()
        new_lead.email_subject = email_data["subject"]
        new_lead.email_content = email_data["body"]
    
    # Update lead in database
    db.commit()
    db.refresh(new_lead)
    
    # Return lead data
    return new_lead.to_dict()


@app.get("/api/leads", response_model=List[LeadResponse])
def get_leads(db: Session = Depends(get_db)):
    """
    Get all leads, ordered by created_at descending.
    """
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
    return [lead.to_dict() for lead in leads]


@app.get("/api/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Get a single lead by ID.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead.to_dict()


@app.post("/api/leads/{lead_id}/book")
def book_meeting(lead_id: int, db: Session = Depends(get_db)):
    """
    Mark a lead as having booked a meeting.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    lead.booking_confirmed = True
    lead.booking_confirmed_at = datetime.utcnow()
    lead.status = "booked"
    
    db.commit()
    db.refresh(lead)
    
    return {
        "success": True,
        "message": "Meeting booked successfully",
        "lead": lead.to_dict()
    }


@app.get("/api/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """
    Get dashboard statistics.
    """
    total_leads = db.query(Lead).count()
    sms_sent = db.query(Lead).filter(Lead.sms_sent == True).count()
    emails_sent = db.query(Lead).filter(Lead.email_sent == True).count()
    meetings_booked = db.query(Lead).filter(Lead.booking_confirmed == True).count()
    
    # Calculate conversion rate
    conversion_rate = (meetings_booked / total_leads * 100) if total_leads > 0 else 0.0
    
    return {
        "total_leads": total_leads,
        "sms_sent": sms_sent,
        "emails_sent": emails_sent,
        "meetings_booked": meetings_booked,
        "conversion_rate": round(conversion_rate, 2)
    }


@app.post("/api/webhooks/calendly")
async def calendly_webhook(request: dict, db: Session = Depends(get_db)):
    """
    Calendly webhook endpoint - automatically marks leads as booked when they schedule via Calendly.
    
    Calendly sends webhook when:
    - invitee.created (someone books a meeting)
    - invitee.canceled (someone cancels)
    
    Webhook payload includes invitee email which we use to find the lead.
    """
    try:
        # Extract event type
        event_type = request.get("event")
        
        # Handle invitee.created (booking confirmed)
        if event_type == "invitee.created":
            payload = request.get("payload", {})
            invitee_email = payload.get("email")
            invitee_name = payload.get("name")
            event_start_time = payload.get("scheduled_event", {}).get("start_time")
            
            if not invitee_email:
                return {"status": "error", "message": "No email in webhook payload"}
            
            # Find lead by email
            lead = db.query(Lead).filter(Lead.email == invitee_email).first()
            
            if lead:
                # Mark as booked
                lead.booking_confirmed = True
                lead.booking_confirmed_at = datetime.utcnow()
                lead.status = "booked"
                db.commit()
                
                print(f"✅ Calendly Webhook: Lead {lead.full_name} ({invitee_email}) booked meeting!")
                print(f"   Event Time: {event_start_time}")
                
                return {
                    "status": "success",
                    "message": f"Lead {lead.full_name} marked as booked",
                    "lead_id": lead.id
                }
            else:
                # Lead not found - might be a new prospect
                print(f"⚠️  Calendly Webhook: No lead found for {invitee_email}")
                return {
                    "status": "warning",
                    "message": f"No lead found for email {invitee_email}"
                }
        
        # Handle invitee.canceled (booking canceled)
        elif event_type == "invitee.canceled":
            payload = request.get("payload", {})
            invitee_email = payload.get("email")
            
            if invitee_email:
                lead = db.query(Lead).filter(Lead.email == invitee_email).first()
                if lead:
                    lead.booking_confirmed = False
                    lead.booking_confirmed_at = None
                    lead.status = "contacted"
                    db.commit()
                    
                    print(f"❌ Calendly Webhook: Lead {lead.full_name} canceled meeting")
                    
                    return {
                        "status": "success",
                        "message": f"Lead {lead.full_name} booking canceled"
                    }
        
        return {"status": "received", "event": event_type}
        
    except Exception as e:
        print(f"❌ Error processing Calendly webhook: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================
# PHASE 2: AGENTIC FOLLOW-UP BRAIN ENDPOINTS
# ============================================================

class TouchpointCreate(BaseModel):
    type: str  # call, sms, email, note
    direction: Optional[str] = None  # inbound, outbound
    content: str  # transcript, message, note


@app.post("/api/leads/{lead_id}/touchpoint")
def add_touchpoint(lead_id: int, touchpoint_data: TouchpointCreate, db: Session = Depends(get_db)):
    """
    Add a new touchpoint (call transcript, email, text, note) and analyze it
    """
    # Get lead
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Create touchpoint
    touchpoint = Touchpoint(
        lead_id=lead_id,
        type=touchpoint_data.type,
        direction=touchpoint_data.direction,
        content=touchpoint_data.content
    )
    
    db.add(touchpoint)
    db.commit()
    db.refresh(touchpoint)
    
    print(f"\n📝 New {touchpoint_data.type} touchpoint added for {lead.full_name}")
    
    # Get previous touchpoints for intent shift detection
    previous_touchpoints = db.query(Touchpoint).filter(
        Touchpoint.lead_id == lead_id,
        Touchpoint.id != touchpoint.id
    ).order_by(Touchpoint.created_at.asc()).all()
    
    previous_touchpoints_dicts = [tp.to_dict() for tp in previous_touchpoints]
    
    # Analyze touchpoint with AI
    lead_dict = lead.to_dict()
    analysis = analyze_touchpoint(touchpoint.content, lead_dict)
    
    # Update touchpoint with analysis
    touchpoint.sentiment = analysis.get("sentiment")
    touchpoint.intent = analysis.get("intent")
    touchpoint.objections = analysis.get("objections", [])
    touchpoint.key_points = analysis.get("key_points", [])
    touchpoint.urgency = analysis.get("urgency")
    db.commit()
    db.refresh(touchpoint)
    
    print(f"🤖 AI Analysis: {analysis.get('intent')} - {len(analysis.get('objections', []))} objections")
    
    # Detect intent shift
    intent_shift = detect_intent_shift(previous_touchpoints_dicts, analysis.get('intent'))
    
    if intent_shift.get('shift_detected'):
        print(f"🔄 {intent_shift.get('message')}")
    
    # Generate follow-up actions (with intent shift context)
    touchpoint_dict = touchpoint.to_dict()
    actions_data = generate_followup_actions(lead_dict, touchpoint_dict, analysis, intent_shift)
    
    actions = []
    for action_data in actions_data:
        followup = FollowUpAction(
            lead_id=lead_id,
            touchpoint_id=touchpoint.id,
            action_type=action_data.get("action_type"),
            priority=action_data.get("priority"),
            content=action_data.get("content"),
            reasoning=action_data.get("reasoning"),
            timing=action_data.get("timing"),
            status="pending"
        )
        db.add(followup)
        actions.append(followup)
    
    db.commit()
    
    print(f"✅ Generated {len(actions)} follow-up actions")
    
    return {
        "touchpoint": touchpoint.to_dict(),
        "analysis": analysis,
        "intent_shift": intent_shift,
        "recommended_actions": [action.to_dict() for action in actions]
    }


@app.get("/api/leads/{lead_id}/touchpoints")
def get_touchpoints(lead_id: int, db: Session = Depends(get_db)):
    """
    Get all touchpoints for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    touchpoints = db.query(Touchpoint).filter(Touchpoint.lead_id == lead_id).order_by(Touchpoint.created_at.desc()).all()
    
    return {
        "lead": lead.to_dict(),
        "touchpoints": [t.to_dict() for t in touchpoints]
    }


@app.get("/api/leads/{lead_id}/actions")
def get_followup_actions(lead_id: int, db: Session = Depends(get_db)):
    """
    Get all follow-up actions for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    actions = db.query(FollowUpAction).filter(FollowUpAction.lead_id == lead_id).order_by(FollowUpAction.created_at.desc()).all()
    
    return {
        "lead": lead.to_dict(),
        "actions": [a.to_dict() for a in actions]
    }


@app.post("/api/followup/{action_id}/execute")
def execute_followup(action_id: int, db: Session = Depends(get_db)):
    """
    Execute a recommended follow-up action (send SMS, email, etc.)
    """
    action = db.query(FollowUpAction).filter(FollowUpAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    lead = db.query(Lead).filter(Lead.id == action.lead_id).first()
    
    result = None
    
    print(f"\n🚀 Executing {action.action_type} action for {lead.full_name}")
    
    if action.action_type == "sms":
        result = send_sms(lead.phone, action.content)
    
    elif action.action_type == "email":
        # Extract subject from content (first line or generate one)
        lines = action.content.split('\n')
        
        # Check if first line has "Subject:" prefix
        if lines[0].lower().startswith("subject:"):
            subject = lines[0].replace("Subject:", "").replace("subject:", "").strip()
            body = '\n'.join(lines[1:]).strip()
        else:
            # If no subject line, use a default and treat all content as body
            subject = f"Follow-up: {lead.insurance_type} Insurance Quote"
            body = action.content.strip()
        
        result = send_email(lead.email, subject, body)
    
    elif action.action_type == "call":
        # For call scripts, just mark as ready
        result = {"status": "script_ready", "message": "Call script prepared"}
    
    elif action.action_type == "escalate":
        # Create escalation record
        result = {"escalated": True, "to": "human_agent", "reason": action.reasoning}
    
    # Mark action as completed
    action.status = "completed"
    action.completed_at = datetime.utcnow()
    db.commit()
    
    print(f"✅ Action executed successfully")
    
    return {
        "action": action.to_dict(),
        "result": result
    }


# PHASE 3: LIFELINE RETENTION AGENT ENDPOINTS

class LifeEventCreate(BaseModel):
    event_type: str
    event_date: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = "manual"


class CustomerResponse(BaseModel):
    response_text: str


@app.post("/api/leads/{lead_id}/life-event")
def add_life_event(lead_id: int, event_data: LifeEventCreate, db: Session = Depends(get_db)):
    """
    Add a life event and trigger automated retention action
    """
    # Get lead
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Parse event date
    from datetime import datetime
    event_date = datetime.fromisoformat(event_data.event_date) if event_data.event_date else datetime.utcnow()
    
    # Create life event
    life_event = LifeEvent(
        lead_id=lead_id,
        event_type=event_data.event_type,
        event_date=event_date,
        description=event_data.description,
        source=event_data.source
    )
    
    db.add(life_event)
    db.commit()
    db.refresh(life_event)
    
    print(f"\n🎉 Life event detected: {event_data.event_type} for {lead.full_name}")
    
    # Calculate policy health score
    touchpoints = db.query(Touchpoint).filter(Touchpoint.lead_id == lead_id).all()
    life_events = db.query(LifeEvent).filter(LifeEvent.lead_id == lead_id).all()
    
    policy_health_data = calculate_policy_health_score(
        lead.to_dict(),
        [t.to_dict() for t in touchpoints],
        [e.to_dict() for e in life_events]
    )
    
    # Save policy health
    policy_health = PolicyHealth(
        lead_id=lead_id,
        health_score=policy_health_data['health_score'],
        churn_risk=policy_health_data['churn_risk'],
        churn_probability=policy_health_data.get('churn_probability'),
        days_to_predicted_churn=policy_health_data.get('days_to_predicted_churn'),
        engagement_score=policy_health_data.get('engagement_score'),
        satisfaction_score=policy_health_data.get('satisfaction_score'),
        usage_score=policy_health_data.get('usage_score'),
        payment_score=policy_health_data.get('payment_score'),
        retention_actions=policy_health_data.get('retention_actions'),
        reasoning=policy_health_data.get('reasoning'),
        priority=policy_health_data.get('priority')
    )
    
    db.add(policy_health)
    db.commit()
    db.refresh(policy_health)
    
    print(f"📊 Policy Health Score: {policy_health_data['health_score']} ({policy_health_data['churn_risk']} risk)")
    
    # Generate retention action
    action_data = generate_retention_action(
        life_event.to_dict(),
        lead.to_dict(),
        policy_health_data
    )
    
    # Update life event with action details
    life_event.action_taken = True
    life_event.action_type = action_data['action_type']
    life_event.action_content = action_data['content']
    life_event.opportunity_type = action_data.get('opportunity_type', 'upsell')
    life_event.recommended_product = action_data.get('recommended_product')
    life_event.estimated_value = action_data.get('estimated_value')
    life_event.outcome = "pending"
    
    db.commit()
    db.refresh(life_event)
    
    # Send SMS automatically
    if action_data['action_type'] == 'sms':
        sms_result = send_sms(lead.phone, action_data['content'])
        print(f"📱 SMS sent to {lead.full_name}")
    
    print(f"✅ Retention action triggered")
    
    return {
        "life_event": life_event.to_dict(),
        "policy_health": policy_health.to_dict(),
        "action": action_data,
        "sms_sent": True
    }


@app.get("/api/leads/{lead_id}/life-events")
def get_life_events(lead_id: int, db: Session = Depends(get_db)):
    """
    Get all life events for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    life_events = db.query(LifeEvent).filter(LifeEvent.lead_id == lead_id).order_by(LifeEvent.created_at.desc()).all()
    
    return {
        "lead": lead.to_dict(),
        "life_events": [e.to_dict() for e in life_events]
    }


@app.get("/api/life-events")
def get_all_life_events(db: Session = Depends(get_db)):
    """
    Get all life events across all leads
    """
    life_events = db.query(LifeEvent).order_by(LifeEvent.created_at.desc()).all()
    
    # Enrich with lead data
    enriched_events = []
    for event in life_events:
        event_dict = event.to_dict()
        lead = db.query(Lead).filter(Lead.id == event.lead_id).first()
        if lead:
            event_dict['lead_name'] = lead.full_name
            event_dict['lead_email'] = lead.email
            event_dict['lead_phone'] = lead.phone
        enriched_events.append(event_dict)
    
    return {"life_events": enriched_events}


@app.get("/api/leads/{lead_id}/policy-health")
def get_policy_health(lead_id: int, db: Session = Depends(get_db)):
    """
    Get current policy health score for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Get most recent policy health
    policy_health = db.query(PolicyHealth).filter(
        PolicyHealth.lead_id == lead_id
    ).order_by(PolicyHealth.calculated_at.desc()).first()
    
    if not policy_health:
        # Calculate if doesn't exist
        touchpoints = db.query(Touchpoint).filter(Touchpoint.lead_id == lead_id).all()
        life_events = db.query(LifeEvent).filter(LifeEvent.lead_id == lead_id).all()
        
        policy_health_data = calculate_policy_health_score(
            lead.to_dict(),
            [t.to_dict() for t in touchpoints],
            [e.to_dict() for e in life_events]
        )
        
        return {
            "lead": lead.to_dict(),
            "policy_health": policy_health_data
        }
    
    return {
        "lead": lead.to_dict(),
        "policy_health": policy_health.to_dict()
    }


@app.post("/api/life-events/{event_id}/respond")
def respond_to_life_event(event_id: int, response_data: CustomerResponse, db: Session = Depends(get_db)):
    """
    Process customer response to life event outreach
    """
    life_event = db.query(LifeEvent).filter(LifeEvent.id == event_id).first()
    if not life_event:
        raise HTTPException(status_code=404, detail="Life event not found")
    
    lead = db.query(Lead).filter(Lead.id == life_event.lead_id).first()
    
    print(f"\n💬 Customer response received: {response_data.response_text}")
    
    # Process response
    response_analysis = process_customer_response(
        response_data.response_text,
        event_id,
        lead.to_dict()
    )
    
    # Update life event
    life_event.customer_response = response_data.response_text
    life_event.outcome = response_analysis['outcome']
    
    db.commit()
    db.refresh(life_event)
    
    # Send auto-response
    if response_analysis.get('response_message'):
        send_sms(lead.phone, response_analysis['response_message'])
        print(f"📱 Auto-response sent")
    
    # ALWAYS recalculate policy health based on customer response
    print(f"\n🔄 Recalculating policy health based on customer response...")
    
    touchpoints = db.query(Touchpoint).filter(Touchpoint.lead_id == lead.id).all()
    life_events = db.query(LifeEvent).filter(LifeEvent.lead_id == lead.id).all()
    
    # Get base policy health from AI
    policy_health_data = calculate_policy_health_score(
        lead.to_dict(),
        [t.to_dict() for t in touchpoints],
        [e.to_dict() for e in life_events]
    )
    
    # Adjust score based on response outcome
    if response_analysis['outcome'] == 'converted':
        # POSITIVE RESPONSE: Boost score significantly
        policy_health_data['health_score'] = min(95, policy_health_data['health_score'] + 20)
        policy_health_data['churn_risk'] = 'low'
        policy_health_data['churn_probability'] = 5
        policy_health_data['reasoning'] = f"Customer converted on life event opportunity. Engagement increased, satisfaction high. {policy_health_data.get('reasoning', '')}"
        policy_health_data['retention_actions'] = [
            "Continue excellent service",
            "Monitor for additional upsell opportunities",
            "Celebrate conversion with thank you message"
        ]
        policy_health_data['priority'] = 'low'
        print(f"✅ POSITIVE RESPONSE: Policy health improved to {policy_health_data['health_score']}")
        
    elif response_analysis['outcome'] == 'declined':
        # NEGATIVE RESPONSE: Lower score, increase follow-up actions
        policy_health_data['health_score'] = max(40, policy_health_data['health_score'] - 15)
        policy_health_data['churn_risk'] = 'high' if policy_health_data['health_score'] < 50 else 'medium'
        policy_health_data['churn_probability'] = min(70, policy_health_data.get('churn_probability', 35) + 20)
        policy_health_data['reasoning'] = f"Customer declined life event opportunity. May indicate dissatisfaction or budget concerns. Requires careful follow-up. {policy_health_data.get('reasoning', '')}"
        policy_health_data['retention_actions'] = [
            "Schedule follow-up call to understand concerns",
            "Offer alternative coverage options at lower price points",
            "Send educational content about product value",
            "Check in again in 30 days with different approach",
            "Monitor for any signs of policy cancellation"
        ]
        policy_health_data['priority'] = 'high'
        print(f"⚠️ NEGATIVE RESPONSE: Policy health decreased to {policy_health_data['health_score']}")
        
    elif response_analysis['outcome'] == 'pending':
        # CURIOUS/UNCLEAR: Slight adjustment, add nurture actions
        policy_health_data['health_score'] = max(50, policy_health_data['health_score'] - 5)
        policy_health_data['retention_actions'] = [
            "Send detailed product information",
            "Provide customer testimonials and case studies",
            "Offer to schedule consultation call",
            "Follow up in 7 days if no response"
        ]
        policy_health_data['priority'] = 'medium'
        print(f"📊 PENDING RESPONSE: Policy health adjusted to {policy_health_data['health_score']}")
    
    # Save updated policy health
    policy_health = PolicyHealth(
        lead_id=lead.id,
        health_score=policy_health_data['health_score'],
        churn_risk=policy_health_data['churn_risk'],
        churn_probability=policy_health_data.get('churn_probability', 35),
        days_to_predicted_churn=policy_health_data.get('days_to_predicted_churn', 90),
        engagement_score=policy_health_data.get('engagement_score'),
        satisfaction_score=policy_health_data.get('satisfaction_score'),
        usage_score=policy_health_data.get('usage_score'),
        payment_score=policy_health_data.get('payment_score'),
        retention_actions=policy_health_data.get('retention_actions'),
        reasoning=policy_health_data.get('reasoning'),
        priority=policy_health_data.get('priority', 'medium')
    )
    
    db.add(policy_health)
    db.commit()
    db.refresh(policy_health)
    
    print(f"💾 Policy health saved: {policy_health.health_score} ({policy_health.churn_risk} risk)")
    
    return {
        "life_event": life_event.to_dict(),
        "response_analysis": response_analysis,
        "auto_response_sent": True,
        "policy_health": policy_health.to_dict(),
        "follow_up_actions": policy_health_data.get('retention_actions', [])
    }


# OCCASIONS ENGINE ENDPOINTS

class OccasionCreate(BaseModel):
    occasion_type: str
    occasion_date: Optional[str] = None
    description: Optional[str] = None


@app.post("/api/leads/{lead_id}/occasion")
def trigger_occasion(lead_id: int, occasion_data: OccasionCreate, db: Session = Depends(get_db)):
    """
    Trigger an occasion and send automated message
    """
    # Get lead
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Parse occasion date
    from datetime import datetime
    occasion_date = datetime.fromisoformat(occasion_data.occasion_date) if occasion_data.occasion_date else datetime.utcnow()
    
    print(f"\n🎉 Occasion triggered: {occasion_data.occasion_type} for {lead.full_name}")
    
    # Generate occasion action
    action_data = generate_occasion_action(
        occasion_data.occasion_type,
        lead.to_dict(),
        {"date": occasion_date}
    )
    
    # Create occasion record
    occasion = Occasion(
        lead_id=lead_id,
        occasion_type=occasion_data.occasion_type,
        occasion_date=occasion_date,
        description=occasion_data.description,
        offer_type=action_data.get('offer_type'),
        offer_value=action_data.get('offer_value'),
        offer_description=action_data.get('offer_description'),
        action_taken=True,
        action_type=action_data['action_type'],
        action_content=action_data['content'],
        outcome="pending"
    )
    
    db.add(occasion)
    db.commit()
    db.refresh(occasion)
    
    # Send SMS (always use SMS for consistency with life events)
    send_sms(lead.phone, action_data['content'])
    print(f"📱 SMS sent to {lead.full_name}")
    
    # Calculate policy health after occasion
    touchpoints = db.query(Touchpoint).filter(Touchpoint.lead_id == lead.id).all()
    life_events = db.query(LifeEvent).filter(LifeEvent.lead_id == lead.id).all()
    
    policy_health_data = calculate_policy_health_score(
        lead.to_dict(),
        [t.to_dict() for t in touchpoints],
        [e.to_dict() for e in life_events]
    )
    
    print(f"✅ Occasion action triggered")
    
    return {
        "occasion": occasion.to_dict(),
        "action": action_data,
        "message_sent": True,
        "policy_health": policy_health_data
    }


@app.get("/api/leads/{lead_id}/occasions")
def get_occasions(lead_id: int, db: Session = Depends(get_db)):
    """
    Get all occasions for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    occasions = db.query(Occasion).filter(Occasion.lead_id == lead_id).order_by(Occasion.created_at.desc()).all()
    
    return {
        "lead": lead.to_dict(),
        "occasions": [o.to_dict() for o in occasions]
    }


@app.get("/api/occasions")
def get_all_occasions(db: Session = Depends(get_db)):
    """
    Get all occasions across all leads
    """
    occasions = db.query(Occasion).order_by(Occasion.created_at.desc()).all()
    
    # Enrich with lead data
    enriched_occasions = []
    for occasion in occasions:
        occasion_dict = occasion.to_dict()
        lead = db.query(Lead).filter(Lead.id == occasion.lead_id).first()
        if lead:
            occasion_dict['lead_name'] = lead.full_name
            occasion_dict['lead_email'] = lead.email
            occasion_dict['lead_phone'] = lead.phone
        enriched_occasions.append(occasion_dict)
    
    return {"occasions": enriched_occasions}


@app.post("/api/occasions/{occasion_id}/respond")
def respond_to_occasion(occasion_id: int, response_data: CustomerResponse, db: Session = Depends(get_db)):
    """
    Process customer response to occasion outreach
    """
    occasion = db.query(Occasion).filter(Occasion.id == occasion_id).first()
    if not occasion:
        raise HTTPException(status_code=404, detail="Occasion not found")
    
    lead = db.query(Lead).filter(Lead.id == occasion.lead_id).first()
    
    print(f"\n💬 Customer response to occasion: {response_data.response_text}")
    
    # Simple response processing
    response_lower = response_data.response_text.lower()
    
    if any(word in response_lower for word in ['yes', 'thanks', 'great', 'awesome', 'appreciate']):
        outcome = "accepted"
        response_message = f"You're so welcome, {lead.full_name.split()[0]}! We're grateful to have you. Enjoy your gift! 🎉"
    elif any(word in response_lower for word in ['no', 'not interested']):
        outcome = "declined"
        response_message = f"No worries at all, {lead.full_name.split()[0]}! The offer is always here if you change your mind. Have a great day! 😊"
    else:
        outcome = "pending"
        response_message = f"Thanks for your response, {lead.full_name.split()[0]}! Let me know if you have any questions. I'm here to help! 😊"
    
    # Update occasion
    occasion.customer_response = response_data.response_text
    occasion.outcome = outcome
    
    db.commit()
    db.refresh(occasion)
    
    # Send auto-response
    send_sms(lead.phone, response_message)
    print(f"📱 Auto-response sent")
    
    # ALWAYS recalculate policy health based on customer response
    print(f"\n🔄 Recalculating policy health based on occasion response...")
    
    touchpoints = db.query(Touchpoint).filter(Touchpoint.lead_id == lead.id).all()
    life_events = db.query(LifeEvent).filter(LifeEvent.lead_id == lead.id).all()
    
    # Get base policy health from AI
    policy_health_data = calculate_policy_health_score(
        lead.to_dict(),
        [t.to_dict() for t in touchpoints],
        [e.to_dict() for e in life_events]
    )
    
    # Adjust score based on response outcome
    if outcome == 'accepted':
        # POSITIVE RESPONSE: Boost score for engagement
        policy_health_data['health_score'] = min(95, policy_health_data['health_score'] + 10)
        policy_health_data['churn_risk'] = 'low'
        policy_health_data['churn_probability'] = 10
        policy_health_data['reasoning'] = f"Customer engaged positively with occasion. Loyalty strengthened. {policy_health_data.get('reasoning', '')}"
        policy_health_data['retention_actions'] = [
            "Continue celebrating milestones",
            "Monitor for additional engagement opportunities",
            "Maintain excellent service"
        ]
        policy_health_data['priority'] = 'low'
        print(f"✅ POSITIVE RESPONSE: Policy health improved to {policy_health_data['health_score']}")
        
    elif outcome == 'declined':
        # NEGATIVE RESPONSE: Slight decrease
        policy_health_data['health_score'] = max(50, policy_health_data['health_score'] - 5)
        policy_health_data['retention_actions'] = [
            "Try different engagement approach",
            "Monitor customer satisfaction",
            "Check in with personalized message"
        ]
        policy_health_data['priority'] = 'medium'
        print(f"⚠️ NEGATIVE RESPONSE: Policy health adjusted to {policy_health_data['health_score']}")
    
    # Save updated policy health
    policy_health = PolicyHealth(
        lead_id=lead.id,
        health_score=policy_health_data['health_score'],
        churn_risk=policy_health_data['churn_risk'],
        churn_probability=policy_health_data.get('churn_probability', 35),
        days_to_predicted_churn=policy_health_data.get('days_to_predicted_churn', 90),
        engagement_score=policy_health_data.get('engagement_score'),
        satisfaction_score=policy_health_data.get('satisfaction_score'),
        usage_score=policy_health_data.get('usage_score'),
        payment_score=policy_health_data.get('payment_score'),
        retention_actions=policy_health_data.get('retention_actions'),
        reasoning=policy_health_data.get('reasoning'),
        priority=policy_health_data.get('priority', 'medium')
    )
    
    db.add(policy_health)
    db.commit()
    db.refresh(policy_health)
    
    print(f"💾 Policy health saved: {policy_health.health_score} ({policy_health.churn_risk} risk)")
    
    return {
        "occasion": occasion.to_dict(),
        "outcome": outcome,
        "auto_response_sent": True,
        "policy_health": policy_health.to_dict(),
        "follow_up_actions": policy_health_data.get('retention_actions', [])
    }


@app.get("/api/leads/{lead_id}/detect-occasions")
def detect_lead_occasions(lead_id: int, db: Session = Depends(get_db)):
    """
    Detect upcoming occasions for a lead
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    occasions = detect_occasions(lead.to_dict())
    
    return {
        "lead": lead.to_dict(),
        "detected_occasions": occasions
    }


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
