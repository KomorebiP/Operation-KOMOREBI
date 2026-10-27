# B78.1. The exact first-stage affine condition at a beta-supporting toric place

Retain the Block 77 target contract and actual depth one. Let v be a variable
place of residue characteristic different from 7 at which beta is ramified. Let
Q be the residue cardinality. The inherited local geometry gives Q=1 mod 7,
natural monodromy content t=1, and residual alpha|G_v=0.

Choose a compatible pro-7 tame generator T and arithmetic Frobenius F with

    F T F^-1 = T^Q.

Write

    h=(Q-1)/7 mod 7,
    c=beta(T) in k^*,
    b=beta(F) in k.

Because alpha is identically zero on this local group, the first-stage equation
`dp=-alpha cup beta` says that p is a local homomorphism.

## Toric normal form

Modulo 49 write

    rho(T)=I+7M,
    rho(F)=I+7A.

The one-order-later tame relation and exact toric trace give

    M^2=0, M_21=c !=0, [A,M]=h M, tr(A)=h.

Every such packet has a unique theta in k and a free Frobenius lower value b with

    M=c [[theta,-theta^2],[1,-theta]],

    A=[[theta*b, theta*h-theta^2*b],
       [b,       h-theta*b]].

Use the Block 73 auxiliary upper triangular reference. Its diagonal first digit
at T is zero and at F is (h,0). Hence

    p(T)=theta*c,
    p(F)=theta*b-h.

Eliminating theta gives the invariant affine equation

    BOX: c*p(F)-b*p(T)=-h*c.                              (1)

Conversely, for c !=0, any pair p(T),p(F) satisfying (1) determines
`theta=p(T)/c`, and the two displayed matrices give a first-order toric packet
with the required p-values. Thus, at this first-order level, P_v^geom is a
nonempty affine hyperplane.

## Independence of the Frobenius lift

Replacing F by T^m F changes

    b -> b+m c,
    p(F) -> p(F)+m p(T).

The left side of (1) is unchanged. Therefore (1) depends on the local
representation, not on the chosen Frobenius lift.

The theorem does not determine theta, b, or a global p. It does not assert that
every first-order packet lifts to the actual Frey representation at all higher
precisions. Those are separate local/global conditions.

The two implementations exhaust all 7*48*49*49=806736 tuples
(h,c,b,theta), verify the normal forms, (1), Frobenius-lift invariance and the
one-order-later commutator relation.
