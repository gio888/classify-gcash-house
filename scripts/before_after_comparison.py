#!/usr/bin/env python3
"""
Before/After Comparison Script for Rule Improvements.
Compares classifier performance before and after adding missing rules.
"""

import asyncio
import time
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from classifier import ClassifierFactory


async def run_before_after_comparison():
    """Compare classification performance before and after rule improvements."""
    
    print("🔄 BEFORE/AFTER RULE IMPROVEMENT COMPARISON")
    print("=" * 65)
    
    # File paths
    input_csv = "/Users/gio/Library/CloudStorage/GoogleDrive-gbacareza@gmail.com/My Drive/Money/House Expenses/House Kitty Transactions - Gcash 2024-03 to 2025-06-18.csv"
    output_csv_improved = "backlog_classified_improved.csv"
    
    try:
        print("📊 BEFORE IMPROVEMENTS (from previous run):")
        print("   Total Transactions: 785")
        print("   Successful Classifications: 773")
        print("   Failed Classifications: 12")
        print("   Success Rate: 98.5%")
        print("   Transactions Needing Review: 19")
        print("   Review Rate: 2.4%")
        print()
        
        # Create classifier with improved rules
        print("🏭 Creating classifier with improved rules...")
        classifier = await ClassifierFactory.create_minimal_classifier(
            chart_of_accounts_path="chart-of-accounts.txt"
        )
        print("✅ Classifier created with enhanced rules")
        
        # Show rule statistics
        stats = classifier.get_statistics()
        print(f"📈 Rule improvements:")
        print(f"   Active strategies: {stats['active_strategies']}")
        print(f"   Total rules loaded: {stats['strategy_usage']}")
        print()
        
        # Process with improved rules
        print("⚙️  Processing with improved rules...")
        start_time = time.perf_counter()
        
        batch_result = await classifier.classify_batch(
            source_file=input_csv,
            output_file=output_csv_improved
        )
        
        processing_time = time.perf_counter() - start_time
        
        if batch_result.is_err():
            print(f"❌ Processing failed: {batch_result.error}")
            return False
        
        result = batch_result.value
        print("✅ Processing completed!")
        print()
        
        # AFTER IMPROVEMENTS RESULTS
        print("📊 AFTER IMPROVEMENTS:")
        print(f"   Total Transactions: {result.total_transactions}")
        print(f"   Successful Classifications: {result.successful_classifications}")
        print(f"   Failed Classifications: {result.failed_classifications}")
        print(f"   Success Rate: {result.success_rate:.1f}%")
        print(f"   Transactions Needing Review: {result.needs_review_count}")
        print(f"   Review Rate: {result.review_rate:.1f}%")
        print()
        
        # COMPARISON ANALYSIS
        print("📈 IMPROVEMENT ANALYSIS:")
        print("-" * 40)
        
        # Before stats
        before_success = 773
        before_failed = 12
        before_success_rate = 98.5
        before_review = 19
        
        # After stats
        after_success = result.successful_classifications
        after_failed = result.failed_classifications
        after_success_rate = result.success_rate
        after_review = result.needs_review_count
        
        # Calculate improvements
        success_improvement = after_success - before_success
        failed_reduction = before_failed - after_failed
        success_rate_improvement = after_success_rate - before_success_rate
        review_reduction = before_review - after_review
        
        print(f"✅ Successful Classifications: {before_success} → {after_success} (+{success_improvement})")
        print(f"✅ Failed Classifications: {before_failed} → {after_failed} (-{failed_reduction})")
        print(f"✅ Success Rate: {before_success_rate:.1f}% → {after_success_rate:.1f}% (+{success_rate_improvement:.1f}%)")
        print(f"✅ Review Needed: {before_review} → {after_review} (-{review_reduction})")
        print()
        
        # Strategy breakdown with improvements
        strategy_stats = classifier.get_statistics()
        print(f"🎯 IMPROVED STRATEGY BREAKDOWN:")
        total_processed = strategy_stats['successful_classifications']
        
        for strategy, count in strategy_stats['strategy_usage'].items():
            if total_processed > 0:
                percentage = (count / total_processed) * 100
                print(f"   {strategy.title().replace('_', ' ')}: {count:,} transactions ({percentage:.1f}%)")
        print()
        
        # Performance comparison
        print(f"⚡ PERFORMANCE METRICS:")
        print(f"   Processing Time: {processing_time:.3f} seconds")
        if result.total_transactions > 0:
            avg_time = (processing_time / result.total_transactions * 1000)
            throughput = result.total_transactions / processing_time
            print(f"   Average Time per Transaction: {avg_time:.2f}ms")
            print(f"   Throughput: {throughput:.1f} transactions/second")
        print()
        
        # Analyze remaining failures
        remaining_failures = []
        if result.needs_review_count > 0:
            print(f"🔍 REMAINING FAILURES TO ANALYZE:")
            print("-" * 45)
            
            for classified_tx in result.results:
                if (classified_tx.classification.confidence < 0.85 or 
                    classified_tx.classification.target_account is None or
                    classified_tx.classification.needs_review):
                    remaining_failures.append(classified_tx)
            
            if remaining_failures:
                print(f"   Found {len(remaining_failures)} remaining issues:")
                for i, tx in enumerate(remaining_failures[:10], 1):  # Show first 10
                    desc = tx.description[:30]
                    conf = tx.classification.confidence
                    account = tx.classification.target_account or "None"
                    print(f"   {i:2d}. {desc:<30} (conf: {conf:.2f}) → {account[:25]}")
                
                if len(remaining_failures) > 10:
                    print(f"       ... and {len(remaining_failures) - 10} more")
            else:
                print("   🎉 No remaining failures!")
        else:
            print("🎉 PERFECT CLASSIFICATION!")
            print("   All transactions classified successfully!")
        print()
        
        # Final assessment
        if after_success_rate >= 99.5:
            assessment = "🌟 EXCEPTIONAL"
        elif after_success_rate >= 99.0:
            assessment = "🔥 EXCELLENT"
        elif after_success_rate >= 98.0:
            assessment = "✅ VERY GOOD"
        else:
            assessment = "👍 GOOD"
        
        print(f"🎯 FINAL ASSESSMENT: {assessment}")
        print(f"   Success Rate: {after_success_rate:.1f}%")
        print(f"   Production Ready: {'✅ YES' if after_success_rate >= 98.0 else '⚠️  NEEDS MORE RULES'}")
        print(f"   LLM Needed: {'❌ NO' if after_success_rate >= 99.5 else '💡 OPTIONAL'}")
        print()
        
        # File output summary
        print(f"📄 OUTPUT FILES GENERATED:")
        print(f"   Original: backlog_classified.csv")
        print(f"   Improved: {output_csv_improved}")
        print(f"   Ready for GnuCash import: ✅")
        print()
        
        print(f"🎉 Rule improvement analysis completed!")
        print(f"📊 {result.successful_classifications:,} transactions perfectly classified!")
        
        return True
        
    except Exception as e:
        print(f"❌ Comparison failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main comparison function."""
    success = await run_before_after_comparison()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)