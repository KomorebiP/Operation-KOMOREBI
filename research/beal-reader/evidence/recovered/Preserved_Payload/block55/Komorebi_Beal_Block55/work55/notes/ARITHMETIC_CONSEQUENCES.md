# Arithmetic consequences of the maximal-order criterion

All arithmetic conclusions retain the complete Block54 geometric hypotheses.
The finite prime sets below bound only high-congruence divisors, not all
prime divisors of C. Low-congruence divisors can be arbitrarily large.

For q outside2,3,5,7 let f_q be its residue degree in K=Q(sqrt5), and put
h_q=v_7(q^f_q-1). Define the rational high-congruence support

    H(C)={q|C, q not in{2,3,5,7}, h_q>=2}.

Both prime ideals above a split q are included in the matrix test. This is
a conservative possible-support set, not a claim of paired ramification.

## B55.6. Full diagonal triviality on an expanded support class

Let

    H_*={197,491,883,1471,1667}.

If H(C) is contained in H_*, then

    eta_n=1 mod7^n,              n<=2.                     (A)

Proof. Every member of H_* has h_q=2. The full seven-column matrix, in order
197(inert), both491, 883(inert), both1471, 1667(inert), is

    0 4 3 0 5 2 0       phi
    1 1 1 1 1 1 1       2
    6 5 5 0 5 5 3       3
    6 6 6 0 2 2 4       sqrt5
    6 4 4 3 2 2 2       7.

The exact residue computations and all 42 restricted ranks pass B55.3.
For a smaller H(C), zero sets only lose columns, so injectivity is preserved.
All omitted variable primes have h<=1 and cannot ramify in eta by Block54.
The criterion therefore gives full triviality at arbitrary n.

Beta must ramify at some variable place. At such a place its inertia order
in eta is7^s, with n=t+2s. Trivial eta forces s=0 and n=t. The inherited
same-basis Frobenius equation then gives h>=n. Since every eligible place
has h<=2, n<=2. QED.

At depth2, any actual beta-supporting rational prime belongs to H_* and

    t_q=2,       v_7(v_q(C))=1.                            (B)

Thus its multiplicity in C is divisible by7 but not49. At least one such
supporting prime exists. If every multiplicity at H(C) is prime to7, depth2
is impossible, so n=1. This remains a conditional multiplicity consequence.

The result does NOT eliminate beta or depths1 and2. At883 all three Kummer
symbols vanish, and no coefficient contradiction follows merely from a
possible beta-support place there.

## B55.7. Stronger than the previous four-place statement

The same argument proves eta_n=1 at EVERY depth if H(C) is contained in
{491,1471}. Block54 had excluded depth3 when all variable divisors belonged
to P0 union{491,1471}. The new statement both kills the entire diagonal
correction and permits arbitrary additional divisors with h<=1.

The numerical conclusion remains n<=2 on this subcase. It would be incorrect
to count that repeated numerical bound as a fresh elimination of depth2.
The new mathematical content is the all-depth character triviality and the
relaxed support hypothesis.

## B55.8. A mixed h=2/h=3 class

The exact test also passes for

    H_3={197,491,883,1373,1471}.

The prime1373 is inert and v_7(1373^2-1)=3. All other members have h=2.
If H(C) is contained in H_3, then eta_n=1 and n<=3. At n=3, beta must be
supported at the unique prime above1373. Consequently

    v_7(v_1373(C))=2,
    a_3/a_5=1.

The first equality follows from n=t. The second follows from its natural
Kummer row (0,3,4): 3a_3+4a_5=0. The unit coefficient a_phi is not determined.
The support theorem ensures that at least this prime ramifies in beta at
n=3; it does not show that an actual depth3 configuration exists.

## B55.9. Complete declared finite classification, not a bound on C

The illustrative universe is

    U={97,197,293,491,587,883,1373,1471,1567,1667}.

It contains ten rational primes and twelve prime ideals. All 1024 rational
subsets were tested. The criterion passes on124 and leaves a nonzero first
layer on900. There are eight maximal passing sets and fifteen minimal
surviving rational supports. Full data and witnesses are in the exact JSON.

Every passing set proves eta=1 provided H(C) is contained in it. Then
n<=max(1,max_{q in H(C)} h_q), using beta's required ramification. A passing
empty high support gives n=1. No part of this enumeration proves H(C) is
contained in U, bounds its cardinality, or exhausts all possible C.

The compatible column circuits comprise six of size2, eight of size3 and
nine of size5. Six have natural Kummer rank1; seventeen have rank2. When a
rank2 circuit lies in an ACTUAL maximal-order support, B55.5 forces normalized
coefficients into F7. It does not show that every actual support contains such
a circuit.

## A surviving first layer that must not be discarded

At the inert primes97 and293, both h=2, the five-row mod7 columns are both

    (1,0,0,0,0)^T.

The character vector(6,1) lies in the kernel. The natural class
alpha=(0,1,1) is annihilated at both places and respects a_3*a_5!=0. Thus this
first-layer system is genuinely nonempty. The associated order7 abstract
ray character has the fixed-prime splitting relations, by class field theory.

The computation does NOT identify it with the actual Frey diagonal or provide
its compatible matrices, full local Frobenius values, or a Diophantine
solution. Its role is to refute a proposed UNIVERSAL vanishing inference from
this criterion alone. The next block needs an additional representation-
specific relation at such surviving supports, not another claim that the
kernel must always be zero.
