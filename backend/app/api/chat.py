from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm_service import process_chat_message
from app.core.database import get_db

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    status: str = "success"

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # User ID 1 is the default guest/admin user (doctor@test.com)
        user_id = 1 
        
        result = await process_chat_message(
            user_message=request.message, 
            session_id=request.session_id,
            user_id=user_id
        )
        return ChatResponse(
            response=result["response"] or "No response generated.",
            session_id=result["session_id"]
        )
    except Exception as e:
        print(f"API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
