# Exact coverage — Model-Theory Normalization v0.4

## Completed cold build

PASS: 23 local modules, 30 expected-outcome tasks,
443 explicit named declarations, all axiom-audited.
Counts: {"def": 192, "theorem": 227, "abbrev": 12, "structure": 5, "instance": 1, "inductive": 6}.
The 11 new modules contain {"def": 117, "theorem": 119, "abbrev": 5, "structure": 1, "inductive": 1}.
Six generic modules contribute {"def": 13, "theorem": 44, "abbrev": 1, "structure": 1, "inductive": 1}; the other
new sources are one concrete-reference module and four generated queue traces.
Generated equations and helper lemmas are not independent discoveries.

Only `propext`, `Classical.choice`, `Quot.sound` occur. No custom project axiom,
`sorryAx`, or `Lean.ofReduceBool`. All proof sources are checked with warnings as
errors. Five negative controls reject for mathematical/type/proof reasons, not
missing files or resource limits. The positive control accepts.

## Accepted proof chain

| Module | Exact scope |
|---|---|
| DiscoveryRank | Actual finite submodule cardinality is a prime power; strict natural rank bounded by rd |
| DiscoveryWorklist | Executable fuelled FIFO algorithm, exact-oracle interface, preserved frontier, both inclusions at empty queue |
| DiscoveryTermination | Decreasing queue/rank potential, universal enough-fuel success, accepted-test and word-horizon bounds |
| DiscoveryFinite | Proved executable finite coefficient-enumeration oracle and concrete total algorithm |
| DiscoveryLogic | Actual matrix-row semantics, generated local logical certificate, actual Mathlib QF/definability endpoint from discovery |
| DiscoveryTrace | Witnessed queue execution, branch evidence, full span and logical formula, exact oracle substitution, successful-output uniqueness, trace/reference equality |
| DiscoveryExamples | Kernel-computed small program results and degenerate/cap cases, plus universal shear behavior/standard formula |
| DiscoveryLargeTrace, DiscoveryDelayTrace, DiscoveryTorsionTrace, DiscoveryZeroTrace | Four literal complete queue traces, their exact reference result, all-word quotient and standard formula |

The prime theorem covers arbitrary natural r,d,k,o including zeros, with prime p.
The computational reference backend enumerates scalar coefficient tuples and can
be exponentially slow. Its mathematical rank is not a runtime cardinality call.
It does not require an unproved membership oracle or assume the final test list.

## Precise limits

The fast Python producer and Smith backend are NOT verified programs. Four actual
fast queue traces are Lean-checked and shown equal to the verified reference
algorithm's output. The other 198 traces are independently checked Python evidence
under the proved trace contract, not newly kernel-checked literal instances.
No source-state enumeration is used by the symbolic trace proofs, including the
2^128-state example. Source transcription is independently tested, not formalized.

The 12 inherited local dependencies are rebuilt. All 222 inherited proof files are
preserved byte-for-byte, but the entire earlier 202-case Lean suite is not rerun.
Upstream pinned Mathlib is reused, not rebuilt. No general minimum number of tests,
minimum formula size, or efficient oracle-complexity theorem is added. All-state
observational semantics remains distinct from single-seed reachability, arbitrary
relational logic, full first-order elementarity and arbitrary algorithms.

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
Mathematical statement/proof review is self-review, not external refereeing.
