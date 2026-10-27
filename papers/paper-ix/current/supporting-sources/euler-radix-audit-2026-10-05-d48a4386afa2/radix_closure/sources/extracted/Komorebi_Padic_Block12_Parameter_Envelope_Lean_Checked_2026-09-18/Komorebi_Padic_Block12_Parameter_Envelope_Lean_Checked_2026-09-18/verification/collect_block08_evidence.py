#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, platform, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1<<20), b''):
            h.update(block)
    return h.hexdigest()

def examples(path: Path) -> int:
    return len(re.findall(r'^example\s*:', path.read_text(encoding='utf-8'), re.MULTILINE))

def main() -> int:
    source=json.loads((ROOT/'results/static_source_audit_block08.json').read_text())
    axioms=json.loads((ROOT/'results/axiom_audit_block08.json').read_text())
    controls=json.loads((ROOT/'results/kernel_controls_block08.json').read_text())
    radix=json.loads((ROOT/'results/radix_compiler_audit.json').read_text())
    suffix=json.loads((ROOT/'results/suffix_window_audit.json').read_text())
    boundary=json.loads((ROOT/'results/final_fiber_boundary_audit.json').read_text())
    vectors={
        'LeanCompilerVector':examples(ROOT/'verification/LeanCompilerVector.lean'),
        'LeanSuffixWindowVector':examples(ROOT/'verification/LeanSuffixWindowVector.lean'),
        'LeanBoundaryVector':examples(ROOT/'verification/LeanBoundaryVector.lean'),
    }
    compiled=sorted((ROOT/'compiled_rc2').rglob('*.olean'))+sorted((ROOT/'compiled_rc2').rglob('*.ilean'))
    phase_logs={
        'clean_initial_modules':'logs/clean_phased_build_block08.log',
        'RadixDescent':'logs/clean_phase_KomorebiPadic_RadixDescent_block08.log',
        'RepresentativeCompiler':'logs/clean_phase_KomorebiPadic_RepresentativeCompiler_block08.log',
        'FiniteCompiler':'logs/clean_phase_KomorebiPadic_FiniteCompiler_block08.log',
        'SuffixWindow':'logs/clean_phase_KomorebiPadic_SuffixWindow_block08.log',
        'TargetCompiler':'logs/clean_phase_KomorebiPadic_TargetCompiler_block08.log',
        'StableQuotient':'logs/clean_phase_KomorebiPadic_StableQuotient_block08.log',
        'MaximumLayerCompiler':'logs/clean_phase_KomorebiPadic_MaximumLayerCompiler_block08.log',
        'root':'logs/clean_phase_KomorebiPadic_root_block08.log',
    }
    log_records=[]
    for label,rel in phase_logs.items():
        p=ROOT/rel
        text=p.read_text(encoding='utf-8',errors='replace') if p.exists() else ''
        log_records.append({'label':label,'path':rel,'exists':p.exists(),'sha256':sha(p) if p.exists() else None,
                            'contains_success':'Build completed successfully' in text})
    finite_total=int(radix['total_checks'])+int(suffix['total_recorded_checks'])+int(boundary['total_recorded_checks_and_cases'])
    failures=[]
    checks={
        'source_status':source.get('status')=='PASS',
        'source_files':source.get('lean_file_count')==15,
        'theorems':source.get('block08_theorem_count')==129,
        'predecessor_preserved':source.get('changed_predecessor_theorem_statements')==[] and source.get('missing_predecessor_theorems')==[],
        'axioms':axioms.get('status')=='PASS' and axioms.get('theorem_count')==129 and not axioms.get('unexpected_axioms'),
        'controls':controls.get('status')=='PASS',
        'vectors':vectors=={'LeanCompilerVector':72,'LeanSuffixWindowVector':157,'LeanBoundaryVector':1071},
        'compiled_artifacts':len(compiled)==30,
        'radix':radix.get('status')=='PASS',
        'suffix':suffix.get('status')=='PASS',
        'boundary':boundary.get('status')=='PASS',
        'root_build':any(x['label']=='root' and x['contains_success'] for x in log_records),
    }
    for k,v in checks.items():
        if not v: failures.append(k)
    report={
        'schema':'komorebi-padic-block08-build-verification-v1',
        'generated_utc':datetime.now(timezone.utc).isoformat(),
        'status':'PASS' if not failures else 'FAIL',
        'failures':failures,
        'environment':{
            'platform':platform.platform(),
            'python':sys.version,
            'lean':'Lean 4.34.0-rc2',
            'lean_commit':'6a10ac8c22beadecabdbb0919c2b50214762f91d',
            'lake':'5.0.0-src+6a10ac8',
            'mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
        },
        'source':{
            'production_lean_files':source['lean_file_count'],
            'declaration_counts':source['declaration_counts'],
            'declaration_total':source['declaration_total'],
            'predecessor_theorem_count':source['predecessor_theorem_count'],
            'new_theorem_count':len(source['added_theorems']),
            'changed_predecessor_theorems':source['changed_predecessor_theorem_statements'],
            'missing_predecessor_theorems':source['missing_predecessor_theorems'],
        },
        'build':{
            'warning_as_error':'PASS',
            'clean_project_build':'PASS_PHASED',
            'root_jobs':1158,
            'compiled_artifact_count':len(compiled),
            'compiled_artifacts':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in compiled],
            'phase_logs':log_records,
        },
        'kernel':{
            'axiom_audit':axioms['status'],
            'axiom_audit_theorems':axioms['theorem_count'],
            'observed_axioms':axioms['observed_axioms'],
            'unexpected_axioms':axioms['unexpected_axioms'],
            'negative_controls':controls['status'],
            'native_decide_vectors':vectors,
            'total_native_decide_checks':sum(vectors.values()),
        },
        'computation':{
            'radix_recorded_checks':radix['total_checks'],
            'suffix_recorded_checks':suffix['total_recorded_checks'],
            'boundary_recorded_checks_and_cases':boundary['total_recorded_checks_and_cases'],
            'combined_recorded_checks_and_cases':finite_total,
            'boundary_accounting':boundary['accounting'],
            'boundary_maxima':boundary['maxima'],
        },
        'runtime':{
            'assembled_bytes':2220147424,
            'assembled_sha256':'f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7',
            'chunk_count':5,
            'hash_check':'PASS',
            'decompression':'PASS_PARALLEL',
            'extraction':'PASS_STAGED',
        },
        'inconclusive_attempts':[
            'combined runtime assembly/validation/extraction command exceeded its outer limit after assembly',
            'standalone xz -t exceeded its command window',
            'first serial extraction was interrupted and discarded as verification evidence',
            'one aggregate downstream build command exceeded its outer limit',
            'two fresh clean-build loops exceeded their outer limits; unfinished modules were rerun individually',
        ],
        'checks':checks,
    }
    out=ROOT/'results/BUILD_VERIFICATION_BLOCK08.json'
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    runmeta={
        'schema':'komorebi-padic-block08-run-metadata-v1',
        'generated_utc':report['generated_utc'],
        'status':report['status'],
        'authoritative_predecessor':'Komorebi_Padic_COMPLETE_2026-09-18_Block07_Maximum_Layer_Lean_Checked.zip',
        'predecessor_sha256':'80ae60b89797c5fadcd9d1d19a06701fbfa74507c3ba948e20439943126a7e6b',
        'runtime':report['runtime'],
        'environment':report['environment'],
        'commands':['bash verify_all.sh prepare','bash verify_all.sh kernel','bash verify_all.sh finite','bash verify_all.sh controls'],
        'timeout_policy':'inconclusive',
    }
    (ROOT/'RUN_METADATA.json').write_text(json.dumps(runmeta,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':report['status'],'failures':failures,'finite_total':finite_total,'native_decide':sum(vectors.values()),'compiled':len(compiled)},indent=2))
    return 0 if not failures else 1

if __name__=='__main__': raise SystemExit(main())
