// src/api/planner.js
const API_BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");

async function postJSON(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${txt}`);
  }
  return res.json();
}

export async function callGraphPlan(init_state, goals) {
  return postJSON("/plan/graphplan", { init_state, goals });
}

export async function callPopPlan(init_state, goals, opts = {}) {
  // planner endpoint expects planner wrapper with init_state/goals; our backend uses plan_pop_with_repair wrapper
  // We'll call /plan/pop and send the same shape used by the FastAPI PlanRequest model
  const payload = {
    init_state,
    goals,
    max_paraller_major_actions_per_week: opts.max_parallel_major_actions_per_week ?? 1
  };
  return postJSON("/plan/pop", payload);
}

export async function callRepair(init_state, goals, executed_actions = [], opts = {}) {
  return postJSON("/plan/repair", {
    init_state,
    goals,
    executed_actions,
    max_parallel_major_actions_per_week: opts.max_parallel_major_actions_per_week ?? 1,
  });
}

export async function callSimulate(state, action_name) {
  return postJSON("/simulate", { state, acttion_name: action_name });
}

export async function getDatasetsInfo() {
  const res = await fetch(`${API_BASE}/datasets/info`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

// NEW trace endpoints
export async function callGraphPlanTrace(init_state, goals) {
  return await postJSON("/plan/graphplan/trace", { init_state, goals });
}

export async function callPopTrace(init_state, goals, opts = {}) {
  // opts ignored for now
  return await postJSON("/plan/pop/trace", { init_state, goals });
}