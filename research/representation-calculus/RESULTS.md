# Retained results — Representation Calculus v0.4

## Lean: final accepted run

**PASS.** 235 local modules rebuilt cold, 259 expected-outcome tasks. All 202
inherited symbolic certificates now have the generic sharp linear-encoding
minimum endpoint. Accepted inputs were unchanged. The only foundational axioms
are `propext`, `Classical.choice`, and `Quot.sound`. No sorryAx, Lean.ofReduceBool
or additional project axiom was detected.

Two supplementary checks passed: an explicit axiom audit of the three attributed
lemmas missed by the main textual inventory and compilation of a fresh exporter
example. The full library inventory is 6,195 explicit named declarations,
including 3,833 theorem declarations. This is a declaration count, not a count of
independent mathematical discoveries.

The cold main audit recorded 636.966 seconds. This is one execution measurement,
not a speed comparison or performance guarantee. A previous unsplit audit timed
out and is not counted as success. The final run uses separate, fresh local
build outputs and exact accepted hashes.

## Python: independent exact audit

**PASS.** Every one of the 202 frozen source/certificate pairs was independently
checked and identically rediscovered. The unchanged matrix bodies were compared
against deterministic exporter output, and new optimality text was checked for
source/prime/precision binding. All factors are nonzero; 17 cases have zero rows,
55 have at least one torsion factor, and in 21 cases the pure cardinality lower
bound is strictly weaker than the certified generator count.

| Check | Count |
|---|---:|
| independent matrix certificate | 202 |
| exact frozen rediscovery | 202 |
| unchanged matrix bodies module headers only | 202 |
| all factors nonzero | 202 |
| minimum export contains universal application | 202 |
| minimum export prime precision binding | 202 |
| every one row linear encoder excluded | 256 |
| nonlinear one residue exact observations | 256 |
| nonlinear quotient has four states | 1 |
| nonlinear pack not additive | 1 |
| cardinality lower never exceeds generator count | 90 |
| corrupted minimum exports rejected | 6 |
| unchanged discovery and checker source | 4 |

The exhaustive Z/16 example checks all 256 possible one-row linear encoders and
all 256 source states under the one-residue nonlinear parity packing. These are
finite independent checks, not the proof of the universal lower bound. The latter
is in Lean. No source state enumeration is used by the generic minimum theorem.

## Preservation and input interpretation

The original v0.3 archive is retained byte-for-byte. All 202 JSON source and
certificate pairs, and the discoverer/Smith/checker source, are unchanged. The
213 parent Lean mathematical bodies are unchanged; their module headers are
explicitly migrated for Mathlib integration. Three previously proved p-adic
module-generator files are included and recompiled. This is not a replay of the
whole p-adic corpus.

The complete cold run, inputs, commands and compiler exit codes are retained in
`evidence/LEAN_EXECUTION.json`. Additional checks have their own record in
`evidence/SUPPLEMENTAL_AUDIT.json`. The v2 Lean and Python evidence manifests pass
hash validation. The final fresh-extraction replay has a separate scope: full
Python audit plus selected cold Lean core/large/torsion/exporter checks. It is NOT
claimed as a second full 202-instance rebuild.

## Interpretation

The result is exact minimum coordinates for linear initial encodings preserving
all states and all future words. Target dynamics may be nonlinear in the lower
bound; the attained upper-bound machine is linear. Nonlinear initial encodings,
single-seed machines, bit encodings, and arbitrary programs have different contracts.
Python executable correctness, learned discovery, empirical superiority, external
refereeing and historical novelty remain separate questions.
