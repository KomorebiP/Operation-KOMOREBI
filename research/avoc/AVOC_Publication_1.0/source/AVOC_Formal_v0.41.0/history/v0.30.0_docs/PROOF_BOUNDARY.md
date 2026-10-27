# AVOC v0.30.0 — exact proof and implementation boundary

## Proved in this block

- Exact reuse of a validated factor/rank certificate for equal linear maps with arbitrary new affine offsets, including a nonzero first-stage offset.
- Repeated retargeting overwrites rather than accumulates offsets. Minimum width and factor tariff are retained.
- Revalidation rejects invalid stored certificates and mismatched current linear maps. Different valid witnesses have the same certified width.
- Selection is against the current original/dense/factor menu, never a stale cached plan. Complete input semantics and per-call nonregression hold.
- Zero/nonzero linear classification provides a sound width floor for any exact two-stage factorization.
- Opportunity and minimum-setup inequalities prove when no positive remaining task-level gain is possible within the declared menu.
- The executed cold/warm preflight Boolean tests are connected to those inequalities, with explicit tariff/emission hypotheses.
- Revalidation is not free; funded import has exact credit bounds. Cold and warm lifecycle comparison has a proved break-even equivalence.
- Concrete offset, nonzero-first-offset, cost, and optimistic-preflight-failure examples are ordinary kernel proofs.

## Executed and independently tested

The Lean entrypoint supplies normalized signatures, preflight decisions, certificate checking, retargeting and selection. Python supplies the inherited candidate generator and a new immutable certificate-snapshot store. Tests use independent homogeneous-matrix semantics, direct AST execution and explicit image enumeration for small shapes.

## Exclusions

1. The optimum is minimum width / tariff for TWO dense affine stages and the current original/direct comparators, not arbitrary sparse or multi-stage circuits or physical execution time.
2. The early-stop conclusion is relative to declared calls, remaining setup costs and this implementation class. Broader cross-task discovery/archival option value is absent. Passing a bound does not guarantee positive realized net.
3. Preflight itself is paid. It can lose money. It is not a net-optimal metareasoning policy. The original program remains valid if generation or validation fails.
4. Nominal tariffs omit parsing, copying, allocation, comparisons outside the explicit tariff, IO, fingerprint checks, process startup, real arithmetic cost and storage maintenance. Per-call records are not authenticated payment histories.
5. Generic algebraic theorems require a Field. The executable uses exact canonical GF(5) residues with dimensions <=8 and bounded syntax/input sizes. No numerical approximate low-rank claim.
6. The tracked-RREF generator is tested, not universally proved complete or complexity-optimal. Failure does not imply absence of a factorization. Direct-wire prior charges are declared data; the wrapper supplies actual nominal meter totals.
7. Cache records are untrusted mathematical data until rechecked. Header/key fingerprints do not establish trusted provenance. Deliberate edits that still form a mathematically valid certificate are not inherently false.
8. Python config/store parsing, filesystem operations, serialization round trips and reading the real snapshot are tested rather than universally formally verified. The host, runtime and exact dependency cache are trusted.
9. Protected single-writer snapshot files; no hostile rollback, remote attestation, general path-race protection or distributed crash guarantee. Publication interruption is tested with a controlled Python exception, not SIGKILL or power loss.
10. The cache does not install code or alter AVOC's research, retry, synthesis or upgrade stores. Those formats are not migrated. No autonomous improvement or real LLM productivity is claimed.
11. The stored original affine offset is part of the certificate and rechecked. The lookup key intentionally omits it; a NEW offset is explicitly compensated in the second stage. That is proved transfer, not byte-identical reuse of the original affine function.
12. Current-source local compilation and complete theorem axiom audit retain pinned external caches. No fresh source rebuild of mathlib or independent Lean-kernel verification is claimed. Historical live/crash/agent suites were not rerun.
