# v0.13 proof ledger

## A. Centering an arbitrary separating probe family

File: `src/CenteredProbeTransverse.lean`

Closed:

- `centeredProbe`
- centered probe kills the chosen defect vector;
- the whole defect line lies in every centered kernel;
- if the original probes separate and the reference sees the defect, the centered joint kernel is exactly the defect line;
- the descended probes generate the full transverse dual.

## B. Actual trace-projector realization

File: `src/ProjectorTraceTransverse.lean`

Closed:

- `projectorTraceProbe P : X |-> tr(PX)`;
- centered functionals equal trace probes of centered projector combinations;
- centered projector probes kill every scalar endomorphism;
- raw projector separation implies centered joint kernel equals `k • 1`;
- the centered quotient probes generate the full transverse dual.

## C. First projector obstruction capstone

File: `src/ActualProjectorCyclicObstruction.lean`

Closed under raw projector separation:

- transverse correction map is surjective;
- full first-order obstruction vanishes iff cyclic scalar residual vanishes;
- obstruction cokernel has finrank one.

## D. Simple-packet detection implies separation

File: `src/AdequateProbeDetection.lean`

Closed:

- common kernel of a covariant probe family is an invariant submodule;
- every nonzero invariant submodule of a finite-dimensional finite-group representation contains an atomic/simple invariant submodule;
- this uses Artinian finite group-algebra module structure, not modular semisimplicity;
- detection of every simple packet implies zero common kernel;
- therefore the dual probe map is surjective.

## E. Conjugation covariance of actual trace probes

File: `src/ConjugationProjectorProbes.lean`

Closed:

- `conjugationRepresentation rho` acts by `X |-> rho(g) X rho(g^-1)`;
- a conjugation-covariant projector family yields a covariant trace-probe family;
- the proof uses the representation law and cyclicity of trace.

## F. Simple-packet projector capstone

File: `src/AdequateProjectorCyclicObstruction.lean`

Closed:

- conjugation covariance plus simple-packet projector detection implies raw trace separation;
- centered transverse correction is surjective;
- quotient-prime obstruction is exactly the cyclic residual;
- obstruction dimension is one.

## G. Finite probe extraction

File: `src/FiniteProbeExtraction.lean`

Closed:

- a separating probe family spans the complete algebraic dual in finite dimension;
- a finite linearly independent subfamily of actual probe functionals exists;
- its cardinality equals the dimension of the source space.

## H. Finite actual projector basis

File: `src/FiniteProjectorProbeExtraction.lean`

Closed:

- centered quotient-projector probes separate the scalar quotient;
- a finite basis of actual centered quotient-projector probes exists;
- its cardinality is exactly the transverse dimension.

## I. Relative/off-scalar spectral detection

File: `src/RelativeSpectralDetection.lean`

Closed:

- define detection only for simple conjugation packets not contained in `k • 1`;
- one reference projector with nonzero trace detects every nonzero simple packet contained in the scalar line;
- therefore off-scalar detection plus the reference projector implies full simple-packet detection;
- no hypothesis `char(k) ∤ dim(W)` is used in this algebraic theorem.

## J. Relative-adequacy capstone

File: `src/RelativeAdequacyProjectorCapstone.lean`

Closed:

- relative/off-scalar detection implies raw trace separation;
- full first-order obstruction vanishes iff cyclic residual vanishes;
- exactly one obstruction dimension survives;
- finite transverse basis extraction follows under the same relative hypotheses.

## Counts

This additive block contains **36 theorem/lemma declarations** and **11 definitions** across ten source modules.

Declaration counts are inventory data, not novelty or difficulty measures.
