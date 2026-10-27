#!/usr/bin/env python3
"""Clean, sequential compile, axiom audit, kernel replay and rejection controls.
No cached PASS is reused. The upstream environment is pinned, not rebuilt here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
MODULES = ['Realization', 'PredictiveClosure', 'Transfer', 'LinearClosure', 'LinearRefinement', 'Normed', 'Polynomial', 'Memory', 'MemoryBounds', 'Examples', 'PacketTree', 'TreeEnergy', 'InvariantCompletion', 'PredictiveCompletion', 'Block2Examples', 'FiniteBayes', 'BayesianClosure', 'BayesianDefect', 'FinitePartitions', 'JointRefinement', 'FiniteStochastic', 'Block3Examples', 'FiniteInstrument', 'PositivePriors', 'NormalizedDefect', 'InstrumentCompletion', 'InstrumentCoordinates', 'InstrumentRealization', 'Block4Examples', 'BehaviorSpace', 'BehaviorMinimality', 'ObservableCore', 'ObservableRealization', 'BehaviorProbability', 'PositivePackets', 'Block5Examples', 'TestCones', 'TestTopology', 'CanonicalCone', 'FiniteTestRows', 'PositiveLift', 'PositiveLiftTopology', 'RobustFiniteDomains', 'FacetRobustness', 'CertifiedCorrection', 'Block6Examples', 'BaseNorm', 'BaseNormTopology', 'InstrumentContraction', 'FiniteTV', 'Conditioning', 'SharpConditioning', 'ObservationTree', 'PolicyComparison', 'BaseNormModels', 'Block7Examples', 'Block7BoundaryExamples', 'DefectPropagation', 'StrongRefinement', 'MemoryStability', 'MemoryApproximation', 'PacketApproximation', 'WeightedReconciliation', 'AtlasReconciliation', 'ReconciliationHilbert', 'Block8Examples', 'Block8ApproximationExamples', 'DataSpan', 'DelayClosure', 'Pseudoinverse', 'IdentificationBound', 'FinitePrefix', 'LearnedRealization', 'Block9Examples', 'RationalFeasibility', 'RationalCertificateSearch', 'RationalCertificateSoundness', 'Block10Examples', 'CoreStability', 'FilteringStability', 'SubspaceCoordinates', 'Block11Examples', 'OneSidedSubspace', 'NoisySubspaceResidual', 'Block12Examples', 'SpectralLowerBound', 'SpectralPseudoinverse', 'SpectralSharpness', 'Block13Examples', 'SpectralSubspaces', 'SpectralTail', 'SingularPerturbation', 'LeftSingularModes', 'NoisySpectralSubspace', 'BasisCoordinates', 'BasisDecoder', 'DecoderMatrixFormula', 'FiniteTableP32', 'Block14Examples', 'StatisticalRefinement', 'ProgramRefinement', 'GrammarAccounting', 'MissingIntervention', 'ResetCertificate', 'SequentialConfidence', 'ConditionalStochasticCompletion', 'AveragedCongruence', 'SequentialLowerCertificate', 'PredictableResidual', 'RotationDensity', 'RotationModel', 'RotationRank', 'LorentzBaseNorm', 'RotationConeGeometry', 'RotationP46', 'RegularPolygonAngles', 'RegularPolygon', 'RotationApproximation', 'CertificateLearning', 'MatrixOrderUnit', 'MatrixEmbedding', 'MatrixRotation', 'UniformIntervalMoments', 'ContinuousInstrument', 'ContinuousReferenceChange', 'ContinuousRecords', 'ContinuousRecordReference', 'PolynomialGram', 'PolynomialGramP53', 'FiniteMomentIdentification', 'LegendreCounterexample', 'ContinuousBins', 'ContinuousBinnedRecords', 'BaseNormIntegration', 'BernsteinKernel', 'CellDistance', 'PositiveCellApproximation', 'TimeRecords', 'ContinuousTVDensity', 'ContinuousTV', 'PositivePolynomialApproximation', 'BernsteinCoefficientError', 'CertifiedTemplate', 'ConditionalEventTV', 'ContinuousPopulationBridge', 'PositiveCellResolution', 'PositiveCellUniform', 'PositiveCellP58', 'ContinuousRealizationP61', 'EllipsoidDiscovery', 'EllipsoidGeometry', 'EllipsoidDualCS', 'OrientedEllipsoid', 'EllipsoidPolynomial', 'EllipsoidDiscoveryP63', 'ObservationEquivalence', 'ObservationPolicyTransport', 'AffineObservationTransport', 'MeasureTVCalculus', 'MarkovMinorization', 'MarkovMarginals', 'BernoulliRecordSeparation', 'BernsteinRationalBasis', 'TensorBernsteinCertificate', 'BernsteinCellPositivity', 'DyadicBernsteinCertificate', 'BernsteinGridSearch', 'ConditionalBernoulli', 'ConditionalHoeffding', 'PredictableResidualAffine', 'ConditionalRandomMultiplier', 'BoundedResponseNoise', 'LorentzCylinder', 'RobustOrientedMargin', 'InteriorRepair', 'ConvexRepairBracketing', 'RationalSemicircle', 'RationalBernsteinMargin', 'CertifiedRepairUpper', 'CoefficientBox3', 'ComplexCoefficientBox', 'ConvexMargin', 'CountableConfidence', 'CoveredAdaptiveActions', 'CoveredActionBoundaries', 'PredictableResidualGeneral', 'PredictableResidualAnytime', 'PredictableResidualP66', 'CoveredAdaptiveEvidence', 'CurvedMomentGeometry', 'CurvedMomentInstrument', 'CurvedMomentPolynomial', 'CurvedMomentMarkov', 'KernelTVMeasurable', 'CurvedMomentTV', 'ObservationLawKernels', 'ObservationLawComparison', 'CurvedMomentRecordTV', 'CurvedMomentReferences', 'EuclideanMatrixNorms', 'DataSelectedGeometry', 'LorentzBoundaryFragility', 'MarkovRecords', 'MarkovWindows', 'ObservableMomentConditional', 'RegressionGeometry', 'ObservableMomentAlgebra', 'ObservableMomentProcess', 'ObservableOperatorSets', 'RegressionGaussian', 'RegressionRadius', 'RegressionExponential', 'VilleInequality', 'RegressionConfidence', 'ObservableMomentConfidence', 'ObservableMomentBoundaries', 'RationalSqrtEnclosure', 'RationalConfidenceArithmetic', 'OutwardConfidenceIntervals', 'RationalLorentzMatrix', 'PerturbedOperatorFixture', 'ProposalError', 'RationalBernsteinTermination', 'RationalLorentzAlgebra', 'ScalarRegressionConfidence', 'RationalRegressionConfidence', 'RationalTransform', 'RecordedBernsteinFixture', 'Section88ProposedDirectPosOrientation', 'Section88ProposedDirectPosGap', 'Section88ProposedDirectNegOrientation', 'Section88ProposedDirectNegGap', 'Section88ProposedRotatedPosOrientation', 'Section88ProposedRotatedPosGap', 'Section88ProposedRotatedNegOrientation', 'Section88ProposedRotatedNegGap', 'Section88ComparisonDirectPosOrientation', 'Section88ComparisonDirectPosGap', 'Section88ComparisonDirectNegOrientation', 'Section88ComparisonDirectNegGap', 'Section88ComparisonRotatedPosOrientation', 'Section88ComparisonRotatedPosGap', 'Section88ComparisonRotatedNegOrientation', 'Section88ComparisonRotatedNegGap', 'Section88Reference', 'UniformAbsoluteMoments', 'Section88ComparisonBudget', 'Section88CertifiedRepair', 'StrictRationalGeometry', 'StrictRationalSearch', 'StructuredLearning', 'StructuredRectangle', 'StructuredLearningCapstone', 'TransferLearningCertificate']
EXPECTED_LEAN = '6a10ac8c22beadecabdbb0919c2b50214762f91d'
ALLOWED_AXIOMS = {'propext','Classical.choice','Quot.sound'}
PROHIBITED = re.compile(r'\b(sorry|admit|axiom|unsafe|native_decide|implemented_by|extern|run_tac|elab|macro)\b|skipKernelTC')
CONTROL_INFRASTRUCTURE_ERROR = re.compile(
    r'does not exist|failed to open file|unknown module|unknown identifier|unknown constant|'
    r'failed to synthesize instance|error\(lean\.synthInstanceFailed\)|'
    r'did not consume the patterns|unexpected token|expected token|invalid field|'
    r'maximum recursion depth|maximum number of heartbeats|deterministic.*timeout|'
    r'timed out|timeout.*exceeded|out of memory|\bPANIC\b|stack overflow', re.I)

def classify_negative_control(rec: dict) -> dict:
    """Exclude setup/resource failures, including mixed diagnostics.

    A single intended mathematical diagnostic is necessary. Its semantic
    correspondence with the false control assertion is reviewed separately.
    """
    output = rec.get('stdout', '') + '\n' + rec.get('stderr', '')
    infrastructure = sorted(set(m.group() for m in CONTROL_INFRASTRUCTURE_ERROR.finditer(output)))
    errors = re.findall(r'\berror(?:\([^\n)]*\))?:', output, re.I)
    reasons = []
    if rec.get('returncode') != 1:
        reasons.append('The compiler did not return the ordinary diagnostic exit code 1.')
    if rec.get('timed_out', False):
        reasons.append('The control execution timed out.')
    if len(errors) != 1:
        reasons.append('Expected exactly one diagnostic from the intended rejected assertion.')
    if infrastructure:
        reasons.append('Setup, elaboration, linter or resource failure appears in the diagnostics.')
    return {'valid_rejection': not reasons, 'reasons': reasons,
            'error_diagnostic_count': len(errors), 'infrastructure_error_matches': infrastructure}

def lean_executable_text(source: str) -> str:
    """Mask comments and literal text while preserving code and line positions.

    Lean block comments nest. Comment delimiters inside strings, character
    literals and quoted identifiers do not open comments. Interpolated-string
    expressions remain code, so a prohibited token inside ``s!"{...}"`` is
    still detected. This is a lexical guard, not a Lean parser or proof check.
    """
    masked = list(source)
    n = len(source)
    i = 0

    def blank(start: int, end: int) -> None:
        for j in range(start, end):
            if source[j] != '\n':
                masked[j] = ' '

    def block_comment() -> None:
        nonlocal i
        start = i
        depth = 1
        i += 2
        while i < n and depth:
            if source.startswith('/-', i):
                depth += 1
                i += 2
            elif source.startswith('-/', i):
                depth -= 1
                i += 2
            else:
                i += 1
        blank(start, i)

    def string_literal(interpolated: bool, hashes: int | None) -> None:
        nonlocal i
        blank(i, i + 1)
        i += 1
        if hashes is not None:
            end = source.find('"' + '#' * hashes, i)
            stop = n if end < 0 else end + 1 + hashes
            blank(i, stop)
            i = stop
            return
        while i < n:
            if source[i] == '\\':
                stop = min(n, i + 2)
                blank(i, stop)
                i = stop
            elif source[i] == '"':
                blank(i, i + 1)
                i += 1
                return
            elif interpolated and source.startswith('{{', i):
                blank(i, i + 2)
                i += 2
            elif interpolated and source[i] == '{':
                blank(i, i + 1)
                i += 1
                code(interpolation=True)
            else:
                blank(i, i + 1)
                i += 1

    def code(interpolation: bool = False) -> None:
        nonlocal i
        braces = 1 if interpolation else 0
        while i < n:
            if source.startswith('--', i):
                end = source.find('\n', i)
                stop = n if end < 0 else end
                blank(i, stop)
                i = stop
            elif source.startswith('/-', i):
                block_comment()
            elif source[i] == '"':
                prefix = source[max(0, i - 64):i]
                raw = re.search(r"(?:^|[^\w'])r(#+)?$", prefix)
                hashes = len(raw.group(1) or '') if raw else None
                string_literal(bool(re.search(r'!\s*$', prefix)), hashes)
            elif source[i] == '«':
                end = source.find('»', i + 1)
                stop = n if end < 0 else end + 1
                blank(i, stop)
                i = stop
            elif source[i] == "'":
                char = re.match(r"'(?:[^'\\\n]|\\(?:u[0-9a-fA-F]{4}|.))'", source[i:])
                if char:
                    stop = i + len(char.group())
                    blank(i, stop)
                    i = stop
                else:
                    i += 1
            elif interpolation and source[i] == '{':
                braces += 1
                i += 1
            elif interpolation and source[i] == '}':
                braces -= 1
                if braces == 0:
                    blank(i, i + 1)
                    i += 1
                    return
                i += 1
            else:
                i += 1

    code()
    return ''.join(masked)

def prohibited_source_hits(source: str) -> list[dict]:
    """Return active prohibited-token locations with original source lines."""
    code = lean_executable_text(source)
    lines = source.splitlines()
    hits = []
    for match in PROHIBITED.finditer(code):
        line = source.count('\n', 0, match.start()) + 1
        hits.append({'line': line, 'token': match.group(), 'text': lines[line - 1]})
    return hits

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory() -> dict[str, str]:
    paths = [ROOT/'KomorebiLSM.lean', ROOT/'AxiomAudit.lean', ROOT/'DECLARATIONS.json',
             ROOT/'lake-manifest.json', ROOT/'lean-toolchain', ROOT/'scripts/verify.py', ROOT/'scripts/ReplayModule.lean', ROOT/'COVERAGE.json', ROOT/'SOURCE_LINEAGE.json',
             ROOT/'scripts/check_metadata.py', ROOT/'scripts/build_inventory.py', ROOT/'scripts/test_source_scan.py', ROOT/'scripts/test_negative_control_classifier.py', ROOT/'RELEASE_COUNTS.json', ROOT/'scripts/RunRationalSearch.lean',
             ROOT/'source/FOUNDATIONS_REVIEWED.md', ROOT/'lakefile.toml', ROOT/'ROADMAP_1.0.json', ROOT/'PROGRESS.json', ROOT/'CURRENT_CHECKPOINT.json']
    paths += list((ROOT/'KomorebiLSM').glob('*.lean'))
    paths += list((ROOT/'negative_controls').glob('*.lean'))
    lineage=json.loads((ROOT/'SOURCE_LINEAGE.json').read_text())
    repair_manifest=lineage.get('control_repair_manifest')
    if repair_manifest:
        paths.append(ROOT/repair_manifest['path'])
        for repair in lineage.get('inherited_control_repairs',{}).values():
            paths.extend(ROOT/repair[key] for key in ('preserved_original','preserved_repaired','clean_receipt'))
        paths += list((ROOT/'history/control_repairs').glob('*.before.stdout.txt'))
        recovered=ROOT/'history/control_repairs/ORIGINAL_DIAGNOSTIC_RECOVERY.json'
        if recovered.is_file(): paths.append(recovered)
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}

def run(args: list[str], env: dict[str,str], timeout: int = 900) -> dict:
    start = time.monotonic()
    proc = subprocess.Popen(args, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                            start_new_session=(os.name == 'posix'))
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name == 'posix': os.killpg(proc.pid, signal.SIGKILL)
        else: proc.kill()
        stdout, stderr = proc.communicate()
    return {'command':args, 'returncode':proc.returncode, 'timed_out':timed_out,
            'seconds':round(time.monotonic()-start,6), 'stdout':stdout,'stderr':stderr}

def parse_axioms(text: str, expected: set[str]) -> dict:
    parsed = {}
    for match in re.finditer(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",text,re.S):
        name, raw = match.groups()
        if name in parsed: raise ValueError(f'duplicate axiom record: {name}')
        parsed[name] = sorted(x.strip() for x in (raw or '').split(',') if x.strip())
    if set(parsed) != expected:
        raise ValueError(f'axiom inventory mismatch: missing={expected-set(parsed)}, extra={set(parsed)-expected}')
    for name,deps in parsed.items():
        if not set(deps) <= ALLOWED_AXIOMS: raise ValueError(f'unapproved axioms in {name}: {deps}')
    return parsed

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kit', type=Path, default=os.environ.get('KOMOREBI_LEAN_KIT'))
    ap.add_argument('--out',type=Path,default=ROOT/'.verification-run')
    ap.add_argument('--timeout',type=int,default=900)
    args=ap.parse_args()
    if args.kit is None: ap.error('provide --kit or KOMOREBI_LEAN_KIT pointing to the restored offline kit')
    kit=args.kit.resolve(); out=args.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    report={'release':'1.0.0','passed':False,'complete':False,'stages':[],
            'source_snapshot':inventory(),'python':sys.version,'platform':sys.platform}
    def save():
        pending=out/'report.json.pending'
        pending.write_text(json.dumps(report,indent=2)+'\n')
        pending.replace(out/'report.json')
    env=os.environ.copy(); env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env.get('PATH','')
    for key in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']: env.pop(key,None)
    lean=str(kit/'toolchain/bin/lean'); checker=str(kit/'toolchain/bin/leanchecker')
    adapter = None
    try:
        version=run([lean,'--version'],env,args.timeout)
        if (version['returncode'] != 0 and
                'failed to locate application' in version['stdout']+version['stderr'] and
                (kit/'compat/app_path.so').is_file()):
            report['runtime_initial_probe']=version
            adapter=tempfile.TemporaryDirectory(prefix='komorebi-lsm-runtime-')
            adapter_path=Path(adapter.name)/'app_path.so'
            shutil.copy2(kit/'compat/app_path.so',adapter_path)
            env['LD_PRELOAD']=str(adapter_path)+(os.pathsep+env['LD_PRELOAD'] if env.get('LD_PRELOAD') else '')
            report['runtime_compatibility']='Bundled executable-path adapter; same startup recovery as the portable kit launcher.'
            version=run([lean,'--version'],env,args.timeout)
        report['runtime_version']=version
        if version['returncode'] != 0 or EXPECTED_LEAN not in version['stdout']:
            raise RuntimeError('pinned Lean compiler/version unavailable')
        manifest=json.loads((ROOT/'lake-manifest.json').read_text())
        deps=[]; paths=[]
        for pkg in manifest['packages']:
            path=kit/'workspace/.lake/packages'/pkg['name']
            rev=run(['git','-C',str(path),'rev-parse','HEAD'],env,args.timeout)
            if rev['returncode'] != 0 or rev['stdout'].strip() != pkg['rev']:
                raise RuntimeError(f'dependency pin mismatch: {pkg["name"]}')
            deps.append({'name':pkg['name'],'revision':rev['stdout'].strip()})
            paths.append(str(path/'.lake/build/lib/lean'))
        report['dependencies']=deps
        report['replay_api']='LeanChecker.replayFromImports (pinned upstream Lean)'
        report['leanchecker_source_sha256']=sha(kit/'toolchain/src/lean/LeanChecker.lean')
        build=ROOT/'.build/lib/lean'
        if (ROOT/'.build').exists(): shutil.rmtree(ROOT/'.build')
        (build/'KomorebiLSM').mkdir(parents=True)
        env['LEAN_PATH']=os.pathsep.join([str(build),*paths,str(kit/'toolchain/lib/lean')])
        active=[ROOT/'KomorebiLSM.lean',ROOT/'AxiomAudit.lean']+list((ROOT/'KomorebiLSM').glob('*.lean'))
        hits=[]
        for p in active:
            hits.extend({'file':str(p.relative_to(ROOT)),**hit}
                        for hit in prohibited_source_hits(p.read_text()))
        if hits: raise RuntimeError(f'prohibited active source: {hits}')
        report['prohibited_source_hits']=hits
        for mod in MODULES + ['__root__']:
            src=ROOT/'KomorebiLSM.lean' if mod=='__root__' else ROOT/'KomorebiLSM'/f'{mod}.lean'
            obj=build/'KomorebiLSM.olean' if mod=='__root__' else build/'KomorebiLSM'/f'{mod}.olean'
            rec=run([lean,'-j1','-DwarningAsError=true','-o',str(obj),str(src)],env,args.timeout)
            rec.update({'phase':'compile','module':mod,'source_sha256':sha(src)})
            report['stages'].append(rec);save()
            if rec['returncode'] != 0 or rec['timed_out']: raise RuntimeError(f'compile failed: {mod}')
            print('COMPILED',mod,flush=True)
        rec=run([lean,'-j1','-DwarningAsError=true',str(ROOT/'scripts/RunRationalSearch.lean')],env,args.timeout)
        rec.update({'phase':'executable_examples','expected_stdout':'true\ntrue\nfalse\ntrue\nfalse'})
        report['stages'].append(rec);save()
        if rec['returncode'] != 0 or rec['timed_out'] or rec['stdout'].strip()!=rec['expected_stdout']:
            raise RuntimeError('exact rational executable examples failed')
        print('EXECUTED exact rational checker and finite search examples',flush=True)
        rec=run([lean,'-j1','-DwarningAsError=true',str(ROOT/'AxiomAudit.lean')],env,args.timeout)
        rec['phase']='axiom_audit';report['stages'].append(rec);save()
        if rec['returncode'] != 0 or rec['timed_out']: raise RuntimeError('axiom audit did not compile')
        declarations=json.loads((ROOT/'DECLARATIONS.json').read_text())
        report['axioms']=parse_axioms(rec['stdout'],{e['name'] for e in declarations})
        for mod in MODULES:
            replay_env=env.copy(); replay_env['KOMOREBI_REPLAY_MODULE']='KomorebiLSM.'+mod
            rec=run([lean,'-j1','-DwarningAsError=true',str(ROOT/'scripts/ReplayModule.lean')],replay_env,args.timeout)
            rec.update({'phase':'kernel_replay','module':mod})
            report['stages'].append(rec);save()
            if rec['returncode'] != 0 or rec['timed_out'] or 'KERNEL_REPLAY_PASS KomorebiLSM.'+mod not in rec['stdout']:
                raise RuntimeError(f'kernel replay failed: {mod}')
            print('REPLAYED',mod,flush=True)
        for src in sorted((ROOT/'negative_controls').glob('*.lean')):
            rec=run([lean,'-j1','-DwarningAsError=true',str(src)],env,args.timeout)
            assessment=classify_negative_control(rec)
            valid_rejection=assessment['valid_rejection']
            rec.update({'phase':'negative_control','name':src.stem,'expected_rejection':valid_rejection,
                        'diagnostic_assessment':assessment})
            report['stages'].append(rec);save()
            if not valid_rejection: raise RuntimeError(f'control not rejected correctly: {src.name}')
            print('REJECTED',src.stem,flush=True)
        if inventory()!=report['source_snapshot']: raise RuntimeError('source changed during verification')
        report['counts']={'theorems':sum(e['kind']=='theorem' for e in declarations),
          'named_declarations':len(declarations),'proof_modules':len(MODULES),'compiled_targets':len(MODULES)+1,
          'kernel_replays':len(MODULES),'negative_controls':len(list((ROOT/'negative_controls').glob('*.lean')))}
        report['passed']=True;report['complete']=True;save()
        print('PASS: clean compilation, axiom audit, kernel replay and negative controls.',flush=True)
        return 0
    except Exception as exc:
        report['failure']=repr(exc)
        try: save()
        except OSError as write_error:
            print('Unable to persist failure report:',write_error,file=sys.stderr)
        print('FAIL:',exc,file=sys.stderr);return 1
    finally:
        if adapter is not None: adapter.cleanup()

if __name__=='__main__': raise SystemExit(main())
