from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

try:
    from .database import Base
except ImportError:
    from database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)
    insurance_type = Column(String, nullable=False)
    current_provider = Column(String, nullable=True)
    
    # Enriched Data
    life_stage = Column(String, nullable=True)
    estimated_age_range = Column(String, nullable=True)
    pain_points = Column(JSON, nullable=True)
    estimated_savings = Column(Integer, nullable=True)
    renewal_date = Column(String, nullable=True)
    
    # Communication Status
    sms_sent = Column(Boolean, default=False)
    sms_sent_at = Column(DateTime, nullable=True)
    sms_content = Column(String, nullable=True)
    
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime, nullable=True)
    email_subject = Column(String, nullable=True)
    email_content = Column(String, nullable=True)
    
    # Conversion Tracking
    calendly_link = Column(String, nullable=True)
    booking_confirmed = Column(Boolean, default=False)
    booking_confirmed_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String, default="new")  # new, enriched, contacted, booked
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    touchpoints = relationship("Touchpoint", back_populates="lead")
    followup_actions = relationship("FollowUpAction", back_populates="lead")
    life_events = relationship("LifeEvent", back_populates="lead")
    policy_health_records = relationship("PolicyHealth", back_populates="lead")
    occasions = relationship("Occasion", back_populates="lead")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "insurance_type": self.insurance_type,
            "current_provider": self.current_provider,
            "life_stage": self.life_stage,
            "estimated_age_range": self.estimated_age_range,
            "pain_points": self.pain_points,
            "estimated_savings": self.estimated_savings,
            "renewal_date": self.renewal_date,
            "sms_sent": self.sms_sent,
            "sms_sent_at": self.sms_sent_at.isoformat() if self.sms_sent_at else None,
            "sms_content": self.sms_content,
            "email_sent": self.email_sent,
            "email_sent_at": self.email_sent_at.isoformat() if self.email_sent_at else None,
            "email_subject": self.email_subject,
            "email_content": self.email_content,
            "calendly_link": self.calendly_link,
            "booking_confirmed": self.booking_confirmed,
            "booking_confirmed_at": self.booking_confirmed_at.isoformat() if self.booking_confirmed_at else None,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Touchpoint(Base):
    """Track every interaction with a lead"""
    __tablename__ = "touchpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    
    # Touchpoint details
    type = Column(String, nullable=False)  # call, sms, email, note
    direction = Column(String, nullable=True)  # inbound, outbound
    content = Column(Text, nullable=False)  # transcript, message, note
    
    # AI Analysis
    sentiment = Column(String, nullable=True)  # positive, neutral, negative
    intent = Column(String, nullable=True)  # browsing, interested, ready, objection
    objections = Column(JSON, nullable=True)  # ["too expensive", "need to think"]
    key_points = Column(JSON, nullable=True)  # Important things mentioned
    urgency = Column(String, nullable=True)  # low, medium, high
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="touchpoints")
    followup_actions = relationship("FollowUpAction", back_populates="touchpoint")
    
    def to_dict(self):
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "type": self.type,
            "direction": self.direction,
            "content": self.content,
            "sentiment": self.sentiment,
            "intent": self.intent,
            "objections": self.objections,
            "key_points": self.key_points,
            "urgency": self.urgency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class FollowUpAction(Base):
    """AI-recommended next actions"""
    __tablename__ = "followup_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    touchpoint_id = Column(Integer, ForeignKey('touchpoints.id'), nullable=True)
    
    # Action details
    action_type = Column(String, nullable=False)  # sms, email, call, wait, escalate
    priority = Column(String, nullable=False)  # high, medium, low
    content = Column(Text, nullable=False)  # Generated message/script
    reasoning = Column(Text, nullable=True)  # Why this action
    timing = Column(String, nullable=True)  # immediate, 1hour, 1day
    
    # Status
    status = Column(String, default="pending")  # pending, completed, skipped
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="followup_actions")
    touchpoint = relationship("Touchpoint", back_populates="followup_actions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "touchpoint_id": self.touchpoint_id,
            "action_type": self.action_type,
            "priority": self.priority,
            "content": self.content,
            "reasoning": self.reasoning,
            "timing": self.timing,
            "status": self.status,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LifeEvent(Base):
    """Track life events for retention and upsell opportunities"""
    __tablename__ = "life_events"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    
    # Event details
    event_type = Column(String, nullable=False)  # new_baby, home_purchase, teen_driver, job_change, marriage, etc.
    event_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String, nullable=True)  # manual, social_media, customer_update, etc.
    
    # AI Analysis
    opportunity_type = Column(String, nullable=True)  # upsell, retention, cross_sell
    recommended_product = Column(String, nullable=True)  # umbrella, life, auto_upgrade, etc.
    estimated_value = Column(Integer, nullable=True)  # Monthly revenue potential
    
    # Action tracking
    action_taken = Column(Boolean, default=False)
    action_type = Column(String, nullable=True)  # sms, email, call
    action_content = Column(Text, nullable=True)
    customer_response = Column(Text, nullable=True)
    outcome = Column(String, nullable=True)  # converted, declined, pending, no_response
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="life_events")
    
    def to_dict(self):
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "event_type": self.event_type,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "description": self.description,
            "source": self.source,
            "opportunity_type": self.opportunity_type,
            "recommended_product": self.recommended_product,
            "estimated_value": self.estimated_value,
            "action_taken": self.action_taken,
            "action_type": self.action_type,
            "action_content": self.action_content,
            "customer_response": self.customer_response,
            "outcome": self.outcome,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PolicyHealth(Base):
    """Track policy health scores and churn predictions"""
    __tablename__ = "policy_health"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    
    # Health metrics
    health_score = Column(Integer, nullable=False)  # 0-100
    churn_risk = Column(String, nullable=False)  # low, medium, high
    churn_probability = Column(Integer, nullable=True)  # 0-100%
    days_to_predicted_churn = Column(Integer, nullable=True)
    
    # Contributing factors
    engagement_score = Column(Integer, nullable=True)  # How engaged is the customer
    satisfaction_score = Column(Integer, nullable=True)  # Customer satisfaction
    usage_score = Column(Integer, nullable=True)  # Policy utilization
    payment_score = Column(Integer, nullable=True)  # Payment history
    
    # Recommendations
    retention_actions = Column(JSON, nullable=True)  # List of recommended actions
    reasoning = Column(Text, nullable=True)  # AI reasoning for the score
    priority = Column(String, nullable=True)  # low, medium, high, critical
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="policy_health_records")
    
    def to_dict(self):
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "health_score": self.health_score,
            "churn_risk": self.churn_risk,
            "churn_probability": self.churn_probability,
            "days_to_predicted_churn": self.days_to_predicted_churn,
            "engagement_score": self.engagement_score,
            "satisfaction_score": self.satisfaction_score,
            "usage_score": self.usage_score,
            "payment_score": self.payment_score,
            "retention_actions": self.retention_actions,
            "reasoning": self.reasoning,
            "priority": self.priority,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
        }


class Occasion(Base):
    """Track occasions and special dates for customer engagement"""
    __tablename__ = "occasions"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    
    # Occasion details
    occasion_type = Column(String, nullable=False)  # policy_anniversary, birthday, renewal, holiday, usage_milestone
    occasion_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    
    # Offer details
    offer_type = Column(String, nullable=True)  # loyalty_discount, free_service, plan_switch, etc.
    offer_value = Column(Integer, nullable=True)  # Dollar value of offer
    offer_description = Column(Text, nullable=True)
    
    # Action tracking
    action_taken = Column(Boolean, default=False)
    action_type = Column(String, nullable=True)  # sms, email
    action_content = Column(Text, nullable=True)
    customer_response = Column(Text, nullable=True)
    outcome = Column(String, nullable=True)  # accepted, declined, pending, no_response
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lead = relationship("Lead", back_populates="occasions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "lead_id": self.lead_id,
            "occasion_type": self.occasion_type,
            "occasion_date": self.occasion_date.isoformat() if self.occasion_date else None,
            "description": self.description,
            "offer_type": self.offer_type,
            "offer_value": self.offer_value,
            "offer_description": self.offer_description,
            "action_taken": self.action_taken,
            "action_type": self.action_type,
            "action_content": self.action_content,
            "customer_response": self.customer_response,
            "outcome": self.outcome,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
