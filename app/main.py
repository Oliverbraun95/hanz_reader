from fastapi import FastAPI, HTTPException
from app.core.analyzer import TextAnalyzer
from app.models.schemas import TextRequest, AnalysisResult

app = FastAPI(title="Hanz Reader Analysis Service")

# Initialize Analyzer (Singleton-ish via module level instance or dependency)
# Ideally use Depends, but for simplicity here:
analyzer = TextAnalyzer()

@app.get("/")
def read_root():
    return {"message": "Service is running. Use /api/v1/analyze for text analysis."}

@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_text(request: TextRequest):
    """
    Analyze the difficulty of the provided Chinese text.
    """
    if not request.content:
        # Return empty result or error? Schema says return result.
        return {
            "total_tokens": 0,
            "difficulty_score": "Unknown",
            "hsk_1_coverage": 0.0,
            "hsk_2_coverage": 0.0,
            "hsk_3_coverage": 0.0,
            "hsk_4_coverage": 0.0,
            "hsk_5_coverage": 0.0,
            "hsk_6_coverage": 0.0,
            "unknown_coverage": 0.0
        }
    
    try:
        result = analyzer.analyze(request.content)
        # result is a dict, Pydantic will validate it against AnalysisResult
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
