# Carry-adapted Padé computation: development and interpretation

Only the two already fixed ordinary parameters T=0 and T=718787533 were
used. The inherited actual local records are comparison data, not substituted
for the new actual coefficient reconstruction. Every reconstructed actual
local coefficient is compared after reduction to the available78 local bits.

An initial rank3 execution rejected an unnecessarily strong implementation
assertion that all Padé denominator coefficients should be even. The rank3
denominator contains a unit coefficient. The correct convergence condition is
integrality: the exact source conversion already supplies8^t. The assertion
was corrected to permit integral coefficients, and the final checker verifies
the sharper structural conclusions that the last denominator coefficient has
valuation1 and all positive-index model moments are even. This was a failed
implementation assumption, not evidence of failure of the convergent model.

The final run checks ranks1 through10, moments through offset20, and next
Hankel determinants through size11. Cramer denominators lose at most9 bits
from384-bit input moments, leaving more than256 bits for each integral ratio.
No unrecorded numerical tolerances, floating point arithmetic, or randomness
are used. Exact source coefficient bounds control every omitted source term;
the model tail starts at t=cutoff-160 with3t>=256. The source chart has slope
2^15, so local coefficients above degree17 vanish at global precision256.

The model critical centers are determined modulo2^77. Exact stationarity and
the local quadratic bound make substitution uncertainty at least154 local
bits, beyond the78 local bits retained. Named assertions test strict transfer
for T=0 at rank3 (critical valuation0, error7) and T=718787533 at rank6
(critical valuation30, error31). These certify previously known values by a
new approximation. They do not enlarge the tested parameter set or prove
universal critical nonvanishing.

The proof separates the carry-range kernel theorem from the source-chart
error theorem for ranks1..10. In particular, denominator integrality includes
d=2^639, but the first-error valuation1 requires d<2^639; at the endpoint the
first actual moment crosses the carry and the first-error valuation is-1.

The accompanying certified manifest and logs pin the final executable,
proof, inherited data, vendored engine, and this record. Runtime fields in
otherwise identical replay outputs may vary.
