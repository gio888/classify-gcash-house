from abc import ABC, abstractmethod
from typing import Protocol, Optional
from ..models import Transaction, ClassificationResult
from ..utils.result import Result


class ClassificationError(Exception):
    """Base exception for classification errors."""
    pass


class ClassificationStrategy(Protocol):
    """Protocol for classification strategies."""
    
    async def classify(self, transaction: Transaction) -> Result[ClassificationResult, ClassificationError]:
        """Classify a transaction."""
        ...
    
    @property
    def name(self) -> str:
        """Strategy name."""
        ...
    
    @property
    def priority(self) -> int:
        """Strategy priority (lower number = higher priority)."""
        ...


class BaseClassificationStrategy(ABC):
    """Base class for classification strategies."""
    
    def __init__(self, name: str, priority: int):
        self._name = name
        self._priority = priority
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def priority(self) -> int:
        return self._priority
    
    @abstractmethod
    async def classify(self, transaction: Transaction) -> Result[ClassificationResult, ClassificationError]:
        """Classify a transaction."""
        pass
    
    def _normalize_description(self, description: str) -> str:
        """Normalize description for consistent matching."""
        import re
        normalized = description.lower().strip()
        return re.sub(r'\s+', ' ', normalized)