from fastapi import APIRouter, Depends, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.openai_service import OpenAIService
from app.services.rate_limiter import check_rate_limit
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user = Depends(get_current_user),
    openai_service: OpenAIService = Depends()
):
    # Rate limit check
    await check_rate_limit(user.id)
    
    # Query OpenAI with file_search
    response = await openai_service.query_with_rag(request.question)
    
    return ChatResponse(
        answer=response.answer,
        sources=response.sources,
        confidence=response.confidence
    )