# Foundations 0.8.0 — release audit

**Komorebi Large Signal Model · Komorebi P. · 9 October 2026**

## Scope and documents

The cumulative volume has 118 pages and 87 propositions with written proofs. The new block has 15 pages and Propositions 80–87. The visual notes have eight pages and six new separate figure sets in PDF, PNG and SVG. Markdown, generated LaTeX, code and calculation records accompany the documents.

Production PR-LASM remains 2.3.0. No Lean proof kernel, real-signal training, GPU execution, remote CI, public publication or license change was performed. The unchanged 0.7.0 archive is included. Its SHA-256 and all 79 inherited proposition/proof spans were checked. That check establishes preservation, not a fresh independent proof audit of every inherited statement.

## Reduced repair

The earlier perturbed operator family and proposed geometry are unchanged. Reset weight 1/32 passes an exact margin-1/64 check. The same declared degree-two coefficient box of radius 1/4096, with exact integrated mass, is retained. The general mass and spatial budgets are still 1/128 each. Their sum equals the margin; the larger output-error family is certified with nonnegative, not strictly positive remaining margin.

The main witness has eight polynomial inequalities, 194 leaves and 3,058 recomputed coefficients. The separate comparison-domain witness has 185 leaves and 2,833 coefficients. A rational separating functional gives a lower repair bound 864543451/37599646576, while 1/32 is a certified upper bound for this fixed geometry, reset path and required margin. No global minimum is claimed.

The retained comparison budget is 87471/1280000 in integrated instrument error and min(1,87471 T/2560000) in full-record total variation. It is nontrivial through horizon 29 and trivial from 30. The uncertainty tube does not claim statistical coverage of the unmodified process.

## Dependent observations and confidence

A separate generator creates one rational five-node Markov path with 262,144 transitions and seed 20261009. The reference measure has weights (7/90,16/45,2/15,16/45,7/90) at (-1,-1/2,0,1/2,1). It is not rounded continuous data. Its first four moments match the continuous uniform reference, but the two measures have total-variation distance one.

The learner receives observations and the fixed protocol, not the generator's true parameters. It assumes an accessible state (1,u,u^2), a supplied two-parameter conditional family and prior parameter bounds. Self-normalized confidence is proved under a predictable conditional-mean model with bounded responses. The new general moment-operator theorem is proved but only its scalar specialization is implemented here.

The final confidence rectangle is a in [89/250,231/500], b in [29/250,29/100]. All its members have density floor 31/125 on the declared curved moment domain. The fitted center is (409/1000,203/1000). No reset correction is applied. The first passing recorded checkpoint is 32,768 transitions; no minimum sample-size or first-individual-step claim is made.

The conditional confidence level is 19/20, simultaneous over time, under the stated model and observation assumptions. It is not an empirical coverage estimate from one seeded run. The exact replay verifies the data fingerprint, sufficient statistics, rational radius enclosures, outward rounding, model identity and whole-rectangle certificate. It does not authenticate observations or establish physical model correctness.

The uniform next-observation discrepancy is at most 2437/90000. Full future records obey min(1,2437 T/90000), trivial from horizon 37. Markov minorization separately gives an all-time single-marginal upper bound 2437/22320. That marginal bound is not substituted for a full-record bound or an arbitrary history-dependent-policy bound.

## Executed reference calculations

The local complete replay ran eight suites and sixteen example/generator programs, 24 scripts in total. Its checkpoint report records script hashes, actual return codes, stdout, stderr and durations. Every script passed.

| Suite | Records |
|---|---:|
| Original foundations | 58 |
| Learning and stability | 86 |
| Controlled stochastic realization | 113 |
| Certified probability domains | 145 |
| Curved domains and continuous observations | 117 |
| Discovery, approximation and evidence | 82 |
| Robust curved certificates | 62 |
| Data-supported domains and smaller repairs | 93 |
| **Total** | **756** |

The new suite has 74 exact records, 16 expected-rejection controls and three seeded-path diagnostics. Cumulatively there are 703 exact rational/symbolic records including rejection controls, 41 numerical records, six seeded-sampling records and six seeded-path diagnostic records. These are finite check records, not general proof-kernel verifications or historical-novelty claims.

The new controls reject incorrect measures, narrowed confidence intervals, altered input records and unsupported coverage claims, alongside certificate and positivity boundary checks. Exact finite marginal comparisons are illustrative checks of the proved inequality, not a substitute for its all-time proof.

The final delivered archive is verified and replayed from a pristine extraction in the separate accompanying extraction report. Hash checking precedes replay because regenerating reports intentionally mutates the working copy. This audit does not embed a self-referential archive hash.

## Documents and visual review

Every current PDF has zero overfull/underfull boxes and zero undefined-reference or duplicate-destination messages. Structural checks find no replacement glyphs or text outside page bounds. All listed fonts are embedded. No standalone font files are distributed.

All cumulative, new-block and visual pages were rendered in MuPDF. All contact sheets were inspected, with full-size review of the new theorem and curved-domain pages. Six new figures use separate Matplotlib plots and an explicit source-data ledger. Confidence intervals are from the exact saved path; prediction curves are certified upper bounds, not empirical accuracy claims.

## Failed attempts and repairs

An early exact-check run failed because SymPy compared two equivalent matrix expressions structurally before expansion. The assertion was corrected to check the expanded zero difference. The identity and test were retained; the final 93-record suite passes.

An exploratory repair weight 1/64 failed a requested positive-margin check. It was not reported as certified. The final text separately proves that 1/64 is insufficient for the final required margin 1/64 using an exact separating functional. This does not by itself prove that the nominal 1/64-repaired model is probability-invalid.

The first new-block PDF build reported a 3.31165-point overfull box in a long theorem heading. Splitting the heading and following definition into paragraphs removed it. The initial visual-guide build stretched figures and separated captions over 14 pages because the generated size specification lacked aspect-ratio preservation. Explicit bounded-width/height includes with keepaspectratio repaired the layout. The final visual guide has eight pages and was rerendered. The theory and numeric values did not change in these layout repairs.

During final proof review the positive-noise-scale hypothesis sigma > 0 was made explicit in Proposition 81's setup, matching the proof's divisions by sigma. Both mathematical PDFs were rebuilt and rechecked. No inherited proposition/proof span was altered.

## Reproducibility and boundaries

The local environment is Linux, Python 3.13.5, with exact package versions in requirements-tested.txt. The PowerShell wrapper was supplied but not executed on Windows. Document regeneration also needs Pandoc and XeLaTeX. No internet is required for the reference replay with installed dependencies.

The next release task is a dependency/assumptions audit of the declared finite foundations. General nonlinear dictionary discovery, unknown hidden-state identification, empirical sensor uncertainty and informative arbitrary-length record guarantees remain distinct research directions rather than silent claims of this release.
