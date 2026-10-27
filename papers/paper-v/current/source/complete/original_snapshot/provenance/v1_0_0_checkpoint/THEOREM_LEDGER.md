# Paper V scoped theorem ledger, v1.0.0

Author: Komorebi P.

All 20 theorem-like manuscript results have a formal counterpart in this **corrected, scope-explicit contract**. There are 225 theorem targets in 23 proof modules. The authoritative build/audit result is verification/verification_status.json. The PDF-to-Lean comparison is a manual review, not a kernel-checked equivalence between documents.

The preserved 31-page manuscript must be read with the updated correction supplement. Conjectures, numerical examples, novelty, and reference implementations are outside the 20-result denominator.

| Result | Checked scope |
|---|---|
| 1.1 Impulse seed theorem | Complex l2 impulse expansion, finite-support identity, unitary shifts and dense shift-generated span. |
| 2.1 Polyphase projector theorem | Bounded orthogonal residue projectors on complex l2. |
| 2.2 Analysis–synthesis identity | Signed integer polyphase linear isometry; channels represented by joint l2 coordinates. |
| 2.3 Exact nested refinement | Literal divisible-modulus bounded projector refinement. |
| 3.1 Exact FIR polyphase transfer law | Time-domain transfer for every bilateral sequence; channel z-transform identity for z nonzero wherever each weighted input series is summable. |
| 4.1 Perfect-reconstruction criterion | Concrete finite Laurent/FIR banks on every bilateral sequence, faithful matrix/operator correspondence, gain and channel delay; original-sample delay is N*d. Arbitrary scalar-matrix criterion is also retained in FiniteTransforms. |
| 4.2 Haar energy identity | Literal interleaved input and normalized low/detail channels in complex l2. |
| 4.3 Exact lifting reconstruction | Pairwise predict/update inverse and determinant one, with both flat finite-signal inverse laws. |
| 5.1 Wavelet-packet reconstruction and energy | All finite depths of literal Haar packet operators; sums of true Hilbert adjoints reconstruct, and packet norms preserve energy. |
| 6.1 Exact known-edge theorem | Exact known-edge cancellation in arbitrary seminormed additive groups. |
| 6.2 Several exact edge packets | Finite families of exactly retained jump packets. |
| 7.1 Packet perturbation bound | Measurable scalar masks in arbitrary measure spaces; extended finite-p norms, and pointwise plus essential supremum bounds. Finite mask and symmetric-difference measures yield the finite real-valued statement. |
| 11.2 Exact synthesis from every complete pruning | Literal finite node sums over covering antichains, with exact operator and applied-signal synthesis under the manuscript conservation hypotheses. |
| 11.3 Finite globally optimal stable selector | Named nonadditive representation/leakage/complexity criterion; attained positive gap when competitors exist, uniform perturbation stability, and singleton case. Every pruning preserves synthesis. |
| 11.4 Dynamic-programming best packet basis | Cached bottom-up evaluator equals the global selector; stop on ties. One comparison per internal node; at most 3*node-count unit operations for visits/comparisons/value additions with node costs supplied. Not a Lean runtime or scalar-cost evaluation bound. |
| 11.5 Local perturbation certificate | Exact maximum antichain error envelope and strict-gap stability; probability transfer from a joint local-error event is proved in PruningAlgorithm. |
| 12.1 Cyclic product law | Formal power-series cyclic product and literal q-tuple power formula over commutative semirings, including q=0. Analytic interpretations apply on their convergence domains; no arbitrary divergent evaluation is asserted. |
| 13.2 Polyphase Möbius action | Explicit exponential root of unity and modulo-N action on the projective quotient of nonzero homogeneous pairs; Cayley conjugacy and the finite-chart formula. |
| 13.3 Impedance–admittance is the two-phase split | The N=2 phase is -1; its action swaps homogeneous coordinates, exchanging zero/infinity and giving inverse impedance on the nonzero chart. |
| 14.1 Dyadic–odd packet factorization | Signed integer CRT residue masks and dyadic-odd factorization. |
