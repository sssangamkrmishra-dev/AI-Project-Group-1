# run_planner_example.py
import json
from planner_module import build_domain, graphplan, pop_plan

def main():
    # 1) try to load estimates.json (optional)
    est = {}
    try:
        with open("estimates.json", "r") as f:
            est = json.load(f)
            print("Loaded estimates.json (data-driven heuristics).")
    except FileNotFoundError:
        print("estimates.json not found — using domain defaults.")

    # 2) build domain using estimates (if any)
    domain_actions = build_domain(effect_estimates=est)

    # 3) choose initial state & goals (example)
    init_state = set(["DSA_LOW", "ML_LOW", "RESUME_LOW", "NOT_BURNOUT"])
    goals = set(["DSA_HIGH", "RESUME_HIGH", "CONF_HIGH"])

    print("\n=== Running GraphPlan ===")
    gp_plan, states_levels, actions_levels = graphplan(domain_actions, init_state, goals)
    if gp_plan is None:
        print("GraphPlan: No plan found.")
    else:
        print("GraphPlan sequence (in order):")
        for i, a in enumerate(gp_plan, 1):
            print(f"  {i}. {a.name} (dur={a.duration}, effort={a.effort_hours})")

    print("\n=== Running POP (with scheduling) ===")
    # call POP: signature pop_plan(actions, init_state, goals, max_search_steps=..., max_parallel_major_actions_per_week=..., max_hours_per_week=...)
    pop_schedule = pop_plan(domain_actions, init_state, goals,
                            max_search_steps=2000,
                            max_parallel_major_actions_per_week=1,
                            max_hours_per_week=40)
    if not pop_schedule:
        print("POP: No plan found.")
    else:
        print("POP scheduled plan (sorted by EST):")
        for item in pop_schedule:
            print(f"  - {item['name']}: start_week={item['est']}, duration_weeks={item['duration']}, effort_hours={item['effort_hours']}")
            print(f"      why: {item['why']}")
            print(f"      benefit: {item['expected_benefit']}")
            print(f"      risk: {item['risk']}")
    print("\nDone.")

if __name__ == '__main__':
    main()
