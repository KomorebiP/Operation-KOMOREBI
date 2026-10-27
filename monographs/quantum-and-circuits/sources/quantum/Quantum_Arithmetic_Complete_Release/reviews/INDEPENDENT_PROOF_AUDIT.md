# Independent proof audit of the Quantum–Arithmetic Bridge

Audit date: 2026-10-07 UTC / 2026-10-06 Chicago.

Primary verdict: **proved as written**, for the explicit finite dimension-12 publication bridge. This is a source/proof audit, not a claim that this reviewer ran a fresh Lean compiler. Current compilation and provenance checks are a separate execution responsibility.

## Normalized target

Let the index set be `Fin 12`. Define the usual positive-sign Fourier matrix

\[
F_{na}=12^{-1/2}\exp(2\pi i na/12),\qquad
U=\{1,5,7,11\},\qquad D_{aa}=\mathbf 1_{a\in U}.
\]

Define

\[
c=(4,0,2,0,-2,0,-4,0,-2,0,2,0),\quad
P_{nm}=c((n-m)\bmod12)/12,
\]

\[
u_a=\tfrac12\mathbf1_{a\in U},\quad
\psi=c/\sqrt{48},\quad\chi=|c|/\sqrt{48}.
\]

The target asserts: both unitarity identities for `F`; `P=F D F†`; `P²=P=P†`; `Fu=psi` and `F†psi=u`; normalization of both states; identical original-basis probabilities; orthogonality of `psi` and `chi`; coprime probability one for the transformed signed state and zero for the transformed unsigned state.

The raw authoritative theorem is `publication_bridge` in the later input package `Komorebi_Quantum_Arithmetic_Lean_v0.2.0_Checked_1_/lean/Publication.lean:68`. The exponential Fourier-entry identification is `fourier_entry_formula` in `Conventions.lean:58`. The exact definitions are in `QuantumArithmeticBridge.lean`, `FiniteFourier.lean`, and `SemanticBridge.lean`. Statements concern these defined objects; they do not quantify over arbitrary modulus or arbitrary quantum circuits.

## Hypotheses and obligations

| Claim | Domain and hypotheses | Evidence | Audit |
|---|---|---|---|
| Coprime labels are exactly `1,5,7,11` | Modulus exactly 12, labels 0 through 11 | `coprime_residues_exact` | Passed |
| Root has order exactly 12 | Coordinate root `(0,1/2,1/2,0)` with stated multiplication | `zeta12_order_certificate`, `root_exact_order` | Passed |
| Phase sum is the integer table | Twelve indexed sample positions | `ramanujanC12_table`, `complex_ramanujan_signal` | Passed |
| DFT supports exactly the four coprime modes | Negative-sign unnormalized transform; positive-sign synthesis | `ramanujan_dft_table` | Passed |
| Literal rational matrix is the Fourier-transported selector | Dimension 12; cyclic difference `(i+12-j)%12` | `exact_projector_matches_rational_table`, `projector_transport` | Passed |
| Fourier matrix is an actual ordinary complex unitary | Scale `1/sqrt(12)` and complex interpretation | `fourier_unitary_left/right`, `fourier_entry_formula` | Passed |
| Signal recovery | Displayed test signal, with perturbation entirely in complementary modes | `projector12_recovers_test_signal` | Passed |
| Energy split 150=48+102 | Standard sum of squared magnitudes, all 12 entries | Energy certificates, `retained_discarded_orthogonal`, `signal_decomposition` | Passed |
| State normalization and action | Scale `1/sqrt(48)` and uniform coprime amplitudes `1/2` | `state_preparation`, `state_recovery`, normalization theorems | Passed |
| Same histogram, different coherent states | The specific signed and absolute-value states | `same_initial_probabilities`, `states_orthogonal`, `complete_phase_separation` | Passed |
| Histogram cannot recover both states | Deterministic function of that one original-basis probability vector | `no_reconstruction_from_initial_probabilities` | Passed |
| Projector is noninjective | Ordinary linear map on the full `Fin 12 -> Complex` space | Explicit nonzero kernel state `chi`; `projector_not_injective` | Passed |
| Every vector reconstructs from component plus residual | Both retained and discarded components supplied | `projector_residual_reconstructs` | Passed |
| General-modulus identity | Positive integer modulus, cyclic finite Fourier conventions | Algebraic derivation in worked example; DLMF crosscheck | Passed as prose mathematics, not general Lean coverage |
| General divisor-shell family | `d` divides the common ambient size `N` | Fourier-order classification derivation | Passed as prose mathematics, not general Lean coverage |
| Quantum circuit implementation or advantage | Would need compilation, cost, and hardware/noise contracts | No such evidence in source | Out of scope |

## Dependency graph

1. Rational coordinate definitions and exact finite calculations establish the concrete phase, matrix, and vector equalities.
2. `interpret` preserves zero, one, rational scalars, addition, multiplication, conjugation, powers, and finite sums.
3. Matrix/vector interpretation commutes with multiplication and adjoint.
4. Exact finite equalities therefore transfer to ordinary complex matrices and vectors.
5. `Conventions.lean` identifies the root with `exp(pi*i/6)` and both coordinate scales with the stated positive real square-root normalizations. It also identifies every Fourier matrix entry with the usual exponential formula.
6. `Publication.lean` bundles the complex identities and establishes the noninjectivity boundaries.

No arrow points back to the bundled conclusion as its own justification. No injectivity of `interpret` is required: the transfer uses forward preservation, so a coordinate identity legitimately implies a complex identity. The coordinate structure need not be installed as a global Lean field instance for these results.

## Decisive independent derivations

Pairing conjugate terms yields

\[
c_{12}(n)=2\cos(\pi n/6)+2\cos(5\pi n/6)
=2(1+(-1)^n)\cos(\pi n/6).
\]

This independently gives the displayed signed table. Character orthogonality makes its DFT coefficient `12` at the four coprime labels and zero elsewhere. Since the Fourier matrix is normalized by `sqrt(12)`, the inverse transformed amplitude is `12/(sqrt(48)sqrt(12))=1/2`, not `12/sqrt(48)`. Its probability is `1/4`.

The perturbation `eta(n)=3 cos(pi*n/2)+2` has unnormalized DFT coefficients `24` at zero and `18` at labels 3 and 9. These labels are disjoint from `U`. Parseval gives

\[
\|c\|^2=(4\cdot12^2)/12=48,\quad
\|\eta\|^2=(24^2+2\cdot18^2)/12=102.
\]

Thus `P(c+eta)=c`, and the input has energy `150` because the supports are orthogonal. This is exact rejection of complementary noise; it says nothing about noise in the selected subspace.

The absolute-value DFT table is

\[
(16,0,4,0,4,0,16,0,4,0,4,0).
\]

Consequently `F†chi` has amplitudes `2/3` at labels 0 and 6, `1/6` at labels 2,4,8,10, and zero elsewhere. Its probabilities are `4/9` at 0 and 6 and `1/36` at 2,4,8,10, summing to one. Its support is disjoint from the signed state's support. Their inner product is `(16+4-4-16-4+4)/48=0`.

For the normalized test input `x/sqrt(150)`, the two projective outcomes have probabilities `48/150=8/25` and `102/150=17/25`. Both outcomes are required for a complete measurement description. The unnormalized map `v -> Pv` alone is not a trace-preserving quantum channel or a unitary.

## General modulus and sign boundary

For every positive integer `q`, the finite orthogonality identity directly yields

\[
\widehat c_q(k)=q\mathbf1_{\gcd(k,q)=1},\qquad
c_q(n)=\sum_{e\mid\gcd(q,n)}e\mu(q/e).
\]

For common ambient length `N` and a divisor `d|N`, labels of exact character order `d` are `j=(N/d)a` with `0<=a<d` and `gcd(a,d)=1`. Thus

\[
P_d(n,m)=N^{-1}\sum_{a\in U_d}e^{2\pi i a(n-m)/d}
=c_d(n-m)/N.
\]

Their disjoint diagonal selectors imply `P_d P_e=delta_de P_d` and `sum_(d|N) P_d=I`. The common denominator is `N`, not `d`. At `d=1`, the shell is the constant/DC subspace and `c_1(n)=1`.

For the right cyclic shift `A x(n)=x(n-1)` and positive-sign Fourier columns, the eigenvalue is `zeta_N^(-j)`. The individual selector matching label `j` is therefore `N^-1 sum_l zeta_N^(j*l) A^l`. A negative exponent selects label `-j` instead. Character-order shells and coprime sets are invariant under negation, so the grouped rational projectors are unaffected. Any manuscript using individual `e_j` must state this convention.

## Earlier proof boundary is not the later proof boundary

The earlier `...v0.2.0_CHECKED/.../PROOF_BOUNDARY.md` correctly discloses that it did not supply the explicit ordinary complex matrix equality `P=F D F†` or normalized state-action identities. The later five-module package supplies those very declarations in `SemanticBridge.lean` and their entry conventions in `Conventions.lean`. It is incorrect to carry the earlier missing-arrow verdict forward into the later edition, and equally incorrect to describe the earlier build as already containing those declarations.

The later source names 96 theorems. This count includes support and bundled statements; it is not 96 novel discoveries. Historical reports describe compiler builds, kernel replay, and three rejected controls. A fresh report for this publication must distinguish a new execution from historical evidence. Earlier package counts must remain assigned to their own input revisions.

## Separate gauge-repair artifact

The patch `downloads/repair/block17_quantum_gauge_repair.patch` changes `src/komorebi_math/quantum/error_correction.py` and associated tests, probes, packaging, and QEC audit records. It repairs a numerical Knill–Laflamme certificate and recovery construction by resolving the Hilbert–Schmidt error span and replacing a decomposition-dependent declared-basis maximum by a unitary-invariant full block norm.

That subsystem is absent from the five-module finite Fourier bridge. The patch neither edits the Ramanujan signal nor supplies the complex transport declarations. It should be preserved and referenced as a related semantic audit, not applied to this standalone Lean project or described as its corrective patch. Its arbitrary ill-conditioned numerical span boundary is likewise a QEC implementation boundary, not a defect in the exact finite coordinate certificate.

## Scope controls

- Raw rational vectors/matrices are unsized lists. `zipWith` truncates unequal lengths and `getD` supplies defaults. Only the concrete length-12 literal assertions are certified with those functions. Generic complex-vector results use `Fin 12`, where the dimension is typed.
- Replacing `psi` by `chi` defines a second prepared state. No universal physical linear operation implementing amplitude-wise absolute value is claimed.
- Identical standard-basis histograms do not imply identical states, but arbitrary tomography from enough measurement bases is not ruled out.
- Perfect discrimination concerns these two states with the specified Fourier-basis/projector measurement, not arbitrary state identification from one sample.
- Dimension 12 is not the usual four-qubit dimension-16 QFT. `F12 direct-sum I4` is a mathematical embedding, not a supplied efficient circuit.
- Rational character-order projectors are not the same operators as coefficient-index residue projectors. A polyphase relation requires its own explicit transforms.

## Strongest safe recovery statement

For every `s` in the range of the exact dimension-12 coprime Fourier projector and every `eta` in its kernel, `P(s+eta)=s`. This is exact linear recovery with a fully explicit selected subspace. The projector's retained and discarded components together reconstruct every vector. The specific normalized states `psi` and `chi` have the same original measurement histogram and orthogonal, disjoint-support Fourier realizations, so their arithmetic selection can be distinguished with certainty by the specified projective measurement. The finite complex realization is supplied by the later Lean source chain; the general-modulus formulas have prose proofs and bounded implementation checks rather than a general Lean certificate.

## External-source check

A targeted attribution/hypothesis check was made against primary sources on the audit date. No global novelty search was conducted and no claim of a new Ramanujan/Fourier theorem is supported by this check.

1. NIST DLMF, section 27.10, equations 27.10.2–27.10.5, current page version 1.2.8 dated 2026-09-15. It gives a positive-sign finite Fourier expansion, negative-sign coefficient recovery with `1/q`, the primitive-root phase sum, and the integer divisor formula. The translation to indices `0,...,q-1` follows by periodicity. Classification: known after notation translation. URL: https://dlmf.nist.gov/27.10 . Retrieved through web text; no separate source bytes retained.
2. IBM Quantum Learning, *Quantum information*, sections *Measurements* and *Unitary operations*. It specifies squared-amplitude probabilities and normalized finite state vectors acted on by ordinary complex unitaries. The application here concerns pure states only. Classification: standard definitions applied to an explicitly proved finite example. URL: https://quantum.cloud.ibm.com/learning/en/courses/basics-of-quantum-information/single-systems/quantum-information . Retrieved through web text; no separate source bytes retained.
3. IBM Quantum Documentation, *QFT*. Its formula uses the positive sign but its circuit API assumes `N=2^n`; therefore it authenticates a sign convention, not implementation of the 12-dimensional transform. URL: https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.QFT . Retrieved through web text; no separate source bytes retained.
4. John Watrous, *The Theory of Quantum Information*, author-hosted 2018 prepublication draft, section 2.3, projective-measurement definition and Proposition 2.40, printed pp.107–108. It confirms the standard interpretation of orthogonal projection families as projective measurements. Classification: known after notation translation. URL: https://cs.uwaterloo.ca/~watrous/TQI/TQI.pdf . Viewed through web retrieval; the source prohibits redistribution, so it is not bundled.
5. Caltech, *The Ramanujan Periodicity Project*, project homepage. It authenticates existing Ramanujan signal-analysis work on subspaces, projection, dictionaries and filter banks. It is an attribution source, not proof of every general projector theorem in this release. URL: https://systems.caltech.edu/dsp/students/srikanth/Ramanujan/ . Retrieved through web text; no separate source bytes retained.

The cheapest remaining check for the finite publication chain is a fresh pinned source build plus kernel replay and axiom audit. That check verifies the proof terms under the recorded toolchain; it must not be inferred merely from this prose audit or agreement between reviewers.

## Additional phase-family illustration

Primary verdict for this added prose consequence: **proved as written**, with the selected probability written `sin²(theta/2)`.

Let `v+` be the positive entries of `c`, divided by `sqrt(48)`, with zeros elsewhere. Let `v-` be the absolute values of the negative entries of `c`, divided by `sqrt(48)`, with zeros elsewhere. Their supports are disjoint, so they are orthogonal. The positive support `0,2,10` and negative support `4,6,8` each have squared norm `(16+4+4)/48=1/2`. Hence

\[
\chi=v_++v_-,\quad\psi=v_+-v_-,\quad
\chi_\theta=v_++e^{i\theta}v_-.
\]

Every `chi_theta` is normalized and has exactly the same original-basis probabilities. Algebra gives

\[
\chi_\theta=\frac{1+e^{i\theta}}2\chi+
\frac{1-e^{i\theta}}2\psi.
\]

Since `P chi=0`, `P psi=psi`, and both are normalized,

\[
\|P\chi_\theta\|^2=\left|\frac{1-e^{i\theta}}2\right|^2
=\frac{1-\cos\theta}{2}=\sin^2(\theta/2),
\qquad
\|(I-P)\chi_\theta\|^2=\cos^2(\theta/2).
\]

The endpoints are `chi_0=chi`, `chi_pi=psi`, and `chi_(2pi)=chi`. The expression `(sin² theta)/2` would be false, for example at theta=pi where the exact probability is one. The correct half-angle formula is a prose corollary of the source-certified finite identities, not an already checked Lean declaration in the inherited package. Any plotted floating curve illustrates the proved formula; a three-coordinate display must label its actual embedding coordinates and must not identify the full 12-dimensional complex Hilbert space with physical three-dimensional space.

## Visual-manuscript mathematical review

Reviewed the 25-page body `visual/Quantum_Arithmetic_Visual_Body.tex` after it was written. The signal/DFT/unsigned-state tables, projector and energy identities, shell ranks and energies, twelve-to-three polyphase address lists, negative-sign assembly equation, continuous phase-family probability, and specified three-coordinate amplitude trajectory pass. In particular, its helix plots `(theta,Re chi_theta(6),Im chi_theta(6))`, with `chi_theta(6)=exp(i theta)/sqrt(3)`; this is an explicit embedding, not a claim that the full state space has three dimensions.

One prose correction was requested: replace the unconditional closing assertion that measurement returns a random outcome and changes the state with a statement that it returns one outcome and generally changes the state. The source example includes deterministic projective eigenstate outcomes whose state remains unchanged. This correction affects explanatory prose, not any equation or proof.

The visual author applied that correction. The page-nine conditional state statement also now names the ideal Lüders projective measurement, matching the instrument explicitly defined in the traditional paper. The final visual-mathematics verdict is **proved as written**, with floating illustrations and inherited formal scope kept distinct.

## Final traditional-manuscript audit

Primary verdict for the current twenty-contract manuscript: **proved as written**.

Read the complete 6,811-word first manuscript, then verified the two requested corrections in both the authoritative Markdown and generated LaTeX body. No raw inherited source was edited in this review.

| Contract | Audit result and decisive conditions |
|---|---|
| QA01 | Passed. Positive modulus, exact root order `q/gcd(a,q)`; zero label and modulus one included. |
| QA02 | Passed. Finite geometric-series argument, including modulus one. |
| QA03 | Passed. Both matrix products use opposite-sign character sums; inverse and Parseval have the correct `1/q` normalization. |
| QA04 | Passed. Möbius coprimality indicator, exchanged finite sums, positive divisors of `gcd(q,n)`; negative `n` understood by positive gcd. |
| QA05 | Passed. DFT support exactly `q` on coprime labels; squared norm `q phi(q)`. |
| QA06 | Passed. Positive common ambient `N`, divisor `d|N`, unique labels `(N/d)b`, common denominator `N`, rank and trace `phi(d)`. |
| QA07 | Passed. Hermitian idempotent yields orthogonal range/kernel components and the energy identity; generic loss condition is exact. |
| QA08 | Passed. Formal series over a field with primitive `L`th root and invertible `L`; finite root averaging is coefficientwise and does not assume convergence. |
| QA09 | Passed. `N=LM`, both factors positive; all lanes supplied for exact inversion; phase signs and alias factor `1/L` correct. |
| QA10 | Passed. Exact divisibility expression and signed/DFT tables match raw source. |
| QA11 | Passed. Complementary Fourier supports, filter action, retained/residual energies and orthogonality exact. |
| QA12 | Passed. State normalization `sqrt(48)=2 sqrt(12)` and unitary recovery exact. |
| QA13 | Passed. Same entrywise squared magnitudes, orthogonal states; positive and negative supports each have energy 24. |
| QA14 | Passed after doubled-transform wording correction. Amplitude tables and disjoint supports exact. |
| QA15 | Passed. Equal histogram cannot determine the two orthogonal states even modulo global phase; the latter clause is explicitly a prose corollary. |
| QA16 | Passed after explicit ideal Lüders instrument hypothesis. Effects fix probabilities; the selected instrument fixes conditional states. Nonzero-branch conditions present. |
| QA17 | Passed. Coordinate multiplication expands correctly with `(sqrt(3))²=3`; equalities transport forward without an injectivity hypothesis. |
| QA18 | Passed. The bundle has defined objects and an acyclic dependency on earlier claims. |
| QA19 | Passed. All family members normalized with a fixed initial histogram; selected probability `sin²(theta/2)`. |
| QA20 | Passed. Completely sample-dephased density is positive with trace one; constant projector diagonal gives `tr(P rho_diag)=1/3`. |

The independent lane calculation gives `c0=(4,0,-4,0)`, `c1=(0,-2,0,2)`, and `c2=(2,0,-2,0)`. Their four-point negative-sign transforms are respectively `(0,8,0,8)`, `(0,4i,0,-4i)`, and `(0,4,0,4)`. At global label one, the two complex terms satisfy `4i zeta^-1 + 4 zeta^-2=4`; together with eight this gives twelve. At global label nine, they are minus four and minus four, giving zero. The same local frequency is therefore resolved by the retained offset phases exactly as claimed.

Two corrections were completed:

1. In QA14, the six-point transform of `(4,0,2,0,2,0)` is eight on labels divisible by three and two otherwise. Its doubled twelve-point transform is sixteen/four. The original ambiguous sentence called the six-point transform sixteen/four; the current sentence explicitly says **the doubled transform**.
2. An orthogonal projector's effects determine the outcome probabilities but do not alone uniquely determine post-measurement states. The current Section 11 explicitly specifies the ideal Lüders instrument with branches `rho -> P rho P` and `rho -> (I-P) rho (I-P)`, and QA16 now states its conclusion for that instrument. This restriction is substantive and is also reflected in visual page nine.

No identification of phase-family averaging with complete dephasing is made. Uniform averaging of the single QA19 relative phase would retain within-support coherence and give selected probability one half. QA20 instead removes every off-diagonal sample-basis entry and correctly gives one third. Its density-matrix/measurement claim is prose mathematics, outside the inherited Lean scope.

The individual cyclic shift projectors have the positive phase exponent required by the manuscript's right-shift/positive-Fourier convention. No unstated converse theorem about all rational selectors is used. The internal prior-paper citation is lineage: the current divisor-shell and shift formulas have their own explicit proofs. Classical attribution and implementation boundaries are stated accurately. Arbitrary-modulus/formal-series results, the phase continuum, global-phase quotient corollary, and complete dephasing are not represented as inherited generic Lean declarations.

Audited content hashes after the two corrections:

| Artifact | SHA-256 |
|---|---|
| `traditional/Quantum_Arithmetic_Traditional.md` | `e8b71ab76ca5514620107ebaa495afcaa4c9f96891f13087f06a1ebb5a383916` |
| `traditional/Quantum_Arithmetic_Traditional_Body.tex` | `417fdb2c110b898a733ca529a54d56287cbb162f82374898caf3bed0ce49c6e2` |
| `visual/Quantum_Arithmetic_Visual_Body.tex` | `d13161e78d40c964f7a0da0690ad9f3a52bde46787e0937d4a330f9388c514a7` |

These identify the mathematical review snapshot. Subsequent layout or proofreading changes must retain their own provenance and should not be called the same byte revision merely because mathematical conclusions are unchanged.

The author subsequently separated the index-set symbol `I_q` from the identity-matrix symbol `Id_q`. I verified the explicit definition and the affected matrix equations. This is a conservative notation correction with no theorem-hypothesis or proof change. The accepted traditional revision now has SHA-256 `c27e9f9850396de2fa3cdd8196958c107304a2c25d1df726038a4e9d71ca8616` for the Markdown and `221dc399945d5a4eff728634f34d28787500e58da1fdacda8c03902a35ac1a20` for the generated body.
