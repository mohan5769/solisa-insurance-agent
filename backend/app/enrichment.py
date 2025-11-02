import random
from datetime import datetime, timedelta

# Life stages for different insurance types
LIFE_STAGES = {
    "Auto": [
        "Young professional commuting to work",
        "Parent with teenage drivers",
        "Rideshare driver needing commercial coverage",
        "Recent car buyer with high loan payments",
        "Multi-car household looking to bundle"
    ],
    "Home": [
        "First-time homebuyer",
        "Growing family needing more space",
        "Empty nester downsizing",
        "Investment property owner",
        "Recent home renovator"
    ],
    "Life": [
        "New parent planning for family's future",
        "Mid-career professional building wealth",
        "Business owner protecting key person",
        "Pre-retiree maximizing estate planning",
        "Young couple getting married"
    ],
    "Health": [
        "Self-employed individual needing coverage",
        "Family with young children",
        "Pre-Medicare retiree (55-64)",
        "Freelancer with variable income",
        "Recent job changer in transition"
    ]
}

# Common pain points by insurance type
PAIN_POINTS = {
    "Auto": [
        "Premiums increased 30% at last renewal",
        "Poor customer service response times",
        "Complicated claims process",
        "No accident forgiveness despite clean record",
        "Limited coverage for rideshare activities",
        "High deductibles eating into savings"
    ],
    "Home": [
        "Underinsured for recent home improvements",
        "High premiums in disaster-prone area",
        "Denied claims for water damage",
        "No coverage for home office equipment",
        "Expensive flood insurance add-on",
        "Poor communication during claims"
    ],
    "Life": [
        "Confusing policy terms and conditions",
        "High premiums for limited coverage",
        "No living benefits or riders included",
        "Difficult beneficiary update process",
        "Limited conversion options",
        "Poor financial strength rating of insurer"
    ],
    "Health": [
        "High deductibles and out-of-pocket maximums",
        "Limited provider network",
        "Prescription drugs not covered",
        "Long wait times for specialist appointments",
        "Confusing explanation of benefits",
        "Denied pre-authorization requests"
    ]
}

# Major insurance providers by type
PROVIDERS = {
    "Auto": ["Geico", "State Farm", "Progressive", "Allstate", "USAA", "Liberty Mutual"],
    "Home": ["State Farm", "Allstate", "Liberty Mutual", "Farmers", "Nationwide", "Travelers"],
    "Life": ["Northwestern Mutual", "New York Life", "MassMutual", "Prudential", "MetLife", "Guardian"],
    "Health": ["Blue Cross Blue Shield", "UnitedHealthcare", "Aetna", "Cigna", "Humana", "Kaiser Permanente"]
}

# Age ranges
AGE_RANGES = ["25-35", "35-45", "45-55", "55+"]


def enrich_lead(lead_data: dict) -> dict:
    """
    Enrich lead data with mock information for demo purposes.
    
    Args:
        lead_data: Dictionary with basic lead info (full_name, email, phone, insurance_type, current_provider)
    
    Returns:
        Dictionary with enriched lead data
    """
    insurance_type = lead_data.get("insurance_type", "Auto")
    
    # Select appropriate life stage
    life_stage = random.choice(LIFE_STAGES.get(insurance_type, LIFE_STAGES["Auto"]))
    
    # Assign age range
    age_range = random.choice(AGE_RANGES)
    
    # Pick current provider if not provided
    current_provider = lead_data.get("current_provider")
    if not current_provider or current_provider.strip() == "":
        current_provider = random.choice(PROVIDERS.get(insurance_type, PROVIDERS["Auto"]))
    
    # Generate renewal date (1-12 months in the future)
    months_ahead = random.randint(1, 12)
    renewal_date = (datetime.now() + timedelta(days=30 * months_ahead)).strftime("%B %Y")
    
    # Select 2 random pain points
    pain_points = random.sample(PAIN_POINTS.get(insurance_type, PAIN_POINTS["Auto"]), 2)
    
    # Calculate estimated savings ($200-$800/year)
    estimated_savings = random.randint(200, 800)
    
    # Return enriched data
    enriched = {
        **lead_data,
        "life_stage": life_stage,
        "estimated_age_range": age_range,
        "current_provider": current_provider,
        "renewal_date": renewal_date,
        "pain_points": pain_points,
        "estimated_savings": estimated_savings
    }
    
    return enriched
