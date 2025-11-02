# 📊 POLICY HEALTH SCORE - HOW IT WORKS

## 🎯 What is Policy Health Score?

A **0-100 score** that predicts how likely a customer is to churn (cancel their policy) in the next 90 days.

---

## 🧮 How We Calculate It

### **Current Implementation (Demo Mode):**

Located in: `backend/app/retention_engine.py` → `calculate_policy_health_score()`

```python
def calculate_policy_health_score(lead_data, touchpoints, life_events):
    # Check if customer has unaddressed life events
    has_life_event = life_events and len(life_events) > 0
    recent_touchpoints = touchpoints and len(touchpoints) > 0
    
    # Lower score if there's an unaddressed life event
    base_score = 75 if not has_life_event else 65
    
    return {
        "health_score": base_score,
        "churn_risk": "medium" if base_score < 70 else "low",
        "churn_probability": 35 if base_score < 70 else 15,
        "days_to_predicted_churn": 90,
        "engagement_score": 70,
        "satisfaction_score": 80,
        "usage_score": 75,
        "payment_score": 95
    }
```

### **Logic:**
1. **Base Score = 75** (healthy customer)
2. **If life event detected** → Score drops to **65** (needs attention)
3. **If customer converts** → Score improves to **85-95** (very healthy)

---

## 📈 Score Components

### **1. Engagement Score (0-100)**
**What it measures:** How actively the customer interacts with us

**Factors:**
- App usage frequency
- Response rate to communications
- Portal logins
- Document views

**Example:**
- High engagement (90): Logs in weekly, responds to emails
- Low engagement (40): Never logs in, ignores communications

---

### **2. Satisfaction Score (0-100)**
**What it measures:** Customer happiness with service

**Factors:**
- Support call sentiment
- Survey responses (NPS, CSAT)
- Complaint history
- Resolution time

**Example:**
- High satisfaction (85): Positive reviews, no complaints
- Low satisfaction (50): Multiple complaints, negative feedback

---

### **3. Usage Score (0-100)**
**What it measures:** How well they're using their policy

**Factors:**
- Claims filed (too many = risk, zero = good)
- Policy utilization
- Feature adoption
- Coverage adequacy

**Example:**
- Good usage (80): No claims, adequate coverage
- Poor usage (45): Multiple claims, underinsured

---

### **4. Payment Score (0-100)**
**What it measures:** Payment reliability

**Factors:**
- On-time payment history
- Payment method (auto-pay = better)
- Past due amounts
- Payment failures

**Example:**
- Excellent payment (95): Auto-pay, never late
- Poor payment (60): Frequently late, manual payments

---

## 🎯 Churn Risk Levels

### **Low Risk (80-100)**
- **Churn Probability:** 5-15%
- **Action:** Maintain relationship, celebrate milestones
- **Color:** 🟢 Green

### **Medium Risk (50-79)**
- **Churn Probability:** 20-40%
- **Action:** Proactive engagement, address concerns
- **Color:** 🟡 Yellow

### **High Risk (0-49)**
- **Churn Probability:** 50-80%
- **Action:** Immediate intervention, retention offers
- **Color:** 🔴 Red

---

## 🔮 90-Day Churn Prediction

### **How It Works:**

**Formula (Simplified):**
```
Churn Probability = 100 - (
    Engagement Score × 0.25 +
    Satisfaction Score × 0.30 +
    Usage Score × 0.20 +
    Payment Score × 0.25
)
```

**Example Calculation:**
```
Customer: Kinjal Chatterjee
- Engagement: 70
- Satisfaction: 80
- Usage: 75
- Payment: 95

Health Score = (70×0.25 + 80×0.30 + 75×0.20 + 95×0.25)
             = (17.5 + 24 + 15 + 23.75)
             = 80.25 → 80

Churn Risk = Low (80 > 70)
Churn Probability = 15%
Days to Churn = 90 days
```

---

## 📊 Real-World Implementation

### **Data Sources Needed:**

1. **CRM Data:**
   - Last login date
   - Email open rates
   - Support ticket history

2. **Payment System:**
   - Payment history
   - Auto-pay status
   - Late payment count

3. **Policy System:**
   - Claims history
   - Coverage changes
   - Policy age

4. **Communication Platform:**
   - SMS/Email responses
   - Sentiment analysis
   - Engagement metrics

---

## 🚀 How We Use It

### **Scenario 1: Life Event Detected**
```
Before: Health Score = 75 (Low Risk)
Event: New baby detected
After: Health Score = 65 (Medium Risk)
Action: Send empathetic upsell offer
Result: Customer converts
New Score: 85 (Low Risk)
```

### **Scenario 2: No Engagement**
```
Current: Health Score = 45 (High Risk)
Reason: No logins in 60 days, 2 late payments
Action: Urgent retention campaign
Offer: Loyalty discount + personal call
Result: Customer re-engages
New Score: 70 (Medium Risk)
```

### **Scenario 3: Perfect Customer**
```
Current: Health Score = 95 (Low Risk)
Reason: Auto-pay, no claims, high engagement
Action: Celebrate anniversary, offer referral bonus
Result: Customer refers friend
New Score: 98 (Excellent)
```

---

## 🎯 Improvement After Conversion

### **When Customer Accepts Upsell:**

```python
# In main.py - respond_to_life_event()
if response_analysis['outcome'] == 'converted':
    # Recalculate with improved metrics
    policy_health_data['health_score'] = min(95, base_score + 20)
    policy_health_data['churn_risk'] = 'low'
    policy_health_data['churn_probability'] = 5
```

**Logic:**
- Customer showed engagement → +20 points
- Purchased additional coverage → Lower churn risk
- Positive interaction → Improved satisfaction

**Example:**
- Before: 65 (Medium Risk, 35% churn)
- After: 85 (Low Risk, 5% churn)
- Improvement: +20 points, -30% churn probability

---

## 🔄 Continuous Updates

### **When to Recalculate:**

1. **After every touchpoint** (call, email, SMS)
2. **After payment** (on-time or late)
3. **After life event** (detected or resolved)
4. **Monthly** (scheduled batch update)
5. **After claim** (filed or resolved)

### **Score Decay:**
- Scores naturally decay over time without engagement
- -1 point per week of no interaction
- Prevents stale "healthy" scores

---

## 📈 Advanced Features (Future)

### **Machine Learning Model:**
```python
from sklearn.ensemble import RandomForestClassifier

# Train on historical data
features = [
    engagement_score,
    satisfaction_score,
    usage_score,
    payment_score,
    policy_age_days,
    claims_count,
    late_payments,
    support_tickets,
    life_events_count
]

model.predict_proba(features)  # Returns churn probability
```

### **Predictive Signals:**
- Sudden drop in engagement
- Competitor research detected
- Life event + no action
- Payment method change
- Coverage decrease request

---

## ✅ Current Demo Implementation

**What's Working:**
- ✅ Base score calculation
- ✅ Life event impact
- ✅ Conversion improvement
- ✅ Churn risk categorization
- ✅ 90-day prediction window

**What's Simulated:**
- Engagement score (fixed at 70)
- Satisfaction score (fixed at 80)
- Usage score (fixed at 75)
- Payment score (fixed at 95)

**For Production:**
- Connect to real CRM data
- Implement ML model
- Add historical analysis
- Enable continuous updates
- Track score changes over time

---

## 🎯 Summary

**Policy Health Score = Predictive indicator of customer churn**

**Components:**
- 25% Engagement
- 30% Satisfaction
- 20% Usage
- 25% Payment

**Prediction:**
- 90-day churn probability
- Risk level (Low/Medium/High)
- Recommended actions

**Impact:**
- Life events lower score (need attention)
- Conversions raise score (engagement)
- No interaction decays score (disengagement)

**Goal:**
- Keep all customers above 70 (Low Risk)
- Intervene when score drops below 70
- Celebrate when score improves

---

**The system works proactively to prevent churn before it happens!** 🎯
