"""AI-powered wildfire risk prediction service using machine learning."""
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WildfireRiskPredictor:
    """
    ML-based wildfire risk predictor.
    Uses a combination of temperature, humidity, wind speed, and historical patterns.
    """
    
    def __init__(self):
        """Initialize the predictor with pre-trained coefficients."""
        # Coefficients based on wildfire risk factors (simplified logistic model)
        # These are derived from domain knowledge of wildfire risk factors
        self.coefficients = {
            'temperature': 0.045,      # Higher temp = higher risk
            'wind_speed_10m': 0.035,   # Higher wind = higher risk
            'rh': -0.040,              # Higher humidity = lower risk (rh is relative humidity)
            'rain_24h': -0.060,        # More rain = lower risk
            'vegetation_dryness': 0.050,  # Drier vegetation = higher risk
            'temp_anomaly': 0.030,     # Temperature above normal = higher risk
            'drought_index': 0.025,    # Higher drought = higher risk
        }
        self.intercept = -3.5  # Base log-odds (low baseline risk)
    
    def _sigmoid(self, x: float) -> float:
        """Sigmoid function to convert log-odds to probability."""
        return 1.0 / (1.0 + np.exp(-x))
    
    def _calculate_temp_anomaly(self, current_temp: float, historical_mean: float) -> float:
        """Calculate temperature anomaly (difference from historical mean)."""
        return current_temp - historical_mean
    
    def _estimate_vegetation_dryness(
        self,
        temperature: float,
        humidity: float,
        rain_24h: float
    ) -> float:
        """
        Estimate vegetation dryness index (0-100).
        Higher values indicate drier, more flammable vegetation.
        """
        # Simple model: high temp + low humidity + no rain = dry vegetation
        dryness = 0.0
        
        # Temperature contribution (normalized to 0-40 range)
        if temperature > 25:
            dryness += min((temperature - 25) / 15 * 40, 40)
        
        # Humidity contribution (inverse)
        dryness += max(0, (100 - humidity) / 100 * 35)
        
        # Rain contribution (inverse)
        if rain_24h < 5:
            dryness += max(0, (5 - rain_24h) / 5 * 25)
        
        return min(dryness, 100)
    
    def _estimate_drought_index(
        self,
        temp_anomaly: float,
        rain_24h: float,
        humidity: float
    ) -> float:
        """
        Estimate drought index (0-100).
        Based on temperature anomaly, precipitation, and humidity.
        """
        drought = 0.0
        
        # Positive temperature anomaly contributes to drought
        if temp_anomaly > 0:
            drought += min(temp_anomaly / 10 * 40, 40)
        
        # Low precipitation contributes to drought
        if rain_24h < 10:
            drought += (10 - rain_24h) / 10 * 35
        
        # Low humidity contributes to drought
        if humidity < 40:
            drought += (40 - humidity) / 40 * 25
        
        return min(drought, 100)
    
    def predict_risk(
        self,
        latitude: float,
        longitude: float,
        temperature: float,
        wind_speed_10m: float,
        rh: float,  # relative humidity (%)
        rain_24h: float = 0.0,
        historical_mean_temp: Optional[float] = None,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict wildfire risk for a location with given conditions.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            temperature: Current temperature (°C)
            wind_speed_10m: Wind speed at 10m (m/s)
            rh: Relative humidity (%)
            rain_24h: 24-hour rainfall (mm)
            historical_mean_temp: Historical mean temperature for this location
            date: Date string for context
        
        Returns:
            Dictionary with:
                - probability: Wildfire risk probability (0-1)
                - risk_level: Risk category (low/moderate/high/extreme)
                - contributing_factors: List of risk factors with their contributions
                - recommendations: Safety recommendations
                - confidence: Prediction confidence (0-1)
        """
        try:
            # Use default historical mean if not provided
            if historical_mean_temp is None:
                historical_mean_temp = 20.0
            
            # Calculate derived features
            temp_anomaly = self._calculate_temp_anomaly(temperature, historical_mean_temp)
            vegetation_dryness = self._estimate_vegetation_dryness(temperature, rh, rain_24h)
            drought_index = self._estimate_drought_index(temp_anomaly, rain_24h, rh)
            
            # Prepare features
            features = {
                'temperature': temperature,
                'wind_speed_10m': wind_speed_10m,
                'rh': rh,
                'rain_24h': rain_24h,
                'vegetation_dryness': vegetation_dryness,
                'temp_anomaly': temp_anomaly,
                'drought_index': drought_index,
            }
            
            # Calculate log-odds
            log_odds = self.intercept
            contributions = {}
            
            for feature_name, value in features.items():
                if feature_name in self.coefficients:
                    contribution = self.coefficients[feature_name] * value
                    log_odds += contribution
                    contributions[feature_name] = contribution
            
            # Convert to probability
            probability = self._sigmoid(log_odds)
            
            # Determine risk level
            if probability < 0.2:
                risk_level = "low"
                risk_color = "#4CAF50"
            elif probability < 0.4:
                risk_level = "moderate"
                risk_color = "#FFC107"
            elif probability < 0.7:
                risk_level = "high"
                risk_color = "#FF9800"
            else:
                risk_level = "extreme"
                risk_color = "#F44336"
            
            # Identify top contributing factors
            sorted_contributions = sorted(
                contributions.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            contributing_factors = []
            for feature, contrib in sorted_contributions[:5]:
                # Format feature name for display
                feature_display = {
                    'temperature': f'Temperature: {temperature:.1f}°C',
                    'wind_speed_10m': f'Wind Speed: {wind_speed_10m:.1f} m/s',
                    'rh': f'Humidity: {rh:.0f}%',
                    'rain_24h': f'Rainfall: {rain_24h:.1f} mm',
                    'vegetation_dryness': f'Vegetation Dryness: {vegetation_dryness:.0f}/100',
                    'temp_anomaly': f'Temp Anomaly: {temp_anomaly:+.1f}°C',
                    'drought_index': f'Drought Index: {drought_index:.0f}/100',
                }.get(feature, feature)
                
                contributing_factors.append({
                    'factor': feature_display,
                    'contribution': float(contrib),
                    'impact': 'increases' if contrib > 0 else 'decreases'
                })
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                probability, temperature, rh, wind_speed_10m, rain_24h
            )
            
            # Calculate confidence based on data completeness
            confidence = 0.85  # Base confidence
            if historical_mean_temp is None:
                confidence -= 0.1
            
            result = {
                'probability': float(probability),
                'risk_level': risk_level,
                'risk_color': risk_color,
                'contributing_factors': contributing_factors,
                'recommendations': recommendations,
                'confidence': float(confidence),
                'features': {
                    'temperature': float(temperature),
                    'wind_speed': float(wind_speed_10m),
                    'humidity': float(rh),
                    'rainfall': float(rain_24h),
                    'vegetation_dryness': float(vegetation_dryness),
                    'drought_index': float(drought_index),
                }
            }
            
            logger.info(f"Risk prediction: {probability:.2%} ({risk_level}) at ({latitude}, {longitude})")
            return result
        
        except Exception as e:
            logger.error(f"Error predicting risk: {e}")
            return {
                'probability': 0.3,
                'risk_level': 'moderate',
                'risk_color': '#FFC107',
                'contributing_factors': [],
                'recommendations': ['Error calculating risk. Please try again.'],
                'confidence': 0.0,
                'features': {}
            }
    
    def _generate_recommendations(
        self,
        probability: float,
        temperature: float,
        humidity: float,
        wind_speed: float,
        rainfall: float
    ) -> List[str]:
        """Generate safety recommendations based on risk factors."""
        recommendations = []
        
        if probability >= 0.7:
            recommendations.append("⚠️ EXTREME RISK: Avoid outdoor activities and be prepared to evacuate")
            recommendations.append("Monitor local emergency alerts and have evacuation plan ready")
        elif probability >= 0.4:
            recommendations.append("⚠️ HIGH RISK: Exercise extreme caution with any fire use")
            recommendations.append("Stay informed about local fire conditions")
        elif probability >= 0.2:
            recommendations.append("⚠️ MODERATE RISK: Be cautious with outdoor fires")
        else:
            recommendations.append("✓ LOW RISK: Normal fire safety precautions apply")
        
        # Specific factor-based recommendations
        if temperature > 35:
            recommendations.append(f"🌡️ Very high temperature ({temperature:.1f}°C) increases fire risk significantly")
        
        if humidity < 20:
            recommendations.append(f"💧 Very low humidity ({humidity:.0f}%) - extremely dry conditions")
        
        if wind_speed > 10:
            recommendations.append(f"💨 Strong winds ({wind_speed:.1f} m/s) can rapidly spread fires")
        
        if rainfall < 1:
            recommendations.append("🌧️ No recent rainfall - vegetation is likely very dry")
        
        return recommendations
    
    def predict_grid_risk(
        self,
        center_lat: float,
        center_lon: float,
        grid_size_deg: float,
        grid_resolution: int,
        base_params: Dict[str, float],
        historical_stats: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Predict wildfire risk for a grid of locations around a center point.
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            grid_size_deg: Grid size in degrees
            grid_resolution: Number of grid cells per side
            base_params: Base parameters (temperature, wind, humidity, etc.)
            historical_stats: Historical temperature statistics
        
        Returns:
            List of grid cells with lat, lon, probability, risk_level
        """
        grid_cells = []
        
        # Calculate step size
        step = grid_size_deg / grid_resolution
        
        # Get historical mean temp
        hist_mean_temp = None
        if historical_stats:
            hist_mean_temp = historical_stats.get('mean_temp', 20.0)
        
        # Generate grid
        for i in range(grid_resolution):
            for j in range(grid_resolution):
                lat = center_lat - grid_size_deg/2 + i * step
                lon = center_lon - grid_size_deg/2 + j * step
                
                # Add some spatial variation (simple model)
                temp_variation = np.random.normal(0, 1.5)
                wind_variation = np.random.normal(0, 1.0)
                humidity_variation = np.random.normal(0, 5.0)
                
                prediction = self.predict_risk(
                    latitude=lat,
                    longitude=lon,
                    temperature=base_params.get('temperature', 25) + temp_variation,
                    wind_speed_10m=base_params.get('wind_speed_10m', 5) + wind_variation,
                    rh=max(0, min(100, base_params.get('rh', 50) + humidity_variation)),
                    rain_24h=base_params.get('rain_24h', 0),
                    historical_mean_temp=hist_mean_temp
                )
                
                grid_cells.append({
                    'latitude': lat,
                    'longitude': lon,
                    'probability': prediction['probability'],
                    'risk_level': prediction['risk_level'],
                    'risk_color': prediction['risk_color']
                })
        
        return grid_cells


# Global instance
wildfire_predictor = WildfireRiskPredictor()
