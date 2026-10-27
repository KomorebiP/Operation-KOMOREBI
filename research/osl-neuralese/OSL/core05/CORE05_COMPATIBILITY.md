# OSL-Core 0.5 Compatibility

## Compatibility statement

OSL-Core 0.5 is a separate executable development release derived from the
Core 0.4 receipt-hardened grammar and runtime. It preserves the packaged
66-program behavioral matrix:

- 42 programs are accepted;
- 24 programs reach their declared safe rejection;
- all 66 programs pass the Core 0.5 conformance and semantic aggregate;
- the native traces contain 1,825 receipts.

This is source-corpus and outcome compatibility. It is not byte-for-byte
receipt compatibility and does not alter the frozen Operator Symbolic AI
Language v0.5 / OSL-Core 0.3 package.

## Version relationships

| Artifact | Role | Core 0.5 treatment |
|---|---|---|
| Operator Symbolic AI Language v0.5 / OSL-Core 0.3 | Frozen canonical package | Unchanged; retains original assurance only |
| OSL-Core 0.4 Receipt Hardening | Separate receipt-hardening release | Unchanged; not relabeled as Core 0.5 |
| OSL-Core 0.5 Semantic Independence | Current development release | Native `core_version = 0.5` evidence and new semantic reports |

Core 0.5 retains receipt schema `osl.core.receipt.v2`, but every native receipt
sets `core_version` to `0.5`. Because the version is hashed, Core 0.4 and Core
0.5 receipt chains differ even when source-level behavior is the same. A Core
0.4 trace must not be presented as native Core 0.5 evidence by renaming or
rehashing it.

## Preserved language behavior

For the packaged corpus, Core 0.5 preserves:

- line-oriented source structure and statement manifests;
- parse, static, statement, finalization, completion, and rejection lifecycle
  shapes;
- global contiguous effect spans;
- packet, proof, capability, memory, action, contract, session, metadata, and
  transaction source constructs;
- the 42/24 accepted/rejected outcome matrix;
- the three-program Discovery Bridge behavior, now recorded as 3/3 programs
  with 71 Core 0.5 receipts.

Same-runtime replay remains available as a compatibility and determinism
signal. It is reported separately from the independent semantic components.

## Intentional source hardening

Core 0.5 rejects several programs whose behavior was previously unspecified,
ill-defined, or insufficiently constrained:

- unknown operator kinds;
- a `transport` result that overwrites an existing operator;
- duplicate secret names;
- duplicate metadata names;
- inference confidence that is nonfinite or outside `[0,1]`;
- malformed, nonnumeric, ragged, dimension-incompatible, or nonfinite vector
  and matrix input;
- a projector that is not a square endomorphism;
- a projector check applied to a non-endomorphism;
- negative or nonfinite projector/intertwiner tolerance;
- a numerical operation that produces a nonfinite result or residual.

These are deliberate fail-closed changes. They preserve all packaged corpus
outcomes but can reject external programs that relied on the former gaps.

Malformed or nonfinite literal failures are normalized into auditable parse or
static rejection paths where applicable rather than propagating raw NumPy or
Python exceptions.

## Semantic verifier compatibility

Core 0.5 adds the aggregate entry point
`reference/osl_semantic_kernel.py`. Its component reports cover:

- numerical/operator state;
- temporal contracts;
- finite session protocols;
- metadata-facing state and assertion accounting;
- audit-prefix intrinsics.

The components verify supplied source and receipt-v2 evidence without invoking
`OSLRuntime`. The numeric, contract, and session components parse their bounded
source fragments separately. The metadata and intrinsic components use the
primary parser, and the receipt-hardened base kernel uses the primary parser
and static checker. Therefore Core 0.5 does not claim a wholly independent
frontend.

## Transaction compatibility

The primary runtime retains Core 0.4 transaction behavior:

- application state and raw secrets are checkpointed;
- explicit or automatic rollback restores modeled application state;
- statement step, append-only audit evidence, and diagnostic events remain
  monotone;
- external `execute` remains forbidden in a rollbackable transaction.

Core 0.5 components additionally reconstruct rollback of their own domain
tables. They do not yet form a second complete cross-domain state machine that
recomputes every transaction projection digest. No stronger compatibility or
atomicity claim should be inferred.

## Evidence compatibility

The Core 0.5 observed gates are:

| Gate | Result |
|---|---:|
| Full tests | 168/168 |
| Focused tests | 75/75 |
| Corpus | 66/66 |
| Native receipts | 1,825 |
| Discovery Bridge | 3/3 programs, 71 receipts |

The fixed focused suite is finite and is not an exhaustive compatibility
proof. External users should rerun their own sources under Core 0.5 and inspect
any newly surfaced parse, static, or numerical rejection.

Compatibility does not close the Core 0.5 claim boundary. General assertion
truth, out-of-domain rejection causality, diagnostic `event_count`, and the
exact complete cross-domain transaction projection remain outside independent
reconstruction. Some verifier paths share primary frontend components;
Python/NumPy remain trusted; SHA-256 supplies no principal identity; symbolic
capabilities supply no OS sandbox; and neural attestations remain trust roots.

## Migration checklist

For a Core 0.4 source moving to Core 0.5:

1. use only the four declared operator kinds;
2. give every space, vector, operator, transport result, secret, and metadata
   declaration a noncolliding name;
3. keep confidence and numerical literals finite;
4. match vector length and matrix shape to declared spaces;
5. use projectors only as square endomorphisms;
6. use finite nonnegative numerical tolerances;
7. regenerate receipts under the Core 0.5 runtime;
8. run both the receipt-hardened base verifier and Core 0.5 semantic aggregate;
9. retain the evidence version in every report and downstream claim.

Do not merge, relabel, or compare receipt digests across versions as if they
were interchangeable.
