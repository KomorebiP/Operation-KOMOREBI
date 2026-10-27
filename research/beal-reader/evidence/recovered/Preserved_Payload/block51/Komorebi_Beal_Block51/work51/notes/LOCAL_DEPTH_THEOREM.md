# Integral monodromy controls the depth of an opposite extension

**Block 51. Written proof, with exact computational checks of its algebraic
identities and examples. Not a Lean certificate.**

The new theorem is independent of Block 50's unfinished extension-geometry
audit. Its application uses the explicit, inherited arithmetic hypotheses
listed in `ARITHMETIC_SUPPORT.md`. Throughout, a lattice means a free
rank-two module over the indicated discrete valuation ring, not a
semisimplified representation.

## 1. Local theorem

Let O be a discrete valuation ring of characteristic zero, with uniformizer
pi and normalized valuation w(pi)=1. Let F be in GL_2(O), let Q be an O-unit
with Q != 1, and let N be a nonzero matrix in M_2(O). Assume

    N^2 = 0,       FN = QN,       NF = N.                  (1)

Fix the displayed integral basis. Put

    t = min_ij w(N_ij),       h = w(Q-1),

where w(0)=infinity. Suppose an integer n >= 1 satisfies

    w(N_21) = n,       F_21 in pi^n O.                    (2)

Then there is an integer s with

    0 <= s <= h,       n = t + 2s.                       (3)

In particular

    t <= n <= t + 2h,       n == t (mod 2).              (4)

No assertion in (3) is a statement about a bounded enumeration. The proof
below works over O, including the unramified quadratic integer ring over
Z_7 used in this project.

### Proof

Since N is a nonzero nilpotent endomorphism in dimension two, its image and
kernel over the fraction field coincide in a line. Choose a primitive
integral generator u=(x,y)^T of the intersection of that line with O^2.
Thus x and y are integral and at least one is a unit.

Every column of N is a multiple of u by an element of O: inspect a unit
coordinate of u. Write N=u l, where l is an integral row. Since l u=0 and
u is primitive, l is an integral scalar multiple of the primitive row
(-y,x). Consequently, for a nonzero m in O,

    N = m [[-xy, x^2], [-y^2, xy]],       w(m)=t.         (5)

The equality w(m)=t follows because one of x^2,y^2 is a unit. Hypothesis
(2) makes y nonzero. Set s=w(y). Equation (5) immediately gives

    n = w(-m y^2) = t + 2s.                             (6)

From NF=N, the image of F-I lies in ker N. Primitivity again gives an
integral row r=(a,b) with

    F = I + u r.                                       (7)

The equation FN=QN implies Fu=Qu, so

    ax + by = Q-1.                                     (8)

The lower-left entry of (7) is ya. Hypothesis (2) implies

    a in pi^(n-s) O = pi^(t+s) O.                       (9)

Both terms ax and by in (8) are divisible by pi^s. Hence s <= h.
Combining with (6) proves the theorem. This also covers s=0 and a
nonunit x. No division by x was used. QED.

## 2. Why this is the relevant depth

For an integral representation with all lower-left entries divisible by
pi^n, replacing the lattice basis (e_1,e_2) by (e_1,pi^n e_2) gives

    [[a,b],[c,d]] -> [[a,pi^n b],[c/pi^n,d]].             (10)

At a split toric place, choose a tame inertia element with matrix I+N,
where the tame character has unit value. The opposite residual extension
is ramified precisely when N_21/pi^n is nonzero modulo pi. That is exactly
w(N_21)=n, not merely w(N_21)>=n.

Frobenius at this place satisfies (1) and, being a matrix of the same
global integral representation, satisfies the second condition in (2).
Thus (3) constrains the primes that can actually ramify in the opposite
extension. It is not a bound on all local representations or all lattices.

The integer s measures how closely the local toric line agrees with the
first global coordinate line. Its square in (5) is essential. Replacing
t+2h by t+h is false.

## 3. Exact boundary for the local cup obstruction

Now set pi=7, assume t>=1 and h>=1, and assume the global reductions have
diagonal characters chi and 1, where chi is cyclotomic. At the present
place Q=1 modulo seven, so the residual coefficient action is trivial.
Use the Block 50 conventions

    alpha(g) = rho(g)_12 mod 7,
    beta(g) = (rho(g)_21/7^n)/chi(g) mod 7.

Assume the opposite extension is ramified here. For our inertia generator
T=I+N, alpha(T)=0 because t>=1, and beta(T)!=0 by (2).

If s=0, (9) makes a divisible by seven, and (8), with h>=1 and y a unit,
makes b divisible by seven. Hence alpha(F)=xb=0 modulo seven.

If s>0, x is a unit. Divide (8) by 7^s and reduce modulo seven. By (9)
the term ax/7^s vanishes, since t>=1. Therefore

    (b mod 7)(y/7^s mod 7) = (Q-1)/7^s mod 7.           (11)

It follows that alpha(F)!=0 exactly when s=h. Since h>=1, this also
excludes the s=0 case. Equivalently,

    alpha|G_v = 0               if n < t+2h,
    alpha(F) beta(T) != 0       if n = t+2h.             (12)

For the first assertion, natural inertia is trivial modulo seven and an
unramified additive character is determined by its Frobenius value.

For the second, if alpha cup beta were a coboundary, alpha and beta would
be the adjacent entries of a homomorphism into U_3(k). This follows
immediately by writing the multiplication law of upper unitriangular
three-by-three matrices; the central entry would solve the coboundary
equation. Every element of U_3(k), in characteristic seven, has exponent
seven. The tame relation F T F^-1=T^Q, with Q=1 modulo seven, would therefore
force the two images to commute. Their commutator instead has nonzero
central entry alpha(F)beta(T)-alpha(T)beta(F). Contradiction.

Consequently the local coupling obstruction is zero below the upper
endpoint and nonzero at that endpoint, **at a ramified place of the
opposite extension under these hypotheses**. In the Block 50 identity

    [alpha] cup [beta] = -delta(a mod 7^n),

the right side is therefore nonzero locally exactly at the upper endpoint.
This does not assert a global character lift or a global cup-zero theorem.

## 4. The bound and every parity class are sharp

Let t>=1, h>=1, 0<=s<=h and put n=t+2s. Choose any positive integer Q,
prime to seven, with v_7(Q-1)=h. The explicit integral matrices

    N = 7^t [[-7^s,1],[-7^(2s),7^s]],
    F = [[1,(Q-1)/7^s],[0,Q]]                           (13)

satisfy (1) and (2), have monodromy content t, and have nonzero opposite
residual inertia at depth n. They are conjugate to split toric matrices by

    P = [[1,0],[7^s,1]]:
    N = P [[0,7^t],[0,0]] P^-1,
    F = P [[Q,(Q-1)/7^s],[0,1]] P^-1.                   (14)

If Q is a prime power, the subgroup generated by F and I+N has the exact
local tame relation with that residue cardinality. One may prescribe an
actual Q throughout (13); there is no need to claim that every integer
1+7^h is a residue cardinality.

For an irreducible compact-group example add

    D = diag(2,1),       U = [[1,1],[0,1]].              (15)

The closed group generated by F,I+N,D,U lies in GL_2(Z_7). All lower-left
entries remain divisible by 7^n, and N attains that valuation. U has a
unit upper-right entry, and D has distinct residual eigenvalues. Thus
both endpoints are nonsplit and their depth is exactly n. Absolute
irreducibility follows because any invariant line for I+N must be
span((1,7^s)), while D does not preserve this line in characteristic zero.
The usual alternating determinant pairing is available.

These examples prove sharpness in the stated integral representation
category. They are not asserted to be global Galois representations,
polarized abelian surfaces, or Frey Jacobians of integer solutions.

For Q=29, h=1 and t=1, the only ramification depths are n=1 and n=3.
The s=1 example gives N=[[-49,7],[-343,49]] and
F=[[1,4],[0,29]], recovering Block 50 exactly.

## 5. Review and scope

The proof was checked again using the independent trace-zero description
N=[[z,b],[c,-z]], z^2+bc=0, and by primitive-line reconstruction after
integral basis changes. The exact verifier exercises both ordinary
integers and Q(sqrt(5)) with denominators prime to seven.

This is a fresh self-review by the same assistant, not an independent
human review, a second-agent review, or a proof-assistant certificate.
The elementary matrix theorem is proved here. The arithmetic use of it
requires the separate global depth and natural-lattice monodromy bridges.
