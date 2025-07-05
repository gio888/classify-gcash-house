from typing import List, Optional
from pathlib import Path

from ..strategies import (
    ExactMatchStrategy, RegexMatchStrategy, KeywordMatchStrategy, ClassificationStrategy
)
from ..strategies.llm_strategy import LLMClassificationStrategy
from ..repositories import CSVTransactionRepository
from ..validators import AccountValidator
from ..infrastructure import TransactionLogger, configure_logging
from .classifier import TransactionClassifier

# Import rules from our rules file
from ..rules import EXACT_PATTERNS, REGEX_PATTERNS, KEYWORD_RULES


class ClassifierFactory:
    """Factory for creating configured TransactionClassifier instances."""
    
    @staticmethod
    async def create_classifier(
        chart_of_accounts_path: str,
        openai_api_key: Optional[str] = None,
        confidence_threshold: float = 0.85,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        enable_llm: bool = True
    ) -> TransactionClassifier:
        """Create a fully configured TransactionClassifier."""
        
        # Configure logging
        logger = configure_logging(log_level=log_level, log_file=log_file)
        transaction_logger = TransactionLogger(logger)
        
        # Create and load account validator
        account_validator = AccountValidator(chart_of_accounts_path)
        load_result = await account_validator.load_chart_of_accounts()
        if load_result.is_err():
            raise RuntimeError(f"Failed to load chart of accounts: {load_result.error}")
        
        # Create classification strategies
        strategies: List[ClassificationStrategy] = []
        
        # Rule-based strategies
        strategies.append(ExactMatchStrategy(EXACT_PATTERNS))
        strategies.append(RegexMatchStrategy(REGEX_PATTERNS))
        strategies.append(KeywordMatchStrategy(KEYWORD_RULES))
        
        # LLM strategy (if enabled and API key provided)
        if enable_llm and openai_api_key:
            llm_strategy = LLMClassificationStrategy(
                api_key=openai_api_key,
                account_validator=account_validator
            )
            strategies.append(llm_strategy)
        
        # Create repository
        repository = CSVTransactionRepository()
        
        # Create classifier
        classifier = TransactionClassifier(
            strategies=strategies,
            repository=repository,
            account_validator=account_validator,
            logger=transaction_logger,
            confidence_threshold=confidence_threshold
        )
        
        return classifier
    
    @staticmethod
    async def create_minimal_classifier(chart_of_accounts_path: str) -> TransactionClassifier:
        """Create a minimal classifier with only rule-based strategies."""
        return await ClassifierFactory.create_classifier(
            chart_of_accounts_path=chart_of_accounts_path,
            enable_llm=False
        )
    
    @staticmethod
    async def create_development_classifier(
        chart_of_accounts_path: str,
        openai_api_key: Optional[str] = None
    ) -> TransactionClassifier:
        """Create a classifier configured for development."""
        return await ClassifierFactory.create_classifier(
            chart_of_accounts_path=chart_of_accounts_path,
            openai_api_key=openai_api_key,
            confidence_threshold=0.7,  # Lower threshold for development
            log_level="DEBUG",
            enable_llm=True
        )
    
    @staticmethod
    async def create_production_classifier(
        chart_of_accounts_path: str,
        openai_api_key: str,
        log_file: str
    ) -> TransactionClassifier:
        """Create a classifier configured for production."""
        return await ClassifierFactory.create_classifier(
            chart_of_accounts_path=chart_of_accounts_path,
            openai_api_key=openai_api_key,
            confidence_threshold=0.85,
            log_level="INFO",
            log_file=log_file,
            enable_llm=True
        )