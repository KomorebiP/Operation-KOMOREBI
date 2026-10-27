# Literature comparison for the coupled family

Checkpoint: SF-DISCOVERY-110. Checked 2026-10-09 UTC.

## Question and conclusion

The precise target is the zero-normalized system

\[
U'=1+U(qz)V(rz),\qquad V'=1+U(az)V(bz),\qquad U(0)=V(0)=0,
\]

for four independently specified positive contractions. Its analytic target
is common entire order \(\rho\) determined by

\[
\operatorname{spr}\begin{pmatrix}q^\rho&r^\rho\\a^\rho&b^\rho\end{pmatrix}=1,
\]

with finite positive lower and upper type when proved in the local manuscript.
The comparison asks about the exact normalization, four scales, quadratic
cross coupling, complex entire continuation, and growth-order conclusion.
Existence on a real bounded interval, linear pantograph equations, and
fractional derivatives are different contracts.

This search authenticated an exact scalar baseline and several substantial
adjacent constructions. It did not authenticate a prior source stating this
specific coupled entire-order theorem. Historical priority remains
**unverified**. The bare use of a positive matrix, multitype trees, or a
spectral-radius-one equation is established mathematics and is not a novelty
claim. The release's analytic conclusion depends on its local proof.

## Authenticated sources and exact comparisons

### L1. Méndez: exact scalar diagonal baseline

Miguel A. Méndez, *Combinatorial differential operators in: Faà di Bruno
formula, enumeration of ballot paths, enriched rooted trees and increasing
rooted trees*, Australasian Journal of Combinatorics 89(3) (2024), 350–384.
[Journal PDF](https://ajc.maths.uq.edu.au/pdf/89/ajc_v89_p350.pdf).
The author preprint is
[arXiv:1610.03602v1](https://arxiv.org/abs/1610.03602v1), 12 October 2016.

The published Theorem 2.1, p.354, proves the formal equation
\(\partial_t P_\phi(t,q)=\phi(P_\phi(qt,q))\) with zero initial value.
Example 2.4, p.356, sets \(\phi(t)=1+t^2\). Under \(q=r=a=b=s\), our
normalized solution has \(U=V=P_\phi(z,s)\). The scalar definition is
**known verbatim**. Independent scales and the coupled growth formula are
not supplied by this scalar theorem. The source also supplies its tree
interpretation. Its formal construction is not being claimed as new here.

Authentication and exact formula extraction succeeded from the journal PDF.
The current fetch succeeds, superseding a transient retrieval failure in an
earlier turn. No third-party PDF is included in the release.

### L2. Alrabaiah et al.: coupled fractional pantograph systems

Hussam Alrabaiah, Israr Ahmad, Kamal Shah, Ghaus Ur Rahman, *Qualitative
analysis of nonlinear coupled pantograph differential equations of fractional
order with integral boundary conditions*, Boundary Value Problems 2020,
article 138, published 12 August 2020.
[DOI:10.1186/s13661-020-01432-2](https://doi.org/10.1186/s13661-020-01432-2).

Equation (1) uses two Riemann–Liouville derivatives of orders in \((1,2]\),
a shared proportional delay, cross-variable terms including fractional
derivatives, and integral boundary conditions on \([0,1]\). Theorem 6 gives
a uniqueness criterion from Lipschitz bounds. Theorem 1 recalls a stability
criterion involving a matrix of Lipschitz constants. This matrix is not our
matrix of scale powers, and its spectral-radius bound is not an entire-order
law. No substitution of symbols makes these hypotheses the present
first-order normalized initial-value problem.

The publisher's full text, equation (1), hypotheses, and theorem statements
were inspected. Classification: **partial or adjacent result only**. No
theorem from this source is a dependency of the local proof.

### L3. Blasiak and Flajolet: multitype increasing trees

Pawel Blasiak and Philippe Flajolet, *Combinatorial Models of
Creation–Annihilation*, Séminaire Lotharingien de Combinatoire 65 (2011),
article B65c. The inspected author version is
[arXiv:1010.0354v3](https://arxiv.org/abs/1010.0354v3), 25 June 2011.

Note 25 and Proposition 24, pp.62–64, describe multitype increasing trees and
ordinary differential systems
\(\partial_z T_j=\phi_j(x_1+T_1,\ldots,x_m+T_m)\), with zero initial
values. This authenticates established multitype combinatorial machinery.
Those displayed arguments all use the same \(z\), so the proposition does
not itself state four independently dilated arguments or their entire
growth law. Its equation (102) is an ordinary differential system.

Metadata and the full proposition were checked in the primary PDF.
Classification: **partial or adjacent result only** for the present coupled
dilation theorem. A stronger historical reduction through weighted species
would require an explicit translation beyond this checked proposition.

### L4. Mauldin and Williams: an established spectral-radius exponent

R. Daniel Mauldin and S. C. Williams, *Hausdorff Dimension in Graph Directed
Constructions*, Transactions of the American Mathematical Society 309(2)
(1988), 811–829.
[Author-hosted journal scan](https://sites.math.unt.edu/~mauldin/papers/no67.pdf).

On p.812 the construction matrix has entries \(t_{ij}^{\beta}\), and
\(\Phi(\beta)\) is its spectral radius. Theorem 2 establishes the monotonic
spectral parameter. Theorem 3, p.813, identifies the Hausdorff dimension by
\(\Phi(\alpha)=1\) for a strongly connected graph-directed geometric
construction satisfying the stated nonoverlap and similarity assumptions.
The dictionary \(t_{11}=q,t_{12}=r,t_{21}=a,t_{22}=b\) gives the same
matrix formula. No geometric realization or separation hypotheses are
established here, and Hausdorff dimension is not entire-function order.

Classification: **partial or adjacent result only**, with the spectral
mechanism itself established. The scan was read visually at pp.811–813 after
text extraction returned blank pages. Temporary read-copy SHA-256:
`f37b28a0fb319d9d51440de94cd50be1af134bec41833ff6256bec52ecd9ff56`.
The publisher endpoint returned HTTP 403. The author copy succeeded and is
not bundled.

### L5. Dascaliuc et al.: nonlinear alpha-Riccati equations

Radu Dascaliuc, Tuan N. Pham, Enrique Thomann, Edward C. Waymire,
*Transformation of Stochastic Recursions and Critical Phenomena in the
Analysis of the Aldous-Shields-Athreya Cascade and Related Mean Flow
Equations*, [arXiv:2411.00629v2](https://arxiv.org/abs/2411.00629v2),
revised 2 May 2025.

Equation (1.8) is \(u'(t)=-u(t)+u(\alpha t)^2\). Theorem 6.1 studies
nonuniqueness and asymptotic behavior in an advanced regime \(\alpha>1\)
for specified real initial values. The present family has constant forcing,
no current-state damping, two components, independent contractions, and
holomorphic normalization. These differences prevent direct identification.
The primary HTML equation and theorem were inspected and the version was
checked against arXiv metadata. Classification: **partial or adjacent result
only**. This extends the comparison already recorded for the scalar family.

### L6. Knessl and Szpankowski: two directional path weights

Charles Knessl and Wojciech Szpankowski, *Binary Trees, Left and Right Paths,
WKB Expansions, and Painlevé Transcendents*, ANALCO 2006, 198–204.
[DOI:10.1137/1.9781611972962.2](https://doi.org/10.1137/1.9781611972962.2),
[author PDF](https://www.cs.purdue.edu/homes/spa/papers/analco06.pdf).

Equations (1.2) and (2.11) state
\(C(w,v,z)=1+zC(w,v,wz)C(w,v,vz)\). Here \(C\) is an ordinary generating
function for unlabeled ordered binary trees with two path-length weights.
This supplies an established product of independently dilated functions.
It has neither the derivative nor the zero normalization in our equation.
The ordinary convolution also differs from the factorial factors arising
in increasing-tree differential recurrences. No transform identifying the
two equations has been established in this check.

The primary author PDF was fetched with the local reader after the web
reader reported it inaccessible. Its equation extraction succeeded.
Classification: **partial or adjacent result only**. This resolves the
previous release's unverified full-text lead, without rewriting that earlier
historical search record. Temporary read-copy SHA-256:
`b81aa8c4e1c553d648ce16f3e60de8c2c9d8b7e559a7f1dac786639be9458b22`.
The PDF is not included in the release.

## Search record and limitations

Two available web search engines were used. Discovery, exact-source
verification, and the second vocabulary strategy were performed by the same
searching agent. This is a second search strategy, not an independent
literature review. Search date was 2026-10-09 UTC. There was no lower date
restriction. The horizon is material accessible through that date. Searches
used English terminology in complex analysis, functional differential
equations, analytic combinatorics, multitype branching, and graph-directed
geometry.

The query strings were:

1. `nonlinear coupled pantograph equations entire function order spectral radius growth quadratic`
2. `"pantograph" "nonlinear" "entire" "order"`
3. `"1610.03602"`
4. `"nonlinear pantograph" "growth" entire`
5. `"pantograph" "spectral radius" nonlinear`
6. `"multitype" "entire functions" growth differential`
7. `"nonlinear" "pantograph" "quadratic" system`
8. `"Mendez" "multivariate" "path length" "trees"`
9. `"multitype increasing trees" differential equations`
10. `"graph directed" "spectral radius" "Mauldin" pdf`
11. `"nonlinear pantograph" "order" "entire" -fractional -wave -neural`
12. `"pantograph" "Perron" "growth"`
13. `"U(qz)" "V(rz)"`
14. `"nonlinear functional differential" "entire" "spectral radius"`
15. `"multitype increasing trees" "path length"`
16. `"Binary Trees, Left and Right Paths, WKB" pdf`
17. `"coupled pantograph" "entire" "growth"`

The earlier scalar/asymmetric ledgers were read first. Méndez's bibliography
was inspected, including its leads to increasing-tree species and
combinatorial differential systems. The separate multitype search led to
Blasiak–Flajolet. The fractional paper's references and spectral-radius
stability statement were inspected. The earlier Knessl–Szpankowski lead was
followed to its now accessible author copy. The graph-directed spectral
search supplied the separate Mauldin–Williams comparison.

No exhaustive backward or forward citation traversal was completed.
MathSciNet, zbMATH, subscription books, non-English historical literature,
and unindexed manuscripts were not systematically searched. General
multisort weighted-species theory might contain the formal construction
after translation even if the exact equation is not printed. Broader
nonlinear renewal and branching-process growth results may also subsume
parts of the analytic argument. These are specific coverage gaps, not
evidence of absence.

## Release wording

A supported description is: *We develop a normalized coupled nonlinear
dilation family, prove its analytic growth statement in this manuscript,
and specify its scalar reductions and an obstruction to constant linear
operator decoupling. Its scalar diagonal and several organizing mechanisms
have established precedents. Priority for the precise coupled results
remains unresolved.*

No retrieved theorem is being used as a substitute for the local entire
continuation, order, type, or identifiability proofs. This report changes
attribution and comparison status only. It supplies no global novelty
certificate and no claim that all possible transformations have been ruled
out.
