from pathlib import Path
import hashlib,json,shutil,zipfile
ROOT=Path.cwd();out=ROOT/'deliverables'
base=out/'Komorebi_Unified_Inference_Stochastic_Bayesian_CONTINUATION_v13_2026-09-12'
work=ROOT/'release_candidate'
focus_name='FD_Certified_Inference_Core_v1.0.0_Checked'
full_name='Komorebi_Unified_Inference_Stochastic_Bayesian_CONTINUATION_v14_2026-09-12'
parent_hash='8f6bde58df0b6b18388f60adff4a22e5fed0a69d0a8f66321922452950cf3ba7'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(root,name):
    files=sorted(p for p in root.rglob('*') if p.is_file() and p!=root/name)
    (root/name).write_text(''.join(f'{sha(p)}  {p.relative_to(root).as_posix()}\n' for p in files));return len(files)
def validate(root,name):
    listed=set()
    for l in (root/name).read_text().splitlines():
        h,p=l.split('  ',1);assert sha(root/p)==h,p;listed.add(p)
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p!=root/name}
    assert listed==actual;return len(listed)
def zipdir(root):
    dest=out/(root.name+'.zip')
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(root.parent))
    with zipfile.ZipFile(dest) as z:assert z.testzip() is None
    dest.with_suffix('.zip.sha256').write_text(f'{sha(dest)}  {dest.name}\n')
    return dict(filename=dest.name,sha256=sha(dest),bytes=dest.stat().st_size)
assert sha(base.with_suffix('.zip'))==parent_hash
base_manifest=validate(base,'SHA256SUMS')
r=json.loads((work/'FINAL_VERIFICATION_RECEIPT.json').read_text())
assert r['status']=='PASS' and r['all_final_receipts_after_clean_start']
assert r['final_modules_passed']==117 and r['theorem_lemma_declarations']==543
assert json.loads((work/'results/FULL_COST_BENCHMARK.json').read_text())['status']=='PASS'
for p in list(work.rglob('__pycache__')):shutil.rmtree(p)
focus=out/focus_name;shutil.copytree(work,focus)
nfocus=manifest(focus,'MANIFEST_SHA256.txt');assert validate(focus,'MANIFEST_SHA256.txt')==nfocus
fzip=zipdir(focus)
full=out/full_name;shutil.copytree(base,full)
history=full/'HISTORY/v13_root_control';history.mkdir()
for p in list(full.iterdir()):
    if p.is_file():shutil.move(str(p),history/p.name)
active='CHECKED_RELEASES/'+focus_name;shutil.copytree(focus,full/active)
(full/'START_HERE.md').write_text(f'''# Start here — v14 / Certified Inference Core 1.0.0

Author: Komorebi P. Date: 2026-09-12.
Read CONTINUE_HERE.md, AUDIT.json and PROTOCOL.md, then
{active}/RELEASE_SCOPE.md and README.md.
This is the finished scoped research core; broader scalability, rounded-selective,
sequential and novelty claims remain explicit extensions. All inherited v13 checked
releases are unchanged. Former root controls are in HISTORY/v13_root_control.
''')
(full/'CONTINUE_HERE.md').write_text(f'''# Komorebi Unified Inference / Stochastic / Bayesian — v14

Author: Komorebi P. Date: 2026-09-12.
Active release: {active}.
Parent archive SHA256: {parent_hash}.

## Frozen first-release claim

Certified Inference Core 1.0.0 completes the declared finite-dimensional,
one-observation inference reference system. For valid exact factor-coded rational
model data, positive noise floor, complete self-adjoint rational packet families,
a covering output-label scan and positive rational epsilon/delta, the canonical
program Komorebi.CachedPosterior.runCached returns a result satisfying ResultValid:

    W2(actual Bayesian posterior, Joseph Gaussian at returned gain) <= epsilon,

passing candidate/tolerance checks, plus outward-rounded mean/covariance intervals
of that same approximation with every radius <= delta. Covariance centers do not
independently define a certified law; delta is not exact-posterior coordinate error.
The parser/exporter are outside universal refinement. A generated Lean instance
certifies its explicit rational data only after actual successful compilation.

## Newly closed mathematical and implementation block

Exact cache state stores G_a = Q_a F(B), e_a = ||G_a||_F^2 and total = sum e_a.
With T = I - tau S and tau = 1/(sigma + trace S), a selected update maintains

    B' = B + tau G_a,       G_a' = G_a T,
    e_a' = ||G_a'||_F^2,    total' = total - e_a + e_a'.

Other output-packet cache entries are unchanged. Initialization and preservation
of every invariant are proved. Cache selection equals the v13 maximum-energy rule;
its trajectory equals the recomputed exact greedy trajectory. Inherited contraction
therefore supplies computed finite fuel. Cached exact-score tests use epsilon^2/4
slack; full rounded verification runs only after that test passes. A sufficient
verification fallback must then succeed. The returned gain is tied to an actual
permitted iterate. The v12 output theorem completes the same returned result.

Main declarations in namespace Komorebi.CachedPosterior:
  initialState_valid, step_valid, total_eq_residual_energy, score_eq,
  chosen_eq, trajectory_gain, trajectory_score_at_fuel,
  solveCached_terminates, cached_solver_gain_origin,
  cached_solver_reaches_posterior_tolerance,
  runCached_terminates, runCached_sound.

The cached selective branch uses exact rational updates and cache values. The
v11 rounded FULL-update solver remains a separate checked branch. Do not combine
these facts into a rounded selective-update theorem.

## Concrete checked results

Coordinate case: six cached updates, selections 0,1,0,1,0,1,
gain (228/343,57/343)^T, 12-bit certificate score 481/1048576, epsilon=1/20.
Singular rotated case: four updates, selections 0,0,0,0,
gain (203/625)ones(2,2), 12-bit certificate score 9111/1048576, epsilon=1/4.
Both use 32-bit parameter output with delta=1/1000. These full-program examples
check selections, actual returns, interval arrays and posterior guarantees.
The stricter exact-score margin explains the extra iteration relative to v13.

Twenty-one additional benchmark candidate certificates (seven models, three modes)
are checked for posterior tolerance. They do not certify Python timing traces or
all timed numeric arrays. Universal output correctness, two full-program instances,
and independent diagnostic formulas cover the declared output obligations.

## An unsuccessful route and honest performance result

Independently rounding gain and cached residual centers breaks cache validity.
A kernel-checked scalar counterexample has cached score zero but true score two;
the independent final verifier rejects it. A rounded cache with propagated error
bounds remains open. No unsafe success theorem is exported for this route.

The bounded benchmark uses dimensions <=8, five repetitions after warmup, identical
exact arithmetic backend/tolerance/output contracts, and an efficient full Richardson
baseline. Caching makes selective iteration roughly 1.9-5.6 times faster than full
packet recomputation. Total producer ratios are only about 1.01-1.17. No overall
advantage over the efficient full baseline is established. Final verification,
output, and Lean checking dominate much of this tested range. BENCHMARK_REPORT.md
includes export and actual per-candidate checking costs; counters are not a formal
bit-complexity theorem and this is not a scalability demonstration.

## Attribution and evidence

The bounded primary-literature review identifies established overlap with
Gauss-Southwell/block descent, cached gradients, pathwise conditioning/Wasserstein
error and formally checked arithmetic certificates. It supports conservative
attribution, not a priority or breakthrough claim. No new external theorem is an
unproved Lean dependency. See LITERATURE_COMPARISON.md for sources and search limits.

All {r['final_modules_passed']} active modules were freshly compiled after their project caches were removed;
{r['inherited_modules_unchanged']} inherited source modules are unchanged. Pinned mathlib caches were reused.
All {r['theorem_lemma_declarations']} theorem/lemma declarations are axiom-audited; {r['new_declarations']} are new support,
universal, concrete and benchmark declarations, not independent discoveries.
Only propext, Classical.choice and Quot.sound occur. Runtime: Lean 4.34.0-rc2,
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06, one thread, warnings as errors.
Final successful source/attempt/log/compiled-output/direct-dependency hashes match.
Three invalid Lean controls rejected; 1,068 diagnostic assertions and nine expected
producer rejections passed. Final Mathbox computation manifest validation passed.
Failures remain preserved. This is a clean build and adversarial self-review,
not an independent external audit. The PowerShell launcher was not run on Windows.

## Reproduction and future work

Read the active README for the proof-producing reference CLI and clean-build command.
Runtime binaries are distributed separately; restoration metadata is retained.
Resource caps may prevent completion. Python success remains provisional until its
exported explicit Lean instance compiles. No bounded-hardware guarantee follows
from the ideal finite-fuel theorem.

The scoped first-release theorem and artifact are complete. Future capabilities
are separate: performance at meaningful scale, faster full certificate checking,
rounded selective updates/approximate selection, hierarchy-changing refinement,
sequential filtering, uncertain inputs, parser refinement, point-valued factors or
sampling, and hardware arithmetic. Independent external review is still welcome.
Do not reopen completed foundations without identifying a concrete defect, and do
not treat these extension goals as silently proved by the first-release label.
''')
(full/'PROTOCOL.md').write_text((base/'PROTOCOL.md').read_text()+'''
The v14 cache invariants and selective trajectory are proved in exact rational
arithmetic. The naive independently rounded cache is refuted; the final verifier
rejects its false internal signal. Performance comparisons include complete cost;
no efficient-baseline superiority or literature priority is established. Maintain
this attribution and scope in future summaries. Clean active-source rebuilds may
reuse pinned mathlib caches but must not be called independent external audits.
''')
(full/'ONE_LINE_START.txt').write_text(f'Open {full_name}.zip; read START_HERE.md, CONTINUE_HERE.md, AUDIT.json and PROTOCOL.md; restore the completed scoped Certified Inference Core 1.0.0 and select a separately named extension without reopening its checked foundations or overstating performance and novelty.\n')
checked=[p for p in (base/'CHECKED_RELEASES').rglob('*') if p.is_file()]
for p in checked:assert sha(p)==sha(full/p.relative_to(base)),str(p)
for p in base.iterdir():
    if p.is_file():assert sha(p)==sha(history/p.name),str(p)
audit=dict(checkpoint='v14',release_version='Certified Inference Core 1.0.0',author='Komorebi P.',status='SCOPED_CORE_COMPLETE',active_release=active,source_commit=None,parent_archive_sha256=parent_hash,active_modules=r['final_modules_passed'],active_declarations=r['theorem_lemma_declarations'],new_declarations=r['new_declarations'],verification_environment=r['environment'],new_closed_checked=[{'id':'exact_cache_invariants','status':'CLOSED_CHECKED','main_theorem':'Komorebi.CachedPosterior.step_valid'},{'id':'cached_trajectory_equivalence','status':'CLOSED_CHECKED','main_theorem':'Komorebi.CachedPosterior.trajectory_gain'},{'id':'cached_posterior_completion','status':'CLOSED_CHECKED','main_theorem':'Komorebi.CachedPosterior.cached_solver_reaches_posterior_tolerance'},{'id':'cached_parameter_output','status':'CLOSED_CHECKED','main_theorem':'Komorebi.CachedPosterior.runCached_terminates'}],completed_bounded_validations=['Full-cost seven-case benchmark with 21 checked posterior candidates','Bounded primary-source attribution comparison','Fresh active-source rebuild and adversarial self-review'],unsuccessful_routes=['Naive independently rounded cache invariant refuted','Overall performance superiority not demonstrated','Literature priority not established'],verification_receipt=active+'/FINAL_VERIFICATION_RECEIPT.json',non_claims=r['non_claims']+['Parameter intervals enclose the certified approximation; centers do not independently define a certified Gaussian.'],future_extensions=['Large-scale practical performance and cheaper certificate checking','Rounded selective-update and approximate-selection convergence','Hierarchy-changing model/packet refinement','Sequential filtering recursion','Uncertain-input and parser refinement semantics','Point-valued output factor or sampler correctness','Hardware arithmetic','Independent external review and broader literature survey'],preservation=dict(source_archive=base.name+'.zip',source_sha256=parent_hash,source_manifest_entries=base_manifest,unchanged_inherited_checked_release_files=len(checked),old_root_controls='HISTORY/v13_root_control'))
(full/'AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
shutil.copy2(Path(__file__).resolve(),full/'PACKAGING_SCRIPT.py')
shutil.copy2(out/fzip['filename'],full/'RELEASE_ZIPS'/fzip['filename'])
nfull=manifest(full,'SHA256SUMS');assert validate(full,'SHA256SUMS')==nfull
zfull=zipdir(full)
record=dict(status='PASS',parent_manifest_entries=base_manifest,unchanged_inherited_checked_files=len(checked),focused_manifest_entries=nfocus,continuation_manifest_entries=nfull,zip_integrity_checks=2,focused=fzip,continuation=zfull)
(out/'CERTIFIED_CORE_PACKAGING_VERIFICATION.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
