# Source verification for the five-core continuation

Checked 26 September 2026. This is a dependency check, not a historical-priority search. No licensed source material is reproduced in the archive.

## 1. Han: hook formula and V-coding

Guo-Niu Han, *The Nekrasov--Okounkov hook length formula: refinement, elementary proof, extension and applications*, arXiv:0805.1398v1, dated 9 May 2008. Published in Annales de l'Institut Fourier 60(1), 2010, pp. 1--29, DOI 10.5802/aif.2515.

- Preprint: https://arxiv.org/pdf/0805.1398
- Published landing page: https://aif.centre-mersenne.org/articles/10.5802/aif.2515/
- Read and visually checked preprint printed page 3 (PDF page index 2).
- Definition 1.1: V-coding conditions v_i=i modulo t and sum v_i=0.
- Theorem 1.1: size identity and weighted Vandermonde identity for odd t.
- Theorem 1.2: Nekrasov--Okounkov hook formula.
- The preceding paragraph states that absence of a hook of length t is equivalent to absence of all hook lengths divisible by t.

Application: t=5, z=25, partition size n-1. Then the squared-norm condition is sum v_i^2=10n, the sign is positive, and the factorial denominator is 1!2!3!4!=288. These source identities imply the packet expression for tau(n). No unproved analytic interpolation in n is used.

## 2. Garvan--Kim--Stanton: count of five-core partitions

Frank Garvan, Dongsu Kim, Dennis Stanton, *Cranks and t-cores*, Inventiones Mathematicae 101 (1990), pp. 1--17. DOI 10.1007/BF01231493.

- Author-uploaded full text inspected at https://www.researchgate.net/publication/226817316_Cranks_andt-cores
- The host identifies the upload as supplied by Frank Garvan on 19 August 2014.
- Section 5, equation (5.3): a_5(n-1)=sum_{d|n} (d/5) n/d.
- Equation (5.2) and Theorem 4 were also checked for consistency.

Application: at n=p prime, the packet count is p+chi_5(p). This is a statement about the number of cores, not the signed weighted tau sum.

## 3. Bounds and nonvanishing target retained from parent note

B. K. Moriya and C. J. Smyth, *Index-dependent divisors of coefficients of modular forms*, author final manuscript (2013).

https://webhomes.maths.ed.ac.uk/~chris/papers/Moriya_Smyth_final.pdf

The parent note uses the Deligne bound to turn the index-dependent congruence modulo p^6 into an exact zero test for tau(p). The five-core continuation does not claim a uniform solution to that congruence.

## Attribution boundary

The hook formula, V-coding, weighted shell representation, and five-core divisor count are classical. The auxiliary polynomial is an explicit algebraic repackaging of those formulas. No claim has been made that this repackaging, or the elementary index-prime unit observation, is absent from the literature. The root certificates are exact computations for the named fixed primes, not a new verification bound for Lehmer's conjecture.
