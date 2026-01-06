import React, { useEffect, useState } from "react";
import { useFireHistory, useSelectFireEvent, useSelectedRegion, useSelectedYear } from "../state/selectors";
import type { FireEvent } from "../api/types";
import { REGION_PRESETS } from "../utils/regions";

interface HistogramData {
  label: string;
  count: number;
  color: string;
  events: FireEvent[];
}

const FireHistoryHistogram: React.FC = () => {
  const fireHistory = useFireHistory();
  const selectFireEvent = useSelectFireEvent();
  const selectedRegion = useSelectedRegion() || 'california';
  const selectedYear = useSelectedYear();
  const [histogramData, setHistogramData] = useState<HistogramData[]>([]);
  const [selectedBar, setSelectedBar] = useState<HistogramData | null>(null);

  useEffect(() => {
    if (!fireHistory?.events || fireHistory.events.length === 0) {
      return;
    }

    // Group fires by month with details, using a numeric key so we can sort chronologically
    const monthGroups: Map<number, FireEvent[]> = new Map();
    fireHistory.events.forEach(event => {
      const date = new Date(event.date);
      const monthStartUtc = Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1);
      const existing = monthGroups.get(monthStartUtc);
      if (existing) {
        existing.push(event);
      } else {
        monthGroups.set(monthStartUtc, [event]);
      }
    });

    // Convert to histogram data and sort by the month key
    const data: HistogramData[] = Array.from(monthGroups.entries())
      .map(([monthStartUtc, events]) => {
        const label = new Date(monthStartUtc).toLocaleString('default', { month: 'short', year: 'numeric' });
        return {
          label,
          count: events.length,
          color: events.length > 5 ? '#ef4444' : events.length > 2 ? '#f59e0b' : '#10b981',
          events,
          sortKey: monthStartUtc
        };
      })
      .sort((a, b) => a.sortKey - b.sortKey)
      .map(({ sortKey, ...rest }) => rest);

    setHistogramData(data);
  }, [fireHistory]);

  const getDateRange = () => {
    const endDate = new Date();
    const startDate = new Date(endDate.getFullYear() - 5, endDate.getMonth(), endDate.getDate());
    // Prefer the period returned by the API for the currently loaded dataset, otherwise use the last 5 years.
    const start = fireHistory?.period_start || startDate.toISOString().split('T')[0];
    const end = fireHistory?.period_end || endDate.toISOString().split('T')[0];
    return { start, end };
  };

  const maxCount = histogramData.length ? Math.max(...histogramData.map(d => d.count)) : 0;

  const yearDisplay = (() => {
    if (selectedYear !== undefined && selectedYear !== null) return selectedYear;
    if (!histogramData.length) return '—';
    const years = Array.from(new Set(histogramData.flatMap(d => d.events.map(e => new Date(e.date).getFullYear()))));
    if (years.length === 1) return years[0];
    const minY = Math.min(...years);
    const maxY = Math.max(...years);
    return `${minY} - ${maxY}`;
  })();

  // When region changes (via timeline), clear selection to avoid mismatch with new dataset.
  useEffect(() => {
    setSelectedBar(null);
  }, [selectedRegion]);

  const handleBarClick = (item: HistogramData) => {
    setSelectedBar(selectedBar?.label === item.label ? null : item);
  };

  const handleEventClick = (event: FireEvent) => {
    selectFireEvent(event);
  };

  let bodyContent: React.ReactNode;
  if (!fireHistory || !histogramData.length) {
    bodyContent = (
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
        No fire history data available
      </p>
    );
  } else {
    bodyContent = (
      <>
        <div style={{
          fontSize: '0.85rem',
          color: 'var(--text-secondary)',
          marginBottom: 'var(--spacing-md)'
        }}>
          Total Events: <strong>{fireHistory.events.length}</strong>
        </div>
        
        {/* Histogram */}
        <div style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: '8px',
          height: '200px',
          padding: '0 var(--spacing-sm)',
          borderBottom: '2px solid var(--border-color)',
          marginBottom: 'var(--spacing-sm)'
        }}>
          {histogramData.map((item, idx) => (
            <div
              key={idx}
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <div style={{
                fontSize: '0.75rem',
                fontWeight: '600',
                color: 'var(--text-primary)'
              }}>
                {item.count}
              </div>
              <div
                style={{
                  width: '100%',
                  height: `${(item.count / maxCount) * 160}px`,
                  background: selectedBar?.label === item.label 
                    ? `linear-gradient(180deg, #3b82f6dd, #3b82f6)` 
                    : `linear-gradient(180deg, ${item.color}dd, ${item.color})`,
                  borderRadius: '4px 4px 0 0',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  position: 'relative',
                  border: selectedBar?.label === item.label ? '2px solid #3b82f6' : 'none'
                }}
                onClick={() => handleBarClick(item)}
                title={(() => {
                  const avgFRP = item.events.reduce((sum, e) => sum + e.fire_radiative_power, 0) / item.events.length;
                  const avgArea = item.events.reduce((sum, e) => sum + (e.area_km2 || 0), 0) / item.events.length;
                  const avgConf = item.events.reduce((sum, e) => sum + e.confidence, 0) / item.events.length;
                  const avgTemp = item.events.reduce((sum, e) => sum + e.brightness_temp, 0) / item.events.length;
                  return `${item.label}\n━━━━━━━━━━━━━━━\n🔥 ${item.count} Fire Event${item.count > 1 ? 's' : ''}\n\n📊 Averages:\n   FRP: ${avgFRP.toFixed(0)} MW\n   Area: ${avgArea.toFixed(1)} km²\n   Confidence: ${avgConf.toFixed(0)}%\n   Temp: ${avgTemp.toFixed(0)}K\n\nClick to see event list`;
                })()}
              >
                <div style={{
                  position: 'absolute',
                  bottom: '-20px',
                  left: '50%',
                  transform: 'translateX(-50%) rotate(-45deg)',
                  fontSize: '0.65rem',
                  color: 'var(--text-secondary)',
                  whiteSpace: 'nowrap',
                  transformOrigin: 'top left'
                }}>
                  {item.label}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Legend */}
        <div style={{
          display: 'flex',
          gap: 'var(--spacing-md)',
          justifyContent: 'center',
          marginTop: 'var(--spacing-lg)',
          fontSize: '0.75rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', background: '#10b981', borderRadius: '2px' }} />
            <span>Low (≤2)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', background: '#f59e0b', borderRadius: '2px' }} />
            <span>Medium (3-5)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', background: '#ef4444', borderRadius: '2px' }} />
            <span>High (&gt;5)</span>
          </div>
        </div>

        {/* Statistics */}
        <div style={{
          marginTop: 'var(--spacing-md)',
          padding: 'var(--spacing-md)',
          background: 'rgba(59, 130, 246, 0.05)',
          borderRadius: '6px',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 'var(--spacing-sm)',
          fontSize: '0.85rem'
        }}>
          <div>
            <div style={{ color: 'var(--text-secondary)' }}>Avg FRP</div>
            <strong>{(fireHistory.events.reduce((sum, e) => sum + e.fire_radiative_power, 0) / fireHistory.events.length).toFixed(0)} MW</strong>
          </div>
          <div>
            <div style={{ color: 'var(--text-secondary)' }}>Avg Area</div>
            <strong>{(fireHistory.events.reduce((sum, e) => sum + e.area_km2, 0) / fireHistory.events.length).toFixed(1)} km²</strong>
          </div>
          <div>
            <div style={{ color: 'var(--text-secondary)' }}>Avg Confidence</div>
            <strong>{(fireHistory.events.reduce((sum, e) => sum + e.confidence, 0) / fireHistory.events.length).toFixed(0)}%</strong>
          </div>
          <div>
            <div style={{ color: 'var(--text-secondary)' }}>Date Range</div>
            <strong>
              {new Date(Math.min(...fireHistory.events.map(e => new Date(e.date).getTime()))).toLocaleDateString('default', { month: 'short', year: 'numeric' })} - {new Date(Math.max(...fireHistory.events.map(e => new Date(e.date).getTime()))).toLocaleDateString('default', { month: 'short', year: 'numeric' })}
            </strong>
          </div>
        </div>

        {/* Event Details Panel */}
        {selectedBar && (
          <div style={{
            marginTop: 'var(--spacing-md)',
            padding: 'var(--spacing-md)',
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%)',
            borderRadius: '8px',
            border: '2px solid #3b82f6',
            maxHeight: '300px',
            overflowY: 'auto'
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: 'var(--spacing-sm)'
            }}>
              <h4 style={{ margin: 0, fontSize: '0.95rem' }}>
                🔥 {selectedBar.label} Events ({selectedBar.count})
              </h4>
              <button
                onClick={() => setSelectedBar(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.2rem',
                  cursor: 'pointer',
                  color: 'var(--text-secondary)',
                  padding: '4px 8px'
                }}
              >
                ✕
              </button>
            </div>
            <div style={{ fontSize: '0.85rem' }}>
              {selectedBar.events.map((event, idx) => (
                <div
                  key={event.event_id}
                  onClick={() => handleEventClick(event)}
                  style={{
                    padding: 'var(--spacing-sm)',
                    marginBottom: '6px',
                    background: 'rgba(255, 255, 255, 0.5)',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    border: '1px solid transparent'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                    e.currentTarget.style.borderColor = '#3b82f6';
                    e.currentTarget.style.transform = 'translateX(4px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.5)';
                    e.currentTarget.style.borderColor = 'transparent';
                    e.currentTarget.style.transform = 'translateX(0)';
                  }}
                >
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between',
                    marginBottom: '4px',
                    fontWeight: '600'
                  }}>
                    <span>📅 {new Date(event.date).toLocaleDateString()}</span>
                    <span style={{ color: event.confidence > 80 ? '#10b981' : '#f59e0b' }}>
                      {event.confidence}%
                    </span>
                  </div>
                  <div style={{ 
                    fontSize: '0.75rem', 
                    color: 'var(--text-secondary)',
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '4px'
                  }}>
                    <div>📍 {event.latitude.toFixed(2)}°, {event.longitude.toFixed(2)}°</div>
                    <div>🔥 {event.fire_radiative_power.toFixed(0)} MW</div>
                    <div>📐 {event.area_km2?.toFixed(1) || 'N/A'} km²</div>
                    <div>🌡️ {event.brightness_temp.toFixed(0)}K</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </>
    );
  }

  return (
    <div className="panel">
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: 'var(--spacing-sm)',
        marginBottom: 'var(--spacing-sm)'
      }}>
        <h3 style={{ margin: 0 }}>📊 Fire History Distribution</h3>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '4px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Region:</span>
            <span>{REGION_PRESETS[selectedRegion]?.name || selectedRegion}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Year:</span>
            <span>{yearDisplay}</span>
          </div>
        </div>
      </div>
      {bodyContent}
    </div>
  );
};

export default FireHistoryHistogram;
