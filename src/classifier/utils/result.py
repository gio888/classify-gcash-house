from typing import Generic, TypeVar, Union
from pydantic import BaseModel

T = TypeVar('T')
E = TypeVar('E', bound=Exception)


class Result(BaseModel, Generic[T, E]):
    """Result type for handling success/failure without exceptions."""
    
    success: bool
    value: T | None = None
    error: E | None = None
    
    @classmethod
    def ok(cls, value: T) -> 'Result[T, E]':
        """Create a successful result."""
        return cls(success=True, value=value)
    
    @classmethod
    def err(cls, error: E) -> 'Result[T, E]':
        """Create a failed result."""
        return cls(success=False, error=error)
    
    def is_ok(self) -> bool:
        """Check if the result is successful."""
        return self.success
    
    def is_err(self) -> bool:
        """Check if the result is an error."""
        return not self.success
    
    def unwrap(self) -> T:
        """Get the value, raising an exception if it's an error."""
        if self.is_err():
            raise self.error
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """Get the value or return a default if it's an error."""
        return self.value if self.is_ok() else default
    
    def map(self, func):
        """Transform the value if successful."""
        if self.is_ok():
            return Result.ok(func(self.value))
        return Result.err(self.error)
    
    def and_then(self, func):
        """Chain operations that return Results."""
        if self.is_ok():
            return func(self.value)
        return Result.err(self.error)
    
    class Config:
        arbitrary_types_allowed = True