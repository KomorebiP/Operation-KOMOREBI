# Lean Block 04 — mathematical proof guide

**Machine-Native Reasoning · Reviewed Core 0.2 · Cumulative formal companion 0.4.0**

The source book is unchanged. New result-level coverage is Core **3.8** and **5.6**, bringing the cumulative total to eleven of 27. The finite probability definitions reuse `Instrument.mass`, `push`, `applyKernel`, `IsDist`, `normalize`, and `Law`. The common policy is the inherited `Instrument.Policy`, whose input is a list of observed action/report pairs.

## 1. One convention for total variation

`Variation.tv p q` is literally

\[
\frac12\sum_x|p(x)-q(x)|.
\]

All later estimates use that convention. `tv_push_le` proves contraction when coordinates are aggregated. `kernel_contraction` proves contraction under a common normalized nonnegative kernel. Neither is assumed as an axiom or imported as an unproved external claim.

For heterogeneous fine and coarse spaces, `push_kernel_step` shows that a uniform error between the aggregated fine kernel columns and the coarse columns gives

\[
\operatorname{TV}(C'Kp,Lq)
\leq \operatorname{TV}(Cp,q)+\varepsilon.
\]

The proof first aggregates the exact fine mixture, replaces its rows with the approximate rows, and then propagates the difference between initial aggregate and approximate beliefs through the common coarse kernel. The finite triangle inequality and column normalization supply every step. This avoids assuming the projected fine state is itself Markov.

## 2. A real full-history object

`ApproximateHistory.Path X A O H` stores the initial state and H chronological action/report/successor triples. `law` is an actual recursively constructed probability law: at each step it multiplies the previous history mass by the policy's action probability and the corresponding instrument entry. `law_succ` establishes the literal product formula, and `law_dist` proves normalization at every horizon.

`observed` removes all state coordinates before the policy is called. `project` keeps all state positions but applies the fine-to-coarse map to each. The identity `project_observed` makes the common-policy information boundary explicit.

The row discrepancy is over the **joint report/next-coarse-state law**, not a report marginal, state marginal, or isolated likelihood entry. `stepRow_error` mixes those bounds using the common action probabilities. `pathKernel_error` adds the same recorded prefix without increasing the error. Applying `push_kernel_step` inductively gives

\[
 d_H=\min\left(1,\delta+\sum_{t=0}^{H-1}\varepsilon_t\right).
\]

The cap one is justified by the proved normalization of both actual path laws. Time-dependent instruments are permitted, but at each time the same observation-only policy is used on both sides. The row assumptions are stated for all represented actions and fine states, not estimated from sampled histories.

**Main endpoints:** `whole_history_bound`, `observed_history_bound`.

## 3. Why the conditioning denominator is a maximum

For two distributions P,Q and one common event E, let u,v be the restrictions and let p,q be their masses. Equal total mass implies that the difference on the complement of E has signed mass q-p. Its absolute sum is at least |p-q|. Therefore

\[
 \|u-v\|_1+|p-q|\leq 2\operatorname{TV}(P,Q).
\]

Adding and subtracting v/p in u/p-v/q gives a normalization estimate with denominator p. Swapping P,Q gives the analogous estimate with denominator q. The stronger of the two uses max(p,q). `condition_bound` proves precisely

\[
\operatorname{TV}(P(\cdot\mid E),Q(\cdot\mid E))
\leq\min\left(1,\frac{\operatorname{TV}(P,Q)}{\max(p,q)}\right).
\]

Both masses must be strictly positive. `conditional_output_bound` then projects to any requested output. The full-history theorem uses this lemma for the same event in the same constructed history laws, and projects to the final coarse state.

The event-probability inequality is also sharp:

\[
 |P(E)-Q(E)|\leq\operatorname{TV}(P,Q).
\]

Consequently, a mass strictly above d_H on either side forces both masses positive. Equality does not suffice. No theorem calls an algebraic normalization at zero a posterior.

**Main endpoints:** `restricted_discrepancy`, `condition_bound`, `conditional_output_bound`, `conditional_final_bound`, `history_event_positive`.

## 4. A changed policy needs a uniform fixed-policy premise

For each fixed policy i, use its own actual pair of path laws P_i,Q_i and the **same** loss function f_i on those paths. If 0 <= f_i <= B, `expectation_bound` proves

\[
 |J_i-\widetilde J_i|\leq B\operatorname{TV}(P_i,Q_i).
\]

Assume this distance is at most d for every policy in one common finite catalogue. Let c minimize approximate risk and let b minimize true risk. Then

\[
 J_c\leq\widetilde J_c+Bd
 \leq\widetilde J_b+Bd
 \leq J_b+2Bd.
\]

The range [0,B] also bounds regret by B. `uniform_policy_regret` obtains min(B,2Bd). The same proof compares the chosen policy to any catalogue member, so specializing to a true minimizer gives the source statement. `minimizing_policies_exist` uses the previously checked finite-minimum construction to establish that both minimizers really exist.

`history_policy_error` and `history_selected_policy_regret` instantiate this argument with the newly constructed complete fine/coarse history laws. They do not merely assume the final history bound as an unexplained input.

For a finite class of observation trees, the general theorem applies once their actual common bounded path losses and corresponding laws are supplied. Padding terminal choices into a common absorbing record is one admissible encoding, but its validity is not automatically established for arbitrary host programs by this block. The result neither constructs hidden action permissions nor certifies a hard budget.

**Main endpoints:** `same_policy_error`, `uniform_policy_regret`, `minimizing_policies_exist`, `history_policy_error`, `history_selected_policy_regret`.

## 5. Exact controls and calibrations

### Rare-event amplification

The four-point laws `rareP delta` and `rareQ delta` share mass 1-delta on an ordinary outcome and put delta on different states inside the same rare-report event. Their total variation is delta, both event masses are delta, and conditional output distance is one. This is proved for every 0 < delta <= 1, rather than sampled at several small values.

`unequal_mass_sharp` uses event masses 1/10 and 1/5, whole-law distance 1/10, and conditional distance 1/2. Thus the stronger maximum-denominator bound can be attained. `positive_threshold_is_strict` shows why an event mass equal to the whole-law bound need not have a positive counterpart.

### Exact regret factor

The true binary law has P(true)=3/4 and the approximate law is uniform. Under classification loss, both choices minimize approximate risk. Choosing false gives true risk 3/4, whereas choosing true gives true risk 1/4. The law distance is 1/4 and regret is 1/2=2*TV. `checked_selected_regret` applies the actual general theorem to this example. The sharpness uses permitted approximate ties; no favorable tie-breaking rule is assumed.

### Misspecified sensor

`calibrated37` gives the fine eight-world sensor a calibration accuracy 37/50. The coarse reference retains the inherited accuracy 3/4. For every world, the total variation of the **joint** report/coarse-successor row is exactly 1/100. `sensor_all_history_error` applies `whole_history_bound` for all priors, all report-history policies, and every finite H, obtaining min(1,H/100).

For three observations and complete loss bound 23/20, kernel-checked arithmetic gives a fixed-policy allowance 69/2000 and changed-policy allowance 69/1000. These are bounds derived from the model contract, not a measured regret or a proof that the old adaptive sensor tree remains optimal after its likelihood changes. The general finite-policy theorem is instantiated on the binary classification example above; the displayed sensor margins are exact coefficient specializations.

### History is not the final state

Two different initial bits followed by the same reset have identical final-state laws but disjoint complete path laws. Both claims are proved. A method that compared only the final state would miss the initial history entirely.

## 6. What this completes, and what it does not

The exact filtering and planning results remain untouched. This block adds the quantitative relationship between their histories and supports selection under a uniform approximate-model error. Core 4.1, which combines a probability-record error with a separate response approximation and a Lipschitz loss, is not silently included: it requires its own response interface and proof.

The proof library uses finite types, exact real numbers, normalized laws, and explicit bounded losses. It does not identify a physical instrument from data, derive statistical confidence from the examples, justify neural generality, prove arbitrary host-program semantics, or reconstruct missing operational permissions. Same-kernel replay and complete transitive axiom audits are recorded separately from the mathematical assumptions.
