# Paper V expanded-manuscript review, v1.1.0

Author: Komorebi P.

The current deliverable is the full 39-page `Paper_V_Expanded_Lean_Checked.pdf`, expanded from the recovered 31-page manuscript. All 20 theorem-like result numbers are unchanged, and every result now has an explicit proof. Appendix D gives the statement correspondence, trust boundary, numerical conventions, and reproduction instructions.

## Source recovery

The original adaptive-tree-resolved release was recovered from `Projector_Seed_Calculus_Two_Finite_Conjectures_Resolved_Handoff.zip`. Its manuscript PDF has SHA256 9b1cbe3c771f90fae651d13eeb41a05804953d9f923bc1160a3e1b385b571e85, identical to the previously preserved baseline. The release includes the actual TeX, all figures, Python sources, numerical data, and all 33 original tests. It is preserved under `provenance/original_companion/`.

## Mathematical and editorial changes

1. Expanded the impulse proof to give the convergent Hilbert-space sum and density argument; made the complex scalar field and adjoint convention explicit.
2. Added boundedness, symmetry, orthogonality, and the correct joint Hilbert channel norm. Clarified that coarse/fine masked packets are added on a common integer lattice.
3. Gave the signed FIR tap bijection and justified the transform step using weighted absolute summability at nonzero z.
4. Specified square finite Laurent/FIR banks; explained faithful impulse testing, polynomial equality, gain, and channel delay. Added the general sample-delay permutation and the two-channel one-sample example.
5. Expanded literal complex Haar energy and finite-depth reconstruction using bounded operators, true adjoints, and polarization. Finite lengths must support the requested dyadic depth.
6. Added the missing explicit proof for several retained packets, including the empty family. Clarified measurable masks, extended finite-p norms, finite-valued conditions, and pointwise versus essential supremum.
7. Handled empty competitor sets in singleton tree selection; specified stop on ties, arbitrary positive arity, the recursive-cut/antichain equivalence, exact maximum error envelopes, strict gaps, joint probability events, and the unit-cost complexity boundary.
8. Stated the formal-series product/power theorem with explicit phase ranges and the exponent-zero empty product. Analytic evaluation retains convergence conditions.
9. Replaced pole-ambiguous Smith statements by a projective action; proved composition using homogeneous matrices, and made zero/infinity exchange explicit. Corrected the Cayley image of the finite closed half-plane and the sensitivity domain. The refinement figure describes nested rays rather than sums of impedance points.
10. Corrected Fourier cutoff 18 to 37 bins in the 1D certificate and Figure 6 axis. Specified the square 2D cutoff, coefficient budgets, and conjugate-pair convention. Clarified finite-iteration harmonic filling. Corrected “Harmically,” the 16/18 figure-count discrepancy, and uncaptained table entries.

## Executed evidence

The actual combined result is in `verification/paper_release_status.json`. Lean's 225 theorem targets and all 827 namespace declarations pass the build/axiom audit with warnings as errors. Only the three disclosed standard axioms occur. No Lean proof source was added or changed by this manuscript revision; Lake's release metadata advanced to 1.1.0.

The original companion suite passes 33 tests. Its numerical JSON reproduces exactly here, including all scalar errors/residuals and the depth-five 458,330-pruning comparison. All 18 figure pairs were regenerated; the only companion source edit corrects the Figure 6 axis wording. The independent suites retain 20 mathematical tests and 305,933 exact assertions; the verifier suite has 16 controls. Total across the three test families: 69.

The final TeX build has no LaTeX/package warnings or overfull/underfull boxes. All mathematical result numbers, 18 figure references, and six table captions are checked. The final PDF was rendered on every page and visually reviewed. The original PDF, source, figures, and numerical data remain available for comparison. The earlier supplement is superseded by the integrated manuscript and archived under `provenance/v1_0_0_checkpoint/`.

## Limits

The twenty-row manuscript-to-Lean correspondence is a manual mathematical review. The numerical Python implementation, physical modelling context, and prose are not themselves proved correct by the Lean kernel. The floating-point optimum gap is a numerical certificate, not interval arithmetic. The two edge-recovery conjectures remain open, as do unclaimed infinite-tree/statistical and optimal-sampling extensions. No claim of mathematical novelty or independent proof count is inferred from source declaration totals.
