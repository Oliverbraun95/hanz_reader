import sys
import unittest
# Add project root to path
sys.path.append(".")
from app.core.reference_loader import get_word_level, load_hsk_data, get_hsk_dataframe

class TestReferenceLoader(unittest.TestCase):
    def setUp(self):
        # Force reload for test isolation if needed, but for read-only static data it's fine.
        pass

    def test_load_data(self):
        df = get_hsk_dataframe()
        self.assertFalse(df.empty, "DataFrame should not be empty")
        self.assertTrue('level' in df.columns, "DataFrame should have 'level' column")
        # Check index is 'word'
        self.assertEqual(df.index.name, 'word')

    def test_get_word_level(self):
        # Based on our dummy data
        # hsk1: 你, 好
        self.assertEqual(get_word_level("你"), 1)
        # hsk2: 苹果
        self.assertEqual(get_word_level("苹果"), 2)
        # Unknown
        self.assertEqual(get_word_level("unknown_word"), 0)

if __name__ == '__main__':
    unittest.main()
