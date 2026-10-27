# Lean guide — Proof Path Theory 1.8.0

## Fresh record

The release builds and replays **18 production modules**, auditing **283 explicit
named declarations**, including **169 named theorems**. The 13 earlier modules
are unchanged. Five new modules implement the current continuation. Counts
include helpers and concrete examples and do not assert historical novelty.

| Module | New mathematical role |
|---|---|
| Trace | Executable strict/causal replay; soundness, extensivity, composition; accepted complete closure and protected verdicts. |
| TraceCompleteness | Causal weakening, finite premise-trace assembly, derivation-to-trace existence, complete forbidden-node witnesses. |
| TraceWire | Exact JSON AST codec, general round trips, injectivity, validity checks, decoded-answer soundness, bounded derived addresses. |
| TraceExamples | Checked good and bad records, cycles, empty inputs, duplicate rule rows, malformed types and changed observations. |
| TraceFixtures | Six generated actual exchange pairs with acceptance and semantic theorems. |

The independent IO consumer `formal/CheckTraceJson.lean` is not one of the 18
proved production modules. It uses the standard JSON parser/printer and reads
canonical NDJSON. Its 83,994-case execution has zero mismatches against the
independent finite model oracle. This is byte-level conformance evidence, not
a universal proof of parsing or operating-system behavior.

## Trust inventory

The compiler hash and nine dependency revisions are checked. Source scans
reject proof placeholders and extra trusted production axioms. All recorded
transitive axioms are among `propext`, `Classical.choice`, and `Quot.sound`.
Ten deliberately invalid proof controls must fail for specified proof diagnostics.
An eleventh uses an explicit false axiom: Lean accepts its consequence relative
to that axiom, and the separate axiom policy rejects that dependency.

The record is `evidence/formal_1.8.0/verification.json`. Per-declaration types can
be inspected in the sources; locations, hashes, axiom sets and related claim
groups are indexed by `formal/CONCORDANCE.json`. The new groups are PPT-042–047.

```bash
python scripts/verify_lean.py --runtime /path/to/portable-kit
```

This is Lean's own-kernel replay against pinned cached imports, not a second
kernel implementation or a fresh rebuild of every Mathlib dependency. Original
evidence is retained with its original versions. The older total-output decoder
remains distinct from `ProofPath.Recovery.Sufficient` on attained outputs.

The checker proof does not certify arbitrary Python execution, byte parsers,
source adapters, or the entire monograph. The semantic validity of labels still
requires a sound declared interpretation. Entropy and social models retain
their separate written/conditional scopes.
