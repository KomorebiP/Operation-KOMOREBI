# Invariant Observable Kernel protocol

**Version:** 0.6.0  
**Author:** Komorebi P.  
**Status:** developmental mechanism block; not confirmatory evidence

## Question

The v0.5 screen found that all twelve latent directions eventually became
visible to a suffix observer.  Exact relation pressure reduced both long-depth
error and semantic/ambient mixing, but the packet objective did not create a
forward-invariant null space.  The v0.6 question is therefore:

> Can an exact or explicitly learned invariant kernel prevent ambient
> contamination while preserving causal operator execution, and can semantic
> relation flatness coexist with nontrivial but behaviorally inert ambient
> holonomy?

This block separates sufficiency, induced learning, and spontaneous emergence.
It does not pool those claims.

## The exact decomposition

For eight output classes, behavior is invariant to adding the same scalar to
every logit.  With

\[
C=I_8-\frac18\mathbf 1\mathbf 1^\top,
\]

the centered-logit interface has maximal linear rank seven.  This is an upper
bound supplied by the declared observation interface, not a claim that seven
is the minimal dimension of argmax semantics.  The actual centered decoder
\(CD\) may have lower rank; identifying an exact five-dimensional kernel
therefore remains conditional on the registered, fail-closed rank-seven
certificate.  The hard arm's registered latent decomposition is

\[
H=S_h\oplus L\oplus K,
\qquad
(\dim S_h,\dim L,\dim K)=(7,1,4).
\]

- \(S_h\) is the embedded Euclidean carrier for centered-logit state.
- \(L\) is the common-logit gauge line.
- \(K\) is the four-dimensional ambient fiber.
- \(N=L\oplus K\) is the five-dimensional centered-observation kernel.

Here and below, implementation symbols such as \(P_S\) refer to the projector
onto \(S_h\).  The distinction between \(L\) and \(K\) is compiled and typed
only in the hard arms.  Both are null to the declared centered-logit interface,
but only \(K\) is used for the vertical-holonomy control.  The learned arm
identifies only the untyped split \(H=S_h\oplus N\); it does not establish a
learned \(L/K\) decomposition or learned \(K\)-holonomy.  Neither hard-arm
null component is called functional memory in this experiment.

## Hard fixed-gauge construction

Let \(W=[U_S\ U_L\ U_K]\in O(12)\) be drawn from a sealed seed and frozen.
For each visible operator table, the hard model executes

\[
M_g=W\bigl(A_g\oplus 1_L\oplus R_g\bigr)W^\top,
\qquad
A_g\in O(7),\quad R_g\in O(4).
\]

Each start anchor has the registered form

\[
h_i=\sqrt{\frac78}\,s_i+\frac1{\sqrt8}\,u_L,
\qquad \|s_i\|=1,
\]

with zero \(K\) component.  When the learned \(s_i\) form the regular
seven-simplex, these eight anchors are orthonormal, so the inherited anchor
conditioning loss remains satisfiable.  The centered readout is restricted to
\(S_h\); \(L\) may contribute only a common logit shift.  Consequently

\[
P_S M_g P_N=0,
\qquad
P_N M_g P_S=0,
\qquad
CDP_N=0,
\]

where \(P_N=P_L+P_K\).  Orthogonality also bounds every hidden norm.

The frame \(W\) is pure gauge and is not optimized.  The nuisance-fiber
encoder is separately initialized and frozen.  Its motion is deliberately
causally inaccessible to the task.  The hard arm is therefore an
architectural positive control, not evidence that a kernel, frame, or ambient
language emerged from terminal supervision.

## Learned-intertwiner arm

The induced-learning arm retains the unrestricted full \(O(12)\) recurrent
model.  An auxiliary row-orthonormal map

\[
\Pi\in\mathbb R^{7\times12},
\qquad
\Pi\Pi^\top=I_7
\]

is learned under explicit auxiliary pressure.  It does not construct
the base model's encoder, decoder, or operators.  It is initialized from the
instantaneous centered-readout rowspace only.  This is output-informed but
data-free scaffolding: it supplies the output boundary and the chosen rank,
while consulting no operator, training example, target value, continuation,
suffix, or future-observability information.  The rowspace is invariant to a
permutation of output rows, so it does not select a class identity or a basis
inside the quotient.  It is nevertheless an initialization advantage and is
not evidence that the observable plane emerged spontaneously.  Let

\[
P=\Pi^\top\Pi,
\qquad
Q=I-P,
\qquad
T_g=\Pi M_g\Pi^\top.
\]

The registered losses are:

\[
G_B=(\Pi B)^\top(\Pi B)=B^\top P B,
\qquad
\mathcal L_{anchor}=\frac{\|G_B-C\|_F^2}{7},
\qquad
C=I_8-\frac18\mathbf1\mathbf1^\top,
\]

\[
\mathcal L_{readout}=
\frac{\|CDQ\|_F^2}{\operatorname{stopgrad}(\|CD\|_F^2)+10^{-4}},
\]

\[
\mathcal L_{int}=\mathbb E_g\frac{
\|\Pi M_gQ\|_F^2+\|QM_g\Pi^\top\|_F^2}{14},
\]

and an anonymous relation loss on products of the induced \(T_g\).  The anchor
target is the centered-simplex Gram matrix, not a selected seven-dimensional
chart.  It is invariant under \(\Pi\mapsto U\Pi\) for every \(U\in O(7)\), so
it supervises quotient-anchor geometry without fixing a basis within the
observed quotient.  More precisely, if \(Z\) is any fixed Helmert chart with
\(Z^\top Z=C\) and \(ZZ^\top=I_7\), then in exact arithmetic

\[
(\Pi B)^\top(\Pi B)=C
\quad\Longleftrightarrow\quad
\Pi B=UZ\ \text{ for some }U\in O(7).
\]

Thus the Gram target is exactly the chart target modulo quotient basis.  It
does not by itself align the observer with the centered readout, eliminate
anchor-specific components in \(N\), or identify a common-logit line inside
\(N\); those are separate claims.  This remains explicit semantic geometry
supervision.

Success in this arm supports a quotient induced under intertwining pressure,
not spontaneous emergence.  The unregularized polar arms retain a sealed
posthoc observability audit as the actual emergence check.

The arm deliberately bundles anchor geometry, centered-readout, intertwining, and
semantic-relation pressure.  A positive result therefore supports the combined
recipe only; it does not causally attribute the effect to any one auxiliary
term.  Component ablations belong to a later block if the combined mechanism
first survives this screen.

To keep those constraints from preventing the task representation from forming
at all, the screen and pilot hold every v0.6 auxiliary at zero through step 800
and linearly ramp it to its registered weight at step 1600.  The forty-step
smoke uses the same shape compressed to steps 0--40.  This staged schedule was
fixed after retired-seed diagnostics showed that strong quotient pressure from
the first update could produce a geometrically tidier but behaviorally collapsed
model.  It is part of the sealed training contract, checkpoint metadata, and
verification receipt; it is not an adaptive early-stopping rule.

### Paired auxiliary-context estimator

Every profile uses exactly eight auxiliary contexts per optimization step. The
registered selection rule is `first_n_accepted_rows_without_replacement`: take
the first eight rows of the accepted terminal batch in stream order. No loss
value, operator geometry, target, or model output is used for selection.
Conditional on the inherited terminal firewall, accepted rows are exchangeable,
so this order-defined sample is an unbiased paired estimator and remains fully
deterministic.

Each selected context supplies all nine anonymous, table-derived relation
cells. One step therefore contains \(8 \times 9 = 72\) context-cell observations
for each context-dependent auxiliary. The registered aggregation is
`mean_over_contexts_and_cells_not_sum`: average across the nine cells within
each context and across the eight contexts. Increasing the number of contexts
therefore reduces estimator variance without multiplying a loss coefficient.

The exact registered exposure map is:

| Field | Registered value |
|---|---|
| `selection` | `first_n_accepted_rows_without_replacement` |
| `contexts_per_step` | 8 |
| `cells_per_context` | 9 |
| `cells_per_step_total` | 72 |
| `aggregation` | `mean_over_contexts_and_cells_not_sum` |
| `shared_across_arms` | `true` |

All six arms share the same eight accepted row indices, row order, and nine
cells per row. Arms for which a particular auxiliary is inactive retain a zero
contribution; they do not receive a different context sample. This pairing
governs every context-dependent v0.6 auxiliary, including full-space relation
flatness, learned-intertwiner operator and semantic-relation terms, and hard
semantic-block relation flatness. Anchor-Gram and centered-readout terms are
model-global and therefore do not acquire an artificial factor of eight.
This correction is training plan
`v0.6-invariant-observable-kernel-dev2`; the preceding single-context `dev1`
plan was retired before the untouched screen seed was run.

## Six-arm panel

| Arm | Recurrent geometry | Additional pressure | Intended role |
|---|---|---|---|
| `polar_supervised` | unrestricted \(O(12)\) | terminal/construction only | full-space baseline |
| `polar_cr` | unrestricted \(O(12)\) | inherited composition and delayed-return pressure | strongest inherited comparator |
| `polar_exact` | unrestricted \(O(12)\) | full-space anonymous relation equality | v0.5 best mechanism |
| `learned_intertwiner` | unrestricted \(O(12)\) | rank-7 anchor geometry, centered-readout, intertwining, semantic relation | induced quotient test |
| `hard_kernel_supervised` | compiled \(7\oplus1\oplus4\) | terminal/construction only | architectural sufficiency control |
| `hard_kernel_semantic_flat` | compiled \(7\oplus1\oplus4\) | semantic-block anonymous relation equality | primary developmental mechanism |

All six arms consume the same accepted/rejected terminal proposal stream and
the same eight-context anonymous relation schedule. Identity and \(r^2\) terminal
action groups remain behind the inherited label firewall.

All four nominally polar arms use a direct linear rollout in v0.6.  Since the
executed matrices are orthogonal, this agrees with the inherited projective
rollout on natural unit-norm trajectories up to rounding.  Removing the
otherwise redundant per-step normalization is necessary for a nonzero
null-space intervention not to change semantic logit scale through a shared
denominator.

## Quotient flatness

For equivalent words \(u\sim v\), define \(L=M_u\) and \(R=M_v\).  Report
separately

\[
\epsilon_S(u,v)=
\frac{\|P_S(L-R)P_S\|_F}{\sqrt7},
\]

\[
\epsilon_K(u,v)=
\frac{\|P_K(L-R)P_K\|_F}{2},
\]

and the full-space defect.  These normalized Frobenius quantities are the
scientific per-case summaries used for medians and percentiles.  The structural
assay and adversarial controls separately use unnormalized operator-norm
maxima; those are worst-case gates and must not be numerically conflated with
the normalized Frobenius summaries.

Small \(\epsilon_S\) constitutes quotient flatness only jointly with the
common-kernel condition: the relevant cross blocks of both paths must also be
small, and \(N\) must be forward invariant under every generator.  Without
that condition, \(P_S(L-R)P_S\) measures only horizontal-block agreement and a
later suffix may reveal the residual.  Quotient flatness does not require
small \(\epsilon_K\).  In the typed hard control, a curved fiber deliberately
sets \(\epsilon_K>0\) while holding semantic operators, states, and readout
fixed.  Its native outputs must be identical to the flat-fiber counterpart.
This demonstrates permitted dormant gauge curvature, not useful ambient
memory or curvature traversed by natural task states.

## Required evaluations

1. **Native behavior:** trained-range accuracy, held-out families, and D4
   depths through 512 using serialized float32 logits and the frozen robust
   margin rule.
2. **Rank certificate:** float64 audit of executed float32 tensors, fixed
   rank-seven threshold, and fail-closed ambiguity handling.
3. **Generator isolation:** worst-generator spectral norms of \(P_SM_gP_N\)
   and \(P_NM_gP_S\), plus the typed \(S/L/K\) cross-block residuals.
4. **Suffix isolation:** centered observation of injected \(L\), \(K\), and
   mixed-\(N\) displacements after suffix lengths
   \(0,1,2,4,8,16,32\).
5. **Relation paths:** balanced derived diamonds and repeated null loops,
   split into semantic, logit-gauge, ambient, and full defects.
6. **Causal specificity:** nonzero \(K\)-only patches must remain behaviorally
   inert; matched-norm \(S\)-patches must produce the registered
   counterfactual continuation.
7. **Gauge covariance:** an outer dense orthogonal conjugation must preserve
   behavior, projector ranks, registered path-defect norms, and intervention
   consequences.  The current assay does not claim to compare the full
   spectrum of the relative holonomy \(R^{-1}L\).
8. **Assay controls:** exact, quotient-curved, cross-block-leaky,
   identity-collapse, random-block, rank-collapse, and coordinate-conjugate
   constructions must receive their registered outcomes.

Natural hard-arm states contain no ambient packet.  Deleting or transplanting
their natural \(K\) component would therefore be an empty intervention.  All
kernel tests inject a registered nonzero displacement and report its norm and
membership; otherwise the condition is `NOT_EVALUATED`.

## Coordinate-free interpretation

For the typed hard arms, the object tracked by Komorebi transport mathematics
is the invariant flag

\[
0\subset K\subset N\subset H
\]


For both the hard construction and the untyped learned quotient, write the
abstract quotient codomain as \(\bar S\cong H/N\), distinct from the embedded
Euclidean complement \(S_h\subset H\).  The associated exact sequence is

\[
0\longrightarrow N\longrightarrow H
\xrightarrow{\Pi}\bar S\longrightarrow0.
\]

Exactness alone is automatic for a surjective rank-seven \(\Pi\).  Its
scientific content here comes from additionally certifying that
\(N=\ker(CD)\), that \(N\) is invariant, and that the descended action is
noncollapsed and behaviorally correct.  The algebraic zero equations and the
exact sequence are covariant under any invertible change of coordinates \(G\),

\[
M_g\mapsto GM_gG^{-1},
\quad
\Pi\mapsto\Pi G^{-1},
\quad
N\mapsto GN,
\]

with \(K\mapsto GK\) in the typed hard case, while the intertwining equation

\[
\Pi M_g=T_g\Pi
\]

is unchanged.  This is covariance of the abstract equations, not of every
Euclidean parameterization or residual magnitude.  The executable gauge assay
is deliberately narrower: it uses \(G\in O(12)\), for which row-orthonormal
observers, Euclidean projectors, principal angles, and the hard
\(W\operatorname{diag}(\cdot)W^\top\) form are preserved.  Extending the
numerical assay to general \(GL(12)\) would require co-transporting the metric
and using metric adjoints, projectors, and norms.  Descended actions, relative
path defects, invariant subspaces, and counterfactual consequences are the
audit objects; individual neurons or frame columns are not.

## Stop rules and claim boundary

The pilot is not run automatically after a successful smoke.  A developmental
screen must first pass execution and assay integrity.  It is stopped if the
learned-intertwiner rank is ambiguous, if any registered control is
misclassified, if kernel interventions lack full eligibility, or if the hard
semantic-flat arm fails its registered absolute geometry, curvature,
deep-execution, loop, or null-retention calibration gates.

A successful block may support:

> Conditional on the rank-seven centered-decoder certificate, a compiled
> seven-dimensional centered-logit quotient with a typed
> one-dimensional logit gauge and four-dimensional invariant ambient fiber is
> sufficient to prevent norm explosion and ambient contamination, while
> permitting nontrivial behaviorally inert vertical holonomy.  Explicit
> intertwining pressure can be tested separately for inducing the same
> quotient in an unrestricted recurrent model.

It does not establish spontaneous Neuralese, useful ambient memory,
architecture-independent emergence, cross-model language, awareness, or
consciousness.
