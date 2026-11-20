# Bounded source check

Author: Komorebi P.
Checked: 20 November 2026.
Question: distinguish the known banded-determinant transfer mechanism from
the specific finite-difference reduction of this differential Hankel family.
This is not a historical-priority audit.

## Authenticated primary version

Max A. Alekseyev and Dmitry I. Khomovsky,
*Constructive recurrences for determinants and permanents of banded Toeplitz
matrices*, arXiv:2609.13674v1, 12 September 2026.

Exact primary text:
https://arxiv.org/html/2609.13674v1

Authentication: arXiv abstract and submission history agree with the versioned
full HTML. Extraction: Sections 1 and 6.1--6.2 were read. The paper gives the
binomial state count for fixed-band Toeplitz determinants; Section 6.2 explicitly
identifies finite-defect recurrence existence as already known. Application:
our stationary band has semibandwidths 4M, hence the same binomial scale.
Our note supplies its own signed matching proof, including the finite initial
boundary, so no defect-state theorem is imported from the source.

Overlap label for the general transfer mechanism: **known after translation
of notation**. Implication verdict: **verified** for the comparison with the
constant-band setting. No claim that our application or its rank/kernel
refinements is historically new has been established.

No full source was retained locally; there is no retained-source byte hash.
The versioned primary URL above is the source locator.

## Additional discovery lead, not a verified implication

Christian Krattenthaler, *Hankel determinants of linear combinations of moments
of orthogonal polynomials, II*, arXiv:2101.04225v5, 10 September 2021:
https://arxiv.org/abs/2101.04225v5

Only abstract metadata and scope were authenticated in this pass. Its exact
coverage of derivative-perturbed, polynomially weighted moments was not
extracted. Implication verdict: **unverified**; overlap label: **partial or
adjacent result only**. It is not used as a proof dependency here.

## Search scope

Two same-searcher primary-source queries used the phrases “banded Toeplitz
determinants rational generating function recurrence transfer matrix” and
“Hankel determinants polynomial central binomial coefficients differential
operators recurrence”, restricted in discovery to arXiv. No comprehensive
backward/forward citation audit or second independent search was performed.
