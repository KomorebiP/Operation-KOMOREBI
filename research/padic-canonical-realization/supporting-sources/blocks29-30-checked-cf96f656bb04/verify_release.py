#!/usr/bin/env python3
"""Read-only evidence replay. This does not run a fresh Lean build."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent
ALLOWED={'propext','Quot.sound','Classical.choice'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def parse_kernel_axioms(text):
 rows=[]
 for line in text.splitlines():
  if not line.startswith('PROJECT_AXIOMS '):continue
  fields=line[len('PROJECT_AXIOMS '):].split('|')
  if len(fields)!=3 or not fields[0].strip() or not fields[1].strip():
   raise ValueError('Malformed kernel inventory record: '+line)
  name,module,deps=(f.strip() for f in fields)
  rows.append((name,module,[a.strip() for a in deps.split(',') if a.strip()]))
 if len({n for n,m,a in rows})!=len(rows):raise ValueError('Duplicate kernel theorem inventory')
 return rows

def analyze(require_checksums=True):
 errors=[];checks=0
 def ck(ok,why):
  nonlocal checks
  checks+=1
  if not ok:errors.append(why)
 inv=json.loads((ROOT/'verification/theorem_inventory.json').read_text())
 expected=set(inv['names'])
 ck(len(expected)==inv['total']==878,'declared theorem inventory')
 phases=json.loads((ROOT/'verification/final_plan.json').read_text())
 for step in phases:
  label=step['label'];rp=ROOT/'results_current'/f'{label}.json';lp=ROOT/'results_current'/f'{label}.log'
  ck(rp.exists() and lp.exists(),'receipt/log missing '+label)
  if not(rp.exists() and lp.exists()):continue
  r=json.loads(rp.read_text());text=lp.read_text()
  ck(r['exit_status']==step['expected_exit'],label+' exit')
  ck(r['status']==('completed' if step['expected_exit']==0 else 'failed'),label+' completed status')
  ck(r['inputs_unchanged'] and r['inputs_before']==r['inputs_after'],label+' frozen inputs')
  ck(sha(lp)==r['log_sha256'],label+' log checksum')
  for f,h in r['inputs_after'].items():
   p=ROOT/f;ck(p.is_file() and sha(p)==h,label+' current input '+f)
  if 'diagnostic' in step:ck(step['diagnostic'] in text,label+' exact rejection diagnostic')
 axtext=(ROOT/'results_current/final_axioms.log').read_text()
 rows=re.findall(r"'([^'\n]+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)",axtext)
 axioms={name:[a.strip() for a in deps.split(',') if a.strip()] for name,deps in rows}
 ck(set(axioms)==expected and len(rows)==len(expected),'all declared theorem axiom closures')
 ck(set().union(*(set(v) for v in axioms.values()))<=ALLOWED,'declared axioms whitelist')
 ktext=(ROOT/'results_current/final_kernel_inventory.log').read_text()
 krows=parse_kernel_axioms(ktext)
 kernel={n:a for n,m,a in krows}
 ck(expected<=set(kernel),'imported kernel environment covers declared inventory')
 ck(set().union(*(set(v) for v in kernel.values()))<=ALLOWED,'all project theorem constants whitelist')
 for n in expected:ck(set(axioms.get(n,[]))==set(kernel.get(n,[])),'dual axiom audit '+n)
 preservation=json.loads((ROOT/'PREDECESSOR_SOURCE_PRESERVATION.json').read_text())
 for row in preservation['rows']:ck(sha(ROOT/row['path'])==row['sha256'],'preserved predecessor '+row['path'])
 new=['PrimePowerIdeals','PrimePowerIdealValuation','CoordinateIdealClosure','IdealMaskAutomaton','CyclicIdealCoordinates','CyclicMaskAutomaton','IdealClosureExamples']
 ck(len(list((ROOT/'lean').rglob('*.lean')))==75,'production module count')
 for f in (ROOT/'lean').rglob('*.lean'):
  # Source guard supplements, rather than replaces, the transitive axiom audit.
  s=re.sub(r'/\-.*?\-/','',f.read_text(),flags=re.S);s=re.sub(r'--[^\n]*','',s)
  ck(not re.search(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',s),'source guard '+f.name)
 ck(len(list((ROOT/'compiled').rglob('*.olean')))==75,'compiled oleans')
 ck(len(list((ROOT/'compiled').rglob('*.ilean')))==75,'compiled ileans')
 for fn in ['generic_ideal_audit_result.json','mask_ideal_audit_result.json']:
  d=json.loads((ROOT/'results_current'/fn).read_text());ck(d['status']=='PASS',fn+' finite status')
 for row in json.loads((ROOT/'compiled/ARTIFACT_HASHES.json').read_text()):
  ck(sha(ROOT/'compiled'/row['path'])==row['sha256'],'compiled artifact '+row['path'])
 ck('Build completed successfully' in (ROOT/'results_current/final_build.log').read_text(),'clean integrated build completion')
 if require_checksums:
  entries={}
  for line in (ROOT/'CHECKSUMS.sha256').read_text().splitlines():
   h,p=line.split('  ',1);q=Path(p);entries[p]=h
   ck(not q.is_absolute() and '..' not in q.parts,'safe checksum path '+p)
   ck((ROOT/q).is_file() and sha(ROOT/q)==h,'checksum '+p)
  actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and '.lake' not in p.relative_to(ROOT).parts and not str(p.relative_to(ROOT)).startswith('verification/__pycache__/')}
  ck(actual==set(entries)|{'CHECKSUMS.sha256'},'exact released file inventory')
 return {'status':'PASS' if not errors else 'FAIL','checks':checks,'errors':errors,'declared_theorems':len(axioms),'project_theorem_constants':len(kernel),'axiom_free_declared':sum(not a for a in axioms.values()),'observed_axioms':sorted(set().union(*(set(a) for a in kernel.values()))),'scope':'read-only retained evidence, hash preservation, and axiom coverage; not a fresh compiler run'}
if __name__=='__main__':
 try:out=analyze(require_checksums='--unsealed' not in sys.argv)
 except Exception as e:out={'status':'FAIL','errors':[repr(e)]}
 print(json.dumps(out,indent=2));sys.exit(out['status']!='PASS')
