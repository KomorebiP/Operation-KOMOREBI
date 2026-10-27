# Binary three-color partitions: exact projector closure and a missing compatibility relation

## Block 15 — authoritative predecessor and outcome

The sole predecessor is `Komorebi_Padic_COMPLETE_Block14.zip`, SHA-256
`9a636b518ac0ffe8700891b37a2a8572b7347c18114b676aee7dbd822367c3d9`.
The original archive is immutable. Current-run evidence is separate from historical
records. The 68 inherited Lean modules and independent certificate checker are unchanged.

The primary target was the exact integer orbit lattice for three-colored binary
partitions. **That complete classification is not closed in this block.** We prove
instead the exact least coefficient-projector-stable enlargement, an all-precision
square-root linear representation bound, and an explicit compatibility obstruction
showing that the enlargement is strictly larger than the actual orbit. A new
specialized exact module constructor provides replayable minimum-realization
certificates at fixed precisions without assuming a closed Smith formula.

The new universal claims below are implemented in six Lean modules. Execution must
be authenticated from `RESULTS.md`, coverage, source hashes, and actual compiler
logs; this exposition alone does not authenticate a build. No historical novelty,
external-referee verdict, or Lean verification of Python is claimed.

## 1. Objects and conventions

Let F be the actual recurrence-defined binary partition series and let G=F^3.
The inherited formal product/counting bridge gives

    G(z)=product_(a>=0) (1-z^(2^a))^(-3),       (1-z)^3 G(z)=G(z^2).

Thus [z^n]G is the number of partitions of n into powers of two with three named
colors. Put x=(1-z)^(-1). The integer polynomial digit action T_d is defined by

    Lambda_d(G P(x)) = G (T_d P)(x),   d=0,1.

It is proved to be the actual coefficient section Lambda_d(sum c_n z^n)=sum
c_(2n+d)z^n, not an arbitrary matrix model. The proof uses faithful polynomial
substitution and multiplication by the unit G. Let

    H = span_Z {T_w 1 : w is a finite binary word}.

Words are least significant digit first, including empty words and high-order zero
padding. H means the integer LINEAR SPAN, not the set of individual iterates.
Scalar-coordinate bounds concern free linear machines, not minimal DFA state count.

Write P_(N,d)=Lambda_d(x^N) in polynomial x coordinates. The inherited exact binary
identity is

    P_(N+2,d)=x(2 P_(N+1,d)-P_(N,d)),     N>=1.

Here T_d(x^n)=P_(n+3,d). The recurrence and vanishing constant coefficients imply

    [x]T_d(P)=0

for every integer polynomial P. Every element of H has zero coefficient at x^1,
including the initial polynomial 1. This missing direction must not be silently
included as a supposed reachable basis element.

## 2. The diagonal containing module

Let w(n)=floor(n(n+1)/6), and use truncated natural subtraction to define

    u(n)=max(0, w(n) - (1 if n mod 3=2 else 2)).

The first u values at degrees 0 through 12 are

    0,0,0,0,1,4,5,7,11,13,16,21,24.

Degree one is EXCLUDED. Define integer monomial atoms a_n=2^u(n)x^n and

    E = direct_sum_(n>=0, n != 1) 2^u(n) Z x^n.

Equivalently P=sum c_j x^j is in E iff c_1=0 and 2^u(j) divides c_j for all j.
Both descriptions are proved equivalent in Lean.

### Invariance [Lean]

The proof establishes, for all n,j,d,

    2^u(j) | 2^u(n) [x^j]P_(n+3,d).

The top coefficient is exactly 2^(n+2). The next is

    [x^(n+2)]P_(n+3,d) = 2^n(2d-(n+3)).

For n>=3 the third coefficient is divisible by 2^(n-3). This follows from the
inherited integer identity

    24 [x^(n+1)]P_(n+3,d) = 2^n Q(2,n+3,d).

Cancel 8 over the INTEGERS and use coprimality with 3. This is not cancellation of
a nonunit in a residue ring. The weight identities are

    u(n+3)<=u(n)+n+2       for all n,
    u(n+3)=u(n)+n+2        for n>=2,
    u(n+2)<=u(n)+n         for n>=4,
    u(n+1)<=u(n)+(n-3)     for n>=5,
    u is nondecreasing.

They control the three leading degrees. At lower degrees j<=n, monotonicity
suffices. Cases n<=4 are exact polynomial base identities verified in Lean.
Coefficients above degree n+3 vanish. Consequently E is invariant under both
actual digit operators and contains H. The map P -> G P(x) transports the
containment to the actual series module.

Main endpoints: `binaryThree_weighted_coefficient_dvd`,
`binaryThreeEnvelope_eq_span`, `binaryThreeEnvelope_invariant`,
`binaryThree_polynomial_orbit_le`, `concrete_binary_three_orbit_envelope`.

## 3. E is exactly the least projector-stable closure [Lean]

Let pi_j(P)=[x^j]P x^j. The module E is preserved by every pi_j. We prove the
following precise minimality statement: if an integer submodule L contains 1 and
is closed under both T_d and every pi_j, then E is contained in L.

No saturation or division is added to this operator grammar. The first atoms are
recovered integrally:

    x^2 = -pi_2(T_1 1),
    x^3 = pi_3(T_1 x^2),
    2x^4 = pi_4(T_1 x^3) - pi_4(T_0 x^2 - 2 T_1 x^2).

The two terms in the last difference are 6x^4 and 4x^4. For n>=2 the top
projection gives exactly

    pi_(n+3)(T_d a_n) = a_(n+3).

These three starting atoms and the three-step raising law generate every a_n
with n!=1. This proves minimality among modules with the stated additional
projector closure, NOT minimality among modules closed under digits alone.

Main endpoints: `binaryThreeEnvelope_projector`, `binaryThree_projector_initial`,
`binaryThreeAtom_project_top`, `binaryThreeEnvelope_le_projector_closed`.

## 4. A coupled obstruction proves that H is strictly smaller [Lean]

For an integer polynomial P=sum c_j x^j define the linear functional

    psi(P)=16 c_4+c_6.

We prove, for EVERY P in E and each digit d,

    psi(T_d P) = 0 mod 64.

It is enough to check monomial atoms. At degrees n<=6 this follows from the exact
small polynomials. At degrees n>=7, u(n)>=7, so the atom is already coefficientwise
divisible by 64. The initial polynomial 1 also has psi(1)=0. Therefore

    H <= {P in E : 16 c_4+c_6 = 0 mod 64}.

But a_6=32x^6 lies in E and has psi(a_6)=32. Hence

    H < E,                  32 G(z)(1-z)^(-6) is NOT in the integer orbit module.

Both the polynomial strictness and the actual partition-series witness are
checked in Lean. The original exact-classification target cannot be met by
relabeling E as H. The missing relation couples coordinates: independent
coefficient divisibility loses information.

Main endpoints: `binaryThreeEnvelope_digit_constraint`,
`binaryThree_orbit_constraint`, `binaryThreeAtom_six_not_reachable`,
`binaryThree_orbit_lt_envelope`, `concrete_binary_three_missing_atom`.

### Exact interpretation at modulus 64 [written argument + instance certificate]

The reduced envelope has six factors, with degrees 0,2,3,4,5,6 and valuations
0,0,0,1,4,5. Its order is 2^26. In normalized coordinates psi/32 is exactly

    a_4+a_6 in F_2.

The two exact digit matrices annihilate this functional. A certified construction
of the actual reachable module at r=6 has Smith valuations 0,0,0,1,4, hence order
2^25. The kernel of this surjective functional on the envelope also has order
2^25. Containment plus equal finite cardinality proves equality at this precision:

    H_6 = {P in E_6 : 16 c_4+c_6 = 0 mod 64}.

This fixed-precision conclusion uses the saved all-word certificate and its
inherited written correctness/minimality reduction. A separate specialized Lean
r=6 module equivalence/cardinality endpoint is NOT claimed. The congruence alone
is not claimed sufficient for H at every higher precision.

## 5. Universal square-root free-machine bound [Lean]

At precision r, atoms with u(n)>=r vanish. Since u(n)>=w(n)-2, all nonzero atoms
have n<D_3(r+2), where the inherited exact function is

    D_3(t)=(isqrt(24t-3)+1)//2,  t>0.

Removing the absent degree one gives the rigorously checked budget

    B(r)=D_3(r+2)-1=(isqrt(24r+45)+1)//2-1.

The finite envelope is invariant under actual residue-ring digits. The inherited
generator theorem for submodules of finite free residue-ring modules, followed
by the actual Cartier realization principle, yields

    a free linear machine with at most B(r) coordinates exists modulo 2^r.

This is checked for every r>=0 (r=0 is the trivial ring). It covers every finite
binary word. It is an upper bound, not the minimum formula for H_r.

Endpoints: `concrete_binary_three_finite_envelope`,
`binary_three_machine_square_root_bound`.

The exact number of nonzero DIAGONAL envelope factors, for r>=1, is

    U(r)=2 + floor((sqrt(24r+25)-1)/6)
           + floor((sqrt(24r+33)-3)/6)
           + floor((sqrt(24r+1)-5)/6).

This formula follows by solving the three degree-residue inequalities. Its exact
integer version is implemented and exhaustively compared through r=1024. The
closed U-count is a written corollary, not a separately assembled Lean count
endpoint. The direct envelope constructor uses exactly the actual indices
u(n)<r,n!=1, never a guessed intrinsic spectrum. Both B and U are O(sqrt(r)).

## 6. Specialized fixed-precision intrinsic compiler and certificates

`BinaryThreeCertified(r)` computes the ACTUAL reachable module inside the small
proved envelope. It neither assumes the observed Smith pattern nor treats the
envelope generators as reachable. Each accepted generator carries a true orbit
word. Strict enlargement is tracked by finite module length, so termination
follows from the inherited chain-ring module construction. Resource caps report
inconclusive refusal, not mathematical nonexistence.

The polynomial P(x) is converted to the canonical numerator

    Q(z)=(1-z)^(3J) P((1-z)^(-1)),    3J>=degree(P).

Thus G P(x)=G Q(z)/B(z)^J with B=(1-z)^3. This puts the certificate in the unchanged
independent checker's exact format. It verifies the initial polynomial, all digit
polynomial identities, true-word membership, invertible ambient transforms, and
nonzero Smith factors. These certificates prove all-index correctness and minimum
free dimension for EACH specified precision under the inherited checker reduction.
They are not a universal closed Smith law and the executable is not Lean-verified.

The observed beginning is

    0,0,0,1,4,7,9,12,15,18,22,26,30,35,40,45,51,57,63,... .

A possible closed continuation is recorded only as a conjectural route. The
successful fixed-precision certificates and finite tests must not upgrade it.

## 7. Executed alternative routes and remaining gap

1. Exact integer Hermite bases of actual word spans through depth six reveal dense
   lower-degree corrections and confirm the absent x direction. They do not prove
   stability of an infinite candidate basis.
2. Monomial valuation-graph experiments suggested the diagonal weight u. The
   explicit arguments above subsequently establish the universal envelope and its
   exact projector-closure property, while the coupled obstruction refutes equality.
3. Three digit-zero Krylov chains starting with 2x^2,4x^3-x^2,8x^4+x^2 have integral
   digit-one coordinates in every tested row through degree 118 (plus the initial
   constant). Their universal closure is not proved. This remains a plausible route,
   not a theorem discarded or silently claimed complete.
4. A full generic high-precision run and a SymPy integer-Hermite normalization were
   resource-limited. The small-envelope chain-ring constructor removes much of the
   computational bottleneck but does not supply the missing universal argument.

The exact all-degree binary three-color orbit basis, universal intrinsic Smith
formula, and its universally assembled sharp count remain unresolved. The finite
r=6 obstruction is a first exact compatibility condition, not a universal arithmetic
obstruction theorem. Ternary completion, higher colors, global prime gluing,
executable verification, independent review, and historical novelty are unchanged
separate obligations.
