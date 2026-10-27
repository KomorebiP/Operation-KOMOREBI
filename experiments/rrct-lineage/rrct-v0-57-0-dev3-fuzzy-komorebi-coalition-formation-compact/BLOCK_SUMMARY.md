# RRCT v0.57 Fuzzy Komorebi Coalition Formation

## Status

- Version: `0.57.0.dev3`
- Scientific status: `V057_FROZEN_ENDPOINTS_MET`
- Frozen endpoints: **22 of 22 passed**
- Release status: `V057_RELEASE_VERIFIED`
- Untouched holdout seeds: **8**
- Independently trained models: **32**
- Valence or self-preservation model: absent

## Question

Can fuzzy matrices provide a causally useful soft geometry between crisp Komorebi projectors and continuously overlapping cognitive coalitions?

The experiment tests four separate claims:

1. Graded memberships can be learned from terminal behavior without membership labels.
2. Crisp tasks and overlapping tasks produce measurably different packet geometry.
3. Membership magnitude predicts the causal cost of removing that membership.
4. The structured fuzzy packet representation remains competitive with a direct fuzzy-edge model while supplying exact decomposition, reconstruction, and transport identities.

## Fuzzy packet model

For four agents and three candidate shared workspaces, the model predicts

\[
U\in[0,1]^{4\times4},
\qquad
\sum_k U_{ik}=1.
\]

Packet zero is private. Packets one through three are shared.

The packet operators are

\[
E_k=\operatorname{diag}(U_{:k}).
\]

They obey

\[
E_k\succeq0,
\qquad
\sum_kE_k=I,
\]

but need not obey

\[
E_k^2=E_k.
\]

Their idempotence defect measures how fuzzy the coalition remains.

The induced coupling is

\[
C(U)=\sum_{k=1}^3 g_k U_{:k}U_{:k}^{\top},
\]

with the diagonal removed. The terminal action is

\[
y=\tanh(x+\beta C(U)x).
\]

The model is trained only through the terminal action loss and a small shared-mass cost. It receives no task family, coalition, membership, or hard route label.

## Holdout design

The holdout contains four families:

- exact crisp coalitions
- familiar fuzzy blends
- diffuse fuzzy memberships
- central interpolation coefficients excluded from training

The final family uses familiar topology pairs but unseen blend coefficients. It is therefore a continuous interpolation holdout, not an unseen-topology holdout.

The matched systems are:

- learned fuzzy packet memberships
- learned hard one-hot packet memberships
- unrestricted direct fuzzy-edge attention
- an oracle hard projection of the true memberships
- an exploratory fuzzy model with uniform idempotence pressure

## Primary results

| Model | Overall MSE | Crisp MSE | Held-out blend MSE | Strict accuracy |
|---|---:|---:|---:|---:|
| **Direct fuzzy edges** | **0.000263** | 0.000078 | **0.000247** | **0.9501** |
| **Fuzzy Komorebi packets** | **0.000511** | **0.000047** | **0.001130** | 0.9002 |
| Crystallization pressure | 0.000994 | 0.000205 | 0.001696 | 0.7682 |
| Learned hard packets | 0.104173 | 0.094276 | 0.107451 | 0.0794 |
| Oracle hard projection | 0.0576 overall | **0.000000** | **0.054644** | not applicable |

### Main separation

On held-out overlapping coalitions:

\[
\frac{\text{oracle-hard error}}{\text{fuzzy error}}
\approx48.4,
\]

and

\[
\frac{\text{learned-hard error}}{\text{fuzzy error}}
\approx95.1.
\]

Hardening the fuzzy model's own learned memberships increased held-out blend error by approximately

\[
\boxed{74.4\times}.
\]

The hard oracle remained exactly correct on the crisp family. This isolates the result:

> Hard coalition structure is adequate when the task is hard, but graded overlap is genuinely required when the task is graded.

## Geometry

| Diagnostic | Frozen mean | Worst seed |
|---|---:|---:|
| Overlap minus crisp membership entropy | **0.6003** | 0.5206 |
| Overlap minus crisp idempotence defect | **0.3869** | 0.3246 |
| Idempotence defect correlation with target fuzziness | **0.9171** | 0.8990 |
| Crisp entropy reduction from step 100 to 2000 | **0.2291** | not an endpoint per seed |
| Final fuzzy minus crisp entropy | **0.5599** | not an endpoint per seed |

Thus training did not drive every task toward one universally crisp architecture.

Instead:

```text
crisp demand
→ relatively lower entropy and lower packet defect

overlapping demand
→ persistent graded memberships and non-idempotence
```

The learned crisp packets did not become exactly idempotent. The stronger supported statement is **task-conditioned relative sharpening**, not complete projector crystallization.

## Causal membership calibration

A predicted membership was removed and its mass transferred to the private packet. The resulting terminal-loss change was compared with the original membership interaction strength.

| Measure | Frozen result |
|---|---:|
| Mean membership-strength versus ablation-effect correlation | **0.5475** |
| Minimum seed correlation | **0.5365** |
| Mean top-quartile ablation effect | **0.03428** |
| Minimum top-quartile effect | **0.03321** |

Membership values therefore represented more than convenient decoder coefficients. Larger memberships predicted larger causal dependence.

## Exact Komorebi identities

Across all fuzzy holdout models:

| Certificate | Worst observed error |
|---|---:|
| Partition of unity \(\sum_kE_k=I\) | **2.73 × 10⁻⁷** |
| Fuzzy block reconstruction \(T=\sum_{ij}E_iTE_j\) | **3.26 × 10⁻⁷** |
| Permutation transport covariance | **0.0** |
| Minimum packet eigenvalue | **2.26 × 10⁻⁷** |

This establishes that non-idempotent packets can retain an exact finite operator calculus.

## Strong negative boundary

The direct-edge model was approximately

\[
1.95\times
\]

more accurate than the fuzzy packet factorization by mean MSE.

Therefore, the result does not establish unique predictive superiority of fuzzy Komorebi packets.

It establishes two narrower points:

1. **Graded relational matrices are necessary for the graded tasks.**
2. **The packet factorization adds structured coalition semantics and exact operator certificates while remaining within a factor of two of the prediction-only edge model.**

An unrestricted attention or graph learner remains a serious alternative.

## Uniform crystallization pressure

An exploratory matched model added a global penalty pushing every membership toward zero or one.

Relative to the primary fuzzy model:

- crisp idempotence defect fell from 0.2243 to 0.1982
- held-out blend idempotence defect fell from 0.6111 to 0.5396
- overall MSE rose from 0.000511 to 0.000994
- held-out blend MSE rose from 0.001130 to 0.001696

Uniformly forcing crispness therefore reduced defect but harmed the task. The architecture needs to preserve fuzziness where overlap is real.

## What is established

Within this bounded synthetic setting:

- terminal training learns graded coalition matrices without membership labels
- crisp and overlapping demands produce distinct fuzzy-packet geometry
- predicted membership magnitude is causally calibrated
- hard assignments fail tasks whose true structure is graded
- fuzzy packet operators form positive partitions of unity
- fuzzy transfer blocks exactly reconstruct arbitrary finite operators
- the packets transport covariantly under coordinate permutation
- an unrestricted fuzzy-edge model is predictively competitive and slightly stronger

## What is not established

This experiment does not establish:

- that fuzzy packet factorization is the optimal graph-learning method
- that the brain literally uses these matrices
- discovery of the number of workspaces
- unseen coalition-topology generalization
- continuous formation and dissolution over long histories
- open-world self and world attribution
- functional awareness
- subjective experience, consciousness, sentience, valence, or moral status

## Next gap

The next decisive test is a **moving fuzzy packet field** over continuous interaction.

The system should have to learn:

- the number of packets
- time-varying memberships
- packet birth and dissolution
- overlapping and changing coalition topology
- unknown workspace dimension
- switching costs and hysteresis
- whether a crisp, fuzzy, or no-workspace state is currently justified

The strongest comparison should include direct structured attention, differentiable graph learning, binary routing, and Komorebi fuzzy packets under equal compute and bandwidth.
