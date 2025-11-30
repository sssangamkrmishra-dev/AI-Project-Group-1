# run_planner_example.py
"""
Interactive runner for the planners (GraphPlan + POP).
Prompts user for initial state and goals (comma-separated) or uses defaults.
Prints:
 - chosen initial state and goals
 - GraphPlan build levels (intermediate states / actions per level if available)
 - GraphPlan final ordered plan and a step-by-step state progression
 - POP scheduled plan and a step-by-step state progression when actions start
"""

import json
import sys
from planner_module import build_domain, graphplan, pop_plan

def parse_input_list(s: str):
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]

def stable_list_from(obj):
    # convert set/list/tuple to sorted list for stable printing
    if obj is None:
        return []
    if isinstance(obj, (set, tuple)):
        return sorted(list(obj))
    if isinstance(obj, list):
        return obj
    return [obj]

def get_attr(o, name, default=None):
    if o is None:
        return default
    if isinstance(o, dict):
        return o.get(name, default)
    return getattr(o, name, default)

def pretty_print_action(action):
    name = get_attr(action, "name", "<unnamed>")
    dur = get_attr(action, "duration", get_attr(action, "duration_weeks", "?"))
    effort = get_attr(action, "effort_hours", get_attr(action, "effort", "?"))
    adds = stable_list_from(get_attr(action, "adds", get_attr(action, "add", [])))
    dels = stable_list_from(get_attr(action, "dels", get_attr(action, "del", get_attr(action, "deletes", []))))
    return {
        "name": name,
        "duration": dur,
        "effort_hours": effort,
        "adds": adds,
        "dels": dels
    }

def simulate_apply(state_set, action):
    """Apply deletes and adds (mutating a shallow copy) and return new state set"""
    s = set(state_set)
    dels = stable_list_from(get_attr(action, "dels", get_attr(action, "deletes", [])))
    adds = stable_list_from(get_attr(action, "adds", get_attr(action, "add", [])))
    for d in dels:
        if d in s:
            s.remove(d)
    for a in adds:
        s.add(a)
    return s

def print_separator():
    print("=" * 80)

def main():
    # load estimates.json optionally
    est = {}
    try:
        with open("estimates.json", "r") as f:
            est = json.load(f)
            print("Loaded estimates.json (data-driven heuristics).")
    except FileNotFoundError:
        print("estimates.json not found — using domain defaults.")

    domain_actions = build_domain(effect_estimates=est)

    # prompt user for input or use defaults
    print_separator()
    print("Planner example (interactive).")
    print("Press Enter to use defaults or provide comma-separated values.")
    default_init = "DSA_LOW, ML_LOW, RESUME_LOW, NOT_BURNOUT"
    default_goals = "DSA_HIGH, RESUME_HIGH, CONF_HIGH"
    try:
        raw_init = input(f"Initial state [{default_init}]: ").strip()
        raw_goals = input(f"Goals [{default_goals}]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nInput interrupted — using defaults.")
        raw_init = ""
        raw_goals = ""

    init_state = set(parse_input_list(raw_init or default_init))
    goals = set(parse_input_list(raw_goals or default_goals))

    print_separator()
    print("Chosen inputs:")
    print("Initial state:", ", ".join(sorted(init_state)) if init_state else "(empty)")
    print("Goals:", ", ".join(sorted(goals)) if goals else "(empty)")
    print_separator()

    # --- GraphPlan ---
    print("\n=== Running GraphPlan ===")
    gp_plan, states_levels, actions_levels = graphplan(domain_actions, init_state, goals)

    if gp_plan is None:
        print("\nGraphPlan: No plan found.")
    else:
        # Print levels if available
        if states_levels:
            print("\nGraph construction levels (states per level):")
            for lvl, s in enumerate(states_levels):
                s_list = sorted(list(s)) if isinstance(s, (set, list, tuple)) else s
                print(f"  Level {lvl}: {len(s_list)} state facts -> {s_list}")

        if actions_levels:
            print("\nActions available per level (graph):")
            for lvl, acts in enumerate(actions_levels):
                names = [get_attr(a, "name", str(a)) for a in acts]
                print(f"  Level {lvl}: {len(names)} actions -> {names}")

        # Final plan
        print("\nGraphPlan final ordered sequence:")
        for i, a in enumerate(gp_plan, 1):
            pa = pretty_print_action(a)
            print(f"  {i}. {pa['name']}: duration={pa['duration']}, effort={pa['effort_hours']}, adds={pa['adds']}, dels={pa['dels']}")

        # Step-by-step simulate applying plan from init_state
        print("\nGraphPlan step-by-step state progression:")
        cur_state = set(init_state)
        print(f"  [start] State ({len(cur_state)}): {sorted(cur_state)}")
        for i, a in enumerate(gp_plan, 1):
            pa = pretty_print_action(a)
            next_state = simulate_apply(cur_state, a)
            adds = pa["adds"]
            dels = pa["dels"]
            print(f"  Step {i}: Apply '{pa['name']}' -> removes: {dels} ; adds: {adds}")
            print(f"    before: {sorted(cur_state)}")
            print(f"    after : {sorted(next_state)}")
            cur_state = next_state

    # --- POP ---
    print_separator()
    print("\n=== Running POP (with scheduling) ===")
    pop_schedule = pop_plan(domain_actions, init_state, goals,
                            max_search_steps=2000,
                            max_parallel_major_actions_per_week=1,
                            max_hours_per_week=40)
    if not pop_schedule:
        print("\nPOP: No plan found.")
    else:
        # print schedule sorted by est
        sorted_sched = sorted(pop_schedule, key=lambda x: get_attr(x, "est", x.get("est", 0) if isinstance(x, dict) else 0))
        print("\nPOP scheduled plan (sorted by EST):")
        for item in sorted_sched:
            name = get_attr(item, "name", item.get("name", "<unnamed>") if isinstance(item, dict) else str(item))
            est_week = get_attr(item, "est", item.get("est", 0) if isinstance(item, dict) else 0)
            duration = get_attr(item, "duration", item.get("duration", get_attr(item, "duration_weeks", "?")))
            effort = get_attr(item, "effort_hours", item.get("effort_hours", get_attr(item, "effort", "?")))
            why = get_attr(item, "why", "")
            expected_benefit = get_attr(item, "expected_benefit", get_attr(item, "benefit", ""))
            risk = get_attr(item, "risk", "")
            adds = stable_list_from(get_attr(item, "adds", get_attr(item, "add", [])))
            dels = stable_list_from(get_attr(item, "dels", get_attr(item, "dels", get_attr(item, "deletes", []))))
            print(f"  - {name}: start_week={est_week}, duration_weeks={duration}, effort_hours={effort}")
            if why:
                print(f"      why: {why}")
            if expected_benefit:
                print(f"      benefit: {expected_benefit}")
            if risk:
                print(f"      risk: {risk}")
            if adds:
                print(f"      adds: {adds}")
            if dels:
                print(f"      deletes: {dels}")

        # Step-by-step simulate state progression by start_week order
        print("\nPOP step-by-step state progression (ordered by start week):")
        cur_state = set(init_state)
        print(f"  [start] State ({len(cur_state)}): {sorted(cur_state)}")
        for item in sorted_sched:
            name = get_attr(item, "name", "<unnamed>")
            est_week = get_attr(item, "est", 0)
            pa = pretty_print_action(item)
            # show when this action starts
            print(f"\n  Week {est_week}: Action '{pa['name']}' starts (duration {pa['duration']} weeks)")
            print(f"    before: {sorted(cur_state)}")
            next_state = simulate_apply(cur_state, item)
            print(f"    after : {sorted(next_state)}")
            cur_state = next_state

    print_separator()
    print("\nDone.")

if __name__ == "__main__":
    main()
