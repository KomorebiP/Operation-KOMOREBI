# Current state

## Written proof completed in this block

1. Any restored NCT oracle admits a protected, write-once-output normal form with 2S+1 gates and 2T Toffolis.
2. Such protected oracles require at least 2 deg(f)-3 Toffolis. The corresponding monomial construction is optimal within this normal form.
3. Power-of-two majority-clique is an explicitly encoded NP-complete family of full F2 degree N=binom(M,2).
4. Its protected Toffoli count is at least 2N-3; unrestricted Toffoli count is at least N-1.
5. Every active midpoint satisfies D=E, A+B=fD, and admits an exact unit-certificate reconstruction. A balanced cut satisfies T+2kappa>=2deg(f)-3.
6. Decoding grade kappa=n-1 occurs in an explicit O(n)-gate reversible prefix; scalar grade is not construction cost.

## Corrections / failed extensions

- Repaired repeated-control nonstandard Toffoli emissions in the predecessor compiler.
- Did not promote the protected 2N-3 bound to the unrestricted model; normalization loses a factor of two.
- Degree is at most N and cannot itself give a superpolynomial endpoint, even for an NP-complete family.
- A timed-out generic graph search is retained as inconclusive and replaced by exact structured certificates.

## Still required for the original goal

A superpolynomial bound for protected-output stable length on the majority-clique family (or another polynomially encoded NP language), allowing arbitrary nonlinear preparation, input modifications, auxiliary workspace and shared cleanup. The normal-form theorem transfers such a bound to unrestricted circuits. No such endpoint is proved here.

The decisive future obligation is a resource-sensitive bound on shared intermediate preparation. Counting interaction degree, dirty coefficient expansion, or the number of local certificates does not discharge it.
