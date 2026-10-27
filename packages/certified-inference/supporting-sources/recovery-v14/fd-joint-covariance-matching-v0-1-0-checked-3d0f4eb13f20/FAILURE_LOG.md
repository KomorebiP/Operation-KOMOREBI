# Failure / correction log

No mathematical counterexample was found in this block.

1. A cached `.olean` was initially written beside its source, but the portable Lake project only searched `.lake/build/lib/lean`; importing the next module failed before theorem elaboration. Fixed by caching compiled modules in the actual Lake build path.
2. The minimal import set does not expose the earlier `PosDef.det_pos` route used in a heavier environment. Replaced it by the stronger available route `PosDef.isUnit` followed by `Matrix.isUnit_iff_isUnit_det`.
3. Warnings-as-errors exposed unused section `Fintype` variables. They were explicitly omitted; theorem content was unchanged.
4. The first packed-covariance assembly rewrote `K S = P Hᵀ` before applying the `XX` identity, destroying the exact rewrite pattern. Reordering the already proved rewrites closed the goal.
5. `noncomm_ring` cannot normalize products of rectangular matrices of changing dimensions. Those steps were replaced by typed matrix distributivity/associativity plus `abel`; the resulting theorem then checked.
6. The optional `FDGaussianJointParamEquality.lean` probability wrapper exceeded the execution window while loading the full multivariate-Gaussian import and produced no theorem diagnostic. It is not counted as checked.
