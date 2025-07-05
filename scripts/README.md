# Development and Analysis Scripts

This folder contains scripts used for development, testing, and rule improvement. These are **not needed for monthly production use**.

## Scripts

### **analyze_backlog.py**
**Purpose**: Comprehensive analysis of large transaction datasets
```bash
python scripts/analyze_backlog.py
```
- Processes production CSV file (785+ transactions)
- Provides performance metrics and strategy breakdown
- Identifies transactions needing attention
- Shows most common transaction patterns

### **before_after_comparison.py**
**Purpose**: Compares classifier performance before/after rule improvements
```bash
python scripts/before_after_comparison.py
```
- Runs improved classifier on same dataset
- Shows success rate improvements
- Analyzes remaining failures
- Provides final assessment

### **missing_rules_analysis.py**
**Purpose**: Identifies patterns for new classification rules
```bash
python scripts/missing_rules_analysis.py
```
- Analyzes failed classifications
- Suggests specific rules to add
- Provides ready-to-use code snippets
- Calculates potential improvement metrics

### **process_csv.py**
**Purpose**: General CSV processing for testing/development
```bash
python scripts/process_csv.py
```
- Handles smaller datasets
- Detailed transaction-by-transaction analysis
- Good for testing new rules

### **example_usage.py**
**Purpose**: Demonstrates classifier usage patterns
```bash
python scripts/example_usage.py
```
- Shows single transaction classification
- Demonstrates batch processing
- Creates sample data for testing

## When to Use These Scripts

- **Rule Improvement**: Use `missing_rules_analysis.py` → add rules → test with `before_after_comparison.py`
- **Performance Analysis**: Use `analyze_backlog.py` for detailed metrics
- **Development Testing**: Use `process_csv.py` and `example_usage.py`
- **Learning**: Check `example_usage.py` to understand the API

## Note
For monthly production use, you only need the main script at the project root:
```bash
./classify_transactions.py --auto-house
```