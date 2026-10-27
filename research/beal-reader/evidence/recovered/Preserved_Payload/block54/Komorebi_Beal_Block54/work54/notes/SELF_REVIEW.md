# Adversarial self-review

Reviewer identity: the same assistant that wrote the proofs. No independent
human, separate-agent review, or Lean certificate is claimed.

1. SAME BASIS: F_21 and N_21 divisibilities and F_22 precision all use the
single actual natural basis. A local diagonalizing basis could destroy the
comparison. The proof factors through the primitive toric line without
changing that basis.

2. ALL VARIABLE PLACES: eta can ramify where beta is unramified. B54.2 covers
those places; the finite grid contains1056 such examples. Restricting eta's
ray support to beta support would be unjustified.

3. FULL FROBENIUS PRECISION: N alone does not rule out the old upper endpoint.
F22=1 mod7^m supplies the missing second summand in Q-1=px+ry. The old Q29
example was explicitly rechecked and fails this new hypothesis, not its own
old statement. The natural t>=1 condition also has a retained counterexample
when removed.

4. LOCAL ORDER: principal units in the unramified quadratic ring need not be
rational integers. Binomial valuation proves the general order formula; a
second sqrt5-basis implementation checks all48 nonzero residue directions.

5. COHOMOLOGY TWIST: delta and alpha cup beta take values in TRIVIAL k. The
Brauer identification is made only after adjoining mu7. The index is prime
to7, and all completions are included. No equality with Br(K)[7] is assumed
before that extension.

6. LIFT VERSUS MATRIX: a global character lift exists, but it need not be the
next matrix diagonal, have the same conductor, or keep the specified local
lifts. No iteration or increased depth follows. The actual endpoint problem
remains open.

7. RECIPROCITY SUPPORT: finite S is the set belonging to a hypothetical fixed
C. The executable fixtures do not bound it. Nonzero reduced C7 survives when
both491 and1471 are allowed, so the code itself rejects a general ray-zero
inference. Full Smith exponents, not just mod7 rank, are checked.

8. PRIME DEGREE: a first exploratory local example used prime-power Q197.
197 is inert in K, so197 is not itself a K-prime norm. The release replaces
that misleading label/example with Q491, a split K-prime norm. The general
algebraic example atQ197 would still have been valid in its local category.

9. DEPTH3 MULTIPLICITY: e=1 and h=2 give n<=3, but they do not force t=1 at
every beta-support prime. The t=3,s=0 case can have trivial inertia correction
and a nontrivial unramified Frobenius correction. The exponent-only analysis retains
both alternatives. The later B54.12 proof eliminates depth3 on the explicit
support only after the exact nonzero ray line forces eta ramification at
all four places. No nonordinary multiplicity is silently discarded.

10. PROOF COVERAGE: finite tests do not certify the geometric leaves, class
field theory, or a Beal solution. New source checks authenticate classical
statements and their translation. Original Block50's interrupted review,
Block52's corrected orbit filter and Block53's environment recovery remain
unchanged in the predecessor.

Assessment: the written deductions are coherent under the declared inherited
hypotheses. Residual risk remains in unformalized proofs and upstream geometry.
The independent implementation validates its finite assertions only.
