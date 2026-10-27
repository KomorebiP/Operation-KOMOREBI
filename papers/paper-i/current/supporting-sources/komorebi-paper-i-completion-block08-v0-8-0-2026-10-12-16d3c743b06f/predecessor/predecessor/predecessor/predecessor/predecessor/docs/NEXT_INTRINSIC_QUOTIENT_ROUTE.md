# Next block: a global-quotient-first route

**Status: mathematical restart plan. These statements have not yet been added to the accepted Lean source closure. They do not contribute to this block's theorem counts or publication coverage.**

The remaining intrinsic identification may be simpler when approached through the quotient of the entire operator module before introducing the intrinsic primary submodule.

## Global quotient

Put R=k[t] and M=`Module.AEval' T`. For an irreducible p, consider

    M / pM,

where pM is the image of multiplication by p, equivalently the literal image p(T)V on the original vector space. This quotient naturally carries the residue-field action of R/(p).

In the actual positive primary presentation, multiplication by p acts coordinatewise. A coordinate R/(q^e) has two cases.

If (q)=(p), its quotient by p is R/(p). If the ideals differ, p and q^e are coprime. Bézout gives u p + v q^e = 1, so multiplication by p is invertible in R/(q^e). Its quotient by p is zero.

Consequently the existing full-product `residueFiberMap` should induce an equivalence

    M / pM  ≃  ∏_{i : (p_i)=(p)} R/(p).

The exact kernel statement to prove on the full product is therefore `ker(residueFiberMap) = pM`. Its kernel contains all the off-primary coordinates, but those coordinates also lie in pM because multiplication by p is onto there. This observation avoids the incorrect worry that using a map from the whole product necessarily gives the wrong kernel.

This would immediately identify the fibre count with an intrinsic quotient dimension of M, independent of any presentation choices.

## Coordinate proof

One possible implementation uses the third isomorphism theorem on each quotient R/(q^e): quotienting again by the image of (p) is equivalent to R/((q^e)+(p)). The ideal sum is (p) in the matching case and R in the coprime case.

The pinned local source contains `Submodule.quotientQuotientEquivQuotientSup` in `Mathlib/LinearAlgebra/Isomorphisms.lean`, lines 191 onward. It is a candidate reusable equivalence, not an API already instantiated by this block. Alternatively, a direct coordinatewise kernel proof can use the existing quotient factor maps and Bézout coefficients.

The induced equivalence must be proved linear over R/(p), not merely over R, before it is used for the residue-field dimension formula. A module structure cannot be silently inferred from a mathematical sentence without constructing or obtaining the appropriate Lean instance.

## Bridge to the printed primary component

The printed theorem uses the intrinsic primary component

    X_p = { x | p(T)^n x = 0 for some n }.

Once the positive primary presentation is available, the p-labelled grouped factor can be identified with this submodule: powers of p kill the matching factors, while multiplication by p is invertible on all the others. One uniform sufficiently large exponent kills all the matching factors because the index set is finite.

The complementary factor is p-invertible. Hence the inclusion of X_p induces

    X_p / p(T)X_p  ≃  V / p(T)V.

Composing this with the global residue quotient gives the exact printed intrinsic multiplicity formula. This also supplies individual-fibre invariance rather than only the already-proved invariance of the maximum.

## Acceptance gates

Do not update the general single-operator record to covered until the quotient action, exact kernel, intrinsic-primary identification and dimension transport are actual compiled declarations. Tests should include a nonlinear irreducible, a repeated primary factor, a different coprime factor that disappears in the quotient, a missing primary label, and the zero module.

The algebraically closed eigenspace formula then needs the linear-factor case and the rank-nullity relation between quotient by T−λI and its kernel. The scalar-extension clause of the six-way cyclic criterion remains a further explicitly checked step.

## Scalar-extension guard

The final cyclic criterion concerns the actual tensor-extended endomorphism on the scalar-extended vector space. The minimal-polynomial preservation step must be proved for that construction. Do not substitute the false blanket assertion that the minimal polynomial of any scalar algebraic element is unchanged when the coefficient field is enlarged. The operator base-change construction and its polynomial identities need their own exact Lean statements.
