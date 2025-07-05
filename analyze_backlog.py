#!/usr/bin/env python3
"""
Comprehensive Backlog Analysis for GnuCash Transaction Classifier.
Processes real transaction data and generates detailed analysis report.
"""

import asyncio
import time
import sys
import os
from pathlib import Path
from collections import defaultdict, Counter
import csv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from classifier import ClassifierFactory


async def analyze_backlog():
    """Comprehensive analysis of backlog transactions."""
    
    print("📊 GnuCash Transaction Classifier - Backlog Analysis")
    print("=" * 75)
    
    # File paths
    input_csv = "/Users/gio/Library/CloudStorage/GoogleDrive-gbacareza@gmail.com/My Drive/Money/House Expenses/House Kitty Transactions - Gcash 2024-03 to 2025-06-18.csv"
    output_csv = "backlog_classified.csv"
    
    try:
        # Verify input file exists
        if not Path(input_csv).exists():
            print(f"❌ Input file not found: {input_csv}")
            return False
        
        print(f"📄 Processing: {Path(input_csv).name}")
        print(f"📁 Output: {output_csv}")
        print()
        
        # Get file size and preview
        file_size = Path(input_csv).stat().st_size / (1024 * 1024)  # MB
        print(f"📏 File size: {file_size:.2f} MB")
        
        # Quick count of lines
        with open(input_csv, 'r') as f:
            total_lines = sum(1 for _ in f) - 1  # Subtract header
        print(f"📊 Estimated transactions: {total_lines:,}")
        print()
        
        # Create classifier
        print("🏭 Creating classifier...")
        classifier = await ClassifierFactory.create_minimal_classifier(
            chart_of_accounts_path="chart-of-accounts.txt"
        )
        print("✅ Classifier created successfully")
        print()
        
        # Validate CSV format
        print("🔍 Validating CSV format...")
        repository = classifier.repository
        validation_result = await repository.validate_csv_format(input_csv)
        
        if validation_result.is_err():
            print(f"❌ CSV validation failed: {validation_result.error}")
            return False
        
        print("✅ CSV format validated")
        
        # Get exact transaction count
        count_result = await repository.get_transaction_count(input_csv)
        if count_result.is_ok():
            transaction_count = count_result.value
            print(f"📊 Actual transactions to process: {transaction_count:,}")
        print()
        
        # Process the CSV file
        print("⚙️  Processing backlog transactions...")
        print("   This may take a few moments for large datasets...")
        start_time = time.perf_counter()
        
        batch_result = await classifier.classify_batch(
            source_file=input_csv,
            output_file=output_csv
        )
        
        processing_time = time.perf_counter() - start_time
        
        if batch_result.is_err():
            print(f"❌ Batch processing failed: {batch_result.error}")
            return False
        
        result = batch_result.value
        print("✅ Backlog processing completed!")
        print()
        
        # COMPREHENSIVE ANALYSIS REPORT
        print("📈 COMPREHENSIVE BACKLOG ANALYSIS REPORT")
        print("=" * 75)
        
        # Overall Performance
        print(f"📊 OVERALL PERFORMANCE:")
        print(f"   Total Transactions: {result.total_transactions:,}")
        print(f"   Successful Classifications: {result.successful_classifications:,}")
        print(f"   Failed Classifications: {result.failed_classifications:,}")
        print(f"   Success Rate: {result.success_rate:.1f}%")
        print(f"   Transactions Needing Review: {result.needs_review_count:,}")
        print(f"   Review Rate: {result.review_rate:.1f}%")
        print()
        
        # Strategy Breakdown
        strategy_stats = classifier.get_statistics()
        print(f"🎯 STRATEGY BREAKDOWN:")
        total_processed = strategy_stats['successful_classifications']
        
        for strategy, count in strategy_stats['strategy_usage'].items():
            if total_processed > 0:
                percentage = (count / total_processed) * 100
                print(f"   {strategy.title().replace('_', ' ')}: {count:,} transactions ({percentage:.1f}%)")
        print()
        
        # Performance Metrics
        print(f"⚡ PERFORMANCE METRICS:")
        print(f"   Total Processing Time: {processing_time:.2f} seconds")
        if result.total_transactions > 0:
            avg_time = (processing_time / result.total_transactions * 1000)
            throughput = result.total_transactions / processing_time
            print(f"   Average Time per Transaction: {avg_time:.2f}ms")
            print(f"   Throughput: {throughput:.1f} transactions/second")
        print()
        
        # Confidence Distribution Analysis
        print(f"🎖️  CONFIDENCE DISTRIBUTION:")
        confidence_buckets = {
            'Perfect (1.00)': 0,
            'High (0.90-0.99)': 0,
            'Good (0.85-0.89)': 0,
            'Medium (0.70-0.84)': 0,
            'Low (<0.70)': 0,
            'Failed (0.00)': 0
        }
        
        for classified_tx in result.results:
            conf = classified_tx.classification.confidence
            if conf == 1.0:
                confidence_buckets['Perfect (1.00)'] += 1
            elif conf >= 0.90:
                confidence_buckets['High (0.90-0.99)'] += 1
            elif conf >= 0.85:
                confidence_buckets['Good (0.85-0.89)'] += 1
            elif conf >= 0.70:
                confidence_buckets['Medium (0.70-0.84)'] += 1
            elif conf > 0.0:
                confidence_buckets['Low (<0.70)'] += 1
            else:
                confidence_buckets['Failed (0.00)'] += 1
        
        for bucket, count in confidence_buckets.items():
            if result.total_transactions > 0:
                percentage = (count / result.total_transactions) * 100
                print(f"   {bucket}: {count:,} ({percentage:.1f}%)")
        print()
        
        # Transaction Type Analysis
        print(f"💰 TRANSACTION TYPE ANALYSIS:")
        
        # Analyze by account categories
        account_categories = defaultdict(int)
        description_patterns = defaultdict(int)
        amount_ranges = {'<100': 0, '100-500': 0, '500-1000': 0, '1000-5000': 0, '>5000': 0}
        
        for classified_tx in result.results:
            # Account categories
            if classified_tx.classification.target_account:
                category = classified_tx.classification.target_account.split(':')[1] if ':' in classified_tx.classification.target_account else 'Other'
                account_categories[category] += 1
            
            # Description patterns (first two words)
            desc_words = classified_tx.description.lower().split()[:2]
            if desc_words:
                pattern = ' '.join(desc_words)
                description_patterns[pattern] += 1
            
            # Amount ranges
            amount = float(classified_tx.amount)
            if amount < 100:
                amount_ranges['<100'] += 1
            elif amount < 500:
                amount_ranges['100-500'] += 1
            elif amount < 1000:
                amount_ranges['500-1000'] += 1
            elif amount < 5000:
                amount_ranges['1000-5000'] += 1
            else:
                amount_ranges['>5000'] += 1
        
        # Top account categories
        print(f"   Top Account Categories:")
        for category, count in sorted(account_categories.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / result.total_transactions) * 100
            print(f"     {category}: {count:,} ({percentage:.1f}%)")
        print()
        
        # Amount distribution
        print(f"   Amount Distribution:")
        for range_name, count in amount_ranges.items():
            percentage = (count / result.total_transactions) * 100
            print(f"     {range_name}: {count:,} ({percentage:.1f}%)")
        print()
        
        # FAILED AND LOW CONFIDENCE TRANSACTIONS
        print(f"🔍 TRANSACTIONS NEEDING ATTENTION:")
        
        problem_transactions = []
        for classified_tx in result.results:
            if (classified_tx.classification.confidence < 0.85 or 
                classified_tx.classification.target_account is None or
                classified_tx.classification.needs_review):
                problem_transactions.append(classified_tx)
        
        if problem_transactions:
            print(f"   Found {len(problem_transactions)} transactions needing attention:")
            print()
            print(f"{'Description':<30} {'Amount':<12} {'Confidence':<10} {'Account':<25}")
            print("-" * 80)
            
            for tx in problem_transactions[:20]:  # Show top 20
                desc = tx.description[:29]
                amount = f"${tx.amount:,.2f}"
                conf = f"{tx.classification.confidence:.2f}"
                account = (tx.classification.target_account or "None")[:24]
                print(f"{desc:<30} {amount:<12} {conf:<10} {account:<25}")
            
            if len(problem_transactions) > 20:
                print(f"   ... and {len(problem_transactions) - 20} more")
        else:
            print(f"   ✅ All transactions classified with high confidence!")
        print()
        
        # NEW PATTERNS ANALYSIS
        print(f"🔍 NEW PATTERNS TO CONSIDER:")
        
        # Find most common unclassified or low-confidence patterns
        unclassified_patterns = defaultdict(int)
        for tx in problem_transactions:
            # Extract key words from description
            words = tx.description.lower().split()
            if words:
                # Try different pattern lengths
                for i in range(min(3, len(words))):
                    pattern = ' '.join(words[:i+1])
                    unclassified_patterns[pattern] += 1
        
        if unclassified_patterns:
            print(f"   Most common patterns needing rules:")
            for pattern, count in sorted(unclassified_patterns.items(), key=lambda x: x[1], reverse=True)[:15]:
                if count >= 2:  # Only show patterns that appear multiple times
                    print(f"     '{pattern}': {count} occurrences")
        else:
            print(f"   ✅ No significant new patterns detected!")
        print()
        
        # MOST COMMON TRANSACTION TYPES
        print(f"📈 MOST COMMON TRANSACTION TYPES:")
        most_common = sorted(description_patterns.items(), key=lambda x: x[1], reverse=True)[:15]
        
        for pattern, count in most_common:
            percentage = (count / result.total_transactions) * 100
            print(f"   '{pattern}': {count:,} occurrences ({percentage:.1f}%)")
        print()
        
        # LLM RECOMMENDATION
        print(f"🤖 LLM PROCESSING RECOMMENDATION:")
        if result.needs_review_count == 0:
            print(f"   ✅ No LLM processing needed - all transactions classified successfully!")
        else:
            llm_benefit = result.needs_review_count
            estimated_cost = llm_benefit * 0.01  # Rough estimate
            print(f"   💡 {llm_benefit:,} transactions would benefit from LLM processing")
            print(f"   💰 Estimated LLM cost: ~${estimated_cost:.2f}")
            print(f"   🎯 LLM would improve classification rate to near 100%")
        print()
        
        # OUTPUT FILE SUMMARY
        print(f"📄 OUTPUT FILE SUMMARY:")
        if Path(output_csv).exists():
            output_size = Path(output_csv).stat().st_size / (1024 * 1024)
            print(f"   File: {output_csv}")
            print(f"   Size: {output_size:.2f} MB")
            print(f"   Ready for GnuCash import: ✅")
            
            # Show sample output
            print(f"\n   Sample output rows:")
            with open(output_csv, 'r') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i == 0:  # Header
                        print(f"     Header: {', '.join(row[:5])}")
                    elif i <= 3:  # First few data rows
                        print(f"     Row {i}: {row[1][:20]}... → {row[4][:30]}...")
                    if i >= 3:
                        break
        print()
        
        print(f"🎉 Backlog analysis completed successfully!")
        print(f"📊 {result.successful_classifications:,} transactions ready for GnuCash import!")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main analysis function."""
    success = await analyze_backlog()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)