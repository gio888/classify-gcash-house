import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Any, Optional
from ..utils.result import Result


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerError(Exception):
    """Exception for circuit breaker errors."""
    pass


class CircuitBreaker:
    """Circuit breaker implementation for handling external service failures."""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 timeout_duration: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.timeout_duration = timeout_duration
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
        
    async def call(self, func: Callable, *args, **kwargs) -> Result[Any, Exception]:
        """Execute a function with circuit breaker protection."""
        
        # Check circuit breaker state
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                return Result.err(CircuitBreakerError("Circuit breaker is OPEN"))
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - reset circuit breaker
            self._on_success()
            return Result.ok(result)
            
        except self.expected_exception as e:
            # Expected failure - record and check threshold
            self._on_failure()
            return Result.err(e)
            
        except Exception as e:
            # Unexpected error - don't trigger circuit breaker
            return Result.err(e)
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker."""
        if self.last_failure_time is None:
            return True
        
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_duration)
    
    def _on_success(self) -> None:
        """Handle successful execution."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = None
    
    def _on_failure(self) -> None:
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
    
    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self.state
    
    def get_failure_count(self) -> int:
        """Get current failure count."""
        return self.failure_count
    
    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        self.last_failure_time = None
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "timeout_duration": self.timeout_duration,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
        }