# Observable learning from finite signals

Komorebi Large Signal Model · Lean 0.9.0 · Komorebi P.

This block closes the five statement mappings P14–P17 and P25. Its dependency path is concrete:

1. Construct the observation map and prove when it closes.
2. Construct the unique fitted map on the sampled span.
3. Construct the orthogonal pseudoinverse and derive its perturbation bound.
4. Prove the obstruction to unrestricted discovery from a finite prefix.
5. Connect the fitted operator to exact and approximate future predictions.

All five statements refer to frozen Foundations 1.0.0. Their source spans and hashes remain in the original proof register. The new files do not alter those spans.

## P14: from a window to a predictive state

`DelayClosure.lean` defines the actual finite observation map

\[
O_hx=(Cx,CLx,\ldots,CL^{h-1}x).
\]

The state space is its range, not the full ambient array space. Its kernel is proved to consist exactly of the vectors whose first h outputs vanish.

The proof first establishes the recurrence

\[
\ker O_{h+1}=\ker C\cap L^{-1}(\ker O_h).
\]

For positive h, the following are equivalent: a range-valued linear transition exists, the kernel of O_h is preserved by L, and the ranks of O_h and O_{h+1} agree. The transition is constructed using quotient factorization. It is not supplied as a field assuming the desired closure equation. Surjectivity onto the actual range proves uniqueness.

The dimension bound is proved through a descending kernel chain. Every strict decrease reduces its dimension. Equality at one stage persists by the displayed recurrence. Therefore a plateau holds by any supplied upper bound d on the hidden dimension. This replaces the manuscript's Cayley–Hamilton argument with an elementary proof of the same conclusion.

The formalization keeps zero-length windows separate. A map into the empty window space always has a trivial transition, but its rank need not equal the rank of the one-output map. Accordingly, the rank/closure equivalence explicitly requires h>0. The proof register already specifies positive delay length. A last-block decoder also needs h>0.

`causal_future_output` links every transition iterate to the actual output at time s+k+h−1 when the initializing window begins at s. It expresses the warm-up convention directly. The initial window is available at time s+h−1, not at s.

Main declarations: `delay_closure_rank_iff`, `dimension_closure`, `transition_unique`, `transition_iterates`, `causal_future_output`.

## P15: the exact meaning of a fitted table

`DataSpan.lean` treats the input and successor columns as linear maps A and B from coefficient space. Their actual sampled span is range A.

A linear ambient fit F with FA=B exists exactly when ker A is contained in ker B. Under that condition, the proof constructs

\[
\operatorname{range}A\longrightarrow Z,
\qquad Aa\longmapsto Ba
\]

through the quotient by ker A. A linear extension gives an ambient fit, and every fit agrees on range A. The fit preserves this span exactly when range B lies inside range A.

The underidentification theorem is also constructive at the mathematical level: if y lies outside a subspace W, a prescribed map on W extends both to F and to another map G with G(y)=F(y)+y. The point y cannot be zero, so these extensions differ. No amount of repeated data entirely inside W distinguishes them.

### The actual Moore–Penrose operator

`Pseudoinverse.lean` constructs the canonical orthogonal inverse, rather than assuming an inverse law. For a finite-dimensional real Hilbert source E, let

\[
Q=P_{(\ker A)^\perp}.
\]

Since Q vanishes on ker A, it factors through range A. Composing that factor with the orthogonal projection onto range A defines J=A†. The proof derives

\[
JA=Q,\qquad AJ=P_{\operatorname{range}A},
\]

and hence all four Penrose conditions: AJA=A, JAJ=J, and symmetry of AJ and JA. These are the real inner-product conditions corresponding to the manuscript's Moore–Penrose notation.

`moore_penrose_fit` then proves BA†A=B from kernel compatibility. Thus the displayed manuscript formula is connected to the fitted map, not replaced by an arbitrary extension.

The construction uses classical quotient and projection machinery over exact real vector spaces. It specifies a mathematical operator determined by the data. It is not executable real arithmetic or a certified numerical SVD implementation.

## P16: conditioning appears in the denominator

`IdentificationBound.lean` works with actual continuous linear maps between finite-dimensional real Hilbert spaces. Their norms are operator norms, corresponding to spectral norms in orthonormal matrix coordinates.

The smallest row singular value is represented variationally:

\[
s=\inf_{v\ne0}\frac{\|A^*v\|}{\|v\|}
 =\inf_{\|v\|=1}\|A^*v\|.
\]

The equality of these two definitions is formalized. This is the variational definition, rather than a separately constructed SVD or an equality to a particular software library's singular-value array. The hypotheses use positive s and perturbation smaller than s. A zero-dimensional output does not acquire a fictitious positive singular value from the empty infimum.

The proof derives

\[
(s-\|E\|)\|v\|\leq\|(A+E)^*v\|.
\]

A positive lower bound makes the adjoint injective. Orthogonal complements then show that A+E is surjective. The pseudoinverse norm estimate is derived using its range in the orthogonal complement of the kernel. If x=(A+E)†y, write $x=(A+E)^*v$ and use

\[
\|x\|^2=\langle v,y\rangle
 \leq\|v\|\,\|y\|.
\]

Combining this identity with the adjoint lower bound yields

\[
\|(A+E)^\dagger\|\leq(s-\|E\|)^{-1}.
\]

For exact successor table BA+R and observed successor perturbation F, the fitted operator is

\[
\widehat B=(BA+R+F)(A+E)^\dagger.
\]

The proof establishes the literal operator identity

\[
\widehat B-B=(R+F-BE)(A+E)^\dagger
\]

and therefore

\[
\|\widehat B-B\|\leq
\frac{\|R\|+\|F\|+\|B\|\|E\|}{s-\|E\|}.
\]

No statistical model is used. The state space and its coordinates remain fixed. Learning a new basis would require additional subspace-error analysis.

## P17: a finite prefix leaves room for a later response

`FinitePrefix.lean` defines a rational shift on Fin n. Its k-th power is evaluated exactly and its n-th power is zero. For every horizon T, choose dimension T+2 and initialize the final coordinate. Observing the first coordinate gives zero at times 0 through T and one at T+1.

The comparison system has zero transition and zero initial state on the same finite rational state space. Both are nilpotent. The final theorem quantifies over every natural T, including T=0. This is a universal proof, not a finite numerical sweep.

This obstruction explains the role of the dimension, model-class, and coverage assumptions in the other results. It does not negate those conditional learning guarantees.

## P25: close the observable learning argument

`LearnedRealization.lean` defines the learned map using only the two data tables. If the input table is onto the declared predictive state space and its successors are true successors, the learned map equals the true transition. This equality gives every future state by induction.

`delay_table_identifies` applies the fit argument to the actual delay range from P14. `causal_future_output` supplies its current-output decoder. The earlier realization laws are used for lossless chart recoding, and `learned_packet_output` proves that complete packet synthesis preserves every decoded prediction. Coherent chart transport remains governed by the unchanged P1–P4 results.

The noisy branch uses the actual fitted operator from P16. `fitted_rollout` derives a local error budget qM_t, where q is the operator-error bound and M_t bounds the true state norm. It inserts that budget into P18's suffix-product envelope. The predicted trajectory is recursively generated by the fitted operator, rather than repeatedly reset to true states.

The contraction theorem gives the all-time radius

\[
\max\left(\|x_0-\widehat x_0\|,
\frac{\delta}{1-\|\widehat B\|}\right)
\]

when the common fitted gain is below one and the true-history defect is bounded by δ. The decoder bound adds its actual operator norm. These remain explicit hypotheses. The theorem does not infer boundedness, contraction, or coverage merely because a fit exists.

## Examples, controls, and scope

Nine new example theorems include the universal delayed-output witness, the zero-window boundary, two distinct operators fitting a closed but incomplete sampled plane, inconsistent zero inputs, exact scalar learning, a sharp scalar perturbation calculation, and collapse at the excluded perturbation boundary. The scalar sharpness calculation is illustrative algebra, not a separate formal identification of its rowGain with a numerical SVD output.

Six new deliberately false proof files test finite-prefix overreach, missing span coverage, inconsistent fitting, zero-delay output recovery, rank survival at equality, and omission of the conditioning denominator. Their release verification must reject mathematical proof attempts. Missing imports and timeouts do not count as valid rejections.

The block adds seven modules and 64 named theorems, including nine example theorems. It does not add a trained model, a benchmark result, an empirical confidence experiment, or verified production software.
