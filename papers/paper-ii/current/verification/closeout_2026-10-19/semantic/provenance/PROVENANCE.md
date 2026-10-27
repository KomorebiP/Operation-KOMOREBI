# Divided difference cycle holomorphy

`ReleaseCycleDSlope.lean` generalizes the analytic estimates in Chris Birkbeck's
Apache 2.0 licensed `DslopeIntegral.lean` from scalar complex functions to
functions with values in an arbitrary complete complex normed space. The
authenticated upstream source is preserved as `UpstreamDslopeIntegral.lean`.

Upstream repository: `CBirkbeck/AINTLIB`

Upstream commit: `2931529d8d72c086f2b5f58c33d25352dc301b16`

Upstream path:
`projects/LeanModularForms/LeanModularForms/ForMathlib/DslopeIntegral.lean`

Upstream blob SHA: `2b50aeb218838f86f4c8d1351e9925d73afe3dea`

New local results establish symmetry of divided differences, identify the
derivative in one node with the repeated divided difference at that node, and
combine these facts with the actual cycle parameter integral theorem. The main
result is
`Komorebi.PaperII.ReleaseCycleDSlope.differentiableOn_lineIntegral_dslope`.

The theorem requires an open complex domain, a holomorphic Banach-valued
function on that domain, and containment of the cycle trace in the domain.
It assumes no conclusion about the holomorphy of the cycle integral. It applies
to the integrable velocities in `IntegralCycle`, without an extra smoothness
or uniform velocity bound.

Strict compiler check on 2026-10-19: PASS with Lean 4.34.0-rc2, warnings as
errors, autoImplicit false, relaxedAutoImplicit false, maxSynthPendingDepth 3,
one compiler thread. After the comment-only Apache modification notice was added, the final strict replay took 8.538 seconds. The axioms audit passed again in 1.812 seconds.

Checked source SHA256:
`f173f1f5a91fda427e40d6f10745701061663a69807b4a033cdb86fbe169965c`
