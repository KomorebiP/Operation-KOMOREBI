# Primary literature and attribution check

Checked October 7, 2026. This is a bounded attribution and dependency check, not an exhaustive novelty search. The present edition proves its packet and enclosure statements internally. No claim of universal historical priority is made.

## Fang and Oosterlee: COS

F. Fang and C. W. Oosterlee, *A Novel Pricing Method for European Options Based on Fourier-Cosine Series Expansions*, SIAM Journal on Scientific Computing 31(2), 826–848 (2008), DOI [10.1137/080718061](https://doi.org/10.1137/080718061). Publisher record and the published primary PDF from the authors' institutional repository were checked: https://ir.cwi.nl/pub/13283/13283D.pdf.

The relevant source is section 2.1, equations (5), (8)–(11), and section 3, equation (19), printed pages 829–831. It relates finite-interval cosine coefficients to characteristic-function samples, distinguishes actual finite-interval coefficients from the full-characteristic-function replacement, and integrates payoff coefficients against the resulting expansion. The notation dictionary is source omega -> present u_k, source interval [a,b] -> present positive interval [0,U], source payoff -> the tilted weighted indicator. The present use additionally needs its own folding/alias and omitted-mode proofs. Those conclusions are not imported from the source's generic convergence discussion.

Overlap classification: COS coefficient machinery is known after translation of notation. The assembled matrix, packet, and accuracy contract is evaluated on its own stated hypotheses.

## Davies: quadratic-form characteristic-function inversion

R. B. Davies, *Algorithm AS 155: The Distribution of a Linear Combination of Chi-Squared Random Variables*, Applied Statistics 29(3), 323–333 (1980), DOI [10.2307/2346911](https://doi.org/10.2307/2346911). Publisher bibliographic record and author-hosted primary article were checked: https://www.robertnz.net/pdf/lc_chisq.pdf, especially printed pages 323–325.

The source handles a signed weighted sum of independent noncentral chi-square variables, with an optional independent Gaussian term, using characteristic-function inversion and numerical error control. This supports the comparator's domain and historical attribution. It does not establish the current Python implementation, requested relative accuracy in extreme tails, or a directed interval contract for this edition. The present independent-normal coefficients lambda map to the source weights; degree-one central terms correspond to zero noncentrality and one degree of freedom.

Overlap classification: the generalized quadratic-form distribution and characteristic-function inversion problem are classical. The comparator implementation requires its own evidence.

## Imhof: historical comparator

J. P. Imhof, *Computing the Distribution of Quadratic Forms in Normal Variables*, Biometrika 48(3–4), 419–426 (1961), DOI [10.1093/biomet/48.3-4.419](https://doi.org/10.1093/biomet/48.3-4.419). The official publisher's article record was authenticated. Full-PDF retrieval failed: the publisher redirected to an inaccessible CDN, and the alternate repository fetch returned an internal error. Therefore this check supports bibliographic attribution only. No precise Imhof theorem is treated as verified by that retrieval.

## Search boundary

Two web search engines were used for exact titles, authors, COS formula sources, and the Imhof/Davies articles. Primary published or author-hosted sources were preferred. No global novelty search, broad citation-graph traversal, or independent source extraction for all classical matrix theorems was performed. Gaussian reduction, exact finite linear algebra and the manuscript's new error bounds are accompanied by internal proofs; remaining Lean obligations are disclosed separately.
