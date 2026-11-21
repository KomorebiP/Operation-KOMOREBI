# Self-review of the coordinate-boundary classification

Claim: Theorem M in EXCEPTIONAL_ORDERS.md, checkpoint SEQ-DH-2026-11-21-004.
Verdict: **proved as written**. This is a separate adversarial pass by the
project authoring agent, not independent review or Lean formalization.

The statement classifies minimal eventual scalar constant-coefficient
recurrence orders over every characteristic-zero field on abuv=0. The entire
union of four coordinate hyperplanes, including all intersections, is covered.
The fully nonzero locus is outside this theorem.

## Dependency and edge-case audit

| Obligation | Finding and decisive evidence |
|---|---|
| Defining moments | The displayed even/odd moments agree with the existing falling-linear weight and first-order operator conventions |
| Four functional reductions | rho1=sigma*rho2; shifted central-binomial ratios and formal integration by parts give every reduction, including the first moments |
| Singular rho1 base | H3=-1; the Rodrigues norms are -2n/(n-2), nonzero for n>=3; no inverse smaller Gram matrix is used |
| Infinite rho1 branch formula | Formal self-adjointness, distinct eigenvalues and the exact Laurent ODE identity identify the monic solution |
| Quadratic transforms | Augmented Vandermonde expansion inherited from K applies with two roots; signs are (-1)^(2N)=1; the scalar normalizations are (-2A)^N/16 and (2A)^N(N-1)(N-2)/4608 |
| Quartic base factors | Elementary symmetric functions of the four bases give the displayed characteristic polynomials; scalar scaling restores u |
| Odd cubic transform | Three roots give (-1)^(3N), hence (-2d)^N/4608; the six bases yield the stated order-42 polynomial |
| Initial boundaries | All ten complete polynomial identities pass: rho1 quadratic N=1,2; rho2 quadratic and odd cubic N=1..4 |
| Repeated roots and leading drops | Recurrence residues are polynomials in original coefficients and vanish generically, hence identically in characteristic zero |
| Infinite GF identification | Smaller uniform bounds hold from N=1, so convolution through the denominator degree determines the complete numerator |
| Parameter coverage | Numerator coefficient degrees j, floor(j/2), floor(j/2), 2j follow from determinant homogeneity and parity; all 75 degree-complete nodes are checked |
| Generic minimality in each normalized family | Four exact identities U*N+V*Q=H exclude every further cancellation outside the listed roots, over any characteristic-zero field |
| Critical parameters | All nine cross multiplications and rational Bezout witnesses pass; their denominators have exactly the displayed degrees |
| Squared-variable normalization | Substituting s=(avz)^2 into the Bezout identity preserves coprimality and doubles degree, including orders 26 and 18 |
| Missing normalization intersections | a=v=0 and a=u=0 have explicit all-index exponential-polynomial formulas with nonzero leading coefficients; all other intersections fall into a normalized family or zero functional |
| Zero weights/operators | If either parameter pair vanishes, every positive-index determinant is zero and order zero is exact |
| Index zero | Nonzero reduced numerators have full denominator degree, so their recurrences start at one; exponential continuations at zero differ from W0=1 |
| Real versus algebraic fields | The orders 10 and 22 require the stated quadratic relations; neither has nonzero real u,v |
| Stronger fully nonzero classification | Not established or claimed |

The theorem table first removes zero functionals, then reads v=0, u=0,
b=0 with auv nonzero, and a=0 with buv nonzero. This is a disjoint exhaustive
decision rule for the remaining coordinate boundary. It prevents conflicting
intersection labels and makes all divisions legitimate in their stated rows.

## Computation provenance and interpretation

- sequence-exceptional-probe-001: 17 exact rational examples, using the parent
  all-index recurrence to reduce GFs and direct monomial determinants. These
  suggested the strata; examples alone do not classify parameters.
- sequence-exceptional-parameter-001: SymPy 1.14.0 constructs four complete
  parameter-polynomial numerators, cleared Bezout witnesses and nine critical
  reductions. The retained result is a certificate, not a trusted black box.
- sequence-exceptional-replay-001: separate Python 3.12.14 standard-library
  sparse polynomial arithmetic replays every load-bearing certificate identity,
  ten small-boundary identities, the rho1 Laurent ODE, all 75 required nodes
  (1,572 numerator coefficient checks), 947 direct monomial determinants and
  96 closed-intersection checks. The Rodrigues/norm checks at n=3..16 are
  regressions; the written formal residue argument supplies all n.

All three runs completed within their recorded bounds. Their manifests pin
inputs and outputs; the runner could not resolve Git on its original PATH,
so repository provenance is supplied separately by CHECKPOINT.json. The parent
50-artifact checkpoint was rehashed without changes. Published parent source
SHA-256: b58c441239f673ed6b65a7203b20b46636376366b6308a95a47c93c26c3fc93d.

## Proofreading self-review

Applied proofread-math self-review to the new theorem and this review. Checked
quantifiers, parameter exclusions, determinant indices, normalization variables,
TeX delimiters, table coverage, cross-references and prose/display continuity.
Reflowed the defining moments. Added explicit norm, uniqueness, base-factor and
one-root calculations as mathematical exposition after the proof audit; these
are research additions, not silent mathematical typo corrections. No earlier
mathematical source or formula was changed. Mathematical-token typo corrections: 0.
After visual inspection, the residue definitions and norm calculation were
reflowed across aligned lines for narrow screens. Their values and hypotheses
are unchanged; the explicit multiplication dot replaces juxtaposition only.

## Route disposition and next work

The formal orthogonal-polynomial route supplies the smaller all-index bounds;
the GF route completes minimality using exact coprimality identities. The direct
determinant route checks implementation and initial boundaries and rejects a
stronger start at zero. The bounded coordinate-boundary target is reached.

The next research target is the exceptional fully nonzero locus abuv!=0.
Its generic order is already 112, but this phase does not classify its critical
subvarieties. Higher-degree weights and higher-order operators remain separate
open work. No claim of historical novelty or external acceptance is made.
