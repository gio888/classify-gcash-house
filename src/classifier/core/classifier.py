import asyncio
import time
import uuid
from typing import List, Optional
from decimal import Decimal

from ..models import (
    Transaction, RawTransaction, ClassifiedTransaction, 
    BatchClassificationResult, ClassificationResult, TransactionDirection
)
from ..strategies import ClassificationStrategy
from ..repositories import TransactionRepository
from ..validators import AccountValidator
from ..infrastructure import TransactionLogger, bind_context, create_request_id
from ..utils.result import Result


class ClassificationError(Exception):
    """Exception for classification errors."""
    pass


class TransactionClassifier:
    """Main orchestrator for transaction classification with dependency injection."""
    
    def __init__(self,
                 strategies: List[ClassificationStrategy],
                 repository: TransactionRepository,
                 account_validator: AccountValidator,
                 logger: Optional[TransactionLogger] = None,
                 confidence_threshold: float = 0.85):
        
        # Sort strategies by priority (lower number = higher priority)
        self.strategies = sorted(strategies, key=lambda s: s.priority)
        self.repository = repository
        self.account_validator = account_validator
        self.logger = logger or TransactionLogger()
        self.confidence_threshold = confidence_threshold
        
        # Statistics tracking
        self.stats = {
            "total_processed": 0,
            "successful_classifications": 0,
            "failed_classifications": 0,
            "strategy_usage": {strategy.name: 0 for strategy in self.strategies}
        }
    
    async def classify_transaction(self, transaction: Transaction) -> Result[ClassificationResult, ClassificationError]:
        """Classify a single transaction using available strategies."""
        
        # Generate transaction ID if not present
        if not transaction.transaction_id:
            transaction.transaction_id = str(uuid.uuid4())[:8]
        
        # Bind context for logging
        bind_context(transaction_id=transaction.transaction_id)
        
        start_time = time.perf_counter()
        
        self.logger.log_transaction_start(
            transaction.transaction_id, 
            transaction.description, 
            float(transaction.amount)
        )
        
        # Try each strategy in priority order
        for strategy in self.strategies:
            strategy_start_time = time.perf_counter()
            
            self.logger.log_classification_attempt(
                transaction.transaction_id,
                strategy.name,
                strategy.priority
            )
            
            try:
                result = await strategy.classify(transaction)
                processing_time = (time.perf_counter() - strategy_start_time) * 1000
                
                if result.is_ok():
                    classification = result.value
                    
                    # Validate account if present
                    if classification.target_account:
                        validation_result = self.account_validator.validate_account(classification.target_account)
                        if validation_result.is_err():
                            suggestions = self.account_validator.suggest_similar_accounts(classification.target_account)
                            self.logger.log_account_validation_error(
                                transaction.transaction_id,
                                classification.target_account,
                                suggestions
                            )
                            classification.needs_review = True
                            classification.confidence = min(classification.confidence, 0.7)
                    
                    # Check confidence threshold
                    if classification.confidence >= self.confidence_threshold:
                        self.logger.log_classification_success(
                            transaction.transaction_id,
                            strategy.name,
                            classification.target_account or "None",
                            classification.confidence,
                            processing_time
                        )
                        
                        self.stats["successful_classifications"] += 1
                        self.stats["strategy_usage"][strategy.name] += 1
                        
                        return Result.ok(classification)
                
                # Strategy didn't produce a confident result, try next strategy
                self.logger.log_classification_failure(
                    transaction.transaction_id,
                    strategy.name,
                    result.error.args[0] if result.is_err() else "Low confidence",
                    processing_time
                )
                
            except Exception as e:
                processing_time = (time.perf_counter() - strategy_start_time) * 1000
                self.logger.log_classification_failure(
                    transaction.transaction_id,
                    strategy.name,
                    str(e),
                    processing_time
                )
        
        # No strategy succeeded
        total_time = (time.perf_counter() - start_time) * 1000
        self.stats["failed_classifications"] += 1
        
        fallback_result = ClassificationResult(
            target_account=None,
            confidence=0.0,
            method="manual_review",
            reasoning="No classification strategy succeeded",
            needs_review=True,
            metadata={"processing_time_ms": total_time}
        )
        
        return Result.ok(fallback_result)
    
    async def classify_batch(self, source_file: str, output_file: str) -> Result[BatchClassificationResult, ClassificationError]:
        """Classify a batch of transactions from CSV file."""
        
        batch_id = create_request_id()
        bind_context(batch_id=batch_id)
        
        start_time = time.perf_counter()
        
        try:
            # Read transactions
            read_result = await self.repository.read_transactions(source_file)
            if read_result.is_err():
                return Result.err(ClassificationError(f"Failed to read transactions: {read_result.error}"))
            
            raw_transactions = read_result.value
            
            self.logger.log_batch_processing_start(batch_id, len(raw_transactions), source_file)
            
            # Convert and classify transactions
            classified_transactions = []
            successful_count = 0
            failed_count = 0
            
            # Process transactions with concurrency control
            semaphore = asyncio.Semaphore(10)  # Limit concurrent operations
            
            async def process_transaction(raw_tx: RawTransaction) -> Optional[ClassifiedTransaction]:
                async with semaphore:
                    try:
                        # Convert raw transaction to Transaction
                        transaction = raw_tx.to_transaction()
                        
                        # Classify transaction
                        classification_result = await self.classify_transaction(transaction)
                        
                        if classification_result.is_ok():
                            return ClassifiedTransaction(
                                transaction_id=transaction.transaction_id or str(uuid.uuid4())[:8],
                                date=transaction.date,
                                description=transaction.description,
                                amount=transaction.amount,
                                direction=transaction.direction.value,
                                classification=classification_result.value
                            )
                    except Exception as e:
                        self.logger.log_error("transaction_processing_error", str(e), {
                            "raw_transaction": raw_tx.dict()
                        })
                    return None
            
            # Process all transactions concurrently
            tasks = [process_transaction(raw_tx) for raw_tx in raw_transactions]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect results
            for result in results:
                if isinstance(result, ClassifiedTransaction):
                    classified_transactions.append(result)
                    successful_count += 1
                else:
                    failed_count += 1
            
            # Write results
            if classified_transactions:
                write_result = await self.repository.write_classifications(classified_transactions, output_file)
                if write_result.is_err():
                    return Result.err(ClassificationError(f"Failed to write results: {write_result.error}"))
            
            processing_time = time.perf_counter() - start_time
            
            # Create batch result
            batch_result = BatchClassificationResult(
                total_transactions=len(raw_transactions),
                successful_classifications=successful_count,
                failed_classifications=failed_count,
                needs_review_count=sum(1 for ct in classified_transactions if ct.classification.needs_review),
                processing_time_seconds=processing_time,
                results=classified_transactions
            )
            
            self.logger.log_batch_processing_complete(
                batch_id,
                batch_result.total_transactions,
                batch_result.successful_classifications,
                batch_result.failed_classifications,
                batch_result.processing_time_seconds
            )
            
            # Update global stats
            self.stats["total_processed"] += len(raw_transactions)
            
            return Result.ok(batch_result)
            
        except Exception as e:
            return Result.err(ClassificationError(f"Batch processing failed: {str(e)}"))
    
    def add_strategy(self, strategy: ClassificationStrategy) -> None:
        """Add a new classification strategy."""
        self.strategies.append(strategy)
        self.strategies.sort(key=lambda s: s.priority)
        self.stats["strategy_usage"][strategy.name] = 0
    
    def remove_strategy(self, strategy_name: str) -> bool:
        """Remove a classification strategy by name."""
        for i, strategy in enumerate(self.strategies):
            if strategy.name == strategy_name:
                del self.strategies[i]
                if strategy_name in self.stats["strategy_usage"]:
                    del self.stats["strategy_usage"][strategy_name]
                return True
        return False
    
    def get_statistics(self) -> dict:
        """Get classification statistics."""
        total_attempts = self.stats["successful_classifications"] + self.stats["failed_classifications"]
        success_rate = (self.stats["successful_classifications"] / max(total_attempts, 1)) * 100
        
        return {
            **self.stats,
            "success_rate_percent": round(success_rate, 2),
            "active_strategies": len(self.strategies),
            "strategy_names": [s.name for s in self.strategies]
        }
    
    def reset_statistics(self) -> None:
        """Reset classification statistics."""
        self.stats = {
            "total_processed": 0,
            "successful_classifications": 0,
            "failed_classifications": 0,
            "strategy_usage": {strategy.name: 0 for strategy in self.strategies}
        }