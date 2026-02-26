from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..services.llm_prompt import build_wildfire_llm_prompt
from ..services.llm_wildfire import call_local_llm, DEFAULT_MODEL, OLLAMA_SEED

router = APIRouter(prefix="/ai-risk/chat", tags=["ai-risk-chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    question: str = Field(..., description="User question for the wildfire assistant")
    latitude: float | None = Field(None, ge=-90, le=90, description="Optional latitude")
    longitude: float | None = Field(None, ge=-180, le=180, description="Optional longitude")
    date: str | None = Field(None, description="Optional ISO date for contextual data")


class ChatResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=ChatResponse)
async def chat_with_wildfire_assistant(request: ChatRequest) -> ChatResponse:
    prompt = build_wildfire_llm_prompt(
        user_question=request.question,
        latitude=request.latitude,
        longitude=request.longitude,
        date_str=request.date,
    )

    payload: dict[str, Any] = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "system": "You are an AI assistant specialized in wildfire risk assessment.",
        "stream": False,
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 500,
    }

    if OLLAMA_SEED is not None:
        payload["seed"] = OLLAMA_SEED

    try:
        text = await call_local_llm(payload)
        answer = text.strip()
        if not answer:
            answer = "LLM returned an empty response."
        return ChatResponse(answer=answer)
    except ValueError as exc:
        logger.error("Wildfire chat LLM call failed: %s", exc)
        return ChatResponse(answer=f"LLM unavailable ({exc})")
