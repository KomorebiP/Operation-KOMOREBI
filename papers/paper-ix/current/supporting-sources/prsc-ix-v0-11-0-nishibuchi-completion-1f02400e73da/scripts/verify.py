#!/usr/bin/env python3
"""Rebuild the complete local Paper IX all-residue proof corpus, then audit explicit declarations.
Author: Komorebi P.  Requires the pinned Linux portable kit and Python 3.10+.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
MODULES = ['ResiduePackets', 'Triangular', 'EGFCoordinates', 'FilteredReconstruction',
           'CongruentialEuler', 'ExponentialSection', 'StandardWindow', 'NormalizationBoundary',
           'OddPowerSeries', 'EulerCoefficients', 'ZigzagCoefficients',
           'OddEulerReconstruction', 'OddEulerExamples', 'DyadicIntegrality',
           'DyadicSeries', 'DyadicReconstruction', 'DyadicExamples',
           'FiniteMahler', 'PadicDifferenceBounds', 'UnitModeDifferences', 'MahlerExamples',
           'UnitTriangular', 'WindowIndependence', 'FiniteUnits', 'DyadicUnits', 'UnitRefinement', 'CRTPackets', 'FiniteArithmeticExamples', 'CompanionPackets', 'FibonacciPackets', 'RecurrenceExamples',
           'HurwitzConvolution', 'HurwitzInverse', 'StandardWindowPeriod',
           'DifferenceFiltration', 'GlobalEulerBoundary', 'DworkCriterion', 'PeriodExamples',
           'DworkAlgebra', 'DworkClosure', 'HurwitzDworkClosure', 'ResidueZeroDwork', 'DifferenceStepMultiples', 'EulerDefect', 'StandardWindowDwork', 'StandardWindowPrecision', 'DworkWindowExamples', 'CyclotomicFiltration', 'PrimeBlockPolynomial', 'CyclicAmiceCoefficients', 'BinomialLogSeries', 'SectionLogBridge', 'WeightedAmice', 'WeightedAmiceDifferential', 'SingularNormalizedSection', 'SingularRatioAmice', 'SingularAmiceExamples']
MODULES += ['WeightedAmiceRing', 'FrobeniusSquare', 'ThetaWeighted', 'WeightedDworkTransfer', 'SeriesDifferenceBridge', 'RatioSeriesSupport', 'EulerSeriesInverse', 'RiccatiFlatPropagation', 'RatioRiccati', 'AllRatiosDwork', 'AllResidueEuler', 'Theorem75', 'AllResidueExamples']
MODULES += ['PeriodFromDifferences', 'CubicDworkAlgebra', 'CubicDworkClosure', 'KummerSequences', 'DyadicFourKernel', 'DyadicFourDwork', 'DyadicFourCongruences', 'NishibuchiCompletion', 'ConjectureExamples']
LEAN_VERSION = '4.34.0-rc2'
MATHLIB_REVISION = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
FORBIDDEN = re.compile(r'\b(?:sorry|admit|axiom|unsafe|native_decide|implemented_by)\b|'
                       r'debug\.skipKernelTC|ofReduceBool|ofReduceNat|Lean\.addDecl|'
                       r'set_option\s+(?:maxRecDepth|maxHeartbeats)\s+0|'
                       r'set_option\s+linter\.[\w.]+\s+false')

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def stripped_source(text: str) -> str:
    """Remove nested block comments, line comments and strings; preserve newlines."""
    out = []; i=0; depth=0; string=False
    while i < len(text):
        ch=text[i]; pair=text[i:i+2]
        if depth:
            if pair=='/-': depth+=1; out.extend('  '); i+=2; continue
            if pair=='-/': depth-=1; out.extend('  '); i+=2; continue
            out.append('\n' if ch=='\n' else ' '); i+=1; continue
        if string:
            if ch=='\\' and i+1 < len(text): out.extend('  '); i+=2; continue
            if ch=='"': string=False
            out.append('\n' if ch=='\n' else ' '); i+=1; continue
        if pair=='/-': depth=1; out.extend('  '); i+=2; continue
        if pair=='--':
            j=text.find('\n',i)
            if j<0: out.extend(' '*(len(text)-i)); break
            out.extend(' '*(j-i)); i=j; continue
        if ch=='"': string=True; out.append(' '); i+=1; continue
        out.append(ch); i+=1
    if depth or string: raise ValueError('Unclosed source comment or string')
    return ''.join(out)

def inspect_source(path: Path) -> dict:
    text = stripped_source(path.read_text())
    forbidden = FORBIDDEN.findall(text)
    if forbidden: raise ValueError(f'{path.name}: forbidden source construct {forbidden}')
    namespaces=re.findall(r'^namespace\s+([\w.]+)',text,re.M)
    if len(namespaces)!=1 or not namespaces[0].startswith('KomorebiPaperIX.'):
        raise ValueError(f'{path.name}: expected one explicit project namespace')
    declarations=[{'kind':k, 'name':namespaces[0]+'.'+n}
                  for k,n in re.findall(r'\b(theorem|lemma|def|abbrev)\s+([A-Za-z_][A-Za-z_0-9]*)',text)]
    if len({x['name'] for x in declarations})!=len(declarations):
        raise ValueError('Duplicate explicit declaration')
    return {'module':path.stem,'source':str(path.relative_to(ROOT)), 'sha256':sha(path),
            'imports':re.findall(r'^public import ([\w.]+)',text,re.M),
            'declarations':declarations}

def source_inventory() -> dict:
    actual={x.stem for x in (ROOT/'formalization').glob('*.lean')}
    if actual!=set(MODULES): raise ValueError('Unexpected or missing active Lean source')
    entries=[inspect_source(ROOT/'formalization'/f'{m}.lean') for m in MODULES]
    seen=set()
    for entry in entries:
        for dep in entry['imports']:
            if dep in MODULES and dep not in seen: raise ValueError('Non-topological module order')
        seen.add(entry['module'])
    return {'release':'PRSC_IX_v0.11.0_Nishibuchi_Completion', 'modules':entries,
            'theorem_count':sum(d['kind'] in ('theorem','lemma') for e in entries for d in e['declarations']),
            'definition_count':sum(d['kind']=='def' for e in entries for d in e['declarations']),
            'abbreviation_count':sum(d['kind']=='abbrev' for e in entries for d in e['declarations'])}

def validate_coverage(inventory: dict) -> dict:
    coverage=json.loads((ROOT/'coverage.json').read_text())
    entries=coverage['entries']
    if len({e['id'] for e in entries})!=len(entries):
        raise ValueError('Duplicate manuscript identifier')
    observed={k:sum(e['status']==v for e in entries) for k,v in
              [('lean_checked','LEAN_CHECKED'),('pending_lean','PENDING_LEAN'),
               ('classical_inputs','CLASSICAL_INPUT'),('conjectures','CONJECTURAL')]}
    observed['manuscript_proved']=observed['lean_checked']+observed['pending_lean']
    if observed!=coverage['counts']: raise ValueError('Stale coverage counts')
    if (observed['manuscript_proved'],observed['classical_inputs'],observed['conjectures'])!=(24,3,2):
        raise ValueError('Changed manuscript register boundary')
    names={d['name'] for m in inventory['modules'] for d in m['declarations']}
    for e in entries:
        if bool(e['targets'])!=(e['status']=='LEAN_CHECKED'):
            raise ValueError('Checked/pending target mismatch')
        if not set(e['targets'])<=names: raise ValueError('Missing coverage target')
        if e['id']=='7.5' and e['status']=='LEAN_CHECKED':
            required={'KomorebiPaperIX.Theorem75.global_finite_difference',
                      'KomorebiPaperIX.AllResidueEuler.global_unnormalized_bound',
                      'KomorebiPaperIX.AllResidueEuler.global_normalized_precision'}
            if not required<=set(e['targets']):
                raise ValueError('Missing unconditional global theorem targets')
        if not set(e.get('partial_targets', []))<=names: raise ValueError('Missing partial target')
        if e.get('partial_targets') and e['status']!='PENDING_LEAN':
            raise ValueError('Partial-target record must remain pending')
    if sha(ROOT/coverage['source_pdf'])!=coverage['source_sha256']:
        raise ValueError('Baseline manuscript hash mismatch')
    for path,digest in json.loads((ROOT/'provenance/upstream_sources.json').read_text()).items():
        if sha(ROOT/path)!=digest: raise ValueError('Upstream proof source changed: '+path)
    return observed

def parse_audits(text: str, expected: set[str]) -> dict[str,list[str]]:
    if re.search(r'PANIC|error:|unknown constant|unknown module',text,re.I):
        raise ValueError('Compiler error in audit output')
    audits={}
    # Lean may wrap an axiom list across lines.
    pattern=r"'([^']+)'\s+(?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)"
    for m in re.finditer(pattern,text,re.S):
        name=m[1]
        if name in audits: raise ValueError('Duplicate axiom report')
        axioms=sorted(x.strip() for x in (m[2] or '').split(',') if x.strip())
        if not set(axioms)<=ALLOWED: raise ValueError(f'Unexpected axioms for {name}: {axioms}')
        audits[name]=axioms
    if set(audits)!=expected:
        raise ValueError(f'Audit inventory mismatch: missing={sorted(expected-set(audits))}, extra={sorted(set(audits)-expected)}')
    return audits

def control_passed(code: int, text: str, tag: str) -> bool:
    if code==0 or code==124: return False
    if re.search(r'unknown module|object file .* does not exist|failed to locate application|PANIC|timed out',text,re.I): return False
    if tag=='placeholder': return 'sorry' in text.lower() and 'error:' in text.lower()
    return 'error:' in text.lower() and ('unsolved goals' in text.lower() or 'rfl' in text.lower() or 'type mismatch' in text.lower())

def execute(command: list[str], cwd: Path, log: Path, timeout: int = 360) -> dict:
    start=time.monotonic()
    # The Lean helper owns the compiler process group and its stricter timeout.
    try:
        proc=subprocess.run(command,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                            text=True,timeout=timeout)
        code=proc.returncode; text=proc.stdout
    except subprocess.TimeoutExpired as exc:
        code=124; text=(exc.stdout or b'').decode(errors='replace') if isinstance(exc.stdout,bytes) else (exc.stdout or '')
        text+='\nOuter orchestration timeout\n'
    log.write_text(text)
    return {'command':command, 'exit_code':code,'seconds':round(time.monotonic()-start,3),
            'log':str(log.relative_to(ROOT)) if log.is_relative_to(ROOT) else str(log),
            'log_sha256':sha(log)}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit',type=Path,required=True)
    parser.add_argument('--run-dir',type=Path,help='Must not already exist')
    args=parser.parse_args()
    kit=args.kit.resolve()
    run=(args.run_dir or ROOT/'verification/runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')).resolve()
    run.mkdir(parents=True,exist_ok=False)
    build=run/'build';build.mkdir()
    report={'release':'PRSC_IX_v0.11.0_Nishibuchi_Completion','started_utc':datetime.now(timezone.utc).isoformat(),
            'status':'INCOMPLETE','fresh_build_directory':True,'modules':[],'controls':[],
            'allowed_axioms':sorted(ALLOWED),'compiler_warnings_are_errors':True,
            'mathlib_rebuilt_from_source':False,'original_numerical_suite_rerun':False}
    try:
        observed=source_inventory()
        pinned=json.loads((ROOT/'inventory.json').read_text())
        if observed!=pinned: raise ValueError('Pinned project inventory does not match active sources')
        report['coverage_counts']=validate_coverage(observed)
        report['upstream_module_count']=70
        report['upstream_sources_unchanged']=True
        report['inventory_sha256']=sha(ROOT/'inventory.json')
        report['verifier_sha256']=sha(Path(__file__))
        report['runner_sha256']=sha(ROOT/'scripts/check_low_memory.py')
        version=execute(['bash',str(kit/'run.sh'),'lean','--version'],kit,run/'version.log')
        if version['exit_code']!=0 or f'version {LEAN_VERSION},' not in (run/'version.log').read_text():
            raise ValueError('Pinned Lean version check failed')
        report['version_check']=version
        report['lean_version_output']=(run/'version.log').read_text().strip()
        manifest_path=kit/'workspace/lake-manifest.json'
        manifest=json.loads(manifest_path.read_text())
        pins=json.loads((ROOT/'provenance/dependency_pins.json').read_text())
        report['dependency_revision_checks']=[]
        for name,revision in pins.items():
            entry=next(x for x in manifest['packages'] if x['name']==name)
            path=kit/'workspace/.lake/packages'/name
            head=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
            if head!=revision or entry['rev']!=revision: raise ValueError(f'Dependency revision mismatch: {name}')
            report['dependency_revision_checks'].append({'name':name,'head':head,'manifest_rev':entry['rev'],'passed':True})
        if pins.get('mathlib')!=MATHLIB_REVISION: raise ValueError('Unexpected Mathlib pin')
        report['theorem_count']=pinned['theorem_count']
        report['definition_count']=pinned['definition_count']
        report['abbreviation_count']=pinned['abbreviation_count']
        for entry in pinned['modules']:
            m=entry['module']
            command=[sys.executable,str(ROOT/'scripts/check_low_memory.py'),'--kit',str(kit),
                     '--threads','1','--timeout','240','--import-dir',str(build),
                     '--output',str(build/f'{m}.olean'),str(ROOT/entry['source'])]
            result=execute(command,ROOT,run/f'{m}.log',timeout=355)
            result.update({'module':m,'source_sha256':entry['sha256']})
            report['modules'].append(result)
            (run/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
            print(f'{m}: exit {result["exit_code"]} ({result["seconds"]}s)',flush=True)
            if result['exit_code']!=0 or 'PANIC' in (run/f'{m}.log').read_text(): raise ValueError(f'Compilation failed: {m}')
        expected={d['name'] for e in pinned['modules'] for d in e['declarations']}
        audit=run/'Audit.lean'
        audit.write_text('module\n'+'\n'.join('public import '+m for m in MODULES)+'\n\n'+
                         '\n'.join('#print axioms '+n for n in sorted(expected))+'\n')
        base=[sys.executable,str(ROOT/'scripts/check_low_memory.py'),'--kit',str(kit),
              '--timeout','240','--import-dir',str(build)]
        result=execute(base+[str(audit)],ROOT,run/'Audit.log')
        if result['exit_code']!=0: raise ValueError('Axiom audit compilation failed')
        report['axiom_audit_run']=result
        report['axiom_dependencies']=parse_audits((run/'Audit.log').read_text(),expected)
        cases={
            'false_equality':'module\npublic import NormalizationBoundary\nexample : (1:ℕ)=0 := by rfl\n',
            'placeholder':'module\npublic import NormalizationBoundary\nexample : (1:ℕ)=0 := by sorry\n',
            'false_normalized_bound':'module\npublic import NormalizationBoundary\nexample : (1:ℤ) ≤ padicValRat 3 (KomorebiPaperIX.Congruential.coeff 6 3 2 - KomorebiPaperIX.Congruential.coeff 6 3 1) := by\n  rw [KomorebiPaperIX.Normalization.difference_valuation]\n  norm_num\n',
            'false_even_length':'module\npublic import OddEulerExamples\nexample : KomorebiPaperIX.OddEuler.truncation 2 0 0 = KomorebiPaperIX.EulerCoefficients.eulerEven 0 := by\n  norm_num [KomorebiPaperIX.OddEuler.truncation, KomorebiPaperIX.EulerCoefficients.inverseEven, KomorebiPaperIX.OddPower.source, Finset.sum_range_succ, KomorebiPaperIX.OddEulerExamples.euler_anchor_values.1]\n',
            'false_extra_precision':'module\npublic import OddEulerExamples\nexample : (5:ℤ)^7 ∣ KomorebiPaperIX.EulerCoefficients.eulerEven 4 - KomorebiPaperIX.OddEuler.truncation 5 4 2 := by\n  rw [KomorebiPaperIX.OddEulerExamples.manuscript_error]\n  norm_num\n'}
        cases.update({
            'false_dyadic_scale': 'module\npublic import DyadicExamples\nexample : (KomorebiPaperIX.EulerCoefficients.eulerEven 1 : ℚ) = ∑ m ∈ Finset.range 2, KomorebiPaperIX.Dyadic.beta m * ((2:ℕ).descFactorial (2*m) : ℚ) * KomorebiPaperIX.Dyadic.sourceEven (1-m) := by\n  rw [KomorebiPaperIX.OddEulerExamples.euler_anchor_values.2.1]\n  norm_num [Finset.sum_range_succ, KomorebiPaperIX.Dyadic.sourceEven, KomorebiPaperIX.DyadicExamples.beta_one, Nat.descFactorial]\n',
            'false_dyadic_factorial': 'module\npublic import DyadicExamples\nexample : KomorebiPaperIX.Dyadic.beta 1 = -(2/3:ℚ) := by\n  rw [KomorebiPaperIX.DyadicExamples.beta_one]\n  norm_num\n',
            'false_dyadic_extra_precision': 'module\npublic import DyadicExamples\nexample : (6:ℤ) ≤ padicValRat 2 ((KomorebiPaperIX.EulerCoefficients.eulerEven 4 : ℚ) - KomorebiPaperIX.DyadicReconstruction.truncation 4 0) := by\n  rw [KomorebiPaperIX.DyadicExamples.manuscript_error_zero_valuation]\n  norm_num\n'
        })
        cases.update({'false_finite_sample_extension': 'module\npublic import MahlerExamples\nexample : KomorebiPaperIX.Mahler.difference 1 1 (fun n : ℕ => (n:ℤ)) 0 =\n KomorebiPaperIX.Mahler.difference 1 1\n (KomorebiPaperIX.Mahler.interpolant 0 (KomorebiPaperIX.Mahler.coefficient (fun n : ℕ => (n:ℤ)))) 0 := by\n norm_num [KomorebiPaperIX.Mahler.interpolant, KomorebiPaperIX.Mahler.coefficient]\n', 'false_zero_valuation': 'module\npublic import MahlerExamples\nexample : KomorebiPaperIX.PadicBounds.order 3 (0:ℤ_[3]) = 0 := by\n simp\n', 'false_nonunit_gain': 'module\npublic import MahlerExamples\nexample : (3:ℤ) ∣ KomorebiPaperIX.Mahler.difference 2 1 (fun n : ℕ => (3:ℤ)^n) 0 := by\n norm_num\n', 'false_unit_extra_gain': 'module\npublic import MahlerExamples\nexample : (5:ℤ)^3 ∣ KomorebiPaperIX.Mahler.difference 4 2 (fun n : ℕ => (2:ℤ)^n) 0 := by\n rw [KomorebiPaperIX.UnitModes.geometric_difference]\n norm_num\n'})
        cases.update({'false_unlifted_root': 'module\npublic import FiniteArithmeticExamples\nexample : (2:ZMod 9)^2=1 := by norm_num\n', 'false_composite_fermat': 'module\npublic import FiniteArithmeticExamples\nexample : (2:ZMod 9)^8=1 := by norm_num\n', 'false_dyadic_sign_collapse': 'module\npublic import FiniteArithmeticExamples\nexample : (1:ZMod 4)=-1 := by norm_num\n', 'false_outside_window_integrality': 'module\npublic import FiniteArithmeticExamples\nexample : ¬ 3 ∣ (KomorebiPaperIX.Congruential.coeff 6 3 1).den := by\n rw [KomorebiPaperIX.Congruential.coefficient_recurrence 6 3 (by decide : 0 < 1)]\n norm_num [Finset.sum_range_succ, Nat.choose]\n', 'false_noncoprime_CRT': 'module\npublic import FiniteArithmeticExamples\nexample : (0:ZMod 4)=2 := by norm_num\n'})
        cases.update({'false_fibonacci_sign': 'module\npublic import RecurrenceExamples\nexample : (Nat.fib 5:ℤ) = 3*(Nat.fib 3:ℤ) + (Nat.fib 1:ℤ) := by norm_num\n', 'false_unjumped_matrix': 'module\npublic import RecurrenceExamples\nopen KomorebiPaperIX FibonacciPackets Matrix\nexample : Companion.packet companion initial 2 0 1 = companion *ᵥ initial := by\n ext i\n fin_cases i <;> norm_num [Companion.packet, Companion.orbit, companion, initial, pow_two, Matrix.mul_apply, Matrix.mulVec, dotProduct, Fin.sum_univ_two]\n', 'false_jump_trace': 'module\npublic import RecurrenceExamples\nopen KomorebiPaperIX.FibonacciPackets\nexample : (companion^3).trace = 3 := by\n rw [trace_power_is_lucas]\n norm_num [lucas]\n'})
        cases.update({'false_period_at_zero': 'module\npublic import PeriodExamples\nopen KomorebiPaperIX WindowIndependence PeriodExamples\nexample : reduced 3 2 1=reduced 3 2 0 := by\n norm_num [reduced_one]\n', 'false_nondivisor_period': 'module\npublic import PeriodExamples\ninstance : Fact (Nat.Prime 5) := ⟨by decide⟩\nopen KomorebiPaperIX WindowIndependence PeriodExamples\nexample : reduced 5 3 3=reduced 5 3 2 := by\n norm_num [nondivisor_reduced_third, reduced_two, Nat.choose]\n', 'false_period_mod_p_squared': 'module\npublic import PeriodExamples\nopen KomorebiPaperIX\nexample : (2:ℤ)≤padicValRat 3 (Congruential.coeff 6 0 2-Congruential.coeff 6 0 1) := by\n rw [PeriodExamples.first_difference_precision_is_one]\n norm_num\n'})
        cases.update({
            'false_defect_derivation': 'module\npublic import DworkWindowExamples\nexample : KomorebiPaperIX.EGF.decode (KomorebiPaperIX.DworkAlgebra.B (PowerSeries.derivative ℚ_[3]) 3 ((PowerSeries.X:PowerSeries ℚ_[3])*PowerSeries.X^2)) 0 = 0 := by\n rw [KomorebiPaperIX.DworkWindowExamples.defect_cubic_constant]\n norm_num\n',
            'false_window_extra_power': 'module\npublic import DworkWindowExamples\nexample : (3:ℤ) ≤ padicValRat 3 (KomorebiPaperIX.Mahler.difference 1 2 (KomorebiPaperIX.Congruential.coeff 6 2) 1) := by\n rw [KomorebiPaperIX.DworkWindowExamples.window_second_difference_valuation]\n norm_num\n',
            'false_nonunit_euler_pivot': 'module\npublic import DworkWindowExamples\nexample : IsUnit (3:ℤ_[3]) := by\n rw [PadicInt.isUnit_iff]\n have h : ‖(3:ℤ_[3])‖ = (3:ℝ)⁻¹ := PadicInt.norm_p\n rw [h]\n norm_num\n',
            'false_composite_binomial_divisibility': 'module\npublic import DworkWindowExamples\nexample : 4 ∣ (4:ℕ).choose 2 := by norm_num [Nat.choose]\n'
        })
        cases.update({
            'false_amice_coefficient_integrality': 'module\npublic import SingularAmiceExamples\nexample : (0:ℤ) ≤ padicValRat 3 (PowerSeries.coeff 3 (KomorebiPaperIX.SectionLogBridge.sectionPullback 3 0)) := by\n rw [KomorebiPaperIX.SingularAmiceExamples.section3_coefficient_valuation]\n norm_num\n',
            'false_singular_ratio_normalization': 'module\npublic import SingularAmiceExamples\nexample : PowerSeries.constantCoeff (KomorebiPaperIX.SingularRatioAmice.rationalRatioPullback 6 (by decide) 2) = 1 := by\n rw [KomorebiPaperIX.SingularAmiceExamples.p3_singular_ratio_constant]\n norm_num\n'
        })
        cases.update({'false_global_extra_power': 'module\npublic import AllResidueExamples\nexample : (3:ℤ) ≤ padicValRat 3 (KomorebiPaperIX.Mahler.difference 1 2 (KomorebiPaperIX.Congruential.unnormalized 6 3) 1) := by\n rw [KomorebiPaperIX.AllResidueExamples.singular_second_valuation]\n norm_num\n', 'false_global_no_factorial_loss': 'module\npublic import AllResidueExamples\nexample : KomorebiPaperIX.GlobalEulerBoundary.precision 3 1 (KomorebiPaperIX.Mahler.difference 1 1 (KomorebiPaperIX.Congruential.coeff 6 3) 1) := by\n rw [KomorebiPaperIX.GlobalEulerBoundary.precision, KomorebiPaperIX.Mahler.difference_one, KomorebiPaperIX.Normalization.normalized_difference]\n norm_num [padicValRat_def, padicValInt, padicValNat.eq_zero_of_not_dvd]\n', 'false_composite_frobenius_square': 'module\npublic import FrobeniusSquare\nexample : (9:ℤ)^2 ∣ (2:ℤ)^(9^2)-(2:ℤ)^9 := by norm_num\n', 'false_centered_ratio_constant': 'module\npublic import RatioRiccati\nexample : PowerSeries.constantCoeff (KomorebiPaperIX.RatioRiccati.ratio 3 6 (by decide) 2 - PowerSeries.C (1:ℚ_[3])) = 0 := by\n rw [map_sub, KomorebiPaperIX.RatioRiccati.ratio_zero]\n norm_num\n'})
        cases.update({
            'false_dyadic_extra_power': 'module\npublic import ConjectureExamples\nexample : (2:ℤ) ≤ padicValRat 2 (KomorebiPaperIX.Congruential.unnormalized 4 1 1 - KomorebiPaperIX.Congruential.unnormalized 4 1 0) := by\n rw [KomorebiPaperIX.ConjectureExamples.dyadic_nonzero_address_valuation]\n norm_num\n',
            'false_degree_shift': 'module\npublic import ConjectureExamples\nexample : (4*(3+2^(3-1)):ℕ)=4*3+2^3 := by norm_num\n',
            'false_fourth_pivot': 'module\npublic import ConjectureExamples\nexample : ¬(2:ℕ) ∣ 4 := by norm_num\n',
            'false_constant_normalization': 'module\npublic import ConjectureExamples\nexample : KomorebiPaperIX.Congruential.unnormalized 4 3 0 = 1 := by norm_num [KomorebiPaperIX.Congruential.unnormalized]\n'
        })
        # This declared type forces the exact capstone parameter range and degree displacement.
        contract_source=(ROOT/'contracts/ExternalStatement.lean.txt').read_text()
        contract=run/'ExternalStatement.lean';contract.write_text(contract_source)
        report['statement_contract']=execute(base+[str(contract)],ROOT,run/'ExternalStatement.log')
        if report['statement_contract']['exit_code']!=0: raise ValueError('External statement contract failed')
        for tag,text in cases.items():
            path=run/f'negative_{tag}.lean.txt';path.write_text(text)
            # Feed an actual .lean file, retaining its clearly separated control role.
            src=run/f'negative_{tag}.lean';src.write_text(text)
            result=execute(base+[str(src)],ROOT,run/f'negative_{tag}.log')
            result.update({'name':tag,'expected_rejection':True,'source_sha256':sha(src)})
            passed=control_passed(result['exit_code'],(run/f'negative_{tag}.log').read_text(),tag)
            result['passed']=passed;report['controls'].append(result)
            src.unlink()
            if not passed: raise ValueError(f'Negative control failed: {tag}')
        report['build_files']={str(x.relative_to(build)):sha(x) for x in sorted(build.rglob('*')) if x.is_file()}
        report['status']='LEAN_BUILD_AND_AXIOM_AUDIT_PASS'
    except Exception as exc:
        report['status']='FAILED';report['failure']=f'{type(exc).__name__}: {exc}'
        print(report['failure'],file=sys.stderr,flush=True)
    finally:
        report['finished_utc']=datetime.now(timezone.utc).isoformat()
        (run/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],flush=True)
    return 0 if report['status']=='LEAN_BUILD_AND_AXIOM_AUDIT_PASS' else 1

if __name__=='__main__': raise SystemExit(main())
