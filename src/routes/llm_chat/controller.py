import logging
from fastapi import APIRouter, status, HTTPException
from routes.llm_chat.models import ChatRequest, ChatResponse
from utils.setup import get_llm

logger = logging.getLogger(__name__)

chat_router = APIRouter()

@chat_router.post("/chat", status_code=status.HTTP_201_CREATED)
async def llm_chat(msg: str) -> ChatResponse:
    """
    Send generic message to llm chat to respond too
    """

    request = ChatRequest(msg=msg)

    try:
        logger.info(f"Recieved chat request: {request.msg[:50]}")
        llm = get_llm(model_type="llm")

        resp = await llm.ainvoke(request.msg)

        # Handle different response types
        if hasattr(resp, 'content'):
            response_text = resp.content
        else:
            response_text = str(resp)

        logger.info(f"Generated response: {response_text[:50]}...")

        return ChatResponse(
            msg=response_text,
        )
    except HTTPException as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )