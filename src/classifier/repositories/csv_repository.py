import csv
from typing import List, Dict, Any
from pathlib import Path
import aiofiles
from pydantic import ValidationError

from ..models import RawTransaction, ClassifiedTransaction
from ..utils.result import Result
from .base import BaseTransactionRepository, RepositoryError


class CSVTransactionRepository(BaseTransactionRepository):
    """Repository for CSV-based transaction storage."""
    
    def __init__(self, encoding: str = "utf-8"):
        self.encoding = encoding
    
    async def read_transactions(self, source: str) -> Result[List[RawTransaction], RepositoryError]:
        """Read transactions from CSV file."""
        try:
            source_path = Path(source)
            if not source_path.exists():
                return Result.err(RepositoryError(f"Source file not found: {source}"))
            
            transactions = []
            async with aiofiles.open(source_path, mode='r', encoding=self.encoding) as file:
                content = await file.read()
                
            # Parse CSV content
            reader = csv.DictReader(content.splitlines())
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Map CSV columns to model fields
                    transaction_data = {
                        "date": row.get("Date", ""),
                        "description": row.get("Description", ""),
                        "personal": row.get("Personal"),
                        "out": self._parse_decimal(row.get("Out")),
                        "in": self._parse_decimal(row.get("In"))
                    }
                    
                    transaction = RawTransaction(**transaction_data)
                    transactions.append(transaction)
                    
                except ValidationError as e:
                    return Result.err(RepositoryError(f"Validation error in row {row_num}: {str(e)}"))
                except Exception as e:
                    return Result.err(RepositoryError(f"Error parsing row {row_num}: {str(e)}"))
            
            return Result.ok(transactions)
            
        except Exception as e:
            return Result.err(RepositoryError(f"Error reading CSV file: {str(e)}"))
    
    async def write_classifications(self, 
                                  classifications: List[ClassifiedTransaction], 
                                  destination: str) -> Result[bool, RepositoryError]:
        """Write classifications to CSV file."""
        try:
            destination_path = Path(destination)
            
            # Ensure parent directory exists
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare CSV data
            fieldnames = [
                "Date", "Description", "Out", "In", "Target Account",
                "Confidence", "Method", "Needs Review", "Reasoning"
            ]
            
            rows = []
            for classified in classifications:
                row = {
                    "Date": classified.date.isoformat(),
                    "Description": classified.description,
                    "Out": str(classified.amount) if classified.direction == "out" else "",
                    "In": str(classified.amount) if classified.direction == "in" else "",
                    "Target Account": classified.classification.target_account or "",
                    "Confidence": f"{classified.classification.confidence:.2f}",
                    "Method": classified.classification.method.value,
                    "Needs Review": classified.classification.needs_review,
                    "Reasoning": classified.classification.reasoning
                }
                rows.append(row)
            
            # Write to CSV
            async with aiofiles.open(destination_path, mode='w', encoding=self.encoding, newline='') as file:
                content = self._create_csv_content(fieldnames, rows)
                await file.write(content)
            
            return Result.ok(True)
            
        except Exception as e:
            return Result.err(RepositoryError(f"Error writing CSV file: {str(e)}"))
    
    def _parse_decimal(self, value: str) -> float | None:
        """Parse decimal value from string."""
        if not value or value.strip() == "":
            return None
        try:
            # Remove commas and quotes from monetary values
            cleaned_value = value.replace(",", "").replace('"', "").strip()
            return float(cleaned_value)
        except ValueError:
            return None
    
    def _create_csv_content(self, fieldnames: List[str], rows: List[Dict[str, Any]]) -> str:
        """Create CSV content string."""
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()
    
    async def validate_csv_format(self, source: str) -> Result[bool, RepositoryError]:
        """Validate CSV file format."""
        try:
            source_path = Path(source)
            if not source_path.exists():
                return Result.err(RepositoryError(f"Source file not found: {source}"))
            
            async with aiofiles.open(source_path, mode='r', encoding=self.encoding) as file:
                content = await file.read()
            
            reader = csv.DictReader(content.splitlines())
            required_columns = {"Date", "Description", "Out", "In"}
            available_columns = set(reader.fieldnames) if reader.fieldnames else set()
            
            if not required_columns.issubset(available_columns):
                missing = required_columns - available_columns
                return Result.err(RepositoryError(f"Missing required columns: {missing}"))
            
            return Result.ok(True)
            
        except Exception as e:
            return Result.err(RepositoryError(f"Error validating CSV format: {str(e)}"))
    
    async def get_transaction_count(self, source: str) -> Result[int, RepositoryError]:
        """Get the number of transactions in CSV file."""
        try:
            source_path = Path(source)
            if not source_path.exists():
                return Result.err(RepositoryError(f"Source file not found: {source}"))
            
            async with aiofiles.open(source_path, mode='r', encoding=self.encoding) as file:
                content = await file.read()
            
            reader = csv.DictReader(content.splitlines())
            count = sum(1 for _ in reader)
            
            return Result.ok(count)
            
        except Exception as e:
            return Result.err(RepositoryError(f"Error counting transactions: {str(e)}"))