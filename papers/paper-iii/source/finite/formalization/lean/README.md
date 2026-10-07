# Paper III Lean Formalization

This Lean 4 project verifies the finite algebraic completion contract for
*Projector-Resolved Seed Calculus III* by Komorebi P.

## Pinned environment

- Lean: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib revision: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Paper III formalization version: `1.0.1`
- Warnings are errors through `moreLeanArgs = ["-E", "warning"]`.

## Build and audit

Run from this directory:

```bash
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

Final verified metrics:

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

The authoritative contract is `LEAN_THEOREM_MAP_v1.0.1.md`, read together with
`INHERITED_DEPENDENCY_MANIFEST_v1.2.1.md` and
`../../provenance/Lean_Completion_Contract.md`. The inherited manifest pins the
separately verified Papers I--II v1.2.1 bundle at SHA-256
`a20cf9353f0e882834d31e665dfd819a04e43fa606d402309be63e3b94447052`;
those declarations are cited but not recompiled by this standalone project.
Build outputs and
`.lake/packages` are deliberately not bundled; Lake resolves the exact pinned
dependency revision from `lake-manifest.json`.
