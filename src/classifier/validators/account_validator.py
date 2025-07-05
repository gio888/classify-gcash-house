from typing import Set, List, Optional
from pathlib import Path
from ..utils.result import Result


class AccountValidationError(Exception):
    """Exception for account validation errors."""
    pass


class AccountValidator:
    """Validator for GnuCash account paths."""
    
    def __init__(self, chart_of_accounts_path: str):
        self.chart_of_accounts_path = Path(chart_of_accounts_path)
        self._valid_accounts: Set[str] = set()
        self._account_hierarchy: dict = {}
        self._loaded = False
    
    async def load_chart_of_accounts(self) -> Result[bool, AccountValidationError]:
        """Load the chart of accounts from file."""
        try:
            if not self.chart_of_accounts_path.exists():
                return Result.err(AccountValidationError(f"Chart of accounts file not found: {self.chart_of_accounts_path}"))
            
            with open(self.chart_of_accounts_path, 'r', encoding='utf-8') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            self._valid_accounts = set(accounts)
            self._build_hierarchy(accounts)
            self._loaded = True
            
            return Result.ok(True)
            
        except Exception as e:
            return Result.err(AccountValidationError(f"Error loading chart of accounts: {str(e)}"))
    
    def _build_hierarchy(self, accounts: List[str]) -> None:
        """Build account hierarchy for validation."""
        self._account_hierarchy = {}
        
        for account in accounts:
            parts = account.split(':')
            current_level = self._account_hierarchy
            
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
    
    def validate_account(self, account: str) -> Result[bool, AccountValidationError]:
        """Validate that an account exists in the chart of accounts."""
        if not self._loaded:
            return Result.err(AccountValidationError("Chart of accounts not loaded"))
        
        if not account:
            return Result.err(AccountValidationError("Account path cannot be empty"))
        
        if account in self._valid_accounts:
            return Result.ok(True)
        
        return Result.err(AccountValidationError(f"Invalid account: {account}"))
    
    def validate_account_path(self, account: str) -> Result[bool, AccountValidationError]:
        """Validate account path structure."""
        if not account:
            return Result.err(AccountValidationError("Account path cannot be empty"))
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '|', '*', '?', '"']
        for char in invalid_chars:
            if char in account:
                return Result.err(AccountValidationError(f"Account path contains invalid character: {char}"))
        
        # Check colon structure
        if account.startswith(':') or account.endswith(':'):
            return Result.err(AccountValidationError("Account path cannot start or end with colon"))
        
        if '::' in account:
            return Result.err(AccountValidationError("Account path cannot contain double colons"))
        
        return Result.ok(True)
    
    def suggest_similar_accounts(self, account: str, max_suggestions: int = 5) -> List[str]:
        """Suggest similar account names for invalid accounts."""
        if not self._loaded:
            return []
        
        account_lower = account.lower()
        suggestions = []
        
        for valid_account in self._valid_accounts:
            if account_lower in valid_account.lower():
                suggestions.append(valid_account)
        
        # Sort by similarity (simple heuristic: shorter accounts first)
        suggestions.sort(key=len)
        
        return suggestions[:max_suggestions]
    
    def get_parent_account(self, account: str) -> Optional[str]:
        """Get the parent account for a given account."""
        if not self._loaded or account not in self._valid_accounts:
            return None
        
        parts = account.split(':')
        if len(parts) <= 1:
            return None
        
        parent = ':'.join(parts[:-1])
        return parent if parent in self._valid_accounts else None
    
    def get_child_accounts(self, account: str) -> List[str]:
        """Get all child accounts for a given account."""
        if not self._loaded or account not in self._valid_accounts:
            return []
        
        prefix = account + ':'
        children = [acc for acc in self._valid_accounts if acc.startswith(prefix)]
        
        return children
    
    def get_account_depth(self, account: str) -> int:
        """Get the depth of an account in the hierarchy."""
        if not account:
            return 0
        return len(account.split(':'))
    
    def get_root_accounts(self) -> List[str]:
        """Get all root-level accounts."""
        if not self._loaded:
            return []
        
        roots = []
        for account in self._valid_accounts:
            if ':' not in account:
                roots.append(account)
        
        return sorted(roots)
    
    def get_accounts_by_type(self, account_type: str) -> List[str]:
        """Get all accounts of a specific type (Assets, Liabilities, etc.)."""
        if not self._loaded:
            return []
        
        type_accounts = []
        for account in self._valid_accounts:
            if account.startswith(account_type + ':') or account == account_type:
                type_accounts.append(account)
        
        return sorted(type_accounts)
    
    def get_statistics(self) -> dict:
        """Get statistics about the chart of accounts."""
        if not self._loaded:
            return {}
        
        stats = {
            "total_accounts": len(self._valid_accounts),
            "root_accounts": len(self.get_root_accounts()),
            "max_depth": max(self.get_account_depth(acc) for acc in self._valid_accounts) if self._valid_accounts else 0,
            "account_types": {}
        }
        
        # Count accounts by type
        for account in self._valid_accounts:
            root = account.split(':')[0]
            stats["account_types"][root] = stats["account_types"].get(root, 0) + 1
        
        return stats