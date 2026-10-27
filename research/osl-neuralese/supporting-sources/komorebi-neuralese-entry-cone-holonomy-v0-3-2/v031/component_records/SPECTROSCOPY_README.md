# Projective Holonomy Spectroscopy Prototype

This directory is an exploratory, checkpoint-agnostic prototype for the next
Neuralese diagnostic block. It does not modify or import the v0.3.0 package and
does not contain learned checkpoint values.

The module separates five claims that should not be conflated:

1. A temporal relation word has a well-defined matrix product in the registered
   column-vector convention.
2. Generator-wise normalization and relation-block normalization preserve the
   same positive ray when no intermediate state is zero.
3. A relation product can be compared with the best positive scalar identity in
   Frobenius norm.
4. Its eigenspectrum can suggest, but cannot by itself certify, projective
   asymptotics.
5. Exact hard survival is decided by pulled-back decoder cone facets over all
   declared suffixes.

The relation-level runner requires permutation-valued semantic maps, reports
primitive and repeated semantic identity separately, and rejects fractional
word symbols, counts, horizons, labels, and invalid numerical tolerances.

Run the transparent tests with:

```bash
python3 -m unittest -v test_holonomy_spectroscopy.py
```

## Main formulas

For a temporal word `w=(g1,...,gk)`,

\[
P_w=M_{g_k}\cdots M_{g_1}.
\]

For a relation repeated `n` times and then suffix `v`, the final ray is the ray
of

\[
P_vP_r^n h.
\]

The target-versus-competitor decision facet pulled back through the suffix is

\[
P_v^\top(d_y-d_j).
\]

The implementation normalizes this pulled-back facet and reports its signed
spherical margin at the post-loop state. Its sign is equal to the sign of the
final normalized decoder margin because all discarded scale factors are
positive. The raw final decoder margin is retained separately to reproduce the
registered hard gate.

## Important limitations

- Nearest positive scalar identity is a full-matrix ambient diagnostic. It is
  not a causal-quotient certificate.
- If `trace(P)/d <= 0`, minimization over strictly positive scalars has an
  unattained boundary infimum at zero. The code reports this explicitly.
- A unique positive dominant eigenvalue is only a candidate projective
  attractor. Orbit-specific left-eigenvector overlap, Jordan structure,
  nonnormal transients, and finite-depth cone margins still matter.
- `frfr=(M_R M_F)^2` and `rfrf=(M_F M_R)^2` necessarily share their
  eigenvalue multisets. Ordered-path differences must therefore be attributed
  through ray orbits, eigenvectors, tangent behavior, and cone facets rather
  than eigenvalues alone.
- Directly forming an unscaled high power can underflow even when the normalized
  recurrence is valid. The implementation iterates relation blocks and
  normalizes after each block.
- Learned runs and comparisons with stored v0.3 witnesses must occur only after
  the next protocol, sources, checkpoints, and fresh episode seeds are frozen.
