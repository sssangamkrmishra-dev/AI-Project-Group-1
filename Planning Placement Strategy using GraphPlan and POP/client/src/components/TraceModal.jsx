// src/components/TraceModal.jsx
import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createPortal } from "react-dom";

// small helper button reused locally
function GlowButton({ children, onClick, variant = "primary", disabled, className = "" }) {
  const variants = {
    primary: "from-purple-600 to-blue-600",
    secondary: "from-slate-600 to-slate-700",
    gold: "from-amber-500 to-orange-500",
  };
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      disabled={disabled}
      className={`px-3 py-2 rounded-lg text-xs font-medium text-white bg-gradient-to-r ${variants[variant]} shadow ${className}`}
    >
      {children}
    </motion.button>
  );
}

// minimal icons used inside modal
const Icons = {
  X: () => (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  ),
  Sparkles: () => (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M5 3v4M3 5h4M6 17v4m-2-2h4M13 3l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  ),
  Play: () => (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    </svg>
  ),
  Pause: () => (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M6 4h4v16H6zM14 4h4v16h-4z" />
    </svg>
  ),
  Left: () => (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
    </svg>
  ),
  Right: () => (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  ),
};

// TraceModal: improved internal navigation, autoplay, copy-to-clipboard, keyboard support
export default function TraceModal({
  isOpen,
  onClose,
  title = "Trace",
  steps = [],
  startIndex = 0,
  autoplayIntervalMs = 1200,
}) {
  const overlayRef = useRef(null);
  const [index, setIndex] = useState(Number(startIndex) || 0);
  const [playing, setPlaying] = useState(false);
  const [copied, setCopied] = useState(false);
  const [speedMs, setSpeedMs] = useState(autoplayIntervalMs);

  // Sync index if parent updates startIndex or steps change
  useEffect(() => {
    setIndex(Math.min(Math.max(Number(startIndex) || 0, 0), Math.max(0, (steps?.length || 1) - 1)));
  }, [startIndex, steps]);

  // lock scroll when modal open
  useEffect(() => {
    if (isOpen) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = prev;
      };
    }
  }, [isOpen]);

  // autoplay timer
  useEffect(() => {
    if (!playing) return;
    if (!steps || steps.length === 0) {
      setPlaying(false);
      return;
    }
    const t = setInterval(() => {
      setIndex((i) => {
        const next = i + 1;
        if (next >= steps.length) {
          // stop or loop - we stop
          setPlaying(false);
          return i;
        }
        return next;
      });
    }, speedMs);
    return () => clearInterval(t);
  }, [playing, steps, speedMs]);

  // expose window events so parent or other UI can control modal (keeps compatibility)
  useEffect(() => {
    const onPrev = () => setIndex((i) => Math.max(0, i - 1));
    const onNext = () =>
      setIndex((i) => {
        if (!steps || steps.length === 0) return i;
        return Math.min(steps.length - 1, i + 1);
      });
    const onToggle = () => setPlaying((p) => !p);
    window.addEventListener("trace-prev", onPrev);
    window.addEventListener("trace-next", onNext);
    window.addEventListener("trace-toggle-play", onToggle);
    return () => {
      window.removeEventListener("trace-prev", onPrev);
      window.removeEventListener("trace-next", onNext);
      window.removeEventListener("trace-toggle-play", onToggle);
    };
  }, [steps]);

  // keyboard navigation while modal open
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e) => {
      if (e.key === "Escape") onClose?.();
      if (e.key === "ArrowLeft") setIndex((i) => Math.max(0, i - 1));
      if (e.key === "ArrowRight") setIndex((i) => (steps?.length ? Math.min(steps.length - 1, i + 1) : i));
      if (e.key === " ") {
        e.preventDefault();
        setPlaying((p) => !p);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, steps, onClose]);

  // copy current step JSON
  const copyCurrent = async () => {
    try {
      const txt = JSON.stringify(steps[index] ?? steps[0] ?? {}, null, 2);
      await navigator.clipboard.writeText(txt);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  };

  // if modal closed, reset playback
  useEffect(() => {
    if (!isOpen) {
      setPlaying(false);
      setCopied(false);
      setIndex(Number(startIndex) || 0);
    }
  }, [isOpen, startIndex]);

  if (!isOpen) return null;

  const total = steps?.length ?? 0;
  const step = steps && steps.length > 0 ? steps[index] : null;

  const modal = (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        ref={overlayRef}
        onClick={(e) => {
          if (e.target === overlayRef.current) onClose?.();
        }}
        className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      >
        <motion.div
          initial={{ y: 20, scale: 0.98, opacity: 0 }}
          animate={{ y: 0, scale: 1, opacity: 1 }}
          exit={{ y: 20, scale: 0.98, opacity: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-5xl bg-slate-900/95 border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
        >
          <div className="flex items-center justify-between p-4 border-b border-white/6">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-md bg-gradient-to-br from-purple-500 to-blue-500">
                <Icons.Sparkles />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">{title}</h3>
                <p className="text-xs text-slate-400">Step viewer — keyboard: ← → , Space = play/pause, Esc = close</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={onClose}
                className="p-2 rounded-md hover:bg-white/5 text-slate-300"
                aria-label="Close"
              >
                <Icons.X />
              </button>
            </div>
          </div>

          <div className="p-6">
            <div className="mb-4">
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm text-slate-400">Showing {total} step{total !== 1 ? "s" : ""}</div>
                <div className="text-xs text-slate-400">Click JSON to copy — <span className="text-white">{copied ? "Copied!" : "Copy"}</span></div>
              </div>

              <div
                onClick={copyCurrent}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === "Enter") copyCurrent(); }}
                className="rounded-lg bg-slate-800/40 p-4 border border-white/5 min-h-[160px] max-h-[48vh] overflow-auto cursor-pointer"
                title="Click to copy this step JSON"
              >
                {step ? (
                  <pre className="text-xs text-slate-200 whitespace-pre-wrap">{JSON.stringify(step, null, 2)}</pre>
                ) : (
                  <div className="text-sm text-slate-400">No trace available.</div>
                )}
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <GlowButton variant="secondary" onClick={() => setIndex((i) => Math.max(0, i - 1))}>
                  <Icons.Left /> Prev
                </GlowButton>

                <GlowButton
                  variant="primary"
                  onClick={() => {
                    if (total === 0) return;
                    // toggle playing
                    setPlaying((p) => !p);
                  }}
                >
                  {playing ? (<><Icons.Pause /> Pause</>) : (<><Icons.Play /> Play</>)}
                </GlowButton>

                <GlowButton variant="secondary" onClick={() => setIndex((i) => Math.min(Math.max(0, total - 1), i + 1))}>
                  Next <Icons.Right />
                </GlowButton>

                <div className="flex items-center gap-2 ml-3 text-xs text-slate-400">
                  <span>Speed</span>
                  <input
                    aria-label="Autoplay speed (ms)"
                    value={speedMs}
                    onChange={(e) => {
                      const v = Number(e.target.value) || 300;
                      setSpeedMs(Math.max(100, Math.min(5000, v)));
                    }}
                    className="w-24 bg-slate-800/40 p-1 rounded text-xs text-white"
                    type="number"
                  />
                  <span className="text-xs text-slate-400">ms</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="text-xs text-slate-400">Step</div>
                <div className="text-sm font-medium text-white">{index + 1} / {total}</div>
              </div>
            </div>

            {/* Step thumbnails / quick nav */}
            <div className="mt-4">
              <div className="flex items-center gap-2 overflow-x-auto py-2">
                {(steps || []).map((s, i) => (
                  <button
                    key={i}
                    onClick={() => setIndex(i)}
                    className={`min-w-[90px] p-2 rounded-md text-xs text-left border ${
                      i === index ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white border-transparent shadow-lg" : "bg-slate-800/30 text-slate-300 border-white/6"
                    }`}
                  >
                    <div className="truncate font-medium">{(s?.name) || `step ${i + 1}`}</div>
                    <div className="text-[11px] text-slate-400 truncate">{Array.isArray(s?.actions) ? `${s.actions.length} actions` : s?.summary || ""}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="p-3 border-t border-white/6 text-xs text-slate-500">
            Trace viewer — rendered in a portal (attached to document.body) with high z-index.
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );

  return createPortal(modal, document.body);
}
