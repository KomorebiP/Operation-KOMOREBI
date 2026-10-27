# Global height requires coercivity along the exact arithmetic locus

Checkpoint ABC-20261025-RR7. Base RR6 archive SHA-256:
026d1f544ba86acc3fd9d63b75b4a8fc73595407f67e15f1b9b7f7e5144d993a.
Owner: /root/komorebi_global_coercivity.

This is an independent Realization Calculus route. It uses the current
Komorebi Space contracts for exact sections, joint defects, protected repair,
and declared transformation costs. It does not assume IUT comparison or
admissibility statements. The all-epsilon ABC height bound remains unproved.

## 1. Exact framework-to-arithmetic dictionary

The current source is *Realization Calculus, Volume I: Komorebi Space*, native
Library file libfile_bd054a01919c8191b1bb6d1a9a4965d6, current file identifier
file_00000000750881f6814ea548be018387, 162 PDF pages. Sections 18-20 distinguish
projection/repair from bounds along an exact space. Section 23 declares
transformation cost separately. The source passages read here are PDF pages
71-73 and 80-83, together with the earlier definitions supplied in the current
research context. This route does not rerun or certify the book's Lean build.

| Framework item | Arithmetic object in this route | Boundary retained |
| --- | --- | --- |
| Intended coherent realization | A positive primitive integer triple a+b=c, with the bounded reconstruction system of the sibling integer_space route | A coherent profinite point is not automatically such an integer triple. |
| Exact defect | d(a,b,c)=a+b-c, an integer | Zero defect is an exact equation; approximate zero needs an archimedean threshold. |
| Dimensionless measured defect | eta=abs(d)/c for c>=1 | Small eta is not the same as abs(d)<1. |
| Archimedean size to control | H=log c on exact positive additive triples | On raw candidates we additionally impose c>=max(a,b). |
| Radical observable | r=log rad(abc) | This is a nonlinear support observation, not a bounded linear map of exponent space. |
| A linear Hilbert surrogate | D for coherence, P for a declared linear observable, ell for a linear size functional | Any identification with actual height and radical must be proved. |

The sibling integer_space construction already gives an explicit intended-source
space at a supplied integer bound B. The question here is whether its required
archimedean bound can be obtained from a radical channel by the quantitative
repair theorem. The next two theorems determine precisely what a linear repair
argument would have to add.

## 2. A positive joint-coercivity theorem

Let E be a real Hilbert space, let R and Y be real Banach spaces, and let
D:E->R and P:E->Y be bounded linear maps. Put L=ker D. Assume ran D is
closed and choose a finite a>=0 such that

    ||x-P_L x|| <= a ||Dx||       for every x in E.          (1)

Here P_L is orthogonal projection onto L. Such an a exists by the closed-range
theorem in the source, but the following implication also has a direct proof
once (1) is supplied.

**Theorem 1.** The following are equivalent:

1. There is a finite K>=0 with

       ||x|| <= K max(||Dx||,||Px||)   for every x in E.

2. There is a finite b>=0 with

       ||v|| <= b ||Pv||             for every v in L.

3. The restriction P|L is injective and has closed range in Y.

When condition 2 holds, the explicit estimate

    ||x|| <= a(1+b||P||)||Dx|| + b||Px||                  (2)

holds. The coefficient on exact v in L is the norm of the inverse of
P:L->P(L), when L is nonzero; in the zero-space case it is zero.

*Proof.* Condition 1 restricted to L gives condition 2 with b=K. Conversely,
write u=x-P_L x and v=P_L x. Then ||u||<=a||Dx|| and

    ||v|| <= b||Pv|| <= b||Px||+b||P||||u||.

The triangle inequality for x=u+v gives (2), which proves condition 1 with
K=a(1+b||P||)+b. For 2=>3, injectivity is immediate. If Pv_n converges in Y,
the estimate on v_n-v_m makes v_n Cauchy in the closed Hilbert subspace L.
Its limit v satisfies Pv=lim Pv_n, so the range is closed. For 3=>2,
P:L->P(L) is a bounded bijection between Banach spaces. The bounded inverse
theorem supplies b. Its least admissible value is the inverse norm directly
from the definition of operator norm. QED.

Theorem 1 isolates a condition beyond small defect: P has to control every
direction in the exact space. If a nonzero v satisfies Dv=Pv=0, its multiples
already disprove condition 1. Injectivity alone is insufficient in infinite
dimension. For example E=ell^2, D=0 and P(e_n)=e_n/n give an injective P,
but ||e_n||=1 and ||Pe_n||=1/n prevent every finite b.

This is a formal linear consequence of the source's closed-range and joint
defect framework, with a complete proof above. It is not an ABC input: no
linear P representing radical support has been constructed.

## 3. The sharper criterion for one height functional

For a height comparison one need not control every coordinate of x. Let
ell:E->R be a bounded real linear functional, and keep the preceding D,P,L.

**Theorem 2.** For a specified finite B>=0, the bound

    abs(ell(v)) <= B||Pv||       for every v in L          (3)

holds if and only if there is a bounded linear functional f:P(L)->R with
||f||<=B and ell|L=f o (P|L), where P(L) has the norm inherited from Y.
This statement does not require P(L) to be closed.

*Proof.* A factorization gives (3). In the opposite direction define
f(Pv)=ell(v). If Pv=Pw, applying (3) to v-w gives ell(v-w)=0, so this is
well defined. It is linear and (3) gives its norm bound. QED.

Consequently ell must vanish on N=L intersect ker P. If P|L has closed range,
this necessary condition is sufficient for some finite B. To see this,
decompose L=N orthogonal_sum N_perp_L. The map P on N_perp_L is a bounded
bijection onto P(L). Its inverse has some finite norm b. For v in L,
ell(v)=ell(v-P_N v) and

    abs(ell(v)) <= ||ell|| b ||Pv||.

Under (1) and (3), every x in E satisfies the concrete transfer estimate

    abs(ell(x))
      <= a(||ell||+B||P||)||Dx|| + B||Px||.               (4)

Indeed, use x=u+v as in Theorem 1. The term ell(u) is bounded by
||ell||||u||, while abs(ell(v))<=B(||Px||+||P||||u||). Substitute (1).

Thus the arithmetic program needs an on-exact-locus size certificate or a
new arithmetic estimate from which to construct it. The source's existence
of a nearest coherent repair alone supplies neither. In particular a linear
height-sensitive direction in N cannot be removed by selecting a different
nearest repair algorithm.

## 4. Execute the obvious exponent-coordinate candidate

For the arithmetic prime-support sector use real exponent coordinates
(x,y,z)>0 and evaluate

    A=2^x,   B=3^y,   C=5^z,
    F(x,y,z)=(A+B-C)/C,
    H(x,y,z)=z log 5.

The candidate radical-channel value is the fixed support cost log 30.
This is explicitly a real relaxation. On integer (x,y,z), the evaluated
coordinates are integers with pairwise disjoint prime supports; away from
integer exponents these are not integer ABC triples, and log 30 is a
declared support-label cost rather than the radical of a real number.

There is an exact family of the relaxed coherence equation:

    x(t)=t,   y(t)=t,
    z(t)=log(2^t+3^t)/log 5,       t>0.                  (5)

It has F=0 and H=log(2^t+3^t)>=t log 3, with the same support-label cost
log 30. Hence no upper bound on H in terms of that support cost can hold
throughout the relaxed exact locus.

The linearized test gives the same failure without a global extrapolation.
At an exact point with A+B=C,

    dF(h)= (A/C)log2 h_x +(B/C)log3 h_y -log5 h_z.

The local support observation is constant on this open sector, so its
derivative P is zero. The vector

    h=(1,0,A log2/(C log5))

has dF(h)=0 but dH(h)=A log2/C>0. Theorem 2's necessary annihilation
condition fails for this candidate. A repair norm controlling transverse
errors cannot control this tangent height direction.

Adding a fixed multiple of distance to the integer exponent lattice does
not give a coercivity estimate on this real relaxation: Euclidean distance
to Z^3 is always at most sqrt(3)/2, whereas (5) has unbounded height.
This does not rule out an arithmetic estimate only on exact integer
points. It rules out using this continuous, fixed-support candidate and
a bounded integrality penalty to establish that estimate.

## 5. An integer near-exact sequence with fixed radical

The preceding failure is not just a concern about arbitrary real labels.
The following exact integer construction tests a stronger proposed transfer
from a dimensionless equation residual to height.

**Lemma 3 (one-sided rational approximation).** If alpha>0 is irrational,
there are positive integers m_j,n_j with n_j tending to infinity and

    0<m_j-n_j alpha ->0.

*Proof.* Partition [0,1) into Q equal intervals. Two of the Q+1 fractional
parts 0,alpha,...,Q alpha lie in the same interval. Their difference shows
that for some positive q one has ||q alpha||<1/Q. If the fractional part
{q alpha} lies in (1-1/Q,1), choose n=q and m=ceil(q alpha).
If delta={q alpha} lies in (0,1/Q), put k=floor(1/delta), n=kq,
and m=ceil(n alpha). Irrationality gives 0<1-k delta<delta, so this pair
again has 0<m-n alpha<1/Q. Apply this for Q tending to infinity. The
positive errors cannot tend to zero along bounded n, because only
finitely many such positive differences can occur with bounded n and
error below one. Thus an unbounded subsequence of n can be chosen.
When alpha>0, m is also positive for all sufficiently large n. QED.

Take alpha=log3/log2, which is irrational: a rational equality alpha=u/v
would imply 3^v=2^u, contradicting unique prime factorization. Lemma 3 gives
positive m_j,n_j tending to infinity with

    delta_j=m_j log2-n_j log3>0,     delta_j->0.

Use the raw integer candidates

    (a_j,b_j,c_j)=(1,3^(n_j),2^(m_j)).                    (6)

They are positive and primitive, c_j>b_j, and rad(a_j b_j c_j)=6. Their
relative additive defects satisfy

    eta_j=abs(1+3^(n_j)-2^(m_j))/2^(m_j)
         <=2^(-m_j)+abs(exp(-delta_j)-1) ->0.             (7)

For m_j>=3 the integer defect is never zero. Indeed modulo 8, 3^n is
1 or 3, so 1+3^n is 2 or 4 and cannot equal 2^m, which is zero modulo 8.
These are near-exact raw candidates, not actual additive ABC triples.
Their heights log c_j=m_j log2 tend to infinity.

It follows that there are no finite constants A,B,C giving

    log c <= A log rad(abc)+B abs(a+b-c)/c+C              (8)

for all positive primitive raw integer candidates with c>=max(a,b).
Along (6), the right side tends to A log6+C, while the left side diverges.
The same conclusion holds if the residual penalty in (8) is replaced by
any function of eta that stays bounded as eta tends to zero.

An illustrative exact candidate is (1,243,256), with radical 6 and
relative defect 12/256=3/64. This finite arithmetic example is not evidence
for the infinite result; that result has the proof above.

The sequence tests this chosen relative archimedean defect. It does not
make every modular view exact or make every possible joint local defect
small. For each nonzero integer defect, a sufficiently fine modulus
detects it. A construction using those additional channels has to be
analyzed with its own residual map and norms.

Equation (8) is a tested reconstruction proposal, not the ABC conjecture.
ABC restricts to defect exactly zero. The failure of a stable residual
penalty neither produces an ABC counterexample nor excludes a specifically
arithmetic estimate on that exact locus. A closed-range certificate at a
fixed local finite model cannot silently supply the missing uniform
certificate over these unbounded integer candidates.

## 6. A positive exact stopping law with an honest height budget

For every integer raw triple with c>=1, put d=a+b-c and eta=abs(d)/c.
Then

    c eta=abs(d),
    c eta<1  implies d=0.                               (9)

The implication follows because a nonzero integer has absolute value at
least one. At a known bound c<=B, eta<1/B suffices, because
c eta<=B eta<1. The strict threshold is necessary for this inference:
a defect of magnitude one attains c eta=1 without being zero.

This supplies a concrete arithmetic tolerance for exactification in the
budgeted integer_space construction. It is not a conductor-to-budget
theorem. The near-exact sequence (6) does not cross its exactness threshold:
for its nonzero defects one always has eta_j>=1/c_j, even though eta_j->0.
Thus the positive stopping law and the negative uniform-residual result
are consistent.

The natural absolute residual abs(d) avoids this particular vanishing
sequence, since nonzero integer residuals are at least one. It still does
not bound height along d=0. Changing the residual scale therefore does
not by itself supply the on-exact-locus coercivity in Theorems 1-2.

## 7. Outcome and the first genuinely arithmetic missing input

Proved here: the joint-observable coercivity criterion and explicit estimate;
the factorization criterion for a height functional; failure of the stated
real-exponent candidate; an integer near-exact fixed-radical sequence that
refutes a uniform bounded relative-residual penalty; and an exact stopping
law at a supplied archimedean budget. All statements have universal proofs,
with no load-bearing finite computation and no new Lean run.

The failed attempt was to infer a conductor-controlled height from stable
coherence repair or from small dimensionless additive residual. It fails
because neither controls the relevant height directions on the exact
relaxation, and normalization hides an unbounded absolute integer scale.
This is a restriction on that mechanism, not on all possible Komorebi
constructions.

The remaining arithmetic input is NOT a definition of an error as H-r.
It must be an actual construction on the intended integer realization
space: a declared comparison/observable and independently proved costs
which control its archimedean height on exact integer points using radical
data, uniformly across supports and exponent depths, with the every-epsilon
coefficient needed for ABC. The prime-support map cannot simply be
substituted for linear P in the Hilbert theorem. The route remains open
under such a concrete new comparison or a new arithmetic coercivity
mechanism. No ABC exponent has improved in this route.

No historical novelty is claimed for the Banach inverse, elementary
approximation, finite-lattice threshold, or these source-derived mechanisms.
