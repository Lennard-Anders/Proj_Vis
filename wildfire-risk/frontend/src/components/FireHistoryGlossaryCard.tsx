import React, { useEffect, useRef, useState } from "react";

export default function FireHistoryGlossaryCard() {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  // Close when clicking outside
  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!open) return;
      const el = rootRef.current;
      if (!el) return;
      if (!el.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  return (
    <div ref={rootRef} style={{ position: "relative", display: "inline-block" }}>
      <button
  type="button"
  onClick={() => setOpen((v) => !v)}
  aria-expanded={open}
  title="Info"
  style={{
    width: 28,
    height: 28,
    borderRadius: 999,
    border: "1px solid rgba(255,0,0,0.5)",
    background: "white",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    cursor: "pointer",
    fontWeight: 800,
    lineHeight: 1,
    userSelect: "none",
  }}
>
  <span
    style={{
      color: "red",
      fontSize: "14px",
      fontWeight: 900,
      lineHeight: "1",
    }}
  >
    ℹ
  </span>
</button>


      {open && (
        <div
          style={{
            position: "absolute",
            right: 0,
            top: 34,
            width: 320,
            border: "1px solid rgba(0,0,0,0.12)",
            borderRadius: 10,
            padding: "10px 12px",
            background: "white",
            boxShadow: "0 12px 24px -12px rgba(0,0,0,0.25)",
            zIndex: 999,
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Abbreviations</div>
          <ul style={{ margin: 0, paddingLeft: 18, lineHeight: 1.45, fontSize: "0.95rem" }}>
            <li><strong>MW</strong> – Mean wind speed (average wind speed).</li>
            <li><strong>RH</strong> – Relative humidity (moisture in the air).</li>
            <li><strong>Temp</strong> – Air temperature (°C).</li>
            <li><strong>Precip</strong> – Precipitation (rain/snow amount).</li>
            <li><strong>NDVI</strong> – Vegetation index (vegetation density/dryness).</li>
            <li><strong>FRP</strong> – Fire Radiative Power (fire intensity proxy).</li>
            <li><strong>Confidence</strong> – Detection confidence (%).</li>
          </ul>
        </div>
      )}
    </div>
  );
}

