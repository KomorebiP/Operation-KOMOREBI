# AVOC v0.29.0 — exact boundary

## Proved and compiled

- Candidate polynomial-identity checker iff exact affine composition and U A V = identity.
- Checked rank equals candidate width and every equivalent two-stage factorization has at least that width.
- Dense two-stage tariff is strictly increasing in width; checked factorization is optimal in this exact class.
- Choosing between original, fused dense map and checked factor preserves all inputs and minimizes their per-call tariffs; no exact two-stage dense competitor is cheaper.
- Full setup-plus-deployment break-even equivalence. Search and checking charges are not refunded when the original wins.
- Resource-checked admission, rejected wrong offsets and lower witnesses, zero-rank and identity cases.
- Concrete sound certificate examples are kernel reduced with ordinary proofs/decide; no native evaluation axiom.

## Executed, not universally formally verified

A Python tracked-RREF proposer emits factors and rank witnesses. The actual Lean gate normalizes the supplied original program and checks them. An independent oracle uses homogeneous matrices, explicit image spans, and direct AST evaluation. Every 2x2 GF(5) linear matrix is included with a specified varied offset, not every affine map in every shape. Constructed rectangular/zero-dimensional/rank families and sampled pipelines broaden the finite regression.

## Non-claims

1. No general globally cheapest affine circuit, arbitrary matrix chain, sparse arithmetic, shared-subexpression or memory optimization. The universal optimum is minimum intermediate width and the associated two-dense-map tariff. The original implementation remains an available exception/comparator.
2. No formal proof that the Python proposer always terminates successfully, produces a certificate for every allowed input, or meets a universal complexity bound. If it fails, no absence-of-factorization conclusion follows. Accepted outputs have the theorem; bounded tests support the proposer.
3. Fields in the rank theorems, not arbitrary rings. The earlier ring-valued semantic theorems remain unchanged.
4. Runtime coefficients are exact canonical GF(5) residues; dimensions <=8; source syntax and input sizes are bounded. No floating-point stability or approximate low-rank claims.
5. Declared generation and checking tariffs are not all physical costs. Inversions carry a declared unit tariff. Copies, allocation, parsing, comparisons outside the explicit tariff, repeated runtime normalization, serializer work and process startup are not fully priced. The direct checker wire accepts generation cost as an external assertion; trusted meter provenance is an implementation obligation.
6. The selector minimizes execution tariff after exploration. It does not prove it was worth exploring, optimally choose a budget, or prevent negative total campaign net. Preserving a zero-cost identity after paid exploration can still lose money.
7. Python parsing/metering, JSON round-trip correspondence, physical runtime and full host/OS authenticity are not formally proved. The theorem concerns the decoded typed candidate and original typed program.
8. No persistent candidate promotion, shared library, live research mutation, autonomous improver or empirical LLM benefit. The wrapper is read-only, with an explicit optional new-file certificate export.
9. Pinned Lean kernel/compiler and nine dependency caches are trusted. This is a full LOCAL project rebuild, not a source rebuild of mathlib or independent kernel verification.
10. Historical filesystem/crash/retry/synthesis tests were retained but not rerun. All claimed new runtime tests and current-source compilation/axiom/negative results are recorded under v0.29.0.
