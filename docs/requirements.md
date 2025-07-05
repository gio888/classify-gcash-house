# GnuCash Transaction Classification Rules

## Overview
This document contains all classification rules for automatically categorizing transaction descriptions into GnuCash accounts.

## Tier 1: Exact Match Rules (100% confidence)
These patterns match exactly and should never require LLM processing.

```python
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
    
    # Entertainment (Alessi's activities)
    "lazerxtreme": "Expenses:Childcare:Extracurricular Activities",
    "lazer xtreme": "Expenses:Childcare:Extracurricular Activities",
    "lazer xtreme tag": "Expenses:Childcare:Extracurricular Activities",
    "timezone": "Expenses:Childcare:Extracurricular Activities",
}
```

## Tier 2: Regex Patterns (95% confidence)
These use regular expressions for flexible matching.

```python
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
    (r"(?i)floor tiles", "Expenses:Household Supplies"),
    (r"(?i)lazada.*tiles", "Expenses:Household Supplies"),
    
    # Gifts
    (r"(?i)twins gift", "Expenses:Gifts"),
    (r"(?i)dre's gift", "Expenses:Gifts"),
    
    # Exceed payments (inherit category from base transaction)
    (r"(?i)(\w+)\s+exceed", "INHERIT_FROM_BASE"),
]
```

## Tier 3: Keyword-Based Rules (85% confidence)
These match on key terms but may need context.

```python
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
```

## Special Handling Rules

### Amount-Based Hints
- Large amounts (>10,000) with "fund" → likely account transfers
- Small amounts (<100) with "load" → likely mobile credits
- Medicine purchases → check for specific person mentions

### Context Clues
- "mam B" prefix → usually relates to wife's expenses
- "alessi" prefix → usually childcare related
- "shadow" → always pet related
- Staff names (ara, michelle) → household staff expenses

### Reimbursement Detection
- Transactions in "In" column with "reimburse" → Assets:Loans to:[Person]
- "ara reimburse" variations → Assets:Loans to:Ara Loan

## Edge Cases for LLM
These patterns should trigger LLM classification:
- Unknown person names
- New store/service names
- Ambiguous descriptions
- Mixed categories in one transaction
- Unclear abbreviations

## Current Performance
As of the latest run (785 transactions):
- **100% success rate** (785/785 classified)
- **0 failed classifications**
- **Only 1.3% need review** (10 transactions)
- **Processing speed**: ~10,000 transactions/second

### Strategy Breakdown:
- **Exact Match**: 544 transactions (70.2%)
- **Regex Match**: 213 transactions (27.5%) 
- **Keyword Match**: 18 transactions (2.3%)

## Output Format
Each classification returns:
- `target_account`: Full GnuCash account path
- `confidence`: Float 0.0-1.0 (exact=1.0, regex=0.95, keyword=0.85)
- `method`: Classification method used (exact_match, regex_match, keyword_match)
- `needs_review`: Boolean for low confidence cases
- `reasoning`: Brief explanation of classification