# Review coverage, corrections and remaining obligations

**Komorebi P. · Same-author review · 13 November 2026**

This review covers the published chemistry overview, all seven original
linked notes, their proof and computation dependencies, and the expanded
reading edition. It separates correctness, boundary cases, exposition,
notation and claim scope from mechanical proofreading and web accessibility.
It is a sequential self-review, not an independent expert report or
proof-assistant verification.

## Main mathematical assessment

The 21-parameter normal-form theorem, the exact three-query count and the
stated sufficient recovery/response bounds survive this review under their
declared real nine-state assumptions. The positivity discussion required
one clarification: failure of an all-compatible sufficient margin does not
make existence undecidable when the estimate itself is already positive
semidefinite.

For instance, $Y=0$ and $\epsilon>0$ produce a compatible positive estimate
$\widehat C=0$ although that sufficient margin fails. The code already
returns the correct feasibility answer. The
[revised recovery note](three-queries.md#positivity-existence-and-an-all-compatible-guarantee)
now distinguishes existence, uniqueness and an all-compatible guarantee.
Cases where $\widehat C$ is not positive semidefinite also include negative
definite matrices; the word “indefinite” alone was too narrow for a complete
description.

No counterexample to the central recovery theorem was found. That statement
records this review's outcome; it is not an independent certification of
every research claim or of physical molecular accuracy.

## Explanatory and notation gaps filled

- The normal-form note now gives the determinant order, hole/electron signs,
  all five basis matrices, the full integral-to-coefficient dictionary and
  direct coefficient extraction by Choi compression and partial trace.
- The recovery note now supplies the least-squares Pythagorean identity,
  raw/unit probe conventions, zero-noise and singleton cases, positivity
  case distinctions and the complete resolvent/source argument.
- The response, broadened source-resolved density, pi-scaled density,
  complex disk and real interval are defined separately. Units and the
  role of positive broadening are explicit.
- The molecular note identifies the hydrogen-chain geometry, basis,
  active-orbital relabeling, energy coordinate and source. It separates
  projection identity, rounding error and unmeasured physical error.
- The full-model bridge proves a conditional bound combining numerical,
  block-mismatch, coupling, source and energy-reference errors. It identifies
  missing caps rather than assigning them unverified values.
- The code's action Gram field `K` is distinguished from the one-body
  normal-form matrix $K$. The reading uses $B$ for the former. Vectorization,
  integral pair order, norms and coefficient conventions are spelled out.

These additions include mathematical explanations and a new conditional
argument. They are not all categorized as punctuation corrections. The
original sealed files remain unchanged; the reading edition and its
source correspondence identify the changes.

## Computation and replay coverage

The original audit passed again with **82 named checks and 260 aggregated
cases**. It includes all 27 integral generators, an independent full-Fock
Jordan–Wigner construction, all 21 normal directions, gauge identities,
exact rank/frame certificates and decoder boundary cases.

The added audit passed **62 named checks and 174 aggregated cases**:
27 complete integral-to-normal dictionaries; 21 direct coefficient
extractions; positivity, parser and outward-root boundaries; 108 exact
discarded-space coupling cases; and an exact ten-state joint-error example.
The finite examples check implementations of the written arguments. They
do not prove the conditional statement for all Hamiltonians by sampling.

The molecular replay again verifies the direct projection, integral
positivity, all measured action error and exact rational response inclusion.
The original fixture container and selected-array view have distinct
hashes. The fresh public records bind the actual view used by the replay.

The validated bundle includes three completed v2 manifests with input and
output hashes, logs, contracts and a standard-library verifier. This fills
the earlier public export's provenance gap: that export intentionally
omitted the original machine-specific runtime manifests. Those original
identifiers remain historical; the new records are fresh executions.

## Language and accessibility coverage

The reading edition corrects compressed numerical spacing, punctuation,
grammar, paragraph transitions, acronym introductions and ambiguous
references. Equations are integrated with their surrounding sentences;
source filenames and implementation fields are distinguished from prose.

The overview and all reading notes are checked for heading structure,
local links, table captions/headers, keyboard disclosures, focus and
scroll behavior, responsive layout, enlarged text, reduced motion,
MathJax completion, script errors and download identity. Source and
provenance details remain available without placing long hashes in the
main reading flow. The probe matrix has a direct text-table alternative.

The [website verification report](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/verification/chemistry-reading-review/validation.json)
states the executed browser matrix and
its results. These checks do not constitute a complete WCAG conformance
audit or testing with every browser, screen reader, magnifier or input
device. The [accessibility reporting route](https://KomorebiP.github.io/Operation-KOMOREBI/collection/ACCESSIBILITY.html)
remains available for barriers not captured by those checks.

The [structured review and reconciliation](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/verification/chemistry-reading-review/report.md)
preserve the source identities, five sequential review lanes, findings,
corrections and limits of this self-review.

## Open obligations

| Obligation | What remains necessary |
|---|---|
| Actual Coulomb realizability | Characterize the additional constraints beyond the positive-Gram relaxation. |
| Original full-H10 response | Bound discarded-space coupling, block-model mismatch and the physical source/reference errors for one consistently defined target. |
| Broadening limit | Supply additional spectral information before claiming a uniform zero-broadening result. |
| Positive-subclass feasibility | Solve and certify the cone-constrained problem when the decoder's exact tests return `null`. |
| Larger sectors | Recompute the operator family, gauges and query obstruction; the nine-state argument does not transfer unchanged. |
| Optimal conditioning | Prove sharp frame constants or a global design optimum; the current constants are sufficient bounds. |
| Runtime advantage | Compare complete costs with a certified observable-specific method on the same input and tolerances. |
| Priority and significance | Extend the primary-source search and obtain independent expert assessment before a novelty claim. |

The [conditional bridge](model-error.md) makes several of these obligations
quantitative, but their numerical values for the original target remain
unestablished. The [source record](literature.md) gives the exact limits of
the prior-art comparison. Reviewing every published note is different
from completing every open problem in computational chemistry.
