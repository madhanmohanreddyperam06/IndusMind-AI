"""REST API routes for hybrid retrieval."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.api.dependencies import get_current_active_user
from app.modules.hybrid_retrieval.service import HybridRetrievalService
from app.models.user import User
from app.modules.hybrid_retrieval.schemas import (
    RetrievalRequest,
    RetrievalResponse,
    ContextRequest,
    ContextResponse,
    QueryAnalysisRequest,
    QueryAnalysisResponse,
    QueryExpansionRequest,
    QueryExpansionResponse,
    HealthCheckResponse,
    StatisticsResponse,
    ConfigResponse,
    TestRequest,
    TestResponse,
    DebugRequest,
    DebugResponse
)
from app.core.logging import setup_logging

logger = setup_logging()

router = APIRouter()


def get_hybrid_retrieval_service(db: Session = Depends(get_db)) -> HybridRetrievalService:
    """Get hybrid retrieval service instance.
    
    Args:
        db: Database session
        
    Returns:
        Hybrid retrieval service
    """
    return HybridRetrievalService(db)


@router.post("/query", response_model=RetrievalResponse)
async def query(
    request: RetrievalRequest,
    service: HybridRetrievalService = Depends(get_hybrid_retrieval_service),
    current_user: User = Depends(get_current_active_user)
) -> RetrievalResponse:
    """Execute hybrid retrieval query.
    
    Args:
        request: Retrieval request
        service: Hybrid retrieval service
        
    Returns:
        Retrieval response with merged and ranked evidence
    """
    try:
        return service.query(request)
    except Exception as e:
        logger.error(f"Query endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/context", response_model=ContextResponse)
async def generate_context(
    request: ContextRequest,
    service: HybridRetrievalService = Depends(get_hybrid_retrieval_service),
    current_user: User = Depends(get_current_active_user)
) -> ContextResponse:
    """Generate context package for RAG.
    
    Args:
        request: Context generation request
        service: Hybrid retrieval service
        
    Returns:
        Context response with structured context package
    """
    try:
        return service.generate_context(request)
    except Exception as e:
        logger.error(f"Context generation endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=QueryAnalysisResponse)
async def analyze(
    request: QueryAnalysisRequest,
    service: HybridRetrievalService = Depends(get_hybrid_retrieval_service),
    current_user: User = Depends(get_current_active_user)
) -> QueryAnalysisResponse:
    """Analyze a user query.
    
    Args:
        request: Query analysis request
        service: Hybrid retrieval service
        
    Returns:
        Query analysis response with detected entities and intent
    """
    try:
        return service.analyze(request)
    except Exception as e:
        logger.error(f"Query analysis endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/expand", response_model=QueryExpansionResponse)
async def expand(
    request: QueryExpansionRequest,
    service: HybridRetrievalService = Depends(get_hybrid_retrieval_service),
    current_user: User = Depends(get_current_active_user)
) -> QueryExpansionResponse:
    """Expand a query with industrial terminology.
    
    Args:
        request: Query expansion request
        service: Hybrid retrieval service
        
    Returns:
        Query expansion response with expanded terms
    """
    try:
        return service.expand(request)
    except Exception as e:
        logger.error(f"Query expansion endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    service: HybridRetrievalService = Depends(get_hybrid_retrieval_service)
) -> HealthCheckResponse:
    """Health check for all retrieval components.
    
    Args:
        service: Hybrid retrieval service
        
    Returns:
        Health check response
    """
    try:
        return service.health_check()
    except Exception as e:
        logger.error(f"Health check endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    service: HybridRetrievalService = Depends(get_hybrid_retrieval_service),
    current_user: User = Depends(get_current_active_user)
) -> StatisticsResponse:
    """Get retrieval statistics.
    
    Args:
        service: Hybrid retrieval service
        
    Returns:
        Statistics response
    """
    try:
        return service.get_statistics()
    except Exception as e:
        logger.error(f"Statistics endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=ConfigResponse)
async def get_config(
    service: HybridRetrievalService = Depends(get_hybrid_retrieval_service),
    current_user: User = Depends(get_current_active_user)
) -> ConfigResponse:
    """Get default configuration.
    
    Args:
        service: Hybrid retrieval service
        
    Returns:
        Configuration response
    """
    try:
        return service.get_config()
    except Exception as e:
        logger.error(f"Config endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=TestResponse)
async def test(
    request: TestRequest,
    service: HybridRetrievalService = Depends(get_hybrid_retrieval_service),
    current_user: User = Depends(get_current_active_user)
) -> TestResponse:
    """Test retrieval with specified sources.
    
    Args:
        request: Test request
        service: Hybrid retrieval service
        
    Returns:
        Test response with source-specific results
    """
    try:
        return service.test(request)
    except Exception as e:
        logger.error(f"Test endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug", response_model=DebugResponse)
async def debug(
    request: DebugRequest,
    service: HybridRetrievalService = Depends(get_hybrid_retrieval_service),
    current_user: User = Depends(get_current_active_user)
) -> DebugResponse:
    """Debug retrieval with detailed intermediate results.
    
    Args:
        request: Debug request
        service: Hybrid retrieval service
        
    Returns:
        Debug response with detailed information
    """
    try:
        return service.debug(request)
    except Exception as e:
        logger.error(f"Debug endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
