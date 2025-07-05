import asyncio
from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from ..models import Transaction, ClassificationResult, ClassificationMethod
from ..utils.result import Result
from ..infrastructure.circuit_breaker import CircuitBreaker
from ..validators import AccountValidator
from .base import BaseClassificationStrategy, ClassificationError


class LLMClassificationStrategy(BaseClassificationStrategy):
    """Strategy for LLM-based classification using OpenAI."""
    
    def __init__(self, 
                 api_key: str,
                 account_validator: AccountValidator,
                 model: str = "gpt-3.5-turbo",
                 max_tokens: int = 150,
                 temperature: float = 0.1):
        super().__init__("llm_classification", priority=4)
        self.client = AsyncOpenAI(api_key=api_key)
        self.account_validator = account_validator
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Circuit breaker for API failures
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout_duration=60,
            expected_exception=Exception
        )
        
        # Cache for repeated classifications
        self._cache: Dict[str, ClassificationResult] = {}
        self._cache_max_size = 1000
    
    async def classify(self, transaction: Transaction) -> Result[ClassificationResult, ClassificationError]:
        """Classify using LLM with circuit breaker protection."""
        try:
            # Check cache first
            cache_key = self._get_cache_key(transaction)
            if cache_key in self._cache:
                cached_result = self._cache[cache_key]
                cached_result.metadata["from_cache"] = True
                return Result.ok(cached_result)
            
            # Use circuit breaker for API call
            result = await self.circuit_breaker.call(self._classify_with_llm, transaction)
            
            if result.is_ok():
                # Cache the result
                self._cache_result(cache_key, result.value)
                return result
            else:
                return Result.err(ClassificationError(f"LLM classification failed: {result.error}"))
                
        except Exception as e:
            return Result.err(ClassificationError(f"Error in LLM classification: {str(e)}"))
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _classify_with_llm(self, transaction: Transaction) -> ClassificationResult:
        """Perform LLM classification with retry logic."""
        prompt = self._build_prompt(transaction)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = self._parse_llm_response(response, transaction)
            
            # Validate the account if provided
            if result.target_account:
                validation_result = self.account_validator.validate_account(result.target_account)
                if validation_result.is_err():
                    # Account is invalid, suggest alternatives
                    suggestions = self.account_validator.suggest_similar_accounts(result.target_account)
                    result.needs_review = True
                    result.confidence = min(result.confidence, 0.7)
                    result.reasoning += f" (Invalid account, suggestions: {suggestions[:3]})"
            
            return result
            
        except Exception as e:
            raise ClassificationError(f"LLM API call failed: {str(e)}")
    
    def _build_prompt(self, transaction: Transaction) -> str:
        """Build the prompt for LLM classification."""
        return f"""
        Classify this financial transaction into a GnuCash account.
        
        Transaction Details:
        - Description: {transaction.description}
        - Amount: {transaction.amount}
        - Direction: {transaction.direction.value}
        - Date: {transaction.date.isoformat()}
        
        Please analyze the transaction and provide a JSON response with:
        - target_account: The most appropriate GnuCash account path
        - confidence: A score from 0.0 to 1.0 indicating classification confidence
        - reasoning: A brief explanation of why this account was chosen
        
        Consider the transaction direction when selecting accounts:
        - For outgoing transactions: Use Expenses:* accounts
        - For incoming transactions: Use Income:* or Assets:* accounts for transfers
        - For staff reimbursements: Use Assets:Loans to:* accounts
        
        Focus on the most specific account possible based on the description.
        """
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for LLM classification."""
        return """
        You are a financial transaction classifier specialized in GnuCash accounting.
        
        Key Classification Rules:
        1. Staff names (ara, michelle, marie) → Expenses:Household Staff:[Name]:*
        2. Child name (alessi) → Expenses:Childcare:*
        3. Pet name (shadow) → Expenses:Household Supplies:Pet Expenses
        4. Food/grocery stores → Expenses:Food:*
        5. Medical/pharmacy → Expenses:Health:*
        6. Transportation → Expenses:Transportation:*
        7. Utilities → Expenses:Utilities:*
        8. Reimbursements → Assets:Loans to:*
        
        Always respond with valid JSON containing target_account, confidence, and reasoning.
        Be conservative with confidence scores - use lower scores when uncertain.
        """
    
    def _parse_llm_response(self, response, transaction: Transaction) -> ClassificationResult:
        """Parse LLM response into ClassificationResult."""
        try:
            import json
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            return ClassificationResult(
                target_account=parsed.get("target_account"),
                confidence=float(parsed.get("confidence", 0.5)),
                method=ClassificationMethod.LLM_CLASSIFICATION,
                reasoning=parsed.get("reasoning", "LLM classification"),
                metadata={
                    "model": self.model,
                    "usage": response.usage.dict() if response.usage else {},
                    "raw_response": content
                }
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback for invalid JSON responses
            return ClassificationResult(
                target_account=None,
                confidence=0.0,
                method=ClassificationMethod.LLM_CLASSIFICATION,
                reasoning=f"Failed to parse LLM response: {str(e)}",
                needs_review=True,
                metadata={"parse_error": str(e)}
            )
    
    def _get_cache_key(self, transaction: Transaction) -> str:
        """Generate cache key for transaction."""
        return f"{transaction.description.lower().strip()}:{transaction.direction.value}:{transaction.amount}"
    
    def _cache_result(self, key: str, result: ClassificationResult) -> None:
        """Cache a classification result."""
        # Simple LRU cache implementation
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        
        self._cache[key] = result
    
    def get_circuit_breaker_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return self.circuit_breaker.get_stats()
    
    def reset_circuit_breaker(self) -> None:
        """Reset the circuit breaker."""
        self.circuit_breaker.reset()
    
    def clear_cache(self) -> None:
        """Clear the classification cache."""
        self._cache.clear()
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "cache_size": len(self._cache),
            "cache_max_size": self._cache_max_size,
            "cache_hit_rate": getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_requests', 1), 1)
        }