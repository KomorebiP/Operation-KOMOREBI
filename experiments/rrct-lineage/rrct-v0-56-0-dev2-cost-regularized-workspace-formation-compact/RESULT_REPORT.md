# RRCT v0.56 Cost-Regularized Workspace Formation — Result Report

## Scientific result

`V056_CONFIRMATION_ENDPOINTS_MET`

All **23 of 23** predeclared endpoints passed on the canonical dev2 confirmation.

## Experimental population

| Cohort | Seeds | Price points | Cases per cell | Total cases |
|---|---:|---:|---:|---:|
| Primary confirmation | 16 | 1 | 20,000 | 320,000 |
| Formation-cost edge | 6 | 13 | 10,000 | 780,000 |
| Naïve expected-loss control | 6 | 1 | 15,000 | 90,000 |
| **Total** | — | — | — | **1,190,000** |

The primary and edge seed namespaces were generated through SHA-256 expansion without executing candidate outcomes. The source, tests, protocol, thresholds, seed receipt, route library, and adjudicator were sealed before the canonical confirmation.

## Primary architecture-selection matrix

Rows are task families. Columns are selected routes.

| Task | local | flat | 01\|23 | 02\|13 | 03\|12 | full |
|---|---:|---:|---:|---:|---:|---:|
| local | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| flat | 0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| pair_01_23 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 |
| pair_02_13 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | 0.000000 |
| pair_03_12 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 0.000000 |
| overlap | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 |

Every task was routed to its predeclared minimal sufficient architecture with probability 1.0 in the primary cohort.

## Causal and dynamic controls

### Cue shuffle

Shuffling task cues reduced route accuracy from **1.000000** to **0.166941**. This establishes that the anonymous dependency cue is causally used rather than ignored.

### Route patch

For episodes in which an incompatible route changes the computed action, forcing that route changed the terminal outcome in **0.989070** of probes. Route selection therefore has downstream causal consequences.

### Graph switching

When task demand changed between episodes, the router switched to the correct graph with accuracy **1.000000**.

### Dissolution

When the following episode required only local processing, all shared routes were closed with accuracy **1.000000**.

This is task-conditioned closure between independent episodes. It is not yet a recurrent teardown process inside one continuous agent history.

## Cost-edge table

| \(\lambda\) | Task accuracy | Minimal-route accuracy | Selected cost | Oracle cost | Excess cost |
|---:|---:|---:|---:|---:|---:|
| 0.00 | 1.000000 | 0.460650 | 3.135250 | 2.085108 | 1.050142 |
| 0.01 | 1.000000 | 0.967117 | 2.136483 | 2.085108 | 0.051375 |
| 0.03 | 1.000000 | 0.999867 | 2.085308 | 2.085108 | 0.000200 |
| 0.05 | 1.000000 | 1.000000 | 2.085108 | 2.085108 | 0.000000 |
| 0.08 | 1.000000 | 1.000000 | 2.085108 | 2.085108 | 0.000000 |
| 0.12 | 0.999983 | 0.999983 | 2.085067 | 2.085108 | -0.000042 |
| 0.16 | 0.999983 | 0.999983 | 2.085067 | 2.085108 | -0.000042 |
| 0.20 | 0.999967 | 0.999967 | 2.085025 | 2.085108 | -0.000083 |
| 0.22 | 0.995638 | 0.995450 | 2.067008 | 2.085108 | -0.018100 |
| 0.24 | 0.886429 | 0.881417 | 1.610925 | 2.085108 | -0.474183 |
| 0.26 | 0.839708 | 0.832467 | 1.415325 | 2.085108 | -0.669783 |
| 0.30 | 0.839092 | 0.831817 | 1.413725 | 2.085108 | -0.671383 |
| 0.40 | 0.415825 | 0.388317 | 0.305000 | 2.085108 | -1.780108 |

## Break-even ordering

For a sufficient route \(r\) and cheaper alternative \(s\), the formation price at which the two are tied is:

\[
\lambda^*_{r\rightarrow s}
=
\frac{L_s-L_r}{C_r-C_s}.
\]

The empirical break-even values were:

| Task structure | Estimated break-even price |
|---|---:|
| flat | 0.992669 |
| pair 01\|23 | 0.398455 |
| pair 02\|13 | 0.398419 |
| pair 03\|12 | 0.398726 |
| overlap/full | 0.249756 |

Because the overlap route has the highest cost relative to its advantage, it becomes uneconomical first. The observed first failure at \(\lambda=0.24\) is within approximately 0.01 of its computed 0.2498 break-even value. The pair hierarchies remain stable until approximately \(\lambda=0.40\).

## Formation regimes

### Regime I: overformation

At \(\lambda=0\), terminal accuracy is perfect but the architecture is unnecessarily deep. Task loss alone cannot distinguish a minimal route from a richer route that also solves the task.

### Regime II: selective formation

Across \(0.03\le\lambda\le0.22\), the router selects no workspace, flat workspace, one matching pair hierarchy, or full overlap according to task demand.

### Regime III: ordered underformation

At \(\lambda=0.24\), the expensive overlap workspace disappears first. Near \(\lambda=0.40\), the pair hierarchies also become uneconomical. This is an ordered collapse predicted by loss-cost break-even ratios, not a generic failure of all computation.

## Interpretation

The experiment supports a bounded economic principle of workspace formation:

\[
\boxed{\text{form the least expensive architecture whose terminal loss is acceptable}}
\]

A cognitive system with no integration cost tends to over-integrate. A system with moderate cost pressure differentiates task-specific workspaces. A system with excessive integration cost under-integrates.

This may be relevant to theories in which biological or artificial cognition forms temporary coalitions only when the expected improvement from global coordination exceeds communication and maintenance costs. The current experiment is a mathematical prototype of that principle, not direct neuroscience evidence.

## Negative and limiting controls

1. **Flat universality remains possible.** The supplied full route can solve all task families. The formation objective selects simpler routes because they are cheaper, not because deeper routes are incapable.
2. **Counterfactual access is unusually strong.** Training evaluates every candidate route, whereas biological or online agents may observe only the route they actually execute.
3. **Task demand is public.** The router receives an anonymous projection of a supplied dependency signature. It does not infer dependency structure from raw sensory histories.
4. **Candidate computations are supplied.** The system selects among graphs but does not learn the route internals end to end.
5. **The candidate set is closed.** It cannot invent a seventh architecture.
6. **Dissolution is episodic.** No persistent pair memory or teardown dynamics are modeled.
7. **No awareness inference follows.** Architecture selection is a control capability, not evidence of experience.
