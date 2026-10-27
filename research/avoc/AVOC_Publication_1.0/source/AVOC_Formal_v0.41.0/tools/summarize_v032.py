#!/usr/bin/env python3
"""Validate v0.32 proof/runtime evidence. Collector time is not total run time."""
from __future__ import annotations
import datetime,hashlib,json,platform,re,sys,time,zipfile
from pathlib import Path
from summarize_v029 import check_record,strip_comments_strings
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.32.0'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def main():
 stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();tick=time.monotonic()
 baseline=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'AVOC_Formal_v0.31.0.zip'
 order=load(RD/'build_order.json');assert len(order)==len(set(order))==176
 for f in order:check_record(load(RD/f'clean_{Path(f).stem}.json'),f,ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean'))
 inv=load(RD/'declaration_inventory.json');expected={x['qualified_name'] for x in inv};assert len(inv)==len(expected)==1692
 check_record(load(RD/'full_axiom_audit.json'),'AVOC/FullAudit.lean')
 text=(RD/'full_axiom_audit.log').read_text();names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
 assert len(names)==len(expected) and set(names)==expected
 deps=set()
 for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):deps.update(x.strip() for x in block.split(',') if x.strip())
 assert deps<={'propext','Classical.choice','Quot.sound'}
 negs=sorted((ROOT/'tests/negative').glob('*.lean'));assert len(negs)==91
 for f in negs:
  rec=load(RD/f'negative_{f.stem}.json');log=(ROOT/rec['log']).read_text()
  assert rec['returncode']!=0 and not rec['timed_out'] and 'error' in log,f
  assert not re.search(r'object file .*does not exist|unknown module|failed to locate application',log),f
  assert rec['source_unchanged'] and rec['imports_unchanged'] and rec['source_sha256']==sha(f)
  assert rec['log_sha256']==sha(ROOT/rec['log'])
  for name,d in rec['import_outputs'].items():assert sha(ROOT/'.lake/build/lib/lean'/Path(name.replace('.','/')).with_suffix('.olean'))==d
 same=0
 with zipfile.ZipFile(baseline) as z:
  assert z.testzip() is None
  prefix='AVOC_Formal_v0.31.0/'
  for name in z.namelist():
   rel=name.removeprefix(prefix)
   if rel.startswith('AVOC/') and rel.endswith('.lean') and Path(rel).name not in ['Audit.lean','FullAudit.lean']:
    assert z.read(name)==(ROOT/rel).read_bytes(),rel;same+=1
 assert same==152
 modules=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']]
 bad=[];census=[]
 for p in modules:
  source=strip_comments_strings(p.read_text())
  hits=re.findall(r'\b(?:sorry|native_decide|axiom|unsafe)\b|\bby\s+admit\b|^\s*admit\s*$',source,re.M)
  if hits:bad.append([p.name,hits])
  census.extend(re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',source,re.M))
 assert not bad and len(census)==len(inv)
 td=RD/'adaptive_probe_tests';diff=load(td/'differential_summary.json');live=load(td/'live_summary.json')
 assert diff['passed'] and diff['requests']==322 and diff['wire_rejections']==6
 assert live['passed'] and live['live_cases']==3
 requests=load(td/'differential_requests.json');outputs=load(td/'differential_outputs.json');runs=load(td/'differential_invocations.json')
 assert len(requests)==len(outputs)==322
 cursor=0
 for rec in runs[:-1]:
  size=min(100,len(requests)-cursor);raw=(json.dumps(requests[cursor:cursor+size],separators=(',',':'))+'\n').encode()
  stdout=''.join(json.dumps(x,separators=(',',':'),ensure_ascii=False)+'\n' for x in outputs[cursor:cursor+size]).encode()
  assert rec['returncode']==0 and not rec['stderr'];assert hashlib.sha256(raw).hexdigest()==rec['request_sha256'];assert hashlib.sha256(stdout).hexdigest()==rec['stdout_sha256'];cursor+=size
 assert cursor==len(requests)
 invalid=load(td/'invalid_outputs.json');assert len(invalid)==6
 raw=(json.dumps([['bad'],['adaptive-rank-probe-f5-v1',2,2,[],[],[],1,1,[]],['adaptive-rank-probe-f5-v1',2,2,[[[1,0],[0,1]]],[[0,2,0,1]],[1],1,1,[]],['adaptive-rank-probe-f5-v1',2,2,[[[1,0],[0,1]]],[[0,1,0,1]],[],1,1,[]],['adaptive-rank-probe-f5-v1',2,2,[[[1,0],[0,1]]],[[0,1,0,1]],[1],1,9,[]],['adaptive-rank-probe-f5-v1',2,2,[[[1,0],[0,1]]],[[0,1,0,1]],[1],1,1,[[0,False]]]],separators=(',',':'))+'\n').encode()
 stdout=''.join(json.dumps(x,separators=(',',':'),ensure_ascii=False)+'\n' for x in invalid).encode()
 assert hashlib.sha256(raw).hexdigest()==runs[-1]['request_sha256'] and hashlib.sha256(stdout).hexdigest()==runs[-1]['stdout_sha256']
 for stage in ['differential','live']:
  r=load(td/f'{stage}_source_record.json');assert r['unchanged'] and r['input_source_before']==r['input_source_after']
  for name,d in r['input_source_after'].items():assert sha(ROOT/name)==d
 pins=load(RD/'dependency_pins.json');assert len(pins)==9 and all(x['passed'] for x in pins)
 counts=load(RD/'source_counts.json');assert counts['new_theorems']==36 and counts['total_theorems']==1692
 summary=dict(passed=True,release='0.32.0',current_compilations=len(order),theorems=len(inv),new_theorems=36,
  axioms=sorted(deps),negative_rejections=len(negs),inherited_unchanged=same,non_audit_modules=len(modules),
  non_audit_source_lines=counts['source_lines'],positive_source_scan_hits=bad,dependency_pins=9,
  differential_requests=322,wire_rejections=6,live_cases=3,positive_probe_choices=diff['positive_probe_choices'],
  baseline_sha256=sha(baseline),scope='Fresh local source compilation and whole-corpus axiom/negative checks against pinned caches. New read-only finite-catalogue adaptive probe tests only; older live/cache/crash suites are historical.')
 (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n');(ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
 outs=[RD/'verification_summary.json',RD/'source_counts.json',RD/'axiom_audit_summary.json',td/'differential_summary.json',td/'live_summary.json']
 manifest={'schema_version':1,'claim_id':'AVOC-v032-adaptive-paid-rank-probes','repository':{'commit':'archive:'+sha(baseline),'dirty':True},
  'command':'python tools/summarize_v032.py '+str(baseline),'environment':{'software':['Lean 4.34.0-rc2 6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06','Python '+platform.python_version()],'hardware':platform.platform()},
  'mathematics':{'assertion_tested':'Current proof records plus exact finite-catalogue adaptive probe codec/evaluator regression. Universal optimality is a separate Lean theorem.','coefficient_domain':'Generic finite catalogue and rational control; rank specialization over fields; runtime GF(5)','conventions':'Uniform retained catalogue; duplicate worlds encode integer weights; Boolean deterministic probe reports; terminal operational benefit; first action wins ties','inputs':['frozen v0.31 source ZIP','4 new Lean modules','actual Lean JSON entrypoint','independent determinant-table Fraction-DP oracle'],'bounds':{'local_targets':176,'theorems':1692,'negative_files':91,'wire_requests':322,'world_cap':32,'probe_cap':16,'horizon_cap':8,'seed':20260914},'non_claims':['No real workload calibration','No noisy probes','No exact rank from failed probes','No efficient general planner','No physical speedup or LLM productivity','No fresh mathlib source build']},
  'randomness':{'used':True,'generator':'random.Random for bounded differential catalogues','seed':20260914},'run':{'started_at':stamp,'runtime_seconds':time.monotonic()-tick,'exit_status':0},
  'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in outs],'checks':['current source/import/output/log hashes','exact theorem axiom inventory','substantive negative failures','byte-identical inherited proof modules','raw request/output hashes','independent exact dynamic programming oracle'],'result':'PASS within stated theorem and bounded runtime scopes','residual_risks':['trusted Lean/compiler/cache/host','tested Python/JSON adapter','supplied catalogue/fees/benefit','exhaustive planner cost','v1 computation metadata is not proof']}
 (RD/'computation_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
