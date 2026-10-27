# Block 47: exact squareclass stratification and its local saturation boundary

Status: a written elementary proof, supported by exact finite residue checks.
No Lean formalization is claimed. This note does not prove nonexistence of
primitive integer solutions of signature (3,5,7).

## 1. Setup and exact claim

Write a hypothetical positive pairwise-coprime solution as

\[
A=a u^2,\qquad B=b v^2,\qquad C=c w^2,
\]

where \(a,b,c\) are positive, pairwise-coprime, squarefree integers and
\(u,v,w\) are positive integers. The equation becomes

\[
F(u,v,w)=a^3u^6+b^5v^{10}-c^7w^{14}=0. \tag{1}
\]

For a prime \(p\), call a triple in \(\mathbf Z_p^3\) primitive if at most
one of \(au^2,bv^2,cw^2\) is divisible by \(p\). We require each root and
base to be nonzero. The local question permits different roots at different
primes. Local solvability is not existence of a single rational or integer
triple.

**Theorem 1: complete primitive local coefficient criterion.**

For every fixed \((a,b,c)\) as above:

1. At \(p=2\), primitive solvability of (1) is equivalent to at least one
   admissible row of the following table.

   | Even base | Required odd coefficients | Required relation |
   |---|---|---|
   | \(A\) | \(b,c\) odd | \(b\equiv c\pmod8\) |
   | \(B\) | \(a,c\) odd | \(a\equiv c\pmod8\) |
   | \(C\) | \(a,b\) odd | \(a+b\equiv0\pmod8\) |

   An even coefficient forces its base to be the even base. If all three
   coefficients are odd, any of the three rows may be used.

2. At an odd prime dividing \(abc\), the criterion is

   \[
   \begin{array}{c|c}
   p\mid a & \left(\frac{bc}{p}\right)=1\\
   p\mid b & \left(\frac{ac}{p}\right)=1\\
   p\mid c & \left(\frac{-ab}{p}\right)=1.
   \end{array} \tag{2}
   \]

3. At every odd prime not dividing \(abc\), there is always a primitive
   local solution.

Consequently, the coefficient family passes every primitive local test if
and only if the finite dyadic table and the finitely many Legendre tests (2)
pass. Higher prime-power tests impose no additional restriction on the
coefficient triple after the local root variables have been projected out.

## 2. Why lifting requires no valuation cutoff

At an odd prime, suppose a primitive solution modulo \(p\) has been found.
There are at least two unit bases. Their corresponding coefficients and
roots are units. The partial derivatives of (1) are

\[
6a^3u^5,\qquad 10b^5v^9,\qquad -14c^7w^{13}.
\]

For an odd prime, at most one of \(6,10,14\) is divisible by \(p\).
Therefore at least one unit variable has unit derivative. Choose integer
lifts for the other variables, replacing a zero residue by the nonzero
integer \(p\) if necessary. Fix those variables. In the remaining variable,
successive correction by a multiple of \(p^n\) uniquely kills the next
residue digit because the derivative is a unit. The corrections converge
to a root in \(\mathbf Z_p\), with all variables nonzero and the original
primitive pattern preserved.

This is the elementary simple-root lifting argument. It applies uniformly
at \(3,5,7\) too. There is no assertion that a finite enumeration of
valuations covers an unproved tail. Instead, every primitive residue
solution lifts to all depths by this argument.

Conversely, a primitive \(\mathbf Z_p\)-solution reduces to a primitive
solution modulo \(p\). Thus the odd-prime local problem is exactly a
finite-field problem.

## 3. Proof at odd primes dividing a coefficient

Suppose \(p\mid a\). Primitivity forces \(b,v,c,w\) to be units, and
reduction gives

\[
b^5v^{10}=c^7w^{14}.
\]

Taking quadratic characters proves necessity of \((bc/p)=1\). For
sufficiency, \(c^7/b^5\) is a square. In the cyclic group
\(\mathbf F_p^\times\), the values \(v^{10}w^{-14}\) are exactly the
squares, since \(\gcd(10,14,p-1)=2\). Choose the two unit roots accordingly
and any nonzero root for the ramified coefficient. The lifting argument
then applies. The cases \(p\mid b\) and \(p\mid c\) use respectively
\(\gcd(6,14,p-1)=2\) and \(\gcd(6,10,p-1)=2\). Moving the second term
across the equality when \(p\mid c\) supplies the sign in \((-ab/p)\).

The cyclic-group assertion can also be checked directly with Bezout
relations \(10\cdot3-14\cdot2=2\),
\(6\cdot5-14\cdot2=2\), and \(6\cdot2-10=2\).

## 4. Proof at odd primes away from the coefficients

Let \(\alpha,\beta,\gamma\in\{1,-1\}\) be the quadratic characters of
\(a,b,c\), and let \(\epsilon=(-1/p)\). A primitive residue solution
with one zero base exists in the respective cases

\[
\beta=\gamma,\qquad \alpha=\gamma,\qquad
\alpha=\epsilon\beta. \tag{3}
\]

Indeed the same Bezout argument applies, now placing a root equal to zero
in the chosen coordinate. The lifting procedure replaces that zero by a
nonzero multiple of \(p\) before lifting another coordinate.

If \(p\equiv1\pmod4\), two of the three signs agree, so one condition in
(3) holds. If \(p\equiv3\pmod4\), failure of all three conditions forces
\(\alpha=\beta=-\gamma\). These remaining two sign patterns have a
solution with all bases units, as follows.

There are \((p+1)/4\) elements \(t\in\mathbf F_p\) for which both
\(t\) and \(1-t\) are nonsquares. To verify the count, let \(\chi\) be
the quadratic character extended by \(\chi(0)=0\). The elementary identity

\[
\sum_x\chi(x^2-d)=-1\quad(d\ne0)
\]

follows by counting \((x-y)(x+y)=d\): there are \(p-1\) such pairs, and
also \(p+\sum_x\chi(x^2-d)\). Completing the square gives
\(\sum_t\chi(t(1-t))=-\chi(-1)=1\). On omitting \(t=0,1\), both
single-character sums are \(-1\). Hence the desired count is
\((p-2+1+1+1)/4=(p+1)/4>0\).

For such \(t\), put

\[
A_0=t^{12}(1-t)^{28},\qquad
B_0=t^7(1-t)^{17},\qquad
C_0=t^5(1-t)^{12}.
\]

The direct identity \(A_0^3+B_0^5=C_0^7\) holds, and the three quadratic
characters are \((1,1,-1)\). Weighted scaling

\[
(A_0,B_0,C_0)\longmapsto
(\lambda^{35}A_0,\lambda^{21}B_0,\lambda^{15}C_0)
\]

preserves the equation. A nonsquare \(\lambda\) changes all three signs,
producing \((-1,-1,1)\). For whichever pattern is required,
\(A_0/a,B_0/b,C_0/c\) (after scaling if needed) are squares, so choose
\(u,v,w\) to be their square roots. This proves finite-field solvability,
and the lifting argument proves local solvability.

The universal identity used here was already among the Block 46 algebraic
identities. Here it gives a uniform explanation of the finite-field
saturation, rather than an inference from the prime sweep.

## 5. Dyadic proof

In a primitive 2-adic solution exactly one base is even. All three odd is
incompatible with reduction modulo 2. A term with an even base has
exponent at least three, so is zero modulo 8. An odd root has square one
modulo 8, and every odd residue satisfies \(x^3\equiv x^5\equiv x^7\equiv
x\pmod8\). This proves necessity of the three table rows.

For sufficiency, fix the selected even base: use root 1 if its coefficient
is even, and root 2 if its coefficient is odd. Fix one odd root to be 1.
Solve for the remaining odd root. After moving the other terms and
dividing by its coefficient power, the required right-hand side is a
2-adic unit congruent to 1 modulo 8, exactly by the selected table row.
Every such unit is a square in \(\mathbf Z_2\), and every odd power map
on \(\mathbf Z_2^\times\) is bijective. It therefore has the required
sixth, tenth, or fourteenth root.

For completeness, the square criterion follows by successive binary
lifting starting from an odd square modulo 8. Changing an odd trial root
by \(2^{n-1}\) changes its square by \(2^n\) modulo \(2^{n+1}\), allowing
the next square digit to be chosen. The trial roots converge 2-adically.
Odd power maps lift uniquely from the sole unit modulo 2 because their
derivative is odd. Thus the sufficiency assertion covers every higher
power of 2, not merely moduli 8 and 16.

## 6. Two explicit strata that survive every local refinement

The coefficient triple \((a,b,c)=(3,5,2)\) passes the dyadic C-even row
because \(3+5=0\pmod8\). At 3, \(bc=10\) is a square residue. At 5,
\(ac=6\) is a square residue. There are no other odd primes dividing the
coefficients. Consequently

\[
27u^6+3125v^{10}=128w^{14}
\]

has a primitive solution over every \(\mathbf Z_p\), with the C base even
at 2. This is not an integer solution or a Beal counterexample.

The coefficient triple \((a,b,c)=(2,3,11)\) passes the A-even row because
\(3\equiv11\pmod8\). At 3, \(ac=22\equiv1\). At 11,
\(-ab=-6\equiv5\equiv4^2\). Consequently

\[
8u^6+243v^{10}=11^7w^{14}
\]

also has a primitive solution over every \(\mathbf Z_p\), with the C base
odd at 2. Both coefficient triples have all three individual squareclasses
and their pairwise products nonsquare. They survive the earlier
square-product exclusions, as well as every local test of (1).

They also have positive real solutions: choose any positive \(u,v\) and
take the positive fourteenth root for \(w\). Local solutions are permitted
to vary with the place, and neither example is asserted to survive
additional global modular restrictions.

**Finite congruence consequence.** For either fixed coefficient triple,
and every positive integer modulus \(M\), there are positive integer
roots giving globally pairwise-coprime bases and satisfying (1) modulo
\(M\). To see this, enlarge \(M\) to contain every prime dividing \(abc\).
Choose primitive local residue triples and combine them by CRT. Choose a
positive root \(u\) in its resulting progression. Choose a positive root
\(v\) in its progression that is 1 at every prime dividing \(u\) outside
the enlarged modulus. Choose \(w\) similarly to avoid every prime dividing
\(uv\) outside that modulus. These auxiliary conditions have coprime
moduli. At primes inside the enlarged modulus the chosen local primitive
conditions already prevent a common prime factor of two bases. At primes
outside it, the coefficients are units and the root-avoidance conditions
prevent a common factor. Thus global pairwise coprimality and every
specified finite congruence are compatible.

This does not produce exact equality. It proves that a finite congruence
sieve on the original equation and coefficient classes alone cannot
eliminate these strata.

## 7. Certified finite computation and correlation loss

The reusable exact script is `computations/stratification.py`; the input
contract is `computations/stratification_contract.json`. The bounded run
is recorded in `verification/stratification_run/manifest.json`, with full
result rows in `result.json` and a compact report in `stdout.txt`.

All declared finite checks passed:

- 1,824 comparisons of the image-table implementation with literal
  root-triple enumeration over moduli 3, 5, 7.
- 3,402 checks that changing a unit coefficient within its squareclass
  preserves the signature-power image set, through prime 101.
- 5,760 comparisons of exhaustive dyadic root tests with the proved
  coefficient criterion, at moduli 8 and 16.
- The benchmark \((1,2,3)\) is excluded modulo 8.
- A deliberately wrong sign in the C-even row is detected by the
  \((1,7,2)\) control.

Among the 160 coefficient triples modulo 8 compatible with squarefree
coefficients and at most one even coefficient, 60 survive and 100 are
excluded. Modulo 16 the respective counts are 480 and 800: each modulo-8
triple has exactly eight coefficient lifts and its status is unchanged.
The theoretical proof above, not these two counts, supplies stabilization
at all higher powers.

Restricting to all-odd coefficients, the joint residue relation allows
36 of the 64 triples modulo 8. Every single-coordinate marginal is the
entire set \(\{1,3,5,7\}\). Replacing the joint relation by the product of
the three marginals therefore restores 28 rigorously excluded triples.
This is an actual arithmetic example of information lost by independent
lane projection. Keeping joint phases can recover those exclusions.

The finite sweep at odd primes up to 101 agrees with Theorem 1. Its
universal force comes from Sections 2–4, not from extrapolation beyond
the tested range.

## 8. Consequence for the Komorebi strategy

Polyphase decomposition and stratification do provide certified exclusions
of infinite coefficient families. Keeping joint labels prevents a real
loss of information. However, the full local squareclass analysis has an
explicit saturation boundary, with survivors in both C-parity branches.
For those survivors, progress requires information coupling local data
through a single global object, such as a fixed modular form and prime
above 7, a marked field element with the full power conditions, or a
global descent obstruction. Refining the projected coefficient residues
alone cannot supply that coupling.

This is an elementary application to the present research program. No
claim of novelty for the underlying local methods is made.
