# GnuCash Transaction Classifier

A production-ready Python classifier that processes CSV transactions and outputs GnuCash-compatible account classifications.

## Monthly Usage (Production Workflow)

### Quick Start
```bash
cd /path/to/classify-gcash-house
./classify_transactions.py --auto-house
```

## Project Structure

```
classify-gcash-house/
├── README.md                    # This file
├── requirements.txt             # Dependencies
├── classify_transactions.py     # MAIN PRODUCTION SCRIPT
├── chart-of-accounts.txt        # GnuCash account structure
├── 
├── scripts/                     # Development and analysis tools
│   ├── analyze_backlog.py       # Comprehensive transaction analysis
│   ├── before_after_comparison.py # Performance comparison
│   ├── missing_rules_analysis.py # Rule improvement suggestions
│   ├── process_csv.py           # General CSV processing
│   ├── example_usage.py         # Usage demonstrations
│   └── README.md                # Script documentation
├── 
├── tests/                       # Test files and sample data
│   ├── test_classifier.py       # Unit tests
│   ├── test_production_csv.py   # Production format tests
│   ├── sample_transactions.csv  # Sample test data
│   └── production_sample.csv    # Production format test data
├── 
├── src/classifier/              # Core implementation
├── docs/                        # Documentation
│   ├── claude.md                # Project overview
│   ├── technical-spec.md        # Technical specification
│   ├── requirements.md          # Classification rules
│   └── data-spec.md             # Data formats
└── outputs/                     # Generated files (git ignored)
    ├── analysis/                # Analysis results
    ├── production/              # Monthly import files
    └── test_runs/               # Development outputs
```

## Main Production Workflow

### **Monthly Usage** (Only command you need)
```bash
cd /path/to/classify-gcash-house
./classify_transactions.py --auto-house
```

**What it does:**
- Auto-detects newest CSV in Google Drive
- Asks for confirmation before processing
- Generates "For Import House Kitty Transactions - YYYY-MM.csv" in `outputs/production/`
- Ready for GnuCash import!

## Development Scripts

For rule improvement and analysis (see [`scripts/README.md`](scripts/README.md)):

```bash
# Comprehensive analysis
python scripts/analyze_backlog.py

# Rule improvement workflow
python scripts/missing_rules_analysis.py
python scripts/before_after_comparison.py

# Development and testing
python scripts/process_csv.py
python scripts/example_usage.py
```

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
cd /path/to/classify-gcash-house

# Install dependencies
pip install -r requirements.txt

# Verify setup
./classify_transactions.py --help
```

### File Locations
- **Main script**: `./classify_transactions.py` (project root)
- **Configuration**: `chart-of-accounts.txt` (project root)
- **Output files**: `outputs/production/` (auto-generated)
- **Documentation**: `docs/` folder
- **Development tools**: `scripts/` folder

## Configuration

### Input/Output Locations
- **Input folder**: `/path/to/GoogleDrive-your-email@gmail.com/My Drive/Money/House Expenses/`
- **Main script output**: Same Google Drive folder (for easy GnuCash import)
- **Development outputs**: `outputs/` folder (analysis results, test runs)
- **Auto-detection**: Finds newest CSV, excludes "For Import" files
- **Output format**: `For Import House Kitty Transactions - YYYY-MM.csv`

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
ls "/path/to/GoogleDrive-your-email@gmail.com/My Drive/Money/House Expenses/"
```

**"Could not import classifier module"**
```bash
# Make sure you're in the project root
cd /path/to/classify-gcash-house

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
# Use the development analysis script
python scripts/analyze_backlog.py
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