# Paper V theorem ledger, v0.3.0

Author: Komorebi P.

The release verifier checks **133 Lean theorem targets in 14 proof modules**. The manuscript has **20 theorem-like results**. These are different counting units. All listed supporting targets are checked, but the full manuscript is not certified.

`matching_statement` means the stated mathematical content has a checked realization. `partial` and `supporting_only` retain explicit obligations. This is a manual scope assessment, not a mechanized proof that a PDF matches Lean.

| Result | Source scope | Checked content | Remaining boundary |
|---|---|---|---|
| 1.1 Impulse seed theorem | checked_matching_statement | Impulse l2 expansion, finite-support expansion, dense shift-generated span, and unitary integer shift action. | No remaining mathematical statement obligation identified in this coordinate realization. |
| 2.1 Polyphase projector theorem | checked_matching_statement | Bounded complex l2 projectors, idempotence, annihilation, exact sum, symmetry, and orthogonality. | No remaining mathematical statement obligation identified. |
| 2.2 Analysis–synthesis identity | checked_matching_statement | Signed integer address equivalence lifted to a linear isometry equivalence, with both inverse laws. | The Hilbert channel space is represented by joint l2 coordinates on Fin N × Z. |
| 2.3 Exact nested refinement | checked_matching_statement | Literal divisible-modulus refinement of bounded complex l2 operators. | No remaining mathematical statement obligation identified. |
| 3.1 Exact FIR polyphase transfer law | checked_partial | Literal finite-support time-domain FIR transfer and signed tap bijection. | A legitimate z-transform/Fourier interpretation and transform-domain transfer bridge remain. |
| 4.1 Perfect-reconstruction criterion | checked_supporting_only | Matrix equality iff equality on all vectors; signed sample and channel delay identities. | Concrete filter-bank operator/matrix representation and transform-domain equivalence remain. |
| 4.2 Haar energy identity | checked_partial | Normalized finite real Haar and infinite complex l2 channel Haar reconstruction and energy identities. | An explicit equality between the sum of the two channel energies and the norm of the original interleaved signal remains to be packaged as a theorem. |
| 4.3 Exact lifting reconstruction | checked_matching_statement | Both pairwise lifting inverses, determinant one, and flat even-length signal reconstruction. | No remaining mathematical statement obligation identified. |
| 5.1 Wavelet-packet reconstruction and energy | checked_supporting_only | Hilbert Haar energy, bounded orthogonal masks, and recursive cut synthesis under conservation. | Finite-depth packet analysis/synthesis operators, adjoints, and the full packet energy decomposition remain. |
| 6.1 Exact known-edge theorem | checked_matching_statement | Exact cancellation and norm equality in arbitrary seminormed additive groups. | No remaining mathematical statement obligation identified. |
| 6.2 Several exact edge packets | checked_matching_statement | Finite collections of exact edge packets with exact cancellation and norm equality. | No remaining mathematical statement obligation identified. |
| 7.1 Packet perturbation bound | checked_supporting_only | Generic separation of smooth and estimated-edge norm errors. | Measurable masks, finite-p symmetric-difference norm formula, amplitude bound, and the L-infinity clause remain. |
| 11.2 Exact synthesis from every complete pruning | checked_partial | Recursive cuts are equivalent to set-valued covering antichains; synthesis holds for every conserved additive node family. | Explicit finite-set node-sum and concrete packet-projector specialization remain. |
| 11.3 Finite globally optimal stable selector | checked_partial | Finite set-valued complete-pruning space, arbitrary-objective minimum, singleton handling, positive gap, and generic stability. | Transport the named manuscript objective and stable chosen selector through the equivalence in one explicit theorem. |
| 11.4 Dynamic-programming best packet basis | checked_partial | Arbitrary-branching global optimizer, stop on ties, and complete-antichain equivalence. | Explicit node-sum cost correspondence and an operational complexity theorem remain. The current comparison count is a structural recurrence. |
| 11.5 Local perturbation certificate | checked_partial | Exact cut-envelope maximum, value perturbation, strict-gap stability, and probability transfer from a joint local-error event. | Concrete antichain/projector cost specialization remains. |
| 12.1 Cyclic product law | none | No source coverage added. | Formal-series cyclic multiplication and iterated-power clauses remain. |
| 13.2 Polyphase Möbius action | checked_partial | Normalized homogeneous action composition, scaling compatibility, nonzero-pair preservation, and admissible-chart composition. | Explicit exponential root-of-unity normalization, modulo-N group law, and quotient-level projective action remain. |
| 13.3 Impedance–admittance is the two-phase split | checked_partial | Half-turn swaps homogeneous coordinates, including zero/infinity; inversion is proved on the nonzero finite chart. | The explicit identity exp(pi*i) = -1 is not yet connected to the named N=2 action. |
| 14.1 Dyadic–odd packet factorization | checked_matching_statement | Chinese-remainder residue-mask factorization and dyadic-odd specialization. | No remaining mathematical statement obligation identified. |
