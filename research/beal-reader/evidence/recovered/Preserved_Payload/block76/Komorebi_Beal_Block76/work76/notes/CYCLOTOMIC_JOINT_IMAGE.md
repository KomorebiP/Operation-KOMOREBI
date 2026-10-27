# B76.1. The actual joint image survives the full cyclotomic tower

Write G1=G_(K(mu7)), Ginf=ker chi_7=G_(K(mu_(7^infty))). On G1, both alpha and
beta are additive homomorphisms; their values are independent of the cocycle's
coboundary choice because the coefficient action is trivial there.

## Full natural residual image

The classes phi,3,sqrt5 are independent in K*/K*7. Valuations above3 and5 eliminate
the latter two exponents. If phi had a seventh root a in K, that root would be a
unit of norm-1. At the positive embedding 1<a<phi, so its integral trace a-a^-1
would lie strictly between0 and1, impossible. A nonzero exponent of phi reduces to
this case by Bezout. The degree-six extension to K(mu7) does not kill a seventh
power class: norm followed by Bezout proves injectivity.

Kummer theory gives all three independent F7-valued coordinates on G1. Since u
is a nonzero trace-zero coefficient and1 is rational, u and1 span k overF7. Thus
alpha(G1)=k. Restriction of nonzero beta to G1 is nonzero: the inflation kernel is
H1(Gal(K(mu7)/K),k(chi^-1)), which is zero by averaging over its order6. Put
B=beta(G1), a nonzero F7-subspace of k.

## Independence of the actual two values

Let W=image(G1 -> k direct-sum B), g |->(alpha(g),beta(g)). This is an F7-linear
subspace. Choose h in G_K with chi(h)=3 modulo7. Conjugation by h induces

    T(x,b)=(3x,5b)

on W. The polynomial projection (T-5I)/(3-5) preserves W and extracts the natural
coordinate; its complement extracts the opposite coordinate. Both coordinate
projections of W are surjective by their definitions. Hence W=k direct-sum B.
This is an equality of the ACTUAL joint image, not a choice of unrelated local
classes.

## Exact restriction to Ginf

For every g in G1 the commutator [h,g]=h g h^-1 g^-1 has EXACT cyclotomic value1,
because chi is an abelian character. Therefore [h,g] belongs to Ginf, not merely
to a finite cyclotomic layer. Its joint value is

    (T-I)(alpha(g),beta(g))=(2alpha(g),4beta(g)).

Both factors2 and4 are units inF7. As g runs through W, these commutator values
run through all W. Consequently

    image(Ginf -> k direct-sum B)=k direct-sum B.          (1)

No assertion that the infinite cyclotomic extension has prime-to-seven degree is
made. No compactness argument selecting compatible finite-level Galois elements
is needed for(1); each commutator already lies in the exact kernel.

In particular rho(Ginf) mod7 is the full upper unipotent U(k), and every b in B
occurs as beta(g) on some g in Ginf with alpha(g)=0. Those elements reduce to the
identity and supply the nonzero first congruence lower directions used next.

External inputs are only the stated Kummer correspondence and degree-six
inflation-restriction. The particular image and commutator arguments are proved
here. This theorem does not construct a labelled finite Galois extension for any
of the eight hypothetical arithmetic realizations.
