from typing import Dict
from ..models import Transaction, ClassificationResult, ClassificationMethod
from ..utils.result import Result
from .base import BaseClassificationStrategy, ClassificationError


class ExactMatchStrategy(BaseClassificationStrategy):
    """Strategy for exact pattern matching."""
    
    def __init__(self, patterns: Dict[str, str]):
        super().__init__("exact_match", priority=1)
        self.patterns = {k.lower(): v for k, v in patterns.items()}
    
    async def classify(self, transaction: Transaction) -> Result[ClassificationResult, ClassificationError]:
        """Classify using exact pattern matching."""
        try:
            normalized_desc = self._normalize_description(transaction.description)
            
            if normalized_desc in self.patterns:
                result = ClassificationResult(
                    target_account=self.patterns[normalized_desc],
                    confidence=1.0,
                    method=ClassificationMethod.EXACT_MATCH,
                    reasoning=f"Exact match for '{normalized_desc}'",
                    metadata={"pattern": normalized_desc}
                )
                return Result.ok(result)
            
            return Result.err(ClassificationError(f"No exact match found for '{normalized_desc}'"))
            
        except Exception as e:
            return Result.err(ClassificationError(f"Error in exact match strategy: {str(e)}"))
    
    def add_pattern(self, pattern: str, account: str) -> None:
        """Add a new pattern."""
        self.patterns[pattern.lower()] = account
    
    def remove_pattern(self, pattern: str) -> bool:
        """Remove a pattern."""
        return self.patterns.pop(pattern.lower(), None) is not None
    
    def get_pattern_count(self) -> int:
        """Get the number of patterns."""
        return len(self.patterns)