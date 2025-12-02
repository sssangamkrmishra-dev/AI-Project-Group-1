# module2_core.py
"""
Core model for Module 2: Search-Based Recommendation.

Includes:
 - readiness(state, weights, burnout)
 - transition(state, burnout, action_name)
 - bfs_search (breadth-first, depth-limited)
 - uniform_cost_search (UCS)
 - a_star_search (A*)
 - single_action_scores (utility per minute)
 - small demo when run as main
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Any
import heapq

# ------------------ Action definitions ------------------
ACTIONS = {
    "Solve DSA Problem": {
        "effects": {"DSA": 0.15, "SystemDesign": 0.0, "Resume": 0.0, "HR": 0.0},
        "time_cost": 60,
        "burnout": 0.05
    },
    "Revise Resume": {
        "effects": {"DSA": 0.0, "SystemDesign": 0.0, "Resume": 0.25, "HR": 0.0},
        "time_cost": 30,
        "burnout": 0.02
    },
    "Practice System Design": {
        "effects": {"DSA": 0.02, "SystemDesign": 0.2, "Resume": 0.0, "HR": 0.0},
        "time_cost": 90,
        "burnout": 0.07
    },
    "Give Mock HR Interview": {
        "effects": {"DSA": 0.0, "SystemDesign": 0.0, "Resume": 0.0, "HR": 0.2},
        "time_cost": 45,
        "burnout": 0.03
    },
    "Quick Revision": {
        "effects": {"DSA": 0.05, "SystemDesign": 0.05, "Resume": 0.05, "HR": 0.05},
        "time_cost": 20,
        "burnout": 0.01
    },
    "Take a Break": {
        "effects": {"DSA": 0.0, "SystemDesign": 0.0, "Resume": 0.0, "HR": 0.0},
        "time_cost": 15,
        "burnout": -0.1
    }
}
SKILL_AREAS = ["DSA", "SystemDesign", "Resume", "HR"]
GOAL_READINESS = 0.75

# ------------------ Utility functions ------------------
def readiness(state: Dict[str, float], weights: Dict[str, float], burnout: float) -> float:
    """
    Compute readiness: weighted skill sum penalized by burnout.
    burnout in [0,1]. Higher burnout reduces readiness multiplicatively.
    """
    skill_sum = sum(weights[k] * state[k] for k in SKILL_AREAS)
    burnout = max(0.0, min(1.0, burnout))
    return skill_sum * (1 - 0.8 * burnout)

def transition(state: Dict[str, float], burnout: float, action_name: str) -> Tuple[Dict[str, float], float, float]:
    """
    Apply an action deterministically.
    Returns (new_state, new_burnout, action_cost).
    action_cost = time_cost + 200 * max(0, delta_burnout)
    """
    action = ACTIONS[action_name]
    new_state = state.copy()
    for k in SKILL_AREAS:
        new_state[k] = max(0.0, min(1.0, new_state[k] + action["effects"].get(k, 0.0)))
    new_burnout = max(0.0, min(1.0, burnout + action["burnout"]))
    cost = action["time_cost"] + 200 * max(0.0, new_burnout - burnout)
    return new_state, new_burnout, cost

def encode_state(state: Dict[str, float], burnout: float) -> Tuple:
    """Round state values for hashing in search algorithms."""
    return tuple(round(state[k], 4) for k in SKILL_AREAS) + (round(burnout, 4),)

@dataclass(order=True)
class PrioritizedItem:
    priority: float
    item: Any = field(compare=False)

# ------------------ BFS (Uninformed, depth-limited) ------------------
def bfs_search(start_state: Dict[str,float], start_burnout: float, weights: Dict[str,float],
               max_depth: int = 12, max_expansions: int = 20000):
    """
    Breadth-first search exploring by plan length (number of actions).
    Returns shortest-length plan if goal reached within max_depth.
    """
    from collections import deque

    frontier = deque()
    frontier.append((start_state, start_burnout, [], 0))
    visited = set()
    expansions = 0

    while frontier and expansions < max_expansions:
        state, burnout, path, depth = frontier.popleft()
        enc = encode_state(state, burnout)

        if enc in visited:
            expansions += 1
            continue
        visited.add(enc)

        # Goal test
        if readiness(state, weights, burnout) >= GOAL_READINESS:
            return {"path": path, "cost": depth, "final_state": state, "burnout": burnout, "expansions": expansions}

        if depth >= max_depth:
            expansions += 1
            continue

        # Expand actions
        for action_name in ACTIONS:
            ns, nb, _ = transition(state, burnout, action_name)
            frontier.append((ns, nb, path + [action_name], depth + 1))

        expansions += 1

    return None

# ------------------ Uniform-Cost Search (UCS) ------------------
def uniform_cost_search(start_state: Dict[str,float], start_burnout: float, weights: Dict[str,float],
                        max_expansions: int = 20000):
    """
    Uniform-Cost Search minimizing accumulated cost (time + burnout penalty).
    """
    frontier = []
    heapq.heappush(frontier, PrioritizedItem(0.0, (start_state, start_burnout, [], 0.0)))
    explored = dict()
    expansions = 0

    while frontier and expansions < max_expansions:
        pi = heapq.heappop(frontier)
        state, burnout, path, cost_so_far = pi.item
        enc = encode_state(state, burnout)

        if enc in explored and explored[enc] <= cost_so_far:
            expansions += 1
            continue
        explored[enc] = cost_so_far

        if readiness(state, weights, burnout) >= GOAL_READINESS:
            return {"path": path, "cost": cost_so_far, "final_state": state, "burnout": burnout, "expansions": expansions}

        for action_name in ACTIONS:
            ns, nb, action_cost = transition(state, burnout, action_name)
            new_cost = cost_so_far + action_cost
            heapq.heappush(frontier, PrioritizedItem(new_cost, (ns, nb, path + [action_name], new_cost)))

        expansions += 1

    return None

# ------------------ Heuristic for A* ------------------
def heuristic(state: Dict[str,float], burnout: float, weights: Dict[str,float]) -> float:
    """
    Admissible heuristic: estimate minutes needed to reach goal assuming the best action repeated.
    h = deficit / best_gain_per_minute
    Returns large number if no useful action exists.
    """
    cur_ready = readiness(state, weights, burnout)
    deficit = max(0.0, GOAL_READINESS - cur_ready)
    best_rate = 0.0
    for a in ACTIONS.values():
        temp_state = state.copy()
        for k in SKILL_AREAS:
            temp_state[k] = min(1.0, temp_state[k] + a["effects"].get(k, 0.0))
        gain = readiness(temp_state, weights, min(1.0, burnout + a["burnout"])) - cur_ready
        rate = gain / a["time_cost"] if a["time_cost"] > 0 else 0.0
        if rate > best_rate:
            best_rate = rate
    if best_rate <= 1e-9:
        return 1e6
    return deficit / best_rate

# ------------------ A* Search ------------------
def a_star_search(start_state: Dict[str,float], start_burnout: float, weights: Dict[str,float],
                  max_expansions: int = 20000):
    """
    A* search using the admissible heuristic above.
    """
    frontier = []
    start_h = heuristic(start_state, start_burnout, weights)
    heapq.heappush(frontier, PrioritizedItem(start_h, (start_state, start_burnout, [], 0.0)))
    explored = dict()
    expansions = 0

    while frontier and expansions < max_expansions:
        pi = heapq.heappop(frontier)
        state, burnout, path, g = pi.item
        enc = encode_state(state, burnout)

        if enc in explored and explored[enc] <= g:
            expansions += 1
            continue
        explored[enc] = g

        if readiness(state, weights, burnout) >= GOAL_READINESS:
            return {"path": path, "cost": g, "final_state": state, "burnout": burnout, "expansions": expansions}

        for action_name in ACTIONS:
            ns, nb, action_cost = transition(state, burnout, action_name)
            new_g = g + action_cost
            h = heuristic(ns, nb, weights)
            f = new_g + h
            heapq.heappush(frontier, PrioritizedItem(f, (ns, nb, path + [action_name], new_g)))

        expansions += 1

    return None

# ------------------ Single-action utility ------------------
def single_action_scores(state: Dict[str,float], burnout: float, weights: Dict[str,float]):
    """
    Return per-action metrics: gain in readiness, time, utility per minute, burnout_delta.
    """
    rows = []
    cur_ready = readiness(state, weights, burnout)
    for name, a in ACTIONS.items():
        ns = state.copy()
        for k in SKILL_AREAS:
            ns[k] = min(1.0, ns[k] + a["effects"].get(k, 0.0))
        nb = min(1.0, burnout + a["burnout"])
        gain = readiness(ns, weights, nb) - cur_ready
        util_per_min = gain / a["time_cost"] if a["time_cost"] > 0 else 0.0
        rows.append({"action": name, "gain": gain, "time": a["time_cost"], "util_per_min": util_per_min, "burnout_delta": a["burnout"]})
    return rows

# ------------------ Demo runner ------------------
if __name__ == "__main__":
    # Example profile (quick test)
    student_state = {"DSA": 0.6, "SystemDesign": 0.3, "Resume": 0.4, "HR": 0.5}
    student_burnout = 0.2
    weights = {"DSA": 0.4, "SystemDesign": 0.25, "Resume": 0.2, "HR": 0.15}

    print("Student state:", student_state, "burnout:", student_burnout)
    print("Start readiness:", round(readiness(student_state, weights, student_burnout), 4))

    ucs_res = uniform_cost_search(student_state, student_burnout, weights)
    astar_res = a_star_search(student_state, student_burnout, weights)
    bfs_res = bfs_search(student_state, student_burnout, weights, max_depth=12)

    print("\n--- UCS Result ---")
    if ucs_res:
        print("First action:", ucs_res["path"][0] if ucs_res["path"] else None)
        print("Total cost:", round(ucs_res["cost"], 2), "Expansions:", ucs_res["expansions"])
    else:
        print("No plan found by UCS.")

    print("\n--- A* Result ---")
    if astar_res:
        print("First action:", astar_res["path"][0] if astar_res["path"] else None)
        print("g-cost:", round(astar_res["cost"], 2), "Expansions:", astar_res["expansions"])
    else:
        print("No plan found by A*.")

    print("\n--- BFS Result (depth-limited) ---")
    if bfs_res:
        print("First action:", bfs_res["path"][0] if bfs_res["path"] else None)
        print("Plan length (actions):", bfs_res["cost"], "Expansions:", bfs_res["expansions"])
    else:
        print("No plan found by BFS within depth limit.")