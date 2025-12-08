from __future__ import annotations

from typing import Optional
import logging

from .rag_fire_history import get_fire_history_context

logger = logging.getLogger(__name__)


def build_wildfire_llm_prompt(
    user_question: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    date_str: Optional[str] = None,
) -> str:
    """
    Build a final prompt for the wildfire LLM, optionally enriched with
    historical fire context from cached CSV exports.
    """
    context = ""
    if latitude is not None and longitude is not None:
        context = get_fire_history_context(
            latitude=latitude,
            longitude=longitude,
            date_str=date_str,
            radius_km=100.0,
            days_back=365,
            limit=20,
        )

    system_header = (
        "You are an AI assistant specialized in wildfire risk assessment. "
        "You can combine domain knowledge with structured historical data "
        "from satellite-based fire history CSVs."
    )

    if context:
        context_block = (
            "Use the following historical wildfire data as trusted context. "
            "If there is any conflict between this data and your prior knowledge, "
            "prefer the data shown here.\n\n"
            f"{context}\n\n"
            "Base your reasoning and explanations on these patterns where relevant."
        )
    else:
        context_block = (
            "No structured historical wildfire dataset was available for this query. "
            "Answer using your general knowledge of wildfire risk, and be explicit "
            "about any assumptions."
        )

    final_prompt = (
        f"{system_header}\n\n"
        f"{context_block}\n\n"
        f"User question:\n{user_question}\n"
    )
    return final_prompt
