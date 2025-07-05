import structlog
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path


def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_logs: bool = True
) -> structlog.stdlib.BoundLogger:
    """Configure structured logging for the application."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper())
    )
    
    # Create processors chain
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="ISO"),
    ]
    
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Set up file logging if specified
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    return structlog.get_logger()


class TransactionLogger:
    """Logger specifically for transaction processing with context."""
    
    def __init__(self, logger: Optional[structlog.stdlib.BoundLogger] = None):
        self.logger = logger or structlog.get_logger()
    
    def log_transaction_start(self, transaction_id: str, description: str, amount: float) -> None:
        """Log the start of transaction processing."""
        self.logger.info(
            "transaction_processing_started",
            transaction_id=transaction_id,
            description=description[:50] + "..." if len(description) > 50 else description,
            amount=float(amount),
            timestamp=datetime.now().isoformat()
        )
    
    def log_classification_attempt(self, 
                                 transaction_id: str, 
                                 strategy_name: str, 
                                 strategy_priority: int) -> None:
        """Log a classification attempt."""
        self.logger.debug(
            "classification_attempt",
            transaction_id=transaction_id,
            strategy=strategy_name,
            priority=strategy_priority
        )
    
    def log_classification_success(self, 
                                 transaction_id: str,
                                 strategy_name: str,
                                 target_account: str,
                                 confidence: float,
                                 processing_time_ms: float) -> None:
        """Log successful classification."""
        self.logger.info(
            "classification_success",
            transaction_id=transaction_id,
            strategy=strategy_name,
            target_account=target_account,
            confidence=confidence,
            processing_time_ms=processing_time_ms
        )
    
    def log_classification_failure(self, 
                                 transaction_id: str,
                                 strategy_name: str,
                                 error: str,
                                 processing_time_ms: float) -> None:
        """Log classification failure."""
        self.logger.warning(
            "classification_failure",
            transaction_id=transaction_id,
            strategy=strategy_name,
            error=error,
            processing_time_ms=processing_time_ms
        )
    
    def log_circuit_breaker_event(self, 
                                service: str, 
                                state: str, 
                                failure_count: int) -> None:
        """Log circuit breaker state changes."""
        self.logger.warning(
            "circuit_breaker_event",
            service=service,
            state=state,
            failure_count=failure_count
        )
    
    def log_batch_processing_start(self, 
                                 batch_id: str, 
                                 transaction_count: int,
                                 source_file: str) -> None:
        """Log the start of batch processing."""
        self.logger.info(
            "batch_processing_started",
            batch_id=batch_id,
            transaction_count=transaction_count,
            source_file=source_file,
            timestamp=datetime.now().isoformat()
        )
    
    def log_batch_processing_complete(self, 
                                    batch_id: str,
                                    total_transactions: int,
                                    successful_classifications: int,
                                    failed_classifications: int,
                                    processing_time_seconds: float) -> None:
        """Log batch processing completion."""
        success_rate = (successful_classifications / total_transactions * 100) if total_transactions > 0 else 0
        
        self.logger.info(
            "batch_processing_complete",
            batch_id=batch_id,
            total_transactions=total_transactions,
            successful_classifications=successful_classifications,
            failed_classifications=failed_classifications,
            success_rate=round(success_rate, 2),
            processing_time_seconds=processing_time_seconds,
            transactions_per_second=round(total_transactions / max(processing_time_seconds, 0.001), 2)
        )
    
    def log_account_validation_error(self, 
                                   transaction_id: str,
                                   invalid_account: str,
                                   suggestions: list) -> None:
        """Log account validation errors."""
        self.logger.warning(
            "account_validation_error",
            transaction_id=transaction_id,
            invalid_account=invalid_account,
            suggestions=suggestions[:3]  # Limit suggestions in logs
        )
    
    def log_performance_metric(self, 
                             metric_name: str, 
                             value: float, 
                             context: Dict[str, Any] = None) -> None:
        """Log performance metrics."""
        log_data = {
            "metric": metric_name,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        if context:
            log_data.update(context)
        
        self.logger.info("performance_metric", **log_data)
    
    def log_error(self, 
                 error_type: str, 
                 error_message: str, 
                 context: Dict[str, Any] = None) -> None:
        """Log errors with context."""
        log_data = {
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        if context:
            log_data.update(context)
        
        self.logger.error("application_error", **log_data)


def get_transaction_logger() -> TransactionLogger:
    """Get a configured transaction logger."""
    return TransactionLogger()


def create_request_id() -> str:
    """Create a unique request ID for tracing."""
    import uuid
    return str(uuid.uuid4())[:8]


def bind_context(**kwargs) -> None:
    """Bind context variables to the logger."""
    structlog.contextvars.bind_contextvars(**kwargs)