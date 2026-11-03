# Route and implementation notes for SF-LEAN-B05

The scalar-series route from TARGET.md succeeded. Padding even degrees with
zero turns the sparse ordinary odd sum into a standard scalar Taylor object.
The exact HasSum reindexing theorem made a separate convergence-radius or
termwise high-derivative estimate unnecessary. Taylor uniqueness then extracts
all coefficients rather than just the six needed for the finite inverse.

The first scratch compilation rejected two arithmetic steps because omega
saw unreduced lambda applications in the injectivity and range-witness goals.
Explicit `change` statements exposed the natural-number arithmetic. No
mathematical premise or conclusion changed. The completed production module
compiled with warnings treated as errors before the full replay began.

The first fresh replay used `Type mismatch` as the expected diagnostic for
the omitted-defect fixture. The pinned compiler reports `Application type
mismatch`, with a lowercase t. The fixture expectation was corrected to that
exact message. Its rejected run and original control manifest are retained
under `attempts/inverse-replay-001/`; the accepted replay uses a new directory.
No production theorem changed, and no earlier receipt was overwritten.

Iterated differentiation remains deferred: it would require the appropriate
local uniform convergence bounds for every differentiated series. The
leading-term route remains deferred: it would require an isolating tail
estimate. Neither route is refuted, and neither is needed for the resolved
target. They may become useful for quantitative estimates later.

The nonzero-defect guard and labels remain explicit. The retained exceptional
example concerns finite jets. No computational sample or interface failure is
used as proof of an analytic counterexample. Placeholder code is confined to
the deliberately rejected fixture.
