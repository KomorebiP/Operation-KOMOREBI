# Paper V second-block review

Author: Komorebi P.

## Decision

Continue proof development from this bundle, but do not publish it as a kernel-verified Paper V release. The source inventory has advanced from 29 to 75 candidate theorem declarations. The exact reference tests and verifier controls pass. **Zero new Lean declarations were kernel-checked.** The compiler and Lake are still absent, and the official-download retry failed with a DNS resolution error.

The 31-page adaptive-tree-resolved manuscript is byte-for-byte unchanged. Its SHA-256 remains `9b1cbe3c771f90fae651d13eeb41a05804953d9f923bc1160a3e1b385b571e85`. The first-block correction supplement is also unchanged. This review does not supersede its singleton, channel-delay, and projective-pole corrections.

## 1. Concrete integer polyphase coordinates

The previous source assumed an arbitrary address equivalence. `IntegerPolyphase.lean` now constructs the actual map from a signed integer address to a residue in `Fin N` and an integer quotient, under the explicit hypothesis `0 < N`. Its inverse is the literal address `N*q+r`.

The 11 declarations cover residue bounds/casts, both inverse laws, the coordinate equivalence, analysis and synthesis, channel delays, general original-sample delays with signed carry, and coarse-to-fine refinement when N divides M. Negative addresses use Euclidean quotient and remainder, not truncation toward zero.

The scope is pointwise functions on the integers. No membership in l2, boundedness, continuity, or unitary equivalence is inferred from the coordinate bijection. Those remain ledger obligations for 2.1 through 2.3.

## 2. Literal FIR transfer

`FIRTransfer.lean` defines a tap equivalence for each output phase k. For tap t, let `s=(k-t) mod N` and `m=-floor((k-t)/N)`. Its inverse is `t=N*m+k-s`. This produces the exact sample-address relation needed by the paper's kernel formula.

The source uses a finitely supported filter `h : Z ->_0 K`, but the input `x : Z -> K` need not have finite support. It reindexes the finite filter support, then partitions that image by input phase. Thus the candidate is an actual finite-sum time-domain transfer identity, not merely a placeholder equality assuming that identity.

There is a remaining presentation distinction in the manuscript's subsequent transform equation: the time-domain finite sum does not by itself define a convergent bilateral z-transform for an arbitrary input. A common convergence region, finite-support interpretation, or explicit Fourier/L2 interpretation must be supplied before treating that equation analytically. No transform-convergence theorem is claimed here.

## 3. Arbitrary finite branching

`FiniteAdaptive.lean` replaces the binary-only source limitation with a finite tree whose internal node has a positive finite number of children. This includes unary branches. A leaf has one stopping cut. A branch has either a stopping cut or one admissible cut in every child subtree.

The 17 declarations include additive root conservation for every recursive cut, synthesis with an identity root, one hit on every typed terminal path, finite attainment for arbitrary objectives, a positive competitor gap under an explicit nonempty-competitor hypothesis, and optimality of the additive dynamic-programming selector. They also include stop-on-ties, synthesis for the selected cut, exact attainment of the perturbation envelope, a value perturbation bound, and unchanged selection under a strict gap.

This is meaningful extra source scope, but it is not yet complete coverage of the paper's antichain definition. The source has not constructed and proved both directions of an equivalence between typed recursive cuts and finite sets of actual tree nodes meeting every terminal path once. The exact Python census checks that correspondence on all shapes with up to eight nodes, but does not fill the universal Lean obligation.

The comparison theorem equates two structural counting recurrences. It does not certify the evaluation time of the noncomputable Lean selector. The independently tested Python solver caches the bottom-up decisions and uses a separate extraction traversal. Exact rational bit complexity and the cost of materializing long path addresses are not treated as constant.

## 4. Finite lifting, normalized Haar, and matrices

`FiniteTransforms.lean` constructs the concrete equivalence between `Fin (2*n)` and `Fin n x Fin 2`. It proves candidate forward and inverse laws for the flat even-length lifting transform, including the vacuous empty-signal case.

The Haar definitions use the real scalar `sqrt(2)` explicitly. Candidate theorems establish pair involution, exact pair energy, finite sums of paired energies, and involution of the flat transform. The tests use exact arithmetic in Q(sqrt(2)), so a numerical tolerance does not hide an incorrect normalization.

The matrix extensionality argument tests each standard basis vector. The resulting abstract criterion says that equality of the composite matrix action on every vector is equivalent to matrix equality. It does not yet prove that the original analysis/synthesis filter-bank operators have that matrix representation. It is therefore recorded as supporting, not full coverage of 4.1.

No infinite l2 theorem, adjoint relation, general packet-tree Hilbert energy theorem, or complex-valued Haar theorem is supplied by these finite real identities.

## 5. Verifier defects and hardening

The first verifier used Python `assert` for mandatory hash, target, pin, and audit gates. Python optimization removes such assertions. This block replaces them with explicit exception-raising checks and adds a real optimized-Python rejection test. This was a verifier defect, not a discovered false mathematical theorem.

The new gates also cover the complete Lean source file set, frozen source/configuration hashes, actual namespace-aware declaration names, theorem locations, root imports, printed axiom targets, and the audit target array. A timeout preserves partial child-process output instead of discarding it. Unexpected compiler output, missing audit success, modified dependency sources, wrong revisions, and nonzero process exits cannot produce a verification success through the intended command path.

The source scanner remains lexical. It is not a parser. The source hash manifest is unsigned. Those checks do not replace a compiler, a kernel, or an adversarially secured supply chain.

The positive Lean branch of the verifier has not been exercised with a real compiler. The negative-control suite does not fabricate a successful compiler or axiom-audit log.

## 6. Executed evidence

| Suite | Tests | Counted mathematical assertions | Result |
|---|---:|---:|---|
| Inherited exact models | 12 | 25,825 | PASS |
| Second-block exact models | 8 | 280,108 | PASS |
| Verifier controls | 14 | Not included in mathematical count | PASS |
| Total | 34 | 305,933 | Python suites only |

The 626-shape tree census checks 129,958 subsets against independently computed root-to-terminal path incidence, recovering 3,467 complete prunings across those shapes. It checks every such cut's root synthesis, 3,130 rational objectives against exhaustive minima, the exact maximum-error envelope, and comparison counts. A separate exhaustive sweep checks 471 objectives with costs in {-1,0,1} on all shapes with at most four nodes.

Other cases include 216 additional sparse FIR examples, very large signed addresses, signed delay composition, arbitrary-channel resynthesis, the sharp strict-gap boundary, singleton trees, finite normalized Haar, and standard-basis matrix comparisons. These are deterministic finite checks. Counted assertions are deliberately reported separately from tests, theorem declarations, and paper statements.

Both ordinary and optimized-Python `--static-only` commands pass. The ordinary full command returns exit 2 and `BLOCKED_NO_LAKE`. The produced status file has `lean_kernel_checked: false` and `full_paper_coverage_certified: false`.

Actual reports are `verification/exact_model_results.json`, `second_block_results.json`, `verifier_controls_results.json`, `static_status.json`, `optimized_static_status.json`, and `verification_status.json`. The environment probe and download log record the failed compiler setup attempt. Historical first-block reports are segregated under provenance.

## 7. Next proof checkpoint

The highest-priority next step is a real pinned Lean build of these 75 candidates, followed by repairing elaboration/API issues and running the namespace axiom audit. The current sources may still contain such issues. Source review and official documentation lookup did not test elaboration.

After that, the largest mathematical scope gaps are the l2 operator bridges, the reverse antichain correspondence, measure-theoretic mask bounds, and the transform/filter-bank representation. The cyclic product and power statements, complex projective Smith action, and CRT factorization remain separate unfinished parts. A theorem is not promoted merely because a narrower finite model passed tests.
