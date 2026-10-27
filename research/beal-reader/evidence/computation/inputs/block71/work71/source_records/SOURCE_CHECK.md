# Source audit and notation translation

Checked 21 September2026. No global novelty claim. This is a bounded verification
of the exact analytic/Galois arrows used here, with an explicit application map.
Primary source pages were inspected through web-rendered PDF pages. No local PDF
cache or downloaded source checksum is claimed.

## Gregory and Liedtke (primary published source)

Oliver Gregory and Christian Liedtke, **p-Adic Tate Conjectures and Abeloid
Varieties**, Documenta Mathematica24(2019),1879-1934. Published author article:
https://ems.press/content/serial-article-files/26496

Section4.4, printed1905-1908. Lemma4.9 on printed1906, and Proposition4.11 on
printed1907-1908, describe the Tate-module extension of an abeloid through the
ell-adic completion of its period lattice, including ell=p. The necessary
commutative diagram of a Galois-equivariant Tate-module homomorphism induces
matrices rho,sigma with gamma(Q_A)*rho=sigma*gamma(Q_B). Applying valuations
provides ord(Q_A)*rho=sigma*ord(Q_B).

Dictionary: source local K -> our F=Q7(sqrt5); source ell=p ->7; source Q_A=Q_B
-> our actual marked2-by-2 period matrix. Source rho,sigma -> S_T,S_Y for actual
multiplication by coefficient w. Our valuation matrix7cI is derived from the
inherited family, not supplied by the source. Cancelling it before reduction gives
S_T=S_Y, then the residual period commutator determines +/-R.

This uses an existing endomorphism of the Tate module and necessary functoriality.
It does NOT require an incorrect general surjectivity from geometric endomorphisms
to all Galois-equivariant homomorphisms. Source authenticity and theorem extraction
were checked; the marked-family application is the written proof in the notes.

## Ichikawa (primary author preprint)

Takashi Ichikawa, **Periods of generalized Tate curves**, arXiv:1909.10149v4,
1June2020,19pages:
https://arxiv.org/pdf/1909.10149v4

Section2.3, printed4-5: A0 is defined over Z after inverting branch separations,
A_Delta=A0[[y_e]], the gluing matrices and multiplier equation are explicit, and
Proposition2.1 gives integral deformation identities. The generalized stable
curve is universal for the marked degeneration and specializes over complete
local rings. Rendered pages4-5 were inspected, not just an abstract or search
snippet.

Dictionary: y_a,y_b are the marked smoothing parameters, both proportional to
our epsilon=C^7/A^3 with7-unit leading constants. Our branch coordinates and
constants are the exact B60 marked data, copied and hash-pinned. All branch
separations used in this two-node family are7-units. Substitution into the
integral deformation and the inherited multiplicative period product gives
relative error1+epsilonO_F. This last source-to-family assertion is spelled out
in SEVEN_ADIC_PERIODS.md; it is not a general permission to discard arbitrary
principal units at p.

The diagonal/off-diagonal leading constants and marked period product are retained
from B60_DIAGONAL_PERIODS.md and B60_SOURCE_CHECK.md. This source audit newly checks
the integral gluing needed at7. It does not reclassify the entire inherited
period proof as externally or formally verified.

## Additional inspected source, not essential to the new implication

Baker and Rabinoff, arXiv:1308.3864, section4.1, was inspected for the uniformization
and lattice context. The actual valuation identity used here is read directly
from the marked periods, and the necessary functoriality is pinned to
Gregory-Liedtke above. No conclusion relies on an uncited global realization
inference from a graph matrix.

## Evidence and search boundaries

Broad searches for period/monodromy terms initially returned irrelevant pages;
those results were discarded. The exact primary sources above were then opened
and their relevant PDF pages rendered. No licensed/private source was uploaded.
The reference audit is by the same assistant, not an independent mathematical
reviewer. No claim of novelty or literature completeness is made.
