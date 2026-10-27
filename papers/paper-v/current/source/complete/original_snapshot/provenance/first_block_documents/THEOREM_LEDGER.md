# Paper V theorem ledger

**Status: no theorem in this package has been kernel-checked in the producing environment.**

Baseline: the 31-page adaptive-tree-resolved PDF. Candidate means drafted Lean source, not accepted proof. The generic norm-error lemma supporting 7.1 is not its measure-theoretic assertion.

| Result | Page | Source candidate | Remaining obligation |
|---|---:|---|---|
| Theorem 1.1: Impulse seed theorem | 4 | none | l2 impulse representation, shift action, and dense span remain to be formalized. |
| Theorem 2.1: Polyphase projector theorem | 4 | partial_candidate | Literal integer residue identities are pointwise; l2 membership, linearity, boundedness, and operator-level bridge remain. |
| Corollary 2.2: Analysis–synthesis identity | 5 | partial_candidate | Both inverse laws for an arbitrary address equivalence. Construct the integer quotient/remainder equivalence and channel Hilbert-space bridge. |
| Theorem 2.3: Exact nested refinement | 6 | partial_candidate | Abstract fiber refinement only. Prove the N-divides-M integer residue factorization and its operator interpretation. |
| Theorem 3.1: Exact FIR polyphase transfer law | 6 | none | Signed FIR finite models tested. Formal finite-sum reindexing, literal transfer kernels, and a legitimate transform interpretation remain. |
| Theorem 4.1: Perfect-reconstruction criterion | 8 | none | Correct channel-delay versus original-sample-delay convention before formalizing the matrix equivalence. |
| Corollary 4.2: Haar energy identity | 8 | none | The rational pair polynomial identity is tested only; normalized Haar and l2 energy are not formalized. |
| Theorem 4.3: Exact lifting reconstruction | 8 | partial_candidate | Both pair inverse laws, determinant, equivalence, and pointwise coordinates are drafted. Explicit even-length signal indexing remains. |
| Theorem 5.1: Wavelet-packet reconstruction and energy | 10 | none | Normalized Haar Hilbert-space map, finite-depth operators, adjoints, and energy sums remain. |
| Theorem 6.1: Exact known-edge theorem | 11 | matching_statement_candidate | Algebraic and norm equalities are drafted at the stated generality. Still requires successful Lean compilation and axiom audit. |
| Corollary 6.2: Several exact edge packets | 11 | matching_statement_candidate | Finite-sum algebraic and norm equalities are drafted. Still requires successful Lean compilation and axiom audit. |
| Theorem 7.1: Packet perturbation bound | 11 | supporting_candidate_only | Only generic error separation and triangle bound. Measurable indicator functions, finite Lp norms, symmetric-difference norm formula, and L-infinity clause remain. |
| Theorem 11.2: Exact synthesis from every complete pruning | 18 | partial_candidate | Recursive binary cuts conserve the root value under local additive conservation. Arbitrary arity, antichain/path correspondence, and projector operator bridge remain. |
| Theorem 11.3: Finite globally optimal stable selector | 19 | partial_candidate | Finite minimum, positive competitor gap, strict perturbation stability, and singleton case are drafted. Identify finite complete-pruning set and connect exact synthesis. |
| Theorem 11.4: Dynamic-programming best packet basis | 19 | partial_candidate | Binary recursive-cut optimizer and global optimum are drafted with stop-on-tie. Arbitrary arity, antichain bridge, and formal operation-count theorem remain. |
| Corollary 11.5: Local perturbation certificate | 20 | partial_candidate | Binary per-cut envelope and general margin lemma drafted separately. Combine for arbitrary finite trees; state probability clause on a joint event. |
| Theorem 12.1: Cyclic product law | 22 | none | Formal-series residue product and iterated power clauses remain. Prior-paper reuse is not counted without an explicit checked import and semantic map. |
| Theorem 13.2: Polyphase Möbius action | 23 | none | Projective-coordinate correction supplied. Formal complex phase representation and projective or admissible-chart action remain. |
| Corollary 13.3: Impedance–admittance is the two-phase split | 23 | none | Two-phase projective inversion or finite-chart theorem with nonzero input remains. |
| Proposition 14.1: Dyadic–odd packet factorization | 26 | none | Literal CRT residue masks, coprimality, and dyadic-odd specialization remain. |
