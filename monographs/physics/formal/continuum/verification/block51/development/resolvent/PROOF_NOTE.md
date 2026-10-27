# Nonreal centered resolvents

Base: checked physics generator source archive SHA-256
`a4bbe33f081240bf9b71b0387c7f10052bf4f5daa03513b1c3ea25d18616cf77`,
containing the preserved Block 49 archive SHA-256
`413b107ea21130ce45ff6ae261263d3a326e63047dfe1d9a389543f0928891aa`.

The target is the strong-resolvent theorem in section 3 of the accepted
`Block50_Spectral_Generator_Bridge.tex`, with physical Fourier transport.
The final production module is
`KomorebiPhysics/Relativistic3DCenteredResolvent.lean`.

## Exact contract

For every real mass, every complex parameter with nonzero imaginary part, and
every vector in the same infinite coefficient Hilbert space, construct actual
centered and continuum resolvents, prove their inverse laws and uniform norm
bound, and prove strong convergence as real spacing tends to zero through either
sign. The continuum resolvent range must lie in the existing maximal Hamiltonian
domain. The same claims and error estimate must transport to the existing
physical torus Hilbert space.

No changing finite grid, conditional resolvent-existence premise, empirical
physical interpretation, or abstract unbounded exponential identification is
part of this claim.

## Proof mechanism

1. A bounded self-adjoint modal operator has real spectrum. The pinned Mathlib
   C-star spectrum theorem therefore proves that its shift by a nonreal complex
   parameter is a unit. `Ring.inverse` gives the actual two-sided inverse.
2. The imaginary part of the quadratic form gives
   `|Im z| * ‖v‖ ≤ ‖A v - z • v‖`. Applying this inequality to the inverse output
   proves the uniform bound `‖R(z)v‖ ≤ |Im z|⁻¹ * ‖v‖`.
3. The proved uniformly bounded modal family defines an actual continuous
   linear operator on the infinite square-summable coefficient space.
4. The continuum inverse identity gives `H R(z)f = f + z R(z)f`. The right side
   is square summable, which supplies a genuine maximal-domain witness.
5. Both inverse identities imply
   `R_h(z)f - R(z)f = R_h(z)(H - H_h)R(z)f`. The uniform inverse bound and the
   independently proved full graph-domain limit yield strong convergence for
   every coefficient vector.
6. Unitary Fourier conjugation transports the domain, both inverse identities,
   operator-norm bounds, graph-error estimate, and convergence to physical
   torus L².

The modal resolvent uses the original filled symbol at zero spacing, which is
the continuum symbol. The bounded centered Hamiltonian uses an auxiliary zero
value there. Consequently all identities relating those two families explicitly
require nonzero spacing, and the final limit is punctured.

## Executed verification

`run_004.json` records the final strict source compilation with
`-j1 -DwarningAsError=true`. It exited 0 with an empty log. It checks the complete
module against the pinned dependency objects, not just a theorem statement.
The final module contains 28 theorem declarations, 6 definitions, and
4 abbreviations. The parent release gate separately performs the complete API,
axiom, mutation, and kernel replay checks.

Final source SHA-256:
`937d369dc7ccc5c1bfb337d5fc4e13b3ffbb93536e04634f650714fe8b8bc909`.
Final development object SHA-256:
`2babf31b6509785dd63f2607257bd936325dfc662a582a418722578eb77ce1c3`.

## Retained failures

The first two isolated modal compilations failed on a missing continuous-linear
map C-star instance and complex coercion simplification. The missing instance
caused elaboration heartbeat exhaustion. The third isolated run compiled with
one unused-section-variable warning, removed in production.

Production run 1 failed on an underdetermined constant-limit expression and
over-expanded physical inverse identities. Run 2 retained one transported-domain
coercion rewrite failure. Run 3 passed. Run 4 adds three explicit physical
estimates at the reviewer's and coordinator's request and also passes. These
unsuccessful production/modal attempts are implementation failures, not
counterexamples to the mathematical target.

The first control cycle failed because imported namespaces made test type aliases
ambiguous. Its aggregate result was FAIL. Two individual rejection booleans were
also unusable because the initial forbidden-diagnostic scanner missed the capital
letter in `Ambiguous`. `CONTROL_RUN_001_INVALIDATION.json` explicitly invalidates
those interpretations while preserving the raw records. The corrected test
files use unique alias names and case-insensitive forbidden-diagnostic screening.

## Restart and scope

Use the final module and the parent's final integrated verification receipt.
Do not reclassify this block as sampled-lattice convergence, an interacting-field
construction, the abstract Stone API linkage, or a repair of the cosmology
production and cutoff failures.
