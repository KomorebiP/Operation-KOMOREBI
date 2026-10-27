from pathlib import Path
import json,hashlib,shutil
base=Path('/workspace/scratch/2e8d212e9ca7');r=base/'work11/Komorebi_LSM_Lean_0.10.0'
cover=json.loads((r/'COVERAGE.json').read_text());counts=json.loads((r/'RELEASE_COUNTS.json').read_text())
remaining=[x['proposition'] for x in cover['entries'] if x['status']!='complete']
progress={'release':'0.11.0','date':'2026-10-15','theory':'1.0.0','production_software_unchanged':'2.3.0','completed':cover['complete'],'partial':[32],'outstanding':remaining,'new_complete':[33,34],'current_block':[32,33,34],'next_restart':[32],'source_verification':{'passed':False,'complete':False,'report':'verification/block11_release_run/report.json'},'archive_verification':'Consult the separate exact-archive verification JSON.','unexecuted':['Full 87-proposition formalization','P32 noisy-table rank and singular-subspace perturbation bridge','Exhaustive upstream Mathlib rebuild/replay','Independent referee or second proof assistant','Production software verification','Training or sensor experiments','External publication']}
(r/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n')
(r/'README.md').write_text('''# Komorebi Large Signal Model — Lean 0.11.0

Komorebi P. Frozen theory: Foundations 1.0.0. This is a formalization release, not a replacement theory or production PR-LASM release.

**38 of 87 propositions complete; P32 partial; 48 not yet formalized.** This release closes P33 and P34 and proves a conditional coordinate-conditioning component of P32. It does not finish the three-proposition block or the whole framework.

Start with `LEAN_GUIDE.md`, `AUDIT.md`, `PROGRESS.json`, and `CONTINUE_HERE.md`. `COVERAGE.json` maps each exact frozen statement to source declarations. The ZIP includes the complete cumulative source, predecessor archive, failure records, verification scripts and evidence. The offline Lean runtime is supplied separately.

Verify `MANIFEST.json` before generating any caches. The source run is in `verification/block11_release_run/report.json`. The separate delivery verification JSON records a fresh extraction and rebuild of the exact ZIP; an old report is not a new verification run.
''')
(r/'LEAN_GUIDE.md').write_text('''# Large Signal Model Lean 0.11.0 — Guide

## Status and scope

38 complete, one partial (P32), 48 not formalized, frozen total 87. Relative to 0.10.0, P33 and P34 are complete. P32 is only partially formalized. The manuscript's written proofs and the status of their Lean translations are distinct. An unfinished Lean obligation is not by itself a counterexample or an open mathematical conjecture.

This release adds four modules, 30 named theorems (eight examples), and four rejection controls. Cumulative inventory: 82 proof modules, 83 compilation targets including the root, 1,338 named declarations, 1,028 named theorems (316 example and 712 supporting), and 76 rejection controls. These are source-index counts; they are not independent results or a measure of scientific completeness.

## P33 — square core reconstruction

`CoreStability.lean` uses the constructed orthogonal pseudoinverse from 0.9.0. The input error satisfies the strict inequality `‖E‖ < rowGain H`. `rowGain` is the inherited variational least row singular value, defined as the infimum of adjoint norm ratios, with the unit-sphere characterization already proved in `IdentificationBound.lean`. This is the same convention used for P16. It is not a new assumed inverse bound or a numerical singular-value calculation.

`core_inverse_laws` proves both inverse identities for the perturbed square core. `coreFit` is `(B H + F) (H+E)†`, now identified with the ordinary inverse estimator under those hypotheses.

The module proves:

- `core_error_identity`: fitted minus true operator equals `(F−BE)(H+E)⁻¹`.
- `core_error_bound`: norm at most `(‖F‖+‖B‖‖E‖)/(rowGain H−‖E‖)`.
- `core_fitted_residual` and `core_fitted_identity`: `(Bhat−B)H=F−Bhat E`, and its right-inverse form.
- `core_fitted_bound`: norm at most `(‖F‖+‖Bhat‖‖E‖)/rowGain H`.
- `core_checked_fitted_bound`: under `‖E‖≤e<rowGain(H+E)`, the denominator may instead be `rowGain(H+E)−e`.

These statements concern a fixed core and exact real linear algebra. They do not establish that finite observations cover the full process, or bound floating-point solve error.

## P34 — normalized filtering

`FilteringStability.lean` works in a real normed state space with a continuous linear mass functional `lam`. The formal name avoids Lean's reserved lambda token. `normalize lam u = (lam u)⁻¹ • u`; all semantic normalization theorems supply nonzero or positive mass explicitly.

`prediction_error` derives `D=L‖zhat−z‖+ε_B R` from the actual state and operator errors. `mass_lower` derives the fitted mass lower bound; `fitted_mass_positive` proves positivity under the strict budget. `normalized_residual` proves the exact subtraction identity. The numerator estimate uses the actual vector, rather than postulating the final posterior error.

`normalized_error_checked` uses a positive checked fitted denominator. `normalized_error_margin` uses the true mass margin minus the dual-norm error budget. `filtering_step` separates the state-error coefficient and forcing term. `filtering_path` applies the existing P18 product-sum theorem to the actual true and fitted recurrences. `filtering_uniform` proves the contraction estimate with a common gain below one and bounded nonnegative forcing.

The true state and posterior radius bounds are supplied hypotheses. A checked realized fitted denominator does not establish a probability cone for every fitted operator, or validity of unchosen branches.

## P32 — exactly what was proved and what remains

`SubspaceCoordinates.lean` constructs the projection from a true subspace to an estimated subspace without choosing orthonormal bases. Given the explicit gap `‖P−Q‖≤δ<1`, it proves the lower bound `sqrt(1−δ²)‖x‖≤‖Qx‖` and injectivity. For equal-dimensional subspaces, `coordinateEquiv` constructs the continuous linear inverse, and `coordinate_inverse_bound` proves the reciprocal square-root bound.

**The gap bound is a hypothesis here. It has not been derived from `Y=X+E`.** Remaining obligations are:

1. Connect the pinned sorted-singular-value definition to the required min-max characterization and prove the perturbation inequalities, including the maximum-rank zero convention.
2. Construct/identify the leading-r left singular subspace of Y and prove its tail residual estimate.
3. Prove the equal-rank orthogonal-projection norm identity, or another valid route to the same `2ε/s` bound.
4. Connect the basis-free coordinate equivalence to `U (Uhatᵀ U)⁻¹` and the stated smallest-singular-value bound.

The pinned Mathlib file `Analysis/InnerProductSpace/SingularValues.lean` supplies the definition, nonnegativity, monotonicity and support/rank facts. It does not supply the missing perturbation chain in the form needed here. No missing link is installed as an axiom or disguised as a completed data-dependent theorem.

## Examples and rejection controls

`Block11Examples.lean` contains eight kernel-checked theorems: positive mass, zero mass at the margin boundary, negative fitted mass, rare-branch amplification for every positive parameter, exact zero-noise core recovery, exact zero-noise filtering, a singular scalar core at the gap boundary, and comparison of the two scalar error bounds. These do not constitute empirical benchmarks.

The four new isolated controls intentionally attempt false claims: positive mass at a zero fitted denominator, positivity of a negative fitted denominator, a unit absolute posterior Lipschitz bound in the rare-branch example, and a strictly positive square-root lower bound at gap one. Controls only count if rejected with genuine proof errors and no missing imports or unknown identifiers.

## Verification and reproduction

Use the pinned Lean 4.34.0-rc2 commit `6a10ac8c22beadecabdbb0919c2b50214762f91d` and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency revisions are checked. The verifier removes project caches and compiles sequentially with warnings as errors, audits every named declaration, replays each project module through LeanChecker, and checks all expected proof rejections.

From the extracted project, before generating files:

```bash
python3 scripts/verify_hashes.py
python3 scripts/build_inventory.py
python3 scripts/check_metadata.py
```

Then run, substituting the restored kit's actual absolute path:

```bash
LD_PRELOAD=/absolute/kit/compat/app_path.so python3 scripts/verify.py --kit /absolute/kit --out /absolute/run-directory
```

The compatibility preload is the supplied runtime path shim, not a proof-check bypass. This host required `.olean.server` alongside proof objects even for batch Lean. Do not omit them when restoring this kit. Imported upstream libraries are pinned, not exhaustively rebuilt/replayed by this project run. No independent referee or second prover is claimed.

## Failure history

The original source archive passed all 1,351 declared hashes. The prior runtime directory had been pruned. First invocation failed because the compiler was missing. All seven saved runtime parts reconstructed the expected combined archive hash. Full extraction exhausted disk. A reduced extraction omitted `.olean.server` files that turned out to be required; those were restored from the same saved parts. These are environment failures, not rejected mathematical propositions.

Development failures include a premature compile before its dependency, the reserved lambda token, an unmarked noncomputable real inverse, a vector argument incorrectly sent to a semiring tactic, scalar/module rewrite and inequality-orientation fixes, explicit recurrence arguments, namespace disambiguation, and warnings-as-errors. An incorrect addition-inequality application caused repeated deterministic heartbeat limits; fixing its orientation resolved the issue. Raising the heartbeat limit alone did not fix it.

One exploratory inherited run compiled and replayed its old target list but failed the final source-snapshot check because development had resumed. An attempted process interruption did not succeed. That run is not accepted release evidence. The accepted cumulative run must use a stable source inventory. The metadata command was also once invoked from the wrong directory and rerun correctly. All available compiler snapshots and diagnostics are retained.

## Continuation

Resume P32 from the exact frozen statement and the gap list above. Preserve the 38 completed propositions and the distinctions between a conditional coordinate lemma, a noisy-table theorem, and global process identification. Do not change the frozen manuscript to make coverage easier.
''')
(r/'AUDIT.md').write_text('''# Block 11 mathematical audit

**Primary verdict: incomplete, with the smallest missing implication.** P33 and P34 have complete formal proof candidates; P32 still lacks the implication from the noisy table hypotheses to the singular-subspace projection-gap estimate. This verdict concerns completion of the requested P32–P34 block, not a refutation of the manuscript.

Review type: self-review against Foundations 1.0.0 §§33–35 and its frozen proof register. No independent referee is claimed. Current acceptance: pending cumulative verification.

| Obligation | Evidence | Status |
|---|---|---|
| P33 strict gap gives a two-sided square inverse | `core_inverse_laws` | Development compile passed |
| P33 exact residual identities | `core_error_identity`, `core_fitted_residual`, `core_fitted_identity` | Development compile passed |
| P33 true, fitted, checked-fitted denominators | Three `core_*_bound` theorems | Development compile passed |
| P34 actual prediction residual budget | `prediction_error` | Development compile passed |
| P34 strict positivity and exact normalized identity | `fitted_mass_positive`, `normalized_residual` | Development compile passed |
| P34 two denominator bounds | `normalized_error_checked`, `normalized_error_margin` | Development compile passed |
| P34 actual path and contraction | `filtering_step`, `filtering_path`, `filtering_uniform` | Development compile passed |
| P32 coordinate lower bound and inverse from an explicit gap | `coordinate_lower`, `coordinate_injective`, `coordinateEquiv`, `coordinate_inverse_bound` | Development compile passed |
| P32 singular-value perturbation/rank separation | Not implemented | Not addressed |
| P32 leading-subspace tail and equal-rank projection norm identity | Not implemented | Not addressed |
| P32 orthonormal-basis decoder formula | Not implemented | Not addressed |
| Boundary examples | Eight named example theorems | Development compile passed |
| Full cumulative and fresh ZIP verification | Separate reports | Pending |

Dependencies: inherited orthogonal pseudoinverse and adjoint-norm bounds → P33; continuous linear norm bounds and exact scalar normalization → P34 one-step inequalities → inherited P18 recurrence → pathwise bounds. Orthogonal Pythagoras + supplied projection gap → P32 conditional lower bound → injectivity + equal dimensions → constructed continuous inverse. No arrow from noisy table data to that supplied gap has been proved here.

P33 uses the inherited variational `rowGain` convention, with its proved unit-sphere characterization. It does not claim an additional bridge to Mathlib's sorted singular-value API. P34 drops unused cone structure and proves the norm statements under their sufficient radius and mass hypotheses; it does not infer a valid fitted probability cone. P32 keeps the missing hypothesis explicit in both source and coverage.

Frozen source and register hashes remain unchanged. The former 78 proof modules, 1,304 declaration records and 72 rejection controls remain unchanged. The original 0.10.0 ZIP and its hash are included for lineage.

Proofreading self-review covers only the four new modules and current release documents. Mathematical notation was translated to Lean's scalar action and continuous linear maps; no manuscript mathematical tokens were edited. Remaining mathematical issues are listed above, not hidden as copyediting corrections.
''')
(r/'PROGRESS.md').write_text('''# Progress — Large Signal Model Lean 0.11.0

38 of 87 complete; P32 partial; 48 not formalized. Thus 49 propositions remain unfinished. P33 and P34 are newly complete proof candidates, pending cumulative acceptance. P32 now has a conditional coordinate-conditioning component.

The four new modules contain 30 named theorems, including eight examples. Total: 82 proof modules; 1,338 declarations; 1,028 theorems; 76 negative controls. Metadata gate: 80 checks. These counts do not replace proposition-level correspondence review.

Next: finish P32's noisy-table-to-subspace-gap chain and the explicit orthonormal-basis decoder. Do not treat the supplied gap in `SubspaceCoordinates` as derived from data. See `LEAN_GUIDE.md` for the exact four remaining links.

Environment and development failures are retained. The inherited exploratory run that saw changing sources is not accepted release evidence. The current source run and separate fresh-archive report determine acceptance.
''')
(r/'CONTINUE_HERE.md').write_text('''# Continue here — Large Signal Model Lean 0.11.0

Current target status: 38 complete, P32 partial, 48 not formalized. P33/P34 have new formal proofs; consult the accepted source and exact-archive reports before relying on release acceptance.

Resume P32. Read Foundations 1.0.0 §33, the proof register, `AUDIT.md`, and `SubspaceCoordinates.lean`. The current coordinate map is projection between actual subspaces. Its lower bound, injectivity, constructed inverse and inverse norm bound take `‖P−Q‖≤δ<1` as an explicit hypothesis. They do NOT derive δ=2ε/s from Y=X+E.

Missing: singular-value min-max/perturbation including maximum-rank convention; actual leading-r left singular subspace and tail residual; equal-rank projection norm identity (or a substitute proof with the same constant); and the explicit orthonormal-basis matrix inverse formula. Avoid circularly putting these conclusions into a structure and calling that P32 complete.

P33 uses inherited variational rowGain and a constructed two-sided inverse, with all three error denominators. P34 includes actual state/operator prediction residuals, denominator positivity, exact normalization, path product-sum and uniform contraction. Keep the true radius and positive branch hypotheses.

Runtime recovery: the saved seven-part offline kit has combined SHA-256 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34. This host needs .olean.server files for batch imports. Full extraction can exceed disk capacity; preserve proof/runtime files, omit only known optional native/editor build artifacts. The runtime is not included in this ZIP. Do not assume transient absolute paths survive.

Verify hashes before generating caches. Preserve all 78 predecessor proof modules and old evidence. Do not edit inventoried files during an accepted verification run. The failed exploratory snapshot and development compiler records remain for diagnosis.
''')
(r/'COVERAGE.md').write_text('# Coverage — Large Signal Model Lean 0.11.0\n\n38 complete, one partial, 48 not formalized. Frozen total 87.\n\n'+''.join(f"- P{e['proposition']}: {e['title']} — {e['status']}\n" for e in cover['entries'])+'\nSee COVERAGE.json for exact source hashes, scope and named targets.\n')
(r/'ROADMAP_1.0.md').write_text('# Roadmap — 0.11.0 to the frozen 87-proposition target\n\n49 remain unfinished: P32 partial and 48 not formalized. Next is P32; the other tracks remain as recorded in ROADMAP_1.0.json.\n\n'+''.join(f"- P{e['proposition']}: {e['title']} — {e['status']}\n" for e in cover['entries'] if e['status']!='complete'))
(r/'PUBLICATION_STATUS.md').write_text('# Publication status\n\nThis is Lean formalization 0.11.0 of unchanged Foundations 1.0.0. Production PR-LASM 2.3.0 is unchanged. No external publication, independent referee report, full 87-proposition completion, or production-software verification is claimed. Frozen source may retain its historical publication wording; this sidecar records current formalization status.\n')
reg=json.loads((r/'source/PROOF_REGISTER_1.0.0.json').read_text())
card={'release':'0.11.0','review_type':'self-review','primary_verdict':'incomplete, with the smallest missing implication','block':[32,33,34],'claims':[dict(next(e for e in reg['entries'] if e['id']==k),formalization_status=cover['entries'][k-1]['status'],scope=cover['entries'][k-1]['scope']) for k in [32,33,34]],'missing_implication':'Noisy finite table and its leading-r singular subspace imply the claimed projection gap; also missing sorted-singular-value and explicit basis-decoder bridges.','kernel_evidence':'Pending stable source and fresh-archive runs; consult actual reports.'}
(r/'verification/BLOCK11_CLAIM_CARD.json').write_text(json.dumps(card,indent=2)+'\n')
for n in ['compile11.py','prepare11.py','docs11.py','restore_server11.py']:
 shutil.copy2(base/n,r/'verification/development_tools'/n)
(r/'verification/BLOCK11_TOOLING_ATTEMPTS.json').write_text(json.dumps({'runtime_archive_hash_verified':True,'environment_failures':['Prior compiler removed during pruning','Full runtime extraction exhausted disk','Reduced extraction omitted required .olean.server files; restored','Two inherited runs failed missing import files','Exploratory inherited run failed changed-source inventory; not accepted evidence','Attempted interruption failed because process id unavailable in command namespace','One metadata invocation used wrong working directory; rerun passed'],'development_log_note':'One overlapping invocation initially shared index 0003; the filtering record and snapshot were moved to 0004 before the core record was written. The compiler helper now reserves indices based on snapshots too. All outputs preserved.','source_run':'verification/block11_release_run/report.json'},indent=2)+'\n')
print('Current documents and claim card written.')
