# Trace exchange contract — version 1

Publication 1.8.0 / Python 1.6.0. This format is separate from the named
proof-field JSON schema and the older minimum-certificate representation.

## Two fixed schemas

A problem is exactly six array elements:

```json
["proof-path/problem/1",4,[0],[[[0],1],[[1],2]],[],[3]]
```

These are tag, node count, admitted leaves, indexed rule rows, positive nodes,
and forbidden nodes. A rule row is `[premises, conclusion]`. Rule addresses are
zero-based list positions. Identical rows at different positions retain different
addresses. Lists of node entries are individually duplicate free, but leaf,
positive, and forbidden sets may overlap. Every node lies below the node count.
An empty address space is allowed when all node-bearing data are empty.

A result is exactly five elements:

```json
["proof-path/certificate/1",true,[0,1,2],[0,1],null]
```

These are tag, feasibility Boolean, reported closure, complete strict trace,
and optional obstruction. An obstruction is `[forbidden_target, causal_trace]`.
Changing the problem's final `[3]` to `[2]` requires this negative result:

```json
["proof-path/certificate/1",false,[0,1,2],[0,1],[2,[0,1]]]
```

The checker accepts the problem separately. The result cannot redefine the
rules, leaves, or protected observations. Authentication that the supplied
problem is the user's intended request is an external input-provenance task.

## Replay and result meaning

Replay starts with the admitted leaves and positive observations. It rejects an
unknown rule index or a missing premise. Strict replay rejects already-known
conclusions, while causal witness replay permits them. The complete checker
requires the reported closure to equal the replayed membership set and be closed
under **every** declared rule. This proves equality with the least seeded model,
not merely that some model was returned.

A positive result has no obstruction and its closure avoids forbidden nodes.
A negative result contains an accepted causal trace to a forbidden node. Both
complete-result branches certify the entire closure. A bare negative witness
has a separate checker and need not carry a complete closure. Rejection of
malformed or incomplete evidence is never interpreted as infeasibility.

## Canonical bytes

Standalone files use compact ASCII JSON, with an optional final LF. Inputs use
exact nonnegative integer tokens, literal `true`/`false`, `null`, strings for
version tags, and arrays. Objects, decimal/exponent spellings, negative numbers,
extra fields, and internal formatting whitespace are rejected. `true` is not
node `1`; `"false"` is not a Boolean. The Python interface has a default 4 MiB
per-file bound. Resource rejection has no mathematical meaning.

The Lean batch IO adapter reads nonempty NDJSON lines, each containing the exact
pair `[problem,certificate]`, with a separate 8 MiB line limit. It compares parsed
records with their canonical reencoding before running the proved checker.
Parser, printer, allocation and file-IO behavior are tested, not formally proved.

## Execute the two implementations

```bash
proof-path wire-export examples/and_dag.json --negative B --output-prefix trial
proof-path wire-check trial.problem.json trial.certificate.json
python scripts/check_trace_exchange.py
python scripts/verify_lean.py --runtime /path/to/portable-kit
```

The first command emits `.problem.json`, `.certificate.json`, and `.binding.json`.
The binding lists the original node/rule names at their assigned addresses.
Check it against the intended `ProofFieldViews` snapshot. Export requires both
the named result checker and the independent indexed checker to accept.

The formal verifier rebuilds 18 modules into a fresh object directory and runs
`formal/CheckTraceJson.lean` on `data/trace_exchange_cases.ndjson`. It compares
all returned verdicts with `data/trace_exchange_expected.txt` and records the
input, expected output, actual output, and source hashes.

## What is proved and what is tested

`Trace.replay_sound`, `checkClosure_exact`, `witness_exists_iff_infeasible`, and
`certificate_decides_feasibility` are general Lean theorems about the executable
checker and the existing field semantics. `Trace.Wire.problem_roundtrip` and
`certificate_roundtrip` prove left inverses on the typed `Json` syntax tree.
`json_acceptance_sound` yields the exact mathematical answer for the decoded
records. `valid_closure_bounded` excludes derived nodes outside the address space.

Six real indexed exchanges also generate kernel-checked example declarations.
The 83,994-case batch covers every stated small model family, selected alterations,
and malformed records. It does not prove arbitrary-input correctness of the
Python implementation, the name-to-index adapter, or the standard text parser.
Witness completeness does not certify the Python producer or shortest proofs.
