# Data Specification for GnuCash Classifier

## Input Data Format

### CSV Structure
The input CSV file contains transaction data with the following columns:

| Column | Description | Type | Required |
|--------|-------------|------|----------|
| `Date` | Transaction date | String (YYYY-MM-DD) | Yes |
| `Description` | Transaction description text | String | Yes |
| `Personal` | Unknown purpose field | String | No (ignored) |
| `Out` | Expense amount (when money goes out) | Float | Conditional* |
| `In` | Income amount (when money comes in) | Float | Conditional* |

*Either `Out` or `In` must have a value, but not both for the same transaction.

### Sample Input Data
```csv
Date,Description,Personal,Out,In
2024-01-15,grab car,,250.00,
2024-01-15,mam b fund,,,15000.00
2024-01-16,shadow clinic payment,,1200.00,
2024-01-16,ara reimburse cash,,,500.00
```

## Output Data Format

### CSV Structure
The output CSV preserves input data and adds classification results:

| Column | Description | Type |
|--------|-------------|------|
| `Date` | Transaction date (preserved) | String (ISO format) |
| `Description` | Transaction description (preserved) | String |
| `Out` | Expense amount (preserved) | Float |
| `In` | Income amount (preserved) | Float |
| `Target Account` | Full GnuCash account path | String |
| `Confidence` | Classification confidence (0.0-1.0) | Float |
| `Method` | Classification method used | String |
| `Needs Review` | Flag for manual review | Boolean |
| `Reasoning` | Explanation of classification decision | String |

### Sample Output Data
```csv
Date,Description,Out,In,Target Account,Confidence,Method,Needs Review,Reasoning
2024-03-01T00:00:00,grab car,250.0,,Expenses:Transportation:Public,1.00,exact_match,False,Exact match for 'grab car'
2024-03-01T00:00:00,mam B fund,,1500.0,Assets:Current Assets:Banks Local:BPI Checking (BE),1.00,exact_match,False,Exact match for 'mam b fund'
2024-03-01T00:00:00,shadow clinic payment,1200.0,,Expenses:Household Supplies:Pet Expenses,1.00,exact_match,False,Exact match for 'shadow clinic payment'
2024-03-01T00:00:00,alessi playdate food,1378.0,,Expenses:Childcare:Others,0.95,regex_match,False,Regex match for pattern '(?i)alessi.*playdate.*food'
```

## GnuCash Chart of Accounts

The complete chart of accounts is stored in [`chart-of-accounts.txt`](./chart-of-accounts.txt). This file contains all valid GnuCash account paths in colon-delimited format.

### Key Account Categories

#### Assets
- **Current Assets**: Cash, bank accounts, GCash wallets
- **Fixed Assets**: Equipment, vehicles, other physical assets
- **Investments**: Properties, business investments, brokerage accounts
- **Loans to**: Money lent to staff and others

#### Liabilities
- **Credit Cards**: Various credit card accounts
- **Loans**: Outstanding loans and mortgages
- **Other**: Staff loan accounts, other payables

#### Income
- **Salary**: Income from employment
- **Interest**: Investment and savings interest
- **Other**: Bonuses, gifts, rental income

#### Expenses
- **Childcare**: Alessi-related expenses (clothes, activities, health)
- **Food**: Groceries, dining, alcohol
- **Household Staff**: Ara, Michelle, Marie expenses by category
- **Health**: Medical, dental, medicines
- **Transportation**: Public transport, gas, parking
- **Utilities**: Electric, water, internet, mobile
- **Housing**: Rent, repairs, gardening
- **Entertainment**: Recreation, music, movies

### Account Validation Rules

1. **Exact Match Required**: Account paths must match exactly (case-sensitive)
2. **Colon Delimited**: Account hierarchy separated by colons
3. **No Trailing Spaces**: Account names must be clean
4. **Valid Parents**: Child accounts must have valid parent accounts

### Common Account Mappings

#### Staff-Related Accounts
- **Ara**: `Expenses:Household Staff:Ara:*` (Load, Others, Benefits, etc.)
- **Michelle**: `Expenses:Household Staff:Michelle:*`
- **Marie**: `Expenses:Household Staff:Marie:*`
- **Reimbursements**: `Assets:Loans to:Ara Loan`

#### Child-Related Accounts
- **Alessi General**: `Expenses:Childcare:Others`
- **Alessi Clothes**: `Expenses:Childcare:Clothes`
- **Alessi Activities**: `Expenses:Childcare:Extracurricular Activities`
- **Alessi Health**: `Expenses:Health:*` (Medicines, Doctor)

#### Pet-Related Accounts
- **Shadow (Pet)**: `Expenses:Household Supplies:Pet Expenses`

#### Banking/Transfer Accounts
- **GCash**: `Assets:Current Assets:Cash Local:GCash`
- **BPI Checking (BE)**: `Assets:Current Assets:Banks Local:BPI Checking (BE)`
- **BPI Savings (GB)**: `Assets:Current Assets:Banks Local:BPI Savings (GB)`

## Data Processing Rules

### Transaction Direction Logic
- **Out Amount**: Expense transaction → Use Expenses:* accounts
- **In Amount**: Income/transfer transaction → Use Assets:* or Income:* accounts
- **Reimbursements**: Special case - "In" amounts with "reimburse" text → Use Assets:Loans to:* accounts

### Text Preprocessing
1. Convert description to lowercase for matching
2. Strip leading/trailing whitespace
3. Normalize multiple spaces to single spaces
4. Handle common abbreviations and typos

### Account Path Validation
1. Verify account exists in chart-of-accounts.txt
2. Ensure proper colon-delimited hierarchy
3. Flag invalid or non-existent accounts for review

### Error Handling
- **Invalid Account**: Flag for manual review
- **Multiple Matches**: Use highest confidence match
- **No Match**: Send to LLM classifier
- **Confidence Below Threshold**: Flag for review