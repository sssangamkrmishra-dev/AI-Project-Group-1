# app.py
"""
FastAPI wrapper for the planners and plan repair endpoint.
Endpoints:
- POST /plan/graphplan
- POST /plan/pop
- POST /plan/repair
- POST /simulate
- GET  /datasets/info
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

# # planner functions
# from planner_module import (
#     build_domain,
#     graphplan,
#     pop_plan,
#     apply_executed_actions_to_state,
#     plan_pop_with_repair,  # kept for compatibility but not required by every endpoint
# )
from planner_module import *

app = FastAPI(title="Placement Planner API (POP+Temporal)")

# Allow CORS for local frontend development (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <--- change in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    init_state: List[str]
    goals: List[str]
    planner: Optional[str] = "pop"  # currently unused but kept for future extension
    max_parallel_major_actions_per_week: Optional[int] = 1
    max_hours_per_week: Optional[float] = 40.0
    max_search_steps: Optional[int] = 2000


class RepairRequest(BaseModel):
    init_state: List[str]
    goals: List[str]
    executed_actions: List[Dict[str, str]]  # list of {"name": ..., "status": "done"/"failed"/"skipped"}
    max_parallel_major_actions_per_week: Optional[int] = 1
    max_hours_per_week: Optional[float] = 40.0
    max_search_steps: Optional[int] = 2000


class SimRequest(BaseModel):
    state: List[str]
    action_name: str


# ---------------- Endpoints ----------------
@app.post("/plan/graphplan")
def api_graphplan(req: PlanRequest):
    actions = build_domain()
    plan, states_levels, actions_levels = graphplan(actions, set(req.init_state), set(req.goals))
    if plan is None:
        raise HTTPException(status_code=404, detail="No plan found with GraphPlan")

    result = [
        {
            "name": a.name,
            "duration_weeks": a.duration,
            "effort_hours": a.effort_hours,
            "preconds": list(a.preconds),
            "adds": list(a.adds),
        }
        for a in plan
    ]
    return {"plan": result, "method": "graphplan"}


@app.post("/plan/pop")
def api_pop(req: PlanRequest):
    domain_actions = build_domain()
    # call pop_plan directly so frontend can pass max_hours_per_week
    schedule = pop_plan(
        domain_actions,
        set(req.init_state),
        set(req.goals),
        max_search_steps=req.max_search_steps or 2000,
        max_parallel_major_actions_per_week=req.max_parallel_major_actions_per_week or 1,
        max_hours_per_week=req.max_hours_per_week,
    )

    if schedule is None:
        raise HTTPException(status_code=404, detail="No plan found with POP")

    return {"schedule": schedule, "method": "pop"}


@app.post("/plan/repair")
def api_repair(req: RepairRequest):
    domain_actions = build_domain()
    # apply executed actions to derive new initial state
    try:
        new_state = apply_executed_actions_to_state(set(req.init_state), req.executed_actions, domain_actions)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error applying executed actions: {e}")

    schedule = pop_plan(
        domain_actions,
        new_state,
        set(req.goals),
        max_search_steps=req.max_search_steps or 2000,
        max_parallel_major_actions_per_week=req.max_parallel_major_actions_per_week or 1,
        max_hours_per_week=req.max_hours_per_week,
    )
    if schedule is None:
        raise HTTPException(status_code=500, detail="Repair/replanning failed")

    return {"repaired_schedule": schedule, "method": "pop_repair"}


@app.post("/simulate")
def api_simulate(req: SimRequest):
    actions = build_domain()
    action = next((a for a in actions if a.name == req.action_name), None)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    state = set(req.state)
    if not action.preconds.issubset(state):
        raise HTTPException(status_code=400, detail=f"Preconditions not met: need {list(action.preconds)}")
    state -= set(action.dels)
    state |= set(action.adds)
    return {"new_state": list(state)}


@app.get("/datasets/info")
def datasets_info():
    return {
        "note": "Place datasets in /data and run dataset_skeleton.run_all_and_save(). "
                "dataset_skeleton provides heuristics for durations / effect probabilities.",
        "expected_files": ["data/leetcode.csv", "data/mock_interviews.json"],
    }


@app.post("/plan/graphplan/trace")
def api_graphplan_trace(req: PlanRequest):
    actions = build_domain()
    plan, trace, states_levels, actions_levels = graphplan_trace(actions, set(req.init_state), set(req.goals))
    if plan is None:
        return {"plan": None, "trace": trace}
    # normalize plan items for frontend
    plan_out = [{"name": a.name, "duration": a.duration, "effort_hours": a.effort_hours, "preconds": list(a.preconds), "adds": list(a.adds)} for a in plan]
    return {"plan": plan_out, "trace": trace}

@app.post("/plan/pop/trace")
def api_pop_trace(req: PlanRequest):
    actions = build_domain()
    scheduled, trace = pop_trace(actions, set(req.init_state), set(req.goals),
                                 max_search_steps=2000,
                                 max_hours_per_week=40)
    return {"schedule": scheduled, "trace": trace}


if __name__ == "__main__":
    # Run with reload during development; in production use a proper ASGI server config.
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
