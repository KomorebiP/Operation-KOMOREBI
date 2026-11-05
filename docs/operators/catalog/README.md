# Operator catalog

[Operator guide](../../OPERATOR_AUDIT.md) · [Catalog](README.md) · [Composition laws](RELATIONS.md) · [Worked calculations](../COMPOSITION.md) · [Finite checks](CHECKS.md)

Find a named operation, inspect its formula and assumptions, then follow its source or a finite example. This catalog connects the worked chapters to **205 entries in twelve families**.

Entries include linear operators, nonlinear maps, functionals, transforms, algorithms, and related constructions. Classical operations, source definitions, and explicit consequences appear together. An entry count is not a count of independent discoveries, inequivalent operators, or proved theorems.

Each **OP identifier** is stable. The family pages retain the formula, scope, source links, mathematical cautions, and related entries. Source links are pinned to the compendium’s 4 November 2026 snapshots.

## Browse by family

| Family | Use it to | Entries |
|---|---|---:|
| [A. Structural operators, projectors, and transfer](A_STRUCTURAL.md) | Specify an operation, split its inputs, reconstruct its output, and compare coordinate descriptions. | 27 |
| [B. Cyclic, spectral, and arithmetic projectors](B_CYCLIC.md) | Select residues, characters, eigenspaces, or arithmetic components under their stated scalar assumptions. | 15 |
| [C. Coordinate, polynomial, and sequence transforms](C_COORDINATES.md) | Move between polynomial bases, sequence coordinates, differences, recurrences, and formal operations. | 37 |
| [D. Prime-power and digit operators](D_ARITHMETIC.md) | Follow finite prime-power data, digit carries, local masks, and lift corrections. | 11 |
| [E. Signal, wavelet, and polyphase operators](E_SIGNAL.md) | Analyze and synthesize signals, route filter phases, preserve continuation state, and recover finite features. | 24 |
| [F. Nonlinear, obstruction, and deformation operators](F_NONLINEAR.md) | Retain mixed terms, identify obstruction spaces, and state the hypotheses for a correction or reduction. | 17 |
| [G. Dynamics, inference, and elimination](G_DYNAMICS.md) | Track finite evolution, probabilistic observations, coarse dynamics, and the memory left by elimination. | 20 |
| [H. Quantum and finite spectral operators](H_QUANTUM.md) | Specify channels, measurements, charge sectors, leakage, and finite spectral constructions. | 12 |
| [I. Computational and finite model operators](I_COMPUTATIONAL.md) | Describe structured matrix actions, finite rewrites, summary maps, and computational realizations. | 20 |
| [J. Finite arithmetic and representation models](J_REPRESENTATIONS.md) | Keep the representation, scalar field, observation map, and finite recovery conditions explicit. | 5 |
| [K. Metric transport and compatibility](K_METRICS.md) | Carry the metric with the coordinates and compare adjoints, distortion, propagation, and defects. | 8 |
| [L. Finite integration and observation](L_INTEGRATION.md) | Separate exact weighted sums, moment identities, pushforwards, quadrature errors, and boundary terms. | 9 |

## Read a calculation first

- For the basic vocabulary, begin with [operator basics](../BASICS.md) and [packets and projectors](../PACKETS.md).
- To use composition laws with explicit inputs and intermediate results, follow the six [worked compositions](../COMPOSITION.md): coordinate bridges, coarse and metric defects, moment covectors, finite measures, and filter state.
- For an operation carried across coordinates, read [transfer and compression](../TRANSFER.md) and [polynomial coordinates](../POLYNOMIAL.md), then compare [OP-041](C_COORDINATES.md#op-041) · [OP-173](C_COORDINATES.md#op-173) · [OP-174](C_COORDINATES.md#op-174) · [OP-175](C_COORDINATES.md#op-175) · [OP-176](C_COORDINATES.md#op-176).
- For measurements that may lose information, use [recovery and repair](../RECOVERY.md), then [OP-179](G_DYNAMICS.md#op-179) · [OP-181](J_REPRESENTATIONS.md#op-181) · [OP-182](J_REPRESENTATIONS.md#op-182) · [OP-184](I_COMPUTATIONAL.md#op-184).
- For a change in coordinates and metric, compare [OP-023](A_STRUCTURAL.md#op-023) · [OP-185](K_METRICS.md#op-185) · [OP-191](K_METRICS.md#op-191) · [OP-192](K_METRICS.md#op-192) with [stability and numerical meaning](../STABILITY.md).
- For exact sums and integral questions, use [OP-193](L_INTEGRATION.md#op-193) · [OP-194](L_INTEGRATION.md#op-194) · [OP-197](L_INTEGRATION.md#op-197) · [OP-198](L_INTEGRATION.md#op-198).

## How to read the evidence

**Finite checks linked** means a named exact fixture illustrates an identity, a counterexample, or a rejected input associated with the entry. **Source entry** means the catalog supplies a source route but assigns no finite fixture. Neither label certifies an entire entry, implementation, or infinite-dimensional extension.

There are **136 entries with finite checks linked** and **69 source entries without an assigned fixture**. The 164 named fixtures were replayed when this catalog was imported. Several entries can share one fixture. The [check register](CHECKS.md) identifies exactly what was tested.

The [source register](SOURCES.md) preserves the source revisions and recorded inspection scope. This import adds no Lean replay and does not alter the separate verification status of the collection’s papers.

## Alphabetical entry index

| Entry | Family | Finite example |
|---|---|---|
| [OP-098 · Adaptive filter weight update](E_SIGNAL.md#op-098) | E | Source entry |
| [OP-005 · Adjoint operator](A_STRUCTURAL.md#op-005) | A | Checks linked |
| [OP-201 · Affine density transport](L_INTEGRATION.md#op-201) | L | Checks linked |
| [OP-058 · Affine pullback](C_COORDINATES.md#op-058) | C | Checks linked |
| [OP-016 · Analysis map](A_STRUCTURAL.md#op-016) | A | Checks linked |
| [OP-062 · Appell basis change](C_COORDINATES.md#op-062) | C | Source entry |
| [OP-193 · Atomic integration functional](L_INTEGRATION.md#op-193) | L | Checks linked |
| [OP-054 · Basepoint antiderivative](C_COORDINATES.md#op-054) | C | Checks linked |
| [OP-126 · Bayesian normalization operator](G_DYNAMICS.md#op-126) | G | Checks linked |
| [OP-044 · Binomial transform](C_COORDINATES.md#op-044) | C | Source entry |
| [OP-151 · Block diagonal operator](I_COMPUTATIONAL.md#op-151) | I | Source entry |
| [OP-142 · Born measurement functional](H_QUANTUM.md#op-142) | H | Checks linked |
| [OP-019 · Canonical coefficient lift](A_STRUCTURAL.md#op-019) | A | Checks linked |
| [OP-018 · Canonical coefficient projection](A_STRUCTURAL.md#op-018) | A | Checks linked |
| [OP-202 · Canonical dual frame synthesis](A_STRUCTURAL.md#op-202) | A | Checks linked |
| [OP-095 · Canonical dual window](E_SIGNAL.md#op-095) | E | Checks linked |
| [OP-162 · Carrier factorization](I_COMPUTATIONAL.md#op-162) | I | Checks linked |
| [OP-036 · Cartier decimation](B_CYCLIC.md#op-036) | B | Checks linked |
| [OP-073 · Cartier linear representation](D_ARITHMETIC.md#op-073) | D | Checks linked |
| [OP-081 · Causal FIR convolution](E_SIGNAL.md#op-081) | E | Checks linked |
| [OP-205 · Causal recursive filter](E_SIGNAL.md#op-205) | E | Checks linked |
| [OP-160 · Certified finite rewrite](I_COMPUTATIONAL.md#op-160) | I | Source entry |
| [OP-137 · Charge-sector projector](H_QUANTUM.md#op-137) | H | Source entry |
| [OP-153 · Circulant operator](I_COMPUTATIONAL.md#op-153) | I | Source entry |
| [OP-023 · Coefficient metric transport](A_STRUCTURAL.md#op-023) | A | Checks linked |
| [OP-007 · Commutator](A_STRUCTURAL.md#op-007) | A | Checks linked |
| [OP-009 · Complete algebraic packet projectors](A_STRUCTURAL.md#op-009) | A | Checks linked |
| [OP-125 · Conditional expectation](G_DYNAMICS.md#op-125) | G | Checks linked |
| [OP-189 · Conformal metric residual](K_METRICS.md#op-189) | K | Checks linked |
| [OP-123 · Continuous Markov generator](G_DYNAMICS.md#op-123) | G | Checks linked |
| [OP-117 · Contraction pullback](F_NONLINEAR.md#op-117) | F | Source entry |
| [OP-040 · Coordinate change](C_COORDINATES.md#op-040) | C | Checks linked |
| [OP-118 · Coupled feedback operator](F_NONLINEAR.md#op-118) | F | Source entry |
| [OP-172 · Covector pullback](C_COORDINATES.md#op-172) | C | Checks linked |
| [OP-034 · CRT idempotent selector](B_CYCLIC.md#op-034) | B | Checks linked |
| [OP-035 · CRT reconstruction](B_CYCLIC.md#op-035) | B | Checks linked |
| [OP-030 · Cyclic product routing](B_CYCLIC.md#op-030) | B | Source entry |
| [OP-149 · Dense matrix operator](I_COMPUTATIONAL.md#op-149) | I | Source entry |
| [OP-140 · Dephasing channel](H_QUANTUM.md#op-140) | H | Checks linked |
| [OP-184 · Descended coarse operator](I_COMPUTATIONAL.md#op-184) | I | Checks linked |
| [OP-188 · Determinant normalization](K_METRICS.md#op-188) | K | Checks linked |
| [OP-150 · Diagonal operator](I_COMPUTATIONAL.md#op-150) | I | Source entry |
| [OP-031 · Differentiation residue transport](B_CYCLIC.md#op-031) | B | Checks linked |
| [OP-072 · Digit carry transfer matrix](D_ARITHMETIC.md#op-072) | D | Checks linked |
| [OP-074 · Digit Cauchy product compilation](D_ARITHMETIC.md#op-074) | D | Source entry |
| [OP-102 · Directional derivative](F_NONLINEAR.md#op-102) | F | Checks linked |
| [OP-091 · Discrete cosine transform](E_SIGNAL.md#op-091) | E | Source entry |
| [OP-090 · Discrete Fourier transform](E_SIGNAL.md#op-090) | E | Source entry |
| [OP-049 · Divisor Möbius inversion](C_COORDINATES.md#op-049) | C | Source entry |
| [OP-135 · Duhamel perturbation operator](G_DYNAMICS.md#op-135) | G | Checks linked |
| [OP-145 · Euclidean transfer](H_QUANTUM.md#op-145) | H | Source entry |
| [OP-176 · Falling-factorial degree operator](C_COORDINATES.md#op-176) | C | Checks linked |
| [OP-175 · Falling-factorial raising operator](C_COORDINATES.md#op-175) | C | Checks linked |
| [OP-173 · Falling-factorial residue projector](C_COORDINATES.md#op-173) | C | Checks linked |
| [OP-104 · Faà di Bruno composition](F_NONLINEAR.md#op-104) | F | Checks linked |
| [OP-131 · Feshbach self-energy](G_DYNAMICS.md#op-131) | G | Source entry |
| [OP-096 · FFT overlap-add convolution](E_SIGNAL.md#op-096) | E | Source entry |
| [OP-083 · Filter cascade operator](E_SIGNAL.md#op-083) | E | Checks linked |
| [OP-169 · Finite cochain coboundary](J_REPRESENTATIONS.md#op-169) | J | Checks linked |
| [OP-180 · Finite controllability operator](G_DYNAMICS.md#op-180) | G | Checks linked |
| [OP-165 · Finite convex gauge operator](I_COMPUTATIONAL.md#op-165) | I | Checks linked |
| [OP-130 · Finite Feynman–Kac transfer](G_DYNAMICS.md#op-130) | G | Source entry |
| [OP-113 · Finite filtered correction](F_NONLINEAR.md#op-113) | F | Source entry |
| [OP-167 · Finite Frobenius action](J_REPRESENTATIONS.md#op-167) | J | Checks linked |
| [OP-039 · Finite group representation projector](B_CYCLIC.md#op-039) | B | Source entry |
| [OP-101 · Finite jump recovery](E_SIGNAL.md#op-101) | E | Source entry |
| [OP-078 · Finite linear lift correction](D_ARITHMETIC.md#op-078) | D | Source entry |
| [OP-108 · Finite Maurer–Cartan evaluation](F_NONLINEAR.md#op-108) | F | Source entry |
| [OP-195 · Finite measure pushforward](L_INTEGRATION.md#op-195) | L | Checks linked |
| [OP-168 · Finite monodromy operator](J_REPRESENTATIONS.md#op-168) | J | Source entry |
| [OP-179 · Finite observability operator](G_DYNAMICS.md#op-179) | G | Checks linked |
| [OP-161 · Finite packet-tree compiler](I_COMPUTATIONAL.md#op-161) | I | Source entry |
| [OP-114 · Finite spectral-sequence differential](F_NONLINEAR.md#op-114) | F | Source entry |
| [OP-181 · Finite trace observation](J_REPRESENTATIONS.md#op-181) | J | Checks linked |
| [OP-038 · Finite-field packet selector](B_CYCLIC.md#op-038) | B | Source entry |
| [OP-199 · Fixed-weight derivative averaging](L_INTEGRATION.md#op-199) | L | Checks linked |
| [OP-060 · Formal composition operator](C_COORDINATES.md#op-060) | C | Checks linked |
| [OP-177 · Formal compositional inversion](C_COORDINATES.md#op-177) | C | Checks linked |
| [OP-053 · Formal derivative](C_COORDINATES.md#op-053) | C | Checks linked |
| [OP-203 · Formal exponential](C_COORDINATES.md#op-203) | C | Checks linked |
| [OP-066 · Formal logarithm operator](C_COORDINATES.md#op-066) | C | Checks linked |
| [OP-065 · Formal series reciprocal](C_COORDINATES.md#op-065) | C | Checks linked |
| [OP-047 · Forward finite difference](C_COORDINATES.md#op-047) | C | Checks linked |
| [OP-037 · Frobenius endomorphism](B_CYCLIC.md#op-037) | B | Checks linked |
| [OP-052 · General normalized basis transport](C_COORDINATES.md#op-052) | C | Checks linked |
| [OP-014 · Generated operator algebra](A_STRUCTURAL.md#op-014) | A | Source entry |
| [OP-107 · Graded packet operation](F_NONLINEAR.md#op-107) | F | Source entry |
| [OP-129 · Green inverse](G_DYNAMICS.md#op-129) | G | Source entry |
| [OP-084 · Haar average and detail](E_SIGNAL.md#op-084) | E | Checks linked |
| [OP-085 · Haar synthesis](E_SIGNAL.md#op-085) | E | Checks linked |
| [OP-146 · Heat semigroup](H_QUANTUM.md#op-146) | H | Source entry |
| [OP-147 · Heat trace functional](H_QUANTUM.md#op-147) | H | Source entry |
| [OP-127 · Hidden Markov filtering operator](G_DYNAMICS.md#op-127) | G | Source entry |
| [OP-109 · Hilbert obstruction projector](F_NONLINEAR.md#op-109) | F | Source entry |
| [OP-067 · Hurwitz product](C_COORDINATES.md#op-067) | C | Checks linked |
| [OP-001 · Identity operator](A_STRUCTURAL.md#op-001) | A | Source entry |
| [OP-200 · Integration-by-parts boundary functional](L_INTEGRATION.md#op-200) | L | Checks linked |
| [OP-057 · Integration-constant defect projector](C_COORDINATES.md#op-057) | C | Checks linked |
| [OP-015 · Intertwining map](A_STRUCTURAL.md#op-015) | A | Checks linked |
| [OP-056 · Interval integration functional](C_COORDINATES.md#op-056) | C | Checks linked |
| [OP-187 · Intrinsic distortion functional](K_METRICS.md#op-187) | K | Checks linked |
| [OP-045 · Inverse binomial transform](C_COORDINATES.md#op-045) | C | Source entry |
| [OP-183 · Joint query encoding](I_COMPUTATIONAL.md#op-183) | I | Checks linked |
| [OP-166 · K-COS coefficient extraction](I_COMPUTATIONAL.md#op-166) | I | Checks linked |
| [OP-115 · Kato moving-packet transport](F_NONLINEAR.md#op-115) | F | Checks linked |
| [OP-148 · Knill–Laflamme compression](H_QUANTUM.md#op-148) | H | Checks linked |
| [OP-139 · Kraus quantum channel](H_QUANTUM.md#op-139) | H | Checks linked |
| [OP-154 · Kronecker structured operator](I_COMPUTATIONAL.md#op-154) | I | Source entry |
| [OP-157 · Krylov subspace construction](I_COMPUTATIONAL.md#op-157) | I | Source entry |
| [OP-076 · Kummer carry statistic and layer transfer](D_ARITHMETIC.md#op-076) | D | Checks linked |
| [OP-046 · Lah coordinate transform](C_COORDINATES.md#op-046) | C | Checks linked |
| [OP-087 · Lifting predict update](E_SIGNAL.md#op-087) | E | Source entry |
| [OP-141 · Lindblad generator](H_QUANTUM.md#op-141) | H | Source entry |
| [OP-070 · Local Mahler mask transform](D_ARITHMETIC.md#op-070) | D | Checks linked |
| [OP-071 · Local mask recovery](D_ARITHMETIC.md#op-071) | D | Checks linked |
| [OP-155 · Low-rank factor operator](I_COMPUTATIONAL.md#op-155) | I | Source entry |
| [OP-156 · Low-rank recompression](I_COMPUTATIONAL.md#op-156) | I | Source entry |
| [OP-111 · Lyapunov–Schmidt reduction](F_NONLINEAR.md#op-111) | F | Source entry |
| [OP-124 · Markov lumping operator](G_DYNAMICS.md#op-124) | G | Checks linked |
| [OP-122 · Markov transition operator](G_DYNAMICS.md#op-122) | G | Checks linked |
| [OP-119 · Matrix semigroup](G_DYNAMICS.md#op-119) | G | Checks linked |
| [OP-133 · Memory-kernel operator](G_DYNAMICS.md#op-133) | G | Checks linked |
| [OP-185 · Metric adjoint](K_METRICS.md#op-185) | K | Checks linked |
| [OP-190 · Metric holonomy residual](K_METRICS.md#op-190) | K | Checks linked |
| [OP-191 · Metric propagation along an edge](K_METRICS.md#op-191) | K | Checks linked |
| [OP-186 · Metric-whitened representation](K_METRICS.md#op-186) | K | Checks linked |
| [OP-198 · Moment discrepancy functional](L_INTEGRATION.md#op-198) | L | Checks linked |
| [OP-194 · Moment integration covector](L_INTEGRATION.md#op-194) | L | Checks linked |
| [OP-041 · Monomial to falling-factorial transport](C_COORDINATES.md#op-041) | C | Checks linked |
| [OP-143 · Moving packet leakage](H_QUANTUM.md#op-143) | H | Source entry |
| [OP-028 · Multi-index residue projector](B_CYCLIC.md#op-028) | B | Checks linked |
| [OP-086 · Multilevel Haar packet tree](E_SIGNAL.md#op-086) | E | Source entry |
| [OP-059 · Multiplication by coordinate](C_COORDINATES.md#op-059) | C | Checks linked |
| [OP-048 · Newton sample-difference transform](C_COORDINATES.md#op-048) | C | Checks linked |
| [OP-116 · Nonlinear residue product](F_NONLINEAR.md#op-116) | F | Checks linked |
| [OP-112 · Nonlinear Schur elimination](F_NONLINEAR.md#op-112) | F | Source entry |
| [OP-204 · Normalized coefficient multiplication](C_COORDINATES.md#op-204) | C | Checks linked |
| [OP-027 · One-dimensional character projector](B_CYCLIC.md#op-027) | B | Source entry |
| [OP-003 · Operator composition](A_STRUCTURAL.md#op-003) | A | Checks linked |
| [OP-013 · Operator polynomial](A_STRUCTURAL.md#op-013) | A | Checks linked |
| [OP-004 · Operator sum and scaling](A_STRUCTURAL.md#op-004) | A | Checks linked |
| [OP-051 · Ordinary to exponential coefficient normalization](C_COORDINATES.md#op-051) | C | Checks linked |
| [OP-010 · Packet block](A_STRUCTURAL.md#op-010) | A | Checks linked |
| [OP-103 · Packet jet](F_NONLINEAR.md#op-103) | F | Source entry |
| [OP-088 · Packet retention projector](E_SIGNAL.md#op-088) | E | Checks linked |
| [OP-120 · Packet semigroup transfer](G_DYNAMICS.md#op-120) | G | Source entry |
| [OP-158 · Packet support propagation](I_COMPUTATIONAL.md#op-158) | I | Checks linked |
| [OP-196 · Partial integration on a product](L_INTEGRATION.md#op-196) | L | Checks linked |
| [OP-079 · Phase analysis operator](E_SIGNAL.md#op-079) | E | Checks linked |
| [OP-080 · Phase synthesis operator](E_SIGNAL.md#op-080) | E | Checks linked |
| [OP-136 · Phase-type survival operator](G_DYNAMICS.md#op-136) | G | Source entry |
| [OP-021 · Physical frame component](A_STRUCTURAL.md#op-021) | A | Checks linked |
| [OP-055 · Point evaluation](C_COORDINATES.md#op-055) | C | Checks linked |
| [OP-106 · Polynomial fixed-point Picard operator](F_NONLINEAR.md#op-106) | F | Checks linked |
| [OP-029 · Polynomial spectral projector](B_CYCLIC.md#op-029) | B | Checks linked |
| [OP-082 · Polyphase convolution matrix](E_SIGNAL.md#op-082) | E | Checks linked |
| [OP-020 · Presentation bridge](A_STRUCTURAL.md#op-020) | A | Checks linked |
| [OP-075 · Prime-free factorial unit extraction](D_ARITHMETIC.md#op-075) | D | Source entry |
| [OP-077 · Prime-power kernel compiler](D_ARITHMETIC.md#op-077) | D | Checks linked |
| [OP-068 · Prime-power reduction](D_ARITHMETIC.md#op-068) | D | Source entry |
| [OP-192 · Quadratic metric-defect composition](K_METRICS.md#op-192) | K | Checks linked |
| [OP-138 · Quantum circuit composition](H_QUANTUM.md#op-138) | H | Source entry |
| [OP-144 · Quantum Feshbach operator](H_QUANTUM.md#op-144) | H | Checks linked |
| [OP-134 · Rational memory transfer](G_DYNAMICS.md#op-134) | G | Checks linked |
| [OP-097 · Rational polyphase resampling](E_SIGNAL.md#op-097) | E | Source entry |
| [OP-063 · Recurrence companion transfer](C_COORDINATES.md#op-063) | C | Checks linked |
| [OP-064 · Recurrence defect extraction](C_COORDINATES.md#op-064) | C | Checks linked |
| [OP-178 · Recurrence reconstruction](C_COORDINATES.md#op-178) | C | Checks linked |
| [OP-025 · Residue coefficient projector](B_CYCLIC.md#op-025) | B | Checks linked |
| [OP-033 · Residue refinement](B_CYCLIC.md#op-033) | B | Source entry |
| [OP-110 · Right-inverse correction operator](F_NONLINEAR.md#op-110) | F | Source entry |
| [OP-105 · Rooted-tree evaluation](F_NONLINEAR.md#op-105) | F | Checks linked |
| [OP-026 · Roots-of-unity projector](B_CYCLIC.md#op-026) | B | Checks linked |
| [OP-022 · Sandwiched coefficient block](A_STRUCTURAL.md#op-022) | A | Checks linked |
| [OP-132 · Schur complement](G_DYNAMICS.md#op-132) | G | Checks linked |
| [OP-121 · Semigroup refinement defect](G_DYNAMICS.md#op-121) | G | Checks linked |
| [OP-061 · Shift polynomial](C_COORDINATES.md#op-061) | C | Source entry |
| [OP-093 · Short-time Fourier analysis](E_SIGNAL.md#op-093) | E | Source entry |
| [OP-094 · Short-time Fourier synthesis](E_SIGNAL.md#op-094) | E | Checks linked |
| [OP-089 · Signal residual operator](E_SIGNAL.md#op-089) | E | Source entry |
| [OP-163 · Signed mass packet completion](I_COMPUTATIONAL.md#op-163) | I | Checks linked |
| [OP-197 · Signed quadrature functional](L_INTEGRATION.md#op-197) | L | Checks linked |
| [OP-043 · Signed Stirling first-kind inverse](C_COORDINATES.md#op-043) | C | Checks linked |
| [OP-008 · Similarity transport](A_STRUCTURAL.md#op-008) | A | Checks linked |
| [OP-128 · Spectral fractional power](G_DYNAMICS.md#op-128) | G | Source entry |
| [OP-042 · Stirling second-kind transform](C_COORDINATES.md#op-042) | C | Checks linked |
| [OP-050 · Subset zeta transform and Mobius inverse](C_COORDINATES.md#op-050) | C | Checks linked |
| [OP-017 · Synthesis map](A_STRUCTURAL.md#op-017) | A | Checks linked |
| [OP-170 · Synthesis-kernel projector](A_STRUCTURAL.md#op-170) | A | Checks linked |
| [OP-006 · Tensor or Kronecker operator](A_STRUCTURAL.md#op-006) | A | Source entry |
| [OP-152 · Toeplitz operator](I_COMPUTATIONAL.md#op-152) | I | Source entry |
| [OP-182 · Trace-table reconstruction](J_REPRESENTATIONS.md#op-182) | J | Checks linked |
| [OP-012 · Transfer block composition](A_STRUCTURAL.md#op-012) | A | Checks linked |
| [OP-011 · Transfer block reconstruction](A_STRUCTURAL.md#op-011) | A | Checks linked |
| [OP-032 · Translation packet transfer](B_CYCLIC.md#op-032) | B | Source entry |
| [OP-024 · Transported bilinear form](A_STRUCTURAL.md#op-024) | A | Checks linked |
| [OP-174 · Transported polynomial product](C_COORDINATES.md#op-174) | C | Checks linked |
| [OP-164 · Tropical residual reconstruction](I_COMPUTATIONAL.md#op-164) | I | Checks linked |
| [OP-069 · Truncated local p-adic coefficient operator](D_ARITHMETIC.md#op-069) | D | Source entry |
| [OP-100 · Truncated-power packet realization](E_SIGNAL.md#op-100) | E | Source entry |
| [OP-171 · Two-endpoint coordinate transport](A_STRUCTURAL.md#op-171) | A | Checks linked |
| [OP-159 · Typed expression replay](I_COMPUTATIONAL.md#op-159) | I | Checks linked |
| [OP-092 · Walsh–Hadamard transform](E_SIGNAL.md#op-092) | E | Source entry |
| [OP-099 · Wavelet coefficient shrinkage](E_SIGNAL.md#op-099) | E | Checks linked |
| [OP-002 · Zero operator](A_STRUCTURAL.md#op-002) | A | Source entry |
