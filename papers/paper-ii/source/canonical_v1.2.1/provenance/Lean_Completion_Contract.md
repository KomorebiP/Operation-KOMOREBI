# Lean Completion Contract

## Frozen denominator

Paper II v1.2.1 counts exactly 25 items:

1. the 21 numbered definitions, propositions, theorems, and corollaries in the
   main text;
2. the Smith two-phase identity labelled `eq:smith-inversion`; and
3. the three algorithmic forms labelled `alg:residue`,
   `alg:weighted-inverse`, and `alg:path-zeta`.

The authoritative item-to-declaration map is
`formalization/lean/LEAN_THEOREM_MAP_v1.1.1.md`. An item may map to several
declarations when the manuscript result is composite, and several items may
reuse a declaration when an algorithm is the executable form of a theorem.

## Acceptance conditions

Completion requires all of the following:

- every one of the 25 items has a compiled Lean target;
- the theorem-map checker resolves every mapped declaration, the aggregate
  Lake target compiles, and `PaperII/KernelAudit.lean` completes;
- the fail-closed audit traverses every compiled `Komorebi.*` declaration and
  finds no `sorryAx`, project-specific axiom dependency, or unsafe declaration;
- theorem assumptions match or strengthen the manuscript’s revised explicit
  hypotheses; and
- certificate-taking theorems are described as verification of supplied data,
  not as automatic construction of those data.

In particular, item 18 is the concrete diagonal result over `ZMod (p^L)`,
with the fibre base and residue cardinality both equal to `p`. The analogous
arbitrary-DVR formula with residue-field cardinality `q` belongs to the
certificate-explicit extension and is not counted as an automatically derived
general-DVR theorem.

## Boundary

This is contract completeness, not a claim that every sentence, motivation,
classical background theorem, numerical example, or bibliographic assertion
has been formalized. Lean kernel acceptance does not establish novelty,
historical priority, publication readiness, or independent peer review.
