# Correction ledger for the final traditional edition

Raw recovered sources were left unchanged. The reading edition uses the corrected integrated finite body, preserves the complete strengthened body and all mathematical supplement sections, and identifies the following exact qualifications. No major new proof or new Lean result was created.

## Historical finite-core repairs reconciled

| Location | Historical issue | Final treatment |
|---|---|---|
| I.2.1–I.2.3 | Cancellation of a zero row dimension and ambiguous zero/empty module conventions | Positive addressed/block dimensions where cancellation is used; zero-module and empty-family cases explicit in the supplement. |
| I.3.1–I.3.2 | Cyclic modulus, order and orthogonality assumptions | N>0, including N=1; unitary order divides N; complete orthogonal local projector families. |
| I.4.1 | Empty circuit indexing | Empty circuit is identity with transfer P_bP_a; nonempty path formula stated separately. |
| I.5.2 | Leakage estimate needed the analytic norm and all real times | Self-adjoint generator, orthogonal projector, Hilbert operator norm, differentiation/mean-value proof; retained Duhamel alternative uses interval length abs(t). |
| I.6.1, I.6.3 | Moving Hamiltonian Hermiticity and actual derivatives | Differentiable unitary coordinates and actual projector derivatives; Hermitian original Hamiltonian explicitly required. |
| I.6.4 and III.24–III.28 | Earlier compact curvature computation omitted geometric construction and bracket meaning | Range-bundle atlas, smooth intrinsic sections, gluing, fiber-valued derivative and actual Lie bracket retained from latest completion; underlying real boundaryless manifold scope explicit. |
| I.8.1 and III.18–III.23 | Error family normalization, null Gram sectors and total recovery under-specified | Single total CPTP decoder, coherent cross terms, scale for unnormalized errors, normalized-channel specialization, null eigenvalues and zero code all explicit. |
| I.9.1 | Eliminated-block invertibility alone did not ensure the full resolvent existed | Both eliminated and full resolvents invertible; retained inverse distinguished from ambient inverse; counterexample preserved. |
| I.10.1 | Minimum eigenvalue and transfer-time scope | Nonempty finite spectrum and nonnegative transfer times; operator positivity distinct from entrywise positivity and field-measure reflection positivity. |
| I.11.1 | Nonzero spacing and stronger estimate scope | h≠0; all-real dispersion bound retained; fixed-frequency interpretation separated from numerical convergence. |
| I.12.1–I.12.5 | Physical common-kernel compression was mistaken for operator closure | Compression is automatic; research target requires operator-level closure and nonzero compatible physical tower; no continuum existence theorem asserted. |

## Independently reviewed strengthened qualifications

Each replacement below was made only in parts/02_strengthened.tex, with the written proof body unchanged.

### S-01: S cyclic charge opening: positive integer modulus, including N=1.

Before:
```latex
Let \(S\) be unitary with \(S^N=I\), and let \(\omega=\e^{2\pi\ii/N}\).
```

After:
```latex
Let \(N\ge1\) be an integer, \(S\) unitary with \(S^N=I\), and \(\omega=\e^{2\pi\ii/N}\).
```

### S-02: S coherence action: repeated unitary symmetry and positive modulus hypotheses.

Before:
```latex
Let \(S^N=I\) and define the conjugation action
```

After:
```latex
Let \(S\) be unitary and \(N\ge1\) an integer with \(S^N=I\), and define the conjugation action
```

### S-03: S Lindblad charge theorem: repeated unitary symmetry and positive modulus hypotheses.

Before:
```latex
Let \(S^N=I\). Assume
```

After:
```latex
Let \(S\) be unitary and \(N\ge1\) an integer with \(S^N=I\). Assume
```

### S-04: S time-dependent propagator: continuity supplies the regularity used by the integral Duhamel leakage proof.

Before:
```latex
where \(H(t)=H(t)^*\). Set
```

After:
```latex
where \(H(t)=H(t)^*\) is continuous on the compact time interval under consideration. Set
```

### S-05: S self-energy stability: both hidden Hamiltonians explicitly self adjoint on fixed comparable spaces; a nonnormal hidden resolvent invalidates the spectral-distance bound.

Before:
```latex
\begin{theorem}[Stability of the self energy]\label{thm:self_energy_stability}
Let
```

After:
```latex
\begin{theorem}[Stability of the self energy]\label{thm:self_energy_stability}
Let \(D=D^*\) and \(\widetilde D=\widetilde D^*\) act on one fixed hidden Hilbert space, and let \(B,\widetilde B\) map that hidden space to one fixed retained Hilbert space. Define
```

### S-06: S uniform Feshbach control: common-space identifications and self adjointness explicitly repeated for norm comparison.

Before:
```latex
For a family of packet decompositions with a common hidden spectral separation \(\delta\) and a common coupling bound \(g\),
```

After:
```latex
For a family represented on fixed retained and hidden Hilbert spaces, with self adjoint hidden Hamiltonians, a common hidden spectral separation \(\delta\), and a common coupling bound \(g\),
```

### S-07: S finite Lindblad input: explicit completely positive trace preserving Schrödinger convention for the imported generator theorem.

Before:
```latex
A norm continuous quantum dynamical semigroup on a finite matrix algebra has a generator of the form
```

After:
```latex
A norm continuous semigroup of completely positive trace preserving maps on a finite matrix algebra, in the Schr\"odinger picture, has a generator of the form
```

### S-08: S multiplicity setup: positive block dimensions and zero-module/empty-family convention.

Before:
```latex
A vector in one block is identified with a \(d_r\) by \(m_r\) coefficient matrix.
```

After:
```latex
Assume \(d_r,m_r\ge1\) for each displayed block. For an empty block family, the seed rank and the displayed finite supremum are defined as zero. A vector in one block is identified with a \(d_r\) by \(m_r\) coefficient matrix.
```

### S-09: S orbit cyclicity: positive row dimension needed to cancel d; zero columns retained to support the zero second factor in the Schmidt corollary.

Before:
```latex
For the action of \(M_d(\CC)\otimes I_m\) on \(\CC^d\otimes\CC^m\), let
```

After:
```latex
For integers \(d\ge1\), \(m\ge0\), and the action of \(M_d(\CC)\otimes I_m\) on \(\CC^d\otimes\CC^m\), let
```

### S-10: S approximate Knill-Laflamme defect: explicit empty-family convention.

Before:
```latex
For a finite error family define
```

After:
```latex
For a finite error family define, with the maximum of the empty family set to zero,
```

### S-11: S heat packet average: sum only over nonempty packet heat traces so every local spectral dimension is defined.

Before:
```latex
d_L(t)
=
\sum_a
\frac{Z_{L,a}(t)}{Z_L(t)}
```

After:
```latex
d_L(t)
=
\sum_{a:Z_{L,a}(t)>0}
\frac{Z_{L,a}(t)}{Z_L(t)}
```

### S-12: S Schmidt cyclicity: nonzero addressed factor for full-support equivalence.

Before:
```latex
Let \(\psi\in\Hcal_A\otimes\Hcal_B\), let \(d_A=\dim\Hcal_A\), and let
```

After:
```latex
Let \(\psi\in\Hcal_A\otimes\Hcal_B\), let \(d_A=\dim\Hcal_A\ge1\), and let
```

### S-13: S circuit formula: positive depth for indexed formula and explicit empty-circuit identity.

Before:
```latex
be a finite circuit and let \((P_a)_{a\in I}\) be a complete orthogonal packet family.
```

After:
```latex
be a finite circuit with \(m\ge1\), and let \((P_a)_{a\in I}\) be a complete orthogonal packet family. For the empty circuit, \(U=I\) and its transfer block is \(P_bP_a=\delta_{ba}P_a\), whose endpoint sum reconstructs \(I\).
```

### S-14: S code obstruction: nonzero code for division by k, Gram positivity from scalar compression, and choice of a code density state.

Before:
```latex
k=\dim\Ccal.
```

After:
```latex
k=\dim\Ccal\ge1.
```

### S-15: S syndrome measurement: normalized channel hypothesis and ambient-complete measurement.

Before:
```latex
The projective measurement \((Q_j)\) identifies the orthogonal error syndrome without resolving the encoded state inside the code.
```

After:
```latex
For a channel trace preserving on code states as in the preceding theorem, the completed projective measurement consisting of \((Q_j)_{\lambda_j>0}\) and \(I-\sum_{\lambda_j>0}Q_j\) identifies the orthogonal error syndrome without resolving the encoded state inside the code. The complement outcome has probability zero on the corrupted code state.
```

### S-16: S correctable observable algebras: explicitly supplied the source-authenticated Heisenberg recovery definition and channel hypotheses.

Before:
```latex
A finite dimensional observable algebra \(\Mcal\subseteq P\End(\Hcal)P\) is correctable for a channel with Kraus operators \((E_a)\) exactly when every compressed product \(PE_a^*E_bP\) belongs to the commutant \(\Mcal'\).
```

After:
```latex
Let \(\Phi\) be a finite completely positive trace preserving channel with Kraus operators \((E_a)\). A finite dimensional unital star subalgebra \(\Mcal\subseteq P\End(\Hcal)P\) is correctable when a completely positive trace preserving recovery \(\Rcal\) satisfies \(P(\Phi^*\circ\Rcal^*)(X)P=X\) for every \(X\in\Mcal\), where stars on maps denote Heisenberg adjoints. This holds exactly when every compressed product \(PE_a^*E_bP\) belongs to the commutant \(\Mcal'\) on the code.
```

### S-17: S Euclidean setup: added nonzero space so min Spec H is defined.

Before:
```latex
Let \(H=H^*\) on a finite dimensional Hilbert space and let
```

After:
```latex
Let \(H=H^*\) on a nonzero finite dimensional Hilbert space and let
```

### S-18: S exact packet direct limit: fixed finite address set makes the finite completeness passage precise.

Before:
```latex
Assume each packet address \(a\) is compatible in the sense
```

After:
```latex
Assume the packet families have one fixed finite address set at every level and each packet address \(a\) is compatible in the sense
```

### S-19: S limit leakage: supplied orthogonal projector and self adjoint hypotheses used for the norm-one Duhamel factors.

Before:
```latex
Let \(P_n\to P\) and \(H_n\to H\) in norm. Then for every bounded time interval,
```

After:
```latex
Let \(P_n\) be orthogonal projectors and \(H_n\) bounded self adjoint operators on one Hilbert space, with \(P_n\to P\) and \(H_n\to H\) in norm. Then for every bounded time interval,
```

### S-20: S heat trace convergence: nonnegative self adjoint operators and trace-class heat operators make spectral calculus and trace-norm convergence typed.

Before:
```latex
Let \(L_n,L\geq0\) act on one Hilbert space, and assume for a fixed \(t>0\) that
```

After:
```latex
Let \(L_n,L\) be nonnegative self adjoint operators on one Hilbert space. For a fixed \(t>0\), assume their heat operators are trace class and that
```

### S-21: S heat trace convergence: explicit trace-class first moments for the optional spectral-dimension conclusion.

Before:
```latex
If also
\[
L_n\e^{-tL_n}\longrightarrow L\e^{-tL}
\]
in trace norm
```

After:
```latex
If also the heat moment operators are trace class and
\[
L_n\e^{-tL_n}\longrightarrow L\e^{-tL}
\]
in trace norm
```

## Additional semantic and editorial reconciliations

- The code section explicitly sends the zero-code branch to the general completion, avoiding the traceless representative denominator k and the nonexistent normalized zero-code state.
- The strengthened error-span criterion now defines one CPTP decoder for all coherent combinations, with a nonnegative error-dependent scalar independent of the logical input; normalized channels in the same span have total scalar one. This uses the already supplied completed criterion, rather than adding an unsupported recovery claim.
- The fourth supplement’s historical “still partial” global-bundle sentence is replaced by a reference to the final mathematical completion below; its displayed curvature and pullback proofs are retained.
- Supplement source-page pointers (pages3,5,6) are replaced by named nearby mathematical discussions so they remain true after reflow.
- Historical compiler/declaration hooks and release pages remain preserved in raw sources and the Lean/evidence guide; all151 substantive supplementary display/align blocks are retained.
- The earlier abbreviated Knill–Laflamme sketch is replaced by the complete necessity, sufficiency, state/operator bridge and coherent-span proof. Its substantive conclusion remains printed with corrected normalization.
- Valid earlier Duhamel, exterior-curvature and restricted low-mode derivations are retained as alternatives. The exterior covariant extension and its Lie-bracket meaning are explicit; the sine-square argument states nonnegativity before squaring.
- Core numerical text is reconciled with recovery of the original numerical companion, without turning historical floating-point observations into theorem proofs.

## Validation and review

- Independent final review: audit/math/FINAL_EDITED_SOURCE_REVIEW.md. No further mathematical correction requested.
- Written-scope review: audit/math/WRITTEN_PROOF_AUDIT.md.
- Preserved explicit source proof bodies:104 after navigation-anchor/namespace/whitespace normalization (19 core, 79 strengthened, 6 supplementary), plus 3 retained alternatives.
- Complete PDF 101 pages; final TeX diagnostics empty; all reported fonts embedded; all internal links valid; no off-page text.
- All 101 pages rendered into contact sheets and inspected for complete text, display placement, float layout and clipping.
- This is an editorial/PDF build, not a new Lean compilation.

Layout-only correction: alias counters give each environment its correct cleveref name while retaining shared numerical order. No mathematical body or theorem number changed.
