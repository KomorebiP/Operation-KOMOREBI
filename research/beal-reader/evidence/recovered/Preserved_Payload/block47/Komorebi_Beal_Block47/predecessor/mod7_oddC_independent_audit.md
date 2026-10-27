# Review of the direct odd-C mod-seven irreducibility proof

Date: 2026-09-19. Predecessor archive SHA-256: `eb8f9537a827c7487875f51f77eb202e3b2008e677f4993f724cc4fc0321349f`.

Reviewed artifact: `mod7_oddC_written_proof.md`.

Reviewed artifact SHA-256: `faa4c7962eab007dd200b8af05f2905c8329125b22aed0e6471b6fffe3f1d0ce`.

**Normalized claim.** For positive pairwise-coprime integers A,B,C satisfying A^3+B^5=C^7 with C odd, the rank-two residual representation at seven of the specified genus-two Jacobian over K=Q(sqrt(5)) is absolutely irreducible.

**Primary verdict: proved as written**, using the named classical inputs at ordinary mathematical written-proof level. This verdict does not mean Lean verification, a complete mod-seven modular elimination, nonexistence of primitive (3,5,7) solutions, or a proof of Beal.

Review provenance: the initial BCDF17/PV source extraction was independent. The reviewer then contributed the determinant-norm replacement and several precision corrections during collaborative repair, and read the complete revised proof. Thus this is not a claim of a fresh uninformed audit of the final repaired argument.

## Imported leaves checked

| Input | Exact locator and verification | Application |
|---|---|---|
| K-defined real multiplication and genus-two realization | Pacetti–Villagra Torcomian [arXiv:2512.17845v1](https://arxiv.org/html/2512.17845v1), Section 7.1 | Gives the two-dimensional K_7 action on V_7(J); explicit rational coordinate changes identify the integral curve |
| Characteristic-zero rank-two conductor at 3 is at most three | Same source, Corollary 3.6 and Table 3.2 | q=5, p=7 satisfy the hypotheses; no residual irreducibility assumption |
| Characteristic-zero rank-two conductor at sqrt(5) is at most three | Same source, Proposition 3.14 and Table 3.5 | q=5, r=3, p=7 satisfy the hypotheses; no residual irreducibility assumption |
| Semistable curve implies semistable Jacobian | Dokchitser–Dokchitser–Maistret–Morgan, [arXiv:1808.02936v2](https://arxiv.org/pdf/1808.02936v2), 15 October 2018, Theorem 1.8(1)=10.3(1) | Genus two and residue characteristic at least seven are in range |
| Semistability implies unipotent prime-to-residue-characteristic inertia | Larson–Vaintrob, [arXiv:1110.0255v4](https://arxiv.org/pdf/1110.0255v4), proof of Lemma 4.6, PDF p. 24, using Grothendieck Proposition 3.5 | Residual one-dimensional constituents are unramified at semistable primes different from seven |
| Associated-character inertia weights at seven | Same source, Lemma 4.10, PDF p. 25; degree convention in Definition 2.8, PDF p. 10 | Semistable J, local ramification index one, degree-one constituent; gives exponents 0,1,7,8 up to reciprocity sign; no large-prime exclusion |
| Principal-idèle relation | Same source, proof of Lemma 5.4 | The eighth-power character evaluated on the global unit has trivial product of local factors |
| Everywhere-unramified finite characters factor through the ordinary class group | BCDF17, [published author PDF](https://lmbp.uca.fr/~billerey/Research/Published/CDF17_ppr.pdf), proof of Theorem 2, p. 4114 | Infinity is also killed by the eighth power; the internally proved class number one applies |

The ordinary Weil pairing and its Galois equivariance are standard structural inputs for the Tate module of a principally polarized Jacobian. The proof uses their four-dimensional determinant consequence, not an unverified assertion about a rank-two polarization. Conductor reduction is justified directly by averaging on finite wild inertia and the behavior of invariant lattices. The class-number assertion has an internal Euclidean proof.

## Reconstruction of the critical chain

**Model and semistability.** The coordinate substitution is over Q, with denominators only involving the nonzero numbers A,B. It identifies curves, rather than only twists. For each prime ell at least seven dividing C, the element u=A^2/B^3 is a unit and satisfies u^3=B and u^5=-A in the residue field. The factorization in the proof is exact. The two quadratics have distinct roots and no common root, since their discriminants are 5 and -16 and their resultant is 45. At each repeated root the double-cover equation has two distinct tangent directions over the residue-field algebraic closure. Hence there are exactly two ordinary nodes. The other two branch points and infinity are smooth. The normalization is a smooth genus-zero curve and has four distinct preimages of nodes. The resulting stable special fiber gives a semistable model; resolution of any thickness in the total space does not require ramified base extension. At ell not dividing C, the discriminant is a unit and gives good reduction. Thus the semistability input to Larson–Vaintrob at seven is proved, not assumed.

**Integral lattice precision.** The action of K_7 makes V_7(J) a rank-two vector space over an unramified quadratic coefficient field. A stable lattice for its maximal order need not equal T_7(J). This causes no gap: its underlying Z_7 lattice is commensurable with T_7(J), and reduction has the same semisimplification. For nested lattices L subset L' with 7L' subset L, the exact sequences through L/7L' and L'/L show equality of composition factors directly; iterating handles commensurable lattices. Therefore the residual constituent is an associated character of J[7], and determinant and Frobenius characteristic polynomial comparisons are legitimate.

**Determinant.** Let delta be the rank-two determinant. The full Tate module has determinant chi squared, while restriction of scalars takes determinant to its field norm. Consequently delta^8=chi^2 modulo seven. This argument requires neither End_K(J) to remain exactly K after specialization nor self-adjointness of a selected real multiplication action. The field norm is the eighth power because (49-1)/(7-1)=8.

**Tameness.** Assume absolute reducibility and write the constituents over the algebraic closure of F7 as lambda and mu. Their product is delta. At wild inertia above 3 or 5, chi is trivial. Raising to the eighth power is injective on a finite abelian group of three-power or five-power order, so delta is trivial there. A nontrivial wild constituent forces its partner to be nontrivial too. Each would have conductor at least two, contradicting the verified sum bound of three. Thus both constituents are tame. The scalar character relation with local Frobenius bounds their tame inertia orders by 8 and 4 at the respective primes. Eighth powers are therefore unramified away from seven and infinity.

**Balancing without an excluded-prime constant.** The unit phi has phi^8=-1 and phi^16=1 modulo seven. Reciprocity applied to lambda^8 forces phi^(8e)=1. It excludes the two mixed weights 1 and 7; the same applies to mu. Both exponents therefore belong to {0,8}. On inertia at seven, the norm determinant identity gives 8(e+f)=16 modulo 48. Only (e,f)=(0,8) or (8,0) works. One constituent nu is consequently unramified at seven. The eighth power of nu is everywhere unramified and trivial at infinity. Class number one gives nu^8=1. This supplies precisely the global implication missing from the rejected 6084 shortcut.

**Frobenius contradiction.** The two smooth characteristic-two reductions have counts (N2,N4)=(3,7) and (3,5). These can be checked without a counting library: over F4 all nonzero x satisfy x^3=1, and y^2+y has image {0,1}. Including two points at infinity gives the stated counts. The full Frobenius polynomial over F4 is Q1 squared or Q0 squared, where Q1=T^2+T+4 and Q0=T^2+4. Hence every constituent eigenvalue alpha satisfies one of these quadratics in the algebraic closure of F7. For Q0, alpha^2=3 gives alpha^8=4. For Q1, alpha^4=5 again gives alpha^8=4. This contradicts nu^8=1. No extraction of a rank-two trace or appeal to 6084 is needed.

## Obligation matrix

| Obligation | Result |
|---|---|
| Domain, primitivity, parity, and source variable dictionary | passed |
| Rational model comparison and genus | passed |
| Semistability at seven without residual irreducibility | passed |
| Source conductor bounds at both bad odd primes | passed |
| Invariance under choice of stable lattice | passed |
| Replacement for exact rank-two cyclotomic determinant | passed |
| Absolute rather than only F49 irreducibility | passed; contradiction begins with Fbar7-valued constituents |
| Local character weights and global unit restriction | passed |
| Class number one and unramified-character conclusion | passed |
| Frobenius data and eighth-power contradiction | passed |
| Lean formalization of Galois-theoretic argument | not addressed |
| C-even branch or surviving Hilbert forms | not addressed |
| Full Beal conclusion | out of scope |

Independent exact Python checks during this review verified the sextic factorization, phi^8=-1, phi^16=1, the two eigenvalue-power identities, and the allowable determinant-weight pairs. The assertions are also justified by the displayed algebra, so their validity does not depend on bounded sampling.

## Scope and relation to the earlier report

The earlier `source_refinement_review.md` correctly rejected a direct specialization based solely on seven not dividing 6084. It did not refute mod-seven irreducibility. The new argument supplies a different global character proof and independently computed Frobenius data. The two verdicts concern different arguments and do not conflict.

The strongest conclusion certified here is the stated absolute irreducibility on the C-odd branch. Applying level lowering, checking any additional restriction-of-image hypotheses, and eliminating all remaining modular forms at seven are separate obligations. No claim of novelty or exhaustive literature coverage is made.
