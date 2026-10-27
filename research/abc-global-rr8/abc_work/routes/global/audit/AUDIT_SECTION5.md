# Independent supplement: prime and binary exponents

**Primary verdict: proved as written.** This verdict covers the newly added Section 5 and confirms that the preceding Theorems 1–2 and their corollaries retain the same valid proof in this revision. It is not a verdict on unrestricted ABC.

Source: `../PROOF_NOTE.md`, SHA-256 `f4b1c1eb8d4e52ee43634b454ea5fa3e12e88488dc148d76ea68e79a58e29bfc`.

The prior audit `AUDIT.md` refers to the earlier source hash. It remains a historical review of that revision. The current source adds Section 5 and renumbers the subsequent sections.

## Prime-exponent identity

Let ell be an odd prime and c=A^ell+B^ell. For an odd p|c, the already reconstructed order condition says d_p/2 divides ell and ell/(d_p/2) is odd. Therefore d_p is either 2 or 2ell.

The order-two primes are exactly the odd p|A+B. Their birth depths are v_p(A+B), so their contribution to W_n is the odd part of U(A+B). Because ell is odd, the output's 2-adic powerful part is also exactly the 2-adic part of U(A+B). Together these factors are U(A+B).

The only possible prime in G_ell is ell. Fermat's congruence gives A^ell+B^ell=A+B modulo ell, so G_ell equals ell when ell|A+B and equals 1 otherwise. This also handles ell|AB: coprimality then implies ell∤c and ell∤A+B. The primitive order-2ell primes cannot equal ell since 2ell does not divide ell−1.

Consequently

    U(A^ell+B^ell)=U(A+B) ell^[ell|A+B] W_prim

is exact. Every nontrivial prime factor of W_prim is exceptional and has 2ell|p−1, hence p>=2ell+1. The restricted ABC consequence follows uniformly because U(A+B)<=A+B<2A and log c>=ell log A, with A>=2. The displayed escape inequality follows by taking logarithms and replacing the possible ell factor by its upper bound ell. No fixed-base assumption is needed.

## Binary-exponent identity

For n=2^s, s>=1, d_p/2 must divide n with odd quotient. A power of two has no nontrivial odd divisor, so d_p/2=n and d_p=2n. Thus every odd output prime satisfies p>=2n+1. Since n has no odd prime factor, G_n=1. The 2-adic powerful part is 1 by the even-exponent case of Theorem 1. Hence U(c)=W_n exactly. In particular every repeated odd output prime is exceptional.

## Obligation matrix

| Obligation | Status |
|---|---|
| Order dichotomy for odd prime exponent | Passed |
| Inherited odd valuations and 2-adic factor | Passed |
| ell factor, including ell|AB edge case | Passed |
| Primitive-prime lower bound | Passed |
| Uniformity of restricted ABC consequence | Passed |
| Binary-exponent order and powerful-part identity | Passed |
| Exclusion or height bound for repeated primitive factors | Not addressed, and not claimed |

## Finite checks

Independently factored every output for coprime 1<=B<A<=8, ell in {3,5,7,11}, and n in {2,4,8}. The 84 prime-exponent identities and 63 binary-exponent identities passed, including the lower congruence bound on primitive primes. The range and result are recorded in `section5_checks.json`. These checks do not prove the universal statements or constrain exceptional prime distributions.

Review provenance: fresh delegated reconstruction and exact finite checks. No source edits. The obstruction remains the weighted birth-depth contribution of large exceptional primitive primes, and the separate unrestricted-input problem remains open.
