# Actual norm-weighted counting from the residue-unit witness

`NormResidueUnitCounting.lean` connects the two proved parts of the argument:
actual signed-region residue counting, and the actual ideal-residue unit
permutation.

For nonzero integral ideals satisfying

\[
(m\mathcal O_K)J\subseteq M\subseteq J,
\qquad M\subseteq m\mathcal O_K,
\]

and a supplied residue-ring unit `u` with `χ(N_m(u))≠1`, the wrapper proves the
finite mean of each signed norm weight is zero. These are exactly the means
required by `NormResidueWeightedCounting`, not means on the larger ambient
residue ring.

It then concludes a surface-order bound for the actual recombined norm-weighted
lattice count:

\[
|W_{M,J,\chi}(t)|\le B(t^{[K:\mathbf Q]-1}+1)\quad(t\ge1).
\]

Both sign portions are recombined before any later division by the number of
roots of unity. There is no hypothesis that multiplication by a residue unit
preserves an individual geometric sign region.

The specialization chooses the actual ideal `M=(m𝓞_K)J`, with `m≠0`. Its
containments and finite quotient have already been proved. The definition
`modulusNormWeightedCount` obtains its finite enumeration internally, so the
specialized bound needs neither a supplied `Fintype` nor a finite-mean premise.

The explicit unit witness remains a hypothesis. No coprimality of `J` is
required for this lattice-counting result. The separate transfer to ideal
character weights must still handle the factor `χ(NJ)`, as explained in
`IDEAL_RESIDUE_UNIT_ROUTE.md`.

The file contains three theorem declarations and one definition. Strict compilation
passed on the first attempt, exit 0, in `privatechecks/norm_unit_count_attempt1.log`.
Frozen source and proof-object hashes are recorded in
`privatechecks/norm_unit_count_hashes.json`. The file was handed to the independent
auditor for the cumulative axiom and replay checks; no separate local axiom run
was performed for this final wrapper. No predecessor source was changed.
