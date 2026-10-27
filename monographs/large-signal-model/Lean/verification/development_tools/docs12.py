from pathlib import Path
import json,hashlib
b=Path('/workspace/scratch/2e8d212e9ca7');r=b/'work12/Komorebi_LSM_Lean_0.12.0'
c=json.loads((r/'RELEASE_COUNTS.json').read_text());cov=json.loads((r/'COVERAGE.json').read_text())
logs=[dict(path=str(p.relative_to(r)),**json.loads(p.read_text())) for p in sorted((r/'verification/development_block12').glob('*.json'))]
summary=dict(invocations=len(logs),successful=sum(x['returncode']==0 for x in logs),failed=sum(x['returncode']!=0 for x in logs),records=[{k:x[k] for k in ['path','returncode','seconds']} for x in logs])
(r/'verification/BLOCK12_DEVELOPMENT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
report=r/'verification/block12_release_run/report.json';rep=json.loads(report.read_text()) if report.exists() else {}
passed=rep.get('passed',False) and rep.get('complete',False)
status=f"PASS: {len(rep['stages'])} cumulative verification stages; 82 metadata/tooling checks." if passed else 'Cumulative verification pending; see the completed delivery report before accepting this release.'
headline='''# Large Signal Model Lean 0.12.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production software PR-LASM 2.3.0 unchanged.

This block proves the strict one-sided-to-full projection bound needed by P32 and connects it to a noisy operator through explicit tail and inverse estimates. It adds 15 named theorems (11 supporting results and four examples), one definition and one proof-rejection control. No new manuscript proposition is marked complete: 38/87 complete, P32 partial, 48 not formalized.
'''
remaining='''## Exact remaining P32 work

1. Prove sorted singular-value perturbation/rank separation for the actual finite table, including the maximal-rank zero convention.
2. Construct the actual leading-r left singular subspace of Y and prove its tail residual bound; equal dimension and the tail are currently supplied hypotheses.
3. Construct the right inverse on the true range with norm at most 1/σ_r(X). The existing pseudoinverse is available, but this exact spectral bridge is still missing.
4. Express the coordinate map in orthonormal bases, prove the minimum-singular-value bound, and derive the explicit decoder U(UhatᵀU)⁻¹.

The full P32 theorem remains incomplete. Nothing here certifies unseen process modes, the adequacy of a finite table, floating-point SVD, learned probability validity, or a known true decoder.
'''
proof=r'''## New theorem and proof

Let P and Q be subspaces of a finite-dimensional real inner-product space, with equal finite dimension. Suppose 0≤δ<1 and

\[\|x-Qx\|\leq\delta\|x\|\quad\text{for every }x\in P.\]

Then \(\|P-Q\|\leq\delta\). Here P and Q in operator expressions denote actual orthogonal projections; the Lean statements use `Submodule.starProjection`.

Put c=√(1−δ²)>0. Pythagoras gives ‖Qx‖≥c‖x‖ on P, so Q restricted to P is injective. Equal finite dimensions make it surjective onto Q, with inverse norm at most 1/c. For y∈Q take x∈P with Qx=y. Self-adjointness gives ⟨Py,x⟩=⟨y,x⟩=‖y‖². Combining Cauchy–Schwarz and c‖x‖≤‖y‖ yields ‖Py‖≥c‖y‖, treating y=0 separately. Pythagoras yields ‖y−Py‖≤δ‖y‖.

Thus ‖(I−P)Q‖≤δ. Adjoint norm preservation gives ‖Q(I−P)‖≤δ. Write v=Pv+(I−P)v and

\[(P-Q)v=(I-Q)Pv-Q(I-P)v.\]

The two right-hand terms are orthogonal. Their squared norms sum to at most δ²(‖Pv‖²+‖(I−P)v‖²)=δ²‖v‖². This proves the operator norm estimate. The Lean proof uses no principal-angle decomposition and proves the bound in the strict regime; it does not claim the unrestricted global projection-norm identity.

For operators X,N:F→E, let Y=X+N and let R:P→F satisfy X(Rx)=x. If ‖(I−Q)Y‖≤η, ‖N‖≤ε and ‖R‖≤κ, with nonnegative budgets, then

\[\|(I-Q)x\|\leq(\eta+\varepsilon)\kappa\|x\|.\]

The proof transfers the observed residual to X by the triangle inequality, then applies R. If (η+ε)κ<1 and P,Q have equal dimension, the previous theorem proves the full gap. Substituting η=ε, κ=1/s and ε<s/2 gives \(\|P-Q\|\leq2\varepsilon/s<1\). The tail estimate and inverse estimate are explicit premises, not derived singular-value conclusions.
'''
modules='''## Source map

| Module | Contents |
|---|---|
| `OneSidedSubspace.lean` | Seven theorems: coordinate lower bound, injection, inverse bound, reverse lower bound and residual, reverse operator bound, full projection gap; one constructed equivalence. |
| `NoisySubspaceResidual.lean` | Four theorems: true residual, residual on the range, conditional noisy projection gap, conditional 2ε/s gap. |
| `Block12Examples.lean` | Zero residual at equal rank forces equal projections; unequal-rank zero one-sided residual; its full gap equals one; a half-gap specialization. |

The unequal-rank example uses P={0}, Q=ℝ. Every x∈P has zero residual, yet ‖P−Q‖=1. The new negative control attempts the false bound ≤0 and must be rejected. This is a boundary check, not an additional positive theorem.
'''
repro='''## Reproduce

Use the existing portable Lean 4.34.0-rc2 runtime. Lean commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; all nine package pins are in `lake-manifest.json`. The runtime is supplied separately in the previously saved seven-part kit.

From a fresh project extraction, before generating files:

```bash
python3 scripts/verify_hashes.py
python3 scripts/build_inventory.py
python3 scripts/check_metadata.py
LD_PRELOAD=/absolute/kit/compat/app_path.so python3 scripts/verify.py --kit /absolute/kit --out /absolute/run-directory
```

The supplied compatibility preload is needed on this host. Keep `.olean.server` files when restoring the runtime. Verification deletes and rebuilds local project objects, checks compiler/dependency pins, compiles every module with warnings as errors, runs the rational examples, audits all named declarations, replays every project module through LeanChecker, and checks the rejection controls. Allowed logical axioms are only `propext`, `Classical.choice`, `Quot.sound`.

The pinned upstream environment is not exhaustively rebuilt or replayed. This is a self-review and kernel check, not an independent referee or a second proof assistant.
'''
failures=f'''## Development and failures

{summary['invocations']} compiler invocations: {summary['successful']} successful, {summary['failed']} failed. Every invocation has a source snapshot and diagnostic JSON in `verification/development_block12/`.

Failures were: the initial dependency lookup did not fall through a new namespace build directory; copying the already verified predecessor objects repaired development imports. An overly broad simplification failed to prove complement-projection idempotence; a direct membership theorem fixed it. Simplifying a vector residual identity left an additive goal; explicit linearity plus additive normalization fixed it. The first boundary-example compile needed the explicit top-projection identity. No failure was hidden by a placeholder or weaker final theorem.

Development compilation used predecessor objects; accepted cumulative verification rebuilds the project from scratch. The first coordinate module was extended while its earlier development invocation was awaiting collection; that exploratory invocation is not final-source evidence. Final cumulative source verification holds the inventoried files fixed.
'''
(r/'LEAN_GUIDE.md').write_text(headline+'\n'+status+'\n\n'+proof+'\n'+modules+'\n'+remaining+'\n'+repro+'\n'+failures)
(r/'README.md').write_text(headline+'\n'+status+'\n\nRead LEAN_GUIDE.md, AUDIT.md and CONTINUE_HERE.md. The delivered ZIP includes all current sources, frozen manuscript/register, predecessor release, verification scripts and failure history. The external exact-archive report records the fresh ZIP verification.\n')
(r/'CONTINUE_HERE.md').write_text(headline+'\n'+remaining+'\nStart from `source/FOUNDATIONS_1.0.0.md` §33, lines 1388–1426, and the P32 record in COVERAGE.json. The earlier written one-sided route is now formalized in OneSidedSubspace.lean. Preserve all predecessor proofs and completed coverage. Do not replace remaining spectral obligations by assumed fields and mark P32 complete.\n\n'+repro)
(r/'verification/P32_NEXT_ROUTE.md').write_text('# P32 continuation after block12\n\nThe block11 one-sided route is now verified in OneSidedSubspace.lean. NoisySubspaceResidual.lean additionally derives the 2ε/s gap from explicit tail and inverse bounds.\n\n'+remaining+'\nSuggested next bounded task: build the finite-dimensional variational/min-max singular-value API using the pinned Mathlib spectral construction. Connect its sorted singular values to the already constructed orthogonal pseudoinverse before claiming a spectral inverse bound. The exact formal statements must retain zero-dimensional/maximal-rank cases.\n')
progress=json.loads((r/'history/PREDECESSOR_0.11.0_PROGRESS.json').read_text());progress.update(release='0.12.0',new_complete=[],current_block=[32],next_restart=[32],development_attempts=summary,source_verification=dict(passed=passed,complete=passed,stages=len(rep.get('stages',[])),report='verification/block12_release_run/report.json',metadata_checks=82))
(r/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n')
(r/'PROGRESS.md').write_text(headline+'\n'+status+'\n\n'+modules+'\n'+remaining+'\n'+failures)
(r/'COVERAGE.md').write_text(headline+'\n'+remaining+'\n## Proposition register\n\n'+ '\n'.join(f"- P{e['proposition']}: {e['title']} — {e['status']}" for e in cov['entries'])+'\n')
(r/'ROADMAP_1.0.md').write_text(headline+'\n'+remaining+'\n## All unfinished propositions\n\n'+ '\n'.join(f"- P{e['proposition']}: {e['title']} — {e['status']}" for e in cov['entries'] if e['status']!='complete')+'\n')
(r/'PUBLICATION_STATUS.md').write_text(headline+'\nNo external publication or independent review was performed. This is a partial formalization, not completion of the 87-proposition framework.\n')
audit=headline+'\n## Verdict\n\nThe new strict one-sided projection theorem is proved as written in Lean. The noisy 2ε/s corollary is proved under its explicit tail, right-inverse and inverse-norm premises. Full P32: **incomplete, with the smallest missing implication** being derivation of those spectral premises from the actual noisy finite table.\n\n'+status+'\n\n'+proof+'''\n## Obligation matrix

| Obligation | Result |
|---|---|
| Actual orthogonal projections and pointwise one-sided hypothesis | Passed |
| Positive c and zero-vector case | Passed |
| Equal dimension used to establish surjectivity | Passed |
| Reverse residual and adjoint norm transfer | Passed |
| Orthogonal decomposition and squared-norm estimate | Passed |
| Noise and tail transfer using actual X,N,R | Passed |
| η=ε, κ=1/s substitution with s>0, ε<s/2 | Passed |
| Equal-dimension necessity counterexample | Passed |
| Sorted singular-value perturbation and leading subspace tail | Not addressed |
| Singular-value bound for constructed right inverse | Not addressed |
| Orthonormal-basis decoder and minimum singular value | Not addressed |
| Independent referee or different prover | Not performed |

Dependency graph: pinned projection/Pythagoras and linear algebra APIs → one-sided coordinate lower bound → constructed equivalence → reverse residual → adjoint operator bound → full gap. Separately: observed tail + perturbation + right inverse → one-sided residual → full gap. No full-gap assumption is used in the new proof. Inherited coordinate results remain unchanged.

No external mathematical citation is required for the new route: its dependencies are imported pinned definitions and kernel-checked lemmas. The frozen P32 source span hash is `062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7`.

All 82 predecessor proof files, 1,338 declaration records and 76 rejection-control files are unchanged. Metadata tests enforce this against the preserved predecessor ZIP. The source run and fresh ZIP run are separate; consult the external verification JSON for exact archive digest and final counts.

Proofreading self-review covered only the three new Lean modules and current release prose, with P32 context. No mathematical-token corrections were made during proofreading. Remaining mathematical gaps are listed explicitly, not treated as typographical issues.
'''+remaining+'\n'+failures
(r/'AUDIT.md').write_text(audit)
(r/'verification/BLOCK12_CLAIM_CARD.json').write_text(json.dumps(dict(release='0.12.0',review_type='self-review',primary_verdict='incomplete, with the smallest missing implication',manuscript_proposition=32,source_span='source/FOUNDATIONS_1.0.0.md:1388-1426',statement_proof_sha256='062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7',new_theorem='Finite-dimensional real inner-product P,Q; equal finrank; 0≤δ<1; ∀x∈P, norm(x-Qx)≤δ norm(x); conclusion norm(P-Q)≤δ.',noisy_corollary='Actual operators X,N,R, X R x=x; nonnegative budgets and tail/noise/inverse bounds; (η+ε)κ<1 and equal dimensions imply full gap≤(η+ε)κ.',remaining=cov['entries'][31]['scope']),indent=2)+'\n')
for n in ['compile12.py','prepare12.py','docs12.py']:
 (r/'verification/development_tools'/n).write_bytes((b/n).read_bytes())
print(status,summary['invocations'],summary['successful'],summary['failed'])
