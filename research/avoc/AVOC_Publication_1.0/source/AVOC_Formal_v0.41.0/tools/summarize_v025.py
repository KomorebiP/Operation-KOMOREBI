#!/usr/bin/env python3
"""Check current compilation/axiom/test evidence before packaging v0.25."""
from pathlib import Path
import argparse,hashlib,json,re,sys,zipfile
from summarize_v022 import without_comments
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.25.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def require(h,msg):
 if not h:raise RuntimeError(msg)
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);a=p.parse_args()
 builds=[]
 for f in read(RD/'build_order.json'):
  source=ROOT/f;out=ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean')
  r=read(RD/f'clean_{source.stem}.json')
  require(r['returncode']==0 and not r['timed_out'],'bad build '+f)
  require(r['source_unchanged'] and r['imports_unchanged'],'changed build inputs '+f)
  require(r['source_sha256']==sha(source) and r['output_sha256']==sha(out),'stale source/output '+f)
  require(r['log_sha256']==sha(ROOT/r['log']),'changed build log '+f)
  imports={name:sha(ROOT/'.lake/build/lib/lean'/Path(name.replace('.','/')).with_suffix('.olean'))
   for name in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',source.read_text(),re.M)}
  require(r['import_outputs']==imports,'stale direct import '+f)
  builds.append(f)
 audit=read(RD/'full_axiom_audit.json'); text=(RD/'full_axiom_audit.log').read_text()
 require(audit['returncode']==0 and not audit['timed_out'],'failed axiom audit')
 require(audit['source_sha256']==sha(ROOT/'AVOC/FullAudit.lean') and
         audit['log_sha256']==sha(RD/'full_axiom_audit.log'),'stale audit')
 require(audit['import_outputs']=={'AVOC':sha(ROOT/'.lake/build/lib/lean/AVOC.olean')},'stale audit imports')
 names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
 inv=read(RD/'declaration_inventory.json')
 require(len(names)==len(inv) and set(names)=={r['qualified_name'] for r in inv},'theorem set mismatch')
 axioms=set()
 for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):axioms.update(x.strip() for x in block.split(',') if x.strip())
 require(axioms<={'propext','Classical.choice','Quot.sound'},'unexpected axiom')
 negatives=[]
 for f in sorted((ROOT/'tests/negative').glob('*.lean')):
  r=read(RD/f'negative_{f.stem}.json'); log=ROOT/r['log']; s=log.read_text()
  require(r['returncode']!=0 and not r['timed_out'],'negative was not rejected '+f.name)
  require(r['source_sha256']==sha(f) and r['log_sha256']==sha(log),'stale negative '+f.name)
  require(not re.search(r'object file .*does not exist|unknown module|failed to locate application',s),'setup failure '+f.name)
  require('error' in s,'no negative diagnostic '+f.name)
  negatives.append(f.name)
 inherited=[]
 with zipfile.ZipFile(a.baseline) as z:
  require(z.testzip() is None,'bad baseline zip')
  for n in z.namelist():
   if re.match(r'[^/]+/AVOC/[^/]+\.lean$',n) and Path(n).name not in ['FullAudit.lean','Audit.lean']:
    rel='/'.join(n.split('/')[1:]);require((ROOT/rel).read_bytes()==z.read(n),'inherited source changed '+rel);inherited.append(rel)
 forbidden=[];census=[]
 for f in (ROOT/'AVOC').glob('*.lean'):
  if f.name in ['Audit.lean','FullAudit.lean']:continue
  code=without_comments(f.read_text())
  census+=re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',code,re.M)
  for pat in [r'\bsorry\b',r'\bnative_decide\b',r'(?m)^\s*(?:unsafe\s+|axiom\s+)',r'(?m)^\s*admit\s*$',r':=\s*admit\b']:
   if re.search(pat,code):forbidden.append([str(f.relative_to(ROOT)),pat])
 require(not forbidden,'forbidden shortcut')
 require(len(census)==len(inv),'independent source census mismatch')
 # Test provenance is tied to the final source and retained output bytes.
 for mode in ['differential','live']:
  rec=read(RD/(mode+'_provenance.json'))
  require(rec['passed'] and rec['returncode']==0 and rec['sources_unchanged'],'failed fresh tests '+mode)
  require(rec['sources_before']==rec['sources_after'],'test inputs changed '+mode)
  for rel,expected in rec['sources_after'].items():require(sha(ROOT/rel)==expected,'stale test source '+rel)
  for rel,expected in rec['outputs'].items():require(sha(ROOT/rel)==expected,'stale test output '+rel)
 diff=read(RD/'differential_summary.json'); live=read(RD/'live_summary.json')
 require(diff['campaign_cases']==747 and diff['direct_checker_cases']==255,'incomplete differential range')
 require(diff['invalid_wire_cases']==10,'missing invalid-wire tests')
 require(live['case_count']==16 and all(x['passed'] for x in live['cases']),'incomplete live suite')
 sys.path.insert(0,str(ROOT/'checks'));import test_synthesis as suite
 checked=0
 for request in sorted(RD.glob('differential_*_requests.json')):
  tag=request.name.removesuffix('_requests.json')
  rs=read(request); outs=[json.loads(x) for x in (RD/(tag+'_stdout.jsonl')).read_text().splitlines()]
  require(len(rs)==len(outs),'retained oracle length mismatch')
  for wire,out in zip(rs,outs):
   require(out['status']=='checked','retained campaign rejected')
   expected=suite.oracle(wire[1])
   for key,value in expected.items():
    if key in ['valid_candidates','invalid_candidates','strict_improvements']:continue
    require(out.get(key)==value,'retained oracle mismatch '+key)
   checked+=1
 require(checked==747,'wrong retained campaign count')
 pins=read(RD/'dependency_pins.json');require(len(pins)==9 and all(x['passed'] for x in pins),'dependency pins failed')
 import synthesize_upgrade;synthesize_upgrade.environment()
 summary=dict(passed=True,baseline_sha256=sha(a.baseline),new_theorems=len(read(RD/'new_declarations.json')),
  total_theorems=len(inv),local_targets=len(builds),negative_tests=len(negatives),inherited_modules=len(inherited),
  axioms=sorted(axioms),source_scan_hits=forbidden,differential_cases=diff['campaign_cases'],
  direct_checker_cases=diff['direct_checker_cases'],invalid_wire_cases=diff['invalid_wire_cases'],
  all_input_execution_checks=diff['full_input_execution_checks'],live_cases=live['case_count'],
  source_lines=read(RD/'source_counts.json')['source_lines'],
  current_test_hash=sha(ROOT/'checks/test_synthesis.py'),
  verification_scope='current-source local compilation and final pinned test suites; pinned external caches retained; old live suites historical')
 (RD/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
