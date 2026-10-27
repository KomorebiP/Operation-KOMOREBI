#!/usr/bin/env python3
"""Exact differential regression for the multi-level affine information controller.

The independent oracle constructs entry/minor outcome tables, performs exact
Fraction dynamic programming over stop/reuse/cold/probe actions, and computes
GF(5) ranks by row reduction.  Lean proves the universal Bellman and algebraic
invariants; this bounded test audits the executable codec and evaluator.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import plan_multi_level as app

RD = ROOT / "results/v0.33.0/multi_level_tests"


def rat(x: Any) -> Fraction:
    if isinstance(x, list):
        a, b = x
        return Fraction(a, b)
    s = str(x).replace(" ", "")
    if "/" in s:
        a, b = s.split("/", 1)
        return Fraction(int(a), int(b))
    return Fraction(int(s), 1)


def rank_mod5(a: list[list[int]]) -> int:
    if not a:
        return 0
    rows = [list(map(lambda x: x % 5, row)) for row in a]
    m, n = len(rows), len(rows[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if rows[i][c] % 5), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        inv = pow(rows[r][c], -1, 5)
        rows[r] = [(x * inv) % 5 for x in rows[r]]
        for i in range(m):
            if i != r and rows[i][c] % 5:
                k = rows[i][c] % 5
                rows[i] = [(x - k * y) % 5 for x, y in zip(rows[i], rows[r])]
        r += 1
        if r == m:
            break
    return r


def detects(a: list[list[int]], p: list[Any]) -> bool:
    if p[0] == "entry":
        return a[p[1]][p[2]] % 5 != 0
    _, i, j, k, l = p
    return (a[i][k] * a[j][l] - a[i][l] * a[j][k]) % 5 != 0


def level(p: list[Any]) -> int:
    return 1 if p[0] == "entry" else 2


@dataclass(frozen=True)
class State:
    worlds: tuple[int, ...]
    remaining: tuple[int, ...]
    lower: int
    done: bool


def parse(req: list[Any]):
    (tag, rows, cols, matrices, probes, fees, reuse_enabled,
     reuse_payoffs, cold_payoffs, horizon, history) = req
    assert tag == "multi-level-affine-f5-v1"
    table = tuple(tuple(detects(a, p) for a in matrices) for p in probes)
    fee = tuple(rat(x) for x in fees)
    reuse = tuple(rat(x) for x in reuse_payoffs)
    cold = tuple(rat(x) for x in cold_payoffs)
    state = State(tuple(range(len(matrices))), tuple(range(len(probes))), 0, False)
    for pi, outcome in history:
        if state.done or pi not in state.remaining:
            raise ValueError("unsupported history")
        support = tuple(w for w in state.worlds if table[pi][w] == outcome)
        if not support:
            raise ValueError("zero-probability history")
        rem = tuple(p for p in state.remaining if p != pi)
        state = State(
            support,
            rem,
            max(state.lower, level(probes[pi])) if outcome else state.lower,
            False,
        )
    return matrices, probes, table, fee, reuse_enabled, reuse, cold, horizon, state


def actions(state: State, reuse_enabled: bool):
    if state.done:
        return (("stop", None),)
    xs = [("stop", None)]
    if reuse_enabled:
        xs.append(("reuse", None))
    xs.append(("cold", None))
    xs.extend(("probe", p) for p in state.remaining)
    return tuple(xs)


def avg(values: tuple[Fraction, ...], worlds: tuple[int, ...]) -> Fraction:
    return sum((values[w] for w in worlds), Fraction()) / len(worlds)


def transition(state: State, action, outcome: bool, table, probes):
    kind, p = action
    if kind != "probe":
        return State(state.worlds, (), state.lower, True)
    support = tuple(w for w in state.worlds if table[p][w] == outcome)
    # Total-update fallback on impossible observations.
    worlds = support if support else state.worlds
    rem = tuple(q for q in state.remaining if q != p)
    lower = max(state.lower, level(probes[p])) if outcome and support else state.lower
    return State(worlds, rem, lower, False)


def action_prob(state: State, action, outcome: bool, table) -> Fraction:
    kind, p = action
    if kind != "probe":
        return Fraction(0) if outcome else Fraction(1)
    q = Fraction(sum(table[p][w] for w in state.worlds), len(state.worlds))
    return q if outcome else 1 - q


def reward(state: State, action, fee, reuse, cold):
    kind, p = action
    if kind == "stop":
        return Fraction(0)
    if kind == "reuse":
        return avg(reuse, state.worlds)
    if kind == "cold":
        return avg(cold, state.worlds)
    return -fee[p]


def solve(req):
    matrices, probes, table, fee, reuse_enabled, reuse, cold, horizon, state0 = parse(req)

    @lru_cache(None)
    def ev(h: int, state: State):
        if h == 0:
            return Fraction(0), ("stop", None), 1
        rows = []
        for action in actions(state, reuse_enabled):
            score = reward(state, action, fee, reuse, cold)
            work = 1
            for outcome in (False, True):
                child = transition(state, action, outcome, table, probes)
                cv, _, cw = ev(h - 1, child)
                score += action_prob(state, action, outcome, table) * cv
                work += 1 + cw
            rows.append((score, action, work))
        best = rows[0]
        for row in rows[1:]:
            # Lean's action order wins ties.
            if row[0] > best[0]:
                best = row
        return best[0], best[1], 1 + sum(row[2] for row in rows)

    return ev(horizon, state0), (matrices, probes, table, fee, reuse_enabled, reuse, cold, state0)


def state_wire(state: State):
    return {
        "retained_worlds": len(state.worlds),
        "remaining_probes": len(state.remaining),
        "rank_floor": state.lower,
        "done": state.done,
    }


def choice_wire(action):
    kind, p = action
    return {"kind": kind} if kind != "probe" else {"kind": kind, "index": p}


def check_result(req, out):
    (value, choice, work), parsed = solve(req)
    matrices, probes, table, fee, reuse_enabled, reuse, cold, state = parsed
    assert out["status"] == "optimal_multi_level_affine_policy", out
    assert out["choice"] == choice_wire(choice), (req, out["choice"], choice)
    assert rat(out["expected_net_value"]) == value, (req, out["expected_net_value"], value)
    assert out["planning_work"] == work, (req, out["planning_work"], work)
    assert out["state"] == state_wire(state), (req, out["state"], state_wire(state))
    assert out["reuse_available"] is reuse_enabled
    assert rat(out["reuse_expected_payoff"]) == avg(reuse, state.worlds)
    assert rat(out["cold_expected_payoff"]) == avg(cold, state.worlds)
    rows = {r["index"]: r for r in out["probe_table"]}
    assert set(rows) == set(state.remaining)
    for p in state.remaining:
        assert rows[p]["certified_level"] == level(probes[p])
        assert rat(rows[p]["fee"]) == fee[p]
        assert rat(rows[p]["success_probability"]) == Fraction(
            sum(table[p][w] for w in state.worlds), len(state.worlds)
        )
    # The retained floor is a genuine algebraic lower bound independently of odds.
    for w in state.worlds:
        assert state.lower <= rank_mod5(matrices[w]), (state, w, matrices[w])
    if choice[0] == "probe":
        p = choice[1]
        q = Fraction(sum(table[p][w] for w in state.worlds), len(state.worlds))
        branches = out["selected_branches"]
        assert rat(branches["success_probability"]) == q
        assert branches["after_failure"] == state_wire(transition(state, choice, False, table, probes))
        assert branches["after_success"] == state_wire(transition(state, choice, True, table, probes))
    else:
        assert out["selected_branches"] is None


def random_probe(rows: int, cols: int, rng: random.Random):
    if rows >= 2 and cols >= 2 and rng.random() < 0.55:
        i, j = rng.sample(range(rows), 2)
        k, l = rng.sample(range(cols), 2)
        return ["minor2", i, j, k, l]
    return ["entry", rng.randrange(rows), rng.randrange(cols)]


def rwire(x: Fraction):
    return [x.numerator, x.denominator]


def random_request(rng: random.Random):
    rows, cols = rng.randrange(1, 5), rng.randrange(1, 5)
    nw, np = rng.randrange(1, 7), rng.randrange(0, 6)
    matrices = [
        [[rng.randrange(5) for _ in range(cols)] for _ in range(rows)]
        for _ in range(nw)
    ]
    probes = [random_probe(rows, cols, rng) for _ in range(np)]
    fees = [rwire(Fraction(rng.randrange(0, 10), rng.randrange(1, 5))) for _ in probes]
    reuse_enabled = bool(rng.randrange(2))
    reuse = [rwire(Fraction(rng.randrange(-15, 21), rng.randrange(1, 5))) for _ in range(nw)]
    cold = [rwire(Fraction(rng.randrange(-15, 31), rng.randrange(1, 5))) for _ in range(nw)]
    history = []
    worlds = tuple(range(nw))
    remaining = list(range(np))
    for _ in range(rng.randrange(0, min(3, np) + 1)):
        if not remaining:
            break
        p = rng.choice(remaining)
        opts = []
        for o in (False, True):
            support = tuple(w for w in worlds if detects(matrices[w], probes[p]) == o)
            if support:
                opts.append((o, support))
        o, worlds = rng.choice(opts)
        history.append([p, o])
        remaining.remove(p)
    return [
        "multi-level-affine-f5-v1", rows, cols, matrices, probes, fees,
        reuse_enabled, reuse, cold, rng.randrange(0, 5), history,
    ]


def differential():
    RD.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20260914)
    requests = [random_request(rng) for _ in range(320)]
    outputs = []
    invocations = []
    start = time.monotonic()
    for i in range(0, len(requests), 80):
        batch = requests[i:i + 80]
        got = app.invoke(batch, batch=True, timeout=120, records=invocations)
        for req, out in zip(batch, got):
            check_result(req, out)
        outputs.extend(got)

    identity = [[[1, 0], [0, 1]]]
    invalid = [
        ["bad"],
        ["multi-level-affine-f5-v1", 2, 2, [], [], [], False, [], [], 1, []],
        ["multi-level-affine-f5-v1", 2, 2, identity, [["entry", 2, 0]], [[1, 1]], False, [[0, 1]], [[0, 1]], 1, []],
        ["multi-level-affine-f5-v1", 2, 2, identity, [["entry", 0, 0]], [], False, [[0, 1]], [[0, 1]], 1, []],
        ["multi-level-affine-f5-v1", 2, 2, identity, [["entry", 0, 0]], [[-1, 1]], False, [[0, 1]], [[0, 1]], 1, []],
        ["multi-level-affine-f5-v1", 2, 2, identity, [["entry", 0, 0]], [[1, 1]], False, [[0, 1]], [[0, 1]], 9, []],
        ["multi-level-affine-f5-v1", 2, 2, identity, [["entry", 0, 0]], [[1, 1]], False, [[0, 1]], [[0, 1]], 1, [[0, False]]],
        ["multi-level-affine-f5-v1", 2, 2, identity, [["entry", 0, 0]], [[1, 0]], False, [[0, 1]], [[0, 1]], 1, []],
    ]
    errors = app.invoke(invalid, batch=True, timeout=120, records=invocations)
    assert all(x.get("status") == "error" for x in errors), errors
    summary = {
        "passed": True,
        "seed": 20260914,
        "valid_requests": len(requests),
        "invalid_requests_rejected": len(errors),
        "probe_choices": sum(x["choice"]["kind"] == "probe" for x in outputs),
        "reuse_choices": sum(x["choice"]["kind"] == "reuse" for x in outputs),
        "cold_choices": sum(x["choice"]["kind"] == "cold" for x in outputs),
        "stop_choices": sum(x["choice"]["kind"] == "stop" for x in outputs),
        "seconds": round(time.monotonic() - start, 6),
        "oracle": "independent GF(5) rank, exact Fraction dynamic programming, and exact work accounting",
        "universal_claim_from_regression": False,
    }
    for name, data in [
        ("differential_summary", summary),
        ("differential_requests", requests),
        ("differential_outputs", outputs),
        ("invalid_outputs", errors),
        ("differential_invocations", invocations),
    ]:
        (RD / f"{name}.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


def live():
    RD.mkdir(parents=True, exist_ok=True)
    records = {}
    invocations = []
    for path in sorted((ROOT / "examples/multi_level").glob("*.json")):
        req = app.read_request(path)
        out = app.invoke(req, records=invocations)
        check_result(req, out)
        records[path.stem] = out
        (RD / f"live_{path.stem}.json").write_text(json.dumps(out, indent=2) + "\n")
    assert records["base_h1"]["choice"] == {"kind": "cold"}
    assert rat(records["base_h1"]["expected_net_value"]) == Fraction(19, 4)
    assert records["base_h2"]["choice"] == {"kind": "probe", "index": 1}
    assert rat(records["base_h2"]["expected_net_value"]) == 9
    assert records["after_minor_success"]["choice"] == {"kind": "reuse"}
    assert records["after_minor_success"]["state"]["rank_floor"] == 2
    assert records["after_minor_failure"]["choice"] == {"kind": "cold"}
    summary = {
        "passed": True,
        "live_cases": len(records),
        "results": {
            k: {
                "choice": v["choice"],
                "value": v["expected_net_value"],
                "rank_floor": v["state"]["rank_floor"],
                "work": v["planning_work"],
            }
            for k, v in records.items()
        },
        "store_mutations": 0,
        "physical_speedup_claim": False,
    }
    (RD / "live_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (RD / "live_invocations.json").write_text(json.dumps(invocations, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "differential"
    sources = [
        Path(__file__),
        ROOT / "tools/plan_multi_level.py",
        ROOT / "tools/MultiLevelMain.lean",
        ROOT / "AVOC/MultiLevelInformation.lean",
        ROOT / "AVOC/MultiLevelRank.lean",
        ROOT / "AVOC/MultiLevelCodec.lean",
    ]
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    started = time.time()
    try:
        (differential if command == "differential" else live)()
    finally:
        after = {q: hashlib.sha256((ROOT / q).read_bytes()).hexdigest() for q in before}
        RD.mkdir(parents=True, exist_ok=True)
        (RD / f"{command}_source_record.json").write_text(json.dumps({
            "started_at_unix": started,
            "input_source_before": before,
            "input_source_after": after,
            "unchanged": before == after,
        }, indent=2) + "\n")
