# B73.4. The [7] adjustment is forbidden in the actual trace/inertia fibre

A fibre here means the collection of framed mod49 representations satisfying
specified COMPLETE data, not a set determined by the current finite trace tables.

Let rho,rho' over O/49 have:
(1) the same fixed residual [[chi,alpha],[0,1]] and determinant chi;
(2) the same normalized lower-entry beta cocycle;
(3) the same O/49-valued trace for EVERY g in G_K;
(4) the same mod49 inertia matrices at every finite place except seven;
(5) local lifts modulo343, with the actual toric hypotheses at a common
beta-supporting place v where [phi]=0 and [7]!=0 in the local seventh Kummer group.
For their fixed-seven valuation comparison, assume both are locally toric at seven.

Then their difference has the form

    rho'=rho+7*xi*E12, [xi] in k[phi],

and their fixed-seven valuation defects are EQUAL. In particular the valuation
cannot be tuned by a nonzero multiple of [7] while retaining all these data.
No finite bound on the remaining conductor is used in this comparison theorem.

## Proof of the reduction to an upper correction

Write rho'=(I+7Y)rho. As in B73.1, Y is an adjoint cocycle. Determinant equality
gives tr Y=0, and equality of the lower-entry cocycles gives Y21=0. Write
Y=[[p,q],[0,-p]]. The adjoint formula shows p is an ordinary additive character.
Trace equality gives (chi(g)-1)*p(g)=0 for every g. Choose h with chi(h)!=1.
Then p(h)=0. For any g with chi(g)=1, both gh and h have nontrivial character,
so p(g)=p(gh)-p(h)=0. The other g already satisfy p(g)=0. Hence p=0 everywhere,
and q=xi is a k(chi) cocycle. This uses complete trace equality, not finitely
many good Frobenius congruences or merely the rational quartic norm of a trace.

## The inertia conditions leave just [phi] and [7]

By Kummer theory, H1(K,k(chi))=k tensor_F7 (K*/K*7). The inertia restrictions
away from seven record the prime valuations modulo7. Condition(4) makes all
those valuations vanish. Since O_K=Z[phi] is a principal ideal domain and7 is
inert, the class must lie in

    [xi]=a[phi]+b[7].                                    (14)

For completeness the class-number/unit statements have elementary proofs.
Round both coefficients of an element in the basis1,phi to integers. The error
a+bphi has |a|,|b|<=1/2, so |Norm(a+bphi)|=|a^2+ab-b^2|<=3/4<1. This is a norm
Euclidean division, hence a principal ideal domain. Its units are +/-phi^m:
rescale a positive real embedding into [1,phi). A norm+1 unit there has integral
trace in[2,sqrt5), forcing1. A norm-1 unit would have integral trace in[0,1),
forcing an impossible additional unit in this interval. Finally7 is inert because
T^2-T-1 has nonsquare discriminant5 modulo7. No class-group correction is omitted.

At v, the class [xi] is unramified and evaluates as b[7](F), since [phi]=0.
Equation (12) forces this value to vanish. Since [7](F)!=0, b=0. Thus the local
valuation of xi at seven is zero. Equation (8) gives equal nu_7. QED.

For two actual Frey lifts in such a fibre with the same residual alpha, equation
(6) also forces (v7(C))^2=(v7(C'))^2 mod7, after eliminating the unspecified local
signs. This is a COMPARISON condition, not a zero-valuation or depth bound.

## Application to all eight frozen patterns: a common detecting prime

Every retained pattern has nonzero beta inertia at the inert prime883. In its
base residue field F_(883^2), direct exact symbols are

    phi^((883^2-1)/7)=1,
    3^((883^2-1)/7)=1,
    (sqrt5)^((883^2-1)/7)=1,
    7^((883^2-1)/7)=296 !=1.                              (15)

The last element has exact order7. Already over F883 one has7^126=749!=1.
Moreover v7(883^2-1)=2, so equation (9) is [A,M]=0 at this place.

Consequently every nonzero [7] upper shift of an ACTUAL candidate, with inertia
unchanged, fails local liftability modulo343 at883. Even adding arbitrary
combinations of the three old unit classes phi,3,sqrt5 cannot cancel this
specific local value, because their three symbols are all1 there. General
extra Kummer generators or changes to full inertia are not covered by that last
restricted-span statement.

## What is NOT proved

This theorem does not say nu_7=0. It says that nu_7 is fixed AFTER complete traces,
lower cocycle, and inertia are fixed. We have not calculated that full global
fibre for any of the eight residual patterns. An arbitrary auxiliary triangular
reference is NOT another actual point in this fibre: it has beta=0 and different
inertia. Comparing with its zero valuation to force7|v7(C) would be invalid.

Thus no pattern is eliminated. The theorem turns an apparent free uniformizer
parameter into a compatibility problem for the SAME integral representation.
