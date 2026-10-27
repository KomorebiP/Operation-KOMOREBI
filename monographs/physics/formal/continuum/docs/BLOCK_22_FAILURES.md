# Block 22 failure and repair record

This record separates checked proof objects from unsuccessful development attempts.

1. The first Lorentz-kinematics draft tried to use the source coefficient `(γ-1)/|v|²` directly. That creates an artificial singularity at zero velocity. The implementation was replaced by the regularized coefficient `γ²/(γ+1)`, and equivalence to the source form was proved away from zero speed.
2. Initial component proofs for vanishing squared norm and the exact boost identities did not close under broad automation. They were replaced by explicit coordinate-square and coefficient identities.
3. A first direct compile of `Relativistic3DDiscreteBoost` lacked the newly produced local `.olean` dependency. Building the prerequisite module through Lake repaired the build-order issue; it was not a mathematical failure.
4. Early rationalization steps in the moving continuum-energy proof left denominator and pointwise-function equalities implicit. Explicit nonzero denominator proofs and function congruences repaired the elaboration.
5. The first generic path-inversion draft left branch and denominator obligations under-inferred. The proof was reorganized through normalized sine-square, eventual positivity, positive square root, and an eventual `arcsin` representation.
6. The first moving-shell draft had under-specified right-hand sides in several `IsBigO` compositions. Explicit function types and congruence statements resolved the ambiguity.
7. The first moving-frequency draft unfolded the physical correction in the wrong place and failed to align the generic path theorem with the concrete shell quotient. A separate coefficient identity and eventual equality bridge repaired it.
8. The first observer-cancellation compile contained a `ring` call after `field_simp` had already closed one goal, attempted an invalid rewrite through an already unfolded wrapper, and used an ill-typed `and_iff_left`. Those were repaired without changing the theorem statement.
9. The first rational-example compile lacked the observer module object file and expected `norm_num` to close square-root identities automatically. The dependency was built explicitly, and exact square-root lemmas plus targeted rewrites were supplied.
10. Several cumulative parallel `lake build` invocations exceeded their external command windows near completion. They are not verification evidence. Repeated incremental runs ultimately completed the aggregate build; the release verifier independently recompiles every active module sequentially.
11. An initial verifier invocation was terminated by the execution wrapper before completion. Its incomplete report is not counted. The authoritative run is the completed `verification/final/report.json` packaged with the release.
12. One shell command initially pointed to a nonexistent runtime subdirectory, and another set `LAKE_PKG_URL_MAP` to invalid empty JSON. Both were environment-command errors and produced no proof claim.

No timeout, partial compilation, stale object file, or failed tactic is counted as theorem evidence. No `sorry`, `admit`, custom axiom, `unsafe`, or weakened replacement theorem was introduced.
