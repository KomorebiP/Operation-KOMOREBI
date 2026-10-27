# Source and claim map

## Classical inputs

The following are established mathematical inputs.

- Symmetric q-numbers and positive discrete-series representations of quantum algebras.
- Clebsch-Gordan and Racah coefficients for quantum-group tensor products.
- q-Hahn, q-Racah, and Askey-Wilson polynomial families.
- q-Racah duality and finite orthogonality.
- The Askey-Wilson q-difference equation.
- The Biedenharn-Elliott or pentagon identity for quantum `6j` symbols.
- Givens factorization of real orthogonal matrices.
- Entropy increase under a doubly stochastic channel.

## Results proved directly in the paper

The paper gives direct finite proofs or derivations of the following statements in its declared convention.

1. The local symmetric q-algebra on the positive shape packet.
2. Coassociativity of the displayed coproduct.
3. The scalar q-Casimir value.
4. The fixed-excitation multiplicity dimension.
5. The explicit two-packet lowest-weight coefficient ratio and closed q-Hahn seed.
6. Orthogonal analysis and synthesis between pair q-Casimir atlases.
7. The equal-half-shape one-excitation q-Racah matrix.
8. Its classical and routing limits.
9. Bistochasticity of squared recoupling amplitudes.
10. Entropy nondecrease for every fixed measurement kernel.
11. Monotonic entropy and spectral gap in the exact two-channel model.
12. Skew-symmetry of the q-deformation generator.
13. The finite pentagon certificate from complete tree bases.
14. The Givens rotation bound.
15. q-Racah duality in the displayed basic-hypergeometric normalization.
16. The termwise q-to-one Racah limit.

## Classical theorem used without full rederivation

The identification of the full three-body recoupling entries with q-Racah functions and the corresponding tridiagonal-pair theorem are classical representation-theoretic results. The code reconstructs the finite matrices from q-Casimir operators and checks the expected orthogonality, spectrum, and tridiagonal structure.

The Askey-Wilson eigenfunction equation is a standard identity. The program evaluates both sides independently at multiple degrees and points.

## Computational certificates

The generator performs 23 named checks. The separate Pytest file performs 20 independent tests. Numerical agreement supports the implementation, but numerical checks do not replace analytic proofs.

The four-body pentagon computation is especially sensitive to packet ordering, sign conventions, completeness, and projector construction. Its residual remains near machine precision in the tested cases.

## Negative control

The row entropy of a higher-excitation q-Racah measurement kernel is not always monotone as q varies. The paper records an explicit numerical decrement near q equal to 0.78. Only the one-excitation monotonicity theorem is claimed.

## Open directions

- Closed shape-parameter formulas for the complete symmetric-convention recoupling matrix.
- Large-excitation asymptotics of the deformation metric.
- Structural criteria for q-monotone measurement entropy.
- Continuous-series packet transforms and Askey-Wilson function transforms.
- Root-of-unity and nonsemisimple packet systems.
- Locality-aware associator compilation.
- Composite logarithmic-number and q-shape quantum observables.

No open direction is presented as solved.
