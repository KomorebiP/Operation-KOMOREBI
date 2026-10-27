# Final visual review: physical pages 101–125

## Artifact and coverage

- PDF: `monograph_v1.9.0/publication/Komorebi_Space_Monograph.pdf`.
- Assigned final-candidate identity: 166 pages, SHA-256 `6459b0c1283c34aa5bf1145897b3308012f7253da34fafc54f7979e4bc58c4ab`. Both immutable receipts, `audit/monograph_v1.9_final_candidate1_render.json` and `audit/final_candidate_01/receipt.json`, record this PDF hash. All 25 inspected PNG SHA-256 values were independently recomputed and match the render receipt. This binds the reviewed images to candidate 1 through its retained render/build evidence.
- Images reviewed: all 25 actual PNGs `tmp/pdfs/monograph_v1.9_final_candidate1/page_101.png` through `page_125.png`.
- Method: each page was opened through `view_image` at its full original 857 × 1109 pixel resolution, in five batches of four followed by one batch of five. No contact sheet or extracted text substituted for the page images.
- Physical page numbers in this report are PDF positions. The corresponding printed folios are 96–120, five lower.
- This review was read-only. No source, figure, PDF or formal file was edited; no Lean run was performed.

## Verdict

**PASS for the entire assigned 25-page visual range.** No concrete outstanding visual issue was found. Mathematical text, subscripts, superscripts, fractions, matrix entries, arrows and equation numbers are legible. No clipping, text/figure/table collision, unresolved rendered reference marker, literal LaTeX leakage, malformed glyph, or orphan heading was observed. The dense proof pages retain adequate bottom margins.

The earlier Figure 28 legend issue is resolved on physical page 109: the blue ellipse is now labeled **“Reachable images at the fixed budget.”** This agrees with the plotted \(T(B_M)\), the point \(Ta\), and the caption. The arrow from \(Ta\) to \(r\), labeled \(v\), remains correctly visible. The axis wording identifies coordinates in the residual/target space and creates no set-label contradiction after this correction.

The coordinate convention visible in §29.2 on physical page 112 explicitly chooses orthonormal ambient and residual coordinates before introducing a possibly nonorthonormal correction basis \(B\). The formulas \(S=dB\), \(G=B^{\mathsf T}B\), and \((S^{\mathsf T}S+\alpha G)c=S^{\mathsf T}r\) are readable and their transpose notation is consistent within that stated convention. Later coordinate material beyond physical page 125 is outside this assignment.

WR14's revised statement on physical page 125 explicitly sets **both** optimizers: \(a=a_\alpha\) and \(z=z_\alpha=r-Ta_\alpha\). The proof likewise sets both values before obtaining equality. The distinction between an arbitrary proposed pair and the optimizing pair is clear in the rendered theorem and proof. This is a visual/prose correspondence check, not a new full mathematical audit or a claim of new formal verification.

## Every-page inspection record

| Physical page | Printed folio | Content checked | Visual outcome |
|---:|---:|---|---|
| 101 | 96 | Chapter 27 opening, evidence box, correction-space definition and weak-subsequence lemma | Pass. Box, restriction/adjoint notation and lemma layout clean. |
| 102 | 97 | Weak-subsequence proof and bounded-feasibility theorem | Pass. Bessel sums, limit indices and pairing displays legible. |
| 103 | 98 | WR01 conclusion, evidence line and nonconvergent sequence example | Pass. No reference or mathematical typography defect; chapter-ending white space acceptable. |
| 104 | 99 | Figure 27, minimum-energy theorem and first proof display | Pass. Legend/caption readable; theorem and tag (27.1) separated; bottom display fits. |
| 105 | 100 | WR02 proof, diagonal example and conclusion box | Pass. Energy identities, sums and box content unclipped. |
| 106 | 101 | Chapter 28 budget profile, attainment theorem and convexity/Lipschitz proof | Pass. Infimum index, closure, limits and inequalities clear. |
| 107 | 102 | WR03 conclusion and dual-budget theorem/proof opening | Pass. Tags (28.1)–(28.2), maximization domain and lower display properly placed. |
| 108 | 103 | WR04 proof conclusion and two-dimensional matrix example | Pass. Matrix, rational expressions and square roots clear. |
| 109 | 104 | Figure 28 and robustness theorem | Pass. Prior legend issue corrected; supporting line, arrow and point annotations legible; caption clear. |
| 110 | 105 | WR05 proof conclusion and Figure 29 uncertainty band | Pass. Legend, uncertainty band and parameter caption fit. |
| 111 | 106 | Chapter 29 normal equation, inverse proof and optimizer construction | Pass. Adjoint, inverse and norm notation legible; tag (29.1) well placed. |
| 112 | 107 | Energy identity, coordinate-basis convention and parameter monotonicity theorem | Pass. Orthonormal-coordinate convention visible; Gram-matrix formulas and tag (29.2) clear. |
| 113 | 108 | WR07 proof and regularization-limit theorem | Pass. Parameter subscripts, witness identities and limit arrows clear; heading has content. |
| 114 | 109 | WR08 five-step proof and evidence line | Pass. Dense proof and large norm expressions fit without collisions. |
| 115 | 110 | Four-case table, Figure 30 and data-sensitivity theorem opening | Pass. Table columns and rows separate; plot maxima/legend/caption readable. |
| 116 | 111 | Sensitivity proof, convergence estimate, WR09 evidence line and box | Pass. Parameter-dependent norm bounds and boxed prose fit. |
| 117 | 112 | Chapter 30 diagonal family and tail estimates | Pass. Long sums, integral bounds and tags (30.1)–(30.2) remain separated. |
| 118 | 113 | WR10 proof conclusion, Figure 31 and §30.2 introduction | Pass. Coordinate curves, markers and caption clear; heading has two following prose lines. |
| 119 | 114 | Sharp asymptotic theorem and Riemann-sum proof | Pass. Floor notation, large delimiters, integral limits and tag (30.3) legible. |
| 120 | 115 | WR11 proof conclusion and Figure 32 certified intervals | Pass. Error bars, legend and asymptote labels readable; caption unclipped. |
| 121 | 116 | Attainable datum, noisy-repair corollary and machine-certification introduction | Pass. Ceiling, parameter exponents and noise bounds clear; both headings have content. |
| 122 | 117 | Chapter 31 introduction, formal-status box and three residual definitions | Pass. Box fits; \(v\), \(g\), \(e\) and restricted-adjoint formula clear. |
| 123 | 118 | WR13 normal-residual estimates, proof and sharpness examples | Pass. Tags (31.1)–(31.4) do not intrude; square-completion alignment and bounds readable. |
| 124 | 119 | Figure 33; vanishing-residual example; dual objective and WR14 identity | Pass. Logarithmic chart and caption legible; example explicitly has \(n\ge1\); dual formula and tag (31.5) fit. |
| 125 | 120 | WR14 two-optimizer statement, gap proof and conclusion | Pass. Both optimizer assignments visible; tag (31.6), multiline formulas and evidence line clear. |

## Scope limit

This report replaces neither the other reviewers' page ranges nor the PDF font/geometry preflight. Its PASS applies to these 25 inspected final-candidate images, linked by the verified immutable render/build receipts to the assigned candidate PDF hash. The mutable publication PDF path was already being rebuilt as candidate 2 during this inspection (observed SHA-256 `04eb0e06db94b49e6c22b097e44f2c0aabdef686f78eed92f3a19c8ae7be7e29`); that expected later build is separate. This reviewer does not claim direct access to a retained candidate 1 PDF, and the PASS must not be silently transferred to a later PDF. Earlier draft findings remain documented in `VISUAL_PAGES_097_120.md`; the Figure 28 finding from that draft is closed by the present render.

## Inspected-image SHA-256 manifest

```json
{
  "page_101.png": "f22e4d37fc035fcfa1ad5f8a0ca7d19fb781a754c6189606524f63691f42a11d",
  "page_102.png": "dbe2560d60026d61f3ca7f089373a1991e57fda36b6cbbc847463afbe1acd1f2",
  "page_103.png": "fdfa0bc7fef0efa3566cb07fe5e30150730a20bdda34d27c2c540367569c651f",
  "page_104.png": "cce81e16b8da06fc427509d4a2c7471c0d8ed1c370a4a18068f5fdf8f560e166",
  "page_105.png": "fb8a9687a6ad0a0a0e08700fc392f4f0f70f0e5b9ec75bc183a7c9de3711ea6d",
  "page_106.png": "31f330e272de1b0a085d9bd6ab41b58ac5b5b4c9f59ba0692645bd2aa21e5451",
  "page_107.png": "f45979ec38e75dffdc0e29f62103e4c1e32997cee819cc66f1a1111704f6cba9",
  "page_108.png": "a7ce34545bcbd8e2f20897b301ec94d3dcf518e790ed8e619fa34c86956d66fc",
  "page_109.png": "da7abdfa66e7db8269506614a0335a0860aa8b42cc09388bd6b2d2c01aaa9c4a",
  "page_110.png": "2b0e7474d6f932856dc275b7290344843fc317be67394cca69ee91b399ddc30c",
  "page_111.png": "209d8e8654734e7b17e4a898d1d6762bd07bf2a29796034b759b56ddae6badc9",
  "page_112.png": "24edea93c5ac45e417dea8a6922a2209c3c31c88dad3aa1425691e9435b9c599",
  "page_113.png": "306b0f96b499b3c155fcfb66502f33371dfbb2eefe18729f0e1b5c5da9252d34",
  "page_114.png": "32740d682a0ad3f2be98b8eb36af60ad58e1e9ca8741f18a0d6b70b0f33dd415",
  "page_115.png": "f831f153aba38b2324d1ef6859c16ffc78ea7e280b9fb023628a8231c968f7ea",
  "page_116.png": "635b868cbfc6cd01b1971aab77b9efc89c0b8c7ab495353f75cc14b172394c2b",
  "page_117.png": "f333d254a13fbb9a77539b6c29fe4147c887bedee1904ff531aacde23ee47b63",
  "page_118.png": "98db4c120d52a0d154edcef5fe4414c7f7af216d5b9c82f359d74049bceafd87",
  "page_119.png": "e752aa7feafcdde344bc296bd7d6e4b48cd0256ddd2854fc62a77d1d38326375",
  "page_120.png": "fbc8ded7dc335a327a025331eebe61e35be7841e4f07e0e092c9094317066a30",
  "page_121.png": "16ec4791e145462949f9f333326d66c24dad584cf67e4bc148627abb333282fe",
  "page_122.png": "f1eb5e0d6844439ec28fde0258d7243a88c48a254d06d9305f67ef4363cdffd2",
  "page_123.png": "5c99d643bb6c095fa4038f96b9a09d053c204a77f1c8ff58f032a18c263f2665",
  "page_124.png": "4279eb0972af98b2d44b85245085fe3097ff35a9ee016b5dd8fa2e3b0a63ef34",
  "page_125.png": "47112fc83920ce6697a46204a58a450938556f7b7d8f40383a40da468f9fa410"
}
```
