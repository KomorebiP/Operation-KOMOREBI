# Integrated result: Stable Quotient v0.2.0

## Bottom line

The original depth failure was not one phenomenon. Raw hidden magnitude was an exact projective gauge; hidden direction carried the causal semantics. Removing the gauge during training changed the result from a bounded depth-12 mechanism into a recurrent operator workspace that remained exact through depth 64 and highly accurate through depth 256 on structured held-out families.

Komorebi anchor transport also supplied an exact, bounded realization of the task. Thus the engineering problem is solved in this finite system. The remaining scientific problem is whether a learned encoder can discover path-flat projective dynamics under weaker structural pressure.

## Principal learned result

Both models below have 4,224 parameters. Training used terminal answers only for randomly conjugated D4 sequences of lengths 1–4.

| Two-seed mean accuracy | L4 | L12 | L64 | L128 | L256 |
|---|---:|---:|---:|---:|---:|
| Raw parent | 0.9990 | 0.8403 | 0.3867 | 0.2869 | 0.0000* |
| Projective terminal-only | **1.0000** | **1.0000** | **1.0000** | **0.9924** | **0.8477** |

`*` Raw float32 overflow counts as incorrect at depth 256. Normalized replay stays finite but remains directionally inaccurate, so the clean conclusion does not depend solely on overflow.

| Projective model, two-seed mean | L64 | L128 | L256 |
|---|---:|---:|---:|
| D4 | **1.0000** | **0.9924** | **0.8477** |
| Held-out C8 | **1.0000** | **0.9917** | **0.7351** |
| Held-out mixed-cycle | **1.0000** | **0.9956** | **0.8665** |
| Arbitrary permutation pair | 0.2629 | 0.2485 | 0.2480 |

The model generalized strongly across the structured families, but not across unrestricted permutation pairs. This is algebra-family reuse, not universal table execution.

## Causal and transport evidence

At depth 64:

| Intervention | Intended edit | Matched random control |
|---|---:|---:|
| Donor hidden-state transplantation | **1.0000** | at most 0.0781 |
| Internal operator replacement | **1.0000** | at most 0.0654 |

An affine map fitted only on short D4 trajectories transported source states into an independently trained target model with:

| Family, length 8 | Target native | Transported | Random map |
|---|---:|---:|---:|
| D4 | 1.0000 | **1.0000** | 0.0039 |
| C8 | 1.0000 | **1.0000** | 0.0010 |
| Mixed-cycle | 1.0000 | **1.0000** | 0.0039 |
| Arbitrary permutation | 0.5879 | **0.5869** | 0.0576 |

Transport preserved both the target model's strengths and its arbitrary-operator limitation.

## Exact Komorebi closure

Let \(B\) contain the learned state embeddings as columns and let \(P\) be the exposed permutation action. Then

\[
M_P=B P B^{-1},
\qquad
M_P^{\mathsf T}G M_P=G,
\qquad
G=B^{-\mathsf T}B^{-1}.
\]

This intertwiner maps every learned state anchor exactly to the anchor selected by the table. In the canonical semantic chart, \(B=I\), \(M_P=P\), and \(G=I\).

The canonical closed arm achieved:

- 1.0000 accuracy for every tested depth through 256 and every tested family
- 1.0000 null-cycle accuracy
- 1.0000 deep state and operator replacement
- metric condition number 1
- zero closure and isometry residual in the canonical chart
- 1.0000 cross-seed continuation, with maximum numerical intertwining residual \(3.56\times10^{-6}\)

This is a constructive positive control. It establishes that stable coordinate-independent execution exists and identifies the learned operator encoder—not the task or state basis—as the remaining source of drift.

## The unresolved clue: projective holonomy

The terminal-only projective models kept all states finite and correctly survived table-verified null-cycle insertions at least 99.41% of the time. Nevertheless, after 16 repeated cycles:

- the worst median angle from the no-cycle ray was 0.4712 radians
- the worst observed angle was 1.1055 radians

The ambient learned matrices also retained substantial scale-free anchor and conformal-isometry defects. Correct answers therefore occupy robust regions of projective state space even while the internal route is not flat. Continued looping eventually crosses a decision boundary.

The immediate target is not another norm penalty. It is to reduce continuation-relevant curvature:

\[
F_p([h])\approx F_q([h])
\quad\text{whenever}\quad
p\text{ and }q\text{ implement the same visible action}.
\]

Anonymous intertwining or composition consistency can test this next, but it is explicit structural supervision and must be compared separately with terminal-only training.

## Scientific status

The v0.2 pilots are developmental, use two seeds, and have thresholds frozen only after an initial screen. They establish a mechanism and an engineering construction. They do not establish spontaneous Neuralese, zero-holonomy learned dynamics, universal operator discovery, or the same mechanism in large language models.

The strongest honest statement is:

> In this finite, randomly re-coordinatized operator task, per-step projective gauge fixing during terminal-only training converts radial explosion into bounded, causally operative recurrent computation and greatly extends compositional depth. Exact Komorebi anchor transport supplies a coordinate-independent stable solution, while residual projective holonomy and unrestricted-operator generalization remain open.
