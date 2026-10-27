# Arithmetic consequences and exact quantifiers

All results retain TARGET_CONTRACT.md. Define

    H(C)={q|C : q outside{2,3,5,7}, v7(q^f_q-1)>=2},
    U={97,197,293,491,587,883,1373,1471,1567,1667}.

## Unconditional within the retained representation branch

For all possible C and all high-prime supports,

    n>=2 =>41*59 divides C,
    n>=3 =>2549 divides C.

These are necessary divisibilities, not contradictions or an upper bound
on C. In particular no contradiction is drawn from the size of their product.

If eta is nontrivial, its highest nonzero layer MUST ramify at some prime
outside U. Both former five-place patterns, and every other highest layer
supported above U, are excluded. Arbitrary additional C divisors are allowed.
Additional highest-layer ramification outside U is not excluded.

## B58.8. Complete high-divisor support in U has depth at most two

If COMPLETE H(C) subset U, then2549 does not divide C, since2549 itself is
high, with h=2, and is not in U. B58.7 now gives

    H(C) subset U => n<=2 and eta=1 mod7^n.               (7)

The diagonal is already fully trivial at depths1,2 by the inherited precision.
This proves(7) independently of the new rank computation, and the rank
computation independently explains why no nontrivial highest layer remains.

Arbitrarily many additional divisors with h<=1 are permitted. The theorem is
NOT restricted to C whose only prime factors lie in U. The former n3 case
with beta supported only at1373 is now excluded under COMPLETE H(C) subset U:
it would force the additional high divisor2549 outside that set.

At depth2 beta must still ramify somewhere. Since eta=1, the inherited local
inertia formula gives s=0,t=n=2. At such a supporting prime q,

    v7(v_q(C))=1,
    h_q>=2,
    alpha|G_v=0.

Thus at least one high prime has multiplicity in C divisible by7 but not49.
If every high-prime multiplicity is prime to7, only n1 remains. The depth2
multiplicity condition itself is NOT a contradiction.

## Boundaries

Eta=1 does not imply beta=0. The nonzero opposite extension and its actual
geometric realization at depths1 or2 remain open. No bound on arbitrary H(C)
has been proved. A general nontrivial highest layer outside U is unclassified.
The new prime2549 need not ramify in eta or beta just because it divides C.
In particular it has not automatically been identified with the outside-U
highest-layer place whose existence follows from the separate rank theorem.

The CM nonboundary rational-point problem, higher Hilbert levels, full
(3,5,7) signature, and full Beal are separate unresolved obligations.
