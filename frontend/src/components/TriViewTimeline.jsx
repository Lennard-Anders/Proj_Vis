import React, { useState, useEffect } from 'react';
import './TriViewTimeline.css';

function TriViewTimeline({ frames, onFrameSelect, currentFrame }) {
  const [selectedView, setSelectedView] = useState('risk');
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (isPlaying && frames && frames.length > 0) {
      const interval = setInterval(() => {
        const nextIndex = (currentFrame + 1) % frames.length;
        onFrameSelect(nextIndex);
      }, 1000 / playbackSpeed);

      return () => clearInterval(interval);
    }
  }, [isPlaying, currentFrame, frames, playbackSpeed, onFrameSelect]);

  const handleViewChange = (view) => {
    setSelectedView(view);
  };

  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="tri-view-timeline">
      <div className="view-selector">
        <button
          className={selectedView === 'risk' ? 'active' : ''}
          onClick={() => handleViewChange('risk')}
        >
          Risk Score
        </button>
        <button
          className={selectedView === 'spread' ? 'active' : ''}
          onClick={() => handleViewChange('spread')}
        >
          Spread Pattern
        </button>
        <button
          className={selectedView === 'intensity' ? 'active' : ''}
          onClick={() => handleViewChange('intensity')}
        >
          Fire Intensity
        </button>
      </div>

      <div className="timeline-controls">
        <button onClick={togglePlayback}>
          {isPlaying ? '⏸ Pause' : '▶ Play'}
        </button>
        <input
          type="range"
          min="0"
          max={frames ? frames.length - 1 : 0}
          value={currentFrame}
          onChange={(e) => onFrameSelect(parseInt(e.target.value))}
          className="timeline-slider"
        />
        <span className="frame-counter">
          Frame {currentFrame + 1} / {frames ? frames.length : 0}
        </span>
        <select
          value={playbackSpeed}
          onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
          className="speed-selector"
        >
          <option value="0.25">0.25x</option>
          <option value="0.5">0.5x</option>
          <option value="1">1x</option>
          <option value="2">2x</option>
          <option value="4">4x</option>
        </select>
      </div>

      {frames && frames[currentFrame] && (
        <div className="frame-info">
          <div className="info-item">
            <span className="label">Timestamp:</span>
            <span className="value">{frames[currentFrame].timestamp}</span>
          </div>
          <div className="info-item">
            <span className="label">Spread Intensity:</span>
            <span className="value">{frames[currentFrame].spread_intensity?.toFixed(2)}</span>
          </div>
          <div className="info-item">
            <span className="label">Affected Area:</span>
            <span className="value">{frames[currentFrame].affected_area_km2?.toFixed(1)} km²</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default TriViewTimeline;
