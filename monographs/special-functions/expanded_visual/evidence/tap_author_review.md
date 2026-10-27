# Tap atlas author review

Scope: exactly 16 new lessons T01--T16, `chapters_taps.tex`, `figures_taps.py`, and their 16 Python/Matplotlib PDF/PNG figure pairs. The review is confined to the newly authored tap material.

Status: PASS, with no unresolved objective mathematical, caption, or figure-layout issue.

## Conventions and authenticated project source

Every sequence is causal and is zero at negative integer indices. The fine OGF delay is `z`; the coarse OGF delay is `u`. Polyphase matrix rows are output phases and columns are input phases. Haar uses adjacent nonoverlapping pairs `(x[2m], x[2m+1])`. The rational resampling example includes the full finite convolution tail. The direct-form streaming example retains the previous `L-1` inputs and flushes `L-1` zeros explicitly.

Read the current project-local extraction `source_context/PSC_V_convolution_extract.txt`, provided by the root agent from `PSC_Paper_V_Annals_Human_Edition.pdf` on 7 October 2026. Theorem 4.2 supplies exact convolution routing, Proposition 4.4 supplies composition, Corollary 4.5 supplies FIR closure, and Example 4.6 supplies the four-phase five-tap matrix. The source uses bilateral `z^{-m}`; this atlas specializes to causal finite filters and uses `u^m` for coarse delays. The reduction is valid because negative coarse offsets have negative fine offsets for residues 0,...,M-1 and therefore vanish for these causal taps.

## Computation

The generator ran successfully with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`. All 15 explicit assertions passed, including 45 signed-filter routing cases, 20 chunk-streaming cases, 121 Haar integer pairs, and 16 rational-coefficient lifting filter pairs. Exact checks use Python integers and `Fraction`; only the frequency illustrations use float64/complex128. The recorded frequency magnitude residual is 1.3322676295501878e-15 on the 801-point plotted grid.

The record `evidence/tap_checks.json` passes the computation-audit manifest validator with `--root`. It is a legacy schema version 1 record. It additionally records execution-input hashes, but has no git revision or machine-checkable resource limits. Those provenance limits are explicitly stated, and its finite output is not presented as a universal proof. The structural routing identity is independently derived by equating fine indices and is authenticated by the source theorem.

- Fibonacci direct convolution first 12: PASS.
- Two-phase matrix coefficients: PASS.
- Four-phase five-tap matrix: PASS.
- Tap composition exact convolution and matrix multiplication: PASS.
- Finite differences of squared integers: PASS.
- Fibonacci annihilator including causal initial residual: PASS.
- Even and odd Fibonacci recurrence residuals: PASS.
- Finite numerator taps acting on infinite reciprocal prefix: PASS.
- Frequency illustration compared with closed magnitude: PASS.
- Symmetric three-tap phase illustration off the zero: PASS.
- Haar sum/difference exact perfect reconstruction: PASS.
- Signed finite predict/update exact invertibility: PASS.
- Rational resampling 3/2 exact routing: PASS.
- Exact chunk streaming and tail flush: PASS.
- General causal FIR phase-routing formula bounded exact tests: PASS.

## Corrections during authoring

- An initial Matplotlib label used `\mathsf T` without braces and failed while saving T13. The label was corrected to `\mathsf{T}` and the complete 16-figure generation reran successfully.
- T04 initially mixed indexed coefficient nodes with polynomial-delay labels. The indexed nodes already carried the shifts, so arrows were corrected to the actual weights `1,2,1` in both panels. This removes a visual double counting of delay. The chapter formulas were already correct.
- T06 initially rendered a comma between the two matrix factors. It was replaced with an explicit multiplication dot; the independently checked matrix-product identity did not change.
- Rounded-box padding in T03 and T13 was clipped by the diagram limits. The common diagram bounds now include that padding.
- T15's horizontal axis was clarified to fine index `n`, with the kept locations `n=2m` stated alongside it.

The independent sequence/polyphase reviewer confirmed the chapter mathematics and noted the two corrected diagram-label issues. The author visually inspected all final figures in four 2-by-2 contact sheets, checking labels, signs, arrows, value annotations, axes, and clipping. The contact images are reproducible temporary QA artifacts, not generated illustrative imagery.

## Figure coverage

| Plate | Author visual review | Final PNG SHA256 |
|---|---|---|
| T01 | PASS | `102aaa6151e3fa3c589f6152b13ecc8e27076a7fdf068de1bc5e06428a7ef91c` |
| T02 | PASS | `1f9469e2a291fc74d80fa87e4027517759a5132d1ea4eb58cfe32ce9cc7aad16` |
| T03 | PASS | `4eae02ff9d72d216de6aba8bed833dbf03dbd55b9c2f307b260c3a93100cadd4` |
| T04 | PASS | `9e83fcf6d58bf17cce68654ab0455d0808b4a8c5961f8284bc9e4d22cbb0637f` |
| T05 | PASS | `287e4d3ffafd8123f5c06c106427fa3c5d9b6b7192133afb95b44265c6192dac` |
| T06 | PASS | `1c785eb2a0b8464f5b78dab76973885d8f889598634c2958c59017d84c646466` |
| T07 | PASS | `5903e10e93830f9a9b5ddbf80191b78936eb452550c5326e2ef13db21b304277` |
| T08 | PASS | `6ba06c03ac2e4dbbc9a00dc741857edaead798efdec28cf8d3f9d00c17d02289` |
| T09 | PASS | `d26c141d81210ac6434bab413eebaee0620e210654e51e8a0dfc0da16c4108de` |
| T10 | PASS | `aec63515c1811e45249f1bb78a2647a487c9feba7a9bf0f918241f668126913d` |
| T11 | PASS | `92652d060d893f87b1cce20f2351db3569b8448d106c42c34bce92de423425ed` |
| T12 | PASS | `42a9ba8b5b0de87b2abfcf141f5d02d03e276afe7dd57aaa6ec92ed9642d14b9` |
| T13 | PASS | `1a94e98980c125a43ea7f7edc73c814054dd4fa124464e42f9baa1c53e18141c` |
| T14 | PASS | `a491d5e09d6a08bdfe4f18725702fff4a6f1bfe12d956f5dcea4484225b2bc1d` |
| T15 | PASS | `1513552bf9b16a02fc8688ced079445c76c1ca22564bb17305c7a92355fb1eb0` |
| T16 | PASS | `561d9d15ab2648e668061d6103e6cd9b6566cc01a6d96778356a00f55d9576c8` |

## LaTeX and conservative proofreading

A standalone wrapper using the project's actual eight-argument `\lesson` macro compiled all 16 tap lessons into exactly 16 pages. It produced no overfull boxes, underfull boxes, or undefined commands/references. The final whole-guide review remains the root agent's integration check.

Proofread: all 16 new titles, displays, four explanatory fields, and source/scope notes in `chapters_taps.tex`.

- Routine edits: a long display was broken at a natural equality/definition boundary; source attribution for composition was made precise (Proposition 4.4); one sentence was clarified.
- Mathematical-token changes to an existing source proof: none. The two corrected diagram labels above are new authoring corrections, recorded explicitly.
- Unresolved issues: none.
- Validation: generator PASS; computation manifest valid; standalone TeX compilation 16 pages with zero reported layout diagnostics.

## Interpretation limits

The chosen resampling filter demonstrates exact routing and is not assigned passband, stopband, or alias-suppression performance. The reciprocal response `H=1/(1-3u+u^2)` is infinite, while its numerator and denominator tap lists are finite. Recurrence residuals retain causal initial impulses. No finite constant-coefficient annihilator is claimed for every OEIS sequence. The Haar normalization is factored symbolically in the exact finite witnesses. Zero frequency-response endpoints have undefined phase and are excluded from phase residuals. The `L-1` saved-input rule describes the direct-form implementation used here, not a universal minimal realization bound.
