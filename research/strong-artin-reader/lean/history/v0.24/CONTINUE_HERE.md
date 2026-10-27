# Continue from Strong Artin v0.24

Read README.md, RESEARCH_BOUNDARY.md and MANIFEST.json. Preserve the exact
v0.23 intrinsic-syzygy branch and all dependency hashes.

The next target is NOT another abstract proof that double annihilators recover
linear images. That is now checked, including the direct presentation-level
composition with v0.23.

The nonlinear gap is exact compatibility. A residual syzygy is not necessarily
an exact integral relation. The example F(x)=(x,x^2), with syzygy (-x,1), is the
mandatory negative control. At x=2 in Z/8Z the residual horizontal target misses
the second component 4.

Two valid routes now exist:

1. SplitCompatibleHensel: construct an integral retraction onto the compatible
   target, prove F stays there on the residual fibre, and give the projected
   approximate right inverse and Taylor gain.
2. MovingRedundancyReduction: prove extra equations are exact combinations
   B(x)F(x), then remove them by the checked triangular row operation. Prove
   the arithmetic presentation/functor comparison separately.

For more general syzygies, normalize the error in the square-zero ideal at each
lifting step and prove it satisfies the correct residual relation identities.
Do not infer this from kernel equality or dimension alone.

The new sources contain 36 theorems, 11 definitions, 1 structure. Replay covers
13 direct dependencies + 7 new modules + a 47-constant axiom audit. Do not add
these to a historical cumulative total without reconciling sibling release
lineages.

Run verify.py in bounded batches as documented in README.md. No asynchronous
work is assumed to be running after this handoff.
