from abc import ABC, abstractmethod
from typing import Protocol, List
from ..models import RawTransaction, ClassifiedTransaction
from ..utils.result import Result


class RepositoryError(Exception):
    """Base exception for repository errors."""
    pass


class TransactionRepository(Protocol):
    """Protocol for transaction repositories."""
    
    async def read_transactions(self, source: str) -> Result[List[RawTransaction], RepositoryError]:
        """Read transactions from source."""
        ...
    
    async def write_classifications(self, 
                                  classifications: List[ClassifiedTransaction], 
                                  destination: str) -> Result[bool, RepositoryError]:
        """Write classifications to destination."""
        ...


class BaseTransactionRepository(ABC):
    """Base class for transaction repositories."""
    
    @abstractmethod
    async def read_transactions(self, source: str) -> Result[List[RawTransaction], RepositoryError]:
        """Read transactions from source."""
        pass
    
    @abstractmethod
    async def write_classifications(self, 
                                  classifications: List[ClassifiedTransaction], 
                                  destination: str) -> Result[bool, RepositoryError]:
        """Write classifications to destination."""
        pass