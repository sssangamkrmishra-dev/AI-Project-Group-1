# run_recommendation.py
"""
Run recommendation for a single student profile.
Usage:
  python run_recommendation.py
It will print recommended next actions for UCS and A*, save results into ./results/
"""

import json, os
from module2_core import readiness, uniform_cost_search, a_star_search, single_action_scores

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Default profile (changeable)
student_state = {"DSA": 0.6, "SystemDesign": 0.3, "Resume": 0.4, "HR": 0.5}
student_burnout = 0.2
weights = {"DSA": 0.4, "SystemDesign": 0.25, "Resume": 0.2, "HR": 0.15}

def main():
    print("Student profile:", student_state, "burnout:", student_burnout)
    print("Start readiness:", round(readiness(student_state, weights, student_burnout), 4))
    ucs = uniform_cost_search(student_state, student_burnout, weights)
    astar = a_star_search(student_state, student_burnout, weights)

    out = {"student_state": student_state, "student_burnout": student_burnout, "start_readiness": readiness(student_state, weights, student_burnout)}
    if ucs:
        out["ucs"] = ucs
        print("\nUCS recommends next action:", ucs["path"][0] if ucs["path"] else None)
        print("UCS total cost:", round(ucs["cost"],2), "expansions:", ucs["expansions"])
    else:
        print("\nUCS found no plan.")

    if astar:
        out["astar"] = astar
        print("\nA* recommends next action:", astar["path"][0] if astar["path"] else None)
        print("A* g-cost:", round(astar["cost"],2), "expansions:", astar["expansions"])
    else:
        print("\nA* found no plan.")

    out["single_action_scores"] = single_action_scores(student_state, student_burnout, weights)

    path = os.path.join(RESULTS_DIR, "recommendation_summary.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("\nSaved results to", path)

if __name__ == "__main__":
    main()