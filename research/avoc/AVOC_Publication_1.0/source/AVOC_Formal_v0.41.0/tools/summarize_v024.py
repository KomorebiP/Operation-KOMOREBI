#!/usr/bin/env python3
"""Check current compilation/axiom/test evidence before packaging v0.24."""
from pathlib import Path
import argparse,hashlib,json,re,sys,zipfile
from summarize_v022 import without_comments
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.24.0'
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
 tests=ROOT/'results/v0.24.0/tests'
 sys.path.insert(0,str(ROOT/'checks'))
 import test_durable_upgrade as suite
 live=[]
 for name in suite.NAMES:
  record=read(tests/(name+'.json'))
  require(record['passed'],'live failure '+name)
  require(record['test_source_sha256']==sha(ROOT/'checks/test_durable_upgrade.py'),'changed live test source '+name)
  require(record['implementation_sha256']==sha(ROOT/'tools/durable_upgrade_campaign.py'),'changed implementation '+name)
  live.append(record)
 diff=read(tests/'differential.json')
 require(diff['passed'] and diff['cases']==1404,'incomplete oracle range')
 inputs=read(tests/'oracle_requests.json'); outputs=read(tests/'oracle_stdout.json')
 require(len(inputs)==len(outputs)==diff['cases'],'oracle length mismatch')
 # Reconstruct expected results independently from the retained request data.
 for index,(wire,out) in enumerate(zip(inputs,outputs)):
  credit,events,actual,command=wire[1],wire[2],wire[3],wire[4]
  replayed=suite.initial()
  try:
   for event in events:replayed=suite.oracle(credit,replayed,event)[0]
   if replayed!=actual:raise ValueError('log/checkpoint mismatch')
   new,changed,ev,sw=suite.oracle(credit,actual,command) if command is not None else (actual,False,0,0)
   require(out.get('status')=='checked' and out.get('journal')==new and out.get('changed')==changed and out.get('evaluation_debit')==ev and out.get('switch_debit')==sw,'oracle mismatch '+str(index))
  except ValueError as e:
   require(out.get('status')=='error' and out.get('error')==str(e),'oracle rejection mismatch '+str(index))
 pins=read(RD/'dependency_pins.json');require(len(pins)==9 and all(x['passed'] for x in pins),'dependency pins failed')
 import durable_upgrade_campaign
 durable_upgrade_campaign.environment()
 summary=dict(passed=True,baseline_sha256=sha(a.baseline),new_theorems=len(read(RD/'new_declarations.json')),
  total_theorems=len(inv),local_targets=len(builds),negative_tests=len(negatives),inherited_modules=len(inherited),
  axioms=sorted(axioms),source_scan_hits=forbidden,differential_cases=diff['cases'],
  accepted_oracle_cases=diff['accepted'],rejected_oracle_cases=diff['rejected'],
  live_cases=len(live),process_exit_scenarios=sum('crash' in x['name'] for x in live),
  protected_source_files=len(read(ROOT/'durable_upgrade_source_pins.json')['sources']),
  current_test_hash=sha(ROOT/'checks/test_durable_upgrade.py'),
  oracle_requests_sha256=sha(tests/'oracle_requests.json'),oracle_outputs_sha256=sha(tests/'oracle_stdout.json'),
  verification_scope='fresh local compilation and current tests against pinned external caches; older filesystem/recovery suites not rerun')
 (RD/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
