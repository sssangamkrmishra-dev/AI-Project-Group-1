# tests/test_searches.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))  # ensure project root on path

from module2_core import readiness, transition, uniform_cost_search, a_star_search

def test_readiness_increases_after_action():
    state = {"DSA":0.5,"SystemDesign":0.5,"Resume":0.5,"HR":0.5}
    weights = {"DSA":0.4,"SystemDesign":0.25,"Resume":0.2,"HR":0.15}
    r1 = readiness(state, weights, 0.1)
    ns, nb, _ = transition(state, 0.1, "Quick Revision")
    r2 = readiness(ns, weights, nb)
    assert r2 >= r1

def test_searches_find_plans():
    state = {"DSA":0.6,"SystemDesign":0.3,"Resume":0.4,"HR":0.5}
    weights = {"DSA":0.4,"SystemDesign":0.25,"Resume":0.2,"HR":0.15}
    u = uniform_cost_search(state, 0.2, weights)
    a = a_star_search(state, 0.2, weights)
    assert u is not None
    assert a is not None