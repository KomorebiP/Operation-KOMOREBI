from pathlib import Path
import json, hashlib, shutil
base=Path(__file__).resolve().parent.parent;root=base/'work/Komorebi_LSM_Lean_Block10';old=base/'deliverables/Komorebi_LSM_Lean_0.9.0'
counts=json.loads((root/'RELEASE_COUNTS.json').read_text());cover=json.loads((root/'COVERAGE.json').read_text());road=json.loads((root/'ROADMAP_1.0.json').read_text())
readme='''# Komorebi Large Signal Model — Lean 0.10.0

Author: Komorebi P. · Frozen mathematical source: Foundations 1.0.0.

Block 10 completes P45, rational finite-certificate search. Cumulative coverage is **36 complete, 0 partial and 51 unformalized**, out of the unchanged 87-proposition target. This is not completion of the whole framework.

The four new modules add 30 named theorems, including eight example theorems. The cumulative source has 78 proof modules, 1,304 explicitly named declarations and 998 named theorems. Seventy-two negative controls include four new certificate-boundary controls.

## Read and continue

- `LEAN_GUIDE.md`: the P45 proof and executable interface, with inherited guides in `history/`.
- `AUDIT.md`: statement mapping, assumptions, dependency obligations and failed attempts.
- `PROGRESS.md` and `PROGRESS.json`: cumulative progress and restart.
- `COVERAGE.json`: exact frozen-statement mapping to Lean declarations.
- `CONTINUE_HERE.md`: next target, P32–P34.
- `verification/block10_release_run/report.json`: source-candidate verification.
- External delivery verification JSON: independent archive extraction and cumulative replay result for the exact delivered ZIP.

## Reproduce

Use the pinned Lean 4.34.0-rc2 portable kit and its unchanged nine dependency pins. Before generating any caches, run `python3 scripts/verify_hashes.py`. Then run `python3 scripts/build_inventory.py`, `python3 scripts/check_metadata.py`, and `python3 scripts/verify.py --kit PATH_TO_KIT --out OUTSIDE_SOURCE_DIRECTORY`. This host uses the kit's supplied `compat/app_path.so` executable-location adapter through `LD_PRELOAD`; no kernel check is bypassed. The runtime itself is reused read-only, not freshly reconstructed for this block.

The verifier rebuilds all 79 project targets, runs the executable rational examples, audits every explicitly named declaration, replays all 78 modules through LeanChecker, and checks 72 isolated expected proof rejections. Allowed foundational axioms remain `propext`, `Classical.choice` and `Quot.sound`. Runtime examples are regression checks, not additional mathematical proofs.

The original theory, its proof register, predecessor proof sources and production PR-LASM 2.3.0 are unchanged. `PUBLICATION_STATUS.md` explains inherited publication metadata. No training, sensor experiment, statistical coverage test, external publication, independent referee or second-prover claim is made.
'''
(root/'README.md').write_text(readme)
guide=r'''# Large Signal Model Lean 0.10.0 — P45 proof guide

**Scope:** P45, Rational finite-certificate search, Foundations 1.0.0 §49 (the frozen heading and proposition are authoritative). This guide explains Block 10; the full 0.9.0 guide and archive remain under `history/`.

## The exact promise

Input consists of finite rational matrices $B_s$, a rational mass row $\lambda$, and a rational initial vector $z_0$, under exact per-action mass identities. If P39 has a rational normalized full-row-rank generator matrix $V$, the search eventually returns a valid certificate. The nonnegative branch lifts $A_s$ and initial coefficients $\alpha_0$ in that assumed certificate can be real. They are not silently assumed rational.

The conclusion is conditional termination and soundness. It does not assert that every valid process has a rational polyhedral certificate, that bounded search decides nonexistence, or that the exhaustive search is practical. No strict positivity or strict margin is required. The hypotheses of the later curved-certificate P77 are not imported into P45.

## Dependency chain

1. `rational_feasible`: a real feasible finite system of weak rational linear inequalities has a rational feasible point.
2. `rational_nonnegative_solution` and `rational_solution`: specialize to nonnegative and unrestricted solutions of rational equations.
3. `rational_right_inverse`: real surjectivity of rational $V$ supplies a rational $R$ with $VR=I$.
4. `rationalize_certificate`: rationalizes each branch-lift column and the initial coefficient vector while keeping the given $V$.
5. `Candidate`, `candidateEncodable`, `Valid`, `checkCode`, `search`: actual computable representations, decoder, exact checker and finite-fuel search.
6. `rational_finite_certificate_search`: some finite fuel returns an accepted witness under precisely the rational-generator hypothesis.
7. `accepted_probability_domain`, `accepted_all_word_probabilities`: connect acceptance to the inherited P39 cone and positive-instrument results.

## Rational feasibility, including faces

`RationalFeasibility.lean` works with any finite row index and $n$ unknowns. The system is

$$\sum_{j<n} a_{ij}x_j\le b_i,\qquad a_{ij},b_i\in\mathbb Q.$$

Induct on $n$. For $n=0$, the same constant inequalities hold over both fields. At a successor step write the leading coefficient as $c_i$, the remaining row as $d_i$, and the first unknown as $t$. Rows with $c_i=0$ survive unchanged. Pair every negative row $i$ with every positive row $k$, divide by $-c_i$ and $c_k$, and add to cancel $t$. Inactive row and pair slots are filled by $0\le0$, so the reduced index remains an explicit finite sum/product type.

A real feasible point satisfies the reduced system. The induction hypothesis supplies a rational tail $y$. Set $r_i=b_i-d_i y$. The paired inequalities say

$$r_i/c_i\le r_k/c_k\quad(c_i<0<c_k).$$

Choose the greatest lower bound from the finite set of active rational lower endpoints; if no lower endpoint exists, choose the least upper endpoint; if neither exists, choose zero. The auxiliary `rational_interval` verifies the closed-interval step. There is no density approximation and no loss of an equality face. The selected rational first coordinate and tail satisfy every original row.

To encode $Vx=z$ and $x\ge0$, use both $Vx\le z$ and $-Vx\le-z$, with $-x_j\le0$. For unrestricted equations omit the sign rows. These are internally proved reductions; no external rational-LP completeness theorem is assumed.

## Rationalizing the actual P39 witness

For every symbol and generator column, the equations $Vq=B_sv_j$ have a nonnegative real solution from the supplied lift. Rational nonnegative feasibility gives a rational solution. Assemble those columns into rational branch lifts.

For the initial vector, append the row of ones to $V$ and append $1$ to $z_0$. Solving that augmented system preserves both $V\alpha=z_0$ and $\sum_j\alpha_j=1$, including zero coefficients.

Real full row rank is represented by surjectivity of the real matrix linear map. Solve $Vq=e_j$ for each rational standard basis vector using unrestricted rational feasibility. The columns give the rational right inverse $R$. Thus requiring $R$ in the enumerated witness does not strengthen the completeness hypothesis.

## What is enumerated and checked

`Candidate r s` is a dependent pair of a natural width $m$ and four rational data blocks:

- $V\in\mathbb Q^{r\times m}$;
- $A_t\in\mathbb Q^{m\times m}$ for each of the $s$ symbols;
- $\alpha\in\mathbb Q^m$;
- $R\in\mathbb Q^{m\times r}$.

The computable `Encodable` instance uses the standard exact rational, finite-vector, product and dependent-pair encodings. `Encodable.decode (Encodable.encode c) = some c` supplies exhaustive coverage of every width and all entries. This is dovetailing over the whole witness, not an inner unbounded search that could block on one infeasible generator matrix.

`Valid` checks exactly

$$\lambda V=\mathbf1^\top,\quad VR=I,\quad B_tV=VA_t,\quad A_t\ge0,$$
$$\alpha\ge0,\quad \mathbf1^\top\alpha=1,\quad V\alpha=z_0.$$

Its decision procedure uses rational arithmetic and finite equalities/sign tests. The supplied model's mass identities are separate input hypotheses for the probability conclusion, as in P45. `rational_mass_identity` explicitly converts the rational column identities to P39's real functional identity.

`checkCode k` decodes one candidate and filters it by `Valid`. `search N` inspects natural codes below $N$, returning the first accepted candidate. Zero fuel returns `none`. Once it returns a candidate, increasing fuel preserves that exact result. For every valid candidate $c$, fuel $\operatorname{encode}(c)+1$ has found some valid candidate, possibly an earlier one. These are proved universal statements. The procedure is exposed as a terminating finite-fuel function; increasing fuel implements the unbounded semidecision procedure. No nonterminating Lean definition or classical choice is hidden in the executable search.

`none` means only “no accepted code in this prefix.” `search_no_certificate` proves the valid forward implication that absence of every rational certificate makes every prefix fail; the converse is not inferred from one prefix.

## Semantic soundness

Cast accepted rational entries to real entries. Matrix multiplication commutes with that cast. $VR=I$ gives real surjectivity. Normalization becomes `readout l ∘ V = mass`; intertwining becomes equality of linear-map compositions. Initial coefficients become a real prior and synthesize the supplied initial state.

Apply the inherited P39 results to obtain a closed, pointed, generating cone with strictly positive mass on nonzero elements, initial-state membership, and invariance under every branch. Exact per-action mass identities produce a nonnegative instrument and word probabilities in $[0,1]$ at every finite depth. An arbitrary action/observation-to-symbol coding is supported, with a finite observation alphabet; no injectivity of that coding is needed for the stated mass identity.

The mass readout and semantic real maps are noncomputable mathematical objects. The rational candidate decoder, checker and finite-fuel search are computable. Classical choice occurs in the existence proofs used to establish eventual success, not as an implementation of the search.

## Boundary examples and executable evidence

Eight named example theorems cover a scalar identity certificate, an allowed zero branch, rejection of a negative branch lift, rejection of a rank-deficient generator, exact decoder/checker recovery of an encoded witness, failure of zero fuel despite a valid certificate, a rational solution on a boundary face, and the distinction between total mass and branch positivity.

`scripts/RunRationalSearch.lean` executes five checks. Expected outputs are `true, true, false, true, false`: accept identity; accept zero branch; reject signed lift; decode/check the identity candidate at its exact code; find no accepted code in the first 64 codes. The last result is deliberately not a nonexistence claim. The executable outputs are checked by both complete verification runs. They do not claim a practical search benchmark or a bound on witness code size.

Four new isolated negative controls try to turn bounded failure into impossibility, require strictly positive branch lifts, accept a signed lift, or omit the rank requirement. The verifier requires real proof diagnostics, not missing imports or timeouts.

## Development repairs and provenance

The first broad `Mathlib` import was narrowed to explicit dependencies. Elimination division identities and sign orientations were repaired; the pinned release's deprecated `if_pos` name was replaced. Dependent witness unfolding and an explicit rational Boolean order decision were needed to synthesize the computable checker. Direct kernel reduction of the matrix examples stalled on opaque arithmetic; their proofs use ordinary exact simplification, while compiled execution is checked separately. The runtime example needed explicit dimensions at the untyped natural-code call. One premature example invocation failed because its imported module had not yet compiled; it is a development failure, not a negative-control success.

The first cumulative preflight rejected the ordinary English word “admit” in a comment because it matched the prohibited-token scanner; the comment was changed without changing the theorem. A metadata-script replacement briefly turned the inherited file count 74 into 44; the consistency gate caught it, and it was repaired. All retained compiler diagnostics and snapshots distinguish failed development attempts from accepted proof evidence.

The predecessor roadmap's standalone `remaining_count` was stale at 57 even though its lists and coverage correctly described 52. This release sets it to the new exact value 51 and adds a gate comparing the field with the exhaustive list. Historical files and predecessor ZIP remain unchanged.

## Reproducibility and limits

Use `README.md` for the pinned verification commands. Counts are source inventory metrics, not mathematical novelty or difficulty measures. Self-review plus Lean kernel acceptance is not an independent referee, a second proof assistant or an exhaustive replay of all upstream Mathlib. The archive manifest and external fresh-extraction receipt identify the delivered bytes. The original source and proof register are not edited by this formalization.
'''
# Use the actual source section heading rather than a guessed section number.
src=(root/'source/FOUNDATIONS_1.0.0.md').read_text();before=src[:src.index('**Proposition 45.')];heading=before[before.rfind('\n# ')+1:].splitlines()[0]
guide=guide.replace('Foundations 1.0.0 §49 (the frozen heading and proposition are authoritative)', 'Foundations 1.0.0, '+heading.lstrip('# ').strip())
(root/'LEAN_GUIDE.md').write_text(guide)
prog=json.loads((old/'PROGRESS.json').read_text());prog.update(release='0.10.0',completed=cover['complete'],partial=[],outstanding=sorted(set(range(1,88))-set(cover['complete'])),new_complete=[45],current_block=[45],next_restart=[32,33,34],source_verification={'passed':False,'complete':False,'report':'verification/block10_release_run/report.json','status':'pending'},verification='See verification/block10_release_run/report.json and external exact-archive delivery verification',date='2026-10-12')
(root/'PROGRESS.json').write_text(json.dumps(prog,indent=2)+'\n')
ledger=(old/'PROGRESS.md').read_text();start=ledger.index('| Block |');end=ledger.index('\n\n',start);table=ledger[start:end]
(root/'PROGRESS.md').write_text('''# Large Signal Model Lean — persistent progress ledger

**Current: 0.10.0 · Frozen theory: 1.0.0 · 36 complete / 87 · 51 outstanding.**

'''+table+'''
| 0.10.0 | P45 rational finite-certificate search | 36 | 51 |

Block 10 proves rational feasibility by weak Fourier–Motzkin elimination, derives rational lift/initial/right-inverse witnesses, implements exhaustive natural-code search with exact checking, and connects accepted witnesses to P39's cone and all-word probability guarantees. Four modules add 30 named theorems, including eight examples; four new negative controls bring the total to 72.

Coverage is not difficulty weighted. All 74 predecessor proof files, 1,256 declaration records and 68 rejection-control sources remain unchanged. Source guides, histories, the frozen manuscript and the complete predecessor archive are retained. The executable search uses no hidden-state generator or supplied certificate as an input. Its completeness proof assumes that a rational-generator certificate exists.

Verification is recorded in `verification/block10_release_run/report.json`, with exact-archive verification supplied externally. Do not infer a successful run merely from this descriptive ledger. The progress JSON is finalized from the actual accepted report. Failed compiler attempts and source snapshots remain under `verification/development_block10/`; the prohibited-word preflight failure is separately preserved.

The roadmap's stale standalone remaining-count field was repaired, and an extra gate now compares it with the exhaustive list. Publication metadata is clarified by `PUBLICATION_STATUS.md`, without changing the frozen documents.

## Next restart

P32–P34: read the exact frozen linear-identification and stability statements and register proofs before selecting the next block. All 51 remaining propositions appear exactly once in `ROADMAP_1.0.json`. Do not jump from this semidecision result to a practical optimizer, complexity bound, universal rational-certificate existence, or completion of the curved-certificate track.

No production PR-LASM changes, training, empirical confidence tests, independent referee, second prover, full upstream rebuild or external publication was performed.
''')
(root/'CONTINUE_HERE.md').write_text('''# Continue here — Large Signal Model Lean 0.10.0

Block 10 completed P45. Current frozen-target coverage is 36 complete, no partial, 51 unformalized out of 87. Read `AUDIT.md`, `LEAN_GUIDE.md`, `PROGRESS.json` and the accepted verification report before continuing.

Next: P32–P34, the remaining linear-identification/stability track. Resolve all three exact frozen statements and hypotheses before choosing the proof order. P45 now has real-to-rational weak feasibility, computable exhaustive candidate decoding/checking, conditional termination, and inherited P39 semantic soundness. Do not reopen it as though only rational witnesses had been assumed.

The finite-fuel API is mathematical exhaustive search, not a practical exact-LP implementation. None from a finite prefix is not impossibility. No strict margin is needed for P45; curved conditional search has different hypotheses and remains open.

The 0.9.0 predecessor archive, 74 proof files, 1,256 declaration records, 68 controls and frozen theory hashes are preserved. Failed attempts remain under `verification/development_block10/`. The stale predecessor roadmap scalar was repaired only in the current roadmap and is now gated.

Verify manifest hashes before generating caches. Use the pinned runtime read-only. Current source evidence is `verification/block10_release_run/report.json`; exact delivered-archive evidence is the external verification JSON. A missing-import diagnostic is never a successful rejection control.
''')
(root/'COVERAGE.md').write_text('# Formalization coverage — 0.10.0\n\n36 complete, 0 partial, 51 unformalized of the frozen 87 propositions. Added P45. `COVERAGE.json` maps exact source hashes and Lean declarations. The whole framework is not complete.\n\n'+ '\n'.join(f"- P{e['proposition']}: {e['title']} — {e['status']}" for e in cover['entries'])+'\n')
(root/'ROADMAP_1.0.md').write_text('# Remaining formalization roadmap — 0.10.0\n\n51 propositions remain. Next: P32–P34. Counts are not difficulty weighted.\n\n'+ '\n\n'.join(t['title']+': '+', '.join('P'+str(n) for n in t['propositions']) for t in road['tracks'])+'\n')
(root/'PUBLICATION_STATUS.md').write_text((old/'PUBLICATION_STATUS.md').read_text()+'''\n## 2026-10-12 — Lean 0.10.0 sidecar\n\nP45 is formalized in addition to the 35 predecessor mappings. Current coverage is 36/87. The frozen publication text and PDFs remain unchanged; its historical no-Lean sentence does not describe the subsequent formalization. This sidecar is not a new publication or typeset revision.\n''')
register=json.loads((root/'source/PROOF_REGISTER_1.0.0.json').read_text());entry=next(x for x in register['entries'] if x['id']==45)
card={'proposition':45,'source':'source/FOUNDATIONS_1.0.0.md','heading':heading,'statement_proof_sha256':entry['statement_proof_sha256'],'normalized_claim':'Finite rational model, exact mass identities; rational normalized full-row-rank generator certificate with possibly real nonnegative lifts and initial coefficients implies eventual return of an exact rational valid certificate. Every return yields a P39 probability domain and all-word bounds under mass identities.','exceptional_cases':['Zero dimensions and empty constraint rows included in general feasibility','Zero coefficients and branch lifts allowed','No global termination if no rational generator certificate exists','Finite prefix failure is inconclusive'],'dependencies':['Internal weak Fourier–Motzkin induction','Pinned Mathlib finite extrema, rational arithmetic and Encodable.encodek','Inherited P39 cone topology and positive instrument results'],'review':'self-review','verdict':'pending cumulative verification'}
(root/'verification/BLOCK10_CLAIM_CARD.json').write_text(json.dumps(card,indent=2)+'\n')
audit='''# Large Signal Model Lean 0.10.0 — P45 audit

**Normalized claim:** Under the frozen rational-model and exact-mass hypotheses, a P39 certificate with rational normalized full-row-rank generators suffices for eventual return of an exact rational certificate. Real nonnegative coefficient witnesses are allowed in the premise. Every return is semantically sound. No strict margin, universal existence or finite-failure impossibility is asserted.

**Primary verdict:** pending cumulative verification. The finalization step replaces this verdict only after the accepted run passes. Review is self-review, not an independent referee report.

## Dependency and obligation matrix

| Obligation | Evidence | Status |
| --- | --- | --- |
| Authoritative claim | Frozen P45 source hash and register, `BLOCK10_CLAIM_CARD.json` | Passed |
| Weak rational feasibility | Induction on unknown count, zero rows and sign-paired elimination | Passed in development compile |
| Boundary faces | Closed rational endpoint selection, not strict density | Passed in development compile |
| Rationalization | Each lift column, augmented initial system, unrestricted inverse columns | Passed in development compile |
| No stronger rank assumption | Real surjectivity derives rational right inverse | Passed in development compile |
| Exhaustive enumeration | Computable sigma/product/finite-vector/rational Encodable; encode/decode identity | Passed in development compile |
| No blocked inner search | One natural code decodes a whole finite witness | Passed |
| Executable exact checking | Finite rational equalities and signs; five compiled examples | Passed in development; rerun in release |
| Conditional termination | Valid candidate's code plus one is sufficient fuel | Passed in development compile |
| Persistent first return | Increasing fuel preserves the same candidate | Passed in development compile |
| All-word soundness | Rational casts, right inverse, P39 cone and instrument | Passed in development compile |
| Rational mass hypotheses | Explicit rational column-to-real-functional theorem | Passed in development compile |
| Frozen-source preservation | Source hashes and predecessor-file gates | Passed metadata gate |
| Cumulative kernel and axiom audit | Full source and fresh archive runs | Pending |
| Practical complexity | Not asserted by P45 | Out of scope |
| Full framework formalization | 51 propositions still unformalized | Out of scope |

No external source theorem is inserted without proof. Rational polyhedron feasibility, which the written proof cites as standard, is established internally here. Pinned Mathlib supports finite arithmetic, encoding, and inherited standard algebra/topology, within the ordinary dependency trust boundary. No internet source was needed for this local-source proof task.

## Adversarial boundaries

Zero unknowns, empty row families, leading coefficient zero, absent lower bounds, absent upper bounds, and coincident rational endpoints are included in the feasibility induction. Inactive rows are tautologies, not dropped under an unchecked filter. Branch and initial coefficients may be exactly zero. Rank is a genuine right-inverse identity; normalized columns alone do not imply spanning. Exact mass alone does not force branch positivity. No fixed search prefix or rejected candidate proves no certificate exists.

The finite-fuel function is the executable interface to unbounded dovetailing: universal existence of successful fuel is the formal termination guarantee. It is not a classical witness masquerading as code. Classical choice is confined to proofs that some enumerated rational witness exists. The decoder/checker/search definitions are ordinary computable Lean definitions, and compiled examples exercise them.

## Failed attempts and repairs

Compiler snapshots and complete diagnostics are retained in `verification/development_block10/`. They include import narrowing, division/sign repairs, pinned-API name changes, dependent-pair reductions, explicit computable order instances, opaque-arithmetic reduction in example proofs, a missing module during a premature example run, and a missing dimension annotation in executable code. None of these failures counts as an accepted proof or negative control.

A preflight prohibited-token check also rejected a normal English comment containing the token `admit`; the replacement “have” changed no mathematics. That failed report remains under `verification/block10_preflight_rejected_word/`. A metadata script's broad replacement briefly changed the inherited file-count literal from 74 to 44; the metadata gate caught it before the full accepted run. The correction is exact and all predecessor hashes remain fixed.

The inherited roadmap scalar claimed 57 remaining while its actual lists and prior coverage had 52. This release corrects the current scalar to 51 and adds a gate tying it to the list. Archived predecessor metadata is preserved as historical evidence.

## Scope and trust

All 74 predecessor proof sources, 1,256 declaration records and 68 controls are preserved. The two frozen theory files and existing PDFs are unchanged. Allowed foundational axioms are exactly `propext`, `Classical.choice` and `Quot.sound`; module replay checks generated declarations beyond the named source inventory. The pinned runtime is reused read-only with its supplied executable-location adapter, not freshly extracted or exhaustively rebuilt.

No independent referee, second prover, statistical experiment, training, production-code verification or external publication is claimed. Exact archive identity and fresh cumulative replay are reported by the external verification JSON. The source report inside the ZIP is not treated as proof about different bytes.

## Conservative mathematical proofreading

Proofread: the four new Lean comment blocks and this block's new guide, audit, coverage and restart prose, with frozen P39/P45 context. Routine edits: clarified weak inequalities, rational-generator versus coefficient hypotheses, finite-fuel interpretation and mass assumptions. Mathematical-token changes: none made as proofreading; mathematical development changes are retained in compiler snapshots. Unresolved issue: no objective notation or source-scope inconsistency found in these new texts. Validation: exact statement hash mapping and metadata checks; cumulative verification recorded separately. Historical prose outside this block was not rewritten.
'''
(root/'AUDIT.md').write_text(audit)
# Preserve the diagnostic probe without making it a released proof target.
p=root/'Probe.lean'
if p.exists():p.rename(root/'verification/development_block10/Probe_final.lean')
print('Documentation prepared; final verification status remains pending.')
