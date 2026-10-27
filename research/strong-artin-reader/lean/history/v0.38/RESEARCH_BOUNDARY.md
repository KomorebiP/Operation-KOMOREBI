# Research boundary after v0.38

## Closed in this release

- Ordered noncommutative power derivative and a uniform ultrametric remainder bound.
- Exact image and uniqueness on a sufficiently small ball from a bounded two-sided inverse.
- Actual entrywise matrix norm, completeness, and integral-matrix reconstruction.
- A finite matrix-unit certificate for Q=p^(-s)B=D_A^(-1), with integral B.
- For m>s, the exact finite criterion modulo p^(m+s) for roots in A+p^m Mat_n(Z_p).
- Actual GL_n(Z_p) roots for unit targets and positive degree.
- A Lean-checked unipotent square-map inverse certificate with singular residual derivative.
- A noncommuting positive control and a negative target rejected by the exact finite test.

## Still open

1. **Derivatives singular over Q_p.** There is no two-sided inverse to use; no universal finite horizon is established here. A unit center can have such a derivative, e.g. the square derivative at diag(1,-1).
2. **General shallow resonant prefixes.** The theorem requires m>s. It does not classify every prefix modulo p^m for m<=s. An algorithm would need to cover suitable deeper centers and handle singular loci, without assuming success at all depths.
3. **Automatic certificate discovery for arbitrary p-adic inputs.** The Lean theorem takes exact finite algebraic identities as hypotheses. The auxiliary exact-rational code covers two-by-two rational centers. No black-box p-adic decision algorithm or arbitrary-dimensional certified matrix-inversion implementation is supplied.
4. **Simultaneous prescriptions in this newly resonant sector.** The previous compactness theorem retains its joint all-depth premise. This release proves one prescribed power at a time.
5. **Arithmetic local conditions, ramified coefficient rings, global localization, auxiliary descent, automorphic carrier, and Strong Artin.** These remain open.

The achieved result removes the all-depth premise in the certified nonsingular derivative sector at sufficient precision, including mod-p resonance. Do not report the entire resonant matrix problem, or Strong Artin, as solved.

Verification rebuilds seven new modules against the pinned Mathlib cache. Historical archives are hash-authenticated and preserved, not newly replayed. There is no independent-kernel check or global novelty claim.
