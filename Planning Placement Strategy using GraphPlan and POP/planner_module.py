# planner_module.py
"""
Enhanced planning module:
- Domain builder with action effect probabilities and effort estimates
- GraphPlan (simple wrapper, level-based)
- POP (partial-order planner) with backtracking and threat-resolution (promotion/demotion)
- Temporal scheduling with resource constraint: max_parallel_actions_per_week (student capacity)
- Explainability: each action returns why/expected_benefit/risk using dataset estimates
"""

from collections import defaultdict, deque
import copy
import math

class Action:
    def __init__(self, name, preconds=None, adds=None, dels=None,
                 duration_weeks=1, effort_hours=None, effect_probs=None, kind="major"):
        """
        effect_probs: dict mapping add-effect -> probability (0..1) that action achieves that add.
        effort_hours: estimated person-hours required to perform the action (total, not per-week).
        kind: "major" or "minor" — used to enforce at-most-one-major-action per week constraint if desired.
        """
        self.name = name
        self.preconds = set(preconds or [])
        self.adds = set(adds or [])
        self.dels = set(dels or [])
        self.duration = duration_weeks
        self.effort_hours = effort_hours if effort_hours is not None else self.duration * 10
        self.effect_probs = effect_probs or {a: 1.0 for a in (adds or [])}
        self.kind = kind

    def __repr__(self):
        return f"Action({self.name})"

# ---------------- Domain ----------------
def build_domain(effect_estimates=None):
    """
    Build the domain. Optionally supply effect_estimates produced by dataset_skeleton.
    effect_estimates: dict of form {action_name: {'duration':float, 'effort_hours':float, 'probs':{add:prob}}}
    """
    ee = effect_estimates or {}
    def e(name, default_dur=1, default_effort=None, adds=None):
        p = ee.get(name, {})
        dur = p.get("duration", default_dur)
        effort = p.get("effort_hours", default_effort if default_effort is not None else dur*10)
        probs = p.get("probs", {a: 1.0 for a in (adds or [])})
        return dur, effort, probs

    actions = []

    dur, effort, probs = e("DSA_Practice_light", default_dur=1, adds=["DSA_MED"])
    actions.append(Action("DSA_Practice_light", preconds=["DSA_LOW"], adds=["DSA_MED","NOT_BURNOUT"],
                          dels=["DSA_LOW"], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="major"))

    dur, effort, probs = e("DSA_Practice_intense", default_dur=2, adds=["DSA_HIGH"])
    actions.append(Action("DSA_Practice_intense", preconds=["DSA_LOW"], adds=["DSA_HIGH","BURNOUT"],
                          dels=["DSA_LOW"], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="major"))

    dur, effort, probs = e("DSA_Keep_practice", default_dur=1, adds=["DSA_HIGH"])
    actions.append(Action("DSA_Keep_practice", preconds=["DSA_MED"], adds=["DSA_HIGH"],
                          dels=["DSA_MED"], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="major"))

    dur, effort, probs = e("DSA_Review", default_dur=1, adds=["DSA_MED"])
    actions.append(Action("DSA_Review", preconds=["DSA_MED"], adds=["DSA_MED"], dels=[],
                          duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="minor"))

    dur, effort, probs = e("ML_Practice", default_dur=1, adds=["ML_MED"])
    actions.append(Action("ML_Practice", preconds=["ML_LOW"], adds=["ML_MED"],
                          dels=["ML_LOW"], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="major"))

    dur, effort, probs = e("ML_Advance", default_dur=2, adds=["ML_HIGH"])
    actions.append(Action("ML_Advance", preconds=["ML_MED"], adds=["ML_HIGH"],
                          dels=["ML_MED"], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="major"))

    dur, effort, probs = e("Resume_Optimize_quick", default_dur=1, adds=["RESUME_MED"])
    actions.append(Action("Resume_Optimize_quick", preconds=["RESUME_LOW"], adds=["RESUME_MED"],
                          dels=["RESUME_LOW"], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="major"))

    dur, effort, probs = e("Resume_Optimize_deep", default_dur=1, adds=["RESUME_HIGH"])
    actions.append(Action("Resume_Optimize_deep", preconds=["RESUME_MED"], adds=["RESUME_HIGH"],
                          dels=["RESUME_MED"], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="major"))

    dur, effort, probs = e("MockInterview_easy", default_dur=1, adds=["CONF_MED"])
    actions.append(Action("MockInterview_easy", preconds=["RESUME_MED"], adds=["CONF_MED"],
                          dels=["NOT_BURNOUT"], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="major"))

    dur, effort, probs = e("MockInterview_full", default_dur=1, adds=["CONF_HIGH"])
    actions.append(Action("MockInterview_full", preconds=["RESUME_HIGH"], adds=["CONF_HIGH"],
                          dels=["BURNOUT"], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="major"))

    dur, effort, probs = e("Company_Research", default_dur=1, adds=["RESEARCH_DONE"])
    actions.append(Action("Company_Research", preconds=[], adds=["RESEARCH_DONE"],
                          dels=[], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="minor"))

    dur, effort, probs = e("Rest", default_dur=1, adds=["NOT_BURNOUT"])
    actions.append(Action("Rest", preconds=["BURNOUT"], adds=["NOT_BURNOUT"], dels=["BURNOUT"],
                          duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="minor"))

    dur, effort, probs = e("Encouragement", default_dur=0, adds=["CONF_MED"])
    actions.append(Action("Encouragement", preconds=[], adds=["CONF_MED"], dels=[], duration_weeks=dur, effort_hours=effort, effect_probs=probs, kind="minor"))

    return actions

# ---------------- GraphPlan (same simplified version) ----------------
def build_planning_graph(actions, init_state, max_levels=8):
    states_levels = [set(init_state)]
    actions_levels = []
    for lvl in range(max_levels):
        current_state = states_levels[-1]
        applicable_actions = set()
        for a in actions:
            if a.preconds.issubset(current_state):
                applicable_actions.add(a)
        # create noops to preserve literals
        noop_actions = set()
        for lit in current_state:
            noop = Action(f"Noop_pos({lit})", preconds=[lit], adds=[lit], dels=[], duration_weeks=0)
            noop_actions.add(noop)
        actions_levels.append(applicable_actions.union(noop_actions))
        next_state = set(current_state)
        for a in actions_levels[-1]:
            next_state |= set(a.adds)
            next_state -= set(a.dels)
        states_levels.append(next_state)
        if states_levels[-1] == states_levels[-2]:
            break
    return states_levels, actions_levels

def extract_plan_graphplan(states_levels, actions_levels, goals):
    plan_levels = [set() for _ in range(len(actions_levels))]
    current_goals = set(goals)
    for level in reversed(range(len(actions_levels))):
        actions_at_level = actions_levels[level]
        selected_actions = set()
        remaining_goals = set()
        for g in current_goals:
            found = False
            for a in actions_at_level:
                if g in a.adds:
                    selected_actions.add(a)
                    found = True
                    break
            if not found:
                remaining_goals.add(g)
        preconds = set()
        for a in selected_actions:
            preconds |= set(a.preconds)
        plan_levels[level] = selected_actions
        current_goals = preconds.union(remaining_goals)
    plan = []
    for lvl_actions in plan_levels:
        for a in lvl_actions:
            if not a.name.startswith("Noop"):
                plan.append(a)
    # dedupe keep order
    seen = set()
    dedup = []
    for a in plan:
        if a.name not in seen:
            dedup.append(a)
            seen.add(a.name)
    return dedup

def graphplan(actions, init_state, goals, max_levels=8):
    states_levels, actions_levels = build_planning_graph(actions, init_state, max_levels=max_levels)
    goal_level = None
    for i, s in enumerate(states_levels):
        if set(goals).issubset(s):
            goal_level = i
            break
    if goal_level is None:
        return None, states_levels, actions_levels
    plan = extract_plan_graphplan(states_levels[:goal_level+1], actions_levels[:goal_level], goals)
    return plan, states_levels, actions_levels

# ---------------- POP with backtracking ----------------
class POPPlan:
    def __init__(self):
        # actions contains Action objects (including START, FINISH)
        self.actions = []
        # orderings (u, v) meaning u before v
        self.orderings = set()
        # causal links (provider, predicate, consumer)
        self.causal_links = []

    def copy(self):
        p = POPPlan()
        p.actions = list(self.actions)
        p.orderings = set(self.orderings)
        p.causal_links = list(self.causal_links)
        return p

def topological_order_exists(orderings, actions):
    # check for cycle using Kahn
    adj = defaultdict(set)
    indeg = defaultdict(int)
    for a in actions:
        indeg[a] = 0
    for (u, v) in orderings:
        adj[u].add(v)
        indeg[v] += 1
    q = deque([a for a in actions if indeg[a] == 0])
    cnt = 0
    while q:
        n = q.popleft()
        cnt += 1
        for nb in adj[n]:
            indeg[nb] -= 1
            if indeg[nb] == 0:
                q.append(nb)
    return cnt == len(actions)

def provider_candidates(pred, plan, domain_actions, start):
    # providers are actions in plan (incl start) or domain actions
    candidates = []
    for a in plan.actions:
        if pred in a.adds:
            candidates.append(a)
    for a in domain_actions:
        if pred in a.adds and a not in plan.actions:
            candidates.append(a)
    # ensure start is included if it adds pred
    if pred in start.adds and start not in candidates:
        candidates.append(start)
    return candidates

def threatens(candidate, causal_link):
    provider, pred, consumer = causal_link
    # candidate threatens if it can delete pred and is not ordered before provider or after consumer
    if pred in candidate.dels:
        return True
    return False

def is_threat_resolved(candidate, causal_link, orderings):
    provider, pred, consumer = causal_link
    # threat resolved if candidate before provider or consumer before candidate
    if (candidate, provider) in orderings or (consumer, candidate) in orderings:
        return True
    return False

def add_ordering_and_check(plan, u, v):
    plan.orderings.add((u, v))
    if not topological_order_exists(plan.orderings, plan.actions):
        # undo and fail
        plan.orderings.remove((u, v))
        return False
    return True

def pop_backtrack_search(plan, domain_actions, start, finish, max_depth=2000, depth=0):
    """
    Improved recursive POP search with:
      - provider scoring that prefers providers with few unsatisfied preconds
      - immediate causal-links from START/existing actions when adding a provider
    """
    if depth > max_depth:
        return None

    # find open preconditions: for each action's precond, check if some causal link provides it
    open_agenda = []
    provided = set()
    for (prov, pred, cons) in plan.causal_links:
        provided.add((cons, pred))
    for a in plan.actions:
        if a.name in ("START",):
            continue
        for p in a.preconds:
            if (a, p) not in provided:
                open_agenda.append((a, p))
    if not open_agenda:
        # all preconds satisfied; return plan
        return plan

    # pick the precondition whose predicate has the fewest provider candidates (fail-fast)
    open_agenda.sort(key=lambda x: provider_count(x[1], plan, domain_actions, start))
    action_need, pred = open_agenda[0]

    providers = provider_candidates(pred, plan, domain_actions, start)

    # score providers:
    # prefer: in-plan providers (0) over new (1), fewer unsatisfied preconds (w.r.t START), shorter duration, higher prob
    def unsatisfied_preconds_count(p):
        # count preconds of p not already provided by START or present in plan.actions' adds
        cnt = 0
        for pr in p.preconds:
            if pr in start.adds:
                continue
            satisfied_by_plan = any((pr in q.adds) for q in plan.actions)
            if not satisfied_by_plan:
                cnt += 1
        return cnt

    def score_provider(p):
        prob = p.effect_probs.get(pred, 1.0)
        in_plan = 0 if p in plan.actions else 1
        unsat = unsatisfied_preconds_count(p)
        return (in_plan, unsat, p.duration, -prob)

    providers.sort(key=score_provider)

    for prov in providers:
        # branch: copy plan
        newplan = plan.copy()

        # add provider if not already in plan
        if prov not in newplan.actions:
            newplan.actions.append(prov)

        # immediately satisfy prov's preconds that are already available:
        #  - from START
        #  - from any existing action already in the plan (prefer the first such)
        for pr in list(prov.preconds):
            # if start already provides it, add causal link start->pr->prov
            if pr in start.adds:
                if (start, pr, prov) not in newplan.causal_links:
                    newplan.causal_links.append((start, pr, prov))
                    newplan.orderings.add((start, prov))
            else:
                # try to find a provider already in the plan
                provider_found = False
                for existing in newplan.actions:
                    if existing is prov:
                        continue
                    if pr in existing.adds:
                        if (existing, pr, prov) not in newplan.causal_links:
                            newplan.causal_links.append((existing, pr, prov))
                            newplan.orderings.add((existing, prov))
                        provider_found = True
                        break
                # if not found, leave it open (will be resolved by further recursion)
                if not provider_found:
                    pass

        # add causal link prov -> pred -> action_need (satisfy the original open precond)
        if (prov, pred, action_need) not in newplan.causal_links:
            newplan.causal_links.append((prov, pred, action_need))

        # add ordering prov before the consumer and finish, and start before prov
        newplan.orderings.add((prov, action_need))
        newplan.orderings.add((start, prov))
        newplan.orderings.add((prov, finish))

        # quick topo check
        if not topological_order_exists(newplan.orderings, newplan.actions):
            continue

        # detect threats: any action t that may delete pred and is unordered relative to the causal link
        threats = [t for t in newplan.actions if (pred in t.dels) and (t != prov) and (t != action_need)]

        # Resolve threats by promotion/demotion recursively
        def resolve_threats_rec(plan_obj, threats_list, idx=0):
            if idx >= len(threats_list):
                return True
            t = threats_list[idx]
            # if already ordered such that threat is resolved, skip
            if is_threat_resolved(t, (prov, pred, action_need), plan_obj.orderings):
                return resolve_threats_rec(plan_obj, threats_list, idx+1)
            # try demotion: t before prov
            clone1 = plan_obj.copy()
            clone1.orderings.add((t, prov))
            if topological_order_exists(clone1.orderings, clone1.actions):
                if resolve_threats_rec(clone1, threats_list, idx+1):
                    plan_obj.actions = clone1.actions
                    plan_obj.orderings = clone1.orderings
                    plan_obj.causal_links = clone1.causal_links
                    return True
            # try promotion: action_need before t
            clone2 = plan_obj.copy()
            clone2.orderings.add((action_need, t))
            if topological_order_exists(clone2.orderings, clone2.actions):
                if resolve_threats_rec(clone2, threats_list, idx+1):
                    plan_obj.actions = clone2.actions
                    plan_obj.orderings = clone2.orderings
                    plan_obj.causal_links = clone2.causal_links
                    return True
            return False

        if not resolve_threats_rec(newplan, threats, 0):
            continue

        # recursive attempt
        result = pop_backtrack_search(newplan, domain_actions, start, finish, max_depth, depth+1)
        if result is not None:
            return result

    # no provider worked -> failure
    return None


def provider_count(pred, plan, domain_actions, start):
    return len(provider_candidates(pred, plan, domain_actions, start))
def pop_plan(actions, init_state, goals,
             max_search_steps=5000,
             max_parallel_major_actions_per_week=1,
             max_hours_per_week=40):
    """
    POP with scheduling and GraphPlan fallback.
    - actions: domain actions (list of Action)
    - init_state: set of literals
    - goals: set of literals
    - max_parallel_major_actions_per_week: legacy constraint
    - max_hours_per_week: if not None, enforce hours-per-week capacity (uses effort_hours)
    Returns: scheduled list of dicts sorted by EST, or None if no plan found and no fallback possible.
    """

    # build START and FINISH sentinel actions
    start = Action("START", preconds=[], adds=list(init_state), dels=[], duration_weeks=0, effort_hours=0)
    finish = Action("FINISH", preconds=list(goals), adds=[], dels=[], duration_weeks=0, effort_hours=0)

    plan = POPPlan()
    plan.actions = [start, finish]
    plan.orderings = {(start, finish)}
    plan.causal_links = []

    domain_actions = list(actions)

    # initial search (backtracking POP)
    solved_plan = pop_backtrack_search(plan, domain_actions, start, finish, max_depth=max_search_steps)
    if solved_plan is None:
        # Fallback: try GraphPlan sequence -> convert to schedule
        print("POP search failed (no partial-order plan found). Attempting GraphPlan fallback...")
        try:
            gp_seq, states_levels, actions_levels = graphplan(domain_actions, set(init_state), set(goals))
        except Exception:
            gp_seq = None
        if not gp_seq:
            # no GraphPlan either -> hard failure
            print("GraphPlan also failed — no plan available.")
            return None
        # convert GraphPlan sequence into a simple scheduled plan (respecting hours/week)
        # We'll schedule actions sequentially in the GP sequence but still apply hours/week capacity and causal delays.
        # Build a map name->Action from domain_actions for lookup
        name_to_action = {a.name: a for a in domain_actions}
        # convert noop/unknowns by ignoring any action not in domain (GP might already use domain actions)
        seq = [a for a in gp_seq if a.name in name_to_action or a.name.startswith("Noop")]

        # helper: weeks range
        def weeks_range(s, d):
            return list(range(int(math.floor(s)), int(math.ceil(s + d))))
        # week load hours
        week_load_hours = defaultdict(float)
        scheduled = []
        current_time = 0
        for a in seq:
            if a.name.startswith("Noop"):
                continue
            # prefer the domain action instance (in case gp returned a distinct Action object)
            act = name_to_action.get(a.name, a)
            # ensure we start at least at current_time
            start_time = max(current_time, 0)
            # ensure providers (if any in sequence earlier) finish before action: since GP is a sequence, previous actions are providers
            # now apply hours/week constraint
            def per_week_hours_for_action(action, start_s):
                if action.duration <= 0:
                    return {}
                hours_per_week = action.effort_hours / action.duration
                weeks = weeks_range(start_s, action.duration)
                return {w: hours_per_week for w in weeks}
            # greedy shift until fits hours cap
            while True:
                per_week = per_week_hours_for_action(act, start_time)
                conflict = False
                for w, h in per_week.items():
                    if week_load_hours[w] + h > max_hours_per_week:
                        conflict = True
                        break
                if not conflict:
                    for w, h in per_week.items():
                        week_load_hours[w] += h
                    break
                start_time += 1
            scheduled.append({
                "name": act.name,
                "est": start_time,
                "duration": act.duration,
                "effort_hours": act.effort_hours,
                "preconds": list(act.preconds),
                "adds": list(act.adds),
                "why": explain_action_choice(act),
                "expected_benefit": expected_benefit(act),
                "risk": risk_estimate(act)
            })
            # advance current_time to reflect sequential execution (finish of this action)
            current_time = start_time + act.duration

        scheduled.sort(key=lambda x: x["est"])
        print("GraphPlan fallback produced a sequential schedule.")
        return scheduled

    # If POP solved, produce scheduled plan from partial-order solution
    solved = solved_plan

    # topologically order plan.actions consistent with orderings (Kahn)
    adj = defaultdict(set)
    indeg = defaultdict(int)
    for a in solved.actions:
        indeg[a] = 0
    for (u, v) in solved.orderings:
        adj[u].add(v)
        indeg[v] += 1
    q = deque([a for a in solved.actions if indeg[a] == 0])
    topo = []
    while q:
        n = q.popleft()
        topo.append(n)
        for nb in adj[n]:
            indeg[nb] -= 1
            if indeg[nb] == 0:
                q.append(nb)

    # compute earliest start times (EST) by orderings
    est = {a: 0 for a in topo}
    for a in topo:
        for nb in adj[a]:
            est_nb = est[a] + a.duration
            if est_nb > est[nb]:
                est[nb] = est_nb

    # Scheduling phase: hours-per-week or legacy parallel-major constraint
    def weeks_range(s, d):
        return list(range(int(math.floor(s)), int(math.ceil(s + d))))

    scheduled = []
    if max_hours_per_week is not None:
        week_load_hours = defaultdict(float)
        def per_week_hours_for_action(action, start_s):
            if action.duration <= 0:
                return {}
            hours_per_week = action.effort_hours / action.duration
            weeks = weeks_range(start_s, action.duration)
            return {w: hours_per_week for w in weeks}

        for a in topo:
            if a.name in ("START", "FINISH"):
                continue
            start_time = est.get(a, 0)
            # ensure providers finish before a starts
            for (prov, pred, cons) in solved.causal_links:
                if cons == a:
                    prov_finish = est.get(prov, 0) + prov.duration
                    if prov_finish > start_time:
                        start_time = prov_finish
            # greedy shift until fit into weekly hours capacity
            while True:
                per_week = per_week_hours_for_action(a, start_time)
                conflict = False
                for w, h in per_week.items():
                    if week_load_hours[w] + h > max_hours_per_week:
                        conflict = True
                        break
                if not conflict:
                    for w, h in per_week.items():
                        week_load_hours[w] += h
                    break
                start_time += 1

            scheduled.append({
                "name": a.name,
                "est": start_time,
                "duration": a.duration,
                "effort_hours": a.effort_hours,
                "preconds": list(a.preconds),
                "adds": list(a.adds),
                "why": explain_action_choice(a),
                "expected_benefit": expected_benefit(a),
                "risk": risk_estimate(a)
            })
    else:
        # legacy constraint
        week_load = defaultdict(int)
        for a in topo:
            if a.name in ("START", "FINISH"):
                continue
            start_time = est.get(a, 0)
            for (prov, pred, cons) in solved.causal_links:
                if cons == a:
                    prov_finish = est.get(prov, 0) + prov.duration
                    if prov_finish > start_time:
                        start_time = prov_finish
            if a.kind == "major":
                while True:
                    conflict = False
                    for w in weeks_range(start_time, a.duration):
                        if week_load[w] >= max_parallel_major_actions_per_week:
                            conflict = True
                            break
                    if not conflict:
                        break
                    start_time += 1
            for w in weeks_range(start_time, a.duration):
                if a.kind == "major":
                    week_load[w] += 1
            scheduled.append({
                "name": a.name,
                "est": start_time,
                "duration": a.duration,
                "effort_hours": a.effort_hours,
                "preconds": list(a.preconds),
                "adds": list(a.adds),
                "why": explain_action_choice(a),
                "expected_benefit": expected_benefit(a),
                "risk": risk_estimate(a)
            })

    scheduled.sort(key=lambda x: x["est"])
    return scheduled




# ---------------- Explainability helpers ----------------
def explain_action_choice(action):
    # short reason template
    if action.name.startswith("DSA"):
        return "Improves algorithmic problem-solving skill (DSA)."
    if action.name.startswith("Resume"):
        return "Improves resume quality to pass recruiter screen."
    if action.name.startswith("MockInterview"):
        return "Simulates interview to increase confidence and reveal weaknesses."
    if action == None:
        return ""
    return f"Action {action.name} chosen to satisfy preconditions and progress toward goals."

def expected_benefit(action):
    # aggregate expected benefit (sum of probs for adds)
    total = 0.0
    for a in action.adds:
        p = action.effect_probs.get(a, 1.0)
        total += p
    return {"sum_prob": total, "adds": {a: action.effect_probs.get(a, 1.0) for a in action.adds}}

def risk_estimate(action):
    # simple risk: if action adds BURNOUT or has high effort_hours, risk = higher
    r = 0.0
    if "BURNOUT" in action.adds or action.effort_hours > 40:
        r = 0.6
    elif action.duration >= 2:
        r = 0.3
    else:
        r = 0.05
    return {"burnout_risk_est": r}

# ---------------- Plan repair (incremental replanning) ----------------
def apply_executed_actions_to_state(init_state, executed_actions, domain_actions):
    """
    executed_actions: list of dicts {name, status} where status in {"done","failed","skipped"}
    Return new_state after applying effects of done actions (failed/skipped do not add effects).
    We'll assume 'done' actions' adds apply, and failed actions may add del effects of themselves (not ideal but acceptable).
    """
    state = set(init_state)
    name_to_action = {a.name: a for a in domain_actions}
    for e in executed_actions:
        a_name = e.get("name")
        status = e.get("status", "done")
        a = name_to_action.get(a_name)
        if not a:
            continue
        if status == "done":
            state -= set(a.dels)
            state |= set(a.adds)
        elif status == "failed":
            # apply no adds; optionally add some negative effect like decreased confidence
            if "CONF_HIGH" in a.adds:
                # failing a mock interview might reduce CONF_MED if present; but keep stable for now
                pass
    return state

# ---------------- Convenience wrapper for API ----------------
def plan_pop_with_repair(init_state, goals, domain_actions=None, executed_actions=None,
                         max_parallel_major_actions_per_week=1, effect_estimates=None):
    domain_actions = domain_actions or build_domain(effect_estimates)
    # if executed actions provided, update state
    if executed_actions:
        init_state = apply_executed_actions_to_state(init_state, executed_actions, domain_actions)
    schedule = pop_plan(domain_actions, init_state, goals, max_parallel_major_actions_per_week=max_parallel_major_actions_per_week)
    return schedule

# End of planner_module.py



# ---------------------------------------------------------------------
# Tracing helpers for GraphPlan and POP (append to planner_module.py)
# ---------------------------------------------------------------------

import json
import time

# ---- GraphPlan trace ----
def extract_plan_graphplan_trace(states_levels, actions_levels, goals):
    """
    Similar to extract_plan_graphplan but also records the selection trace:
    - for each backward level, which actions were chosen to satisfy which goal
    Returns (plan_list, trace_steps)
    """
    trace = []
    plan_levels = [set() for _ in range(len(actions_levels))]
    current_goals = set(goals)

    trace.append({"type": "start_extraction", "desc": f"Goals to achieve: {sorted(list(current_goals))}"})

    for level in reversed(range(len(actions_levels))):
        actions_at_level = actions_levels[level]
        selected_actions = set()
        remaining_goals = set()
        trace.append({"type": "level", "level": level, "avail_actions": [a.name for a in actions_at_level],
                      "desc": f"At planning graph level {level}, trying to support goals {sorted(list(current_goals))}"})
        for g in current_goals:
            found = False
            for a in actions_at_level:
                if g in a.adds:
                    selected_actions.add(a)
                    trace.append({"type": "select_provider", "goal": g, "action": a.name,
                                  "preconds": list(a.preconds), "adds": list(a.adds),
                                  "desc": f"Chose action {a.name} at level {level} to supply goal {g}"})
                    found = True
                    break
            if not found:
                remaining_goals.add(g)
                trace.append({"type": "unsatisfied_goal", "goal": g,
                              "desc": f"Goal {g} not provided at this level -> carry back to earlier level"})
        preconds = set()
        for a in selected_actions:
            preconds |= set(a.preconds)
        plan_levels[level] = selected_actions
        current_goals = preconds.union(remaining_goals)

    # build final plan (order by level low->high)
    plan = []
    for lvl_actions in plan_levels:
        for a in lvl_actions:
            if not a.name.startswith("Noop"):
                plan.append(a)
    # dedupe keep order
    seen = set()
    dedup = []
    for a in plan:
        if a.name not in seen:
            dedup.append(a)
            seen.add(a.name)

    trace.append({"type": "finished_extraction", "desc": f"Extracted plan of {len(dedup)} actions",
                  "plan": [a.name for a in dedup]})
    return dedup, trace

def graphplan_trace(actions, init_state, goals, max_levels=8):
    """
    Returns:
      - plan (or None)
      - trace: list of chronological trace steps useful for visualization
      - states_levels, actions_levels (raw)
    """
    # build graph
    states_levels, actions_levels = build_planning_graph(actions, init_state, max_levels=max_levels)
    trace = []
    trace.append({"type": "graph_build_start", "desc": "Start building planning graph",
                  "init_state": sorted(list(states_levels[0]))})
    for i, (s, a_lvl) in enumerate(zip(states_levels, actions_levels)):
        trace.append({
            "type": "level_built",
            "level": i,
            "state_literals": sorted(list(states_levels[i])),
            "applicable_actions": sorted([a.name for a in actions_levels[i]])
        })
    # find first level where goals are included
    goal_level = None
    for i, s in enumerate(states_levels):
        if set(goals).issubset(s):
            goal_level = i
            trace.append({"type": "goals_reached", "level": i, "desc": f"goals are available at level {i}"})
            break
    if goal_level is None:
        trace.append({"type": "fail", "desc": "Goals not reachable in planning graph"})
        return None, trace, states_levels, actions_levels

    plan, extract_trace = extract_plan_graphplan_trace(states_levels[:goal_level+1], actions_levels[:goal_level], goals)
    trace.extend(extract_trace)
    return plan, trace, states_levels, actions_levels


# ---- POP trace ----
def pop_backtrack_search_with_trace(plan, domain_actions, start, finish, max_depth=2000, depth=0, trace=None):
    """
    POP search instrumented with trace logging. Returns (plan_or_None, trace)
    """
    if trace is None:
        trace = []
    if depth > max_depth:
        trace.append({"type": "abort", "desc": f"Exceeded max depth {max_depth}", "depth": depth})
        return None, trace

    # find open preconditions
    open_agenda = []
    provided = set()
    for (prov, pred, cons) in plan.causal_links:
        provided.add((cons, pred))
    for a in plan.actions:
        if a.name in ("START",):
            continue
        for p in a.preconds:
            if (a, p) not in provided:
                open_agenda.append((a, p))

    trace.append({"type": "open_agenda", "items": [(x[0].name, x[1]) for x in open_agenda], "depth": depth})

    if not open_agenda:
        trace.append({"type": "plan_complete", "desc": "All preconditions satisfied", "actions": [a.name for a in plan.actions]})
        return plan, trace

    # heuristic pick smallest provider_count
    open_agenda.sort(key=lambda x: provider_count(x[1], plan, domain_actions, start))
    action_need, pred = open_agenda[0]
    trace.append({"type": "pick_open", "action": action_need.name, "pred": pred, "depth": depth,
                  "provider_count": provider_count(pred, plan, domain_actions, start)})

    providers = provider_candidates(pred, plan, domain_actions, start)
    # order providers heuristically
    def score_provider(p):
        prob = p.effect_probs.get(pred, 1.0)
        in_plan = 0 if p in plan.actions else 1
        return (in_plan, p.duration, -prob)
    providers_sorted = sorted(providers, key=score_provider)
    trace.append({"type": "providers", "pred": pred, "providers": [p.name for p in providers_sorted]})

    for prov in providers_sorted:
        trace.append({"type": "try_provider", "provider": prov.name, "pred": pred, "for_action": action_need.name, "depth": depth})
        newplan = plan.copy()
        if prov not in newplan.actions:
            newplan.actions.append(prov)
            trace.append({"type": "added_action", "action": prov.name, "depth": depth})
        newplan.causal_links.append((prov, pred, action_need))
        newplan.orderings.add((prov, action_need))
        newplan.orderings.add((start, prov))
        newplan.orderings.add((prov, finish))
        if not topological_order_exists(newplan.orderings, newplan.actions):
            trace.append({"type": "ordering_inconsistent", "desc": f"Adding ordering for {prov.name}->{action_need.name} created cycle", "depth": depth})
            continue

        # check threats
        threats = [t for t in newplan.actions if (pred in t.dels) and (t != prov) and (t != action_need)]
        if threats:
            trace.append({"type": "threats_detected", "pred": pred, "threats": [t.name for t in threats], "depth": depth})
        resolved_ok = True

        def resolve_threats_rec(plan_obj, threats_list, idx=0):
            if idx >= len(threats_list):
                return True
            t = threats_list[idx]
            # already resolved?
            if is_threat_resolved(t, (prov, pred, action_need), plan_obj.orderings):
                trace.append({"type": "threat_already_resolved", "threat": t.name, "depth": depth})
                return resolve_threats_rec(plan_obj, threats_list, idx+1)
            # demotion
            clone1 = plan_obj.copy()
            clone1.orderings.add((t, prov))
            trace.append({"type": "try_demotion", "threat": t.name, "demote_before": prov.name, "depth": depth})
            if topological_order_exists(clone1.orderings, clone1.actions):
                if resolve_threats_rec(clone1, threats_list, idx+1):
                    plan_obj.actions = clone1.actions
                    plan_obj.orderings = clone1.orderings
                    plan_obj.causal_links = clone1.causal_links
                    trace.append({"type": "demotion_success", "threat": t.name, "depth": depth})
                    return True
            # promotion
            clone2 = plan_obj.copy()
            clone2.orderings.add((action_need, t))
            trace.append({"type": "try_promotion", "threat": t.name, "promote_after": action_need.name, "depth": depth})
            if topological_order_exists(clone2.orderings, clone2.actions):
                if resolve_threats_rec(clone2, threats_list, idx+1):
                    plan_obj.actions = clone2.actions
                    plan_obj.orderings = clone2.orderings
                    plan_obj.causal_links = clone2.causal_links
                    trace.append({"type": "promotion_success", "threat": t.name, "depth": depth})
                    return True
            trace.append({"type": "resolution_failed_for_threat", "threat": t.name, "depth": depth})
            return False

        if not resolve_threats_rec(newplan, threats, 0):
            resolved_ok = False

        if not resolved_ok:
            trace.append({"type": "provider_failed_due_to_threats", "provider": prov.name, "depth": depth})
            continue

        # recursive
        result, trace = pop_backtrack_search_with_trace(newplan, domain_actions, start, finish, max_depth, depth+1, trace)
        if result is not None:
            return result, trace
        trace.append({"type": "backtrack_provider", "provider": prov.name, "for": f"{action_need.name}:{pred}", "depth": depth})

    trace.append({"type": "fail_open_precondition", "action": action_need.name, "pred": pred, "depth": depth})
    return None, trace


def pop_trace(actions, init_state, goals, max_search_steps=5000, max_hours_per_week=40):
    """
    Runs POP search with trace. Returns:
      - scheduled (if plan found) or None
      - trace: list of steps describing the search + scheduling steps
    """
    start = Action("START", preconds=[], adds=list(init_state), dels=[], duration_weeks=0, effort_hours=0)
    finish = Action("FINISH", preconds=list(goals), adds=[], dels=[], duration_weeks=0, effort_hours=0)

    plan = POPPlan()
    plan.actions = [start, finish]
    plan.orderings = {(start, finish)}
    plan.causal_links = []

    trace = [{"type": "pop_start", "desc": "Starting POP search", "init_state": sorted(list(init_state)), "goals": sorted(list(goals))}]
    domain_actions = list(actions)

    solved_plan, trace = pop_backtrack_search_with_trace(plan, domain_actions, start, finish, max_depth=max_search_steps, depth=0, trace=trace)
    if solved_plan is None:
        trace.append({"type": "pop_failed", "desc": "POP failed to find partial-order plan"})
        # fallback to graphplan sequence (we will still return trace)
        gp_plan, gp_trace, _, _ = graphplan_trace(domain_actions, set(init_state), set(goals))
        trace.append({"type": "graphplan_fallback", "desc": "Attempting GraphPlan fallback", "gp_trace": gp_trace})
        # produce sequential schedule from graphplan (reuse earlier fallback scheduling)
        if gp_plan:
            # simple scheduling - sequential respecting hours/week
            week_load_hours = defaultdict(float)
            scheduled = []
            current_time = 0
            for a in gp_plan:
                start_time = current_time
                def per_week_hours_for_action(action, start_s):
                    if action.duration <= 0:
                        return {}
                    hours_per_week = action.effort_hours / action.duration
                    weeks = list(range(int(math.floor(start_s)), int(math.ceil(start_s + action.duration))))
                    return {w: hours_per_week for w in weeks}
                while True:
                    per_week = per_week_hours_for_action(a, start_time)
                    conflict = False
                    for w, h in per_week.items():
                        if week_load_hours[w] + h > max_hours_per_week:
                            conflict = True
                            break
                    if not conflict:
                        for w, h in per_week.items():
                            week_load_hours[w] += h
                        break
                    start_time += 1
                scheduled.append({"name": a.name, "est": start_time, "duration": a.duration, "effort_hours": a.effort_hours, "preconds": list(a.preconds), "adds": list(a.adds)})
                current_time = start_time + a.duration
            trace.append({"type": "fallback_schedule_created", "desc": "Sequential schedule from GraphPlan fallback"})
            return scheduled, trace

        return None, trace

    # solved_plan -> produce topo order and schedule (same as pop_plan scheduling)
    solved = solved_plan

    # topological order (Kahn)
    adj = defaultdict(set)
    indeg = defaultdict(int)
    for a in solved.actions:
        indeg[a] = 0
    for (u, v) in solved.orderings:
        adj[u].add(v)
        indeg[v] += 1
    q = deque([a for a in solved.actions if indeg[a] == 0])
    topo = []
    while q:
        n = q.popleft()
        topo.append(n)
        for nb in adj[n]:
            indeg[nb] -= 1
            if indeg[nb] == 0:
                q.append(nb)

    trace.append({"type": "partial_order_solution", "actions": [a.name for a in topo]})

    # compute ESTs
    est = {a: 0 for a in topo}
    for a in topo:
        for nb in adj[a]:
            est_nb = est[a] + a.duration
            if est_nb > est[nb]:
                est[nb] = est_nb

    # scheduling with hours per week
    week_load_hours = defaultdict(float)
    scheduled = []
    def per_week_hours_for_action(action, start_s):
        if action.duration <= 0:
            return {}
        hours_per_week = action.effort_hours / action.duration
        weeks = list(range(int(math.floor(start_s)), int(math.ceil(start_s + action.duration))))
        return {w: hours_per_week for w in weeks}

    for a in topo:
        if a.name in ("START", "FINISH"):
            continue
        start_time = est.get(a, 0)
        for (prov, pred, cons) in solved.causal_links:
            if cons == a:
                prov_finish = est.get(prov, 0) + prov.duration
                if prov_finish > start_time:
                    start_time = prov_finish
        # greedy shift to satisfy weekly hours
        while True:
            per_week = per_week_hours_for_action(a, start_time)
            conflict = False
            for w, h in per_week.items():
                if week_load_hours[w] + h > max_hours_per_week:
                    conflict = True
                    break
            if not conflict:
                for w, h in per_week.items():
                    week_load_hours[w] += h
                break
            start_time += 1
        scheduled.append({"name": a.name, "est": start_time, "duration": a.duration, "effort_hours": a.effort_hours, "preconds": list(a.preconds), "adds": list(a.adds)})

    scheduled.sort(key=lambda x: x["est"])
    trace.append({"type": "schedule_created", "desc": "POP schedule created", "scheduled_count": len(scheduled)})
    return scheduled, trace
