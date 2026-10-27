# Reading this guide

Signal reconstruction has three distinct kinds of evidence in this edition: mathematical proofs in the traditional paper, finite computations with preserved outputs, and related Lean proofs inherited from Paper V. The unknown-edge estimator and the self-calibration procedure are developed in the first two layers. The recovered Lean sources establish packet, transfer, known-edge, mask, and finite-pruning contracts that support parts of the framework. They do not supply an end-to-end formal proof of the July signal-recovery algorithms.

This guide makes those relationships inspectable. It presents literal source excerpts, explains their types and hypotheses, and identifies the additional obligations required by the Signal paper. The editable Markdown files are included with the TeX, PDFs, original sources, mappings, and verification records. A displayed source excerpt retains its original declaration name; explanatory mathematics surrounding it is interpretation, not an additional declaration checked by Lean. Some excerpts stop at the theorem's type and proof delimiter; the complete proof remains in the quoted raw source file. The excerpts are not standalone modules.

The author is **Komorebi P.** The edition date is October 6, 2026. The word “complete” describes this publication set and its disclosed evidence, not a claim that all Signal theorems have been formalized.

## Evidence layers

| Evidence | What it establishes | Limit |
|---|---|---|
| Current traditional proofs | The stated mathematical implications under their explicit assumptions | Human mathematical proofs, with external theorem inputs identified |
| Preserved Paper V source and historical build | Related typed theorem statements and the archived checks for that source version | Inherited evidence; no new Signal elaboration |
| Fresh static correspondence | Saved contract names, source files and lines agree with the inherited audit | Text and hash validation, not kernel execution |
| Fresh Python runs | The declared finite cases and negative controls reproduce their recorded behavior | Bounded computations, not universal proofs |
| Source review and counterexamples | Specific overstatements are repaired or excluded | Neither a compiler result nor a blanket correctness certificate |

The current runtime probe found neither `lean` nor `lake` on the active PATH. No new Lean build was attempted. `verification/FRESH_LEAN_STATUS.json` records this narrow fact. A passing publication build, an absence of `sorry` in text, or a matching declaration inventory cannot substitute for elaboration and kernel checking.

# The recovered formal source

The related formal tree is `related_formal/paper_v/formalization/lean/`. It comes from the checked **Paper V v1.1.0 checkpoint**, `Paper_V_Complete_v1.1.0_With_Visual_Appendix.zip`. The archive has 23,437,514 bytes and 493 members, and passed the archive CRC check. Its SHA-256 is:

`7a15b94133739c26b8da5aadb2a2415c0bc539888430cec1baf0fb6425ea580e`

The later archive `Komorebi_Paper_V_Final_Traditional_Visual_Lean_2026-10-05.zip` was retrieved twice, including an independent retry, and neither downloaded copy could be opened as a ZIP. Both had the advertised size and the same SHA-256. Python reported `BadZipFile: File is not a zip file`; an end-of-central-directory signature was not found. The cause of the malformed payload has not been established. It was not used as verified formal evidence. The failure, retry, and checked fallback are separately recorded in `provenance/PAPER_V_FINAL_ARCHIVE_FAILURE.json`, `provenance/PAPER_V_FINAL_ARCHIVE_RETRY.json`, and `provenance/PAPER_V_CHECKED_CHECKPOINT.json`.

The release preserves the selected checkpoint's formal sources, contracts, logs, and relevant metadata. It does not contain a portable Lean runtime or the complete original Paper V distribution. The original full verification driver expects files beyond this selected related-source subset.

## Version pins and historical checks

| Item | Recorded identity |
|---|---|
| Lean toolchain | `leanprover/lean4:v4.34.0-rc2` |
| Lean commit | `6a10ac8c22beadecabdbb0919c2b50214762f91d` |
| Mathlib commit | `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` |
| Warning policy | `-DwarningAsError=true` |
| Implicit undeclared variables | `autoImplicit=false` |
| Historical scoped manuscript results | 20 |
| Historical explicit theorem targets | 225 |

The archived build log reports `Build completed successfully (3296 jobs).` These jobs include dependency compilation; they are not 3,296 new theorems. The inherited axiom audit allows `propext`, `Classical.choice`, and `Quot.sound`, and also records declarations that depend on no axioms. The archived register reports 827 declarations in the namespace, including compiler-generated declarations. That number has a different meaning from the current textual count of explicit source declarations.

The fresh static review checks every one of the 225 contract targets against its exact source filename, line, and theorem base identifier, and checks the inherited audit's corresponding axiom record. `verification/RELATED_FORMAL_STATIC_CORRESPONDENCE.json` reports that consistency check. It is separate from the historical build and does not establish that the saved source can be compiled in the current environment.

The 20-result English-to-Lean correspondence in the old scope contract was manually reviewed. A kernel checks the formal type, not whether an English sentence elsewhere in a PDF has been faithfully translated. The current per-SG concordance therefore includes the live Signal statement, hypotheses and domain, the exact related declarations, and an explicit coverage classification.

# How to read the Lean contracts

Lean declarations expose several distinctions that are easy to blur in prose. A function type `E → E` does not assert linearity. A continuous linear map type asserts both linearity and continuity. An equivalence `I ≃ J` supplies inverse functions; a linear isometry equivalence adds linearity and norm preservation. A theorem over an arbitrary type can be algebraic even when the motivating application is an analytic signal.

| Source notation | Meaning used here |
|---|---|
| `[AddCommGroup E]` | An additive commutative group; subtraction and cancellation are available |
| `[SeminormedAddCommGroup E]` | An additive group with a seminorm; distinct vectors can have zero seminorm |
| `[Fintype R]` | A finite index type supporting an exact finite sum |
| `Fin N` | Integers from zero through $N-1$ with a proof of the bound |
| `ℤ →₀ K` | A finitely supported coefficient function, carrying finite support |
| `H →L[ℂ] H` | A continuous complex-linear map |
| `H ≃ₗᵢ[ℂ] H'` | A complex-linear isometric equivalence |
| `HasSum u x` | The series of vectors $u$ converges to $x$ in the specified topology |
| `eLpNorm f p μ` | An extended nonnegative $L^p$ seminorm, possibly infinite |

Section variables apply to declarations below them. For example, a theorem whose printed first line mentions only a phase function may still require a finite phase type and an additive commutative monoid through the preceding `variable` command. The source-anchor inventory records these contexts in words alongside the literal excerpt. The full raw file remains authoritative when replaying the declaration.

A `noncomputable def` is a legitimate mathematical definition. It can use classical choice or operations on arbitrary real values that are not provided as executable algorithms. A proof about such a definition does not certify the performance of a Python implementation. This is particularly relevant to the pruning evaluator, whose real-valued cost comparison is defined noncomputably and whose work theorem concerns an explicit abstract cost model.

# Coordinate packets

The first packet object is a coordinate restriction. Given a phase map $\phi:I\to R$, the packet $P_r x$ retains $x(i)$ exactly when $\phi(i)=r$, and is zero at all other addresses. The formal definition initially requires only a zero value in the coefficient type and decidable equality of phase labels.

{{anchor:packet}}

The idempotence proof is pointwise: at an address in the selected phase, applying the same restriction again retains the same value; outside that phase both restrictions return zero. Distinct phase labels give mutually annihilating restrictions. No Fourier transform, topology, smoothness, or recovery of an unknown phase map enters these proofs.

For a finite phase type and an additive commutative coefficient monoid, the source proves an exact completeness identity.

{{anchor:packet_complete}}

At each address exactly one summand survives, the one indexed by $\phi(i)$. This is a finite algebraic partition identity. It applies to all coordinates simultaneously, including negative integer addresses when $I=\mathbb Z$, but it does not by itself establish an infinite-series reconstruction or a bounded Hilbert-space operator. The later `HilbertPackets` module supplies those stronger structures on a particular signal space.

`packet_refinement` formalizes a fine phase map and a supplied coarsening map. A coarse packet is the sum of the fine packets mapped to its label. The theorem does not discover a favorable partition, infer hidden parameters, or claim that every refinement improves an approximation. It asserts the representation identity when the phase relation is given.

# Addresses and signed integer polyphase coordinates

The address-equivalence abstraction starts with a known bijection $I\simeq R\times Q$. Analysis reads a sequence at the inverse address; synthesis sends each original address to its phase and quotient. Both round trips follow from the bijection. Nothing is discarded, so this is exact coordinate rearrangement rather than recovery from fewer observations.

{{anchor:address_roundtrip}}

The integer specialization makes the division convention explicit. For $N>0$, every $n\in\mathbb Z$ has an address $n=Nq+r$ with $0\le r<N$. The source uses Lean's Euclidean integer division and remainder. For example, when $N=3$ and $n=-1$, the address is $(r,q)=(2,-1)$, not a quotient obtained by truncating toward zero.

{{anchor:integer_equiv}}

The `hN : 0 < N` argument is essential: the phase type `Fin N` must contain the remainder and the coordinate map must be invertible. Analysis itself can be written for any $N$, but the inverse-law theorems require positivity. `IntegerPolyphase.synthesis_analysis` and `analysis_synthesis` prove the two inverse identities for arbitrary coefficient functions.

## Delay conventions

A delay by $d$ in a channel index corresponds to a delay by $Nd$ in the original sample address. A general original-sample delay changes the channel label and introduces a signed carry in the quotient.

{{anchor:sample_delay}}

For $N=3$, output phase $r=0$, and original delay $d=1$, the input address uses phase $2$ and quotient $q-1$. This carry is required by $3q-1=3(q-1)+2$. An implementation that changes the phase label while retaining quotient $q$ computes a different operator.

`residue_refinement` requires positive $N,M$ and $N\mid M$. It is a literal reduction of a finer residue partition to a coarser one. It supplies infrastructure for phase-resolved signal descriptions; it does not prove that aliased exponential nodes can be identified from a selected measurement lattice. That latter claim needs an additional injectivity theorem for the actual observation set.

# The Hilbert-space bridge

The formal Hilbert signal is a complex square-summable sequence. The exponent is part of the definition.

{{anchor:hilbert_signal}}

The coordinate restriction belongs to the same square-summable space because its pointwise magnitude never exceeds the original sequence's magnitude. The source then proves its norm bound, linearity, and continuity, and constructs a genuine bounded linear projector. Idempotence and annihilation now hold as equalities of continuous linear maps.

`projector_complete` says that the finite sum of these bounded projectors is the identity operator. `projector_symmetric` and `projector_orthogonal` establish the inner-product structure. These results strengthen the earlier coordinate identities in a specified analytic space; they are not generic consequences for every topology on every sequence space.

## Exact polyphase energy

The output is square-summable on the **joint index** `Fin N × ℤ`. It is not the supremum norm on a function space of channels. The isometry therefore gives the intended total channel energy.

{{anchor:hilbert_polyphase}}

In conventional notation, if $c_r(q)=x(Nq+r)$, the theorem corresponds to

$$\sum_{r=0}^{N-1}\sum_{q\in\mathbb Z}|c_r(q)|^2
=\sum_{n\in\mathbb Z}|x(n)|^2.$$

The displayed equality interprets the formal norm identity. The proof uses a bijective reindexing of square-summable coordinates, so it does not require a Fourier-series convergence argument.

## Impulses and convergence

{{anchor:impulse_expansion}}

Here `lp.single 2 i (x i)` is a one-coordinate square-summable vector. `HasSum` asserts convergence in the $\ell^2$ norm, not merely formal equality of coefficients. The companion finite-support theorem converts this series to a finite sum when all coefficients outside a supplied finite set vanish. The shift-generated impulse span is dense in the same sequence space.

An impulse in this module is a coordinate vector. It is not the Dirac measure used in the distributional derivative of a discontinuous function on a continuous torus. Moving from a continuous signal to Fourier moments, then to an exponential node model, requires additional definitions and proofs. That bridge is part of the current traditional argument and remains outside this archived formal target set.

# Transfer blocks and finite-support convolution

`FIRTransfer` formalizes convolution by a finitely supported kernel. Its coefficient type is any semiring, and the input is an arbitrary bilateral sequence. This generality is possible because every sum in the time-domain law is finite.

{{anchor:fir_definitions}}

For output channel $k$, input channel $s$, and channel delay $m$, the transfer coefficient is

$$h_{k,s}(m)=h(Nm+k-s).$$

The signed tap formula is derived from the address identity

$$Nn+k-(Nm+k-s)=N(n-m)+s.$$

The `tapEquiv` bijection assigns every original tap to one input-channel/delay pair for each fixed output channel. `transferSupport` and `delays` retain the actual finite support rather than summing an invented infinite tail.

{{anchor:fir_transfer}}

This is an exact operator identity for a supplied kernel. It does not certify a numerical estimator for an unknown kernel, select model order, or prove convergence of an infinite impulse response. To use a bilateral $z$-transform, the associated transform theorems require a nonzero evaluation point and a convergent weighted series for each input channel.

# Finite Laurent filter banks

`FilterBank.Laurent` is the finite Laurent coefficient algebra `AddMonoidAlgebra ℂ ℤ`. A matrix of these coefficients acts on a finite set of complex bilateral channels. The source proves that multiplication of Laurent matrices agrees with composition of the corresponding channel operators, and that impulses distinguish their coefficients.

The perfect-reconstruction statement quantifies over **every** channel sequence. It therefore characterizes the operator identity rather than checking a particular example.

{{anchor:filter_pr}}

`gainDelay c d` is a diagonal matrix whose action is gain $c$ and channel delay $d$. No nonzero-gain hypothesis appears in this equivalence: for $c=0$, it correctly characterizes the zero composite operator. To obtain an invertible reconstruction interpretation one must separately assume the desired nonzero gain.

The exact correspondence is useful because a matrix formula and its implemented signal action must agree. It does not identify the analysis or synthesis bank from unknown data, and it does not supply the frequency-offset calibration introduced in the Signal paper. The offsets are integers; the recovered node locations are continuous.

{{anchor:filter_sample_delay}}

After returning to original sample coordinates, the delay is $Nd$. Replacing it with $d$ changes the claim. The transform-level theorem `bank_transform` also retains `HasTransform` assumptions; arbitrary bilateral inputs need not possess a convergent bilateral transform at a chosen point.

# Supplied known edges

The known-edge result captures the key error cancellation when an edge component is retained exactly. The namespace is **`KomorebiPaperV`**; `KnownEdge` is the filename, not an extra namespace component.

{{anchor:known_edge}}

The function $Q$ is arbitrary. The proof does not need $Q$ to be linear, idempotent, bounded, or a Fourier truncation. Both sides contain the same supplied edge $j$, so additive cancellation removes it. In a seminormed additive group the source immediately obtains the equality of error seminorms.

This is a meaningful formal statement, but its strength is conditional: the edge has already been supplied exactly. It contains no edge locations, jump amplitudes, measured moments, noise bound, Hankel matrix, or unknown-order recovery algorithm.

When the supplied edge is an estimate, the algebraic decomposition and triangle inequality give a two-term error budget.

{{anchor:estimated_edge}}

In an $L^p$ application, one can instantiate the relevant normed-space structure once the functions represent members of that space. A rate for $s-Qs$ and a bound for $j-\widehat j$ remain separate analytic obligations. The source does not provide them simply because the cancellation theorem is available.

The current resolved-synthesis inequality may require a bounded **linear** reconstruction map $A_M$ when it moves an edge-estimation error through that map. That assumption serves a different purpose from the arbitrary $Q$ in exact known-edge cancellation. The two contracts should not be merged.

# Measurable masks and extended norms

The mask object `jump S a` is the function equal to complex amplitude $a$ on a set $S$ and zero elsewhere. The exact equal-amplitude mask error is controlled by the measure of the symmetric difference. For finite exponent the source uses an extended-valued norm.

{{anchor:mask_finite}}

The hypotheses are measurable $S,T$, an arbitrary measure $\mu$, $1\le p<\infty$, and complex amplitudes $a,b$. The right side separates amplitude error on the original mask from a changed-mask term:

$$\|a-b\|\,\mu(S)^{1/p}+\|b\|\,\mu(S\mathbin{\triangle}T)^{1/p}.$$

This conventional finite expression is an interpretation when the indicated quantities are finite. The actual Lean statement lives in `ENNReal` and remains valid if an extended norm or measure is infinite. One must establish finiteness before translating it into ordinary real arithmetic. In particular, `ENNReal.toReal` is not a safe automatic coercion of an arbitrary extended inequality: it sends infinity to zero.

The full-signal theorem adds the background error and assumes that both backgrounds are almost everywhere strongly measurable. It is again a bound for supplied functions, masks and amplitudes. It is not a theorem deriving those masks from observations.

## Infinity norm and actual set equality

{{anchor:mask_infinity}}

The source's indicator condition is **$S\triangle T=\varnothing$ as an actual set**. It is not the assertion that the symmetric difference has measure zero. The proof first establishes a bound at every point and then passes to the essential supremum. Consequently this bound can remain coarse even if the masks agree almost everywhere. Replacing its set condition by a measure-zero condition would state a different theorem, although a sharper essential-supremum theorem may be possible with an additional argument.

Small displacement of a jump can produce a small finite-$p$ error and a nonvanishing infinity error. This is why an unknown-edge location estimate alone does not automatically yield uniform signal convergence across discontinuities. A Fourier reconstruction also determines an almost-everywhere class unless a representative, such as a right-continuous one, is fixed.

## The zero-mean periodic edge bound

The traditional paper repairs the location term in a zero-mean periodic edge estimate. For the period-$T$ sawtooth $G(x)=1/2-x/T$, interpreted periodically, its distributional derivative is $\delta_0-dx/T$. For canonical mean-zero packets with matched real jumps, both amplitude sums zero, and circular displacement $d_\ell\le T/2$, the repaired estimate is

$$\|j-\widehat j\|_1\le
\frac{T}{4}\sum_\ell |a_\ell-\widehat a_\ell|
+2\sum_\ell |\widehat a_\ell|d_\ell(1-d_\ell/T).$$

The factor two comes from the translated **zero-mean** sawtooth, not merely the measure of one interval. The old printed bound without that factor fails even for a shifted single interval with its mean removed. The original source is preserved; the corrected statement appears in the new paper and review. `MaskPerturbation.finite_p_perturbation` provides related indicator-function infrastructure, but it does not formalize this periodic primitive calculation. The new sawtooth bound has a prose proof and finite controls, without a recovered Lean target.

# Finite packet trees and complete prunings

The finite-tree formalization distinguishes a complete representation from an arbitrary collection of convenient packets. A cut either stops at a node or splits into cuts of all children. A complete node set meets each terminal path exactly once. The source proves the equivalence between complete sets and covering antichains and provides an equivalence with the inductive cut type.

Under a conservation law saying that each parent value is the sum of its child values, every complete pruning synthesizes the root. For operator-valued labels this yields an actual identity on the input space.

{{anchor:pruning_synthesis}}

The conservation assumption `h` and root identity `hr` are input hypotheses. The result proves their propagation to a complete covering antichain; it does not verify that a particular image dictionary satisfies them. Nor does it assert that packets selected by an unrelated greedy fitting routine form such an antichain.

The finite grammar matters. The proof uses finite sums and a finite cut type. An ideal unbounded family of geometric packets and an implementation with finite candidate caps require different arguments for approximation, convergence, or selection.

# Selection, optimality, and work

For an additive node-cost objective the formal evaluator compares stopping at the current node with splitting into all child solutions. Its real-valued costs are supplied inputs, and it stops on ties.

{{anchor:pruning_solver}}

`solve_correct` identifies both its reported cost and its chosen cut with the already proved dynamic-programming value and minimizer. `computed_antichain_optimal` carries this additive optimum to a complete antichain.

{{anchor:pruning_work}}

The work expression counts one node visit, one comparison at each internal node, and one addition per child when summing cached values. The linear bound excludes the cost of producing node costs, geometric fitting, numerical linear algebra, storage of a fully expanded output, and wall-clock execution of Lean or Python. The source makes this unit-cost model explicit.

For a possibly nonadditive objective $R(S)+\eta L(S)+\tau K(S)$, the source proves existence of a minimizer because the admissible pruning family is finite. That does not imply that the same local recurrence computes it. A globally coupled leakage term can break the additive decomposition needed by dynamic programming.

## Stability needs a margin

The antichain selector theorem assumes a positive objective gap $\gamma$ and an error envelope satisfying $2E<\gamma$. The arbitrary-objective stability theorem similarly assumes a uniform error bound and the same strict margin. These hypotheses give a precise conditional statement. They do not derive a margin from a noise level alone.

The Signal branch-selection argument has the same logical structure: estimation error must be smaller than the separation of competing branches. A rate $O(1/N)$ does not automatically beat a branch spacing also of order $1/N$. The constants and a strict margin must remain in the theorem.

# The unformalized Signal obligations

The following obligations explain the gap between supplied-edge infrastructure and unknown-edge reconstruction. They identify concrete mathematical dependencies rather than treating all missing work as a single label.

## Continuous signals to exponential moments

The observation model must fix the torus period and Fourier normalization, define the discontinuous edge component and its representative, and prove the distributional derivative and integration-by-parts relation. The recovered Paper V sequence-space impulses do not provide this continuous distributional theorem. Zero mean, zero total jump, and the missing constant coefficient must be handled explicitly.

If the smooth component occupies a known finite Fourier band, the out-of-band derivative moments reduce to a finite exponential sum $y_n=\sum_{\ell=1}^L a_\ell z_\ell^n$. The hypotheses include distinct nonzero unit-circle nodes and nonzero amplitudes after removing redundant zero jumps. The order-zero case is a separate exact branch, with no polynomial roots to solve.

## Hankel factorization and annihilation

A dedicated formalization would need the finite Hankel factorization, Vandermonde invertibility, rank under the distinct-node hypotheses, the annihilating recurrence, and uniqueness of the recovered polynomial. None is a target in the preserved Paper V contract. The prose proof can use standard finite-dimensional linear algebra, but finite computations of ranks or roots do not certify the universal statement.

The full algebraic reconstruction includes polynomial root extraction and matching, not only linear algebra. A computational root routine can choose branches or return noisy approximations; its connection with an exact finite-set theorem must be stated separately.

## Dictionary null secants

For a nuisance basis $B$ and edge dictionary $D$, the exact identifiability condition excludes every nonzero sparse coefficient difference from the kernel of the nuisance-projected dictionary. It must distinguish a full-column-rank basis from a rank-deficient set of columns and define the sparse support size correctly.

Under the usual convention that a full-column-rank $m\times n$ matrix has spark $n+1$, the familiar spark condition must be capped at $\min(2s,n)$; a different infinity convention must be declared if used. For a wide support submatrix, the compact SVD lists only $\min(m,k)$ singular values. A positive last returned singular value does not eliminate a column nullspace when $k>m$. Its restricted separation is zero. The numerical execution copy now tests these cases explicitly; this remains computational evidence rather than a Lean theorem.

## Perturbation, roots, and matching

The singular-value threshold argument uses a spectral-norm perturbation bound. A guaranteed order gate requires a supplied threshold between the noise bound and the lower bound on the last nonzero singular value. The largest adjacent singular-value ratio is a practical heuristic with a different contract.

An exact stress witness uses three unit-circle nodes $1,i,-1$, amplitudes $100,-99,-1$, and a $4\times4$ Hankel matrix. Its singular values are $(400,396,4,0)$. Adding $0.1(-i)^n$ gives $(400,396,4,0.4)$ with perturbation norm $0.4<4/2$. The largest adjacent ratio is $396/4=99$, exceeding $4/0.4=10$, so the ratio rule chooses order two. A supplied threshold in $(0.4,3.6)$ still selects the correct order three. The exact Fourier-matrix diagonalization verifies this example; no new Lean certificate is asserted for it.

The Rouché root-disk argument requires disjoint true-root disks, a strict boundary inequality, and a coefficient error bound. For unit-circle root centers, $|z|\le1+\rho$ supplies the factor $\sum_k|\delta q_k|(1+\rho)^k$. This is a deterministic conditional stability certificate. Its true centers and true coefficient errors are not generally available from the observed data alone, so the theorem is not an independently computable a posteriori test without further estimates.

Location error must be measured after a specified matching, using a circular distance. An amplitude bound then needs the conditioning of the corresponding Vandermonde system. Without separation, uniformly Lipschitz location recovery fails even for fixed-order pairs of narrow pulses; it is not enough to give only a variable-order or undefined-metric example.

## Self-calibration and branch resolution

The multi-offset phase identity requires at least one adjacent product. A branch-spacing statement requires at least two candidate branches. Phase denominators must be nonzero and must remain bounded away from zero for a stable inverse. The source's integer polyphase coordinate equivalence has none of these data-dependent quantities.

A complete formal statement would need the frequency-offset observation model, the phase-product identity, the normalization/inversion gate, the alias candidate set, the chosen branch metric, the strict separation margin, and the final reconstructed-signal bound. The offsets in this model are integers, while node locations vary continuously. Exact integer address arithmetic is relevant infrastructure but proves none of those estimation gates automatically.

## Resolved synthesis and signal norm

After estimating an edge, the background recovery must be specified as a bounded linear map on the relevant error space when the proof uses its operator norm. The final error estimate combines background reconstruction, edge-estimation error, and any truncation or approximation term. Fourier information yields an almost-everywhere class, so pointwise statements at jumps require a fixed representative. The corrected periodic $L^1$ bound and the nonvanishing infinity error must retain their different conclusions.

# Computation is a separate evidence layer

The release preserves the original run records and fresh finite replays, including negative cases. The initial complex benchmark validation required finite location and jump errors in every case. That condition failed: in `bursts_6_jump`, the model-order heuristic estimated nine jumps instead of six, and the evaluator reported infinite location and jump errors for the unmatched orders. The improved reconstruction RMSE was finite. These facts can coexist; improved signal error does not establish correct parameter identification.

The follow-up report scopes the benchmark to its actual measured outputs and retains the order-mismatch stress failure. The original failed record remains available. Neither the benchmark nor its follow-up is a theorem proving reliable recovery of every complex signal.

The generic dictionary runner also required repairs. A QR basis computed from rank-deficient nuisance columns can include additional orthogonal directions; its projector then removes more than the intended column space. Compact SVD can falsely suggest positive separation for a wide support. The preserved original source and the rank-aware execution copy are distinct, with negative controls and provenance recording the correction. The traditional theorem handles the zero-edge branch explicitly. The native `EdgeModel` and `recover_unknown_edges` API still exclude order zero; the dictionary rank correction did not add an order-zero wrapper.

## Adaptive image packets

The standalone image scripts receive the complete image array. They fit and extend a packet dictionary using those pixels, and their pixel-completion routine can retain the remaining residual. This is adaptive approximation of available data. It is not unknown-edge recovery from a finite collection of Fourier measurements.

Several additional limits matter when comparing the implementation with exact packet theory:

- The ideal geometric grammar is unbounded, while the tested generator uses finite candidate and mask caps.
- The default ridge term modifies least-squares refitting. Its mathematical residual law is exactly $M^{\mathsf T}r=\lambda c$. Numerical checks test that law within tolerance. The generally nonzero right side distinguishes ridge refitting from exact orthogonal projection onto a nested subspace.
- Clipping a reconstruction to $[0,1]$ is nonlinear. For truths in that box it can improve the pixel error, but it is not the bounded linear operator used by the resolved-synthesis proof.
- Retaining a full residual gives an exact archive identity; it does not prove sparse compression or recovery from missing data.
- Some historical per-method runtime fields are zero placeholders because the implementation checked a method label that did not match the stored labels. Case-level runtime and fresh measurements must be read separately.

Finite tolerances in reconstruction, monotonicity, and stationarity tests are part of those computational contracts. Passing them supports the tested cases and tolerances. It does not turn the finite dictionary, ridge refit, or greedy search into the ideal complete-pruning theorem.

# Concordance with the traditional paper

The machine-readable map `lean/Claim_Lean_Concordance.json` copies each current SG statement, hypotheses, and domain from `traditional/Claim_Concordance.json`, and records the hash of that live input. Related declaration anchors include qualified names, exact source files, lines and SHA-256 hashes. A corresponding CSV supports inspection without a JSON reader.

The classification “direct supplied-object contract” is used only when the archived theorem gives the relevant algebraic or operator implication after an explicitly described instantiation. “Related infrastructure” identifies a narrower result that helps express the mathematics but does not prove the whole SG claim. “No recovered target” means no declaration for that claim was identified in the inspected 225-target corpus; it does not assert that the mathematics is impossible to formalize or absent from all Lean libraries.

{{concordance}}

The prose interpretation field is deliberately separate from `source_quoted`. An association does not silently import a Fourier model, observation scheme, numerical algorithm, or omitted hypothesis into the Lean type.

# Reproducing and inspecting the evidence

From the release root, the static inventory and correspondence checks can be regenerated without Lean:

```text
python lean/build_lean_inventory.py
python verification/check_related_formal.py
python lean/build_lean_guide.py
python build_release.py --only lean
```

The first two commands inspect saved source and saved evidence. The guide builder writes Markdown, TeX, anchors, and the per-claim map from those inputs; the publication builder invokes pdfLaTeX. None performs a formal proof check.

With the pinned Lean toolchain and Mathlib dependency installed, the preserved project's focused historical commands can be replayed from its Lean folder:

```text
cd related_formal/paper_v/formalization/lean
lake env lean --version
lake build KomorebiPaperV
lake env lean -DwarningAsError=true KernelAudit.lean
```

These are future replay instructions, not commands reported as executed for this Signal edition. The `lake-manifest.json` pins the recorded dependency identity. Dependencies and a compatible toolchain must actually be available; the source archive alone does not supply an executable runtime. The selected related-source subset is sufficient to inspect the proof targets, but the original all-purpose `verification/verify.py` expects the full Paper V distribution and should not be treated as a self-contained Signal driver.

The verification register and run directories distinguish current computations, source preservation, static related-formal inspection, and inherited compiler logs. If the sources or claims change, the mappings must be regenerated and their input hashes reviewed. A later successful full Signal formalization would need its own source tree, typed observation model, target contract, actual build and axiom evidence, and English-to-formal correspondence review.

# Source inventory

The current textual inventory scans nested-comment and string-masked source and includes noncomputable declarations. It finds **23 production modules and 349 explicitly named declarations**: 225 theorems, 107 definitions, seven abbreviations, nine inductive types, and one structure. All production modules occur in the root import list. Including the root import file and axiom harness gives 25 Lean files.

The 225 explicit theorem declarations agree with the checked target contract's names, files, lines and kinds. The remaining named declarations define the objects, coordinate maps, finite trees, evaluators, and related structures. The count measures a preserved source corpus, not independent new results or the completion percentage of Signal formalization.

{{modules}}

Full declaration and module inventories are included in JSON and CSV. `lean/SOURCE_ANCHORS.json` contains the exact quoted excerpts used in this guide, their contexts, their interpretations, and their source hashes. `reviews/LEAN_REPORT.md` records the current review and publication checks. Original `.md` materials and source maps are included with the release so that readers can inspect the mathematical statements and their changes alongside the PDFs.
