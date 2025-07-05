#!/usr/bin/env python3
"""
CSV Processing Pipeline for GnuCash Transaction Classifier.
Demonstrates full end-to-end workflow with real CSV data.
"""

import asyncio
import time
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from classifier import ClassifierFactory


async def process_csv_pipeline():
    """Process CSV file through the complete classification pipeline."""
    
    print("🔄 GnuCash Transaction Classifier - CSV Processing Pipeline")
    print("=" * 70)
    
    # File paths
    input_csv = "sample_transactions.csv"
    output_csv = "classified_transactions.csv"
    
    try:
        # Verify input file exists
        if not Path(input_csv).exists():
            print(f"❌ Input file not found: {input_csv}")
            return False
        
        print(f"📄 Input file: {input_csv}")
        print(f"📄 Output file: {output_csv}")
        print()
        
        # Create classifier
        print("🏭 Creating classifier...")
        classifier = await ClassifierFactory.create_minimal_classifier(
            chart_of_accounts_path="chart-of-accounts.txt"
        )
        print("✅ Classifier created successfully")
        
        # Show classifier configuration
        stats = classifier.get_statistics()
        print(f"🔧 Active strategies: {stats['active_strategies']}")
        print(f"🔧 Strategy names: {', '.join(stats['strategy_names'])}")
        print()
        
        # Validate CSV format
        print("🔍 Validating CSV format...")
        repository = classifier.repository
        validation_result = await repository.validate_csv_format(input_csv)
        
        if validation_result.is_err():
            print(f"❌ CSV validation failed: {validation_result.error}")
            return False
        
        print("✅ CSV format is valid")
        
        # Get transaction count
        count_result = await repository.get_transaction_count(input_csv)
        if count_result.is_ok():
            transaction_count = count_result.value
            print(f"📊 Found {transaction_count} transactions to process")
        print()
        
        # Process the CSV file
        print("⚙️  Processing transactions...")
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
        print("✅ Batch processing completed successfully!")
        print()
        
        # Display comprehensive results
        print("📊 COMPREHENSIVE PROCESSING REPORT")
        print("=" * 70)
        
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
        print(f"🎯 Strategy Usage Breakdown:")
        total_processed = strategy_stats['successful_classifications']
        
        for strategy, count in strategy_stats['strategy_usage'].items():
            if count > 0:
                percentage = (count / total_processed) * 100 if total_processed > 0 else 0
                print(f"   {strategy}: {count} transactions ({percentage:.1f}%)")
        print()
        
        # Performance metrics
        print(f"⚡ Performance Metrics:")
        print(f"   Total Processing Time: {processing_time:.3f} seconds")
        print(f"   Average Time per Transaction: {(processing_time / result.total_transactions * 1000):.2f}ms")
        print(f"   Throughput: {(result.total_transactions / processing_time):.1f} transactions/second")
        print()
        
        # Detailed transaction analysis
        print(f"📋 DETAILED TRANSACTION ANALYSIS")
        print("-" * 70)
        
        high_confidence = 0
        medium_confidence = 0
        low_confidence = 0
        llm_candidates = 0
        
        print(f"{'Description':<25} {'Account':<35} {'Method':<12} {'Conf':<6} {'Review'}")
        print("-" * 70)
        
        for classified_tx in result.results:
            desc = classified_tx.description[:24]
            account = (classified_tx.classification.target_account or "None")[:34]
            method = classified_tx.classification.method.value[:11]
            conf = f"{classified_tx.classification.confidence:.2f}"
            review = "Yes" if classified_tx.classification.needs_review else "No"
            
            print(f"{desc:<25} {account:<35} {method:<12} {conf:<6} {review}")
            
            # Count confidence levels
            if classified_tx.classification.confidence >= 0.85:
                high_confidence += 1
            elif classified_tx.classification.confidence >= 0.7:
                medium_confidence += 1
            else:
                low_confidence += 1
                
            # Check if would benefit from LLM
            if (classified_tx.classification.target_account is None or 
                classified_tx.classification.confidence < 0.85):
                llm_candidates += 1
        
        print()
        
        # Confidence analysis
        print(f"🎖️  Classification Confidence Analysis:")
        print(f"   High Confidence (≥0.85): {high_confidence} ({high_confidence/result.total_transactions*100:.1f}%)")
        print(f"   Medium Confidence (0.7-0.84): {medium_confidence} ({medium_confidence/result.total_transactions*100:.1f}%)")
        print(f"   Low Confidence (<0.7): {low_confidence} ({low_confidence/result.total_transactions*100:.1f}%)")
        print()
        
        # LLM recommendation analysis
        print(f"🤖 LLM Processing Analysis:")
        if llm_candidates == 0:
            print("   ✅ All transactions classified with high confidence")
            print("   ✅ No LLM processing needed for this dataset")
        else:
            print(f"   🔄 {llm_candidates} transactions would benefit from LLM processing")
            print("   💡 Consider enabling LLM fallback for unknown transactions")
        print()
        
        # Show output file preview
        print("📄 OUTPUT CSV PREVIEW")
        print("-" * 70)
        
        if Path(output_csv).exists():
            with open(output_csv, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:10]):  # Show first 10 lines
                    print(f"{i+1:2d}: {line.rstrip()}")
                if len(lines) > 10:
                    print(f"    ... and {len(lines) - 10} more lines")
        else:
            print("❌ Output file not found")
        
        print()
        print(f"✅ Full pipeline completed successfully!")
        print(f"📁 Output saved to: {output_csv}")
        print(f"🎯 Ready for GnuCash import!")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main processing function."""
    success = await process_csv_pipeline()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)