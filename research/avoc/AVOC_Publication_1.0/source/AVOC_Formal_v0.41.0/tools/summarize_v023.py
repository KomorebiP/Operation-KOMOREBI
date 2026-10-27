#!/usr/bin/env python3
"""Check current compilation/axiom/test evidence before packaging v0.23."""
from pathlib import Path
import argparse,hashlib,json,re,sys,zipfile
from summarize_v022 import without_comments
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.23.0'
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
 reports=sorted((read(p) for p in RD.glob('upgrade_test_*.json')),key=lambda r:r['start'])
 expected=0
 for r in reports:
  require(r['passed'] and r['start']==expected,'test slice gap')
  require(r['test_source_sha256']==sha(ROOT/'checks/test_upgrade_campaign.py'),'test source changed')
  require(r['request_sha256']==sha(RD/f"upgrade_requests_{r['start']:04d}.json"),'changed request')
  require(r['output_sha256']==sha(RD/f"upgrade_output_{r['start']:04d}.jsonl"),'changed output')
  expected+=r['count']
 require(reports and expected==reports[0]['total_cases'],'missing test cases')
 defense=read(RD/'upgrade_defense_tests.json');require(defense['passed'],'defense failed')
 require(defense['test_source_sha256']==sha(ROOT/'checks/test_upgrade_campaign.py'),'stale defense')
 pins=read(RD/'dependency_pins.json');require(all(x['passed'] for x in pins),'dependency pins failed')
 import run_upgrade_campaign
 run_upgrade_campaign.checked_environment()
 summary=dict(passed=True,baseline_sha256=sha(a.baseline),new_theorems=len(read(RD/'new_declarations.json')),
  total_theorems=len(inv),local_targets=len(builds),negative_tests=len(negatives),inherited_modules=len(inherited),
  axioms=sorted(axioms),source_scan_hits=forbidden,differential_campaign_cases=expected,
  observed_promotions=sum(r['promotions'] for r in reports),observed_rejections=sum(r['rejections'] for r in reports),
  observed_unfunded=sum(r['unfunded'] for r in reports),wrapper_rejections=len(defense['wrapper_rejections']),
  wire_rejections=defense['raw_wire_rejections'],
  verification_scope='fresh local build and tests against exact cached external dependencies; older live suites not rerun')
 (RD/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
