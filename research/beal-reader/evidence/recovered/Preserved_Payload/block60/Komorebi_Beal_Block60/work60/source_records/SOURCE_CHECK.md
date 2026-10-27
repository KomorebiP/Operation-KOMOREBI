# Source/application check for Block60

Checked 19 September 2026. No global novelty assertion. Broad discovery queries
returned substantial irrelevant material, which was not used. Exact sources
were opened directly. No local PDF-byte cache or PDF hash is claimed.

## S1. Diagonal period factor

Takashi Ichikawa, The universal periods of curves and the Schottky problem,
Compositio Mathematica85 (1993),1-8. Published identifier CM_1993__85_1_1_0.
Source: `https://www.numdam.org/item/CM_1993__85_1_1_0.pdf`.

Rendered and inspected printed pp3,5,6 (zero-index PDF pages3,5,6). Section1.2
states the multiplicative Jacobian period product; in the diagonal identity
coset its factor is the generator multiplier y_i. Proposition2.4 and
sections2.5-2.7 show the other factors tend to1 in the degeneration, and give
the specialization to actual periods. Application: after computing the marked
smoothing derivative y_i/epsilon, Pi_ii/epsilon has the same residue. A formula
for a generic Schottky multiplier alone would not identify that derivative.

## S2. Universal marked gluing and actual specialization

Takashi Ichikawa, Periods of generalized Tate curves, arXiv:1909.10149v4,
1 June2020. Source: `https://arxiv.org/html/1909.10149` (the opened page explicitly
identifies v4). Section2.3 gives the Schottky matrix in terms of two marked
points and y_e, the formal quotient construction, and the universal deformation
statement for a split degenerate stable curve over a complete local base.

Translation: in w=(lambda-P+)/(lambda-P-), that matrix gives w(gamma(lambda))=
y_e w(lambda); the two branch coordinates therefore multiply to y_e. Applying
the stated deformation to the actual normalized family identifies its
first-order y_e with the coefficient obtained from UV=delta(f_epsilon-f_0).
This local algebra and its unit/sign factors are proved anew in DIAGONAL_PERIODS.md.
The marked points remain distinct and all required differences are units.

## S3. Retained inputs, not newly substituted sources

The actual Frey model, twist, natural-lattice identification and stable reduction
remain inherited Block59 inputs, with seven immediate source leaves pinned by
SHA256 and the entire predecessor byte-preserved. Its Mumford1972 uniformization
and Gregory-Liedtke2019 Tate/Kummer source records remain available in the
predecessor. The finite-level torsion argument, including sufficiency, is also
proved directly in LOCAL_CRITERION.md.

## Evidence boundary

The sources establish the classical period and deformation framework. They do
not state the new constants for this Frey family or prove the global branch.
The comparison and arithmetic consequences received an author self-review, not
an independent mathematical review or Lean verification. The finite programs
cannot authenticate the analytic theorem by themselves.
