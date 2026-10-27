# A global countermodel to the retained arithmetic axioms

Date: 26 September 2026. This lemma is an obstruction to a proof strategy,
not a counterexample to Lehmer's conjecture for Ramanujan's actual tau.

## Prime existence input

Use the following Chebotarev consequence supplied by the arithmetic
investigation and independently verified in `FINAL_BRANCH_AUDIT.md`:

> For every positive integer L, a positive density set of primes q satisfies
> q=-1 modulo 5L and tau(q)=0 modulo L.

This document proves everything after that input. The independent audit
checks the exact Galois representation, Frobenius and complex conjugation
hypotheses against the raw arithmetic proof and its source leaves. Thus the
lemma below is unconditional using the established Deligne and Chebotarev
theorems. No claim that tau(q) is zero or nonzero as an integer is included
in the prime existence input.

## Lemma

For every real B>=1 and positive integer M there exists a multiplicative
integer sequence f on the positive integers with all the following properties:

1. f(1)=1 and f(n)=tau(n) for every n<=B.
2. f(n)=tau(n) modulo 10M for every positive integer n.
3. For every prime p and every r>=2,
   f(p^r)=f(p)f(p^(r-1))-p^11*f(p^(r-2)).
4. |f(n)|<=d(n)*n^(11/2), where d(n) is the number of positive divisors of n.
5. f(n) is odd if and only if n is an odd square; also
   f(n)=n*sigma_1(n) modulo 5.
6. With the purely arithmetic transform

   R_f(n)=sum_(d^2 divides n) mu(d)*chi_5(d)*d^10*f(n/d^2),

   one has R_f(s^2) nonzero for every s>=1.
7. Nevertheless, f(q)=R_f(q)=0 for some prime q>B.

This includes any finite coefficient check and any finite list of fixed
congruence moduli by increasing B and replacing M by a common multiple.
Property 6 is a nonvanishing statement at every square, not a bounded test.

## Proof

Apply the prime existence input with L=10M and choose q>B from its positive
density set. Increasing q further ensures it avoids every prime divisor of
10M. Then q=-1 modulo 50M and tau(q)=0 modulo 10M.

Define prime parameters a_p=tau(p) for p different from q and a_q=0.
For each prime set F_(p,0)=1, F_(p,1)=a_p and

F_(p,r)=a_p*F_(p,r-1)-p^11*F_(p,r-2).

Define f(n) as the finite product of F_(p,v_p(n)) over primes dividing n.
Unique prime factorization makes this a well-defined integral multiplicative
sequence. It has the desired recurrence by construction.

Only the parameter at q has changed. Every n<=B is coprime to q, so f(n)=tau(n).
At q the old and new parameters agree modulo 10M. Induction on r in the
integral recurrence proves F_(q,r)=tau(q^r) modulo 10M for every r. All other
prime blocks agree exactly. Multiplicativity now proves f(n)=tau(n) modulo 10M
at every n. Both the global parity criterion and the modulo-5 congruence follow
at once, since 2 and 5 divide 10M.

For p different from q, the usual local consequence of Deligne's bound is
|tau(p^r)|<=(r+1)*p^(11r/2): if alpha,beta are the Hecke roots, each has absolute
value p^(11/2), and tau(p^r)=sum_(j=0)^r alpha^(r-j)*beta^j has r+1 terms.
For the modified prime,

F_(q,2m)=(-q^11)^m,     F_(q,2m+1)=0.

Its local block obeys the same bound at every exponent, including exponent 0.
Multiplying the local inequalities proves

|f(n)|<=product_(p^r exactly divides n) (r+1)*p^(11r/2)
       =d(n)*n^(11/2).

The square-supported convolution defining R_f is multiplicative and gives

R_f(p^r)=F_(p,r)-chi_5(p)*p^10*F_(p,r-2)  for r>=2,

with R_f(1)=1 and R_f(p)=a_p. At every prime other than q its local factor
equals the already audited R factor. At q, chi_5(q)=1 because q=-1 modulo 5,
so direct evaluation yields

R_f(q^(2m))=(-1)^m*q^(11m-1)*(q+1),

which is nonzero for m>=1. Every factor of R_f(s^2) is therefore nonzero,
and multiplicativity proves property 6. Finally, R_f(q)=a_q=f(q)=0.

## Exact logical interpretation

The lemma produces an actual arithmetic sequence satisfying the listed
properties and having a zero. It therefore refutes the implication

listed properties  =>  every coefficient is nonzero.

It does not show that the sequence is the coefficient sequence of a modular
form, has a packet-shell realization, or carries the compatible Galois
representations of Delta. Those properties are deliberately absent from the
premises being tested.

The proof does not need tau(q) to be nonzero. If tau(q) is nonzero, f differs
from tau; if tau(q) is zero, f equals tau at every index and Lehmer is already
false. In either case the weaker-axiom implication fails. Consequently the
unconditional statement must not describe f as nonmodular: if tau(q)=0, it
could simply be Delta's coefficient sequence. One may say only that the
construction does not impose or establish modularity. If it is independently
known that tau(q) is nonzero, normalized level-one weight-12 uniqueness would
then exclude that modular realization, but that extra condition is unnecessary
for the obstruction above.

The next missing input must distinguish the actual fixed modular form or
actual packet shells from this arithmetic class. More coefficient checks,
more fixed congruence moduli, the same Hecke recurrence, parity, the Deligne
bound, and all-square primitive nonvanishing do not suffice, even in combination.
