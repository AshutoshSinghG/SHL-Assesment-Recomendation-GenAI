"""
FastAPI application for SHL Assessment Recommendation System.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from .recommend import RecommendationEngine

load_dotenv()

app = FastAPI(
    title="SHL Assessment Recommendation API",
    description="AI-powered recommendation system for SHL assessments",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommendation engine
recommendation_engine = None

def get_engine():
    """Lazy initialization of recommendation engine."""
    global recommendation_engine
    if recommendation_engine is None:
        try:
            enable_reranking = os.getenv("ENABLE_RERANKING", "true").lower() == "true"
            recommendation_engine = RecommendationEngine(enable_reranking=enable_reranking)
        except Exception as e:
            print(f"Error initializing recommendation engine: {e}")
            raise
    return recommendation_engine


class RecommendationRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10


class AssessmentRecommendation(BaseModel):
    assessment_name: str
    assessment_url: str
    test_type: str
    description: Optional[str] = None


class RecommendationResponse(BaseModel):
    recommendations: List[AssessmentRecommendation]
    query: str
    count: int


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_assessments(request: RecommendationRequest):
    """
    Get SHL assessment recommendations for a given query or job description.
    
    Args:
        request: Request containing query text and optional top_k parameter
        
    Returns:
        List of recommended assessments
    """
    try:
        engine = get_engine()
        recommendations = engine.recommend(request.query, top_k=request.top_k)
        
        return RecommendationResponse(
            recommendations=recommendations,
            query=request.query,
            count=len(recommendations)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "SHL Assessment Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

