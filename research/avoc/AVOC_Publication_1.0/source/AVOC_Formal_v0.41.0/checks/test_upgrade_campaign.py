#!/usr/bin/env python3
"""Exact differential tests of the executed Lean upgrade gate, plus wrapper defenses.
Only finite test evidence. General guarantees are in the Lean modules.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import run_upgrade_campaign as gate
RD = ROOT / "results/v0.23.0"


def project(s: dict) -> dict:
    u = -70 if s['active'] == 'dynamic' else -7
    return dict(initial='dynamic', active=s['active'], revision=s['revision'],
        funded_trials=s['trials'], evaluation_spent=s['evaluations'], switch_spent=s['switches'],
        guaranteed_gain=8*s['revision'], initial_utility=-70, active_utility=u,
        net_endpoint_gain=u+70-s['evaluations']-s['switches'],
        certified_net_lower_bound=8*s['revision']-s['evaluations'])


def oracle(credit: int, proposals: list[list]) -> dict:
    s = dict(active='dynamic', revision=0, trials=0, evaluations=0, switches=0)
    events = []
    for parent, rev, candidate, core, objective in proposals:
        evaluation_debit = switch_debit = 0
        outcome = 'unfunded'
        if s['evaluations']+s['switches']+3 <= credit:
            evaluation_debit = 3
            u_old = -70 if s['active'] == 'dynamic' else -7
            u_new = -70 if candidate == 'dynamic' else -7
            qualifies = (parent == s['active'] and rev == s['revision'] and
                core == gate.CORE and objective == gate.OBJECTIVE and candidate != 'always_retry' and
                u_new-u_old >= 9 and s['evaluations']+s['switches']+4 <= credit)
            s['evaluations'] += 3
            s['trials'] += 1
            outcome = 'rejected'
            if qualifies:
                s['active'] = candidate
                s['revision'] += 1
                s['switches'] += 1
                switch_debit = 1
                outcome = 'promoted'
        events.append(dict(outcome=outcome, candidate=candidate, evaluation_debit=evaluation_debit,
                           switch_debit=switch_debit, state=project(s)))
        assert s['evaluations']+s['switches'] <= credit
        assert s['active'] != 'always_retry'
    return dict(final=project(s), events=events)


def suite() -> list[list]:
    def p(parent='dynamic', rev=0, candidate='threshold', core=gate.CORE, objective=gate.OBJECTIVE):
        return [parent, rev, candidate, core, objective]
    variants = [p(), p(candidate='always_retry'), p(candidate='dynamic'), p(rev=1),
        p(parent='threshold', rev=1), p(core='changed'), p(objective='easier')]
    wires = []
    for credit in list(range(16))+[24,40,76,100]:
        for n in range(3):
            for ps in itertools.product(variants, repeat=n):
                wires.append(['avoc-upgrade-campaign-v1', credit, list(ps)])
    rng = random.Random(230023)
    for _ in range(300):
        wires.append(['avoc-upgrade-campaign-v1', rng.randint(0,100),
                      [rng.choice(variants) for _ in range(rng.randint(3,12))]])
    wires += [['avoc-upgrade-campaign-v1', 100, [p(candidate='always_retry')]*24+[p()]],
              ['avoc-upgrade-campaign-v1', 100, [p(),p()]]]
    return wires


def run_batch(start: int, count: int) -> None:
    RD.mkdir(parents=True, exist_ok=True)
    cases = suite()[start:start+count]
    if not cases:
        raise ValueError('empty test slice')
    lean, env = gate.checked_environment()
    request = RD / f'upgrade_requests_{start:04d}.json'
    request.write_text(json.dumps(cases))
    cmd = [str(lean), '--run', str(ROOT/'tools/UpgradeMain.lean'), '--batch', str(request)]
    t = time.monotonic()
    result = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=90)
    elapsed = time.monotonic()-t
    (RD/f'upgrade_output_{start:04d}.jsonl').write_text(result.stdout)
    (RD/f'upgrade_errors_{start:04d}.log').write_text(result.stderr)
    assert result.returncode == 0, result.stderr
    outputs = [json.loads(line) for line in result.stdout.splitlines()]
    assert len(outputs) == len(cases)
    promotions = rejections = unfunded = 0
    for wire, actual in zip(cases, outputs):
        expected = oracle(wire[1], wire[2])
        assert actual['status'] == 'checked'
        assert actual['final'] == expected['final'], (wire, actual, expected)
        assert actual['events'] == expected['events'], (wire, actual, expected)
        for row in actual['active_component_execution']:
            h = row['horizon']
            assert row['reference_retry'] == row['active_retry'] == (h>0)
            assert row['reference_visits'] == h+1
            assert row['active_visits'] == (h+1 if actual['final']['active']=='dynamic' else 1)
        for ev in actual['events']:
            promotions += ev['outcome']=='promoted'
            rejections += ev['outcome']=='rejected'
            unfunded += ev['outcome']=='unfunded'
    record = dict(passed=True,start=start,count=len(cases),total_cases=len(suite()),
        promotions=promotions,rejections=rejections,unfunded=unfunded,seconds=elapsed,
        command=cmd,returncode=result.returncode,seed=230023,
        test_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        request_sha256=hashlib.sha256(request.read_bytes()).hexdigest(),
        output_sha256=hashlib.sha256(result.stdout.encode()).hexdigest())
    (RD/f'upgrade_test_{start:04d}.json').write_text(json.dumps(record,indent=2)+'\n')
    print(record)


def run_defenses() -> None:
    base=dict(credits=100,proposals=[dict(parent='dynamic',revision=0,candidate='threshold')])
    invalid=[]
    for name,value in [('negative',-1),('bool',True),('float',4.0),('oversize',10001)]:
        x=deepcopy(base);x['credits']=value;invalid.append((name,x))
    for name,key,value in [('forged_lower','lower',10000),('free_search','evaluationCost',0),
                           ('self_approval','approved',True),('new_checker','checker','accept_all')]:
        x=deepcopy(base);x['proposals'][0][key]=value;invalid.append((name,x))
    x=deepcopy(base);x['proposals'][0]['candidate']='untrusted_source.py';invalid.append(('arbitrary_code',x))
    x=deepcopy(base);x['proposals'][0]['revision']=True;invalid.append(('bool_revision',x))
    x=deepcopy(base);x['proposals']*=129;invalid.append(('too_many',x))
    rejected=[]
    for name,x in invalid:
        try: gate.make_wire(x)
        except ValueError: rejected.append(name)
        else: raise AssertionError(name)
    try:json.loads('{"credits":1,"credits":2}',object_pairs_hook=gate.unique_object)
    except ValueError:rejected.append('duplicate_keys')
    else:raise AssertionError('duplicate JSON accepted')
    lean,env=gate.checked_environment()
    good=gate.make_wire(base)
    raw_bad=[None,{},[],['avoc-upgrade-campaign-v2',1,[]],['avoc-upgrade-campaign-v1',True,[]],
        ['avoc-upgrade-campaign-v1',-1,[]],['avoc-upgrade-campaign-v1',10001,[]],
        ['avoc-upgrade-campaign-v1',100,[['dynamic',0,'evil',gate.CORE,gate.OBJECTIVE]]],
        ['avoc-upgrade-campaign-v1',100,[['dynamic',0,'threshold',gate.CORE,gate.OBJECTIVE,'extra']]],
        ['avoc-upgrade-campaign-v1',100,[['dynamic',1001,'threshold',gate.CORE,gate.OBJECTIVE]]],
        ['avoc-upgrade-campaign-v1',100,[['dynamic',0,'threshold','x'*257,gate.OBJECTIVE]]]]
    req=RD/'invalid_upgrade_wire.json';req.write_text(json.dumps(raw_bad))
    cp=subprocess.run([str(lean),'--run',str(ROOT/'tools/UpgradeMain.lean'),'--batch',str(req)],
                      cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
    assert cp.returncode==0,cp.stderr
    replies=[json.loads(x) for x in cp.stdout.splitlines()]
    assert len(replies)==len(raw_bad) and all(x['status']=='error' for x in replies)
    (RD/'invalid_upgrade_output.jsonl').write_text(cp.stdout)
    # Workspace-local controlled mutation; never edit the inherited release or a user registry.
    source=ROOT/'AVOC/UpgradeSpecialization.lean';original=source.read_bytes()
    try:
        source.write_bytes(original+b'\n-- test-only drift\n')
        try:gate.checked_environment()
        except RuntimeError as exc:
            assert 'source drift' in str(exc);rejected.append('protected_source_drift')
        else:raise AssertionError('altered source passed pins')
    finally:source.write_bytes(original)
    gate.checked_environment()
    record=dict(passed=True,wrapper_rejections=rejected,raw_wire_rejections=len(raw_bad),
        test_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        restored_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    (RD/'upgrade_defense_tests.json').write_text(json.dumps(record,indent=2)+'\n')
    print(record)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--start',type=int,default=0)
    p.add_argument('--count',type=int,default=200);p.add_argument('--defenses',action='store_true')
    ns=p.parse_args()
    if ns.defenses:run_defenses()
    else:run_batch(ns.start,ns.count)
