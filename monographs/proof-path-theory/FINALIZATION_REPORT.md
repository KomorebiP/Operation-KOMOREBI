# Proof Path Theory — executable trace and exchange release 1.8.0

**Author:** Komorebi P.  
**Date:** 19 October 2026  
**Publication:** 1.8.0  
**Python distribution:** 1.6.0

## 1. Lineage and completed boundary

The working source started from the delivered 1.7.0 archive. All **719** predecessor
manifest entries were verified before editing. Its thirteen production Lean
modules, prior tests, named-field schemas and existing mathematical environments
are preserved. Source identity is recorded in `editorial/baseline_1.7.0.json`.

This continuation formalizes the checker identified in the prior progress ledger.
It does not redefine mathematical validity as whatever a Python routine returns.
The new finite indexed input constructs the existing `Field Nat Nat` semantics,
and accepted traces are related to the existing `Field.closure` and `Extends`.

## 2. What the new theorems establish

### Replay is a proved program

`Trace.replay` is an executable list-based checker. Rule IDs are list positions,
including distinct positions for identical rows. Missing rules or missing premises
cause explicit failure. Strict replay adds only new conclusions; causal replay
permits conclusions already known. The latter supports witness reuse after
positive observations have been strengthened.

Theorems prove that replay preserves the known nodes, introduces only derivable
nodes, and composes by list concatenation with explicit failure propagation.
This is a proof about the implemented Lean recursion, not an assumed replay law.

### Least closure needs both tests

Replay proves every reported node derivable. The final model test proves the
reported set contains every consequence. Their two inclusions yield **exactly
the least seeded model**. A replayed partial derivation may not be saturated;
a closed superset may contain unsupported nodes. Both counterexamples are
kernel-checked and shown in the new visual study.

Accepted complete result certificates carry this exact closure in both branches.
A positive result also proves it avoids the forbidden set. A negative result
includes a valid causal derivation of a specifically forbidden node. The Boolean
flag is proved equivalent to feasibility of that fixed protected request.

### Obstruction witnesses are complete

Every inductive derivation in the finite-premise rule field has a finite causal
trace. Premise traces can be concatenated because replay is monotone under
larger known sets. Thus an accepted forbidden-node witness exists **if and only
if** the protected extension problem is infeasible. No acyclicity assumption is
needed for this checker theorem. Unseeded cycles do not manufacture derivations.

This witness-completeness theorem is not a theorem that a Python producer finds
the shortest witness or that an arbitrary producer implementation is correct.
A bare witness can be checked without a complete closure; the complete result
format asks for both because it promises both kinds of information.

### Typed exchange retains its data

Problem and certificate use different exact-length positional JSON arrays and
separate version tags. All node and rule addresses are exact nonnegative integers.
The AST decoder does not treat a Boolean as an integer or a string as a Boolean.
Bounds and duplicate-node checks are distinct from structural decoding.

The Lean encoders have general proved left inverses on typed records, so they
are injective. Acceptance of actual decoded JSON syntax trees implies the exact
closure/feasibility theorem for that decoded problem. A separate theorem proves
that a valid indexed problem derives no unnamed node outside its address space.

The universal theorem ends at Lean's **Json syntax-tree boundary**. The standard
text parser/printer, IO, Python implementation and named-source address adapter
have executable conformance tests, not newly asserted universal correctness.
A fixed indexed request must still be bound to the intended source snapshot.

## 3. Fresh formal verification

| Check | Result |
|---|---:|
| Production modules compiled in a new object directory | 18 passed |
| Lean own-kernel replays | 18 passed |
| Explicit named declarations in axiom audit | 283 |
| Named theorem declarations, including helpers and examples | 169 |
| Deliberately invalid proof controls | 10 rejected for expected proof diagnostics |
| Explicit extra-axiom control | Accepted relative to its axiom; rejected by the separate axiom policy |
| Actual canonical JSON consumer | 83,994 verdicts; zero mismatches |

The five new modules are `Trace`, `TraceCompleteness`, `TraceWire`,
`TraceExamples`, and `TraceFixtures`. The latter contains six generated concrete
exchange pairs with acceptance and semantic theorems. The independent IO adapter
`CheckTraceJson.lean` is executed but not counted as a universally proved IO module.

The pinned compiler is Lean 4.34.0-rc2 at commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`. Its binary hash and nine dependency
revisions are verified. Allowed foundational axioms remain `propext`,
`Classical.choice`, and `Quot.sound`. The release contains no additional trusted
production axiom or proof placeholder. Cached Mathlib imports are not rebuilt
or replayed as a whole, and Lean's own-kernel replay is not a second independent
kernel implementation.

The full formal record is `evidence/formal_1.8.0/verification.json`.
`formal/CONCORDANCE.json` gives source positions, hashes, axiom sets, and related
claim groups. A named declaration, a concrete example, and a result group are
different inventories and are not counts of historical discoveries.

## 4. Python and cross-language tests

The new module `trace_codec.py` implements typed exchange, canonical bytes,
an independent indexed checker, and adapters from the named proof-field snapshot.
The existing CLI gains `wire-export` and `wire-check`. Prior functions and the
provenance byte format remain unchanged. The named-field checker and indexed
checker must both accept before export succeeds.

| Executed check | Result |
|---|---:|
| Source-package tests | 233 passed, no failures/errors/skips |
| Same suite against separately installed wheel | 233 passed, no failures/errors/skips |
| Named protected problems in trace exchange | 65,536 |
| Lower-level cyclic-capable problems | 16,384 |
| Altered certificates | 2,048 |
| Malformed input records | 26 |
| Total exact serialized conformance cases | 83,994 |
| Accepted positive verdicts | 14,993 |
| Accepted negative verdicts | 67,951 |
| Rejected records/certificates | 1,050 |

The altered-certificate suite deliberately includes both harmless changes and
invalid changes. It does not count every alteration as a mandatory rejection.
The independent oracle enumerates finite rule models and computes their least
seeded intersection. These counts describe the declared small input domains,
not a universal proof of the Python interpreter or parser.

The named 3-node input family is still acyclic. The 2-node arbitrary rule family
is exercised through the new lower-level indexed interface; it does not relax
the old public named-field invariant. Cyclic and empty-input fixtures make that
scope distinction explicit.

Earlier exact checks are rerun: 5,039 binary linear systems, 223,232 node-covering
patch families, 65,536 protected problems and 65,536 staged closures in the
recovery/extension suite, 1,555 finite factorizations, 4,681 decoder-composition
triples, 22,621 joint-task comparisons, 18 certificate-cost comparisons,
100 greedy-bound instances, 1,024 retention identities and 114 covariance cases.
Overlapping domains in separate suites are not presented as distinct discoveries.

## 5. Monograph and visual refinement

The final manuscript is **76 pages**, with **25 numbered vector figures**, one
separate exact cover motif, **six worked visual studies**, and **47 result groups**.
All **149** predecessor mathematical environments are unchanged; **14** new
statement/proof environments add the checker and codec development.

The added chapter section explains the proof of both inclusions, why causal
witnesses differ from strict closure traces, and why typed decoding must be
separated from validation and source interpretation. The figure works through
one explicit chain and two different protected requests. Existing finite
illustration data are unchanged.

The ledger is balanced across three pages, the new corollary is kept with its
proof, and formal reproduction commands are separated from the finite build
instructions. Body text is not reduced to hide layout problems. All final pages
are rendered and inspected, with enlarged review of new theorem, figure, code,
and ledger pages. Figure generation is repeated to check identical PDF/PNG
assets. Final build and structural preflight records are separate from the
mathematical verification record.

## 6. Failures retained and corrected

Early trace proofs needed the current Boolean-lemma interface and explicit
Option/list equalities. The completeness and codec developments needed finite
trace assembly and specialized round-trip lemmas. One example needed an explicit
certificate parameter. Those failed compiler outputs are preserved.

The container's streaming mode was unavailable before command execution. An
initial direct integrated command then exceeded its outer 200-second limit
after all production modules compiled but before all kernel replays completed.
Its partial record is retained. A complete tracked rerun passed all stages.
Neither interruption was labeled a mathematical counterexample or a successful
formal replay.

The first layout exposed a split proof, an end-of-part orphan, and a near-empty
ledger tail. The new exposition was rearranged and the ledger balanced. A source
cross-reference review corrected codec theorem names to the actual compiled
identifiers. These are recorded editorial corrections, not new mathematics.

Development evidence is under `evidence/development_1.8.0/`; complete execution
records are under `evidence/release_1.8.0/`. The final extracted-file manifest and
ZIP coverage check are recorded after packaging, not inferred from ZIP CRC alone.

## 7. Remaining work

The main next task is a general semantic refinement of the **named source to
indexed problem adapter**. Define a finite named-source snapshot in Lean,
construct node/rule address maps, and prove that the indexed request preserves
its leaves, certified rules and positive/negative observations. The byte parser
and IO boundary must remain separately visible. A full producer termination and
output-refinement theorem also remains distinct from witness completeness.

Further obligations include derivation-valued rule transport, native semantic
adapter verification, selected wider manuscript formalizations, independent
mathematical review, empirical testing of the social models and an author-selected
license. No redistribution license or claim of full manuscript formalization
was introduced. Hosted CI, native Windows execution, and every supported Python
version were not run in this Linux verification session.
