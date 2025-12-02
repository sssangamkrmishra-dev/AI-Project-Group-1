# experiments.py
"""
Run experiments across several profiles, compare UCS and A* first actions, write CSV and a plot.
"""
import csv, os, json
import matplotlib.pyplot as plt
from module2_core import bfs_search, uniform_cost_search, a_star_search, readiness

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

profiles = [
    {"name":"balanced_mid", "state":{"DSA":0.6,"SystemDesign":0.3,"Resume":0.4,"HR":0.5}, "burnout":0.2},
    {"name":"dsastrong", "state":{"DSA":0.8,"SystemDesign":0.2,"Resume":0.3,"HR":0.4}, "burnout":0.15},
    {"name":"resume_weak", "state":{"DSA":0.5,"SystemDesign":0.4,"Resume":0.1,"HR":0.6}, "burnout":0.1},
    {"name":"burned_out", "state":{"DSA":0.6,"SystemDesign":0.5,"Resume":0.5,"HR":0.5}, "burnout":0.6},
]

weights = {"DSA":0.4,"SystemDesign":0.25,"Resume":0.2,"HR":0.15}

rows = []
for p in profiles:
    s = p["state"]; b = p["burnout"]
    bfs = None
    try:
        from module2_core import bfs_search
        bfs = bfs_search(s,b,weights,max_depth=12)  # increase depth so BFS often finds a plan
    except Exception:
        bfs = None
    ucs = uniform_cost_search(s,b,weights)
    astar = a_star_search(s,b,weights)
    rows.append({
        "profile": p["name"],
        "start_readiness": round(readiness(s,weights,b), 4),
        "bfs_first": (bfs["path"][0] if bfs else None),
        "bfs_cost": (bfs["cost"] if bfs else None),
        "ucs_first": (ucs["path"][0] if ucs else None),
        "ucs_cost": (round(ucs["cost"],2) if ucs else None),
        "astar_first": (astar["path"][0] if astar else None),
        "astar_cost": (round(astar["cost"],2) if astar else None)
    })

csv_path = os.path.join(RESULTS_DIR, "experiment_results.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
print("Saved", csv_path)

# plot first-action per algorithm
labels = [r["profile"] for r in rows]
actions = sorted({a for r in rows for a in (r["ucs_first"], r["astar_first"], r["bfs_first"]) if a})
action_to_idx = {a:i for i,a in enumerate(actions)}
def encode(arr):
    return [action_to_idx[a] if a else -1 for a in arr]

ucs_actions = [r["ucs_first"] for r in rows]
astar_actions = [r["astar_first"] for r in rows]
bfs_actions = [r["bfs_first"] for r in rows]

plt.figure(figsize=(9,4))
plt.plot(labels, encode(ucs_actions), marker='o', label='UCS')
plt.plot(labels, encode(astar_actions), marker='s', label='A*')
plt.plot(labels, encode(bfs_actions), marker='^', label='BFS')
plt.yticks(range(len(actions)), actions)
plt.title("First action chosen by algorithm per profile")
plt.legend()
plt.tight_layout()
plot_path = os.path.join(RESULTS_DIR, "experiment_first_actions.png")
plt.savefig(plot_path)
print("Saved", plot_path)

with open(os.path.join(RESULTS_DIR, "experiment_results.json"), "w") as f:
    json.dump(rows, f, indent=2)
print("Saved experiment JSON.")