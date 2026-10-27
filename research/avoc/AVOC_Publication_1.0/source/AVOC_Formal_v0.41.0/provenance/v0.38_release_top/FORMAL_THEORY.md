# AVOC Formal Theory through v0.38.0

## Certified Quote Authority and Robust Quote Planning

AVOC v0.38 extends the exact lazy staged controller of v0.37 from point-valued setup quotes to authority-bound interval evidence.  Its formal chain is

\[
\text{bounded quote evidence}
\to
\text{finite-horizon value/Q certificates}
\to
\text{robust admissible control}
\to
\text{selected-only artifact execution}
\to
\text{quote-bound recovery}.
\]

All load-bearing numeric statements use exact natural numbers and rationals.

## 1. Exact quote identity

For dimensions `n,m`, a quote identity binds:

- operation kind (`warm` cache inspection or `cold` generation);
- the exact affine source signature;
- declared deployment-call count;
- cost-model identifier;
- cache or generator identifier;
- checker identifier;
- environment identifier;
- quote schema/version.

The formal authority compares decoded records by exact equality.  Hashes used by wrappers are integrity fingerprints only and are not assumed injective.

## 2. Certified interval evidence

A bounded quote carries

\[
s\in[s_L,s_U],\qquad
g\in[g_L,g_U],\qquad
p\in[p_L,p_U],
\]

with

\[
0\le s_L\le s_U,
\qquad
0\le g_L\le g_U,
\qquad
0\le p_L\le p_U\le1.
\]

Here `s` is setup cost, `g` is gross deployment saving, and `p` is operation-success probability.  Interval validity is a syntactic/formal fact; it does not establish empirical calibration.

The conservative nominal staged model uses

\[
\widehat s=s_U,
\qquad
\widehat g=g_L,
\qquad
\widehat p=p_L.
\]

A compatible exact realization supplies point values inside all six warm/cold intervals.

## 3. Errors derived from the quote widths

The setup/gross widths give action-specific reward radii.  The probability width gives a full-\(L^1\) radius for the binary success/failure observation law.  These are lifted into the inherited finite-horizon stochastic-abstraction theorem.

For continuation horizon `h`, AVOC defines:

\[
D_h=\text{valueRadius}(h),
\]

and an action-specific Q radius

\[
\rho_h(a)
=
D_h+ho_R(a)+hR_{\max}\rho_P(a).
\]

For every compatible exact realization,

\[
\boxed{
\widehat Q_h(s,a)-\rho_h(a)
\le Q_h^{\mathrm{true}}(s,a)
\le \widehat Q_h(s,a)+\rho_h(a)
}
\]

and

\[
\boxed{
\widehat V_h(s)-D_h
\le V_h^{\mathrm{true}}(s)
\le \widehat V_h(s)+D_h.
}
\]

The proof does not substitute probability endpoints into Bellman expectations without justification.  It first derives reward and transition-law errors, then uses the existing stochastic transport bound.

## 4. Robust action choice

Define

\[
\underline Q_h(s,a)=\widehat Q_h(s,a)-\rho_h(a),
\qquad
\overline Q_h(s,a)=\widehat Q_h(s,a)+\rho_h(a).
\]

The robust selector maximizes `lowerQ` over the state-dependent feasible action set, using the same stable action ordering as v0.37.  It is proved admissible.

### Certified dominance

If a feasible action \(a^*\) satisfies

\[
\underline Q_h(s,a^*)\ge\overline Q_h(s,a)
\]

for every feasible competitor, then

\[
\boxed{
Q_h^{\mathrm{true}}(s,a)
\le Q_h^{\mathrm{true}}(s,a^*)
}
\]

for every compatible exact realization.

### Local and complete-policy regret

The interval certificate yields a local true-Q gap for the robust action.  The selector is then lifted to a complete adaptive policy.  Reusing AVOC's existing telescoping theorem gives

\[
\boxed{
0\le
V_n^{\mathrm{true}}(s)-J_n^{\mathrm{true}}(s,\pi_{\mathrm{robust}})
\le
\sum_{k<n}2\,\overline\rho_k.
}
\]

This is a whole-policy statement, not a first-action bound relabeled as end-to-end performance.

## 5. Exact collapse to v0.37

Let `ExactBands` mean that every setup, gross, and probability interval is a singleton.  AVOC proves:

\[
D_h=0,
\qquad
\rho_h(a)=0,
\]

and therefore

\[
\underline Q_h=\widehat Q_h=\overline Q_h.
\]

With the same tie-breaking rule,

\[
\boxed{
\operatorname{robustChoice}
=
\operatorname{v0.37Choice}.
}
\]

Thus v0.38 is a conservative extension of the exact v0.37 staged controller.

## 6. Artifact refinement

A returned proof-carrying artifact is accepted only if it:

- matches the exact quote identity and selected operation kind;
- is semantically equivalent to the protected affine source;
- does not increase execution cost;
- has exact setup and gross values inside the authorized bands.

Successful refinement replaces deterministic fields with singleton bands:

\[
[s,s],\qquad[g,g].
\]

The probability interval is deliberately retained:

\[
[p_L,p_U].
\]

Checking a realized artifact does not by itself calibrate its future success probability.

The executable `confirmExec` is proved equal to the declarative transition.  Infrastructure fault yields no report and no state transition.  Warm success preserves the cold artifact and cold evidence exactly; cold success preserves the warm side exactly.

## 7. Quote-bound durable recovery

An intent binds:

\[
(\text{sequence},\text{pre-state},\text{selected action},
 \text{warm evidence},\text{cold evidence}).
\]

A commit additionally records the exact checked outcome and post-state.  Acknowledgement re-executes the checked transition and rejects changes to:

- quote identities or interval endpoints;
- sequence number;
- pre-state or post-state;
- outcome tag.

An exact duplicate acknowledgement returns the complete same checkpoint.  It cannot duplicate budget, spending, quote evidence, artifacts, or the sequence counter.  An unfinished intent is rejected as non-evidence and is not silently retried.

## 8. Checked examples

### Exact rank-one quote

For the inherited rank-one affine example with singleton quote bands, the robust and exact v0.37 controllers both choose warm inspection.  At continuation horizon one:

\[
\widehat Q_{\mathrm{warm}}=14867,
\qquad
\widehat Q_{\mathrm{cold}}=14804,
\]

all radii are zero, and the complete-policy regret certificate is zero.

### Uncertainty changes the action

The nominal conservative model gives:

\[
\widehat Q_{\mathrm{warm}}=120,
\qquad
\widehat Q_{\mathrm{cold}}=60.
\]

The warm local radius is 208 while the cold radius is zero, so

\[
\underline Q_{\mathrm{warm}}=-88
<60=
\underline Q_{\mathrm{cold}}.
\]

The robust controller therefore chooses cold.  The reported complete-policy bound is 416.

### Certified dominance

A checked example has warm interval score exactly 100 and cold exactly 50.  The executable dominance certificate reports warm as optimal for every compatible realization.

## 9. Executed bounded evidence

A separate Python `Fraction` oracle enumerated compatible point realizations and independently calculated finite-horizon values.  It matched the Lean executable on:

- 21 plan instances;
- 1,523 compatible exact realizations;
- exact collapse, uncertainty reversal, dominance, interval overlap, artifact refinement, identity mutation, fault separation, unfinished intent, and acknowledgement behavior.

The selected-only SQLite workflow additionally checked:

- warm execution with the cold artifact path absent;
- cold execution with the warm artifact path absent;
- commit-before-ack recovery without a second selected-operation call;
- duplicate resume idempotence.

These are bounded implementation tests.  They do not prove the Python interpreter, SQLite, operating system, Lean compiler, or physical host.

## 10. Provenance

v0.37 is the sole authoritative verified predecessor.  Its complete source was reconstructed from the complete v0.35 archive plus retained v0.36 specification material because a complete v0.36 source archive was unavailable.  v0.38 preserves that provenance boundary and does not retroactively claim independent verification of missing v0.36 source.
