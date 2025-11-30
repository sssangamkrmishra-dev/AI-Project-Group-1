

import React, { useState, useEffect, useMemo, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    callGraphPlan,
    callPopPlan,
    callRepair,
    callSimulate,
    getDatasetsInfo,
    callGraphPlanTrace,
    callPopTrace
} from "../services/API";
import TraceModal from "./TraceModal";

// Icons as SVG components
const Icons = {
    Brain: () => (
        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
    ),
    Rocket: () => (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
    ),
    Calendar: () => (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
    ),
    Check: () => (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
    ),
    X: () => (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
    ),
    Play: () => (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    ),
    Clock: () => (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    ),
    Target: () => (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
    ),
    Sparkles: () => (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
    ),
    Info: () => (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    ),
    GitHub: () => (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
        </svg>
    ),
    Refresh: () => (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
    ),
};

function parseListInput(s) {
    if (!s) return [];
    return s.split(",").map((x) => x.trim()).filter(Boolean);
}

// Particle background component
function ParticleBackground() {
    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
            {[...Array(50)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute w-1 h-1 bg-purple-500/20 rounded-full"
                    initial={{
                        x: Math.random() * window.innerWidth,
                        y: Math.random() * window.innerHeight,
                    }}
                    animate={{
                        x: Math.random() * window.innerWidth,
                        y: Math.random() * window.innerHeight,
                    }}
                    transition={{
                        duration: Math.random() * 20 + 10,
                        repeat: Infinity,
                        repeatType: "reverse",
                    }}
                />
            ))}
        </div>
    );
}

// Animated gradient orbs
function GradientOrbs() {
    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
            <motion.div
                className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/30 rounded-full blur-3xl"
                animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.3, 0.5, 0.3],
                }}
                transition={{ duration: 8, repeat: Infinity }}
            />
            <motion.div
                className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/30 rounded-full blur-3xl"
                animate={{
                    scale: [1.2, 1, 1.2],
                    opacity: [0.5, 0.3, 0.5],
                }}
                transition={{ duration: 8, repeat: Infinity }}
            />
            <motion.div
                className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl"
                animate={{
                    scale: [1, 1.3, 1],
                    rotate: [0, 180, 360],
                }}
                transition={{ duration: 20, repeat: Infinity }}
            />
        </div>
    );
}

// Glowing button component
function GlowButton({ children, onClick, variant = "primary", disabled, className = "", icon }) {
    const variants = {
        primary: "from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 shadow-purple-500/25",
        success: "from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-500/25",
        danger: "from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 shadow-rose-500/25",
        secondary: "from-slate-600 to-slate-700 hover:from-slate-500 hover:to-slate-600 shadow-slate-500/25",
        gold: "from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 shadow-amber-500/25",
    };

    return (
        <motion.button
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={onClick}
            disabled={disabled}
            className={`
        relative px-4 py-2.5 rounded-xl font-medium text-white
        bg-gradient-to-r ${variants[variant]}
        shadow-lg transition-all duration-300
        disabled:opacity-50 disabled:cursor-not-allowed
        flex items-center justify-center gap-2
        ${className}
      `}
        >
            {icon && <span>{icon}</span>}
            {children}
            <motion.div
                className="absolute inset-0 rounded-xl bg-white/20"
                initial={{ opacity: 0 }}
                whileHover={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
            />
        </motion.button>
    );
}

// Card component with glass effect
function GlassCard({ children, className = "", delay = 0 }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay }}
            className={`
        relative backdrop-blur-xl bg-white/5 border border-white/10
        rounded-2xl shadow-2xl overflow-hidden
        ${className}
      `}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
            <div className="relative z-10">{children}</div>
        </motion.div>
    );
}

// Tag/Badge component
function Tag({ children, color = "purple" }) {
    const colors = {
        purple: "bg-purple-500/20 text-purple-300 border-purple-500/30",
        blue: "bg-blue-500/20 text-blue-300 border-blue-500/30",
        emerald: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
        amber: "bg-amber-500/20 text-amber-300 border-amber-500/30",
        rose: "bg-rose-500/20 text-rose-300 border-rose-500/30",
    };

    return (
        <span className={`px-2 py-0.5 text-xs rounded-full border ${colors[color]}`}>
            {children}
        </span>
    );
}

// Timeline Gantt Component
function Gantt({ schedule }) {
    const { min, max, items } = useMemo(() => {
        if (!Array.isArray(schedule)) return { min: 0, max: 0, items: [] };
        let min = Infinity;
        let max = -Infinity;
        const items = schedule.map((it, idx) => {
            const est = Number(it.est) || 0;
            const dur = Number(it.duration) || 1;
            min = Math.min(min, est);
            max = Math.max(max, est + dur);
            return { ...it, _idx: idx, est, dur };
        });
        if (!isFinite(min)) min = 0;
        if (!isFinite(max)) max = 0;
        return { min, max, items };
    }, [schedule]);

    const span = Math.max(1, Math.ceil(max - min));
    const weeks = Array.from({ length: span }, (_, i) => i + min);

    const colors = [
        "from-purple-500 to-indigo-500",
        "from-emerald-500 to-teal-500",
        "from-amber-500 to-orange-500",
        "from-rose-500 to-pink-500",
        "from-blue-500 to-cyan-500",
    ];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6"
        >
            <div className="flex items-center gap-2 mb-4">
                <Icons.Calendar />
                <h4 className="text-lg font-semibold text-white">Timeline View</h4>
            </div>

            <div className="overflow-x-auto rounded-xl bg-slate-900/50 p-4 border border-white/5">
                {/* Header */}
                <div className="flex mb-4">
                    <div className="w-48 flex-shrink-0 text-sm text-slate-400 font-medium">Action</div>
                    <div className="flex-1 flex">
                        {weeks.map((w) => (
                            <div
                                key={w}
                                className="flex-1 text-center text-xs text-slate-500 border-l border-slate-700/50 py-1"
                            >
                                Week {w}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Rows */}
                {items.map((it, idx) => (
                    <motion.div
                        key={it._idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="flex items-center mb-3"
                    >
                        <div className="w-48 flex-shrink-0 pr-4">
                            <span className="text-sm font-medium text-white truncate block">{it.name}</span>
                            <span className="text-xs text-slate-400">{it.effort_hours}h effort</span>
                        </div>
                        <div className="flex-1 relative h-10">
                            {/* Grid lines */}
                            <div className="absolute inset-0 flex">
                                {weeks.map((w) => (
                                    <div key={w} className="flex-1 border-l border-slate-700/30" />
                                ))}
                            </div>
                            {/* Bar */}
                            <motion.div
                                initial={{ scaleX: 0 }}
                                animate={{ scaleX: 1 }}
                                transition={{ delay: idx * 0.1 + 0.2, duration: 0.5 }}
                                style={{
                                    left: `${((it.est - min) / span) * 100}%`,
                                    width: `${(it.dur / span) * 100}%`,
                                    originX: 0,
                                }}
                                className={`absolute top-1 bottom-1 rounded-lg bg-gradient-to-r ${colors[idx % colors.length]} shadow-lg`}
                            >
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <span className="text-xs font-semibold text-white drop-shadow-md px-2 truncate">
                                        {it.dur}w
                                    </span>
                                </div>
                            </motion.div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
}

// Action Card Component
function ActionCard({ action, index, onMark, onDetails, type = "schedule" }) {
    const [isHovered, setIsHovered] = useState(false);

    const gradients = [
        "from-purple-500/20 to-indigo-500/20 border-purple-500/30",
        "from-emerald-500/20 to-teal-500/20 border-emerald-500/30",
        "from-amber-500/20 to-orange-500/20 border-amber-500/30",
        "from-rose-500/20 to-pink-500/20 border-rose-500/30",
        "from-blue-500/20 to-cyan-500/20 border-blue-500/30",
    ];

    return (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => setIsHovered(false)}
            className={`
        relative p-4 rounded-xl border backdrop-blur-sm
        bg-gradient-to-br ${gradients[index % gradients.length]}
        transition-all duration-300
        ${isHovered ? "scale-[1.02] shadow-xl" : ""}
      `}
        >
            {/* Index badge */}
            <div className="absolute -top-2 -left-2 w-6 h-6 rounded-full bg-white/10 border border-white/20 flex items-center justify-center">
                <span className="text-xs font-bold text-white">{index + 1}</span>
            </div>

            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <h5 className="font-semibold text-white mb-2">{action.name}</h5>

                    <div className="flex flex-wrap gap-2 mb-3">
                        {type === "schedule" && (
                            <>
                                <Tag color="blue">Week {action.est}</Tag>
                                <Tag color="purple">{action.duration}w duration</Tag>
                            </>
                        )}
                        <Tag color="amber">{action.effort_hours || action.effort_hours}h effort</Tag>
                    </div>

                    {/* Preconditions */}
                    {action.preconds && action.preconds.length > 0 && (
                        <div className="mb-2">
                            <span className="text-xs text-slate-400">Requires: </span>
                            <span className="text-xs text-slate-300">{action.preconds.join(", ")}</span>
                        </div>
                    )}

                    {/* Effects */}
                    {action.adds && action.adds.length > 0 && (
                        <div>
                            <span className="text-xs text-slate-400">Adds: </span>
                            <span className="text-xs text-emerald-400">{action.adds.join(", ")}</span>
                        </div>
                    )}
                </div>

                {/* Action buttons */}
                <AnimatePresence>
                    {isHovered && type === "schedule" && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.8 }}
                            className="flex flex-col gap-2 ml-3"
                        >
                            <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                onClick={() => onMark(action.name)}
                                className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                            >
                                <Icons.Check />
                            </motion.button>
                            <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                onClick={() => onDetails(action)}
                                className="p-2 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30"
                            >
                                <Icons.Info />
                            </motion.button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
}

// Modal Component
function Modal({ isOpen, onClose, title, children }) {
    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        onClick={(e) => e.stopPropagation()}
                        className="w-full max-w-lg bg-slate-900/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden"
                    >
                        <div className="flex items-center justify-between p-4 border-b border-white/10">
                            <h3 className="text-lg font-semibold text-white">{title}</h3>
                            <button
                                onClick={onClose}
                                className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                            >
                                <Icons.X />
                            </button>
                        </div>
                        <div className="p-4">{children}</div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

// Stats Card
function StatsCard({ icon, label, value, color = "purple" }) {
    const colors = {
        purple: "from-purple-500 to-indigo-500",
        emerald: "from-emerald-500 to-teal-500",
        amber: "from-amber-500 to-orange-500",
        blue: "from-blue-500 to-cyan-500",
    };

    return (
        <motion.div
            whileHover={{ scale: 1.05, y: -5 }}
            className="relative p-4 rounded-xl bg-white/5 border border-white/10 overflow-hidden"
        >
            <div className={`absolute inset-0 bg-gradient-to-br ${colors[color]} opacity-10`} />
            <div className="relative">
                <div className="flex items-center gap-2 mb-2">
                    <span className={`text-transparent bg-clip-text bg-gradient-to-r ${colors[color]}`}>
                        {icon}
                    </span>
                    <span className="text-xs text-slate-400 uppercase tracking-wider">{label}</span>
                </div>
                <div className="text-2xl font-bold text-white">{value}</div>
            </div>
        </motion.div>
    );
}

// Main Component
export default function PlacementPlannerUI() {
    const [initStateText, setInitStateText] = useState("DSA_LOW, ML_LOW, RESUME_LOW, NOT_BURNOUT");
    const [goalsText, setGoalsText] = useState("DSA_HIGH, RESUME_HIGH, CONF_HIGH");
    const [schedule, setSchedule] = useState(null);
    const [graphPlan, setGraphPlan] = useState(null);
    const [loading, setLoading] = useState(false);
    const [datasetsInfo, setDatasetsInfo] = useState(null);
    const [error, setError] = useState(null);
    const [executedActions, setExecutedActions] = useState([]);
    const [selectedActionToMark, setSelectedActionToMark] = useState(null);
    const [repairLoading, setRepairLoading] = useState(false);
    const [maxParallel, setMaxParallel] = useState(1);
    const [activeTab, setActiveTab] = useState("graphplan");
    const [showDetailsModal, setShowDetailsModal] = useState(false);
    const [selectedAction, setSelectedAction] = useState(null);
    const [showSimulateModal, setShowSimulateModal] = useState(false);
    const [traceSteps, setTraceSteps] = useState([]);
    const [showTraceModal, setShowTraceModal] = useState(false);
    const [traceTitle, setTraceTitle] = useState("");
    const [traceLoading, setTraceLoading] = useState(false);
    const [traceIndex, setTraceIndex] = useState(0);
const [tracePlaying, setTracePlaying] = useState(false);


    // inside PlacementPlannerUI component
useEffect(() => {
  const onNext = () => setTraceIndex(i => Math.min((traceSteps?.length || 1) - 1, i + 1));
  const onPrev = () => setTraceIndex(i => Math.max(0, i - 1));
  const onToggle = () => setTracePlaying(p => !p);

  window.addEventListener("trace-next", onNext);
  window.addEventListener("trace-prev", onPrev);
  window.addEventListener("trace-toggle-play", onToggle);
  return () => {
    window.removeEventListener("trace-next", onNext);
    window.removeEventListener("trace-prev", onPrev);
    window.removeEventListener("trace-toggle-play", onToggle);
  };
}, [traceSteps]);

    useEffect(() => {
        (async () => {
            try {
                const info = await getDatasetsInfo();
                setDatasetsInfo(info);
            } catch (e) {
                // ignore
            }
        })();
    }, []);

    const callGraph = async () => {
        setError(null);
        setLoading(true);
        setGraphPlan(null);
        try {
            const init_state = parseListInput(initStateText);
            const goals = parseListInput(goalsText);
            const resp = await callGraphPlan(init_state, goals);
            setGraphPlan(resp.plan || resp);
            setActiveTab("graphplan");
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    const callPop = async () => {
        setError(null);
        setLoading(true);
        setSchedule(null);
        try {
            const init_state = parseListInput(initStateText);
            const goals = parseListInput(goalsText);
            const resp = await callPopPlan(init_state, goals, { max_parallel_major_actions_per_week: maxParallel });
            setSchedule(resp.schedule || resp);
            setActiveTab("pop");
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    const doRepair = async (markActionName, status = "done") => {
        setRepairLoading(true);
        setError(null);
        try {
            const newExecuted = [...executedActions, { name: markActionName, status }];
            setExecutedActions(newExecuted);
            const init_state = parseListInput(initStateText);
            const goals = parseListInput(goalsText);
            const resp = await callRepair(init_state, goals, newExecuted, { max_parallel_major_actions_per_week: maxParallel });
            setSchedule(resp.repaired_schedule || resp.schedule || resp);
        } catch (e) {
            setError(e.message);
        } finally {
            setRepairLoading(false);
        }
    };

    const doSimulate = async (stateText, actionName) => {
        setError(null);
        setLoading(true);
        try {
            const state = parseListInput(stateText);
            const resp = await callSimulate(state, actionName);
            alert("New state: " + JSON.stringify(resp.new_state || resp));
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchGraphTrace = async () => {
        setTraceLoading(true);
        try {
            const init_state = parseListInput(initStateText);
            const goals = parseListInput(goalsText);
            const resp = await callGraphPlanTrace(init_state, goals);
            // resp: { plan: [...], trace: [...] }
            setTraceSteps(resp.trace || []);
            setTraceTitle("GraphPlan Trace");
            setShowTraceModal(true);
        } catch (e) {
            setError(e.message || String(e));
        } finally {
            setTraceLoading(false);
        }
    };

    const fetchPopTrace = async () => {
        setTraceLoading(true);
        try {
            const init_state = parseListInput(initStateText);
            const goals = parseListInput(goalsText);
            const resp = await callPopTrace(init_state, goals);
            // resp: { schedule: [...], trace: [...] }
            setTraceSteps(resp.trace || []);
            setTraceTitle("POP Trace");
            setShowTraceModal(true);
        } catch (e) {
            setError(e.message || String(e));
        } finally {
            setTraceLoading(false);
        }
    };


    const handleShowDetails = (action) => {
        setSelectedAction(action);
        setShowDetailsModal(true);
    };

    const totalEffort = useMemo(() => {
        if (!schedule) return 0;
        return schedule.reduce((sum, a) => sum + (a.effort_hours || 0), 0);
    }, [schedule]);

    const totalWeeks = useMemo(() => {
        if (!schedule) return 0;
        return Math.max(...schedule.map(a => (a.est || 0) + (a.duration || 0)), 0);
    }, [schedule]);

    const presets = [
        { name: "Beginner", init: "DSA_LOW,ML_LOW,RESUME_LOW,NOT_BURNOUT", goals: "DSA_HIGH,RESUME_HIGH,CONF_HIGH" },
        { name: "Intermediate", init: "DSA_MED,ML_LOW,RESUME_MED,NOT_BURNOUT", goals: "DSA_HIGH,ML_MED,RESUME_HIGH" },
        { name: "Advanced", init: "DSA_MED,ML_MED,RESUME_MED,NOT_BURNOUT", goals: "DSA_HIGH,ML_HIGH,CONF_HIGH" },
    ];

    return (
        <div className="min-h-screen bg-slate-950 text-white overflow-hidden">
            {/* Background effects */}
            <ParticleBackground />
            <GradientOrbs />

            {/* Header */}
            <motion.header
                initial={{ y: -100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="relative z-10 border-b border-white/10 backdrop-blur-xl bg-slate-900/50"
            >
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                                className="p-2 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500"
                            >
                                <Icons.Brain />
                            </motion.div>
                            <div>
                                <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                                    Placement Planner
                                </h1>
                                <p className="text-xs text-slate-400">GraphPlan & POP Scheduler</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <Tag color="emerald">v2.0</Tag>
                            <div className="text-xs text-slate-400">
                                Backend: <code className="text-purple-400">{(import.meta.env.VITE_API_URL || "localhost:8000")}</code>
                            </div>
                        </div>
                    </div>
                </div>
            </motion.header>

            {/* Main Content */}
            <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">
                {/* Error Alert */}
                <AnimatePresence>
                    {error && (
                        <motion.div
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="mb-6 p-4 rounded-xl bg-rose-500/20 border border-rose-500/30 text-rose-300 flex items-center gap-3"
                        >
                            <Icons.X />
                            <span>{error}</span>
                            <button onClick={() => setError(null)} className="ml-auto p-1 hover:bg-rose-500/20 rounded">
                                <Icons.X />
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left Panel - Configuration */}
                    <div className="lg:col-span-4 space-y-6">
                        {/* Profile Card */}
                        <GlassCard className="p-6" delay={0.1}>
                            <div className="flex items-center gap-2 mb-4">
                                <Icons.Target />
                                <h3 className="font-semibold text-lg">Student Profile</h3>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm text-slate-400 mb-2">Initial State</label>
                                    <textarea
                                        rows={3}
                                        value={initStateText}
                                        onChange={(e) => setInitStateText(e.target.value)}
                                        className="w-full p-3 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all resize-none"
                                        placeholder="e.g., DSA_LOW, ML_LOW, RESUME_LOW"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-slate-400 mb-2">Goals</label>
                                    <textarea
                                        rows={2}
                                        value={goalsText}
                                        onChange={(e) => setGoalsText(e.target.value)}
                                        className="w-full p-3 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all resize-none"
                                        placeholder="e.g., DSA_HIGH, RESUME_HIGH"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm text-slate-400 mb-2">Max Parallel Actions/Week</label>
                                    <input
                                        type="number"
                                        min={1}
                                        value={maxParallel}
                                        onChange={(e) => setMaxParallel(Number(e.target.value || 1))}
                                        className="w-full p-3 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all"
                                    />
                                </div>
                            </div>

                            {/* Presets */}
                            <div className="mt-4">
                                <label className="block text-sm text-slate-400 mb-2">Quick Presets</label>
                                <div className="flex flex-wrap gap-2">
                                    {presets.map((preset) => (
                                        <motion.button
                                            key={preset.name}
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={() => {
                                                setInitStateText(preset.init);
                                                setGoalsText(preset.goals);
                                            }}
                                            className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm hover:bg-white/10 transition-colors"
                                        >
                                            {preset.name}
                                        </motion.button>
                                    ))}
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="mt-6 space-y-3">
                                <GlowButton
                                    variant="primary"
                                    onClick={callGraph}
                                    disabled={loading}
                                    className="w-full"
                                    icon={<Icons.Brain />}
                                >
                                    {loading && activeTab !== "pop" ? "Computing..." : "Run GraphPlan"}
                                </GlowButton>
                                <GlowButton
                                    variant="success"
                                    onClick={callPop}
                                    disabled={loading}
                                    className="w-full"
                                    icon={<Icons.Calendar />}
                                >
                                    {loading && activeTab === "pop" ? "Scheduling..." : "Run POP Scheduler"}
                                </GlowButton>
                            </div>
                            <div className="mt-2 flex gap-2">
                                <GlowButton onClick={fetchGraphTrace} variant="secondary" className="flex-1" disabled={traceLoading}>
                                    Show GraphPlan Trace
                                </GlowButton>
                                <GlowButton onClick={fetchPopTrace} variant="secondary" className="flex-1" disabled={traceLoading}>
                                    Show POP Trace
                                </GlowButton>
                            </div>

                        </GlassCard>

                        {/* Quick Stats */}
                        {schedule && schedule.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="grid grid-cols-2 gap-3"
                            >
                                <StatsCard
                                    icon={<Icons.Rocket />}
                                    label="Actions"
                                    value={schedule.length}
                                    color="purple"
                                />
                                <StatsCard
                                    icon={<Icons.Clock />}
                                    label="Total Hours"
                                    value={totalEffort}
                                    color="amber"
                                />
                                <StatsCard
                                    icon={<Icons.Calendar />}
                                    label="Duration"
                                    value={`${totalWeeks}w`}
                                    color="emerald"
                                />
                                <StatsCard
                                    icon={<Icons.Check />}
                                    label="Completed"
                                    value={executedActions.length}
                                    color="blue"
                                />
                            </motion.div>
                        )}

                        {/* Simulate Panel */}
                        <GlassCard className="p-6" delay={0.2}>
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <Icons.Play />
                                    <h3 className="font-semibold">Simulate Action</h3>
                                </div>
                                <GlowButton
                                    variant="secondary"
                                    onClick={() => setShowSimulateModal(true)}
                                    className="text-sm py-1.5"
                                >
                                    Open
                                </GlowButton>
                            </div>
                            <p className="text-sm text-slate-400">
                                Test how individual actions affect the state.
                            </p>
                        </GlassCard>
                    </div>

                    {/* Right Panel - Results */}
                    <div className="lg:col-span-8 space-y-6">
                        {/* Tabs */}
                        <GlassCard className="p-2" delay={0.2}>
                            <div className="flex gap-2">
                                {["graphplan", "pop"].map((tab) => (
                                    <motion.button
                                        key={tab}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => setActiveTab(tab)}
                                        className={`
                      flex-1 py-3 px-4 rounded-xl font-medium transition-all
                      ${activeTab === tab
                                                ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg"
                                                : "text-slate-400 hover:text-white hover:bg-white/5"
                                            }
                    `}
                                    >
                                        {tab === "graphplan" ? "GraphPlan Results" : "POP Schedule"}
                                    </motion.button>
                                ))}
                            </div>
                        </GlassCard>

                        {/* Loading State */}
                        <AnimatePresence>
                            {loading && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="flex items-center justify-center py-20"
                                >
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                        className="w-12 h-12 border-4 border-purple-500/30 border-t-purple-500 rounded-full"
                                    />
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* GraphPlan Results */}
                        {!loading && activeTab === "graphplan" && (
                            <GlassCard className="p-6" delay={0.3}>
                                <div className="flex items-center gap-2 mb-4">
                                    <Icons.Sparkles />
                                    <h3 className="font-semibold text-lg">Action Sequence</h3>
                                    {graphPlan && <Tag color="purple">{graphPlan.length} actions</Tag>}
                                </div>

                                {!graphPlan && (
                                    <div className="text-center py-12 text-slate-400">
                                        <Icons.Brain />
                                        <p className="mt-2">Run GraphPlan to see the action sequence</p>
                                    </div>
                                )}

                                {graphPlan && graphPlan.length === 0 && (
                                    <div className="text-center py-12 text-slate-400">
                                        <p>No plan found. Try adjusting your goals.</p>
                                    </div>
                                )}

                                {graphPlan && graphPlan.length > 0 && (
                                    <div className="space-y-3">
                                        {graphPlan.map((action, idx) => (
                                            <ActionCard
                                                key={idx}
                                                action={typeof action === 'string' ? { name: action } : action}
                                                index={idx}
                                                type="graphplan"
                                                onMark={() => { }}
                                                onDetails={handleShowDetails}
                                            />
                                        ))}
                                    </div>
                                )}
                            </GlassCard>
                        )}

                        {/* POP Schedule Results */}
                        {!loading && activeTab === "pop" && (
                            <>
                                <GlassCard className="p-6" delay={0.3}>
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center gap-2">
                                            <Icons.Calendar />
                                            <h3 className="font-semibold text-lg">Scheduled Actions</h3>
                                            {schedule && <Tag color="emerald">{schedule.length} actions</Tag>}
                                        </div>
                                    </div>

                                    {!schedule && (
                                        <div className="text-center py-12 text-slate-400">
                                            <Icons.Calendar />
                                            <p className="mt-2">Run POP Scheduler to see the timeline</p>
                                        </div>
                                    )}

                                    {schedule && schedule.length === 0 && (
                                        <div className="text-center py-12 text-slate-400">
                                            <p>No schedule generated. Try adjusting your inputs.</p>
                                        </div>
                                    )}

                                    {schedule && schedule.length > 0 && (
                                        <div className="space-y-3">
                                            {schedule.map((action, idx) => (
                                                <ActionCard
                                                    key={idx}
                                                    action={action}
                                                    index={idx}
                                                    type="schedule"
                                                    onMark={setSelectedActionToMark}
                                                    onDetails={handleShowDetails}
                                                />
                                            ))}
                                        </div>
                                    )}
                                </GlassCard>

                                {/* Gantt Chart */}
                                {schedule && schedule.length > 0 && (
                                    <GlassCard className="p-6" delay={0.4}>
                                        <Gantt schedule={schedule} />
                                    </GlassCard>
                                )}

                                {/* Repair Panel */}
                                {schedule && schedule.length > 0 && (
                                    <GlassCard className="p-6" delay={0.5}>
                                        <div className="flex items-center gap-2 mb-4">
                                            <Icons.Refresh />
                                            <h3 className="font-semibold text-lg">Plan Repair</h3>
                                        </div>

                                        <div className="flex gap-3 items-end">
                                            <div className="flex-1">
                                                <label className="block text-sm text-slate-400 mb-2">Mark Action</label>
                                                <select
                                                    value={selectedActionToMark || ""}
                                                    onChange={(e) => setSelectedActionToMark(e.target.value)}
                                                    className="w-full p-3 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                                >
                                                    <option value="">Select action...</option>
                                                    {schedule.map((a, i) => (
                                                        <option key={i} value={a.name}>{a.name}</option>
                                                    ))}
                                                </select>
                                            </div>
                                            <GlowButton
                                                variant="success"
                                                onClick={() => selectedActionToMark && doRepair(selectedActionToMark, "done")}
                                                disabled={!selectedActionToMark || repairLoading}
                                                icon={<Icons.Check />}
                                            >
                                                Done
                                            </GlowButton>
                                            <GlowButton
                                                variant="danger"
                                                onClick={() => selectedActionToMark && doRepair(selectedActionToMark, "failed")}
                                                disabled={!selectedActionToMark || repairLoading}
                                                icon={<Icons.X />}
                                            >
                                                Failed
                                            </GlowButton>
                                        </div>

                                        {executedActions.length > 0 && (
                                            <div className="mt-4">
                                                <span className="text-sm text-slate-400">Executed: </span>
                                                <div className="flex flex-wrap gap-2 mt-2">
                                                    {executedActions.map((a, i) => (
                                                        <Tag key={i} color={a.status === "done" ? "emerald" : "rose"}>
                                                            {a.name} ({a.status})
                                                        </Tag>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </GlassCard>
                                )}
                            </>
                        )}
                    </div>
                </div>
            </main>

            {/* Footer */}
            <motion.footer
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                className="relative z-10 border-t border-white/10 backdrop-blur-xl bg-slate-900/50 mt-12"
            >
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        <div className="flex items-center gap-2">
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                                className="p-1.5 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500"
                            >
                                <Icons.Brain />
                            </motion.div>
                            <span className="text-sm text-slate-400">
                                Placement Planner © 2024 • AI-Powered Career Planning
                            </span>
                        </div>

                        <div className="flex items-center gap-6">
                            <motion.a
                                href="#"
                                whileHover={{ scale: 1.1, y: -2 }}
                                className="text-slate-400 hover:text-white transition-colors"
                            >
                                <Icons.GitHub />
                            </motion.a>
                            <div className="flex items-center gap-2 text-sm text-slate-400">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                System Online
                            </div>
                        </div>
                    </div>
                </div>
            </motion.footer>

            {/* Details Modal */}
            <Modal
                isOpen={showDetailsModal}
                onClose={() => setShowDetailsModal(false)}
                title="Action Details"
            >
                {selectedAction && (
                    <div className="space-y-4">
                        <div>
                            <h4 className="text-lg font-semibold text-white mb-2">{selectedAction.name}</h4>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            {(selectedAction.duration !== undefined || selectedAction.duration_weeks !== undefined) && (
                                <div className="p-3 rounded-xl bg-white/5">
                                    <span className="text-xs text-slate-400">Duration</span>
                                    <p className="text-white font-medium">{(selectedAction.duration ?? selectedAction.duration_weeks)} weeks</p>
                                </div>
                            )}
                            {(selectedAction.effort_hours !== undefined || selectedAction.effort !== undefined) && (
                                <div className="p-3 rounded-xl bg-white/5">
                                    <span className="text-xs text-slate-400">Effort</span>
                                    <p className="text-white font-medium">{(selectedAction.effort_hours ?? selectedAction.effort)} hours</p>
                                </div>
                            )}
                            {selectedAction.est !== undefined && (
                                <div className="p-3 rounded-xl bg-white/5">
                                    <span className="text-xs text-slate-400">Start Week</span>
                                    <p className="text-white font-medium">Week {selectedAction.est}</p>
                                </div>
                            )}
                        </div>

                        {selectedAction.preconds && selectedAction.preconds.length > 0 && (
                            <div>
                                <span className="text-sm text-slate-400 block mb-2">Preconditions</span>
                                <div className="flex flex-wrap gap-2">
                                    {selectedAction.preconds.map((p, i) => (
                                        <Tag key={i} color="amber">{p}</Tag>
                                    ))}
                                </div>
                            </div>
                        )}

                        {selectedAction.adds && selectedAction.adds.length > 0 && (
                            <div>
                                <span className="text-sm text-slate-400 block mb-2">Effects (Adds)</span>
                                <div className="flex flex-wrap gap-2">
                                    {selectedAction.adds.map((a, i) => (
                                        <Tag key={i} color="emerald">{a}</Tag>
                                    ))}
                                </div>
                            </div>
                        )}

                        {selectedAction.dels && selectedAction.dels.length > 0 && (
                            <div>
                                <span className="text-sm text-slate-400 block mb-2">Effects (Removes)</span>
                                <div className="flex flex-wrap gap-2">
                                    {selectedAction.dels.map((d, i) => (
                                        <Tag key={i} color="rose">{d}</Tag>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </Modal>

            {/* Simulate Modal */}
            <Modal
                isOpen={showSimulateModal}
                onClose={() => setShowSimulateModal(false)}
                title="Simulate Action"
            >
                <SimulatePanel onSimulate={doSimulate} onClose={() => setShowSimulateModal(false)} />
            </Modal>
            <TraceModal
                isOpen={showTraceModal}
                onClose={() => setShowTraceModal(false)}
                title={traceTitle}
                steps={traceSteps}
            />
        </div>
    );
}

// Simulate Panel Component
function SimulatePanel({ onSimulate, onClose }) {
    const [stateText, setStateText] = useState("DSA_LOW,RESUME_MED,NOT_BURNOUT");
    const [actionName, setActionName] = useState("");

    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm text-slate-400 mb-2">Current State</label>
                <textarea
                    rows={3}
                    value={stateText}
                    onChange={(e) => setStateText(e.target.value)}
                    className="w-full p-3 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 resize-none"
                    placeholder="e.g., DSA_LOW, RESUME_MED"
                />
            </div>

            <div>
                <label className="block text-sm text-slate-400 mb-2">Action Name</label>
                <input
                    value={actionName}
                    onChange={(e) => setActionName(e.target.value)}
                    className="w-full p-3 rounded-xl bg-slate-800/50 border border-white/10 text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                    placeholder="e.g., DSA_Practice_intense"
                />
            </div>

            <div className="flex gap-3 pt-2">
                <GlowButton
                    variant="primary"
                    onClick={() => onSimulate(stateText, actionName)}
                    disabled={!actionName}
                    className="flex-1"
                    icon={<Icons.Play />}
                >
                    Simulate
                </GlowButton>
                <GlowButton variant="secondary" onClick={onClose}>
                    Cancel
                </GlowButton>
            </div>
        </div>
    );
}

// Add Icons.Play to the Icons object (already included above)