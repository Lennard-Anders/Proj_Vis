import React from "react";
import type { FramesResponse } from "../../api/types";
import { useFrames } from "../../state/selectors";

const EventExplorer: React.FC = () => {
  const frames = useFrames();

  return (
    <div className="panel">
      <h2>Event Explorer</h2>
      {!frames && <p>No frames available.</p>}
      {frames && (
        <div className="event-explorer__strip">
          {frames.frames.map((frame: FramesResponse["frames"][number]) => (
            <div key={frame.frame_id} className="event-explorer__item">
              <img src={frame.url} alt={frame.frame_id} />
              <span>{frame.timestamp}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EventExplorer;
