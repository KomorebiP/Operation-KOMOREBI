# Block 20 failure and repair record

This record separates checked results from unsuccessful development attempts.

1. A direct brute-force expansion of the full seven-factor `4×4` matrix product exceeded the available execution window. The final proof was reorganized into nested Clifford sandwich identities (`y-z-y`, then `x-y-z-y-x`, then the mass palindrome).
2. Early `InvolutionExponential4` drafts reversed the explicit bridge inverse or conjugation orientation, mishandled scalar normalization, and invoked an unsuitable determinant-inverse theorem. The bridge was proved two-sided explicitly, and the determinant transport was rewritten through valid similarity identities.
3. Initial sandwich proofs generated noncommutative scalar-normalization and module-law side goals. Dedicated `linearFactor_sq`, `closedFactor_sq`, and anticommuting-sandwich lemmas replaced brittle direct normalization.
4. An early walk proof used an association pattern inconsistent with the literal definition. The final definition and unitarity proof retain explicit parentheses matching the seven-factor product.
5. Early dispersion calculations mishandled the complex identity `i²=-1` and the ordering of angle products. The final coefficient norm is first proved over the reals, then cast to the complex numbers.
6. Initial characteristic-determinant attempts expanded the `4×4` determinant with unsuitable simplification order and produced unresolved `i²` terms. The final proof reduces by the first row, uses the explicit `3×3` determinant formula, and normalizes the resulting polynomial exactly.
7. Several exact-example drafts left unnecessary tactics after goals had already closed or failed to normalize matrix entries. These scripts were simplified and rerun with warnings as errors.
8. A preliminary aggregate invocation failed because upstream local modules had not yet been compiled in the clean build tree. This was an environment/build-order failure, not a mathematical counterexample; the cumulative verifier recompiles modules in dependency order.
9. One full `lake build` status call exceeded its external command window after compiling many modules. It is not counted as proof evidence. Only the completed production verifier and fresh-extraction verifier may establish release PASS status.

No failed compile, timeout, cached object, or partial run is counted as a checked theorem. No admission, custom axiom, or weakened mathematical statement was introduced to repair these failures.
