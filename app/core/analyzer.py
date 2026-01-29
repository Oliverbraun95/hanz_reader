import jieba
import pandas as pd
import re
from typing import Dict, Any
from app.core.reference_loader import get_hsk_dataframe

class TextAnalyzer:
    def __init__(self):
        # Pre-load data to ensure fast first request
        self.hsk_df = get_hsk_dataframe()
        self._initialize_tokenizer()

    def _initialize_tokenizer(self):
        """
        Syncs HSK vocabulary with Jieba's dictionary.
        This provides a 'nudge' to the probabilistic tokenizer to prefer our known words.
        """
        # 1. Boost frequency of all HSK words
        # Note: This loops ~5000 times (HSK 6). inexpensive.
        for word in self.hsk_df.index:
            # We don't specify freq, let Jieba calculate a high default or use existing
            jieba.add_word(word)
            
        # 2. Handle specific "Sticky Words"
        # "这是" (This is) is extremely common in Jieba's default corpus and often wins 
        # against "这" + "是" even if we add them. We explicitly force the split.
        jieba.suggest_freq(('这', '是'), True)
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the input text for HSK difficulty.
        
        Args:
            text (str): The raw Chinese text.
            
        Returns:
            Dict: Analysis results including total tokens, coverage per level, and overall score.
        """
        if not text:
             return {"total_tokens": 0, "difficulty_score": "Unknown"}

        # 1. Segmentation
        tokens = jieba.lcut(text)
        
        # 2. Vectorized Analysis
        # Create a Series from tokens
        token_series = pd.Series(tokens, name='token')
        
        # Filter Punctuation/Spaces (simple regex for non-word chars, keeping it simple for now)
        # Assuming we want to keep Chinese characters mainly.
        # A common regex for Chinese is [\u4e00-\u9fff], but we might also want to match English words if they were in HSK (unlikely).
        # The prompt says: "Filter out punctuation/special characters."
        # Let's filter out anything that doesn't look like a word.
        # Actually, simpler is: we only care about what matches the HSK database?
        # No, "Lexical Density: Total words vs Unique words" implies we need a clean word list.
        
        # Let's remove punctuation using regex
        # This regex removes tokens that are purely punctuation/whitespace
        clean_tokens_mask = token_series.astype(str).str.match(r'^\w+$')
        # Note: \w in Python regex matches alphanumeric + underscore, including Chinese chars.
        # But commonly punctuation like '，' or '。' might not match \w depending on locale/implementation.
        # A safer check for Chinese punctuation:
        # Instead of strict filtering, let's keep everything that IS NOT purely punctuation.
        
        # Optimization: We can just use the HSK dataframe to find matches first.
        # But we need total count of "words" (meaningful tokens) for percentage.
        
        # Let's refine the mask to exclude common punctuation.
        # Or iterate over tokens and check? No, vectorized.
        # clean_tokens = token_series[token_series.str.isalnum()] # This usually works for Chinese chars too.
        # Let's try str.isalnum()
        
        # Wait, jieba.lcut returns a list.
        
        clean_tokens = token_series[token_series.str.strip().str.match(r'^[^\s\W]+$')]
        # This regex ^[^\s\W]+$ means: start, one or more chars that are NOT (whitespace or non-word), end.
        # Effectively alphanumeric.
        
        if clean_tokens.empty:
            return {"total_tokens": 0, "difficulty_score": "Unknown"}

        total_words = len(clean_tokens)
        unique_words = clean_tokens.nunique()
        
        # 3. Match against HSK Reference
        # We merge the clean tokens with the HSK dataframe.
        # token_series is the left side, hsk_df is the right side (index=word)
        
        # "Senior Data Engineer way": Convert input to DF/Series and join.
        token_df = pd.DataFrame(clean_tokens, columns=['token'])
        
        # Left join to preserve all words in text, but find HSK info where available
        merged_df = token_df.join(self.hsk_df, on='token', how='left')
        
        # Fill NaN levels with 0 (Unknown)
        merged_df['level'] = merged_df['level'].fillna(0).astype(int)
        
        # 4. Calculate Coverage
        # Value counts of 'level'
        level_counts = merged_df['level'].value_counts(normalize=True).sort_index()
        
        # Build counting dictionary
        coverage: Dict[str, float] = {}
        for level in range(1, 7):
            if level in level_counts:
                coverage[f"hsk_{level}_coverage"] = round(level_counts[level], 4)
            else:
                coverage[f"hsk_{level}_coverage"] = 0.0
                
        coverage["unknown_coverage"] = round(level_counts.get(0, 0.0), 4)

        # 5. Determine Difficulty Score
        # Simple heuristic: heavily weighted towards the highest level present? 
        # Or the level with majority? 
        # The prompt says: Returns difficulty score 'A1' etc.
        # Let's map HSK to CEFR or just return the dominant HSK level for now.
        # HSK 1 = A1, HSK 2 = A2, HSK 3 = B1, HSK 4 = B2, HSK 5 = C1, HSK 6 = C2.
        
        # Let's calculate the weighted average or just look at the distribution.
        # "Difficulty Analysis" object.
        # For simplicity in Sprint 1: The level with the highest cumulative coverage accumulating from bottom? 
        # Or just "The highest level that constitutes > X% of text?"
        # Let's use a simple Weighted Average Level for the "score" or just return the highest significant level.
        # Given "This text is 60% HSK1...", let's call it HSK1 if HSK1 is dominant.
        
        # Let's compute a weighted Score:
        # sum(level * count) / total_tokens? 
        # No, "Difficulty Score" usually implies the level required to understand the text.
        # If 20% is HSK6, it's hard.
        
        # Let's stick to the example output: "difficulty_score": "A1".
        # Mapping:
        # HSK1 -> A1
        # HSK2 -> A2
        # ...
        
        # Simple Algorithm:
        # If unknown > 50% -> Unknown
        # Else: 
        #   Take the weighted tail?
        #   Let's just take the max level that has non-trivial presence (e.g. > 5%)?
        #   Actually, let's keep it extremely simple: Level with max coverage -> Score.
        
        primary_level = 0
        max_cloud = 0.0
        # Check HSK 6 down to 1
        # If HSK 6 > 5%, it's C2.
        # If HSK 5 > 5%, it's C1...
        # This is a "Threshold" approach.
        
        # Let's assume a threshold of 10% for a level to "dictate" the difficulty?
        difficulty_map = {1: "A1", 2: "A2", 3: "B1", 4: "B2", 5: "C1", 6: "C2"}
        final_score = "A1" # Default
        
        cumulative = 0.0
        # Start from HSK1 and go up. When we cover say 80% of tokens, that's the level?
        # "You need top be at Level X to understand 80% of this text".
        # Yes, 80% comprehension is a standard metric.
        
        # Sort levels 1-6
        # Add unknown to the 'uncovered' part.
        # If Unknown is high, difficulty is "Unknown/High".
        
        current_coverage = 0.0
        target_comprehension = 0.80
        
        found_level = 1
        for lvl in range(1, 7):
            current_coverage += coverage.get(f"hsk_{lvl}_coverage", 0)
            if current_coverage >= target_comprehension:
                found_level = lvl
                break
            # If we sum 1-6 and don't reach 80%, it means "Unknown" is too high.
        
        if current_coverage < target_comprehension:
            # Too many unknown words
            final_score = "Unknown (>20%)"
        else:
            final_score = difficulty_map.get(found_level, "A1")
            
        result = {
            "total_tokens": int(total_words),
            "unique_words": int(unique_words),
            "difficulty_score": final_score
        }
        result.update(coverage)
        
        return result
