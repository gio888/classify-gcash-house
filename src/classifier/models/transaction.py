from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class TransactionDirection(str, Enum):
    """Direction of transaction flow."""
    OUTGOING = "out"
    INCOMING = "in"


class Transaction(BaseModel):
    """A financial transaction to be classified."""
    
    date: datetime = Field(..., description="Transaction date")
    description: str = Field(..., min_length=1, description="Transaction description")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    direction: TransactionDirection = Field(..., description="Transaction direction")
    transaction_id: Optional[str] = Field(None, description="Unique transaction identifier")
    
    @validator('description')
    def validate_description(cls, v):
        """Validate and normalize description."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }


class RawTransaction(BaseModel):
    """Raw transaction data from CSV input."""
    
    date: str = Field(..., description="Date string from CSV")
    description: str = Field(..., description="Description from CSV")
    personal: Optional[str] = Field(None, description="Personal field (ignored)")
    out: Optional[Decimal] = Field(None, description="Outgoing amount")
    in_: Optional[Decimal] = Field(None, alias="in", description="Incoming amount")
    
    @validator('description')
    def validate_description(cls, v):
        """Validate description is not empty."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()
    
    def to_transaction(self) -> Transaction:
        """Convert raw transaction to normalized Transaction."""
        # Determine direction and amount
        if self.out is not None and self.in_ is not None:
            raise ValueError("Transaction cannot have both in and out amounts")
        
        if self.out is not None:
            amount = self.out
            direction = TransactionDirection.OUTGOING
        elif self.in_ is not None:
            amount = self.in_
            direction = TransactionDirection.INCOMING
        else:
            raise ValueError("Transaction must have either in or out amount")
        
        # Parse date - support multiple formats
        try:
            # Try ISO format first
            parsed_date = datetime.fromisoformat(self.date)
        except ValueError:
            try:
                # Try M/D/YYYY format
                from datetime import datetime as dt
                parsed_date = dt.strptime(self.date, "%m/%d/%Y")
            except ValueError:
                try:
                    # Try MM/DD/YYYY format
                    parsed_date = dt.strptime(self.date, "%m/%d/%Y")
                except ValueError:
                    raise ValueError(f"Invalid date format: {self.date}. Supported formats: YYYY-MM-DD, M/D/YYYY")
        
        return Transaction(
            date=parsed_date,
            description=self.description,
            amount=amount,
            direction=direction
        )