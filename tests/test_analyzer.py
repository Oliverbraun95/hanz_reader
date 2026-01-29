import unittest
import pandas as pd
import sys
# Add project root to path
sys.path.append(".")
from app.core.analyzer import TextAnalyzer

class TestTextAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TextAnalyzer()
        # Ensure our mock data is working via the setup, 
        # but the analyzer uses `reference_loader` which loads from disk.
        # The disk files are the dummy ones we created.
        
    def test_analyze_simple(self):
        # "你好, 我是学生."
        # Tokens (expected from jieba): 你好 (or 你, 好 depends on jieba), ,, 我, 是, 学生, .
        # In our CSV:
        # 你 (1), 好 (1), 我 (1), 是 (1), 学生 (1).
        # "你是学生" -> all HSK1.
        
        text = "你好, 我是学生." 
        # Note: Jieba might cut "你好" as one word. "你好" is typical greeting.
        # If "你好" is not in our CSV, it might be Unknown.
        # Our CSV has "你" and "好" separately.
        # Jieba usually cuts unique words. "你好" is often one token.
        # Let's use a sentence with clearly separate words in our dictionary, or update CSV.
        # Update: We created "ni" and "hao". 
        # Let's see what Jieba cuts.
        
        # Test input: "我 是 学生" (spaces help jieba sometimes, but it handles no spaces)
        # "我是学生" -> [我, 是, 学生] likely.
        
        text_simple = "我是学生"
        result = self.analyzer.analyze(text_simple)
        
        self.assertEqual(result["total_tokens"], 3)
        self.assertEqual(result["hsk_1_coverage"], 1.0)
        self.assertEqual(result["difficulty_score"], "A1")

    def test_analyze_mixed(self):
        # HSK1: 苹果 (Actually we put Apple in HSK2 in our mock)
        # HSK2: 苹果
        # HSK1: 我
        # Text: "我是苹果" -> I am an apple.
        # Tokens: 我 (1), 是 (1), 苹果 (2)
        # Total: 3
        # HSK1: 2/3 = 0.66
        # HSK2: 1/3 = 0.33
        
        text = "我是苹果"
        result = self.analyzer.analyze(text)
        
        self.assertEqual(result["total_tokens"], 3)
        self.assertAlmostEqual(result["hsk_1_coverage"], 0.6667, places=3)
        self.assertAlmostEqual(result["hsk_2_coverage"], 0.3333, places=3)
        # Difficulty: 
        # Cumul HSK1: 0.66. < 0.8
        # Cumul HSK1+2: 1.0 >= 0.8 -> Level 2 -> A2.
        self.assertEqual(result["difficulty_score"], "A2")

    def test_analyze_unknown(self):
        text = "StrangeWord 123 !!"
        # "StrangeWord" -> Unknown
        # "123" -> removed by regex/logic?
        # Clean tokens check.
        # "StrangeWord" is alphanumeric. 123 is alphanumeric.
        # Should be filtered? 
        # Implementation: regex `^[^\s\W]+$` keeps alphanumeric.
        # So "StrangeWord" and "123" are tokens.
        # Both unknown.
        
        result = self.analyzer.analyze(text)
        # If strict filtering of non-Chinese was used, total might be 0.
        # But we allowed alphanumeric.
        
        self.assertTrue(result["total_tokens"] > 0)
        self.assertEqual(result["hsk_1_coverage"], 0.0)
        self.assertTrue(result["unknown_coverage"] > 0.9) # 100%
        self.assertEqual(result["difficulty_score"], "Unknown (>20%)")

    def test_analyze_segmentation_fix(self):
        # Test case reported by user: "王明：这是？"
        # Should split "这是" into "这"(1) and "是"(1).
        # "王明" (Unknown), "这" (1), "是" (1).
        # Total tokens: 3.
        # HSK1 coverage: 2/3 = 0.66
        
        text = "王明：这是？"
        result = self.analyzer.analyze(text)
        
        # Check that we found 3 tokens (excluding punctuation)
        self.assertEqual(result["total_tokens"], 3)
        self.assertAlmostEqual(result["hsk_1_coverage"], 0.6667, places=3)

if __name__ == '__main__':
    unittest.main()
