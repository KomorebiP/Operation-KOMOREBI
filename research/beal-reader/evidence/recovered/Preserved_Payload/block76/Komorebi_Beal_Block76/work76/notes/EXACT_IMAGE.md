# B76.3. Exact depth-one image over the full cyclotomic tower

Assume A1-A3. Let H=rho(G_(K(mu_(7^infty)))). Continuity makes H compact and hence
closed. The determinant is exactly1 on this subgroup. Put B=beta(G_(K(mu7))),
d=dim_F7(B) in{1,2}, and define

    J_B = { M in SL2(O): M mod7=[[1,x],[0,1]] for some x in k,
                           (M21/7) mod7 belongs to B }.

B76.1 makes this B the same as the beta-image on the full cyclotomic kernel.
The lower coordinate is additive on J_B: the residual diagonal entries are1.
Thus J_B is a closed subgroup, and H is contained in it.

## Exact first layer

The first congruence layer V_1 of H has lower projection precisely B. Indeed,
B76.1 realizes(0,b) for every b in B. Applying B76.2 to one nonzero seed gives
kH0 and kE12; subtracting these components from each seed gives every bE21. Hence

    V_1 = { [[a,z],[b,-a]] : a,z in k, b in B },
    dim_F7 V_1 = 4+d.                                   (7)

This is equality, not merely a lower bound. There is no scalar first direction:
determinant1 makes the first matrix traceless.

## Exact full image

B76.2 gives K_2 subset H. The reduction of H modulo7 is U(k), of order7^2. Equation
(7) says the kernel of H modulo49 -> H modulo7 has order7^(4+d). Thus H modulo49
has order7^(6+d), exactly the order of J_B modulo49. One can also see equality
without counting: match a target's residual upper value with an element of H;
its residual-identity error has a traceless leading matrix in(7), which can be
corrected by H intersect K_1. The remaining error is in K_2 subset H. Therefore

    BOX: rho(G_(K(mu_(7^infty)))) = J_B.                 (8)

This is an exact CONDITIONAL image theorem for the actual representation, not a
construction of a surjection from G_K to J_B for arbitrary input data.

## Orders of the actual finite torsion images

For j>=2, each successive K_s/K_(s+1) has order7^6. Thus

    |H mod7|=7^2,
    |H mod7^j|=7^(6j-6+d),              j>=2.             (9)

Equivalently these are the degrees of K_infty(J[7^j])/K_infty, for a hypothetical
actual realization. The field K_infty is infinite, but each torsion extension
in(9) is finite Galois. No defining equations for it have been computed.

Under the eight retained bounded patterns, beta is descended and normalized over
F7, so B=F7 and d=1. Hence

    |H mod49|=7^7=823543,
    |H mod343|=7^13=96889010407,
    |ker(H mod343 -> H mod49)|=7^6=117649.                (10)

These huge group orders follow from the universal reduction, NOT exhaustive
computer enumeration of their elements. No degree of an explicitly constructed
Frey torsion field is being reported.

## Integral semilinearity specializes B, but does not change the image proof

In Block75's endpoint-adapted frame, sigma(H)=H. Hence sigma(B)=B. A nonzero
sigma-stable F7-subspace of k is F7, wF7, or all k: the only one-dimensional
invariant lines are the +1 and -1 eigenspaces of sigma. Thus the unrestricted
arithmetic depth-one image has these three possibilities for its first lower
coordinate. Only the bounded all-inert descended case has already proved B=F7.

The image remains nonabelian and generally has nonrational coefficient traces.
It is not SL2(O) (its residual image is U(k)), and when d=1 it does not even
contain all of K_1. The matrices with lower first digit outside B are excluded.
