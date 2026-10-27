#!/usr/bin/env python3
"""Write scoped Block 51 metadata only after a bound, passing fresh gate exists.

This script never edits Lean sources, controls, project configuration or runtime.
It preserves predecessor metadata and refuses to overwrite an existing closeout.
"""
from __future__ import annotations
import argparse
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil

VERSION = '0.51.0'
GENERATOR = 'KomorebiPhysics.Relativistic3DGeneratorBridge'
LATE_BASELINE_MODULES = [
    'KomorebiPhysics.Relativistic3DFourierHilbertStability',
    'KomorebiPhysics.Relativistic3DFourierCompactTime',
    'KomorebiPhysics.Relativistic3DFullFourierEvolution',
    'KomorebiPhysics.Relativistic3DTorusFourierEvolution',
    'KomorebiPhysics.Relativistic3DUnboundedDirac',
    'KomorebiPhysics.Relativistic3DWeightedDiracDomain',
]

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def require(condition: bool, message: str) -> None:
    if not condition: raise RuntimeError(message)

def read(path: Path):return json.loads(path.read_text())

def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(value.rstrip()+'\n')

def copied(source: Path, target: Path) -> dict:
    require(source.is_file() and not source.is_symlink(),f'Not a regular source: {source}')
    digest=sha(source)
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():require(sha(target)==digest,f'Refusing different existing copy: {target}')
    else:shutil.copy2(source,target)
    require(sha(target)==digest==sha(source),f'Copy identity failed: {source}')
    return {'bytes':target.stat().st_size,'sha256':digest}

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',type=Path,required=True)
    ap.add_argument('--task-root',type=Path,required=True)
    ap.add_argument('--gate',type=Path,required=True)
    ap.add_argument('--check-only',action='store_true')
    a=ap.parse_args()
    project,task,gate=(p.resolve() for p in (a.project,a.task_root,a.gate))
    receipt_path=gate/'receipt.json'; receipt=read(receipt_path)
    require(receipt.get('schema')=='komorebi.physics.centered-gate.v1','Wrong gate schema')
    require(receipt.get('status')=='PASS_SCOPED_CENTERED_EXTENSION','Fresh acceptance gate has not passed')
    for key in ('source_unchanged','objects_unchanged','relevant_runtime_unchanged'):
        require(receipt.get(key) is True,f'Unconfirmed gate identity: {key}')
    review_path=task/'review/FROZEN_SOURCE_REVIEW.json'; review=read(review_path)
    require(review['status']=='PASS_SEMANTIC_SOURCE_REVIEW','Semantic review is not passing')
    for row in review['source_files']:
        require(sha(project/row['path'])==row['sha256'],'Reviewed source changed: '+row['path'])
        require(receipt['source_sha256'][row['path']]==row['sha256'],'Gate differs from reviewed source')
    baseline_path=task/'BASELINE_MATHEMATICAL_INPUTS.json'; baseline=read(baseline_path)
    require(len(baseline['files'])==912,'Unexpected predecessor mathematical input count')
    for name,digest in baseline['files'].items():
        require(sha(project/name)==digest,'Inherited Lean input changed: '+name)
    require(sha(gate/'source_inputs.json')==receipt['source_inputs_sha256'],'Source-input receipt mismatch')
    inputs=read(gate/'source_inputs.json')
    for original,row in inputs.items():
        require(sha(Path(original))==row['sha256']==sha(gate/'snapshot'/row['snapshot']),
                'Current/snapshot input mismatch: '+original)
    require(sha(gate/'declarations.json')==receipt['declarations_sha256'],'Declaration inventory hash differs')
    declarations=read(gate/'declarations.json')
    require(len(declarations)==receipt['declarations'],'Declaration count differs')
    require(len({r['name'] for r in declarations})==len(declarations),'Duplicate declaration names')
    require(all(set(r['axioms'])<={'propext','Classical.choice','Quot.sound'} for r in declarations),
            'Forbidden axiom in declaration inventory')
    new_modules=set(receipt['new_modules'])
    require(new_modules=={r['module'] for r in review['source_files']},'Reviewed/gated root set differs')
    new_rows=[r for r in declarations if r['module'] in new_modules]
    generator_rows=[r for r in declarations if r['module']==GENERATOR]
    require(len(new_rows)==receipt['new_declarations'],'New declaration count differs')
    require(len(new_rows)+len(generator_rows)==len(declarations),'Unexpected audited root module')
    require(sha(gate/'commands.json')==receipt['commands_sha256'],'Command receipt hash differs')
    commands=read(gate/'commands.json')
    require(len(commands)==receipt['commands'],'Command count differs')
    for row in commands:
        require(sha(gate/row['log'])==row['log_sha256'],'Command log changed')
    source_counts=collections.Counter()
    for row in review['source_files']:source_counts.update(row['lexical_named_counts'])
    require(dict(source_counts)=={'theorem':74,'lemma':0,'def':15,'abbrev':11},'Source counts changed')
    legacy=read(project/'declaration_inventory.json')
    require(len(legacy['modules'])==142 and len(legacy['declarations'])==3718,'Legacy inventory changed')
    require(not (project/'BLOCK51_ACCEPTANCE.json').exists(),'Refusing existing Block51 closeout')
    if a.check_only:
        print(json.dumps({'status':'READY_TO_WRITE','gate_receipt_sha256':sha(receipt_path),
                          'new_environment_declarations':len(new_rows),'baseline_inputs':912},indent=2))
        return

    history=project/'history/metadata_v0.49.0'
    originals={}
    for name in ('README.md','CONTINUE_HERE.md','docs/SOURCE_MAP.md','declaration_inventory.json'):
        originals[name]=copied(project/name,history/name)
    write_json(history/'PRESERVATION.json',{'schema':'komorebi.physics.predecessor-metadata.v1',
        'note':'Exact predecessor metadata. Its content may describe older frontiers than the source archive label.',
        'files':originals})

    evidence=project/'verification/block51/current'
    for name in ('receipt.json','declarations.json'):
        copied(gate/name,evidence/name)
    provenance=project/'verification/block51/provenance'
    provenance_files={}
    candidates=[task/'runtime_recovery_receipt.json',task/'runtime_verification.log',
                task/'runtime_integrity_audit.json',task/'runtime_disk_cleanup.json',
                task/'verification/centered_run01/receipt.json']
    candidates.extend(sorted((task/'verification/baseline').rglob('*')))
    for path in candidates:
        if path.is_file() and not path.is_symlink():
            relative=path.relative_to(task)
            provenance_files[relative.as_posix()]=copied(path,provenance/relative)
    copied(baseline_path,provenance/'BASELINE_MATHEMATICAL_INPUTS.json')
    copied(review_path,provenance/'FROZEN_SOURCE_REVIEW.json')
    for name in ('FROZEN_SOURCE_REVIEW.md','INDEPENDENT_MATHEMATICAL_AUDIT.md'):
        if (task/'review'/name).is_file():copied(task/'review'/name,provenance/name)

    counts=receipt['control_counts']; total_controls=sum(counts.values())
    receipt_sha=sha(receipt_path)
    now=dt.datetime.now(dt.timezone.utc).isoformat()
    inventory={
      'schema':'komorebi.physics.scoped-declaration-inventory.v2','schema_version':2,
      'checkpoint':'PHYS-CENT-51','version':VERSION,
      'scope':'Historical inventory and current scoped audit are separate. No combined corpus-wide fresh count is asserted.',
      'legacy_inventory':{'path':'history/metadata_v0.49.0/declaration_inventory.json',
        'sha256':originals['declaration_inventory.json']['sha256'],'modules':142,'declaration_records':3718,
        'status':'preserved_historical_not_freshly_audited',
        'known_late_baseline_modules_missing_from_legacy':LATE_BASELINE_MODULES,
        'additional_generator_overlay':GENERATOR,
        'note':'The legacy list predates these later accepted modules. It is not a complete inventory of the current source tree.'},
      'fresh_gate':{'path':'verification/block51/current/receipt.json','sha256':receipt_sha,
        'local_import_closure_targets':receipt['local_targets'],'commands':receipt['commands'],
        'audited_root_environment_declarations':len(declarations),
        'declarations_path':'verification/block51/current/declarations.json',
        'declarations_sha256':receipt['declarations_sha256']},
      'current_scoped_extension':{'modules':receipt['new_modules'],'source_named_counts':dict(source_counts),
        'source_named_total':sum(source_counts.values()),'environment_declarations':len(new_rows),
        'declarations':new_rows,'source_files':review['source_files']},
      'preserved_generator_recheck':{'module':GENERATOR,'source_named_counts':{'theorem':37,'def':2},
        'environment_declarations':len(generator_rows),'declarations':generator_rows,
        'note':'Environment counts include generated declarations and differ from explicit source declarations.'}
    }
    write_json(project/'declaration_inventory.json',inventory)

    readme=f'''# Komorebi Physics: centered continuum verification

Formal checkpoint **{VERSION}**, PHYS-CENT-51.

This source package completes the centered approximation block for the free
Dirac field on a fixed flat torus. Its centered operators act on the same
infinite Fourier coefficient space as the self-adjoint continuum Hamiltonian.
The checked results cover the full maximal first-order domain, every nonreal
spectral parameter, and quadratic generator and propagator bounds under an
explicit third-order Fourier moment assumption.

The four new modules contain **74 named theorems, 15 definitions and 11
abbreviations**. The fresh gate audited **{len(new_rows)} compiled environment
declarations** from those modules, including generated helpers. The unchanged
strong-generator module contributes **37 named theorems and 2 definitions**,
with **{len(generator_rows)} compiled environment declarations** rechecked in
the same gate. These are scoped counts, not a total for the physics program.

## Main results

- Bounded, self-adjoint centered operators for every nonzero real spacing.
- Graph-domain convergence for every vector in the maximal continuum domain.
- Two-sided strong-resolvent convergence for every nonreal complex parameter
  and every square-summable field, with actual inverse and domain laws.
- Generator error at most `h² M₃(f) / 6` and propagator error at most
  `|t| h² M₃(f) / 6`, with the corresponding uniform bound on `|t| ≤ T`, `T ≥ 0`.
- All these statements transported through the actual Fourier equivalence to
  physical torus fields. The modal perturbation proof does not assume that
  different Dirac matrices commute.

## Evidence and navigation

- [Accepted gate receipt](verification/block51/current/receipt.json):
  {receipt['local_targets']} fresh local compilation targets, {receipt['commands']} recorded commands,
  {total_controls} controls ({counts['positive']} positive, {counts['elaboration_reject']} elaboration rejections,
  {counts['policy_reject']} axiom-policy rejection).
- [Proof guide](docs/BLOCK_51_PROOF_GUIDE.md) and [source map](docs/SOURCE_MAP.md).
- [Scoped inventory](declaration_inventory.json) and [progress ledger](PROGRESS_LEDGER_v0.51.0.md).
- [Preservation record](BLOCK51_PRESERVATION.json) and [acceptance record](BLOCK51_ACCEPTANCE.json).
- [Predecessor metadata](history/metadata_v0.49.0/PRESERVATION.json), retained unchanged.

The compiler is Lean 4.34.0-rc2 at commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned to
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Compiled external dependencies
are reused. The new local import closure was compiled into an empty object
directory. The five root modules received recursive axiom audits and actual
`leanchecker` replay using the same Lean kernel and imported environment.

## Replay

With the documented pinned portable runtime restored, run from this directory:

```sh
python3 verification/block51/current/snapshot/runner/verify_centered.py \\
  --project . \\
  --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \\
  --controls verification/block51/current/snapshot/CONTROL_MANIFEST.json \\
  --out-dir /absolute/path/to/a-new-verification-directory
```

The output directory must not already exist. The runtime is external and is not
reconstructed from this source package. Its compiler/source/cache identity is
checked by the supplied runner. Mutable dependency Git indexes are explicitly
excluded from the relevant runtime endpoint comparison and retained in the
provenance records.

## Exact boundaries

The bounded global operator has an explicitly auxiliary zero value at spacing
zero. Its modal evaluation and inverse laws require nonzero spacing, and its
graph limit uses a punctured neighborhood. The centered modal propagator and
resolvent instead use their continuum fill at zero. They are not identified as
the evolution or inverse of the auxiliary zero operator there.

The third-order moment requires actual series summability. The compact-time
bound retains `T ≥ 0`. This checkpoint proves strong resolvent convergence,
not operator-norm resolvent convergence. It does not identify a changing finite
sampled lattice with the fixed Fourier space.

Abstract unbounded spectral-functional-calculus linkage, finite-grid comparison,
interacting gauge evolution, the wider historical evidence audit, and physical
cosmological production remain separate obligations. Earlier cosmological
failures have not been repaired by these free-field theorems.

Original code retains the supplied MIT grant. Original prose and figures retain
the supplied CC BY 4.0 grant and third-party exceptions. See the publication
license and provenance notices supplied alongside this formal package.
'''
    write_text(project/'README.md',readme)

    continuation=f'''# Continue from the centered continuum checkpoint

Accepted checkpoint: **{VERSION}**, PHYS-CENT-51. The exact current receipt is
[verification/block51/current/receipt.json](verification/block51/current/receipt.json),
SHA-256 `{receipt_sha}`.

The strong generator and its entire maximal domain were already checked. This
checkpoint additionally closes the centered bounded-operator construction,
full graph-domain convergence, all-nonreal-parameter strong resolvents, and the
third-order-moment quadratic generator and propagator bounds. All physical
torus statements use the inherited actual Fourier equivalence.

## Next formal target

Link the existing unbounded self-adjoint Hamiltonian and its checked strongly
continuous unitary group to an abstract unbounded spectral-functional-calculus
or Stone-theorem API. The source-level generator characterization is already
proved. Do not replace this remaining API linkage with agreement only on finite
packets, or relabel the completed centered convergence theorems as still open.

## Separate continuation targets

1. Define sampling, interpolation, Nyquist projection and aliasing comparison
   for an actual changing finite spatial grid. The fixed infinite Fourier-space
   theorem does not supply those maps.
2. Transport regular background-gauge link estimates into the full Hamiltonian
   setting. Dynamical gauge fields and the Gauss constraint require their own
   definitions and proofs.
3. Reconcile the wider historical/gauge evidence and perform the remaining
   whole-book scientific review.
4. Keep cosmology matching, incoming states, coupled cutoff tests, capture and
   abundance inference in their separately tracked physical research program.

## Restart discipline

Replay the supplied current runner before changing a theorem. Keep the same
coefficient and physical Hilbert spaces, all-real mass quantification, nonzero
spacing witnesses, both-sided punctured limits, and actual third-order
summability. Preserve the distinction between the auxiliary zero-spacing global
operator and the continuously filled modal families. The propagator estimate
must retain `|t|`; the compact-time statement retains `T ≥ 0`.

Use the [proof guide](docs/BLOCK_51_PROOF_GUIDE.md), [source map](docs/SOURCE_MAP.md),
and [scoped inventory](declaration_inventory.json). The historical inventory has
142 module entries and 3,718 records and is deliberately not presented as a
fresh or complete census of the present source tree.
'''
    write_text(project/'CONTINUE_HERE.md',continuation)

    source_map_add='''

## Block 51: centered continuum operators, resolvents and rates

Source: *The Dirac Group and Its Generator*, section 3 (centered generator
family and resolvent limit), section 4 (global quadratic spacing estimate), and
its physical torus corollary. The accepted mathematical statements concern the
same infinite Fourier index space. Earlier sections of this source map retain
their historical status wording and are not revised into claims of a new audit.

| Source statement | Formal representatives | Exact scope |
|---|---|---|
| Bounded centered operator, `lem:bounded` | `Relativistic3DCenteredConvergence.centeredCoeffOperator`, `centeredCoeffOperator_norm_le`, `centeredCoeffOperator_selfAdjoint` | All real mass and nonzero real spacing, bound `sqrt(m²+3h⁻²)`. Zero spacing is an explicitly auxiliary zero global operator. |
| Exact Clifford difference, `eq:differenceenergy` | `norm_centered_mode_sub_sq` | Equality of squared spinor norm with the sum of the three squared momentum errors. |
| Full graph-domain limit, `thm:graphconv` | `centered_graph_tendsto`, `physical_centered_graph_tendsto` | Entire maximal first-order domain, two-sided punctured limit, no third-order assumption. |
| Genuine resolvents | `Relativistic3DCenteredResolvent.continuumCoeffResolvent_mem_domain`, `continuum_shift_resolvent`, `continuum_resolvent_shift`, `centered_shift_resolvent`, `centered_resolvent_shift` | Actual range/domain and inverse laws for every `z.im ≠ 0`. Centered inverse laws retain `h ≠ 0`. |
| Resolvent limit, `thm:resolvent` | `centered_resolvent_identity`, `centered_resolvent_error_le`, `centered_resolvent_tendsto` | Strong convergence on every coefficient field and all nonreal parameters, using the resolvent norm bound `1/abs(z.im)`. |
| Physical resolvent corollary | `physical_centered_resolvent_error_le`, `physical_centered_resolvent_tendsto` and physical inverse laws | Unitary transport through the existing torus Fourier equivalence. |
| Uniform sine error, `lem:sine` | `Relativistic3DCenteredRates.sinQuot_cubic_bound` | Global sharp stated coefficient `1/6`, all real arguments and spacings with the continuous modal fill. No separate optimality theorem. |
| Third-order moment, `eq:weight3` | `thirdOrderWeight`, `HasThirdOrderMoment`, `thirdOrderMoment` | Actual summability of `sum_j abs(k_j)^6 * norm(f_n)^2`, not merely a totalized sum expression. |
| Generator rate, `eq:genrate` | `centered_generator_quadratic_bound` | `h ≠ 0` and third-order summability imply `norm((H_h-H)f) ≤ h² M₃(f)/6`. Domain membership is derived. |
| Noncommuting modal comparison | `Relativistic3DModalPerturbation.modal_interpolation_hasDerivAt`, `modal_perturbation_bound` | Differentiates the actual product of the two unitary evolutions. No commutation of the distinct Hamiltonians is assumed. |
| Propagator rate, `eq:prop_rate` | `centered_propagator_quadratic_bound`, `centered_propagator_compactTime_bound` | All real times, bound with `abs(t)`, uniform for `abs(t) ≤ T` with `T ≥ 0`. |
| Physical rates, `cor:physicalrates` | `physical_generator_quadratic_bound`, `physical_propagator_quadratic_bound`, `physical_propagator_compactTime_bound` | Same moment measured on the physical field's Fourier coefficients. |

The exact fresh evidence and declaration inventory are linked from
[`../verification/block51/current/receipt.json`](../verification/block51/current/receipt.json)
and [`../declaration_inventory.json`](../declaration_inventory.json). The abstract
unbounded spectral-calculus API linkage remains outside this certificate, as do
finite sampled lattices, interacting gauge dynamics and cosmological validity.
'''
    write_text(project/'docs/SOURCE_MAP.md',(history/'docs/SOURCE_MAP.md').read_text().rstrip()+source_map_add)

    guide='''# Block 51 proof guide

The source target is the centered approximation argument in sections 3 and 4 of
*The Dirac Group and Its Generator*. The proof works on the inherited complete
coefficient Hilbert space and the actual torus Fourier equivalence.

## Construction and proof order

1. `Relativistic3DCenteredConvergence` transports the arbitrary real-momentum
   Clifford square into the Hilbert spinor representation. Its exact norm
   identity controls both individual symbols and their differences.
2. `boundedModewiseOperator` lifts any uniformly bounded family of mode maps
   to a continuous linear operator on the full coefficient space. The sine
   bound gives the centered norm estimate `sqrt(m²+3h⁻²)` for `h ≠ 0`.
   Summing modal symmetry proves self-adjointness.
3. The sine quotient is expressed using the continuous sinc function. This
   supplies a genuine two-sided modal limit. Centered modal norms are bounded
   by continuum modal norms, so errors are dominated by twice the continuum
   output. Its square sum is finite on the maximal domain. The checked
   coefficient dominated-convergence lemma yields the complete graph limit.
4. `Relativistic3DCenteredResolvent` constructs modal inverses for every nonreal
   parameter, using self-adjoint real spectrum and the imaginary-part norm
   lower bound. The uniform `1/abs(z.im)` estimate lifts the inverses to the
   coefficient space. The identity `H R_z f = f + z R_z f` proves range
   membership in the unbounded domain, and both inverse laws are supplied.
5. Applying the resolvent identity to `g = R_z f` reduces the resolvent error
   to the already proved graph error at this actual domain vector. The bound
   proves strong resolvent convergence for every square-summable input and
   every nonreal parameter. No convergence in operator norm is asserted.
6. `Relativistic3DCenteredRates` uses the global sine error with coefficient
   `1/6`. The third-order condition is a `Summable` proposition. It implies
   first-order domain membership and bounds the summed squared modal errors.
   This proves the full generator estimate under precisely the stated extra
   regularity.
7. `Relativistic3DModalPerturbation` differentiates the interpolation
   `U_A(t-s) U_B(s) ψ`. The two matrices need not commute. Unitarity and the
   real mean-value estimate give the perturbation bound with `abs(t)` for
   positive and negative times. Applying the exact Clifford difference norm
   and the third-order moment yields the full propagator rate.
8. The inherited Fourier equivalence transports graph limits, actual
   resolvents, inverse laws, and rates to physical torus fields. The compact
   time bounds are pointwise uniform on `[-T,T]` with the explicit `T ≥ 0`.

## Zero spacing and domain boundaries

The bounded global centered operator has auxiliary value zero at `h = 0`.
Its mode evaluation and inverse identities require `h ≠ 0`, and graph
convergence uses a punctured neighborhood. The filled modal propagator and
resolvent take continuum values at zero and are not identified as the
evolution or inverse of that auxiliary zero operator there.

The global third-order moment is not a finite-grid approximation. No rate is
claimed for arbitrary square-summable data without its summability hypothesis.
Strong resolvent convergence, in contrast, does hold for every such input.
The rate keeps the stated coefficient `1/6`; its optimality is not separately
proved.

## Verification and sensitivity

The fresh gate compiles the exact local import closure into empty local object
storage, audits all compiled constants owned by the five root modules, replays
each root with `leanchecker`, and runs positive, elaboration-rejection and
axiom-policy controls. Named source declarations and generated environment
constants are counted separately. External compiled dependencies and the Lean
kernel are reused under their recorded pins.

Positive controls exercise negative mass, negative spacing and time, physical
transport, arbitrary nonreal parameters, and concrete modes. Rejection controls
remove or alter spacing/domain/moment witnesses, signs, constants and filter
types. The custom-axiom control compiles in isolation before the recursive
axiom audit rejects it. Missing imports, timeouts and resource errors are not
accepted as intended rejections.

The complete result is in the [gate receipt](../verification/block51/current/receipt.json)
and [scoped inventory](../declaration_inventory.json). The [progress ledger](../PROGRESS_LEDGER_v0.51.0.md)
preserves failed development and infrastructure attempts separately from the
accepted run.

## Remaining programs

The abstract unbounded spectral-functional-calculus API linkage remains open.
Finite-grid sampling, interpolation and aliasing require separate maps and
estimates. Background or dynamical gauge coupling and cosmological matching,
state preparation, capture and abundance are not consequences of this block.
The full historical physics aggregate has not received a new complete audit.
'''
    write_text(project/'docs/BLOCK_51_PROOF_GUIDE.md',guide)

    ledger=f'''# Komorebi Physics progress ledger

Version: **{VERSION}**. Checkpoint: **PHYS-CENT-51**.
Accepted gate finished: **{receipt['finished_utc']}**.
Predecessor: the checked strong-generator frontier `v0.50.0-g1`, layered over
the preserved Block 49 source archive.

## Completed and accepted

- Four new mathematical modules, with 74 named theorems, 15 definitions and
  11 abbreviations. The actual gate audited {len(new_rows)} compiled constants
  owned by those modules, including generated helpers.
- Bounded self-adjoint centered operators for nonzero real spacing, exact
  modal difference norms, and two-sided full graph-domain convergence.
- Genuine continuum and centered resolvents for every nonreal parameter,
  actual domain and inverse laws, resolvent error bounds and strong limits.
- Third-order-moment generator and propagator rates with coefficient `1/6`,
  all real times and explicit compact-time hypotheses.
- Physical torus transport of operators, resolvents, convergence and rates.
- The unchanged generator source and all 912 recorded inherited Lean inputs
  retain their exact predecessor bytes.

## Fresh verification

The passing [receipt](verification/block51/current/receipt.json) is bound by
SHA-256 `{receipt_sha}`. It records {receipt['local_targets']} local compilation
targets, {receipt['commands']} commands, and {total_controls} controls:
{counts['positive']} positive, {counts['elaboration_reject']} elaboration rejection,
and {counts['policy_reject']} axiom-policy rejection. Five root modules received
actual kernel replay in the imported pinned environment. The audit covers
{len(declarations)} environment constants across those roots, including the
preserved generator module's {len(generator_rows)} constants. Its 37 named
theorems and 2 definitions are not newly added results.

The [independent source review](verification/block51/provenance/FROZEN_SOURCE_REVIEW.json)
examined the exact frozen source. Agreement is review evidence, not a substitute
for the compiler and kernel records. The external proof cache is pinned and
reused, not rebuilt from source. This is not a second proof assistant or a
fresh audit of the entire historical corpus.

## Failures and corrections

1. The first predecessor build used an unsupported Lake `-j` option and
   failed before compilation. [Record](verification/block51/provenance/verification/baseline/attempt01/launch.json)
   and [log](verification/block51/provenance/verification/baseline/attempt01/build.log).
2. The next predecessor build failed when the filesystem filled during
   runtime restoration. It was not counted as a pass. Removing reproducible
   downloaded archives freed space and the next build completed.
   [Failure](verification/block51/provenance/verification/baseline/attempt02_disk_full/FAILURE.json)
   and [successful build log](verification/block51/provenance/verification/baseline/attempt03/build.log).
3. The original optional all-files runtime check failed on mutable dependency
   Git-index bytes. A complete scan found nine such differences and no other
   declared-row mismatch. The strict all-files failure remains recorded.
   The accepted gate explicitly excludes those mutable indexes while checking
   compiler, source and cache bytes at both endpoints.
   [Recovery record](verification/block51/provenance/runtime_recovery_receipt.json).
4. The first integrated centered gate stopped before executing compiler
   commands because the runner wrongly required a build directory for the
   unused source-only `Cli` dependency. The runner was corrected to record
   such directories and verify each actual direct external import against the
   pinned cache. [Failed receipt](verification/block51/provenance/verification/centered_run01/receipt.json).
5. Early proof/control drafts contained elaboration, coercion, namespace,
   arithmetic simplification and strict-lint errors. Corrected sources passed
   their later checks. The delivered development evidence preserves those
   attempts separately from the accepted fresh run.

## Remaining obligations

The abstract unbounded spectral-calculus API linkage remains outside this
certificate. Actual finite spatial grids require sampling, interpolation,
Nyquist and aliasing comparisons. Interacting gauge dynamics, the wider
historical evidence audit, whole-book specialist review, and the unresolved
cosmological production/state/matching problems remain separate work.

## Exact restart point

Read [CONTINUE_HERE.md](CONTINUE_HERE.md), the [proof guide](docs/BLOCK_51_PROOF_GUIDE.md),
and the four modules listed in the scoped inventory. Replay the current gate
before edits. Preserve the actual domain witnesses, all-nonreal parameter
scope, both-sided punctured limits, third-order summability, `abs(t)` and
`T ≥ 0`. Do not turn the auxiliary zero-spacing bounded map into the unbounded
continuum operator by notation alone.
'''
    write_text(project/'PROGRESS_LEDGER_v0.51.0.md',ledger)

    preservation={'schema':'komorebi.physics.block51-preservation.v1','status':'PASS',
      'created_utc':now,'baseline_manifest_sha256':sha(baseline_path),'inherited_lean_inputs':912,
      'all_inherited_lean_inputs_unchanged':True,'files':baseline['files'],
      'predecessor_metadata':originals,'reviewed_new_sources':review['source_files'],
      'provenance_copies':provenance_files,
      'scope':'Byte identity and evidence copy provenance, not a fresh proof of every inherited declaration.'}
    write_json(project/'BLOCK51_PRESERVATION.json',preservation)
    metadata_names=['README.md','CONTINUE_HERE.md','docs/SOURCE_MAP.md','declaration_inventory.json',
                    'PROGRESS_LEDGER_v0.51.0.md','docs/BLOCK_51_PROOF_GUIDE.md','BLOCK51_PRESERVATION.json']
    acceptance={'schema':'komorebi.physics.block51-acceptance.v1','status':'PASS_SCOPED_CENTERED_EXTENSION',
      'version':VERSION,'checkpoint':'PHYS-CENT-51','created_utc':now,
      'gate_receipt':'verification/block51/current/receipt.json','gate_receipt_sha256':receipt_sha,
      'semantic_review_sha256':sha(review_path),'source_named_counts':dict(source_counts),
      'source_named_total':sum(source_counts.values()),'new_environment_declarations':len(new_rows),
      'generator_environment_declarations':len(generator_rows),'all_root_environment_declarations':len(declarations),
      'local_targets':receipt['local_targets'],'commands':receipt['commands'],'control_counts':counts,
      'metadata_sha256':{n:sha(project/n) for n in metadata_names},
      'trust_boundary':receipt['trust_boundary'],
      'remaining':['Abstract unbounded spectral-functional-calculus API linkage',
        'Finite sampled-lattice comparison','Interacting gauge dynamics',
        'Historical evidence and whole-book scientific review','Cosmological production and empirical validation']}
    write_json(project/'BLOCK51_ACCEPTANCE.json',acceptance)
    for name,digest in baseline['files'].items():require(sha(project/name)==digest,'Final preservation failed')
    for row in review['source_files']:require(sha(project/row['path'])==row['sha256'],'Final reviewed source changed')
    print(json.dumps({'status':'SCOPED_METADATA_WRITTEN','acceptance_sha256':sha(project/'BLOCK51_ACCEPTANCE.json'),
                      'gate_receipt_sha256':receipt_sha,'metadata_files':metadata_names},indent=2))

if __name__=='__main__':main()
