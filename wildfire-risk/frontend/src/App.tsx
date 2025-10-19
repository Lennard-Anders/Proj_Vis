import React, { useEffect } from "react";
import TriView from "./components/TriView";
import WhatIfPanel from "./components/WhatIfPanel";
import ExplanationPanel from "./components/ExplanationPanel";
import QualityBoard from "./components/QualityBoard";
import EventExplorer from "./components/EventExplorer";
import { useTriViewState, TriViewState } from "./state/store";
import TimeScrubber from "./components/TimeScrubber";
import PromptBar from "./components/PromptBar";
import { FaCloudSun, FaBolt, FaWind, FaCloudRain } from "react-icons/fa";

const App: React.FC = () => {
  const initialize = useTriViewState((state: TriViewState) => state.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <div className="app-layout">
      {/* Sticky timeline bar */}
      <div className="timeline-bar">
        <div className="timeline-bar__inner">
          <TimeScrubber date={new Date().toISOString().slice(0, 10)} onChange={() => {}} />
        </div>
      </div>

      <div className="shell-grid">
        {/* Left icon dock */}
        <aside className="shell-dock">
          <button className="icon-btn" title="Weather"><FaCloudSun /></button>
          <button className="icon-btn" title="Thunder"><FaBolt /></button>
          <button className="icon-btn" title="Wind"><FaWind /></button>
          <button className="icon-btn" title="Rain"><FaCloudRain /></button>
        </aside>

        {/* Main content */}
        <main className="shell-main">
          <TriView />
        </main>

        {/* Right charts/controls */}
        <aside className="shell-aside">
          <WhatIfPanel />
          <ExplanationPanel />
          <QualityBoard />
          <EventExplorer />
        </aside>
      </div>

      {/* Footer prompt bar */}
      <footer className="prompt-footer">
        <PromptBar />
      </footer>
    </div>
  );
};

export default App;
