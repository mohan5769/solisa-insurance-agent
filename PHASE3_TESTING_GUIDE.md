# 🎯 PHASE 3: LIFELINE RETENTION AGENT - TESTING GUIDE

## 📋 Overview

Phase 3 consists of **TWO SEPARATE AI AGENTS** with distinct functionalities:

### 1. **LIFE EVENT ENGINE** 🍼
**Purpose:** Detect major life changes and trigger proactive upsell/retention actions

**Triggers:**
- New baby → Umbrella insurance ($25/mo)
- Home purchase → Bundle discount ($150/mo)
- Teen driver → Auto upgrade ($75/mo)
- Job change → Policy review

**Functionality:**
- Detects life events
- Calculates policy health score (0-100)
- Predicts churn risk
- Sends empathetic, personalized SMS
- Processes customer responses
- Auto-closes deals on positive responses

---

### 2. **OCCASIONS ENGINE** 🎉
**Purpose:** Celebrate special dates and milestones to build loyalty

**Triggers:**
- Policy anniversary → Loyalty discount ($50 off)
- Birthday → Free roadside assistance (1 month)
- Policy renewal → Proactive review offer
- Usage milestone → Pay-per-mile savings ($340/year)
- Holiday season → Travel safety reminder

**Functionality:**
- Detects anniversaries and special dates
- Generates celebration messages
- Offers loyalty rewards
- Identifies usage-based savings opportunities
- Builds long-term customer relationships

---

## 🧪 TESTING FLOW

### **SETUP**
1. Open http://localhost:3000
2. Click **"Retention"** in navigation
3. Select a customer (e.g., Kinjal Chatterjee)

---

## TEST 1: LIFE EVENT ENGINE - New Baby 🍼

### **Step 1: Trigger Life Event**
1. Select **Kinjal** from customer list
2. Click **"New Baby"** button (pink card)
3. ✅ **Expected:** Toast notification appears

### **Step 2: Observe AI Actions**
**Backend Console Output:**
```
🎉 Life event detected: new_baby for Kinjal Chatterjee
📊 Policy Health Score: 65 (medium risk)
📱 SMS sent to Kinjal Chatterjee
✅ Retention action triggered
```

**SMS Content (Empathetic):**
```
🎉 Congratulations on your new baby, Kinjal! What an exciting time 
for your family. As you settle into this new chapter, I wanted to 
share something that might give you peace of mind - many new parents 
find umbrella insurance helpful for protecting their growing family's 
future. No pressure at all, but if you'd like to learn more, I'm here. 
Wishing you and your little one all the best! 💙
```

### **Step 3: Check Policy Health**
**Left Sidebar Shows:**
- Health Score: **65** (yellow/medium risk)
- Churn Risk: **MEDIUM**
- Engagement: 70
- Satisfaction: 80
- Usage: 75
- Payment: 95
- Predicted churn: **90 days**

### **Step 4: Simulate Customer Response**
1. In the life events list, find the "New Baby" event
2. Click **"Simulate Customer Response"**
3. Type: `"Yes, let's do it!"`
4. Click **"Send Response"**

### **Step 5: Observe AI Auto-Close**
**Backend Processing:**
```
💬 Customer response received: Yes, let's do it!
📱 Auto-response sent
✅ Upsell successful! Policy health improved to 85
```

**Auto-Response (Warm & Grateful):**
```
That's wonderful, Kinjal! I'm so glad this feels right for you and 
your family. I'll get everything set up for you today, and you'll 
receive a confirmation email with all the details shortly. Thank you 
for trusting us with your family's protection. If you have any 
questions at all, I'm always here. 💙
```

**Policy Health Updates:**
- Health Score: **65 → 85** (improved!)
- Churn Risk: **MEDIUM → LOW**
- Event Outcome: **converted**
- Revenue: **+$25/month**

---

## TEST 2: LIFE EVENT ENGINE - Other Events

### **Home Purchase** 🏠
1. Click "Home Purchase" button
2. SMS: Congratulations message + bundle offer
3. Potential savings: **$150/mo**

### **Teen Driver** 🚗
1. Click "Teen Driver" button
2. SMS: Empathetic message acknowledging parent's feelings
3. Mentions good student discounts
4. Potential revenue: **+$75/mo**

### **Job Change** 💼
1. Click "Job Change" button
2. SMS: Congratulations + policy review offer
3. No pressure, just checking in

---

## TEST 3: OCCASIONS ENGINE - Policy Anniversary 🎉

### **Step 1: Trigger Occasion**
1. Select a customer
2. In the **Occasions** tab (if implemented), click **"Policy Anniversary"**
3. Or use API directly:

**API Call:**
```bash
curl -X POST http://localhost:8000/api/leads/1/occasion \
  -H "Content-Type: application/json" \
  -d '{
    "occasion_type": "policy_anniversary",
    "description": "2 year anniversary"
  }'
```

### **Step 2: Observe Celebration Message**
**SMS Content:**
```
🎉 Happy 2-year anniversary with Solisa, Kinjal! We're so grateful 
to have you as part of our family. As a thank you for your loyalty, 
here's a special gift: $50 off your next renewal! You've been an 
amazing customer, and we look forward to many more years together. 
Cheers to you! 🥳
```

**Offer Details:**
- Type: Loyalty discount
- Value: **$50 off**
- No action required (gift!)

### **Step 3: Customer Response**
1. Customer replies: `"Thanks so much!"`
2. AI responds: `"You're so welcome, Kinjal! We're grateful to have you. Enjoy your gift! 🎉"`
3. Outcome: **accepted**

---

## TEST 4: OCCASIONS ENGINE - Birthday 🎂

### **Trigger:**
```bash
curl -X POST http://localhost:8000/api/leads/1/occasion \
  -H "Content-Type: application/json" \
  -d '{
    "occasion_type": "birthday",
    "description": "Customer birthday"
  }'
```

### **SMS:**
```
🎂 Happy Birthday, Kinjal! We hope your day is filled with joy and 
celebration. As a birthday gift from us, enjoy free roadside assistance 
for the entire month! It's our way of saying thank you for being such 
a valued customer. Have a wonderful day! 🎈
```

**Offer:**
- Free roadside assistance
- Duration: 1 month
- Value: ~$10

---

## TEST 5: OCCASIONS ENGINE - Usage-Based Savings 🚗

### **Trigger:**
```bash
curl -X POST http://localhost:8000/api/leads/1/occasion \
  -H "Content-Type: application/json" \
  -d '{
    "occasion_type": "usage_based_savings",
    "description": "Low mileage detected"
  }'
```

### **SMS:**
```
Hi Kinjal, I noticed something interesting - you're driving about 40% 
less than the average policyholder! That's great for the environment 
and your wallet. Have you considered switching to our pay-per-mile plan? 
Based on your driving, you could save around $340 per year. Want to 
learn more? No obligation, just thought you'd like to know! 🚗
```

**Offer:**
- Pay-per-mile plan
- Potential savings: **$340/year**
- Requires action: Yes (plan switch)

---

## 🔍 KEY DIFFERENCES BETWEEN ENGINES

### **LIFE EVENT ENGINE**
- **Reactive:** Responds to major life changes
- **Focus:** Upsell & retention
- **Urgency:** High (life events are time-sensitive)
- **Policy Health:** Tracks and predicts churn
- **Tone:** Empathetic, understanding, supportive
- **Goal:** Prevent churn + increase coverage

### **OCCASIONS ENGINE**
- **Proactive:** Celebrates milestones
- **Focus:** Loyalty & engagement
- **Urgency:** Low (relationship building)
- **Policy Health:** Not directly tracked
- **Tone:** Celebratory, grateful, warm
- **Goal:** Build long-term relationships + delight customers

---

## 📊 SUCCESS METRICS

### **Life Event Engine:**
- ✅ Policy health score calculated
- ✅ Churn risk identified
- ✅ Empathetic SMS sent
- ✅ Customer responds positively
- ✅ Deal auto-closed
- ✅ Policy health improves
- ✅ Revenue tracked

### **Occasions Engine:**
- ✅ Occasion detected/triggered
- ✅ Celebration message sent
- ✅ Offer delivered
- ✅ Customer feels valued
- ✅ Loyalty strengthened
- ✅ No pressure applied

---

## 🎯 DEMO SCRIPT

### **For Investors/Stakeholders:**

**"Let me show you our two AI agents working together..."**

**1. Life Event Engine (2 min)**
- "Kinjal just had a baby. Watch what happens..."
- Trigger event → Show SMS → Simulate response → Show auto-close
- "Policy health improved from 65 to 85. Deal closed automatically."

**2. Occasions Engine (1 min)**
- "It's also Kinjal's 2-year anniversary with us..."
- Trigger occasion → Show celebration SMS → Show loyalty offer
- "No sales pressure - just building relationships."

**3. Results (30 sec)**
- "Life Event: +$25/month revenue, prevented churn"
- "Occasion: Customer delighted, loyalty strengthened"
- "Both AI agents work 24/7, no human intervention needed"

---

## 🐛 TROUBLESHOOTING

### **Backend Not Running:**
```bash
cd backend/app && ../venv/bin/python main.py
```

### **Frontend Not Running:**
```bash
cd frontend && npm run dev
```

### **Database Issues:**
- Delete `backend/solisa.db`
- Restart backend (auto-creates tables)

### **SMS Not Sending:**
- Check DEMO_MODE=true in `.env`
- In demo mode, SMS are logged but not actually sent

---

## ✅ COMPLETION CHECKLIST

- [ ] Life Event Engine tested (all 4 events)
- [ ] Policy health score calculated
- [ ] Customer response processed
- [ ] Deal auto-closed
- [ ] Occasions Engine tested (3+ occasions)
- [ ] Celebration messages sent
- [ ] Loyalty offers delivered
- [ ] Both engines working independently
- [ ] Empathetic tone verified
- [ ] No pushy sales language

---

## 🚀 READY TO DEMO!

**Phase 3 is complete with TWO distinct AI agents:**
1. **Life Event Engine** - Proactive retention & upsell
2. **Occasions Engine** - Loyalty & celebration

Both work automatically, 24/7, with empathetic human-like communication! 🎉
