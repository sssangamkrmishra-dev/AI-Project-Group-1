# dataset_skeleton.py
"""
Simplified dataset skeleton (no resume_scores special-case).
- Place your data files into data/
  - data/leetcode.csv             (optional)
  - data/mock_interviews.json    (optional) or data/mock_interviews.csv
  - other CSVs: 05_person_skills.csv, 06_skills.csv, 04_experience.csv, etc. (optional)
- Run: python dataset_skeleton.py
- Output: estimates.json (used by planner_module.build_domain(effect_estimates=...))
"""

import pandas as pd
import json
from pathlib import Path
import statistics

DATA_DIR = Path("data")
OUT_FILE = Path("estimates.json")

def load_leetcode_csv(path: Path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    # ensure an 'avg_time_hours' numeric column exists (fallback from difficulty)
    def difficulty_to_hours(d):
        d = str(d).strip().lower()
        if d == "easy":
            return 6.0
        if d == "medium":
            return 20.0
        if d == "hard":
            return 45.0
        return 15.0
    if 'avg_time_hours' not in df.columns:
        if 'difficulty' in df.columns:
            df['avg_time_hours'] = df['difficulty'].apply(difficulty_to_hours)
        else:
            df['avg_time_hours'] = 20.0
    # coerce numeric
    df['avg_time_hours'] = pd.to_numeric(df['avg_time_hours'], errors='coerce').fillna(20.0)
    return df

def estimate_dsa_effect_from_leetcode(df):
    avg_hours = float(df['avg_time_hours'].mean()) if (df is not None and not df.empty) else 20.0
    light_weeks = max(1.0, avg_hours / 10.0)
    intense_weeks = max(1.0, avg_hours / 25.0)
    return {
        "DSA_Practice_light": {"duration": light_weeks, "effort_hours": light_weeks * 10.0, "probs": {"DSA_MED": 0.6, "NOT_BURNOUT": 0.95}},
        "DSA_Practice_intense": {"duration": intense_weeks, "effort_hours": intense_weeks * 25.0, "probs": {"DSA_HIGH": 0.85, "BURNOUT": 0.3}},
        "DSA_Keep_practice": {"duration": 1.0, "effort_hours": 12.0, "probs": {"DSA_HIGH": 0.7}},
        "DSA_Review": {"duration": 1.0, "effort_hours": 6.0, "probs": {"DSA_MED": 0.5}}
    }

def load_mock_interviews_json(path: Path):
    data = json.loads(path.read_text(encoding='utf-8'))
    questions = data.get('questions') if isinstance(data, dict) and 'questions' in data else data
    df = pd.DataFrame(questions)
    return df

def estimate_mock_effects(df_mock):
    count = len(df_mock) if df_mock is not None else 0
    base = min(0.9, 0.6 + min(0.3, count / 500.0))
    return {
        "MockInterview_easy": {"duration": 1.0, "effort_hours": 3.0, "probs": {"CONF_MED": base}},
        "MockInterview_full": {"duration": 1.0, "effort_hours": 5.0, "probs": {"CONF_HIGH": min(0.95, base + 0.15)}}
    }

def aggregate_resume_related(data_dir: Path):
    """
    Scan CSV files with names indicating resume/skill/experience, and look for numeric columns
    with names containing 'hour','time','effort' to estimate typical effort.
    Returns default resume estimates if none found.
    """
    candidates = []
    for p in data_dir.glob("*.csv"):
        name = p.name.lower()
        if any(k in name for k in ("resume","skill","skills","experience","person","ability","abilities")):
            try:
                df = pd.read_csv(p)
                candidates.append((p.name, df))
            except Exception:
                continue
    # search for plausible numeric columns
    hours_values = []
    for name, df in candidates:
        for col in df.columns:
            low = col.lower()
            if any(k in low for k in ("hour","time","effort")):
                try:
                    vals = pd.to_numeric(df[col], errors='coerce').dropna().tolist()
                    hours_values.extend([float(v) for v in vals if v > 0])
                except Exception:
                    continue
    if hours_values:
        avg = float(sum(hours_values) / len(hours_values))
        quick = max(1.0, avg * 0.5 / 10.0)  # weeks-ish heuristic
        deep = max(1.0, avg / 10.0)
        return {
            "Resume_Optimize_quick": {"duration": quick, "effort_hours": max(4.0, avg * 0.5), "probs": {"RESUME_MED": min(0.95, 0.5 + avg/80.0)}},
            "Resume_Optimize_deep": {"duration": deep, "effort_hours": max(10.0, avg), "probs": {"RESUME_HIGH": min(0.99, 0.7 + avg/80.0)}}
        }
    # fallback defaults
    return {
        "Resume_Optimize_quick": {"duration": 1.0, "effort_hours": 8.0, "probs": {"RESUME_MED": 0.7}},
        "Resume_Optimize_deep": {"duration": 1.0, "effort_hours": 20.0, "probs": {"RESUME_HIGH": 0.9}}
    }

def run_all_and_save(data_folder='data', out='estimates.json'):
    data_folder = Path(data_folder)
    estimates = {}

    # LeetCode
    leet = data_folder / 'leetcode.csv'
    if leet.exists():
        try:
            df_leet = load_leetcode_csv(leet)
            estimates.update(estimate_dsa_effect_from_leetcode(df_leet))
        except Exception as e:
            print("Failed to parse leetcode.csv:", e)
    else:
        estimates.update({
            "DSA_Practice_light": {"duration": 1.0, "effort_hours": 10.0, "probs": {"DSA_MED": 0.6, "NOT_BURNOUT": 0.95}},
            "DSA_Practice_intense": {"duration": 2.0, "effort_hours": 40.0, "probs": {"DSA_HIGH": 0.85, "BURNOUT": 0.3}},
            "DSA_Keep_practice": {"duration": 1.0, "effort_hours": 12.0, "probs": {"DSA_HIGH": 0.7}},
            "DSA_Review": {"duration": 1.0, "effort_hours": 6.0, "probs": {"DSA_MED": 0.5}}
        })

    # Mock interviews
    mock_json = data_folder / 'mock_interviews.json'
    mock_csv = data_folder / 'mock_interviews.csv'
    if mock_json.exists():
        try:
            df_mock = load_mock_interviews_json(mock_json)
            estimates.update(estimate_mock_effects(df_mock))
        except Exception as e:
            print("Failed to parse mock_interviews.json:", e)
    elif mock_csv.exists():
        try:
            df_mock = pd.read_csv(mock_csv)
            estimates.update(estimate_mock_effects(df_mock))
        except Exception as e:
            print("Failed to parse mock_interviews.csv:", e)
    else:
        estimates.update({
            "MockInterview_easy": {"duration": 1.0, "effort_hours": 3.0, "probs": {"CONF_MED": 0.6}},
            "MockInterview_full": {"duration": 1.0, "effort_hours": 5.0, "probs": {"CONF_HIGH": 0.75}}
        })

    # Resume-related aggregation (no special resume_scores.csv)
    resume_est = aggregate_resume_related(data_folder)
    estimates.update(resume_est)

    # Save
    Path(out).write_text(json.dumps(estimates, indent=2))
    print(f"Saved estimates to {out}")

if __name__ == "__main__":
    run_all_and_save()
