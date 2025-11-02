# Solisa AI SDR - Phase 1: AI Lead Gen + SDR Agent

## 🎯 Phase 1 Goal

**Transform website visitors into booked appointments in under 2 minutes**

### Input:
- Website visitor form submission
- Basic info: Name, Email, Phone, Insurance Type

### Output:
- Qualified, warm lead
- Booked appointment in Calendly

### Must Solve:
✅ Hyper-personalized outreach in seconds  
✅ Auto-enrich lead with life stage, current insurer, pain points  
✅ AI SDR books meeting via SMS + Email  
✅ 1-click Calendly booking  

### Demo Goal:
```
Visitor fills form 
→ AI sends SMS 
→ Prospect replies "yes" 
→ Meeting booked in Calendly 
→ All in < 2 mins
```

---

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd app
python main.py
```

Backend runs on **http://localhost:8000**

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on **http://localhost:3000**

---

## 🧪 Test Phase 1

1. Open http://localhost:3000
2. Fill the form with test data
3. Watch real-time timeline
4. Check SMS/Email generated
5. Simulate booking

**Complete flow: < 2 minutes** ✅

---

## 📁 Project Structure

```
solisa-ai-sdr/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI endpoints
│   │   ├── models.py            # Database models
│   │   ├── database.py          # DB connection
│   │   ├── enrichment.py        # Lead enrichment
│   │   ├── ai_engine.py         # Claude AI
│   │   └── communications.py    # SMS/Email
│   ├── requirements.txt
│   └── .env
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── LandingPage.jsx  # Lead capture
    │   │   └── Dashboard.jsx    # Analytics
    │   └── App.jsx
    └── package.json
```

---

## 🔧 Environment Variables

Edit `backend/.env`:

```bash
# Demo Mode (no real APIs needed)
DEMO_MODE=true

# For production:
ANTHROPIC_API_KEY=your_key_here
CALENDLY_LINK=https://calendly.com/yourname/30min
```

---

## ✅ Phase 1 Requirements Met

| Requirement | Status |
|------------|--------|
| Hyper-personalized outreach | ✅ |
| Auto-enrich: Life stage | ✅ |
| Auto-enrich: Current insurer | ✅ |
| Auto-enrich: Pain points | ✅ |
| SMS in prospect's tone | ✅ |
| Email with ROI proof | ✅ |
| Calendar 1-click booking | ✅ |
| Complete flow < 2 mins | ✅ |

---

## 🎯 Next: Phase 2 & 3

- **Phase 2:** Agentic Follow-up Brain
- **Phase 3:** Lifeline Retention Agent

---

**Built for hackathons. Ready to demo.** 🚀
