# Komorebi Transport Geometry Lean Project

**Version:** 0.3.0  
**Toolchain:** `leanprover/lean4:v4.34.0-rc2`

This project is dependency-free apart from Lean's bundled `Std` library.

## Build

```bash
lake build
```

## Full Block 03 verification

From the bundle root:

```bash
python verification/verify_block03.py --clean
```

When Lean and Lake are not on `PATH`, set their exact executable paths:

```bash
LEAN_BIN=/path/to/lean \
LAKE_BIN=/path/to/lake \
python verification/verify_block03.py --clean
```

The verifier performs a clean Lake build, elaborates every Lean source with
warnings treated as errors, scans for prohibited proof placeholders and axiom
declarations, checks the required Block 03 interface, compares the preserved
Block 02 core hashes, and writes
`verification/block03_final/verification.json`.

## Core modules

- `KTG.Basic`: typed contexts and dependency-free `KPreorder`.
- `KTG.Transport`: common-carrier transport and structural relatedness.
- `KTG.Certification`: realization certificates and obstruction control.
- `KTG.Coricity`: invariance predicates.
- `KTG.Hull`: closure and enclosure operators.
- `KTG.Observable`: monotone scalar observables.
- `KTG.Witness`: measurement witnesses and hull witnesses.
- `KTG.Normalization`: typed normalization and grade-space bridges.
- `KTG.CertifiedBound`: witness bridge and generic certified bound.
- `KTG.Countermodels`: finite logical non-implication models.
- `KTG.Examples`: positive generic full-pipeline model.
- `KTG.Curvature`: relational path flatness and curvature witnesses.
- `KTG.SafeAbstraction`: safe factorization through public abstractions.
- `KTG.IUT312Model`: non-circular Block 02 interface for the audited hinge.

## Block 03 source-faithful modules

- `KTG.IUT312Types`: distinct IUT-shaped object and measurement types.
- `KTG.IUT312Certificates`: IPL, SHE, APT, and obstruction-control interfaces.
- `KTG.IUT312Normalization`: determinant/procession grades and grade bridge.
- `KTG.IUT312WitnessObligation`: exact open Step (xi-e) witness theorem.
- `KTG.IUT312SourceCountermodel`: all pre-witness fields without containment.
- `KTG.IUT312Cor312Bridge`: refinement of the abstract Corollary 3.12 interface.
- `KTG.IUT312SourceExample`: positive finite equality-model realization.

## Claim boundary

The project verifies the formal interface, countermodel, and finite positive
example. It does not formalize all of IUT and does not prove or disprove IUT III
Corollary 3.12. The IUT-specific inhabitant of
`IUT312.SourceWitnessTheorem` remains open.
