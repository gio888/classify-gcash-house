# GnuCash Transaction Classifier

A production-ready Python classifier that processes CSV transactions and outputs GnuCash-compatible account classifications.

## Monthly Usage (Production Workflow)

### Quick Start
```bash
cd /Users/gio/Code/classify-gcash-house
./classify_transactions.py --auto-house
```

## Available Scripts

### 1. **Main Production Script**
```bash
./classify_transactions.py --auto-house
```
**Purpose**: Automated monthly workflow for processing house expenses
- Auto-detects newest CSV in Google Drive
- Asks for confirmation before processing
- Generates "For Import" file ready for GnuCash

### 2. **Comprehensive Analysis**
```bash
python analyze_backlog.py
```
**Purpose**: Detailed analysis of large transaction datasets
- Processes production CSV file (785+ transactions)
- Provides performance metrics and strategy breakdown
- Identifies transactions needing attention
- Shows most common transaction patterns

### 3. **Rule Improvement Analysis**
```bash
python missing_rules_analysis.py
```
**Purpose**: Identifies patterns for new classification rules
- Analyzes failed classifications
- Suggests specific rules to add
- Provides ready-to-use code snippets
- Calculates potential improvement metrics

### 4. **Performance Comparison**
```bash
python before_after_comparison.py
```
**Purpose**: Compares classifier performance before/after rule improvements
- Runs improved classifier on same dataset
- Shows success rate improvements
- Analyzes remaining failures
- Provides final assessment

### 5. **General CSV Processing**
```bash
python process_csv.py
```
**Purpose**: Processes sample CSV files for testing/development
- Handles smaller datasets
- Detailed transaction-by-transaction analysis
- Good for testing new rules

### 6. **Usage Examples**
```bash
python example_usage.py
```
**Purpose**: Demonstrates classifier usage patterns
- Shows single transaction classification
- Demonstrates batch processing
- Creates sample data for testing

### What It Does
1. **Auto-detects** the newest CSV file in your Google Drive folder
2. **Asks for confirmation** before processing
3. **Classifies all transactions** using the rule engine (98.5%+ accuracy)
4. **Generates output** as "For Import House Kitty Transactions - YYYY-MM.csv"
5. **Ready for GnuCash import** - just drag and drop!

### Example Output
```
🏠 GnuCash Transaction Classifier - House Expenses
============================================================
🔍 Searching for newest CSV file...

📄 FOUND FILE TO PROCESS:
   Input:  House Kitty Transactions - Gcash 2024-03 to 2025-06-18.csv
   Size:   0.10 MB
   Count:  785 transactions
   Output: For Import House Kitty Transactions - 2025-06.csv

🤔 Process this file? (y/n): y

⚙️  PROCESSING TRANSACTIONS...
==================================================
🏭 Creating classifier...
📊 Classifying transactions...

✅ PROCESSING COMPLETE!
==================================================
📈 Total Transactions: 785
✅ Successful Classifications: 785
❌ Failed Classifications: 0
📊 Success Rate: 100.0%
⏱️  Processing Time: 0.08 seconds

📁 Output saved to: For Import House Kitty Transactions - 2025-06.csv
🎯 Ready for GnuCash import!

🎉 Monthly processing complete!
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Google Drive folder access
- Project dependencies installed

### First-Time Setup
```bash
# Clone/download the project
cd /Users/gio/Code/classify-gcash-house

# Install dependencies
pip install -r requirements.txt

# Verify setup
./classify_transactions.py --help
```

### File Structure
```
/Users/gio/Code/classify-gcash-house/
├── classify_transactions.py    # Main CLI script
├── chart-of-accounts.txt      # GnuCash account structure
├── src/classifier/            # Classification engine
└── requirements.txt           # Dependencies
```

## Configuration

### Input Folder
```
/Users/gio/Library/CloudStorage/GoogleDrive-gbacareza@gmail.com/My Drive/Money/House Expenses/
```

### Auto-Detection Rules
- Finds newest CSV file by modification date
- Excludes files starting with "For Import"
- Processes house expense transactions only

### Output Format
- **Filename**: `For Import House Kitty Transactions - YYYY-MM.csv`
- **Location**: Same folder as input file
- **Format**: GnuCash-ready CSV with account classifications

## Classification Rules

### 3-Tier System
1. **Exact Match** (100% confidence) - 544 transactions (70.2%)
2. **Regex Match** (95% confidence) - 213 transactions (27.5%)
3. **Keyword Match** (85% confidence) - 18 transactions (2.3%)

### Common Categories
- **Transportation**: Grab cars, delivery fees
- **Childcare**: Alessi activities, food, health
- **Household Staff**: Ara/Michelle loads, benefits
- **Pet Expenses**: Shadow clinic, food, medicines
- **Health**: Medicines, doctor visits
- **Food**: Groceries, dining, delivery

## Troubleshooting

### Common Issues

**"Google Drive folder not found"**
```bash
# Check if Google Drive is synced
ls "/Users/gio/Library/CloudStorage/GoogleDrive-gbacareza@gmail.com/My Drive/Money/House Expenses/"
```

**"Could not import classifier module"**
```bash
# Make sure you're in the project root
cd /Users/gio/Code/classify-gcash-house

# Install dependencies
pip install -r requirements.txt
```

**"No CSV files found"**
- Check that CSV files exist in the Google Drive folder
- Verify files don't all start with "For Import"
- Try running with a specific file path

### Manual Processing
If auto-detection doesn't work, you can still use the analysis scripts:
```bash
# Edit analyze_backlog.py to point to your specific file
python analyze_backlog.py
```

## Monthly Workflow Summary

1. **Run the script**: `./classify_transactions.py --auto-house`
2. **Confirm the file**: Check it found the right CSV
3. **Wait for processing**: Usually takes <1 second
4. **Import to GnuCash**: Use the generated "For Import" file
5. **Done!** All transactions classified and ready

## Performance
- **Speed**: ~10,000 transactions/second
- **Accuracy**: 98.5%+ success rate
- **Memory**: Minimal footprint
- **Reliability**: Production-tested on 785+ transactions

---

*Last updated: July 2025*