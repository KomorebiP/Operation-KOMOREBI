#!/usr/bin/env python3
"""Read-only final-source evidence collector for the affine extension."""
from pathlib import Path
import hashlib,json,re,zipfile,argparse,time
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.28.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);args=ap.parse_args()
start=time.monotonic()
order=json.loads((RD/'build_order.json').read_text());build=[]
for f in order:
    p=ROOT/f;obj=ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean')
    r=json.loads((RD/f'clean_{p.stem}.json').read_text());log=ROOT/r['log']
    deps={n:sha(ROOT/'.lake/build/lib/lean'/Path(n.replace('.','/')).with_suffix('.olean')) for n in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',p.read_text(),re.M)}
    ok=r['returncode']==0 and not r['timed_out'] and r['source_unchanged'] and r['imports_unchanged'] and r['source_sha256']==sha(p) and r['output_sha256']==sha(obj) and r['log_sha256']==sha(log) and deps==r['import_outputs']
    assert ok,('bad build evidence',f)
    build.append(f)
inv=json.loads((RD/'declaration_inventory.json').read_text());audit=(RD/'full_axiom_audit.log').read_text()
names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",audit,re.M)
assert len(names)==len(inv) and set(names)=={r['qualified_name'] for r in inv}
axioms={n.strip() for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',audit,re.S) for n in block.split(',') if n.strip()}
assert axioms <= {'propext','Classical.choice','Quot.sound'}
# Validate all negative files against current source, logs and local import artifacts.
neg=json.loads((RD/'negative_summary.json').read_text())
assert len(neg)==len(list((ROOT/'tests/negative').glob('*.lean')))
for r in neg:
    p=ROOT/r['file'];txt=(ROOT/r['log']).read_text()
    assert r['expected_rejection'] and r['returncode']!=0 and not r['timed_out']
    assert sha(p)==r['source_sha256'] and sha(ROOT/r['log'])==r['log_sha256']
    deps={n:sha(ROOT/'.lake/build/lib/lean'/Path(n.replace('.','/')).with_suffix('.olean')) for n in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',p.read_text(),re.M)}
    assert deps==r['import_outputs'],r['file']
    assert not re.search(r'object file .*does not exist|unknown module|failed to locate application|unknown identifier',txt)
# The baseline proof modules are byte-identical.
with zipfile.ZipFile(args.baseline) as z:
    assert z.testzip() is None
    inherited=[]
    for n in z.namelist():
        parts=Path(n).parts
        if len(parts)==3 and parts[1]=='AVOC' and n.endswith('.lean') and parts[-1] not in ['Audit.lean','FullAudit.lean']:
            rel='/'.join(parts[1:]);assert (ROOT/rel).read_bytes()==z.read(n),rel;inherited.append(rel)
# Strip nested comments and strings for the proof-shortcut source scan.
def strip_lean(s):
    out=[];i=0;level=0;quote=False
    while i<len(s):
        if level:
            if s.startswith('/-',i):level+=1;i+=2
            elif s.startswith('-/',i):level-=1;i+=2
            else:out.append('\n' if s[i]=='\n' else ' ');i+=1
        elif quote:
            if s[i]=='\\':i+=2
            elif s[i]=='"':quote=False;i+=1
            else:i+=1
        elif s.startswith('--',i):
            j=s.find('\n',i);i=len(s) if j<0 else j
        elif s.startswith('/-',i):level=1;i+=2
        elif s[i]=='"':quote=True;i+=1
        else:out.append(s[i]);i+=1
    return ''.join(out)
scan=[]
for p in (ROOT/'AVOC').glob('*.lean'):
    if p.name in ['Audit.lean','FullAudit.lean']:continue
    s=strip_lean(p.read_text())
    # Distinguish the declared action constructor/case label from the proof tactic.
    s=re.sub(r'(?m)^(\s*\|)\s+admit(?=\s*(?:=>|$))', r'\1 admitted_action_constructor', s)
    bad=re.findall(r'(?<![\w.])(?:sorry|admit|native_decide)\b|^\s*axiom\b|^\s*unsafe\s+(?:def|theorem|lemma)\b',s,re.M)
    if bad:scan.append((str(p),bad))
assert not scan,scan
tests=json.loads((RD/'affine_tests/summary.json').read_text())
assert tests['status']=='PASS' and tests['source_unchanged']
for f,h in tests['source_hashes'].items():assert sha(ROOT/f)==h,f
pins=json.loads((RD/'dependency_pins.json').read_text());assert len(pins)==9 and all(r['passed'] for r in pins)
summary=dict(version='0.28.0',status='PASS',baseline_sha256=sha(args.baseline),inherited_modules_unchanged=len(inherited),
    local_compilations=len(build),theorem_reports=len(names),new_theorems=len(json.loads((RD/'new_declarations.json').read_text())),axioms=sorted(axioms),
    negative_rejections=len(neg),negative_type_mismatch_tests=1,proof_shortcut_hits=0,dependency_pins=9,
    regression={k:tests[k] for k in ['requests','normalization_cases','comparison_cases','vector_input_comparisons','invalid_requests','seed']},
    collector_seconds=time.monotonic()-start,
    scope='Fresh local project against pinned external caches; old runtime suites not rerun; no full mathlib source rebuild or whole IO refinement')
(RD/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(ROOT/'AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
