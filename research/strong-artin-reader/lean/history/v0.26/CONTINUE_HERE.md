# Continue from v0.26 — representation obstruction, not a comparison interface

Read `README.md`, `RESEARCH_BOUNDARY.md`, `PROOF_LEDGER.md`, and the inherited audit before extending the work.

## Base and branch

Use this uniquely named v0.26 branch, with exact embedded base:

```text
Strong_Artin_Lean_v0.25.0_Graded_Compatibility_Lifting_Checked.zip
cf9669502a2cfa332e4c6d9da5b40d51f98b226e2099a5593017287cfdbb492c
```

Do not substitute the sibling SquareZero Syzygy v0.25 archive, and do not sum sibling counts as if they were one replayed library.

## Strongest checked theorem

For a surjective square-zero ring map and an actual unit or matrix representation:

```text
set-theoretic unit lifts exist
  -> actual coefficient action on the kernel
  -> actual normalized defect is a Mathlib 2-cocycle
  -> class independent of section
  -> original representation lifts iff the class is zero
```

For a prescribed subgroup lift, the primitive must vanish on that subgroup; an explicit relative cochain quotient provides the corresponding exact criterion. The negative control proves this condition is not redundant.

## Next meaningful work

The natural follow-on is continuity plus genuine local constraints, not another assumed isomorphism between a convenient algebraic space and dual Selmer.

Choose a precise arithmetic case and specify the coefficient extension, topology, representation, prescribed restriction/local conditions, and gauge equivalence. Construct the normalized defect as a continuous cocycle. Establish the correct continuous/relative obstruction class and show its vanishing in that case. A result of the form `if this obstruction vanishes, a lift exists` is already proved algebraically here; merely restating it under a new name adds no vanishing theorem.

A useful narrowly scoped intermediate task is continuity-preserving section and correction construction for finite discrete coefficient extensions and profinite G. Any extension to complete coefficients needs separate limiting arguments.

## Replay

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Preserve warnings-as-errors, the source hashes, and the absence of proof escapes. A partial resumed run remains `PARTIAL` until every module and the 87-constant axiom audit has passed.
