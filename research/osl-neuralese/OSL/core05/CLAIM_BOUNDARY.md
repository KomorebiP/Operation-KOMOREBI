# OSL-Core 0.5 Claim Boundary

## Strongest justified claim

If every packaged Core 0.5 gate passes, the justified statement is:

> For the packaged finite 66-program OSL corpus, OSL-Core 0.5 preserves the declared 42 accepted and 24 expected-rejection outcomes. Its source-bound receipt evidence passes the receipt-hardened protected-state kernel and the separately implemented numerical, contract, finite-session, metadata-facing, and audit-intrinsic semantic verifiers. The observed release gates comprise 1,825 native receipts, 168/168 full tests, 75/75 focused Core 0.5 tests, and 3/3 Discovery Bridge programs with 71 receipts.

This is a finite executable conformance and semantic-reconstruction result. It
is stronger than receipt hashing or same-runtime replay alone. It is weaker
than a mechanized proof of the language, a complete independent second
interpreter, or a universal security theorem.

## What the release may claim

A passing Core 0.5 report may claim, within the named finite evidence:

- exact source, AST, lifecycle, statement-span, receipt-chain, and terminal
  bindings checked by the receipt-hardened base kernel;
- independent protected-state reconstruction for packets, proofs, memories,
  capabilities, actions, identities, and the protected rollback projection;
- independent numerical reconstruction for spaces, vectors, operators,
  application, transport, and the implemented projector/intertwiner checks;
- independent reconstruction of the five implemented temporal-contract
  templates and feedback-deadline behavior;
- independent reconstruction and graph checking of the implemented finite
  synchronous session protocols;
- independent reconstruction of secret commitments, metadata values,
  assertion accounting, `show` bindings, and their component-local rollback;
- independent recomputation of each embedded `verify_receipts` prefix report;
- rejection of the fully rehashed semantic mutations represented in the
  75-case focused gate;
- preservation of the 66-source 42/24 outcome matrix;
- a passing finite Discovery Bridge gate for its three packaged worlds.

Here, `independent` means that the semantic component does not import or invoke
`OSLRuntime`. It does not mean independent authorship, independent hardware,
or absence of shared dependencies and assumptions.

## Remaining semantic gaps

Core 0.5 does not independently establish:

1. the general truth of all fourteen assertion forms. It checks source binding,
   successful assertion accounting, and named underlying domains, but it is
   not a universal assertion evaluator;
2. the exact complete cross-domain transaction projection and all transaction
   projection digests. Components reconstruct their own rollback state, while
   the complete composite digest still depends on the primary implementation
   and supplementary replay;
3. interpreter rejection causality outside the predicates explicitly
   reconstructed by the independent components;
4. diagnostic `event_count` or the complete diagnostic event stream;
5. an independently implemented frontend in every path. The base kernel,
   metadata verifier, and audit-intrinsic verifier use primary parser or static
   components.

These gaps must remain visible in summaries and downstream papers. Exact
same-runtime replay may bind them for the packaged run, but replay is not an
independent semantic proof.

## Trusted computing base

The runtime and verifiers are Python programs. NumPy implements the finite
numerical operations in both the runtime and numerical checker. Canonical JSON,
SHA-256 implementations, Python behavior, NumPy/BLAS/LAPACK behavior, the host
platform, and the supplied source and evidence are part of the trusted
computing base.

The implementation is not verified in Lean, Coq, Agda, Isabelle, or another
proof assistant. Separate Python control flow reduces shared runtime-helper
risk but does not eliminate shared-library defects, specification mistakes,
platform behavior, or coordinated implementation errors.

## Generality

The evidence covers the packaged finite programs and focused test cases. It
does not prove correctness or safety for every syntactically valid OSL program,
arbitrary future grammar extensions, dynamically loaded code, unbounded
recursion, or unknown receipt schemas.

The focused 75-case suite is not exhaustive adversarial testing. Passing all
168 tests is an observed software result, not a proof that no untested defect
exists.

## Identity, integrity, and external authority

SHA-256 supplies content integrity under its cryptographic assumptions. It
does not authenticate a human, model, process, machine, or organization. It
does not establish authorship, consent, freshness, trusted time,
nonrepudiation, or principal identity.

An OSL capability is a symbolic ledger entry. Without separate host
enforcement, it is not an operating-system sandbox, network policy, hardware
boundary, access-control mechanism, or guarantee that a real external action
was authorized or executed correctly.

Transactions apply only to modeled in-memory state. They do not imply database
durability, distributed atomicity, crash consistency, secure erasure, or
rollback of an effect that escaped the runtime. Append-only evidence
intentionally preserves the historical fact of an attempted rolled-back
operation.

## Neural and semantic truth boundary

Trusted neural origin and relevance attestations remain explicit trust roots.
The verifiers can check their encoded structure, binding, and lifecycle. They
cannot prove that an attestation is true, that a neural proposal is relevant or
world-grounded, or that a system is conscious, self-aware, intentional, or
generally intelligent.

The Discovery Bridge result applies only to its explicitly finite packaged
worlds. It does not establish open-world operator discovery, universal
algebraic laws, semantic understanding, or general intelligence.

## Numerical boundary

The numerical evidence concerns finite NumPy computations under the declared
profile and tolerances. It does not establish exact real-number algebra beyond
that profile. The numerical verifier is independent of `OSLRuntime` control
flow but shares NumPy and the host floating-point environment.

## Information-flow and session boundary

Passing explicit provenance and metadata checks does not prove universal
noninterference. Timing, termination, resource usage, caches, latent
representations, model weights, prompts, filesystems, networks, tools, and
other covert or implicit channels are outside the general claim.

Session verification covers declared finite synchronous graphs. It does not
prove fairness or liveness for asynchronous or lossy networks, recursive
protocols, dynamic participants, Byzantine behavior, or external schedulers.

## Compatibility and legacy evidence

The frozen OSL v0.5 / Core 0.3 artifacts and the separate Core 0.4 release
retain only their originally stated assurance. Core 0.5 does not rewrite or
retroactively upgrade them. Source-level outcome compatibility does not make a
Core 0.4 receipt a Core 0.5 receipt; the version field and resulting digest
chain differ.

## Reporting discipline

Every release-level statement should identify:

1. runtime and verifier version;
2. receipt and evidence profile;
3. exact corpus, test set, or finite model;
4. passed, failed, skipped, and not-run counts;
5. relevant generated report and trace-bundle digest;
6. remaining delegated semantics and trusted assumptions.

Use `verified` only with a named verifier and finite scope. Use `exhaustive`
only when the complete declared finite state space was enumerated. Do not use
`authenticated`, `formally proved`, `universally safe`, `causal`, `emergent`,
or similar stronger language unless a separate result establishes it.

If an artifact is stale, partially regenerated, inconsistent with the
manifest, missing a dependency, or associated with a failed or skipped gate,
the correct status is failure or `NOT_RUN`, not an inferred pass.
