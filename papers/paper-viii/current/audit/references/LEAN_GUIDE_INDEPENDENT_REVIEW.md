# Paper VIII Lean Guide: independent documentation review

Reviewed on 2026-10-06 UTC. The guide passes the requested instructional correspondence review at the inspected level. All ten chapters explain represented mathematical objects, relevant hypotheses, and concrete proof moves. They are substantive teaching chapters rather than a declaration catalog. Two context repairs and one clarification are now present: noncommutative product order, the nonempty Jacobi index type, and the positive Toeplitz length. The final Krylov wording also correctly avoids implying Hilbert-space self-adjointness.

This is a read-only review. No raw Lean, benchmark, or author file was changed by this reviewer. It is not a fresh Lean compilation or a complete independent audit of every one of the 392 theorem proofs. The source-bound accepted compiler run remains inherited evidence, and the guide explicitly identifies supplied classical and SVD inputs.

## Frozen document identity

| Artifact | SHA-256 |
|---|---|
| Main guide TeX | `0856f764bd75c992f80e80c473443231a6bd5f5cc82a819188c919c8077a587b` |
| Final 86-page PDF | `31588954796fdf72b68a49698b507aeb9a8d716925033586c03e37fb8e57a8fb` |
| Independent JSON review | `1101a9692fe2dea39dc19b8a756b98932c526ecc171a90991c9ad47ddd388b64` |
| Inherited accepted summary | `768b48a902e571c8f5e7dacc8424aea447add7df03bbd9d79dd892fe27cae629` |

The JSON review pins every chapter, the preamble, all generated JSON tables, the exact excerpt register, the 40 active sources and saved compiler logs, and both rejected controls. The parent editor performs the separate all-page rendering review.

## Independent static reconciliation

The reviewer wrote and ran `replay_lean_guide_review.py`; it does not import the guide assembler or invoke Lean. Its namespace and nested-comment parser independently reproduced all 536 declaration records and their source locations, including the attribute-prefixed foundation theorem that a plain line-start count misses. The resulting count is 392 theorem/lemma declarations: 373 Paper VIII declarations and 19 reused foundation declarations.

All 458 literal `#print axioms` names are unique and match the generated catalog. The difference is 66 construction audits, not 66 extra theorem proofs. The ten sixth-block modules independently contain the advertised 79 new theorem declarations. All 61 raw UTF-8 excerpts, totaling 635 source lines, match their contiguous active-source selections and their source/excerpt hashes. Every selection is taught exactly once in the chapters.

Every active source hash and saved log hash matches the accepted summary. Independently parsed saved axiom sets match all 458 recorded sets and stay inside the recorded policy. Both invalid-proof controls have matching retained source/log identities and the recorded rejection exit code. The exact generated coverage ledger matches the preserved ledger: 85 numbered records, 56 checked manuscript-proved records, and four separately tracked classical records. Every checked record's listed theorem names occur in the audit inventory. These checks authenticate retained bytes and documentation reconciliation; they do not recreate compiled interfaces, rebuild imported Mathlib, or certify prose-to-code equivalence.

Neither Lean nor Lake is installed on this review host. `fresh_lean_kernel_run` remains false. The guide makes this distinction in the title material, reading chapter, replay chapter, and its machine-readable report.

## Targeted instructional findings

| Chapter or topic | Correspondence reviewed and result |
|---|---|
| Exact semantics | Ring-valued mutually annihilating projectors, actual exact-nonzero filtering, target-first block order, composition support inclusion, and cancellation controls agree with source. Adjoint semantics explicitly supply self-adjointness. The stored Python key-set distinction is stated. |
| Representation algebra | Storage/application counts use declared finite event/address models. Roofline capacity inequalities are premises. Actual rectangular BDLR factors are constructed, and Woodbury exposes both base and small-update unit assumptions. |
| Structured algorithms | Column-major vectorization uses ordinary transpose in the Kronecker formula. Tensor and Walsh claims concern actual recursive maps. Toeplitz/generator declarations inherit `[NeZero n]`; zero-padding remains defined without it. Fourier algebra does not claim a verified FFT execution cost. |
| Transfer graphs and solves | Path sums include zero length and allow cancellation. Inverse support uses finite dimensionality and a supplied inverse identity. DAG levels are constructed and optimal within the stated unit-duration model. Forward substitution is constructed for dependent block spaces, with correctness and uniqueness proved separately. |
| Error propagation | Local errors are actual continuous linear maps with source support. The product step now says the perturbed factor times the previous discrepancy, preserving noncommutative order. The chain endpoint exposes `NormOneClass`; residual propagation uses supplied actual residual bounds and does not infer floating-point stability. |
| Precision allocation | Positive costs, sensitivities and budget, nonempty finite edge set, exact budget equality, the logarithmic global comparison, and strict uniqueness match source. Capped allocation distinguishes a unique tolerance vector from a potentially nonunique scale at full cap. Natural subtraction is guarded in discrete optimization. |
| Exact compilers | Legal cuts are defined independently of the recurrence. The endpoint combines a universal lower bound with an attaining compiled cut. Option-valued budget semantics distinguish infeasibility. Stored arrays have an explicit refinement proof and declared unit-cost work model. Stability uses solved-score half-gap control at every node; cached updates require valid cached sibling values. |
| Krylov and contracts | Abstract fair-match fields and decoding identity are supplied models. The exact Krylov statement is inclusion, not equality with the full independent sum of local spaces. Directness uses mutually annihilating projectors. Approximate distance inherits its positive-power premise. Historical benchmark metadata are not claimed to instantiate the complete signature. |
| Jacobi and CG | The condition uses the L2 operator norm and the actual inverse positive square root. The repaired prose says the matrix index type is finite and nonempty at the condition-bound endpoint. The CG energy bound is explicitly `hCG`; the formal theorem propagates a condition upper bound through the convergence factor and does not prove CG algorithm correctness or the classical convergence theorem. |
| Small-core optimality | Compact factors use actual column-space dimensions equal to matrix ranks and classical choice of bases, not a floating-point QR kernel. `BestRank` quantifies over every ambient rank-bounded competitor. Compression rank contraction and both norm contractions are used to transfer core bounds. Diagonal spectral lower bounds use an actual kernel witness; Frobenius bounds use an actual kernel frame and a proved finite weighted-tail inequality. The final theorem discharges core optimality rather than accepting it as an SVD field. |

The small-core norm functions explicitly select the L2 operator and Frobenius norm scopes. `OrderedThinSVD` supplies two isometries, nonnegative antitone real values, and reconstruction equations. It supplies no optimality, residual-tail identity, norm-preservation conclusion, or ambient competitor certificate. The endpoint constructs factors with exactly `min d k` columns and proves both global best-rank conclusions and the exact spectral/Frobenius tail errors. Zero ranks, zero values and full retention remain defined without inverting a zero singular value.

General SVD existence, identification with Mathlib's canonical singular-values API, a floating-point SVD/QR implementation and numerical stability remain outside this formal block. The replay chapter correctly keeps the four classical boundaries separate: general Eckart–Young–Mirsky, classical CG convergence, the floating-point product model, and simultaneous spectral decomposition. Numerical mirrors and historical CPU/GPU timings are explicitly qualified as their own evidence classes.

## Repairs and residual scope

The reviewer requested the noncommutative-order wording repair and the nonempty Jacobi context repair; both are present in the frozen guide. The author independently supplied the positive Toeplitz context and sharpened the Krylov directness language. No unresolved mandatory instructional finding remains in this review.

The verdict is documentation correspondence passed, conditional on the explicitly supplied mathematical data and inherited compiler evidence. It should not be shortened to a claim that this host freshly kernel-checked the development, fully authenticated every bibliographic theorem, replicated hardware results, or formally proved equivalence among manuscript, Lean and prototype code.

Reproduce the static checks with:

```text
python replay_lean_guide_review.py --source PATH_TO_original_snapshot --guide PATH_TO_lean_guide --output REVIEW.json
```
