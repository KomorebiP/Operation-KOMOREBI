# Target contract and attained scope

Continue from Block75, preserving its exact archive, rather than substitute a free
triangular Kummer lift for the actual depth-one representation. The immediate
predecessor's default verifier was reproduced before development and returned
PASS_DECLARED_CHECKS in 11.242384 seconds. It did not replay the whole history.

## Exact domains and hypotheses

A1. K=Q(sqrt5), O=Z7[w]/(w^2-5), k=F49, and rho:G_K->GL2(O) is the ACTUAL natural
continuous representation. det(rho)=chi_7, with the determinant character taking
values in Z7*. The reduction is [[chi,alpha],[0,1]].
A2. The ACTUAL depth is n=1: all lower entries belong to7O and the normalized
opposite class beta(g)=bar(rho21(g)/7)/bar chi(g) is nonzero. This assertion is not
extended to n>=2.
A3. In the normalized actual residual frame,
alpha=u[phi]+r[3]+[sqrt5], with u in wF7*, r in F7*, and final coefficient1.
The three Kummer generators are independent. Block75 supplies the coefficient
restriction under its named geometric inputs; the elementary independence proof
is recalled here. In particular alpha has full k-image on G_(K(mu7)).
A4. Only for classifying B under sigma: Block75's integral semilinear comparison
and its normalized endpoint frame. The main group-theoretic image theorem itself
needs only A1-A3 and the indicated cyclotomic action, not a new analytic period
comparison.
A5. Only for the eight-pattern numerical specialization: retain their old complete
bounded conductor and the proven F7-valued descended beta. This gives B=F7. No
new conductor bound or extension of that classification is inserted.

The base phi and coefficient w are different objects. K_infty means the full
K(mu_(7^infty)), NOT only K(mu7), and H=rho(G_(K_infty)) is a closed subgroup of
SL2(O). Define B=beta(G_(K(mu7))); the proof shows beta has the SAME image over
K_infty, and B has F7-dimension d=1 or2.

## Exact target achieved

For J_B={M in SL2(O): M mod7=[[1,x],[0,1]], x in k,
                      (M21/7) mod7 in B}, prove H=J_B.
Prove the full K2=ker(SL2(O)->SL2(O/49)) is contained in H, including the closure
argument at every higher precision. Compute exact finite quotient orders without
pretending to enumerate groups of order7^13.

## Routes executed

1. Reconstruct and audit Block75's endpoint/intertwiner chain, and reproduce its
   declared verifier. No internal defect was found in the displayed conditional
   chain. This is self-review, not independent acceptance of upstream geometry.
2. Try to turn its symmetry into an excluded global adjoint deformation. No
   arithmetic obstruction or actual labelled trace was obtained. A broad external
   probe for Massey/deformation results did not provide an applicable theorem for
   the twisted, fixed-local integral problem; none was used as a proof input.
3. Determine the forced cyclotomic image via actual joint residual values,
   unipotent conjugation, congruence commutators, powers, and closedness. This route
   yields the exact image theorem and removes uncertainty about the matrix-image
   group at depth one. It does not determine the arithmetic quotient map.
