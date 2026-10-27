# Large Signal Model Lean 0.10.0 — P45 audit

**Normalized claim:** Under the frozen rational-model and exact-mass hypotheses, a P39 certificate with rational normalized full-row-rank generators suffices for eventual return of an exact rational certificate. Real nonnegative coefficient witnesses are allowed in the premise. Every return is semantically sound. No strict margin, universal existence or finite-failure impossibility is asserted.

**Primary verdict: proved as written.** The cumulative source verification passed all 231 stages. Review is self-review, not an independent referee report.

## Dependency and obligation matrix

| Obligation | Evidence | Status |
| --- | --- | --- |
| Authoritative claim | Frozen P45 source hash and register, `BLOCK10_CLAIM_CARD.json` | Passed |
| Weak rational feasibility | Induction on unknown count, zero rows and sign-paired elimination | Passed: compile, axiom audit and kernel replay |
| Boundary faces | Closed rational endpoint selection, not strict density | Passed: compile, axiom audit and kernel replay |
| Rationalization | Each lift column, augmented initial system, unrestricted inverse columns | Passed: compile, axiom audit and kernel replay |
| No stronger rank assumption | Real surjectivity derives rational right inverse | Passed: compile, axiom audit and kernel replay |
| Exhaustive enumeration | Computable sigma/product/finite-vector/rational Encodable; encode/decode identity | Passed: compile, axiom audit and kernel replay |
| No blocked inner search | One natural code decodes a whole finite witness | Passed |
| Executable exact checking | Finite rational equalities and signs; five compiled examples | Passed in release execution |
| Conditional termination | Valid candidate's code plus one is sufficient fuel | Passed: compile, axiom audit and kernel replay |
| Persistent first return | Increasing fuel preserves the same candidate | Passed: compile, axiom audit and kernel replay |
| All-word soundness | Rational casts, right inverse, P39 cone and instrument | Passed: compile, axiom audit and kernel replay |
| Rational mass hypotheses | Explicit rational column-to-real-functional theorem | Passed: compile, axiom audit and kernel replay |
| Frozen-source preservation | Source hashes and predecessor-file gates | Passed metadata gate |
| Cumulative kernel and axiom audit | Full source passed; exact-archive fresh run reported externally | Source passed |
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

Accepted source-candidate result: PASS, 231 stages: 79 compilation targets, one executable-example stage, one axiom-audit stage, 78 kernel replays and 72 proof rejections. All 1,304 named declaration axiom records passed. Metadata: 76 checks. Development: 36 compiler invocations, 11 successful and 25 failed, all retained. No subprocess timeout occurred in the accepted run.
