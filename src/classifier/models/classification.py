from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class ClassificationMethod(str, Enum):
    """Method used for classification."""
    EXACT_MATCH = "exact_match"
    REGEX_MATCH = "regex_match"
    KEYWORD_MATCH = "keyword_match"
    LLM_CLASSIFICATION = "llm_classification"
    MANUAL_REVIEW = "manual_review"


class ClassificationResult(BaseModel):
    """Result of a transaction classification."""
    
    target_account: Optional[str] = Field(None, description="Target GnuCash account")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Classification confidence")
    method: ClassificationMethod = Field(..., description="Classification method used")
    reasoning: str = Field("", description="Explanation of classification")
    needs_review: bool = Field(False, description="Requires manual review")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Classification timestamp")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Validate confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v
    
    @validator('needs_review', always=True)
    def set_needs_review(cls, v, values):
        """Auto-set needs_review based on confidence."""
        confidence = values.get('confidence', 0.0)
        if confidence < 0.85:
            return True
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ClassifiedTransaction(BaseModel):
    """A transaction with its classification result."""
    
    transaction_id: str = Field(..., description="Unique transaction identifier")
    date: datetime = Field(..., description="Transaction date")
    description: str = Field(..., description="Transaction description")
    amount: Decimal = Field(..., description="Transaction amount")
    direction: str = Field(..., description="Transaction direction")
    classification: ClassificationResult = Field(..., description="Classification result")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }


class BatchClassificationResult(BaseModel):
    """Result of batch classification operation."""
    
    total_transactions: int = Field(..., description="Total number of transactions processed")
    successful_classifications: int = Field(..., description="Number of successful classifications")
    failed_classifications: int = Field(..., description="Number of failed classifications")
    needs_review_count: int = Field(..., description="Number of transactions needing review")
    processing_time_seconds: float = Field(..., description="Total processing time")
    results: list[ClassifiedTransaction] = Field(default_factory=list, description="Individual results")
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_transactions == 0:
            return 0.0
        return (self.successful_classifications / self.total_transactions) * 100
    
    @property
    def review_rate(self) -> float:
        """Calculate review rate as percentage."""
        if self.total_transactions == 0:
            return 0.0
        return (self.needs_review_count / self.total_transactions) * 100