import re
from typing import Dict, List, Tuple

# Tier 1: Exact Match Rules (100% confidence)
EXACT_PATTERNS = {
    # Account funding
    "mam b fund": "Assets:Current Assets:Banks Local:BPI Checking (BE)",
    "mam b fund 11,150": "Assets:Current Assets:Banks Local:BPI Checking (BE)",
    "mam b fund 14,701.25": "Assets:Current Assets:Banks Local:BPI Checking (BE)",
    "mam b fund 14038.50": "Assets:Current Assets:Banks Local:BPI Checking (BE)",
    "mam b meds 14038.50": "Assets:Current Assets:Banks Local:BPI Checking (BE)",
    "sir gio fund": "Assets:Current Assets:Banks Local:BPI Savings (GB)",
    
    # Transportation
    "grab car": "Expenses:Transportation:Public",
    
    # Staff mobile loads
    "load ara arguilla": "Expenses:Household Staff:Ara:Load",
    "load michelle arguilla": "Expenses:Household Staff:Michelle:Load",
    "load ara": "Expenses:Household Staff:Ara:Load",
    "load michelle": "Expenses:Household Staff:Michelle:Load",
    
    # Pet expenses - Shadow
    "cat clinic shadow": "Expenses:Household Supplies:Pet Expenses",
    "shadow clinic": "Expenses:Household Supplies:Pet Expenses",
    "shadow clinic payment": "Expenses:Household Supplies:Pet Expenses",
    "shadow clinic payment 10,150": "Expenses:Household Supplies:Pet Expenses",
    "the cat clinic": "Expenses:Household Supplies:Pet Expenses",
    "pet express shadow": "Expenses:Household Supplies:Pet Expenses",
    "shadows food": "Expenses:Household Supplies:Pet Expenses",
    "pet shop shadow liter": "Expenses:Household Supplies:Pet Expenses",
    "shadow grab": "Expenses:Household Supplies:Pet Expenses",
    "shadow payment indrive": "Expenses:Household Supplies:Pet Expenses",
    "shadows hotel": "Expenses:Household Supplies:Pet Expenses",
    "shadows medicines": "Expenses:Household Supplies:Pet Expenses",
    
    # Staff reimbursements (IN transactions)
    "ara reimbursed": "Assets:Loans to:Ara Loan",
    "ara reimburse cash": "Assets:Current Assets:Cash Local:Cash for Groceries",
    "ara reimburse cash (reimbursed at kitty)": "Assets:Current Assets:Cash Local:Cash for Groceries",
    "reimburse to ara dinner playdate": "Expenses:Childcare:Others",
    
    # Staff expenses
    "ara lunch": "Expenses:Household Staff:Ara:Others",
    "ara BBQ Birthday": "Expenses:Household Staff:Ara:Others",
    "ara CAKE": "Expenses:Household Staff:Ara:Others",
    "ara PSA certificate": "Expenses:Household Staff:Ara:Others",
    "ara pag-ibig & philhealth payment": "Expenses:Household Staff:Ara:Benefits",
    "norina payment fee benefits": "Expenses:Household Staff:Ara:Benefits",
    
    # Basic household supplies
    "butane": "Expenses:Household Supplies",
    "light bulb": "Expenses:Household Supplies",
    "aquaflask": "Expenses:Household Supplies",
    "aquaflask alessi": "Expenses:Household Supplies",
    "ikea ziplocs": "Expenses:Household Supplies",
    "windproof": "Expenses:Household Supplies",
    "national book store": "Expenses:Childcare:Books",
    
    # Appliances/Electronics
    "soda stream": "Expenses:Household Supplies",
    "phone battery & repair": "Expenses:Electronics & Software",
    "extension wireless": "Expenses:Electronics & Software",
    
    # Food stores/restaurants
    "shake shack": "Expenses:Food:Dining",
    
    # Transfers
    "gcash (cash)": "Assets:Current Assets:Cash Local:GCash",
    
    # Entertainment
    "lazerxtreme": "Expenses:Childcare:Extracurricular Activities",
    "lazer xtreme": "Expenses:Childcare:Extracurricular Activities",
    "lazer xtreme tag": "Expenses:Childcare:Extracurricular Activities",
    "timezone": "Expenses:Childcare:Extracurricular Activities",
    
    # Missing patterns identified from backlog analysis
    "grab": "Expenses:Transportation:Public",
    "cat clinic": "Expenses:Household Supplies:Pet Expenses",
    "ara load": "Expenses:Household Staff:Ara:Load",
    "dinner playdate": "Expenses:Childcare:Others",
    "dinner playdate sleepover": "Expenses:Childcare:Others",
    "dinner playdate tylers": "Expenses:Childcare:Others",
    "mam b medicine": "Assets:Current Assets:Banks Local:BPI Checking (BE)",
    "mam b meds": "Assets:Current Assets:Banks Local:BPI Checking (BE)",
    "mam b delivery": "Expenses:Personal Care",
    "mam b items": "Expenses:Miscellaneous:Others",
    "tennis exceed": "Expenses:Childcare:Extracurricular Activities",
    "honey exceed": "Expenses:Food:Groceries",
    "shadow taxi fee": "Expenses:Household Supplies:Pet Expenses",
    "rider change for house kitty": "Expenses:Professional Fees",
    "mold activity": "Expenses:Housing:Repairs",
    "extension wireless (no change)": "Expenses:Electronics & Software",
    "puyat farms payment": "Expenses:Food:Groceries",
    "soda stream pick up grab": "Expenses:Transportation:Public",
}

# Tier 2: Regex Patterns (95% confidence)
REGEX_PATTERNS = [
    # Delivery services
    (r"(?i)(grab delivery|lalamove|del fee)", "Expenses:Food:Dining"),  # Large amounts likely food delivery
    (r"(?i)delivery fee", "Expenses:Professional Fees"),
    (r"(?i)rider.*fee", "Expenses:Professional Fees"),
    (r"(?i)lalamove.*del", "Expenses:Professional Fees"),
    
    # Staff documents/benefits
    (r"(?i)(ara|michelle) nbi", "Expenses:Household Staff:{staff}:Others"),
    
    # Alessi activities
    (r"(?i)tennis alessi", "Expenses:Childcare:Extracurricular Activities"),
    (r"(?i)swimming alessi", "Expenses:Childcare:Extracurricular Activities"),
    (r"(?i)coach jon", "Expenses:Childcare:Extracurricular Activities"),
    
    # Alessi personal items
    (r"(?i)alessi.*h & m", "Expenses:Childcare:Clothes"),
    (r"(?i)alessi.*boxers", "Expenses:Childcare:Clothes"),
    (r"(?i)knee pad alessi", "Expenses:Childcare:Clothes"),
    
    # Alessi food/snacks
    (r"(?i)alessi.*snacks", "Expenses:Childcare:Others"),
    (r"(?i)snacks alessi", "Expenses:Childcare:Others"),
    (r"(?i)alessi.*playdate.*food", "Expenses:Childcare:Others"),
    (r"(?i)playdate.*dinner", "Expenses:Childcare:Others"),
    (r"(?i)alessi.*taho", "Expenses:Childcare:Others"),
    (r"(?i)alessi.*pastry", "Expenses:Childcare:Others"),
    (r"(?i)alessi.*egg chocolates", "Expenses:Childcare:Others"),
    
    # Alessi health/medicine
    (r"(?i)alessi.*gummies", "Expenses:Health:Medicines"),
    (r"(?i)alessi.*medicine", "Expenses:Health:Medicines"),
    (r"(?i)alessi.*meds", "Expenses:Health:Medicines"),
    (r"(?i)alessi.*allergologist", "Expenses:Childcare:Doctor"),
    
    # Medicine/pharmacy
    (r"(?i)mercury drug", "Expenses:Health:Medicines"),
    
    # Gaming/entertainment for kids
    (r"(?i)roblox", "Expenses:Childcare:Others"),
    (r"(?i)twins.*roblox", "Expenses:Childcare:Others"),
    
    # Home repairs/improvements
    (r"(?i)curtain alter", "Expenses:Housing:Repairs"),
    (r"(?i)floor tiles", "Expenses:Housing:Repairs"),
    (r"(?i)lazada.*tiles", "Expenses:Household Supplies"),
    (r"(?i)floor tiles", "Expenses:Household Supplies"),
    
    # Gifts
    (r"(?i)twins gift", "Expenses:Gifts"),
    (r"(?i)dre's gift", "Expenses:Gifts"),
    
    # Exceed payments (inherit category from base transaction)
    (r"(?i)(\w+)\s+exceed", "INHERIT_FROM_BASE"),
    
    # Additional patterns identified from backlog analysis
    (r"(?i)dinner.*playdate", "Expenses:Childcare:Others"),
    (r"(?i)mam b.*medicine", "Expenses:Health:Medicines"),
    (r"(?i)mam b.*delivery", "Expenses:Personal Care"),
    (r"(?i)cat clinic(?!.*shadow)", "Expenses:Household Supplies:Pet Expenses"),
    (r"(?i).*exceed.*tennis", "Expenses:Childcare:Extracurricular Activities"),
    (r"(?i)rider.*change", "Expenses:Professional Fees"),
    (r"(?i)shadow.*taxi", "Expenses:Household Supplies:Pet Expenses"),
    (r"(?i)mam b.*items", "Expenses:Miscellaneous:Others"),
    (r"(?i).*exceed.*honey", "Expenses:Food:Groceries"),
    (r"(?i)puyat.*farms", "Expenses:Food:Groceries"),
    (r"(?i)mold.*activity", "Expenses:Housing:Repairs"),
]

# Tier 3: Keyword-Based Rules (85% confidence)
KEYWORD_RULES = {
    # Food/groceries
    "santis": "Expenses:Food:Groceries",
    "bernard": "Expenses:Food:Groceries",
    "berries": "Expenses:Food:Groceries",
    "healthy option": "Expenses:Food:Groceries",
    "lettuce": "Expenses:Food:Groceries",
    "veggies": "Expenses:Food:Groceries",
    "nuts": "Expenses:Food:Groceries",
    "fruits": "Expenses:Food:Groceries",
    "grab mart": "Expenses:Food:Groceries",
    
    # General Alessi expenses (lower confidence)
    "alessi": "Expenses:Childcare:Others",
    
    # Specific stores/services
    "watsons": "Expenses:Health:Medicines",
    "pink berry": "Expenses:Food:Dining",
}

# Confidence levels for each tier
CONFIDENCE_LEVELS = {
    "exact": 1.0,
    "regex": 0.95,
    "keyword": 0.85
}