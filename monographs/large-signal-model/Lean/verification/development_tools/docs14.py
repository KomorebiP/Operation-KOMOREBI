from pathlib import Path
import json,hashlib
b=Path('/workspace/scratch/2e8d212e9ca7');r=b/'work14/Komorebi_LSM_Lean_0.14.0'
c=json.loads((r/'RELEASE_COUNTS.json').read_text());cov=json.loads((r/'COVERAGE.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
logs=[dict(path=str(p.relative_to(r)),**json.loads(p.read_text())) for p in sorted((r/'verification/development_block14').glob('*.json'))]
summary=dict(invocations=len(logs),successful=sum(x['returncode']==0 for x in logs),failed=sum(x['returncode']!=0 for x in logs),lean_invocations=sum('strace' not in x['command'] for x in logs),blocked_trace_invocations=sum('strace' in x['command'] for x in logs),failure_categories={'Lean proof or warnings-as-errors diagnostics':9,'output file creation under disk pressure':2,'trace diagnostic blocked by process permissions':1},records=[{k:x[k] for k in ['path','returncode','seconds']} for x in logs])
(r/'verification/BLOCK14_DEVELOPMENT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
report_path=r/'verification/block14_release_run/report.json'
rep=json.loads(report_path.read_text()) if report_path.exists() else {};passed=rep.get('passed',False) and rep.get('complete',False)
status=f"PASS: {len(rep['stages'])} cumulative stages; 84 metadata/tooling checks. Exact delivered-ZIP replay is recorded separately in the external verification JSON." if passed else 'New proof modules compile. Final cumulative and exact-archive verification are pending.'
headline='''# Large Signal Model Lean 0.14.0

Komorebi P. — 2026-10-15. Frozen theory 1.0.0; PR-LASM production software 2.3.0 unchanged.

P32 is complete in its stated finite-table scope. This block constructs the leading singular subspace, proves singular-value perturbation and the exact observed residual, and proves the ordinary matrix inverse decoder and its conditioning. It adds 54 named Lean theorems (47 supporting and seven examples), nine definitions, ten proof modules and two rejection controls. Coverage is now 39/87 complete, zero partial and 48 not formalized.
'''
proof=r'''## Exact result

Let X,N:E→F be linear maps between finite-dimensional real inner-product spaces. Write r=dim(range X)>0, s=σ_r(X), Y=X+N, and assume ‖N‖≤ε<s/2. The nonnegative noise budget follows from ‖N‖≤ε. Let P project onto range X. The release constructs Q from the first r ordered right Gram modes of Y and their images, and proves that Q is the span of r orthonormal left singular modes.

\[
\sigma_r(Y)\ge s-\varepsilon,\qquad
\sigma_{r+1}(Y)\le\varepsilon,\qquad
\|(I-Q)Y\|=\sigma_{r+1}(Y),\qquad
\|P-Q\|\le 2\varepsilon/s<1.
\]

Singular values are the actual pinned Mathlib singular values, indexed from zero and padded with zero. Thus manuscript σ_r is index r−1, and σ_(r+1) is index r. The zero convention at maximum possible rectangular rank is proved explicitly.

For any orthonormal bases U and Uhat of range X and Q, let C=UhatᵀU. The formal matrix entries are inner products of the estimated and true basis vectors, and equality with the literal transpose product is proved in an arbitrary ambient orthonormal basis. Then

\[
\sigma_{\min}(C)\ge\sqrt{1-(2\varepsilon/s)^2}.
\]

The estimated coordinate map is injective on range X. The explicit decoder uses the ordinary matrix inverse,

\[
D=U(Uhat^\top U)^{-1},\qquad
D(Uhat^\top x)=x\quad(x\in\operatorname{range}X),\qquad
Uhat^\top Dy=y,
\]

and

\[
\|D\|\le [\sqrt{1-(2\varepsilon/s)^2}]^{-1}.
\]

This remains a finite-table statement. It does not establish that the selected history/test table captures every process mode or supply missing intervention coverage.
'''
route=r'''## Proof mechanism

The previous release supplied the actual right Gram eigenbasis, the weighted squared-norm identity and the exact pseudoinverse norm 1/s. This release uses the span of the first k basis vectors and its orthogonal complement. Their coordinate supports give lower and upper norm estimates from the ordered singular values.

Mapping the retained span through A gives the left subspace. The discarded image is orthogonal to that subspace, so its residual projection equals A applied to the discarded right projection. The upper estimate gives the tail bound; the next basis vector attains it. If k is the full domain dimension, zero padding gives the zero tail. Positive modes give injectivity of A on the retained span and hence its dimension. Normalized image modes are orthonormal eigenvectors of AA*, proving the correspondence with leading left singular vectors.

For perturbation at index k below the domain dimension, intersect the first k+1 right modes of A with the complement of the first k right modes of B. Their dimensions sum to one more than the domain dimension, so the intersection contains a nonzero vector. On it, the spectral lower bound for A, upper bound for B and triangle inequality yield σ_k(A)≤σ_k(B)+‖A−B‖. Swapping A and B gives the absolute perturbation inequality. Above the domain dimension both spectra are zero. This proves the required spectral inequalities without invoking an unverified min-max or Weyl theorem.

The noise bounds force Y to have at least r positive singular values, so the constructed Q has dimension r. Its proved tail bound feeds the block13 inverse construction and block12 projection argument. No desired tail, inverse bound, dimension equality or projection gap is assumed by the final noisy endpoint.

The cross matrix acts as projection P→Q expressed through the two orthonormal coordinate isometries. The earlier coordinate lower bound therefore controls its smallest singular value, evaluated on its actual final Gram basis vector. The constructed coordinate equivalence has an inverse matrix; the matrix multiplication identities identify that matrix with the ordinary nonsingular inverse C⁻¹. This proves the explicit decoder formula, both inverse laws and its norm bound.
'''
modules='''## Source map

| Module | Contribution |
|---|---|
| SpectralSubspaces | Retained right spans, dimensions, coordinate support and two spectral bounds. |
| SpectralTail | Constructed left subspace, dimension, residual identity and exact tail norm. |
| SingularPerturbation | Dimension intersection; all-index absolute singular-value perturbation; noisy lower and upper bounds. |
| LeftSingularModes | Normalized left modes, orthonormality, left Gram eigenvector relation and span equality. |
| NoisySpectralSubspace | Data-selected subspace, derived rank/dimension/tail and full spectral/projection endpoint; rectangular maximum-rank convention. |
| BasisCoordinates | Cross matrix, coordinate maps, actual minimum-singular-value bound and injectivity. |
| BasisDecoder | Ordinary inverse matrix, explicit decoder, both inverse laws, true-range membership and norm bound. |
| DecoderMatrixFormula | Ambient basis columns, literal transpose product and matrix decoder formula. |
| FiniteTableP32 | Unified basis-conditioning and decoder endpoint with only P32's noise hypotheses. |
| Block14Examples | Seven exact checks, including sharp perturbation, retained/discarded scalar modes and the rectangular zero-tail boundary. |
'''
repro=f'''## Reproduction and verification scope

There are {c['proof_modules']} proof modules, 100 compilation targets including the root, {c['named_declarations']:,} named declarations and {c['named_theorems']:,} named theorems ({c['supporting_theorems']} supporting, {c['example_theorems']} in example modules). There are {c['negative_controls']} isolated rejection controls. These are separate from the 87 manuscript propositions.

Use the separately saved portable Lean 4.34.0-rc2 runtime: Lean commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine dependency pins are unchanged. From a fresh extraction, check hashes before creating build files:

```bash
python3 scripts/verify_hashes.py
python3 scripts/build_inventory.py
python3 scripts/check_metadata.py
LD_PRELOAD=/absolute/kit/compat/app_path.so python3 scripts/verify.py --kit /absolute/kit --out /absolute/run-directory
```

The verifier removes project caches, compiles with warnings as errors, runs the inherited exact rational examples, audits every named declaration, replays all 99 proof modules with LeanChecker and checks all 81 isolated rejections. Expected total: 282 stages (100 compilation, one exact-example execution, one axiom audit, 99 module replays, 81 rejection controls). Permitted logical axioms are only `propext`, `Classical.choice`, `Quot.sound`. Inventoried sources must remain identical during each accepted run and between the source and archive runs.

Keep the runtime's `.olean.server` files and use its supplied path compatibility preload on this host. The runtime was reused without alteration. Imported upstream libraries are not exhaustively rebuilt or replayed. The proof audit and manuscript correspondence are self-review, not an independent referee or second proof assistant. The external verification JSON binds the exact ZIP hash to its fresh extraction run.
'''
failures=f'''## Preserved development record

There were {summary['invocations']} recorded tool invocations: {summary['successful']} succeeded and {summary['failed']} failed. Of these, 21 invoked Lean and one diagnostic tracing attempt was blocked before Lean ran. Every attempted source snapshot and its output is retained in `verification/development_block14/`.

Nine failures were ordinary Lean proof or warnings-as-errors diagnostics: an incorrect namespace and a deprecated Fin accessor; coercion/type inference around a finite span's dimension; unfolding a Gram eigenbasis and normalizing inverse arithmetic; function versus finitely supported function coercions; unused finite-dimensional section assumptions; subtype equality and continuous/linear-map coercions; and explicit scalar operator-norm simplification. Typed intermediate facts, the pinned API and explicit coercions resolved them. The stated mathematical target was not weakened.

Two tail-module runs reached output-file creation and failed while disk space was critically low. Already-saved duplicate extraction/build trees were removed, and the unchanged tail source then compiled. A `strace` diagnostic was rejected by process tracing permissions; no bypass was attempted. These are environment failures, not rejected mathematical claims. The logs are preserved and the cumulative verifier rebuilds all project objects from scratch.

The first metadata pass also failed because an inherited roadmap check still required 49 unfinished propositions. The check was updated to 48 after P32 completion, while retaining exact set equality and disjoint coverage of all 87 propositions. This diagnostic is recorded separately in BLOCK14_METADATA_DEVELOPMENT.json.
'''
lineage='''## Preservation

All 89 predecessor proof files, 1,378 declaration records and 79 rejection-control files remain unchanged. The frozen Foundations 1.0.0 manuscript and proof register retain their hashes. Prior progress records remain historical evidence: their then-partial P32 status is not retroactively changed.

The compact 0.13.0 source snapshot was made from the exact delivered ZIP (`7a8f9e5e94c88afb5ada3f73496b09c00e3479d9b165906a7cfe7a3bf914f8c5`). It preserves all non-archive files and records omitted nested ZIP payloads. Its original manifest is renamed; the source snapshot is not represented as the original delivered archive. The original archive remains saved separately. All historical non-archive records are retained. To avoid disk exhaustion and repeated nested payloads, older ZIP files are represented by exact hashes and member paths in HISTORY_ARCHIVE_REFERENCES.json; their bytes are preserved inside the separately saved exact 0.13.0 archive. The immediate 0.13.0 source snapshot stays embedded. This changes packaging, not current proof content or predecessor diagnostics.
'''
nextstep='''## Continuation

No P32 implication remains open in the stated finite-table theorem. The broader program has 48 unformalized propositions; see ROADMAP_1.0.json for the exhaustive disjoint list.

Next bounded target: P31, missing-intervention nonidentifiability, in frozen Foundations §32. The exact manuscript construction uses one hidden state and two observations. Both models give (1/2,1/2) under action a; they give (1,0) and (0,1) under b. Formalize actual stochastic models, prove every a-only word has common probability 2^(-length), and exhibit the one-step b disagreement. Existing instrument and word-probability APIs should supply the construction. P31 is not counted as proved by this handoff.

P35's reset-experiment probability certificate and P37's conditional observation-based completion remain further parts of the learning chain. P32 does not silently supply their statistical or coverage assumptions.
'''
(r/'LEAN_GUIDE.md').write_text(headline+'\n'+status+'\n\n'+proof+'\n'+route+'\n'+modules+'\n'+repro+'\n'+failures+'\n'+lineage+'\n'+nextstep)
(r/'README.md').write_text(headline+'\n'+status+'\n\nRead LEAN_GUIDE.md, AUDIT.md and CONTINUE_HERE.md. The ZIP contains all current sources, frozen theory, proof register, preserved histories and verification tooling.\n')
(r/'CONTINUE_HERE.md').write_text('# Continue from Lean 0.14.0\n\nP32 is complete in its finite-table scope. Coverage: 39 complete, zero partial, 48 unformalized. Current proof endpoints are `Spectral.finite_table_stability`, `FiniteTableP32.coordinates_and_decoder` and `BasisCoordinates.decoder_matrix_formula`.\n\n'+status+'\n\nSee `verification/P32_CLOSEOUT.md` for the phase synthesis and `AUDIT.md` for hypotheses and self-review limits. The frozen manuscript is unchanged.\n\n'+nextstep)
progress=json.loads((r/'history/PREDECESSOR_0.13.0_PROGRESS.json').read_text());progress.update(release='0.14.0',completed=cov['complete'],partial=[],outstanding=[e['proposition'] for e in cov['entries'] if e['status']!='complete'],new_complete=[32],current_block=[32],next_restart=[31],development_attempts=summary,source_verification=dict(passed=passed,complete=passed,stages=len(rep.get('stages',[])),report='verification/block14_release_run/report.json',metadata_checks=84));progress['unexecuted']=[s for s in progress['unexecuted'] if not s.startswith('P32')]
(r/'PROGRESS.json').write_text(json.dumps(progress,indent=2)+'\n')
(r/'PROGRESS.md').write_text(headline+'\n'+status+'\n\n'+modules+'\n'+nextstep+'\n'+failures)
(r/'COVERAGE.md').write_text(headline+'\n'+nextstep+'\n## Proposition register\n\n'+'\n'.join(f"- P{e['proposition']}: {e['title']} — {e['status']}" for e in cov['entries'])+'\n')
(r/'ROADMAP_1.0.md').write_text(headline+'\n'+nextstep+'\n## Unformalized propositions\n\n'+'\n'.join(f"- P{e['proposition']}: {e['title']}" for e in cov['entries'] if e['status']!='complete')+'\n')
(r/'PUBLICATION_STATUS.md').write_text(headline+'\nNo external publication or independent review was performed. Full framework completion is not claimed.\n')
obligations='''## Self-review obligation matrix

| Obligation | Result and evidence |
|---|---|
| Actual sorted singular-value definition and zero-based indexing | Passed; inherited spectral expansion and new perturbation theorem. |
| Retained span, its dimension, and coordinate support | Passed; SpectralSubspaces. |
| Actual left singular subspace rather than an assumed candidate | Passed; SpectralTail and LeftSingularModes. |
| Exact residual norm, including k=0 and k=domain dimension | Passed; leadingLeft_tail_norm, scalar boundary examples. |
| All-index perturbation, rectangular maps and padded zeros | Passed; singularValue_abs_sub_le, singularValue_zero_at_max_rank. |
| Positive true rank and data-derived dimension equality | Passed; noisy_rank_lower and learnedLeft_finrank. |
| Projection gap from only the stated noise/rank premises | Passed; finite_table_stability. |
| Cross matrix equals UhatᵀU with correct operation order | Passed; cross_entry and cross_eq_transpose_mul. |
| Actual minimum singular value and coordinate injection | Passed; cross_min_singular and coordinates_injective. |
| Ordinary matrix inverse, both decoder inverse laws, true-range image | Passed; BasisDecoder. |
| Literal matrix decoder and claimed operator norm | Passed; decoder_matrix_formula and decoder_norm_bound. |
| Frozen P32 statement/proof correspondence | Passed by self-review; the complete finite-table conclusion is covered. |
| Source and archive cumulative replay | See verification status and exact-archive JSON. |
| Exhaustive upstream rebuild or independent referee | Not performed. |
| Full-process coverage and statistical confidence | Out of scope for P32; not inferred. |
'''
audit=headline+'\n## Primary verdict\n\n**Proved as written**, for P32 in frozen Foundations 1.0.0 §33, lines 1388–1426, statement/proof span SHA256 `062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7`. This is a self-review verdict on formal-statement correspondence. The formal modules compile; cumulative release acceptance is stated below.\n\n'+status+'\n\n'+proof+'\n'+route+'\n'+obligations+'''\n## Dependency and source checks

Pinned Gram spectral theorem and ordered singular-value definition → weighted norm expansion → retained/tail coordinate estimates. Those estimates plus dimension intersection → all-index perturbation. Positive image modes → actual leading-left span and dimension; orthogonality and the next Gram vector → exact residual norm. Noise inequalities → data-derived rank and tail. Inherited exact pseudoinverse norm and one-sided-to-full projection argument → full gap. Coordinate isometries and that gap → cross-matrix lower bound; actual final Gram vector → minimum singular value. Coordinate equivalence plus matrix composition identities → ordinary inverse decoder and norm bound.

No dependency points back to a conclusion as an input. The strongest noisy endpoints take X, N, positive rank and the original noise inequalities; no spectral perturbation, observed tail, gap, inverse bound or matrix nonsingularity is supplied. Auxiliary conditional lemmas retain their own explicit hypotheses.

External mathematical leaves are the exact local pinned Mathlib sources: SingularValues.lean, Spectrum.lean, PiL2.lean, Orthogonal.lean, Projection/Basic.lean, Projection/FiniteDimensional.lean, LinearAlgebra/Dimension/{Constructions,Finrank,StrongRankCondition}.lean, FiniteDimensional/Lemmas.lean, Matrix/{ToLin,NonsingularInverse}.lean and Analysis/Normed/Lp/Matrix.lean. The new perturbation argument is proved internally, so no named external perturbation theorem is imported on trust. Upstream compiled dependencies remain part of the stated verification boundary.

The seven examples use exact Lean identities, not numerical estimates. Two new controls request residual ≤1 for the scalar-two map with no modes retained, and singular-value change ≤1 for scalar two versus zero. Both are mathematically false and must be rejected. They test the new bounds' sharpness without treating finite examples as universal proof.

No mathematical proof obstruction remains for P32. The failed development steps were implementation diagnostics or environment failures, recorded below. Alternative min-max-library and best-low-rank-approximation routes were not needed once the dimension-intersection construction succeeded; they are not reported as failed or exhausted research routes.
'''+failures+'\n'+lineage+'\n'+nextstep
(r/'AUDIT.md').write_text(audit)
newmods=['SpectralSubspaces','SpectralTail','SingularPerturbation','LeftSingularModes','NoisySpectralSubspace','BasisCoordinates','BasisDecoder','DecoderMatrixFormula','FiniteTableP32','Block14Examples']
proofhashes={f'KomorebiLSM/{n}.lean':sha(r/f'KomorebiLSM/{n}.lean') for n in newmods}
card=dict(release='0.14.0',checkpoint='P32-block14-complete',base_archive_sha256='7a8f9e5e94c88afb5ada3f73496b09c00e3479d9b165906a7cfe7a3bf914f8c5',review_type='self-review',primary_verdict='proved as written',manuscript_proposition=32,source_span='source/FOUNDATIONS_1.0.0.md:1388-1426',statement_proof_sha256='062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7',formal_scope=cov['entries'][31]['scope'],proof_files=proofhashes,remaining_p32_obligations=[],remaining_framework_propositions=progress['outstanding'],verification=status)
(r/'verification/BLOCK14_CLAIM_CARD.json').write_text(json.dumps(card,indent=2)+'\n')
(r/'verification/BLOCK14_PROOFREAD.json').write_text(json.dumps(dict(mode='self-review',scope=['ten new Lean modules','current release prose and equation displays'],routine_edits='Reviewed grammar, types, zero-based versus one-based indices, r>0, rectangular dimensions, transpose order, inverse formula and inverse norm.',mathematical_token_changes='None during proofreading.',unresolved='No proofreading issue remains. The broad framework still has 48 unformalized propositions.',validation=status),indent=2)+'\n')
closeout='''# P32 phase closeout — block14

Checkpoint and contemporaneous assessment: `P32-block14-complete`, 2026-10-15. Base: exact delivered Lean 0.13.0 archive SHA256 `7a8f9e5e94c88afb5ada3f73496b09c00e3479d9b165906a7cfe7a3bf914f8c5`. Current proof-file hashes are in BLOCK14_CLAIM_CARD.json; accepted source inventory is in block14_release_run/report.json. This project is an archive-based handoff, not a Git checkout.

The target was P32 as printed in frozen Foundations 1.0.0 §33. It is reached in its finite-table scope. The inverse-norm, leading-subspace, perturbation, coordinate-conditioning and explicit decoder dependencies are all proved. Earlier releases' partial status remains correct for their historical cutoffs.

Decisive records: block11 constructed coordinates under a supplied gap; block12 supplied the one-sided-to-full projection argument; block13 derived and sharpened the actual spectral pseudoinverse norm; block14 constructed the leading-left subspace, proved exact tail and perturbation bounds, and closed the basis matrix decoder. The preserved predecessor summaries and all source files retain that history.

Current formal endpoints:

- `Spectral.finite_table_stability` in NoisySpectralSubspace.lean: actual noisy spectrum and projection gap.
- `FiniteTableP32.coordinates_and_decoder` in FiniteTableP32.lean: actual cross-matrix minimum singular value, injection, both inverse laws and norm.
- `BasisCoordinates.decoder_matrix_formula` in DecoderMatrixFormula.lean: literal U(UhatᵀU)⁻¹ formula in ambient orthonormal coordinates.
- `Spectral.leadingLeft_eq_span_leftModes` and `leftModes_orthonormal`: proof that the constructed space is the claimed leading-left singular subspace.

The structural spectral route succeeded. Implementation failures and two output-write failures were repaired and retained in development_block14; no contrary mathematical result remains unresolved. The attempted trace diagnostic was blocked and abandoned. No fresh-agent independence is claimed.

P32 has no remaining named implication. Further unformalized work is outside this phase. The live continuation is CONTINUE_HERE.md; its next target is P31's exact one-state controlled stochastic counterexample. The broader 48-item list remains in ROADMAP_1.0.json.

'''+status+'\n\nSee AUDIT.md, BLOCK14_DEVELOPMENT_SUMMARY.json, BLOCK14_PROOFREAD.json and the external exact-archive verification JSON for review and execution limits.\n'
(r/'verification/P32_CLOSEOUT.md').write_text(closeout)
(r/'verification/P32_NEXT_ROUTE.md').write_text('# P32 status after block14\n\nCompleted. See P32_CLOSEOUT.md and the current CONTINUE_HERE.md. The former perturbation, leading-left-tail and matrix-decoder obligations are now formal theorems. Earlier route notes are preserved in the exact predecessor source snapshot.\n')
(r/'verification/P32_SPECTRAL_API_NOTES.md').write_text('# Spectral API after block14\n\nActual zero-indexed spectral perturbation is `singularValue_abs_sub_le`. The constructed leading-left subspace is `leadingLeft`; its tail norm is `leadingLeft_tail_norm`. Positive-mode correspondence is `leadingLeft_eq_span_leftModes`. The final noisy endpoint is `finite_table_stability`. The matrix decoder and its norm are in BasisDecoder and DecoderMatrixFormula. P32 is no longer partial.\n')
for n in ['compile14.py','trace14.py','prepare14.py','docs14.py']:
 (r/'verification/development_tools'/n).write_bytes((b/n).read_bytes())
print(status)
