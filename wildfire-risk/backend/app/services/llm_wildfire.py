import json
import logging
from typing import Any, Dict
import re
from time import monotonic

import httpx
from httpx import HTTPStatusError, RequestError

from ..core.config import get_settings
from .llm_prompt import build_wildfire_llm_prompt


settings = get_settings()
logger = logging.getLogger(__name__)
OLLAMA_URL = (
    getattr(settings, "ollama_url", None)
    or "http://localhost:11434/api/generate"
)
OLLAMA_API_BASE = OLLAMA_URL.split("/api/")[0] + "/api"
ALT_OLLAMA_URL = (
    "http://host.docker.internal:11434/api/generate"
    if "localhost" in OLLAMA_URL
    else "http://localhost:11434/api/generate"
)
DEFAULT_MODEL = "mistral:latest"
OLLAMA_SEED = getattr(settings, "ollama_seed", None)
CACHE_TTL_SECONDS = 300  # 5 minutes
PROMPT_VERSION = "v3"  # bump to invalidate cache when prompt changes
CONFIDENCE_PROMPT_VERSION = "v2"  # separate versioning for confidence prompt changes

# Simple in-memory cache: key -> (expires_at, payload)
_llm_cache: dict[tuple, tuple[float, Dict[str, Any]]] = {}


async def call_local_llm(payload: Dict[str, Any]) -> str:
    urls_to_try = [OLLAMA_URL]
    if ALT_OLLAMA_URL not in urls_to_try:
        urls_to_try.append(ALT_OLLAMA_URL)

    last_error: Exception | None = None
    for url in urls_to_try:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
            text = data.get("response", "")
            if not isinstance(text, str):
                text = str(text)
            if not text.strip():
                raise ValueError("LLM response is empty")
            return text
        except (HTTPStatusError, RequestError, ValueError) as exc:
            last_error = exc
            logger.warning("LLM request failed for %s: %s", url, exc)

    raise ValueError(f"LLM request failed after trying {len(urls_to_try)} endpoints: {last_error}")


async def list_local_llm_models() -> list[str]:
    configured = list(getattr(settings, "ollama_tag_endpoints", []) or [])

    if getattr(settings, "ollama_url", None):
        base = settings.ollama_url
        if base.endswith("/api/generate"):
            configured.insert(0, base.replace("/api/generate", "/api/tags"))
        elif "/api" in base:
            configured.insert(0, base.split("/api")[0].rstrip("/") + "/api/tags")
        else:
            configured.insert(0, base.rstrip("/") + "/api/tags")

    fallback = [
        "http://localhost:11434/api/tags",
        "http://host.docker.internal:11434/api/tags",
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


async def estimate_wildfire_prediction_confidence_llm(
    *,
    predicted_probability_percent: int,
    temperature_c: float,
    wind_speed_kmh: float,
    relative_humidity_percent: float,
    rain_last_24h_mm: float,
    model: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    date_str: str | None = None,
) -> Dict[str, Any]:
    """Ask the local LLM for a subjective confidence score (0-100) for a given probability.

    This is intentionally a *separate* request from the ML prediction.
    """

    def _clamp_int(value: int, lo: int, hi: int) -> int:
        return lo if value < lo else hi if value > hi else value

    predicted_probability_percent = _clamp_int(int(predicted_probability_percent), 0, 100)

    system_prompt = (
        "You are an AI model that estimates confidence in an ML probability estimate for wildfire ignition risk. "
        "Confidence means: how likely the ML probability is directionally correct and stable for these inputs. "
        "IMPORTANT: low probability does NOT imply low confidence. High confidence is possible for a low-risk scenario. "
        "You MUST output a single valid JSON object with one field: \"confidence_percent\" (integer 0-100). "
        "Output nothing outside the JSON object."
    )

    location_line = (
        "Location not provided"
        if latitude is None or longitude is None
        else f"Location: lat {latitude:.4f}, lon {longitude:.4f}"
    )
    date_line = f"- Date: {date_str}" if date_str else "- Date: not provided"

    base_question = (
        "We have an ML model that predicted wildfire ignition risk probability for the following conditions. "
        "Return how confident you are in that probability estimate.\n\n"
        "Note: you MUST NOT base confidence on whether the probability is numerically low or high. "
        "Instead, judge confidence by how clear the inputs are and whether the predicted probability directionally matches them.\n\n"
        f"- Air temperature: {temperature_c:.1f} degC\n"
        f"- Wind speed: {wind_speed_kmh:.1f} km/h\n"
        f"- Relative humidity (RH): {relative_humidity_percent:.1f} %\n"
        f"- Rainfall during the last 24 hours: {rain_last_24h_mm:.1f} mm\n"
        f"- {location_line}\n"
        f"{date_line}\n\n"
        "How to judge confidence (key rules):\n"
        "1) Confidence is about certainty of the prediction, NOT the magnitude of the probability.\n"
        "   - Very wet conditions (RH ~90-100% and meaningful rain) usually make low risk *high-confidence*.\n"
        "   - Very dry/hot/windy conditions (low RH, high wind, no rain) usually make high risk *high-confidence*.\n"
        "2) Lower confidence when the signals are mixed/contradictory (e.g., very high RH but extreme wind/heat; or rain but very low RH).\n"
        "3) If location/date are missing and the case is borderline/moderate, confidence should be lower (but not automatically).\n\n"
        "Examples (for calibration):\n"
        "- Example A: Predicted 5%, RH 100%, rain 15mm, wind 10km/h, temp 18C => confidence 85-95 (clear low risk).\n"
        "- Example B: Predicted 85%, RH 10%, rain 0mm, wind 45km/h, temp 35C => confidence 85-95 (clear high risk).\n"
        "- Example C: Predicted 40-60% with moderate values => confidence 35-65 (ambiguous).\n\n"
        "Return an integer 0-100 only.\n\n"
        "Return JSON:\n{\n  \"confidence_percent\": <INTEGER_BETWEEN_0_AND_100>\n}"
    )

    prompt = build_wildfire_llm_prompt(
        user_question=base_question,
        latitude=latitude,
        longitude=longitude,
        date_str=date_str,
    )

    selected_model = model or DEFAULT_MODEL

    def _round(value: float | None) -> float | None:
        return None if value is None else round(value, 4)

    cache_key = (
        CONFIDENCE_PROMPT_VERSION,
        "confidence",
        selected_model,
        predicted_probability_percent,
        _round(temperature_c),
        _round(wind_speed_kmh),
        _round(relative_humidity_percent),
        _round(rain_last_24h_mm),
        _round(latitude),
        _round(longitude),
        date_str,
        OLLAMA_SEED,
    )

    now = monotonic()
    cached = _llm_cache.get(cache_key)
    if cached and cached[0] > now:
        return dict(cached[1])

    payload: Dict[str, Any] = {
        "model": selected_model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "temperature": 0.0,
        "top_p": 1.0,
        "max_tokens": 120,
    }

    if OLLAMA_SEED is not None:
        payload["seed"] = OLLAMA_SEED

    # Deterministic confidence (clarity + consistency) to prevent probability->confidence coupling.
    def _clamp01(x: float) -> float:
        return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

    # Normalize core signals
    rh = _clamp01(relative_humidity_percent / 100.0)
    rain = _clamp01(rain_last_24h_mm / 10.0)  # 10mm+ treated as "wet"
    wind = _clamp01(wind_speed_kmh / 50.0)   # 50km/h treated as "very windy"
    temp = _clamp01((temperature_c - 10.0) / 30.0)  # 10C..40C mapped to 0..1

    dry_score = _clamp01(0.45 * (1.0 - rh) + 0.25 * wind + 0.20 * temp + 0.10 * (1.0 - rain))
    wet_score = _clamp01(0.50 * rh + 0.35 * rain + 0.10 * (1.0 - wind) + 0.05 * (1.0 - temp))

    extreme = max(dry_score, wet_score)
    eps = 1e-9
    ambiguity = min(dry_score, wet_score) / (extreme + eps)  # 0..1 (high means mixed)
    clarity = _clamp01(extreme * (1.0 - ambiguity))

    # Expected direction from inputs (wet -> lower risk, dry -> higher risk)
    diff = dry_score - wet_score
    # map diff roughly into a pseudo expected probability
    expected_prob = 50.0 + 50.0 * max(-1.0, min(1.0, diff * 1.6))
    mismatch = abs(predicted_probability_percent - expected_prob) / 100.0

    heuristic_conf = 25.0 + 75.0 * clarity
    # Penalize when predicted probability disagrees with conditions.
    heuristic_conf *= (1.0 - 0.75 * mismatch)

    # If date is missing and the scenario is not very clear, slightly reduce.
    if date_str is None and clarity < 0.55:
        heuristic_conf -= 8.0

    # Guardrails for very obvious cases
    if rh >= 0.9 and rain >= 0.5 and wind <= 0.8:
        heuristic_conf = max(heuristic_conf, 88.0)
    if rh <= 0.2 and rain <= 0.05 and (temp >= 0.7 or wind >= 0.5):
        heuristic_conf = max(heuristic_conf, 85.0)
    if ambiguity >= 0.65 and clarity <= 0.5:
        heuristic_conf = min(heuristic_conf, 65.0)

    heuristic_conf_int = _clamp_int(int(round(heuristic_conf)), 0, 100)
    # Try LLM; if it fails, fall back to heuristic only.
    try:
        raw_text = await call_local_llm(payload)
    except ValueError as exc:
        logger.warning("LLM confidence call failed for model %s: %s", selected_model, exc)
        result = {"confidence_percent": heuristic_conf_int}
        _llm_cache[cache_key] = (now + CACHE_TTL_SECONDS, result)
        return result

    text = raw_text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                data = json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

    confidence_val = data.get("confidence_percent") if isinstance(data, dict) else None
    try:
        confidence_int = int(float(confidence_val))
    except (TypeError, ValueError):
        confidence_int = heuristic_conf_int

    confidence_int = _clamp_int(confidence_int, 0, 100)

    # Blend: keep LLM as a smaller influence, rely primarily on deterministic model.
    blended = int(round(0.1 * confidence_int + 0.9 * heuristic_conf_int))
    result = {"confidence_percent": _clamp_int(blended, 0, 100)}

    _llm_cache[cache_key] = (now + CACHE_TTL_SECONDS, result)
    return result


async def estimate_wildfire_risk_llm(
    temperature_c: float,
    wind_speed_kmh: float,
    relative_humidity_percent: float,
    rain_last_24h_mm: float,
    model: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    date_str: str | None = None,
) -> Dict[str, Any]:
    """Use local LLM (Ollama) to estimate wildfire risk."""

    system_prompt = (
        "You are an AI model that provides a concise assessment of wildfire ignition risk. "
        "Use weather plus factors like vegetation abundance/dryness, human presence, and lightning where relevant. "
        "If a location is provided, tailor the explanation to it. "
        "Your answer MUST be a single valid JSON object with fields \"wildfire_probability_percent\" (0-100 integer), \"explanation\" (English), \"feature_contributions\" (list), and \"feature_interactions\" (list). "
        "Do not use ellipsis (...), avoid quotes inside the explanation text, and output nothing outside the JSON object."
    )

    location_line = "Location not provided" if latitude is None or longitude is None else f"Location: lat {latitude:.4f}, lon {longitude:.4f}"
    date_line = f"- Date: {date_str}" if date_str else "- Date: not provided"

    base_question = (
        "Estimate the relative risk of a vegetation or forest wildfire in percent based on the following parameters:\n\n"
        f"- Air temperature: {temperature_c:.1f} degC\n"
        f"- Wind speed: {wind_speed_kmh:.1f} km/h\n"
        f"- Relative humidity (RH): {relative_humidity_percent:.1f} %\n"
        f"- Rainfall during the last 24 hours: {rain_last_24h_mm:.1f} mm\n"
        f"- {location_line}\n"
        f"{date_line}\n\n"
        "Guidance: be location-aware if coordinates are given; consider weather plus vegetation moisture/abundance, human presence, and lightning; avoid long prose.\n\n"
        "Return the result strictly as JSON in the following format:\n\n"
        "{\n"
        '    "wildfire_probability_percent": <INTEGER_BETWEEN_0_AND_100>,\n'
        '    "explanation": "<ENGLISH_TEXT_EXPLAINING WHY THE VALUE IS HIGH OR LOW>",\n'
        '    "feature_contributions": [\n'
        '        {"feature": "rh", "weight": -0.09},\n'
        '        {"feature": "wind_speed_10m", "weight": -0.02},\n'
        '        {"feature": "rain_24h", "weight": -0.02}\n'
        "    ],\n"
        '    "feature_interactions": [\n'
        '        {"pair": "rh - wind_speed_10m", "weight": 0.02},\n'
        '        {"pair": "rain_24h - vpd", "weight": 0.02}\n'
        "    ]\n"
        "}\n\n"
        "Requirements:\n"
        '- "wildfire_probability_percent" is an integer between 0 and 100.\n'
        '- "explanation" uses clear, well-structured English sentences explaining how temperature, wind, humidity, and rainfall contribute to the risk.\n'
        '- "feature_contributions" is a short list (0-6 items) of {"feature", "weight"} where weight is numeric and can be negative/positive.\n'
        '- "feature_interactions" is a short list (0-6 items) of {"pair", "weight"}, where pair is a string like "rh - wind_speed_10m" and weight is numeric.\n'
        "- Do not mention yourself as an AI, do not add disclaimers, only provide a factual explanation.\n"
    )

    prompt = build_wildfire_llm_prompt(
        user_question=base_question,
        latitude=latitude,
        longitude=longitude,
        date_str=date_str,
    )

    def _round(value: float | None) -> float | None:
        return None if value is None else round(value, 4)

    selected_model = model or DEFAULT_MODEL

    def _cache_key(active_model: str) -> tuple:
        return (
            PROMPT_VERSION,
            active_model,
            _round(temperature_c),
            _round(wind_speed_kmh),
            _round(relative_humidity_percent),
            _round(rain_last_24h_mm),
            _round(latitude),
            _round(longitude),
            date_str,
            OLLAMA_SEED,
        )

    now = monotonic()
    cached = _llm_cache.get(_cache_key(selected_model))
    if cached and cached[0] > now:
        return dict(cached[1])

    payload: Dict[str, Any] = {
        "model": selected_model,
        "prompt": prompt,
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
        logger.warning("LLM call failed for model %s: %s", selected_model, exc)
        if model and model != DEFAULT_MODEL:
            selected_model = DEFAULT_MODEL
            payload["model"] = selected_model
            try:
                raw_text = await call_local_llm(payload)
            except ValueError as exc2:
                logger.error("LLM fallback to default failed: %s", exc2)
                result = {
                    "wildfire_probability_percent": 0,
                    "explanation": f"LLM unavailable (model error: {exc2})",
                    "feature_contributions": [],
                    "feature_interactions": [],
                }
                _llm_cache[_cache_key(selected_model)] = (now + CACHE_TTL_SECONDS, result)
                return result
        else:
            result = {
                "wildfire_probability_percent": 0,
                "explanation": f"LLM unavailable (model error: {exc})",
                "feature_contributions": [],
                "feature_interactions": [],
            }
            _llm_cache[_cache_key(selected_model)] = (now + CACHE_TTL_SECONDS, result)
            return result

    text = raw_text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = text[start : end + 1]

            json_str = json_str.replace("ƒ?İ", " ")
            json_str = json_str.replace("...", " ")
            json_str = json_str.replace("ƒ?o", '"').replace("ƒ??", '"').replace("ƒ?T", "'")
            json_str = re.sub(r"[\u0000-\u001F]", " ", json_str)

            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                prob_match = re.search(r'"wildfire_probability_percent"\s*:\s*([0-9]+(?:\.[0-9]+)?)(?:\s*%)?', json_str)
                expl_match = re.search(r'"explanation"\s*:\s*"(.*)"', json_str, re.DOTALL)

                if not expl_match:
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
            result = {
                "wildfire_probability_percent": 0,
                "explanation": "The AI explanation service returned an invalid response.",
                "feature_contributions": [],
                "feature_interactions": [],
            }
            _llm_cache[_cache_key(selected_model)] = (now + CACHE_TTL_SECONDS, result)
            return result

    prob_raw = data.get("wildfire_probability_percent", 0)
    try:
        prob = int(prob_raw)
    except (TypeError, ValueError):
        prob = 0

    explanation = str(data.get("explanation", "")).strip()

    def _extract_contrib_list(raw_list: Any, key_name: str) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        if isinstance(raw_list, list):
            for item in raw_list:
                if not isinstance(item, dict):
                    continue
                name = item.get(key_name)
                weight = item.get("weight")
                if isinstance(name, str) and isinstance(weight, (int, float)):
                    out.append({key_name: name, "weight": float(weight)})
        return out

    contribs = _extract_contrib_list(data.get("feature_contributions"), "feature")
    interactions = _extract_contrib_list(data.get("feature_interactions"), "pair")

    prob = max(0, min(100, prob))

    result = {
        "wildfire_probability_percent": prob,
        "explanation": explanation or "The AI explanation service returned an invalid response.",
        "feature_contributions": contribs,
        "feature_interactions": interactions,
    }

    _llm_cache[_cache_key(selected_model)] = (now + CACHE_TTL_SECONDS, result)

    return result
