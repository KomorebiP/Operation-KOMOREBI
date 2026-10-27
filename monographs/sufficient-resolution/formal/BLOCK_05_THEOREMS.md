# Block 05 — Continuous-time memory and sufficient resolution

**Komorebi P. · v0.5.0 · 13 September 2026**

97 new theorem/lemma declarations in eight modules. 112 new named declarations.
The statements below are proved in Lean under their printed hypotheses. Helper
lemmas and examples contribute to the counts. These are not 97 novelty claims.

## 1. Analytic flow and variation of constants

Namespace: `Komorebi.SufficientResolution.ContinuousFlow`.

For a bounded real linear operator D on a Banach space, `flow D t` is exactly
`NormedSpace.exp (t • D)`, not a formal stand-in or an assumed solution.

`hasDerivAt_flow`, `hasDerivAt_flow_right`, `flow_add` and the inverse-time
identities establish the operator evolution. For continuous f and an actual
curve z satisfying z'=Dz+f at every real time,

    variation_of_constants:
    z(t) = exp(tD)z(0) + integral_0^t exp((t-s)D)f(s) ds.

`backward_forced_derivative` proves the cancellation of D when differentiating
exp((t-s)D)z(s). The fundamental theorem of calculus then gives the integral
identity. Continuity and interval integrability are proved, not postulated for
the block application. `homogeneous_solution`, `homogeneous_unique` and
`forced_unique` supply the corresponding uniqueness statements.

Scope: all real t with oriented intervals. The general forced theorem assumes
the differential equation and continuous forcing, not the desired integral formula.
For the block system, the differential equation is derived from the full exponential.

## 2. Algebraic-to-analytic transport bridge

For bounded observations K and J of two bounded generator algebras,

    mapped_flow_eq_iff_powers_eq:
    [for all t, K(exp(tL)) = J(exp(tD))]
      iff [for all n, K(L^n) = J(D^n)].

The forward direction differentiates actual exponential jets. The reverse
maps the norm-convergent exponential series through bounded linear maps and
uses uniqueness of its sum (`mapped_flow_hasSum`).

Specializations:

    sandwich_flow_zero_iff:
    [for all t, B exp(tD) G=0] iff [for all n, B D^n G=0].

    compressed_flow_iff_powers:
    [for all t, C exp(tL) R=exp(tA)] iff [for all n, C L^n R=A^n].

This is what legitimately transports the preserved discrete algebraic results
to continuous dynamics. Equality of a finite selection of sampled times is
never substituted for an all-time identity.

`compressed_flow_defect` establishes, with Q=I-RC,

    C exp((s+t)L)R - (C exp(sL)R)(C exp(tL)R)
       = C exp(sL) Q exp(tL)R.

This identity needs no CR=I assumption. With a split representation, Q is the
actual discarded-state projector and the expression records a hidden return.

## 3. Actual full block dynamics and hidden elimination

Namespace: `Komorebi.SufficientResolution.ContinuousBlockDynamics`.

A `ContinuousBlockDynamics V H` contains four bounded real maps A,B,G,D.
The full bounded generator is L(y,z)=(Ay+Bz,Gy+Dz). V and H are Banach spaces
for the flow theorems. Neither need be finite-dimensional.

`visible` and `hiddenState` are components of exp(tL)(y0,z0).
`hasDerivAt_visible` and `hasDerivAt_hiddenState` derive their ODEs.

    hidden_elimination:
    z(t) = exp(tD)z0 + integral_0^t exp((t-s)D)G y(s) ds.

    hidden_forcing_decomposition:
    Bz(t) = B exp(tD)z0 + integral_0^t M(t-s)y(s) ds,
    where M(t)=B exp(tD)G.

    continuous_memory_equation:
    y'(t) = Ay(t) + B exp(tD)z0 + integral_0^t M(t-s)y(s) ds.

The last statement is a `HasDerivAt` theorem for the constructed trajectory.
`prepared_memory_equation` sets z0=0 and removes only the initial-state term.
`full_solution_unique` identifies every solution of the full homogeneous ODE
with its exponential trajectory.

Boundary: a converse theorem constructing z from an arbitrary Volterra solution
y is not included. No claim about unbounded generators or their domains is made.

## 4. Exact prepared closure and the finite certificates

Let C(y,z)=y, R(y)=(y,0), and E(t)=C exp(tL)R. The following are equivalent:

    E(t)=exp(tA) for every real t;
    M(t)=0 for every real t;
    B D^n G=0 for every natural n;
    E(s+t)=E(s)E(t) for every real s,t.

Declarations:

- `prepared_exact_iff_generator_powers`
- `prepared_exact_iff_discrete`
- `memory_zero_iff_moments`
- `prepared_exact_iff_memory_zero`
- `prepared_semigroup_iff_exact`
- `prepared_semigroup_iff_memory_zero`

The proofs use both directions of the analytic bridge and the unchanged
algebraic memory-closure theorem. The semigroup converse is also proved by
recovering the generator ODE from the assumed composition law.

When d=dim H is finite,

    prepared_exact_iff_finite_memory:
    [E(t)=exp(tA) for all t] iff [B D^k G=0 for 0<=k<d].

    prepared_exact_iff_finite_generator:
    [E(t)=exp(tA) for all t] iff [C L^n R=A^n for 0<=n<=d+1].

The zero-dimensional case is included. The visible space may remain
infinite-dimensional. `prepared_exact_of_annihilator` uses a supplied monic
polynomial p with p(D)=0 and the first deg(p) vanishing feedback moments,
without imposing finite dimension on H.

`nonclosure_has_finite_moment` gives a nonzero moment witness below d when
all-time closure fails. `nonzero_moment_forces_nonclosure` proves existence
of a real time at which prepared closure fails. It does not assert a
particular numerical time or locate that witness computationally.

## 5. Actual iterated derivatives, not formal coefficient notation

`iteratedDeriv_mapped_flow` and `iteratedDeriv_flow_zero` identify the jets with
Mathlib's actual `iteratedDeriv`.

    iteratedDeriv_prepared_zero: E^(n)(0)=C L^n R.
    iteratedDeriv_memory_zero: M^(n)(0)=B D^n G.

Therefore,

    prepared_exact_iff_finite_derivatives:
    [E(t)=exp(tA) for all t]
       iff [E^(n)(0)=A^n for 0<=n<=d+1].

    memory_zero_iff_finite_derivatives:
    [M(t)=0 for all t] iff [M^(n)(0)=0 for 0<=n<d].

If the first k hidden-return moments vanish, then

    derivative_prefix_of_memory_prefix:
    E^(n)(0)=A^n for n<=k+1;

    first_return_derivative:
    E^(k+2)(0)-A^(k+2)=B D^k G.

The factorial belongs to Taylor coefficients, not derivatives. The leading
Taylor discrepancy corresponding to the last identity is divided by (k+2)!.
These certificates test complete operator identities, never finite trajectory
samples or numerical tolerances.

## 6. Arbitrary bounded split compression and all-state closure

Namespace: `...ContinuousFlow`.

For bounded C:X->Z and R:Z->X with CR=I and finite-dimensional ker C,

    compressed_flow_iff_finite_generator:
    [C exp(tL)R=exp(tCLR) for all t]
       iff [C L^n R=(CLR)^n for n<=dim ker C+1].

This uses the actual discarded space. No orthogonality or finite ambient
state-space dimension is required. The algebraic canonical ker C block
construction is the preserved predecessor theorem, not a redefined substitute.

For bounded C, independently of a chosen lift,

    intertwines_flow_iff_generators:
    [C exp(tL)=exp(tA)C for every t] iff [CL=AC].

For the visible/hidden block system,

    all_state_closure_iff_B_zero:
    [visible(y0,z0,t)=exp(tA)y0 for every t,y0,z0] iff [B=0].

Prepared closure only requires all B D^k G to vanish. Both B and G may then be
nonzero. Arbitrary initial hidden state is a distinct condition.

## 7. Exact examples

Namespace: `...ContinuousExamples`.

`delayed` has V=R, H=R^2, A=0, B(z1,z2)=z1, G(y)=(0,y), D(z1,z2)=(z2,0).

    delayed_hidden_flow: exp(tD)(z1,z2)=(z1+t z2,z2).
    delayed_memory: M(t)=t I.
    delayed_moment_zero: M_0=0.
    delayed_moment_one: M_1=I.
    delayed_first_return_derivative: E^(3)(0)-A^3=I.

`delayed_derivative_prefix`, `delayed_nonclosure` and `delayed_not_semigroup`
certify shallow agreement and later failure. The explicit hidden exponential
is proved from the ODE and uniqueness, not a symbolic Python calculation.

`disconnectedReturn` changes D to zero but keeps the same nonzero B and G.
`disconnected_memory_zero` and `disconnected_prepared_exact` prove zero feedback
and exact prepared evolution. `disconnected_all_state_not_closed` and
`disconnected_initial_derivative` prove that hidden initialization is still
immediately visible.

## 8. Verification boundary

Read VERIFICATION_SUMMARY.md and the actual principal signatures in
verification/PRINCIPAL_SIGNATURES_v0.5.0.log. Compilation, transitive axiom
audits, same-kernel replay, exact finite Python controls and ZIP integrity
are separate evidence categories. None certifies novelty, external arithmetic
existence, data-driven identification or a universal nonlinear realization.
