# Frobenius precision in the actual lattice

Block 56, version 5.6.0. Written proof under the explicit input contract.
This is not a Lean certificate or an independent review of the inherited geometry.

## B56.1. The trace and determinant gain the norm-congruence depth

Let O be the unramified quadratic integer ring over Z_7, with valuation w(7)=1.
Let F be the actual rank-two Frobenius at a good place v away from 7. Write
Q=Nv, h=v_7(Q-1), n for the actual global lattice depth, and

    m = floor(n/2)+1,             r = min(n, m+h).

The inherited global diagonal character gives, in the same actual basis,

    F = [[a,b],[7^n c,d]],
    det(F)=Q,
    a = Q eta(F) mod 7^n,
    d = eta(F)^(-1) mod 7^n,
    eta(F) = 1 mod 7^m.

Then

    tr_E(F) = Q+1 mod 7^r,                         (1)
    det_E(1-F) belongs to 7^r O,                    (2)
    P_v(T) = (T-1)^2(T-Q)^2 mod 7^r,                (3)
    7^(2r) divides #J^nu(F_Q).                      (4)

Here P_v is the characteristic polynomial on the underlying four-dimensional
Q_7 representation. Formula (3) is a congruence, not an equality of matrices.

### Proof

Choose a lift eta=1+u in O with u in 7^m O. In the quotient modulo 7^n,

    tr_E(F)-(Q+1)
      = Q(1+u)+(1+u)^(-1)-(Q+1)
      = (Q-1)u + u^2/(1+u).

The two terms have valuations at least m+h and 2m. Since 2m>n, the claimed
precision is min(n,m+h), proving (1). The elementary identity

    det_E(1-F)=1-tr_E(F)+det_E(F)

proves (2). Alternatively, (1-a)(1-d)-7^n bc gives the same bound directly.

The rank-two characteristic polynomial is T^2-tr_E(F)T+Q. Its norm from
E to Q_7 is the characteristic polynomial after restriction of scalars.
Both conjugates are congruent to (T-1)(T-Q) modulo 7^r, proving (3).
Taking the norm of (2) proves (4), because Norm(7^r)=7^(2r). Good-reduction
Frobenius identifies that norm with the finite Jacobian order. QED.

The classical Frobenius/order identification is checked in
source_records/SOURCE_CHECK.md. It does not supply the actual diagonal
precision. That precision is the inherited Block 53 hypothesis.

## Corollaries used here

At n>=2 the character is trivial at least modulo 49. At every good place,
P_v is therefore congruent to the split target modulo 49.

At n>=3 and h>=1, m>=2 and r>=3. The target congruence holds modulo 343,
and the Jacobian order is divisible by 7^6.

At both auxiliary rational primes in this block, h=2:

    q=197: f=2, Q=38809, v_7(Q-1)=2;
    q=491: f=1, Q=491,   v_7(Q-1)=2.

The first improves the old general order bound 7^(2m): at depth three,
m=2 but r=3. No value of an independently chosen ray character is inserted.

## Precision boundary

One cannot remove the minimum with n. At n=2, Q=491, the integral matrix

    F = [[540,1],[49,1]]

has determinant 491 and the required diagonal entries modulo 49, but its
trace exceeds Q+1 by 49, not a multiple of 343. This is a local algebraic
control, not an actual Frey reduction.

The new theorem neither increases n nor produces the next actual diagonal.
