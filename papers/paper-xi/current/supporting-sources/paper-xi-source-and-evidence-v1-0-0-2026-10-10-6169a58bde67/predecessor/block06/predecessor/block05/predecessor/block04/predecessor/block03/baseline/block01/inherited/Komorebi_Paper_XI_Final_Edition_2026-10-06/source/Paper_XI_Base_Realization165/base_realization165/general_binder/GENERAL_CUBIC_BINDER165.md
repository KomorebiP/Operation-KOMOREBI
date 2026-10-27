# An explicit cubic binder for every exponent prime to three

Date: 2026-10-05. The construction below is a stratum-level theorem. It does
not assert full-character attachment, prescribed native-action realization,
phase matching, or H5 for the resulting candidate.

## Statement

Let F = F_3((t)), let E = F(e), where e^3 + te + t = 0, and put pi = -t.
Use V = E^3 with ordered F-basis w_{3i+r} = e^i v_r, for 0 <= i,r <= 2.
Let A be the complete period-nine hereditary order and P its radical, with
entry grade 9 v_F(z) + row - column. Let B = M_3(E), with induced complete
period-three E-chain order and radical Q. Use the retained normalized
corestriction s, characterized on coefficient matrix units T_{ij} by

    s(T_{i0}) = -e^i,
    s(T_{i1}) = e^(i+2)/t,
    s(T_{i2}) = e^(i+1)/t.

It acts entrywise on the three-by-three E-lane blocks.

For every positive integer h with 3 not dividing h, put a = 4h and define

    j_l = the residue of 2al in {0,...,8}, for l = 0,1,2,3,
    x_h(w_{j_l}) = pi^floor((j_l+a)/9) w_{(j_l+a) mod 9},
    x_h(w_j) = 0 on the other basis vectors.

Then x_h belongs to P^a, its square is zero, and

    c_h = -s(x_h e^(-4h) x_h)

has nonzero coefficients on all three lanes of degree -a in Q. More
precisely, if R v_0=v_1, R v_1=v_2, R v_2=e v_0, then

    c_h = R^(-a) mod Q^(1-a).

Thus E[c_h] is totally ramified of degree three over E, and c_h is minimal
over E, by the retained primitive-cycle lemma.

For positive h_1 < h_2 with neither divisible by three, put

    gamma = e^(-4h_2) I_3,
    b_0 = e^(-4h_1) I_3,
    beta = gamma + (1+x_{h_1}) b_0 (1-x_{h_1}).

The retained square-zero binder theorem then gives an actual simple stratum
of level n=12h_2 and critical exponent -4h_1. Its parameter field F[beta]
has degree and ramification index nine over F, with residue degree one.
Both input summands retain their original conjugacy classes with
multiplicity three. No established correspondence is used to select beta.

## 1. Chain shift and the leading term of e

Define the F-linear chain shift S by

    S w_j = w_{j+1} for j<8, and S w_8 = pi w_0.

It has grade one and S^9=pi. Multiplication by e sends

    w_r -> w_{3+r} -> w_{6+r} -> pi w_r + pi w_{3+r}.

Consequently, if m_e denotes multiplication by e on V,

    m_e - S^3 belongs to P^6.

Both terms have valuation three, so their inverses differ in P^0.
Expanding a difference of positive or negative powers by the finite
telescoping identity proves, for every positive integer a,

    m_e^(-a) - S^(-3a) belongs to P^(-3a+3).

No commutation of m_e and S is required for this estimate. For negative
powers first apply A^(-1)-B^(-1)=A^(-1)(B-A)B^(-1), and then telescope the
positive powers of the inverses.

## 2. Exact square-zero support

Because 3 does not divide a, multiplication by a permutes the residues
modulo nine. The four domain indices of x_h are

    {0,2a,4a,6a} modulo nine,

and their four image indices are

    {a,3a,5a,7a} modulo nine.

These sets are disjoint. Therefore x_h^2=0 exactly, for every h in the
stated infinite family. Every nonzero entry has grade a by its displayed
power of pi. Equivalently, if D is the diagonal projection onto the four
domain basis vectors, then x_h = S^a D.

## 3. The three surviving quadratic paths

The estimate of Section 1, multiplied on both sides by x_h, gives

    x_h m_e^(-a) x_h = x_h S^(-3a) x_h mod P^(3-a).

For an input indexed by j in the domain support, the rightmost x_h shifts
j to j+a, S^(-3a) then shifts it to j-2a, and the leftmost x_h survives
exactly when j-2a is again in the domain support.

Of the four domain residues, exactly three satisfy that condition:

    T = {2a,4a,6a} modulo nine.

For each surviving path, the total shift is -a and its leading coefficient
is one in the S-coordinate convention. Thus, writing D_T for the indicated
diagonal projection, there is the exact matrix identity

    x_h S^(-3a) x_h = S^(-a) D_T.

The three elements of T have distinct residues modulo three. Hence there
is exactly one surviving path on each E-input lane. In particular there
can be no cancellation between paths in the same E-input lane.

## 4. Normalized corestriction and its sign

For 0 <= i,j <= 2, the displayed formulas for s give

    s(T_{ij}) = -e^(i-j) mod e^(i-j+1) O_E.

For j=0 this is exact. For j=1,2 use

    pi = e^3/(1+e), so 1/t = -(1+e)/e^3.

More generally, for every integer k, including negative k,

    s(pi^k T_{ij})
      = -e^(3k+i-j) mod e^(3k+i-j+1) O_E.

Indeed pi^k=e^(3k)(1+e)^(-k), and the last factor has leading residue one.
The same formulas show directly that s(P^d) is contained in Q^d for every
integer d. The retained normalization gives the stronger equality used
by the binder theorem.

Take a surviving input index j=3b+s with E-lane s in {0,1,2}. Write its
shifted output index as i=3c+r and S^(-a)w_j=pi^k w_i. Then

    9k+i-j = -a,
    3k+c-b = (s-a-r)/3.

Applying minus s to this path produces, on E-entry (r,s), the leading
monomial

    e^((s-a-r)/3), where r = (s-a) mod 3.

That is exactly the (r,s)-entry of R^(-a). There is one path for each s.
Thus

    -s(S^(-a)D_T) = R^(-a) mod Q^(1-a).

The error from Section 3 lies in Q^(3-a), which is contained in Q^(1-a).
This proves the claimed leading congruence for c_h.

## 5. Application to the actual parameter field

The initial parameter gamma'=gamma+b_0 lies in E and has E-valuation
-4h_2, which is prime to [E:F]=3. The residue extension is trivial, so
gamma' is minimal over F and generates E. The fixed E-multiplication
normalizes the period-nine chain. Hence the initial minimal stratum has
level n=12h_2 and the required centralizer B=M_3(E).

For the retained binder theorem the remaining numerical values are

    b = 12h_1, a = 4h_1, q = b-2a = 4h_1, r = 3.

We have n>b, a>=1, q>0, gcd(q,r)=1, and the preceding proof gives the
required nonzero degree -q coefficients. Moreover s([x_h,b_0])=0 by
B-bimodularity, so the derived leading term is exactly the one just
constructed. The theorem therefore applies to beta with the asserted
field degree, ramification, and critical exponent.

The result holds uniformly for all h_1<h_2 prime to three. Any bounded
computer verification accompanying this note checks the implementation
and signs; it is not the source of the universal quantifier.

## Remaining scope boundary

This construction answers the square-zero stratum binder problem for this
fixed cubic extension and all the specified exponent pairs. It does not
prove that the resulting host contains every supplied marked Heisenberg
packet, that prescribed full source characters have compatible arithmetic
attachments, that native stabilizer actions occur in the required sense,
or that the same candidate satisfies H5. Those claims are not consequences
of the leading-cycle calculation alone.
