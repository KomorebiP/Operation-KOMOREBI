# Artifact format and supported proof fragment

## Target manifest

Exactly these fields are accepted:

```json
{"schema":"avoc-proposition-1","task":"identity","statement":["imp",["atom",0],["atom",0]],"dependencies":[]}
```

Task names are nonempty ASCII identifiers matching `[A-Za-z0-9][A-Za-z0-9_.-]{0,79}`. Dependencies are an ordered duplicate-free list of already-admitted task names. Self dependencies are rejected.

The target's exact UTF-8 text, including whitespace, is part of the ticket. Equivalent text with different bytes deliberately requires re-registration.

## Formulas

| JSON | Meaning |
|---|---|
| `["atom", n]` | Proposition indexed by nonnegative integer n |
| `["true"]` | Truth |
| `["false"]` | Falsity |
| `["and", F, G]` | Conjunction |
| `["or", F, G]` | Disjunction |
| `["imp", F, G]` | Implication |

## Proof candidate

The candidate file contains only a proof array. For identity:

```json
["intro",["atom",0],["hyp",["atom",0]]]
```

| Proof data | Rule |
|---|---|
| `["hyp", F]` | Use F when F is present in the current context |
| `["true"]` | Prove truth |
| `["pair", p, q]` | Conjunction introduction |
| `["fst", p]`, `["snd", p]` | Conjunction elimination |
| `["intro", F, p]` | Prove the body p under additional premise F |
| `["mp", p, q]` | Implication elimination; q must prove p's exact antecedent |
| `["left", G, p]` | From p proving F, infer F or G |
| `["right", F, p]` | From p proving G, infer F or G |
| `["cases", p, q, r]` | Disjunction elimination; both branch conclusions must agree |
| `["absurd", F, p]` | Infer F only when p proves falsity |

No other constructors, candidate-supplied imports, tactics, macros or source-code commands are supported.

## Persistent identities

A registered ticket carries schema, generation, target/candidate paths, exact target/candidate text, complete admitted dependency snapshots and environment descriptor. Paths are provenance labels, not a replacement for bytes. A receipt carries schema, the complete subject ticket and an approved Boolean. The authority for admission is current rechecking, not the Boolean or authorship of this JSON.

`state.json` contains a next-generation counter, at most one pending ticket, admitted records keyed by task and a local event list. The example intentionally uses a single pending slot. Registering another task supersedes the previous pending ticket and increments generation.

Dependencies preserve their admitted immutable versions. If the directly referenced admitted dependency version changes after registration, admission rejects that ticket and requires re-registration. Older embedded transitive certificates remain exact snapshots and are rechecked; this is not global proof-graph invalidation or a declaration that old mathematical proofs became false.

## Bounds

The Python adapter requires valid UTF-8 and strict JSON without duplicate object keys or non-finite numeric tokens. It limits a candidate, target, checker request and stored state to 1 MiB each. Formula depth must be below 64, proof depth below 128, proof nodes at most 10,000, atom indices at most 1,000,000, dependencies at most 64 per target, and dependency traversal depth at most 16. The Lean proof-data parsers have corresponding formula/proof depth fuel. The single-request checker uses a 20-second inner timeout.

Malformed, oversized, timed-out, wrong-version and setup-failure requests do not count as proof acceptance. The prototype copies full snapshots and may hit the small store limit quickly; scalable content-addressed storage is a later engineering extension.
