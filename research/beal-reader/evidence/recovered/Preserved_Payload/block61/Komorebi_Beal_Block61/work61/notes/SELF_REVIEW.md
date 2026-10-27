# Adversarial self-review

This is review by the same assistant, not independent mathematical review.

1. **Matrix sign and scaling.** With d=1+7^nD and a=Q-7^nD, det expansion gives
   bc=(Q-1)D-7^nD^2. beta is bar(c)/chi, so local nonzero at Q=1 means c unit.
   No division by b or a potentially nonunit toric coordinate is used.
2. **Unramified is not trivial.** The proof explicitly evaluates Frobenius.
   Without eta precision the Q29 matrix in OPPOSITE_FROBENIUS.md survives.
3. **Good versus bad.**29,71,491 are bad because the inherited n>=2 divisibilities
   force them into C. No point count is used at a bad curve. Exact toric trace
   belongs to the same characteristic-zero representation.
4. **Descent.** The action on H1 includes coefficients. At all four inert support
   primes q=1 mod7, both coefficient and tame-conjugation factors are1. The
   class difference is killed by inherited inertia injectivity and split7.
   Inflation–restriction only descends this class, not rho or alpha.
5. **Correct twist.** Primes b move to b/a, and chi^-1 covariance gives weights b.
   The independent checker rederives the permutation in theta=zeta^-1 and
   changes the primitive residue generator. Constant weights fail covariance.
6. **Class group and units.** No unramified seven-character is omitted. Cl(M)[7]
   vanishes by norm/extension from inherited Cl(L)[7]=0. Units have no chi^-1
   eigenspace. The prime over7 is fixed and its value is forced zero.
7. **Rank and coefficients.** R has rank3, not4. Its nonzero k-line is retained.
   All2352 normalized k-valued alpha directions and48 nonzero kernel vectors
   were checked; no F7 coefficient descent assumption is imposed. The final
   contradiction is the nonzero2x2 determinant6, not an enumeration alone.
8. **Conductor quantifier.** The main theorem assumes all beta ramification in S,
   not all divisors of C in S. Additional unramified divisors are harmless, while
   new beta ramification adds columns. COMPLETE H(C) subset U is used separately
   to obtain n<=2 and all beta support in S.
9. **Local positive families.** They remain valid local curves. They do not
   produce one global beta or one compatible natural alpha. No local theorem
   is retracted by the global support contradiction.
10. **Inherited analytical proofs.** The period-source comparison is not proved
    by these new finite tests. It is explicitly inherited and hash-pinned.
    There has been no independent upstream acceptance or Lean compilation.

Unresolved risk is principally upstream hypothesis validation and independent
mathematical review, not an undisclosed extra finite search range. No global
novelty claim is made.
