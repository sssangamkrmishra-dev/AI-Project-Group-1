# tests_planner.py
"""
Simple test harness that:
- builds domain with optional estimates (not using dataset files here)
- runs GraphPlan and the enhanced POP for 5 profiles
- demonstrates repair endpoint usage locally by simulating an executed action and replanning
"""

from planner_module import build_domain, graphplan, plan_pop_with_repair
import json

profiles = [
    ({"DSA_LOW","ML_LOW","RESUME_LOW","NOT_BURNOUT"},{"DSA_HIGH","RESUME_HIGH","CONF_HIGH"}),
    ({"DSA_MED","ML_LOW","RESUME_LOW","NOT_BURNOUT"},{"DSA_HIGH","RESUME_MED"}),
    ({"DSA_LOW","ML_MED","RESUME_MED","NOT_BURNOUT"},{"DSA_HIGH","RESUME_HIGH","CONF_MED"}),
    ({"DSA_LOW","ML_LOW","RESUME_LOW","BURNOUT"},{"RESUME_MED","DSA_MED"}),
    ({"DSA_MED","ML_MED","RESUME_MED","NOT_BURNOUT"},{"ML_HIGH","DSA_HIGH"}),
]

def run():
    actions = build_domain()
    for i, (init, goals) in enumerate(profiles,1):
        print("-"*60)
        print(f"Profile {i}: init={init}, goals={goals}")
        gp, sl, al = graphplan(actions, init, goals)
        if gp:
            print("GraphPlan sequence:", [a.name for a in gp])
        else:
            print("GraphPlan: No plan found")
        pop_schedule = plan_pop_with_repair(init, goals, domain_actions=actions, max_parallel_major_actions_per_week=1)
        if pop_schedule:
            print("POP schedule:")
            for s in pop_schedule:
                print(f"  - {s['name']} (est week {s['est']}, dur {s['duration']}) -> why: {s['why']} benefit: {s['expected_benefit']} risk: {s['risk']}")
        else:
            print("POP: No plan found")

    # Demo repair: assume in profile 1 we executed DSA_Practice_intense but it failed
    print("\nDemo repair (profile 1): mark DSA_Practice_intense as failed and replan")
    init, goals = profiles[0]
    executed = [{"name":"DSA_Practice_intense", "status":"failed"}]
    repaired = plan_pop_with_repair(init, goals, domain_actions=actions, executed_actions=executed, max_parallel_major_actions_per_week=1)
    print("Repaired schedule:")
    print(json.dumps(repaired, indent=2))

if __name__ == "__main__":
    run()
