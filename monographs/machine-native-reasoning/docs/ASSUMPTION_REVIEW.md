# Assumption and statement-fidelity review

This is a source-to-Lean review conducted within Operation Komorebi. The compiler verifies the actual elaborated types, not an intended English interpretation. The formalization did not require a mathematical amendment to any of the six selected source statements.

## 1.1 — A decoder from attained evidence

`Attained r` is literally a subtype with a witness that a record was produced. No interpretation of impossible records is assumed. The backward proof chooses a producing world and proves that the choice is immaterial from fibre constancy. The function is noncomputable in general. The result generalizes the source's finite setting to arbitrary types. It does not bound description length or discovery cost. `no_decoder_of_collision` is universal over all decoders.

## 1.2 — Behavioral quotient, initialization, minimality

`run` executes the head action before the tail. `SameBehavior` quantifies over every finite action word including the empty word. Its setoid is built, successor congruence is proved, and actual quotient operations and readout are defined. The canonical predictor's correctness field is proved from those operations, not assumed. Arbitrary alternative predictors must satisfy their stated exactness contract before the necessity and lower-bound arguments apply.

The state-count theorem compares the image of initialization, not a potentially much larger ambient predictor type. With finite X, all attained state sets are finite even when the ambient type is not. `canonical_initialized_card` proves attainment of the lower bound. This is not a procedure for discovering or efficiently enumerating an arbitrary behavioral quotient.

## 2.1 — Split encoding and compression

The implementation uses actual linear maps over a field. Whole-state composition uses S composed with A equal to identity. No orthogonality is assumed. The hidden-return identity holds even without the compression splitting C composed with R equal to identity; it therefore implies the source statement under that extra premise. A separate theorem establishes projector idempotence when the splitting is supplied. The exact swapped-coordinate witness demonstrates the nonzero return. No norm, approximation, or numerical stability conclusion is added.

## 2.3 — Word order, invariant scope, matched output

`forward_transport` is the total-domain version. `invariant_forward_transport` and `invariant_forward_output` explicitly carry the preserved source domain and domain-restricted premises. The action-name map is fixed. The proof does not require injectivity, an inverse translator, equality of all target operations, a learned translation, or cheap execution. Output matching is a separate premise rather than inferred from hidden-state intertwining. A noncommuting arithmetic example checks the chronology convention.

## 3.1 — Memory for correction

`EvidenceAlgebra` assumes the whole world set and binary-intersection closure. Events filter a fixed world rather than changing it. `Memory` is the actual image of the full correction signature. The updated signature is independent of the chosen realizing candidate set. Readout recovers the current target set, and induction covers any finite event list.

The minimality argument derives signature separation from another memory's readout and update guarantees, then constructs a surjection onto signatures. It is not proved by assuming the desired separation. Empty candidate sets are included. Finite cardinality is proved with finite Ω. The separate partition-evidence occupancy formula (source 3.2) is not formalized by this result.

## 3.6 — Genuine joint stochastic law

`Law` supplies nonnegative real entries and exact normalization over each action's combined report/successor column. Orientation is K(action, report, successor, input). The surjection onto coarse states is explicit. `coarseLaw` is actually constructed by aggregating a chosen input representative. Its positivity and normalization are proved. The fibre criterion then proves representative-independent intertwining, and surjectivity proves uniqueness of the whole law (proof fields are irrelevant).

Point-mass distributions prove the necessity direction. Report-mass and positive-posterior preservation are proved equivalent to the complete linear interface on actual nonnegative laws. At zero report mass, nonnegativity forces the entire column-weighted vector to vanish. The exposed `posterior?` returns `none`, not a made-up distribution. The internal total `normalize` function does use Lean's total division; its probability interpretation is invoked only under positive mass.

History evolution is defined using the same history-dependent action probabilities in both models. The general linear identities hold for arbitrary real vectors; to read them as probability claims one supplies `IsDist`, normalized kernels and a `Policy`. `totalHistoryMass_eq` and the posterior-distribution theorem establish that interpretation. Policy input contains observed actions and reports, not the hidden state.

A separate `StoppingPolicy` splits mass between continuation and terminal decisions. It preserves joint terminal records, and a finite-cutoff conservation theorem sums stopped probability plus surviving active probability. It does not assert that every stopping policy eventually stops. No equality of independently optimized planners, total-variation bound, physical calibration guarantee, or floating-point implementation is inferred.

## Counterexamples are theorems, not test-count proxies

The examples prove the sensor's nonidentification, calibrated decoding, chronological order, hidden return, lost target/convention association, opposite posteriors with matching marginals, and a nontrivial failure of the joint fibre criterion. A four-to-two-state positive quotient also instantiates arbitrary finite feedback. Small concrete instances do not supply the general results, whose quantified proof terms are checked separately.

## Trusted base

The transitive axiom audit permits only propositional extensionality (`propext`), classical choice, and quotient soundness. Source preflight rejects explicit production axioms, placeholders, native-decision shortcuts and unsafe declarations. Generated implementation auxiliaries do not enlarge the theorem axiom allowance. `leanchecker` replays local declarations into the imported environment using the same Lean kernel, so it is not an independent kernel or a proof that all upstream software is flawless.

The generated audit intentionally names auxiliary theorem constants to inspect them. Only that audit file disables the unstable-auxiliary-name linter. No such linter change is applied to production proofs; warnings remain errors there. The complete axiom set, not absence of a source keyword alone, is the trust-policy gate.
