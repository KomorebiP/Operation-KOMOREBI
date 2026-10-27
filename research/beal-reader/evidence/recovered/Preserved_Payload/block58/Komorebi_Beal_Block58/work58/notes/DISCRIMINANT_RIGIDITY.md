# Rank-two Frobenius precision and discriminant rigidity

## B58.6. General discriminant-collapse lemma

Let O be an unramified quadratic extension of Z_7, with nontrivial
automorphism sigma. Let Q>0 be an integer prime power. Suppose a good
rank-four Frobenius polynomial has the actual factorization

    P(T)=(T^2-tau T+Q)(T^2-sigma(tau) T+Q)
        =T^4-S T^3+C2 T^2-Q S T+Q^2

with integral coefficients, tau in O, and all four roots of complex
absolute value sqrt(Q). Suppose moreover

    tau=Q+1 mod7^r O.                                    (3)

Define the integer

    D=S^2-4(C2-2Q).

Then

    D=(tau-sigma(tau))^2,
    7^(2r) divides D,
    0<=D<=16Q.                                          (4)

Proof of integrality/divisibility. S=tau+sigma(tau) is an integer and
C2-2Q=tau*sigma(tau) is an integer. The displayed identity follows by
expansion. Equation(3) is preserved by sigma. Thus the difference is in
7^r O, and its square in7^(2r) O. Since O is unramified, intersection
with Z gives integer divisibility by7^(2r).

Proof of the real bound. Tau satisfies the monic integral quadratic
Z^2-SZ+(C2-2Q), so it is algebraic even if initially described p-adically.
Under either complex embedding of its trace field, T^2-tau T+Q divides
P(T). Its two roots alpha,beta have product Q and magnitude sqrt(Q).
Hence beta is the complex conjugate of alpha and their sum is real,
with absolute value at most2sqrt(Q). The same holds for the other trace.
Their difference is therefore real, of absolute value at most4sqrt(Q).
Squaring gives the bound in(4). No unrestricted semilinear comparison of
Frey lattices, nor an assumption that tau belongs globally to Q(sqrt5),
is used in this bound.

If7^(2r)>16Q, (4) forces D=0. Then tau=sigma(tau)=S/2 is rational and
integral, hence an integer a, and

    P(T)=(T^2-aT+Q)^2,
    |a|<=2sqrt(Q),       a=Q+1 mod7^r.                   (5)

This is a written proof, not an inference from a finite scan of polynomials.
The classical Weil magnitude statement and curve/Jacobian trace formulas
are documented in SOURCE_CHECK.md. The actual factorization and congruence
are inherited representation inputs.

## B58.7. Every depth at least three forces bad2549

The integer2549 is prime (trial division through50), splits in K because
2549=4 mod5, and

    2549-1=49*52,       h=v7(2549-1)=2.

Suppose n>=3 and2549 does not divide C. It would be a good place with
Q=2549. Block56's actual trace precision gives

    r=min(n,floor(n/2)+1+h)>=3.

Use r=3 in B58.6. The constants are

    7^6=117649 >16*2549=40784,
    floor(2sqrt(2549))=100,
    Q+1=2550=149 mod343.

There is no integer a in[-100,100] congruent to149 modulo343. Equivalently,
the two nearest representatives are149 and-194. Equation(5) is impossible.
Therefore

    n>=3 =>2549 divides C.                               (6)

No point counts at2549 are performed or needed. This is not just a generic
Weil magnitude bound: it also uses the scalar congruence on the SAME
rank-two trace. At the bad prime2549, h=2 rather than0, so the new result
does NOT supply local triviality or another pi2549 reciprocity row.

## Necessary negative control: quartic congruence alone is insufficient

At Q=2549 take

    tau=-47+49phi, sigma(tau)=-47+49(1-phi),
    S=-45, C2=2603,
    P(T)=T^4+45T^3+2603T^2+114705T+6497401.

Here D=5*49^2=12005. Both real traces have magnitude less than2sqrt(Q):
sqrt(D)<110, so the larger absolute trace is less than155/2, and
155^2<16Q. Each quadratic therefore has Weil roots of magnitude sqrt(Q).
The polynomial factors over the prescribed coefficient field and satisfies

    P(T)=(T-1)^2(T-Q)^2 mod343.

Nevertheless tau-Q-1=49(phi-53) is NOT divisible by343 in O, and D is
NOT divisible by7^6. Thus the rank-four congruence cannot replace(3).
This is a generic Weil polynomial, not an asserted Frey reduction or a
constructed abelian variety. It falsifies the missing implication exactly.

The complete reciprocal-integer scan in the declared Weil coefficient
interval leaves18 quartic-mod343 candidates, but none satisfying the stronger
D-divisibility. The scan is a control; the universal proof is(4)-(5).
