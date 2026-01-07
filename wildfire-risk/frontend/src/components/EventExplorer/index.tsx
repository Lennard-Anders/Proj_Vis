import React, { useEffect, useMemo, useState } from "react";
import { useFireHistory, useSelectedFireEvent, useLoadFireHistory, useSelectFireEvent, useSelectedRegion, useSetSelectedRegion, useSelectedYear, useSetSelectedYear } from "../../state/selectors";
import { REGION_PRESETS } from "../../utils/regions";
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
  const selectedRegion = useSelectedRegion() || 'california';
  const setSelectedRegion = useSetSelectedRegion();
  const [hoverInfo, setHoverInfo] = useState<{ event: FireEvent; left: number } | null>(null);
  const [hoverLocation, setHoverLocation] = useState<string>('');
  const [hoverLocationLoading, setHoverLocationLoading] = useState(false);
  const selectedYear = useSelectedYear() ?? null;
  const setSelectedYear = useSetSelectedYear();
  const [showInfoTooltip, setShowInfoTooltip] = useState(false);

  useEffect(() => {
    if (loadFireHistory && typeof loadFireHistory === 'function' && !fireHistory) {
      // Initial load: fetch global dataset for the time window
      loadTimeRange(0, undefined);
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

  const loadTimeRange = (yearsBackValue: number, regionKey?: string) => {
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
      
      // If a region is provided, load around that region; otherwise, load globally.
      let lat: number | undefined;
      let lon: number | undefined;
      let radius: number | undefined;
      if (regionKey) {
        const region = REGION_PRESETS[regionKey];
        if (!region) {
          console.warn(`Unknown region key: ${regionKey}`);
          setLoading(false);
          return;
        }
        lat = region.lat;
        lon = region.lon;
        radius = region.radius;
        console.log(`Loading fires: ${region.name}, ${startDateStr} to ${endDateStr}`);
      } else {
        console.log(`Loading fires: Global (Americas), ${startDateStr} to ${endDateStr}`);
      }

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
    if (setSelectedRegion) {
      setSelectedRegion(newRegion);
    }
    // No reload needed; we keep a global dataset and filter client-side.
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
    const region = REGION_PRESETS[selectedRegion];
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

  const yearFilteredEvents = useMemo(() => {
    if (!selectedYear) return filteredEvents;
    return filteredEvents.filter((ev) => new Date(ev.date).getFullYear() === selectedYear);
  }, [filteredEvents, selectedYear]);

  const frpScale = useMemo(() => {
    if (!yearFilteredEvents.length) return { min: 0, max: 0 };
    const values = yearFilteredEvents.map((ev) => Math.max(ev.fire_radiative_power, 0));
    const min = Math.min(...values);
    const max = Math.max(...values);
    return { min, max };
  }, [yearFilteredEvents]);

  const getEmojiSize = (frp: number) => {
    const minSize = 12;
    const maxSize = 60;
    const min = frpScale.min;
    const max = frpScale.max;
    if (max <= min) return (minSize + maxSize) / 2;
    const clamped = Math.max(frp, min);
    const t = (clamped - min) / (max - min);
    const eased = Math.sqrt(t); // emphasize higher FRP while keeping low values small
    return minSize + eased * (maxSize - minSize);
  };

  const monthGroups = useMemo(() => {
    if (!yearFilteredEvents.length) return [];
    const sorted = [...yearFilteredEvents].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
    const groups: Array<{ key: string; label: string; events: FireEvent[] }> = [];

    sorted.forEach((ev) => {
      const d = new Date(ev.date);
      const key = `${d.getFullYear()}-${d.getMonth()}`;
      const label = d.toLocaleString('en-US', { month: 'short' });
      const current = groups[groups.length - 1];
      if (current && current.key === key) {
        current.events.push(ev);
      } else {
        groups.push({ key, label, events: [ev] });
      }
    });

    return groups;
  }, [yearFilteredEvents]);

  const availableYears = useMemo(() => {
    const events = fireHistory?.events || [];
    if (!events.length) return [] as number[];
    const years = Array.from(new Set(events.map((ev) => new Date(ev.date).getFullYear())));
    return years.sort((a, b) => b - a);
  }, [fireHistory?.events]);

  useEffect(() => {
    if (!filteredEvents.length) {
      if (setSelectedYear) setSelectedYear(null);
      return;
    }
    const newest = Math.max(...filteredEvents.map((ev) => new Date(ev.date).getFullYear()));
    if (setSelectedYear) setSelectedYear((selectedYear && availableYears.includes(selectedYear)) ? selectedYear : newest);
  }, [filteredEvents, availableYears]);

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

  // Compute total event counts per region strictly for the selectedYear
  const regionCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    const events = fireHistory?.events || [];
    if (!selectedYear) {
      // No selected year -> show 0 for all regions to avoid aggregating across years
      Object.keys(REGION_PRESETS).forEach((key) => { counts[key] = 0; });
      return counts;
    }
    const byYear = (ev: FireEvent) => new Date(ev.date).getFullYear() === selectedYear;

    const calculateDistanceKmLocal = (lat1: number, lon1: number, lat2: number, lon2: number) => {
      const toRad = (deg: number) => (deg * Math.PI) / 180;
      const R = 6371;
      const dLat = toRad(lat2 - lat1);
      const dLon = toRad(lon2 - lon1);
      const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      return R * c;
    };

    Object.entries(REGION_PRESETS).forEach(([key, region]) => {
      let regionEvents: FireEvent[] = [];
      if (region.bounds) {
        const { latMin, latMax, lonMin, lonMax } = region.bounds;
        regionEvents = events.filter((ev) => (
          ev.latitude >= latMin && ev.latitude <= latMax &&
          ev.longitude >= lonMin && ev.longitude <= lonMax
        ));
      } else if (region.lat !== undefined && region.lon !== undefined && region.radius !== undefined) {
        regionEvents = events.filter((ev) => calculateDistanceKmLocal(region.lat!, region.lon!, ev.latitude, ev.longitude) <= region.radius!);
      } else {
        regionEvents = events;
      }
      counts[key] = regionEvents.filter(byYear).length;
    });
    return counts;
  }, [fireHistory?.events, selectedYear]);

  // Compute global per-year counts (All Americas) for year dropdown
  const yearCounts = useMemo(() => {
    const counts: Record<number, number> = {};
    const events = fireHistory?.events || [];
    events.forEach((ev) => {
      const yr = new Date(ev.date).getFullYear();
      counts[yr] = (counts[yr] ?? 0) + 1;
    });
    return counts;
  }, [fireHistory?.events]);

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
          <div style={{ position: 'relative', display: 'inline-flex' }}>
            <span
              role="button"
              tabIndex={0}
              aria-label="Emoji size legend"
              aria-describedby={showInfoTooltip ? 'emoji-size-tooltip' : undefined}
              onMouseEnter={() => setShowInfoTooltip(true)}
              onMouseLeave={() => setShowInfoTooltip(false)}
              onFocus={() => setShowInfoTooltip(true)}
              onBlur={() => setShowInfoTooltip(false)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  setShowInfoTooltip((v) => !v);
                }
              }}
              style={{
                marginLeft: '4px',
                display: 'inline-flex',
                width: '18px',
                height: '18px',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid #888',
                borderRadius: '50%',
                fontSize: '12px',
                fontWeight: 700,
                color: '#555',
                backgroundColor: '#fff',
                cursor: 'default',
                userSelect: 'none',
                outline: 'none'
              }}
            >
              i
            </span>
            {showInfoTooltip && (
              <div
                id="emoji-size-tooltip"
                role="tooltip"
                style={{
                  position: 'absolute',
                  top: '22px',
                  left: '-4px',
                  backgroundColor: '#fff',
                  color: '#333',
                  border: '1px solid #ddd',
                  borderRadius: '6px',
                  padding: '6px 8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                  fontSize: '0.8rem',
                  whiteSpace: 'nowrap',
                  zIndex: 10
                }}
              >
                Fire emoji size indicates fire intensity (FRP). Larger = higher FRP.
              </div>
            )}
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Region selector with total events count visible for all regions */}
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
            {Object.entries(REGION_PRESETS).map(([key, region]) => (
              <option key={key} value={key}>
                {region.name} ({regionCounts[key] ?? 0})
              </option>
            ))}
          </select>
          
          <select
            value={selectedYear ?? ''}
            onChange={(e) => setSelectedYear && setSelectedYear(Number(e.target.value))}
            disabled={loading || availableYears.length === 0}
            style={{
              padding: '4px 8px',
              fontSize: '0.85rem',
              borderRadius: '4px',
              border: '1px solid #ccc',
              backgroundColor: 'white',
              minWidth: '120px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {availableYears.length === 0 && <option value="">No years</option>}
            {availableYears.map((yr) => (
              <option key={yr} value={yr}>{yr} ({yearCounts[yr] ?? 0})</option>
            ))}
          </select>
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
      
      {fireHistory && yearFilteredEvents.length === 0 && (
        <div className="timeline-message">
          ✅ No fires found ({fireHistory.period_start} to {fireHistory.period_end})
        </div>
      )}
      
      {fireHistory && yearFilteredEvents.length > 0 && (
        <>
          <div className="timeline-scroll">
            <div className="timeline-track">
              {monthGroups.map((group, groupIndex) => (
                <div
                  key={`month-group-${group.key}`}
                  className={`timeline-month-group ${groupIndex === 0 ? 'timeline-month-group--first' : ''}`}
                  style={{ flex: group.events.length || 1 }}
                >
                  {group.events.map((event) => {
                    const isSelected = selectedFireEvent?.event_id === event.event_id;
                    const frp = event.fire_radiative_power;
                    const emoji = '🔥';
                    const emojiSize = getEmojiSize(frp);

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
                        <div className="timeline-event-emoji" style={{ fontSize: `${emojiSize}px` }}>{emoji}</div>
                        {isSelected && <div className="timeline-event-marker">📍</div>}
                      </div>
                    );
                  })}
                </div>
              ))}
              {hoverInfo && (
                <div className="timeline-tooltip" style={{ left: hoverInfo.left }}>
                  <div className="timeline-tooltip__row">📍 {hoverLocationLoading ? 'Loading...' : hoverLocation || 'Unknown location'}</div>
                  <div className="timeline-tooltip__row">📅 {formatDate(hoverInfo.event.date)}</div>
                  <div className="timeline-tooltip__row">🔥 FRP: {hoverInfo.event.fire_radiative_power.toFixed(1)} MW</div>
                  <div className="timeline-tooltip__row">✅ Confidence: {hoverInfo.event.confidence}%</div>
                </div>
              )}
            </div>
            {monthGroups.length > 0 && (
              <div className="timeline-months-overlay">
                {monthGroups.map((group, idx) => (
                  <div
                    key={`label-${group.key}`}
                    className={`timeline-months-segment ${idx === 0 ? 'timeline-months-segment--first' : ''}`}
                    style={{ flex: group.events.length || 1 }}
                  >
                    <div className="timeline-months-segment__label">{group.label}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {selectedFireEvent && (
            <div className="timeline-hint">
              💡 <strong>Fire marked on global context map</strong> - Hover for details
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default EventExplorer;
