export const PARAM_LABELS: Record<string, string> = {
  temperature: "Temperature (°C)",
  wind_speed_10m: "Wind speed (10 m, m/s)",
  rh: "Humidity (%)",
  rain_24h: "Rain (last 24h, mm)",
};

export const PARAM_HELP: Record<string, string> = {
  temperature: "Air temperature used for the scenario simulation.",
  wind_speed_10m: "Wind speed measured at 10 m height (input in m/s).",
  rh: "Relative humidity (0–100%). Lower humidity generally increases wildfire risk.",
  rain_24h: "Total precipitation over the last 24 hours (mm).",
};
