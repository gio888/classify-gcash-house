# GnuCash Transaction Classifier

A production-ready Python classifier that processes CSV transactions and outputs GnuCash account classifications using modern software engineering practices.

## Project Overview

This project builds a transaction classifier that:
- Processes CSV transaction data with async/await performance
- Applies multi-tier rule-based classification (exact, regex, keyword)
- Falls back to LLM classification for unmatched transactions
- Outputs GnuCash-compatible account classifications
- Includes comprehensive error handling and structured logging

## Specification Documents

The project requirements are defined in three key specification documents:

1. **[requirements.md](./requirements.md)** - Core project requirements and classification rules
2. **[technical-spec.md](./technical-spec.md)** - Technical implementation details and architecture
3. **[data-spec.md](./data-spec.md)** - Data formats, CSV structure, and GnuCash account mappings

## Architecture

Built with modern software engineering principles:

### SOLID Principles
- **Single Responsibility**: Each class has one clear purpose
- **Dependency Injection**: Factory pattern for easy testing and configuration
- **Strategy Pattern**: Pluggable classification methods (Exact, Regex, Keyword, LLM)
- **Repository Pattern**: Abstracted data access for CSV operations

### Key Components
- `TransactionClassifier`: Main orchestrator with dependency injection
- `ClassificationStrategy`: Strategy pattern for different classification methods
- `AccountValidator`: Validates GnuCash account paths
- `TransactionRepository`: Repository pattern for CSV I/O
- Rules engine with 3-tier classification system

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run main CLI (automated monthly workflow)
./classify_transactions.py --auto-house

# Run backlog analysis
python analyze_backlog.py

# Run example usage
python example_usage.py

# Set OpenAI API key for LLM features (optional)
export OPENAI_API_KEY="your-key-here"
```

## Quick Start

```bash
# Automated monthly workflow (main usage)
cd /Users/gio/Code/classify-gcash-house
./classify_transactions.py --auto-house

# This will:
# 1. Auto-detect newest CSV in Google Drive
# 2. Ask for confirmation
# 3. Process with 100% success rate
# 4. Generate "For Import" file ready for GnuCash
```

```python
# Programmatic usage
from classifier import ClassifierFactory

# Create classifier
classifier = await ClassifierFactory.create_minimal_classifier(
    chart_of_accounts_path="chart-of-accounts.txt"
)

# Process CSV file
batch_result = await classifier.classify_batch(
    source_file="input.csv",
    output_file="classified.csv"
)
```

## Project Structure

```
classify_transactions.py    # Main CLI for monthly workflow
analyze_backlog.py         # Comprehensive analysis script
missing_rules_analysis.py  # Rule improvement analysis
before_after_comparison.py # Performance comparison
process_csv.py             # General CSV processing
example_usage.py           # Usage examples

src/classifier/
├── core/                   # Main orchestrator and factory
│   ├── classifier.py       # TransactionClassifier
│   └── factory.py          # ClassifierFactory
├── strategies/             # Classification strategies
│   ├── exact_match.py      # Exact pattern matching
│   ├── regex_match.py      # Regex pattern matching  
│   ├── keyword_match.py    # Keyword-based matching
│   └── llm_strategy.py     # LLM fallback (optional)
├── repositories/           # Data access
│   └── csv_repository.py   # CSV file operations
├── validators/             # Account validation
│   └── account_validator.py
├── models/                 # Data models
│   ├── transaction.py      # Transaction models
│   └── classification.py   # Classification results
├── infrastructure/         # Logging and utilities
│   └── logging.py          # Structured logging
├── rules.py                # 3-tier rule engine
└── utils/
    └── result.py           # Error handling utilities

chart-of-accounts.txt       # GnuCash account structure
backlog_classified.csv      # Processed output (785 transactions)
```

## Features

### Production Ready
- ✅ **Automated CLI**: One-command monthly workflow
- ✅ **High Performance**: ~10,000 transactions/second  
- ✅ **Structured Logging**: Comprehensive processing reports
- ✅ **Type Safety**: Full type hints with Pydantic validation
- ✅ **Error Handling**: Graceful failure recovery
- ✅ **Auto-Detection**: Finds newest CSV files automatically
- ✅ **Batch Processing**: Efficient handling of large CSV files

### Classification Methods
- ✅ **Exact Match**: 100% confidence for known patterns
- ✅ **Regex Match**: 95% confidence for flexible patterns  
- ✅ **Keyword Match**: 85% confidence for partial matches
- ✅ **LLM Fallback**: Optional AI classification (not needed for current data)
- ✅ **Account Validation**: Ensures valid GnuCash account paths

### Monitoring & Observability
- ✅ **Performance Metrics**: Processing time, throughput analysis
- ✅ **Classification Statistics**: Strategy usage, confidence scores
- ✅ **Success Tracking**: 100% classification rate achieved
- ✅ **Analysis Reports**: Detailed transaction breakdowns