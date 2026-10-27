#!/usr/bin/env python3
"""Validate current-source compilation, axioms, negative tests and crash evidence."""
from pathlib import Path
import hashlib,json,re,sys,zipfile,argparse
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.20.0'
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,default=Path('/mnt/data/AVOC_Formal_v0.19.0.zip'));args=ap.parse_args()
sys.path.insert(0,str(ROOT/'tools'))
import run_recoverable_workflow as live

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def demand(b,msg):
    if not b:raise RuntimeError(msg)

def strip_comments(s):
    out=[];i=0;depth=0
    while i<len(s):
        if depth:
            if s.startswith('/-',i):depth+=1;i+=2
            elif s.startswith('-/',i):depth-=1;i+=2
            else:out.append('\n' if s[i]=='\n' else ' ');i+=1
        elif s.startswith('/-',i):depth=1;i+=2
        elif s.startswith('--',i):
            e=s.find('\n',i);i=len(s) if e<0 else e
        elif s[i]=='"':
            out.append(' ');i+=1
            while i<len(s):
                if s[i]=='\\':i+=2
                elif s[i]=='"':i+=1;break
                else:out.append('\n' if s[i]=='\n' else ' ');i+=1
        else:out.append(s[i]);i+=1
    return ''.join(out)

order=json.loads((RD/'build_order.json').read_text());build=[]
for f in order:
    p=RD/f'clean_{Path(f).stem}.json';r=json.loads(p.read_text())
    demand(r['returncode']==0 and not r['timed_out'] and r['source_unchanged'],'bad compilation '+f)
    demand(r['source_sha256']==sha(ROOT/f),'changed build source '+f)
    demand(r['log_sha256']==sha(ROOT/r['log']),'changed log '+f)
    out=ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean')
    demand(r['output_sha256']==sha(out),'changed output '+f)
    build.append(dict(source=f,**r))
(RD/'final_local_build_summary.json').write_text(json.dumps(build,indent=2)+'\n')
inv=json.loads((RD/'declaration_inventory.json').read_text())
audit=json.loads((RD/'axiom_audit_summary.json').read_text())
ar=json.loads((RD/'full_axiom_audit.json').read_text())
demand(ar['source_sha256']==sha(ROOT/'AVOC/FullAudit.lean') and ar['returncode']==0,'stale axiom run')
demand(ar['log_sha256']==sha(ROOT/ar['log']),'axiom log changed')
demand(audit['passed'] and audit['audited']==len(inv) and audit['expected']==len(inv),'audit census')
files=[p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ('Audit.lean','FullAudit.lean')]
scans=[];decls=0
for p in files:
    stripped=strip_comments(p.read_text())
    bad=re.findall(r'\b(?:sorry|native_decide)\b|^\s*(?:axiom|unsafe)\b|\bby\s+admit\b|^\s*admit(?:\s|$)',stripped,re.M)
    demand(not bad,'forbidden source term '+str(p)+' '+str(bad))
    n=len(re.findall(r'\b(?:theorem|lemma)\s+[\w\u0370-\u03ff\u2080-\u209f.\']+',stripped))
    decls+=n;scans.append(dict(source=str(p.relative_to(ROOT)),theorems=n,sha256=sha(p)))
for p in [ROOT/f for f in order if f.startswith('tools/')]:
    stripped=strip_comments(p.read_text())
    bad=re.findall(r'\b(?:sorry|native_decide)\b|^\s*(?:axiom|unsafe)\b|\bby\s+admit\b|^\s*admit(?:\s|$)',stripped,re.M)
    demand(not bad,'forbidden trusted entrypoint '+str(p)+' '+str(bad))
demand(decls==len(inv),'independent source count mismatch')
(RD/'source_scan.json').write_text(json.dumps({'declarations':decls,'forbidden_hits':0,'sources':scans},indent=2)+'\n')
neg=[]
for p in sorted((ROOT/'tests/negative').glob('*.lean')):
    r=json.loads((RD/f'negative_{p.stem}.json').read_text());log=(ROOT/r['log']).read_text()
    demand(r['source_sha256']==sha(p) and r['returncode']!=0 and not r['timed_out'],'bad negative '+p.name)
    demand(r['log_sha256']==sha(ROOT/r['log']),'negative log changed')
    demand('error:' in log and not re.search(r'object file .*does not exist|unknown module|failed to locate application',log),
           'setup-only negative '+p.name)
    neg.append(dict(source=str(p.relative_to(ROOT)),**r))
(RD/'final_negative_summary.json').write_text(json.dumps(neg,indent=2)+'\n')
# Case order lives in the test file; parse without executing its main block.
text=(ROOT/'checks/test_recovery.py').read_text()
import ast
node=ast.parse(text);cases=None
for n in node.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CASES' for t in n.targets):cases=ast.literal_eval(n.value)
demand(cases is not None,'test inventory missing')
rows=[]
for name in cases:
    p=RD/'recovery_tests'/f'{name}.json';r=json.loads(p.read_text())
    demand(r['passed'] and r['script_sha256']==sha(ROOT/'checks/test_recovery.py'),'bad/stale case '+name)
    demand(r['source_pins']==live.pins(),'stale implementation '+name)
    rows.append({'case':name,'record':str(p.relative_to(ROOT)),'record_sha256':sha(p),'seconds':r['seconds']})
(RD/'recovery_test_summary.json').write_text(json.dumps({'passed':True,'count':len(rows),'cases':rows},indent=2)+'\n')
# Source immutability is checked against the actual baseline archive.
z=zipfile.ZipFile(args.baseline)
inherited=[]
for name in z.namelist():
    rel=name.split('/',1)[1]
    if rel.startswith('AVOC/') and rel.endswith('.lean') and Path(rel).name not in ('Audit.lean','FullAudit.lean'):
        demand((ROOT/rel).read_bytes()==z.read(name),'inherited proof changed '+rel);inherited.append(rel)
(RD/'inherited_source_match.json').write_text(json.dumps({'count':len(inherited),'all_byte_identical':True,'files':inherited},indent=2)+'\n')
result={'version':'0.20.0','status':'PASS','new_theorems':len(json.loads((RD/'new_declarations.json').read_text())),
 'theorems':len(inv),'local_targets':len(build),'axioms':audit['axioms'],'negative_tests':len(neg),
 'recovery_cases':len(rows),'inherited_modules':len(inherited),'source_forbidden_hits':0,
 'verification_scope':'Fresh local sources against pinned external cache, not a source rebuild of mathlib.',
 'recovery_scope':'Atomic protected-store commit reconciliation; unfinished intents are not retried.',
 'evidence':'results/v0.20.0/'}
(ROOT/'AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
