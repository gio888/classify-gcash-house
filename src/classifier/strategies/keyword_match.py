from typing import Dict
from ..models import Transaction, ClassificationResult, ClassificationMethod
from ..utils.result import Result
from .base import BaseClassificationStrategy, ClassificationError


class KeywordMatchStrategy(BaseClassificationStrategy):
    """Strategy for keyword-based matching."""
    
    def __init__(self, keywords: Dict[str, str]):
        super().__init__("keyword_match", priority=3)
        self.keywords = {k.lower(): v for k, v in keywords.items()}
    
    async def classify(self, transaction: Transaction) -> Result[ClassificationResult, ClassificationError]:
        """Classify using keyword matching."""
        try:
            normalized_desc = self._normalize_description(transaction.description)
            
            # Find all matching keywords
            matches = []
            for keyword, account in self.keywords.items():
                if keyword in normalized_desc:
                    matches.append((keyword, account))
            
            if not matches:
                return Result.err(ClassificationError(f"No keyword match found for '{normalized_desc}'"))
            
            # Use the longest keyword match (most specific)
            best_match = max(matches, key=lambda x: len(x[0]))
            keyword, account = best_match
            
            result = ClassificationResult(
                target_account=account,
                confidence=0.85,
                method=ClassificationMethod.KEYWORD_MATCH,
                reasoning=f"Keyword match for '{keyword}'",
                metadata={
                    "keyword": keyword,
                    "all_matches": [match[0] for match in matches]
                }
            )
            return Result.ok(result)
            
        except Exception as e:
            return Result.err(ClassificationError(f"Error in keyword match strategy: {str(e)}"))
    
    def add_keyword(self, keyword: str, account: str) -> None:
        """Add a new keyword."""
        self.keywords[keyword.lower()] = account
    
    def remove_keyword(self, keyword: str) -> bool:
        """Remove a keyword."""
        return self.keywords.pop(keyword.lower(), None) is not None
    
    def get_keyword_count(self) -> int:
        """Get the number of keywords."""
        return len(self.keywords)