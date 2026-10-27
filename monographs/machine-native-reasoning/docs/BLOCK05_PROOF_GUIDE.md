# Block 05 — from approximate records and responses to one decision

**Machine-Native Reasoning · Reviewed Core 0.2 · Formal companion 0.5.0 · Komorebi P.**

## 1. The source result and its exact extension

The newly admitted source result is **Core 4.1**, label `r:risk`, printed page 15, canonical LaTeX lines 533–550. Core 3.8 already compares complete laws and their conditional records. Core 5.6 already compares a *fixed* bounded loss across models before optimizing. Neither alone covers a separately approximated response inside the loss. This block supplies that missing step.

Let `p` and `q` be nonnegative normalized distributions on the same finite world type `X`. Let `v,w : X → V` give exact and approximate responses in one metric space. For a common decision loss `loss : A → V → R`, define

    R(a) = sum_x loss(a,v(x)) p(x)
    Q(a) = sum_x loss(a,w(x)) q(x).

The finite action catalogue is shared. It is not legal to compare different meanings of the same printed loss name, or to use a probability guarantee from a different record. The source statement uses a globally bounded, K-Lipschitz loss. The fundamental Lean theorem needs bounds only at the actual paired responses; `decision_error_global` verifies the source specialization explicitly. A pseudometric space suffices, so the proof is slightly more general than the stated metric case. The example's affine scalar losses are bounded on their attained responses in [0,1], not on all of R.

## 2. The two error terms are proved separately

The finite sum identity underlying `loss_change_bound` is

    |risk(p,f) - risk(p,g)| <= sum_x |f(x)-g(x)| p(x).

Nonnegativity of p is used when taking absolute values. If each discrepancy is at most r, normalization makes the sum at most r. This is `loss_change_uniform`.

Insert the intermediate sum `risk(p, loss(a,w(-)))`. The response part is at most K d when `dist(v(x),w(x)) <= d` and the paired loss changes by at most K times that distance. Block04's fixed-loss total-variation theorem bounds the remaining change of probability record by e. Thus

    |R(a)-Q(a)| <= e + K d.

Both actual risks lie in [0,1], yielding

    xi = min(1,e+K d),    |R(a)-Q(a)| <= xi.

`decision_error` and `decision_error_global` supply these endpoints. The scalar inequality is conditional on the two actual error bounds. It neither estimates e or d from data nor proves that the candidate worlds include a physical truth.

A supporting generalization, `expected_response_error`, permits a bound on `sum_x p(x) dist(v(x),w(x))` instead of the uniform response bound. The weight is the declared true-model record p, not an arbitrary average of observed errors. It remains a conditional mathematical premise, not an executable estimator.

## 3. Minima, regret, and the strict gap

For any common finite nonempty catalogue, the library's finite-minimum construction produces both an approximate minimizer and a true model-risk minimizer. `metric_minimizers_exist` derives the uniform risk allowance from the metric premises and returns the minimizing decisions together with the regret bound. This does not assume a minimizing decision has been supplied by an oracle.

For a specified approximate minimizer c and any true comparator b,

    R(c) - R(b) <= min(1,2 xi).

`regret_to_minimum` states the source form directly against `Planning.finiteMin`, whose attainment is separately proved. The factor two comes from the two evaluated actions, not from doubling the probability discrepancy before it is used. The cap one comes from the loss range.

If every alternative j has `Q(c)+2 xi < Q(j)`, then `R(c)<R(j)`. `unique_minimizer_transfer` proves the strict comparison for all other catalogue members and that any true minimizing member must equal c. Equality at the gap threshold does not certify uniqueness. The counterexample has exact response 1/2 and approximate response 2/5 under a point-mass world: the approximate action is unique, its gap is exactly 2(1/10), and the true actions tie. A second example gives an actual reversal below the threshold.

The auxiliary `approximate_optimizer_regret` separately accounts for a solver residual eta, giving `min(1,2 xi+eta)`. Numerical/model approximation and incomplete optimization are different obligations. Core 4.1 itself uses an exact minimizer, not this additional allowance.

## 4. An actionable interval and threshold

The same error certificate gives

    max(0,Q(a)-xi) <= R(a) <= min(1,Q(a)+xi).

If `Q(a)+xi <= tau`, then `R(a)<=tau`. These are `risk_interval` and `risk_threshold`. They concern expected loss under the specified model. They are not a hard execution budget, a zero-risk claim, an authorization rule, or an externally established deployment-safety guarantee.

## 5. Connection to conditional histories and stored records

Let P and Q be the actual full-history laws from Block04, and let E denote the same positive-probability event on both sides. For a retained coordinate map f, define

    recordAfter(f,E,P) = push_f(normalize(P restricted to E)).

No positive-probability assumption is hidden in notation: every theorem using this as a probability record requires positive masses under P and Q. An algebraic normalization of a zero vector is not a probability record.

If `TV(P,Q)<=delta`, the established conditional-output result gives

    e_event = min(1, delta / max(P(E),Q(E))).

Now suppose the actually stored normalized record r differs from the approximate conditional record by at most s. The triangle inequality and range cap yield

    e_record = min(1,e_event+s).

The response theorem gives one combined allowance

    xi = min(1,e_record+K d).

`conditioning_and_storage` proves the intermediate record bound. `conditioned_response_error` performs the actual composition. The complete-history endpoints instantiate P and Q with `ApproximateHistory.law` and its fine-to-coarse projection, using the already proved accumulation `min(1,delta0+sum_t epsilon_t)`. The same action/report-only policy is used across the two models.

The mathematical conditional theorem allows any specified event. Operational use additionally requires that the event be accessible to the observer. This is not inferred from its `Finset` representation. In the concrete example E is precisely the observed report-one event.

## 6. One source-faithful sensor calculation

The example uses the inherited eight-world `PlanningSensor.initialFine`: physical target b equals sensor convention s after display zero, while the nuisance bit is unresolved. Both diagonal (b,s) possibilities initially have mass 1/2.

The true model is the inherited `ApproximationExamples.calibrated37` with calibration accuracy 37/50. The comparison model is `PlanningSensor.sensorLaw` with accuracy 3/4. The true and comparison joint report/next-state distributions are constructed from those instruments and the same initial record. `sensor_evidence_bound` obtains a law allowance 1/100 from the existing **complete joint-row** proof, not from a claim about an isolated likelihood entry.

The observed event is report one. Both event masses are proved to equal 1/2. The true posterior assigns probability 37/50 to target one, and the comparison posterior assigns 3/4. A specified stored record uses 19/25 for target one and 6/25 for target zero. It is proved normalized and has storage discrepancy 1/100 from the comparison posterior.

The exact target response is 0 or 1. The approximate response is 1/100 or 99/100. Each response error is exactly 1/100. The common loss is y for decision zero and 1-y for decision one; it has unit Lipschitz sensitivity and lies in [0,1] at every used response.

The certified chain is therefore

    whole-law allowance:        1/100
    conditional allowance:      (1/100)/(1/2) = 1/50
    stored-record allowance:    1/50 + 1/100 = 3/100
    response allowance:         1/100
    final risk allowance xi:    1/25.

For decision one, the approximate risk is 613/2500 = 0.2452. The true model risk is 13/50 = 0.26. The certificate establishes the upper value 713/2500 = 0.2852, which is below 3/10. The other approximate action has risk 1887/2500 = 0.7548, so the approximate gap exceeds 2/25. The generic gap theorem, rather than direct true-risk comparison alone, certifies uniqueness of decision one.

The exact discrepancy 37/2500 = 0.0148 and the sharper exact record difference 1/50 are computed for inspection. They are **not substituted** for the more conservative pre-established composition when issuing the certificate. This makes the argument traceable from the same model, report, record and response.

The constructed storage record and response approximation are supplied finite artifacts. No generic rounding algorithm, training process or physical observation is claimed. This is one terminal decision after one report, not a re-proof that the earlier three-report policy remains optimal under the changed sensor accuracy.

## 7. Failure boundaries

The positive library contains exact proofs that: perfect probabilities do not eliminate response error; exact responses do not eliminate probability error; a gap of exactly 2 xi can leave a true tie; changing the objective is unaccounted for; bounded loss need not be unit-Lipschitz; losses outside [0,1] defeat the cap and coefficient; optimization residual cannot disappear; zero-mass conditioning produces no probability record; and stored-record error cannot be ignored.

Nine deliberately false fixtures try to assert corresponding invalid conclusions. The compiler must reject each with the specified mathematical diagnostic. A missing import or timeout is not counted as the expected rejection.

## 8. Reading and source boundary

Production modules are `ResponseDecision`, `DecisionHistory`, and `ResponseExamples`. `checks/CheckResponseAPI.lean` independently restates the source's finite sums, cap, finite minimum, unique-gap conclusion, and risk threshold. `THEOREM_MAP.json` promotes only Core 4.1. The 18 preceding substantive modules and the source book remain byte-identical. All other claims retain their own status.

Exact real arithmetic and classical finite minimizers establish conditional mathematical results. No efficient extracted optimizer, finite-precision host refinement, hardware law, or independent kernel implementation is asserted. The next book-level target is Core 4.2, which asks whether the corrected information can support one common artifact for fixed recipients.
