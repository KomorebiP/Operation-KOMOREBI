# Formalization scope: 34 freshly checked theorem constants

- **H12PrincipalSeven (17):** the actual principal and dual matrices, cube and
  commutation identities, exact image/conductor functionals, the primitive cubic
  norm invariant, and the winding-boundary identity.
- **H12NormTransfer (13):** finite weighted telescoping/inversion, finite residue
  trace coefficients, and the polynomial numerators used in the seven-gamma
  identity.
- **H12PrincipalModel (4):** the actual rank-six period-label carries under the
  principal map and collapse of the alternating model cocycle.

Every theorem is compiled with the pinned Lean 4.34.0-rc2 compiler, bundled Std,
one worker and warnings as errors. The complete transitive axiom list of every
exported theorem is audited. Only propext, Classical.choice and Quot.sound may
occur. No project axioms, admitted proofs, unsafe declarations or native_decide
are allowed. A deliberately false equality is required to be rejected.

Not formalized in this block: elliptic gamma and its analytic continuation, the
smooth/global-holomorphic transfer-series convergence, the infinite Fourier
obstruction theorem, the interpretation of the model as a gerbe, or any actual
gamma/model comparison. Those interpretations are ordinary proofs/inputs in
PROOF.md. The finite integer gamma-kernel identities do not falsely claim to be
a formal proof of the analytic infinite-product theorem.

The predecessor ZIP and its historical verification evidence are retained
byte-for-byte. Its inherited declarations are NOT freshly replayed here. The
main phase equality is not a hypothesis hidden inside a claimed solution.
