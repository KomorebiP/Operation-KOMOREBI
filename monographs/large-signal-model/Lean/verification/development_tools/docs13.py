from pathlib import Path
import json,hashlib
b=Path('/workspace/scratch/2e8d212e9ca7');r=b/'work13/Komorebi_LSM_Lean_0.13.0'
c=json.loads((r/'RELEASE_COUNTS.json').read_text());cov=json.loads((r/'COVERAGE.json').read_text())
logs=[dict(path=str(p.relative_to(r)),**json.loads(p.read_text())) for p in sorted((r/'verification/development_block13').glob('*.json'))]
summary=dict(invocations=len(logs),successful=sum(x['returncode']==0 for x in logs),failed=sum(x['returncode']!=0 for x in logs),records=[{k:x[k] for k in ['path','returncode','seconds']} for x in logs])
(r/'verification/BLOCK13_DEVELOPMENT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
rep=json.loads((r/'verification/block13_release_run/report.json').read_text());passed=rep.get('passed',False) and rep.get('complete',False)
status=f"PASS: {len(rep['stages'])} cumulative verification stages; 84 metadata/tooling checks." if passed else 'Final cumulative verification pending; see the completed delivery report.'
headline='''# Large Signal Model Lean 0.13.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production PR-LASM 2.3.0 unchanged.

This block proves the exact spectral norm of the existing orthogonal pseudoinverse and constructs the bounded right inverse on the actual column space. It removes the inverse and inverse-norm hypotheses from the previous noisy-subspace theorem. It adds 20 named Lean theorems (16 supporting and four examples), four definitions and two rejection controls. P32 remains partial; coverage remains 38/87 complete, one partial and 48 not formalized.
'''
remaining='''## Exact remaining P32 obligations

1. Prove sorted singular-value perturbation and rank separation for the actual finite table, including the maximal-rank tail-zero convention.
2. Construct the actual leading-r left singular subspace of Y and prove its observed tail bound. The current strongest gap theorem still takes the candidate subspace's dimension and observed tail as inputs.
3. Prove the orthonormal-basis matrix minimum-singular-value bound and the explicit decoder U(UhatᵀU)⁻¹.

The right inverse on the true range and its bound from σ_r(X) are now proved. The earlier one-sided-to-full projection argument and basis-free coordinate conditioning are already proved. None of these results certifies unseen process modes or the adequacy of a chosen finite table.
'''
proof=r'''## Main result

Let A:E→F be a linear map between finite-dimensional real inner-product spaces. Let r=dim(range A)>0 and s=σ_r(A), the smallest positive singular value of the actual map. Lean's singular-value sequence is zero-indexed, so s is `A.singularValues (r-1)`.

The release proves

\[
s\|x\|\leq\|Ax\|\quad(x\in(\ker A)^\perp),\qquad
\|A^\dagger\|=s^{-1}.
\]

The existing orthogonal pseudoinverse is used, with its earlier proved Penrose identities. Its restriction R:range A→E is constructed and satisfies ARy=y and ‖R‖=s⁻¹. These are conclusions, not fields or supplied hypotheses.

## Proof route

Choose the actual ordered orthonormal eigenbasis b_i of A* A. The pinned singular-value definition identifies its eigenvalues with σ_i². Adjointness and the eigenvector relation give

\[
\langle Ab_i,Ax\rangle=\sigma_i^2\langle b_i,x\rangle,\qquad
\|Ax\|^2=\sum_i\sigma_i^2\langle b_i,x\rangle^2.
\]

A zero singular mode has Ab_i=0. If x lies in (ker A)⊥, its coefficient at every zero mode is zero. On the other modes, ordering gives σ_i≥s. Parseval therefore gives ‖Ax‖²≥s²‖x‖². Nonnegativity gives the stated lower norm bound. This lower-bound theorem also accommodates rank zero with s=0; positivity is asserted only when r>0.

For y∈F, the existing pseudoinverse satisfies A†y∈(ker A)⊥ and AA†y=P_range(A)y. Applying the lower bound and projection contraction gives s‖A†y‖≤‖y‖. Hence ‖A†‖≤1/s, and the range restriction has the same upper bound.

For sharpness, choose the eigenbasis vector at index r−1. Its norm is one, its image norm is s, and its positive eigenvalue places it in (ker A)⊥. The pseudoinverse maps its image back to that unit vector. The operator norm inequality therefore gives 1≤‖A†‖s, and also 1≤‖R‖s. The upper and lower estimates yield both exact norm identities.

## Noisy-table consequence

Let X,N:E→F, let Q be an actual subspace of F of dimension rank(X)>0, and put s=σ_r(X). Suppose 0≤ε<s/2, ‖N‖≤ε and the observed tail satisfies ‖(I−Q)(X+N)‖≤ε. Then

\[
\|P_{\operatorname{range}X}-Q\|\leq 2\varepsilon/s<1.
\]

`gap_from_observed_tail` constructs R from X, proves XR=id on the true range and supplies the derived norm bound to the block12 residual theorem. It does not assume that Q is a leading singular subspace or prove that its observed tail is small. Those are remaining obligations. The inherited coordinate theorem then applies to this proved projection gap.
'''
modules='''## Source map

| Module | Contents |
|---|---|
| `SpectralLowerBound.lean` | Six theorems and two definitions: ordered Gram basis, spectral norm expansion, zero modes, actual least positive singular value and lower bound on the kernel complement. |
| `SpectralPseudoinverse.lean` | Five theorems and one definition: pointwise/operator inverse bounds, constructed range inverse, right-inverse law and noisy gap with derived inverse premises. |
| `SpectralSharpness.lean` | Five theorems: basis image norm, positive-mode orthogonality, unit minimizer and exact norms for the full and restricted pseudoinverse. |
| `Block13Examples.lean` | Four theorems and one definition: scalar factor two has s=2 and inverse norm 1/2; zero map has s=0; a rank-one projection disproves a global-domain lower bound. |

The counterexample uses the actual first-coordinate projection from Euclidean ℝ² and the second unit vector. The two negative controls deliberately attempt inverse norm ≤1/4 for scalar factor two and strict positivity of the zero map's least singular value. They must fail in isolation.
'''
repro='''## Verification and reproduction

The release has 89 proof modules, 90 compilation targets including the root, 1,378 named declarations and 1,063 named theorems. Of those theorems, 324 occur in example modules and 739 are supporting results. There are 79 isolated rejection controls. These counts are not manuscript-proposition counts.

Use the separately saved portable Lean 4.34.0-rc2 runtime. Lean commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine package pins remain unchanged.

From a fresh project extraction, run the file check before creating build files:

```bash
python3 scripts/verify_hashes.py
python3 scripts/build_inventory.py
python3 scripts/check_metadata.py
LD_PRELOAD=/absolute/kit/compat/app_path.so python3 scripts/verify.py --kit /absolute/kit --out /absolute/run-directory
```

The verifier rebuilds project objects, compiles with warnings as errors, runs inherited exact rational examples, audits all named declarations, replays every project proof module with LeanChecker and checks all rejection controls. Allowed logical axioms are only `propext`, `Classical.choice`, `Quot.sound`. Keep `.olean.server` files in the runtime. The supplied path compatibility preload is required on this host.

The upstream pinned libraries are not exhaustively rebuilt/replayed. This is a self-review and Lean kernel verification, not an independent referee or second proof assistant. The external verification JSON links the exact delivered archive hash to its fresh extraction run.
'''
failures=f'''## Development record

{summary['invocations']} compiler invocations: {summary['successful']} successful and {summary['failed']} failed. Source snapshots and diagnostics are retained in `verification/development_block13/`.

The failures were a missing unfolding/rewrite for the named eigenbasis in the inner-product identity; a continuous-map versus linear-map coercion blocking a norm rewrite; scalar examples needing explicit quotient arithmetic and inverse notation; and an attempted simplification with deprecated or unused arguments, rejected by warnings-as-errors. Direct typed equalities and the appropriate algebraic rewrites resolved them. No statement was weakened, and no proof placeholder was accepted.

Development used previously checked predecessor objects. The accepted cumulative runs rebuild all project objects. Inventoried sources are frozen during accepted runs.
'''
lineage='''## Preservation

All 85 predecessor proof files, 1,354 declaration records and 77 predecessor rejection-control files remain unchanged. The frozen manuscript and proof register are unchanged.

The package contains a compact 0.12.0 source snapshot made from the exact delivered ZIP. It preserves proof, control, declaration and report evidence while omitting redundant nested ZIP payloads; its original archive manifest is clearly renamed. The original delivered 0.12.0 ZIP remains saved separately, with its identity and hash recorded in SOURCE_LINEAGE.json. Existing earlier history is preserved. This prevents recursive archive duplication without representing the compact snapshot as the original ZIP.
'''
(r/'LEAN_GUIDE.md').write_text(headline+'\n'+status+'\n\n'+proof+'\n'+modules+'\n'+remaining+'\n'+repro+'\n'+failures+'\n'+lineage)
(r/'README.md').write_text(headline+'\n'+status+'\n\nRead LEAN_GUIDE.md, AUDIT.md and CONTINUE_HERE.md. The ZIP contains all current Lean sources, frozen theory, proof register, histories and verification tooling.\n')
(r/'CONTINUE_HERE.md').write_text(headline+'\n'+remaining+'\nResume from `source/FOUNDATIONS_1.0.0.md` §33, lines 1388–1426. Use `gap_from_observed_tail` as the strongest current endpoint. Prove the spectral-tail inputs from the actual leading-left subspace before claiming P32 complete. Preserve zero-based indexing and rectangular/maximal-rank cases.\n\n'+repro)
progress=json.loads((r/'history/PREDECESSOR_0.12.0_PROGRESS.json').read_text());progress.update(release='0.13.0',new_complete=[],current_block=[32],next_restart=[32],development_attempts=summary,source_verification=dict(passed=passed,complete=passed,stages=len(rep.get('stages',[])),report='verification/block13_release_run/report.json',metadata_checks=84))
(r/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n')
(r/'PROGRESS.md').write_text(headline+'\n'+status+'\n\n'+modules+'\n'+remaining+'\n'+failures)
(r/'COVERAGE.md').write_text(headline+'\n'+remaining+'\n## Proposition register\n\n'+ '\n'.join(f"- P{e['proposition']}: {e['title']} — {e['status']}" for e in cov['entries'])+'\n')
(r/'ROADMAP_1.0.md').write_text(headline+'\n'+remaining+'\n## All unfinished propositions\n\n'+ '\n'.join(f"- P{e['proposition']}: {e['title']} — {e['status']}" for e in cov['entries'] if e['status']!='complete')+'\n')
(r/'PUBLICATION_STATUS.md').write_text(headline+'\nNo external publication or independent review was performed. Full framework completion is not claimed.\n')
audit=headline+'\n## Primary verdict\n\nFull P32: **incomplete, with the smallest missing implication** being the perturbation and leading-left-subspace tail results for the actual noisy table. The spectral lower bound, sharp pseudoinverse norms, constructed right inverse and the stated conditional noisy gap are proved as written in Lean.\n\n'+status+'\n\n'+proof+'''\n## Obligation matrix

| Obligation | Result |
|---|---|
| Actual sorted singular values of A, not a variational surrogate | Passed |
| Gram eigenbasis and weighted norm identity | Passed |
| Zero modes lie in ker A; retained vectors have zero tail coefficients | Passed |
| Rank−1 index validity and positive least singular value for r>0 | Passed |
| Lower bound restricted to the actual kernel complement | Passed |
| Existing orthogonal pseudoinverse and actual range inverse | Passed |
| Upper norm estimates and explicit unit minimizer for sharpness | Passed |
| Full and restricted inverse norm equality | Passed |
| Noisy gap removes the supplied inverse/norm premises | Passed |
| Scalar and rank-deficient boundary examples | Passed |
| Perturbation/rank separation | Not addressed |
| Actual leading-left subspace and tail characterization | Not addressed |
| Orthonormal-basis decoder and minimum-singular-value formula | Not addressed |
| Independent referee / second proof assistant | Not performed |

Dependency graph: pinned singular-value definition and spectral eigenbasis → weighted norm expansion and zero-mode elimination → lower bound on (ker A)⊥ → existing Penrose identities → inverse upper bounds. Positive final Gram mode → unit minimizer → matching inverse lower bounds. Constructed range inverse + block12 residual/projection theorem → noisy gap under the supplied observed tail and dimension.

No circular full-gap or inverse-bound premise is used in the new endpoint. The source correspondence is to frozen P32 span hash `062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7`. Upstream mathematical leaves are the project-pinned Lean definitions and lemmas inspected locally; no unverified external theorem is invoked.

Proofreading self-review covered the four new modules and current release prose in P32 context. No mathematical-token corrections were made during proofreading. Outstanding spectral and decoder proofs are substantive gaps, not copyediting issues.
'''+remaining+'\n'+failures+'\n'+lineage
(r/'AUDIT.md').write_text(audit)
(r/'verification/P32_NEXT_ROUTE.md').write_text('# P32 after block13\n\nThe spectral inverse bound is now formalized, including exact sharp norms. The strongest endpoint is `Spectral.gap_from_observed_tail`.\n\n'+remaining+'\nNext bounded target: construct the leading-r left subspace for an operator Y and prove its tail norm in terms of the sorted singular value at index r. Then prove perturbation/rank separation to supply the ε tail bound. Use the Gram spectral expansion and preserve rectangular-domain conventions. Neither route is counted as proved by this planning note.\n')
(r/'verification/P32_SPECTRAL_API_NOTES.md').write_text('# Spectral continuation after block13\n\nThe earlier planned lower bound on (ker X)⊥ and pseudoinverse bridge are now proved in SpectralLowerBound.lean, SpectralPseudoinverse.lean and SpectralSharpness.lean.\n\nThe pinned singular-value sequence is zero-indexed: σ_r(X) is index r−1 for r>0, while the tail σ_(r+1) is index r. `rightBasis` is a right Gram basis, not a leading-left-subspace construction. The latter and the Weyl/min-max perturbation argument remain unproved. See P32_NEXT_ROUTE.md.\n')
card=dict(release='0.13.0',review_type='self-review',primary_verdict='incomplete, with the smallest missing implication',manuscript_proposition=32,source_span='source/FOUNDATIONS_1.0.0.md:1388-1426',statement_proof_sha256='062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7',new_claims=['Finite-dimensional real inner-product A:E→F; s=actual singularValues(rank(range A)−1); s norm(x)≤norm(Ax) for x∈ker(A)perp.','If rank A>0 then s>0, norm(pinv A)=1/s, and the constructed inverse on range A has the same exact norm.','If X has positive rank, Q has equal dimension, observed tail≤ε, noise≤ε and 0≤ε<s/2, then full projection gap≤2ε/s<1; inverse premises are derived.'],remaining=cov['entries'][31]['scope'])
(r/'verification/BLOCK13_CLAIM_CARD.json').write_text(json.dumps(card,indent=2)+'\n')
(r/'verification/BLOCK13_PROOFREAD.json').write_text(json.dumps(dict(mode='self-review',scope=['four new Lean modules','current release prose'],routine_edits='Checked typing, zero-based indexing, rank restrictions, projection domains and conditional wording.',mathematical_token_changes='None during proofreading.',unresolved='Three substantive P32 obligations remain explicitly listed.',validation='Warnings-as-errors development compilation; final cumulative reports control release acceptance.'),indent=2)+'\n')
for n in ['compile13.py','prepare13.py','docs13.py']:(r/'verification/development_tools'/n).write_bytes((b/n).read_bytes())
print(status)
