# Komorebi Lean verification report

Author: Komorebi P.  
Release: v0.2.0  
Verification date: 2026-09-02

## Outcome

The recovered `ProjectorCore.lean` v1.2.2 compiles unchanged under Lean
4.34.0-rc2 and the Mathlib dependency graph locked by `lake-manifest.json`.
The verification tranche also adds a non-circular exact-coordinate theorem and
an independently defined fibre-refinement theorem, together with concrete
rational-coordinate smoke tests.

| Result | Lean declaration | Status | What supplies the conclusion |
|---|---|---:|---|
| Exact packet-coordinate equivalence | `LinearProjectorFamily.exactPacketCoordinates` | Kernel accepted | completeness, idempotence, orthogonality; packet space is the explicit product of projector ranges |
| Synthesis after analysis | `rangeSynthesis_rangeAnalysis` | Kernel accepted | completeness |
| Analysis after synthesis | `rangeAnalysis_rangeSynthesis` | Kernel accepted | packet range witnesses, idempotence, orthogonality |
| Concrete fibre family | `fibreLinearProjectorFamily` | Kernel accepted | pointwise equality masks |
| Exact nested fibre refinement | `fibreLinearProj_refinement` | Kernel accepted | independent coarse and fine masks plus the address map |
| Exact modular-residue refinement | `Residue.residueProj_refinement` | Kernel accepted | independent modulo-`N` and modulo-`N*M` masks plus the modular identity |
| Transfer-block reconstruction | `transferBlock_reconstruction` | Kernel accepted | completeness of source and target families |
| Transfer-block composition | `transferBlock_comp` | Kernel accepted | completeness of the middle family |
| Transitive support is multiplicatively closed | `MatrixSupported.mul` | Kernel accepted | transitivity of the support relation |
| Weighted difference of a geometric mode | `iteratedWeightedDiff_geometric` | Kernel accepted | induction and commutative-ring algebra |
| Polyphase section composition | `coeffSection_comp` | Kernel accepted | arithmetic reindexing |

The concrete audit specializes the family to `Fin 4 → ℚ`.  It checks both
coordinate inverse laws, parity refinement from four fine coordinates to two
coarse lanes, and exact reconstruction of an arbitrary linear operator from
all sixteen coordinate blocks.

The residue specialization proves, for `N,M > 0`, that the coefficient mask
selecting residue `r` modulo `N` equals the sum of exactly those independently
defined masks modulo `N*M` whose residue reduces to `r` modulo `N`.

## Circularity audit

The old unrestricted synthesis/analysis identity proves only synthesis after
analysis and is a direct restatement of the family's completeness field.  It
cannot justify analysis after synthesis for arbitrary values in `ι → M`.

`ExactCoordinates.lean` repairs this precisely:

1. `PacketSpace P` is independently defined as
   `(i : ι) → LinearMap.range (P.proj i)`.
2. `rangeAnalysis` applies each projector and carries its range certificate.
3. `rangeSynthesis` is the ordinary finite sum of packet values.
4. The reverse inverse law is then proved using idempotence on the selected
   range and annihilation of every other range.

Likewise, the refinement theorem defines the fine and coarse masks separately;
the coarse mask is not defined to be the desired fine sum.

## Kernel and axiom audit

Commands:

```bash
lake build
lake env lean KomorebiVerification/KernelAudit.lean
```

Both commands exit successfully.  `#print axioms` reports no project axiom and
no `sorryAx`.  Depending on the declaration, the only reported foundations are
the standard Lean/Mathlib principles `propext`, `Classical.choice`, and
`Quot.sound`.  The polyphase composition theorem reports only `propext`; the
weighted-difference theorem reports `propext` and `Quot.sound`.

The final clean project build completed all 8,872 jobs successfully.

The recovered core has SHA-256:

```text
41775abb0c089d315b4afd8815b04122d19c1be1c256b50be89b6e88bdfcff17
```

The only compiler diagnostic is a non-fatal style linter suggesting `simp`
instead of `simpa` at legacy-core line 549.

## Scope boundary

This verifies the declarations imported by this project.  It does not verify
all 594 records in the companion claim catalogue, every file counted in the
earlier 60-file static audit, the full categorical lane-transport theorem, the
factorial/hypergeometric realization, global universality assertions, or any
claim of historical novelty.  Catalogue metadata and numerical regression
tests remain evidence of a different kind and are not Lean proofs.
