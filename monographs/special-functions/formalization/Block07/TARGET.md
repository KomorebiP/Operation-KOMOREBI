# SF-LEAN-B07 target contract

Base checkpoint: `ac74a88377d7c5a4daa8bc463d3f45629277e192`.
Source: the characteristic-exponent and positive-vector section of
`monograph/sections_v11/coupled_growth_full.tex` (before Theorem F.2).

For labeled real scales 0<q,r,a,b<1, prove a unique rho>0 satisfying
(1-q^rho)(1-b^rho)=(ar)^rho, with real powers. For
P(t)=[[q^t,r^t],[a^t,b^t]], prove the stated positive right and left
eigenvectors, max-normalize the right vector, identify the second eigenvalue
q^rho+b^rho-1 and its absolute-value bound, and establish the actual complex
matrix spectral-radius characterization. Matrix rows, columns, and scalar
extensions must be explicit. These are prerequisites for F.2, not its order
or type bounds.

Primary route: continuous strictly increasing determinant balance on t>=0,
its signs at zero and infinity, then IVT and uniqueness. Explicit 2x2
determinant/spectrum algebra handles the eigenvectors and spectral radius.
First discriminators: the pinned real-power limit/monotonicity APIs and
the exact matrix spectrum API. Success requires proof terms, fresh replay,
source and I/O inventories, and calibrated current records.

Alternatives: general positive-matrix spectral-radius monotonicity followed
by IVT (first uncertainty: comparison and continuity APIs), or logarithmic
scalar parametrization (first uncertainty: a cleaner invertible-variable
monotonicity contract). Both remain available if the explicit route stalls.
Boundary tests include t=0, a scale equal to one, the all-half tuple, and
the existing rational tuple with characteristic exponent one. Numerical
eigensolvers or sampled roots cannot prove the universal target.

Scope excludes analytic order, lower order, type bounds, Perron proportions
for growth type vectors, operator decoupling and whole-monograph coverage.
Review is self-review; all existing proof blocks and manuscripts are preserved.
