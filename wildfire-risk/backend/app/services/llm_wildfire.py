import json
import logging
from typing import Any, Dict
import re
from time import monotonic

import httpx
from httpx import HTTPStatusError, RequestError

from ..core.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)
OLLAMA_URL = (
    # Allow overriding the Ollama endpoint via environment variable, so
    # Docker containers can talk to the host (e.g. host.docker.internal).
    getattr(settings, "ollama_url", None)
    or "http://host.docker.internal:11434/api/generate"
)
OLLAMA_API_BASE = OLLAMA_URL.split("/api/")[0] + "/api"
DEFAULT_MODEL = "mistral:latest"
OLLAMA_SEED = getattr(settings, "ollama_seed", None)
CACHE_TTL_SECONDS = 300  # 5 minutes
PROMPT_VERSION = "v1"  # bump to invalidate cache when prompt changes

# Simple in-memory cache: key -> (expires_at, payload)
_llm_cache: dict[tuple, tuple[float, Dict[str, Any]]] = {}


async def call_local_llm(payload: Dict[str, Any]) -> str:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)
            response.raise_for_status()
            data = response.json()
    except (HTTPStatusError, RequestError) as exc:
        logger.error("LLM request failed: %s", exc)
        raise ValueError(f"LLM request failed: {exc}") from exc
    except ValueError as exc:
        logger.error("LLM response decode failed: %s", exc)
        raise ValueError("LLM response decode failed") from exc

    text = data.get("response", "")
    if not isinstance(text, str):
        text = str(text)
    if not text.strip():
        raise ValueError("LLM response is empty")
    return text


async def list_local_llm_models() -> list[str]:
    # Start with user-provided endpoints (env/config), then fall back to common hosts.
    configured = list(getattr(settings, "ollama_tag_endpoints", []) or [])

    # If an explicit ollama_url is provided, also probe its /tags endpoint.
    if getattr(settings, "ollama_url", None):
        base = settings.ollama_url
        if base.endswith("/api/generate"):
            configured.insert(0, base.replace("/api/generate", "/api/tags"))
        elif "/api" in base:
            configured.insert(0, base.split("/api")[0].rstrip("/") + "/api/tags")
        else:
            configured.insert(0, base.rstrip("/") + "/api/tags")

    fallback = [
        f"{OLLAMA_API_BASE}/tags",  # host.docker.internal (default)
        "http://localhost:11434/api/tags",  # local host
        "http://host.docker.internal:11434/api/tags",  # host from container
        "http://ollama:11434/api/tags",  # common docker service name
    ]

    seen_urls: set[str] = set()
    tag_urls = []
    for url in configured + fallback:
        if url and url not in seen_urls:
            seen_urls.add(url)
            tag_urls.append(url)

    seen_models: set[str] = set()
    models: list[str] = []

    for url in tag_urls:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
        except (HTTPStatusError, RequestError) as exc:
            logger.warning("LLM models list failed for %s: %s", url, exc)
            continue

        if isinstance(data, dict) and isinstance(data.get("models"), list):
            for item in data["models"]:
                name = item.get("name") if isinstance(item, dict) else None
                if isinstance(name, str) and name not in seen_models:
                    seen_models.add(name)
                    models.append(name)

    return models


async def estimate_wildfire_risk_llm(
    temperature_c: float,
    wind_speed_kmh: float,
    relative_humidity_percent: float,
    rain_last_24h_mm: float,
    model: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> Dict[str, Any]:
    """Use local LLM (Ollama) to estimate wildfire risk.

    Returns a dict with keys:
    - wildfire_probability_percent: int 0-100
    - explanation: English explanation string
    """

    system_prompt = (
        "You are an AI model that provides a concise assessment of wildfire ignition risk. "
        "Use weather plus factors like vegetation abundance/dryness, human presence, and lightning where relevant. "
        "If a location is provided, tailor the explanation to it. "
        "Your answer MUST be a single valid JSON object with fields \"wildfire_probability_percent\" (0-100 integer) and \"explanation\" (English). "
        "Do not use ellipsis (...), avoid quotes inside the explanation text, and output nothing outside the JSON object."
    )

    location_line = "Location not provided" if latitude is None or longitude is None else f"Location: lat {latitude:.4f}, lon {longitude:.4f}"

    user_prompt = f"""
Estimate the relative risk of a vegetation or forest wildfire in percent based on the following parameters:

- Air temperature: {temperature_c:.1f} °C
- Wind speed: {wind_speed_kmh:.1f} km/h
- Relative humidity (RH): {relative_humidity_percent:.1f} %
- Rainfall during the last 24 hours: {rain_last_24h_mm:.1f} mm
- {location_line}

Guidance: be location-aware if coordinates are given; consider weather plus vegetation moisture/abundance, human presence, and lightning; avoid long prose.

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

    def _round(value: float | None) -> float | None:
        return None if value is None else round(value, 4)

    cache_key = (
        PROMPT_VERSION,
        model or DEFAULT_MODEL,
        _round(temperature_c),
        _round(wind_speed_kmh),
        _round(relative_humidity_percent),
        _round(rain_last_24h_mm),
        _round(latitude),
        _round(longitude),
        OLLAMA_SEED,
    )

    now = monotonic()
    cached = _llm_cache.get(cache_key)
    if cached and cached[0] > now:
        return dict(cached[1])

    payload: Dict[str, Any] = {
        "model": model or DEFAULT_MODEL,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False,
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 300,
    }

    if OLLAMA_SEED is not None:
        payload["seed"] = OLLAMA_SEED

    try:
        raw_text = await call_local_llm(payload)
    except ValueError as exc:
        logger.error("LLM call failed: %s", exc)
        return {
            "wildfire_probability_percent": 0,
            "explanation": "The AI explanation service is currently unavailable.",
        }

    text = raw_text.strip()

    # Try to parse JSON directly, fall back to extracting and sanitizing JSON object
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = text[start : end + 1]

            # Broad sanitization: remove ellipsis, smart quotes, and control chars
            json_str = json_str.replace("…", " ")
            json_str = json_str.replace("...", " ")
            json_str = json_str.replace("“", '"').replace("”", '"').replace("’", "'")
            json_str = re.sub(r"[\u0000-\u001F]", " ", json_str)

            # Attempt strict JSON parse first
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                # Regex-based tolerant extraction
                prob_match = re.search(r'"wildfire_probability_percent"\s*:\s*([0-9]+(?:\.[0-9]+)?)(?:\s*%)?', json_str)
                expl_match = re.search(r'"explanation"\s*:\s*"(.*)"', json_str, re.DOTALL)

                if not expl_match:
                    # fallback: capture after key even if quotes are broken
                    expl_match = re.search(r'explanation\s*:\s*(.+)', json_str, re.DOTALL)

                if prob_match:
                    try:
                        prob_val = float(prob_match.group(1))
                    except ValueError:
                        prob_val = 0.0
                else:
                    prob_val = 0.0

                if expl_match:
                    expl_val = expl_match.group(1)
                    # strip trailing braces/commas/quotes
                    expl_val = expl_val.strip().strip('"').strip("',}). ")
                else:
                    expl_val = "The AI explanation service returned an invalid response."

                data = {
                    "wildfire_probability_percent": prob_val,
                    "explanation": expl_val.strip(),
                }
                logger.warning("LLM JSON recovered via tolerant parse: prob=%s text=%s", prob_val, expl_val[:200])
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

    result = {
        "wildfire_probability_percent": prob,
        "explanation": explanation or "The AI explanation service returned an invalid response.",
    }

    _llm_cache[cache_key] = (now + CACHE_TTL_SECONDS, result)

    return result
    return {
        "wildfire_probability_percent": prob,
        "explanation": explanation,
    }
