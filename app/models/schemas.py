from pydantic import BaseModel
from typing import Dict, Optional

class TextRequest(BaseModel):
    content: str
    target_level: str = "HSK2" # Optional in prompt implementation, but good to have

class AnalysisResult(BaseModel):
    total_tokens: int
    difficulty_score: str
    hsk_1_coverage: float = 0.0
    hsk_2_coverage: float = 0.0
    hsk_3_coverage: float = 0.0
    hsk_4_coverage: float = 0.0
    hsk_5_coverage: float = 0.0
    hsk_6_coverage: float = 0.0
    unknown_coverage: float = 0.0
