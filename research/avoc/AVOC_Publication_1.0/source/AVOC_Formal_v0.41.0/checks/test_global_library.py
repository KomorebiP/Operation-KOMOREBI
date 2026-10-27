#!/usr/bin/env python3
"""Exact independent oracle and adversarial imports; not a production-LLM benchmark."""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/v0.27.0/library_tests'
OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('library_wrapper',ROOT/'tools/global_library.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
CERT=json.loads((ROOT/'examples/library/global.json').read_text())
INPUTS=list(itertools.product([False,True],repeat=3))

def size(p):
    return 1 if p[0] in ('literal','variable') else 1+sum(size(q) for q in p[1:])

def interpret(p,x):
    t=p[0]
    if t=='literal':return p[1]
    if t=='variable':return x[p[1]]
    if t=='not':return not interpret(p[1],x)
    a,b=interpret(p[1],x),interpret(p[2],x)
    if t=='and':return a and b
    if t=='or':return a or b
    if t=='xor':return a!=b
    raise ValueError(t)

def mask(p):return sum(int(interpret(p,x))<<i for i,x in enumerate(INPUTS))

def oracle_costs():
    # Independent exact-size enumeration. It does not inspect supplied certificate costs.
    best={0:1,255:1,240:1,204:1,170:1};levels={1:set(best)}
    for n in range(2,11):
        found={255^a for a in levels.get(n-1,set())}
        for i in range(1,n-1):
            for a in levels.get(i,set()):
                for b in levels.get(n-i-1,set()):found.update([a&b,a|b,a^b])
        levels[n]=found-set(best)
        best.update({m:n for m in levels[n]})
    assert len(best)==256
    return best

ORACLE=oracle_costs()

def tariff(c):return 196869+len(c[4])+8*sum(size(row[2]) for row in c[4])

def independently_valid(c):
    if len(c)!=5 or c[:4]!=gate.DESCRIPTORS or len(c[4])!=256:return False
    costs=[]
    for i,(bits,n,p) in enumerate(c[4]):
        if bits!=[bool(i&(1<<j)) for j in range(8)] or size(p)!=n or mask(p)!=i:return False
        costs.append(n)
    if any(costs[i]>1 for i in [0,255,240,204,170]):return False
    for a in range(256):
        if costs[255^a]>1+costs[a]:return False
        for b in range(256):
            if any(costs[m]>1+costs[a]+costs[b] for m in [a&b,a|b,a^b]):return False
    return True


def run_wire():
    t=time.perf_counter();cases=[]
    refs=[['not',['not',row[2]]] for row in CERT[4]]
    rng=random.Random(20260913)
    def gen(d):
        if not d or rng.randrange(4)==0:return rng.choice([['literal',False],['literal',True],['variable',0],['variable',1],['variable',2]])
        op=rng.choice(['not','and','or','xor'])
        return [op,gen(d-1)] if op=='not' else [op,gen(d-1),gen(d-1)]
    refs+= [gen(5) for _ in range(128)]
    def add(name,c,credit=10**6,qs=None,expected='globally_certified'):
        cases.append((name,['avoc-library-load-v1',c,credit,[] if qs is None else qs],expected))
    add('all_semantics_and_random_queries',copy.deepcopy(CERT),qs=refs)
    alternate=copy.deepcopy(CERT)
    for row in alternate[4]:
        p=row[2]
        if p[0] in ('and','or','xor'):row[2]=[p[0],p[2],p[1]]
    add('different_optimal_witnesses',alternate,qs=refs[:256])
    for name in ['wrong_signature','wrong_cost','larger_valid_witness','all_zero_costs','swapped_rows','duplicate_row']:
        c=copy.deepcopy(CERT)
        if name=='wrong_signature':c[4][1][0][0]=not c[4][1][0][0]
        if name=='wrong_cost':c[4][1][1]+=1
        if name=='larger_valid_witness':
            c[4][1][2]=['not',['not',c[4][1][2]]];c[4][1][1]+=2
            assert all(mask(p)==i and size(p)==n for i,(_,n,p) in enumerate(c[4]))
        if name=='all_zero_costs':
            for r in c[4]:r[1]=0
        if name=='swapped_rows':c[4][10],c[4][11]=c[4][11],c[4][10]
        if name=='duplicate_row':c[4][1]=copy.deepcopy(c[4][2])
        assert not independently_valid(c)
        add(name,c,expected='invalid_certificate')
    for pos,name in enumerate(['schema','grammar','order','cost_model']):
        c=copy.deepcopy(CERT);c[pos]+='-changed';add('changed_'+name,c,expected='error')
    c=copy.deepcopy(CERT);c[4].pop();add('missing_entry',c,expected='error')
    c=copy.deepcopy(CERT);c[4].append(c[4][0]);add('extra_entry',c,expected='error')
    c=copy.deepcopy(CERT);c[4][0][2]=['eval','arbitrary code'];add('code_injection',c,expected='error')
    c=copy.deepcopy(CERT);c[4][0][0][0]=0;add('nonboolean_signature',c,expected='error')
    c=copy.deepcopy(CERT);c[4][0][1]=True;add('boolean_cost',c,expected='error')
    c=copy.deepcopy(CERT);c.append({'optimal':True});add('extra_claim_field',c,expected='error')
    fee=tariff(CERT)
    for credit in [0,fee-1]:add('unfunded_'+str(credit),CERT,credit,refs[:3],expected='unfunded')
    add('validation_only_credit',CERT,fee,refs[:3])
    add('partial_query_credit',CERT,fee+9,refs[:1]+[['literal',True]])
    add('exact_query_credit',CERT,fee+sum(8*size(p)+1 for p in refs[:3]),refs[:3])
    add('negative_credit',CERT,-1,expected='error')
    add('excess_queries',CERT,10**6,[['literal',False]]*513,expected='error')
    lean,env=gate.verify_checker_sources()
    request=OUT/'wire_requests.json';request.write_text(json.dumps([x[1] for x in cases],separators=(',',':')))
    before=gate.sha(request.read_bytes())
    command=[str(lean),'--run',str(ROOT/'tools/SemanticLibraryMain.lean'),'--batch',str(request)]
    proc=subprocess.run(command,cwd=ROOT,env=env,text=True,capture_output=True,timeout=100)
    (OUT/'wire_stdout.jsonl').write_text(proc.stdout);(OUT/'wire_stderr.txt').write_text(proc.stderr)
    assert proc.returncode==0,(proc.returncode,proc.stderr)
    replies=[json.loads(x) for x in proc.stdout.splitlines()]
    assert len(replies)==len(cases)
    checks=[];query_count=0;truth_count=0
    for (name,req,expected),out in zip(cases,replies):
        assert out['status']==expected,(name,out)
        if expected in ['globally_certified','invalid_certificate','unfunded']:
            c,credit,qs=req[1:]
            fee=tariff(c)
            assert out['validation_charged']==(fee if fee<=credit else 0),(name,out)
            qcost=out['query_charged']
            assert out['remaining']+out['validation_charged']+qcost==credit
            if expected=='globally_certified':
                available=credit-fee
                assert len(out['queries'])==len(qs)
                for p,r in zip(qs,out['queries']):
                    price=8*size(p)+1
                    if price>available:
                        assert r['status']=='query_unfunded' and r['program'] is None and r['charged']==0
                    else:
                        q=r['program'];assert mask(q)==mask(p)
                        assert size(q)==r['nodes']==ORACLE[mask(p)]
                        assert r['charged']==price
                        available-=price;query_count+=1;truth_count+=8
                    assert r['remaining']==available
                assert available==out['remaining']
        checks.append({'name':name,'status':out['status'],'passed':True})
    result={'passed':True,'cases':len(cases),'successful_query_comparisons':query_count,
            'individual_truth_comparisons':truth_count,'seed':20260913,
            'commands':[command],'returncode':proc.returncode,'timed_out':False,
            'runtime_seconds':time.perf_counter()-t,'cases_detail':checks,
            'oracle':'independent exact-node-size semantic enumeration, complete through size 10',
            'request_sha256_before':before,'request_sha256_after':gate.sha(request.read_bytes()),
            'stdout_sha256':gate.sha(proc.stdout.encode()),'source_sha256':gate.sha(Path(__file__).read_bytes())}
    (OUT/'wire_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases_detail'},indent=2))


def run_store():
    t=time.perf_counter();cases=[];calls=[]
    scratch=OUT/'stores';scratch.mkdir(exist_ok=True)
    def cli(args,ok):
        p=subprocess.run([sys.executable,str(ROOT/'tools/global_library.py'),*map(str,args)],cwd=ROOT,text=True,capture_output=True,timeout=45)
        calls.append({'args':list(map(str,args)),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
        assert (p.returncode==0)==ok,(args,p.returncode,p.stdout,p.stderr)
        return json.loads(p.stdout) if p.stdout.strip() else None
    def passed(name):cases.append({'name':name,'passed':True})
    with tempfile.TemporaryDirectory(prefix='case-',dir=scratch) as tmp:
        base=Path(tmp);store=base/'saved'
        pub=cli(['publish',ROOT/'examples/library/global.json','--store',store,'--credit',300000],True)
        assert pub['published'];passed('publish_exact_valid_snapshot')
        snapshots={p.name:p.read_bytes() for p in store.iterdir()}
        for i in range(2):
            q=cli(['query',store,'--queries',ROOT/'examples/library/queries.json','--credit',300000],True)
            assert q['validation_charged']==210245 and q['regenerated_candidates'] is False
            assert [x['nodes'] for x in q['queries']]==[3,3,5]
            assert snapshots=={p.name:p.read_bytes() for p in store.iterdir()}
            passed('fresh_process_revalidation_'+str(i))
        cli(['publish',ROOT/'examples/library/global.json','--store',store],False);passed('existing_destination_not_overwritten')
        incomplete=base/'incomplete';incomplete.mkdir();shutil.copy(store/'library.json',incomplete/'library.json')
        cli(['query',incomplete,'--queries',ROOT/'examples/library/queries.json'],False);passed('incomplete_publication_rejected')
        symlink=base/'link';symlink.symlink_to(store,target_is_directory=True)
        cli(['query',symlink,'--queries',ROOT/'examples/library/queries.json'],False);passed('store_symlink_rejected')
        altered=base/'altered';shutil.copytree(store,altered)
        data=json.loads((altered/'library.json').read_text());data[4][1][1]+=1
        (altered/'library.json').write_text(json.dumps(data))
        cli(['query',altered,'--queries',ROOT/'examples/library/queries.json'],False);passed('checksum_drift_rejected')
        m=json.loads((altered/'manifest.json').read_text());m['certificate_sha256']=gate.sha((altered/'library.json').read_bytes());m['initial_validation']={'status':'globally_certified'}
        (altered/'manifest.json').write_text(json.dumps(m))
        r=cli(['query',altered,'--queries',ROOT/'examples/library/queries.json'],False)
        assert r['status']=='invalid_certificate';passed('forged_checksum_and_old_approval_cannot_bypass_checker')
        m=json.loads((store/'manifest.json').read_text());m['initial_validation']={'status':'invented'}
        (store/'manifest.json').write_text(json.dumps(m))
        r=cli(['query',store,'--queries',ROOT/'examples/library/queries.json'],True)
        assert r['status']=='globally_certified';passed('historical_approval_not_used_as_authority')
        malformed=base/'bad.json';malformed.write_text('["broken"')
        cli(['publish',malformed,'--store',base/'badstore'],False)
        assert not (base/'badstore').exists();passed('truncated_file_not_published')
        badtype=copy.deepcopy(CERT);badtype[4][0][1]=True
        malformed.write_text(json.dumps(badtype));cli(['validate',malformed],False);passed('python_boolean_integer_rejected')
        malformed.write_text('{"x":1,"x":2}');cli(['validate',malformed],False);passed('duplicate_json_fields_rejected')
        original=gate.write_fsynced;partial=base/'partial'
        def injected(path,raw):
            original(path,raw)
            if path.name=='library.json':raise RuntimeError('controlled publication interruption')
        gate.write_fsynced=injected
        try:
            try:gate.publish(ROOT/'examples/library/global.json',partial,300000,40)
            except RuntimeError:pass
            else:raise AssertionError('injection not triggered')
        finally:gate.write_fsynced=original
        assert not (partial/'READY').exists()
        cli(['query',partial,'--queries',ROOT/'examples/library/queries.json'],False);passed('interrupted_partial_store_not_trusted')
    result={'passed':True,'cases':len(cases),'case_details':cases,'commands':calls,
            'runtime_seconds':time.perf_counter()-t,'source_sha256':gate.sha(Path(__file__).read_bytes()),
            'scope':'actual Lean processes and local files; one controlled Python exception, no power-loss or process-kill claim'}
    (OUT/'store_summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['commands']},indent=2))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--part',choices=['wire','store','all'],default='all');a=ap.parse_args()
    assert independently_valid(CERT)
    assert {i:n for i,(_,n,_) in enumerate(CERT[4])}==ORACLE
    if a.part in ['wire','all']:run_wire()
    if a.part in ['store','all']:run_store()

if __name__=='__main__':main()
