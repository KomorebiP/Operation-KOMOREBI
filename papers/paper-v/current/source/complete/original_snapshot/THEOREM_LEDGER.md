# Paper V theorem ledger, v1.1.0

Author: Komorebi P.

All 20 theorem-like results in the expanded 39-page manuscript have reviewed formal counterparts: 225 Lean theorem targets in 23 proof modules. The manuscript now states the checked hypotheses directly and supplies 20 explicit proofs. Result numbering is preserved; page numbers below refer to the expanded PDF. The PDF-to-Lean mathematical correspondence is manually reviewed.

Conjectures and numerical certificates are separate from this count. The 33 original numerical tests have been rerun, alongside the 36 independent-model/verifier tests. See verification/paper_release_status.json for the combined result.

| Result | Page | Checked scope |
|---|---:|---|
| 1.1 Impulse seed theorem | 5 | Complex l2 impulse expansion, finite-support identity, unitary shifts and dense shift-generated span. |
| 2.1 Polyphase projector theorem | 6 | Bounded orthogonal residue projectors on complex l2. |
| 2.2 Analysis–synthesis identity | 6 | Signed integer polyphase linear isometry; channels represented by joint l2 coordinates. |
| 2.3 Exact nested refinement | 8 | Literal divisible-modulus bounded projector refinement. |
| 3.1 Exact FIR polyphase transfer law | 8 | Time-domain transfer for every bilateral sequence; channel z-transform identity for z nonzero wherever each weighted input series is summable. |
| 4.1 Perfect-reconstruction criterion | 10 | Concrete finite Laurent/FIR banks on every bilateral sequence, faithful matrix/operator correspondence, gain and channel delay; original-sample delay is N*d. Arbitrary scalar-matrix criterion is also retained in FiniteTransforms. |
| 4.2 Haar energy identity | 10 | Literal interleaved input and normalized low/detail channels in complex l2. |
| 4.3 Exact lifting reconstruction | 11 | Pairwise predict/update inverse and determinant one, with both flat finite-signal inverse laws. |
| 5.1 Wavelet-packet reconstruction and energy | 12 | All finite depths of literal Haar packet operators; sums of true Hilbert adjoints reconstruct, and packet norms preserve energy. |
| 6.1 Exact known-edge theorem | 12 | Exact known-edge cancellation in arbitrary seminormed additive groups. |
| 6.2 Several exact edge packets | 13 | Finite families of exactly retained jump packets. |
| 7.1 Packet perturbation bound | 14 | Measurable scalar masks in arbitrary measure spaces; extended finite-p norms, and pointwise plus essential supremum bounds. Finite mask and symmetric-difference measures yield the finite real-valued statement. |
| 11.2 Exact synthesis from every complete pruning | 21 | Literal finite node sums over covering antichains, with exact operator and applied-signal synthesis under the manuscript conservation hypotheses. |
| 11.3 Finite globally optimal stable selector | 21 | Named nonadditive representation/leakage/complexity criterion; attained positive gap when competitors exist, uniform perturbation stability, and singleton case. Every pruning preserves synthesis. |
| 11.4 Dynamic-programming best packet basis | 22 | Cached bottom-up evaluator equals the global selector; stop on ties. One comparison per internal node; at most 3*node-count unit operations for visits/comparisons/value additions with node costs supplied. Not a Lean runtime or scalar-cost evaluation bound. |
| 11.5 Local perturbation certificate | 23 | Exact maximum antichain error envelope and strict-gap stability; probability transfer from a joint local-error event is proved in PruningAlgorithm. |
| 12.1 Cyclic product law | 25 | Formal power-series cyclic product and literal q-tuple power formula over commutative semirings, including q=0. Analytic interpretations apply on their convergence domains; no arbitrary divergent evaluation is asserted. |
| 13.2 Polyphase Möbius action | 27 | Explicit exponential root of unity and modulo-N action on the projective quotient of nonzero homogeneous pairs; Cayley conjugacy and the finite-chart formula. |
| 13.3 Impedance–admittance is the two-phase split | 27 | The N=2 phase is -1; its action swaps homogeneous coordinates, exchanging zero/infinity and giving inverse impedance on the nonzero chart. |
| 14.1 Dyadic–odd packet factorization | 30 | Signed integer CRT residue masks and dyadic-odd factorization. |
