import axios from "axios";
const apiBase = import.meta.env.VITE_API_BASE_URL || "/api";
const api = axios.create({ baseURL: apiBase });
const DEFAULT_DATE = new Date().toISOString().slice(0, 10);
const DEFAULT_BBOX = "-120.5,35.0,-120.0,35.5";
const DEFAULT_POINT = { lat: 35.25, lon: -120.25 };
export async function fetchRiskGrid(_ = undefined) {
    const params = { date: DEFAULT_DATE, bbox: DEFAULT_BBOX };
    const { data } = await api.get("/risk", { params });
    return data;
}
export async function fetchExplain(_ = undefined) {
    const params = {
        date: DEFAULT_DATE,
        lat: DEFAULT_POINT.lat,
        lon: DEFAULT_POINT.lon,
    };
    const { data } = await api.get("/explain", { params });
    return data;
}
export async function fetchFrames() {
    const params = { date: DEFAULT_DATE, lat: DEFAULT_POINT.lat, lon: DEFAULT_POINT.lon };
    const { data } = await api.get("/frames", { params });
    return data;
}
export async function runCounterfactual(overrides) {
    const payload = {
        lat: DEFAULT_POINT.lat,
        lon: DEFAULT_POINT.lon,
        date: DEFAULT_DATE,
        overrides,
    };
    const { data } = await api.post("/risk/counterfactual", payload);
    return data;
}

export async function fetchFireHistory(
    lat,
    lon,
    radiusKm,
    daysBack,
    startDate,
    endDate
) {
    const params = {};
    
    // Use either explicit dates or days_back
    if (startDate && endDate) {
        params.start_date = startDate;
        params.end_date = endDate;
    } else if (daysBack) {
        params.days_back = daysBack;
    } else {
        params.days_back = 1825; // Default 5 years
    }
    
    // Only add location params if provided (otherwise searches all Americas)
    if (lat !== undefined && lon !== undefined) {
        params.lat = lat;
        params.lon = lon;
        params.radius_km = radiusKm || 100;
    }
    const { data } = await api.get("/gee/fire-history", { params });
    return data;
}

export async function fetchFireAnalysis(eventId, lat, lon, date) {
    const params = { lat, lon, date };
    const { data } = await api.get(`/gee/fire-analysis/${eventId}`, { params });
    return data;
}

export async function fetchWildfireRiskLLM(params) {
    const query = {
        temperature_c: params.temperature_c,
        wind_speed_kmh: params.wind_speed_kmh,
        relative_humidity_percent: params.relative_humidity_percent,
        rain_last_24h_mm: params.rain_last_24h_mm,
    };
    if (params.model) query.model = params.model;
    if (typeof params.lat === "number") query.lat = params.lat;
    if (typeof params.lon === "number") query.lon = params.lon;

    const { data } = await api.get("/wildfire-llm/risk", { params: query });
    return data;
}

export async function fetchWildfireModels() {
    const { data } = await api.get("/wildfire-llm/models");
    return data;
}

export async function predictAIRisk(
    latitude,
    longitude,
    temperature,
    wind_speed_10m,
    rh,
    rain_24h = 0,
    date
) {
    const payload = {
        latitude,
        longitude,
        temperature,
        wind_speed_10m,
        rh,
        rain_24h,
        date,
        use_historical_context: true,
    };
    const { data } = await api.post("/ai-risk/predict", payload);
    return data;
}

export async function predictAIRiskGrid(
    center_lat,
    center_lon,
    temperature,
    wind_speed_10m,
    rh,
    rain_24h = 0,
    grid_size_deg = 1.0,
    grid_resolution = 20
) {
    const payload = {
        center_lat,
        center_lon,
        grid_size_deg,
        grid_resolution,
        temperature,
        wind_speed_10m,
        rh,
        rain_24h,
    };
    const { data } = await api.post("/ai-risk/predict-grid", payload);
    return data;
}

export async function fetchAIRiskConfidence(params) {
    const payload = {
        predicted_probability_percent: Math.round(params.predicted_probability_percent),
        latitude: params.latitude,
        longitude: params.longitude,
        temperature: params.temperature,
        wind_speed_10m: params.wind_speed_10m,
        rh: params.rh,
        rain_24h: params.rain_24h ?? 0,
        date: params.date,
        model: params.model,
    };
    const { data } = await api.post("/ai-risk/confidence", payload);
    return data;
}
