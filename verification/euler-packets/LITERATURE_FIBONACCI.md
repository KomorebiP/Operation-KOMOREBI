# Source check: Fibonacci packets and polynomial calculus

EULER-CASE-005 · checked 29 October 2026. This is a bounded check of Komorebi
project literature, not a global novelty search. Exact source revisions,
SHA-256 hashes, Git blob identities, hypotheses and translation are recorded in
[LITERATURE_FIBONACCI.json](LITERATURE_FIBONACCI.json).

## Authenticated sources and extraction

1. **Komorebi P., Paper IX, Euler Congruences: Completion, factorial
   strengthening, and sharp dyadic geometry.** Collection revision
   `2dc495d16c5c76d2e55e04f73b9e9872193fd4c2`.
   `sources/main/parts/10_foundations.tex`, theorem
   `thm:companion-foundation`, states and proves companion packet dynamics and
   their characteristic-polynomial recurrence. The following Fibonacci
   specialization supplies trace L_N and determinant (-1)^N.
2. **The same paper, supplement_06.tex, sections 3 and 4.** The source derives
   Fibonacci states from the actual sequence, Lucas traces from an independently
   defined recurrence, the parity sign, the N=0 boundary and packet uniqueness.
   Its reported formal results are source evidence only. This extension runs no
   Lean and does not reattest the historical formal build.
3. **The same paper, 72_recovered.tex.** The exact locators are
   `hist:lem:matrix_power_amplification`,
   `hist:thm:matrix_polyphase_precision`,
   `hist:ex:refined_fibonacci_ladder`, and
   `hist:ex:fibonacci_finite_adelic`. The checked version includes explicit
   corrections requiring positive L and integral matrices, states and
   observation vectors. Those requirements are retained here. The C^12 and
   C^24 matrices were checked entry by entry against exact powers.
4. **Komorebi P., Komorebi Math, Exact typed expressions across two bases.**
   `docs/TYPED_EXPRESSION_EXAMPLE.md`, pinned library revision
   `a3aa04ac18a523f30c50c7f5dba709f88e904eff`, sections 1–8 and the reverse-identity
   adversary. It gives the five vectors, primitive and connection matrices,
   derivative, identity round trip, scalar integral 5/4 and reverse boundary
   defect. The production calculus implementation at that same pin provides a
   separate finite numerical comparison, not an independent universal proof.

The collection was fetched from origin before the check; library source matches
the site's exact pin. Author/title metadata were checked in the paper README and
library CITATION.cff. The public GitHub connector then fetched all four exact
revision paths. Recomputed Git blob identities of those public contents matched
the local objects. The web renderer could not fetch these immutable GitHub
pages, so it supplied no statement evidence. Primary text was read from the
authenticated Git objects. Full fetched sources were not duplicated here.

## Translation and implication verdicts

| Application | Translation and required hypotheses | Verdict / overlap |
|---|---|---|
| Sampled Fibonacci recurrence | C is [[1,1],[1,0]], state (F_(n+1),F_n); integer scalar observation is the second coordinate; all N,j,k natural | **Verified; known after translation of notation.** The source's characteristic recurrence gives u_(k+2)=L_N u_(k+1)-(-1)^N u_k. The worked page separately derives the two-by-two identity entrywise. |
| Euler transfer followed by sampling | Compose the preceding L(H) sequence encoding with a finite-row selector; target is F_(Nk+j+1) because g_k=F_(k+1) | **Verified; formal corollary not stated.** No invertibility of a single sampled lane is inferred. |
| Dyadic refinement and binomial expansion | H=12, L=3, integer initial state and observation; a,n,r,x,j nonnegative | **Verified; known after translation of notation.** The finite expansion is valid for nonnegative integer x; no p-adic continuation is claimed without a separate domain/convergence statement. |
| Sharpness at n=1 | B_0=I modulo 2 and B_(a+1)=B_a+2^(a+2)B_a^2 | **Verified; formal corollary not stated.** The remaining observed factor is odd, giving exact valuation (a+3)r. |
| Simultaneous factor 144 | The source's factor-24 matrix has every entry divisible by six; all matrices remain integral | **Verified; formal corollary not stated.** The source guarantees 24^r; the explicit extra factor gives 144^r, hence both 2^(4r) and 3^(2r). No general optimality assertion is made. |
| Polynomial calculus chain | Source G_k becomes B_k; source polynomial E_n becomes mathcal E_n. C_d maps Euler to Fibonacci degree-d columns. D and J use different source/target degree bounds. | **Verified; known after translation of notation.** The displayed chain is I_4, and integral covectors pair to 5/4. |
| Reverse primitive/derivative | Evaluation at zero in Fibonacci coordinates is (1,0,1,0,1), not first-coordinate extraction | **Verified; known after translation of notation.** J_0D=I-1*ev_0, with an explicit rank-one boundary defect. |

Authentication, extraction and application have all been performed. No source
ambiguity or missing hypothesis remains for these finite/integral applications.
The checked source scope supplies no historical priority, exclusive-method,
speed or global literature conclusion.
