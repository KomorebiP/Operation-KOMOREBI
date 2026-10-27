#!/usr/bin/env python3
"""Serial source compilation, axiom allowlist, kernel replay, and negative controls.

The portable runtime and its cached dependencies are required and not bundled.
Imported Lean/Mathlib objects are trusted; leanchecker replays only our modules.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, platform, re, shutil
import subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULES = ['ExactResolution', 'Compression', 'Globalization', 'ObstructionTransport', 'Behavioral', 'Examples', 'DiscreteMemory', 'MemoryClosure', 'FiniteMemory', 'SplitMemory', 'MemoryExamples', 'FiniteHorizon', 'BehavioralMinimality', 'FiniteObservableModel', 'FiniteCertificate', 'ObservableExamples', 'ApproximateAlgebra', 'ApproximateBounds', 'ScalarBudgets', 'StableApproximation', 'ApproximateComposition', 'ApproximateExamples', 'ContinuousFlow', 'VariationOfConstants', 'ExponentialTransfer', 'ContinuousMemory', 'ContinuousClosure', 'ContinuousJets', 'ContinuousSplit', 'ContinuousExamples', 'ContinuousDefect', 'ExponentialBudgets', 'ContinuousApproximation', 'ContinuousStability', 'ContinuousApproxExamples', 'OrthogonalResolution', 'HilbertGlobalization', 'HilbertConditioning', 'GlobalizationRefinement', 'FiniteGlobalization', 'GlobalizationExamples', 'MinimumNormReconstruction', 'MinimumNormOptimality', 'SourceConditioning', 'ClosedRangeReconstruction', 'ReconstructionGlobalization', 'ReconstructionExamples', 'MetricObstruction', 'MetricRepresentatives', 'IntrinsicGlobalization', 'MetricObstructionTransport', 'MetricRefinement', 'QuotientMetricBoundaries']
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
PIN = '4.34.0-rc2'
PREFIX = 'Komorebi.SufficientResolution.'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def registry():
    rows=[]
    for f in sorted((ROOT/'Komorebi').rglob('*.lean')):
        ns=[]
        for n,line in enumerate(f.read_text().splitlines(),1):
            s=line.strip()
            m=re.match(r'namespace\s+(\S+)',s)
            if m: ns.append(m.group(1)); continue
            if re.match(r'end(?:\s|$)',s):
                if ns: ns.pop()
                continue
            m=re.match(r'(?:@\[[^\]]*\]\s*)?(theorem|lemma|def|abbrev|structure)\s+(\w+)',s)
            if m: rows.append({'name':'.'.join(ns+[m.group(2)]),'kind':m.group(1),
                               'file':str(f.relative_to(ROOT)),'line':n})
    if len({r['name'] for r in rows}) != len(rows):
        raise ValueError('Duplicate qualified declarations in source registry')
    return rows


def parse_axioms(text):
    pat=r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)"
    return {name: sorted(x.strip() for x in (deps or '').replace('\n',' ').split(',') if x.strip())
            for name,deps in re.findall(pat,text,re.S)}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', type=pathlib.Path, required=True,
                    help='Extracted Komorebi_Portable_Lean_4.34.0-rc2 directory')
    ap.add_argument('--out', default='verification/local-replay')
    ap.add_argument('--timeout', type=int, default=180,
                    help='Per-command wall-clock timeout, seconds')
    ap.add_argument('--skip-kernel-replay', action='store_true',
                    help='Explicitly skip leanchecker; recorded as reduced verification')
    args=ap.parse_args()
    kit=args.runtime.expanduser().resolve(); launcher=kit/'run.sh'
    if not launcher.is_file(): ap.error('Missing portable runtime run.sh')
    if args.timeout < 1: ap.error('--timeout must be positive')
    out=(ROOT/args.out).resolve()
    if not out.is_relative_to(ROOT): ap.error('--out must stay inside the project')
    out.mkdir(parents=True,exist_ok=True)
    started=datetime.datetime.now(datetime.timezone.utc).isoformat(); t0=time.monotonic()
    env=os.environ.copy(); env['LEAN_NUM_THREADS']='1'; env['TERM']=env.get('TERM','dumb')
    base=['bash',str(launcher)]
    events=[]; passed=False; error=None; axioms={}; rows=[]
    source_inputs=[ROOT/'Komorebi.lean',ROOT/'AxiomAudit.lean',ROOT/'lean-toolchain',
                   ROOT/'lakefile.toml',ROOT/'lake-manifest.json',
                   ROOT/'scripts/verify.py',ROOT/'scripts/check_examples.py',
                   ROOT/'scripts/check_discrete_memory.py',ROOT/'scripts/validate_manifest.py',
                   ROOT/'scripts/observable_model.py',ROOT/'scripts/check_observable_model.py',
                   ROOT/'scripts/approximate_certificate.py',ROOT/'scripts/check_approximate_bounds.py',
                   ROOT/'scripts/check_continuous_memory.py',ROOT/'scripts/check_continuous_approximation.py',
                   ROOT/'scripts/hilbert_certificate.py',ROOT/'scripts/check_hilbert_globalization.py',
                   ROOT/'scripts/reconstruction_certificate.py',ROOT/'scripts/check_reconstruction.py',
                   ROOT/'examples/reconstruction_input.json', ROOT/'scripts/quotient_metric_certificate.py',
                   ROOT/'scripts/check_quotient_metric.py', ROOT/'examples/quotient_metric_input.json']
    source_inputs+=sorted((ROOT/'Komorebi').rglob('*.lean'))
    before={str(p.relative_to(ROOT)):sha(p) for p in source_inputs}

    def run(name, command, expect_failure=False, contains=None):
        log=out/(name+'.log'); t=time.monotonic()
        rc=None; timed_out=False
        with log.open('w') as f:
            proc=subprocess.Popen(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,
                                  env=env,start_new_session=(os.name=='posix'))
            try: rc=proc.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out=True
                if os.name=='posix':
                    import signal
                    os.killpg(proc.pid,signal.SIGKILL)
                else: proc.kill()
                proc.wait(); rc=124
        text=log.read_text(errors='replace')
        ok=(rc!=0 if expect_failure else rc==0) and not timed_out
        if contains is not None: ok=ok and contains in text
        event={'name':name,'argv':command,'exit_status':rc,'timeout':timed_out,
               'seconds':time.monotonic()-t,'expected_failure':expect_failure,
               'passed':ok,'log':str(log.relative_to(ROOT))}
        events.append(event)
        print(('PASS ' if ok else 'FAIL ')+name,flush=True)
        if not ok: raise RuntimeError(f'{name} failed; see {log.relative_to(ROOT)}')
        return text

    try:
        run('attach',base+['attach',str(ROOT)])
        version=run('lean_version',base+['lean','--version'],contains=PIN)
        run('lake_version',base+['lake','--version'])
        manifest=json.loads((ROOT/'lake-manifest.json').read_text())
        for package in manifest['packages']:
            folder=ROOT/manifest['packagesDir']/package['name']
            got=run('pin_'+package['name'],['git','-C',str(folder),'rev-parse','HEAD'])
            if got.strip()!=package['rev']: raise RuntimeError('Dependency pin mismatch: '+package['name'])
        rows=registry()
        for f in [ROOT/'Komorebi.lean']+sorted((ROOT/'Komorebi').rglob('*.lean')):
            text=re.sub(r'/\-.*?\-/','',f.read_text(),flags=re.S)
            text=re.sub(r'--[^\n]*','',text)
            bad=re.findall(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',text)
            if bad: raise RuntimeError(f'Forbidden production construct in {f}: {bad}')
        # Clean only our own compiler output, never the attached dependencies.
        build=ROOT/'.lake/build/lib/lean'
        if not build.resolve().is_relative_to(ROOT): raise RuntimeError('Build output escapes project')
        if (build/'Komorebi').exists(): shutil.rmtree(build/'Komorebi')
        (build/'Komorebi.olean').unlink(missing_ok=True)
        for module in MODULES:
            src='Komorebi/SufficientResolution/'+module+'.lean'
            obj=build/'Komorebi/SufficientResolution'/(module+'.olean')
            obj.parent.mkdir(parents=True,exist_ok=True)
            run('compile_'+module,base+['lake','env','lean','-j1','-DwarningAsError=true',
                                       '-o',str(obj.relative_to(ROOT)),src])
        run('compile_root',base+['lake','env','lean','-j1','-DwarningAsError=true',
                                '-o',str((build/'Komorebi.olean').relative_to(ROOT)),'Komorebi.lean'])
        audit=out/'AxiomAudit.lean'
        audit.write_text('import Komorebi\n\n'+'\n'.join('#print axioms '+r['name'] for r in rows)+'\n')
        text=run('axiom_audit',base+['lake','env','lean','-j1','-DwarningAsError=true',str(audit)])
        axioms=parse_axioms(text)
        if set(axioms)!={r['name'] for r in rows}: raise RuntimeError('Axiom audit did not cover exact registry')
        unexpected={k:v for k,v in axioms.items() if set(v)-ALLOWED}
        if unexpected: raise RuntimeError('Unapproved axioms: '+repr(unexpected))
        (out/'axioms.json').write_text(json.dumps(axioms,indent=2)+'\n')
        (out/'declarations.json').write_text(json.dumps(rows,indent=2)+'\n')
        controls=out/'negative_controls'; controls.mkdir(exist_ok=True)
        false=controls/'FalseStatement.lean'
        false.write_text('theorem deliberatelyFalse : (0 : Nat) = 1 := by rfl\n')
        run('negative_false',base+['lean','-DwarningAsError=true',str(false)],True,'error:')
        placeholder=controls/'Placeholder.lean'
        placeholder.write_text('theorem deliberatePlaceholder : False := by sorry\n')
        run('negative_placeholder',base+['lean','-DwarningAsError=true',str(placeholder)],True,'sorry')
        custom=controls/'CustomAxiom.lean'
        custom.write_text('axiom forbiddenPremise : False\ntheorem basedOnForbidden : False := forbiddenPremise\n#print axioms basedOnForbidden\n')
        text=run('negative_custom_axiom_compiles',base+['lean','-DwarningAsError=true',str(custom)])
        found=parse_axioms(text).get('basedOnForbidden',[])
        if not (set(found)-ALLOWED): raise RuntimeError('Axiom screen failed its deliberate custom-axiom control')
        events.append({'name':'custom_axiom_screen_rejects','passed':True,'detected':found})
        if not args.skip_kernel_replay:
            for module in MODULES:
                run('kernel_'+module,base+['lake','env','leanchecker','--verbose',PREFIX+module])
        run('exact_rational_sanity', [sys.executable,str(ROOT/'scripts/check_examples.py')])
        run('exact_discrete_memory_sanity', [sys.executable,str(ROOT/'scripts/check_discrete_memory.py')])
        run('exact_observable_model_sanity', [sys.executable,str(ROOT/'scripts/check_observable_model.py')])
        run('exact_approximate_bounds_sanity', [sys.executable,str(ROOT/'scripts/check_approximate_bounds.py')])
        run('exact_continuous_memory_sanity', [sys.executable,str(ROOT/'scripts/check_continuous_memory.py')])
        run('exact_continuous_approximation_sanity', [sys.executable,str(ROOT/'scripts/check_continuous_approximation.py')])
        run('exact_hilbert_globalization_sanity', [sys.executable,str(ROOT/'scripts/check_hilbert_globalization.py')])
        run('exact_reconstruction_sanity', [sys.executable,str(ROOT/'scripts/check_reconstruction.py')])
        run('exact_quotient_metric_sanity', [sys.executable,str(ROOT/'scripts/check_quotient_metric.py')])
        after={str(p.relative_to(ROOT)):sha(p) for p in source_inputs}
        if before!=after: raise RuntimeError('Execution inputs changed during verification')
        passed=True
    except Exception as exc:
        error=str(exc); print('FAILED: '+error,flush=True)
    after={str(p.relative_to(ROOT)):sha(p) if p.exists() else None for p in source_inputs}
    report={'passed':passed,'started_at':started,'runtime_seconds':time.monotonic()-t0,
            'exit_status':0 if passed else 1,'error':error,'project_root':str(ROOT),
            'runtime_root':str(kit),'platform':platform.platform(),
            'source_module_count':len(MODULES),'named_declarations':len(rows),
            'theorem_declarations':sum(r['kind'] in ('theorem','lemma') for r in rows),
            'allowed_axioms':sorted(ALLOWED),'axiom_audit_count':len(axioms),
            'kernel_replay_performed':not args.skip_kernel_replay,
            'kernel_trust_boundary':'Same Lean kernel; imported Lean/Mathlib cache reused, not freshly replayed.',
            'events':events,'input_artifacts':[{'path':p,'sha256':v,'sha256_after':after.get(p)} for p,v in before.items()],
            'resource_limits':{'wall_seconds_per_command':args.timeout,'lean_num_threads':1,
                               'memory_cap':'not separately enforced','commands_run_serially':True},
            'non_claims':['No historical novelty or priority certificate.',
                          'The existing obstruction quotient retains Mathlib quotient norms. Projection hypotheses are explicit; nonclosed quotient seminorms may vanish on nonzero classes. Refinement fixes the compatibility space and ambient metric.',
                          'Canonical bounded source reconstruction uses complete actual range or an explicit closed-range hypothesis; arbitrary source recovery is only modulo ker(A). Source alpha and compatibility sigma are distinct.',
                          'Bounded real Banach-space generators only: no unbounded-generator/domain theorem, time-varying blocks, nonlinear dynamics, stochastic noise, or sampled-data identification guarantee.',
                          'Orthogonal Hilbert decomposition needs the stated projection/closed-range hypotheses; no positivity realization, general Lyapunov stability certificate, or Langlands correspondence.',
                          'Theorem declarations include helpers and concrete examples.',
                          'The Python row-reduction implementation is exact-rational tested, not itself formally verified or extracted from Lean.',
                          'Known operator models only; no inference guarantee from sampled data.',
                          'Finite continuous closure certificates concern exact generator moments/time derivatives at zero, not sampled-time values.',
                          'The full exponential solves the derived memory equation; converse reconstruction of arbitrary Volterra solutions is not separately formalized.',
                          'No unbounded-generator extension, inferred flow-growth hypothesis, sampled-data guarantee, or independently implemented proof checker.']}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    manifest={'schema_version':1,'claim_id':'KSR-0.9.0-METRIC-OBSTRUCTION-QUOTIENT',
              'repository':{'commit':None,'dirty':True,'note':'New source snapshot; input hashes recorded.'},
              'command':[sys.executable,'scripts/verify.py','--runtime',str(kit),'--out',args.out],
              'environment':{'software':['Lean 4.34.0-rc2','Mathlib '+ 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06',
                                         'Python '+platform.python_version(), 'SymPy '+__import__('sympy').__version__], 'hardware':platform.platform()},
              'mathematics':{'assertion_tested':'The enumerated Lean declarations compile, have only allowlisted axioms, and replay in the same kernel.' if not args.skip_kernel_replay else 'Source compilation and axiom checks only; kernel replay explicitly skipped.',
                             'coefficient_domain':'Semiring modules for exact resolution; commutative-ring modules for discrete dynamics and quotients; fields for finite observation/certificate results; finite ambient dimension for bounded observation horizon and dimension-minimality; finite alphabet for enumeration; finite hidden dimension for memory certificates; rationals for earlier examples; nontrivially normed fields and normed modules for analytic bounds (no finite dimension or completeness); real scalars for sharpness and unbounded-error theorems; real Banach spaces and bounded continuous linear generators for continuous memory/closure, finite hidden dimension or a supplied monic annihilator for finite continuous certificates; bounded real Banach generators and explicit nonnegative-time flow envelopes for continuous quantitative approximation; real inner-product spaces with explicitly projectable subspaces for orthogonal globalization, finite local dimension for automatic coercivity, and explicit closed realized range for Hilbert-space existence.',
                             'conventions':'S*T applies T first; chronological words i::w apply T_i before w.',
                             'inputs':list(before),'bounds':{'production_modules':len(MODULES),'theorem_declarations':report['theorem_declarations'],
                                                           'quantification':'General theorem statements, not inferred from sampled matrices.'},
                             'non_claims':report['non_claims']},
              'randomness':{'used':True,'generator':'Python random.Random, finite exact-rational controls only; Lean proofs deterministic','seed':20260913},
              'run':{'started_at':started,'runtime_seconds':report['runtime_seconds'],'exit_status':report['exit_status']},
              'outputs':[{'path':str((out/'report.json').relative_to(ROOT)),'sha256':sha(out/'report.json')}],
              'checks':[e['name'] for e in events if e.get('passed')],
              'result':'PASS' if passed else 'FAIL: '+str(error),
              'residual_risks':['Imported standard-library artifacts are trusted.','No independently implemented proof kernel used.','Version-1 manifest; extra before/after input hashes are in report.json.']}
    (out/'computation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'passed':passed,'report':str((out/'report.json').relative_to(ROOT)),
                      'theorems':report['theorem_declarations'],'audited':len(axioms)}),flush=True)
    return 0 if passed else 1

if __name__ == '__main__': raise SystemExit(main())
