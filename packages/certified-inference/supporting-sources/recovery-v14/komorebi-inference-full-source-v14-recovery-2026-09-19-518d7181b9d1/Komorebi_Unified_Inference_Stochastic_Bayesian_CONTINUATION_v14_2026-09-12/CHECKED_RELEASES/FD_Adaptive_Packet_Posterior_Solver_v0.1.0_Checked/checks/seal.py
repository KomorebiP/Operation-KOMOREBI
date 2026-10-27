#!/usr/bin/env python3
"""Check exact final-source compilation receipts and all declaration axiom lists.

This audit does not rerun Lean. Use verify_blocks.py first to reproduce builds.
It compares current source, log, output, and direct dependency hashes against
successful per-process records. Failed/incomplete runs are reported separately.
"""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,platform,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'propext','Classical.choice','Quot.sound'}
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->None:
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True);a=ap.parse_args()
    rt=a.runtime.resolve();cache=rt/'workspace/.lake/build/lib/lean/Komorebi'
    modules=json.loads((ROOT/'MODULE_ORDER.json').read_text())
    inherited=json.loads((ROOT/'INHERITED_SOURCES.json').read_text())
    decls=json.loads((ROOT/'DECLARATIONS.json').read_text())
    records=[]
    for p in sorted((ROOT/'audit').glob('*/*.json')):
        r=json.loads(p.read_text())
        if not isinstance(r,dict) or 'module' not in r:continue
        records.append((p,r))
    final=[];failures=[]
    for path,r in records:
        if r['exit_status']!=0:
            failures.append({**r,'receipt_path':str(path.relative_to(ROOT))})
    for n in modules:
        source=ROOT/'Komorebi'/f'{n}.lean';out=cache/f'{n}.olean'
        assert source.is_file() and out.is_file(),f'Missing source or compiled output: {n}'
        digest=sha(source);output=sha(out)
        assert not re.search(r'\b(?:sorry|admit|axiom|unsafe|native_decide|sorryAx|ofReduceBool)\b',source.read_text()),n
        if n in inherited:assert digest==inherited[n]['sha256'],'Inherited source changed: '+n
        valid=[]
        for path,r in records:
            if r['module']!=n or r['exit_status']!=0:continue
            if any(r.get(key)!=digest for key in ['source_sha256_before','source_sha256_after','staged_source_sha256']):continue
            if r['output_sha256']!=output:continue
            if sha(path.with_suffix('.log'))!=r['log_sha256']:continue
            if sha(path.with_suffix('.lean'))!=digest:continue
            good=True
            expected=set(re.findall(r'^import (Komorebi\.\w+)',source.read_text(),re.M))
            if expected!=set(r['dependencies']):continue
            for dep,h in r['dependencies'].items():
                dn=dep.rsplit('.',1)[1]
                if h['source_sha256']!=sha(ROOT/'Komorebi'/f'{dn}.lean') or h['olean_sha256']!=sha(cache/f'{dn}.olean'):
                    good=False;break
            if good:valid.append((path,r))
        assert valid,'No matching successful final-source/dependency receipt: '+n
        path,r=valid[-1];final.append({**r,'receipt_path':str(path.relative_to(ROOT))})
    ar=next(r for r in final if r['module']=='AdaptiveAxiomAudit')
    log=(ROOT/ar['receipt_path']).with_suffix('.log').read_text()
    parsed={}
    for name,values in re.findall(r"(?m)^'([^\n]+)' depends on axioms: \[([^\]]*)\]",log):
        assert name not in parsed,'Duplicate axiom output '+name
        parsed[name]=[v.strip() for v in values.split(',') if v.strip()]
    for name in re.findall(r"(?m)^'([^\n]+)' does not depend on any axioms",log):
        assert name not in parsed
        parsed[name]=[]
    assert set(parsed)=={d['name'] for d in decls},('Axiom coverage mismatch',len(parsed),len(decls))
    ax=[]
    for d in decls:
        assert set(parsed[d['name']])<=ALLOWED,(d['name'],parsed[d['name']])
        ax.append({**d,'axioms':parsed[d['name']],
                   'source_sha256':sha(ROOT/'Komorebi'/f'{d["module"]}.lean')})
    (ROOT/'AXIOM_AUDIT.json').write_text(json.dumps(dict(status='PASS',covered=len(ax),
        allowed_axioms=sorted(ALLOWED),declarations=ax),indent=2)+'\n')
    negative=json.loads((ROOT/'results/NEGATIVE_CONTROLS.json').read_text())
    assert len(negative)==3 and all(r['exit_status']!=0 and r['expected_rejection'] for r in negative)
    diagnostics=json.loads((ROOT/'computations/adaptive-final/diagnostics.json').read_text())
    assert diagnostics['status']=='PASS'
    incomplete=[]
    for p in sorted((ROOT/'audit').glob('*/*.lean')):
        if not p.with_suffix('.json').exists():incomplete.append(str(p.relative_to(ROOT)))
    try:commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:commit=None
    report=dict(status='PASS',sealed_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),source_commit=commit,
        scope='Greedy exact-rational output-packet updates, contraction, rounded posterior certification, and interval output',
        environment=dict(lean_version=final[0]['lean_version'],mathlib_commit=final[0]['mathlib_commit'],
            platform=platform.platform(),warning_as_error=True,threads_per_lean_process=1),
        final_modules_passed=len(final),inherited_modules_unchanged=len(inherited),
        theorem_lemma_declarations=len(decls),new_declarations=sum(d['group']=='new' for d in decls),
        successful_final_modules=final,failed_completed_attempts=failures,current_block_failed_attempts=[r for r in failures if r['module'] in modules and r['module'] not in inherited],incomplete_attempt_source_snapshots=incomplete,
        accumulated_final_compile_process_seconds=round(sum(r['elapsed_seconds'] for r in final),3),
        negative_controls=negative,exact_diagnostics=diagnostics,
        verification_boundary='This seal checks final-source successful receipts, compiled output and dependency hashes, and full axiom coverage; it is not a new Lean run.',
        non_claims=['This selective solver uses exact rational packet updates. The inherited rounded full-update solver is a separate branch.',
            'No IEEE-754, finite word-size, input uncertainty, parser, or exporter refinement proof.',
            'Precision bound is sufficient, not optimal; no score monotonicity in precision is assumed.',
            'Fixed packet geometry; no hierarchy-changing refinement, sequential filtering, or added Ito foundations.',
            'No literature novelty, performance superiority, or hardware resource guarantee.',
            'New modules compiled this block; unchanged inherited receipts and compiled outputs were hash-validated from v12. Pinned mathlib caches reused.'])
    (ROOT/'FINAL_VERIFICATION_RECEIPT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','final_modules_passed','inherited_modules_unchanged',
        'theorem_lemma_declarations','new_declarations','accumulated_final_compile_process_seconds']},indent=2))
    print('Failed completed attempts:',len(failures),'incomplete source snapshots:',len(incomplete))
if __name__=='__main__':main()
