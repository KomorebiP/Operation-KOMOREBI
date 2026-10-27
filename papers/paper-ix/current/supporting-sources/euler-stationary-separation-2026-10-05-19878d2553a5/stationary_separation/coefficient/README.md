# Prescribed coefficient coupling: frozen continuation

Main proof: [FULL_RECURRENCE_CONTACT.md](FULL_RECURRENCE_CONTACT.md).
Current computation evidence: [certified_run_pinned/manifest.json](certified_run_pinned/manifest.json)
and [results.json](certified_run_pinned/results.json), execution root the workspace.
`certified_run/` and `certified_run_final/` are superseded after a harmless
correction of v2(322!)-floor(log2 322)=319-8=311 in the proof and explicit
checker assertions of the source-decay and stationary-lift prerequisites.

The complete actual beta cubic and finite cutoff imply balanced forcing
identities at both ordinary derivative orders. The actual normalized forcing
has valuation155, and its derivative at a stationary point has valuation156.
The actual operator square H^2 A has valuation307 and derivative valuation306.
These nonzero terms do not imply a nonzero stationary scalar: the forcing
jets are exactly balanced by twice the coefficient-index jets, and the
nonlinear product is not the square of the residual value.

The [product note](product/NEWTON_SOURCE_PRODUCT.md) supplies the exact
source product and an explicit source-specific locality counterexample.
Its [correction record](product/DEVELOPMENT_CORRECTION.md) withdraws a failed
source-umbral dictionary. The main proof and checker never use that dictionary.

The three previously fixed ordinary controls were reused solely to audit
these new assertions. No multiplier digits, additional approximation ranks,
or universal nonvanishing theorem were produced. The required new arithmetic
separation remains open.
