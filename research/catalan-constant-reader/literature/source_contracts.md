# Catalan Series 08: primary source contracts

Checked 9 October 2026. This record separates bibliographic authentication, the displayed source result, and its application to the recovered packet script. It is not a referee certificate for any complete paper. Original explanations below are written for this project. Complete source papers and full extractions are retained privately outside the distributed project.

## LC01: Zudilin recurrence and identification of its limit

**Source.** Wadim Zudilin, *An Apéry-like difference equation for Catalan’s constant*, Electronic Journal of Combinatorics 10(1), R14 (2003), DOI [10.37236/1707](https://doi.org/10.37236/1707). Published 23 April 2003. The authenticated arXiv copy is [math/0201024v3](https://arxiv.org/abs/math/0201024v3), revised 28 October 2002. PDF SHA-256: `aa81ca0887d316073fd6ae91ae44fa29497b44ed23283bd0c42bbc2832a2becf`. Extraction available. The published PDF was independently read through the journal download.

**Exact input.** Equations (2)–(4), Theorem 1, pages 2–3. For integers n≥1, set p(n)=20n²−8n+1 and q(n)=3520n⁶+5632n⁵+2064n⁴−384n³−156n²+16n+7. Both rational sequences satisfy

\[
(2n+1)^2(2n+2)^2p(n)w_{n+1}-q(n)w_n-(2n-1)^2(2n)^2p(n+1)w_{n-1}=0.
\]

The initial pairs are (u₀,u₁)=(1,7/4), (v₀,v₁)=(0,13/8). Theorem 1 identifies lim v_n/u_n with G=β(2). The script has exactly this normalization. Positivity of v is understood for n≥1, since v₀=0. The recurrence domain excludes n=0 when solving forwards. Classification: known after exact notation translation.

## LC02: exponential rates of the recurrence

Same source, page 3 immediately after Theorem 1. Put φ=(1+√5)/2. The source states lim u_n^(1/n)=φ⁵ and lim |u_nG−v_n|^(1/n)=φ^(−5). The limiting characteristic polynomial is λ²−11λ−1, with roots φ⁵ and −φ^(−5). These are asymptotic statements, separate from a finite recurrence check. The project may derive its own Wronskian and parity bracket algebraically, then invoke the externally identified limit G. Classification: known verbatim up to symbols.

## LC03: integral normalization correction

Same source, Theorem 3, equation (6), page 3, and the final display of §3, page 8. Both the authenticated arXiv v3 PDF and published journal PDF literally print

\[
u_nG-v_n=(-1)^nJ_n/4,
\qquad
J_n=\int_{[0,1]^2}\frac{x^{n-1/2}(1-x)^ny^n(1-y)^{n-1/2}}{(1-xy)^{n+1}}\,dx\,dy.
\]

The printed factor is incompatible with u₀=1. It must not be imported unchanged. An independent exact evaluation gives J₀=8G: substitute x=t², y=1−s², integrate over s, then set t=sinθ. This produces J₀=4∫₀^{π/2}θ cscθ dθ. Integration by parts, with the boundary terms zero, gives −4∫₀^{π/2}log tan(θ/2)dθ=8G, using G=−∫₀^{π/4}log tan z dz. The normalized identity needed by the project is

\[
J_n=8(-1)^n(u_nG-v_n).
\]

Eskandari's independent displayed coefficient formula (LC06) and J₀=8G use this normalization. The factor correction is an explicitly recorded source discrepancy, not a silent change and not a claim that an erratum was found. No erratum was recovered in the bounded search. The all-n identity is justified in `audits/integral_normalization_derivation.md`: a Tonelli/Euler beta expansion of J_n and the exact displayed Whipple transform give F_n=(−1)^nJ_n, while the formal partial fraction coefficient identification gives F_n=8(u_nG−v_n). The printed gamma prefactors leave no factor 2.

## LC04: asymptotic denominator bounds, not exact sharp bounds

**Source.** Wadim Zudilin, *A few remarks on linear forms involving Catalan’s constant*, [math/0210423v1](https://arxiv.org/abs/math/0210423v1), 21 October 2002. Russian publication: Chebyshev Sbornik 3:2(4) (2002), 60–70. SHA-256: `d48f9cec9b496bebf14087e10be6e481532c49693fc3cc2e3adc99aad455b53c`. Extraction available.

**Exact input.** Theorem 1, page 2, supplies 2^(4n+o(n))u_n and 2^(4n+o(n))D_(2n−1)²v_n integrality, with the error exponent of logarithmic size. The recovered recurrence normalization is the same. These statements support exponential denominator rates, but do not alone prove the exact integer T_n=16^nu_n at every n. The older empirical exact bounds must not be relabeled as theorem-level merely because many terms were checked.

## LC05: sharp coefficient arithmetic and a universal proof of T integrality

**Source.** Christian Krattenthaler and Tanguy Rivoal, *On a linear form for Catalan’s constant*, South East Asian Journal of Mathematics and Mathematical Sciences 6(2) (2008), 3–15. Authenticated [0810.1927v1](https://arxiv.org/abs/0810.1927v1), submitted 10 October 2008. SHA-256: `3499b0508c106236a98d5d7be94f04baab82c113655bc1c3c5d2339a5a60e1bc`. Extraction available. Author publication page independently confirms journal placement.

**Notation bridge.** Their G_n in §2 equation (2.1), after k=t+1, is −1/2 times Zudilin’s hypergeometric series F_n. The linear numerator changes by a factor 1/2, the sign changes by −1, and all Pochhammer factors agree. Matching the actual formal partial-fraction coefficients, rather than assuming independence of 1 and G, gives a_n=−4u_n and b_n=−4v_n.

**Exact input.** Theorem 1 in §3 gives 16^na_n∈Z for positive integer n. Theorem 2 in §4 gives 16^nD_(2n)²b_n∈Z. Thus 4·16^nD_(2n)²v_n is an integer, and the project’s weaker factor 8 clearing is valid universally. The n=0 case is checked directly.

Lemma 3, equation (3.1), page 4, gives the additional explicit formula

\[
u_n=\sum_{j=0}^n\binom nj\binom{n-1/2}{j}\binom{n+j-1/2}{j}.
\]

This yields an elementary project proof that T_n=16^nu_n∈Z: for integer h≥0, the coefficient of z^j in (1+4z)^h(1+4z)^(−1/2) is 4^j binom(h−1/2,j). It is an integer because the second factor has coefficients (−1)^j binom(2j,j). Apply this to h=n and h=n+j. After multiplying a summand by 16^n, the remaining factor is 16^(n−j). Every summand is integral. This is a written universal argument, distinct from the finite exact-division audit. Classification: known formula plus an elementary corollary supplied here.

## LC06: Eskandari filter and exact notation dictionary

**Source.** Payman Eskandari, *Improved rational approximations to Catalan’s constant*, [2609.26354v1](https://arxiv.org/abs/2609.26354v1), 22 September 2026. SHA-256: `47bc30efc97bb68c58f1cbacaafdf54a4de596183964a7609ddff11c8764ece6`. Extraction available. The source is a preprint, not labeled peer reviewed here. arXiv HTML advertises CC BY 4.0. Author’s publication page labels the work a preprint.

Use capitals U_n,V_n for this source's integral coefficients to prevent collision with LC01. Then U_n=8(−1)^nu_n, V_n=8(−1)^nv_n, J_n=U_nG−V_n. Put ψ=xy(1−x)(1−y)/(1−xy). Equations (2.4)–(2.5) define the filter J̃_(n,m)=Σ_i(−16)^i binom(m,i)J_(n+i). Its coefficient pair is

\[
\widetilde U_{n,m}=8(-1)^n16^{-n}\sum_{i=0}^m\binom miT_{n+i},
\qquad
\widetilde V_{n,m}=8(-1)^n16^{-n}\sum_{i=0}^m\binom mi16^{n+i}v_{n+i}.
\]

Consequently multiplying by 16^nD_(2(n+m))² gives exactly the historical script's pair A,B. This is not a new filter invention. The arithmetic derives from LC05 because D_(2k) divides D_(2(n+m)) for k≤n+m.

The integral measure is dxdy/[√(x(1−y))(1−xy)], not dxdy/√(x(1−y)(1−xy)). The square root does not cover the factor 1−xy. The maximum ψ is φ^(−5)≈0.09017, greater than 1/16. Therefore the filter changes sign. Even m guarantees J̃_(n,m)>0. Positivity for arbitrary odd m is not supplied.

## LC07: filter growth, decay bound, and exponent index

Same Eskandari source, equations (3.4)–(3.5), (4.2)–(4.5), §5 and Theorem 1.1. For integer m=m(n)≥0 with m/n→α≥0, put R=16φ⁵=88+40√5 and

\[
M(\alpha)=\max\left\{\frac1{16(1+\alpha)}\left(\frac\alpha{1+\alpha}\right)^\alpha,
\phi^{-5}(16\phi^{-5}-1)^\alpha\right\},
\]

with the first expression extended continuously at α=0. The source gives lim (log|Ũ_(n,m)|)/n=−log16+logR+αlog(1+R) and limsup |J̃_(n,m)|^(1/n)≤M(α). The latter is an upper bound, not an equality for the actual integral. Choose m even to prove nonzero error. After reduction, the guaranteed denominator exponent is at least

\[
\frac{\log R+\alpha\log(1+R)-\log16-\log M(\alpha)}{4(1+\alpha)+\log R+\alpha\log(1+R)}.
\]

The source reports a maximum ≈0.62335 at α≈3.31765 and states its rounded theorem as ≥0.62. This is a preprint result with all stated dependencies. It is below 1 and does not imply irrationality. A positive exponent for an upper bound on cleared error only demonstrates that this estimate does not force decay, not that the actual forms diverge. Classification: explicit known filter; no novelty claim.

## LC08: recent irrationality claim and criticism

**Claim source.** Zhi-Wei Sun, *Catalan’s constant is irrational*, [2609.04176v1](https://arxiv.org/abs/2609.04176v1), 3 September 2026. SHA-256: `0aa3bc7e80be3658630fa5d82cb773cba7ec8692d9855a70e71e47f235d2819f`. Extraction available. The abstract claims a proof. The checked arXiv submission history showed only v1 on 9 October 2026. This is a preprint claim, not an established theorem imported here.

**Criticism source.** Dane Wachs, *A note on a recent claimed proof of the irrationality of Catalan’s constant*, [2609.22339v1](https://arxiv.org/abs/2609.22339v1), 16 September 2026, dated 15 September internally. SHA-256: `82940e9304cc0b36662ae3b56cf1bfa452deab2e1f1860efeb8026dd40b289ab`. Extraction available. This is also a preprint. Its §3.4 identifies a quadratic contribution from the prime 2 that it says the displayed asymptotic derivation does not account for. It separately reports finite computations and explicitly does not conclude G is rational or irrational. This project did not independently reproduce those determinant computations and does not treat the critical note as a global theorem disproving every possible repair.

**Safe status sentence.** As of the stated edition date, no proof of Catalan’s constant's irrationality is established by the material checked for this publication. A recent preprint claims a proof and a subsequent primary note identifies an incomplete derivation. This series does not resolve that dispute or prove irrationality. A later verified result would require updating this dated statement.

## LC09: a disjunction about six beta values

**Source.** Wadim Zudilin, *Arithmetic of Catalan's constant and its relatives*, [1804.09922v2](https://arxiv.org/abs/1804.09922v2), updated 31 May 2019, published in Abhandlungen aus dem Mathematischen Seminar der Universität Hamburg 89(1) (2019), 45–53, DOI [10.1007/s12188-019-00203-w](https://doi.org/10.1007/s12188-019-00203-w). The versioned primary HTML and publisher metadata were checked. No complete local source retained for this background contract.

Theorem 1 states that at least one of β(2), β(4), β(6), β(8), β(10), β(12) is irrational. This is a disjunction. It does not isolate β(2)=G, and cannot be turned into irrationality of G without a further argument. The result may appear as context, not as a missing implication in the project's proof. Classification: partial result only.

## LC10: least common multiple growth and the prime number theorem

**Source.** Don Zagier, *Newman’s short proof of the prime number theorem*, American Mathematical Monthly 104(8) (1997), 705–708, DOI 10.2307/2975232. Author-hosted primary PDF https://people.mpim-bonn.mpg.de/zagier/files/doi/10.2307/2975232/fulltext.pdf checked 9 October 2026. Bibliographic first page, definitions on p705 and steps III–VI on pp706–707 were read. The source proves theta(x)/x tends to 1, with theta(x) the sum of log p for primes p at most x. Complete source bytes are not distributed. Eskandari §5, immediately before Eq(5.3), explicitly uses log L_n asymptotic to n as the prime number theorem input.

**Translation supplied here.** Prime factorization gives log L_N = sum_{p^a<=N} log p = theta(N)+sum_{a>=2}theta(N^(1/a)). The source’s theta(x)=O(x) bounds the latter by O(sqrt(N) log N), which is o(N). Hence log L_N/N tends to 1. For m/n tending to finite alpha>=0, N=2(n+m) tends to infinity and log(8L_N^2)/n tends to 4(1+alpha). This is an external classical theorem plus an elementary application, not a finite lcm experiment or a proof of the prime number theorem in this monograph.

## Search boundary and acquisition diagnostics

The bounded search used arXiv abstract pages, primary PDFs/HTML, the journal page, and author publication pages. Exact identifiers and titles were checked, with discovery searches for Zudilin's polynomial coefficients, Eskandari's filter, strong denominator bounds, and recent Catalan irrationality claims. Searches of the user's Library for Zudilin/Eskandari and exact arXiv IDs returned irrelevant fuzzy results and did not identify an authorized cached primary paper. No global novelty claim is made.

Several arXiv legacy HTML/PDF requests through the web reader returned Internal Error or DisabledError. Direct PDF acquisition through the authorized host network succeeded and was checked for PDF signatures, hashed, and extracted with system pdftotext. Three modern PDFs produced a font-type mismatch extraction warning but exited 0. Formula checks used source PDF text plus independent algebra, and the normalization error was checked in the published journal PDF as well. One cache lookup initially failed because the project directory had not yet been created. A cache ingest initially failed because a private cache had no Git ignore coverage. A dedicated private ignored cache was then initialized and all six source ingests succeeded. The full failed/successful command diagnostics are recorded in accompanying JSON logs. A GitHub preprint directory discovery candidate could not be opened through the web reader. It was not used as verified evidence. No messages were sent to authors.
