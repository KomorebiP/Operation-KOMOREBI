# Block 11 — Constructed spectral solutions and the differentiability domain

Komorebi Physics Lean v0.11.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF pages 31–33 of 550, printed pages 18–20. The literal target is the constructed evolution in (6.26) and its application to (6.27)–(6.41). The authoritative cumulative result is `verification/final/report.json`. The source page images were inspected, including locally rendered pages 31 and 33 when Files did not return those images. The original PDF is unchanged.

## 1. Scope and inventory

| Module | Theorem declarations | Definitions | Main role |
|---|---:|---:|---|
| L2DominatedLimits | 4 | 0 | Square-summable dominated convergence and actual Hilbert derivatives |
| SpectralTimeContinuity | 20 | 2 | Strong time continuity, actual domain invariance, graph continuity |
| SpectralSchrodinger | 13 | 0 | Actual l2 derivative and its sharp domain characterization |
| SpectralSolutions | 10 | 0 | Existence, uniqueness and countable packet-current consequences |
| SpectralTimeApproximation | 8 | 1 | Uniform-in-time state and velocity cutoff approximation |
| SpectralEvolutionExamples | 26 | 4 | Rough states, norm-discontinuity and nonzero normalized dynamics |
| **Block 11** | **81** | **7** | **88 new inventoried declarations** |

The cumulative inventory contains **977 theorem declarations, 1,172 inventoried declarations and 58 mathematical modules**. It comprises 39 recovered Paper VII theorem declarations and 938 full-edition declarations. The 52 mathematical files from v0.10.0 are preserved byte-for-byte. The new count is 55 general/support theorems and 26 example/support theorems. These are not independent physical discoveries or a completion percentage for the full edition.

The general evolution results use the actual infinite-dimensional space

    Space = lp (fun _ : Nat => Complex) 2.

The eigenvalue sequence lambda : Nat -> Real is arbitrary. It need not be positive, bounded, increasing or distinct. The harmonic examples use lambda_n=n+1/2. The operator is the previously constructed maximal self-adjoint real diagonal multiplier, not an arbitrary non-diagonal Hamiltonian.

## 2. Actual continuity, not only scalar continuity

The operators are the actual bounded multipliers already constructed in Block 10:

\[
(U(t)x)_n=e^{-it\lambda_n}x_n.
\]

`evolution` is a named alias for that existing operator, not a new family supplied with a continuity axiom. Each multiplier has modulus one, and the existing group law and norm preservation are reused.

`L2DominatedLimits.tendsto` proves that coordinate convergence upgrades to convergence in the l2 norm when the errors have a square-summable dominating sequence. It applies Tannery's theorem to squared coordinate norms, identifies their sum with the actual squared l2 norm, and then takes the continuous square root. Coordinate convergence alone is not an input sufficient for its conclusion.

For fixed x, the phase errors are bounded by 2|x_n|, whose squares sum. This gives `continuous_orbit`:

\[
\boxed{t\longmapsto U(t)x\text{ is continuous in }\ell^2\quad\text{for every }x\in\ell^2.}
\]

This is **strong time continuity**. It is distinct from cutoff convergence and from continuity in the norm of bounded operators. A later exact example refutes the latter in the harmonic model.

## 3. The actual maximal domain is preserved

The domain is

\[
D(H)=\{x\in\ell^2:(\lambda_nx_n)_n\in\ell^2\},
\qquad (Hx)_n=\lambda_nx_n.
\]

`domain_preserved` proves square summability of the weighted evolved vector. The proof uses the actual unit-modulus coordinates, not finite support. `domainEvolution` packages the resulting member of the actual domain subtype. It has its own audited proof obligation.

The proofs establish

\[
HU(t)x=U(t)Hx\quad(x\in D(H)),
\qquad U(t)x\in D(H)\iff x\in D(H).
\]

The reverse implication uses U(-t). Thus evolution preserves the domain rather than smoothing every state into it.

The graph norm is also preserved, and `graph_continuity` proves actual convergence in that norm. This uses continuity of both U(t)x and U(t)Hx plus the preceding block's graph-convergence equivalence. No differentiability in the graph norm is asserted; a further H-squared domain would be relevant to that stronger question.

## 4. The Schrödinger derivative is an l2 theorem

The coordinate derivative is proved from the real-time derivative of the complex exponential. To pass to the Hilbert space, the new argument establishes

\[
|e^{-is\lambda_n}-e^{-it\lambda_n}|\le |s-t|\,|\lambda_n|.
\]

For a domain initial state, every coordinate of the difference quotient is bounded by |(Hx)_n|. The desired velocity has the same coordinate magnitude. The difference between the slope and that velocity is therefore bounded by 2|(Hx)_n|, a genuinely square-summable bound.

`hasDerivAt_of_dominated_slope` combines the coordinate derivatives with that bound and proves convergence of the actual vector-valued slopes in the punctured neighborhood filter. It yields

\[
\boxed{\frac{d}{dt}U(t)x=-iHU(t)x\quad(x\in D(H)).}
\]

The literal checked Lean conclusion is

```lean
HasDerivAt (fun s => evolution eig s (x : Space))
  ((-Complex.I) • DiagonalDomain.operator eig (domainEvolution eig t x)) t
```

There is no supplied trajectory derivative, energy balance or claimed solution field in this theorem. The actual exponential multiplier supplies the trajectory.

The velocity is continuous, its norm equals ||Hx|| at every time, and the orbit obeys the quantified bound

\[
\|U(s)x-U(t)x\|\le |s-t|\,\|Hx\|.
\]

The constant depends on the particular domain state. It is not a nonexistent uniform bounded-operator norm for the unbounded H.

## 5. Differentiability characterizes the domain

The converse is separately proved. An assumed ambient l2 derivative y can be evaluated by the actual continuous coordinate maps. Uniqueness of scalar derivatives forces

\[
y_n=-i\lambda_n(U(t)x)_n.
\]

Since y belongs to l2, multiplying by i proves weighted square summability of U(t)x. The domain-invariance equivalence then recovers x in D(H). Consequently, at every real time t,

\[
\boxed{U(\cdot)x\text{ is differentiable in }\ell^2\text{ at }t
\iff x\in D(H).}
\]

All states have continuous orbits. Domain states have continuously differentiable orbits. States outside the domain have no ambient l2 derivative at any real time. Statements use `DifferentiableAt`/`HasDerivAt`; no conclusion is inferred from Lean's totalized `deriv` at a nondifferentiable point.

## 6. Constructed global existence and uniqueness

`exists_unique_solution` proves, for each domain initial vector, existence and uniqueness of a domain-valued trajectory on all real times satisfying the original ambient Schrödinger derivative and initial condition. Its witness is `domainEvolution`, and `solution_formula` identifies any such solution with that witness.

The uniqueness lemma is more general: for any symmetric partially defined linear operator, two given domain-valued all-real-time solutions agreeing at one time agree everywhere. It differentiates the squared norm of their difference and proves it remains zero. This does **not** assert existence for an arbitrary symmetric operator. Existence here is supplied only by the constructed real diagonal model.

This closes the previously missing evolution premise for the spectral realization of (6.26). It is not a new proof of the general Stone theorem or a claimed general spectral representation theorem.

## 7. Countable current laws now consume a constructed solution

For any `DomainAtlas` of this diagonal operator, not only its spectral coordinate atlas, the existing current theorem is specialized with the newly proved original vector derivative:

\[
\frac{d}{dt}\|P_iU(t)x\|^2=\sum_j J_{ij}(t),
\quad J_{ij}=2\operatorname{Im}\langle P_iU(t)x,HP_jU(t)x\rangle.
\]

`packet_current_hasSum` proves a genuine `HasSum`, not just equality to a totalized infinite-sum expression. The earlier symmetry/domain-invariance argument supplies its summability. For a finite receiving region B, `region_boundary_limit` gives the actual finite-subset limit of currents entering from F minus B. No unrestricted infinite double-array rearrangement is used.

For every strong orthogonal atlas and every initial l2 state, even outside D(H), Parseval and norm preservation give

\[
\sum_i\|P_iU(t)x\|^2=\|x\|^2.
\]

No termwise differentiation of that infinite sum is required. In the spectral coordinate atlas the individual energies are constant and currents are zero, correctly reflecting that this atlas diagonalizes H. The general domain-atlas specialization does not assume that diagonalization.

## 8. Uniform time approximation for a fixed state

The exact cutoff relation is

\[
\|U(t)x-S_MU(t)x\|=\|x-S_Mx\|.
\]

The error is independent of time. Thus for each fixed state and each epsilon, one cutoff threshold works for every real time. This is **not** uniform convergence over the entire unit ball and does not contradict the earlier operator-norm error of one.

Every finite-support cutoff belongs to the actual domain, even when x does not. Its orbit has a proved derivative. For x in D(H), the velocity error is exactly

\[
\left\|\frac{d}{dt}U(t)x-\frac{d}{dt}S_MU(t)x\right\|
=\|Hx-S_MHx\|.
\]

Velocity cutoffs therefore converge uniformly over all real times for a fixed domain state. This additional generator tail cannot be omitted from differentiation arguments.

## 9. Exact infinite-dimensional witnesses

### A rough state and divergent cutoff velocities

In the harmonic model, construct the actual l2 vector

\[
x_n=\frac1{n+1/2}.
\]

Square summability is proved with the p-series theorem. Its weighted coordinates are all one, so the weighted sequence is not square summable and x is proved outside D(H). This witness is nonzero but is not normalized in the package.

Its orbit is continuous and nowhere differentiable in the ambient l2 norm. Nevertheless every coordinate is differentiable, and every cutoff orbit is genuinely differentiable in l2. The exact calculation is

\[
\boxed{\left\|\frac{d}{dt}S_MU(t)x\right\|^2=M\quad\text{for every }M,t.}
\]

Thus the smooth cutoff approximation lacks derivative control; increasing the cutoff does not repair that omission. There is no contradiction with the domain-only derivative theorem.

### Strong continuity without operator-norm continuity

Let t_n=pi/(n+1/2). Lean proves t_n tends to zero, while the n-th phase is exactly minus one. Testing that coordinate gives the norm lower bound two; the unit-modulus upper bound gives equality:

\[
\boxed{\|U(t_n)-I\|=2.}
\]

`not_operator_norm_continuous` uses these limits to refute continuity at zero in the bounded-operator norm. The all-state strong continuity theorem still holds.

### Nonzero observable rate on a global normalized solution

The actual domain state is

\[
\psi_0=\tfrac35 e_0+\tfrac45 i e_1,\qquad\|\psi_0\|=1.
\]

Its constructed orbit remains normalized for every real time and obeys the proved original Schrödinger equation. Define the coherent coordinate amplitude z(t)=psi(t)_0+psi(t)_1. Then

\[
z(0)=\tfrac35+\tfrac45 i,\qquad z'(0)=\tfrac65-\tfrac3{10}i,
\]

and the actual quadratic-observable derivative is

\[
\boxed{\left.\frac{d}{dt}\frac{|z(t)|^2}{2}\right|_{t=0}=\frac{12}{25}\ne0.}
\]

This is a global normalized solution, not a local affine witness. The module checks the coherent quadratic expression and its derivative; it does not separately construct a new non-spectral projector atlas for this example.

## 10. Audit and remaining boundaries

The cumulative verifier recompiles all 58 mathematical modules and the aggregate with one worker and warnings as errors, audits all 1,172 inventoried names, and tests all 81 invalid controls. Eight new controls reject domain inclusion of the rough state, coordinatewise differentiation as sufficient, automatic smoothing into the domain, operator-norm continuity, zero half-turn norm error, bounded rough-cutoff velocities, and two wrong coherent-observable rates. Each control needs its own intended diagnostic in its mapped source range. Import errors, timeouts and a nonzero batch exit alone do not pass the contract.

All 52 prior mathematical files are checked against the new block10 preservation layer; older layers remain active. The full v0.10.0 baseline was freshly verified before extension. New active sources contain no admissions, custom axioms, native evaluation or kernel-bypass options. Only propext, Classical.choice and Quot.sound are permitted dependencies. The existing pinned Lean/Mathlib cache is reused, not rebuilt wholesale. Lean is 4.34.0-rc2; Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The exact runtime is external, with checksum restoration support included.

Completion of this block does not establish a general Stone theorem, a general non-diagonal spectral representation, equivalence with the differential oscillator on L2(R), the square-root form-domain hierarchy, graph-norm differentiability without further domain assumptions, heat-semigroup time derivatives, infinite coarse-cell domain/current rearrangement, nonlinear or dissipative flow existence, density positivity preservation, continuum gravity/cosmology or empirical adequacy. Prior statements retaining a supplied flow hypothesis remain valid as general interfaces; this block discharges that hypothesis for the diagonal spectral model only.

**Next source target: Section 6.5, (6.42)–(6.47).** Construct actual strong coarse projectors for infinite cells, prove their domain compatibility where justified, and separate state/energy regrouping from the stronger convergence needed to expand unbounded-generator coarse currents. Per-row absolute current summability is not global double-array summability.
