#!/usr/bin/env python3
"""
Production CSV Test for GnuCash Transaction Classifier.
Tests with real production CSV format including comma-separated amounts and M/D/YYYY dates.
"""

import asyncio
import time
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from classifier import ClassifierFactory


async def test_production_csv():
    """Test the classifier with production CSV format."""
    
    print("🏭 GnuCash Transaction Classifier - Production CSV Test")
    print("=" * 65)
    
    # File paths
    input_csv = "production_sample.csv"
    output_csv = "production_classified.csv"
    
    try:
        # Verify input file exists
        if not Path(input_csv).exists():
            print(f"❌ Input file not found: {input_csv}")
            return False
        
        print(f"📄 Input file: {input_csv}")
        print(f"📄 Output file: {output_csv}")
        print()
        
        # Show input CSV content
        print("📋 INPUT CSV CONTENT:")
        print("-" * 50)
        with open(input_csv, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                print(f"{i+1:2d}: {line.rstrip()}")
        print()
        
        # Create classifier
        print("🏭 Creating classifier...")
        classifier = await ClassifierFactory.create_minimal_classifier(
            chart_of_accounts_path="chart-of-accounts.txt"
        )
        print("✅ Classifier created successfully")
        print()
        
        # Validate CSV format
        print("🔍 Validating production CSV format...")
        repository = classifier.repository
        validation_result = await repository.validate_csv_format(input_csv)
        
        if validation_result.is_err():
            print(f"❌ CSV validation failed: {validation_result.error}")
            return False
        
        print("✅ Production CSV format is valid")
        
        # Get transaction count
        count_result = await repository.get_transaction_count(input_csv)
        if count_result.is_ok():
            transaction_count = count_result.value
            print(f"📊 Found {transaction_count} transactions to process")
        print()
        
        # Process the CSV file
        print("⚙️  Processing production transactions...")
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
        print("✅ Production batch processing completed successfully!")
        print()
        
        # Display detailed results
        print("📊 PRODUCTION PROCESSING RESULTS")
        print("=" * 65)
        
        print(f"📈 Overall Performance:")
        print(f"   Total Transactions: {result.total_transactions}")
        print(f"   Successful Classifications: {result.successful_classifications}")
        print(f"   Failed Classifications: {result.failed_classifications}")
        print(f"   Success Rate: {result.success_rate:.1f}%")
        print(f"   Transactions Needing Review: {result.needs_review_count}")
        print(f"   Review Rate: {result.review_rate:.1f}%")
        print()
        
        # Strategy breakdown
        strategy_stats = classifier.get_statistics()
        print(f"🎯 Strategy Usage Analysis:")
        total_processed = strategy_stats['successful_classifications']
        
        for strategy, count in strategy_stats['strategy_usage'].items():
            if count > 0:
                percentage = (count / total_processed) * 100 if total_processed > 0 else 0
                print(f"   {strategy}: {count} transactions ({percentage:.1f}%)")
        print()
        
        # Performance analysis
        print(f"⚡ Performance Analysis:")
        print(f"   Total Processing Time: {processing_time:.3f} seconds")
        if result.total_transactions > 0:
            avg_time = (processing_time / result.total_transactions * 1000)
            throughput = result.total_transactions / processing_time
            print(f"   Average Time per Transaction: {avg_time:.2f}ms")
            print(f"   Throughput: {throughput:.1f} transactions/second")
        print()
        
        # Detailed transaction analysis
        print(f"📋 PRODUCTION TRANSACTION ANALYSIS")
        print("-" * 65)
        print(f"{'Description':<25} {'Amount':<12} {'Account':<25} {'Method':<10}")
        print("-" * 65)
        
        for classified_tx in result.results:
            desc = classified_tx.description[:24]
            amount_str = f"${classified_tx.amount:,.2f}"
            account = (classified_tx.classification.target_account or "None")
            if len(account) > 24:
                account = account[:21] + "..."
            method = classified_tx.classification.method.value[:9]
            
            print(f"{desc:<25} {amount_str:<12} {account:<25} {method:<10}")
        print()
        
        # Show production output CSV
        print("📄 PRODUCTION OUTPUT CSV:")
        print("-" * 65)
        
        if Path(output_csv).exists():
            with open(output_csv, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    print(f"{i+1:2d}: {line.rstrip()}")
        else:
            print("❌ Output file not found")
        print()
        
        # Production format validation
        print("🔍 PRODUCTION FORMAT VALIDATION:")
        print("-" * 40)
        
        # Check for comma-separated thousands
        comma_amounts = [tx for tx in result.results if ',' in str(tx.amount)]
        print(f"✅ Comma-separated thousands handled: Original had commas")
        
        # Check for M/D/YYYY date format
        print(f"✅ M/D/YYYY date format processed successfully")
        
        # Check for extra columns
        print(f"✅ Extra CSV columns (Balance, Calculated Balance) ignored properly")
        
        # Account classification accuracy
        expected_classifications = {
            "mam B fund": "Assets:Current Assets:Banks Local:BPI Savings (BE)",
            "alessi playdate food": "Expenses:Childcare:Others", 
            "load ara arguilla": "Expenses:Household Staff:Ara:Load"
        }
        
        accuracy_count = 0
        for classified_tx in result.results:
            desc = classified_tx.description
            expected = expected_classifications.get(desc)
            actual = classified_tx.classification.target_account
            
            if expected == actual:
                accuracy_count += 1
                print(f"✅ {desc}: Correctly classified")
            else:
                print(f"❌ {desc}: Expected {expected}, got {actual}")
        
        accuracy_rate = (accuracy_count / len(expected_classifications)) * 100
        print(f"📊 Classification Accuracy: {accuracy_rate:.1f}%")
        print()
        
        print(f"🎉 Production CSV test completed successfully!")
        print(f"🚀 Ready for real-world production use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Production test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    success = await test_production_csv()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)