# Continue from Lean 0.14.0

P32 is complete in its finite-table scope. Coverage: 39 complete, zero partial, 48 unformalized. Current proof endpoints are `Spectral.finite_table_stability`, `FiniteTableP32.coordinates_and_decoder` and `BasisCoordinates.decoder_matrix_formula`.

PASS: 282 cumulative stages; 84 metadata/tooling checks. Exact delivered-ZIP replay is recorded separately in the external verification JSON.

See `verification/P32_CLOSEOUT.md` for the phase synthesis and `AUDIT.md` for hypotheses and self-review limits. The frozen manuscript is unchanged.

## Continuation

No P32 implication remains open in the stated finite-table theorem. The broader program has 48 unformalized propositions; see ROADMAP_1.0.json for the exhaustive disjoint list.

Next bounded target: P31, missing-intervention nonidentifiability, in frozen Foundations §32. The exact manuscript construction uses one hidden state and two observations. Both models give (1/2,1/2) under action a; they give (1,0) and (0,1) under b. Formalize actual stochastic models, prove every a-only word has common probability 2^(-length), and exhibit the one-step b disagreement. Existing instrument and word-probability APIs should supply the construction. P31 is not counted as proved by this handoff.

P35's reset-experiment probability certificate and P37's conditional observation-based completion remain further parts of the learning chain. P32 does not silently supply their statistical or coverage assumptions.
