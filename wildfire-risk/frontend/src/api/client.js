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
