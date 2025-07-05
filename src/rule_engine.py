import re
from typing import Optional

from .models import ClassificationResult
from .rules import EXACT_PATTERNS, REGEX_PATTERNS, KEYWORD_RULES, CONFIDENCE_LEVELS


class RuleEngine:
    """Rule-based transaction classifier with three-tier matching system."""
    
    def __init__(self):
        self.exact_patterns = EXACT_PATTERNS
        self.regex_patterns = REGEX_PATTERNS
        self.keyword_rules = KEYWORD_RULES
        self.confidence_levels = CONFIDENCE_LEVELS
    
    def match(self, description: str) -> Optional[ClassificationResult]:
        """
        Attempt to classify a transaction description using rule-based matching.
        
        Args:
            description: The transaction description to classify
            
        Returns:
            ClassificationResult if a match is found, None otherwise
        """
        if not description:
            return None
        
        # Normalize the description for matching
        normalized_desc = self._normalize_description(description)
        
        # Try exact match first (highest confidence)
        result = self._try_exact_match(normalized_desc)
        if result:
            return result
        
        # Try regex patterns (medium-high confidence)
        result = self._try_regex_match(normalized_desc)
        if result:
            return result
        
        # Try keyword matching (medium confidence)
        result = self._try_keyword_match(normalized_desc)
        if result:
            return result
        
        # No match found
        return None
    
    def _normalize_description(self, description: str) -> str:
        """Normalize description for consistent matching."""
        # Convert to lowercase and strip whitespace
        normalized = description.lower().strip()
        
        # Normalize multiple spaces to single spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def _try_exact_match(self, description: str) -> Optional[ClassificationResult]:
        """Try exact pattern matching."""
        if description in self.exact_patterns:
            return ClassificationResult(
                target_account=self.exact_patterns[description],
                confidence=self.confidence_levels["exact"],
                reasoning=f"Exact match for '{description}'",
                method="exact_match"
            )
        return None
    
    def _try_regex_match(self, description: str) -> Optional[ClassificationResult]:
        """Try regex pattern matching."""
        for pattern, account in self.regex_patterns:
            match = re.search(pattern, description)
            if match:
                # Handle special cases like {staff} substitution
                if "{staff}" in account:
                    # Extract staff name from the match
                    staff_name = self._extract_staff_name(match)
                    if staff_name:
                        account = account.replace("{staff}", staff_name.title())
                    else:
                        continue  # Skip if we can't extract staff name
                
                # Handle special INHERIT_FROM_BASE case
                if account == "INHERIT_FROM_BASE":
                    # This would need context from the base transaction
                    # For now, we'll skip this pattern
                    continue
                
                return ClassificationResult(
                    target_account=account,
                    confidence=self.confidence_levels["regex"],
                    reasoning=f"Regex match for pattern '{pattern}'",
                    method="regex_match"
                )
        return None
    
    def _try_keyword_match(self, description: str) -> Optional[ClassificationResult]:
        """Try keyword-based matching."""
        for keyword, account in self.keyword_rules.items():
            if keyword.lower() in description:
                return ClassificationResult(
                    target_account=account,
                    confidence=self.confidence_levels["keyword"],
                    reasoning=f"Keyword match for '{keyword}'",
                    method="keyword_match"
                )
        return None
    
    def _extract_staff_name(self, match) -> Optional[str]:
        """Extract staff name from regex match groups."""
        try:
            # Look for staff names in the match groups
            for group in match.groups():
                if group and group.lower() in ["ara", "michelle", "marie"]:
                    return group.lower()
        except (AttributeError, IndexError):
            pass
        return None
    
    def add_rule(self, pattern: str, account: str, confidence: float, rule_type: str = "exact"):
        """Add a new rule to the engine."""
        if rule_type == "exact":
            self.exact_patterns[pattern.lower()] = account
        elif rule_type == "regex":
            self.regex_patterns.append((pattern, account))
        elif rule_type == "keyword":
            self.keyword_rules[pattern.lower()] = account
        else:
            raise ValueError(f"Unknown rule type: {rule_type}")
    
    def get_statistics(self) -> dict:
        """Get statistics about the loaded rules."""
        return {
            "exact_patterns": len(self.exact_patterns),
            "regex_patterns": len(self.regex_patterns),
            "keyword_rules": len(self.keyword_rules),
            "total_rules": len(self.exact_patterns) + len(self.regex_patterns) + len(self.keyword_rules)
        }