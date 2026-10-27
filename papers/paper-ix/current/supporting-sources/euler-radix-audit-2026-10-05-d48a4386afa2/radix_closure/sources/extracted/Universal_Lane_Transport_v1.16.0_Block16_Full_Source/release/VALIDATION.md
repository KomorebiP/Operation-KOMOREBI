# Release validation record

Date: 2026-08-31  
Release: v1.16.0

## Controlling artifact hashes

| Artifact | SHA-256 |
|---|---|
| Integrated 239-page PDF | `17fb4ac6b42c1ceb7a82e423b24bbcd943ec276f16774b5698302f992308d1c0` |
| Standalone 7-page PDF | `a135f66c7092b2b912d99dad5361770ebeb86abc7b3585c7cd99a0503a4a763b` |
| Finite-profile theorem section | `c1ae8aa2472eda9df467bbbf20b3c861f1261333364af06ffaf1cd455b5ab026` |
| Holonomy-twisted theorem section | `2f4d6deaa95f51b17f4ba107c2b202f28e3b58cca6da516ca3233ed8dd3747ba` |
| Standalone LaTeX source | `3ad51e47467f6e12b585c3a51019b8a121093072fb62ed59ffa16aa021aa5902` |
| Block 16 validation JSON | `ae16bea6a7be9eb54571e880988923e41c27f4f6dff24eacba1a4b1a5141d0d0` |
| Block 16 publication-audit JSON | `8e70c7388c7b114270858111277c3fdfd6d89cf57b65e9b147ef0e9301fff383` |

## Exact implementation regression

### Finite-profile baseline

- Status: `PASS`
- Assertions: `197,099`
- Failures: `0`

### Holonomy-twisted extension

- Seed: `20260831`
- Status: `PASS`
- Assertions: `1,344,823`
- Failures: `0`

| Validation family | Assertions |
|---|---:|
| Group actions and object-orbit descent | 7,780 |
| Pair-orbit partitions and intertwiner bases | 3,537 |
| Orbital path composition and structure constants | 1,212,963 |
| Compatible selectors and negative controls | 994 |
| Equivariant refinement and orbit-projector sums | 10,162 |
| Rational cyclotomic orbit projectors | 109,374 |
| Theorem-source contract | 13 |

## Publication-source audit

- Status: `PASS`
- Checks: `85`
- Failures: `0`
- TeX source graph: `60` files
- Abstract: `346` words
- Labels: `542`
- Cross-references: `138`
- Citation keys: `14`
- Graphics: `57`
- Concordance: `57` entries through `FND-17`

## PDF preflight

| Check | Integrated | Standalone |
|---|---:|---:|
| Opens successfully | yes | yes |
| Encrypted | no | no |
| Pages | 239 | 7 |
| Page size | US Letter, portrait and declared landscape pages | US Letter |
| Extractable text | yes | yes |
| Embedded fonts | yes | yes |
| XFA | absent | absent |
| Structural warnings | none | none |

## Interpretation boundary

The exact suites and audits are internal checks for implementation,
transcription, synchronization, and release integrity. The symbolic proofs do
not depend on finite sampling. Conversely, the computations do not constitute
independent proof review, peer review, or historical-priority validation.
