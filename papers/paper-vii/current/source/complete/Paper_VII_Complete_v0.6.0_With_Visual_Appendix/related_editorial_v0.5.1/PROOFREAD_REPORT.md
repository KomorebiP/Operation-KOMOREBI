# Paper VII: final proofreading and integration report

**Komorebi P.**  
**Edition:** 0.5.1, 6 September 2026  
**Input:** `PRSC_VII_v0.5.0_Checked_Fifth_Block.zip`  
**Primary revised paper:** `manuscript/Paper_VII_Proofread_Integrated.pdf`

## Disposition

**The registered finite framework passes this review, with the corrected hypotheses and meanings now printed in one integrated paper.** The finite register remains 19/19 and the Lean corpus remains 296 named theorem declarations in 27 modules. No new theorem declaration was added, removed or changed during this editorial pass. Every local proof module was nevertheless freshly compiled and its theorem audits rechecked.

The old main PDF was not a self-contained statement of the final checked scope. It still required amendments and supplements to correct or qualify several assertions. That was the principal release issue. The current 31-page PDF integrates these amendments and develops the two final results in the body, while retaining the original section/result numbering and all 19 figures.

The 55 recorded edits include exposition, assumptions, proof integration, claim boundaries and layout. They are not 55 distinct mathematical errors. The original PDF, original TeX and all five historical supplements remain unchanged. An exact source diff is supplied.

## 1. Final two results integrated into the body

### Projected connection: Classical Input 6.4

The previous short statement did not communicate the completed geometric construction and its scope. The revised statement explicitly uses a smooth real manifold without boundary and finite-dimensional real ambient fibers, with the quantum case interpreted through the underlying real space of a complex Hilbert space.

The proof now constructs `T_a(x) = P(x)P(a) + (I-P(x))(I-P(a))`, proves local invertibility and the intertwining relation, and gives the range-coordinate transitions. These show local rank constancy and provide smooth bundles on open rank regions, including disconnected bases with different component ranks. Smooth range sections and the projected derivative are explained before the connection rules and curvature computation.

The curvature expression retains the actual Lie-bracket correction. No commuting-vector-field assumption, global frame or globally constant-rank premise is inserted. The expression `P(dP ∧ dP)P` is interpreted on the range bundle rather than presented as an unsupported formal symbol. This is not a claim of a boundary extension or complex-analytic base-manifold formalization.

### Error correction: Classical Input 8.1

The term “correctable error family” was under-specified without stating normalization and the action of recovery. The revised text defines a complete Kraus recovery, quantifies all coherent combinations of the supplied errors and all code-supported matrices, and permits a nonnegative scalar depending on the error but not the logical input. That scalar is an unnormalized weight, not necessarily a probability.

Necessity now explains the rank-one positivity argument, scalar recovery branches and positive Gram matrix. Sufficiency uses unitary diagonalization of that matrix, removes zero-eigenvalue errors by proving their compressed operators vanish, and normalizes only the positive sectors. The additional unused-space branch makes recovery trace preserving on the entire ambient space. The calculation extends to every finite ancillary dimension through the Kraus positivity result.

A separate normalized-channel statement recovers with scalar one. Zero-code and empty-error-family cases are explicit. This integration neither changes the existing Lean criterion nor treats the three-qubit worked example as the proof of the general equivalence.

## 2. Assumptions and analytic meaning repaired

**Schur–Feshbach, Theorem 9.1.** The paper now requires invertibility of both the eliminated block and the full resolvent matrix. The inverse on the retained space is clearly distinguished from an ambient-space inverse. The proof explains Schur-complement invertibility, and the existing finite counterexample shows why the missing full-resolvent condition cannot be dropped.

**Seed rank and local orbit, Section 2.** Positive block dimensions, zero-space/empty-family conventions, and the nonempty addressed factor in the cyclicity equivalence are explicit. The reduced operator need not be a normalized density matrix for its support calculation. Corollary 2.3 now has a prose proof. Algebraic orbit-span generation is separated from unitary reachability and deterministic state preparation, especially for bipartite systems.

**Cyclic and tensor projectors, Section 3.** The modulus is positive, including the case N=1. The order of the unitary is stated to divide N, not necessarily equal N. Self-adjointness, completeness, and the complete orthogonal factor hypotheses are explicit.

**Circuit and Hamiltonian results, Sections 4–6.** Empty circuits are handled separately. Real times, self-adjoint Hamiltonians, differentiability and orthogonal projectors are stated where used. All analytic norms are Hilbert-induced operator norms. The leakage proof follows the checked differentiation of unitary conjugation and mean-value argument, including negative and zero time. The moving-frame Hamiltonian's Hermiticity is not asserted without Hermiticity of the original Hamiltonian.

**Bloch curvature.** The local scalar-connection convention is stated as `A = -i <u,du>`, so the displayed `+ sin(theta)/2` has an explicit sign convention. The Pauli-commutator calculation is shown. This worked scalar specialization is not counted as another registered Lean theorem.

**Channel and transfer parameters.** The amplitude-damping parameter lies in [0,1]. The Euclidean time parameters are nonnegative, and the finite state space is nonempty when taking the minimum eigenvalue. Operator positivity is not equated with entrywise nonnegativity or reflection positivity of a Euclidean field measure.

**Dispersion and heat trace, Section 11.** The spacing is nonzero. The existing formal bound is stated in its stronger all-real-frequency form, with the fixed-frequency qualification needed for its second-order convergence interpretation. The heat-trace endpoint claim includes its zero-mode hypothesis; the different large-time behavior of a strictly positive operator is stated. A finite spectral-dimension window is not a proof of physical continuum dimension.

**Memory and refinement.** The displayed Volterra derivation uses a time-independent Hamiltonian and fixed projectors; a genuinely time-dependent Hamiltonian needs a two-time propagator. The coarse and fine map types are explicit. A left inverse is not silently treated as an adjoint or an isometric embedding. These are reviewed prose statements, not new entries in the formal register.

## 3. Constraint diagnostic and continuum claims

For finite matrix constraints and the exact common-kernel projector, every constraint annihilates the physical range. The anomaly operator therefore annihilates that range automatically, and its physical compression is zero even when operator closure fails. The revised text includes a small concrete counterexample and explains that a nonzero measured compression contradicts the exact-kernel assumptions or reflects approximation/implementation error.

**Conjecture 12.1 was explicitly amended, not proved.** The former compression-only condition was too weak to serve as the intended closure target. The revised research target asks for operator-level anomaly cancellation in a specified nontrivial model, nonzero physical spaces and compatible refinement. The text also says that the model, dynamics and refinement maps still need specification. This is a strengthening and clarification of the research program, not a new theorem or a claim that a fully specified gravitational model has been constructed.

Uniform bounds on self-energies are not asserted to imply strong-resolvent convergence by themselves. Suitable common-space identifications, compatibility and an actual convergence criterion are needed. The former “logically independent” language was removed because no formal independence theorem was supplied. The five continuum targets remain unproved and are not counted among the 19 finite entries.

## 4. Numerical history and figures

The original report says 22/22 numerical tests passed. That historical claim has not been reproduced in this edition. The numerical Python experiment package and raw JSON/CSV were not recovered, so the paper now labels the reported calculations as archived observations. A displayed floating-point zero is not presented as an independent exact-arithmetic proof. The table contains 23 reported measurements; it is not a reconstructed one-row-per-test ledger for the unavailable suite.

The standalone vector assets were missing from the checked source/evidence bundle. The original PDF retained 19 named embedded figure objects. These were extracted with their resources into individual vector PDFs. Each recovered decoded root drawing stream was compared with its source and matched exactly. A portable recovery utility independently repeated the extraction in a new directory. Recovery does not recreate the experiments, validate their raw data, or alter the plotted values.

The historical module-layout table is retained as documentation of the earlier numerical companion, but its absent Python modules are no longer advertised as files included in the current ZIP. The present archive supplies the actual Lean sources, checker, manuscript sources, figures and evidence.

## 5. Fresh verification record

| Check | Observed result |
|---|---|
| Input ZIP CRC and manifest | PASS; all 367 input checksum entries match |
| Proof source preservation | All 27 Lean files byte-identical to v0.5.0 |
| Clean local Lean compilation | 27/27 modules accepted |
| Registered theorem audit | 296/296 unique names match the inventory |
| Observed transitive axioms | Only propext, Classical.choice, Quot.sound |
| Invalid equality control | Rejected |
| Proof-placeholder control | Rejected with warnings fatal |
| Existing verifier tests | 15 passed |
| Editorial/build tests | 12 passed |
| Manuscript result numbering and crosswalk | 19 entries matched to audited principal targets |
| Original and revised named finite environments | 15 theorems, one corollary, three classical inputs |
| Continuum conjecture environments | Five retained, unproved |
| Final three-pass PDF build | PASS; 31 pages |
| Final LaTeX diagnostics | No warnings, undefined references, overfull or underfull boxes |
| PDF preflight and fonts | Openable, unencrypted, all reported fonts embedded |
| Final visual inspection | All 31 pages rendered and reviewed |

The first Lean orchestration attempt ended incomplete. A separate clean retry accepted the full corpus. The incomplete report remains preserved and is not counted as a partial substitute for the successful run. The new PDF-build helper initially failed to recognize a page-count line wrapped by TeX. That parser was fixed, additional wrapped-line cases were covered by regression tests, and a separate accepted build completed.

Lean's local build directory was initially empty, and old development build products were not used. The pinned Mathlib compiled cache was reused, not independently rebuilt. The verifier is unchanged and still names the v0.5.0 proof collection. This editorial edition adds zero new theorem declarations; historical “new in fifth block” fields are not new-proof claims for v0.5.1.

## 6. Remaining boundary and readiness

No further blocker was identified in the 19-result finite scope during this review. The integrated paper is the appropriate reading copy of that scope. This is not a claim that every unnumbered sentence, numerical observation or physical interpretation is certified by Lean, nor an automated theorem equating prose with formal types.

The five continuum conjectures remain open within this project. Papers I–VI, the full Mathlib source tree and the original numerical suite were not rebuilt here. Independent mathematical review of the prose-to-formal correspondence remains valuable, even with a successful kernel check. Bibliography entries remain deferred to the consolidated end-of-series bibliography, as in the original publication plan.

The exact changes, source hashes, theorem ledger, successful and incomplete run records, build evidence and preservation checks accompany this report. The current README gives the reproducible commands and identifies the integrated PDF as the primary paper.
