# Beal research, Block 53
## Global diagonal rigidity and the good-13 depth-one reduction

**Release v5.3.0, 19 September 2026.**

The proposed good-13 argument can be completed under the checkpoint's explicit
inherited geometric inputs. In fact it gives a stronger global statement:

\[
\boxed{\eta_n\equiv1\pmod{7^{\lfloor n/2\rfloor+1}}.}
\]

Here n is the actual global stable-lattice depth of the twisted RM
representation, and eta_n is its actual diagonal correction. Consequently,

\[
\boxed{13\nmid C\Longrightarrow n=1.}
\]

This removes every higher-depth case when 13 is good, without assumptions on
ordinary multiplicities or norm congruences. It does not eliminate depth one,
the bad-13 cases, the complete reducible branch, or the full signature. All
arithmetic conclusions concern the inherited reducible branch of
A^3+B^5=C^7. They are written proofs with explicit input dependencies, not new
Lean certificates or independently reviewed theorems.

## 1. The fixed-prime gap was the decisive issue

The previous brainstorm needed more than residual local splitting. It needed
the two characteristic-zero local toric characters to be exactly chi_7 and 1
at 2,3,5,7 after the specified twist. The preserved geometric notes supply
this through their actual torus and period-lattice descriptions.

At2 and 7 the twist cancels the common unramified quadratic graph character.
At3 and 5 the twisted Jacobian itself has split totally toric reduction. At7,
the analytic uniformization gives the generic torsion sequence at every
7-power level, so passage to the Tate module is valid even in residue
characteristic7. The RM action preserves the filtration, giving one-dimensional
E-pieces with characters chi_7 and 1.

A local character-identification lemma then works to the full available
precision7^n. If a_n+d_n=chi_7+1, a_n*d_n=chi_7, and the residual orientation
is a_n=chi_bar,d_n=1, an element with chi_bar not1 distinguishes the two
characters. Compare traces at that element and its product with an arbitrary
g. The resulting unit cancellation proves a_n=chi_7,d_n=1 locally.

Frobenius supplies the separating element at 2,3,5. At7 it must be an inertia
element, not a falsely assigned cyclotomic Frobenius value49. Thus eta_n is
locally trivial at all four fixed places, not merely unramified there.

The exact inherited file hashes and stronger hypothesis translation are in
notes/LOCAL_INPUT_AUDIT.md. This is an audit of their application, not a claim
that every upstream geometric theorem has now been independently reviewed.

## 2. Natural monodromy gives the uniform precision bound

At every variable bad place outside 2,3,5,7, natural inertia has the shape

\[
I+N,\qquad N=\begin{pmatrix}u&b\\7^n c&-u\end{pmatrix},
\quad N^2=0,\quad b\in 7\mathcal O.
\]

The upper-entry divisibility comes from the natural monodromy content
1+v_7(v_q(C))>=1. The lower-entry divisibility comes from the same global
lattice depth. Hence

\[
u^2=-7^n bc\in 7^{n+1}\mathcal O,
\quad u\in 7^{\lfloor n/2\rfloor+1}\mathcal O.
\]

The reduction of eta_n to that precision is therefore unramified at every
variable bad place, whether or not beta ramifies there. All other finite
places are covered by good reduction and the twist's conductor. Its finite
7-group image has trivial real inertia as well.

The field K=Q(sqrt5) has class number one. The proof includes both the
norm-Euclidean argument and the short Minkowski-bound check. Hilbert class
field theory therefore kills this everywhere-unramified abelian character,
proving the displayed global precision theorem.

This is a global compatibility argument. Local sharpness examples alone
cannot detect the unramified-character obstruction.

## 3. The actual scalar at 13 rules out every n>=2 there

Block52 gives rho(Frob_(13))=-13I at good 13, while chi_7(Frob_(13))=169.
Consequently eta_n(Frob_(13))=-1/13. But

\[
v_7(-1/13-1)=1,\qquad -1/13\equiv15\not\equiv1\pmod{49}.
\]

For n>=2 the global theorem forces eta_n=1 modulo 49. This contradiction proves
n=1. The result is not restricted to the previously isolated ordinary depth 3.

An important negative control is retained: modulo 49, the matrices -13I and
diag(169,1) have identical traces and determinants but different diagonals.
Thus merely comparing characteristic polynomials would miss the depth 2
contradiction. The actual scalar Frobenius identity is essential.

## 4. A stronger order bound at every good place

Put m=floor(n/2)+1. For a good place of normQ outside 7, the actual matrix has
d=1 mod 7^m and lower-left entry divisible7^n. Thus det_E(1-rho(Frob)) lies in
7^m O. Restriction of scalars and the finite-field Frobenius theorem give

\[
\boxed{7^{2m}\mid\#J^\nu(\mathbb F_Q).}
\]

Unlike the earlier Block52 bound, this does not require Q=1 modulo 7.
The Weil bound then implies

\[
7^m\le(1+\sqrt Q)^2.
\]

At split primes 11 and 31, the Jacobian order is strictly less than2401.
For n>=2 this contradicts its required divisibility by 7^4 if reduction is
good. Hence

\[
n\ge2\Longrightarrow11\cdot31\mid C.
\]

Together with good 13=>n=1, the earlier29*43 condition, and 3990*71|C, this gives

\[
\boxed{n\ge2\Longrightarrow1566013238790\mid C.}
\]

No new point counts were needed. This divisor is a necessary condition,
not a contradiction, an upper bound forC, or a uniform upper bound for n.

## 5. What the remaining character can still do

The theorem does not identify all n digits of eta_n. Since2m>=n+1, its
remaining range is square-zero and can be written uniquely as

\[
\eta_n=1+7^m\theta_n\pmod{7^n},
\qquad \theta_n:G_K\longrightarrow\mathcal O/7^{n-m}\mathcal O
\]

with theta_n additive. It is locally zero at 2,3,5,7, but may ramify at variable
C-primes. At n=2, eta2 is exactly trivial and the diagonal lifting obstruction
vanishes. This does not prove beta=0. At n=3, theta3 is an F49-valued character,
and its next-level lifting obstruction can still be nonzero.

The old nonliftable ray family at n=2 cannot be the actual diagonal even when
13 is bad. At n>=3 on bad 13 it is not excluded by the precision theorem alone.
The stronger claim eta_n=1 modulo 7^n is false for the local matrix hypotheses;
a concrete n=3 counterexample remains in the tests.

## 6. Depth-one Kummer support is still constrained, not eliminated

Good13 now automatically puts us at depth 1. Its earlier consequences therefore
need no extra depth hypothesis: a_phi=0, beta is unramified above 71, ramification
above 29 requires a_3/a_5=2, and above 43 requires that ratio5. Beta cannot use
both 29 and 43 and must use an eligible divisor other than71. Other eligible
support remains possible.

There is also a new paired-place restriction without assuming good 13. Normalize
a_5=1 and write u=a_phi/a_5,r=a_3/a_5!=0. If depth-one beta ramified at both
places over 71, the compatible local zero conditions would be
2u+r=0 and 5u+r=0. These force u=r=0, a contradiction. Thus simultaneous
ramification is impossible even on bad 13.

No semilinear conjugation map has been constructed, so this does not establish
paired support, individual unramifiedness at 71 on bad 13, or r inF7.

## 7. Verification and scope of the evidence

The authoritative Block52 verifier, including Block51 and its six selected
historical checks, passed in isolated copies before the new work. Its original
ZIP is preserved byte for byte. The new exact checks use two separate programs:

| Check | Exact coverage/result |
|---|---:|
| Generated nilpotent matrices in Z[phi] | 644, including 600 nonrational examples |
| Admissible matrix/depth instances | 4298, including 320 tight instances |
| Independent full O/343 enumeration | 117649 elements;49 square-zero elements |
| Independent separated-character root checks in O/49 | 112847 candidates;2303 correct roots |
| Exact determinant/norm instances | 10500 |
| Square-zero multiplication instances | 300 |
| Complete normalized Kummer coefficient vectors | 2352 |

Additional cyclic character checks, second-trace checks, inverse checks, prime
splitting tests and exact Weil inequalities are recorded in the JSON outputs.
Counterexamples to missing natural divisibility, full-depth overstrengthening,
missing residual separation, and a trace-only good 13 argument are retained.

The portable verifier deletes outputs in temporary copies, recreates them,
compares exact JSON references and hashes, checks the frozen input documents,
and optionally replays all declared predecessor computations. The separate
release replay record reports the actual clean-extraction execution outcome.
Finite computations do not establish class field theory or the inherited
geometric inputs. The proof review was a self-review, not an independent
mathematical review. No new Lean compilation was performed.

The initial streaming-container launch failed before execution and was replaced
by an observed successful normal subprocess run. That environment failure and
the historical Block50 review interruption and Block52 orbit-filter correction
remain explicitly recorded in DEVELOPMENT_FAILURES.md.

## 8. Next boundary

The remaining reducible cases are now separated more sharply: good 13 necessarily
has depth 1, while all higher-depth cases have13|C and the stronger required
divisors. The unknown global Kummer ratio, eligible beta support, and the actual
remaining additive character theta_n are still not determined. The next block
should impose a genuine reciprocity or representation-algebra restriction on
these same objects, or construct the missing arithmetic conjugation comparison.

The CM cover, higher Hilbert-level branches, full(3,5,7) signature, and full
Beal remain separate obligations. No percentage of completion is inferred from
the number of tests, coefficient vectors, or excluded subcases.
