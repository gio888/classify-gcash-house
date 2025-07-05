#!/usr/bin/env python3
"""
Example usage of the GnuCash Transaction Classifier.

This demonstrates how to use the modern, production-ready classifier
with all its features including async processing, error handling,
and structured logging.
"""

import asyncio
import os
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from classifier import ClassifierFactory, Transaction, TransactionDirection
from decimal import Decimal
from datetime import datetime


async def main():
    """Demonstrate classifier usage."""
    
    print("🚀 GnuCash Transaction Classifier Demo")
    print("=" * 50)
    
    # Configuration
    chart_of_accounts_path = "chart-of-accounts.txt"
    openai_api_key = os.getenv("OPENAI_API_KEY")  # Set this environment variable
    
    try:
        # Create classifier with dependency injection
        print("📋 Creating classifier...")
        if openai_api_key:
            classifier = await ClassifierFactory.create_development_classifier(
                chart_of_accounts_path=chart_of_accounts_path,
                openai_api_key=openai_api_key
            )
            print("✅ Classifier created with LLM support")
        else:
            classifier = await ClassifierFactory.create_minimal_classifier(
                chart_of_accounts_path=chart_of_accounts_path
            )
            print("✅ Classifier created (rule-based only)")
        
        # Test sample transactions
        test_transactions = [
            ("grab car", 250.00, TransactionDirection.OUTGOING),
            ("mam b fund", 15000.00, TransactionDirection.INCOMING),
            ("tennis alessi", 500.00, TransactionDirection.OUTGOING),
            ("mercury drug", 150.00, TransactionDirection.OUTGOING),
            ("unknown merchant", 100.00, TransactionDirection.OUTGOING),
        ]
        
        print("\n🔍 Classifying sample transactions...")
        print("-" * 50)
        
        for desc, amount, direction in test_transactions:
            transaction = Transaction(
                date=datetime.now(),
                description=desc,
                amount=Decimal(str(amount)),
                direction=direction
            )
            
            result = await classifier.classify_transaction(transaction)
            
            if result.is_ok():
                classification = result.value
                confidence_emoji = "🟢" if classification.confidence >= 0.85 else "🟡" if classification.confidence >= 0.7 else "🔴"
                review_flag = " ⚠️ NEEDS REVIEW" if classification.needs_review else ""
                
                print(f"{confidence_emoji} {desc}")
                print(f"   Account: {classification.target_account or 'None'}")
                print(f"   Confidence: {classification.confidence:.2f}")
                print(f"   Method: {classification.method.value}")
                print(f"   Reasoning: {classification.reasoning}{review_flag}")
                print()
            else:
                print(f"❌ Failed to classify: {desc}")
                print(f"   Error: {result.error}")
                print()
        
        # Show statistics
        print("📊 Classification Statistics:")
        print("-" * 30)
        stats = classifier.get_statistics()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # Demonstrate batch processing if CSV exists
        sample_csv = "sample_transactions.csv"
        if Path(sample_csv).exists():
            print(f"\n📄 Processing batch file: {sample_csv}")
            
            batch_result = await classifier.classify_batch(
                source_file=sample_csv,
                output_file="classified_transactions.csv"
            )
            
            if batch_result.is_ok():
                result = batch_result.value
                print(f"✅ Batch processing complete!")
                print(f"   Total: {result.total_transactions}")
                print(f"   Success: {result.successful_classifications}")
                print(f"   Failed: {result.failed_classifications}")
                print(f"   Review needed: {result.needs_review_count}")
                print(f"   Success rate: {result.success_rate:.1f}%")
                print(f"   Processing time: {result.processing_time_seconds:.2f}s")
            else:
                print(f"❌ Batch processing failed: {batch_result.error}")
        else:
            print(f"\n💡 Create '{sample_csv}' to test batch processing")
            
            # Create sample CSV
            sample_content = """Date,Description,Personal,Out,In
2024-01-15,grab car,,250.00,
2024-01-15,mam b fund,,,15000.00
2024-01-16,tennis alessi,,500.00,
2024-01-16,mercury drug,,150.00,
2024-01-17,unknown store,,75.00,"""
            
            with open(sample_csv, 'w') as f:
                f.write(sample_content)
            print(f"📝 Created {sample_csv} for testing")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print("\n🎉 Demo completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())