import re
from typing import List, Tuple, Optional
from ..models import Transaction, ClassificationResult, ClassificationMethod
from ..utils.result import Result
from .base import BaseClassificationStrategy, ClassificationError


class RegexMatchStrategy(BaseClassificationStrategy):
    """Strategy for regex pattern matching."""
    
    def __init__(self, patterns: List[Tuple[str, str]]):
        super().__init__("regex_match", priority=2)
        self.patterns = [(re.compile(pattern), account) for pattern, account in patterns]
    
    async def classify(self, transaction: Transaction) -> Result[ClassificationResult, ClassificationError]:
        """Classify using regex pattern matching."""
        try:
            normalized_desc = self._normalize_description(transaction.description)
            
            for pattern, account in self.patterns:
                match = pattern.search(normalized_desc)
                if match:
                    # Handle special cases like {staff} substitution
                    processed_account = self._process_account_template(account, match)
                    
                    # Skip special cases that need more context
                    if processed_account == "INHERIT_FROM_BASE":
                        continue
                    
                    if processed_account:
                        result = ClassificationResult(
                            target_account=processed_account,
                            confidence=0.95,
                            method=ClassificationMethod.REGEX_MATCH,
                            reasoning=f"Regex match for pattern '{pattern.pattern}'",
                            metadata={
                                "pattern": pattern.pattern,
                                "match_groups": match.groups(),
                                "match_span": match.span()
                            }
                        )
                        return Result.ok(result)
            
            return Result.err(ClassificationError(f"No regex match found for '{normalized_desc}'"))
            
        except Exception as e:
            return Result.err(ClassificationError(f"Error in regex match strategy: {str(e)}"))
    
    def _process_account_template(self, account: str, match: re.Match) -> Optional[str]:
        """Process account template with match data."""
        if "{staff}" in account:
            staff_name = self._extract_staff_name(match)
            if staff_name:
                return account.replace("{staff}", staff_name.title())
            return None
        return account
    
    def _extract_staff_name(self, match: re.Match) -> Optional[str]:
        """Extract staff name from regex match groups."""
        try:
            for group in match.groups():
                if group and group.lower() in ["ara", "michelle", "marie"]:
                    return group.lower()
        except (AttributeError, IndexError):
            pass
        return None
    
    def add_pattern(self, pattern: str, account: str) -> None:
        """Add a new regex pattern."""
        self.patterns.append((re.compile(pattern), account))
    
    def get_pattern_count(self) -> int:
        """Get the number of patterns."""
        return len(self.patterns)