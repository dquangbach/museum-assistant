"""Public question answering API; Gemini credentials stay on the server."""
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.rag.answer import answer_question

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    topic_id: str | None = Field(default=None, pattern=r"^TOPIC[0-9]{3}$")


class ChatSource(BaseModel):
    chunk_id: str
    topic_id: str
    title: str
    image_urls: list[str]
    image_names: list[str]


class ChatResponse(BaseModel):
    answer: str
    answered: bool
    sources: list[ChatSource]


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, request: Request):
    settings = request.app.state.settings
    if not settings.gemini_api_key:
        raise HTTPException(503, "Trợ lý chưa được cấu hình GEMINI_API_KEY trên server.")
    try:
        return answer_question(payload.question.strip(), payload.topic_id,
                               settings.dataset_dir, settings.gemini_api_key, settings.gemini_model)
    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(502, "Trợ lý chưa thể trả lời lúc này.")
