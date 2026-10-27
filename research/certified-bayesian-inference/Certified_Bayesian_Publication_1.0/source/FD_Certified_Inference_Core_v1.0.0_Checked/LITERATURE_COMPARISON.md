# Bounded literature comparison

Author: Komorebi P. Checked 2026-09-12. This is an attribution and overlap review,
not a claim that no matching result exists elsewhere. No external paper is a new
unproved dependency of the Lean development. Mathematical source interpretation
and software proof checking are separate evidence streams.

## Scope and method

Two discovery passes used public web search with English terminology for greedy
coordinate/block descent, cached residuals, approximate Gauss–Southwell selection,
Gaussian pathwise conditioning, iterative posterior solvers, Wasserstein error,
and formally checked rounded-arithmetic certificates. The strongest candidates
were read in primary author/publisher PDFs. Search queries included:

- Nutini Schmidt Laradji Friedlander Koepke 2015 Gauss Southwell coordinate descent arxiv
- Wilson Borovitskiy Terenin Mostowska Deisenroth pathwise conditioning Gaussian processes 2021
- Daumas Melquiond certification bounds expressions Gappa Coq 2010
- site.arxiv.org Gaussian process posterior conjugate gradients Wasserstein error residual iterative pathwise sampling
- site.arxiv.org Lean verified Gaussian conditioning posterior Wasserstein certificate
- Nutini Laradji Schmidt block coordinate descent go fast 2017 greedy selection

The initial Wilson author query contained a spelling error; the primary article
identifies Peter Mostowsky. The block-descent search followed the scalar-descent
source into the block setting. Gaussian searches followed the pathwise/iterative
connection into later kernel solvers. This did not constitute an exhaustive
forward-citation survey or a search of every proof-assistant repository. The same
reviewer performed both passes. PDFs were inspected through the web reader and
not redistributed; URLs and publication/version identifiers are recorded below.
No PDF-content hash is claimed. Public web search and publisher/arXiv retrieval
were available; specialist paid-index coverage was not used.

## 1. Greedy selection and cached gradients

Julie Nutini, Mark Schmidt, Issam H. Laradji, Michael Friedlander, Hoyt Koepke,
“Coordinate Descent Converges Faster with the Gauss-Southwell Rule Than Random
Selection,” ICML 2015, PMLR 37, pp. 1632–1641.
Primary published PDF: https://proceedings.mlr.press/v37/nutini15.pdf

The paper analyzes largest-coordinate-gradient selection. Its early discussion
explains maintaining gradients/residual quantities and max-heaps to reduce
selection cost on sparse problems. Section 7 treats multiplicative and additive
errors in approximate selection. Thus greedy choice, cached gradient maintenance,
and controlled approximate greedy rules are established algorithmic ideas.
Classification: **known after translation of notation** at the selection-mechanism
level. Its scalar-coordinate convergence statements are not verbatim proofs of
our matrix residual bound, arithmetic graph, or program-specific posterior theorem.

## 2. Block selection

Julie Nutini, Issam Laradji, Mark Schmidt, “Let's Make Block Coordinate Descent
Converge Faster: Faster Greedy Rules, Message-Passing, Active-Set Complexity, and
Superlinear Convergence,” JMLR 23(131):1–74, 2022.
Primary published PDF: https://jmlr.org/papers/volume23/18-045/18-045.pdf

Section 3 analyzes block gradient rules. Section 3.2, equation (12), selects a
block by its squared gradient norm divided by its block Lipschitz constant. With
common constants this agrees with the ordinary block Gauss–Southwell rule.
The paper also develops other block choices and computational refinements.
Classification: **known after translation of notation** for our maximum-energy
output-packet selection, rather than evidence of a new optimization principle.
Our conservative residual-energy rate and Lean implementation proof are a specific
specialization and formal construction, not a claimed improvement to those rates.

## 3. Gaussian conditioning, approximation, and Wasserstein error

James T. Wilson, Viacheslav Borovitskiy, Alexander Terenin, Peter Mostowsky,
Marc Peter Deisenroth, “Pathwise Conditioning of Gaussian Processes,”
JMLR 22(105):1–47, 2021.
Primary published PDF: https://jmlr.org/papers/volume22/20-1260/20-1260.pdf

The paper develops Gaussian conditioning at the random-variable level and studies
approximate pathwise updates. Sections 5.6 and 6 compare cost/accuracy and analyze
posterior error in 2-Wasserstein metrics. Figure 5 includes exact, sparse and
conjugate-gradient updates with caching considerations. Section 6 assumes a compact
finite-measure domain for its process-space analysis.
Classification: **partial or adjacent result only** for the complete release theorem,
with substantial overlap in the conditioning, common-noise approximation and
Wasserstein-error ingredients. This source rules out portraying the broad combination
of pathwise conditioning, iterative solution and Wasserstein analysis as newly
introduced here. It does not by itself identify our particular Lean program theorem.

## 4. Formal certification of rounded arithmetic

Marc Daumas, Guillaume Melquiond, “Certification of bounds on expressions involving
rounded operators,” arXiv:cs/0701186v2, 24 May 2007; later ACM TOMS publication.
Version inspected: https://arxiv.org/pdf/cs/0701186
The inspected PDF labels itself v2, 24 May 2007.

The source describes Gappa's interval and forward-error reasoning over exact and
rounded operations, dyadic endpoints, and generated formal certificates. Section
3.2 explains Boolean reflection in the Coq support library. The inspected version
distinguishes its established Coq library from a then-incomplete HOL Light support
boundary. It also explicitly places general branches and loops outside that work's
scope. Classification: **partial or adjacent result only** for our inference solver,
but direct prior art for arithmetic bounds and proof-producing numerical certificates.
We should credit this established methodology rather than claim to have invented
proof-carrying numerical error bounds.

## 5. Iterative Gaussian inference at practical scale

Jihao Andreas Lin, Shreyas Padhy, Javier Antorán, Austin Tripp, Alexander Terenin,
Csaba Szepesvári, José Miguel Hernández-Lobato, David Janz,
“Stochastic Gradient Descent for Gaussian Processes Done Right,” ICLR 2024.
Inspected author PDF: https://arxiv.org/pdf/2310.20581

The inspected PDF identifies the ICLR 2024 paper. It formulates iterative Gaussian
inference through kernel linear systems and studies stochastic dual descent,
momentum, averaging and large-scale experiments. Classification: **partial or
adjacent result only**. It reinforces that iterative Gaussian inference and practical
scalability are established research areas. Our seven cases of dimension at most
eight do not constitute a competitive evaluation against such methods.
An attempted arXiv HTML-v2 view failed; the PDF fallback was available. No
version-sensitive theorem from this source is used as a proof dependency.

## Explicit dictionary for the optimization overlap

This dictionary is a mathematical interpretation of our definitions, not an
additional Lean theorem claimed by this release. Let C=PH^T and consider

    phi(B) = (1/2) tr(B S B^T) - <B,C>_F.

For symmetric positive-definite S, its Frobenius gradient is B S-C=-F(B).
The orthogonal output-packet subspaces are

    V_a = { Q_a X : X is a state-by-observation matrix }.

The projected gradient is -Q_a F(B). Therefore maximizing our packet energy
E(Q_a F(B)) maximizes the squared block-gradient norm. An orthonormal basis
adapted to the ranges of Q_a converts these subspaces into ordinary coordinate
blocks. Such a basis may be real even when Q_a is rational; this interpretation
is not a claim of rational basis conversion in the executable solver.

Our update B'=B+tau Q_a F(B) is the corresponding block-gradient step with a
conservative common step size. The residual cache is maintained by exact linear
identities. These ingredients should be attributed as a formalized specialization
of established methods. Our proof measures residual energy directly and then
connects it to a particular Gaussian posterior certificate.

## What this comparison supports

The defensible contribution statement is an integrated, machine-checked finite-
dimensional inference implementation: cache invariants, exact selective trajectory,
computed finite fuel and verification precision, rounded certificate evaluation,
actual posterior tolerance, and interval parameter output, with explicit trust and
resource boundaries. This statement describes the delivered artifact. It does not
establish that its exact theorem combination is the first in the literature.

We found significant component overlap, not a contradiction of the Lean proofs.
An established breakthrough or globally novel architecture claim remains unsupported.
No item is classified “apparently new” on the basis of this bounded search.
