# Block 30 failure ledger

- **Portable runtime extraction:** the first extraction command exceeded its
  outer execution window after all seven parts and the combined archive hash
  had passed.  It was not counted as success.  Extraction was completed from
  the already verified archive and the pinned Lean version was rechecked.
- **Cold parent builds:** two one-worker attempts to fill an empty cumulative
  project cache exceeded their outer windows.  They are inconclusive.  The
  Block 29 import closure later completed successfully, and the final v0.30
  cumulative build completed all 3,788 jobs with one worker.
- **Finite cube instance:** the first operator packaging lacked a `Fintype`
  instance for the Boolean cube vertex.  An explicit equivalence with
  `Bool × Bool × Bool` supplied the reducible finite enumeration.
- **Continuous-linear extensional proofs:** initial `rfl` attempts did not
  expose composition and subtraction applications.  The repaired proofs use
  the relevant apply lemmas and function extensionality.
- **Edge-ratio algebra:** an attempted division lemma did not match the unit
  group presentation.  The final equivalence is proved by group cancellation
  through `mul_inv_eq_one`-style identities.
- **Namespaced dot notation:** local wrappers around `FineEdgePair` initially
  failed under inferred namespace arguments.  They were replaced by explicit
  functions with fully determined parameters.
- **First final verifier invocation:** the verifier redundantly replayed the
  successful one-worker cumulative build and exceeded the outer tool window
  before reaching the API audit.  That run is excluded.  The completed
  one-worker receipt was frozen and imported into a clean verifier rerun, which
  passed every remaining gate.
- **No mathematical counterexample:** none of these events refuted a Block 30
  theorem.  Failed elaborations and timeouts were repaired or excluded rather
  than counted as evidence.
