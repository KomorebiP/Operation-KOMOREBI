# Lean Formalization Plan

## Phase A — Abstract KTG core

**Block 02 status: complete for the present audit and compiler-verified.**

Checked components include typed contexts, relational transport, realization
certificates, obstruction control, hulls, monotone observables, measurement
witnesses, grade-space bridges, curvature, safe abstraction, and finite positive
and negative models.

## Phase B — Generic theorem pipeline

**Status: complete for the present audit.**

Checked theorems include:

- certified realization implies structural relatedness
- structural relatedness does not imply certified realizability
- normalization equations compose only through an explicit `KGradeBridge`
- `KWitnessBridge` isolates witness preservation
- `CertifiedTransportBound` packages realization, normalization, and witness
- `certified_transport_bound` derives the scalar order only after all gates
- the pre-witness gates do not imply hull membership
- a positive finite model instantiates the complete generic route

Further generic work, such as quotient-action invariance or bridge composition,
is useful but not required to decide the present IUT hinge.

## Phase C — Non-circular IUT 3.12 interface

**Block 02 status: complete and compiler-verified.**

The abstract interface separates structural linkage, realizability,
normalization, witness, witness soundness, and scalar conclusion. `Witness312`
is independent of the desired inequality.

## Phase D — Source-faithful Step (xi) model

**Block 03 status: interface complete and compiler-verified.**

Completed:

1. distinct types for output, q-pilot, hull input, line object, prime-strip,
   trace, structure, and measurement
2. typed IPL, SHE, and APT certificates
3. explicit Ind1–Ind3 and six additional live obstruction channels
4. determinant and procession normalization through an explicit grade bridge
5. separate representation of the downstream IUT IV `j²` weight
6. exact open proposition `StepXiEWitnessPreservation`
7. finite countermodel proving that all pre-witness fields are insufficient
8. positive finite equality model
9. bridge back to the Block 02 `Cor312Interface`
10. field-by-field source and page mapping

The source-faithful interface is not yet an IUT instantiation. Most fields are
parameterized by types and predicates whose actual IUT constructors remain to
be supplied.

## Phase E — Concrete IUT instantiation

**Current frontier.**

### E1. Object shell

Construct concrete records for the Step (xi-c) output package, fixed q-pilot,
prime-strip, determinant-line object, and log-volume datum. Keep domain and
codomain arithmetic-holomorphic structures tagged.

### E2. Certificate constructors

Convert cited Theorem 3.11 and Remark 3.11.1 data into actual constructors for
`InputPrimeStripLink`, `AlgorithmicParallelTransport`, and
`SimultaneousHolomorphicExpressibility`. Source assertions that have not been
formalized remain explicit hypotheses.

### E3. Obstruction subtheorems

Attempt concrete statements for:

- Ind1 procession-automorphism invariance
- Ind2 direct-summand or tensor-factor invariance
- Ind3 one-sided upper semi-compatibility
- unit-multiple absorption by the holomorphic hull
- tensor-power grade preservation
- vertical-shift rectification
- log-link and logarithmic-conjugate measurement invariance
- an exact interpretation of the Step (xi-f) approximation language

### E4. Normalization instance

Instantiate determinant power, summand multiplicities, structure-sheaf
correction, and procession averaging. Prove the grade equation independently of
hull membership.

### E5. Witness decomposition

Decompose `SourceWitnessTheorem` into the smallest source-level statements:

1. construction of a candidate representative of the fixed q-pilot
2. membership of the candidate in the relevant output hull
3. invariance of its measurement under permitted indeterminacies
4. orientation of the final one-sided order

A source-backed proof of these lemmas would close the witness. Failure of an
overstrong sublemma should be preserved as a formal countermodel or explicit
open boundary.

### E6. Observable instance

Instantiate the actual log-volume observable and prove monotonicity for the
selected measurement order. Only then apply the checked scalar theorem.

## Verification policy

- Never mark an IUT-specific assumption as proved because its intended meaning
  appears plausible.
- Distinguish source definition, source assertion, Lean hypothesis, Lean
  constructor, Lean theorem, and interpretation.
- Do not use the scalar conclusion as the definition of the witness.
- Build after every material change.
- Treat failed elaboration and timeouts as recorded outcomes.
- Run every source with warnings as errors.
- Preserve predecessor hashes and failed attempts.
