# Physics continuum convergence target

Checkpoint: PHYS-CENT-51, extending the accepted v0.50.0-g1 generator.

The user requested completion after the recommendation to close the centered-operator and resolvent formal block. This work also includes the manuscript's third-order regularity rates. It does not claim completion of cosmological production, interacting physics, finite sampled-lattice comparison, or the separate abstract spectral-functional-calculus API linkage.

## Pinned base

- Open publication archive SHA-256: d3666da56363b10b6a629f392c9e52247cfa11a802383372877fb93494b24583.
- Checked generator source archive SHA-256: a4bbe33f081240bf9b71b0387c7f10052bf4f5daa03513b1c3ea25d18616cf77.
- Embedded Block 49 archive SHA-256: 413b107ea21130ce45ff6ae261263d3a326e63047dfe1d9a389543f0928891aa.
- Checked generator module SHA-256: ee721cc3ab78f500bab87c1edb358be8b30a0892e7047c9e9cb5aa31a6d51499.

The mathematical target is sections 3 and 4 of the current chapter `The Dirac Group and Its Generator`, with its physical-space corollary. All inherited mathematical modules remain unchanged.

## Required conclusions

1. On the existing infinite coefficient Hilbert space, construct the bounded centered Dirac multiplier for every real mass and nonzero real spacing. Prove its Hermitian/self-adjoint property and the stated uniform mode bound.
2. Prove convergence of its action to the maximal continuum Hamiltonian output for every vector in the full first-order Fourier domain, as spacing tends to zero through both signs. A finite-packet or one-sided result alone does not close this target.
3. Construct the centered and continuum resolvent actions for every nonreal complex spectral parameter. Prove inverse laws, the continuum range/domain property, the bound by the reciprocal of the absolute imaginary part, and strong convergence on every coefficient vector. Merely assuming these properties is insufficient.
4. Define the actual third-order Fourier moment. Under its finiteness, prove the generator error bound h^2 M3/6 and propagator error bound |t| h^2 M3/6 for every real time. Prove the uniform form for |t| <= T with T >= 0.
5. Transport the convergence and estimates through the existing physical torus Fourier isometry.

The proof may not assume the different centered and continuum mode Hamiltonians commute. Strong resolvent convergence must not be relabeled operator-norm convergence. The h=0 extension is auxiliary and must not be used to erase a nonzero-spacing hypothesis.

## Evidence required for acceptance

Fresh exact-source compilation, an inventory including proof-bearing definitions, recursive axiom auditing, successful positive uses, isolated hypothesis-sensitive negative controls, module kernel replay, preserved failed attempts, and exact package/source/log/object bindings. Compiler and pinned external dependencies remain part of the stated trust boundary.

## Work ownership

- Centered operator and graph limit: physics_centered.
- Resolvent construction and convergence: physics_resolvent.
- Sharp regularity rates and physical transport: physics_rates, with modal perturbation support by its child.
- Independent mathematical and source review: physics_review.
- Runtime restoration: physics_runtime.
- Integration, fresh acceptance gates, publication and delivery: root.

Status: active. No new theorem is accepted solely because it is drafted or described here.
