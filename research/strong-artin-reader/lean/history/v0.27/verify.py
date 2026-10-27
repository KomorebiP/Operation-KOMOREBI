#!/usr/bin/env python3
"""Fresh, bounded Lean replay for the v0.27 direct dependency closure.
Uses an existing pinned portable kit. No network requests or package updates.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib, json, os, re, shutil, subprocess, sys, time, zipfile
from pathlib import Path

BASE_NAME = 'Strong_Artin_Lean_v0.26.0_Representation_H2_Obstruction_Checked.zip'
BASE_SHA = '6ab67721841940b82a621642dcb78a0e67e6012c1df20a9bb519ac01c8ee8bbd'
BASE_ROOT = 'Strong_Artin_Lean_v0.26.0_Representation_H2_Obstruction'
MATHLIB = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
LEAN_COMMIT = '6a10ac8c22beadecabdbb0919c2b50214762f91d'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def code_only(text: str) -> str:
    """Mask nested Lean block/line comments and strings, retaining line breaks."""
    out=[]; i=0; depth=0
    while i<len(text):
        if depth:
            if text.startswith('/-',i): depth+=1; out.extend('  '); i+=2
            elif text.startswith('-/',i): depth-=1; out.extend('  '); i+=2
            else: out.append('\n' if text[i]=='\n' else ' '); i+=1
        elif text.startswith('/-',i): depth=1;out.extend('  ');i+=2
        elif text.startswith('--',i):
            while i<len(text) and text[i]!='\n':out.append(' ');i+=1
        elif text[i]=='"':
            out.append(' ');i+=1
            while i<len(text):
                if text[i]=='\\':out.extend('  ');i+=2
                elif text[i]=='"':out.append(' ');i+=1;break
                else:out.append('\n' if text[i]=='\n' else ' ');i+=1
        else:out.append(text[i]);i+=1
    if depth:raise ValueError('Unclosed source comment')
    return ''.join(out)

def run() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kit',required=True,type=Path)
    ap.add_argument('--timeout',type=int,default=90,help='Per-module seconds')
    ap.add_argument('--resume',action='store_true')
    ap.add_argument('--max-modules',type=int,default=None)
    args=ap.parse_args()
    root=Path(__file__).resolve().parent; kit=args.kit.resolve(); workspace=kit/'workspace'
    lean=kit/'toolchain/bin/lean'; ml=workspace/'.lake/packages/mathlib'
    version=subprocess.check_output([str(lean),'--version'],text=True).strip()
    if '4.34.0-rc2' not in version or LEAN_COMMIT not in version:raise RuntimeError(version)
    revision=subprocess.check_output(['git','-C',str(ml),'rev-parse','HEAD'],text=True).strip()
    if revision!=MATHLIB:raise RuntimeError('Wrong mathlib revision: '+revision)
    base=root/'base'/BASE_NAME
    if sha(base)!=BASE_SHA:raise RuntimeError('Base archive checksum mismatch')
    modules=json.loads((root/'MODULES.json').read_text())
    with zipfile.ZipFile(base) as z:
        if z.testzip() is not None:raise RuntimeError('Base ZIP CRC failure')
        for module in modules['dependency_modules']:
            kind='dependencies' if module=='SquareZeroRepresentationDefect' else 'src'
            member=f'{BASE_ROOT}/{kind}/{module}.lean'
            if z.read(member)!=(root/'dependencies'/f'{module}.lean').read_bytes():
                raise RuntimeError('Ancestral source changed: '+module)
    decls=json.loads((root/'DECLARATIONS.json').read_text())
    paths={m:root/'dependencies'/f'{m}.lean' for m in modules['dependency_modules']}
    paths.update({m:root/'src'/f'{m}.lean' for m in modules['new_modules']})
    paths[modules['audit_module']]=root/'audit'/f"{modules['audit_module']}.lean"
    violations=[];counts=Counter()
    for m,p in paths.items():
        txt=code_only(p.read_text())
        if m!=modules['audit_module']:
            bad=re.findall(r'\b(?:sorry|admit|axiom|opaque|native_decide|unsafe)\b',txt)
            if bad:violations.append({'module':m,'markers':bad})
        if m in modules['new_modules']:
            counts.update(re.findall(r'(?m)^\s*(?:@\[[^\n]*\]\s*)?(?:(?:noncomputable|private|protected|public)\s+)*(theorem|lemma|def|abbrev|structure)\s+',txt))
    if violations:raise RuntimeError('Disallowed source markers: '+str(violations))
    if dict(counts)!=dict(Counter(d['kind'] for d in decls)):
        raise RuntimeError('Source declaration counts differ from named audit list')
    hashes={m:sha(p) for m,p in paths.items()}
    out=root/'verification/fresh'; result=root/'RESULT.json'
    if not args.resume:
        if out.exists():shutil.rmtree(out)
    for d in ['src','olean','logs']:(out/d).mkdir(parents=True,exist_ok=True)
    records=[]
    if args.resume and result.exists():
        previous=json.loads(result.read_text())
        if previous.get('source_hashes')!=hashes:raise RuntimeError('Sources changed since preceding run')
        records=previous['module_results']
        for rec in records:
            if rec['returncode']!=0:raise RuntimeError('Cannot resume a failed invocation; run a fresh replay')
            obj=root/rec['object_file']
            if not obj.exists() or sha(obj)!=rec['object_sha256']:raise RuntimeError('Stale/missing compiled object')
    for m,p in paths.items():shutil.copy2(p,out/'src'/p.name)
    lp=subprocess.check_output(['bash',str(kit/'run.sh'),'lake','env','printenv','LEAN_PATH'],cwd=workspace,text=True).strip()
    env=os.environ.copy();env['LEAN_PATH']=str(out/'olean')+':'+str(out/'src')+':'+lp
    env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
    manifest={
        'checkpoint':'Strong Artin v0.27.0 — Continuous Obstruction and Finite-Quotient Vanishing',
        'status':'IN_PROGRESS','verification_scope':'fresh direct source dependency closure; not a full ancestor replay',
        'lean':version,'mathlib':revision,'base_archive':BASE_NAME,'base_sha256':BASE_SHA,
        'ancestor_dependency_unchanged':True,'dependency_modules':len(modules['dependency_modules']),
        'new_modules':len(modules['new_modules']),'source_modules':len(paths)-1,'audit_modules':1,
        'additive_declarations':dict(counts),'named_constants_audited':len(decls),
        'local_anonymous_instances':sum(len(re.findall(r'(?m)^\s*local instance\b', code_only(paths[m].read_text()))) for m in modules['new_modules']),
        'new_source_lines':sum(len(paths[m].read_text().splitlines()) for m in modules['new_modules']),
        'warning_as_error':True,'source_hashes':hashes,'module_results':records,
        'prohibited_active_source_occurrences':violations,'cohomology':'explicit continuous inhomogeneous degree-two cochain quotient, using Mathlib cocycles and differential; no claimed equivalence with the separate continuousCohomology functor',
        'relative_cohomology':'explicit continuous degree-two kernel-of-restriction quotient; literal preservation of a specified subgroup lift',
        'closed_scope':['continuous provisional sections and continuous obstruction criterion',
            'continuous prescribed clopen-subgroup criterion',
            'finite-group H2 and H1 primitives by normalized averaging',
            'finite-image order-invertible continuous lifting preserving the exact kernel',
            'prescribed finite-subgroup lifting under explicit order invertibility',
            'compact-source specialization and positive/nonvanishing controls'],
        'open_boundaries':['formal comparison with separate homogeneous/derived continuous cohomology API',
            'general closed-subgroup local prescriptions and restriction up to conjugacy',
            'Selmer/local deformation conditions and wild arithmetic obstruction vanishing',
            'compatible iteration through all coefficient depths with those local conditions',
            'automorphic carrier existence and Strong Artin'],
        'reuse':'pinned Mathlib compiled cache reused; no full Mathlib rebuild or independent kernel'
    }
    def save():
        manifest['last_observed_utc']=datetime.now(timezone.utc).isoformat()
        result.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    save();done={r['module'] for r in records};count=0
    for m in paths:
        if m in done:continue
        if args.max_modules is not None and count>=args.max_modules:
            manifest['status']='PARTIAL';save();print('PARTIAL: explicit module limit reached');return 0
        obj=out/'olean'/f'{m}.olean';log=out/'logs'/f'{m}.log'
        command=[str(lean),'-j1','-DwarningAsError=true','-R',str(out/'src'),'-o',str(obj),str(out/'src'/f'{m}.lean')]
        started=time.monotonic()
        try:
            proc=subprocess.run(command,cwd=workspace,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=args.timeout)
            rc=proc.returncode;output=proc.stdout
        except subprocess.TimeoutExpired as e:
            rc=124;output=(e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else (e.stdout or ''))+'\nPER-MODULE TIMEOUT\n'
        log.write_text(output)
        record={'module':m,'source_sha256':hashes[m],'returncode':rc,'seconds':round(time.monotonic()-started,3),
                'command':command,'cwd':str(workspace),'log':str(log.relative_to(root)),
                'log_sha256':sha(log),'sorryAx':bool(re.search(r'\bsorryAx\b',output)),
                'object_file':str(obj.relative_to(root)), 'object_sha256':sha(obj) if obj.exists() else None}
        records.append(record);count+=1
        print(f'{m}: rc={rc}, {record["seconds"]}s',flush=True)
        if rc!=0 or record['sorryAx']:
            manifest['status']='FAIL';save();print(output);return 1
        save()
    audit=(out/'logs'/f"{modules['audit_module']}.log").read_text()
    reports={name:set(filter(None,(s.strip() for s in body.replace('\n',' ').split(','))))
             for name,body in re.findall(r"'([^']+)' depends on axioms: \[(.*?)\]",audit,re.S)}
    empty=re.findall(r"'([^']+)' does not depend on any axioms",audit)
    reports.update({name:set() for name in empty})
    missing=[d['name'] for d in decls if d['name'] not in reports]
    extra=sorted(set().union(*reports.values())-ALLOWED)
    manifest['axiom_reports_found']=len(reports)
    manifest['missing_axiom_reports']=missing;manifest['unexpected_axioms']=extra
    manifest['axiom_dependencies']=sorted(set().union(*reports.values()))
    manifest['all_exit_codes_zero']=all(r['returncode']==0 for r in records)
    if missing or extra:
        manifest['status']='FAIL';save();print('Axiom audit failed',missing,extra);return 1
    manifest['status']='PASS';save();print(f'PASS: {len(paths)-1} source modules + 1 all-constant axiom audit',flush=True)
    return 0

if __name__=='__main__':
    try:sys.exit(run())
    except Exception as exc:
        print(f'VERIFICATION ERROR: {exc}',file=sys.stderr);sys.exit(1)
