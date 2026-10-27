# V0.2 design freeze

**Frozen before any v0.2 model outcome was inspected:** 2026-09-02 UTC

## Question

Does a single learned positive-definite latent metric, combined with an
independently encoded anonymous composition law, convert the operator-shaped
permutation-table executor into a dynamically controlled recurrent system while
preserving exact behavior on operator tables excluded from training?

## Corrections inherited from the v0.1.1 audit

1. V0.1.1 exhausted all 10,080 slot-ordered D4 generator-table pairs. V0.2
   partitions individual permutation tables into deterministic 60/20/20
   train/development/test sets and rejects every cross-partition exposure.
2. The original donor-state and operator-code patches are native splice checks,
   not independent mechanistic evidence. V0.2 adds distinct-context state
   substitution and independently encoded composed-operator substitution with
   on-manifold wrong-state and wrong-composition controls.
3. V0.1.1 transport anchors were unbalanced and included many repeated initial
   embeddings. V0.2 balances nonzero anchor depths and compares affine transport
   with shuffled-fit and decode-then-re-embed baselines.
4. V0.1.1 source digests included generated integrity files. V0.2 uses explicit
   code and protocol digests and fails closed when gates or arm/seed cells are
   missing.

## Factorial arms

- terminal-only linear recurrence
- fixed-Euclidean isometry pressure
- learned-metric isometry pressure
- anonymous composition pressure
- learned metric plus anonymous composition, the primary mechanism
- learned metric plus shuffled composition, a matched structural null
- the strongest pre-existing named-relation comparator, frozen at weight 0.60
- an unconstrained GRU comparator

All learned linear arms retain the same eight-dimensional recurrent state and
the same full transition-table input. The auxiliary composition objective may
use only visible tables. It may not access canonical operator identities,
coordinate permutations, or named D4 relations. Every independently encoded
composition table used in training must belong to the train partition.

## Metric mechanism

One global metric is shared by every episode and operator. For a symmetric,
trace-free, smoothly bounded log metric S,

\[
G=\exp(S),\qquad Q(M)=\exp(S/2)M\exp(-S/2).
\]

The isometry objective is the intrinsic whitened residual

\[
\|Q(M)^\top Q(M)-I\|_F^2/d.
\]

The determinant is fixed at one by construction, and metric condition number is
audited. A small residual obtained through an ill-conditioned metric is a
failure, not a success.

## Composition mechanism

For row-coded observable tables, applying P and then Q gives

\[
T_{Q\circ P}=T_PT_Q.
\]

The independently encoded table must satisfy

\[
E(T_PT_Q)\approx E(T_Q)E(T_P).
\]

Comparing a recurrent product with itself is forbidden because it is
tautological. Shuffled or reversed composed tables form the matched null.

## Primary evaluation domains

- exact held-out individual operator tables from the test partition
- D4 depths 7, 8, 9, 31, 32, 33, 63, 64, 65, 127, 128, and 129
- C8 at the same depths
- independently sampled permutation pairs as secondary OOD evidence
- hidden finite rate, Euclidean and G-norm growth, singular-value distortion,
  isometry defect, spectral radius, and word-product growth
- composed-table substitution, cross-context state substitution, and controls
- balanced nonzero-depth cross-seed transport plus trivial label baselines

## Interpretation boundary

The full transition table is supplied to a model whose operator encoder maps an
8 by 8 table to an 8 by 8 latent matrix. An exact analytic solution exists:
encode the table transpose and represent states one-hot. Success therefore
establishes stable learned equivariant table execution under an explicit
operator-form bias. It does not establish spontaneous Neuralese, recovery of a
canonical abstract operator, open-ended operator discovery, unrestricted or
unbounded recurrence, language-model generality, awareness, or consciousness.

The development smoke run may choose numerical weights using only development
partitions and development seeds. The locked primary protocol, seeds, weights,
thresholds, and code digest must be written before any primary test-partition
outcome is evaluated.
