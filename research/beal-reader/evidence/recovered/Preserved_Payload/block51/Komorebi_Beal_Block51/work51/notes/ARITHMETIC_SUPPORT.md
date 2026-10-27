# Depth-sensitive support on the remaining Beal branch

**Block 51. A necessary condition, not a proof of Beal or of (3,5,7).**

## Contract and inherited inputs

Assume positive pairwise-coprime integers A,B,C satisfy

    A^3+B^5=C^7,       3990 | C.

Let K=Q(sqrt(5)), O_7=Z_7[(1+sqrt(5))/2], k=F_49, and let V be the
rank-two O_7-linear Tate representation of the natural Jacobian, twisted
by the same quadratic character nu as in Blocks 48--50. The natural
lattice is denoted Lambda_0. No new choice of a Frey representation is made.

The following are inherited arithmetic inputs, not newly formalized here:

1. V is absolutely irreducible in characteristic zero. Its natural
   residual representation has nonsplit orientation chi by 1, with
   determinant chi_7. See work49/notes/extension_route.md and local_types.md.
2. At the prime above three the twist has split toric reduction, Frobenius
   eigenvalues 9 and 1, and natural monodromy content zero over O_7,
   because its integral period matrix is (7v_3(C)-3) I_2.
3. For an opposite residual extension, the lattice-independent local
   arguments of work49/notes/extension_route.md give splitting at 2,3,5,7
   and at variable C-primes v with Nv != 1 modulo seven. Good places are
   unramified for every lattice.
4. The class group of L=K(zeta_7) has no seven-primary part. This follows
   from h(Q(zeta_35))=1 and the degree-two extension/norm argument. The
   source, Masley (1976), Main Theorem, printed p.179, was rechecked in
   this block, including the table and the phi(m)<=24 sentence.
5. The natural seven-adic lattice is free of rank two over O_7, with the
   inherited self-adjoint RM action. The twist is the split toric twist
   at variable primes established in the predecessor.

All uses of these inputs remain subject to their original proof boundaries.
This block has not re-proved the full modular, character-classification,
or potential-reduction chain behind them.

## 1. A canonical finite depth, constructed on the actual lattice

Choose arithmetic Frobenius g_0 at three. Its eigenvalues are exactly 9
and 1. Their difference 8 is an O_7-unit. The projectors

    E_9=(rho(g_0)-I)/8,       E_1=(9I-rho(g_0))/8

are integral complementary rank-one idempotents. Choose generators of
their images, putting rho(g_0)=diag(9,1). The first residual line is the
chi-line, since chi(g_0)=2 in F_7. Thus every lower-left entry of rho(g)
is divisible by seven.

The tame monodromy at three in this basis is strictly upper triangular.
Its upper-right entry is a unit, because its content is zero. Conversely
some lower-left entry is nonzero in characteristic zero, since otherwise
V would have a global invariant line. Hence the positive finite integer

    n = min_{g: rho(g)_21 != 0} v_7(rho(g)_21)            (16)

exists and is attained. Replacing the basis by (e_1,7^n e_2) gives a
stable lattice Lambda_n and the matrices in equation (10) of
LOCAL_DEPTH_THEOREM.md. Its reduction has subcharacter 1 and quotient chi.
It is nonsplit: a complementary chi-line would have to be the first
coordinate line, because g_0 has distinct residual eigenvalues. But the
attained minimum in (16) gives a nonzero lower-left entry in that
reduction.

This construction supplies an actual nonzero class

    beta in H^1(K,k(chi^-1)).

Moreover every stable O_7-lattice is fixed by the two integral projectors
of g_0. Up to homothety it therefore has the form

    Lambda_j = O_7 e_1 + O_7 7^j e_2.

The unit upper-right monodromy at three forces j>=0, and (16) forces
j<=n. Conversely every integer 0<=j<=n gives a stable lattice. Thus the
stable lattices form precisely this finite segment. The natural lattice
is one endpoint, and n is its distance to the opposite endpoint, not a
freely chosen truncation depth or a search cutoff.

This argument makes the relevant Ribet lattice explicit in the present
setting. It does not require transferring natural finite flatness to a
changed lattice or asserting a global character lift.

## 2. Natural monodromy at every variable eligible prime

Let q outside {2,3,5,7} divide C, let v be a prime of K above q, and put
c=v_q(C)>0. Since K/Q is unramified at q, c is also the normalized
valuation in K_v. The natural twisted Jacobian has monodromy content

    t_v = 1 + v_7(c).                                  (17)

Here is the local bridge, including its normalization.

Use the completed-square sextic

    f(X)=X^6+10BX^3+12AX+5B^2.

Modulo v, the element u_0=-B^2/A satisfies u_0^5=-A and u_0^3=B because
A^3=-B^5. Hensel lifting supplies a unit u in K_v with u^5=-A and this
residue. Put beta=B/u^3=1+epsilon. Then

    beta^5-1=C^7/u^15,       v(epsilon)=7c,

because the cofactor of beta-1 is a unit at q!=5. Scaling X=ux gives

    f(ux)/u^6 = F_0(x)+10epsilon x^3+10epsilon+5epsilon^2,
    F_0(x)=(x^2+x-1)^2(x^2-2x+5).

The two roots r of g=x^2+x-1 lie in K_v and remain distinct modulo v.
Write h=x^2-2x+5. The quantities g'(r), h(r), and 20r are units because
q is outside {2,3,5}. The two nodes are ordinary transverse nodes, and
the derivative of the smoothing perturbation at r is 20r. It follows
by the critical-point/ordinary-node coordinate argument that each node
has smoothing parameter epsilon times a unit and therefore thickness
7c. At these odd residue characteristics one may also complete the
square in the two transverse coordinates. No extra discriminant factor
contributes to the node thickness.

For completeness, the node-coordinate argument can be made directly in
the complete local ring. Since F_0''(r)=2 g'(r)^2 h(r) is a unit, Hensel's
lemma gives a unique nearby critical point r(epsilon) with derivative
zero. Its critical value is 20r epsilon+O(epsilon^2), of valuation 7c.
After translation to that point the remaining series is a unit times
X^2 times a series congruent to 1 modulo X. Once the quadratic coefficient
is a square, take its square root and the formal square root of this
last series, using that 2 is a unit. This is an invertible formal change
of coordinate. The curve equation becomes UV equal to its critical
value times a unit. The split twist in the next paragraph supplies the
square quadratic coefficient, so the claimed thickness is exactly 7c,
not merely a lower bound from a discriminant valuation.

For the twist D=3(5-sqrt(5))/2, both branch radicands D h(r) are squares:
the two h(r) have ratio phi^2, where phi=(1+sqrt(5))/2. The branches at each node, the torus,
and the period lattice are split. The special fiber has rational normalization
and two self-nodes. In its two-loop basis the edge pairing is 7c I_2.

Baker--Rabinoff, arXiv:1308.3864v1, Theorem 2.9 and Remark 6.7, identify
this with the valuation of the analytic period matrix. For a tame inertia
element with unit seven-adic tame character, the full rank-four natural
Tate module consequently has nilpotent monodromy whose nonzero elementary
divisors are both 7c. Units in the local period entries add no prime-to-q
ramification: their seventh-power roots at every level are obtained over
the maximal unramified extension by Hensel lifting.

The RM-linear nilpotent N has rank one over O_7. Divisibility of this
O_7-linear endomorphism by 7^a is equivalent to divisibility of its
underlying Z_7-linear endomorphism by 7^a. The scalar-extension basis
introduces no factor of seven because O_7/Z_7 is unramified. Hence its
content is exactly v_7(7c), proving (17).

This bridge concerns the natural lattice only. The change of its inertia
under passage to Lambda_n is handled by the new matrix theorem, not
silently discarded.

## 3. The refined necessary support condition

Let S consist of the primes v of K above rational divisors q of C outside
{2,3,5,7}, with

    Q_v = Nv = q^f,       Q_v == 1 (mod 7).

Here f=1 at split rational primes and f=2 at inert ones. Set

    h_v=v_7(Q_v-1),       t_v=1+v_7(v_q(C)),
    S_n={v in S: n=t_v+2s for some integer 0<=s<=h_v}.    (18)

**Theorem.** The actual opposite extension beta has ramification support
contained in S_n, and S_n is nonempty. More precisely beta ramifies at
at least one prime in S_n.

**Proof.** At a ramified eligible prime, a tame generator has natural
matrix I+N with content t_v by (17). Opposite ramification means
v_7(N_21)=n. Frobenius has lower-left entry divisible by 7^n by (16),
and the split toric sequence gives FN=Q_v N and NF=N. Apply the local
theorem to obtain (18).

Outside S the inherited lattice-independent splitting/unramifiedness
arguments apply. If beta also had trivial inertia at every prime of S_n,
it would be everywhere unramified after restriction to L=K(zeta_7).
Restriction is injective because [L:K]=6 is prime to seven. The nonzero
class would give a seven-primary quotient of Cl(L), contradicting the
inherited class-number input. Thus at least one allowed prime ramifies.
QED.

In rational terms there must be q|C in the old residue classes

    q mod 35 in {1,8,13,22,27,29},

but now the same q must satisfy

    n = 1 + v_7(v_q(C)) + 2s,
    0 <= s <= v_7(q^f-1).                               (19)

This is strictly more precise conditional information than membership in
the six residue classes. It is not a contradiction: n depends on the
actual representation and surviving primes can satisfy (19).

## 4. Consequences with explicit hypotheses

**Multiplicity cost.** At a supporting prime,

    v_7(v_q(C)) >= max(0,n-1-2h_v),
    v_7(v_q(C)) == n-1 (mod 2).                         (20)

For example, if n is even, some eligible prime must divide C with
multiplicity divisible by seven (indeed its seven-adic multiplicity
valuation is odd). This is not the statement that seven divides q or
that C is itself a seventh power.

**Ordinary multiplicity regime.** Suppose every eligible q has
7 not dividing v_q(C). Then t_v=1 everywhere in S, so n is odd and

    n <= 1+2 max_{v in S} h_v.

**Two-depth regime.** If, in addition, every eligible v satisfies
Q_v != 1 modulo 49, then h_v=1 and

    n in {1,3}.                                        (21)

Depth one has the cup-zero property of Block 50. At depth three, every
ramified supporting prime is at the upper local endpoint, so the local
cup and diagonal character-lifting obstruction are nonzero. Neither
case is excluded by this block.

In particular, depth at least four requires some eligible prime with
Q_v=1 modulo 49 or multiplicity v_q(C) divisible by seven. This states
a necessary arithmetic cost for deep lattice changes. It is not a
uniform upper bound on n for all possible C.

## 5. The old ray-character obstruction now has an exact local cost

Block 50 used q=1504231, with q=1 modulo 35 and v_7(q-1)=1, to construct
characters eta_n at every n>=2 with a nonzero local connecting class.
They were explicitly not realized as diagonal characters of the Frey
representation.

Suppose such a diagonal character chi_7 eta_n actually occurs at the
endpoint depth n of the present representation, and suppose q is one
of its C-primes. The natural alpha is unramified at q. Nonzero local
delta forces alpha cup beta nonzero. If beta were also unramified,
this cup would vanish (both characters factor through the procyclic
unramified quotient; the central cochain is a binomial quadratic).
Thus beta is ramified and section 3 of LOCAL_DEPTH_THEOREM.md applies.
Its nonzero endpoint criterion gives

    n = t_v+2h_v = 3+v_7(v_q(C)).                       (22)

Hence n=2 is incompatible with these actual local periods. For n>=3,

    v_7(v_q(C))=n-3.                                   (23)

For example, depth five in this particular character family would
require q to occur in C to a multiplicity divisible by 49 but not 343.
This does not prohibit that multiplicity, or realize the character.

There is also a compatible Kummer-coordinate restriction. Under the
Block 50 natural Kummer-support assertion, write

    alpha=a_phi[phi]+a_3[3]+a_5[sqrt(5)].

At q the seventh-power symbols of 3 and sqrt(5) are trivial. The two
roots of 5 modulo q are 684240 and 819991. With the order-seven root
zeta=1114923, the symbols of phi are zeta^2 and zeta^5 respectively.
Thus nonzero local alpha forces a_phi!=0. These exact residue statements
are checked in `computations/depth_checks.py`. The project has not
computed a_phi in the actual global Jacobian, so this is another
necessary condition, not an exclusion.

## 6. Boundary

The local-depth theorem and support corollaries are written proofs.
Finite checks test their displayed algebra and explicit examples only.
No new theorem here is asserted to have been compiled in Lean.

The full (3,5,7) problem still has the reducible branch, the surviving CM
congruence/cover problem, and the higher Hilbert levels. The other
exponent signatures needed for the full Beal conjecture remain outside
this block. Even a future complete solution of (3,5,7) would not by
itself prove Beal.
