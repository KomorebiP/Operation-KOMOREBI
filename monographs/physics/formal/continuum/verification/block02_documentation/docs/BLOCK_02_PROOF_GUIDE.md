# Block 02: moving frames and whole-object deformation

## Result and scope

This block formalizes Chapter 2.5 and Chapter 2.6 of the 550-page full physics master in a bounded-operator / normed-algebra setting. It is a mathematical continuation, not an empirical validation of a physical model. The machine-verification outcome is in `verification/final/report.json`; this explanatory note is not a substitute for that outcome.

The central result has only these mathematical inputs: a complete normed real algebra R, actual derivatives U'(t)=dU and X'(t)=dX, and invertibility of U(t). P and Q are fixed elements of R. For physical projector interpretation, supply the fine projector laws separately. P and Q are fixed reference projectors. Identifying them literally with the transported values at time zero additionally requires the appropriate initial normalization, such as U(0)=I; the local derivative theorem does not require that normalization. The derivative identity is stronger algebraically: it does not need P and Q to be idempotent.

Set

    p(s) = U(s) P U(s)^{-1},
    q(s) = U(s) Q U(s)^{-1},
    K    = dU U(t)^{-1}.

Then the actual derivative at t is

    (p X q)' = p dX q + [K,p] X q + p X [K,q].

The inverse operation in Lean is `Ring.inverse`. Away from invertible elements it is a totalized operation. The theorem assumes invertibility at the base point, and the imported Banach-algebra inverse calculus establishes the local derivative there. No physical interpretation is assigned to a noninvertible frame.

## Public mathematical derivation

1. Inversion has derivative `-U^{-1} dU U^{-1}` at an invertible element. The Lean theorem composes this Fréchet derivative with the actual real-time derivative of U.
2. Differentiate `U P U^{-1}`. Associativity and `U^{-1}U=1` turn its two terms into `[dU U^{-1},p]`.
3. Differentiate the three-factor product `p X q` without changing operator order. Substitute the projector derivatives from step 2. This produces all three terms in the displayed theorem.
4. Noncommutative algebra rewrites the same rate as `[K,p X q] + p(dX-[K,X])q`.
5. Sum over a finite resolution of the identity. The sum of `[K,P_i]` is `[K,I]=0`, so all frame terms cancel and the derivative of the reconstructed object is dX.

## Why the moving-coordinate bridge matters

For a unitary operator curve, define

    phi(s) = U(s)* psi(s),
    Gamma  = U(t)* dU,
    A_eff  = U(t)* A U(t) - Gamma.

The new code differentiates `U* U=I`, derives skew-adjointness of Gamma, differentiates the actual phi trajectory, and obtains `phi'(t)=A_eff phi(t)`. If A is skew-adjoint, A_eff is too. The proof then invokes the Block 01 energy theorem with the derived trajectory, yielding a genuine zero derivative of the total squared norm.

The moving atlas is constructed, not postulated: `unitaryAtlas` builds `U P_i U*`, proves its exact resolution and projector multiplication laws using `transportedFamily`, and separately proves self-adjointness. `unitary_atlas_energy` identifies its laboratory packet energies with the energies in moving coordinates. `hasDerivAt_lab_packet_energy` carries the derivative balance back to those actual laboratory norms.

## Hypotheses that cannot be silently removed

A generic invertible frame preserves idempotence and exact reconstruction, but not the Hilbert-space metric. The shear witness proves that distinction exactly. Unitary assumptions are therefore retained for orthogonality, squared-norm identities, and skew-generator claims.

The Hilbert-space layer uses globally defined bounded complex-linear maps and real-time operator-norm derivatives. Completeness is explicit where adjoints or the automatic inverse calculus need it. Strong-operator differentiability alone, countably infinite projector sums, unbounded Hamiltonian domains, flow existence, and continuum limits are not covered by these statements.

The full 550-page manuscript is not claimed complete. Chapter 2's listed core identities now have checked representatives in the declared finite-atlas/bounded setting. The equation map records where statements are definitions, hypotheses, preserved results, new proofs, or added consequences. Chapter 3's physical units, variational sequents, and asymptotic targets are not thereby discharged.

## Exact tests, not numerical tests

The active witness module proves exact real-matrix statements. The shear `I+tN` has inverse `I-tN` for every real t, with N squared zero. The moved projector `P-tN` is idempotent but has a nonzero derivative. At t=1 it is not symmetric. A separate exact three-term witness has rates 4N, -3N, 2N and total 3N. All three deletion alternatives and the reversed commutator have exact disequality proofs.

The deliberately invalid files are isolated under `negative_controls/`. They are required to fail for the intended mathematical diagnostic. Import failures and missing object files cannot count as successful negative controls.

## Reproducibility and counts

The pinned compiler is Lean 4.34.0-rc2. The pinned Mathlib revision is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The verifier deletes local compiled outputs, compiles all ten mathematical modules and the aggregate import with one worker and warnings as errors, and audits the complete 160-name inventory via ordinary `#print axioms` commands in module batches.

There are 51 new theorem declarations in this block, 37 unchanged theorem declarations authored in Block 01, and 39 unchanged recovered Paper VII theorem declarations: 127 total. The 13 new definitions are counted among audited names, not added to the theorem total. The restored imported Lean/Mathlib cache is trusted and was not rebuilt wholesale.
