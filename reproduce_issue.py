import jieba
import sys
sys.path.append(".")
from app.core.analyzer import TextAnalyzer

analyzer = TextAnalyzer()

# Fix for "这是"
jieba.suggest_freq(('这', '是'), True)

cases = [
    "王明：这是？",
    "王明：是？"
]

print("Loading HSK Data...")
# We rely on existing CSVs.

for text in cases:
    print(f"\nScanning: '{text}'")
    tokens = jieba.lcut(text)
    print(f"Jieba Tokens: {tokens}")
    
    result = analyzer.analyze(text)
    print(f"Analysis Result: {result}")
