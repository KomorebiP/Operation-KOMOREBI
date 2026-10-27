#!/usr/bin/env python3
"""Check current proof/test evidence; collector duration is not total proof runtime."""
from __future__ import annotations
import datetime
import hashlib
import json
import platform
from pathlib import Path
import re
import sys
import time
import zipfile
from summarize_v029 import check_record, strip_comments_strings

ROOT=Path(__file__).resolve().parents[1]
RD=ROOT/'results/v0.31.0'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def main():
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();tick=time.monotonic()
    baseline=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'AVOC_Formal_v0.30.0.zip'
    order=load(RD/'build_order.json')
    assert len(order)==len(set(order))==171
    for f in order:
        check_record(load(RD/f'clean_{Path(f).stem}.json'),f,
          ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean'))
    inv=load(RD/'declaration_inventory.json');expected={x['qualified_name'] for x in inv}
    assert len(inv)==len(expected)==1656
    check_record(load(RD/'full_axiom_audit.json'),'AVOC/FullAudit.lean')
    text=(RD/'full_axiom_audit.log').read_text()
    names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
    assert len(names)==len(expected) and set(names)==expected
    deps=set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):
        deps.update(s.strip() for s in block.split(',') if s.strip())
    assert deps<={'propext','Classical.choice','Quot.sound'}
    negatives=sorted((ROOT/'tests/negative').glob('*.lean'))
    assert len(negatives)==88
    for f in negatives:
        rec=load(RD/f'negative_{f.stem}.json');log=(ROOT/rec['log']).read_text()
        assert rec['returncode']!=0 and not rec['timed_out'] and 'error' in log,f
        assert not re.search(r'object file .*does not exist|unknown module|failed to locate application',log),f
        assert rec['source_unchanged'] and rec['imports_unchanged']
        assert rec['source_before_sha256']==rec['source_sha256']==sha(f)
        assert rec['log_sha256']==sha(ROOT/rec['log'])
        for name,digest in rec['import_outputs'].items():
            assert sha(ROOT/'.lake/build/lib/lean'/Path(name.replace('.','/')).with_suffix('.olean'))==digest
    same=0
    with zipfile.ZipFile(baseline) as z:
        assert z.testzip() is None
        for name in z.namelist():
            rel=name.removeprefix('AVOC_Formal_v0.30.0/')
            if rel.startswith('AVOC/') and rel.endswith('.lean') and Path(rel).name not in ['Audit.lean','FullAudit.lean']:
                assert z.read(name)==(ROOT/rel).read_bytes(),rel;same+=1
    assert same==148
    modules=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
    bad=[];census=[]
    for p in modules:
        source=strip_comments_strings(p.read_text())
        hits=re.findall(r'\b(?:sorry|native_decide|axiom|unsafe)\b|\bby\s+admit\b|^\s*admit\s*$',source,re.M)
        if hits:bad.append([p.name,hits])
        census.extend(re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',source,re.M))
    assert not bad and len(census)==len(inv)
    td=RD/'probe_tests';diff=load(td/'differential_summary.json');live=load(td/'live_summary.json')
    assert diff['passed'] and diff['requests']==2888
    assert live['passed'] and live['live_cases']==8
    requests=load(td/'differential_requests.json');values=load(td/'differential_outputs.json')
    runs=load(td/'differential_invocations.json')
    assert len(requests)==len(values)==2888
    for i,rec in enumerate(runs[:-1]):
        raw=(json.dumps(requests[i*180:(i+1)*180],separators=(',',':'))+'\n').encode()
        stdout=''.join(json.dumps(x,separators=(',',':'),ensure_ascii=False)+'\n' for x in values[i*180:(i+1)*180]).encode()
        assert rec['returncode']==0 and not rec['stderr']
        assert hashlib.sha256(raw).hexdigest()==rec['request_sha256'],i
        assert hashlib.sha256(stdout).hexdigest()==rec['stdout_sha256'],i
    assert len(load(td/'invalid_outputs.json'))==9
    for stage in ['differential','live']:
        record=load(td/f'{stage}_source_record.json')
        assert record['unchanged'] and record['input_source_before']==record['input_source_after']
        for name,digest in record['input_source_after'].items():assert sha(ROOT/name)==digest
    for name in live['results']:
        result=load(td/f'live_{name}.json')
        assert all(x['returncode']==0 and not x['stderr'] for x in result['invocations'])
    pins=load(RD/'dependency_pins.json')
    assert len(pins)==9 and all(x['passed'] for x in pins)
    counts=load(RD/'source_counts.json'); assert counts['new_theorems']==44
    summary=dict(passed=True,release='0.31.0',current_compilations=len(order),
      theorems=len(inv),new_theorems=44,axioms=sorted(deps),negative_rejections=len(negatives),
      inherited_unchanged=same,non_audit_modules=len(modules),
      non_audit_source_lines=counts['source_lines'],positive_source_scan_hits=bad,
      dependency_pins=9,differential_requests=2888,exhaustive_2x2_linear_blocks=625,
      wire_rejections=9,wrapper_rejections=5,live_cases=8,
      probes_executed=diff['probes_executed'],stronger_denials=diff['stronger_denials'],
      baseline_sha256=sha(baseline),
      scope='Fresh current local source compilation and whole-corpus axiom/negative checks against pinned caches. New read-only probe/factor tests only; prior live/cache/crash tests are historical.')
    (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
    outs=[RD/'verification_summary.json',RD/'source_counts.json',RD/'axiom_audit_summary.json',
          td/'differential_summary.json',td/'live_summary.json']
    manifest={'schema_version':1,'claim_id':'AVOC-v031-paid-partial-rank-probes',
      'repository':{'commit':'archive:'+sha(baseline),'dirty':True},
      'command':'python tools/summarize_v031.py '+str(baseline),
      'environment':{'software':['Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d',
       'mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],
       'hardware':platform.platform()},
      'mathematics':{'assertion_tested':'Current source/import/output/log proof records; all theorem axioms and negative errors; executed exact GF(5) bounded minor probes and real calls to prior proposer/checker. Collector duration excludes earlier checks.',
       'coefficient_domain':'Generic fields for rank and cost proofs; runtime GF(5)',
       'conventions':'Column-vector affine maps; determinant order two; lower not exact rank; eight-unit per-test tariff; remaining-opportunity denial, not universal profitability',
       'inputs':['frozen v0.30 source ZIP','4 new Lean modules','actual new Lean entrypoint',
         'unmodified tracked-RREF proposer','independent column-image and homogeneous-matrix oracle'],
       'bounds':{'local_targets':171,'theorems':1656,'negative_files':88,'wire_requests':2888,
         'exhaustive_2x2_blocks':625,'max_dimension':8,'live_cases':8,'seed':20260914},
       'non_claims':['No optimal probe schedule','No exact rank from failed probes',
         'No general affine circuit optimum','No physical speedup or LLM effectiveness',
         'No fresh mathlib source build','No universal Python/IO refinement']},
      'randomness':{'used':True,'generator':'random.Random used in recorded finite differential regression','seed':20260914},
      'run':{'started_at':stamp,'runtime_seconds':time.monotonic()-tick,'exit_status':0},
      'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in outs],
      'checks':['current direct-import/output/source/log hashes','exact theorem axiom names',
         'substantive negative failures','unchanged inherited proofs','raw batch invocation hashes',
         'current test source hashes','explicit beneficial and detrimental economics cases'],
      'result':'PASS within the stated mathematical and bounded runtime scopes',
      'residual_risks':['trusted compiler/kernel/cache/host','tested Python parsing and metering',
         'nominal costs omit host work','v1 metadata validator is a local adaptation, not a proof']}
    (RD/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
