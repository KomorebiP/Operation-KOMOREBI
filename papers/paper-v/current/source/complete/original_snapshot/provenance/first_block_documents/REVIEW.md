# Paper V: first formalization block and manuscript corrections

**Author:** Komorebi P.  
**Working release:** 0.1.0, first block  
**Status:** manuscript baseline recovered; proof candidates drafted; new exact finite tests passed; Lean build not run.

## Baseline and evidence

The starting manuscript is **Projector_Resolved_Seed_Calculus_V_Adaptive_Tree_Resolved.pdf**, 31 pages. Its SHA-256 is:

```text
9b1cbe3c771f90fae651d13eeb41a05804953d9f923bc1160a3e1b385b571e85
```

This matches the Paper V PDF entry in the retrieved `Projector_Seed_Calculus_Two_Finite_Conjectures_Resolved_SHA256SUMS.txt`. The earlier 28-page edition is not the development baseline. The recovered edition contains 36 numbered records, of which 20 are theorems, corollaries, or propositions. Numerical certificates, conjectures, classical inputs, definitions, remarks, and boundary statements are not promoted to Lean theorem targets.

The 31-page PDF is preserved unchanged. Its original editable LaTeX and companion source archive were not recovered by the performed Library searches. Their filenames occur in the checksum manifest, but a filename is not the file itself. This package therefore supplies a separate correction supplement, not a silently reconstructed or modified full manuscript. It does not claim that no other Paper V archive or formalization exists.

The manuscript reports 18 figures and 33 companion tests. Those 33 tests were not rerun. The tests described below are newly written finite reference models.

## 1. Corrections that affect formal statements

### 1.1 Theorem 11.3, page 19: the singleton gap

The original statement defines the gap by taking the minimum of the cost differences over competing prunings. A tree consisting only of its root has exactly one complete pruning. In that case the competing set is empty, so the displayed minimum is not a real number.

**Replacement.** Every real-valued cost on the nonempty finite set of complete prunings attains a minimum. If there is only one pruning, its selection is unchanged by every modification of the objective. Otherwise, if the minimizer is unique, the finite nonempty competitor set has a strictly positive minimum gap. The usual half-gap perturbation theorem then applies.

For a uniform perturbation bound `epsilon`, the condition is `2 * epsilon < gamma`. Equality is not enough. The two objectives `(0, 2)` and `(1, 1)` give an exact boundary example: the original gap is two, the uniform change is one, and uniqueness is lost.

The new finite reference model represents the no-competitor case by a distinct `None` gap rather than by zero, an arbitrary large finite constant, or an unevaluated empty minimum. It returns the same root-only cut for all real-valued costs.

### 1.2 Theorem 11.4, pages 19–20: ties and computation cost

The printed rule describes what happens when either branch is strictly smaller but does not specify equal costs. Either branch remains optimal, but a deterministic implementation needs a convention.

**Replacement.** Stop at a node when its local cost is less than or equal to the sum of the child optima. Refine otherwise. The new implementation uses this rule.

The `O(|T|)` claim counts scalar additions and comparisons after local costs are available. It is not a claim that computing representation or leakage costs is free, nor that exact rational arithmetic has constant bit complexity. The new implementation uses a value/decision pass and a separate selected-cut pass, rather than repeatedly concatenating complete cuts at every ancestor.

### 1.3 Corollary 11.5, page 20: simultaneous probability event

The deterministic envelope is sound. For its probabilistic interpretation, the local error bounds must all hold on one event with probability at least `1-delta`. Individual bounds of probability `1-delta` at every node do not automatically give that joint probability.

**Replacement.** State a simultaneous event for all nodes. On that event, the pruning-cost envelope holds. A fixed baseline gap greater than twice that envelope preserves the selected optimum. If only separate failure probabilities are known, first combine them, for example with a union bound, before claiming a global probability.

### 1.4 Theorem 4.1, page 8: channel delay is not original-sample delay

The variable in the polyphase matrix is the channel transform variable. Thus `R(z)E(z)=z^(-d) I_N` describes a delay of `d` channel indices, equivalent to a delay of `N*d` original samples.

For an original-sample delay `D=qN+t`, with `0 <= t < N`, output channel `r` comes from channel `(r-t) mod N` and is delayed by `q + 1_{r<t}` channel indices. A one-original-sample delay with two channels has matrix

```text
[ 0   z^(-1) ]
[ 1      0   ]
```

not `z^(-1) I_2`. The exact test suite checks this distinction, including negative delays and negative signal addresses. The repair preserves the printed scalar criterion by explicitly naming its delay unit, and supplies the general permutation-and-delay matrix when arbitrary sample delays are intended.

### 1.5 Theorem 13.2 and Corollary 13.3, page 23: poles of the Smith action

The rational expression has poles. On the boundary, the half-turn takes zero normalized impedance to infinite impedance. It is not an everywhere-defined map from finite complex numbers to finite complex numbers. Ordinary totalized division in Lean must not silently stand in for a point at infinity.

Two valid formulations are available:

1. Use projective coordinates `[u:v]` on the complex projective line. The matrix
   `M(w) = [[1+w, 1-w], [1-w, 1+w]]` has determinant `4w`, and `M(u)M(v)=2M(uv)`. For nonzero phases this defines the required projective action. The half-turn swaps `[u:v]` and `[v:u]`, including zero and infinity.
2. Work on the open passive half-plane `Re(z)>0`, where the corresponding reflection coefficient is inside the open disk. Rotations preserve that disk, so all the finite formulas are well-defined. Boundary points require a separate projective treatment or explicit denominator conditions.

The finite closed passive half-plane maps to the closed reflection disk with the point `Gamma=1` omitted. That missing point represents infinite impedance. The supplement states the projective version and a safe finite-chart interpretation.

### 1.6 Analytic and measure-theoretic hypotheses

For Theorem 3.1, the FIR time-domain identity is valid without taking an analytic z-transform. Its transform restatement should specify finite-support Laurent polynomials, an appropriate formal representation, or a common convergence domain. Membership of a general signal in `l2` alone does not license an arbitrary pointwise bilateral z-transform.

For Theorem 7.1, explicitly take measurable masks and require the relevant indicator functions to belong to the stated `Lp` spaces. Finite measures of the original mask and symmetric difference are sufficient for the finite-p formula. Distinguish the ordinary pointwise supremum from an essential supremum. The printed nonempty-set bound is still an upper bound for the essential supremum, but it is not the sharp null-set formulation.

These are requirements for the future formal statements, not reasons to discard the underlying algebraic identities.

## 2. Editorial corrections

- Page 28, implementation table: `visuals.py` still says “the sixteen figure pairs used in the paper,” while the current abstract and figure list contain eighteen. Synchronize the table with the current release.
- Page 30, Appendix A.3, item 3: change “Harmically fill” to “Harmonically fill.”
- Keep the newly resolved finite adaptive-tree results distinct from the still-open infinite-tree and universal statistical selection questions.

This is an initial formalization-oriented review, not a claim that every line of the manuscript has received a final publication proofread.

## 3. What was written in Lean

Five source modules contain **29 theorem declarations**, all classified as **uncompiled candidates**:

| Module | Candidate scope | Not included |
|---|---|---|
| `Packets.lean` | Partition idempotence, annihilation, resolution, fiber refinement, generic address-equivalence inverse laws, literal integer residue specializations | Concrete quotient/remainder equivalence, Hilbert-space norms and bounded operators |
| `KnownEdge.lean` | Exact error cancellation, finite sums of exact edge packets, norm identities, generic perturbed-error bound | Edge discovery; measurable-mask `Lp` perturbation theorem |
| `Lifting.lean` | Both inverse laws, determinant one, an equivalence and pointwise coordinate roundtrip | Normalized Haar and infinite-dimensional energy |
| `FiniteSelection.lean` | Finite minimum, positive competitor gap, perturbation stability, singleton selection | Construction of the general set of complete tree prunings |
| `BinaryAdaptive.lean` | Recursive binary-cut synthesis under local conservation, globally optimal stop-on-tie selector, binary perturbation envelope | Arbitrary-arity antichain/path correspondence; formal operation count; probability theory |

No candidate declaration is counted as an accepted proof. The ledger identifies which paper clauses each module addresses and what remains. In particular, proving a generic inverse identity does not automatically formalize the concrete signal-space realization, and a binary-tree result does not automatically formalize an arbitrary-branching-tree statement.

The Lean project uses the same declared toolchain and Mathlib revision as the attached Paper IV package. This preserves intended dependency compatibility only. It does not inherit Paper IV's recorded build evidence.

## 4. What was actually run

The new Python suite passed **12 tests with 25,825 counted mathematical assertions**, using exact `fractions.Fraction` arithmetic. It also passed six expected-exception checks for invalid input, which are not included in the 25,825 count.

The tests include signed integer addresses, FIR transfer with negative taps, distinct sample and channel delays, lifting inverses, finite mask-error bounds, singleton trees, unary/binary/ternary trees, ties, negative costs, complete-cut synthesis, local envelopes, and projective Smith-matrix identities. Dynamic programming was compared with exhaustive enumeration for 300 cost assignments across six fixed tree shapes, including a depth-four binary tree with 677 prunings. This is a finite regression suite, not a universal proof or a randomized test of the Lean code itself.

The count `458330` for a complete binary tree of depth five was independently recovered from `c_0=1`, `c_(d+1)=1+c_d^2`. This run did **not** enumerate all 458330 depth-five objectives and does **not** reproduce the manuscript's recorded optimum, gap, or floating-point residuals.

The strict-gap boundary example and zero-impedance pole are executable regression cases. The original numerical results remain attributed to the source manuscript, not to this run.

## 5. What failed or could not be completed

`lean` and `lake` are absent from the runtime. The attempted official Lean binary fetch could not resolve `github.com` from the container. No fresh elaboration, compilation, theorem-kind audit, or axiom audit ran. No new kernel-checked Paper V result is reported.

`verification/verify.py` is fail-closed. Without `lake`, its full mode returns a nonzero exit status and records `BLOCKED_NO_LAKE`, even though its independent Python tests pass. Static-only mode explicitly records that formal verification was not requested. The generated `KernelAudit.lean` is a harness to run later, not a saved success transcript.

The verification harness itself has only been exercised on its local/static and missing-tool paths here. Its positive Lean path is not claimed to have been tested.

## 6. Next proof sequence

First compile the 29 source candidates and correct any elaboration or API errors. Then construct the concrete integer polyphase equivalence and finite-support convolution reindexing. Extend the binary-cut theorems to arbitrary finite branching and prove their equivalence with the manuscript's complete-antichain definition. Finally connect the Hilbert-space energy, measure-theoretic masks, formal power-series multiplication, and projective Smith action.

The two manuscript conjectures, 7.2 and 15.1, remain conjectures. A complete formalization of the paper's proved contract does not require relabeling those conjectures as proved.
