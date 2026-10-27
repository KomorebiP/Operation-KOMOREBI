# Komorebi Physics v0.46.0 — Deep progress audit

## Executive assessment

Block 46 removes the finite Fourier cutoff from the free Dirac propagator convergence theorem. The continuum and central-difference evolutions now act on the complete coefficient Hilbert space

\[
\ell^2(\mathbb Z^3;\mathbb C^4),
\]

not merely on a fixed finite packet. Both evolutions are exact unitary linear isometric equivalences, and the lattice evolution converges to the continuum evolution uniformly on every fixed compact time interval for every square-summable coefficient field.

This closes the principal stability and cutoff-removal problem for the free Fourier-diagonal matter sector. It does not yet identify the coefficient-space theorem with a formally constructed physical torus `L²` evolution, nor does it define the full unbounded Dirac generator and its weighted domain.

## Dependency-weighted completion estimates

These percentages measure unresolved scientific dependency depth rather than theorem count.

| Program layer | Current estimate | Assessment |
|---|---:|---|
| Finite local quantum/operator foundation | 92–96% | Mature: exact Clifford dynamics, Hilbert unitarity, gauge covariance, finite propagation, operator domains, and reconstruction machinery are formalized. |
| State-space discrete-to-continuum bridge | 95–98% | Euclidean dyadic `L²` density and strong finite-resolution projection convergence are checked. Fourier coefficient to physical torus `L²` transport remains. |
| Free Dirac continuum dynamics | 88–92% | Generator consistency, finite-packet propagation, compact-time control, exact stability, and full coefficient-space cutoff removal are checked. Unbounded operator/domain identification remains. |
| Background abelian gauge refinement | 75–82% | Exact link refinement, curvature budgets, regular-connection scaling, and summable refinement defects are checked. Gauge-covariant continuum propagation remains. |
| Dynamical gauge-field sector | 20–30% | Background links and holonomy are formalized, but independent gauge degrees of freedom, Gauss law, field energy, evolution, and backreaction are not complete. |
| Emergent geometry/tetrad sector | 10–18% | Refinement geometry and holonomy exist, but no complete metric/tetrad reconstruction or covariant constraint system is proved. |
| Quantum gravity and constraint closure | 5–12% | The required Hamiltonian/diffeomorphism constraints, anomaly-free closure, and spin-two infrared sector remain largely open. |
| Cosmology and observables | 5–10% | No complete cosmological dynamics, perturbation theory, or observational pipeline is yet checked. |
| Entire original Komorebi Physics vision | **42–48%** | Midpoint estimate: **about 45%**. |
| Narrow discrete-local/global-continuous matter framework | **88–92%** | Midpoint estimate: **about 90%**. |

The large gap between the narrow and full estimates is deliberate. The free-matter continuum bridge is near maturity, while dynamical gauge fields, geometry, gravity, and cosmology contain fewer existing modules but much greater unresolved conceptual depth.

## What Block 46 proves

### Complete coefficient Hilbert space

The mode set is the integer momentum lattice

\[
\mathrm{Mode}=\mathbb Z^3,
\]

encoded as `Fin 3 → ℤ`. A full four-spinor Fourier field is

\[
f=(f_n)_{n\in\mathbb Z^3}
\in
\ell^2(\mathbb Z^3;\mathbb C^4).
\]

The general construction `modewiseIsometry` proves that any family of norm-preserving mode operators induces an exact linear isometry on the complete coefficient space.

### Full continuum and lattice evolutions

The continuum propagator acts modewise by

\[
(U(t)f)_n=e^{-itH_n}f_n.
\]

The central-difference propagator acts by

\[
(U_h(t)f)_n=e^{-itH_{h,n}}f_n.
\]

The preceding Hilbert-stability block proves each mode operator is unitary. Block 46 therefore proves

\[
\|U(t)f\|=\|f\|,
\qquad
\|U_h(t)f\|=\|f\|.
\]

Opposite-time identities imply surjectivity, so both maps are packaged as linear isometric equivalences. Their time-group laws hold on the complete coefficient space.

### Canonical finite truncations

For a finite mode set `S`, `coeffTruncation S f` retains the coefficients in `S` and sets all others to zero. Lean proves that the series of singleton coefficients sums to `f`. Therefore

\[
\forall\varepsilon>0,
\quad
\exists S\subset\mathbb Z^3\text{ finite},
\quad
\|f-P_Sf\|<\varepsilon.
\]

This is the density theorem used to remove the cutoff.

### Finite-core error

For a finite truncation, the squared coefficient residual is exactly

\[
\|U_h(t)P_Sf-U(t)P_Sf\|^2
=
\sum_{n\in S}
\|(U_{h,n}(t)-U_n(t))f_n\|^2.
\]

The coefficient residual norm is formally identified with the torus finite-packet residual from the previous blocks. It therefore inherits the checked compact-time quadratic estimate

\[
\|U_h(t)P_Sf-U(t)P_Sf\|
\le K_S h^2
\]

uniformly for `|t| ≤ T` and sufficiently small positive `h`.

### Cutoff removal

Exact norm preservation gives the two-tail inequality

\[
\|U_h(t)f-U(t)f\|
\le
2\|f-P_Sf\|
+
\|U_h(t)P_Sf-U(t)P_Sf\|.
\]

Given `ε > 0`, choose `S` so the tail is below `ε/4`, then choose `h` so the finite-core error is below `ε/2` for all `|t| ≤ T`. Lean concludes

\[
\forall\varepsilon>0,
\quad
\forall^{\mathrm{eventually}}h\to0^+,
\quad
\forall |t|\le T,
\quad
\|U_h(t)f-U(t)f\|<\varepsilon.
\]

This is compact-time strong convergence on the complete coefficient Hilbert space.

## Why no global quadratic rate is claimed

A fixed finite packet has an `O(h²)` propagator error. An arbitrary square-summable field may have a Fourier tail with no prescribed regularity or moment bound. The cutoff-removal argument proves convergence, but its chosen cutoff depends on the requested tolerance. It does not produce one universal `O(h²)` constant for every `f ∈ ℓ²`.

A global rate would require additional regularity, such as weighted square summability corresponding to Sobolev control. Block 46 deliberately avoids overstating this.

## Verification evidence

### Production tree

- direct warning-as-error compilation: pass;
- module import-closure build: pass, 3,058 jobs in the cache-warm final run;
- public API: 40 of 40 declarations checked;
- theorem audit: 29 of 29 theorem declarations checked;
- observed imported axioms: `Classical.choice`, `Quot.sound`, `propext` only;
- source trust scan: no `sorry`, `admit`, `native_decide`, `unsafe`, or custom `axiom`;
- negative controls: 3 of 3 rejected;
- predecessor preservation: 886 parent Lean files byte-identical, with only the expected integration root changed and one new module added.

### Clean extraction

The candidate source archive was extracted into a new directory and attached to the pinned offline runtime. Three long dependency-build invocations ended at 3,055/3,058, 3,056/3,058, and 3,057/3,058 jobs when their external command windows closed. They are recorded as inconclusive rather than passes.

On the unchanged extracted tree:

- all 3,057 predecessor dependency jobs were completed across the resumptions;
- the Block 46 source passed direct warning-as-error compilation;
- a fresh Block 46 object file was emitted;
- 40 API declarations passed;
- 29 theorem axiom audits passed;
- all 3 negative controls were rejected;
- 895 Lean/configuration files matched the production candidate byte-for-byte.

The release classification is therefore `checked modular cumulative`, not a claim that one monolithic clean Lake invocation emitted a 3,058-job terminal receipt.

## Failure record

The following operations were excluded from proof evidence:

1. two partial predecessor builds before the production dependency closure completed;
2. one direct-compile wrapper invoked from the wrong directory;
3. one combined negative-control loop that stalled after the first rejection;
4. three fresh Lake invocations that stopped at 3,055, 3,056, and 3,057 jobs;
5. any status poll, cached file existence, or prose summary without a terminal proof gate.

## Exact remaining boundary

Block 46 does not yet prove:

- a formal unitary Fourier-series equivalence with physical torus `L²`;
- that the coefficient propagators are conjugate to operators on physical torus fields;
- the full unbounded continuum Dirac operator and its weighted Fourier domain;
- self-adjointness of that unbounded operator;
- identification of the continuum coefficient propagator with its spectral functional-calculus exponential;
- strong-resolvent convergence;
- gauge-covariant full-space propagation;
- dynamical gauge-field equations or matter backreaction;
- emergent metric gravity, cosmology, or empirical predictions.

## Next load-bearing program

The next efficient sequence is:

1. construct the four-spinor Fourier-series unitary
   \[
   \mathcal F:L^2(\mathbb T^3;\mathbb C^4)
   \simeq
   \ell^2(\mathbb Z^3;\mathbb C^4);
   \]
2. conjugate `continuumCoeffUnitary` and `centralCoeffUnitary` through `\mathcal F`;
3. transport compact-time strong convergence to physical torus `L²`;
4. define the weighted Fourier domain of the full continuum Dirac Hamiltonian;
5. prove self-adjointness and identify the spectral propagator;
6. only then address strong-resolvent convergence and gauge-covariant interactions.
