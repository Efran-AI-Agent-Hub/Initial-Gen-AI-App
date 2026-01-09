from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """
    Request model for chatting with LLM
    """
    msg: str = Field(..., description="User message to send to LLM")
    stream: bool = Field(False, description="Determine to stream mgm from LLM")

    model_config = {
        "example": {
            "msg": "Hello chatbot, what is 2 + 2?",
            "stream": False,
        }
    }

class ChatResponse(BaseModel):
    """
    LLM response model
    """
    msg: str = Field(..., description="Response message")