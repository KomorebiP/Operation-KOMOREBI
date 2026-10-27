#!/usr/bin/env python3
"""Independent exact-rational regression for AVOC v0.38 robust quotes.

The oracle below reimplements the finite staged controller with Fraction arithmetic.
It does not call Lean for its Bellman or interval calculations.  Lean is invoked only
through the public JSON endpoint and the results are compared.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import random
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "tools/run_robust_quote.py"
RESULT = ROOT / "results/v0.38.0/robust_quote_regression.json"
REQUEST_DIR = ROOT / "results/v0.38.0/robust_quote_requests"

ACTIONS = ("stop", "inspect_warm", "generate_cold", "deploy_warm", "deploy_cold")


def frac_wire(q: Fraction) -> list[int]:
    return [q.numerator, q.denominator]


def F(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, list) and len(value) == 2:
        return Fraction(int(value[0]), int(value[1]))
    raise TypeError(f"not an exact rational: {value!r}")


def status_state(warm: str, cold: str, budget: int, spent: int = 0,
                 total: int | None = None, done: bool = False) -> tuple:
    return (warm, cold, budget, spent, budget + spent if total is None else total, done)


@dataclass(frozen=True)
class Quote:
    setup_lo: int
    setup_hi: int
    gross_lo: Fraction
    gross_hi: Fraction
    prob_lo: Fraction
    prob_hi: Fraction

    @property
    def setup_width(self) -> Fraction:
        return Fraction(self.setup_hi - self.setup_lo)

    @property
    def gross_width(self) -> Fraction:
        return self.gross_hi - self.gross_lo

    @property
    def prob_width(self) -> Fraction:
        return self.prob_hi - self.prob_lo


@dataclass(frozen=True)
class Params:
    warm: Quote
    cold: Quote


@dataclass(frozen=True)
class ExactParams:
    warm_setup: int
    cold_setup: int
    warm_gross: Fraction
    cold_gross: Fraction
    warm_prob: Fraction
    cold_prob: Fraction


def parse_quote(wire: list) -> Quote:
    return Quote(int(wire[1][0]), int(wire[1][1]), F(wire[2][0]), F(wire[2][1]),
                 F(wire[3][0]), F(wire[3][1]))


def action_list(params: Params, state: tuple) -> list[str]:
    warm, cold, budget, _spent, _total, done = state
    if done:
        return ["stop"]
    out = ["stop"]
    if warm == "untried" and params.warm.setup_hi <= budget:
        out.append("inspect_warm")
    if cold == "untried" and params.cold.setup_hi <= budget:
        out.append("generate_cold")
    if warm == "ready":
        out.append("deploy_warm")
    if cold == "ready":
        out.append("deploy_cold")
    return out


def step(params: Params, state: tuple, action: str, success: bool) -> tuple:
    warm, cold, budget, spent, total, done = state
    if action in ("stop", "deploy_warm", "deploy_cold"):
        return (warm, cold, budget, spent, total, True)
    if action == "inspect_warm":
        fee = params.warm.setup_hi
        return ("ready" if success else "failed", cold,
                budget - fee, spent + fee, total, done)
    if action == "generate_cold":
        fee = params.cold.setup_hi
        return (warm, "ready" if success else "failed",
                budget - fee, spent + fee, total, done)
    raise ValueError(action)


def nominal_reward(params: Params, action: str) -> Fraction:
    if action == "stop": return Fraction(0)
    if action == "inspect_warm": return Fraction(-params.warm.setup_hi)
    if action == "generate_cold": return Fraction(-params.cold.setup_hi)
    if action == "deploy_warm": return params.warm.gross_lo
    if action == "deploy_cold": return params.cold.gross_lo
    raise ValueError(action)


def nominal_prob(params: Params, action: str) -> Fraction:
    if action == "inspect_warm": return params.warm.prob_lo
    if action == "generate_cold": return params.cold.prob_lo
    return Fraction(0)


def true_reward(exact: ExactParams, action: str) -> Fraction:
    if action == "stop": return Fraction(0)
    if action == "inspect_warm": return Fraction(-exact.warm_setup)
    if action == "generate_cold": return Fraction(-exact.cold_setup)
    if action == "deploy_warm": return exact.warm_gross
    if action == "deploy_cold": return exact.cold_gross
    raise ValueError(action)


def true_prob(exact: ExactParams, action: str) -> Fraction:
    if action == "inspect_warm": return exact.warm_prob
    if action == "generate_cold": return exact.cold_prob
    return Fraction(0)


def dp(params: Params, horizon: int, state: tuple, exact: ExactParams | None = None):
    @lru_cache(maxsize=None)
    def rec(h: int, s: tuple) -> tuple[Fraction, str | None]:
        if h == 0:
            return Fraction(0), None
        rows: list[tuple[str, Fraction]] = []
        for a in action_list(params, s):
            reward = nominal_reward(params, a) if exact is None else true_reward(exact, a)
            p = nominal_prob(params, a) if exact is None else true_prob(exact, a)
            v0 = rec(h - 1, step(params, s, a, False))[0]
            v1 = rec(h - 1, step(params, s, a, True))[0]
            rows.append((a, reward + (1-p)*v0 + p*v1))
        # Stable first winner, matching ExecutablePlanner.best.
        best_a, best_v = rows[0]
        for a, v in rows[1:]:
            if v > best_v:
                best_a, best_v = a, v
        return best_v, best_a

    def q(h_cont: int, s: tuple, a: str) -> Fraction:
        reward = nominal_reward(params, a) if exact is None else true_reward(exact, a)
        p = nominal_prob(params, a) if exact is None else true_prob(exact, a)
        return reward + (1-p)*rec(h_cont, step(params, s, a, False))[0] + \
            p*rec(h_cont, step(params, s, a, True))[0]

    value, choice = rec(horizon, state)
    return value, choice, q


def radii(params: Params):
    eps = params.warm.setup_width + params.cold.setup_width + \
          params.warm.gross_width + params.cold.gross_width
    delta = 2*(params.warm.prob_width + params.cold.prob_width)
    envelope = Fraction(params.warm.setup_hi + params.cold.setup_hi) + \
               params.warm.gross_hi + params.cold.gross_hi

    def value_radius(h: int) -> Fraction:
        return sum((eps + delta*Fraction(k)*envelope for k in range(h)), Fraction(0))

    def reward_radius(a: str) -> Fraction:
        return {
            "stop": Fraction(0),
            "inspect_warm": params.warm.setup_width,
            "generate_cold": params.cold.setup_width,
            "deploy_warm": params.warm.gross_width,
            "deploy_cold": params.cold.gross_width,
        }[a]

    def prob_radius(a: str) -> Fraction:
        if a == "inspect_warm": return 2*params.warm.prob_width
        if a == "generate_cold": return 2*params.cold.prob_width
        return Fraction(0)

    def local(h: int, a: str) -> Fraction:
        return value_radius(h) + reward_radius(a) + prob_radius(a)*Fraction(h)*envelope

    def global_q(h: int) -> Fraction:
        return value_radius(h) + eps + delta*Fraction(h)*envelope

    return value_radius, local, global_q


def robust_oracle(params: Params, state: tuple, h_cont: int) -> dict[str, Any]:
    value, nominal_choice, q = dp(params, h_cont + 1, state)
    value_radius, local, global_q = radii(params)
    actions = action_list(params, state)
    rows = []
    robust_choice = actions[0]
    robust_low = None
    for a in actions:
        nq = q(h_cont, state, a)
        rr = local(h_cont, a)
        lo, hi = nq - rr, nq + rr
        if robust_low is None or lo > robust_low:
            robust_choice, robust_low = a, lo
        rows.append({"action": a, "nominal_q": nq, "radius": rr,
                     "lower_q": lo, "upper_q": hi})
    for row in rows:
        row["certified_dominance"] = all(
            other["upper_q"] <= row["lower_q"] for other in rows)
    total_h = h_cont + 1
    vr = value_radius(total_h)
    whole = sum((2*global_q(k) for k in range(total_h)), Fraction(0))
    return {
        "robust_choice": robust_choice,
        "nominal_choice": nominal_choice,
        "nominal_value": value,
        "lower_value": value-vr,
        "upper_value": value+vr,
        "local_regret_bound": 2*global_q(h_cont),
        "whole_policy_regret_bound": whole,
        "exact_bands": all(x == 0 for x in (
            params.warm.setup_width, params.cold.setup_width,
            params.warm.gross_width, params.cold.gross_width,
            params.warm.prob_width, params.cold.prob_width)),
        "actions": rows,
    }


def parse_plan_request(req: list) -> tuple[Params, tuple, int]:
    return Params(parse_quote(req[3]), parse_quote(req[4])), tuple(req[5]), int(req[6])


def call_lean_batch(requests: list[list], name: str) -> list[dict[str, Any]]:
    REQUEST_DIR.mkdir(parents=True, exist_ok=True)
    path = REQUEST_DIR / f"{name}.json"
    path.write_text(json.dumps(["robust-quote-batch-v1", requests], separators=(",", ":")))
    env = os.environ.copy()
    env.setdefault("AVOC_LEAN_KIT", "/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2")
    cp = subprocess.run([sys.executable, str(WRAPPER), str(path), "--timeout", "300"],
                        cwd=ROOT, env=env, text=True, capture_output=True, timeout=330)
    if cp.returncode != 0:
        raise AssertionError(f"Lean batch {name} failed: {cp.stderr}")
    data = json.loads(cp.stdout)
    assert data["status"] == "robust_quote_batch"
    assert len(data["results"]) == len(requests)
    return data["results"]


def compare_plan_output(req: list, name: str, got: dict[str, Any]) -> dict[str, Any]:
    params, state, h = parse_plan_request(req)
    want = robust_oracle(params, state, h)
    for key in ("robust_choice", "nominal_choice", "exact_bands"):
        assert got[key] == want[key], (name, key, got[key], want[key])
    for key in ("nominal_value", "lower_value", "upper_value",
                "local_regret_bound", "whole_policy_regret_bound"):
        assert F(got[key]) == want[key], (name, key, got[key], want[key])
    grows = {r["action"]: r for r in got["actions"]}
    for row in want["actions"]:
        gr = grows[row["action"]]
        for key in ("nominal_q", "radius", "lower_q", "upper_q"):
            assert F(gr[key]) == row[key], (name, row["action"], key, gr[key], row[key])
        assert gr["certified_dominance"] == row["certified_dominance"]
    return {"name": name, "choice": got["robust_choice"], "actions": len(want["actions"])}

def exact_points(lo: Fraction, hi: Fraction) -> list[Fraction]:
    pts = {lo, hi, (lo+hi)/2}
    return sorted(pts)


def exact_ints(lo: int, hi: int) -> list[int]:
    return list(range(lo, hi+1))


def check_realizations(req: list, lean: dict[str, Any]) -> int:
    params, state, h = parse_plan_request(req)
    rows = {r["action"]: r for r in lean["actions"]}
    count = 0
    for ws in exact_ints(params.warm.setup_lo, params.warm.setup_hi):
      for cs in exact_ints(params.cold.setup_lo, params.cold.setup_hi):
       for wg in exact_points(params.warm.gross_lo, params.warm.gross_hi):
        for cg in exact_points(params.cold.gross_lo, params.cold.gross_hi):
         for wp in exact_points(params.warm.prob_lo, params.warm.prob_hi):
          for cp in exact_points(params.cold.prob_lo, params.cold.prob_hi):
            ex = ExactParams(ws,cs,wg,cg,wp,cp)
            value, _choice, q = dp(params, h+1, state, ex)
            assert F(lean["lower_value"]) <= value <= F(lean["upper_value"])
            for a in action_list(params, state):
                tq = q(h,state,a)
                assert F(rows[a]["lower_q"]) <= tq <= F(rows[a]["upper_q"])
            count += 1
    return count


def make_quote(template: list, *, setup: tuple[int,int], gross: tuple[Fraction,Fraction],
               prob: tuple[Fraction,Fraction], provider: str) -> list:
    q = copy.deepcopy(template)
    q[0][5] = provider
    q[1] = [setup[0], setup[1]]
    q[2] = [frac_wire(gross[0]), frac_wire(gross[1])]
    q[3] = [frac_wire(prob[0]), frac_wire(prob[1])]
    return q


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=RESULT)
    ns = ap.parse_args()
    random.seed(20260918)
    exact_req = json.loads((ROOT/"examples/robust_quote/exact_plan.json").read_text())
    unc_req = json.loads((ROOT/"examples/robust_quote/uncertain_plan.json").read_text())
    dom_req = json.loads((ROOT/"examples/robust_quote/dominance_plan.json").read_text())

    named_plan_requests: list[tuple[str,list]] = [
        ("exact_plan_regression", exact_req),
        ("uncertain_plan_regression", unc_req),
        ("dominance_plan_regression", dom_req),
    ]

    base_w, base_c = exact_req[3], exact_req[4]
    random_cases = 18
    for idx in range(random_cases):
        calls = 1
        warm_setup_lo = random.randint(0,1); warm_setup_hi = random.randint(warm_setup_lo,2)
        cold_setup_lo = random.randint(0,1); cold_setup_hi = random.randint(cold_setup_lo,2)
        wg0 = Fraction(random.randint(0,5)); wg1 = Fraction(random.randint(int(wg0),7))
        cg0 = Fraction(random.randint(0,5)); cg1 = Fraction(random.randint(int(cg0),7))
        pvals = [Fraction(0),Fraction(1,2),Fraction(1)]
        wp0 = random.choice(pvals); wp1 = random.choice([x for x in pvals if x >= wp0])
        cp0 = random.choice(pvals); cp1 = random.choice([x for x in pvals if x >= cp0])
        w = make_quote(base_w, setup=(warm_setup_lo,warm_setup_hi), gross=(wg0,wg1),
                       prob=(wp0,wp1), provider=f"random-warm-{idx}")
        c = make_quote(base_c, setup=(cold_setup_lo,cold_setup_hi), gross=(cg0,cg1),
                       prob=(cp0,cp1), provider=f"random-cold-{idx}")
        w[0][3]=calls; c[0][3]=calls
        budget=max(warm_setup_hi,cold_setup_hi)
        req=["robust-quote-plan-f5-v1",exact_req[1],calls,w,c,
             ["untried","untried",budget,0,budget,False],random.choice([0,1])]
        named_plan_requests.append((f"random_{idx:02d}",req))

    plan_items = call_lean_batch([q for _,q in named_plan_requests], "plan_batch")
    records=[]
    realization_checks=0
    for (name,req),item in zip(named_plan_requests,plan_items):
        assert item["ok"] is True, (name,item)
        got=item["value"]
        records.append(compare_plan_output(req,name,got))
        realization_checks += check_realizations(req,got)

    boundary_names=["validate_exact","validate_mutated","warm_transition","cold_transition",
                    "warm_recover","fault_transition","outside_artifact","mutated_recover"]
    boundary_reqs=[json.loads((ROOT/f"examples/robust_quote/{n}.json").read_text())
                   for n in boundary_names]
    unfinished=["robust-quote-unfinished-f5-v1",exact_req[1],exact_req[2],
                exact_req[3],exact_req[4],196,"inspect_warm"]
    boundary_names.append("unfinished_intent"); boundary_reqs.append(unfinished)
    boundary_items=call_lean_batch(boundary_reqs,"boundary_batch")
    expected_ok={"validate_exact","validate_mutated","warm_transition","cold_transition","warm_recover"}
    accepted=[]; rejected=[]
    for name,item in zip(boundary_names,boundary_items):
        if name in expected_ok:
            assert item["ok"] is True,(name,item)
            val=item["value"]
            accepted.append({"name":name,"status":val.get("status"),"accepted":val.get("accepted")})
        else:
            assert item["ok"] is False,(name,item)
            rejected.append({"name":name,"error":item["error"]})
    assert "no durable result" in next(x["error"] for x in rejected if x["name"]=="unfinished_intent")

    # Direct output assertions for refinement and recovery.
    warm = next(item["value"] for name,item in zip(boundary_names,boundary_items)
                if name=="warm_transition")
    after=warm["after"]
    assert after["warm_evidence"]["setup"] == 133
    assert F(after["warm_evidence"]["gross"]) == 15000
    assert after["warm_evidence"]["probability_band"] == ["1","1"]
    assert after["cold_artifact"] is None and after["cold_evidence"] is None
    recov = next(item["value"] for name,item in zip(boundary_names,boundary_items)
                 if name=="warm_recover")
    assert recov["sequence_before"] == 0 and recov["sequence_after"] == 1
    assert recov["duplicate_ack_idempotent"] is True

    result={
        "schema":"avoc-v0.38-robust-quote-regression-v1",
        "seed":20260918,
        "lean_plan_comparisons":len(records),
        "compatible_realization_checks":realization_checks,
        "accepted_boundary_cases":accepted,
        "rejected_boundary_cases":rejected,
        "records":records,
        "non_claims":[
            "finite exact regression is not a universal proof",
            "quote probability bands are supplied and not empirically calibrated",
            "the independent oracle does not verify Lean, Python, or the host runtime"
        ],
        "result":"all exact comparisons passed"
    }
    ns.output.parent.mkdir(parents=True,exist_ok=True)
    ns.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("records","accepted_boundary_cases","rejected_boundary_cases")},sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
