# Block 12 — Infinite coarse cells, explicit domains and current regrouping

Komorebi Physics Lean v0.12.0. Source: *Projector-Refinement Physics: Complete Unified Theory*, physical PDF page 33 of 550, printed page 20, Section 6.5, equations (6.42)–(6.47). The page image was inspected. The original source PDF is unchanged. The authoritative cumulative verification result is `verification/final/report.json`. A partial run, a source count or this guide alone is not a completed proof audit.

## 1. Inventory and scope

| New module | Theorems | Other inventoried declarations | Role |
|---|---:|---:|---|
| InfiniteCells | 22 | 3 | Strongly summed actual coarse projections and energy regrouping |
| ClosedCellDomains | 11 | 4 | Closed-graph domain construction and graph-compatible coarsening |
| InfiniteCellCurrents | 13 | 0 | Certified iterated currents, explicit joint summability and actual derivatives |
| SpectralCells | 14 | 3 | Coordinate masks, maximal-domain/graph properties and constructed dynamics |
| InfiniteCellAlgebra | 10 | 1 | Complement, support, composition and reflected atlases |
| InfiniteCoarseExamples | 25 | 5 | Infinite parity cells and nonzero transfer on a true normalized solution |
| CurrentSummationExamples | 11 | 2 | Row/column/iterated summability versus joint summability |
| **Block 12** | **106** | **18** | **124 new inventoried declarations** |

The cumulative inventory is **1,083 theorem declarations, 1,296 named declarations and 65 mathematical modules**. There are 87 negative controls. The previous 58 mathematical sources are byte-identical. Of the 1,083 theorem declarations, 39 are recovered Paper VII declarations and 1,044 were authored across the full-edition blocks. The new count includes 70 general/support theorems and 36 example/support theorems. Counts are not independent physical discoveries or a full-edition completion percentage.

The general ambient space is a complete complex Hilbert space, not necessarily finite-dimensional or separable. The index sets need not be finite; the formal hypotheses are unconditional strong sums over finite subsets. These include the manuscript's countable case. The partially defined generator has an actual linear domain. At the Hilbert projection layer no generator hypothesis is used. At the domain layer, closedness and graph compatibility are explicit sufficient conditions. At the scalar current layer, domain symmetry and independently established coarse-domain preservation suffice.

## 2. Actual strong coarse projections: (6.42)

For a complete orthogonal `StrongAtlas` P and an arbitrary set C of fine labels, define

\[
Q_Cx=\sum_{i\in C}P_ix.
\]

`cell_hasSum` first proves an actual `HasSum` by taking a subseries of the strong atlas resolution. The sum is not treated as meaningful merely because Lean permits a totalized `tsum` expression. Finite Pythagoras and the strong limit prove

\[
\|Q_Cx\|\le\|x\|.
\]

`cell` then constructs a bounded complex-linear map from this actual sum, with a proved bound. Its linearity and continuity are proof obligations in the constructor and are included in the axiom audit.

The new proofs establish

\[
Q_C^*=Q_C,\qquad Q_C^2=Q_C,\qquad\|Q_C\|\le1,
\]
\[
P_iQ_Cx=\begin{cases}P_ix&i\in C,\\0&i\notin C,\end{cases}
\qquad Q_CQ_D=Q_{C\cap D}.
\]

Empty cells give zero, the whole label set gives the identity, complementary cells sum to the identity, and disjoint cells are orthogonal. The fixed-vector and zero-vector criteria are proved in terms of the original fine coordinates.

For any address map f:I→J, `coarsenInfinite f` is an actual new strong orthogonal atlas with projectors Q_(f^-1{a}). Its completeness follows from the proved fiber regrouping of the original vector `HasSum`. Infinite and empty fibers are allowed.

`coarsen_cell` and `coarsenInfinite_comp` prove sequential-versus-composed coarse projections for arbitrary address maps, not only finite partitions. Their energy quantities agree as well. These are additional algebraic consequences beyond the literal six source equations.

## 3. Energy regrouping: (6.43)–(6.44)

Finite Pythagoras is passed through the actual vector limit, yielding

\[
\boxed{\|Q_Cx\|^2=\sum_{i\in C}\|P_ix\|^2.}
\]

`cell_energy_hasSum` proves the genuine scalar `HasSum` with the displayed value, and `coarsenInfinite_energy` identifies the actual coarse energy. No Hamiltonian, domain condition, graph convergence or derivative is needed here. This is a Hilbert-space identity for every state.

The type of convergence is strong on each state. These results do not assert operator-norm convergence of finite partial cell projections.

## 4. Coarse domain preservation is derived from a closed graph

Let T:D(T)⊂H→H be the existing partially defined linear operator, P a domain-invariant fine atlas, T closed, and P graph-compatible. Graph compatibility uses the net of all finite subsets, not only a single ordered enumeration:

\[
S_Fx\to x,\qquad TS_Fx\to Tx\quad(x\in D(T)).
\]

For a fixed cell C, both subseries are constructed:

\[
\sum_{i\in C}P_ix=Q_Cx,\qquad
\sum_{i\in C}TP_ix=y_C.
\]

Every finite partial pair lies in the actual graph of T. The proved convergence of the two components and graph closedness imply

\[
(Q_Cx,y_C)\in\operatorname{graph}(T).
\]

Only then does the formalization conclude

\[
\boxed{Q_Cx\in D(T),\qquad TQ_Cx=\sum_{i\in C}TP_ix.}
\]

This is `cell_pair_mem_graph`, `cell_mem_domain`, and `cell_action_hasSum`. `cellProject` constructs the genuine domain-valued linear map after these membership proofs. `cell_graph_tendsto` proves convergence in the actual graph norm. `coarsenClosed_graph` proves graph compatibility of the resulting coarse atlas.

Ambient strong convergence alone is not used to infer membership in an unbounded operator domain. Neither is absolute summability of scalar currents substituted for that operator-domain argument. The vector action series here is unconditionally convergent; no claim of absolute summability of its vector norms is made.

A separate `coarsenOfPreserves` constructor accepts coarse-domain invariance established by another proof. Closedness plus graph compatibility are sufficient, not asserted necessary. Self-adjointness of the original spectral model already supplies closedness, but the domain construction itself works for any closed operator meeting these hypotheses.

## 5. Actual coarse amplitudes and currents: (6.45)–(6.47)

Let T be symmetric on its domain, x∈D(T), and all the relevant coarse projections preserve D(T). Define receiving-first currents by

\[
J_{ij}=2\operatorname{Im}\langle P_ix,TP_jx\rangle,
\qquad J^c_{ab}=2\operatorname{Im}\langle Q_ax,TQ_bx\rangle.
\]

For one fixed fine receiving packet, symmetry gives

\[
\sum_{j\in C_b}\langle P_ix,TP_jx\rangle
=\sum_{j\in C_b}\langle TP_ix,P_jx\rangle
=\langle TP_ix,Q_bx\rangle
=\langle P_ix,TQ_bx\rangle.
\]

The source-cell vector sum is paired with the fixed domain vector TP_ix. The last equality uses the proved or supplied coarse-domain membership. It does not commute an unbounded T with an ambient limit without justification.

Summing the resulting pairing over the receiving cell then proves

\[
\boxed{J^c_{ab}=\sum_{i\in C_a}\left(\sum_{j\in C_b}J_{ij}\right).}
\]

Both the inner and outer series have genuine `HasSum` proofs. The corresponding complex amplitude identity is also proved. This scalar route requires symmetry and coarse-domain preservation, not an additional graph-compatibility hypothesis. The closed-graph construction above is one way to discharge that preservation requirement.

`coarse_current_reverse_hasSum` separately proves the reverse iteration, using antisymmetry and the swapped-cell theorem. Thus these two iterated sums agree under the operator/domain hypotheses. This is not a generic Fubini theorem based solely on rowwise summability.

`coarse_current_outer_abs_summable` proves

\[
\sum_{i\in C_a}\left|\sum_{j\in C_b}J_{ij}\right|<\infty.
\]

It does **not** assert

\[
\sum_{(i,j)\in C_a\times C_b}|J_{ij}|<\infty.
\]

Flattening into a single product-index `HasSum` is a separate theorem, `coarse_current_product`, with joint summability explicitly required. The complex amplitude version retains its own joint-summability hypothesis. For real or complex arrays this is the usual absolute-convergence condition. The source's finite grouping is included as the finite special case; it is not used to pretend an infinite double array is finite.

## 6. The infinite-cell derivative is obtained without termwise differentiation

Starting with the actual ambient evolution derivative

\[
\dot\psi=-iT\psi,
\]

`infinite_cell_hasDerivAt` applies the already checked derivative theorem to the constructed bounded coarse projector, then substitutes the separately proved energy identity:

\[
\boxed{\frac{d}{dt}\sum_{i\in C_a}\|P_i\psi(t)\|^2
=\sum_b J^c_{ab}(t).}
\]

The derivative is a conclusion about the actual infinite energy-sum function. There is no assumption permitting termwise differentiation of the infinite fine-energy sum. Internal infinite cells cancel as certified iterated sums.

For the constructed real diagonal spectral evolution, `constructed_coarse_hasDerivAt` supplies the original Schrödinger derivative itself. Any graph-compatible fine domain atlas can be used; it need not diagonalize the Hamiltonian. This does not construct dynamics for an arbitrary non-diagonal Hamiltonian.

## 7. Arbitrary spectral cells preserve the maximal domain

The spectral mask is the actual strong coarse projection, and its coordinate formula is proved:

\[
(Q_Cx)_n=\mathbf1_C(n)x_n.
\]

For the actual maximal real diagonal operator, the formalization derives domain membership, commutation TQ_C=Q_CT on D(T), contraction in the graph norm, and the exact weighted energy sum

\[
\|Q_Cx\|_T^2=\sum_{n\in C}(1+\lambda_n^2)|x_n|^2.
\]

These masks commute with the constructed spectral evolution. Their energies are constant for every initial l2 vector; the explicitly stated derivative interface uses a domain initial vector. Spectral coarse currents are correctly zero. General domain-compatible coarse atlases need not have zero current, as the following example demonstrates.

## 8. Genuine infinite cells with nonzero transfer

On actual l2(N,C), construct the bounded self-adjoint involution U with matrix

\[
\begin{pmatrix}3/5&4/5\\4/5&-3/5\end{pmatrix}
\]

on the first two coordinates and identity on every other coordinate. The operator is defined by bounded coordinate evaluation and injection maps. The coordinate formula, self-adjointness, U²=I, norm preservation and invariance of every maximal real diagonal domain are all proved.

The fine atlas is the actual reflected atlas \(\widetilde P_n=UP_nU\). Coarse labels are even and odd fine indices. **Both fibers are proved infinite.** Every arbitrary reflected cell preserves the generator domain by composing U, the spectral mask and U; this independently discharges coarse-domain preservation without assuming graph compatibility for the example.

Use the genuinely unbounded harmonic generator lambda_n=n+1/2 and the earlier normalized domain vector

\[
\psi_0=\frac35e_0+\frac45i\,e_1.
\]

The actual constructed orbit is global, normalized, domain-valued and satisfies the original Schrödinger equation. The new exact calculations give

\[
\|Q_{\mathrm{even}}\psi_0\|^2=\frac{337}{625},
\]
\[
\boxed{J^c_{\mathrm{even}\leftarrow\mathrm{odd}}(0)=\frac{288}{625},
\qquad J^c_{\mathrm{odd}\leftarrow\mathrm{even}}(0)=-\frac{288}{625}.}
\]

The true derivative theorem yields

\[
\boxed{\left.\frac{d}{dt}\sum_{n\text{ even}}
\|\widetilde P_n\psi(t)\|^2\right|_{t=0}=\frac{288}{625}.}
\]

The iterated fine-cell current expansion is separately identified with that same nonzero value. This is not an affine local witness, a bounded Hamiltonian substituted for the unbounded one, or a purely formal infinite index on a finite ambient space. The particular nonzero transfer is carried by two modes of the state, while both coarse fibers and the ambient model remain infinite. No claim of nonzero current at every tail mode is made.

## 9. Rowwise and iterated convergence do not imply joint convergence

`CurrentSummationExamples` repeats the previously checked nonzero three-cycle on disjoint blocks indexed by N. The label set is N×Fin3. The resulting real array K is antisymmetric, every row and column has finite support and zero sum, and both iterated series have genuine `HasSum` equal to zero.

Nevertheless,

\[
\boxed{\neg\operatorname{Summable}_{(i,j)}K_{ij},
\qquad \sum_{i,j}|K_{ij}|\text{ is not summable}.}
\]

There is an injective sequence of edges all equal to one. Restricting a hypothetical jointly summable array to those edges would make the constant-one real sequence summable, a contradiction.

This example is an abstract array counterexample. It is not asserted to be realized by the particular Hamiltonian/current construction above. Its role is to refute the generic logical shortcut from rows or agreeing iterated sums to a jointly summable double array.

## 10. Verification and retained boundaries

The production verifier freshly compiles all 65 mathematical modules and the aggregate with one worker and warnings as errors, audits all 1,296 inventoried declarations including constructors, and checks 87 invalid controls. Each invalid control needs its own designated diagnostic within its mapped source range. Import failures, extra diagnostics, timeouts and a nonzero batch exit alone do not pass this contract. The six new controls cover wrong coarse energy, wrong derivative sign, zero non-spectral coarse current, finite parity cells, rowwise-to-joint summability and iterated-to-joint summability.

All 58 prior mathematical sources are checked against `reference/block11_preservation.json`; earlier preservation layers remain active. The 977-theorem Block 11 baseline was freshly reverified before extension. The exact Lean version is 4.34.0-rc2 and Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Nine dependency revisions and clean tracked trees are checked. Imported compiled dependencies are reused, not rebuilt wholesale. The only permitted axiom dependencies are propext, Classical.choice and Quot.sound. No active admissions, custom axioms, native evaluation or kernel-bypass options are used. Compiler/runtime bytes remain external, with restoration support included.

The domain hypotheses are not dropped for arbitrary infinite groupings. Product-index current sums retain joint summability. This block does not prove general non-diagonal spectral representation or Stone's theorem, identify the harmonic sequence model with a differential oscillator, complete the form-domain hierarchy, construct residue/ladder operators, establish compact/Hilbert–Schmidt reconstruction, or solve the earlier nonlinear/dissipative existence and positivity-preservation problems. The later gravitational, cosmological and empirical obligations remain separate. Chapter 3 is still not exhaustively inventoried.

**Next literal target:** Section 6.6, equations (6.48)–(6.52): actual residue projectors from finite character sums, their equality to infinite spectral masks, and domain-correct ladder routing. Require a positive modulus and retain lowering-at-zero and weighted-domain obligations. No infinite coarse theorem licenses an unbounded ladder composition without its domain proof.
