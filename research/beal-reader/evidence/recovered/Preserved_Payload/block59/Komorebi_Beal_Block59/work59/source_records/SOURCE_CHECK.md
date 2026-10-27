# External source authentication and application audit

Checked during this Block59 execution, 19 September2026 (system research date).
Source PDFs were opened on their publisher/archival hosts through the web tool.
The load-bearing formula pages were rendered and visually inspected, not
accepted from snippets or a failed text search. No local PDF cache or PDF-byte
hash is claimed. No broad novelty classification is made.

## S1. Split nodal curve uniformization

David Mumford, An analytic construction of degenerating curves over complete
local rings, Compositio Mathematica24 (1972),129–174.
https://www.numdam.org/item/CM_1972__24_2_129_0.pdf
Pinned published article identifier CM_1972__24_2_129_0.

Checked Theorem3.3 and the component/node tree dictionary (printedp160,
PDFpage33), and Theorem4.20 plus its preceding fixed-end argument (printedp174,
PDFpage47). The latter page was rendered. The theorem starts with a stable
curve with smooth generic fiber and k-split degenerate special fiber.

Translation: our twisted normalized special fiber is one rational component
with four distinct rational branches paired into two nodes. Its graph is a
bouquet; the two loop generators have fixed ends in the four marked branch
directions. Node thickness affects their multiplier valuation, not the
residue positions. This supplies the adapted Schottky marking over the local
field itself, with no residue extension silently introduced.

## S2. Period product and constant term

Takashi Ichikawa, The universal periods of curves and the Schottky problem,
Compositio Mathematica85 (1993),1–8.
https://www.numdam.org/item/CM_1993__85_1_1_0.pdf
Pinned published article identifier CM_1993__85_1_1_0.

Rendered printedpp3,5,6 (PDFpages4,6,7). Checked §1.2's actual multiplicative
Jacobian period product, Proposition2.4, Corollary2.5, specialization in2.6,
and constant factors in2.7. The author attributes the analytic product to
Manin–Drinfeld. We use this published statement, not a claim to have reread
that separate original source.

Important translation: i!=j, so the identity double coset contributes the
paired fixed-point cross-ratio. Nonidentity factors reduce to1 after positive
multipliers specialize into the maximal ideal; pairwise fixed-point differences
are units. The c_ij on printedp6 is the constant factor, not the normalized
series p_ij/c_ij. The four branch points are kept in their actual node pairs.
A possible orientation inverse has no effect on the7^d-power conclusion.

## S3. Torus periods and the Tate/Kummer extension

Oliver Gregory and Christian Liedtke, p-Adic Tate Conjectures and Abeloid
Varieties, Documenta Mathematica24 (2019),1879–1934.
https://ems.press/content/serial-article-files/26496
Pinned published volume/page edition (received7May2019, revised26September2019).

Rendered printedpp1905–1906 (PDFpages27–28): §4.4, exact sequence(7), and
Lemma4.9(2)–(3). These identify the Tate extension with the period lattice's
Kummer classes. The direct finite-level proof in NODAL_PERIOD.md is also
provided, avoiding any inference from rational Tate modules to a different
integral lattice.

The arXiv HTML uses different section/lemma numbering (§3.4,Lemma3.9 in one
version). This package cites the published §4.4,Lemma4.9 only. For our residue
characteristic q!=7, principal units have uniquely divisible7-primary power
maps. Trivial full natural torsion, not just a split semisimplification, is
what forces all finite-level period classes to vanish.

## Source scope and residual audit risk

These sources establish the classical uniformization and Kummer inputs.
The actual Frey stable model, twist, O-natural-lattice identification and
monodromy content remain inherited project hypotheses, pinned by source
hashes. The new source-to-model dictionary and resulting arithmetic proof
received an adversarial AUTHOR self-review, not external review or Lean
verification. A valid abstract toric representation need not have the actual
marked nodal period.

Broad initial searches returned irrelevant pages, which were discarded.
A secondary discovery source, Morrison–Ren, Algorithms for Mumford curves,
arXiv1309.5243, helped locate the Schottky/period terminology; it is not a
load-bearing additional leaf after the published sources above were checked.
No conclusion follows from search-result counts or source unavailability.
