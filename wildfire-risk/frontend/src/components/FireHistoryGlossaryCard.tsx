import React from "react";
import InfoPopover from "./InfoPopover";

const FIRE_HISTORY_INFO = {
  description:
    "Overview of historical wildfire activity. Includes the global context map and the monthly distribution for the selected region.",
  abbreviations: [
    { term: "MW", meaning: "Mean wind speed (average wind speed)." },
    { term: "RH", meaning: "Relative humidity (moisture in the air)." },
    { term: "Temp", meaning: "Air temperature (°C)." },
    { term: "Precip", meaning: "Precipitation (rain/snow amount)." },
    { term: "NDVI", meaning: "Vegetation index (vegetation density/dryness)." },
    { term: "FRP", meaning: "Fire Radiative Power (fire intensity proxy)." },
    { term: "Confidence", meaning: "Detection confidence (%)." },
  ],
};

export default function FireHistoryGlossaryCard() {
  return (
    <InfoPopover
      description={FIRE_HISTORY_INFO.description}
      abbreviations={FIRE_HISTORY_INFO.abbreviations}
    />
  );
}
