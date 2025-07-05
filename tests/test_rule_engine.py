import unittest
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rule_engine import RuleEngine
from models import ClassificationResult


class TestRuleEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.rule_engine = RuleEngine()
    
    def test_exact_match_grab_car(self):
        """Test exact match for 'grab car'."""
        result = self.rule_engine.match("grab car")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.target_account, "Expenses:Transportation:Public")
        self.assertEqual(result.confidence, 1.0)
        self.assertEqual(result.method, "exact_match")
        self.assertFalse(result.needs_review)
    
    def test_exact_match_mam_b_fund(self):
        """Test exact match for 'mam b fund'."""
        result = self.rule_engine.match("mam b fund")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.target_account, "Assets:Current Assets:Banks Local:BPI Savings (BE)")
        self.assertEqual(result.confidence, 1.0)
        self.assertEqual(result.method, "exact_match")
        self.assertFalse(result.needs_review)
    
    def test_regex_match_tennis_alessi(self):
        """Test regex match for 'tennis alessi'."""
        result = self.rule_engine.match("tennis alessi")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.target_account, "Expenses:Childcare:Extracurricular Activities")
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.method, "regex_match")
        self.assertFalse(result.needs_review)
    
    def test_regex_match_mercury_drug(self):
        """Test regex match for 'mercury drug'."""
        result = self.rule_engine.match("mercury drug")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.target_account, "Expenses:Health:Medicines")
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.method, "regex_match")
        self.assertFalse(result.needs_review)
    
    def test_case_insensitive_matching(self):
        """Test that matching is case insensitive."""
        # Test uppercase
        result = self.rule_engine.match("GRAB CAR")
        self.assertIsNotNone(result)
        self.assertEqual(result.target_account, "Expenses:Transportation:Public")
        
        # Test mixed case
        result = self.rule_engine.match("Mam B Fund")
        self.assertIsNotNone(result)
        self.assertEqual(result.target_account, "Assets:Current Assets:Banks Local:BPI Savings (BE)")
    
    def test_whitespace_normalization(self):
        """Test that extra whitespace is handled properly."""
        # Test extra spaces
        result = self.rule_engine.match("  grab   car  ")
        self.assertIsNotNone(result)
        self.assertEqual(result.target_account, "Expenses:Transportation:Public")
    
    def test_keyword_match_alessi(self):
        """Test keyword matching for 'alessi'."""
        result = self.rule_engine.match("alessi")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.target_account, "Expenses:Childcare:Others")
        self.assertEqual(result.confidence, 0.85)
        self.assertEqual(result.method, "keyword_match")
        self.assertTrue(result.needs_review)  # Should need review due to low confidence
    
    def test_no_match(self):
        """Test that unknown descriptions return None."""
        result = self.rule_engine.match("unknown transaction description")
        self.assertIsNone(result)
    
    def test_empty_description(self):
        """Test that empty descriptions return None."""
        result = self.rule_engine.match("")
        self.assertIsNone(result)
        
        result = self.rule_engine.match(None)
        self.assertIsNone(result)
    
    def test_rule_engine_statistics(self):
        """Test that statistics are properly reported."""
        stats = self.rule_engine.get_statistics()
        
        self.assertIn("exact_patterns", stats)
        self.assertIn("regex_patterns", stats)
        self.assertIn("keyword_rules", stats)
        self.assertIn("total_rules", stats)
        
        # Check that we have some rules loaded
        self.assertGreater(stats["exact_patterns"], 0)
        self.assertGreater(stats["regex_patterns"], 0)
        self.assertGreater(stats["keyword_rules"], 0)
        self.assertGreater(stats["total_rules"], 0)
    
    def test_priority_matching(self):
        """Test that exact matches take priority over regex/keyword matches."""
        # Add a test case where the same text could match multiple patterns
        # Since "alessi" is both in exact patterns and keyword rules, 
        # we need to check that exact match takes priority
        
        # For now, let's test that exact match works when there's also a keyword match
        result = self.rule_engine.match("aquaflask alessi")
        self.assertIsNotNone(result)
        self.assertEqual(result.target_account, "Expenses:Household Supplies")
        self.assertEqual(result.method, "exact_match")
        self.assertEqual(result.confidence, 1.0)


if __name__ == '__main__':
    unittest.main()