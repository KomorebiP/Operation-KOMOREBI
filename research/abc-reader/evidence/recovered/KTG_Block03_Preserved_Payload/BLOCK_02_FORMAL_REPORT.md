# Komorebi Transport Geometry — Block 02 Formal Report

**Release:** v0.2.0  
**Date:** 2026-09-17  
**Status:** dependency-free KTG transport/witness pipeline compiler-verified

## Result

Block 02 turns the first KTG sketch into a checked separation between five
logically different notions:

1. **structural relatedness** of objects in a common transport carrier,
2. **transported realizability** by an application-specific certificate,
3. **obstruction control** for that certificate,
4. **normalization preservation** across typed grade spaces,
5. **measurement-level hull membership**, followed only then by scalar
   monotonicity.

The central application interface is `KTG.KWitnessBridge`.  Its field
`witness_preserved` is the exact theorem that an application must prove before
`KTG.certified_transport_bound` can emit a scalar bound.  No structural word
such as “linked”, “related”, “compatible”, or “simultaneously represented” is
allowed to stand in for that witness.

## Baseline repair

The predecessor claimed to be dependency-free but used the Mathlib-style names
`Set` and `Preorder` while importing only `Std`.  The untouched baseline build
failed for exactly those undeclared dependencies.

Block 02 repairs the mismatch by introducing:

- `KTG.KPreorder`, a small explicit preorder class with notation `≼`;
- predicate-valued transport output instead of an undeclared `Set` alias.

The mathematical intent is unchanged.  The hidden dependency is removed.

## New checked interfaces

### Certified realization

`KTG.KTransportCertification` supplies an application-specific certificate
type, an obstruction extracted from each certificate, a controlled-obstruction
predicate, and a soundness theorem:

```text
certificate + controlled obstruction  ⟹  structural relatedness.
```

`KTG.CertifiedRealization` packages the certificate and its obstruction proof.
The converse implication is intentionally absent.

### Typed normalization composition

`KTG.KGradeBridge` explicitly maps the target grade space of one normalization
to the source grade space of the next.  The theorem
`normalization_composes_through_bridge` proves the composite grade equation only
through that bridge.  This is the formal slot in which changes of units,
multiplicity, tensor degree, or a weighting such as a later `j²` factor must be
represented.

### Witness-preservation bridge

For source context `A`, target context `B`, transport `T`, certification `C`,
normalization `N`, target measurement map `μ`, and hull `H`, a
`KWitnessBridge` contains

```text
rawOutput : A.Obj → B.MeasureObj

witness_preserved :
  CertifiedRealization C a b →
  NormalizationWitness N a b →
  HullWitness B H (μ.measure b) (rawOutput a).
```

This is deliberately stronger than structural relatedness.  Once it is proved,
`CertifiedTransportBound.fromBridge` packages every gate and
`certified_transport_bound` applies the monotone observable.

### Abstract IUT III 3.12 interface

`KTG.Cor312Interface` now separates:

- `structuralLinked`,
- `transportedRealizable`,
- `normalizationPreserved`,
- `hullWitness`,
- `hullWitness_sound`.

`Witness312` is the independent hull-witness proposition.  It is no longer
defined as the desired scalar inequality, which would only rename the
conclusion.  `cor312_scalar_of_witness` derives the scalar order from the
separately supplied witness and its soundness theorem.

## Checked logical separations

Two finite Boolean countermodels are compiler-checked.

1. `structural_relation_does_not_imply_realizability`:
   a universal structural relation can coexist with an empty realization
   certificate type.

2. `prewitness_gates_do_not_imply_hull_witness`:
   structural relatedness, a controlled realization, and a normalization
   witness can all hold while the measurement-level hull witness fails.

The abstract IUT model also proves
`all_prewitness_gates_not_sufficient`: the three pre-witness propositions do not
logically force either `Witness312` or the scalar inequality.

These are logical independence results about the interfaces.  They are not
counterexamples to IUT and make no assertion about whether IUT's upstream
machinery proves the missing witness.

## Positive smoke model

`KTG.Examples.identity_pipeline_scalar_bound` instantiates the complete pipeline
on a finite Boolean equality model.  It constructs a controlled realization,
normalization witness, witness-preservation bridge, and monotone observable, and
then obtains the scalar bound through the generic theorem.  This checks that the
interface is constructible rather than merely a negative gatekeeping device.

## Verification

The release is pinned and checked with:

```text
Lean 4.34.0-rc2
Lake 5.0.0-src+6a10ac8
```

The final audit performed:

- a clean `lake build`: **17 jobs passed**;
- direct elaboration of all **15 Lean source files** with
  `-DwarningAsError=true`;
- a source scan finding no `sorry`, `admit`, `unsafe`, or axiom declaration;
- SHA-256 recording for every Lean source;
- a regenerated full-bundle manifest.

The predecessor's uncompiled v4.19.0 source is preserved under
`verification/predecessor_uncompiled/`.  The active release pin was changed to
the compiler actually used for verification.

## Exact remaining IUT obligation

No status change is claimed for IUT III Corollary 3.12.  To use this framework
for Step (xi-e) → Step (xi-f), a later block must map source definitions and
prove an IUT-specific instance of `KWitnessBridge.witness_preserved`.
Concretely, that requires:

1. typed source and target objects for the multiradial output and fixed q-pilot;
2. a realization certificate built from the precise IPL/SHE/APT data;
3. an explicit controlled-obstruction theorem;
4. an explicit normalization law, including every multiplicity and the later
   `j²` weighting where it enters;
5. a theorem placing the q-pilot measurement below or inside the relevant
   holomorphic/log-volume hull;
6. only then, application of the monotone log-volume observable.

Until item 5 is sourced or proved, the framework records an open obligation,
not a flaw and not a completed proof.
