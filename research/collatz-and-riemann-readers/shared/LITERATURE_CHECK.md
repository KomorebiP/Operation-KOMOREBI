# External mathematical sources for the Collatz and Riemann pieces

Checked 2026-10-08. Task: authenticate classical definitions, hypotheses, normalizations, and the exact external implications used by the two manuscripts. This is a bounded source check, not a novelty investigation and not a fresh audit of the Komorebi proofs. The mathematical literature-check workflow was applied. No external PDFs were retained locally, so there are no source-cache hashes. Source extraction occurred through the cited official pages, author preprints, and publisher-authorized journal mirrors.

## Collatz

### C1. Classical map and odd-only map

**Verified source:** Terence Tao, *Almost all orbits of the Collatz map attain almost bounded values*, Forum of Mathematics, Pi **10** (2022), e12. Version used: arXiv:1909.03562v7, 16 July 2026. The version page reports corrections including the statement of Lemma 7.9. The source check here uses only the introduction and its stated results.

Links: <https://arxiv.org/abs/1909.03562v7>, <https://arxiv.org/html/1909.03562v7>. Published DOI: <https://doi.org/10.1017/fmp.2022.8>.

The classical map is C(n)=3n+1 for odd positive n and C(n)=n/2 for even positive n. The Collatz conjecture says every positive orbit reaches 1. In section 1.2, the Syracuse map on positive odd integers is S(n)=(3n+1)/2^{v_2(3n+1)}. Its orbit consists of the odd elements of the corresponding classical orbit. Conjecture 1.5 is the equivalent assertion that every positive odd orbit reaches 1.

**Translation:** The project's odd-map symbol may differ, but it must strip every factor of 2. It is distinct from the shortcut map T(n)=(3n+1)/2 for odd n. This distinction is essential for branch exponents and stopping-time counts.

### C2. Tao's exact density statement

Same checked source, Theorem 1.3 and Definition 1.2. For any f:N_{>0}->R satisfying f(n)->+infinity, C_min(n)<f(n) outside a set of logarithmic density zero. Equivalently the logarithmically weighted relative frequency of the good set tends to 1. Theorem 1.6 gives the corresponding statement for the odd-only map, with density relative to positive odd integers.

This is an almost-all theorem. It does not assert that every orbit reaches 1 or that a single fixed finite bound holds on a set of logarithmic density 1. Any such stronger application is unsupported by the citation.

### C3. Finite stopping time of natural density one

**Statement checked in primary research text:** Tao, same version, section 1.1, attributes C_min(n)<n for almost all n to Terras and independently Everett, and explicitly says natural density can be used for these earlier results.

**Original publication metadata authenticated:**

1. Riho Terras, *A stopping time problem on the positive integers*, Acta Arithmetica **30** (1976), 241–252. DOI <https://doi.org/10.4064/aa-30-3-241-252>. Publisher record <https://www.impan.pl/get/doi/10.4064/aa-30-3-241-252>.
2. Riho Terras, *On the existence of a density*, Acta Arithmetica **35** (1979), 101–102. DOI <https://doi.org/10.4064/aa-35-1-101-102>. Publisher record <https://www.impan.pl/get/doi/10.4064/aa-35-1-101-102>.
3. C. J. Everett, *Iteration of the number-theoretic function f(2n)=n, f(2n+1)=3n+2*, Advances in Mathematics **25** (1977), 42–45. DOI <https://doi.org/10.1016/0001-8708(77)90087-1>. Publisher record <https://www.sciencedirect.com/science/article/pii/0001870877900871>.

**Acquisition boundary:** The Terras original PDF links returned HTTP 403 or fetch errors. Everett's original body was unavailable through the retrieval tool. Their original proofs were not reread. The exact density statement is supported by the checked Tao text. Cite both Terras papers when presenting the historical density result, since the 1979 note supplies details of the density argument.

The claim concerns some iterate strictly below its own starting value. Iteration of that conclusion across all starting values is not supplied by a density-one assertion.

### C4. Author survey and conventions

Jeffrey C. Lagarias, *The 3x+1 Problem: An Overview*, in *The Ultimate Challenge: The 3x+1 Problem*, AMS, Providence, RI, 2010, pp. 3–29. Checked corrected author preprint: arXiv:2111.02635v1, 4 November 2021, <https://arxiv.org/abs/2111.02635v1>, <https://arxiv.org/pdf/2111.02635v1>.

The first page separately defines the classical map C and shortcut map T. It identifies T(n)=C(C(n)) for odd n and T(n)=C(n) for even n. Its survey horizon is 2010, despite the 2021 preprint posting. It is suitable for background and notation, not a current computational verification record.

## Riemann hypothesis

### R1. Completion and zeros

**Verified official mathematical documentation:** NIST Digital Library of Mathematical Functions, version 1.2.8, release 15 September 2026, sections 25.4 and 25.10(i).

Links: <https://dlmf.nist.gov/25.4.E4>, <https://dlmf.nist.gov/25.4.E3>, <https://dlmf.nist.gov/25.10.i>.

The completion is xi(s)=s(s-1)Gamma(s/2)pi^{-s/2}zeta(s)/2 and satisfies xi(s)=xi(1-s). The nontrivial zeros of zeta lie in 0<Re(s)<1 and have symmetry about the real axis and Re(s)=1/2. RH says all nontrivial zeros have real part 1/2.

**Translation:** z=rho-1/2 is a centered zero. In a heat packet, z may have nonzero real part until RH is proved. Replacing all z by imaginary ordinates in an unconditional identity would silently assume RH.

### R2. Möbius summatory equivalent

Lynnelle Ye, *Bounding sums of the Möbius function over arithmetic progressions*, arXiv:1406.7326v1, 27 June 2014, section 1. Links: <https://arxiv.org/abs/1406.7326v1>, <https://arxiv.org/html/1406.7326v1>.

The introduction explicitly states the classical equivalence RH iff M(x)=O_epsilon(x^{1/2+epsilon}) for every epsilon>0, where M(x)=sum_{1<=n<=x}mu(n). The implied constant may depend on epsilon. This exact statement was extracted from the research paper, not independently proved during this source check. The source distinguishes RH from GRH assumptions for arithmetic progressions.

The stronger bound |M(x)|<=sqrt(x) is not this equivalence. Nor does a bound at finitely many x prove the asymptotic criterion.

### R3. Báez–Duarte's exact sequential criterion

**Verified full primary journal PDF:** Luis Báez–Duarte, *A sequential Riesz-like criterion for the Riemann hypothesis*, International Journal of Mathematics and Mathematical Sciences **2005**, no. 21 (2005), 3527–3537. Revised 18 August 2005. DOI <https://doi.org/10.1155/IJMMS.2005.3527>. Authorized EMIS journal mirror <https://www.maths.tcd.ie/EMIS/journals/IJMMS/Volume2005_21/141565.pdf>.

Theorem 1.1, equations (1.1)–(1.2): c_k=sum_{j=0}^k(-1)^j binom(k,j)/zeta(2j+2). RH holds iff c_k=O_epsilon(k^{-3/4+epsilon}) for every epsilon>0 as k tends to infinity. Equation (3.6), p. 3532, identifies exactly c_k=sum_{n>=1}mu(n)n^{-2}(1-n^{-2})^k. For k=0, use the defining finite binomial sum or the convention (1-n^{-2})^0=1.

Theorem 1.1 also states that the stronger estimate c_k=O(k^{-3/4}) implies simplicity of the nontrivial zeros. It is not interchangeable with the epsilon-family equivalent to RH.

**Application:** The project's K-indexed coefficient is c_K verbatim if its weight is n^{-2}(1-n^{-2})^K. The criterion and coefficient are classical. Packet decomposition may reorganize them but does not make the criterion new.

### R4. Guinand–Weil explicit formula with checked normalization

**Verified primary open research article:** Andriy Bondarenko, Danylo Radchenko, Kristian Seip, *Fourier Interpolation with Zeros of Zeta and L-Functions*, Constructive Approximation **57** (2023), 405–461. Version of record 10 November 2022. DOI and full text <https://doi.org/10.1007/s00365-022-09599-w>, <https://link.springer.com/article/10.1007/s00365-022-09599-w>.

Introduction equation (1.1) uses fhat(xi)=integral_R f(r)e^{-2pi i r xi}dr. It applies when f is analytic in |Im z|<1/2+epsilon and decays there as O((1+|z|)^{-1-delta}), epsilon,delta>0. Its zero sum is sum_rho f((rho-1/2)/i), with multiplicities, without assuming RH. The other terms are the pole evaluations f(±i/2), the digamma integral, and a prime-power Fourier sum weighted Lambda(n)/sqrt(n).

**Gaussian application derived here:** For t>0 and real u, choose f(r)=e^{-tr^2}cos(ur). Its Fourier transform is sqrt(pi/t)/2 times the two Gaussians centered at ±u/(2pi). Pole contribution is 2e^{t/4}cosh(u/2). Reflection symmetry identifies its zero sum with sum_rho e^{t(rho-1/2)^2+u(rho-1/2)}. This is the manuscript's heat packet normalization.

The original historical article's metadata was authenticated: A. P. Guinand, *A Summation Formula in the Theory of Prime Numbers*, Proceedings of the London Mathematical Society (2) **50** (1948), 107–119, DOI <https://doi.org/10.1112/plms/s2-50.2.107>. Its complete body was not accessible. Use the checked modern equation for normalization and hypotheses.

### R5. Digamma series

NIST DLMF, same version, equation 5.7.6: <https://dlmf.nist.gov/5.7.E6>. For z outside 0,-1,-2,...,

psi(z)=-gamma+sum_{k>=0}(1/(k+1)-1/(k+z)).

**Derived estimate:** For a>0 and real y, subtract the series at a to obtain psi(a+iy)-psi(a)=sum_{k>=0}iy/((k+a)(k+a+iy)). Therefore |psi(a+iy)|<=|psi(a)|+|y|sum_{k>=0}(k+a)^{-2}. This ensures sufficient polynomial growth for a fixed positive-width Gaussian transform. Any stronger asymptotic assertion needs a separate argument.

### R6. Hermite normalization and Mehler identity

NIST DLMF, same version: Table 18.3.1 <https://dlmf.nist.gov/18.3.T1>; L^2 expansions in section 18.18(i) <https://dlmf.nist.gov/18.18.i>; Mehler equation 18.18.28 <https://dlmf.nist.gov/18.18.E28>.

For physicists' H_n, the weight is e^{-x^2}, the squared norm is sqrt(pi)2^n n!, and the leading coefficient is 2^n. Thus phi_n(x)=pi^{-1/4}(2^n n!)^{-1/2}H_n(x)e^{-x^2/2} is the standard normalized Hermite basis of L^2(R).

Mehler's identity holds for |q|<1: sum_{n>=0}H_n(x)H_n(y)q^n/(2^n n!)=(1-q^2)^{-1/2}exp((2xyq-(x^2+y^2)q^2)/(1-q^2)). Multiplication by the normalizing Gaussian gives the Hermite-function kernel. It does not, by itself, establish positivity of a different arithmetic packet operator.

## Verification boundary and source failures

The classical statements above were checked in the specified versions. No source check supplies the missing global Collatz descent, an RH arithmetic cancellation estimate, or the manuscript's novel implication. Those need the project's own proofs.

Unavailable original texts: Terras PDF links produced HTTP 403/fetch failures, Everett and Guinand complete original bodies were unavailable, and a Cambridge rendering of Tao's journal page exceeded the fetch size limit. Successful alternatives were the version-pinned Tao author preprint, the full Báez–Duarte journal mirror, and the full Bondarenko–Radchenko–Seip version of record. No inaccessible original body is represented as having been reread.

## Addendum: zero-count bound for Gaussian summability

Checked later on 2026-10-08 in response to the manuscript proof audit. Bondarenko–Radchenko–Seip, same version of record, section 2.4, equation (2.11), explicitly states the unconditional Riemann–von Mangoldt formula

N(T)=T/(2pi) log(T/(2pi e))+O(log T).

Here N(T) is the usual count of nontrivial zeros at positive height up to T, with multiplicity. Consequently N(T)=O(T log T). Conjugation symmetry gives the corresponding bound for both signs of the height. This justifies summing any fixed polynomial weight against exp(-t gamma^2), t>0, and locally uniform Gaussian domination when t stays bounded away from zero.

Exact locator: <https://link.springer.com/article/10.1007/s00365-022-09599-w>, section 2.4, equation (2.11). DLMF section 25.10 discusses the counting function but does not display this asymptotic, so it should not be the sole citation for the bound. The zero-count estimate does not assume RH and does not convert off-line zeros to real ordinates.
