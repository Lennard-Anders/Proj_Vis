import React, { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

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
  const [panelStyle, setPanelStyle] = useState<React.CSSProperties | null>(null);
  const rootRef = useRef<HTMLDivElement | null>(null);
  const panelRef = useRef<HTMLDivElement | null>(null);
  const closeTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    function onDocClick(event: MouseEvent) {
      if (!open) return;
      const el = rootRef.current;
      const panel = panelRef.current;
      const target = event.target as Node;
    if (el?.contains(target)) return;
    if (panel?.contains(target)) return;
    setOpen(false);
  }

    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  useEffect(() => {
    return () => {
      if (closeTimeoutRef.current !== null) {
        window.clearTimeout(closeTimeoutRef.current);
      }
    };
  }, []);

  const updatePanelPosition = useCallback(() => {
    if (!open || typeof window === "undefined") return;
    const root = rootRef.current;
    if (!root) return;

    const margin = 12;
    const rect = root.getBoundingClientRect();
    const safeWidth = Math.max(0, Math.min(width, window.innerWidth - margin * 2));
    let left = align === "left" ? rect.left : rect.right - safeWidth;

    if (left < margin) left = margin;
    if (left + safeWidth > window.innerWidth - margin) {
      left = Math.max(margin, window.innerWidth - margin - safeWidth);
    }

    const top = rect.bottom + 10;

    setPanelStyle({
      width: safeWidth,
      top,
      left,
      position: "fixed",
      zIndex: 2000,
    });
  }, [open, width, align]);

  useLayoutEffect(() => {
    if (!open) {
      setPanelStyle(null);
      return;
    }
    updatePanelPosition();
  }, [open, updatePanelPosition]);

  useEffect(() => {
    if (!open) return;
    const handle = () => updatePanelPosition();
    window.addEventListener("resize", handle);
    window.addEventListener("scroll", handle, true);
    return () => {
      window.removeEventListener("resize", handle);
      window.removeEventListener("scroll", handle, true);
    };
  }, [open, updatePanelPosition]);

  const clearCloseTimeout = () => {
    if (closeTimeoutRef.current !== null) {
      window.clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
    }
  };

  const scheduleClose = () => {
    clearCloseTimeout();
    closeTimeoutRef.current = window.setTimeout(() => {
      setOpen(false);
    }, 120);
  };

  const handleOpen = () => {
    clearCloseTimeout();
    setOpen(true);
  };

  return (
    <div ref={rootRef} className="info-popover">
      <button
        type="button"
        className="info-popover__button"
        onClick={() => setOpen((v) => !v)}
        onMouseEnter={handleOpen}
        onMouseLeave={scheduleClose}
        onFocus={handleOpen}
        onBlur={scheduleClose}
        aria-expanded={open}
        aria-label="Panel info"
        title="Info"
      >
        <span className="info-popover__icon" aria-hidden="true">
          ℹ
        </span>
      </button>

      {open && panelStyle && typeof document !== "undefined" &&
        createPortal(
          <div
            ref={panelRef}
            className="info-popover__panel"
            style={panelStyle}
            onMouseEnter={handleOpen}
            onMouseLeave={scheduleClose}
          >
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
          </div>,
          document.body
        )}
    </div>
  );
};

export default InfoPopover;
