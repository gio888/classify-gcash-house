import pytest
import asyncio
import tempfile
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from classifier import ClassifierFactory, Transaction, TransactionDirection
from classifier.strategies import ExactMatchStrategy, RegexMatchStrategy, KeywordMatchStrategy
from classifier.validators import AccountValidator
from classifier.repositories import CSVTransactionRepository


class TestModernClassifier:
    """Test the modern architecture classifier."""
    
    @pytest.fixture
    async def sample_chart_of_accounts(self):
        """Create a temporary chart of accounts file."""
        content = """Assets
Assets:Current Assets
Assets:Current Assets:Banks Local
Assets:Current Assets:Banks Local:BPI Savings (BE)
Assets:Current Assets:Banks Local:BPI Savings (GB)
Assets:Current Assets:Cash Local
Assets:Current Assets:Cash Local:GCash
Assets:Loans to
Assets:Loans to:Ara Loan
Expenses
Expenses:Transportation
Expenses:Transportation:Public
Expenses:Childcare
Expenses:Childcare:Extracurricular Activities
Expenses:Health
Expenses:Health:Medicines
Expenses:Household Staff
Expenses:Household Staff:Ara
Expenses:Household Staff:Ara:Load
Expenses:Household Staff:Michelle
Expenses:Household Staff:Michelle:Load"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            f.flush()
            yield f.name
        
        # Cleanup
        os.unlink(f.name)
    
    @pytest.fixture
    async def classifier(self, sample_chart_of_accounts):
        """Create a test classifier."""
        return await ClassifierFactory.create_minimal_classifier(sample_chart_of_accounts)
    
    @pytest.mark.asyncio
    async def test_exact_match_strategy(self, classifier):
        """Test exact match classification."""
        transaction = Transaction(
            date=datetime.now(),
            description="grab car",
            amount=Decimal("250.00"),
            direction=TransactionDirection.OUTGOING
        )
        
        result = await classifier.classify_transaction(transaction)
        
        assert result.is_ok()
        classification = result.value
        assert classification.target_account == "Expenses:Transportation:Public"
        assert classification.confidence == 1.0
        assert classification.method.value == "exact_match"
        assert not classification.needs_review
    
    @pytest.mark.asyncio
    async def test_regex_match_strategy(self, classifier):
        """Test regex match classification."""
        transaction = Transaction(
            date=datetime.now(),
            description="tennis alessi",
            amount=Decimal("500.00"),
            direction=TransactionDirection.OUTGOING
        )
        
        result = await classifier.classify_transaction(transaction)
        
        assert result.is_ok()
        classification = result.value
        assert classification.target_account == "Expenses:Childcare:Extracurricular Activities"
        assert classification.confidence == 0.95
        assert classification.method.value == "regex_match"
        assert not classification.needs_review
    
    @pytest.mark.asyncio
    async def test_keyword_match_strategy(self, classifier):
        """Test keyword match classification."""
        transaction = Transaction(
            date=datetime.now(),
            description="mercury drug vitamins",
            amount=Decimal("150.00"),
            direction=TransactionDirection.OUTGOING
        )
        
        result = await classifier.classify_transaction(transaction)
        
        assert result.is_ok()
        classification = result.value
        # This should match the regex pattern for mercury drug
        assert classification.target_account == "Expenses:Health:Medicines"
        assert classification.confidence == 0.95
        assert classification.method.value == "regex_match"
    
    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self, classifier):
        """Test that matching is case insensitive."""
        transaction = Transaction(
            date=datetime.now(),
            description="GRAB CAR",
            amount=Decimal("300.00"),
            direction=TransactionDirection.OUTGOING
        )
        
        result = await classifier.classify_transaction(transaction)
        
        assert result.is_ok()
        classification = result.value
        assert classification.target_account == "Expenses:Transportation:Public"
        assert classification.confidence == 1.0
    
    @pytest.mark.asyncio
    async def test_no_match_fallback(self, classifier):
        """Test fallback when no strategy matches."""
        transaction = Transaction(
            date=datetime.now(),
            description="unknown merchant xyz",
            amount=Decimal("100.00"),
            direction=TransactionDirection.OUTGOING
        )
        
        result = await classifier.classify_transaction(transaction)
        
        assert result.is_ok()
        classification = result.value
        assert classification.target_account is None
        assert classification.confidence == 0.0
        assert classification.method.value == "manual_review"
        assert classification.needs_review
    
    @pytest.mark.asyncio
    async def test_account_validation(self, sample_chart_of_accounts):
        """Test account validation."""
        validator = AccountValidator(sample_chart_of_accounts)
        await validator.load_chart_of_accounts()
        
        # Valid account
        result = validator.validate_account("Expenses:Transportation:Public")
        assert result.is_ok()
        
        # Invalid account
        result = validator.validate_account("Invalid:Account:Path")
        assert result.is_err()
        
        # Suggestions for invalid account
        suggestions = validator.suggest_similar_accounts("Transport")
        assert "Expenses:Transportation:Public" in suggestions
    
    @pytest.mark.asyncio
    async def test_strategy_priority(self, classifier):
        """Test that strategies are executed in priority order."""
        # This transaction should match both exact and keyword patterns
        # but exact should win due to higher priority
        transaction = Transaction(
            date=datetime.now(),
            description="aquaflask alessi",  # Exact match exists
            amount=Decimal("200.00"),
            direction=TransactionDirection.OUTGOING
        )
        
        result = await classifier.classify_transaction(transaction)
        
        assert result.is_ok()
        classification = result.value
        assert classification.method.value == "exact_match"  # Exact match should win
        assert classification.confidence == 1.0
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, classifier):
        """Test that statistics are properly tracked."""
        initial_stats = classifier.get_statistics()
        
        transaction = Transaction(
            date=datetime.now(),
            description="grab car",
            amount=Decimal("250.00"),
            direction=TransactionDirection.OUTGOING
        )
        
        await classifier.classify_transaction(transaction)
        
        updated_stats = classifier.get_statistics()
        assert updated_stats["successful_classifications"] == initial_stats["successful_classifications"] + 1
        assert updated_stats["strategy_usage"]["exact_match"] > initial_stats["strategy_usage"]["exact_match"]


class TestCSVRepository:
    """Test CSV repository functionality."""
    
    @pytest.mark.asyncio
    async def test_csv_validation(self):
        """Test CSV format validation."""
        repository = CSVTransactionRepository()
        
        # Create a valid CSV file
        content = """Date,Description,Personal,Out,In
2024-01-01,Test transaction,,100.00,
2024-01-02,Another transaction,,,50.00"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write(content)
            f.flush()
            
            result = await repository.validate_csv_format(f.name)
            assert result.is_ok()
            
            # Test transaction count
            count_result = await repository.get_transaction_count(f.name)
            assert count_result.is_ok()
            assert count_result.value == 2
        
        os.unlink(f.name)


if __name__ == '__main__':
    # Run tests with asyncio
    pytest.main([__file__, "-v"])