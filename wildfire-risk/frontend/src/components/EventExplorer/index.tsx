import React, { useEffect, useState } from "react";
import { useFireHistory, useSelectedFireEvent, useLoadFireHistory, useSelectFireEvent } from "../../state/selectors";
import type { FireEvent } from "../../api/types";

const EventExplorer: React.FC = () => {
  const fireHistory = useFireHistory();
  const selectedFireEvent = useSelectedFireEvent();
  const loadFireHistory = useLoadFireHistory();
  const selectFireEvent = useSelectFireEvent();
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [currentYear] = useState(new Date().getFullYear());
  const [yearsBack, setYearsBack] = useState(0);
  const [selectedRegion, setSelectedRegion] = useState('california');

  // Region definitions
  const regions: Record<string, { name: string; lat?: number; lon?: number; radius?: number }> = {
    americas: { name: '🌎 Americas' },
    northamerica: { name: '🇺🇸 North America', lat: 45, lon: -100, radius: 2500 },
    southamerica: { name: '🇧🇷 South America', lat: -15, lon: -60, radius: 2500 },
    amazon: { name: '🌳 Amazon Basin', lat: -5, lon: -62, radius: 1500 },
    california: { name: '🔥 California', lat: 37, lon: -120, radius: 500 },
    australia: { name: '🇦🇺 Australia', lat: -25, lon: 135, radius: 2000 },
    canada: { name: '🇨🇦 Canada', lat: 60, lon: -110, radius: 2000 },
  };

  useEffect(() => {
    if (loadFireHistory && typeof loadFireHistory === 'function' && !fireHistory) {
      loadTimeRange(0);
    }
  }, [loadFireHistory]);

  const handleEventClick = (event: FireEvent) => {
    if (selectFireEvent) {
      selectFireEvent(selectedFireEvent?.event_id === event.event_id ? undefined : event);
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const getSeverityColor = (frp: number) => {
    if (frp > 100) return '#ff3333';
    if (frp > 50) return '#ff9933';
    return '#ffcc33';
  };

  const getStatusColor = () => {
    if (loading) return '#ffa500';
    if (loadError) return '#ff3333';
    if (fireHistory && fireHistory.events.length > 0) return '#00cc66';
    if (fireHistory) return '#999999';
    return '#999999';
  };

  const handleLoadClick = () => {
    loadTimeRange(yearsBack);
  };

  const handleGoBack5Years = () => {
    const newYearsBack = yearsBack + 1;
    setYearsBack(newYearsBack);
    loadTimeRange(newYearsBack);
  };

  const handleGoForward5Years = () => {
    if (yearsBack > 0) {
      const newYearsBack = yearsBack - 1;
      setYearsBack(newYearsBack);
      loadTimeRange(newYearsBack);
    }
  };

  const loadTimeRange = (yearsBackValue: number) => {
    if (loadFireHistory && typeof loadFireHistory === 'function') {
      setLoading(true);
      setLoadError(false);
      
      // Calculate the specific 5-year window
      const now = new Date();
      const yearsAgo = yearsBackValue * 5;
      const endDate = new Date(now.getFullYear() - yearsAgo, now.getMonth(), now.getDate());
      const startDate = new Date(endDate.getFullYear() - 5, endDate.getMonth(), endDate.getDate());
      
      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];
      
      // Get region parameters
      const region = regions[selectedRegion];
      const lat = region.lat;
      const lon = region.lon;
      const radius = region.radius;
      
      console.log(`Loading fires: ${region.name}, ${startDateStr} to ${endDateStr}`);
      
      loadFireHistory(lat, lon, radius, undefined, startDateStr, endDateStr)
        .then(() => console.log('Fire history loaded'))
        .catch((error) => {
          console.error('Load error:', error);
          setLoadError(true);
        })
        .finally(() => setLoading(false));
    }
  };

  const handleRegionChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedRegion(event.target.value);
    // Reload data with new region
    loadTimeRange(yearsBack);
  };

  const getYearRangeLabel = () => {
    const endYear = currentYear - (yearsBack * 5);
    const startYear = endYear - 5;
    return `${startYear}-${endYear}`;
  };

  return (
    <div className="panel event-explorer">
      <h2 style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
        🔥 Wildfire History
        <span 
          className="status-indicator" 
          style={{ backgroundColor: getStatusColor() }}
          title={loading ? 'Loading...' : loadError ? 'Error' : fireHistory ? 'Loaded' : 'Not loaded'}
        />
        <button 
          onClick={handleLoadClick}
          disabled={loading}
          style={{
            padding: '4px 12px',
            fontSize: '0.8rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            backgroundColor: loading ? '#ccc' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            marginLeft: 'auto'
          }}
        >
          {loading ? 'Loading...' : '🔄'}
        </button>
      </h2>
      
      {/* Region selector */}
      <div style={{ marginBottom: '12px' }}>
        <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px', fontWeight: '500' }}>
          Region:
        </label>
        <select 
          value={selectedRegion}
          onChange={handleRegionChange}
          style={{
            width: '100%',
            padding: '6px 8px',
            fontSize: '0.9rem',
            borderRadius: '4px',
            border: '1px solid #ccc',
            backgroundColor: 'white',
            cursor: 'pointer'
          }}
        >
          {Object.entries(regions).map(([key, region]) => (
            <option key={key} value={key}>
              {region.name}
            </option>
          ))}
        </select>
      </div>
      
      {/* Time navigation */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', padding: '8px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
        <button
          onClick={handleGoBack5Years}
          disabled={loading}
          style={{
            padding: '6px 12px',
            fontSize: '0.85rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            backgroundColor: loading ? '#ccc' : '#64748b',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
          }}
        >
          ◀ -5 Yrs
        </button>
        
        <div style={{ flex: 1, textAlign: 'center', fontWeight: 'bold', fontSize: '0.9rem', color: '#1a1f3a' }}>
          {getYearRangeLabel()}
        </div>
        
        <button
          onClick={handleGoForward5Years}
          disabled={loading || yearsBack === 0}
          style={{
            padding: '6px 12px',
            fontSize: '0.85rem',
            cursor: (loading || yearsBack === 0) ? 'not-allowed' : 'pointer',
            backgroundColor: (loading || yearsBack === 0) ? '#ccc' : '#64748b',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
          }}
        >
          +5 Yrs ▶
        </button>
      </div>
      
      {loading && <p className="event-explorer__loading">Loading fires...</p>}
      
      {loadError && (
        <div className="event-explorer__error" style={{ color: '#ff3333', padding: '10px' }}>
          ❌ Failed to load. Try again.
        </div>
      )}
      
      {!loading && !loadError && !fireHistory && (
        <p className="event-explorer__empty">No data.</p>
      )}
      
      {fireHistory && fireHistory.events.length === 0 && (
        <div className="event-explorer__empty">
          <p>✅ No fires found</p>
          <small>{fireHistory.period_start} to {fireHistory.period_end}</small>
        </div>
      )}
      
      {fireHistory && fireHistory.events.length > 0 && (
        <>
          <div className="event-explorer__header">
            <p className="event-explorer__summary">
              {fireHistory.total_events} fire{fireHistory.total_events !== 1 ? 's' : ''}
              <br />
              <small>{fireHistory.period_start} to {fireHistory.period_end}</small>
            </p>
          </div>
          
          <div className="event-explorer__timeline">
            {fireHistory.events.map((event) => {
              const isSelected = selectedFireEvent?.event_id === event.event_id;
              const severityColor = getSeverityColor(event.fire_radiative_power);
              
              return (
                <div
                  key={event.event_id}
                  className={`event-explorer__event ${isSelected ? 'event-explorer__event--selected' : ''}`}
                  onClick={() => handleEventClick(event)}
                  style={{ borderLeftColor: severityColor }}
                >
                  <div className="event-explorer__event-icon" style={{ backgroundColor: severityColor }}>
                    🔥
                  </div>
                  <div className="event-explorer__event-info">
                    <div className="event-explorer__event-date">{formatDate(event.date)}</div>
                    <div className="event-explorer__event-location">
                      {event.latitude.toFixed(3)}°N, {event.longitude.toFixed(3)}°E
                    </div>
                    <div className="event-explorer__event-meta">
                      <span title="Fire Radiative Power">FRP: {event.fire_radiative_power.toFixed(1)} MW</span>
                      <span title="Confidence">Conf: {event.confidence}%</span>
                    </div>
                  </div>
                  {isSelected && (
                    <div className="event-explorer__event-indicator">📍</div>
                  )}
                </div>
              );
            })}
          </div>
          
          {selectedFireEvent && (
            <div className="event-explorer__hint">
              💡 <strong>Fire marked on map</strong> - Hover for details
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default EventExplorer;
