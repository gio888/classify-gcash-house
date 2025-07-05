#!/usr/bin/env python3
"""
Test script for the GnuCash Transaction Classifier.
Tests the classifier with real transaction descriptions.
"""

import asyncio
import time
from datetime import datetime
from decimal import Decimal
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from classifier import ClassifierFactory, Transaction, TransactionDirection


async def test_classifier():
    """Test the classifier with sample transaction descriptions."""
    
    print("🧪 GnuCash Transaction Classifier - Test Suite")
    print("=" * 60)
    
    # Create sample test data
    test_transactions = [
        {
            "description": "grab car",
            "amount": Decimal("250.00"),
            "direction": TransactionDirection.OUTGOING,
            "expected_account": "Expenses:Transportation:Public",
            "expected_method": "exact_match"
        },
        {
            "description": "mam b fund", 
            "amount": Decimal("15000.00"),
            "direction": TransactionDirection.INCOMING,
            "expected_account": "Assets:Current Assets:Banks Local:BPI Savings (BE)",
            "expected_method": "exact_match"
        },
        {
            "description": "tennis alessi",
            "amount": Decimal("500.00"), 
            "direction": TransactionDirection.OUTGOING,
            "expected_account": "Expenses:Childcare:Extracurricular Activities",
            "expected_method": "regex_match"
        },
        {
            "description": "mercury drug",
            "amount": Decimal("150.00"),
            "direction": TransactionDirection.OUTGOING,
            "expected_account": "Expenses:Health:Medicines", 
            "expected_method": "regex_match"
        },
        {
            "description": "load ara arguilla",
            "amount": Decimal("100.00"),
            "direction": TransactionDirection.OUTGOING,
            "expected_account": "Expenses:Household Staff:Ara:Load",
            "expected_method": "exact_match"
        },
        {
            "description": "shadow clinic",
            "amount": Decimal("1200.00"),
            "direction": TransactionDirection.OUTGOING,
            "expected_account": "Expenses:Household Supplies:Pet Expenses",
            "expected_method": "exact_match"
        }
    ]
    
    try:
        # Create classifier
        print("📋 Creating classifier...")
        classifier = await ClassifierFactory.create_minimal_classifier(
            chart_of_accounts_path="chart-of-accounts.txt"
        )
        print("✅ Classifier created successfully")
        print()
        
        # Test each transaction
        print("🔍 Testing Sample Transactions")
        print("-" * 60)
        
        results = []
        total_processing_time = 0
        
        for i, test_data in enumerate(test_transactions, 1):
            print(f"Test {i}: '{test_data['description']}'")
            
            # Create transaction
            transaction = Transaction(
                date=datetime.now(),
                description=test_data['description'],
                amount=test_data['amount'],
                direction=test_data['direction']
            )
            
            # Measure processing time
            start_time = time.perf_counter()
            result = await classifier.classify_transaction(transaction)
            processing_time = (time.perf_counter() - start_time) * 1000
            total_processing_time += processing_time
            
            if result.is_ok():
                classification = result.value
                
                # Check if classification matches expectations
                account_match = classification.target_account == test_data['expected_account']
                method_match = classification.method.value == test_data['expected_method']
                
                # Status indicators
                account_status = "✅" if account_match else "❌"
                method_status = "✅" if method_match else "❌"
                confidence_status = "🟢" if classification.confidence >= 0.85 else "🟡" if classification.confidence >= 0.7 else "🔴"
                
                print(f"   {account_status} Account: {classification.target_account}")
                print(f"   {method_status} Method: {classification.method.value}")
                print(f"   {confidence_status} Confidence: {classification.confidence:.2f}")
                print(f"   ⏱️  Processing: {processing_time:.2f}ms")
                print(f"   💭 Reasoning: {classification.reasoning}")
                
                if classification.needs_review:
                    print(f"   ⚠️  NEEDS REVIEW")
                
                # Store result for statistics
                results.append({
                    'description': test_data['description'],
                    'classification': classification,
                    'processing_time': processing_time,
                    'account_match': account_match,
                    'method_match': method_match,
                    'expected_account': test_data['expected_account'],
                    'expected_method': test_data['expected_method']
                })
                
            else:
                print(f"   ❌ Classification failed: {result.error}")
                results.append({
                    'description': test_data['description'],
                    'classification': None,
                    'processing_time': processing_time,
                    'account_match': False,
                    'method_match': False,
                    'error': str(result.error)
                })
            
            print()
        
        # Generate Statistics Report
        print("📊 CLASSIFICATION STATISTICS REPORT")
        print("=" * 60)
        
        # Overall stats
        successful_classifications = len([r for r in results if r['classification'] is not None])
        failed_classifications = len(results) - successful_classifications
        
        account_accuracy = len([r for r in results if r.get('account_match', False)]) / len(results) * 100
        method_accuracy = len([r for r in results if r.get('method_match', False)]) / len(results) * 100
        
        print(f"📈 Overall Performance:")
        print(f"   Total Transactions: {len(results)}")
        print(f"   Successful Classifications: {successful_classifications}")
        print(f"   Failed Classifications: {failed_classifications}")
        print(f"   Account Accuracy: {account_accuracy:.1f}%")
        print(f"   Method Accuracy: {method_accuracy:.1f}%")
        print()
        
        # Strategy usage
        strategy_usage = {}
        confidence_scores = []
        
        for result in results:
            if result['classification']:
                method = result['classification'].method.value
                strategy_usage[method] = strategy_usage.get(method, 0) + 1
                confidence_scores.append(result['classification'].confidence)
        
        print(f"🎯 Strategy Usage:")
        for strategy, count in strategy_usage.items():
            percentage = (count / successful_classifications) * 100 if successful_classifications > 0 else 0
            print(f"   {strategy}: {count} transactions ({percentage:.1f}%)")
        print()
        
        # Confidence analysis
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            min_confidence = min(confidence_scores)
            max_confidence = max(confidence_scores)
            
            high_confidence = len([c for c in confidence_scores if c >= 0.85])
            medium_confidence = len([c for c in confidence_scores if 0.7 <= c < 0.85])
            low_confidence = len([c for c in confidence_scores if c < 0.7])
            
            print(f"🎖️  Confidence Analysis:")
            print(f"   Average Confidence: {avg_confidence:.3f}")
            print(f"   Min Confidence: {min_confidence:.3f}")
            print(f"   Max Confidence: {max_confidence:.3f}")
            print(f"   High Confidence (≥0.85): {high_confidence} ({high_confidence/len(confidence_scores)*100:.1f}%)")
            print(f"   Medium Confidence (0.7-0.84): {medium_confidence} ({medium_confidence/len(confidence_scores)*100:.1f}%)")
            print(f"   Low Confidence (<0.7): {low_confidence} ({low_confidence/len(confidence_scores)*100:.1f}%)")
            print()
        
        # Performance metrics
        avg_processing_time = total_processing_time / len(results)
        transactions_per_second = 1000 / avg_processing_time if avg_processing_time > 0 else 0
        
        print(f"⚡ Performance Metrics:")
        print(f"   Total Processing Time: {total_processing_time:.2f}ms")
        print(f"   Average Processing Time: {avg_processing_time:.2f}ms")
        print(f"   Transactions per Second: {transactions_per_second:.1f}")
        print()
        
        # Classifier internal statistics
        classifier_stats = classifier.get_statistics()
        print(f"🔧 Classifier Internal Stats:")
        for key, value in classifier_stats.items():
            print(f"   {key}: {value}")
        print()
        
        # Detailed results table
        print("📋 DETAILED RESULTS")
        print("-" * 60)
        print(f"{'Description':<20} {'Expected':<15} {'Actual':<15} {'Conf':<6} {'Time':<8}")
        print("-" * 60)
        
        for result in results:
            desc = result['description'][:19]
            expected = result.get('expected_method', 'N/A')[:14]
            
            if result['classification']:
                actual = result['classification'].method.value[:14]
                conf = f"{result['classification'].confidence:.2f}"
            else:
                actual = "FAILED"
                conf = "0.00"
            
            time_str = f"{result['processing_time']:.1f}ms"
            
            print(f"{desc:<20} {expected:<15} {actual:<15} {conf:<6} {time_str:<8}")
        
        print("\n🎉 Test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    success = await test_classifier()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)