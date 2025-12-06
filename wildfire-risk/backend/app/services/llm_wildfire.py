import json
import logging
from typing import Any, Dict

import httpx

from ..core.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)
OLLAMA_URL = (
    # Allow overriding the Ollama endpoint via environment variable, so
    # Docker containers can talk to the host (e.g. host.docker.internal).
    getattr(settings, "ollama_url", None)
    or "http://host.docker.internal:11434/api/generate"
)
DEFAULT_MODEL = "llama3.2:latest"


async def call_local_llm(payload: Dict[str, Any]) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        # Ollama /generate with stream=false returns JSON
        data = response.json()
        text = data.get("response", "")
        if not isinstance(text, str):
            text = str(text)
        return text


async def estimate_wildfire_risk_llm(
    temperature_c: float,
    wind_speed_kmh: float,
    relative_humidity_percent: float,
    rain_last_24h_mm: float,
    model: str | None = None,
) -> Dict[str, Any]:
    """Use local LLM (Ollama) to estimate wildfire risk.

    Returns a dict with keys:
    - wildfire_probability_percent: int 0-100
    - explanation: English explanation string
    """

    system_prompt = (
        "You are an AI model that provides a rough assessment of the risk "
        "of vegetation and forest fires based on environmental parameters. "
        "You are NOT a real-time warning system and do not replace official fire warnings.\n\n"
        "Your answer MUST be a single valid JSON object with the fields "
        "\"wildfire_probability_percent\" (integer 0-100) and \"explanation\" (English text). "
        "No additional text, no comments, nothing outside this JSON object."
    )

    user_prompt = f"""
Estimate the relative risk of a vegetation or forest wildfire in percent based on the following parameters:

- Air temperature: {temperature_c:.1f} °C
- Wind speed: {wind_speed_kmh:.1f} km/h
- Relative humidity (RH): {relative_humidity_percent:.1f} %
- Rainfall during the last 24 hours: {rain_last_24h_mm:.1f} mm

Return the result strictly as JSON in the following format:

{{
  "wildfire_probability_percent": <INTEGER_BETWEEN_0_AND_100>,
  "explanation": "<ENGLISH_TEXT_EXPLAINING_WHY_THE_VALUE_IS_HIGH_OR_LOW>"
}}

Requirements:
- "wildfire_probability_percent" is an integer between 0 and 100.
- "explanation" uses clear, well-structured English sentences explaining how temperature, wind, humidity, and rainfall contribute to the risk.
- Do not mention yourself as an AI, do not add disclaimers, only provide a factual explanation.
""".strip()

    payload: Dict[str, Any] = {
        "model": model or DEFAULT_MODEL,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False,
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": 300,
    }

    raw_text = await call_local_llm(payload)
    text = raw_text.strip()

    # Try to parse JSON directly, fall back to extracting and sanitizing JSON object
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = text[start : end + 1]

            # Simple sanitization for common LLM issues (e.g. trailing ellipsis)
            # Example: "..." at the end of explanation
            json_str = json_str.replace("...\"", "\"")

            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                logger.error("LLM JSON parse failed after sanitization: %s", json_str[:300])
                return {
                    "wildfire_probability_percent": 0,
                    "explanation": "The AI explanation service returned an invalid response.",
                }
        else:
            logger.error("LLM response is not valid JSON: %s", text[:300])
            return {
                "wildfire_probability_percent": 0,
                "explanation": "The AI explanation service returned an invalid response.",
            }

    prob_raw = data.get("wildfire_probability_percent", 0)
    try:
        prob = int(prob_raw)
    except (TypeError, ValueError):
        prob = 0

    explanation = str(data.get("explanation", "")).strip()

    prob = max(0, min(100, prob))

    return {
        "wildfire_probability_percent": prob,
        "explanation": explanation,
    }
