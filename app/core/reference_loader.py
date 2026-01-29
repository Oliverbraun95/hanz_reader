import pandas as pd
import pathlib
import os

HSK_LEVELS_DIR = pathlib.Path(__file__).parent.parent / "data" / "hsk_levels"

def load_hsk_data() -> pd.DataFrame:
    """
    Loads HSK 1-6 CSV files into a single Pandas DataFrame.
    Optimized for lookup by setting 'word' as the index.
    
    Returns:
        pd.DataFrame: Columns [level, pinyin, meaning], Index [word]
    """
    dfs = []
    
    # Iterate through HSK 1-6
    for level in range(1, 7):
        file_path = HSK_LEVELS_DIR / f"hsk{level}.csv"
        if not file_path.exists():
            # In production we might log a warning or error, for now skip or raise
            continue
            
        try:
            df = pd.read_csv(file_path)
            # Add level column if it doesn't exist (assuming CSVs don't have it)
            df['level'] = level
            dfs.append(df)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    if not dfs:
        return pd.DataFrame()

    full_df = pd.concat(dfs, ignore_index=True)
    
    # Clean duplicates? Assuming words are unique across levels or we take higher/lower?
    # For now, drop duplicates keeping first.
    full_df.drop_duplicates(subset=['word'], inplace=True)
    
    # Set index to 'word' for O(1) lookups
    full_df.set_index('word', inplace=True)
    
    return full_df

_hsk_cache = None

def get_hsk_dataframe() -> pd.DataFrame:
    """Singleton accessor for HSK data."""
    global _hsk_cache
    if _hsk_cache is None:
        _hsk_cache = load_hsk_data()
    return _hsk_cache

def get_word_level(word: str) -> int:
    """
    Look up valid HSK words. Returns level (1-6) or 0 if not found.
    (This function is mainly for testing/individual lookup, but vectorization is preferred)
    """
    df = get_hsk_dataframe()
    if word in df.index:
        return int(df.at[word, 'level'])
    return 0
