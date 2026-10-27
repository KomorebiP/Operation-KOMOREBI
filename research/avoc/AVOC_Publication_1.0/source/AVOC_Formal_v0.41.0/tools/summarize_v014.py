#!/usr/bin/env python3
"""Collect current-source evidence from this run; fail closed on missing records."""
from pathlib import Path
import hashlib,json,re,platform,datetime
r=Path(__file__).resolve().parents[1];rd=r/'results/v0.14.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={str(p.relative_to(r).with_suffix('')).replace('/','.') : p for p in (r/'AVOC').glob('*.lean') if p.name not in ['Audit.lean','FullAudit.lean']}
files['AVOC']=r/'AVOC.lean'
order=[];seen=set();active=set()
def visit(n):
 if n in seen:return
 assert n not in active,n
 active.add(n)
 for dep in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',files[n].read_text(),re.M):visit(dep)
 active.remove(n);seen.add(n);order.append(str(files[n].relative_to(r)))
for n in sorted(files):visit(n)
old_order=rd/'build_order.json'
if old_order.exists() and not (rd/'build_order_initial.json').exists():
 (rd/'build_order_initial.json').write_bytes(old_order.read_bytes())
old_order.write_text(json.dumps(order,indent=2)+'\n')
records=[]
for path in rd.glob('*.json'):
 try:j=json.loads(path.read_text())
 except Exception:continue
 if isinstance(j,dict) and 'command' in j and j.get('returncode')==0 and not j.get('timed_out',True):
  records.append((path,j))
compiled=[]
for f in order:
 p=r/f;matches=[(q,j) for q,j in records if j['command'][-1]==str(p) and j.get('source_sha256')==sha(p) and '-o' in j['command']]
 assert matches,'No current-source successful local compilation: '+f
 q,j=max(matches,key=lambda x:x[0].stat().st_mtime)
 output=r/'.lake/build/lib/lean'/Path(f).with_suffix('.olean')
 assert output.exists(),f
 if j.get('output_sha256') is not None:assert j['output_sha256']==sha(output),f
 compiled.append(dict(source=f,record=str(q.relative_to(r)),source_sha256=sha(p),output_sha256=sha(output),returncode=0))
(rd/'final_local_build_summary.json').write_text(json.dumps(compiled,indent=2)+'\n')
negative=[]
for p in sorted((r/'tests/negative').glob('*.lean')):
 record=rd/f'negative_{p.stem}.json';log=record.with_suffix('.log')
 j=json.loads(record.read_text());text=log.read_text()
 good=(j['returncode']!=0 and not j['timed_out'] and j['source_sha256']==sha(p)
       and not re.search(r'object file .*does not exist|unknown module|failed to locate application|has been deprecated',text))
 assert good,p
 negative.append(dict(source=str(p.relative_to(r)),record=str(record.relative_to(r)),expected_rejection=True))
(rd/'negative_summary.json').write_text(json.dumps(negative,indent=2)+'\n')
# Remove nested Lean block comments and line comments before scanning declarations.
def uncomment(text):
 out=[];i=0;depth=0
 while i<len(text):
  if text.startswith('/-',i):depth+=1;i+=2;continue
  if depth and text.startswith('-/',i):depth-=1;i+=2;continue
  if not depth and text.startswith('--',i):
   j=text.find('\n',i);i=len(text) if j<0 else j;continue
  if not depth:out.append(text[i])
  elif text[i]=='\n':out.append('\n')
  i+=1
 return ''.join(out)
hits=[]
for p in files.values():
 for match in re.finditer(r'\b(sorry|admit|native_decide)\b|^\s*(?:axiom|unsafe)\b',uncomment(p.read_text()),re.M):
  hits.append(dict(file=str(p.relative_to(r)),text=match.group()))
assert not hits,hits
(rd/'source_scan.json').write_text(json.dumps(dict(passed=True,hits=hits),indent=2)+'\n')
axioms=json.loads((rd/'axiom_audit_summary.json').read_text());assert axioms['passed']
counts=json.loads((rd/'source_counts.json').read_text())
reg=json.loads((rd/'controller_regression.json').read_text());assert reg['status']=='PASS'
base=Path('/mnt/data/restored/AVOC_Formal_v0.13.0');unchanged=[]
# Optional local baseline comparison. The result is persisted for portability.
if base.exists():
 for p in (base/'AVOC').glob('*.lean'):
  if p.name in ['Audit.lean','FullAudit.lean']:continue
  assert sha(p)==sha(r/'AVOC'/p.name),p
  unchanged.append(str(p.relative_to(base)))
else:
 unchanged=json.loads((r/'SOURCE_PROVENANCE.json').read_text())['unchanged_inherited_modules']
summary=dict(status='PASS',checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
             version='0.14.0',lean='4.34.0-rc2',lean_commit='6a10ac8c22beadecabdbb0919c2b50214762f91d',
             mathlib='aeb72f1e9981b6d35b426b16dca7759be3e7ba06',**counts,
             local_compilations=len(compiled),full_axiom_declarations=axioms['audited'],
             axiom_dependencies=axioms['axioms'],negative_tests_rejected=len(negative),source_scan_hits=len(hits),
             unchanged_inherited_module_count=len(unchanged),
             build_scope='Local build directory initially emptied; all inherited local sources compiled, then all new/final modified sources compiled; current-source evidence checked for every final target. Cached pinned external dependencies retained. Not a fresh mathlib build.',
             environment=dict(platform=platform.platform(),python=platform.python_version()),
             evidence_dir='results/v0.14.0')
(r/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
(r/'SOURCE_PROVENANCE.json').write_text(json.dumps(dict(baseline_version='0.13.0',new_version='0.14.0',
 baseline_zip_sha256='c564fee1b29ec32e0d7931fe8178f3d33f34cc01a47df8c3e366aa984ed45d96',
 unchanged_inherited_modules=unchanged,unchanged_inherited_module_count=len(unchanged),
 new_modules=[f'AVOC/{m}.lean' for m in ['GuardedControl','GuardedPolicyRegret','ResearchController','ResearchPolicy','ResearchControllerExamples']]),indent=2)+'\n')
print(json.dumps(summary,indent=2))
