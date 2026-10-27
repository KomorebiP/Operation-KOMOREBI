P69 individual formalization scope

`ObservationLawKernels.law` is the actual finite joint history measure, formed
recursively by the policy composition product, observation composition product,
and measurable append pushforward. It retains the initial history and all
recorded action-observation pairs. Its probability and prefix-consistency facts
are derived from the supplied Markov kernels.

`KernelTVMeasurable.distance` is the existing genuine measure total variation
`SequentialLowerCertificate.lawTV`. Its measurability is derived from joint
Radon--Nikodym densities against the local sum kernel; no common latent state
space or fixed model reference measure is assumed.

`ObservationLawComparison.lawTV_le_expected` proves

  TV(law(π,P,μ₀,T), law(π,Q,ν₀,T))
  ≤ min(1, TV(μ₀,ν₀) + Σ(t<T) ∫ TV(Pₜ(h,a),Qₜ(h,a)) d(law(π,P,μ₀,t) ⊗ πₜ)).

The expected drift is integrable and is also identified as the chronological
iterated history/action expectation. The adjacent hybrid uses the P prefix and
Q continuation. Common policy and continuation contraction come from the
separately checked actual-measure `MeasureTVCalculus`, and the one-kernel change
cost is derived by bounded tests and integration. No desired recurrence or
contraction property is included as a premise.

The standard Borel assumption is on observations Y; the initial-history and
action spaces are arbitrary measurable spaces. Policies are arbitrary total
measurable Markov kernels. P and Q are total history/action observation kernels,
with the Markov property at every history, including histories null under Q.
This is the explicit completion requirement, not a silent rejection rule.

Same-initial-law, fixed-initial-history, uniform time-dependent budgets, and
arbitrary measurable observation readouts are explicit corollaries. No claim
that a residual lower certificate implies a statistical upper bound is made.

Evidence is individual-development evidence, not a cumulative release check.
