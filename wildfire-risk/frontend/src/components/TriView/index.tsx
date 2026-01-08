import React, { useMemo, useState, useEffect } from "react";
import DeckGL from "@deck.gl/react";
import type { PickingInfo } from "@deck.gl/core";
import { ScatterplotLayer, IconLayer } from "@deck.gl/layers";
import { HeatmapLayer, ScreenGridLayer } from "@deck.gl/aggregation-layers";
import { TileLayer } from "@deck.gl/geo-layers";
import { BitmapLayer } from "@deck.gl/layers";
import type { RiskGridCell } from "../../api/types";
import { useRisk, useScenario, useLoading, useSelectedFireEvent, useFireAnalysis, useSetClickedLocation, useAIRiskPrediction } from "../../state/selectors";
import { useTriViewState, TriViewState } from "../../state/store";
import MapHeatmap from "../MapHeatmap";
import MapLegend from "../MapLegend";
import TimeScrubber from "../TimeScrubber";
import InfoPopover from "../InfoPopover";

interface TemperaturePoint {
  latitude: number;
  longitude: number;
  temperature: number;
}

interface WindPoint {
  latitude: number;
  longitude: number;
  wind_speed: number;
}

interface HumidityPoint {
  latitude: number;
  longitude: number;
  humidity: number;
}

interface RainPoint {
  latitude: number;
  longitude: number;
  rain: number;
}

interface RiskGridPoint {
  latitude: number;
  longitude: number;
  temperature: number;
  wind_speed: number;
  humidity: number;
  rain: number;
  probability: number;
  risk_level: "low" | "moderate" | "high" | "extreme";
  risk_color: string;
}

// Color scale for temperature - smooth red gradient
const TEMP_COLOR_RANGE = [
  [255, 255, 100],   // Cold: Light yellow
  [255, 200, 50],    // Cool: Yellow-orange
  [255, 150, 40],    // Mild: Orange
  [255, 100, 30],    // Warm: Deep orange
  [255, 50, 20],     // Hot: Red-orange
  [220, 20, 20],     // Very hot: Deep red
];

// Color scale for wind speed - blue spectrum
const WIND_COLOR_RANGE = [
  [200, 230, 255],   // 0 m/s: Very light blue
  [150, 200, 255],   // 5 m/s: Light blue
  [100, 170, 255],   // 10 m/s: Medium blue
  [60, 140, 240],    // 15 m/s: Blue
  [30, 100, 220],    // 20 m/s: Deep blue
  [10, 60, 180],     // 25 m/s: Dark blue
];

// Color scale for humidity - phthalo green spectrum
const HUMIDITY_COLOR_RANGE = [
  [200, 255, 220],   // 0%: Very light green
  [150, 240, 200],   // 20%: Light green
  [100, 220, 180],   // 40%: Medium green
  [50, 190, 150],    // 60%: Phthalo green
  [20, 160, 120],    // 80%: Deep green
  [10, 130, 100],    // 100%: Dark phthalo green
];

// Color scale for rain - purple spectrum
const RAIN_COLOR_RANGE = [
  [230, 200, 255],   // 0mm: Very light purple
  [200, 150, 255],   // 5mm: Light purple
  [170, 100, 240],   // 10mm: Medium purple
  [140, 60, 220],    // 20mm: Purple
  [110, 40, 180],    // 30mm: Deep purple
  [80, 20, 140],     // 40mm: Dark purple
];

// Color scale for wildfire risk (low -> extreme)
const RISK_COLOR_RANGE = [
  [76, 175, 80],     // Low: green
  [255, 193, 7],     // Moderate: yellow
  [255, 152, 0],     // High: orange
  [244, 67, 54],     // Extreme: red
];

const INITIAL_VIEW_STATE = {
  longitude: -120.25,
  latitude: 35.25,
  zoom: 5,
  pitch: 0,
  bearing: 0,
};

const NORTH_AMERICA_BOUNDS = {
  minLat: 25,
  maxLat: 50,
  minLon: -125,
  maxLon: -70,
};

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

const getValueRange = <T,>(data: T[], getValue: (item: T) => number) => {
  if (!data.length) return null;
  let min = Number.POSITIVE_INFINITY;
  let max = Number.NEGATIVE_INFINITY;
  data.forEach((item) => {
    const value = getValue(item);
    if (!Number.isFinite(value)) return;
    min = Math.min(min, value);
    max = Math.max(max, value);
  });
  if (!Number.isFinite(min) || !Number.isFinite(max)) return null;
  return { min, max };
};

const getLegendValues = (range: { min: number; max: number } | null, fallback: [number, number, number]) => {
  if (!range) return fallback;
  const mid = (range.min + range.max) / 2;
  return [range.min, mid, range.max] as [number, number, number];
};

const interpolateColor = (colorRange: number[][], t: number) => {
  if (colorRange.length === 0) return [0, 0, 0];
  if (colorRange.length === 1) return colorRange[0];
  const clamped = clamp(t, 0, 1);
  const scaled = clamped * (colorRange.length - 1);
  const index = Math.floor(scaled);
  const localT = scaled - index;
  const start = colorRange[index];
  const end = colorRange[Math.min(index + 1, colorRange.length - 1)];
  return [
    Math.round(start[0] + (end[0] - start[0]) * localT),
    Math.round(start[1] + (end[1] - start[1]) * localT),
    Math.round(start[2] + (end[2] - start[2]) * localT),
  ];
};

const getColorForValue = (value: number, range: { min: number; max: number } | null, colors: number[][], alpha = 200) => {
  if (!range || !Number.isFinite(value) || range.max === range.min) {
    const fallback = colors[colors.length - 1] || [255, 255, 255];
    return [fallback[0], fallback[1], fallback[2], alpha];
  }
  const t = (value - range.min) / (range.max - range.min);
  const color = interpolateColor(colors, t);
  return [color[0], color[1], color[2], alpha];
};

const getScaledValue = (value: number, range: { min: number; max: number } | null, minOut: number, maxOut: number) => {
  if (!range || !Number.isFinite(value) || range.max === range.min) {
    return (minOut + maxOut) / 2;
  }
  const t = clamp((value - range.min) / (range.max - range.min), 0, 1);
  return minOut + (maxOut - minOut) * t;
};

const getRiskLevelFromProbability = (probability: number) => {
  if (probability < 0.2) return "low";
  if (probability < 0.4) return "moderate";
  if (probability < 0.7) return "high";
  return "extreme";
};

const toCoordKey = (lat: number, lon: number) => `${lat.toFixed(6)},${lon.toFixed(6)}`;

const isInBounds = (lat: number, lon: number, bounds = NORTH_AMERICA_BOUNDS) =>
  lat >= bounds.minLat && lat <= bounds.maxLat && lon >= bounds.minLon && lon <= bounds.maxLon;

const findNearestPoint = <T,>(
  data: T[],
  lat: number,
  lon: number,
  getLat: (item: T) => number,
  getLon: (item: T) => number
) => {
  let best: T | null = null;
  let bestDist = Number.POSITIVE_INFINITY;
  for (const item of data) {
    const dLat = lat - getLat(item);
    const dLon = lon - getLon(item);
    const dist = dLat * dLat + dLon * dLon;
    if (dist < bestDist) {
      bestDist = dist;
      best = item;
    }
  }
  return best;
};

const sigmoid = (x: number) => 1 / (1 + Math.exp(-x));

const estimateVegetationDryness = (temperature: number, humidity: number, rain24h: number) => {
  let dryness = 0;
  if (temperature > 25) {
    dryness += Math.min(((temperature - 25) / 15) * 40, 40);
  }
  dryness += Math.max(0, ((100 - humidity) / 100) * 35);
  if (rain24h < 5) {
    dryness += Math.max(0, ((5 - rain24h) / 5) * 25);
  }
  return Math.min(dryness, 100);
};

const estimateDroughtIndex = (tempAnomaly: number, rain24h: number, humidity: number) => {
  let drought = 0;
  if (tempAnomaly > 0) {
    drought += Math.min((tempAnomaly / 10) * 40, 40);
  }
  if (rain24h < 10) {
    drought += ((10 - rain24h) / 10) * 35;
  }
  if (humidity < 40) {
    drought += ((40 - humidity) / 40) * 25;
  }
  return Math.min(drought, 100);
};

const calculateWildfireRisk = (temperature: number, windSpeed: number, humidity: number, rain24h: number) => {
  const tempAnomaly = temperature - 20;
  const vegetationDryness = estimateVegetationDryness(temperature, humidity, rain24h);
  const droughtIndex = estimateDroughtIndex(tempAnomaly, rain24h, humidity);

  const logOdds =
    -3.5 +
    temperature * 0.045 +
    windSpeed * 0.035 +
    humidity * -0.04 +
    rain24h * -0.06 +
    vegetationDryness * 0.05 +
    tempAnomaly * 0.03 +
    droughtIndex * 0.025;

  const probability = sigmoid(logOdds);

  if (probability < 0.2) {
    return { probability, risk_level: "low" as const, risk_color: "#4CAF50" };
  }
  if (probability < 0.4) {
    return { probability, risk_level: "moderate" as const, risk_color: "#FFC107" };
  }
  if (probability < 0.7) {
    return { probability, risk_level: "high" as const, risk_color: "#FF9800" };
  }
  return { probability, risk_level: "extreme" as const, risk_color: "#F44336" };
};

const TriView: React.FC = () => {
  const risk = useRisk();
  const scenario = useScenario();
  const loading = useLoading();
  const selectedFireEvent = useSelectedFireEvent();
  const fireAnalysis = useFireAnalysis();
  const setClickedLocation = useSetClickedLocation();
  const aiRiskPrediction = useAIRiskPrediction();
  const wildfireLlmExplanation = useTriViewState((state: TriViewState) => state.wildfireLlmExplanation);
  const aiRiskGrid = useTriViewState((state: TriViewState) => state.aiRiskGrid);
  const [date, setDate] = useState<string>("2013-01-01"); // Use date that exists in historical dataset
  const [temperatureData, setTemperatureData] = useState<TemperaturePoint[]>([]);
  const [windData, setWindData] = useState<WindPoint[]>([]);
  const [humidityData, setHumidityData] = useState<HumidityPoint[]>([]);
  const [rainData, setRainData] = useState<RainPoint[]>([]);
  const [showTempLayer, setShowTempLayer] = useState(false);
  const [showWindLayer, setShowWindLayer] = useState(false);
  const [showHumidityLayer, setShowHumidityLayer] = useState(false);
  const [showRainLayer, setShowRainLayer] = useState(false);
  const [showRiskLayer, setShowRiskLayer] = useState(false);
  const [mapViewState, setMapViewState] = useState(INITIAL_VIEW_STATE);
  const [pulsePhase, setPulsePhase] = useState(0);
  const clickedLocationRef = useTriViewState((state: TriViewState) => state.clickedLocation);
  const fallbackProbability = wildfireLlmExplanation
    ? wildfireLlmExplanation.wildfire_probability_percent / 100
    : null;
  const predictionProbability =
    aiRiskPrediction?.probability ?? (fallbackProbability ?? null);
  const predictionRiskLevel =
    aiRiskPrediction?.risk_level ??
    (predictionProbability !== null ? getRiskLevelFromProbability(predictionProbability) : undefined);
  const showPredictionLayer =
    clickedLocationRef !== undefined && predictionProbability !== null;
  const temperatureRange = useMemo(() => getValueRange(temperatureData, (d) => d.temperature), [temperatureData]);
  const windRange = useMemo(() => getValueRange(windData, (d) => d.wind_speed), [windData]);
  const humidityRange = useMemo(() => getValueRange(humidityData, (d) => d.humidity), [humidityData]);
  const rainRange = useMemo(() => getValueRange(rainData, (d) => d.rain), [rainData]);
  const riskRadiusPixels = useMemo(() => {
    const zoom = mapViewState?.zoom ?? INITIAL_VIEW_STATE.zoom;
    const scale = Math.pow(1.2, Math.max(0, zoom - 4));
    return clamp(80 * scale, 80, 280);
  }, [mapViewState?.zoom]);

  useEffect(() => {
    if (!showPredictionLayer) {
      setPulsePhase(0);
      return;
    }
    const cycleMs = 1400;
    const tickMs = 60;
    const start = Date.now();
    const interval = window.setInterval(() => {
      const elapsed = Date.now() - start;
      const nextPhase = (elapsed % cycleMs) / cycleMs;
      setPulsePhase(nextPhase);
    }, tickMs);
    return () => window.clearInterval(interval);
  }, [showPredictionLayer]);
  const riskGridData = useMemo(() => {
    if (!showRiskLayer) return [];
    if (!windData.length || !humidityData.length || !rainData.length) return [];

    const humidityCandidates = humidityData.filter((point) =>
      isInBounds(point.latitude, point.longitude)
    );
    const humiditySource = humidityCandidates.length ? humidityCandidates : humidityData;
    const humidityMap = new Map<string, number>();
    humiditySource.forEach((point) => {
      humidityMap.set(toCoordKey(point.latitude, point.longitude), point.humidity);
    });

    const rainCandidates = rainData.filter((point) =>
      isInBounds(point.latitude, point.longitude)
    );
    const rainSource = rainCandidates.length ? rainCandidates : rainData;
    const rainMap = new Map<string, number>();
    rainSource.forEach((point) => {
      rainMap.set(toCoordKey(point.latitude, point.longitude), point.rain);
    });

    const temperatureCandidates = temperatureData.filter((point) =>
      isInBounds(point.latitude, point.longitude)
    );
    const temperatureSource = temperatureCandidates.length ? temperatureCandidates : temperatureData;
    const temperatureMap = new Map<string, number>();
    temperatureSource.forEach((point) => {
      temperatureMap.set(toCoordKey(point.latitude, point.longitude), point.temperature);
    });

    const riskPoints: RiskGridPoint[] = [];

    windData.forEach((windPoint) => {
      if (!isInBounds(windPoint.latitude, windPoint.longitude)) return;
      const key = toCoordKey(windPoint.latitude, windPoint.longitude);
      let humidity = humidityMap.get(key);
      if (humidity === undefined) {
        const nearestHumidity = findNearestPoint(
          humiditySource,
          windPoint.latitude,
          windPoint.longitude,
          (point) => point.latitude,
          (point) => point.longitude
        );
        if (nearestHumidity) {
          humidity = nearestHumidity.humidity;
        }
      }

      let rain = rainMap.get(key);
      if (rain === undefined) {
        const nearestRain = findNearestPoint(
          rainSource,
          windPoint.latitude,
          windPoint.longitude,
          (point) => point.latitude,
          (point) => point.longitude
        );
        if (nearestRain) {
          rain = nearestRain.rain;
        }
      }

      if (humidity === undefined || rain === undefined) return;

      let temperature = temperatureMap.get(key);
      if (temperature === undefined) {
        const nearestTemp = findNearestPoint(
          temperatureSource,
          windPoint.latitude,
          windPoint.longitude,
          (point) => point.latitude,
          (point) => point.longitude
        );
        if (nearestTemp) {
          temperature = nearestTemp.temperature;
        }
      }

      if (temperature === undefined) return;

      const riskResult = calculateWildfireRisk(
        temperature,
        windPoint.wind_speed,
        humidity,
        rain
      );

      riskPoints.push({
        latitude: windPoint.latitude,
        longitude: windPoint.longitude,
        temperature,
        wind_speed: windPoint.wind_speed,
        humidity,
        rain,
        probability: riskResult.probability,
        risk_level: riskResult.risk_level,
        risk_color: riskResult.risk_color,
      });
    });

    return riskPoints;
  }, [showRiskLayer, windData, humidityData, rainData, temperatureData]);

  // Load temperature data - ALWAYS load, just control visibility
  useEffect(() => {
    const loadTemperatureData = async () => {
      try {
        console.log('Loading temperature data for date:', date);
        const response = await fetch('http://localhost:8000/api/temperature/heatmap', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            date,
            region: 'global',
            bbox: null
          })
        });
        if (response.ok) {
          const result = await response.json();
          console.log('Loaded temperature points:', result.count);
          setTemperatureData(result.data || []);
        } else {
          console.error('Temperature API error:', response.status);
        }
      } catch (err) {
        console.error('Failed to load temperature data:', err);
      }
    };
    loadTemperatureData(); // Always load, visibility controlled by showTempLayer
  }, [date]);

  // Load weather data from GEE-powered API endpoints
  // Wind always uses today's date for real-time data
  useEffect(() => {
    const loadWeatherData = async () => {
      // Wind uses today's date to get real GEE data
      const today = new Date().toISOString().split('T')[0];
      
      const windRequestBody = {
        date: today,  // Always use today for wind
        region: 'north_america',
        bbox: { min_lat: 25, max_lat: 50, min_lon: -125, max_lon: -70 }
      };

      // Load wind data (uses today's date)
      try {
        console.log('Loading real-time wind data from GEE for:', today);
        const windResponse = await fetch('http://localhost:8000/api/weather/wind/heatmap', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(windRequestBody)
        });
        if (windResponse.ok) {
          const result = await windResponse.json();
          console.log('Loaded wind points:', result.count);
          setWindData(result.data || []);
        } else {
          console.error('Wind API error:', windResponse.status);
        }
      } catch (err) {
        console.error('Failed to load wind data:', err);
      }

      // Load humidity data (uses historical date)
      const otherRequestBody = {
        date,
        region: 'global',
        bbox: null
      };
      
      try {
        console.log('Loading humidity data for date:', date);
        const humidityResponse = await fetch('http://localhost:8000/api/weather/humidity/heatmap', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(otherRequestBody)
        });
        if (humidityResponse.ok) {
          const result = await humidityResponse.json();
          console.log('Loaded humidity points:', result.count);
          setHumidityData(result.data || []);
        } else {
          console.error('Humidity API error:', humidityResponse.status);
        }
      } catch (err) {
        console.error('Failed to load humidity data:', err);
      }

      // Load rain data (uses historical date)
      try {
        console.log('Loading rain data for date:', date);
        const rainResponse = await fetch('http://localhost:8000/api/weather/rain/heatmap', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(otherRequestBody)
        });
        if (rainResponse.ok) {
          const result = await rainResponse.json();
          console.log('Loaded rain points:', result.count);
          setRainData(result.data || []);
        } else {
          console.error('Rain API error:', rainResponse.status);
        }
      } catch (err) {
        console.error('Failed to load rain data:', err);
      }
    };

    loadWeatherData();
  }, [date]);

  const layers = useMemo(() => {
    const baseLayers: any[] = [
      new TileLayer({
        id: "base-map",
        data: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        minZoom: 0,
        maxZoom: 19,
        tileSize: 256,
        renderSubLayers: (props: any) => {
          if (!props.data) return null;
          
          const {
            bbox: {west, south, east, north}
          } = props.tile;
          
          return new BitmapLayer(props, {
            data: null,
            image: props.data,
            bounds: [west, south, east, north]
          });
        },
      }),
    ];

    if (!risk) {
      return baseLayers;
    }
    
    // const riskLayer = new ScatterplotLayer<RiskGridCell>({
    //   id: "risk-layer",
    //   data: risk.grid,
    //   getPosition: (cell: RiskGridCell) => [cell.lon, cell.lat],
    //   getRadius: 8000,
    //   radiusUnits: "meters",
    //   getFillColor: (cell: RiskGridCell) => {
    //     const intensity = Math.min(255, Math.round(cell.prob * 255));
    //     const cooled = Math.max(0, 170 - Math.round(intensity / 2));
    //     return [220, 50, 50, 220];
    //   },
    //   opacity: 1.0,
    //   pickable: true,
    // });
    
    // Temperature heatmap layer - sharp edges, visible map
    const tempLayer = showTempLayer && temperatureData.length > 0 ? new HeatmapLayer({
      id: 'temperature-weather-map',
      data: temperatureData,
      getPosition: (d: TemperaturePoint) => [d.longitude, d.latitude],
      getWeight: (d: TemperaturePoint) => Math.max(0, d.temperature + 20),
      radiusPixels: 30,
      intensity: 1,
      threshold: 0.1,
      opacity: 0.6,
      colorRange: TEMP_COLOR_RANGE as any,
      aggregation: 'MEAN',
      pickable: false,
    }) : null;

    // Wind speed heatmap - blends faster than temp
    const windLayer = showWindLayer && windData.length > 0 ? new HeatmapLayer({
      id: 'wind-speed-map',
      data: windData,
      getPosition: (d: WindPoint) => [d.longitude, d.latitude],
      getWeight: (d: WindPoint) => d.wind_speed * 2,
      radiusPixels: 55,
      intensity: 1.3,
      threshold: 0.05,
      opacity: 0.6,
      colorRange: WIND_COLOR_RANGE as any,
      aggregation: 'MEAN',
      pickable: false,
    }) : null;

    // Humidity heatmap - blends faster than temp
    const humidityLayer = showHumidityLayer && humidityData.length > 0 ? new HeatmapLayer({
      id: 'humidity-map',
      data: humidityData,
      getPosition: (d: HumidityPoint) => [d.longitude, d.latitude],
      getWeight: (d: HumidityPoint) => d.humidity,
      radiusPixels: 55,
      intensity: 1.3,
      threshold: 0.05,
      opacity: 0.6,
      colorRange: HUMIDITY_COLOR_RANGE as any,
      aggregation: 'MEAN',
      pickable: false,
    }) : null;

    // Rain heatmap - blends faster than temp
    const rainLayer = showRainLayer && rainData.length > 0 ? new HeatmapLayer({
      id: 'rain-map',
      data: rainData,
      getPosition: (d: RainPoint) => [d.longitude, d.latitude],
      getWeight: (d: RainPoint) => d.rain * 3,
      radiusPixels: 55,
      intensity: 1.3,
      threshold: 0.05,
      opacity: 0.6,
      colorRange: RAIN_COLOR_RANGE as any,
      aggregation: 'MEAN',
      pickable: false,
    }) : null;

    const riskHeatmapLayer = showRiskLayer && riskGridData.length > 0 ? new HeatmapLayer({
      id: 'wildfire-risk-heatmap',
      data: riskGridData,
      getPosition: (d: RiskGridPoint) => [d.longitude, d.latitude],
      getWeight: (d: RiskGridPoint) => Math.max(0.02, d.probability),
      radiusPixels: riskRadiusPixels,
      intensity: 1.6,
      threshold: 0.01,
      opacity: 0.6,
      colorRange: RISK_COLOR_RANGE as any,
      aggregation: 'MEAN',
      pickable: false,
    }) : null;

    const riskHoverLayer = showRiskLayer && riskGridData.length > 0 ? new ScatterplotLayer<RiskGridPoint>({
      id: 'wildfire-risk-hover',
      data: riskGridData,
      getPosition: (d) => [d.longitude, d.latitude],
      getRadius: Math.max(8, riskRadiusPixels * 0.55),
      radiusUnits: 'pixels',
      getFillColor: [0, 0, 0, 0],
      getLineColor: [0, 0, 0, 0],
      getLineWidth: 0,
      pickable: true,
      opacity: 0,
      stroked: false,
      autoHighlight: false,
    }) : null;

    const temperaturePointsLayer = showTempLayer && temperatureData.length > 0 ? new ScatterplotLayer<TemperaturePoint>({
      id: 'temperature-points',
      data: temperatureData,
      getPosition: (d) => [d.longitude, d.latitude],
      getRadius: (d) => getScaledValue(d.temperature, temperatureRange, 4, 10),
      radiusUnits: 'pixels',
      getFillColor: (d) => getColorForValue(d.temperature, temperatureRange, TEMP_COLOR_RANGE, 220),
      getLineColor: [255, 255, 255, 160],
      getLineWidth: 1,
      lineWidthUnits: 'pixels',
      pickable: true,
      autoHighlight: true,
      opacity: 0.9,
      stroked: true,
    }) : null;

    const windPointsLayer = showWindLayer && windData.length > 0 ? new ScatterplotLayer<WindPoint>({
      id: 'wind-points',
      data: windData,
      getPosition: (d) => [d.longitude, d.latitude],
      getRadius: (d) => getScaledValue(d.wind_speed, windRange, 4, 10),
      radiusUnits: 'pixels',
      getFillColor: (d) => getColorForValue(d.wind_speed, windRange, WIND_COLOR_RANGE, 220),
      getLineColor: [255, 255, 255, 160],
      getLineWidth: 1,
      lineWidthUnits: 'pixels',
      pickable: true,
      autoHighlight: true,
      opacity: 0.9,
      stroked: true,
    }) : null;

    const humidityPointsLayer = showHumidityLayer && humidityData.length > 0 ? new ScatterplotLayer<HumidityPoint>({
      id: 'humidity-points',
      data: humidityData,
      getPosition: (d) => [d.longitude, d.latitude],
      getRadius: (d) => getScaledValue(d.humidity, humidityRange, 4, 10),
      radiusUnits: 'pixels',
      getFillColor: (d) => getColorForValue(d.humidity, humidityRange, HUMIDITY_COLOR_RANGE, 220),
      getLineColor: [255, 255, 255, 160],
      getLineWidth: 1,
      lineWidthUnits: 'pixels',
      pickable: true,
      autoHighlight: true,
      opacity: 0.9,
      stroked: true,
    }) : null;

    const rainPointsLayer = showRainLayer && rainData.length > 0 ? new ScatterplotLayer<RainPoint>({
      id: 'rain-points',
      data: rainData,
      getPosition: (d) => [d.longitude, d.latitude],
      getRadius: (d) => getScaledValue(d.rain, rainRange, 4, 10),
      radiusUnits: 'pixels',
      getFillColor: (d) => getColorForValue(d.rain, rainRange, RAIN_COLOR_RANGE, 220),
      getLineColor: [255, 255, 255, 160],
      getLineWidth: 1,
      lineWidthUnits: 'pixels',
      pickable: true,
      autoHighlight: true,
      opacity: 0.9,
      stroked: true,
    }) : null;

    const pulseValue = 0.5 - 0.5 * Math.cos(pulsePhase * Math.PI * 2);
    const pulseRadius = 10 + 18 * pulseValue;
    const pulseAlpha = Math.round(140 * (1 - pulseValue));
    const predictionPoint = showPredictionLayer
      ? [
          {
            latitude: clickedLocationRef!.lat,
            longitude: clickedLocationRef!.lon,
            probability: predictionProbability!,
            risk_level: predictionRiskLevel,
          },
        ]
      : [];

    const aiPredictionSpotLayer =
      predictionPoint.length > 0
        ? new ScatterplotLayer({
            id: "ai-risk-prediction-spot",
            data: predictionPoint,
            getPosition: (d: any) => [d.longitude, d.latitude],
            getRadius: 8,
            radiusUnits: "pixels",
            getFillColor: (d: any) =>
              getColorForValue(d.probability, RISK_PROB_RANGE, RISK_COLOR_RANGE, 230),
            pickable: true,
            opacity: 0.9,
            stroked: false,
          })
        : null;

    const aiPredictionPulseLayer =
      predictionPoint.length > 0
        ? new ScatterplotLayer({
            id: "ai-risk-prediction-pulse",
            data: predictionPoint,
            getPosition: (d: any) => [d.longitude, d.latitude],
            getRadius: pulseRadius,
            radiusUnits: "pixels",
            getFillColor: (d: any) => {
              const base = getColorForValue(d.probability, RISK_PROB_RANGE, RISK_COLOR_RANGE, 200);
              return [base[0], base[1], base[2], pulseAlpha];
            },
            pickable: false,
            opacity: 0.6,
            stroked: false,
          })
        : null;

    // AI Risk Grid layer
    const aiRiskLayer = aiRiskGrid && aiRiskGrid.grid_cells.length > 0 ? new ScatterplotLayer({
      id: 'ai-risk-grid',
      data: aiRiskGrid.grid_cells,
      getPosition: (d: any) => [d.longitude, d.latitude],
      getRadius: 12000,
      radiusUnits: 'meters',
      getFillColor: (d: any) => {
        const hex = d.risk_color.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);
        return [r, g, b, 150];
      },
      pickable: true,
      opacity: 0.7,
    }) : null;
    
    // Add fire event marker if one is selected
    const fireMarkerLayer = selectedFireEvent ? new ScatterplotLayer({
      id: "fire-marker",
      data: [selectedFireEvent],
      getPosition: (d: any) => [d.longitude, d.latitude],
      getRadius: 15000,
      radiusUnits: "meters",
      getFillColor: [255, 50, 50, 200],
      getLineColor: [255, 255, 255, 255],
      getLineWidth: 300,
      lineWidthUnits: "meters",
      pickable: true,
      stroked: true,
      onHover: (_info: any) => {
        // Fire hover handling moved to WorldMap component
      },
    }) : null;

    // Click location pin marker - thumbtack style with risk-based color
    const clickPinLayer = clickedLocationRef ? new IconLayer({
      id: 'click-pin-marker',
      data: [{
        latitude: clickedLocationRef.lat,
        longitude: clickedLocationRef.lon,
        probability: predictionProbability ?? 0,
      }],
      getPosition: (d: any) => [d.longitude, d.latitude],
      getIcon: (d: any) => {
        // Determine color based on probability
        let pinColor = '#ff6b35'; // Default orange
        if (predictionProbability !== null) {
          const prob = d.probability;
          if (prob < 0.3) {
            pinColor = '#22c55e'; // Green - low risk
          } else if (prob < 0.6) {
            pinColor = '#ff9933'; // Orange - medium risk
          } else {
            pinColor = '#ef4444'; // Red - high risk
          }
        }
        
        return {
          url: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="24" height="36">
              <!-- Pin point -->
              <path d="M12 36 L12 16" stroke="${pinColor}" stroke-width="2" fill="none"/>
              <!-- Pin head circle -->
              <circle cx="12" cy="8" r="7" fill="${pinColor}" stroke="#ffffff" stroke-width="2"/>
              <!-- Inner dot -->
              <circle cx="12" cy="8" r="3" fill="#ffffff"/>
            </svg>
          `),
          width: 24,
          height: 36,
          anchorY: 36,
        };
      },
      getSize: 48,
      pickable: true,
    }) : null;
    
    return [
      ...baseLayers,
      tempLayer,
      windLayer,
      humidityLayer,
      rainLayer,
      riskHeatmapLayer,
      riskHoverLayer,
      temperaturePointsLayer,
      windPointsLayer,
      humidityPointsLayer,
      rainPointsLayer,
      // riskLayer,
      aiRiskLayer,
      aiPredictionPulseLayer,
      aiPredictionSpotLayer,
      fireMarkerLayer,
      clickPinLayer,
    ].filter(Boolean);
  }, [risk, selectedFireEvent, showTempLayer, showWindLayer, showHumidityLayer, showRainLayer, showRiskLayer, temperatureData, windData, humidityData, rainData, aiRiskGrid, clickedLocationRef, temperatureRange, windRange, humidityRange, rainRange, aiRiskPrediction, wildfireLlmExplanation, riskGridData, riskRadiusPixels, pulsePhase, showPredictionLayer, predictionProbability, predictionRiskLevel]);

  return (
    <div className="panel" aria-busy={loading}>
      <div style={{ marginBottom: 'var(--spacing-md)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <h2 style={{ margin: 0 }}>🗺️ Wildfire Risk Visualization</h2>
            <InfoPopover
              description="Interactive scenario map with risk grid cells and optional weather layers. Click the map to set the What-If location."
              abbreviations={[
                { term: "AI", meaning: "Artificial Intelligence risk layer." },
                { term: "Temp", meaning: "Temperature layer." },
                { term: "FRP", meaning: "Fire Radiative Power (intensity proxy)." },
              ]}
            />
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button 
              onClick={() => setShowTempLayer(!showTempLayer)}
              style={{
                padding: '6px 12px',
                fontSize: '0.85rem',
                background: showTempLayer ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : 'var(--bg-secondary)',
                color: 'Black',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              title="Toggle temperature layer"
            >
              {showTempLayer ? '🌡️ Hide Temp' : '🌡️ Show Temp'}
            </button>
            <button 
              onClick={() => setShowWindLayer(!showWindLayer)}
              style={{
                padding: '6px 12px',
                fontSize: '0.85rem',
                background: showWindLayer ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 'var(--bg-secondary)',
                color: 'Black',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              title="Toggle wind speed layer"
            >
              {showWindLayer ? '💨 Hide Wind' : '💨 Show Wind'}
            </button>
            <button 
              onClick={() => setShowHumidityLayer(!showHumidityLayer)}
              style={{
                padding: '6px 12px',
                fontSize: '0.85rem',
                background: showHumidityLayer ? 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' : 'var(--bg-secondary)',
                color: 'Black',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              title="Toggle humidity layer"
            >
              {showHumidityLayer ? '💧 Hide Humidity' : '💧 Show Humidity'}
            </button>
            <button 
              onClick={() => setShowRainLayer(!showRainLayer)}
              style={{
                padding: '6px 12px',
                fontSize: '0.85rem',
                background: showRainLayer ? 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)' : 'var(--bg-secondary)',
                color: 'Black',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              title="Toggle rain layer"
            >
              {showRainLayer ? '🌧️ Hide Rain' : '🌧️ Show Rain'}
            </button>
            <button 
              onClick={() => setShowRiskLayer(!showRiskLayer)}
              style={{
                padding: '6px 12px',
                fontSize: '0.85rem',
                background: showRiskLayer ? 'linear-gradient(135deg, #f97316 0%, #ef4444 100%)' : 'var(--bg-secondary)',
                color: 'Black',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              title="Toggle wildfire risk grid"
            >
              {showRiskLayer ? '🔥 Hide Risk' : '🔥 Show Risk'}
            </button>
          </div>
        </div>
        <div style={{ 
          display: 'flex', 
          gap: 'var(--spacing-md)', 
          flexWrap: 'wrap',
          fontSize: '0.9rem',
          color: 'var(--text-secondary)'
        }}>
          <div>
            <strong style={{ color: 'var(--accent-orange)' }}>Scenario:</strong> {scenario}
          </div>
          <div>
            <strong style={{ color: 'var(--accent-orange)' }}>Date:</strong> {date}
          </div>
        </div>
      </div>
      {loading && (
        <div style={{ 
          textAlign: 'center', 
          padding: 'var(--spacing-xl)',
          color: 'var(--text-secondary)' 
        }}>
          ⏳ Loading risk data...
        </div>
      )}
      {!loading && risk && (
        <>
          <div className="tri-view">
            {/* <h3>Scenario Risk Map</h3>
            <div className="tri-view__grid">
              {risk.grid.slice(0, 6).map((cell: RiskGridCell) => (
                <div key={`${cell.lat}-${cell.lon}`} className="tri-view__cell">
                  <span>
                    {cell.lat.toFixed(2)}, {cell.lon.toFixed(2)}
                  </span>
                  <span>{(cell.prob * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div> */}
            <div className="tri-view__deck">
              <DeckGL
                style={{ width: "100%", height: "100%" }}
                layers={layers}
                viewState={mapViewState as any}
                onViewStateChange={({ viewState }: any) => setMapViewState(viewState)}
                controller
                onClick={(info: any) => {
                  if (info?.coordinate && Array.isArray(info.coordinate)) {
                    const [lon, lat] = info.coordinate;
                    setClickedLocation?.({ lat, lon });
                    console.log("Map click -> set What-If coords", { lat, lon });
                  }
                }}
                getTooltip={(info: PickingInfo<any>) => {
                  if (info.layer?.id === 'temperature-points') {
                    const point = info.object as TemperaturePoint | null;
                    if (!point) return null;
                    return {
                      html: `
                        <div style="padding: 10px 12px; max-width: 220px; background: rgba(10, 14, 39, 0.98); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12);">
                          <div style="font-weight: 700; color: #f97316; margin-bottom: 6px;">🌡️ Temperature</div>
                          <div style="color: #e2e8f0; line-height: 1.5;">
                            <div><strong>${point.temperature.toFixed(1)}°C</strong></div>
                            <div style="font-size: 12px; color: #9ca3af;">Lat ${point.latitude.toFixed(2)}°, Lon ${point.longitude.toFixed(2)}°</div>
                          </div>
                        </div>
                      `,
                      style: { backgroundColor: 'transparent', padding: '0' },
                    };
                  }

                  if (info.layer?.id === 'wind-points') {
                    const point = info.object as WindPoint | null;
                    if (!point) return null;
                    return {
                      html: `
                        <div style="padding: 10px 12px; max-width: 220px; background: rgba(10, 14, 39, 0.98); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12);">
                          <div style="font-weight: 700; color: #38bdf8; margin-bottom: 6px;">💨 Wind Speed</div>
                          <div style="color: #e2e8f0; line-height: 1.5;">
                            <div><strong>${point.wind_speed.toFixed(1)} m/s</strong></div>
                            <div style="font-size: 12px; color: #9ca3af;">Lat ${point.latitude.toFixed(2)}°, Lon ${point.longitude.toFixed(2)}°</div>
                          </div>
                        </div>
                      `,
                      style: { backgroundColor: 'transparent', padding: '0' },
                    };
                  }

                  if (info.layer?.id === 'humidity-points') {
                    const point = info.object as HumidityPoint | null;
                    if (!point) return null;
                    return {
                      html: `
                        <div style="padding: 10px 12px; max-width: 220px; background: rgba(10, 14, 39, 0.98); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12);">
                          <div style="font-weight: 700; color: #22c55e; margin-bottom: 6px;">💧 Humidity</div>
                          <div style="color: #e2e8f0; line-height: 1.5;">
                            <div><strong>${point.humidity.toFixed(0)}%</strong></div>
                            <div style="font-size: 12px; color: #9ca3af;">Lat ${point.latitude.toFixed(2)}°, Lon ${point.longitude.toFixed(2)}°</div>
                          </div>
                        </div>
                      `,
                      style: { backgroundColor: 'transparent', padding: '0' },
                    };
                  }

                  if (info.layer?.id === 'rain-points') {
                    const point = info.object as RainPoint | null;
                    if (!point) return null;
                    return {
                      html: `
                        <div style="padding: 10px 12px; max-width: 220px; background: rgba(10, 14, 39, 0.98); border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.12);">
                          <div style="font-weight: 700; color: #a855f7; margin-bottom: 6px;">🌧️ Rain</div>
                          <div style="color: #e2e8f0; line-height: 1.5;">
                            <div><strong>${point.rain.toFixed(1)} mm</strong></div>
                            <div style="font-size: 12px; color: #9ca3af;">Lat ${point.latitude.toFixed(2)}°, Lon ${point.longitude.toFixed(2)}°</div>
                          </div>
                        </div>
                      `,
                      style: { backgroundColor: 'transparent', padding: '0' },
                    };
                  }

                  if (info.layer?.id === 'wildfire-risk-hover') {
                    const point = info.object as RiskGridPoint | null;
                    if (!point) return null;
                    const probabilityPercent = point.probability * 100;
                    return {
                      html: `
                        <div style="padding: 10px 12px; max-width: 220px; background: rgba(10, 14, 39, 0.98); border-radius: 8px; border: 2px solid ${point.risk_color};">
                          <div style="font-weight: 700; color: ${point.risk_color}; margin-bottom: 6px;">Wildfire Risk</div>
                          <div style="color: #e2e8f0; line-height: 1.5;">
                            <div><strong>${probabilityPercent.toFixed(1)}%</strong> (${point.risk_level})</div>
                          </div>
                        </div>
                      `,
                      style: { backgroundColor: 'transparent', padding: '0' },
                    };
                  }

                  if (info.layer?.id === 'ai-risk-prediction-spot') {
                    const point = info.object as { probability: number; risk_level?: string } | null;
                    if (!point) return null;
                    const probabilityPercent = point.probability * 100;
                    const riskColor = getColorForValue(point.probability, RISK_PROB_RANGE, RISK_COLOR_RANGE, 230);
                    return {
                      html: `
                        <div style="padding: 10px 12px; max-width: 220px; background: rgba(10, 14, 39, 0.98); border-radius: 8px; border: 2px solid rgb(${riskColor[0]}, ${riskColor[1]}, ${riskColor[2]});">
                          <div style="font-weight: 700; color: rgb(${riskColor[0]}, ${riskColor[1]}, ${riskColor[2]}); margin-bottom: 6px;">What-If Risiko</div>
                          <div style="color: #e2e8f0; line-height: 1.5;">
                            <div><strong>${probabilityPercent.toFixed(1)}%</strong>${point.risk_level ? ` (${point.risk_level})` : ''}</div>
                          </div>
                        </div>
                      `,
                      style: { backgroundColor: 'transparent', padding: '0' },
                    };
                  }

                  // Show click pin tooltip
                  if (info.layer?.id === 'click-pin-marker' && clickedLocationRef) {
                    const probability = predictionProbability ?? undefined;
                    const riskLevel = probability 
                      ? (probability < 0.3 ? 'Low' : probability < 0.6 ? 'Medium' : 'High')
                      : 'Unknown';
                    const riskColor = probability
                      ? (probability < 0.3 ? '#22c55e' : probability < 0.6 ? '#ff9933' : '#ef4444')
                      : '#ff6b35';
                    
                    return {
                      html: `
                        <div style="padding: 12px; max-width: 280px; background: rgba(10, 14, 39, 0.98); border-radius: 8px; border: 2px solid ${riskColor};">
                          <div style="font-weight: bold; font-size: 14px; color: ${riskColor}; margin-bottom: 8px;">
                            📍 Clicked Location
                          </div>
                          <div style="color: #e0e6f5; line-height: 1.6;">
                            <div style="margin-bottom: 6px;">
                              <span style="color: #9ca3af; font-size: 12px;">Latitude:</span>
                              <span style="float: right; font-weight: 600;">${clickedLocationRef.lat.toFixed(4)}°</span>
                            </div>
                            <div style="margin-bottom: 6px;">
                              <span style="color: #9ca3af; font-size: 12px;">Longitude:</span>
                              <span style="float: right; font-weight: 600;">${clickedLocationRef.lon.toFixed(4)}°</span>
                            </div>
                            ${probability !== undefined ? `
                              <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(224, 230, 245, 0.2);">
                                <div style="margin-bottom: 4px;">
                                  <span style="color: #9ca3af; font-size: 12px;">Fire Risk:</span>
                                  <span style="float: right; font-weight: 600; color: ${riskColor};">${riskLevel}</span>
                                </div>
                                <div>
                                  <span style="color: #9ca3af; font-size: 12px;">Probability:</span>
                                  <span style="float: right; font-weight: 600;">${(probability * 100).toFixed(1)}%</span>
                                </div>
                              </div>
                            ` : ''}
                          </div>
                        </div>
                      `,
                      style: {
                        backgroundColor: 'transparent',
                        padding: '0',
                      }
                    };
                  }

                  // Show fire analysis tooltip if hovering fire marker
                  if (info.layer?.id === 'fire-marker' && fireAnalysis) {
                    const analysis = fireAnalysis;
                    return {
                      html: `
                        <div style="padding: 12px; max-width: 320px; background: rgba(10, 14, 39, 0.98); border-radius: 8px; border: 2px solid #ff6b35;">
                          <div style="font-weight: bold; font-size: 16px; color: #ff6b35; margin-bottom: 8px;">
                            🔥 ${analysis.fire_data.date}
                          </div>
                          <div style="color: #e0e6f5; line-height: 1.6; margin-bottom: 8px;">
                            ${analysis.description}
                          </div>
                          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(224, 230, 245, 0.2);">
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Severity</div>
                              <div style="font-weight: bold; color: ${analysis.analysis.severity === 'High' ? '#ff3333' : analysis.analysis.severity === 'Medium' ? '#ff9933' : '#ffcc33'};">
                                ${analysis.analysis.severity}
                              </div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">FRP</div>
                              <div style="font-weight: bold; color: #ff6b35;">${analysis.fire_data.max_frp.toFixed(1)} MW</div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Elevation</div>
                              <div style="color: #e0e6f5;">${analysis.location.elevation_m.toFixed(0)}m</div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Slope</div>
                              <div style="color: #e0e6f5;">${analysis.location.slope_degrees.toFixed(1)}°</div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Temperature</div>
                              <div style="color: #e0e6f5;">${analysis.environmental_conditions.temperature_c.toFixed(1)}°C</div>
                            </div>
                            <div>
                              <div style="font-size: 11px; color: #9ca3af;">Humidity</div>
                              <div style="color: #e0e6f5;">${analysis.environmental_conditions.humidity_percent.toFixed(0)}%</div>
                            </div>
                          </div>
                          ${analysis.risk_factors.length > 0 ? `
                            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(224, 230, 245, 0.2);">
                              <div style="font-size: 11px; color: #9ca3af; margin-bottom: 4px;">Risk Factors:</div>
                              ${analysis.risk_factors.map((factor: string) => 
                                `<div style="color: #ff9933; font-size: 13px;">⚠️ ${factor}</div>`
                              ).join('')}
                            </div>
                          ` : ''}
                        </div>
                      `,
                      style: {
                        backgroundColor: 'transparent',
                        padding: '0',
                      }
                    };
                  }
                  
                  // Show risk cell tooltip
                  const cell = info?.object as RiskGridCell | null;
                  if (!cell || !cell.lat || !cell.lon || cell.prob === undefined) {
                    return null;
                  }
                  return `Risk ${(cell.prob * 100).toFixed(1)}% at ${cell.lat.toFixed(2)}, ${cell.lon.toFixed(2)}`;
                }}
              />
            </div>
            {/* <MapHeatmap data={risk} /> */}
            {/* <MapLegend /> */}
            
            {/* Weather Parameter Legends */}
            {(showTempLayer || showWindLayer || showHumidityLayer || showRainLayer || showRiskLayer) && (
              <div style={{ 
                marginTop: 'var(--spacing-md)', 
                padding: 'var(--spacing-md)',
                background: 'var(--bg-secondary)',
                borderRadius: '8px',
                display: 'grid',
                gap: 'var(--spacing-md)'
              }}>
                <h4 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-primary)' }}>
                  🌍 Active Weather Layers
                </h4>
                
                {showTempLayer && (
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '6px', color: 'var(--text-primary)' }}>
                      🌡️ Temperature (°C)
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      height: '24px', 
                      borderRadius: '4px',
                      overflow: 'hidden',
                      marginBottom: '4px'
                    }}>
                      {TEMP_COLOR_RANGE.map((color, i) => (
                        <div
                          key={i}
                          style={{
                            flex: 1,
                            background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`
                          }}
                        />
                      ))}
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      fontSize: '0.75rem',
                      color: 'var(--text-secondary)'
                    }}>
                      {(() => {
                        const [min, mid, max] = getLegendValues(temperatureRange, [-10, 20, 50]);
                        return (
                          <>
                            <span>{min.toFixed(1)}°C</span>
                            <span>{mid.toFixed(1)}°C</span>
                            <span>{max.toFixed(1)}°C</span>
                          </>
                        );
                      })()}
                    </div>
                  </div>
                )}

                {showWindLayer && (
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '6px', color: 'var(--text-primary)' }}>
                      💨 Wind Speed (m/s)
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      height: '24px', 
                      borderRadius: '4px',
                      overflow: 'hidden',
                      marginBottom: '4px'
                    }}>
                      {WIND_COLOR_RANGE.map((color, i) => (
                        <div
                          key={i}
                          style={{
                            flex: 1,
                            background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`
                          }}
                        />
                      ))}
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      fontSize: '0.75rem',
                      color: 'var(--text-secondary)'
                    }}>
                      {(() => {
                        const [min, mid, max] = getLegendValues(windRange, [0, 15, 30]);
                        return (
                          <>
                            <span>{min.toFixed(1)} m/s</span>
                            <span>{mid.toFixed(1)} m/s</span>
                            <span>{max.toFixed(1)} m/s</span>
                          </>
                        );
                      })()}
                    </div>
                  </div>
                )}

                {showHumidityLayer && (
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '6px', color: 'var(--text-primary)' }}>
                      💧 Relative Humidity (%)
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      height: '24px', 
                      borderRadius: '4px',
                      overflow: 'hidden',
                      marginBottom: '4px'
                    }}>
                      {HUMIDITY_COLOR_RANGE.map((color, i) => (
                        <div
                          key={i}
                          style={{
                            flex: 1,
                            background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`
                          }}
                        />
                      ))}
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      fontSize: '0.75rem',
                      color: 'var(--text-secondary)'
                    }}>
                      {(() => {
                        const [min, mid, max] = getLegendValues(humidityRange, [0, 50, 100]);
                        return (
                          <>
                            <span>{min.toFixed(0)}%</span>
                            <span>{mid.toFixed(0)}%</span>
                            <span>{max.toFixed(0)}%</span>
                          </>
                        );
                      })()}
                    </div>
                  </div>
                )}

                {showRainLayer && (
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '6px', color: 'var(--text-primary)' }}>
                      🌧️ Precipitation (mm/24h)
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      height: '24px', 
                      borderRadius: '4px',
                      overflow: 'hidden',
                      marginBottom: '4px'
                    }}>
                      {RAIN_COLOR_RANGE.map((color, i) => (
                        <div
                          key={i}
                          style={{
                            flex: 1,
                            background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`
                          }}
                        />
                      ))}
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      fontSize: '0.75rem',
                      color: 'var(--text-secondary)'
                    }}>
                      {(() => {
                        const [min, mid, max] = getLegendValues(rainRange, [0, 25, 50]);
                        return (
                          <>
                            <span>{min.toFixed(1)} mm</span>
                            <span>{mid.toFixed(1)} mm</span>
                            <span>{max.toFixed(1)} mm</span>
                          </>
                        );
                      })()}
                    </div>
                  </div>
                )}

                {showRiskLayer && (
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '6px', color: 'var(--text-primary)' }}>
                      🔥 Wildfire Risk
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      height: '24px', 
                      borderRadius: '4px',
                      overflow: 'hidden',
                      marginBottom: '4px'
                    }}>
                      {RISK_COLOR_RANGE.map((color, i) => (
                        <div
                          key={i}
                          style={{
                            flex: 1,
                            background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`
                          }}
                        />
                      ))}
                    </div>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      fontSize: '0.75rem',
                      color: 'var(--text-secondary)'
                    }}>
                      <span>0%</span>
                      <span>50%</span>
                      <span>100%</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Temperature Heatmap Visualization - HIDDEN */}
          {false && (
          <div className="tri-view" style={{ marginTop: 'var(--spacing-lg)' }}>
            <h3>🌡️ Global Temperature Heatmap</h3>
            <div className="tri-view__deck" style={{ height: '500px' }}>
              <DeckGL
                style={{ width: "100%", height: "100%" }}
                layers={[
                  new TileLayer({
                    id: "temp-base-map",
                    data: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    minZoom: 0,
                    maxZoom: 19,
                    tileSize: 256,
                    renderSubLayers: (props: any) => {
                      if (!props.data) return null;
                      const {
                        bbox: {west, south, east, north}
                      } = props.tile;
                      return new BitmapLayer(props, {
                        data: null,
                        image: props.data,
                        bounds: [west, south, east, north]
                      });
                    },
                  }),
                  showTempLayer && temperatureData.length > 0 ? new HeatmapLayer({
                    id: 'global-temperature-heatmap',
                    data: temperatureData,
                    getPosition: (d: TemperaturePoint) => [d.longitude, d.latitude],
                    getWeight: (d: TemperaturePoint) => Math.max(0, d.temperature + 10),
                    radiusPixels: 50,
                    intensity: 2,
                    threshold: 0.05,
                    colorRange: TEMP_COLOR_RANGE as any,
                    aggregation: 'MEAN',
                  }) : null,
                ].filter(Boolean)}
                initialViewState={{
                  longitude: 0,
                  latitude: 20,
                  zoom: 2,
                  pitch: 0,
                  bearing: 0
                }}
                controller
                getTooltip={(info: PickingInfo<any>) => {
                  const temp = info?.object as TemperaturePoint | null;
                  if (!temp || temp.temperature === undefined) return null;
                  return `Temperature: ${temp.temperature.toFixed(1)}°C`;
                }}
              />
            </div>
            <div style={{ 
              marginTop: 'var(--spacing-md)', 
              padding: 'var(--spacing-md)',
              background: 'var(--bg-secondary)',
              borderRadius: '8px'
            }}>
              <h4 style={{ marginBottom: 'var(--spacing-sm)', fontSize: '0.9rem' }}>
                Temperature Scale (°C)
              </h4>
              <div style={{ 
                display: 'flex', 
                height: '30px', 
                borderRadius: '4px',
                overflow: 'hidden',
                marginBottom: 'var(--spacing-sm)'
              }}>
                {TEMP_COLOR_RANGE.map((color, i) => (
                  <div
                    key={i}
                    style={{
                      flex: 1,
                      background: `rgb(${color[0]}, ${color[1]}, ${color[2]})`
                    }}
                  />
                ))}
              </div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                fontSize: '0.75rem',
                color: 'var(--text-secondary)'
              }}>
                <span>-10°C (Blue)</span>
                <span>20°C (Green)</span>
                <span>50°C (Red)</span>
              </div>
            </div>
          </div>
          )}
        </>
      )}
      <TimeScrubber date={date} onChange={setDate} />
    </div>
  );
};

export default TriView;
