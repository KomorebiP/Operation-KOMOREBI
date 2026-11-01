# Physics collection

**Komorebi P.**

How does a state exchange probability between its parts? What changes when we alter its phase, coordinates or spatial resolution? This collection follows those questions from small calculations to the free Dirac field, then into finite models of energy exchange and cosmological research.

Begin with a calculation you can inspect. Each selection connects to its written mathematics, available code and recorded evidence. The [Physics book](works/monographs-physics.md) provides the main reading volume.

## Choose a starting point

| Explore | Start here | Continue to |
|---|---|---|
| Probability flowing between packets | [Run the two-packet rotation](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-current) | [Local balance and boundary currents](#packet-current) |
| Phase and quantum measurement | [Run the phase comparison](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-phase) | [Exact probabilities and dephasing](#quantum-phase) |
| A discrete symbol approaching a continuum one | [Run the centered-symbol comparison](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-centered) | [The formal continuum extension](#continuum-limit) |
| Functions, recurrences and recovery | [Explore the existing sequence plots](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#sequence-growth) | [Special Functions](#special-functions) |
| Energy exchange and backreaction | [Read the finite model](works/physics-energy-backreaction.md) | [Conservation and physical acceptance](#energy-exchange) |
| Origin locking and curved backgrounds | [Read the research sequence](#origin-and-curvature) | [Origin locking](works/physics-origin-locking.md) and [curvature states](works/physics-curvature-states.md) |

The browser examples run when you press **Run**. They use the Python standard library; the playground supplies plotting and downloads. Their code is editable and downloadable. The calculations below also work as a reading route without running software.

<a id="packet-current"></a>

## Probability moves between packets

Split a vector into orthogonal packets with projectors $P_i$. Let its trajectory satisfy $\dot\psi=A\psi$, where $A$ is a bounded skew-adjoint operator. For a finite complete orthogonal atlas, define

```math
e_i=\|P_i\psi\|^2,\qquad
J_{i\leftarrow j}=2\operatorname{Re}\langle P_i\psi,A P_j\psi\rangle.
```

The inner product is conjugate-linear in its first argument. The receiving packet comes first in the current index. The balance identity is

```math
\dot e_i=\sum_j J_{i\leftarrow j},\qquad
J_{i\leftarrow j}=-J_{j\leftarrow i}.
```

Internal currents cancel when packets are grouped, leaving only current across the group's boundary. Here $e_i$ is a squared norm; interpreting it as a particular physical energy needs the model's additional definitions.

For the coordinate projectors, $A=\begin{pmatrix}0&-1\\1&0\end{pmatrix}$ and $\psi(0)=(1,1)^{\mathsf T}$, the initial packet squared norms are $(1,1)$ and their derivatives are $(-2,2)$. The exact trajectory is $(\cos t-\sin t,\sin t+\cos t)^{\mathsf T}$. Its total squared norm stays at $2$; divide packet squared norms by $2$ to obtain normalized probabilities.

[Run this example](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-current). For the analytic statements and their hypotheses, follow the [source-to-Lean map](../monographs/physics/formal/continuum/docs/SOURCE_MAP.md): `Atlas.hasDerivAt_subset_energy` derives the boundary balance from the supplied vector evolution equation. The map also distinguishes a supplied trajectory from a theorem of flow existence.

<a id="quantum-phase"></a>

## Quantum phase changes interference

The normalized states $\psi=(3/5,4i/5)^{\mathsf T}$ and $\phi=(3/5,4/5)^{\mathsf T}$ have the same coordinate probabilities, $(9/25,16/25)$. After the Hadamard transformation their probabilities are respectively

```math
(1/2,1/2)\quad\text{and}\quad(49/50,1/50).
```

Equal probabilities in one basis therefore leave information about relative phase unresolved. Forgetting the result of a coordinate measurement removes the off-diagonal density-matrix entries; the resulting purity is $337/625$ for either of these states.

[Run the comparison](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-phase), then follow the [complete hand calculation](examples/17_QUANTUM_MEASUREMENT.md) into [Paper VII](works/paper-vii.md). The [Quantum and Circuits book](works/monographs-quantum-and-circuits.md) extends the reading route into arithmetic, symmetry, finite gate costs and projected quantum trajectories. Its [edition guide](../monographs/quantum-and-circuits/README.md) separates the written results, finite computations and selected formal developments.

The extended [phase, measurement, and information-loss derivation](demonstrations/QUANTUM_PHASE_MEASUREMENT.md)
continues through exact tomography, partial dephasing, coherent versus classical
records, and parity-packet refinement. [Run its editable coherence experiment](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-dephasing)
and export the exact measurement probabilities and purity.
The same walkthrough includes amplitude damping, three-qubit syndrome
recovery, and the Quantum and Circuits book's modulus-12 arithmetic phase
example. [Run the arithmetic comparison](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-arithmetic-phase)
to distinguish coherent sign replacement from complete coordinate dephasing.

Continue in Paper VII's illustrated chapters on
[measurements](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-vii/measurements.html),
[Kraus channels](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-vii/quantum-channels.html), and
[error correction](https://KomorebiP.github.io/Operation-KOMOREBI/read/paper-vii/error-correction.html).
Their statement/proof links lead into the retained manuscript, with figures
displayed inline and text descriptions available alongside them.

<a id="continuum-limit"></a>

## Centered approximation reaches the free continuum field

A centered spatial symbol replaces a momentum coordinate $k$ by

```math
s_h(k)=\frac{\sin(hk)}{h},\qquad h\ne0.
```

The scalar error obeys $|s_h(k)-k|\le h^2|k|^3/6$. [Compare the symbols and their errors](https://KomorebiP.github.io/Operation-KOMOREBI/playground.html#physics-centered). The plot keeps the momentum fixed while changing spacing. For momentum $(1,2,-1)$ and a unit spinor, the modal operator-error envelope is $h^2\sqrt{66}/6$. The downloadable CSV contains four floating-point comparisons.

The larger result concerns the free Dirac field on a fixed flat torus. The centered and continuum operators act on the same infinite Fourier coefficient space. For a square-summable Fourier spinor field $f$, write $k_j(n)$ for the physical momentum coordinates of mode $n$, and define

```math
M_3(f)^2=\sum_n\left(k_1(n)^6+k_2(n)^6+k_3(n)^6\right)\|f_n\|^2.
```

When this series is summable and $h\ne0$, the recorded extension proves

```math
\|(H_h-H)f\|\le\frac{h^2}{6}M_3(f),\qquad
\|(U_h(t)-U(t))f\|\le\frac{|t|h^2}{6}M_3(f).
```

The compact-time version retains $|t|\le T$ and $T\ge0$. The extension also records graph-domain convergence on the full maximal Hamiltonian domain and strong resolvent convergence for every nonreal spectral parameter and every square-summable input. The latter does not require the third-order moment. See the [proof guide](../monographs/physics/formal/continuum/docs/BLOCK_51_PROOF_GUIDE.md) for the constructions and the distinct hypotheses.

The rate is linked to [`centered_generator_quadratic_bound` and its neighboring propagator results](../monographs/physics/formal/continuum/KomorebiPhysics/Relativistic3DCenteredRates.lean). The [accepted receipt](../monographs/physics/formal/continuum/verification/block51/current/receipt.json) records the scoped Lean gate; the [formal edition guide](../monographs/physics/formal/continuum/README.md) gives the pinned runtime, replay command and trust boundary. The browser samples illustrate the modal estimate and add no formal coverage.

The fixed Fourier-space result leaves finite sampled-grid comparison, the abstract spectral-functional-calculus linkage and interacting-field evolution as separate obligations. The auxiliary bounded global operator at zero spacing has its own convention; it must not be substituted into the nonzero-spacing inverse laws. Cosmological production also remains a separate research problem.

<a id="special-functions"></a>

## Special functions connect coefficients and recovery

The [Special Functions collection](SPECIAL_FUNCTIONS.md) brings together a monograph, worked visual lessons, a coupled-function atlas and the original series. Use its [reading map and reproduction guide](../monographs/special-functions/README.md) to choose between the books, recurrence laboratories and exact computations. Read the original series together with its consolidated correction register.

The [current formal status](../monographs/special-functions/LEAN_STATUS.md) records selected results on the coupled recurrence, coefficient positivity, local convergence, tail bounds and generic recovery. The remaining analytic and global continuation obligations are listed there. The [sequence plotting guide](demonstrations/SEQUENCE_SHAPES.md) supplies a related computational entry point; a shared coefficient vocabulary alone does not establish a physical model.

<a id="energy-exchange"></a>

## Finite energy exchange has a conservation theorem

The [Energy and Backreaction study](works/physics-energy-backreaction.md) derives conservation of mechanical-plus-mode energy in a finite regulated quantum model, together with nonnegative occupations and an energy bound. Its [edition guide](../research/physics-energy-backreaction/README.md) links the written proof, independent oscillator implementation, sampled trajectories and reproduction commands.

This is a useful second kind of exhibit: an exact finite conservation law can coexist with an unsuccessful attempt to remove regulator dependence. The study's attempted physical depth-independence gate fails. Its measured numerical energy residual is also distinct from the theorem and from a certified solver-error bound. The original cosmological production benchmark remains unrepaired.

For reproduction, start with the guide's saved-result checker. Its stricter physical-acceptance command deliberately returns exit code $3$ for the retained failed gate. Keep that distinction when presenting the result.

<a id="origin-and-curvature"></a>

## Origin locking and curvature remain research checkpoints

The [Origin Locking supplement](works/physics-origin-locking.md) follows the finite energy study into matching, locking and homogeneous expansion. Its [edition guide](../research/physics-origin-locking/README.md) records the corrected locking target $q=0$, finite pressure-work and Friedmann identities, reproducible configurations and two retained failed gates. The accelerated-expansion stress test remains momentum-cutoff dependent; some highly occupied altered-model long runs also fail an absolute mode-hyperboloid check in double precision.

The [Curvature States and Conserved Subtraction checkpoint](works/physics-curvature-states.md) continues into initial-state and subtraction questions. Its [source guide](../research/physics-curvature-states/README.md) identifies the supplied study and verification records. Reproducible code, stored arrays, figure source and editable manuscript source were not located for that checkpoint, so present it as a research record with that limitation.

## Follow a complete reading route

For a short introduction, run the packet-current and quantum-phase examples, then read their calculations above. For a technical visit, continue through the centered-symbol plot, formal proof guide, exact Lean types and accepted receipt. For research discussion, finish with energy exchange, origin locking and curvature, keeping their different models and acceptance criteria explicit.

[All reading routes](READING_ROUTES.md) · [Physics book and proof sources](works/monographs-physics.md) · [Browse every work](BROWSE.md) · [Evidence labels](COMPLETION_STATUS.md) · [Download selections](DOWNLOADS.md)
