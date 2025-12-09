import React, { useEffect, useState } from "react";
import TriView from "./components/TriView";
import WhatIfPanel from "./components/WhatIfPanel";
import ExplanationPanel from "./components/ExplanationPanel";
import QualityBoard from "./components/QualityBoard";
import EventExplorer from "./components/EventExplorer";
import WorldMap from "./components/WorldMap";
import FireHistoryHistogram from "./components/FireHistoryHistogram";
import { useTriViewState, TriViewState } from "./state/store";

const App: React.FC = () => {
  const [isLeftVisible, setIsLeftVisible] = useState(false);
  const initialize = useTriViewState((state: TriViewState) => state.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>Wildfire Risk Explorer</h1>
        <p>Synthetic tri-view for wildfire risk scenarios.</p>
      </header>
      <section className="app-timeline-section">
        <EventExplorer />
      </section>
      <main className={`app-main ${isLeftVisible ? "" : "app-main--left-hidden"}`}>
        <section className={`app-main__left ${isLeftVisible ? "" : "is-collapsed"}`}>
          <div className="left-toggle-container">
            <button
              className="toggle-btn"
              aria-pressed={isLeftVisible}
              aria-label={isLeftVisible ? "Hide What-if panel" : "Show What-if panel"}
              title={isLeftVisible ? "Hide What-if panel" : "Show What-if panel"}
              onClick={() => setIsLeftVisible((v) => !v)}
            >
              <span>What-if 🌡️</span>
              {isLeftVisible ? (
                // Chevron-left icon (collapse)
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              ) : (
                // Chevron-right icon (expand)
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              )}
            </button>
          </div>
          {isLeftVisible && (
            <>
              <WhatIfPanel />
              <ExplanationPanel />
              <FireHistoryHistogram />
              <QualityBoard />
            </>
          )}
        </section>
        <aside className="app-main__center">
          <TriView />
        </aside>
        <section className="app-main__right">
          <WorldMap />
        </section>
      </main>
    </div>
  );
};

export default App;
