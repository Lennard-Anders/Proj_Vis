import React, { useEffect } from "react";
import TriView from "./components/TriView";
import WhatIfPanel from "./components/WhatIfPanel";
import ExplanationPanel from "./components/ExplanationPanel";
import QualityBoard from "./components/QualityBoard";
import EventExplorer from "./components/EventExplorer";
import WorldMap from "./components/WorldMap";
import { useTriViewState, TriViewState } from "./state/store";

const App: React.FC = () => {
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
      <main className="app-main">
        <section className="app-main__left">
          <TriView />
        </section>
        <aside className="app-main__center">
          <WhatIfPanel />
        </aside>
        <section className="app-main__right">
          <WorldMap />
          <ExplanationPanel />
          <QualityBoard />
          <EventExplorer />
        </section>
      </main>
    </div>
  );
};

export default App;
