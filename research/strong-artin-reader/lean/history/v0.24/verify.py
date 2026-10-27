#!/usr/bin/env python3
"""Replay all direct source dependencies and new v0.24 modules in bounded batches.
The portable kit is not included. No archive download or network access is used.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, re, shutil, subprocess, sys, time, zipfile
from pathlib import Path

ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def read_member_chain(base: Path, members: list[str]) -> bytes:
    data = base.read_bytes()
    for member in members:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            data = z.read(member)
    return data

def check_source(text: str) -> None:
    # The release sources do not contain these tokens even in comments.
    if re.search(r'\b(sorry|admit)\b', text):
        raise RuntimeError('Prohibited proof escape token in source')
    if re.search(r'^\s*(?:public\s+)?(?:axiom|opaque)\s', text, re.M):
        raise RuntimeError('Custom axiom/opaque declaration in source')

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kit', type=Path, required=True)
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--max-modules', type=int, default=6)
    ap.add_argument('--timeout', type=int, default=60)
    args = ap.parse_args()
    if args.max_modules < 1 or args.timeout < 1:
        ap.error('max-modules and timeout must be positive')
    root = Path(__file__).resolve().parent
    mf = json.loads((root/'MANIFEST.json').read_text())
    kit = args.kit.resolve()
    lean = kit/'toolchain/bin/lean'
    workspace = kit/'workspace'
    version = subprocess.check_output([str(lean),'--version'],text=True).strip()
    if mf['lean'] not in version:
        raise RuntimeError(f'Unexpected Lean: {version}')
    revision = subprocess.check_output(['git','rev-parse','HEAD'],cwd=workspace/'.lake/packages/mathlib',text=True).strip()
    if revision != mf['mathlib']:
        raise RuntimeError('mathlib pin mismatch')
    for name,h in mf['bases'].items():
        if digest((root/'base'/name).read_bytes()) != h:
            raise RuntimeError(f'Base archive mismatch: {name}')
    modules = mf['dependency_modules']+mf['new_modules']
    sources: dict[str,Path] = {}
    for module in mf['dependency_modules']:
        rec = mf['dependency_sources'][module]
        data = read_member_chain(root/'base'/rec['archive'], rec['members'])
        p = root/'dependencies'/f'{module}.lean'
        if digest(data) != rec['sha256'] or p.read_bytes() != data:
            raise RuntimeError(f'Dependency provenance mismatch: {module}')
        sources[module]=p
    for rec in mf['new_sources']:
        module=rec['module'];p=root/'src'/f'{module}.lean'
        if digest(p.read_bytes()) != rec['sha256']:
            raise RuntimeError(f'New source hash mismatch: {module}')
        sources[module]=p
    for p in sources.values():
        check_source(p.read_text())
    stage=root/'verification/fresh/src'; out=root/'verification/fresh/olean'
    logs=root/'verification/fresh/logs'; progress=root/'verification/fresh/progress.json'
    if not args.resume:
        if stage.parent.exists():shutil.rmtree(stage.parent)
        for p in [stage,out,logs]:p.mkdir(parents=True,exist_ok=True)
        for p in sources.values():shutil.copy2(p,stage/p.name)
        shutil.copy2(root/'AxiomAudit.lean',stage/'AxiomAudit.lean')
        evidence=[]
        if (root/'RESULT.json').exists():(root/'RESULT.json').unlink()
    else:
        evidence=json.loads(progress.read_text())['module_results']
        for module,p in sources.items():
            if (stage/f'{module}.lean').read_bytes()!=p.read_bytes():
                raise RuntimeError(f'Resume source changed: {module}')
        if (stage/'AxiomAudit.lean').read_bytes()!=(root/'AxiomAudit.lean').read_bytes():
            raise RuntimeError('Resume audit changed')
        for rec in evidence:
            obj=out/f"{rec['module']}.olean"
            if digest(obj.read_bytes())!=rec['object_sha256']:
                raise RuntimeError('Completed object changed')
    path = subprocess.check_output(['bash',str(kit/'run.sh'),'lake','env','printenv','LEAN_PATH'],cwd=workspace,text=True).strip()
    env=os.environ.copy();env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
    env['LEAN_PATH']=str(out)+':'+str(stage)+':'+path
    done={r['module'] for r in evidence}
    all_modules=modules+['AxiomAudit']
    ran=0
    for module in all_modules:
        if module in done:continue
        if ran>=args.max_modules:break
        p=stage/f'{module}.lean';obj=out/f'{module}.olean';start=time.monotonic()
        command=[str(lean),'-j1','-DwarningAsError=true','-R',str(stage),'-o',str(obj),str(p)]
        print('CHECK',module,flush=True)
        try:
            proc=subprocess.run(command,cwd=workspace,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=args.timeout)
            code=proc.returncode;text=proc.stdout
        except subprocess.TimeoutExpired as exc:
            code=124;text=exc.stdout or ''
            if isinstance(text,bytes):text=text.decode(errors='replace')
            text+=f'\nTIMEOUT after {args.timeout} seconds\n'
        (logs/f'{module}.log').write_text(text)
        ax=set()
        for chunk in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',text,re.S):
            ax.update(x.strip() for x in chunk.split(',') if x.strip())
        if code or 'sorryAx' in text or ax-ALLOWED_AXIOMS or not obj.exists():
            (stage.parent/'FAILED.json').write_text(json.dumps({'module':module,'returncode':code,'axioms':sorted(ax),'log':str(logs/f'{module}.log')},indent=2)+'\n')
            print(text,flush=True)
            return code or 1
        rec={'module':module,'returncode':code,'source_sha256':digest(p.read_bytes()),'object_sha256':digest(obj.read_bytes()),'seconds':round(time.monotonic()-start,3),'axioms':sorted(ax)}
        evidence.append(rec);done.add(module);ran+=1
        progress.write_text(json.dumps({'status':'INCOMPLETE','module_results':evidence},indent=2)+'\n')
        print('PASS',module,rec['seconds'],'s',flush=True)
    if len(done)!=len(all_modules):
        print(f'INCOMPLETE: {len(done)}/{len(all_modules)} compiled. Resume with --resume.',flush=True)
        return 0
    audittext=(logs/'AxiomAudit.log').read_text()
    audit_count=len(re.findall(r'depends on axioms:',audittext)) + len(re.findall(r'does not depend on any axioms',audittext))
    wanted=sum(mf['new_declarations'][k] for k in ['theorem','lemma','def','abbrev'])
    if audit_count!=wanted:raise RuntimeError(f'Audit count {audit_count} != {wanted}')
    result={'checkpoint':'Strong Artin v0.24 — Compatible Target / Syzygy-Aware Hensel','status':'PASS','verification_scope':'fresh source replay of 13 direct dependency modules and 7 additive modules, plus all-new-declaration axiom audit','lean':version,'mathlib':revision,'base_hashes':mf['bases'],'dependency_modules':len(mf['dependency_modules']),'new_modules':len(mf['new_modules']),'source_modules_replayed':len(modules),'audit_modules_replayed':1,'new_declarations':mf['new_declarations'],'new_source_lines':mf['new_source_lines'],'new_declarations_axiom_audited':audit_count,'all_exit_codes_zero':True,'axiom_dependencies':sorted(set().union(*(set(e['axioms']) for e in evidence))),'module_results':evidence,'open_boundaries':['Arithmetic cotangent/Selmer comparison and one-prime interface','Construction of an integral compatible target or exact redundancy elimination for the arithmetic equations','Local continuous Galois cohomology, Tate pairing and Chebotarev instantiation','Determinant-bearing automorphic occurrence, patching, twist equivariance and ramified compatibility','Solvable-image and unrestricted Strong Artin']}
    (root/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    progress.write_text(json.dumps({'status':'PASS','module_results':evidence},indent=2)+'\n')
    print('PASS: all sources and all 47 new proof/definition declarations audited.',flush=True)
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        print(f'VERIFICATION ERROR: {type(exc).__name__}: {exc}',file=sys.stderr)
        sys.exit(1)
