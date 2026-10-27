# Block 52 target contract

Release: v5.2.0. Research date: 19 September 2026.

The authoritative predecessor is the complete Block 51 archive:

`Komorebi_Beal_Block51_Monodromy_Depth_v5.1.0.zip`

SHA256: `2db43f22efa22e5e21ee2359eb132d4744a18c60dda39792f57f12a3385c5fd6`.

That archive contains the recovered Blocks 49 and 50, both original archives,
and their distinct review statuses. This block neither reconstructs nor edits
any predecessor. The original Block 51 ZIP is included byte for byte.

## Original objective

Constrain the actual global stable-lattice depth or calculate the natural
Kummer coordinates and higher diagonal character in compatible global bases.
Test their coupling in the ordinary depths one and three. A generic residual
extension, an independently normalized local coefficient, or a numerical
non-solution is not an answer to this objective.

The underlying goal remains elimination of the reducible branch of
A^3+B^5=C^7. Neither elimination of that branch, the complete signature, nor
full Beal is a claimed outcome of this bounded block.

## Fixed input contract H

H1. A,B,C are positive pairwise-coprime integers, A^3+B^5=C^7, and 3990|C.
The Jacobian J comes from the specific curve

    y^2+(x^3+B)y = 2Bx^3+3Ax+B^2,
    equivalently Z^2=X^6+10BX^3+12AX+5B^2.

H2. K=Q(sqrt5), phi=(1+sqrt5)/2, E=Q_7(sqrt5), O=Z_7[phi], k=F_49.
The prime 7 is inert. The rank-two RM Tate representation, twisted by the
even quadratic character nu of Q(zeta15)^+/K, has determinant chi_7 and
natural residual orientation 0 -> k(chi) -> Vbar -> k -> 0.
The underlying four-dimensional representation is restriction of scalars.
Good reduction and the unramified quadratic twist have the usual Frobenius
compatibility at the auxiliary primes in this block.

H3. In the one global Frobenius-at-three eigenbasis established in Block 51,

    rho(g) = [[a(g),b(g)],[7^n c(g),d(g)]],
    a mod7 = chi, d mod7 = 1,

where n>=1 is the actual finite segment depth, not an adjustable modulus.
Its natural and opposite endpoint classes are alpha and beta. The latter is
nonzero and must ramify at an eligible prime over a divisor of C.

H4. The natural Kummer class has the global expansion

    alpha = a_phi[phi] + a_3[3] + a_5[sqrt5],   a_3*a_5 != 0 in k.

This is the Kummer group tensored with k, not exponentiation by elements of
F_49. The coefficients are fixed together, up to one common nonzero scalar.
The inherited finite-flat/natural-lattice and class-number inputs giving
this expansion are not newly proved by point counting.

H5. The Block 51 local equality and endpoint criterion hold at an actually
ramified variable place: t=1+v_7(v_q(C)), h=v_7(q^f-1), and

    n=t+2s, 0<=s<=h.

For eligible places the natural local class is zero below t+2h and nonzero
at t+2h. The coupling identity is

    [alpha] cup [beta] = -delta(a mod7^n).

All five hypotheses refer to the inherited written mathematical arguments,
not new Lean certificates. Different new conclusions require different
subsets of H; the theorem index makes these dependencies explicit.

## Executed routes

1. A determinant/norm obstruction translates depth >=2 into divisibility of
actual finite-field Jacobian orders. It yields fixed-prime constraints.
2. Exact scalar Frobenius at good 13 gives a compatible global Kummer
coefficient, and a local value of the actual higher diagonal character.
3. Local seventh-power relations at 29,43,71 couple those same global
coefficients to the depth-one support condition and to old ray examples.

The computational range is exactly q in {13,29,43,71}, plus the stated
symbol/matrix controls. Any future enlargement is a new run, not implicit
coverage. Timeouts are inconclusive and never count as empty residue sets.
