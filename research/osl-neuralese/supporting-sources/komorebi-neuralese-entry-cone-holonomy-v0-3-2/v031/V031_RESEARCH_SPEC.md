# Neuralese v0.3.1 — Entry, Cone, and Holonomy Factorization

Author: Komorebi P.  
Version: 0.3.1  
Date: 2026-09-03  
Status before execution: prospectively frozen adaptive-developmental diagnostic

## Purpose

This block does not train or repair a model. It examines the two frozen
projective-terminal systems through three finite diagnostic views:

1. an entry-interface defect at an unadvanced anchor;
2. a finite recurrent region whose history-bearing states remain inside the
   correct decoder decision cones;
3. path-dependent projective drift that can cross a future decoder facet,
   with repeated-relator paths contrasted against a finite frozen
   matched-control panel.

The exact registration is machine-readable in `V031_PREREGISTRATION.json`.
`DESIGN_DISCLOSURE.json` records that relation matrices and spectra,
grouped/stepwise equivalence, and published continuation margins, ray angles,
predictions, and revealing-suffix outcomes on the 930000/931000 episodes were
inspected during design. They are exploratory design context. No
learned-checkpoint endpoint was computed on the exact serialized
940000/941000 episode realizations before freeze. The study remains
adaptive-developmental and nonconfirmatory because the checkpoints and task
family were already studied.

## Causal interface

Let the decoder row for semantic state (q) be (d_q). For an episode-specific
canonical generator matrix (A_g), a canonical word
(w=(g_1,\ldots,g_m)) acts on column states by

\[
A_w=A_{g_m}\cdots A_{g_1}.
\]

The recurrence divides by a strictly positive norm after each generator. It
therefore preserves the positive ray and the sign of every downstream linear
decision comparison. For exact semantic endpoint (wq), define

\[
\ell_{q,w,j}(h)
=
(d_{wq}-d_j)^\mathsf{T}A_wh,
\qquad j\ne wq.
\]

The finite safe cone is

\[
K_q^{(H)}
=
\bigcap_{|w|\le H}\bigcap_{j\ne wq}
\{h:\ell_{q,w,j}(h)>0\}.
\]

The cone is open and homogeneous. The study checks only membership of declared
reached states. It does not solve the ambient polyhedral feasibility problem or
claim that (K_q^{(H)}) stabilizes as (H\to\infty).

For a nonzero pulled-back facet, the signed angular clearance is

\[
c_{q,w,j}(h)
=
\frac{(d_{wq}-d_j)^\mathsf{T}A_wh}
{\|A_w^\mathsf{T}(d_{wq}-d_j)\|_2\,\|h\|_2}.
\]

Its sign is the hard decision sign, while its magnitude is invariant to a
positive rescaling of either the state or the word product.
Any registered pulled-back decoder facet with norm at or below (10^{-14})
causes a conditioning abort rather than being normalized or interpreted.

## Module A — entry versus recurrence

For every semantic state (q) and generator (g\in\{R,F\}), construct

\[
z_{q,g}=\operatorname{normalize}(A_g a_{g^{-1}q}),
\]

where (a_q) is the stored native anchor. Native anchors, R-incoming states,
and F-incoming states are followed under every suffix through horizon eight.
The registered hard questions are whether the known seed-0 state-2 issue is
confined to the empty suffix, whether both uniform reanchoring schemes repair
it without regression, and whether the two incoming routes share one hard
continuation signature.

A wrong-semantic decoy uses the incoming state for
(q^\dagger=(q+1)\bmod 8) while being presented as a candidate replacement for
(q). It must follow the exact future of (q^\dagger), never (q). This rules
out a generic norm-only or common-attractor explanation. The intervention is
oracle-assisted and is not presented as a learned repair.

## Module B — finite observed-state cones

Every canonical history of exact length one through eight and every visible
start is enumerated for each fresh episode. Every such state is checked under
all suffixes cumulatively through horizon eight. One episode-local bank stores
the exact suffix products, semantic actions, and normalized pulled-back decoder
facets. The same bank is reused across all reached states and long-path
conditions; the logical Cartesian history–suffix domain is unchanged.

The primary table reports, for every exact history depth (L) and horizon
(H), state count, logical decision count, number of safe states, strict
minimum margin, minimum signed angular clearance, and a locator for the weakest
facet. A recursive descendant computation is checked against direct shell
enumeration. The robustness flag (c>10^{-10}) is separate from strict
positivity.

## Module C — repeated relations and projective spectroscopy

Four identity blocks are registered:

| Name | Canonical word | Length |
|---|---|---:|
| `f2` | F F | 2 |
| `r4` | R R R R | 4 |
| `frfr` | F R F R | 4 |
| `rfrf` | R F R F | 4 |

`f2` is evaluated at every repeat 0–32; the length-four blocks at every repeat
0–16. Each configuration is followed under all suffixes through horizon eight.
The base domain crosses all eight starts with a frozen nonempty path to each of
the eight D4 endpoints, giving 64 recurrent base cases per episode without
reusing a raw entry anchor.

This long-path starting domain is a deterministic transversal: exactly one
selected nonempty prehistory per D4 endpoint crossed with eight starts. It does
not enumerate every prehistory or recurrent state, and its continuation
suffixes stop at H=8. The cone module's exhaustive histories through L=8 do
not make this 64-case long-path domain exhaustive. Long-path conclusions are
therefore restricted to this transversal and do not describe a path
distribution.

For relation product (P_r=A_r), normalized stepwise execution and repeated
application of a positively rescaled (P_r) must agree within (10^{-10}) in
both unit-state distance and positive-ray angle. This is a numeric reduction,
not a semantic success criterion.

The primary causal endpoints are absolute hard failure, hard disagreement from
the same-semantic shallow baseline, first revealing suffix, first failing
suffix, and minimum margin. Spectra, singular values, nonnormality, and the
nearest positive scalar-identity defect are mechanism descriptors. They do not
certify the causal quotient. Moreover, `frfr` and `rfrf` have the AB/BA
isospectral relation, so any ordered-path difference must be established by
orbits, eigenvectors, or decision facets rather than eigenvalues alone.

`B0` requires every one of the 64 base-transversal cases in every fresh episode
to be strictly eligible through H=8, and `P0` checks grouped-versus-stepwise
ray agreement. `H0` and `H1` are complementary scientific outcomes: no exit,
or at least one exit, on the registered grid. `H2` is a stronger replication
predicate: one common `(relation, repeat_count)` cell must contain an exit in
each of the four checkpoint-by-episode-half strata. Marginal coverage pooled
across different cells does not satisfy it. `H3` marks at least one delayed
reveal at suffix depth greater than zero.

## Module D — exact matched paths

The reference panel repeats each of the four relation templates to inserted
budgets 16, 32, and 64. For every reference and parity-reachable D4 endpoint,
an exact dynamic program globally minimizes the first three scientific match
coordinates and then globally applies Hamming and binary-lexical tie-breaks
for a unique deterministic choice:

1. generator-count L1 distance;
2. directed-bigram-count L1 distance;
3. run-second-moment error;
4. Hamming deterministic tie break;
5. binary lexical deterministic tie break.

The identity control must differ from its reference. Word length parity is a
D4 invariant: an even-length word can reach only `e`, `R2`, `FR`, and `FR3`.
The missing odd endpoints therefore cannot be called same-length controls. The
v0.3.1 bank contains exactly 48 primary controls and does not materialize the
secondary B-1/B+1 sandwich. Any later sandwich is a separately frozen parity
sensitivity analysis.

Together with 12 references, those controls define 60 condition aliases but
only 54 distinct word trajectories. There are 12 directed
reference-versus-identity-control condition comparisons and nine unique
unordered word pairs. At each budget, the `frfr` reference is the `rfrf`
identity control and conversely; the two directed cells therefore encode one
unordered identity-path comparison. These aliases are reported rather than
treated as independent evidence.

Every control is evaluated against its own exact semantic endpoint and a
frozen shallow path to that same endpoint. The comparisons report finite
path-contrast patterns. The bank is finite and deterministic; no p-value or
sampled-word population claim is made.

Only the distinct identity control holds the reference's semantic endpoint
fixed. The `R2`, `FR`, and `FR3` controls are exact-length and exposure-matched
but cross semantic endpoints. Their severity contrasts cannot by themselves
separate path effects from endpoint or decoder-facet difficulty. Accordingly,
the finite panel contrasts patterns; it does not identify a generic-versus-
relator-specific mechanism or support a word-population claim.

For the finite classifications, path severity is ordered lexicographically by
hard-failing base-case count, hard-revealing base-case count, and negative
minimum target margin, aggregated separately inside each checkpoint. A
classification requiring replication must hold in the same relation-budget
cell in both checkpoint aggregates. The direct reference-versus-identity-
control contrast compares the full prediction matrices, not merely their
separate error totals.

The descriptive predicates have the following exact meanings:

- `X0`, replicated nonidentity-control excess: in one relation-budget cell,
  the same one of `R2`, `FR`, or `FR3` has greater severity than the identity
  reference in each checkpoint aggregate.
- `X1`, finite-pair identity-path hard-signature difference: in one cell, the
  repeated identity relator and its one distinct exact-length identity control
  disagree directly in each checkpoint aggregate.
- `X2`, finite-pair relator-reference severity dominance: in one cell, the
  repeated identity relator has greater severity than its one distinct
  exact-length identity control in each checkpoint aggregate.
- `X3`, reference-over-all-nonidentity-control dominance: in one cell, the
  repeated identity reference has greater severity than each of the `R2`,
  `FR`, and `FR3` controls in each checkpoint aggregate.
- `X4`, mixed finite comparison pattern: `X0` is true and at least one of `X2`
  or `X3` is true; their supporting cells need not be the same. `X1` is not
  part of this formula.

`M0` requires every same-endpoint shallow baseline for `e`, `R2`, `FR`, and
`FR3` to remain eligible through H=8. `M1` requires all 60 frozen condition
aliases, corresponding to 54 distinct words, to execute in every episode.
The `X` predicates are interpretable only when both `M0` and `M1` hold.

As in Module C, the matched analysis uses only the 64-case deterministic base
transversal per episode and suffixes through H=8. It does not enumerate all
prehistories or recurrent states.

## Interpretation contract

The registered execution is one-shot. It requires CPython 3.12.13 and NumPy
2.3.5, authenticates the complete frozen byte set before importing scientific
modules, and atomically creates `results/V031_RUN_STARTED.json` after validation
but before either checkpoint is opened. An existing start ledger, invalid-attempt
record, or final result permanently forbids another v0.3.1 execution.

Integrity and eligibility predicates determine whether an analysis is
interpretable; scientific outcome predicates report which finite pattern
occurred. In particular, `H0` and `H1` are complements, and `X0`–`X4` are
classifications rather than pass/fail quality gates. There is no rule under
which all predicates should be true.

The preregistered finite composites are:

- entry-localized finite behavior: `E0 and E1 and E2 and E3 and E4`;
- finite observed-cone safety: `K0 and K1`, robust only with `K2` as well;
- registered long-path exit: `B0 and P0 and H1`, broadly replicated only with
  `H2`, and delayed only with `H3`;
- matched-panel interpretability: `M0 and M1`, after which `X0`–`X4` may be
  reported; otherwise they are not interpretable rather than false;
- full finite factorization: entry-localized finite behavior, finite
  observed-cone safety, and registered long-path exit together.

The study can establish a finite decomposition such as:

\[
\text{faulty entry chart}
+
\text{short-horizon safe recurrent cone}
+
\text{long-path cone exit}.
\]

It cannot establish a universal hidden language, a minimal causal quotient,
infinite-depth closure, an invariant metric, or normally attracting nuisance
fibers. Every composite is descriptive only on the exact frozen finite and
transversal domains; none licenses a task-family, path-distribution,
model-population, or universal-Neuralese claim. A metric, projection, reset,
damping, or retraining intervention is deferred until this finite diagnostic
block supplies evidence about which repair is worth testing.
