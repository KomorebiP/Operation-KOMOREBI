# IUT III Corollary 3.12 — Open Obligations after Block 03

## Status convention

- **Typed:** the proposition and all relevant object types exist in Lean.
- **Source located:** the source contains the named construction or property.
- **Instantiated:** an actual IUT object/theorem has been supplied as a Lean term.
- **Closed:** the resulting term passes the project verifier without assumptions,
  placeholders, or axioms.

## O1 — Concrete source types

**State:** Typed; source located; not instantiated.

Instantiate `TypedData` with the actual multiradial output package, q-pilot,
holomorphic-hull input, determinant-line object, prime-strip, algorithm trace,
and log-volume measurement objects used in IUT III.

A mere alias of all fields to one ambient type is not acceptable. The point of
Block 03 is to preserve the distinctions used in Steps (xi-c)–(xi-f).

## O2 — IPL/SHE/APT constructors

**State:** Typed; source located; not instantiated.

Construct `SourceRealizationCertificate` from the precise Theorem 3.11 and
Remark 3.11.1 data:

- an actual full poly-isomorphism for IPL;
- an actual construction trace;
- production and input-use certificates for APT;
- simultaneous executability in the two arithmetic-holomorphic structures;
- the fixed/coric q-pilot input condition.

These fields may not be replaced by a proposition named “Theorem 3.11 holds”.

## O3 — Obstruction control

**State:** Channels typed and source locations mapped; not instantiated.

Supply one theorem for each field of `ObstructionControl`:

1. Ind1 procession automorphisms;
2. Ind2 tensor-factor/direct-summand automorphisms;
3. Ind3 upper semi-compatibility;
4. unit multiples absorbed by hulls;
5. tensor-power twists preserved by grades;
6. vertical shift rectified by the 1-column log-Kummer correspondence;
7. log-link iterates invisible at the measurement level;
8. logarithmic conjugates invisible at the measurement level;
9. the “approximation” of Step (xi-f) expressed as a specific one-sided order.

A source statement that only proves invariance of a different object or a
different quotient does not close the corresponding field.

## O4 — Determinant/procession normalization instance

**State:** Generic two-stage theorem closed; IUT instance open.

Instantiate `NormalizationData` and prove:

- existence of an intermediate comparable determinant-line object;
- the positive tensor power `M`;
- direct-summand multiplicities/weights;
- the structure-sheaf correction;
- procession averaging normalization;
- the explicit grade bridge between determinant and procession conventions.

The later IUT IV `j²` weight is represented separately by
`attachIUTIVSquareWeight`. It must not be used to manufacture the IUT III
containment witness.

## O5 — Step (xi-e) witness preservation

**State:** Typed and isolated; open.

Prove an inhabitant of

```lean
SourceWitnessTheorem D S N
```

or equivalently prove `StepXiEWitnessPreservation D S N`.

This is the load-bearing source theorem. It must turn a concrete certified
realization plus a concrete normalization witness into
`QPilotHullContainment D out q`.

The following are insufficient by themselves:

- IPL linkage;
- SHE;
- APT;
- all named obstruction controls;
- determinant/procession normalization;
- equality of scalar conventions;
- the statement that two objects are comparable.

`IUT312SourceCountermodel.lean` proves this logical non-implication for the
complete typed interface.

## O6 — Concrete log-volume observable

**State:** Generic monotonicity route closed; IUT instance open.

Instantiate `KObservable (targetContext D) Λ` with the actual log-volume value
and prove monotonicity for the selected measurement order/hull. Then apply
`scalarBoundOfSourceWitness` or `cor312ScalarBoundOfSourceWitness`.

## Decisive completion condition

Block 03 should be regarded as source-instantiation complete only when O1–O6
are closed and the exact IUT source theorem supporting O5 is recorded with its
full dependency chain. Until then, the release is a checked audit interface, not
a proof or disproof of Corollary 3.12.
