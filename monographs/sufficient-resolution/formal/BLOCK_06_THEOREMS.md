# Block 06 — Continuous approximate sufficiency

**v0.6.0 · Komorebi P. · 13 September 2026**

57 new theorem declarations; five modules. The prefix of every namespace below is
`Komorebi.SufficientResolution`. The production sources and printed signatures are
authoritative. Counts include helper lemmas and exact examples.

## 1. Defect transport from actual flows

`ContinuousDefect.generatorDefect q L A` means \(\delta=qL-Aq\).
`ContinuousDefect.evolutionDefect q L A t` means
\(E(t)=q e^{tL}-e^{tA}q\).
The operators act on real Banach spaces. `q` need not be injective or surjective.

`backward_derivative` proves the actual derivative
\[
\frac{d}{ds}\bigl(e^{(t-s)A}q e^{sL}\bigr)
 = e^{(t-s)A}\delta e^{sL}.
\]
`duhamel` applies the interval fundamental theorem of calculus to obtain
\[
E(t)=\int_0^t e^{(t-s)A}\delta e^{sL}\,ds.
\]
This is an equality of continuous linear maps, not just pointwise observations.
Continuity and integrability are supplied by `continuous_transportKernel`.
All real times are allowed here, with oriented negative-time integrals.

`derivative_at_zero` identifies the generator discrepancy as the actual derivative
at zero. `generatorDefect_zero_iff` proves both directions of
\[
\delta=0\quad\Longleftrightarrow\quad E(t)=0\text{ for all real }t.
\]

`evolutionDefect_add` gives
\[
E(s+t)=E(s)e^{tL}+e^{sA}E(t).
\]
`generatorDefect_composite` and `evolutionDefect_composite` give, for a second
model p:Z→W with generator B,
\[
\delta_{pq}=p\delta_q+\delta_p q,
\qquad E_{pq}(t)=pE_q(t)+E_p(t)q.
\]
Thus a second model does not erase the first model's error.

## 2. Exact scalar response

The `ExponentialBudgets` namespace defines
\[
R(a,b,t)=\int_0^t e^{b(t-s)}e^{as}\,ds.
\]
`response_of_ne` and `response_self` prove
\[
R(a,b,t)=
\begin{cases}
(e^{at}-e^{bt})/(a-b),&a\ne b,\\
t e^{at},&a=b.
\end{cases}
\]
They include arbitrary real rates and oriented times. The inequalities below
restrict to t≥0 where indicated.

`response_nonneg`, `response_mono`, `response_nonexpansive` and
`response_common_rate_le` prove positivity and rate comparisons. In particular,
R(a,b,t)≤t for a,b≤0 and R(a,b,t)≤t exp(c t) when a,b≤c.

For rate>0,
\[
R(0,-\mathrm{rate},t)=\frac{1-e^{-\mathrm{rate}t}}{\mathrm{rate}}
\le\frac1{\mathrm{rate}}.
\]
These are `response_stable_formula` and `response_stable_le`. The upper inequality
also holds for negative t as a scalar statement, but norm estimates never use it
to claim a positive-time bound at negative time.

## 3. Whole-operator estimates

`ContinuousApproximation.norm_evolution_le_envelopes` proves the more general
result for continuous envelope functions u,v known on [0,t]:
\[
\|E(t)\|\le\varepsilon\int_0^t v(t-s)u(s)\,ds,
\]
where \(\|e^{sL}\|\le u(s)\), \(\|e^{sA}\|\le v(s)\),
\(\|\delta\|\le\varepsilon\), and \(t,\varepsilon\ge0\).

`norm_evolution_le_response` specializes to
\[
\|e^{sL}\|\le M_L e^{as},\quad
\|e^{sA}\|\le M_A e^{bs},\quad s\ge0,
\]
and gives
\[
\boxed{\|E(t)\|\le M_LM_A\varepsilon R(a,b,t).}
\]
The amplitudes and epsilon are nonnegative. The two rates can have either sign.
The proof of this base estimate in fact does not need the separate amplitude
nonnegativity hypotheses once the interval norm bounds have been supplied; they
are retained in its interface and used by its monotonicity-based corollaries.

For readouts O:X→Y and V:Z→Y, define
\[
F(t)=Oe^{tL}-Ve^{tA}q.
\]
`norm_output_le_response` proves, when \(\|O-Vq\|\le\eta\),
\[
\|F(t)\|\le\eta M_L e^{at}
 +\|V\|M_LM_A\varepsilon R(a,b,t).
\]
The target Y only needs a normed real vector-space structure, not completeness.

`same_representation_bound` shows that when qx=qy,
\[
\|Oe^{tL}x-Oe^{tL}y\|\le e\|x-y\|\quad\text{if }\|F(t)\|\le e.
\]
This is approximate observational sufficiency, not an approximate dimension theorem.

## 4. Uniform stability and initialization

`ContinuousStability.norm_evolution_bounded` proves the linear-time estimate
M_L M_A epsilon t when both flows are uniformly bounded by the amplitudes.
`norm_evolution_distinct` and `norm_evolution_equal` give the closed-form two-rate
bounds without dividing by zero in the equal-rate case.

If the true flow is bounded by M_L and the reduced flow obeys
\(\|e^{tA}\|\le M_Ae^{-rt}\), r>0, then
`norm_evolution_stable` and `norm_evolution_uniform` prove
\[
\|E(t)\|\le M_LM_A\varepsilon\frac{1-e^{-rt}}r
\le\frac{M_LM_A\varepsilon}r.
\]
`norm_output_uniform` gives
\[
\|F(t)\|\le\eta M_L+\|V\|\frac{M_LM_A\varepsilon}r.
\]

For an arbitrary reduced initial state z,
`norm_initialization_uniform` proves
\[
\|Oe^{tL}x-Ve^{tA}z\|
\le
\left(\eta M_L+\|V\|\frac{M_LM_A\varepsilon}r\right)\|x\|
+\|V\|M_Ae^{-rt}\|qx-z\|.
\]
The state norm multiplying the model allowance is essential.

`norm_composite_evolution` and `norm_composite_generator` propagate independent
allowances through representation chains with their explicit map norms.

## 5. Sharpness and a genuine boundary counterexample

`ContinuousApproxExamples.scalar_flow` identifies the actual exponential of a
scalar operator using the differential equation and uniqueness.
`scalar_response_sharp` proves for b≤a and t≥0
\[
\|e^{at}-e^{bt}\|=(a-b)R(a,b,t).
\]
Here q is the identity and both flow amplitudes are exactly one. The universal
estimate is attained by these actual systems.

For every epsilon>0, set L=epsilon, A=0 and q=1.
`unstable_generator_exact`, `unstable_error_exact` and `unstable_error_unbounded`
prove
\[
\|\delta\|=\varepsilon,\quad
\|E(t)\|=e^{\varepsilon t}-1\ge\varepsilon t,\quad
\forall B\in\mathbb R\ \exists t\ge0:\ \|E(t)\|>B.
\]
This refutes a uniform-error inference based on a small generator defect alone.
It does not contradict the stability theorem, whose true-flow growth hypothesis
fails in this example.

## Non-claims

Bounded time-independent generators only. No unbounded domains, time-varying or
nonlinear/stochastic forcing theorem. No eigenvalue-based inference of common
flow growth, no sampled-data identification, no automatic positive/integral
realization, no approximate minimum-dimension theorem, no arithmetic existence.
The separate Python tests check finite rational coefficients; they do not prove
these universal statements or verify an arbitrary system's growth assumptions.
