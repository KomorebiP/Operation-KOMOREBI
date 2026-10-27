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
import time

ROOT = Path(__file__).resolve().parents[1]
MODULES = ['Realization','PredictiveClosure','Transfer','LinearClosure','LinearRefinement',
           'Normed','Polynomial','Memory','MemoryBounds','Examples',
           'PacketTree','TreeEnergy','InvariantCompletion','PredictiveCompletion','Block2Examples',
           'FiniteBayes','BayesianClosure','BayesianDefect','FinitePartitions','JointRefinement','FiniteStochastic','Block3Examples',
           'FiniteInstrument','PositivePriors','NormalizedDefect','InstrumentCompletion','InstrumentCoordinates','InstrumentRealization','Block4Examples',
           'BehaviorSpace', 'BehaviorMinimality', 'ObservableCore', 'ObservableRealization', 'BehaviorProbability', 'PositivePackets', 'Block5Examples', 'TestCones', 'TestTopology', 'CanonicalCone', 'FiniteTestRows', 'PositiveLift', 'PositiveLiftTopology', 'RobustFiniteDomains', 'FacetRobustness', 'CertifiedCorrection', 'Block6Examples','BaseNorm','BaseNormTopology','InstrumentContraction','FiniteTV','Conditioning','SharpConditioning','ObservationTree','PolicyComparison','BaseNormModels','Block7Examples','Block7BoundaryExamples','DefectPropagation','StrongRefinement','MemoryStability','MemoryApproximation','PacketApproximation','WeightedReconciliation','AtlasReconciliation','ReconciliationHilbert','Block8Examples','Block8ApproximationExamples','DataSpan','DelayClosure','Pseudoinverse','IdentificationBound','FinitePrefix','LearnedRealization','Block9Examples','RationalFeasibility','RationalCertificateSearch','RationalCertificateSoundness','Block10Examples','CoreStability','FilteringStability','SubspaceCoordinates','Block11Examples','OneSidedSubspace','NoisySubspaceResidual','Block12Examples','SpectralLowerBound','SpectralPseudoinverse','SpectralSharpness','Block13Examples','SpectralSubspaces','SpectralTail','SingularPerturbation','LeftSingularModes','NoisySpectralSubspace','BasisCoordinates','BasisDecoder','DecoderMatrixFormula','FiniteTableP32','Block14Examples']
EXPECTED_LEAN = '6a10ac8c22beadecabdbb0919c2b50214762f91d'
ALLOWED_AXIOMS = {'propext','Classical.choice','Quot.sound'}
PROHIBITED = re.compile(r'\b(sorry|admit|axiom|unsafe|native_decide|implemented_by|extern|run_tac|elab|macro)\b|skipKernelTC')

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory() -> dict[str, str]:
    paths = [ROOT/'KomorebiLSM.lean', ROOT/'AxiomAudit.lean', ROOT/'DECLARATIONS.json',
             ROOT/'lake-manifest.json', ROOT/'lean-toolchain', ROOT/'scripts/verify.py', ROOT/'scripts/ReplayModule.lean', ROOT/'COVERAGE.json', ROOT/'SOURCE_LINEAGE.json',
             ROOT/'scripts/check_metadata.py', ROOT/'scripts/build_inventory.py', ROOT/'RELEASE_COUNTS.json', ROOT/'scripts/RunRationalSearch.lean']
    paths += list((ROOT/'KomorebiLSM').glob('*.lean'))
    paths += list((ROOT/'negative_controls').glob('*.lean'))
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}

def run(args: list[str], env: dict[str,str], timeout: int = 120) -> dict:
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
    ap.add_argument('--timeout',type=int,default=120)
    args=ap.parse_args()
    if args.kit is None: ap.error('provide --kit or KOMOREBI_LEAN_KIT pointing to the restored offline kit')
    kit=args.kit.resolve(); out=args.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    report={'release':'0.14.0','passed':False,'complete':False,'stages':[],
            'source_snapshot':inventory(),'python':sys.version,'platform':sys.platform}
    def save(): (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    env=os.environ.copy(); env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env.get('PATH','')
    for key in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']: env.pop(key,None)
    lean=str(kit/'toolchain/bin/lean'); checker=str(kit/'toolchain/bin/leanchecker')
    try:
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
            for n,line in enumerate(p.read_text().splitlines(),1):
                if PROHIBITED.search(line): hits.append({'file':str(p.relative_to(ROOT)),'line':n,'text':line})
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
            text=rec['stdout']+rec['stderr']
            valid_rejection=(rec['returncode'] != 0 and not rec['timed_out'] and 'error:' in text
                and not any(s in text for s in ['does not exist','failed to open file','unknown module','Unknown identifier','unknown identifier','Unknown constant','Invalid field']))
            rec.update({'phase':'negative_control','name':src.stem,'expected_rejection':valid_rejection})
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
        report['failure']=repr(exc);save();print('FAIL:',exc,file=sys.stderr);return 1

if __name__=='__main__': raise SystemExit(main())
