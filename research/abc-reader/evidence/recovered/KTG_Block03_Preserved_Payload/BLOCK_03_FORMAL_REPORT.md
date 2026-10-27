# Komorebi Transport Geometry — Block 03 Formal Report

**Release:** v0.3.0  
**Date:** 2026-09-17  
**Status:** source-faithful Step (xi-e) → Step (xi-f) interface compiler-verified, IUT-specific witness theorem open

## Result

Block 03 replaces the single abstract IUT 3.12 interface with a typed model of
the actual proof boundary described around IUT III Steps (xi-d), (xi-e), and
(xi-f). It does not formalize all of IUT. It identifies the smallest set of
objects and certificates needed to state the disputed transition without
renaming the desired scalar inequality as an assumption.

The formal pipeline is now:

```text
multiradial output package
+ fixed q-pilot
+ IPL prime-strip linkage
+ APT construction trace carrying SHE
+ nine channel-specific obstruction controls
+ determinant/tensor-power normalization
+ procession normalization through an explicit grade bridge
+ Step (xi-e) witness-preservation theorem
⇒ q-pilot hull containment
⇒ monotone scalar bound.
```

Every implication before the witness-preservation theorem is implemented. The
IUT-specific inhabitant of that theorem is not supplied.

## Typed source vocabulary

`KTG.IUT312.TypedData` introduces definitionally distinct types for:

- a multiradial output package
- a fixed q-pilot
- a holomorphic-hull input
- an intermediate comparable determinant-line object
- a prime-strip
- an algorithm trace
- an arithmetic-holomorphic structure
- a log-volume measurement

The distinction prevents an output object, q-pilot, hull input, and scalar
measurement from collapsing into a single ambient type without an explicit
map. The source and target measurements meet only in the shared ordered
measurement space.

The exact measurement-level target is
`KTG.IUT312.QPilotHullContainment`. It states that the fixed q-pilot
measurement lies below the holomorphic hull of the raw output measurement. The
theorem `qPilotHullContainment_iff_hullWitness` identifies this proposition with
the generic KTG `HullWitness` interface.

## IPL, SHE, and APT certificate

`KTG.IUT312.SourceRealizationCertificate` records:

1. `InputPrimeStripLink`, an actual `FullPolyIso` between the output and fixed
   q-pilot prime-strips
2. `AlgorithmicParallelTransport`, an algorithm trace that produces the output
   and uses the fixed input
3. `SimultaneousHolomorphicExpressibility`, asserting that the same trace is
   executable in the domain and codomain arithmetic-holomorphic structures
   while the q-pilot remains fixed
4. an explicit obstruction bundle

The certificate contains no hull-membership field and no scalar inequality.
APT is represented by a trace and predicates, not by a set-theoretic map from
one region to another. This follows the warning in IUT III Remark 3.11.1 that
the construction should not be understood as ordinary transport of a region by
a function.

## Obstruction ledger

`ObstructionSemantics`, `ObstructionBundle`, and `ObstructionControl` separate
nine channels:

1. Ind1 procession automorphisms
2. Ind2 tensor-factor or direct-summand automorphisms
3. Ind3 upper semi-compatibility
4. unit multiples
5. tensor-power twists
6. vertical shifts
7. log-link iterates
8. logarithmic conjugates
9. the one-sided approximation language in Step (xi-f)

Each channel has its own state and proof predicate. Naming the channel does not
prove it harmless. An IUT instantiation must supply a theorem for every field of
`ObstructionControl`.

## Two-stage normalization

Block 03 makes the normalization chain explicit:

```text
OutputGrade
  -- determinantSigma --> DeterminantGrade
  -- determinantToProcessionGrade --> ProcessionInputGrade
  -- processionSigma --> QPilotGrade.
```

The grades track:

- vector rank
- weighted positive determinant power
- direct-summand multiplicity
- structure-sheaf correction
- procession averaging scale

`normalizationGradeBridge` is an explicit `KGradeBridge` between the
determinant and procession conventions. `directNormalization` requires an
actual intermediate comparable line object and proofs for both normalization
stages. The theorem `directNormalization_grade_eq` checks the complete grade
equation.

The later IUT IV square weight is represented separately by
`IUTIVSquareWeightedGrade` and `attachIUTIVSquareWeight`. The theorem
`attachIUTIVSquareWeight_exponent` checks that the attached exponent is exactly
`j * j`. This factor is intentionally downstream of the IUT III Step (xi)
witness and cannot be used to manufacture that witness.

## Exact open theorem

The remaining source theorem has the Lean type:

```lean
def StepXiEWitnessPreservation
    (D : TypedData)
    (S : CertificateSemantics D)
    (N : NormalizationData D) : Prop :=
  ∀ {out q},
    CertifiedRealization (certification D S) out q →
    NormalizationWitness (directNormalization D N) out q →
    QPilotHullContainment D out q
```

`SourceWitnessTheorem` is a named wrapper for this proposition.
`witnessBridgeOfSourceTheorem` converts an inhabitant into the generic
`KWitnessBridge`. The scalar theorems then follow mechanically.

The project supplies no IUT-specific inhabitant of `SourceWitnessTheorem`.
Consequently the formal development neither repairs nor invalidates IUT III
Corollary 3.12. It makes the exact missing proof term auditable.

## Source-specific logical countermodel

`IUT312SourceCountermodel.lean` constructs a finite Boolean model in which all
of the following hold:

- IPL
- APT
- SHE
- all nine obstruction-control fields
- the full two-stage normalization witness

but `QPilotHullContainment` fails. Lean checks both
`all_source_prewitness_fields_do_not_imply_containment` and
`no_sourceWitnessTheorem`.

This is a logical independence result about the formal interface. It is not a
counterexample to IUT because the finite model does not instantiate IUT's
mathematical objects or theorems.

## Positive equality model

`IUT312SourceExample.lean` provides a finite equality model in which the IPL
proof itself supplies the containment witness. It constructs a complete source
certificate, normalization chain, source witness theorem, monotone observable,
and the final scalar bound. This proves that the source-faithful interface is
constructible and that its positive route composes correctly.

## Bridge to the Block 02 Corollary 3.12 interface

`IUT312Cor312Bridge.lean` refines the abstract `Cor312Interface` with the Block
03 typed data. It proves:

- `Witness312` is exactly `QPilotHullContainment`
- an actual source witness theorem yields a complete `Cor312Certificate`
- the source-faithful route and the generic Block 02 route produce the same
  scalar target

No circular definition of `Witness312` is reintroduced.

## Source mapping

`notes/IUT_312_FIELD_TO_SOURCE_MAP.md` maps every object, certificate field,
obstruction channel, grade component, and open witness proposition to the
relevant IUT III or IUT IV location. The map distinguishes:

- a source statement that was located
- a formal interpretation of that statement
- a theorem that has actually been instantiated in Lean
- an open theorem

`notes/IUT_312_OPEN_OBLIGATIONS.md` records the remaining source instantiation
work as O1–O6.

## Verification

The checked release uses:

```text
Lean 4.34.0-rc2
Lake 5.0.0-src+6a10ac8
```

The final verifier performs:

- a clean Lake build of 24 jobs
- direct elaboration of all 22 Lean sources with warnings treated as errors
- a scan finding no `sorry`, `admit`, `unsafe`, or axiom declaration
- a required-interface and documentation contract audit
- a predecessor-core audit confirming all 14 Block 02 module sources remain
  byte-for-byte unchanged
- SHA-256 recording for every Lean source

The offline runtime reconstruction command exceeded its execution cap during
archive extraction, although the resulting runtime was complete and usable.
That event is recorded as an environment timeout, not as proof evidence. The
project-specific clean build and every source-level check completed normally.

## Exact remaining boundary

The next mathematical block is not another generic scalar lemma. It must
instantiate actual IUT objects and prove at least one load-bearing theorem of
the following form:

```text
concrete Theorem 3.11 / Remark 3.11.1 realization
+ concrete obstruction controls
+ concrete determinant/procession normalization
→ concrete q-pilot holomorphic-hull containment.
```

Until that theorem is established from the source dependency chain, the status
of IUT III Corollary 3.12 remains unchanged: neither proved nor disproved by
this project.
