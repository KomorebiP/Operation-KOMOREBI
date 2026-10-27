# Current evidence and development corrections

Current proof: `CONSTRAINED_TANGENT_AND_CONTIGUOUS_CONTACT.md`.
Current recorded run: `frozen_run/manifest.json` (validated against the
workspace root). `certified_run` is a successful historical run superseded
because the proof source locator changed from Section4 to Section3 and the
current-evidence path changed. Its old proof pin is intentionally stale.
`DEVELOPMENT_CHECK.json` is exploratory and is not the current certificate.

The first runner invocation was rejected before computation because the
contract omitted the required `mathematics.inputs` field. The contract was
corrected before either successful run; no mathematical result came from
the rejected invocation.

Two preliminary mathematical estimates were corrected before the recorded
run. Using packet1 alone missed its actual stationary cancellation against
the leading upper packet. In the corrected sum, omitting packet162 then
gave a wrong low unit. The proof records the final exact valuations and
units, and the independent replay confirms those displayed values.

The recorded computation tests three fixed actual indices, including a
critical value of valuation91. It neither searches for new digits nor
proves universal critical-value nonvanishing. The uniform normal-direction
identities are proved by exact packet arithmetic. The adjacent-index
contact identity is exact and still contains the unknown critical scalar.
