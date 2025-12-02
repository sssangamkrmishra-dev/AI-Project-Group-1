# generate_report.py
"""
Generate a simple markdown report summarizing results in results/ and convert to PDF using pandoc (optional).
"""
import os, json, textwrap, subprocess
RESULTS = "results"
summary_path = os.path.join(RESULTS, "experiment_results.json")
if not os.path.exists(summary_path):
    print("Run experiments.py first to produce results.")
    exit(0)

with open(summary_path) as f:
    rows = json.load(f)

md = ["# Module 2 - Experiment Summary\n"]
for r in rows:
    md.append(f"## Profile: {r['profile']}")
    md.append(f"- Start readiness: {r['start_readiness']}")
    md.append(f"- UCS first action: {r['ucs_first']} (cost: {r['ucs_cost']})")
    md.append(f"- A* first action: {r['astar_first']} (cost: {r['astar_cost']})")
    md.append(f"- BFS first action: {r.get('bfs_first')} (cost: {r.get('bfs_cost')})")
    md.append("")

out_md = os.path.join(RESULTS, "summary.md")
with open(out_md, "w") as f:
    f.write("\n".join(md))
print("Saved", out_md)
# Convert to PDF if pandoc available:
try:
    subprocess.run(["pandoc", out_md, "-o", os.path.join(RESULTS,"summary.pdf")], check=True)
    print("Generated PDF (results/summary.pdf)")
except Exception:
    print("pandoc not available or conversion failed; kept markdown only.")