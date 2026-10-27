# Final edited mathematical source review

Primary verdict: **conditional on named classical inputs**.

The final traditional edition's direct finite derivations and its cumulative corrected 19-item mathematical scope passed this independent written review under the now-explicit domains, normalizations, and hypotheses. The named external standard facts remain separate inputs, especially the exact Lindblad/GKSL representation and correctable-observable-algebra criterion. This verdict does not promote Part II or any numerical examples into the archived Lean formal coverage.

The final sources are pinned in `final_reviewed_sources.json`. In particular:

- Part I `traditional/parts/01_finite_core.tex`: SHA-256 `6343e63851fad35706c147344648959217ca2e03682115af44ac7403f4b2e9ae`.
- Part II `traditional/parts/02_strengthened.tex`: SHA-256 `a0bf61933b7a637e7eae96db287a9f6c77c4773a1886f7f0efefd119aff3e994`.

The main document explicitly inputs the corrected core, strengthened development, all six mathematical supplements, and the retained alternative derivations. The substantive scope in all six supplement copies has exactly the same151 displayed mathematical/align blocks as the raw source, with no missing or added mathematical block. All79 strengthened proof bodies are conserved after normalizing namespace labels, invisible anchors, and whitespace. These are textual conservation checks; mathematical correctness comes from the independent raw read-through and the focused final proof review, not those counts.

## Final correction matrix

| Mathematical obligation | Final result |
|---|---|
| Feshbach hidden inverse, full inverse, and retained-space typing | Passed. Part I requires both hidden and full invertibility and explains equivalence to Schur invertibility. Part II requires hidden and Schur invertibility. Both triangular elimination/lift signs are correct. |
| Raw common-kernel anomaly compression | Passed correction. Compression is stated automatic, operator closure is tested separately, and the conjectural existence target explicitly asks for a specified nontrivial compatible model. |
| Nonzero code for Part II traceless quotient representative, coefficient PSD deduction, and prepared-state recovery extension | Passed. Part II states `k=dim C>=1`; Part I and fifth supplement separately retain zero-code branches. |
| Exact error-span semantics | Passed. One CPTP decoder returns each unnormalized coherent error output with its nonnegative scalar weight; normalized channels in the same span have total weight one. Core full proof establishes both directions and includes empty/zero cases. |
| Syndrome probabilities and complete measurement | Passed. Part II expressly inherits a channel trace preserving on code states and includes the complementary projector. Complement probability on corrupted code output is zero; positive-syndrome probabilities are normalized Gram eigenvalues. |
| Null Gram eigenvalues and complex index/sign conventions | Passed. Zero transformed errors are removed before square roots. Fifth supplement's polarization identity and corrected cross term `C_ba` are right; both unitary diagonalization conventions in Parts I and II are internally consistent. |
| Orbit/cyclicity dimension boundary | Passed. Positive addressed dimension is explicit. The standalone Part II orbit theorem allows `m>=0`, so the Schmidt corollary's empty remote factor is covered. Empty block supremum is explicitly0. |
| Spacing and cyclic modulus | Passed. Core dispersion requires `h!=0`, with physical spacing positive. Part II's initial and reopened cyclic conventions explicitly state an integer `N>=1` and unitary symmetry. `N=1`, zero/negative frequency and empty tensor factors retain the correct interpretations. |
| Empty approximate-error family | Passed. Its defect maximum is assigned0 explicitly. |
| Empty packet heat quotients | Passed. The heat-weight sum explicitly ranges only over positive packet heat traces; no `0/0` local dimension is multiplied by a zero weight. |
| Self-energy comparison spaces and normality | Passed. Both hidden blocks are expressly self-adjoint on one identified hidden space, and both coupling maps have the same retained target. The uniform family corollary expressly uses fixed identified spaces and self-adjoint hidden Hamiltonians. The nonnormal raw-scope witness is excluded by these necessary hypotheses. |
| Kato transport, moving-frame sign and moving-packet leakage | Passed. The canonical generator is skew-adjoint, the invariant conjugate is `W* P W`, the frame term is `-iK`, and the off-packet Duhamel coupling is `Q(H-iK)P`. Continuous finite `H(t)` on the compact interval is now explicit, so the integral proof has its required regularity. |
| Global projected range bundle and curvature | Passed. Actual local range products come from a near-anchor invertible intertwiner; curvature includes the actual Lie bracket and retains noncommutative order. Scope is boundaryless real smooth differential calculus, including complex Hilbert spaces through their real differential calculus. |
| Retained exterior-form curvature alternative | Passed. The exterior extension on bundle-valued forms is expressly defined, making `nabla^2` unambiguous. The retained Duhamel and restricted low-mode alternatives also remain valid under their stated hypotheses. |
| Finite transfer/ground energy | Passed. Nonzero finite Hilbert space is stated before choosing `min Spec H`; the excited-gap convergence result separately requires an excited eigenvalue. |
| Bounded/direct/trace-norm limits | Passed. Fixed finite packet addresses, common Hilbert-space norm limits, orthogonal projector/self-adjoint Hamiltonian assumptions, and trace-class heat and moment assumptions are explicit. These do not assert an unbounded physical Hamiltonian or interacting continuum existence. |
| Choi and channel conventions | Passed. Choi order is output tensor input; covariance uses `U tensor conjugate(U)` and TP takes the output partial trace. Root-level Watrous source authentication separately discharges that exact standard input. |
| Finite-group coefficients | Passed by independent averaging reconstruction in `FINITE_GROUP_RECONSTRUCTION.md`, including dimension normalization and coefficient `pi(g^-1)_ji`. This is mathematical reconstruction, not exact Serre-source authentication. |
| Theta transformation and fixed-time torus dimension | Passed mathematical application. Root-level DLMF source authentication supplies the exact Gaussian theta identity. The result selects one positive diffusion time per epsilon and then sufficiently large lattice; it does not assert an unstated uniform interval or a joint `t(N)->0` limit. |
| Lindblad generator source and convention | Conditional external input. Final text explicitly uses finite norm-continuous CPTP semigroups in the Schrödinger picture. Charge preservation of the displayed generator is independently proved algebraically. Exact primary representation theorem access failed, as recorded in `LINDBLAD_SOURCE_CHECK.json`. |
| Correctable observable-algebra theorem | Conditional external input. Final statement specifies a finite CPTP channel, a unital code star algebra, and the correct Heisenberg recovery composition `Phi* circ R*`. The scalar code case is internally proved in Part I/fifth supplement. No independent exact-source authentication of the general algebra theorem is asserted here. |

## Dependencies, remaining gate and safe statement

The dependency graph and full raw obligation matrix are in `WRITTEN_PROOF_AUDIT.md`; the final corrections above discharge its raw hypothesis/type failures. The finite-group leaf is discharged by elementary finite unitary averaging; the Choi/Kraus and theta leaves have separate root primary-source reports. Finite Hermitian diagonalization and ordinary finite complex linear algebra remain classical background, with the formal checkpoint's own imports and trust boundary recorded by the separate formal audit.

There is no remaining concrete missing implication in the corrected direct finite derivations found by this pass. The remaining gate is exact-source authentication of the explicitly named Lindblad/GKSL and general observable-algebra-correction inputs. Keeping them named standard facts, with their source limitations visible in the evidence guide, is faithful to this review.

The strongest safe conclusion is that the complete amended finite written argument is coherent, all six mathematical supplement scopes are integrated, and Part II's extensions are mathematically sound under their now-explicit hypotheses and external inputs. The five physical continuum milestones remain separate open requirements. Neither the151 preserved mathematical blocks,79 proof bodies,269 exact finite arithmetic assertions, nor archived declaration counts substitute for those physical proofs.

## Checks performed and limits

All eight reviewed raw manuscript byte strings still match `reviewed_sources.json`. Final source hashes and the produced PDF hash are separately pinned. The strengthened proof comparison was rerun on the settled source; all79 bodies match. No raw source was edited by this auditor. The exact rational script was independently reviewed and replayed successfully, with269/269 finite assertions and output equality; the arithmetic replay remains finite-only evidence. This pass did not run a new Lean compiler check or independently authenticate every Mathlib import, and it did not rerun the author's historical numerical experiment suite.
