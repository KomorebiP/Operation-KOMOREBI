# Operation Komorebi · Lehmer · Conjecture Series 07

Author: Komorebi P.  
Reader edition: 1.0, 9 October 2026

This package accompanies the monograph and visual guide on **Lehmer's conjecture for Ramanujan's tau function**. The target is `tau(n) != 0` for every positive integer. The general target remains open in this work.

## Readers

- `output/pdf/Komorebi_Lehmer_Conjecture_Piece_v1.0.pdf`
- `output/pdf/Komorebi_Lehmer_Visual_Guide_v1.0.pdf`

The monograph develops the defining series, exact coefficient engines, five-core packet identity, universal null corrections, dyadic refinement, primitive content extraction, local recurrence theorems and the remaining global prime obligation. The guide supplies a separate visual route through the same mathematics.

## Source and evidence map

| Path | Role |
|---|---|
| `paper/` | Monograph LaTeX source |
| `visual/` | Guide LaTeX and scientific figure generator |
| `shared/` | Typography and figure assets |
| `historical/` | Six recovered source ZIPs and unchanged extracted content |
| `evidence/historical_inputs.json` | SHA-256 identities of the six recovered inputs |
| `evidence/computation/` | Fresh exact replay outputs, domains and provenance |
| `evidence/proof_audit/` | Reconstruction of the raw mathematical claims |
| `evidence/formal/` | Definition audit and proof-assistant source inventory |
| `evidence/literature/` | Checked external theorem contracts and primary-source locators |
| `evidence/BUILD_ENVIRONMENT.json` | Tested runtime and dependency versions |
| `evidence/FULL_LAYOUT_VALIDATION.json` | Hash-bound page review coverage |
| `evidence/FONT_VALIDATION.json` | Font embedding and text-map checks |
| `evidence/SOURCE_VALIDATION.json` | Final reader and build checks |
| `MANIFEST.json` | Every archived file's size and SHA-256 digest |

The historical files preserve contemporaneous statements and evidence labels. The current reviews determine what this edition claims. Original reports of bounded computations are not substituted for fresh replay. A finite computation can validate an explicit certificate or a stated range. It cannot establish all-prime tau nonvanishing.

## Rebuild

Use Python 3 with the dependencies recorded in `evidence/BUILD_ENVIRONMENT.json`, a standard TeX Live installation with pdfLaTeX, and Poppler for page rendering.

```bash
python3 code/run_replays.py --output-root evidence/computation/reproduced
python3 build.py --figures
python3 quality_check.py
python3 validate_fonts.py
```

The replay runner is the computational entry point. Its output directory must be fresh. The build writes the two readers to `output/pdf/`. The layout checker renders immutable snapshots to a temporary directory outside the source package. Automated layout checks do not replace human inspection. `validate_release.py` requires a matching completed page-review record before approving the final readers. `package.py` creates the source/evidence ZIP and verifies every member against its manifest.

## Mathematical boundary

The primitive residual satisfies `R(p)=tau(p)`. Its all-square nonvanishing theorem and equality of its zero set with tau's zero set leave the prime obligation intact. Fixed-modulus Chebotarev witnesses do not select one prime satisfying every modulus. Trace-zero local models do not identify the actual global Delta representation. Synthetic recurrence sequences are tests of weaker hypotheses and are not claimed to be actual zeros of tau.

The recovered packages contain written mathematical arguments and exact computation. No recovered Lehmer proof-assistant project or compiled Lehmer certificate is claimed.
