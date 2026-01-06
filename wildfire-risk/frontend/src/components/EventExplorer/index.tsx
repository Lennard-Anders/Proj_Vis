import React, { useEffect, useMemo, useState } from "react";
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
  const [hoverInfo, setHoverInfo] = useState<{ event: FireEvent; left: number } | null>(null);
  const [hoverLocation, setHoverLocation] = useState<string>('');
  const [hoverLocationLoading, setHoverLocationLoading] = useState(false);

  // Region definitions
  const regions: Record<string, { name: string; lat?: number; lon?: number; radius?: number; bounds?: { latMin: number; latMax: number; lonMin: number; lonMax: number } }> = {
    americas: { name: '🌎 Americas' },
    northamerica: { name: '🇺🇸 North America', lat: 45, lon: -100, radius: 2500, bounds: { latMin: 5, latMax: 83, lonMin: -170, lonMax: -50 } },
    southamerica: { name: '🇧🇷 South America', lat: -15, lon: -60, radius: 2500, bounds: { latMin: -60, latMax: 15, lonMin: -90, lonMax: -30 } },
    amazon: { name: '🌳 Amazon Basin', lat: -5, lon: -62, radius: 1500, bounds: { latMin: -20, latMax: 10, lonMin: -75, lonMax: -45 } },
    california: { name: '🔥 California', lat: 37, lon: -120, radius: 700, bounds: { latMin: 32, latMax: 42.5, lonMin: -125, lonMax: -114 } },
    australia: { name: '🇦🇺 Australia', lat: -25, lon: 135, radius: 2000, bounds: { latMin: -44, latMax: -10, lonMin: 112, lonMax: 155 } },
    canada: { name: '🇨🇦 Canada', lat: 60, lon: -110, radius: 2200, bounds: { latMin: 41, latMax: 83, lonMin: -141, lonMax: -52 } },
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

  const loadTimeRange = (yearsBackValue: number, regionKey: string = selectedRegion) => {
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
      const region = regions[regionKey];
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
    const newRegion = event.target.value;
    setSelectedRegion(newRegion);
    // Reload data with new region
    loadTimeRange(yearsBack, newRegion);
  };

  const getYearRangeLabel = () => {
    const endYear = currentYear - (yearsBack * 5);
    const startYear = endYear - 5;
    return `${startYear}-${endYear}`;
  };


  const calculateDistanceKm = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const toRad = (deg: number) => (deg * Math.PI) / 180;
    const R = 6371; // Earth radius in km
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  const filteredEvents = useMemo(() => {
    if (!fireHistory) return [];
    const region = regions[selectedRegion];
    if (!region) return fireHistory.events;

    // If we have bounds, use them for a tighter geographic filter; otherwise fall back to radius.
    if (region.bounds) {
      const { latMin, latMax, lonMin, lonMax } = region.bounds;
      return fireHistory.events.filter((event) => (
        event.latitude >= latMin && event.latitude <= latMax &&
        event.longitude >= lonMin && event.longitude <= lonMax
      ));
    }

    if (region.lat !== undefined && region.lon !== undefined && region.radius !== undefined) {
      return fireHistory.events.filter((event) => {
        const distance = calculateDistanceKm(region.lat!, region.lon!, event.latitude, event.longitude);
        return distance <= region.radius!;
      });
    }

    return fireHistory.events;
  }, [fireHistory, selectedRegion]);

  // Fetch location for hovered event (matches Global Context Map behavior)
  useEffect(() => {
    if (!hoverInfo?.event) {
      setHoverLocation('');
      setHoverLocationLoading(false);
      return;
    }

    const { latitude, longitude } = hoverInfo.event;
    let cancelled = false;
    setHoverLocationLoading(true);

    const timer = setTimeout(async () => {
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=5&addressdetails=1`,
          { headers: { 'User-Agent': 'WildfireRiskExplorer/1.0' } }
        );
        const data = await response.json();
        const address = data.address || {};
        const parts: string[] = [];
        if (address.state || address.region) parts.push(address.state || address.region);
        if (address.country) parts.push(address.country);
        const name = parts.length > 0 ? parts.join(', ') : 'Unknown location';
        if (!cancelled) setHoverLocation(name);
      } catch (error) {
        console.error('Failed to fetch location:', error);
        if (!cancelled) setHoverLocation('Unknown location');
      } finally {
        if (!cancelled) setHoverLocationLoading(false);
      }
    }, 200);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [hoverInfo?.event]);

  return (
    <div className="timeline-wrapper">
      <div className="timeline-controls">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>
            🔥 Wildfire History
          </h3>
          <span 
            className="status-indicator" 
            style={{ backgroundColor: getStatusColor() }}
            title={loading ? 'Loading...' : loadError ? 'Error' : fireHistory ? 'Loaded' : 'Not loaded'}
          />
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <select 
            value={selectedRegion}
            onChange={handleRegionChange}
            style={{
              padding: '4px 8px',
              fontSize: '0.85rem',
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
          
          <button
            onClick={handleGoBack5Years}
            disabled={loading}
            style={{
              padding: '4px 8px',
              fontSize: '0.85rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              backgroundColor: loading ? '#ccc' : '#64748b',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
            }}
          >
            ◀
          </button>
          
          <div style={{ fontWeight: 'bold', fontSize: '0.85rem', color: '#1a1f3a', minWidth: '80px', textAlign: 'center' }}>
            {getYearRangeLabel()}
          </div>
          
          <button
            onClick={handleGoForward5Years}
            disabled={loading || yearsBack === 0}
            style={{
              padding: '4px 8px',
              fontSize: '0.85rem',
              cursor: (loading || yearsBack === 0) ? 'not-allowed' : 'pointer',
              backgroundColor: (loading || yearsBack === 0) ? '#ccc' : '#64748b',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
            }}
          >
            ▶
          </button>
          
          <button 
            onClick={handleLoadClick}
            disabled={loading}
            style={{
              padding: '4px 8px',
              fontSize: '0.85rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              backgroundColor: loading ? '#ccc' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
            }}
          >
            🔄
          </button>
        </div>
      </div>
      
      {loading && (
        <div className="timeline-message">⏳ Loading fires...</div>
      )}
      
      {loadError && (
        <div className="timeline-message" style={{ color: '#ff3333' }}>
          ❌ Failed to load. Try again.
        </div>
      )}
      
      {!loading && !loadError && !fireHistory && (
        <div className="timeline-message">No data loaded</div>
      )}
      
      {fireHistory && filteredEvents.length === 0 && (
        <div className="timeline-message">
          ✅ No fires found ({fireHistory.period_start} to {fireHistory.period_end})
        </div>
      )}
      
      {fireHistory && filteredEvents.length > 0 && (
        <>
          <div className="timeline-scroll">
            <div className="timeline-track">
              {filteredEvents
                .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
                .map((event) => {
                  const isSelected = selectedFireEvent?.event_id === event.event_id;
                  const frp = event.fire_radiative_power;
                  const emoji = '🔥';
                  
                  return (
                    <div
                      key={event.event_id}
                      className={`timeline-event ${isSelected ? 'timeline-event--selected' : ''}`}
                      onClick={() => handleEventClick(event)}
                      onMouseEnter={(e) => {
                        const target = e.currentTarget;
                        const left = target.offsetLeft + target.offsetWidth / 2;
                        setHoverInfo({ event, left });
                      }}
                      onMouseLeave={() => setHoverInfo(null)}
                    >
                      <div className="timeline-event-emoji">{emoji}</div>
                      {isSelected && <div className="timeline-event-marker">📍</div>}
                    </div>
                  );
                })}
              {hoverInfo && (
                <div className="timeline-tooltip" style={{ left: hoverInfo.left }}>
                  <div className="timeline-tooltip__row">📍 {hoverLocationLoading ? 'Loading...' : hoverLocation || 'Unknown location'}</div>
                  <div className="timeline-tooltip__row">📅 {formatDate(hoverInfo.event.date)}</div>
                  <div className="timeline-tooltip__row">🔥 FRP: {hoverInfo.event.fire_radiative_power.toFixed(1)} MW</div>
                  <div className="timeline-tooltip__row">✅ Confidence: {hoverInfo.event.confidence}%</div>
                </div>
              )}
            </div>
          </div>
          
          {selectedFireEvent && (
            <div className="timeline-hint">
              💡 <strong>Fire marked on map</strong> - Hover for details
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default EventExplorer;
