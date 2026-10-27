# Proof ledger — v0.37

The new result supplies an effective resonant criterion in the scalar unit
sector. It does not replace or relax any boundary of the v0.36 parent.

| Block | Status | Evidence |
| --- | --- | --- |
| Exact scalar polynomial norm scaling | Checked | EffectivePadicHensel.lean |
| Exact small-ball Hensel image | Checked | EffectivePadicHensel.lean |
| Congruence and derivative-valuation translation | Checked | Both scalar modules |
| Explicit uniform scalar horizon | Checked | ResonantScalarHorizon.lean |
| Deep-fibre uniqueness and existence-only criterion | Checked | ResonantScalarHorizon.lean |
| Computed horizon iff all-depth occupancy | Checked | ResonantScalarHorizon.lean |
| Fixed diagonal algebra criterion | Checked | DiagonalResonantHorizon.lean |
| Actual invertible p-adic matrix consequence | Checked | DiagonalResonantHorizon.lean |
| Positive and dying-prefix controls | Checked | EffectiveResonanceControls.lean |
| General noncommutative matrix effective criterion | Open | RESEARCH_BOUNDARY.md |
| Global arithmetic and automorphic obligations | Open | Inherited boundaries preserved |

The accepted fresh replay checks four source modules, 25 theorem declarations,
one definition, and an axiom audit covering all 26 named constants. It uses
Lean 4.34.0-rc2 with warnings as errors and the pinned Mathlib cache. Axiom
dependencies are confined to propext, Classical.choice, and Quot.sound.
There are no active sorry/admit markers, custom axioms, custom opaque declarations,
native_decide calls, or unsafe declarations in the new source modules.

The exact-arithmetic run checked 51 parameter families at p=2,3,5. It enumerated
21,378 finite unit candidates, compared 214,188 target-prefix combinations between
the horizon and two further levels, compared 22,218 finite certificate decisions
against independent full-residue enumeration, and checked 3,892 digit-lifting
steps. See checks/contract.json and computations/exact_horizons/results.json for
the exact ranges. The higher digit runs are deterministic examples. These finite
tests supplement, and do not establish, the universal mathematical statements.

The parent archive is SHA-256 authenticated and its payload hash manifest is
checked. Its old Lean closure is not freshly replayed here. The new scalar proof
uses Mathlib directly and does not import project modules from that archive.
This is not an independent-kernel or all-historical verification.
