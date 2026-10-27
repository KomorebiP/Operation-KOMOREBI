# An explicit arithmetic Komorebi Space with an archimedean budget

Checkpoint ABC-20261025-RR7. Base: RR6 archive SHA-256
026d1f544ba86acc3fd9d63b75b4a8fc73595407f67e15f1b9b7f7e5144d993a.

This route constructs an independent arithmetic realization system. It does
not assume IUT's admissibility or comparison theorems. Its starting interface
is the strict view system of Realization Calculus, Volume I, sections 1-3:
a contravariant set-valued functor, with coherent sections satisfying its
actual restriction equations. No linear structure on prime support is used.

## 1. Finite views defined before any height inequality

Let N>=3 be an integer and M_N=N!. For an integer B>=2, let F_N(B) be the
following finite set of residue triples in (Z/M_N Z)^3:

    (alpha,beta,gamma) belongs to F_N(B)
      iff there are integers 1<=A,B',C<=B representing its coordinates,
          A+B' congruent C mod M_N,
          gcd(A,B',M_N)=1.

The letter B is the budget; B' is one lifted coordinate. Both conditions
on the lifts depend only on their residues. The definition requires an
actual bounded lift, rather than declaring every locally coherent point
to be the image of one. The budget is archimedean information retained
explicitly in the contract.

Reduction modulo M_N maps F_(N+1)(B) into F_N(B), using the same bounded
integer representatives and divisibility M_N|M_(N+1). Identity and
composition follow from modular reduction. These maps define a strict
view system on the ordered levels, with arrows from a lower level to a
higher level and restrictions in the opposite direction.

For B<=B_1 there is a natural inclusion F_N(B) into F_N(B_1), commuting
with reduction. Let K_B be its set of coherent sections, namely the inverse
limit over N. This is an explicitly declared Komorebi Space.

## 2. Bounded arithmetic reconstruction theorem

Let X_B be the set of positive integer triples

    A+B'=C,  gcd(A,B')=1,  max(A,B',C)<=B.

**Theorem 1.** Coordinate reduction gives a bijection X_B -> K_B.

Proof. A triple in X_B supplies a coherent residue family satisfying every
finite condition. For the converse, let r_N be a coherent section. Choose
N_0>=3 with M_(N_0)>B. The bounded integer lift of r_(N_0) is unique in
each coordinate: the difference of two integers in [1,B] has magnitude
less than M_(N_0), so cannot be a nonzero multiple of it. Denote this
lift by (A,B',C).

For every N>=N_0, a bounded lift of r_N also lifts r_(N_0). Uniqueness at
N_0 forces it to be that same triple. Therefore the fixed integer
A+B'-C is divisible by every M_N, and so is zero. If a prime p divided
both A and B', choose N>=max(N_0,p). Then p|M_N, contradicting the
finite primitivity condition. Thus the triple belongs to X_B. Reduction
and reconstruction are inverse by the uniqueness just proved. QED.

There is an explicit finite stabilization bound. If N>=B+1, then
M_N>2B and every prime that can divide two coordinates in [1,B] divides
M_N. The finite congruence then forces A+B'=C, since

    |A+B'-C|<2B<M_N.

The finite gcd condition forces gcd(A,B')=1. Reduction at such a level
therefore already identifies F_N(B) with X_B. The safe bound N>=B+1
is not claimed optimal or efficient in the logarithmic height log B.

This theorem proves an intended-source realization statement for the
declared arithmetic system. It does not prove a conductor-dependent B.

## 3. The exact additive protected-correction interface

Before imposing positivity and a budget, use the additive module E=Z^3
with D(A,B',C)=A+B'-C. Protect the residue triple modulo M. The permitted
corrections form M Z^3, whose image under D is exactly M Z. Hence the
protected obstruction is

    [D(A,B',C)] in Z/M Z.

It vanishes exactly when some correction in M Z^3 makes D zero. Explicitly,
if D(A,B',C)=M t, subtract (M t,0,0). The corrected tuple retains the
residues and has exact additive relation. The correction need not retain
positivity or the bound B. Those additional constraints are handled by
the set-valued spaces F_N(B), not by pretending a bounded positive set
is an additive subgroup.

This is a concrete instance of the protected-correction quotient in
Volume I, section 3. The quotient is defined from D and its permitted
correction subgroup before testing whether its class vanishes.

## 4. A coherent family of actual finite triples that escapes every budget

Put

    b_N=sum_(k=1)^(N-1) k!,
    x_N=(1,b_N,b_N+1) reduced mod N!.

Each displayed integer triple is positive, primitive, and exactly
additive. Since b_(N+1)=b_N+N!, the residue triples are coherent.
Consequently x is a point of lim_N union_B F_N(B).

For N>=3 one has

    (N-1)! <= b_N <= 2(N-1)!,
    0<b_N<b_N+1<N!.

The upper estimate follows inductively from sum_(k=1)^n k!<=2n! for
n>=2. The strict final inequality can be checked at N=3, where b_N+1=4,
and follows for N>=4 from 2(N-1)!+1<N!. In particular the least positive
integer representatives of the last two coordinates are b_N and b_N+1.
Thus any common coordinate budget for this level must be at least b_N+1.
These required budgets tend to infinity.

No positive integer b represents all of these beta coordinates: for
large N with N!>b, its least nonnegative residue is b, whereas the
corresponding residue b_N eventually exceeds b. In fact the coherent
beta coordinate is not any ordinary integer. For a negative fixed b,
its residue for large N is N!+b; divided by N! this tends to 1, whereas
b_N/N!<=2/N tends to zero. These residues cannot agree for all N.

We have therefore proved the strict inclusion

    union_B lim_N F_N(B)
        properly contained in lim_N union_B F_N(B).          (1)

The left side is the actual set of positive primitive additive integer
triples, by Theorem 1 and the natural budget inclusions. The right side
has a coherent point whose every finite observation is represented by
an actual such triple, but which has no ordinary integer realization.
This is an arithmetic example of escaping finite repairs, not a
counterexample to gluing under a fixed budget.

The minimal level-N budget in this family is exactly b_N+1. Its
logarithm is between log((N-1)!) and log(2(N-1)!+1). This is a proved
cost, not a numerical estimate inferred from sampling.

## 5. How multiplication and radical observations enter

At level N, multiplication of coordinate residues is the ordinary
finite-ring multiplication, compatible with every reduction. Its p-power
subviews can be refined by the Teichmuller/carry diagrams constructed in
the witt_space route. Such a refinement must retain the restriction maps
and distinguish a multiplicative section from an additive one.

For each prime p<=N, the statement p divides a coordinate is well defined
from its residue modulo N!. These Boolean prime-support observations
commute with reduction once that prime is present. They need not form a
linear observable. For a fixed budget B and a sufficiently large N, all
primes that divide the reconstructed coordinates occur among these views.
The support data then recover rad(A B' C) exactly. This supplies a typed
place for the conductor/radical channel within the construction.

## 6. The independent global theorem still required

The reconstruction theorem concerns existence and recovery at a supplied
budget. For ABC one still needs, for every epsilon>0, a constant C_epsilon
such that every intended coherent point representing a primitive triple
has

    log C <= (1+epsilon) log rad(A B' C)+C_epsilon.

No estimate of this kind follows merely from (1), the reconstruction
bijection, or the availability of every local finite view. In particular,
the factorial escape family is not asserted to violate ABC; its radicals
are not held fixed or bounded in this proof.

The next arithmetic task is to construct a protected comparison with an
independently bounded archimedean cost in terms of the radical channel.
The present system makes admissibility and intended-source membership
explicit, so this task no longer depends on interpreting an unspecified
IUT output family. Its quantitative estimate remains open.

Evidence: complete elementary proofs above, with no load-bearing finite
computation. No Lean compilation or new formal verification is asserted.
No historical novelty is claimed for finite reconstruction or the
noncommutation of bounded realization and inverse limits.
