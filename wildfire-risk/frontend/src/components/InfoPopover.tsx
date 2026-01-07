import React, { useEffect, useRef, useState } from "react";

type Abbreviation = {
  term: string;
  meaning: string;
};

type InfoPopoverProps = {
  description: string;
  abbreviations?: Abbreviation[];
  title?: string;
  width?: number;
  align?: "left" | "right";
};

const InfoPopover: React.FC<InfoPopoverProps> = ({
  description,
  abbreviations = [],
  title = "About this panel",
  width = 320,
  align = "right",
}) => {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    function onDocClick(event: MouseEvent) {
      if (!open) return;
      const el = rootRef.current;
      if (!el) return;
      if (!el.contains(event.target as Node)) setOpen(false);
    }

    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  const panelStyle: React.CSSProperties = {
    width,
    ...(align === "left" ? { left: 0 } : { right: 0 }),
  };

  return (
    <div ref={rootRef} className="info-popover">
      <button
        type="button"
        className="info-popover__button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label="Panel info"
        title="Info"
      >
        <span className="info-popover__icon" aria-hidden="true">
          ℹ
        </span>
      </button>

      {open && (
        <div className="info-popover__panel" style={panelStyle}>
          {title && <div className="info-popover__title">{title}</div>}
          <p className="info-popover__desc">{description}</p>
          {abbreviations.length > 0 && (
            <>
              <div className="info-popover__subtitle">Abbreviations</div>
              <ul className="info-popover__list">
                {abbreviations.map((item) => (
                  <li key={item.term}>
                    <strong>{item.term}</strong> - {item.meaning}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default InfoPopover;
