# Paper III Lean Formalization

This Lean 4 project verifies the finite algebraic completion contract for
*Projector-Resolved Seed Calculus III* by Komorebi P.

## Pinned environment

- Lean: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib revision: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Paper III formalization version: `1.0.1`
- Warnings are errors through `moreLeanArgs = ["-E", "warning"]`.

## Current release entry point

The default Lake target is now `PaperIIIContinuation`, including the Section 16
coordinate results and the Section 17 multilinear, continuous range-jet, and
partition composition/support modules. See
[README_CONTINUATION.md](README_CONTINUATION.md) for fresh acceptance and replay
commands and the current
[FINAL_VERIFICATION_SUMMARY.json](verification/FINAL_VERIFICATION_SUMMARY.json)
for accepted results. The metrics below refer to the preserved finite predecessor
only.

## Preserved finite-predecessor build and audit

The historical commands below belong to the preserved source directory
`checkpoint_v0.3.0/baseline/source/finite/formalization/lean/`, relative to the
release root. They describe reproduction of that finite predecessor. From the
release root, their original working directory and commands are:

```bash
cd checkpoint_v0.3.0/baseline/source/finite/formalization/lean
lake --wfail build
python3 scripts/verify_theorem_map.py
lake env lean -E warning KomorebiPaperIII/KernelAudit.lean
```

The executable theorem-map gate checks row numbering, declaration uniqueness,
compiled declaration kinds, manuscript status references, and explicit audit
coverage. `KernelAudit.lean` then prints the transitive axioms of every audited
target and scans the entire compiled `Komorebi.PaperIII` namespace. The audit
rejects project axioms, opaque or unsafe declarations, `sorryAx`, and any
transitive axiom outside `propext`, `Classical.choice`, and `Quot.sound`.

Historical finite-predecessor metrics:

- theorem-map rows: `41`
- unique mapped declarations: `143`
- mapped theorem declarations: `88`
- mapped constructions: `55`
- supporting-only audit declarations: `0`
- unique explicit kernel-audit targets: `143`
- Paper III manuscript status invocations/references: `42 / 99`
- inherited manuscript status invocations/references/unique targets: `6 / 14 / 12`
- fail-closed namespace declarations/theoremInfo declarations: `468 / 229`
- clean aggregate build jobs: `3076`

## Modules

- `EdgeOperators.lean` — packet graphs, elementary edge matrices, broken-word
  vanishing, and finite word/walk expansions.
- `EdgeExtensions.lean` — endpoint collapse, coefficient-level walk sums,
  reachability support, and heterogeneous finite packet paths.
- `Transport.lean` — exact frames, canonical transport, a minimal independent
  connection API, and the concrete nontrivial three-point example.
- `CoordinateNaturality.lean` — exact coordinate maps, composition, cocycle,
  triangle, and naturality laws.
- `ReversibleConnections.lean` — reversible fiberwise connections, additive
  defect, flatness, path transport, gauge action, canonical reconstruction,
  and packet-resolution primitives.
- `HolonomyBlocks.lean` — packet-resolved obstruction detection and its
  gauge-covariant block form.
- `NonlinearObstructions.lean` — unary/binary operation-tree locality and
  candidate-specific obstruction certificates.
- `KernelAudit.lean` — explicit axiom reports plus the fail-closed namespace
  gate.
- `scripts/verify_theorem_map.py` — executable manuscript/map/environment/audit
  parity check.

The finite predecessor's contract is
`LEAN_THEOREM_MAP_v1.0.1.md`, read together with
`INHERITED_DEPENDENCY_MANIFEST_v1.2.1.md` in that preserved Lean source directory,
and the preserved
[Lean completion contract](../checkpoint_v0.3.0/baseline/source/finite/provenance/Lean_Completion_Contract.md).
The inherited manifest pins the
separately verified Papers I--II v1.2.1 bundle at SHA-256
`a20cf9353f0e882834d31e665dfd819a04e43fa606d402309be63e3b94447052`;
those declarations are cited but not recompiled by this standalone project.
The preserved finite predecessor omitted build outputs. The current release
retains owned generated objects; the compiler and upstream dependency caches
remain excluded. Lake resolves the exact pinned dependency revisions from
`lake-manifest.json`.
