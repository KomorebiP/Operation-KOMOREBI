# Publication computation and layout QA

Date: 9 October 2026. Reviewer scope: numeric assertions and their finite
contracts, plus the assigned full-resolution guide pages. The geometric proofs
and external theorem hypotheses are audited separately.

## Guide review status

All 34 spread captions and all figure contracts have been read. The numeric
mapping is consistent with `computation/verifieddata.json`, the clean replay
results and the exact calculations listed below. Two mathematical wording
corrections were requested and applied to `visual/main.tex`:

1. Spread07: the axis and diagonal image lines are nonorthogonal but their
   intersection is zero. The incorrect assertion that their images overlap
   was replaced with their image directions having nonzero inner product.
2. Spread28: the uniform five-phase family explicitly requires
   q > 5, 1 <= b < q and gcd(b,q) = 1. The omitted support range is now stated.

Root separately requested the all-degree dyadic claim downgrade on spreads13
and14 and the real-extension convention on spread04. Those revisions are
visible in the current source. The guide does not convert finite enumeration
into an all-degree classification proof.

The first root-rendered full-resolution images of physical pages25 through36
were individually inspected at1754x1241 resolution. Several initial charts
had clipped titles or axis/category labels. A full-page display also made several leading heading digits appear absent.
That observation did not survive direct pixel inspection and enlarged crops of
the saved raster: the digits are present. It is not a PDF defect. The old chart
clipping findings were resolved by the final corrected figures.

## Exact numeric mapping

| Spread | Numbers and assertions checked | Evidence or calculation |
| --- | --- | --- |
| 02 | Coefficients1/2,-2/3,5/6 | Defined example, not measured data |
| 03 | 0 <= p,q <=4, 25 cells, middle p+q=4 | Direct index enumeration |
| 05 | Compression1, rankC1, augmented rank2 | Exact 2x1 rational counterexample |
| 06 | detS3, coefficients1/3,4/3,5/3, alpha(2,3) | Exact rational reconstruction |
| 07 | Parent[[2,1],[1,1]], det1, zero kernel intersection | Direct matrix calculation, nonorthogonal image directions |
| 09 | Lowering r=n-p+1, return d+p-1, example n4,p2 gives3 andd+1 | Degree-shift substitution |
| 10 | Characteristic polynomialt^2-4t+3 and inverse(4I-T)/3 | Exact rational 2x2 identity |
| 11 | Degree70 tuple, 24 distinct conjugates, residue sum210 | Fresh Carrier70 replay and direct integer orbit |
| 12 | gcds3/1, conductors70/210 | Exact gcd formula |
| 13 | Modulus32 six-entry star and three complementary pairs | Exact multiset identity, all three blocks balanced |
| 14 | q8, root4, six internal parent edges, four-vertex star boundary6 | Direct tree and completed trivalent boundary count |
| 15 | Smith diagonal(1,33,33,33,33), torus degree33^4, ambient242h^2 | Fresh Fermat33 replay, 11*22=242 for recorded complete-intersection classes |
| 16 | Modulus50 tuple and two pair stabilizations | Exact K23 multiset identity, independently regenerated |
| 17 | Ages1,1,2,1,2,2 and signs-1,-1,1,-1,1,1 | Integer residue sums at all units modulo7 |
| 18 | 364 freshly regenerated K23 certificates | New reconstruction with8,336 exact age rows |
| 19 | Six-by-six A, determinant-2100, A^T a=70(3,3,1,3,2,3) | Fresh Carrier70 replay |
| 20 | Weights(10,6,3,3,3,8), degree30, sum33, canonical coefficient-3 | Exact AW and sum |
| 21 | Cone dimension5, three singular planes of dimension2, codimension3 | Fresh exact gradient-radical certificate |
| 22 | Integer B=210A^-1, AB=210I, B1=7W | Fresh exact carrier matrices |
| 23 | Orbit dimensions24/48, conductors70/210, sum630 | Fresh transfer replay and independent orbit check |
| 24 | Fourteen signed terms, 30 entries per side | Fresh signed incidence and independent sparse-polynomial check |
| 25 | Auxiliaries24 each, stabilized54 entries, dimension52, remove24 pairs to6 | Exact length and Fermat dimension=length-2 |
| 26 | Capacities6/5,2,1,2,1,1,11/10,1 at25,33,35,39,40,55,70,210 | Exact primal/dual replays and Bellman-Ford checks |
| 27 | 27,131 vectors, 143 invariant, length<=13, cost420, tail14*31=434 | Fresh transfer enumeration plus exact uniform-tail argument |
| 28 | q>5, 1<=b<q, gcd1, dual weights(1,1,1,1,1,q-5)/q | Exact source symbolic congruence, finite checks separate |
| 29 | Degree110 tuple, multiplier11, image(11,44,22,11,11,11), sums330/110 | Fresh witness and direct residues |
| 30 | Equations degreesq,2q,5, degree10q^2, kappa^q=-1/5 | Newton identity and degree product, geometric integrality separate |
| 31 | q7,b1,m35, socle33, coefficient10,504,375*kappa^6, period denominator350 | 625*7^5=10,504,375 and50*7=350, fresh socle tests |
| 32 | One ordered orbit24, permutation sector720 atq7 | Exact orbit and120*(7-1), distinct from total Hodge dimension |
| 33 | Ambient real tangent18, nonsplit graph6, split graph12 | Fresh Weil linearized audit and independent rank check |
| Sources | 34 figures, replay groups24/46/137, exhaustive dyadic through128 | Figure-contract count and current computation manifests |

Schematic spread01's gap size and spread34's status rows are not numerical
measurements. The finite coefficient and period arithmetic does not replace
the geometric complete-intersection period theorem or its normalization.
Historical symmetric-surface and universal statements are identified through
their source arguments, rather than inferred from a pass label.

## Initial layout findings

| Physical page | Spread | Initial root-render findings |
| --- | --- | --- |
| 25 | 24 | Chart title clipped above frame, vertical axis label clipped |
| 26 | 25 | Full-page heading-display observation; saved pixels contain both digits |
| 27 | 26 | Chart title/ylabel/xlabel initially clipped; heading pixels contain both digits |
| 28 | 27 | Legible, no numeric or layout defect found |
| 29 | 28 | Parameter support range correction requested; heading pixels complete |
| 30 | 29 | Chart title initially clipped; heading pixels complete |
| 31 | 30 | Legible, symbolic exponent labels use literal caret notation |
| 32 | 31 | Heading-display observation not reproduced in saved pixels; data legible |
| 33 | 32 | Heading-display observation not reproduced in saved pixels; data legible |
| 34 | 33 | Chart title, left category labels and xlabel clipped |
| 35 | 34 | Heading-display observation not reproduced in saved pixels; status rows legible |
| 36 | Sources | Legible, replay count/range statement matches evidence |

All issues were reported to the visual author and root. No visual files were
edited by this reviewer. Frozen guide acceptance follows. Reader acceptance remains separate.

## Frozen guide acceptance

**PASS** for the numeric contract and assigned physical pages 25–36 of the
36-page frozen guide. The reviewed PDF SHA256 is
`a413b1a74052a91d52bc604972404c3041148e98dbebb0e40977ac46b1c1e30d`.

Each of those twelve actual full-page images was individually inspected at
1754 × 1241 pixels, using both an independently hash-pinned PyMuPDF render and
an explicit `/usr/bin/pdftoppm` (Poppler 24.02.0) render at 150 dpi. Current
figure titles, legends, axes, support restrictions and math labels are legible;
no unresolved clipping or overlap was found. Physical page 31 now uses proper
mathematical exponent labels. Physical page 29 includes the complete support
restriction in both figure and prose. Physical page 34 shows all three Weil
real dimensions, 18, 6 and 12, with intact category labels.

All 34 figure PDF hashes and all 8 current input pins in
`visual/figure_contract.json` match their current files. The publication
numbers and ranges remain consistent with the exact replay outputs. The
machine-readable `GUIDE_COMPUTATION_QA.json` records the PDF, source and image
hashes and each assigned page's inspection status. This acceptance is limited
to this PDF revision and this reviewer scope; it is not a universal proof or
a replacement for geometric and external-source audits.

## Reader numeric review

The reader's opening, August chapters, carrier, transfer, capacity/cycle,
Weil, current evidence and appendix sources were read for numeric claims and
finite ranges. No conflicting numeric claim remains. The final 126-page reader pin is
`9fe0ad078543e195cbf8d1ff7bd0115de23c9adefbb09a7e4b7e48c3a71775ee`.
The numeric review is accepted for this revision. Final assigned-page layout acceptance is recorded below.

| Reader assertion | Verification and scope |
| --- | --- |
| September grouped checks 24 / 46 / 137 | Fresh retained verifiers and validated manifests |
| Five-phase support 241,920 and balance/conjugacy 218,836 | Fresh range 2 <= q <= 64; determinants q = 2,3,4,5,7,11,17; every b at q = 2,7,11 for socle tests |
| Transfer family benchmarks 75 | Fresh inclusive range 6 <= q <= 80 |
| K23 certificates 364 and age comparisons 8,336 | Independently rebuilt seven retained inputs; per-input 40,60,48,48,48,48,72 |
| Dyadic census at 8,16,32,64,128 | All five orbit / pair / SAT(2) / SAT(3) table rows agree with fresh exact census; no all-degree inference |
| Fresh weighted dyadic coefficient equalities 87,376 | Exponents 3 <= s <= 9, two coefficient vectors; historical 89,478,480 at s <= 14 was not fully rerun |
| New degree-33 definitions b=(0,1,1,0,0,1), C=33A^-1 | Fresh Fermat33 matrix and pullback-exponent output verify the stated identity and beta=(1,2,2,1,1,2) |
| Legacy groups 14,4,4,13 | Fresh bounded degree-33, tower, conductor and odd-prime replay; the combined historical 53 includes 18 numerical toy checks |
| All 18 toy table values and tolerances | Match the current float64 replay to displayed precision; not exact variety/cycle proofs |
| Odd-prime spot counts 124 / 436 / 827 | Match archived JSON at degrees 49 / 81 / 125; those three censuses were not freshly reenumerated |
| Global residual table | All 29 tuples at 16 degrees match archived JSON exactly; historical grammar bound N <= 8 and degrees 3 through 100 are not a new complete replay |
| Atomic search 6,600 graphs / 158,400 pairs / max 296/315 | Match historical search70.json; current certificate replay is separate |
| Invariant columns 1,955 of degree <= 18 | Match historical general70.json; discovery optimizer not the proof object |
| Transfer incidence, conductor, capacities and 54-entry stabilization | Same exact data as the guide numeric mapping; fresh independent incidence and orbit checks |
| Global dual 27,131 compositions / 143 invariant / cost 420 / tail 434 | Fresh enumeration, independent shortest paths and stated uniform tail |
| Weil 32 terms each, Gram 2160,-32,-32, 924 basis vectors | Fresh exact exterior computation and independent graph restriction; image dimension 2 |
| Weil isogeny eigenvalues -234,-70,150,250 and multiplicities 2,72,450,400 | Fresh all-basis projector; denominator -30,480,384 equals the three differences' product |
| Weil seed periods 96,0,-8; dual 64 terms; real tangents 18 / 6 / 12 | Fresh source and independent exact rank controls; selected graph only |
| Nilpotent K-rank 2 / Q-rank 4 and mod-3 control | Fresh exact matrix/finite control; no geometric degeneration constructed |
| Invalid m45 example | Tuple sums 131 versus required 135; historical 34/45 capacity excluded |
| q7 cycle degree 490, coefficient 10,504,375, denominator 350 | 10*7^2, 625*7^5, 50*7; geometric period hypotheses handled separately |
| Lean 17 scripts and missing compiler/Mathlib | Consistent with separate formal-source status; no new compiler pass claimed |

The reference to the through-2^14 companion dyadic JSON was corrected to
explicit archival-report wording. That range is historical. The fresh
triangle/tree evaluation range is s = 3 through 9. Numeric agreement does not
close the uniform-write-up obligation or construct a Chow correspondence.


## Reader assigned-page inspection, first frozen revision

All 26 physical pages 77–102 of the 125-page reader with SHA256
`816b4c77d908c2ff0b808198ff246bef4f9bb4433428702fdc15303b46db7594`
were individually inspected in actual full-resolution 1241 × 1754 pixel system-
Poppler images. No clipped equation, figure label, tuple, table cell or
mathematical symbol was found. Displayed values and ranges agree with exact
data.

A minor orphan subsection 36.8.2 “Exact witnesses” on physical 88 was reported.
The author applied a Needspace correction in the successor revision. Physical
91 is a heading-only Part XI divider, identified as a design choice. The live
126-page successor also has heading/TOC edits and explicit degree-33 b/C
definitions. It is not accepted under the old 125-page pin. The per-page hash
record is retained in the prior-review history of
`READER_COMPUTATION_LAYOUT_QA.json`; successor acceptance follows below. No authoring file was edited by this reviewer.


## Final reader acceptance

**PASS** for numeric claims and assigned physical pages 78–103 of the final
126-page reader, SHA256
`9fe0ad078543e195cbf8d1ff7bd0115de23c9adefbb09a7e4b7e48c3a71775ee`.

The 17 changed physical pages 82, 85–91, 93 and 96–103 were individually
inspected in their current actual 1241 × 1754 pixel system-Poppler images.
The other nine page bodies are exact RGB matches above PDF y = 775 points
to previously individually inspected pages of the pinned 125-page baseline.
The current body hashes were independently recomputed; root’s separate
all-page footer validation covers the changed page numbers. The machine
record names each inherited baseline page and pins every final page image.

No unresolved clipping, overlap, equation truncation or numeric discrepancy
was found. The Exact witnesses heading now stays with the beginning of its
table on physical page 89; the continuation repeats its header on page 90.
The heading-only Part XI page 92 is an intentional section divider. The
new degree-33 b/C definitions match the exact retained matrix output.

This acceptance covers the finite arithmetic and the assigned publication
layout. It does not convert a bounded run into a universal proof, replace
the geometric or external-source audits, or assert a solution of the general
Hodge conjecture. No reader or visual authoring file was edited by this
reviewer.
