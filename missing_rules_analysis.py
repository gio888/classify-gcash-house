#!/usr/bin/env python3
"""
Analysis of missing rules based on backlog processing results.
Identifies patterns that should be added to improve classification accuracy.
"""

import csv
from collections import defaultdict

def analyze_missing_rules():
    """Analyze failed classifications and suggest new rules."""
    
    print("🔍 MISSING RULES ANALYSIS")
    print("=" * 50)
    
    # Read the classified results to find failed transactions
    failed_transactions = []
    
    try:
        with open('backlog_classified.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                confidence = float(row['Confidence'])
                target_account = row['Target Account']
                
                # Find failed or low confidence transactions
                if confidence == 0.0 or target_account.lower() == 'none':
                    failed_transactions.append({
                        'description': row['Description'],
                        'amount': row['Out'] or row['In'],
                        'confidence': confidence,
                        'account': target_account,
                        'reasoning': row['Reasoning']
                    })
    
        print(f"📊 Found {len(failed_transactions)} failed transactions")
        print()
        
        # Group by description patterns
        patterns = defaultdict(list)
        for tx in failed_transactions:
            desc = tx['description'].lower()
            patterns[desc].append(tx)
        
        print("🎯 SUGGESTED NEW RULES:")
        print("-" * 30)
        
        # Analyze each unique failed pattern
        suggested_rules = []
        
        for desc, transactions in patterns.items():
            count = len(transactions)
            amounts = [float(tx['amount']) for tx in transactions]
            avg_amount = sum(amounts) / len(amounts)
            
            # Suggest rules based on pattern analysis
            rule_type = "exact"
            suggested_account = None
            reasoning = ""
            
            if "dinner playdate" in desc:
                suggested_account = "Expenses:Childcare:Others"
                reasoning = "Playdate food expenses for children"
            elif "cat clinic" in desc and "shadow" not in desc:
                suggested_account = "Expenses:Household Supplies:Pet Expenses"
                reasoning = "Pet medical expenses"
            elif desc.startswith("mam b ") and "medicine" in desc:
                suggested_account = "Expenses:Health:Medicines"
                reasoning = "Medicine purchases"
            elif desc.startswith("mam b ") and "delivery" in desc:
                suggested_account = "Expenses:Professional Fees"
                reasoning = "Delivery fees"
            elif desc.startswith("mam b ") and "items" in desc:
                suggested_account = "Expenses:Miscellaneous:Others"
                reasoning = "General purchases"
            elif "ara load" == desc:
                suggested_account = "Expenses:Household Staff:Ara:Load"
                reasoning = "Staff mobile load - exact match missing"
            elif desc == "grab" and avg_amount < 300:
                suggested_account = "Expenses:Transportation:Public"
                reasoning = "Transportation expenses"
            elif "exceed" in desc and "tennis" in desc:
                suggested_account = "Expenses:Childcare:Extracurricular Activities"
                reasoning = "Tennis lesson exceed payment"
            elif "exceed" in desc and "honey" in desc:
                suggested_account = "Expenses:Food:Groceries"
                reasoning = "Grocery exceed payment"
            elif "rider change" in desc:
                suggested_account = "Expenses:Professional Fees"
                reasoning = "Delivery service fees"
            elif "mold activity" in desc:
                suggested_account = "Expenses:Housing:Repairs"
                reasoning = "Home maintenance"
            elif "puyat farms" in desc:
                suggested_account = "Expenses:Food:Groceries"
                reasoning = "Food supplier"
            elif "soda stream" in desc and "grab" in desc:
                suggested_account = "Expenses:Transportation:Public"
                reasoning = "Transportation for appliance pickup"
            elif "shadow taxi" in desc:
                suggested_account = "Expenses:Household Supplies:Pet Expenses"
                reasoning = "Pet transportation"
            elif "extension wireless" in desc:
                suggested_account = "Expenses:Electronics & Software"
                reasoning = "Electronics purchase"
            
            if suggested_account:
                suggested_rules.append({
                    'pattern': desc,
                    'account': suggested_account,
                    'type': rule_type,
                    'count': count,
                    'reasoning': reasoning,
                    'avg_amount': avg_amount
                })
        
        # Sort by frequency
        suggested_rules.sort(key=lambda x: x['count'], reverse=True)
        
        print("📝 RECOMMENDED RULE ADDITIONS:")
        print()
        
        exact_rules = []
        regex_rules = []
        
        for rule in suggested_rules:
            print(f"Pattern: '{rule['pattern']}'")
            print(f"  → Account: {rule['account']}")
            print(f"  → Occurrences: {rule['count']}")
            print(f"  → Avg Amount: ${rule['avg_amount']:.2f}")
            print(f"  → Reasoning: {rule['reasoning']}")
            print()
            
            # Format for code addition
            if rule['type'] == 'exact':
                exact_rules.append(f'    "{rule["pattern"]}": "{rule["account"]}",')
        
        print("🔧 CODE TO ADD TO EXACT_PATTERNS:")
        print("```python")
        for rule in exact_rules:
            print(rule)
        print("```")
        print()
        
        # Generate regex patterns for broader matching
        print("🔧 ADDITIONAL REGEX PATTERNS TO CONSIDER:")
        print("```python")
        print('    (r"(?i)dinner.*playdate", "Expenses:Childcare:Others"),')
        print('    (r"(?i)mam b.*medicine", "Expenses:Health:Medicines"),')
        print('    (r"(?i)mam b.*delivery", "Expenses:Professional Fees"),')
        print('    (r"(?i)cat clinic(?!.*shadow)", "Expenses:Household Supplies:Pet Expenses"),')
        print('    (r"(?i).*exceed.*tennis", "Expenses:Childcare:Extracurricular Activities"),')
        print('    (r"(?i)rider.*change", "Expenses:Professional Fees"),')
        print('    (r"(?i)shadow.*taxi", "Expenses:Household Supplies:Pet Expenses"),')
        print("```")
        print()
        
        # Calculate improvement potential
        total_failed = len(failed_transactions)
        rules_would_catch = len([r for r in suggested_rules if r['account']])
        
        print(f"📈 IMPROVEMENT POTENTIAL:")
        print(f"   Current failed: {total_failed}")
        print(f"   Rules would catch: {rules_would_catch}")
        print(f"   Potential success rate improvement: +{(rules_would_catch/785)*100:.1f}%")
        print(f"   New success rate would be: {((773+rules_would_catch)/785)*100:.1f}%")
        
    except FileNotFoundError:
        print("❌ backlog_classified.csv not found. Run the main analysis first.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_missing_rules()