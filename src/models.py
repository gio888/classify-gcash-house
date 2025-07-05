from dataclasses import dataclass
from typing import Optional


@dataclass
class ClassificationResult:
    """Result of a transaction classification attempt."""
    target_account: Optional[str] = None
    confidence: float = 0.0
    reasoning: str = ""
    needs_review: bool = False
    method: str = "unknown"
    
    def __post_init__(self):
        """Validate and set defaults after initialization."""
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        # Auto-set needs_review if confidence is low
        if self.confidence < 0.85:
            self.needs_review = True