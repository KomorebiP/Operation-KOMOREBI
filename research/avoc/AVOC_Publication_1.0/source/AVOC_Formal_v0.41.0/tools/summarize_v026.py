#!/usr/bin/env python3
"""Verify current source/compiler/test evidence. Does not count history as a fresh run."""
from pathlib import Path
import argparse,hashlib,json,re,sys,zipfile
from summarize_v022 import without_comments
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.26.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path);a=ap.parse_args()
 builds=[]
 for f in read(RD/'build_order.json'):
  p=ROOT/f;artifact=ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean');r=read(RD/f'clean_{p.stem}.json')
  require(r['returncode']==0 and not r['timed_out'],'bad build '+f)
  require(r['source_unchanged'] and r['imports_unchanged'],'changed build input '+f)
  require(r['source_sha256']==sha(p) and r['output_sha256']==sha(artifact),'stale source/output '+f)
  require(r['log_sha256']==sha(ROOT/r['log']),'stale build log '+f)
  imports={n:sha(ROOT/'.lake/build/lib/lean'/Path(n.replace('.','/')).with_suffix('.olean')) for n in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',p.read_text(),re.M)}
  require(r['import_outputs']==imports,'stale imported output '+f)
  builds.append(f)
 r=read(RD/'full_axiom_audit.json');text=(RD/'full_axiom_audit.log').read_text()
 require(r['returncode']==0 and not r['timed_out'],'audit failed')
 require(r['source_sha256']==sha(ROOT/'AVOC/FullAudit.lean') and r['log_sha256']==sha(RD/'full_axiom_audit.log'),'stale audit')
 require(r['import_outputs']=={'AVOC':sha(ROOT/'.lake/build/lib/lean/AVOC.olean')},'stale aggregate audit')
 names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
 inv=read(RD/'declaration_inventory.json')
 require(len(names)==len(inv) and set(names)=={x['qualified_name'] for x in inv},'audit name mismatch')
 axioms=set()
 for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):axioms.update(x.strip() for x in block.split(',') if x.strip())
 require(axioms<={'propext','Classical.choice','Quot.sound'},'unapproved axiom')
 negative=[]
 for p in sorted((ROOT/'tests/negative').glob('*.lean')):
  r=read(RD/f'negative_{p.stem}.json');s=(ROOT/r['log']).read_text()
  require(r['returncode']!=0 and not r['timed_out'],'negative did not finish rejecting '+p.name)
  require(r['source_sha256']==sha(p) and r['log_sha256']==sha(ROOT/r['log']),'stale negative '+p.name)
  require(not re.search(r'object file .*does not exist|unknown module|failed to locate application',s),'negative setup failure '+p.name)
  require('error' in s,'no substantive negative diagnostic '+p.name)
  negative.append(p.name)
 inherited=read(RD/'inherited_source_hashes.json')
 for name,digest in inherited.items():require(sha(ROOT/name)==digest,'changed inherited module '+name)
 baseline_digest=None
 if a.baseline:
  with zipfile.ZipFile(a.baseline) as z:
   require(z.testzip() is None,'bad baseline archive')
   for name,digest in inherited.items():require(hashlib.sha256(z.read('AVOC_Formal_v0.25.0/'+name)).hexdigest()==digest,'wrong baseline source '+name)
  baseline_digest=sha(a.baseline)
 census=[];forbidden=[]
 for p in (ROOT/'AVOC').glob('*.lean'):
  if p.name in ('Audit.lean','FullAudit.lean'):continue
  s=without_comments(p.read_text());census+=re.findall(r'^(?:@\[[^\]]+\]\s*)?(?:theorem|lemma)\s+([^\s(]+)',s,re.M)
  for pat in [r'\bsorry\b',r'\bnative_decide\b',r'(?m)^\s*(?:unsafe\s+|axiom\s+)',r'(?m)^\s*admit\s*$',r':=\s*admit\b']:
   if re.search(pat,s):forbidden.append((str(p.relative_to(ROOT)),pat))
 require(not forbidden,'forbidden proof shortcut');require(len(census)==len(inv),'independent census mismatch')
 tests=read(RD/'semantic_tests/summary.json')
 require(tests['passed'] and tests['source_pins_before']==tests['source_pins_after'],'bad semantic regression')
 for name,digest in tests['source_pins_after'].items():require(sha(ROOT/name)==digest,'stale semantic test input '+name)
 for p in (RD/'semantic_tests').glob('*_run.json'):
  r=read(p);prefix=p.name.removesuffix('_run.json')
  require(r['returncode']==0,'failed test subprocess')
  for suffix,key in [('_requests.json','input_sha256'),('_stdout.jsonl','stdout_sha256'),('_stderr.txt','stderr_sha256')]:
   require(sha(p.with_name(prefix+suffix))==r[key],'changed test evidence '+prefix)
 cli=read(RD/'cli/summary.json');require(cli['passed'],'bad CLI tests')
 require(cli['wrapper_sha256']==sha(ROOT/'tools/run_semantic_synthesis.py'),'wrapper changed since execution')
 require(cli['recorder_sha256']==sha(ROOT/'tools/record_semantic_cli.py'),'CLI recorder changed')
 for c in cli['cases']:
  require(c['passed'] and c['returncode']==c['expected'],'CLI result mismatch')
  require(sha(ROOT/c['output_path'])==c['output_sha256'],'CLI output changed')
 pins=read(RD/'dependency_pins.json');require(len(pins)==9 and all(x['passed'] for x in pins),'dependency pins mismatch')
 summary=dict(passed=True,new_theorems=len(read(RD/'new_declarations.json')),total_theorems=len(inv),local_targets=len(builds),
  axiom_reports=len(names),axioms=sorted(axioms),negative_rejections=len(negative),inherited_modules_unchanged=len(inherited),
  baseline_sha256=baseline_digest,source_scan_hits=forbidden,source_counts=read(RD/'source_counts.json'),
  query_cases=tests['query_cases'],budget_cases=tests['budget_cases'],equivalence_cases=tests['equivalence_cases'],
  campaign_cases=tests['campaign_cases'],invalid_wire_cases=tests['invalid_wire_cases'],cli_cases=len(cli['cases']),
  matched_depth2=tests['builds'][4:6],depth3=tests['builds'][6],timings=tests['timing_runs'],median_seconds=tests['median_seconds'],
  scope='current local-source compilation against pinned external caches; actual Lean semantic synthesis and read-only CLI tests; inherited live/crash suites not rerun')
 (RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (RD/'negative_final.json').write_text(json.dumps(negative,indent=2)+'\n')
 (ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
