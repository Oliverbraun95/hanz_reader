from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.analyzer import TextAnalyzer
from app.core.scraper import WebScraper
from app.models.schemas import TextRequest, UrlRequest, AnalysisResult

app = FastAPI(title="Hanz Reader Analysis Service")

# Initialize Analyzer and Scraper
analyzer = TextAnalyzer()
scraper = WebScraper()

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def read_root():
    return FileResponse('app/static/index.html')

@app.post("/api/v1/analyze", response_model=AnalysisResult)
async def analyze_text(request: TextRequest):
    """
    Analyze the difficulty of the provided Chinese text.
    """
    if not request.content:
        return AnalysisResult(
            total_tokens=0,
            difficulty_score="Unknown",
            hsk_1_coverage=0.0
        )
    
    try:
        result_dict = analyzer.analyze(request.content)
        # Convert dict to Pydantic model (Pydantic does this mostly automatically if keys match)
        return AnalysisResult(**result_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze/url", response_model=AnalysisResult)
async def analyze_url(request: UrlRequest):
    """
    Fetches content from a URL and analyzes its difficulty.
    """
    if not request.url:
         raise HTTPException(status_code=400, detail="URL is required")

    # 1. Scrape
    scrape_result = scraper.fetch_and_extract(request.url)
    
    if scrape_result.get("error"):
        raise HTTPException(status_code=400, detail=f"Scraping failed: {scrape_result['error']}")
        
    content = scrape_result.get("content", "")
    if not content:
         raise HTTPException(status_code=422, detail="Unable to extract meaningful content from the URL.")
         
    # 2. Analyze
    try:
        analysis = analyzer.analyze(content)
        
        # 3. Combine with metadata
        result = AnalysisResult(**analysis)
        result.title = scrape_result.get("title")
        result.url = scrape_result.get("url")
        
        return result
        
    except Exception as e:
        # Log error in real app
        raise HTTPException(status_code=500, detail=str(e))
