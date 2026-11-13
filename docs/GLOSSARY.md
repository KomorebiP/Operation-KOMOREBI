# Glossary

This guide explains 332 terms used across the collection, its operator guide and worked examples. Use the [first reading route](#a-first-reading), [follow a subject route](#subject-reading-routes), [compare nearby ideas](#compare-nearby-ideas), [browse by subject](#browse-by-subject), or open the [alphabetical index](#alphabetical-index).

[Find a glossary term on the reading website](https://KomorebiP.github.io/Operation-KOMOREBI/collection/GLOSSARY.html#glossary-lookup): search names, abbreviations, definitions and short examples, or choose a subject. Open the glossary beside a paper with **Read side by side**.

A word can have a more specific meaning in another paper. The paper’s definitions and hypotheses take precedence. Examples and source links provide context without changing any recorded evidence status.

[Operator guide](OPERATOR_AUDIT.md) · [Look up notation across the collection](NOTATION_INDEX.md) · [Work through the calculations by hand](HAND_WORKED_EXAMPLES.md) · [Papers, proofs, Lean, and code by topic](LEARNING_MAP.md) · [First software runs](FIRST_RUN.md)

## A first reading

Follow these terms for a short route through the main ideas. Use their examples and source links to go deeper.

1. [Realization](#realization) · [Seed](#seed) · [Seed rank](#seed-rank) — Identify the system, the allowed action and the data that generate it.
2. [Projector](#projector) · [Packet](#packet) — See how an object splits into selected components.
3. [Coordinates](#coordinates) · [Analysis and synthesis](#analysis-synthesis) — Follow a representation from the object to coordinates and back.
4. [Transfer block](#transfer-block) · [Residual](#residual) — Track an operation between components and check a reconstruction.
5. [Refinement](#refinement) · [Coarsening](#coarsening) · [Obstruction](#obstruction) — Check which distinctions survive a change of description and which lost information prevents a requested recovery.
6. [Hypothesis](#hypothesis) · [Exact](#exact) · [Proof](#proof) — Identify the assumptions, arithmetic setting and supporting argument for the claim being read.

## Subject reading routes

Choose a question, follow its terms in order, then work through the linked reading. Quick examples are small illustrations; the linked works state their full assumptions and evidence.

<a id="route-linear"></a>

### Read the linear algebra

What spaces do the maps connect, and what information can they preserve?

[Domain and codomain](#domain-codomain) → [Linear map](#linear-map) → [Basis](#basis) → [Kernel](#kernel) → [Image](#image) → [Rank–nullity identity](#rank-nullity)

[Continue with the operator basics](operators/BASICS.md).

<a id="route-packets"></a>

### Generate and select packets

How can one seed generate many directions, and how do selectors split them?

[Operator orbit](#operator-orbit) → [Cyclic vector](#cyclic) → [Seed rank](#seed-rank) → [Projector](#projector) → [Complete packet family](#complete-packet-family) → [Transfer block](#transfer-block)

[Continue with the complete packet calculation](demonstrations/PACKETS.md).

<a id="route-recovery"></a>

### Decide what a summary can recover

Which questions have the same answer on every input sharing a summary?

[Fiber](#fiber) → [Sufficient summary for a requested output](#sufficient-summary) → [Factorization through a map](#factorization) → [Collision witness](#collision-witness) → [Exact recovery from a summary](#exact-recovery) → [Repair direction](#repair-direction)

[Continue with recovery and its obstruction](demonstrations/RECOVERY.md).

<a id="route-coordinates"></a>

### Use redundant coordinates

When does analysis followed by synthesis recover the object, and which coefficient lists are valid?

[Finite frame](#finite-frame) → [Analysis and synthesis](#analysis-synthesis) → [Left inverse](#left-inverse) → [Canonical dual synthesis](#canonical-dual) → [Coefficient projection](#coefficient-projection) → [Reconstruction component](#reconstruction-component)

[Continue with redundant-coordinate reconstruction](examples/06_REDUNDANT_COORDINATES.md).

<a id="route-polynomials"></a>

### Move between polynomial bases

What changes when an ordinary power is represented in falling-factorial coordinates?

[Falling factorial](#falling-factorial) → [Stirling transform](#stirling-transform) → [Forward difference](#forward-difference) → [Falling-degree operator](#degree-operator) → [Roots-of-unity filter](#roots-of-unity-filter) → [Transported product](#transported-product)

[Continue with roots of unity and falling factorials](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md).

<a id="route-signals"></a>

### Follow a signal through a filter

Which steps rearrange samples, which filter them, and where can information disappear?

[Polyphase decomposition](#polyphase) → [Downsampling](#downsampling) → [Haar pair](#haar-pair) → [Analysis filter bank](#filter-bank) → [Polyphase carry](#polyphase-carry) → [Signal boundary convention](#boundary-condition) → [Parseval identity in chosen coordinates](#parseval-identity)

[Continue with the multilevel wavelet and polyphase study](demonstrations/WAVELET_POLYPHASE.md).

<a id="route-quantum"></a>

### Track quantum phase and measurement

Which probabilities detect relative phase, and what is lost when outcomes are discarded?

[Qubit](#qubit) → [Relative phase](#relative-phase) → [Density matrix](#density-matrix) → [Quantum measurement effect](#quantum-effect) → [Selective projective measurement](#selective-measurement) → [Dephasing](#dephasing) → [Quantum state tomography](#quantum-tomography)

[Continue with the exact phase and measurement study](demonstrations/QUANTUM_PHASE_MEASUREMENT.md).

<a id="route-smith"></a>

### Read the Smith chart

How do a physical load, a reflection point and a realizable circuit relate?

[Impedance](#impedance) → [Normalized impedance](#normalized-impedance) → [Reflection coefficient](#reflection-coefficient) → [Lossless transmission line](#lossless-line) → [Cyclic reachability](#cyclic-reachability) → [Circuit realization](#circuit-realization)

[Continue with the Smith-chart reading companion](demonstrations/SMITH_CHART.md).

<a id="route-singular"></a>

### Test a singular interpolation boundary

Why can singular data still force an unmeasured value?

[Scalar Schur function](#schur-function) → [Interpolation](#interpolation) → [Pick matrix](#pick-matrix) → [Positive semidefinite matrix](#positive-semidefinite) → [Moore–Penrose inverse](#pseudoinverse) → [Singular block range condition](#singular-range-condition)

[Continue with the singular Pick-data calculation](demonstrations/SMITH_SINGULAR_COMPLETION.md).

<a id="route-memory"></a>

### Find the memory a summary hides

Does the visible state determine its next value, or is history needed?

[Finite linear state-space realization](#state-space-realization) → [Visible state](#visible-state) → [Hidden state](#hidden-state) → [Discrete memory maps](#memory-kernel) → [State sufficient for a deterministic update](#markov-state) → [State augmentation](#state-augmentation)

[Continue with the hidden-memory example](examples/22_HIDDEN_MEMORY.md).

<a id="route-evidence"></a>

### Read a claim with its evidence

What was proved, what was checked, and what does a failed search leave unresolved?

[Hypothesis](#hypothesis) → [Formal statement](#formal-statement) → [Lean correspondence](#lean-correspondence) → [Derivation trace](#derivation-trace) → [Finite check](#finite-check) → [Inconclusive search](#search-inconclusive)

[Continue with the shared-premise certificate example](examples/21_PROOF_CERTIFICATES.md).

<a id="route-error"></a>

### Interpret a numerical answer

Is the reported quantity a residual, an error bound or a guaranteed enclosure?

[Residual](#residual) → [Absolute error](#absolute-error) → [Relative error](#relative-error) → [Backward error](#backward-error) → [Condition number of a coordinate map](#condition-number) → [Directed enclosure](#directed-enclosure)

[Continue with stability and numerical meaning](operators/STABILITY.md).

## Compare nearby ideas

These distinctions use the glossary’s stated settings. Follow both entries for their definitions and examples.

| Terms | Distinction to keep in view |
|---|---|
| [Seed rank](#seed-rank) / [Dimension](#dimension) | Seed rank counts generators under the declared operator action. Vector-space dimension counts basis vectors under scalar linear combinations. In the two-dimensional seed example, seed rank is one. |
| [Projector](#projector) / [Orthogonal projector](#orthogonal-projector) | A projector satisfies P² = P. Orthogonality additionally depends on an inner product; algebraic packet reconstruction also permits oblique projectors. |
| [Left inverse](#left-inverse) / [Inverse](#inverse) | SA = I recovers original objects after analysis. A two-sided inverse also satisfies AS = I on the coordinate space. Redundant coordinates can have the first identity without the second. |
| [Kernel](#kernel) / [Fiber](#fiber) | For a linear map, the kernel is the fiber over zero. Every nonempty fiber is a translate of that kernel. Fibers of a general nonlinear map need not have this form. |
| [Residual](#residual) / [Obstruction](#obstruction) | A residual records a discrepancy for the stated calculation. An obstruction rules out a proposed construction under specified assumptions. A nonzero residual alone need not rule out a different construction. |
| [Precision](#precision) / [Precision matrix](#precision-matrix) | Arithmetic precision counts significant digits in a representation. A precision matrix is an inverse covariance. The shared word refers to different objects. |
| [Finite check](#finite-check) / [Proof](#proof) | Exhaustive checking can prove a statement about its declared finite domain. Sampled cases in a larger domain require an additional argument to establish a universal statement. |
| [Coordinate change](#coordinate-change) / [Operator conjugation](#conjugation) | A coordinate change sends vectors from x to y = Cx. Under that convention, the same operator T has matrix CTC⁻¹ in the y coordinates. Both the vector and operator descriptions must follow the declared direction. |
| [Intertwiner](#intertwiner) / [Operator conjugation](#conjugation) | An intertwiner C satisfies CT = UC and can be noninvertible. When C is invertible, this identity gives the conjugation U = CTC⁻¹. |
| [Module support](#module-support) / [Multiplicity in the module example](#multiplicity) | Support records where a module remains nonzero after localization. In Q[t]/(tᵏ), every positive k gives the same support {(t)}, while k records the different module lengths and rational dimensions. |
| [Inclusion-minimal certificate](#inclusion-minimal) / [Least certificate](#least-certificate) | An inclusion-minimal certificate cannot be made smaller while remaining valid. A least certificate must be contained in every valid certificate for the same request. Incomparable minimal certificates can exist without a least one. |
| [Least certificate](#least-certificate) / [Minimum-cost certificate](#minimum-cost-certificate) | Least compares certificates by inclusion. Minimum cost compares their declared numerical costs. The shared-premise example has two minimum-cost certificates and no least certificate. |
| [Free linear repair](#free-repair) / [Finite repair menu](#repair-menu) | Free linear repair allows added directions chosen freely over the stated field. A finite repair menu restricts the choices to supplied candidates, with their costs and selection rules. Their minima answer different problems. |
| [Reconstruction component](#reconstruction-component) / [Projector](#projector) | Reconstruction components SEᵢA sum to the identity when the coefficient selectors partition all coordinates and SA = I. In a redundant system, individual components need not satisfy Cᵢ² = Cᵢ. A projector must satisfy that extra identity. |
| [Classical frame operator](#classical-frame-operator) / [Coefficient projection](#coefficient-projection) | A*A acts on the original vector space and measures the frame analysis. AS acts on coefficient space and projects onto valid analyzed coordinates. The reconstruction identity is SA = I, a third map with a different role. |
| [Spectral radius](#spectral-radius) / [Induced operator norm](#operator-norm) | Spectral radius uses eigenvalue magnitudes. An induced norm measures the largest one-step gain over all directions. The nilpotent matrix [[0,M],[0,0]] has spectral radius zero and Euclidean operator norm M. |
| [Strong operator convergence](#strong-convergence) / [Operator norm convergence](#operator-norm-convergence) | Strong convergence follows each fixed input. Operator norm convergence controls all unit inputs uniformly. The first-m-coordinate projections on ℓ² converge strongly to I while their operator norm distance from I stays one. |
| [Ordinary generating function](#ordinary-generating-function) / [Exponential generating function](#exponential-generating-function) | An ordinary generating function stores aₙ against zⁿ. An exponential generating function stores aₙ against tⁿ/n!. Multiplication therefore uses ordinary coefficient convolution in the first convention and binomial convolution in the second. |
| [Formal reciprocal](#formal-reciprocal) / [Compositional inverse of a formal series](#compositional-inverse) | A reciprocal solves A(t)B(t) = 1 and needs a nonzero constant coefficient over a field. A substitution inverse solves A(B(t)) = t and needs zero constant coefficient with nonzero linear coefficient. |
| [Bell numbers](#bell-numbers) / [Fubini numbers](#fubini-numbers) | Bell numbers count partitions into unordered blocks. Fubini numbers count the same partitions with their blocks linearly ordered. The factor k! records the possible orders of k blocks. |
| [Residue coefficient selector](#coefficient-selector) / [Roots-of-unity filter](#roots-of-unity-filter) | A residue coefficient selector retains named basis positions and is defined over any commutative ring. Roots-of-unity averaging realizes that selector over a field with the required primitive root and invertible modulus. |
| [Analytic error budget](#analytic-error-budget) / [Directed enclosure](#directed-enclosure) | An analytic budget bounds the stated approximation steps. A directed numerical enclosure must also control finite arithmetic and outward rounding. A small analytic bound alone does not certify the computed endpoints. |
| [Orthogonal matrix](#orthogonal-matrix) / [Linear isometry](#isometry) | A square orthogonal or unitary matrix is a surjective isometry. A rectangular isometric embedding preserves lengths but can leave part of its codomain unattained. |
| [Eigenvalue](#eigenvalue) / [Singular value](#singular-value) | Eigenvalues describe scalar action on invariant directions of a square operator. Singular values describe nonnegative gains through A*A and also apply to rectangular maps. A nonzero nilpotent matrix can have only zero eigenvalues and a positive singular value. |
| [Induced operator norm](#operator-norm) / [Hilbert–Schmidt norm](#hilbert-schmidt-norm) | The induced Euclidean norm is the largest singular value. The Hilbert–Schmidt norm is the square root of the sum of their squares. For diag(3,4), these norms are 4 and 5. |
| [Bilinear form](#bilinear-form) / [Inner product](#inner-product) | A real inner product is a symmetric positive definite bilinear form. Bilinearity alone allows indefinite or degenerate forms. Complex inner products instead use conjugate linearity in one argument. |
| [Absolute error](#absolute-error) / [Relative error](#relative-error) | Absolute error uses the output’s units. Relative error divides by a specified nonzero reference size. Near a zero target, the same absolute error can give a large or undefined relative error. |
| [Forward error](#forward-error) / [Backward error](#backward-error) | Forward error asks how far the computed answer is from the exact answer. Backward error asks how much permitted input data must change to make the computed answer exact. Conditioning links the two. |
| [Formal power series](#formal-power-series) / [Radius of convergence](#radius-of-convergence) | Formal series support coefficientwise algebra without numerical evaluation. A radius of convergence belongs to an analytic evaluation problem. A formal identity alone does not supply a truncation-error bound at a chosen argument. |
| [Forward difference](#forward-difference) / [Backward difference](#backward-difference) | The forward difference is f(x+1)−f(x); the backward difference is f(x)−f(x−1). On x² they give 2x+1 and 2x−1. Direction and step belong to the definition. |
| [Falling factorial](#falling-factorial) / [Rising factorial](#rising-factorial) | The falling product decreases successive factors by one, while the rising product increases them. The symbol (a)ₙ is convention-dependent, so compare the displayed product before using a formula. |
| [Global phase](#global-phase) / [Relative phase](#relative-phase) | A common phase on the whole state cancels in its density matrix. A phase difference between components remains in off-diagonal entries and can change interference measurements. |
| [Quantum measurement effect](#quantum-effect) / [Projector](#projector) | A measurement effect satisfies 0 ≤ E ≤ I. A projective effect also satisfies E² = E. The valid effect I/2 is not a projector. |
| [Selective projective measurement](#selective-measurement) / [Dephasing](#dephasing) | Selective measurement retains the outcome and conditions the state on it. Coordinate dephasing discards that outcome and sums the branches, deleting the cross-coordinate coherence. |
| [Lossless transmission line](#lossless-line) / [Cyclic reachability](#cyclic-reachability) | The line model uses a continuous physical length at a stated wavelength. A fixed order-N cyclic action permits only N phase rotations. Both preserve reflection magnitude, but their allowed phases differ. |
| [Pick matrix](#pick-matrix) / [Circuit realization](#circuit-realization) | Positive semidefinite Pick data decide feasibility in the stated scalar Schur interpolation problem. They do not alone decide realizability with a restricted transformer-free topology or a specified reactive-element count. |
| [Necessary condition](#necessary-condition) / [Sufficient condition](#sufficient-condition) | A necessary condition must hold for every solution. A sufficient condition guarantees a solution or property. A condition is both only after both implications are established. |
| [Counterexample](#counterexample) / [Inconclusive search](#search-inconclusive) | An admissible counterexample disproves its stated universal claim. An inconclusive search has established neither a witness nor a proof of nonexistence. Rejecting one proposed witness can still leave many valid ones. |

## Browse by subject

- [Linear foundations](#linear-foundations) — 39 terms
- [Operators, seeds, and packets](#operators-and-packets) — 34 terms
- [Coordinates and transfer](#coordinates-and-transfer) — 33 terms
- [Refinement and constraints](#refinement-and-constraints) — 27 terms
- [Arithmetic and error](#arithmetic-and-error) — 24 terms
- [Claims and evidence](#claims-and-evidence) — 23 terms
- [Series and cyclic functions](#series-and-functions) — 40 terms
- [Signals and spectral evaluation](#signal-and-spectral-evaluation) — 19 terms
- [Smith chart and circuit synthesis](#smith-chart-and-synthesis) — 19 terms
- [Finite quantum systems](#finite-quantum) — 23 terms
- [Arithmetic and modules](#arithmetic-and-modules) — 26 terms
- [Dynamics, memory, and calibration](#dynamics-and-calibration) — 16 terms
- [Inference and probability](#inference-and-probability) — 9 terms

<a id="linear-foundations"></a>

## Linear foundations

The objects and notation used in the finite examples.

[Scalar](#scalar) · [Field](#field) · [Vector](#vector) · [Vector space](#vector-space) · [Linear map](#linear-map) · [Matrix](#matrix) · [Identity operator](#identity) · [Span](#span) · [Linear independence](#linear-independence) · [Basis](#basis) · [Dimension](#dimension) · [Kernel](#kernel) · [Image](#image) · [Rank](#rank) · [Inner product](#inner-product) · [Norm](#norm) · [Subspace](#subspace) · [Nullity](#nullity) · [Rank–nullity identity](#rank-nullity) · [Injective map](#injective) · [Surjective map](#surjective) · [Linear isomorphism](#isomorphism) · [Direct sum](#direct-sum) · [Quotient space](#quotient-space) · [Determinant](#determinant) · [Domain and codomain](#domain-codomain) · [Affine map](#affine-map) · [Row space](#row-space) · [Covector](#covector) · [Positive definite matrix](#positive-definite) · [Seminorm](#seminorm) · [Dual space](#dual-space) · [Orthogonal complement](#orthogonal-complement) · [Orthonormal basis](#orthonormal-basis) · [Singular value](#singular-value) · [Singular value decomposition](#singular-value-decomposition) · [Bilinear form](#bilinear-form) · [Quadratic form](#quadratic-form) · [Triangular matrix](#triangular-matrix)

<a id="scalar"></a>

### Scalar

A number from the declared coefficient field, used to multiply vectors. The hand-worked matrix examples use real scalars and exact rational entries.

**Quick example:** In 3(2,−1) = (6,−3), the number 3 is the scalar.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Field](#field) · [Vector](#vector)

<a id="field"></a>

### Field

A number system with addition, subtraction, multiplication, and division by every nonzero element. The rational, real, and complex numbers are examples. A result over one field does not automatically hold over another.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Scalar](#scalar)

<a id="vector"></a>

### Vector

An element of a vector space. In the finite examples it is a column of numbers. Its coordinates depend on a chosen representation.

**Quick example:** The pair (2,3) and the polynomial 2+3x are vectors in different declared vector spaces.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Vector space](#vector-space) · [Coordinates](#coordinates)

<a id="vector-space"></a>

### Vector space

A collection of vectors closed under addition and scalar multiplication, with the usual distributive and associative laws. The space of pairs of real numbers is denoted R².

**Quick example:** Pairs (x,y) with x+y = 0 form a vector space; pairs with x+y = 1 do not contain zero.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Field](#field) · [Span](#span) · [Basis](#basis)

<a id="linear-map"></a>

### Linear map

A map T satisfying T(au + bv) = aT(u) + bT(v) for all vectors u, v and allowed scalars a, b. A linear map preserves linear combinations.

**Also called:** Linear transformation.

**Quick example:** T(x,y) = (x+2y,3x) is linear. Adding a fixed nonzero offset would make it affine.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Matrix](#matrix) · [Kernel](#kernel) · [Image](#image)

<a id="matrix"></a>

### Matrix

A rectangular array representing a linear map after bases have been chosen. An m by n matrix takes n coordinates to m coordinates. Each output coordinate is a row multiplied by the input column.

**Quick example:** The matrix [[1,2],[3,4]] sends (2,3) to (8,18).

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Linear map](#linear-map) · [Basis](#basis) · [Composition](#composition)

<a id="identity"></a>

### Identity operator

The map I that leaves every input unchanged, so Ix = x. The subscript in I₂ or I₃ specifies the dimension when needed.

**Also called:** Identity map.

**Quick example:** I₂(2,3) = (2,3). The identity is different from a matrix with every entry equal to one.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Inverse](#inverse) · [Complete packet family](#complete-packet-family)

<a id="span"></a>

### Span

All finite linear combinations of a specified set of vectors. The span of the empty set consists only of the zero vector. With an operator action, one may first apply allowed operators and then take the span.

**Also called:** Linear span.

**Quick example:** The span of (1,1) is the line {(a,a) : a is a scalar}.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Seed](#seed) · [Basis](#basis) · [Linear independence](#linear-independence)

<a id="linear-independence"></a>

### Linear independence

A family is linearly independent when the only linear combination giving zero has every coefficient zero. No member of a finite independent family can be formed from the others.

**Quick example:** (1,0) and (0,1) are independent, while (1,0) and (2,0) are dependent.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Span](#span) · [Basis](#basis)

<a id="basis"></a>

### Basis

A linearly independent spanning family. Every vector has a unique finite linear combination in that basis. Redundant measurements can describe a vector without forming a basis.

**Quick example:** In the basis {(1,1),(1,−1)}, the vector (4,2) has coefficients (3,1).

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Span](#span) · [Linear independence](#linear-independence) · [Redundant coordinates](#redundancy) · [Finite frame](#finite-frame) · [Falling factorial](#falling-factorial) · [Orthonormal basis](#orthonormal-basis) · [Monic polynomial](#monic-polynomial)

<a id="dimension"></a>

### Dimension

The number of vectors in a basis of a finite-dimensional vector space. In these examples, R² has dimension two even when three redundant measurements are stored.

**Quick example:** The subspace spanned by (1,0,0) and (0,1,0) has dimension two inside R³.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Basis](#basis) · [Rank](#rank) · [Seed rank](#seed-rank)

<a id="kernel"></a>

### Kernel

For a linear map T, the vectors sent to zero: ker T = {x : Tx = 0}. A nonzero kernel describes directions that this map cannot distinguish from zero.

**Also called:** Nullspace, Null space.

**Quick example:** For R(x,y) = x+y, the kernel is span{(1,−1)}.

**In the worked example:** For the sum map R(a,b) = a+b over R, the vector (1,−1)ᵀ lies in the kernel: R(1,−1) = 0. Adding this vector does not change the observed sum.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Image](#image) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Sufficient summary for a requested output](#sufficient-summary) · [Orthogonal complement](#orthogonal-complement)

<a id="image"></a>

### Image

The outputs actually attained by a map. For a linear map T, im T = {Tx : x is an allowed input} is a subspace of the target. The declared target can be larger than the image.

**Also called:** Range, Range of a linear map.

**Quick example:** The map x ↦ (x,0) has image the horizontal axis, even if its codomain is all of R².

**In the worked example:** For A(a,b) = (a,b,a+b), the image consists of triples whose third coordinate is the sum of the first two. The coordinate vector (0,0,1)ᵀ lies outside it.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Kernel](#kernel) · [Rank](#rank) · [Left inverse](#left-inverse)

<a id="rank"></a>

### Rank

For a finite linear map, the dimension of its image. A matrix has full column rank when its columns are linearly independent, so it has no nonzero input in its kernel.

**Quick example:** The matrix [[1,1],[2,2]] has rank one because its second row and column add no independent direction.

**Keep in mind:** Matrix rank and seed rank answer different questions.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Dimension](#dimension) · [Image](#image) · [Seed rank](#seed-rank)

<a id="inner-product"></a>

### Inner product

For real vector spaces, a symmetric bilinear pairing with ⟨v,v⟩ > 0 for every nonzero v. It defines lengths and angles. Positive weights give the pairing sum_i w_i u_i v_i. Complex inner products use conjugate symmetry and conjugate linearity in one argument.

**Quick example:** For u = (1,2), the weighted inner product with weights (1,3) gives ⟨u,u⟩ = 1+12 = 13.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#averages) · [Norm](#norm) · [Orthogonal projector](#orthogonal-projector)

<a id="norm"></a>

### Norm

A nonnegative measure of size that is zero only at the zero vector, scales by the absolute value of a scalar and satisfies the triangle inequality. The Euclidean norm is the square root of the sum of squared coordinates.

**Quick example:** The Euclidean norm of (3,4) is 5, while its 1-norm is 7.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Inner product](#inner-product) · [Residual](#residual) · [Tolerance](#tolerance) · [Induced operator norm](#operator-norm) · [Seminorm](#seminorm) · [Hilbert–Schmidt norm](#hilbert-schmidt-norm) · [Linear isometry](#isometry)

<a id="subspace"></a>

### Subspace

A subset of a vector space that contains zero and is closed under addition and scalar multiplication. Kernels and images of linear maps are subspaces.

**Quick example:** The plane z = 0 in R³ is a subspace; the parallel plane z = 1 is not.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Kernel](#kernel) · [Image](#image)

<a id="nullity"></a>

### Nullity

The dimension of the kernel of a finite-dimensional linear map. It counts independent input directions erased by the map.

**Quick example:** The map R(x,y,z) = x+y has kernel {(a,−a,b)}, so its nullity is two.

**In the worked example:** For T(x₁,x₂,x₃) = (x₁+x₂,x₂+x₃), the kernel is span{(−1,1,−1)ᵀ}. It has one free direction, so nullity T = 1.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Kernel](#kernel) · [Dimension](#dimension)

<a id="rank-nullity"></a>

### Rank–nullity identity

For a linear map with finite-dimensional domain V, dim V = rank T + nullity T. The rank concerns the image, not the dimension of the entire declared target.

**Also called:** Rank-nullity theorem.

**Quick example:** For R(x,y,z) = x+y, domain dimension 3 equals rank 1 plus nullity 2.

**In the worked example:** The map T(x₁,x₂,x₃) = (x₁+x₂,x₂+x₃) has rank two and a one-dimensional kernel. Its three-dimensional domain therefore satisfies 3 = 2 + 1 = rank T + nullity T.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Rank](#rank) · [Nullity](#nullity)

<a id="injective"></a>

### Injective map

A map that sends distinct inputs to distinct outputs. A linear map is injective exactly when its kernel contains only zero.

**Also called:** Injection, One-to-one map.

**Quick example:** The map x ↦ (x,2x) is injective, although it does not reach every pair.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Kernel](#kernel) · [Left inverse](#left-inverse)

<a id="surjective"></a>

### Surjective map

A map whose image is its entire declared target. Surjectivity depends on which target is specified.

**Also called:** Surjection, Onto map.

**Quick example:** The map (x,y) ↦ x reaches every real number, although many pairs have the same output.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Image](#image) · [Rank](#rank)

<a id="isomorphism"></a>

### Linear isomorphism

A bijective linear map between vector spaces over the same field. Its inverse is linear. It preserves the vector-space structure, although lengths need not be preserved.

**Also called:** Invertible linear map.

[Hand-worked example](examples/03_COORDINATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Inverse](#inverse) · [Coordinate change](#coordinate-change)

<a id="direct-sum"></a>

### Direct sum

A decomposition into subspaces in which each vector has a unique sum of components. For two subspaces, uniqueness is equivalent to their intersection containing only zero.

**Quick example:** Every pair (x,y) is uniquely (x,0)+(0,y), the sum of one vector from each coordinate axis.

[Hand-worked example](examples/01_PACKETS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Subspace](#subspace) · [Complete packet family](#complete-packet-family)

<a id="quotient-space"></a>

### Quotient space

The vector space V/W obtained by identifying vectors whose difference lies in a subspace W. A coset x+W records the equivalence class of x.

**Quick example:** Modulo span{(1,−1)}, the pairs (2,3) and (4,1) represent the same class because their difference is (2,−2).

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Subspace](#subspace) · [Fiber](#fiber)

<a id="determinant"></a>

### Determinant

A scalar attached to a square matrix. For [[a,b],[c,d]] it is ad − bc. Over a field, a square matrix is invertible exactly when its determinant is nonzero.

**Quick example:** The matrix [[1,2],[3,4]] has determinant 4−6 = −2 and is invertible over the real numbers.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#elimination) · [Inverse](#inverse) · [Field](#field)

<a id="domain-codomain"></a>

### Domain and codomain

The declared input and target spaces of a map. The codomain includes all permitted outputs, while the image consists of outputs actually attained.

**Quick example:** For T: R² → R³ with T(x,y) = (x,y,0), the domain is R², codomain is R³ and image is a plane.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#typed-paths) · [Image](#image) · [Surjective map](#surjective) · [Typed system](#typed-system)

<a id="affine-map"></a>

### Affine map

A map between vector spaces of the form x↦Lx+c, where L is linear and c is a fixed output vector. The translation c may move zero, so the map is linear exactly when c=0.

**Also called:** Affine transformation.

**Quick example:** f(x) = 2x+1 is affine; f(0) = 1 shows it is not linear.

**In the worked example:** The rule A(x₁,x₂)=2x₁−x₂+3 is affine. Its linear part is L(x₁,x₂)=2x₁−x₂, and A(0,0)=3.

[Hand-worked example](operators/BASICS.md#2-linear-affine-and-nonlinear-rules) · [Linear map](#linear-map) · [Nonlinear map](#nonlinear-map) · [Operator](#operator)

<a id="row-space"></a>

### Row space

The span of a matrix’s row vectors over its declared coefficient field. When rows represent scalar measurements, their row space is the set of all linear combinations of those measurements.

**Also called:** Row span.

**Quick example:** The rows (1,1) and (2,2) span the one-dimensional row space of [[1,1],[2,2]].

**In the worked example:** The rows (1,1,0) and (0,1,1) span the target row (1,2,1), obtained by adding them. Thus adding the corresponding two measurements recovers that target exactly.

[Hand-worked example](operators/RECOVERY.md#3-linear-recovery-row-spaces-and-kernels) · [Span](#span) · [Rank](#rank) · [Kernel](#kernel) · [Exact recovery from a summary](#exact-recovery)

<a id="covector"></a>

### Covector

A linear functional from a vector space to its coefficient field. With column-vector coordinates, it is stored as a row ℓ and acts by ℓx. Covectors form the dual space. A chosen inner product can identify vectors with covectors, but that identification depends on the metric.

**Also called:** Linear functional, Dual vector.

**In the worked example:** The sum observation R(a,b) = a+b is the covector (1,1). The requested first-coordinate observation F(a,b) = a is the covector (1,0).

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](operators/catalog/C_COORDINATES.md#op-172) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Linear map](#linear-map) · [Covector pullback](#covector-pullback) · [Inner product](#inner-product) · [Coordinates](#coordinates)

<a id="positive-definite"></a>

### Positive definite matrix

A real symmetric or complex Hermitian matrix Q for which x*Qx > 0 for every nonzero vector x. It defines an inner product and is invertible. Positive semidefiniteness only requires x*Qx ≥ 0 and can allow nonzero vectors of zero length.

**Also called:** Positive-definite matrix, SPD matrix, HPD matrix.

**Quick example:** diag(1,3) is positive definite because x²+3y² > 0 for every nonzero pair.

**In the worked example:** For the example's analysis matrix, Q = A*A = [[2,1],[1,2]]. Its quadratic form is a²+b²+(a+b)², which is positive whenever (a,b) ≠ (0,0).

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/K_METRICS.md#op-185) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Positive semidefinite matrix](#positive-semidefinite) · [Inner product](#inner-product) · [Classical frame operator](#classical-frame-operator) · [Metric adjoint](#metric-adjoint)

<a id="seminorm"></a>

### Seminorm

A nonnegative function satisfying absolute homogeneity and the triangle inequality, while allowing a nonzero vector to have value zero. For linear synthesis S from a redundant coefficient space, p(c) = ‖Sc‖ is a seminorm whose zero directions are exactly ker S. Passing to the quotient by those directions gives a norm.

**Also called:** Semi-norm.

**Quick example:** p(x,y) = |x| is a seminorm on R² that vanishes on every vertical vector.

**In the worked example:** The coefficient vector g = (−1,−1,1) is nonzero but satisfies ‖Sg‖ = 0 for the example's synthesis map. Its ordinary Euclidean norm is √3.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Norm](#norm) · [Coefficient gauge](#coefficient-gauge) · [Coefficient metric](#coefficient-metric) · [Quotient space](#quotient-space)

<a id="dual-space"></a>

### Dual space

For a vector space V over a field, the vector space V* of linear scalar-valued functions on V. Its elements are covectors or linear functionals. In finite coordinates a row vector acts on a column vector, but identifying covectors with vectors requires additional choices.

**Quick example:** On pairs, ℓ(x,y) = 2x−y is a covector. It sends (3,4) to 2.

[Further reading](operators/BASICS.md) · [Covector](#covector) · [Covector pullback](#covector-pullback) · [Inner product](#inner-product)

<a id="orthogonal-complement"></a>

### Orthogonal complement

For a subspace W of an inner-product space, W⊥ consists of all vectors perpendicular to every vector in W. In finite dimensions the space decomposes as the orthogonal direct sum W ⊕ W⊥.

**Also called:** Perpendicular complement.

**Quick example:** In Euclidean R², the perpendicular complement of span{(1,1)} is span{(1,−1)}.

**Keep in mind:** Perpendicularity depends on the inner product. A weighted inner product can change the complement.

[Further reading](operators/PACKETS.md) · [Subspace](#subspace) · [Inner product](#inner-product) · [Orthogonal projector](#orthogonal-projector) · [Direct sum](#direct-sum)

<a id="orthonormal-basis"></a>

### Orthonormal basis

A basis whose vectors have norm one and are pairwise perpendicular in the chosen inner product. In finite real or complex coordinates, the matrix Q with these basis columns satisfies Q*Q = I.

**Quick example:** The Haar vectors (1,1)/√2 and (1,−1)/√2 form an orthonormal basis of Euclidean R².

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Basis](#basis) · [Inner product](#inner-product) · [Orthogonal matrix](#orthogonal-matrix) · [Unitary matrix](#unitary)

<a id="singular-value"></a>

### Singular value

A nonnegative square root of an eigenvalue of A*A for a real or complex matrix A, with zero-padding conventions stated when needed. The largest singular value is the induced Euclidean operator norm. Singular values describe gain and rank without requiring A to be square.

**Quick example:** For A = [[0,2],[3,0]], A*A = diag(9,4), so its singular values are 3 and 2.

**Keep in mind:** A small computed singular value needs a tolerance or enclosure before it is treated as exactly zero.

[Further reading](operators/STABILITY.md) · [Adjoint matrix](#adjoint) · [Gram operator](#gram-operator) · [Induced operator norm](#operator-norm) · [Rank](#rank)

<a id="singular-value-decomposition"></a>

### Singular value decomposition

A factorization A = UΣV* of a finite real or complex matrix, where U and V are orthogonal or unitary and Σ is rectangular diagonal with nonnegative entries. These entries are the singular values. It separates input directions, gains and output directions.

**Also called:** SVD.

**Quick example:** The diagonal matrix diag(3,1) already has an SVD with U = V = I and Σ = diag(3,1).

**Keep in mind:** Truncating an SVD changes the operator unless all omitted singular values are zero.

[Further reading](operators/STABILITY.md) · [Singular value](#singular-value) · [Unitary matrix](#unitary) · [Moore–Penrose inverse](#pseudoinverse) · [Rank](#rank)

<a id="bilinear-form"></a>

### Bilinear form

A scalar-valued function B(u,v) linear separately in u and v. Over the real numbers a matrix M gives B(u,v) = uᵀMv. Symmetry, positivity and nondegeneracy are additional properties rather than part of bilinearity.

**Quick example:** B(u,v) = u₁v₁−u₂v₂ is symmetric and bilinear, but B((0,1),(0,1)) = −1, so it is not an inner product.

**Keep in mind:** For complex inner products one argument is conjugate-linear. That pairing is sesquilinear.

[Further reading](operators/BASICS.md) · [Inner product](#inner-product) · [Quadratic form](#quadratic-form) · [Positive definite matrix](#positive-definite)

<a id="quadratic-form"></a>

### Quadratic form

In the real finite-dimensional setting, a scalar expression q(x) = xᵀMx, usually written with M symmetric. In complex Hermitian geometry the corresponding real-valued expression is x*Mx with M Hermitian. Positivity asks whether this value is nonnegative for every input.

**Quick example:** With M = [[1,1],[1,1]], q(x,y) = (x+y)². It is nonnegative and vanishes on the nonzero direction (1,−1).

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Bilinear form](#bilinear-form) · [Positive semidefinite matrix](#positive-semidefinite) · [Gaussian quadratic form](#gaussian-quadratic-form)

<a id="triangular-matrix"></a>

### Triangular matrix

A square matrix with every entry on one side of its diagonal zero. A unitriangular matrix also has all diagonal entries equal to one, so it is invertible over any field. Triangular coordinate maps let successive coefficients be recovered in order.

**Quick example:** The lower-triangular matrix [[1,0],[3,1]] sends (a,b) to (a,3a+b); recover b by subtracting 3a.

[Further reading](operators/POLYNOMIAL.md) · [Matrix](#matrix) · [Inverse](#inverse) · [Stirling transform](#stirling-transform)

<a id="operators-and-packets"></a>

## Operators, seeds, and packets

How an allowed action generates, selects, and decomposes objects.

[Realization](#realization) · [Seed](#seed) · [Address](#address) · [Projector](#projector) · [Packet](#packet) · [Typed system](#typed-system) · [Operator algebra](#operator-algebra) · [Seed rank](#seed-rank) · [Cyclic vector](#cyclic) · [Orthogonal projector](#orthogonal-projector) · [Complete packet family](#complete-packet-family) · [Mutual annihilation](#mutual-annihilation) · [Invariant subspace](#invariant-subspace) · [Eigenvector](#eigenvector) · [Eigenvalue](#eigenvalue) · [Eigenspace](#eigenspace) · [Diagonalizable operator](#diagonalizable) · [Polynomial in an operator](#polynomial-in-operator) · [Minimal polynomial](#minimal-polynomial) · [Spectral projector](#spectral-projector) · [Commutator](#commutator) · [Typed path](#typed-path) · [Operator relation](#relation) · [Nilpotent operator](#nilpotent) · [Operator](#operator) · [Nonlinear map](#nonlinear-map) · [Tensor product of operators](#tensor-product) · [Oblique projector](#oblique-projector) · [Spectral radius](#spectral-radius) · [Falling-factorial raising operator](#raising-operator) · [Falling-degree operator](#degree-operator) · [Normal matrix](#normal-matrix) · [Involution](#involution) · [Operator orbit](#operator-orbit)

<a id="realization"></a>

### Realization

A way to represent a declared system using concrete spaces and operations while respecting its required relations. A finite matrix realization assigns a space to each type and a matrix to each permitted arrow.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Typed system](#typed-system) · [Operator algebra](#operator-algebra) · [Compatibility](#compatibility)

<a id="seed"></a>

### Seed

Initial generating data from which the allowed operator action produces further elements. Whether a seed is sufficient depends on both the object and the declared action.

**In the worked example:** On R², let N(a,b) = (b,0) and v = (0,1). Then Nv = (1,0), so v and its image generate every vector by linear combinations.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Span](#span) · [Seed rank](#seed-rank) · [Cyclic vector](#cyclic)

<a id="address"></a>

### Address

A label for a legal operator path or a packet coordinate. Examples include signal phases, residue classes, and positions in a packet tree. An address identifies a location in a representation, not necessarily a physical location.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Typed system](#typed-system) · [Packet](#packet) · [Residue class](#residue-class)

<a id="projector"></a>

### Projector

A linear operator P satisfying P² = P. Applying it twice has the same effect as applying it once. This algebraic definition does not require orthogonality.

**Also called:** Projection, Idempotent linear operator.

**In the worked example:** On R², P₁(a,b) = (a,0). Applying P₁ again still gives (a,0), so P₁² = P₁.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Orthogonal projector](#orthogonal-projector) · [Packet](#packet) · [Redundant coordinates](#redundancy) · [Oblique projector](#oblique-projector) · [Reconstruction component](#reconstruction-component) · [Fixed point](#fixed-point) · [Involution](#involution)

<a id="packet"></a>

### Packet

In the finite projector example, a selected component Pᵢx or the subspace in which it lies, according to context. Signal, algebraic and arithmetic works may assign the word more specific meanings.

**In the worked example:** For x = (2,3)ᵀ, the coordinate projectors give packets P₁x = (2,0)ᵀ and P₂x = (0,3)ᵀ. Their sum recovers x.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Complete packet family](#complete-packet-family) · [Address](#address)

<a id="typed-system"></a>

### Typed system

A system that records which objects an operation accepts and returns. A path of operations is legal only when consecutive input and output types agree. Types are part of the mathematical specification.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#typed-finite-expressions) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Linear map](#linear-map) · [Composition](#composition) · [Realization](#realization)

<a id="operator-algebra"></a>

### Operator algebra

In the finite linear setting, a collection of linear operators closed under sums, scalar multiples, and composition. When a unital algebra is intended, the identity operator is included.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Composition](#composition) · [Seed](#seed) · [Invariant subspace](#invariant-subspace)

<a id="seed-rank"></a>

### Seed rank

In the finite linear example, the least number of seeds whose operator-generated span is the whole space. More general definitions can involve modules, dense generation, and cardinalities. Read the definition in the chosen work.

**In the worked example:** For N(a,b) = (b,0) on R², one seed v = (0,1) suffices. With only the zero operator and the identity, two seeds are needed on the same space.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Seed](#seed) · [Span](#span) · [Rank](#rank)

<a id="cyclic"></a>

### Cyclic vector

For a single linear operator T, a vector v is cyclic when v, Tv, T²v and further iterates span the space under consideration. One cyclic vector is enough to generate that operator module.

**Also called:** Cyclic seed.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Seed](#seed) · [Span](#span)

<a id="orthogonal-projector"></a>

### Orthogonal projector

A projector onto a subspace whose residual x − Px is perpendicular to that subspace in the specified inner product. In ordinary real Euclidean coordinates its matrix is symmetric as well as idempotent.

**Also called:** Orthogonal projection.

**In the worked example:** With weights (1,3,2), the averaging map sends (2,6,9)ᵀ to (5,5,9)ᵀ. Its residual (−3,1,0)ᵀ has weighted inner product −3a + 3a = 0 with every retained vector (a,a,b)ᵀ. The averaging matrix is not symmetric in ordinary coordinates.

**Keep in mind:** Orthogonality depends on the inner product. Weighted averaging need not have a symmetric matrix in ordinary coordinates.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Inner product](#inner-product)

<a id="complete-packet-family"></a>

### Complete packet family

In these finite examples, projectors Pᵢ with PᵢPⱼ = 0 for distinct indices and sum_i Pᵢ = I. These identities decompose every vector as x = sum_i Pᵢx.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Mutual annihilation](#mutual-annihilation) · [Reconstruction](#reconstruction)

<a id="mutual-annihilation"></a>

### Mutual annihilation

The relation PᵢPⱼ = 0 whenever i and j differ. Applying one selection after a different selection gives zero. For a pair of projectors, both orders must be checked.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Complete packet family](#complete-packet-family)

<a id="invariant-subspace"></a>

### Invariant subspace

A subspace W preserved by an operator T, meaning T(W) is contained in W. Preservation does not require T to act as the identity on W.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Span](#span) · [Operator algebra](#operator-algebra)

<a id="eigenvector"></a>

### Eigenvector

A nonzero vector v for which Tv = λv. The scalar λ is the associated eigenvalue. Zero is excluded from the definition of eigenvector.

**Also called:** Characteristic vector.

**Quick example:** For T = diag(2,3), the nonzero vector (1,0) is an eigenvector with eigenvalue 2.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Eigenvalue](#eigenvalue) · [Invariant subspace](#invariant-subspace)

<a id="eigenvalue"></a>

### Eigenvalue

A scalar λ such that Tv = λv for some nonzero v over the specified field. A real matrix may have no real eigenvalue even though it has eigenvalues over the complex numbers.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Eigenvector](#eigenvector) · [Field](#field) · [Singular value](#singular-value) · [Normal matrix](#normal-matrix)

<a id="eigenspace"></a>

### Eigenspace

For an operator T and scalar λ, the kernel of T − λI. It includes zero and all eigenvectors with eigenvalue λ.

**Quick example:** For T = diag(2,2,3), the eigenvalue-2 eigenspace is the plane {(x,y,0)}.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Kernel](#kernel) · [Eigenvector](#eigenvector)

<a id="diagonalizable"></a>

### Diagonalizable operator

An operator that has a basis of eigenvectors over the stated field. Equivalently, its matrix becomes diagonal after an invertible change of basis.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Basis](#basis) · [Eigenvector](#eigenvector) · [Coordinate change](#coordinate-change)

<a id="polynomial-in-operator"></a>

### Polynomial in an operator

Substitute T into p(t) = a₀ + a₁t + ⋯ + aₙtⁿ to obtain p(T) = a₀I + a₁T + ⋯ + aₙTⁿ. The constant term acts through the identity operator.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Operator algebra](#operator-algebra) · [Identity operator](#identity)

<a id="minimal-polynomial"></a>

### Minimal polynomial

For a linear operator on a nonzero finite-dimensional space over a field, the monic polynomial of least degree with m(T) = 0. It records an exact operator relation.

**Quick example:** For T = diag(2,3), the minimal polynomial is (t−2)(t−3).

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Polynomial in an operator](#polynomial-in-operator) · [Operator relation](#relation)

<a id="spectral-projector"></a>

### Spectral projector

In the diagonalizable finite example, the projector onto one eigenspace along the sum of the others. Distinct eigenvalues allow a polynomial interpolation formula for these projectors.

**Also called:** Eigenprojector.

**In the worked example:** For T(a,b) = (2a+b,3b), the projectors P₂ = 3I−T and P₃ = T−2I split (2,3)ᵀ into (−1,0)ᵀ and (3,3)ᵀ. The identity T = 2P₂+3P₃ then gives T(2,3)ᵀ = (7,9)ᵀ.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Projector](#projector) · [Eigenspace](#eigenspace) · [Diagonalizable operator](#diagonalizable)

<a id="commutator"></a>

### Commutator

For operators on the same space, [A,B] = AB − BA. A zero commutator means the two orders of composition agree.

**Quick example:** For P = diag(1,0) and T swapping coordinates, PT−TP = [[0,1],[−1,0]].

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#typed-paths) · [Composition](#composition) · [Operator algebra](#operator-algebra)

<a id="typed-path"></a>

### Typed path

A sequence of arrows in which each output type matches the next input type. Its realization is the corresponding ordered composition. An empty path at a type acts as its identity.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#typed-paths) · [Typed system](#typed-system) · [Composition](#composition) · [Identity operator](#identity)

<a id="relation"></a>

### Operator relation

A required equality between legal operator expressions, such as T² = 0. In a typed system, both sides must have the same input and output types.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#typed-paths) · [Typed path](#typed-path) · [Realization](#realization) · [Minimal polynomial](#minimal-polynomial)

<a id="nilpotent"></a>

### Nilpotent operator

An operator N for which Nᵏ = 0 for some positive integer k. It can be nonzero. The smallest such k on a nonzero space is its nilpotency index.

**Also called:** Nilpotent linear map, Nilpotent endomorphism.

**Quick example:** N = [[0,1],[0,0]] is nonzero, but N² = 0.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Operator algebra](#operator-algebra) · [Minimal polynomial](#minimal-polynomial)

<a id="operator"></a>

### Operator

A specified rule T:X→Y taking each allowed input to an output of the declared type. The word alone does not imply linearity, invertibility, or continuity. Those are additional properties of the rule.

**In the worked example:** R(x₁,x₂)=x₁+x₂ maps a pair to a scalar, while B(s)=(s,0) maps a scalar to a pair. Thus RB and BR act on different spaces.

[Hand-worked example](operators/BASICS.md#1-typed-operators-domains-and-codomains) · [Linear map](#linear-map) · [Domain and codomain](#domain-codomain) · [Composition](#composition)

<a id="nonlinear-map"></a>

### Nonlinear map

A map between vector spaces that does not satisfy the linear-combination identity for all allowed vectors and scalars. Splitting its input into packets need not split its output into the sum of the separate packet outputs.

**Also called:** Nonlinear operator.

**In the worked example:** For f(x₁,x₂)=x₁x₂, f(1,0)+f(0,1)=0 but f((1,0)+(0,1))=1. The two input directions interact.

[Hand-worked example](operators/BASICS.md#2-linear-affine-and-nonlinear-rules) · [Linear map](#linear-map) · [Affine map](#affine-map) · [Pointwise transfer defect](#transfer-defect)

<a id="tensor-product"></a>

### Tensor product of operators

For linear maps A:X→X′ and B:Y→Y′, the linear map A⊗B determined by (A⊗B)(x⊗y)=Ax⊗By. Choosing bases represents it by a Kronecker matrix on the tensor-product coordinates.

**Also called:** Tensor product, Kronecker product of matrices.

**In the worked example:** With A=diag(2,3) and B the two-coordinate swap, A⊗B sends (1,2,0,0)ᵀ to (4,2,0,0)ᵀ. It acts on four coordinates, while AB acts on two.

[Hand-worked example](operators/ALGEBRA.md#7-tensor-products-and-kronecker-matrices) · [Linear map](#linear-map) · [Composition](#composition) · [Matrix](#matrix)

<a id="oblique-projector"></a>

### Oblique projector

A linear projector whose range and kernel are complementary but not perpendicular in the chosen inner product. It reconstructs by x=Px+(I−P)x, while the two pieces need not give an orthogonal energy decomposition.

**Also called:** Oblique projection.

**In the worked example:** P(x₁,x₂)=(x₁+x₂,0) splits (2,3)ᵀ as (5,0)ᵀ+(−3,3)ᵀ. Their squared Euclidean lengths sum to 43, although the original squared length is 13.

[Hand-worked example](operators/PACKETS.md#3-orthogonal-and-oblique-projectors) · [Projector](#projector) · [Orthogonal projector](#orthogonal-projector) · [Inner product](#inner-product) · [Induced operator norm](#operator-norm)

<a id="spectral-radius"></a>

### Spectral radius

For an n by n complex matrix with n ≥ 1, the largest absolute value of its eigenvalues. For a real matrix, use its complex eigenvalues. This scalar need not equal the largest one-step amplification measured by an induced norm.

**In the worked example:** N=[[0,M],[0,0]] with M>0 has spectral radius zero and Euclidean operator norm M. Since N²=0, this large one-step gain disappears at the second power.

[Hand-worked example](operators/STABILITY.md#6-spectrum-and-nonnormal-growth) · [Eigenvalue](#eigenvalue) · [Induced operator norm](#operator-norm) · [Nilpotent operator](#nilpotent)

<a id="raising-operator"></a>

### Falling-factorial raising operator

On rational polynomials, the operator Af(x)=x f(x−1), which sends bₖ to bₖ₊₁. It is multiplication by the source variable transported through Φ(zᵏ)=bₖ, so A=Φ(z·)Φ⁻¹.

**Also called:** Raising operator in the polynomial example.

**In the worked example:** A b₂=x(x−1)(x−2)=b₃. Together with Δbₖ=k bₖ₋₁, this gives (ΔA−AΔ)bₖ=bₖ.

**Keep in mind:** The identity ΔA−AΔ=I is on the full polynomial space. A finite square truncation that drops the highest raised degree changes the boundary calculation.

[Hand-worked example](operators/POLYNOMIAL.md#3-raising-and-degree-operators) · [Falling factorial](#falling-factorial) · [Forward difference](#forward-difference) · [Falling-degree operator](#degree-operator) · [Commutator](#commutator)

<a id="degree-operator"></a>

### Falling-degree operator

On rational polynomials, N=AΔ with A the falling-factorial raising operator. Explicitly, Nf(x)=x(f(x)−f(x−1)), and Nbₖ=k bₖ. Its eigenvalue records falling degree in this basis.

**Also called:** Degree operator in the falling-factorial basis.

**In the worked example:** For b₃=x(x−1)(x−2), Nb₃=3b₃.

**Keep in mind:** In positive characteristic, different degrees can give the same eigenvalue. Over F₃, b₀ and b₃ both have eigenvalue zero, so a polynomial in N cannot separate them.

[Hand-worked example](operators/POLYNOMIAL.md#3-raising-and-degree-operators) · [Falling-factorial raising operator](#raising-operator) · [Forward difference](#forward-difference) · [Eigenvalue](#eigenvalue) · [Residue coefficient selector](#coefficient-selector)

<a id="normal-matrix"></a>

### Normal matrix

A complex square matrix T satisfying T*T = TT*. In finite complex dimensions, normal matrices admit an orthonormal eigenbasis. Hermitian and unitary matrices are normal; an arbitrary diagonalizable matrix need not be normal.

**Quick example:** The nonzero nilpotent matrix [[0,1],[0,0]] is not normal: T*T = diag(0,1), while TT* = diag(1,0).

[Further reading](operators/STABILITY.md) · [Adjoint matrix](#adjoint) · [Hermitian matrix](#hermitian) · [Unitary matrix](#unitary) · [Diagonalizable operator](#diagonalizable)

<a id="involution"></a>

### Involution

An operation U whose square is the identity: U² = I. Applying it twice restores the input. A linear involution over a field where 2 is invertible splits the space into its +1 and −1 eigenspaces via (I+U)/2 and (I−U)/2.

**Quick example:** Reflection of a polynomial, Uf(x) = f(−x), is an involution. Its +1 and −1 parts are the even and odd polynomials.

**Keep in mind:** The identity U² = I does not by itself make U orthogonal or unitary.

[Further reading](operators/POLYNOMIAL.md) · [Projector](#projector) · [Eigenvalue](#eigenvalue) · [Unitary matrix](#unitary)

<a id="operator-orbit"></a>

### Operator orbit

The set of outputs obtained from one input by the declared allowed operations. For a single operator T, its forward orbit is {v,Tv,T²v,…}. Taking the linear span of an orbit is a further step in the definition of a cyclic vector.

**Quick example:** If T swaps two coordinates, the orbit of (1,0) is {(1,0),(0,1)}; its span is all of R².

[Further reading](examples/02_SEEDS.md) · [Seed](#seed) · [Cyclic vector](#cyclic) · [Span](#span) · [Address](#address)

<a id="coordinates-and-transfer"></a>

## Coordinates and transfer

How descriptions change and operations move between components.

[Coordinates](#coordinates) · [Analysis and synthesis](#analysis-synthesis) · [Transfer block](#transfer-block) · [Coordinate change](#coordinate-change) · [Inverse](#inverse) · [Left inverse](#left-inverse) · [Redundant coordinates](#redundancy) · [Composition](#composition) · [Operator conjugation](#conjugation) · [Intertwiner](#intertwiner) · [Block matrix](#block-matrix) · [Schur complement](#schur-complement) · [Elimination](#elimination) · [Orthogonal matrix](#orthogonal-matrix) · [Normalization](#normalization) · [Right inverse](#right-inverse) · [Transported product](#transported-product) · [Leakage from a retained packet](#packet-leakage) · [Pointwise transfer defect](#transfer-defect) · [Finite frame](#finite-frame) · [Frame bounds](#frame-bounds) · [Classical frame operator](#classical-frame-operator) · [Canonical dual synthesis](#canonical-dual) · [Moore–Penrose inverse](#pseudoinverse) · [Coefficient projection](#coefficient-projection) · [Reconstruction component](#reconstruction-component) · [Coefficient gauge](#coefficient-gauge) · [Coefficient metric](#coefficient-metric) · [Metric adjoint](#metric-adjoint) · [Covector pullback](#covector-pullback) · [Operator compression](#compression) · [Linear isometry](#isometry) · [Algebra homomorphism](#algebra-homomorphism)

<a id="coordinates"></a>

### Coordinates

Values describing an object relative to a chosen representation. Coordinates can be unique basis coefficients or redundant measurements, depending on the setup.

**In the worked example:** The coordinate change C(a,b) = (a + b/2,b) sends x = (2,3)ᵀ to y = (7/2,3)ᵀ. These describe the same object in two coordinate systems.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Basis](#basis) · [Coordinate change](#coordinate-change) · [Redundant coordinates](#redundancy)

<a id="analysis-synthesis"></a>

### Analysis and synthesis

Analysis sends an object to coordinates. Synthesis returns an object from coordinates. In the finite linear model, A and S are linear maps and exact reconstruction is the identity SA = I.

**In the worked example:** The analysis A(a,b) = (a,b,a+b) sends (2,3)ᵀ to (2,3,5)ᵀ. The example’s synthesis S returns (2,3)ᵀ, with SA = I₂.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Left inverse](#left-inverse) · [Coordinates](#coordinates) · [Reconstruction](#reconstruction) · [Finite frame](#finite-frame) · [Canonical dual synthesis](#canonical-dual) · [Reconstruction component](#reconstruction-component)

<a id="transfer-block"></a>

### Transfer block

The part of an operation connecting a source component to a target component. With source projector Pᵢ, target projector Qⱼ and operator T, the block is QⱼTPᵢ. Complete source and target families allow the blocks to reconstruct T.

**In the worked example:** For T = [[1,2],[3,4]], the coordinate block P₁TP₂ sends (2,3)ᵀ to (6,0)ᵀ. It carries source coordinate 2 into target coordinate 1.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Projector](#projector) · [Composition](#composition) · [Reconstruction](#reconstruction)

<a id="coordinate-change"></a>

### Coordinate change

A transformation between descriptions of the same object. In the invertible linear example the convention is y = Cx, so x = C⁻¹y. Keeping track of the direction prevents inverse formulas from being swapped.

**Also called:** Change of coordinates.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Coordinates](#coordinates) · [Inverse](#inverse) · [Operator conjugation](#conjugation) · [Algebra homomorphism](#algebra-homomorphism) · [Linear isometry](#isometry)

<a id="inverse"></a>

### Inverse

A map that undoes another map in both directions. For a square invertible matrix C, the inverse satisfies C⁻¹C = CC⁻¹ = I.

**Also called:** Two-sided inverse.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Identity operator](#identity) · [Left inverse](#left-inverse)

<a id="left-inverse"></a>

### Left inverse

For A mapping an input space to a coordinate space, S is a left inverse when SA = I on the input space. This gives exact reconstruction of analyzed inputs. It does not imply AS = I on the entire coordinate space.

**In the worked example:** The redundant-coordinate example has SA = I₂ but AS ≠ I₃. S recovers every original vector even though it does not invert every three-coordinate input.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Inverse](#inverse) · [Analysis and synthesis](#analysis-synthesis) · [Image](#image)

<a id="redundancy"></a>

### Redundant coordinates

A representation containing more coordinate entries than are needed for a basis description. Valid coordinate lists can satisfy relations, such as a third measurement being the sum of the first two.

**Also called:** Redundant representation.

**Keep in mind:** The reconstruction components SEᵢA can sum to the identity without being projectors.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Basis](#basis) · [Analysis and synthesis](#analysis-synthesis) · [Projector](#projector)

<a id="composition"></a>

### Composition

Applying one map after another. In a matrix product UT, T acts first and U acts second. The intermediate dimensions or types must agree.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#typed-finite-expressions) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Typed system](#typed-system) · [Matrix](#matrix) · [Transfer block](#transfer-block)

<a id="conjugation"></a>

### Operator conjugation

The change in an operator matrix under an invertible coordinate change. With y = Cx and original operator T, the new matrix is CTC⁻¹. This usage is distinct from complex conjugation.

**Also called:** Similarity transformation.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Coordinate change](#coordinate-change) · [Intertwiner](#intertwiner)

<a id="intertwiner"></a>

### Intertwiner

A linear map C connecting operators T and U by CT = UC. Applying T and then C agrees with applying C and then U. An intertwiner need not be invertible.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Operator conjugation](#conjugation) · [Commuting diagram](#commuting-diagram)

<a id="block-matrix"></a>

### Block matrix

A matrix grouped into rectangular submatrices according to decompositions of its input and output coordinates. Block products require the inner dimensions to agree.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Matrix](#matrix) · [Transfer block](#transfer-block)

<a id="schur-complement"></a>

### Schur complement

For the block matrix [[A,B],[C,D]] with invertible A, the Schur complement of A is D − CA⁻¹B. It is the remaining operator after eliminating the first block of unknowns.

**Quick example:** In [[2,1],[1,3]], eliminating the invertible upper-left entry gives the scalar complement 3−1/2 = 5/2.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#elimination) · [Block matrix](#block-matrix) · [Elimination](#elimination) · [Inverse](#inverse)

<a id="elimination"></a>

### Elimination

Removing selected unknowns by solving part of a system and substituting into the remaining equations. The substitution requires its stated invertibility or solvability assumptions.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#elimination) · [Schur complement](#schur-complement) · [Reconstruction](#reconstruction)

<a id="orthogonal-matrix"></a>

### Orthogonal matrix

A real square matrix Q with QᵀQ = QQᵀ = I. It preserves the Euclidean inner product and norm. A transform with orthogonal rows can still need normalization to satisfy this identity.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#haar) · [Inner product](#inner-product) · [Norm](#norm) · [Normalization](#normalization)

<a id="normalization"></a>

### Normalization

A declared scaling convention. For a Haar pair, dividing sums and differences by two gives averages, while dividing by √2 gives a Euclidean norm-preserving transform.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#haar) · [Haar pair](#haar-pair) · [Orthogonal matrix](#orthogonal-matrix)

<a id="right-inverse"></a>

### Right inverse

For R:X→S, a map B:S→X satisfying RB=I on S. It chooses an input that produces each summary value. This identity does not require BR=I on X.

**Quick example:** For R(x,y) = x, the map S(x) = (x,0) satisfies RS = I. The reverse product SR deletes the second coordinate.

**In the worked example:** For R(x₁,x₂)=x₁+x₂ and B(s)=(s,0), RB(s)=s. But BR(0,1)=(1,0), so this choice does not recover every original pair.

[Hand-worked example](operators/BASICS.md#6-left-and-right-inverses) · [Left inverse](#left-inverse) · [Inverse](#inverse) · [Projector](#projector)

<a id="transported-product"></a>

### Transported product

Given an invertible linear map Φ between two representations, the target product f⋆g=Φ(Φ⁻¹f·Φ⁻¹g), where · is the declared source product. This carries the source multiplication law into the target coordinates.

**Also called:** Transported multiplication, Star product in the polynomial example.

**In the worked example:** For Φ(zᵏ)=bₖ, one has bₐ⋆bᵦ=bₐ₊ᵦ and x⋆x=x(x−1). The forward difference satisfies Δ(f⋆g)=(Δf)⋆g+f⋆(Δg).

**Keep in mind:** Ordinary target multiplication is a different product: Δ(x²)=2x+1, whereas Δ(x⋆x)=2x.

[Hand-worked example](operators/POLYNOMIAL.md#6-transported-multiplication-and-its-product-rule) · [Coordinate change](#coordinate-change) · [Composition](#composition) · [Falling factorial](#falling-factorial) · [Forward difference](#forward-difference)

<a id="packet-leakage"></a>

### Leakage from a retained packet

For a projector P and a linear operator T, the map (I−P)TP records output leaving the retained range after the input starts in that range. It vanishes exactly when that range is invariant under T.

**Also called:** Packet leakage, Off-packet leakage.

**In the worked example:** With P=diag(1,0), T=[[1,2],[3,4]], and x=(2,0)ᵀ, the full output is (2,6)ᵀ and the retained output is (2,0)ᵀ. The leakage is (0,6)ᵀ.

**Keep in mind:** For an arbitrary input, T−PTP also includes transfers starting in the discarded input range. The single leakage term is not the whole residual in that setting.

[Hand-worked example](operators/TRANSFER.md#6-leakage-from-a-retained-packet) · [Transfer block](#transfer-block) · [Invariant subspace](#invariant-subspace) · [Projector](#projector) · [Residual](#residual)

<a id="transfer-defect"></a>

### Pointwise transfer defect

Given representation maps R_X,R_Y, an operation f, and a proposed transferred rule f̄, the discrepancy Δ_f(x)=R_Y(f(x))−f̄(R_X(x)). The subtraction requires a common vector-space output. The defect depends on the proposed rule and the input.

**Also called:** Transfer defect, Nonlinear transfer defect.

**In the worked example:** For f(x₁,x₂)=x₁x₂, R_X(x)=x₁+x₂, R_Y=I, and f̄(s)=s²/4, the defect at (2,3) is 6−25/4=−1/4. The candidate is exact on inputs (t,t).

**Keep in mind:** A pointwise defect can be nonlinear. Failure of one proposed rule is not by itself an obstruction to every possible rule.

[Hand-worked example](operators/TRANSFER.md#7-nonlinear-transfer-defects) · [Nonlinear map](#nonlinear-map) · [Commuting diagram](#commuting-diagram) · [Residual](#residual) · [Exact recovery from a summary](#exact-recovery)

<a id="finite-frame"></a>

### Finite frame

A spanning family in a finite-dimensional real or complex inner-product space, used to analyze a vector through its inner products with the family. A frame may contain redundant vectors. In orthonormal coordinates, its analysis matrix A has full column rank and admits a left inverse.

**Also called:** Frame, Finite analysis frame.

**In the worked example:** The vectors (1,0), (0,1) and (1,1) give A(a,b) = (a,b,a+b). Three measurements recover a vector in R², although the three frame vectors are not a basis.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/A_STRUCTURAL.md#op-202) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Basis](#basis) · [Analysis and synthesis](#analysis-synthesis) · [Frame bounds](#frame-bounds) · [Canonical dual synthesis](#canonical-dual)

<a id="frame-bounds"></a>

### Frame bounds

Positive constants α and β such that α‖x‖² ≤ ‖Ax‖² ≤ β‖x‖² for every input x of a frame analysis map A. The lower bound ensures that analysis loses no vector direction. Both bounds depend on the declared inner products and normalization.

**Also called:** Lower frame bound, Upper frame bound.

**In the worked example:** For A(a,b) = (a,b,a+b), ‖Ax‖² = a²+b²+(a+b)² lies between ‖x‖² and 3‖x‖² in Euclidean norm. The optimal bounds are α = 1 and β = 3.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md#5-scope-boundary) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Finite frame](#finite-frame) · [Norm](#norm) · [Classical frame operator](#classical-frame-operator)

<a id="classical-frame-operator"></a>

### Classical frame operator

For a finite frame analysis map A with fixed inner products, the operator G = A* A on the original vector space. In orthonormal stored coordinates, * is conjugate transpose. G is positive definite and invertible when A has full column rank. Its inverse gives canonical dual synthesis G⁻¹A*.

**Also called:** Frame operator, Analysis Gram operator.

**In the worked example:** The example's analysis matrix gives G = [[2,1],[1,2]], with eigenvalues 1 and 3. This is different from the reconstruction SA = I₂ and the coefficient projection AS.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/A_STRUCTURAL.md#op-202) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Finite frame](#finite-frame) · [Positive definite matrix](#positive-definite) · [Canonical dual synthesis](#canonical-dual) · [Coefficient projection](#coefficient-projection)

<a id="canonical-dual"></a>

### Canonical dual synthesis

For a finite full-column-rank analysis matrix A in orthonormal coordinates, the synthesis S = (A* A)⁻¹A*. It satisfies SA = I, while AS is the orthogonal projector onto the image of A. For fixed A, applying S is linear. Constructing S as A varies requires the rank condition.

**Also called:** Canonical dual frame synthesis, Canonical left inverse.

**In the worked example:** For A(a,b) = (a,b,a+b), canonical dual synthesis is S = (1/3)[[2,−1,1],[−1,2,1]]. It sends (2,3,5) back to (2,3).

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/A_STRUCTURAL.md#op-202) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Finite frame](#finite-frame) · [Classical frame operator](#classical-frame-operator) · [Moore–Penrose inverse](#pseudoinverse) · [Left inverse](#left-inverse)

<a id="pseudoinverse"></a>

### Moore–Penrose inverse

For a real or complex matrix A in Euclidean coordinates, the unique matrix A⁺ satisfying AA⁺A = A, A⁺AA⁺ = A⁺, (AA⁺)* = AA⁺ and (A⁺A)* = A⁺A. It is defined even for rectangular or rank-deficient matrices. AA⁺ and A⁺A are orthogonal projectors on the respective coordinate spaces.

**Also called:** Pseudoinverse, Moore-Penrose pseudoinverse, Moore Penrose inverse.

**Quick example:** For the column A = (1,1)ᵀ, A† = (1/2,1/2). Thus A†A = 1, while AA† projects onto equal-coordinate pairs.

**In the worked example:** For the full-column-rank matrix A in Example 6, A⁺ is the displayed synthesis S. Thus A⁺A = I₂ but AA⁺ ≠ I₃.

**Keep in mind:** A pseudoinverse does not recover directions in the kernel of A. With nonorthonormal coordinates, metric choices must be carried explicitly.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/F_NONLINEAR.md#op-109) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Canonical dual synthesis](#canonical-dual) · [Orthogonal projector](#orthogonal-projector) · [Kernel](#kernel) · [Metric adjoint](#metric-adjoint) · [Singular block range condition](#singular-range-condition) · [Singular value decomposition](#singular-value-decomposition)

<a id="coefficient-projection"></a>

### Coefficient projection

For linear analysis A and linear synthesis S satisfying SA = I, the map P = AS on coefficient space. It satisfies P² = P, has image im A and kernel ker S, and sends any coefficient vector to analyzed coordinates representing the same underlying vector. It need not be orthogonal for an arbitrary left inverse S.

**Also called:** Analysis-synthesis coefficient projector.

**In the worked example:** The triple c = (0,0,1) is not in im A. Its projection is AS c = (1/3,1/3,2/3), whose third coordinate is the sum of the first two.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Analysis and synthesis](#analysis-synthesis) · [Coefficient gauge](#coefficient-gauge) · [Canonical dual synthesis](#canonical-dual) · [Projector](#projector)

<a id="reconstruction-component"></a>

### Reconstruction component

For linear maps A and S with SA = I and a coefficient selector Eᵢ, the map Cᵢ = SEᵢA on the original space. When the selectors partition all coordinates, the Cᵢ sum to the identity. In a redundant system, an individual Cᵢ need not be idempotent, so additive reconstruction alone does not make it a projector.

**Also called:** Physical frame component, Analysis-synthesis component.

**In the worked example:** The first component is C₁ = (1/3)[[2,0],[−1,0]]. It satisfies C₁² = (2/3)C₁ ≠ C₁, even though C₁+C₂+C₃ = I₂.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/A_STRUCTURAL.md#op-021) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Projector](#projector) · [Finite frame](#finite-frame) · [Coefficient projection](#coefficient-projection) · [Reconstruction](#reconstruction)

<a id="coefficient-gauge"></a>

### Coefficient gauge

The kernel of a linear synthesis map S in a redundant linear presentation. Adding g ∈ ker S to a coefficient vector c leaves the represented vector unchanged because S(c+g) = Sc. The quotient of coefficient space by ker S records the represented vectors. For SA = I, (I−AS)c is the gauge part of c.

**Also called:** Synthesis kernel, Coefficient gauge subspace.

**In the worked example:** For the displayed synthesis S, the nonzero vector g = (−1,−1,1) satisfies Sg = 0. Coefficients c and c+g therefore synthesize to the same vector.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Kernel](#kernel) · [Quotient space](#quotient-space) · [Coefficient projection](#coefficient-projection) · [Coefficient metric](#coefficient-metric)

<a id="coefficient-metric"></a>

### Coefficient metric

In a finite linear presentation with Euclidean inner products on the stored spaces, H = S* S pulls the underlying vector geometry back to coefficient space: c*Hd = (Sc)*(Sd). H is positive semidefinite and its kernel is ker S. It gives a genuine inner product after quotienting out those gauge directions.

**Also called:** Synthesis pullback metric, Coefficient seminorm metric.

**In the worked example:** With the example's synthesis S and g = (−1,−1,1), g*Hg = ‖Sg‖² = 0 although g is nonzero. This coefficient metric is singular.

**Keep in mind:** For an underlying metric Q rather than the identity, the pulled-back coefficient metric is S*QS.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md#1-redundant-analysis--synthesis-presentations) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Coefficient gauge](#coefficient-gauge) · [Seminorm](#seminorm) · [Positive semidefinite matrix](#positive-semidefinite) · [Metric adjoint](#metric-adjoint)

<a id="metric-adjoint"></a>

### Metric adjoint

The adjoint of a linear map T:X→Y for declared positive-definite Hermitian metric matrices Q_X and Q_Y. In stored coordinates it is T♯ = Q_X⁻¹T*Q_Y, where * is raw conjugate transpose. It satisfies ⟨Tx,y⟩_Y = ⟨x,T♯y⟩_X. The formula requires Q_X to be invertible.

**Also called:** Weighted adjoint, Adjoint relative to a metric.

**In the worked example:** Using the example's analysis A with source metric Q_X = A*A and target metric Q_Y = I₃ makes A♯ = (A*A)⁻¹A*, the displayed canonical synthesis S.

**Keep in mind:** A singular coefficient metric cannot be inverted by this formula. Its gauge directions require a quotient or a separately justified generalized inverse.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/K_METRICS.md#op-185) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Adjoint matrix](#adjoint) · [Positive definite matrix](#positive-definite) · [Coefficient metric](#coefficient-metric) · [Canonical dual synthesis](#canonical-dual)

<a id="covector-pullback"></a>

### Covector pullback

For a linear map A:X→Y and a covector ℓ on Y, the covector ℓA on X, defined by (ℓA)(x) = ℓ(Ax). Pullback composes an observation with the map and does not require A to be invertible. Under a coordinate change y = Cx, storing the same observation in y coordinates instead gives the row ℓC⁻¹.

**Also called:** Pullback of a linear functional.

**In the worked example:** Pulling the scalar observation ℓ(s) = 2s back along R(a,b) = a+b gives ℓR(a,b) = 2a+2b. Its row is (2,2).

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](operators/catalog/C_COORDINATES.md#op-172) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Covector](#covector) · [Composition](#composition) · [Coordinate change](#coordinate-change) · [Factorization through a map](#factorization)

<a id="compression"></a>

### Operator compression

A retained description of an operation. For a projector P and operator T, PTP acts on the retained range. For a summary R and a chosen lift S, RTS is a candidate reduced operation. Exact agreement with all original inputs requires an additional compatibility condition.

**Quick example:** For T = [[1,2],[3,4]] and P = diag(1,0), PTP retains only the upper-left entry 1.

**Keep in mind:** A compression can be useful even when the retained state does not determine its own exact future.

[Further reading](operators/TRANSFER.md) · [Coarsening](#coarsening) · [Leakage from a retained packet](#packet-leakage) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [Transfer block](#transfer-block)

<a id="isometry"></a>

### Linear isometry

A linear map preserving the specified norm of every input. Between finite inner-product spaces, preserving inner products is equivalent. In orthonormal coordinates an isometric embedding Q satisfies Q*Q = I; it need not be onto its codomain.

**Quick example:** The map x ↦ (x,0) preserves Euclidean length. Its matrix is rectangular, so it is not a unitary automorphism of R².

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Norm](#norm) · [Inner product](#inner-product) · [Unitary matrix](#unitary) · [Left inverse](#left-inverse)

<a id="algebra-homomorphism"></a>

### Algebra homomorphism

A linear map between algebras that also preserves their specified multiplication; in the unital convention it preserves the identity element. A linear coordinate isomorphism alone need not satisfy the multiplication condition.

**Quick example:** The falling-factorial map sends z² to x(x−1), while the square of its value on z is x². It therefore fails to preserve ordinary multiplication.

[Further reading](operators/POLYNOMIAL.md) · [Transported product](#transported-product) · [Coordinate change](#coordinate-change) · [Commutative ring with identity](#ring)

<a id="refinement-and-constraints"></a>

## Refinement and constraints

How descriptions become finer, discard information or meet a compatibility condition.

[Refinement](#refinement) · [Obstruction](#obstruction) · [Coarsening](#coarsening) · [Polyphase decomposition](#polyphase) · [Residue class](#residue-class) · [Compatibility](#compatibility) · [Commuting diagram](#commuting-diagram) · [Reconstruction](#reconstruction) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Lift](#lift) · [Finite conditional expectation](#conditional-expectation) · [Completion](#completion) · [Haar pair](#haar-pair) · [Detail coefficient](#detail-coefficient) · [Repair direction](#repair-direction) · [Free linear repair](#free-repair) · [Finite repair menu](#repair-menu) · [Repair selection cost](#repair-cost) · [Feasibility](#feasibility) · [Linear obstruction witness](#dual-witness) · [Admissible input set](#admissible-input) · [Exact recovery from a summary](#exact-recovery) · [Collision witness](#collision-witness) · [Partition of a set](#partition) · [Sufficient summary for a requested output](#sufficient-summary) · [Linear quotient map](#quotient-map)

<a id="refinement"></a>

### Refinement

A compatible move from a coarser description to a finer one. In finite packet refinement, each fine packet has a coarse parent and each coarse projector is the sum of its children.

**In the worked example:** The zero-based even indices split into residue classes 0 and 2 modulo 4. Their selectors satisfy P₀ = F₀ + F₂.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Coarsening](#coarsening) · [Compatibility](#compatibility) · [Residue class](#residue-class)

<a id="obstruction"></a>

### Obstruction

An identified reason a requested construction cannot meet its stated conditions. In the recovery example, two inputs have the same coarse value but require different answers, so no recovery function from that value alone exists.

**In the worked example:** The inputs (1,0) and (0,1) have the same sum but different first coordinates. No function of their sum alone can return the first coordinate for every real input.

**Keep in mind:** A nonzero numerical residual is not automatically a proof that every possible construction fails.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Residual](#residual)

<a id="coarsening"></a>

### Coarsening

Passing to a description that groups or forgets distinctions. Combining fine packets can recover a coarse packet, while discarding the fine values can prevent later reconstruction.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Refinement](#refinement) · [Obstruction](#obstruction) · [Fiber](#fiber) · [Sufficient summary for a requested output](#sufficient-summary) · [Operator compression](#compression)

<a id="polyphase"></a>

### Polyphase decomposition

For a sequence x and a positive integer m, the phase r collects samples x_(mk+r), with 0 ≤ r < m. Interleaving all phases reconstructs the indexed sequence. Filtering requires additional boundary and convention choices.

**Also called:** Polyphase splitting.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Address](#address) · [Residue class](#residue-class) · [Reconstruction](#reconstruction) · [Polyphase carry](#polyphase-carry) · [Finite impulse response filter](#finite-impulse-response-filter) · [Downsampling](#downsampling) · [Analysis filter bank](#filter-bank) · [Circular shift](#circular-shift)

<a id="residue-class"></a>

### Residue class

Integers with the same remainder modulo a positive integer m. Two integers belong to the same class when their difference is a multiple of m. Even and odd indices are the two classes modulo two.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Polyphase decomposition](#polyphase) · [Address](#address) · [Residue coefficient selector](#coefficient-selector) · [Factorial lane](#factorial-lane)

<a id="compatibility"></a>

### Compatibility

Agreement between specified maps, operations or levels of a construction. The relevant equality must be stated, such as a coarse projector equaling the sum of its fine children.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Commuting diagram](#commuting-diagram) · [Refinement](#refinement) · [Completion](#completion)

<a id="commuting-diagram"></a>

### Commuting diagram

A diagram in which the declared routes between the same starting and ending objects give the same map. In Example 3 the equality is D_y C = C D.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Composition](#composition) · [Compatibility](#compatibility) · [Intertwiner](#intertwiner)

<a id="reconstruction"></a>

### Reconstruction

Recovering an object from its representation under the stated identities. Exact reconstruction may use all packet components or a synthesis map. Dropping components generally introduces a residual.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Analysis and synthesis](#analysis-synthesis) · [Residual](#residual) · [Complete packet family](#complete-packet-family)

<a id="fiber"></a>

### Fiber

For a map R and an output s, the set of all inputs with R(x) = s. A proposed observation can be recovered from R(x) alone only if it is constant on each fiber.

**Also called:** Fibre, Preimage of a point.

**In the worked example:** For R(a,b) = a+b on R², the fiber over 1 consists of all (t,1−t) with real t. It contains both (1,0) and (0,1).

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Kernel](#kernel) · [Factorization through a map](#factorization)

<a id="factorization"></a>

### Factorization through a map

Writing one map F as G composed with another map R, so F(x) = G(R(x)). This means the intermediate value R(x) contains enough information for the requested output F(x).

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Fiber](#fiber) · [Obstruction](#obstruction) · [Composition](#composition)

<a id="lift"></a>

### Lift

An object at a finer or richer level that maps to a specified object at a coarser level. Existence, uniqueness and compatibility of lifts are separate questions.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#7-constrain) · [Refinement](#refinement) · [Compatibility](#compatibility) · [Obstruction](#obstruction)

<a id="conditional-expectation"></a>

### Finite conditional expectation

For positive weights and a finite partition, replace each value by its group’s weighted mean. The resulting map fixes group-constant vectors and is an orthogonal projector in the corresponding weighted inner product.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#averages) · [Orthogonal projector](#orthogonal-projector) · [Inner product](#inner-product) · [Coarsening](#coarsening)

<a id="completion"></a>

### Completion

A construction that adds or realizes limits or missing structure under a specified mathematical definition. There is no single universal completion operation across the collection. A finite compatible tower does not by itself construct an infinite limit.

**Keep in mind:** Mathematical completion and the editorial completion stage of a paper are different uses of the word.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#8-complete) · [Compatibility](#compatibility) · [Lift](#lift)

<a id="haar-pair"></a>

### Haar pair

A two-sample transform that separates an average and a difference. The tutorial uses a = (u+v)/2 and d = (u−v)/2, with inverse (u,v) = (a+d,a−d). Other Haar normalizations use square roots.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#haar) · [Detail coefficient](#detail-coefficient) · [Normalization](#normalization) · [Refinement](#refinement)

<a id="detail-coefficient"></a>

### Detail coefficient

In the Haar pair example, the signed half-difference d = (u−v)/2. It records the information lost when the pair is replaced by its repeated average.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#haar) · [Haar pair](#haar-pair) · [Residual](#residual)

<a id="repair-direction"></a>

### Repair direction

An allowed vector added to the span of the original image so that a required target can become reachable. Both the target equation and the permitted coefficient system must remain specified.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Image](#image) · [Span](#span) · [Finite repair menu](#repair-menu)

<a id="free-repair"></a>

### Free linear repair

A repair problem allowing freely chosen added directions over the declared field. In the rational finite-dimensional setting, the minimum added dimension is the dimension of the span of the target residual classes in the original cokernel.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Repair direction](#repair-direction) · [Cokernel](#cokernel) · [Dimension](#dimension)

<a id="repair-menu"></a>

### Finite repair menu

A supplied finite list of candidate directions, with costs and any selection restrictions. Feasibility and optimality are judged using this list and the original target equation.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Repair direction](#repair-direction) · [Repair selection cost](#repair-cost) · [Feasibility](#feasibility)

<a id="repair-cost"></a>

### Repair selection cost

The declared cost of the selected repair choices. In the tutorial it is the sum of their selection costs, paid once per choice, independently of the rational coefficients used to combine them.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Finite repair menu](#repair-menu) · [Free linear repair](#free-repair)

<a id="feasibility"></a>

### Feasibility

Existence of a solution satisfying the stated equations and admissibility conditions. Failure of one candidate or exhaustion of a search budget does not by itself show infeasibility.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Hypothesis](#hypothesis) · [Obstruction](#obstruction) · [Certificate](#certificate)

<a id="dual-witness"></a>

### Linear obstruction witness

A linear functional that annihilates every allowed direction but has a nonzero value on the required target. It proves that this target lies outside their span under the stated linear problem.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Linear map](#linear-map) · [Kernel](#kernel) · [Obstruction](#obstruction) · [Feasibility](#feasibility)

<a id="admissible-input"></a>

### Admissible input set

The declared set of inputs on which a construction or claim is required to work. Restricting this set can change fibers, recovery, and feasibility, so the input restriction belongs to the mathematical statement.

**Also called:** Admissible inputs.

**In the worked example:** The sum s=x₁+x₂ does not determine x₁ on all of R². On the restricted inputs (t,t), it does: x₁=s/2.

[Hand-worked example](operators/RECOVERY.md#2-exact-recovery-and-factorization) · [Domain and codomain](#domain-codomain) · [Hypothesis](#hypothesis) · [Fiber](#fiber) · [Exact recovery from a summary](#exact-recovery)

<a id="exact-recovery"></a>

### Exact recovery from a summary

Recovery of a requested answer F(x) by a rule G using only a summary R(x), with F=G∘R on the declared input set. Such a rule on the attained summaries exists exactly when F has the same value on every fiber of R.

**Also called:** Task-relative recovery, Summary sufficiency.

**In the worked example:** From R(x₁,x₂)=x₁+x₂, the answer H(x₁,x₂)=2x₁+2x₂ is recovered by G(s)=2s. The first coordinate alone is not recoverable on all real pairs.

**Keep in mind:** The fiber criterion establishes existence. Continuity, stability, and efficient evaluation require their own hypotheses.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](operators/RECOVERY.md#2-exact-recovery-and-factorization) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Factorization through a map](#factorization) · [Fiber](#fiber) · [Admissible input set](#admissible-input) · [Collision witness](#collision-witness)

<a id="collision-witness"></a>

### Collision witness

Two admissible inputs u,v with R(u)=R(v) but F(u)≠F(v). They prove that no function of the summary R alone recovers the requested answer F on the whole declared input set.

**Also called:** Recovery collision.

**In the worked example:** The inputs (1,0) and (0,1) have the same sum 1 but different first coordinates. For linear R and F, their difference w=(1,−1) gives Rw=0 and Fw=1.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](operators/RECOVERY.md#4-collision-and-kernel-witnesses) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Exact recovery from a summary](#exact-recovery) · [Fiber](#fiber) · [Kernel](#kernel) · [Obstruction](#obstruction)

<a id="partition"></a>

### Partition of a set

A family of nonempty, pairwise disjoint subsets whose union is the whole set. Each element lies in exactly one block. A finer partition divides coarse blocks into smaller blocks; this set-theoretic use of block is distinct from an operator matrix block.

**Quick example:** The partition {{0,2},{1,3}} groups four indices by parity. The singleton partition refines it.

[Further reading](demonstrations/REFINEMENT.md) · [Refinement](#refinement) · [Coarsening](#coarsening) · [Finite conditional expectation](#conditional-expectation) · [Bell numbers](#bell-numbers)

<a id="sufficient-summary"></a>

### Sufficient summary for a requested output

A map R that retains enough information to determine a specified output F: there is a map G on the attained summary values such that F = G∘R. Equivalently, F is constant on each fiber of R. Sufficiency is relative to the requested output and admissible inputs.

**Quick example:** R(x,y) = x+y is sufficient for F(x,y) = 2(x+y), but is insufficient for recovering x on all of R².

**Keep in mind:** This deterministic recovery definition is separate from statistical sufficiency for a family of probability laws.

[Further reading](operators/RECOVERY.md) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Exact recovery from a summary](#exact-recovery) · [Admissible input set](#admissible-input)

<a id="quotient-map"></a>

### Linear quotient map

For a vector space V and subspace K, the canonical linear map V → V/K sending x to its equivalence class x+K. Its kernel is K and it is surjective. It retains exactly the distinction between inputs differing by an element of K.

**Quick example:** Quotienting R² by span{(1,−1)} identifies all pairs with the same sum.

[Further reading](operators/RECOVERY.md) · [Quotient space](#quotient-space) · [Kernel](#kernel) · [Surjective map](#surjective) · [Factorization through a map](#factorization)

<a id="arithmetic-and-error"></a>

## Arithmetic and error

How exact values, stored approximations, and error measures differ.

[Residual](#residual) · [Exact](#exact) · [Numerical](#numerical) · [Precision](#precision) · [Dyadic rational](#dyadic-rational) · [Rounding](#rounding) · [ULP](#ulp) · [Numerical ternary](#ternary) · [Tolerance](#tolerance) · [Integer congruence](#congruence) · [Coprime integers](#coprime) · [Modular inverse](#modular-inverse) · [Chinese remainder theorem](#chinese-remainder) · [Induced operator norm](#operator-norm) · [Condition number of a coordinate map](#condition-number) · [Strong operator convergence](#strong-convergence) · [Operator norm convergence](#operator-norm-convergence) · [Hilbert–Schmidt norm](#hilbert-schmidt-norm) · [Absolute error](#absolute-error) · [Relative error](#relative-error) · [Forward error](#forward-error) · [Backward error](#backward-error) · [Interval arithmetic](#interval-arithmetic) · [Bounded linear operator](#bounded-operator)

<a id="residual"></a>

### Residual

A discrepancy computed for a specified identity or reconstruction. In Example 5 it is r = x − x̂. Other operations may use a different sign or norm, so the definition belongs with the reported number.

**In the worked example:** Dropping residue class 2 modulo 4 from (1,2,3,4,5,6,7,8) gives r = (0,0,3,0,0,0,7,0). Its squared Euclidean norm is 58.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Norm](#norm) · [Tolerance](#tolerance) · [Obstruction](#obstruction) · [Absolute error](#absolute-error) · [Forward error](#forward-error) · [Backward error](#backward-error)

<a id="exact"></a>

### Exact

Computed or stated in exact algebra or arithmetic under the declared hypotheses. Exact rational arithmetic avoids rounding of those rational values. It does not establish an unchecked modeling assumption.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Numerical](#numerical) · [Hypothesis](#hypothesis) · [Dyadic rational](#dyadic-rational)

<a id="numerical"></a>

### Numerical

Computed with finite-precision arithmetic and interpreted using a stated error or residual rule. A zero observed floating-point residual does not turn the whole computation into an exact-arithmetic proof.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Exact](#exact) · [Residual](#residual) · [Tolerance](#tolerance)

<a id="precision"></a>

### Precision

The capacity of a numerical representation. For the binary model here it is the number of significant binary digits, including the leading bit. More precision does not alone prove that an algorithm or its input is accurate.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Rounding](#rounding) · [ULP](#ulp) · [Numerical](#numerical)

<a id="dyadic-rational"></a>

### Dyadic rational

A rational number expressible as an integer divided by a power of two. These are precisely the rational numbers with a finite binary expansion, apart from representation range limits.

**Also called:** Binary rational.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Exact](#exact) · [Rounding](#rounding)

<a id="rounding"></a>

### Rounding

Choosing a representable stored value for an exact value according to a specified rule. Nearest, ties to even chooses the closer value and resolves an exact midpoint by the parity of the last retained significand bit.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Precision](#precision) · [ULP](#ulp) · [Numerical ternary](#ternary)

<a id="ulp"></a>

### ULP

A unit in the last retained place at a specified precision and exponent. In the three-bit example the spacing in [1, 2) is 1/4, while the spacing in [2, 4) is 1/2. It is not one fixed absolute distance.

**Also called:** Unit in the last place.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Precision](#precision) · [Rounding](#rounding)

<a id="ternary"></a>

### Numerical ternary

A numerical return whose sign compares the stored result with the exact value under the operation’s contract. Zero means exact, negative means below and positive means above. An error sentinel is not a numerical direction.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Rounding](#rounding) · [Exact](#exact)

<a id="tolerance"></a>

### Tolerance

A declared threshold used by a numerical acceptance rule. Its units, scaling and comparison must match the residual being checked. A residual below tolerance is evidence within that rule, not exact equality in general.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Residual](#residual) · [Norm](#norm) · [Numerical](#numerical)

<a id="congruence"></a>

### Integer congruence

The relation a ≡ b modulo m means m divides a − b, with m a positive integer. It compares residue classes, not the ordinary sizes of a and b.

**Also called:** Congruence modulo m.

**Quick example:** 17 and 2 are congruent modulo 5 because their difference 15 is divisible by 5.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#modular) · [Residue class](#residue-class) · [Modular inverse](#modular-inverse)

<a id="coprime"></a>

### Coprime integers

Integers with greatest common divisor one. Pairwise coprime moduli give independent residue coordinates in the ordinary Chinese remainder theorem.

**Also called:** Relatively prime integers.

**Quick example:** The integers 4 and 9 are coprime; 4 and 6 have common divisor 2.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#modular) · [Chinese remainder theorem](#chinese-remainder) · [Integer congruence](#congruence)

<a id="modular-inverse"></a>

### Modular inverse

An integer b with ab ≡ 1 modulo m. For m greater than one, it exists exactly when a and m are coprime. The inverse is a residue class modulo m.

**Also called:** Multiplicative inverse modulo m.

**Quick example:** The inverse of 3 modulo 7 is 5 because 3·5 = 15 is congruent to 1.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#modular) · [Integer congruence](#congruence) · [Coprime integers](#coprime)

<a id="chinese-remainder"></a>

### Chinese remainder theorem

For pairwise coprime positive moduli, a tuple of residues specifies exactly one residue class modulo their product. Selecting an integer representative requires an additional convention.

**Also called:** CRT.

**Quick example:** The requirements x ≡ 1 modulo 2 and x ≡ 2 modulo 3 give x ≡ 5 modulo 6.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#modular) · [Residue class](#residue-class) · [Coprime integers](#coprime) · [Reconstruction](#reconstruction)

<a id="operator-norm"></a>

### Induced operator norm

For a linear map between specified normed spaces with a nonzero domain, the supremum of ‖Tx‖/‖x‖ over nonzero inputs. It is the smallest uniform amplification bound when finite. The input and output norms are part of its meaning.

**Also called:** Operator norm, Induced matrix norm.

**In the worked example:** For E=[[0,2],[3,0]], the Euclidean induced norm is 3 because EᵀE=diag(9,4). Thus ‖Ex‖₂≤3‖x‖₂ for every input.

**Keep in mind:** For the zero input space, the operator norm is defined to be zero.

[Hand-worked example](operators/STABILITY.md#1-vector-norms-and-induced-operator-norms) · [Norm](#norm) · [Condition number of a coordinate map](#condition-number) · [Spectral radius](#spectral-radius)

<a id="condition-number"></a>

### Condition number of a coordinate map

For an invertible linear coordinate map C on a nonzero finite-dimensional normed space, κ(C)=‖C‖‖C⁻¹‖. It bounds how the chosen coordinate representation can amplify errors, and depends on the norms being used.

**Also called:** Condition number, Coordinate conditioning.

**Quick example:** For C = diag(1,100), κ₂(C) = 100. The map stretches one coordinate one hundred times more than the other.

**In the worked example:** C=[[1,10],[0,1]] and C⁻¹ both have infinity norm 11, so κ∞(C)=121. Conjugating diag(1,2) by C keeps its eigenvalues but changes its infinity norm from 2 to 11.

[Hand-worked example](operators/STABILITY.md#4-coordinate-conditioning) · [Coordinate change](#coordinate-change) · [Induced operator norm](#operator-norm) · [Operator conjugation](#conjugation)

<a id="strong-convergence"></a>

### Strong operator convergence

For bounded linear maps Tₘ and T between fixed normed spaces, convergence Tₘx→Tx in the output norm for every fixed input x. It does not require one error bound to tend to zero uniformly over all unit inputs.

**Also called:** Strong convergence of operators.

**In the worked example:** On ℓ², let Pₘ keep the first m coordinates. Then ‖x−Pₘx‖₂² is the tail sum of |xₖ|² and tends to zero for each fixed square-summable x.

**Keep in mind:** The square-summable sequence space ℓ² consists of sequences x for which Σₖ|xₖ|² is finite.

[Hand-worked example](operators/STABILITY.md#7-finite-truncation-and-infinite-convergence) · [Operator norm convergence](#operator-norm-convergence) · [Truncation](#truncation) · [Norm](#norm)

<a id="operator-norm-convergence"></a>

### Operator norm convergence

Convergence ‖Tₘ−T‖→0 for bounded linear maps between fixed normed spaces. It controls the error uniformly over all inputs of norm at most one, and implies strong operator convergence.

**Also called:** Norm convergence of operators.

**In the worked example:** The first-m-coordinate projectors Pₘ on ℓ² converge strongly to I, but ‖I−Pₘ‖=1 for every finite m: a unit vector beyond the retained coordinates is still completely omitted.

[Hand-worked example](operators/STABILITY.md#7-finite-truncation-and-infinite-convergence) · [Strong operator convergence](#strong-convergence) · [Induced operator norm](#operator-norm) · [Truncation](#truncation)

<a id="hilbert-schmidt-norm"></a>

### Hilbert–Schmidt norm

For a finite real or complex matrix A, the norm defined by ‖A‖HS² = tr(A*A), equal to the sum of the squared absolute values of its entries. It measures matrix size in the specified orthonormal coordinates and differs from the largest-singular-value operator norm.

**Also called:** Frobenius norm, HS norm.

**Quick example:** For diag(3,4), the Hilbert–Schmidt norm is 5, while the induced Euclidean norm is 4.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Matrix trace](#trace) · [Adjoint matrix](#adjoint) · [Induced operator norm](#operator-norm) · [Residual](#residual)

<a id="absolute-error"></a>

### Absolute error

The size of an approximation error measured in a stated norm, such as |x−x̂| for scalars or ‖x−x̂‖ for vectors. It retains the units and scale of the quantity. An acceptance threshold must use the same units and norm.

**Quick example:** Approximating 100 by 99 gives absolute error 1, while approximating 0.001 by 0 gives absolute error 0.001.

[Further reading](operators/STABILITY.md) · [Residual](#residual) · [Relative error](#relative-error) · [Tolerance](#tolerance)

<a id="relative-error"></a>

### Relative error

An absolute error divided by a specified nonzero reference size. With exact target x, a common rule is ‖x−x̂‖/‖x‖ when x ≠ 0. The reference and zero-target rule must be stated.

**Quick example:** Approximating 100 by 99 gives relative error 1/100. Approximating 0.001 by 0 gives relative error 1.

**Keep in mind:** A small absolute error can have a large relative error near zero.

[Further reading](operators/STABILITY.md) · [Absolute error](#absolute-error) · [Tolerance](#tolerance) · [Condition number of a coordinate map](#condition-number)

<a id="forward-error"></a>

### Forward error

The difference between a computed output and the exact output of the declared problem on the declared input. A forward bound controls the answer directly. It can include effects from input uncertainty, operator approximation and finite arithmetic.

**Quick example:** For the equation 2x = 6, a computed answer x̂ = 2.9 has absolute forward error 0.1.

[Further reading](operators/STABILITY.md) · [Backward error](#backward-error) · [Residual](#residual) · [Condition number of a coordinate map](#condition-number)

<a id="backward-error"></a>

### Backward error

The size of an allowed perturbation to the input data that makes the computed answer an exact solution. The data components allowed to change and their norm determine the backward-error problem. Small backward error gives a useful forward guarantee only with suitable conditioning.

**Quick example:** For 2x = 6, x̂ = 2.9 exactly solves 2x = 5.8. If only the right side may change, that perturbation has absolute size 0.2.

[Further reading](operators/STABILITY.md) · [Forward error](#forward-error) · [Condition number of a coordinate map](#condition-number) · [Residual](#residual)

<a id="interval-arithmetic"></a>

### Interval arithmetic

Arithmetic on sets represented by intervals, with operations producing intervals that contain all allowed exact outputs. Finite implementations need outward rounding. Repeated occurrences of an uncertain quantity can widen an enclosure because interval endpoints do not record all dependencies.

**Also called:** Interval enclosure arithmetic.

**Quick example:** For x in [1,2], direct interval subtraction gives x−x in [−1,1], although the expression is identically zero when both occurrences denote the same x.

[Further reading](KCOS_NUMERICAL_CERTIFICATION_AUDIT.md) · [Directed enclosure](#directed-enclosure) · [Rounding](#rounding) · [Certificate](#certificate)

<a id="bounded-operator"></a>

### Bounded linear operator

A linear map T between normed spaces for which a finite constant C satisfies ‖Tx‖ ≤ C‖x‖ for every input. Its induced norm is the least such bound. All linear maps between finite-dimensional normed spaces are bounded; infinite-dimensional cases need this hypothesis.

**Quick example:** Multiplication of every coordinate by 2 on Euclidean space is bounded with induced norm 2.

[Further reading](operators/STABILITY.md) · [Induced operator norm](#operator-norm) · [Strong operator convergence](#strong-convergence) · [Operator norm convergence](#operator-norm-convergence)

<a id="claims-and-evidence"></a>

## Claims and evidence

How to read assumptions, proofs, formal links, and computation records.

[Certificate](#certificate) · [Conditional](#conditional) · [Lean correspondence](#lean-correspondence) · [Hypothesis](#hypothesis) · [Theorem](#theorem) · [Proof](#proof) · [Heuristic](#heuristic) · [Finite check](#finite-check) · [Finite proof field](#proof-field) · [Admissible leaf](#admissible-leaf) · [Recorded inference rule](#inference-rule) · [Verification closure](#verification-closure) · [Inclusion-minimal certificate](#inclusion-minimal) · [Least certificate](#least-certificate) · [Minimum-cost certificate](#minimum-cost-certificate) · [Derivation trace](#derivation-trace) · [Shared premise](#shared-premise) · [Counterexample](#counterexample) · [Necessary condition](#necessary-condition) · [Sufficient condition](#sufficient-condition) · [Inconclusive search](#search-inconclusive) · [Formal statement](#formal-statement) · [Reproducible computation](#reproducibility)

<a id="certificate"></a>

### Certificate

A structured report describing a particular check, with its evidence class, residuals, and assumptions. The producer determines what was checked. A saved certificate describes a past calculation and needs revalidation for a new one.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Exact](#exact) · [Numerical](#numerical) · [Conditional](#conditional) · [Derivation trace](#derivation-trace) · [Inconclusive search](#search-inconclusive)

<a id="conditional"></a>

### Conditional

A result that retains explicitly listed assumptions. In a computation record, some of those assumptions may not have been established by the computation. Passing its checks does not discharge them.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Hypothesis](#hypothesis) · [Certificate](#certificate) · [Completion](#completion)

<a id="lean-correspondence"></a>

### Lean correspondence

A recorded connection between a written claim and a formal Lean statement. Compare hypotheses, the full formal type, source edition, and execution record. A similar declaration name or a working link alone does not establish the correspondence.

[Further reading](COMPLETION_STATUS.md#lean-coverage) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Proof](#proof) · [Theorem](#theorem) · [Certificate](#certificate)

<a id="hypothesis"></a>

### Hypothesis

An assumption required by a statement or construction. It may describe the space, arithmetic, domain, regularity or supplied data. A conclusion applies only where its hypotheses hold.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](VERIFICATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#averages) · [Conditional](#conditional) · [Theorem](#theorem) · [Certificate](#certificate) · [Necessary condition](#necessary-condition) · [Sufficient condition](#sufficient-condition)

<a id="theorem"></a>

### Theorem

A mathematical statement established by a proof from its specified assumptions. A theorem may be conditional on explicit hypotheses, even when the implication itself is fully proved.

[Further reading](VERIFICATION.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Hypothesis](#hypothesis) · [Proof](#proof) · [Conditional](#conditional)

<a id="proof"></a>

### Proof

An argument establishing a statement from its hypotheses and accepted prior results. A worked input illustrates a statement. A general identity or argument is needed to establish a claim about every allowed input.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](VERIFICATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Theorem](#theorem) · [Finite check](#finite-check) · [Lean correspondence](#lean-correspondence)

<a id="heuristic"></a>

### Heuristic

A method for discovery, search or estimation without a complete guarantee for the claimed outcome. Its suggestions can lead to later proofs or checks, but the suggestions alone do not establish them.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Proof](#proof) · [Finite check](#finite-check)

<a id="finite-check"></a>

### Finite check

A check over specified, finitely many inputs or cases. Exhaustive checking can prove a claim about that finite domain. Sampling a larger domain does not establish the universal claim without an additional argument.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](VERIFICATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Proof](#proof) · [Certificate](#certificate) · [Hypothesis](#hypothesis)

<a id="proof-field"></a>

### Finite proof field

A declared finite collection of claim nodes, admissible leaves, and recorded inference rules. Certificate validity is relative to this supplied system.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Recorded inference rule](#inference-rule) · [Admissible leaf](#admissible-leaf) · [Certificate](#certificate)

<a id="admissible-leaf"></a>

### Admissible leaf

A node allowed as a starting point under the declared proof-field contract. Selecting such a leaf does not require deriving it again inside that certificate.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Finite proof field](#proof-field) · [Hypothesis](#hypothesis)

<a id="inference-rule"></a>

### Recorded inference rule

A specified set of premise nodes together with a conclusion node. The certificate can use the rule only when the required premises have been derived and its recorded certification permits it.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Finite proof field](#proof-field) · [Verification closure](#verification-closure)

<a id="verification-closure"></a>

### Verification closure

The nodes obtainable by admitting selected admissible leaves and repeatedly applying the retained certified rules whose premises are available.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Admissible leaf](#admissible-leaf) · [Recorded inference rule](#inference-rule) · [Certificate](#certificate)

<a id="inclusion-minimal"></a>

### Inclusion-minimal certificate

A valid node-and-rule certificate with no valid strictly smaller subcertificate under componentwise inclusion. Several incomparable minimal certificates can exist.

**In the worked example:** The certificate built from leaves s₁ and s₃ derives a, b, c and d, then the target t. Removing either selected leaf or any of its five retained rules breaks that derivation, so this certificate is inclusion-minimal.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Certificate](#certificate) · [Least certificate](#least-certificate) · [Minimum-cost certificate](#minimum-cost-certificate)

<a id="least-certificate"></a>

### Least certificate

A certificate contained componentwise in every certificate for the same request and rule system. This is stronger than being inclusion-minimal or having minimum numerical cost.

**In the worked example:** The two optimal certificates start from {s₁,s₃} and {s₂,s₄}. Their intersection contains no admissible leaf. With no mandatory starting leaves, it cannot derive t, so there is no least certificate in this rule system.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Inclusion-minimal certificate](#inclusion-minimal) · [Minimum-cost certificate](#minimum-cost-certificate)

<a id="minimum-cost-certificate"></a>

### Minimum-cost certificate

A valid certificate attaining the lowest declared total cost among the permitted certificates. Costs count selected items according to the supplied rule, so a shared premise need not be charged each time it is used.

**In the worked example:** Each selected leaf costs one and supplies two of four required obligations. Either pair {s₁,s₃} or {s₂,s₄} reaches the target at cost two, while zero or one leaf cannot. Reusing a selected leaf for two consequences does not double its cost.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Certificate](#certificate) · [Least certificate](#least-certificate) · [Finite proof field](#proof-field)

<a id="derivation-trace"></a>

### Derivation trace

A recorded sequence of inference steps showing how admitted leaves and previously established conclusions reach a target. Each step must cite an allowed rule with all its premises available. Checking a trace establishes its validity within the declared rule system.

**Also called:** Proof trace.

**Quick example:** Admit s₁ and s₃, derive a,b,c,d using their recorded rules, then apply {a,b,c,d} ⇒ t.

**Keep in mind:** A valid trace in a supplied proof field does not establish the soundness of arbitrary externally supplied rules.

[Further reading](examples/21_PROOF_CERTIFICATES.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Recorded inference rule](#inference-rule) · [Admissible leaf](#admissible-leaf) · [Certificate](#certificate) · [Verification closure](#verification-closure)

<a id="shared-premise"></a>

### Shared premise

An established node used by more than one later inference. Sharing allows a derivation to be represented as a directed acyclic graph instead of copying the whole premise derivation into each branch. Costs depend on whether reused nodes are charged once or once per use.

**Also called:** Proof sharing.

**Quick example:** In the certificate example, s₁ supplies both a and b but its selected-leaf cost is charged only once.

[Further reading](examples/21_PROOF_CERTIFICATES.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Derivation trace](#derivation-trace) · [Minimum-cost certificate](#minimum-cost-certificate) · [Recorded inference rule](#inference-rule)

<a id="counterexample"></a>

### Counterexample

An admissible instance on which a claimed universal conclusion fails. A counterexample must satisfy the claim’s hypotheses. For a recovery claim, two admissible inputs with the same summary and different requested outputs provide a collision counterexample.

**Quick example:** The pairs (1,0) and (0,1) have the same sum and different first coordinates, disproving recovery of the first coordinate from the sum alone.

[Further reading](demonstrations/RECOVERY.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Hypothesis](#hypothesis) · [Collision witness](#collision-witness) · [Proof](#proof) · [Obstruction](#obstruction)

<a id="necessary-condition"></a>

### Necessary condition

A condition that must hold whenever a requested property holds. If A implies B, then B is necessary for A. Failing B rules out A, but passing B alone need not establish A.

**Quick example:** Equal reflection magnitude is necessary for cyclic reachability on the Smith chart. A prescribed finite rotation order also restricts the phase.

[Further reading](demonstrations/SMITH_CHART.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Sufficient condition](#sufficient-condition) · [Obstruction](#obstruction) · [Feasibility](#feasibility)

<a id="sufficient-condition"></a>

### Sufficient condition

A condition that guarantees the requested property. If A implies B, then A is sufficient for B. The same implication makes B necessary for A. An equivalence provides both directions.

**Quick example:** For linear F and R on a common vector space, ker R contained in ker F is sufficient for recovering F from R on the whole space.

[Further reading](operators/RECOVERY.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Necessary condition](#necessary-condition) · [Exact recovery from a summary](#exact-recovery) · [Kernel](#kernel)

<a id="search-inconclusive"></a>

### Inconclusive search

A search that has established neither a valid witness nor a proof that none exists within the specified problem. A timeout, an exhausted budget or rejection of one proposed certificate can leave the existence question unresolved.

**Also called:** UNKNOWN, Search timeout, Unresolved search.

**Quick example:** Rejecting the one-leaf proposal {s₁} leaves the valid two-leaf certificate {s₁,s₃} available.

[Further reading](examples/21_PROOF_CERTIFICATES.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Certificate](#certificate) · [Feasibility](#feasibility) · [Finite check](#finite-check) · [Counterexample](#counterexample)

<a id="formal-statement"></a>

### Formal statement

A proposition expressed in a proof assistant’s language with explicit types, hypotheses and conclusion. Its relationship to a written theorem depends on the interpretation of every object and assumption. A declaration name alone does not specify that relationship.

**Quick example:** A declaration proving a finite matrix identity covers that identity under its encoded hypotheses; it does not automatically cover an infinite-dimensional analogue.

[Further reading](routes/PROOF_REVIEW.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Lean correspondence](#lean-correspondence) · [Hypothesis](#hypothesis) · [Proof](#proof)

<a id="reproducibility"></a>

### Reproducible computation

A computation with enough recorded inputs, source identity, environment information and instructions to repeat the stated check. Reproduction should compare the promised outputs or invariants. Repeating a calculation preserves the scope of the calculation rather than extending it.

**Quick example:** A source archive, its hash, the arithmetic convention and the expected rational output let another reader replay one exact example.

[Further reading](routes/PROOF_REVIEW.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Certificate](#certificate) · [Finite check](#finite-check) · [Exact](#exact) · [Numerical](#numerical)

<a id="series-and-functions"></a>

## Series and cyclic functions

Coefficient operations and the distinction between a finite truncation and an infinite series.

[Coefficient](#coefficient) · [Power series](#power-series) · [Truncation](#truncation) · [Formal reciprocal](#formal-reciprocal) · [Coefficient convolution](#convolution) · [Root of unity](#root-of-unity) · [Derivative in the series example](#derivative) · [Differential equation](#differential-equation) · [Initial condition](#initial-condition) · [Contracted argument](#contracted-argument) · [Coefficient recurrence](#coefficient-recurrence) · [Falling factorial](#falling-factorial) · [Forward difference](#forward-difference) · [Residue coefficient selector](#coefficient-selector) · [Polynomial translation operator](#translation-operator) · [Newton coefficient formula](#newton-coefficients) · [Ordinary generating function](#ordinary-generating-function) · [Exponential generating function](#exponential-generating-function) · [Binomial coefficient convolution](#binomial-convolution) · [Stirling numbers of the second kind](#stirling-second-kind) · [Signed Stirling numbers of the first kind](#stirling-first-kind) · [Stirling transform](#stirling-transform) · [Bell numbers](#bell-numbers) · [Fubini numbers](#fubini-numbers) · [Touchard polynomial](#touchard-polynomial) · [Roots-of-unity filter](#roots-of-unity-filter) · [Factorial lane](#factorial-lane) · [Generalized hypergeometric series](#hypergeometric-series) · [Signed Euler numbers](#signed-euler-numbers) · [Secant numbers](#secant-numbers) · [Formal series composition](#formal-composition) · [Compositional inverse of a formal series](#compositional-inverse) · [Polynomial degree](#polynomial-degree) · [Monic polynomial](#monic-polynomial) · [Rising factorial](#rising-factorial) · [Cauchy product](#cauchy-product) · [Formal power series](#formal-power-series) · [Radius of convergence](#radius-of-convergence) · [Taylor coefficient](#taylor-coefficient) · [Backward difference](#backward-difference)

<a id="coefficient"></a>

### Coefficient

The scalar multiplying a specified basis term. In f(z) = sum aₙzⁿ, aₙ is the coefficient of zⁿ.

**Quick example:** In 2+5x+3x², the coefficient of x is 5; in a different basis the coefficient list changes.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Scalar](#scalar) · [Basis](#basis) · [Newton coefficient formula](#newton-coefficients) · [Ordinary generating function](#ordinary-generating-function)

<a id="power-series"></a>

### Power series

An expression sum aₙzⁿ with infinitely many coefficient positions. A formal power series is manipulated through its coefficients. Evaluating it at a number additionally requires convergence.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Coefficient](#coefficient) · [Truncation](#truncation) · [Ordinary generating function](#ordinary-generating-function) · [Exponential generating function](#exponential-generating-function) · [Formal series composition](#formal-composition) · [Formal power series](#formal-power-series) · [Radius of convergence](#radius-of-convergence)

<a id="truncation"></a>

### Truncation

Keeping only specified degrees or levels. Equality modulo zᴺ means the coefficients of degrees below N agree. It need not be equality of the full functions or series.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Power series](#power-series) · [Residual](#residual)

<a id="formal-reciprocal"></a>

### Formal reciprocal

For a power series over a field with nonzero constant coefficient, the unique series whose product with it is one. Its coefficients are determined recursively. A finite truncation only verifies the corresponding finite set of coefficient identities.

**Also called:** Multiplicative inverse of a formal series.

**Quick example:** The formal reciprocal of 1−z is 1+z+z²+⋯ because their Cauchy product is 1.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Power series](#power-series) · [Coefficient convolution](#convolution) · [Field](#field) · [Compositional inverse of a formal series](#compositional-inverse)

<a id="convolution"></a>

### Coefficient convolution

The multiplication rule cₙ = sum from k=0 to n of aₖbₙ₋ₖ for ordinary power series. Each output coefficient is a finite sum, even when the series are infinite.

**Also called:** Cauchy product.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Coefficient](#coefficient) · [Power series](#power-series) · [Binomial coefficient convolution](#binomial-convolution)

<a id="root-of-unity"></a>

### Root of unity

A complex number ω with ωᴺ = 1 for a positive integer N. It is primitive when N is its least positive such exponent. A weighted average over the powers of a primitive Nth root selects coefficients in one residue class modulo N.

**Quick example:** The number i has exact order 4: i⁴ = 1, and no smaller positive power equals 1.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Residue class](#residue-class) · [Packet](#packet) · [Roots-of-unity filter](#roots-of-unity-filter) · [Residue coefficient selector](#coefficient-selector) · [Cyclic reachability](#cyclic-reachability)

<a id="derivative"></a>

### Derivative in the series example

For n≥1, differentiating a power-series term aₙzⁿ gives n aₙzⁿ⁻¹. Constant terms differentiate to zero. Formal differentiation acts on coefficients. An analytic interpretation uses the function’s convergence and differentiability conditions.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Coefficient](#coefficient) · [Power series](#power-series) · [Taylor coefficient](#taylor-coefficient)

<a id="differential-equation"></a>

### Differential equation

An equation relating an unknown function to one or more of its derivatives. The example also evaluates the same function at contracted arguments qz and rz.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Derivative in the series example](#derivative) · [Initial condition](#initial-condition) · [Contracted argument](#contracted-argument)

<a id="initial-condition"></a>

### Initial condition

A specified value, or collection of derivative values, used with a differential equation. The feedback example fixes T(0)=0, and the equation then forces T′(0)=1.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Differential equation](#differential-equation) · [Derivative in the series example](#derivative)

<a id="contracted-argument"></a>

### Contracted argument

Evaluation at qz with 0<q<1 in the feedback example. A term cₙzⁿ becomes cₙqⁿzⁿ after this substitution. The scaling is inside the defining equation.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Coefficient](#coefficient) · [Differential equation](#differential-equation)

<a id="coefficient-recurrence"></a>

### Coefficient recurrence

A rule determining successive series coefficients from earlier ones. It gives exact finite calculations at each degree. Analytic convergence and bounds for a discarded tail require additional arguments.

**Also called:** Recurrence for coefficients.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Coefficient](#coefficient) · [Truncation](#truncation) · [Coefficient convolution](#convolution)

<a id="falling-factorial"></a>

### Falling factorial

The polynomial b₀(x)=1 and bₖ(x)=x(x−1)⋯(x−k+1) for k≥1. These monic polynomials form a basis of the polynomial space. Falling degree records the basis index k, which need not match an ordinary-power packet after expansion.

**Also called:** Falling-factorial polynomial.

**In the worked example:** b₃(x)=x³−3x²+2x, while x³=b₁(x)+3b₂(x)+b₃(x). The map Φ(zᵏ)=bₖ therefore has Φ⁻¹(x³)=z+3z²+z³.

[Hand-worked example](operators/POLYNOMIAL.md#1-falling-factorial-coordinates) · [Basis](#basis) · [Forward difference](#forward-difference) · [Residue coefficient selector](#coefficient-selector) · [Newton coefficient formula](#newton-coefficients) · [Rising factorial](#rising-factorial) · [Monic polynomial](#monic-polynomial)

<a id="forward-difference"></a>

### Forward difference

The operator Δf(x)=f(x+1)−f(x). On rational polynomials, Δbₖ=k bₖ₋₁ for the falling-factorial basis and Δb₀=0. Under Φ(zᵏ)=bₖ, this is the transported source derivative: Δ=ΦD_zΦ⁻¹.

**Also called:** Unit forward difference, Delta operator in the polynomial example.

**In the worked example:** For f(x)=x³, Δf(x)=3x²+3x+1. Ordinary differentiation in x instead gives 3x², so the coordinate transport matters.

[Hand-worked example](operators/POLYNOMIAL.md#2-forward-difference-as-a-transported-derivative) · [Falling factorial](#falling-factorial) · [Derivative in the series example](#derivative) · [Polynomial translation operator](#translation-operator) · [Transported product](#transported-product)

<a id="coefficient-selector"></a>

### Residue coefficient selector

For an integer m≥2 and 0≤r<m, the projector Pᵣ retaining exactly the coefficients whose basis degree k satisfies k≡r modulo m. The basis is part of the definition. In falling-factorial coordinates the corresponding projector is Qᵣ=ΦPᵣΦ⁻¹.

**Also called:** Coefficient selector, Residue projector.

**In the worked example:** For x³=b₁+3b₂+b₃, the even falling-degree packet is 3b₂ and the odd packet is b₁+b₃. At x=4 their values are 36 and 28, summing to 64.

**Keep in mind:** Coefficient selection is defined over any commutative ring. Over a field, its roots-of-unity averaging formula requires a primitive mth root and invertible m.

[Hand-worked example](operators/POLYNOMIAL.md#5-transported-projectors-and-a-complete-packet-calculation) · [Further reading](operators/POLYNOMIAL.md#4-coefficient-selectors-and-roots-of-unity-averaging) · [Projector](#projector) · [Residue class](#residue-class) · [Falling factorial](#falling-factorial) · [Root of unity](#root-of-unity) · [Roots-of-unity filter](#roots-of-unity-filter)

<a id="translation-operator"></a>

### Polynomial translation operator

For a specified scalar shift h, the operator T_h f(x)=f(x+h). Over rational polynomials it is linear, with T₀=I and T_hT_k=T_{h+k}. In falling-factorial coordinates, a unit shift satisfies T₁=I+Δ.

**Also called:** Translation operator, Polynomial shift operator.

**In the worked example:** For f=x³ and the even falling-degree projector Q₀, Q₀T₁f(4)=73 while T₁Q₀f(4)=60. Both orders translate the total correctly after all packets are added, but the individual packets differ.

[Hand-worked example](operators/POLYNOMIAL.md#7-translation-carries-information-between-packets) · [Forward difference](#forward-difference) · [Falling factorial](#falling-factorial) · [Transfer block](#transfer-block) · [Commutator](#commutator)

<a id="newton-coefficients"></a>

### Newton coefficient formula

For f=Σₖaₖbₖ in the falling-factorial basis over Q, the coefficient is aₖ=Δᵏf(0)/k!. Repeated forward differences lower the basis index, and evaluation at zero isolates the matching coefficient.

**Also called:** Newton coefficients, Finite-difference coefficient recovery.

**In the worked example:** The samples of x³ at 0,1,2,3 are 0,1,8,27. The first entries of successive difference rows are 0,1,6,6. Dividing by 0!,1!,2!,3! yields the coefficients 0,1,3,1.

**Keep in mind:** This division formula requires the factorial denominators to be invertible. The integral Stirling basis change remains invertible over any commutative ring, even where this sampling formula fails.

[Hand-worked example](operators/POLYNOMIAL.md#8-recover-coordinates-and-check-the-coefficient-ring) · [Coefficient](#coefficient) · [Falling factorial](#falling-factorial) · [Forward difference](#forward-difference) · [Field](#field)

<a id="ordinary-generating-function"></a>

### Ordinary generating function

The formal series A(z) = Σₙ≥₀ aₙzⁿ used to store a sequence (aₙ). The coefficient of zⁿ is aₙ itself. This convention determines the multiplication rule and differs from factorial normalization.

**Also called:** OGF.

**In the worked example:** The reciprocal of 1+z+z² is (1−z)/(1−z³), with ordinary coefficient pattern 1, −1, 0, 1, −1, 0, ….

**Keep in mind:** Formal coefficient identities do not by themselves justify evaluating the series outside its convergence region.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Power series](#power-series) · [Coefficient](#coefficient) · [Exponential generating function](#exponential-generating-function) · [Coefficient convolution](#convolution)

<a id="exponential-generating-function"></a>

### Exponential generating function

The formal series A(t) = Σₙ≥₀ aₙtⁿ/n! over a coefficient field of characteristic zero. The sequence entry aₙ is the coefficient in the basis tⁿ/n!, while the ordinary coefficient of tⁿ is aₙ/n!.

**Also called:** EGF.

**In the worked example:** The Bell numbers have EGF exp(eᵗ−1). Its degree-five term is 52t⁵/5!, because B₅ = 52.

**Keep in mind:** The Euler demonstration uses the compressed index n for degree 2n. Its secant denominator is (2n)!, not n!.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Ordinary generating function](#ordinary-generating-function) · [Binomial coefficient convolution](#binomial-convolution) · [Normalization](#normalization) · [Coefficient](#coefficient)

<a id="binomial-convolution"></a>

### Binomial coefficient convolution

The product rule for exponentially normalized series: if A(t) = Σ aₙtⁿ/n! and B(t) = Σ bₙtⁿ/n!, their product has coefficient cₙ = Σₖ₌₀ⁿ binom(n,k)aₖbₙ₋ₖ in that same basis.

**Also called:** Binomial convolution, Exponential coefficient convolution.

**In the worked example:** In the secant recurrence, the degree-four row is s₂ = 6s₁ − s₀ = 5. The factor 6 is binom(4,2).

[Hand-worked example](demonstrations/EULER_PACKETS.md) · [Coefficient convolution](#convolution) · [Exponential generating function](#exponential-generating-function) · [Normalization](#normalization)

<a id="stirling-second-kind"></a>

### Stirling numbers of the second kind

The integers S(n,k) counting partitions of an n-element labelled set into k nonempty, unlabelled blocks. For n ≥ 1 they satisfy S(n,k) = S(n−1,k−1) + kS(n−1,k), with S(0,0) = 1 and zero outside 0 ≤ k ≤ n.

**Also called:** Stirling partition numbers.

**Quick example:** S(3,2) = 3: the singleton can be any of the three labels, with the other two in the second block.

**In the worked example:** The row at n = 5 is (0,1,15,25,10,1). In particular, S(5,3) = 7+3·6 = 25.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling transform](#stirling-transform) · [Bell numbers](#bell-numbers) · [Fubini numbers](#fubini-numbers) · [Falling factorial](#falling-factorial)

<a id="stirling-first-kind"></a>

### Signed Stirling numbers of the first kind

The coefficients s(n,k) in x(x−1)⋯(x−n+1) = Σₖ₌₀ⁿ s(n,k)xᵏ. Their lower-triangular matrix is the inverse of the second-kind Stirling matrix. The sign is part of this convention.

**Also called:** Signed first-kind Stirling numbers.

**In the worked example:** The n = 5 coefficient row is (0,24,−50,35,−10,1). Applied to (F₀,…,F₅), it gives 24−150+455−750+541 = 120 = 5!.

**Keep in mind:** Unsigned first-kind Stirling numbers count permutations by cycles and remove these alternating signs. They are not the inverse matrix used here.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Stirling transform](#stirling-transform) · [Inverse](#inverse) · [Falling factorial](#falling-factorial)

<a id="stirling-transform"></a>

### Stirling transform

The triangular sequence map cₙ = Σₖ₌₀ⁿ S(n,k)aₖ. Each output uses finitely many input entries. Signed first-kind Stirling numbers invert the full triangular map, and the EGF form is C(t) = A(eᵗ−1).

**In the worked example:** Weights aₖ = 1 produce Bell numbers. Weights aₖ = k! produce Fubini numbers through the same matrix.

**Keep in mind:** Recovering an input sequence from all preceding output values is different from recovering an arbitrary partition row from a single row sum.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Signed Stirling numbers of the first kind](#stirling-first-kind) · [Formal series composition](#formal-composition) · [Inverse](#inverse)

<a id="bell-numbers"></a>

### Bell numbers

The integers Bₙ counting all partitions of an n-element labelled set into nonempty, unlabelled blocks. Equivalently Bₙ = Σₖ₌₀ⁿ S(n,k), with B₀ = 1.

**Quick example:** B₃ = 1+3+1 = 5, summing S(3,1), S(3,2) and S(3,3).

**In the worked example:** Adding the n = 5 Stirling row gives B₅ = 1+15+25+10+1 = 52.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Fubini numbers](#fubini-numbers) · [Touchard polynomial](#touchard-polynomial)

<a id="fubini-numbers"></a>

### Fubini numbers

The integers Fₙ counting partitions of an n-element labelled set whose blocks are linearly ordered. A partition with k blocks has k! possible block orders, so Fₙ = Σₖ₌₀ⁿ k!S(n,k), with F₀ = 1.

**Also called:** Ordered Bell numbers.

**Quick example:** F₃ = 1!·1+2!·3+3!·1 = 13.

**In the worked example:** F₅ = 1·1!+15·2!+25·3!+10·4!+1·5! = 541. The EGF is 1/(2−eᵗ).

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Bell numbers](#bell-numbers) · [Formal reciprocal](#formal-reciprocal)

<a id="touchard-polynomial"></a>

### Touchard polynomial

The polynomial Tₙ(z) = Σₖ₌₀ⁿ S(n,k)zᵏ retaining the complete partition row as coefficients. Evaluation at z = 1 gives Bₙ. Applying the functional zᵏ ↦ k! gives Fₙ.

**Also called:** Bell polynomial of one variable.

**Quick example:** T₃(z) = z+3z²+z³. Its value at 1 is B₃ = 5.

**In the worked example:** T₅(z) = z+15z²+25z³+10z⁴+z⁵. Its value at 1 is 52, while ∫₀∞ e⁻ᵘT₅(u) du = 541.

**Keep in mind:** The one-variable Touchard family is distinct from the multivariable partial Bell polynomials, which encode a different set of inputs.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Bell numbers](#bell-numbers) · [Fubini numbers](#fubini-numbers)

<a id="roots-of-unity-filter"></a>

### Roots-of-unity filter

For m ≥ 2 and 0 ≤ r < m, work over a field containing a primitive mth root ζ and in which m is invertible. The operator Pᵣf(z) = (1/m)Σₗ₌₀ᵐ⁻¹ ζ⁻ʳˡf(ζˡz) selects precisely the monomials whose degrees are congruent to r modulo m. The polynomial identity also applies coefficientwise to formal series.

**Also called:** Character filter, Residue-degree projector.

**In the worked example:** On a monomial zᵏ, the multiplier (1/m)Σₗ ζˡ⁽ᵏ⁻ʳ⁾ equals one when k ≡ r modulo m and zero otherwise.

**Keep in mind:** The coefficient selector itself does not require roots of unity. This averaging formula needs both the stated root and division by m. A different polynomial basis requires transporting the projector through its basis change.

[Hand-worked example](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md) · [Root of unity](#root-of-unity) · [Residue class](#residue-class) · [Projector](#projector) · [Refinement](#refinement) · [Residue coefficient selector](#coefficient-selector)

<a id="factorial-lane"></a>

### Factorial lane

For integers N ≥ 1 and n ≥ 0, a product of n factors in one arithmetic progression: (a)ₙ;N = ∏ₖ₌₀ⁿ⁻¹(a+Nk), with empty product one. Splitting the factors of a factorial into disjoint residue lanes gives an exact product decomposition.

**Also called:** Step factorial, Arithmetic-progression product.

**In the worked example:** The lane starting at 5 with step 10 and three factors is 5·15·25 = 1875. Taking three factors in each of the ten lanes starting at 5 through 14, multiplying the lanes, then multiplying by 4!, reconstructs 34!.

**Keep in mind:** A multiplicative lane of factors and an additive residue section of a series are different objects. The factorial demonstration explicitly relates them.

[Hand-worked example](demonstrations/FACTORIAL_LANES.md) · [Residue class](#residue-class) · [Generalized hypergeometric series](#hypergeometric-series) · [Normalization](#normalization)

<a id="hypergeometric-series"></a>

### Generalized hypergeometric series

The coefficient-defined series ₚF_q(a₁,…,aₚ; b₁,…,b_q; z) = Σₙ≥₀ [(a₁)ₙ⋯(aₚ)ₙ/((b₁)ₙ⋯(b_q)ₙ)]zⁿ/n!, where (a)ₙ = a(a+1)⋯(a+n−1). The denominator factors must be defined and nonzero for the terms being used.

**Also called:** Hypergeometric series.

**In the worked example:** The identity (r)ₙ;10 = 10ⁿ(r/10)ₙ converts the selected exponential section into a ₀F₉ series. The parameter r/10 = 1 supplies the separate n! factor.

**Keep in mind:** The displayed identity is coefficientwise. Analytic convergence depends on the parameters and the argument. Terminating cases also require the appropriate denominator conditions.

[Hand-worked example](demonstrations/FACTORIAL_LANES.md) · [Factorial lane](#factorial-lane) · [Power series](#power-series) · [Coefficient recurrence](#coefficient-recurrence)

<a id="signed-euler-numbers"></a>

### Signed Euler numbers

In the Euler demonstration, the sequence Eⱼ is defined by sech(t) = Σⱼ≥₀ Eⱼtʲ/j!. Odd entries vanish and even entries alternate in sign. The sign and index convention must be fixed before comparing Euler tables.

**Also called:** Euler numbers in the sech convention.

**In the worked example:** E₀ = 1, E₂ = −1, E₄ = 5 and E₆ = −61. The sequence a(n) = E₂ₙ has a(1) = −1, although E₁ = 0.

[Hand-worked example](demonstrations/EULER_PACKETS.md) · [Secant numbers](#secant-numbers) · [Exponential generating function](#exponential-generating-function) · [Formal reciprocal](#formal-reciprocal)

<a id="secant-numbers"></a>

### Secant numbers

The positive coefficients sₙ defined by sec(t) = Σₙ≥₀ sₙt²ⁿ/(2n)!. Their compressed index n refers to ordinary degree 2n. In the signed sech convention, E₂ₙ = (−1)ⁿsₙ.

**Also called:** Positive Euler secant numbers.

**In the worked example:** The first values are 1, 1, 5, 61, 1385, 50521 and 2702765. Thus s₆ = 2702765 is the coefficient of t¹²/12!, not t⁶/6!.

[Hand-worked example](demonstrations/EULER_PACKETS.md) · [Signed Euler numbers](#signed-euler-numbers) · [Binomial coefficient convolution](#binomial-convolution) · [Formal reciprocal](#formal-reciprocal)

<a id="formal-composition"></a>

### Formal series composition

Substitution A(u(t)) of one formal series into another. If u has zero constant term, each output coefficient receives only finitely many contributions, so an arbitrary formal A can be composed without an analytic convergence assumption.

**Also called:** Formal substitution.

**In the worked example:** Substituting u(t) = eᵗ−1 into the weight EGF A(u) gives the transformed EGF C(t) = A(eᵗ−1).

**Keep in mind:** If A is a polynomial, substitution is also a finite operation without the zero-constant-term condition. General infinite outer series need a valid formal or analytic setting.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Power series](#power-series) · [Compositional inverse of a formal series](#compositional-inverse) · [Stirling transform](#stirling-transform)

<a id="compositional-inverse"></a>

### Compositional inverse of a formal series

For a formal series u(t) over a field with u(0) = 0 and nonzero linear coefficient, the unique series v(t) with v(0) = 0 satisfying u(v(t)) = t and v(u(t)) = t. The inverse concerns substitution.

**Also called:** Series reversion, Formal inverse under substitution.

**Quick example:** The substitution inverse of u(t) = 2t is v(t) = t/2. Their product is not the identity being tested.

**In the worked example:** The compositional inverse of eᵗ−1 is log(1+t). Consequently C(t) = A(eᵗ−1) is inverted by A(u) = C(log(1+u)).

**Keep in mind:** A formal reciprocal solves u(t)v(t) = 1 and requires a nonzero constant coefficient. These are different inverse operations with different hypotheses.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Formal series composition](#formal-composition) · [Formal reciprocal](#formal-reciprocal) · [Inverse](#inverse)

<a id="polynomial-degree"></a>

### Polynomial degree

For a nonzero polynomial, the largest exponent having a nonzero coefficient. Over a field, degrees add under multiplication of nonzero polynomials. The zero polynomial needs a separate convention, often degree −∞, when degree formulas include it.

**Also called:** Degree of a polynomial.

**Quick example:** The polynomial 4−2x+3x³ has degree 3. A falling-factorial basis element b₃ also has ordinary degree 3.

[Further reading](operators/POLYNOMIAL.md) · [Coefficient](#coefficient) · [Falling factorial](#falling-factorial) · [Truncation](#truncation)

<a id="monic-polynomial"></a>

### Monic polynomial

A nonzero polynomial whose highest-degree coefficient is one. A sequence with one monic polynomial of each degree gives an invertible triangular change from ordinary powers on every finite degree range.

**Quick example:** x(x−1)(x−2) = x³−3x²+2x is monic. The constant polynomial 1 is monic of degree zero.

[Further reading](operators/POLYNOMIAL.md) · [Polynomial degree](#polynomial-degree) · [Basis](#basis) · [Falling factorial](#falling-factorial)

<a id="rising-factorial"></a>

### Rising factorial

The finite product (a)ₙ = a(a+1)⋯(a+n−1), with (a)₀ = 1. This is the Pochhammer convention used in the hypergeometric series entry. The notation must be distinguished from falling factorials and from the step-N factorial lanes.

**Also called:** Pochhammer symbol.

**Quick example:** (2)₃ = 2·3·4 = 24, while the falling factorial 2(2−1)(2−2) is zero.

[Further reading](demonstrations/FACTORIAL_LANES.md) · [Falling factorial](#falling-factorial) · [Factorial lane](#factorial-lane) · [Generalized hypergeometric series](#hypergeometric-series)

<a id="cauchy-product"></a>

### Cauchy product

The coefficient rule for multiplying ordinary formal power series: the coefficient of zⁿ in A(z)B(z) is Σₖ₌₀ⁿ aₖbₙ₋ₖ. Each coefficient uses finitely many terms, so this formal rule needs no analytic convergence assumption.

**Quick example:** The coefficient of z² in (1+2z+3z²)(1+4z+5z²) is 5+8+3 = 16.

[Further reading](demonstrations/EULER_PACKETS.md) · [Coefficient convolution](#convolution) · [Binomial coefficient convolution](#binomial-convolution) · [Ordinary generating function](#ordinary-generating-function)

<a id="formal-power-series"></a>

### Formal power series

An infinite coefficient list written as Σₙ≥₀ aₙzⁿ and manipulated coefficientwise over a declared ring. Addition and multiplication are algebraic operations on these lists. Evaluating the series at a numerical z is a separate analytic question.

**Also called:** Formal series.

**Quick example:** The identity (1−z)(1+z+z²+⋯) = 1 is valid formally even when no numerical value for z is chosen.

[Further reading](demonstrations/EULER_PACKETS.md) · [Power series](#power-series) · [Formal reciprocal](#formal-reciprocal) · [Formal series composition](#formal-composition) · [Truncation](#truncation)

<a id="radius-of-convergence"></a>

### Radius of convergence

For a complex power series centered at zero, the radius R such that the series converges absolutely for |z| < R and diverges for |z| > R. The endpoints R = 0 and R = ∞ are allowed. Boundary convergence must be checked separately.

**Quick example:** The geometric series Σₙ≥₀ zⁿ has radius 1. At z = 1 its terms do not tend to zero.

[Further reading](demonstrations/EULER_PACKETS.md) · [Power series](#power-series) · [Formal power series](#formal-power-series) · [Truncation](#truncation)

<a id="taylor-coefficient"></a>

### Taylor coefficient

For a function analytic near zero, the ordinary coefficient of zⁿ in its Taylor series is f⁽ⁿ⁾(0)/n!. Its exponentially normalized coefficient is f⁽ⁿ⁾(0). The basis convention determines which number is called the stored coefficient.

**Quick example:** For exp(z), every derivative at zero is 1, while its ordinary coefficients are 1, 1, 1/2, 1/6, ….

[Further reading](demonstrations/EULER_PACKETS.md) · [Coefficient](#coefficient) · [Derivative in the series example](#derivative) · [Exponential generating function](#exponential-generating-function)

<a id="backward-difference"></a>

### Backward difference

The polynomial operator ∇f(x) = f(x)−f(x−1), with unit step. It differs from the forward difference Δf(x) = f(x+1)−f(x). The falling-degree operator is x∇, while the falling-factorial lowering operator is Δ.

**Quick example:** For f(x) = x², ∇f = 2x−1 and Δf = 2x+1.

[Further reading](operators/POLYNOMIAL.md) · [Forward difference](#forward-difference) · [Falling-degree operator](#degree-operator) · [Polynomial translation operator](#translation-operator)

<a id="signal-and-spectral-evaluation"></a>

## Signals and spectral evaluation

Finite transforms, phase carries, Gaussian quadratic forms and the distinct error controls used in K-COS.

[Finite impulse response filter](#finite-impulse-response-filter) · [Polyphase carry](#polyphase-carry) · [Discrete Fourier transform](#discrete-fourier-transform) · [Discrete cosine transform](#discrete-cosine-transform) · [Gram operator](#gram-operator) · [Range core](#range-core) · [Characteristic function](#characteristic-function) · [Gaussian quadratic form](#gaussian-quadratic-form) · [COS method](#cos-method) · [Centered spectral packet](#centered-spectral-packet) · [Directed enclosure](#directed-enclosure) · [Analytic error budget](#analytic-error-budget) · [Circular shift](#circular-shift) · [Downsampling](#downsampling) · [Aliasing](#aliasing) · [Analysis filter bank](#filter-bank) · [Wavelet lifting step](#lifting-step) · [Parseval identity in chosen coordinates](#parseval-identity) · [Signal boundary convention](#boundary-condition)

<a id="finite-impulse-response-filter"></a>

### Finite impulse response filter

A linear filter given by finitely many taps, or coefficients, applied to specified shifts of a signal. In a causal convention yₙ = Σₗ₌₀ᴸ⁻¹ hₗxₙ₋ₗ. A finite signal also needs a boundary rule, such as zero extension or circular indexing.

**Also called:** FIR, FIR filter, Finite convolution filter.

**In the worked example:** On the sixteen-sample circular signal, H = I+2T−T² gives (Hx)₁₀ = 12+2(−4)−(−4) = 8.

**Keep in mind:** The worked wavelet example uses circular indexing. The catalog’s causal FIR entry uses zero extension. The transfer formula must retain the chosen boundary convention.

[Hand-worked example](demonstrations/WAVELET_POLYPHASE.md) · [Further reading](operators/catalog/E_SIGNAL.md#op-081) · [Polyphase decomposition](#polyphase) · [Polyphase carry](#polyphase-carry) · [Linear map](#linear-map) · [Composition](#composition)

<a id="polyphase-carry"></a>

### Polyphase carry

The extra shift in a phase coordinate required when an index crosses a residue boundary. Splitting a signal into residue phases changes both the phase label and, when necessary, the position within that phase.

**Also called:** Lane-boundary carry, Phase carry.

**In the worked example:** For even and odd rows E and O, one backward circular shift sends the even output to ZO and the odd output to E. Its two-phase matrix is [[0,Z],[I,0]], with Z the half-rate delay.

**Keep in mind:** Forward shifts place the carry in a different block from backward shifts. Its position follows from the index convention.

[Hand-worked example](demonstrations/WAVELET_POLYPHASE.md) · [Polyphase decomposition](#polyphase) · [Finite impulse response filter](#finite-impulse-response-filter) · [Transfer block](#transfer-block) · [Residue class](#residue-class)

<a id="discrete-fourier-transform"></a>

### Discrete Fourier transform

For a complex vector x of length N ≥ 1, the convention used here is x̂ₖ = Σₙ₌₀ᴺ⁻¹ xₙ exp(−2πikn/N). The inverse uses the positive exponential sign and divides by N.

**Also called:** DFT, Finite Fourier transform.

**Keep in mind:** A different normalization may distribute the factor 1/N between the two maps. Changing conventions changes their matrix entries.

[Further reading](operators/catalog/E_SIGNAL.md#op-090) · [Root of unity](#root-of-unity) · [Coordinates](#coordinates) · [Normalization](#normalization) · [Discrete cosine transform](#discrete-cosine-transform)

<a id="discrete-cosine-transform"></a>

### Discrete cosine transform

A coordinate transform of a real vector of length N ≥ 1 using cosine samples. The catalog fixes orthonormal DCT-II: yₖ = αₖΣₙ₌₀ᴺ⁻¹xₙ cos(π(n+1/2)k/N), where α₀ = 1/√N and αₖ = √(2/N) for k > 0.

**Also called:** DCT, DCT-II.

**Keep in mind:** DCT type and normalization are part of the definition. The COS probability method uses a Fourier-cosine expansion but is not simply this finite data transform.

[Further reading](operators/catalog/E_SIGNAL.md#op-091) · [Discrete Fourier transform](#discrete-fourier-transform) · [Orthogonal matrix](#orthogonal-matrix) · [Normalization](#normalization) · [COS method](#cos-method)

<a id="gram-operator"></a>

### Gram operator

For a real matrix A, either K = AAᵀ on its output space or H = AᵀA on its input space. Both are positive semidefinite. Their positive eigenvalues agree with multiplicity, although their dimensions and zero-eigenvalue multiplicities can differ.

**Also called:** Gram matrix, Sample Gram, Feature Gram.

**Keep in mind:** For a column partition A = [A₁ … A_B], the exact identity AAᵀ = Σ_b A_bA_bᵀ retains every column. Dropping a block changes the operator.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/01_gaussian.tex#L39) · [Positive semidefinite matrix](#positive-semidefinite) · [Eigenvalue](#eigenvalue) · [Range core](#range-core) · [Gaussian quadratic form](#gaussian-quadratic-form) · [Classical frame operator](#classical-frame-operator)

<a id="range-core"></a>

### Range core

A representation of a real factor A in coordinates on a chosen subspace. If Q has orthonormal columns and the range of A is contained in the range of Q, then B = QᵀA gives A = QB. The matrices BBᵀ and AAᵀ have the same nonzero spectrum, including multiplicity. The core is smaller when Q has fewer columns than A has rows.

**Also called:** Exact range core, Range compression.

**Keep in mind:** If the chosen subspace misses part of the range, the omitted residual requires a separate bound. A floating-point rank threshold does not establish exact range capture.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/04_range.tex#L127) · [Gram operator](#gram-operator) · [Image](#image) · [Orthogonal projector](#orthogonal-projector) · [Residual](#residual)

<a id="characteristic-function"></a>

### Characteristic function

For a real random variable Q, φ(t) = E[exp(itQ)] at real frequency t. It encodes the probability law in Fourier coordinates. Unlike a real moment-generating function, it is defined for every real t because the integrand has modulus one.

**Also called:** Probability characteristic function, CF.

**Keep in mind:** For an admissible exponential tilt with cumulant generator κ, the monograph uses φθ(t) = exp(κ(θ+it)−κ(θ)). The domain and logarithm branch are stated with that transform.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/06_packets.tex#L73) · [COS method](#cos-method) · [Gaussian quadratic form](#gaussian-quadratic-form) · [Complex conjugate](#complex-conjugate)

<a id="gaussian-quadratic-form"></a>

### Gaussian quadratic form

A random variable Q = XᵀMX with real Gaussian vector X and symmetric matrix M. In the central positive case X has mean zero and covariance Σ, M is positive semidefinite, and Q has the same law as ΣⱼλⱼZⱼ² for independent standard normal Zⱼ and eigenvalues λⱼ of Σ¹ᐟ²MΣ¹ᐟ².

**Also called:** Quadratic form of a Gaussian vector.

**Keep in mind:** The zero-mean assumption gives the central reduction. Positive semidefiniteness makes the eigenvalues nonnegative and the law supported on [0,∞), as required by the positive-tail formula. A central indefinite form has the same reduction with signed eigenvalues. Noncentral forms require their additional parameters. With no nonzero eigenvalues, Q is identically zero.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/01_gaussian.tex#L9) · [Finite-dimensional Gaussian model](#gaussian-model) · [Covariance matrix](#covariance) · [Eigenvalue](#eigenvalue) · [Characteristic function](#characteristic-function)

<a id="cos-method"></a>

### COS method

A Fourier-cosine method for evaluating distributional quantities from characteristic-function values. K-COS applies this representation to Gaussian quadratic-form tails, with a stated window, retained mode count, spectral approximation and error bounds.

**Also called:** Fourier-cosine method.

**Keep in mind:** The positive-tail formula uses frequencies kπ/b on [0,b] and half weight on the zero mode. A finite sum is an approximation until the applicable remainders and numerical arithmetic have been controlled.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/07_inversion.tex#L1) · [Characteristic function](#characteristic-function) · [Gaussian quadratic form](#gaussian-quadratic-form) · [Centered spectral packet](#centered-spectral-packet) · [Analytic error budget](#analytic-error-budget)

<a id="centered-spectral-packet"></a>

### Centered spectral packet

In K-COS, a nonempty group P of eigenvalues represented by its count n, mean μ and centered power sums Mₘ = Σⱼ∈P(λⱼ−μ)ᵐ. Thus M₀ = n and M₁ = 0. Truncated transform expansions also carry a remainder bound.

**Also called:** Spectral packet, Centered packet.

**Keep in mind:** The expansion needs |2s/(1−2sμ)|·maxⱼ|λⱼ−μ| < 1 on the frequencies and tilt being used. Nearby eigenvalues alone do not establish that condition for every query.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/06_packets.tex#L94) · [Packet](#packet) · [Eigenvalue](#eigenvalue) · [COS method](#cos-method) · [Analytic error budget](#analytic-error-budget)

<a id="directed-enclosure"></a>

### Directed enclosure

An interval guaranteed to contain the specified exact quantity. Its finite arithmetic rounds outward, and its final endpoints include every required analytic remainder. The claim concerns the encoded inputs and stated mathematical model.

**Also called:** Outward-rounded enclosure, Probability enclosure.

**Keep in mind:** For a probability interval [p₋,p₊], the stated relative acceptance test requires p₋ > 0 and p₊/p₋−1 ≤ ε. A narrow interval is insufficient if a required source of error was omitted.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/09_intervals.tex#L1) · [Certificate](#certificate) · [Rounding](#rounding) · [Analytic error budget](#analytic-error-budget) · [Tolerance](#tolerance)

<a id="analytic-error-budget"></a>

### Analytic error budget

A sum of justified bounds for the approximation steps in a mathematical model. The K-COS budget separates spectral-packet approximation, support and cosine-folding error, and omitted Fourier modes.

**Also called:** Packet-support-mode budget.

**Keep in mind:** These real or complex arithmetic bounds do not automatically enclose floating-point rounding. A numerical certificate must also account for its finite arithmetic and exact-input interpretation.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/07_inversion.tex#L1) · [Centered spectral packet](#centered-spectral-packet) · [Truncation](#truncation) · [Directed enclosure](#directed-enclosure) · [Residual](#residual)

<a id="circular-shift"></a>

### Circular shift

A shift of a finite length-N signal with indices reduced modulo N. Under the convention (Sx)ₙ = xₙ₋₁ mod N, the last sample moves to the first position. This boundary rule differs from zero extension.

**Also called:** Cyclic shift, Periodic delay.

**Quick example:** The circular delay sends (1,2,3,4) to (4,1,2,3).

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Finite impulse response filter](#finite-impulse-response-filter) · [Polyphase carry](#polyphase-carry) · [Discrete Fourier transform](#discrete-fourier-transform)

<a id="downsampling"></a>

### Downsampling

Retaining samples on a specified residue class: with factor m and phase r, yₖ = xₘₖ₊ᵣ. The phase and boundary convention are part of the operation. Retaining only one phase generally loses information about the others.

**Also called:** Decimation.

**Quick example:** Taking the even phase of (1,2,3,4) gives (1,3). Retaining the odd phase (2,4) as well permits interleaving back to the original signal.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Polyphase decomposition](#polyphase) · [Aliasing](#aliasing) · [Reconstruction](#reconstruction)

<a id="aliasing"></a>

### Aliasing

Failure of a sampling operation to distinguish different inputs. In frequency language, distinct oscillations can produce the same retained samples. Additional input restrictions or complementary filter-bank outputs are needed for exact recovery.

**Quick example:** On integer indices, the signals 1 and (−1)ⁿ both give the constant sequence 1 after retaining only even-indexed samples.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Downsampling](#downsampling) · [Collision witness](#collision-witness) · [Exact recovery from a summary](#exact-recovery)

<a id="filter-bank"></a>

### Analysis filter bank

A collection of filters and sampling maps sending one signal to several component streams. A synthesis bank combines those streams into an output signal. Perfect reconstruction is a property of the combined analysis and synthesis maps with their declared delays and boundary conventions.

**Quick example:** For a pair (u,v), the Haar analysis stores average (u+v)/2 and detail (u−v)/2; synthesis returns their sum and difference.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Analysis and synthesis](#analysis-synthesis) · [Downsampling](#downsampling) · [Polyphase decomposition](#polyphase) · [Finite impulse response filter](#finite-impulse-response-filter)

<a id="lifting-step"></a>

### Wavelet lifting step

An invertible update of one component using another, such as predicting odd samples from even samples and then updating the even stream with the prediction residual. The inverse undoes the updates in reverse order. This signal-processing meaning of lifting differs from lifting an object through a quotient.

**Quick example:** Set d = v−u, then a = u+d/2. Recover u = a−d/2 and v = u+d.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Analysis filter bank](#filter-bank) · [Haar pair](#haar-pair) · [Inverse](#inverse) · [Lift](#lift)

<a id="parseval-identity"></a>

### Parseval identity in chosen coordinates

An equality between the squared norm of an object and the correctly weighted squared magnitudes of its complete transform coefficients. Orthonormal coordinates use unit weights. Other normalizations change the weights, so energy formulas must follow the analysis convention.

**Quick example:** With a = (u+v)/2 and d = (u−v)/2, u²+v² = 2(a²+d²). The factor 2 belongs to this normalization.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Orthonormal basis](#orthonormal-basis) · [Coefficient metric](#coefficient-metric) · [Normalization](#normalization)

<a id="boundary-condition"></a>

### Signal boundary convention

A rule supplying samples outside the stored finite signal, such as periodic continuation, zero extension or reflection. A filter’s taps do not determine its finite matrix until this rule and the indexing convention have been fixed.

**Also called:** Zero extension, Periodic boundary.

**Quick example:** Delaying (1,2,3,4) by one sample gives (0,1,2,3) with zero extension and (4,1,2,3) with circular indexing.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Finite impulse response filter](#finite-impulse-response-filter) · [Circular shift](#circular-shift) · [Compatibility](#compatibility)

<a id="smith-chart-and-synthesis"></a>

## Smith chart and circuit synthesis

Impedance, reflection, cyclic reachability and the distinction between interpolation and a circuit realization.

[Impedance](#impedance) · [Normalized impedance](#normalized-impedance) · [Admittance](#admittance) · [Reflection coefficient](#reflection-coefficient) · [Impedance Cayley transform](#cayley-transform) · [Matched load](#matched-load) · [Voltage standing-wave ratio](#vswr) · [Return loss](#return-loss) · [Lossless transmission line](#lossless-line) · [Cyclic reachability](#cyclic-reachability) · [Pole of a rational function](#pole) · [Rational function](#rational-function) · [Positive-real impedance function](#positive-real-function) · [Scalar Schur function](#schur-function) · [Interpolation](#interpolation) · [Pick matrix](#pick-matrix) · [Singular block range condition](#singular-range-condition) · [Scalar McMillan degree](#mcmillan-degree) · [Circuit realization](#circuit-realization)

<a id="impedance"></a>

### Impedance

The complex voltage-to-current ratio of a linear one-port at a stated frequency, written Z = R+iX. Its real part is resistance and its imaginary part is reactance. The Smith-chart guide uses a positive real reference resistance Z₀ and normalized impedance z = Z/Z₀.

**Quick example:** The load Z = 25+i25 ohms with Z₀ = 50 ohms has normalized impedance z = (1+i)/2.

[Further reading](demonstrations/SMITH_CHART.md) · [Normalized impedance](#normalized-impedance) · [Admittance](#admittance) · [Reflection coefficient](#reflection-coefficient)

<a id="normalized-impedance"></a>

### Normalized impedance

The dimensionless ratio z = Z/Z₀ relative to a declared reference impedance. In the Smith-chart guide Z₀ is positive and real, so the real and imaginary parts are normalized resistance and reactance.

**Quick example:** Changing Z₀ from 50 to 25 ohms changes the coordinates of a 50-ohm resistor from z = 1 to z = 2, while the physical resistor stays the same.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance](#impedance) · [Normalization](#normalization) · [Reflection coefficient](#reflection-coefficient)

<a id="admittance"></a>

### Admittance

The reciprocal Y = 1/Z where Z is nonzero, measured in siemens. With normalized impedance z, normalized admittance is y = 1/z. Switching to the admittance grid changes the description of the same load.

**Quick example:** If z = (1+i)/2, then y = 1−i.

**Keep in mind:** A short has zero impedance and no finite reciprocal admittance.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance](#impedance) · [Normalized impedance](#normalized-impedance) · [Impedance Cayley transform](#cayley-transform)

<a id="reflection-coefficient"></a>

### Reflection coefficient

For normalized impedance z with z ≠ −1, the Smith coordinate Γ = (z−1)/(z+1). For finite passive loads with nonnegative resistance, |Γ| ≤ 1. Its magnitude measures mismatch relative to the declared positive real reference resistance.

**Also called:** Gamma, Load reflection coefficient.

**Quick example:** For z = (1+i)/2, Γ = (−1+2i)/5 and |Γ|² = 1/5.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance Cayley transform](#cayley-transform) · [Impedance](#impedance) · [Matched load](#matched-load) · [Voltage standing-wave ratio](#vswr)

<a id="cayley-transform"></a>

### Impedance Cayley transform

The fractional-linear coordinate map Γ = (z−1)/(z+1) and its inverse z = (1+Γ)/(1−Γ), on their stated domains. It takes the open positive-real half-plane to the open unit disk and finite purely reactive impedances to its boundary.

**Quick example:** The matched point z = 1 maps to Γ = 0. The point Γ = 1 has no finite impedance under the inverse formula.

**Keep in mind:** Other literature uses different Cayley-transform conventions. Keep this direction and reference normalization explicit.

[Further reading](demonstrations/SMITH_CHART.md) · [Reflection coefficient](#reflection-coefficient) · [Normalized impedance](#normalized-impedance) · [Pole of a rational function](#pole)

<a id="matched-load"></a>

### Matched load

A load with impedance equal to the chosen reference resistance in this real-reference model. Its normalized impedance is z = 1 and its reflection coefficient is zero. Matching is relative to the reference and frequency being used.

**Quick example:** A 50-ohm resistor is matched to a 50-ohm real reference and gives VSWR 1.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance](#impedance) · [Reflection coefficient](#reflection-coefficient) · [Return loss](#return-loss)

<a id="vswr"></a>

### Voltage standing-wave ratio

For reflection magnitude r with 0 ≤ r < 1, VSWR = (1+r)/(1−r). The matched case gives one; as r approaches one the ratio diverges. The ideal passive boundary is assigned infinite VSWR.

**Also called:** VSWR, Standing-wave ratio, SWR.

**Quick example:** Reflection magnitude 1/3 gives VSWR 2.

[Further reading](demonstrations/SMITH_CHART.md) · [Reflection coefficient](#reflection-coefficient) · [Matched load](#matched-load) · [Return loss](#return-loss)

<a id="return-loss"></a>

### Return loss

For 0 < |Γ| ≤ 1, the quantity −20 log₁₀|Γ| in decibels. Smaller reflected magnitude gives larger return loss. The matched limit |Γ| = 0 has ideal infinite return loss; the passive boundary |Γ| = 1 gives zero decibels.

**Also called:** RL.

**Quick example:** For |Γ| = 1/√5, return loss is 10 log₁₀5, approximately 6.99 decibels.

[Further reading](demonstrations/SMITH_CHART.md) · [Reflection coefficient](#reflection-coefficient) · [Voltage standing-wave ratio](#vswr) · [Matched load](#matched-load)

<a id="lossless-line"></a>

### Lossless transmission line

In the guide’s propagation convention, a line of length ℓ gives Γin = ΓL exp(−4πiℓ/λ) at wavelength λ. It rotates the reflection point while preserving its magnitude. This is a physical line model with its own length and reference assumptions.

**Quick example:** A quarter wavelength multiplies Γ by −1 and sends a finite nonzero normalized load z to 1/z.

**Keep in mind:** Line rotation alone cannot turn a nonzero reflection magnitude into a matched load.

[Further reading](demonstrations/SMITH_CHART.md) · [Reflection coefficient](#reflection-coefficient) · [Cyclic reachability](#cyclic-reachability) · [Matched load](#matched-load)

<a id="cyclic-reachability"></a>

### Cyclic reachability

Reachability by a fixed finite set of phase rotations Γ ↦ ωᴷΓ, where ω = exp(2πi/N), N > 0 and K is an integer. For Γ₀ ≠ 0, a target Γ* is reachable exactly when (Γ*/Γ₀)ᴺ = 1. The zero start reaches only zero.

**Quick example:** For N = 4, the orbit of Γ₀ = 1/2 is {1/2,i/2,−1/2,−i/2}. A point at angle π/4 with radius 1/2 is outside this orbit.

[Further reading](demonstrations/SMITH_CHART.md) · [Root of unity](#root-of-unity) · [Necessary condition](#necessary-condition) · [Lossless transmission line](#lossless-line) · [Feasibility](#feasibility)

<a id="pole"></a>

### Pole of a rational function

A point where a rational function has a nonremovable singularity after common factors are cancelled. A zero in a displayed denominator is only a candidate until cancellation is considered. Individual terms in a decomposition can have poles that cancel in their sum.

**Quick example:** The function 1/(1−t) has a pole at t = 1. By contrast, (1−t)/(1−t) extends to the constant 1 after cancellation.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance Cayley transform](#cayley-transform) · [Rational function](#rational-function) · [Packet](#packet)

<a id="rational-function"></a>

### Rational function

A quotient of polynomials over a declared field, understood with common factors cancelled when studying its poles or degree. In circuit work the variable is often complex frequency s. Frequency samples alone do not determine an arbitrary rational function without further constraints.

**Quick example:** The one-inductor example has normalized impedance z(s) = (7s+5)/(2s+4).

[Further reading](demonstrations/SMITH_FIRST_ORDER_RL.md) · [Pole of a rational function](#pole) · [Scalar McMillan degree](#mcmillan-degree) · [Interpolation](#interpolation)

<a id="positive-real-function"></a>

### Positive-real impedance function

In the real-rational scalar circuit setting, a rational function Z(s) analytic for Re s > 0 and satisfying Re Z(s) ≥ 0 there. Real coefficients give the usual conjugation symmetry. Boundary poles and realization restrictions require their stated additional conditions.

**Also called:** Positive-real function, PR function.

**Quick example:** For positive R and L, the series RL function Z(s) = R+sL has positive real part throughout Re s > 0.

**Keep in mind:** Checking finitely many frequency samples is insufficient to establish positivity on the whole half-plane.

[Further reading](demonstrations/SMITH_FIRST_ORDER_RL.md) · [Rational function](#rational-function) · [Scalar Schur function](#schur-function) · [Circuit realization](#circuit-realization)

<a id="schur-function"></a>

### Scalar Schur function

A complex analytic function F on the open unit disk satisfying |F(t)| ≤ 1 throughout that disk. The Smith-chart research uses such reflection functions for interpolation. A rational Schur function has a finite rational description, with its degree and boundary behavior still to be specified.

**Quick example:** F(t) = t is a Schur function. It realizes the sample values 1/2 at t = 1/2 and −1/2 at t = −1/2.

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Positive-real impedance function](#positive-real-function) · [Pick matrix](#pick-matrix) · [Impedance Cayley transform](#cayley-transform)

<a id="interpolation"></a>

### Interpolation

Finding a function in a declared class that takes prescribed values at prescribed nodes. Feasibility, uniqueness and the range of possible unmeasured values are separate questions. A fit in an unrestricted polynomial class need not satisfy the analytic or passive constraints of a circuit model.

**Quick example:** The data F(1/2) = 1/2 and F(−1/2) = −1/2 admit F(t) = t in the Schur class.

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Scalar Schur function](#schur-function) · [Pick matrix](#pick-matrix) · [Identifiability relative to a model class](#identifiability)

<a id="pick-matrix"></a>

### Pick matrix

For distinct disk nodes tₖ and proposed scalar values vₖ, the Hermitian matrix Pₖₗ = (1−vₖ conjugate(vₗ))/(1−tₖ conjugate(tₗ)). Its positive semidefiniteness is the classical scalar Schur interpolation criterion used in the linked reading.

**Quick example:** The nodes 1/2 and −1/2 with equal respective values give P = [[1,1],[1,1]], a rank-one singular matrix.

**Keep in mind:** The nodes are distinct and strictly inside the disk. This criterion is not a component-count theorem for a restricted circuit topology.

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Interpolation](#interpolation) · [Scalar Schur function](#schur-function) · [Positive semidefinite matrix](#positive-semidefinite) · [Singular block range condition](#singular-range-condition)

<a id="singular-range-condition"></a>

### Singular block range condition

For Hermitian P ≥ 0, the block matrix [[P,b],[b*,d]] is positive semidefinite exactly when b is perpendicular to ker P and d ≥ b*P†b. Here P† is the Moore–Penrose inverse. The range condition remains essential when P is singular.

**Quick example:** If P = 0, its range is {0}. Positivity of the augmented block forces b = 0 as well as d ≥ 0.

**Keep in mind:** Substituting a pseudoinverse into the scalar inequality while omitting the range condition is insufficient.

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Pick matrix](#pick-matrix) · [Moore–Penrose inverse](#pseudoinverse) · [Schur complement](#schur-complement) · [Kernel](#kernel)

<a id="mcmillan-degree"></a>

### Scalar McMillan degree

For a proper scalar rational transfer function p(s)/q(s) in lowest terms, the degree of q. It counts the minimal state dimension of an unrestricted finite linear realization. Improper functions and restricted passive circuit component counts need their own conventions.

**Quick example:** The proper function (7s+5)/(2s+4) has no common numerator-denominator factor and has McMillan degree one.

**Keep in mind:** A minimal state dimension does not alone give the minimum number of reactive elements in a transformer-free network.

[Further reading](demonstrations/SMITH_FIRST_ORDER_RL.md) · [Rational function](#rational-function) · [Circuit realization](#circuit-realization) · [Finite linear state-space realization](#state-space-realization)

<a id="circuit-realization"></a>

### Circuit realization

A network built from the allowed components whose driving-point impedance or transfer function equals the specified function on its stated domain. The component alphabet, positivity rules and permitted transformers determine the realization problem.

**Quick example:** The linked one-inductor example uses a series resistor 5/4 followed by a parallel resistor 9/4 and inductor 9/8 in normalized units.

**Keep in mind:** An approximation by a lower-degree function is a realization of the approximating function. It does not establish an exact lower-component realization of the target.

[Further reading](demonstrations/SMITH_FIRST_ORDER_RL.md) · [Positive-real impedance function](#positive-real-function) · [Scalar McMillan degree](#mcmillan-degree) · [Realization](#realization)

<a id="finite-quantum"></a>

## Finite quantum systems

States, measurement and channels on finite complex vector spaces.

[Complex conjugate](#complex-conjugate) · [Adjoint matrix](#adjoint) · [Unitary matrix](#unitary) · [Quantum amplitude](#amplitude) · [Density matrix](#density-matrix) · [Matrix trace](#trace) · [Born probability](#born-probability) · [Purity of a density matrix](#purity) · [Dephasing](#dephasing) · [Kraus operators](#kraus-operator) · [Hermitian matrix](#hermitian) · [Positive semidefinite matrix](#positive-semidefinite) · [Coherence in a chosen basis](#coherence) · [Qubit](#qubit) · [Global phase](#global-phase) · [Relative phase](#relative-phase) · [Pure quantum state](#pure-state) · [Mixed quantum state](#mixed-state) · [Quantum measurement effect](#quantum-effect) · [Quantum observable](#observable) · [Quantum channel](#quantum-channel) · [Quantum state tomography](#quantum-tomography) · [Selective projective measurement](#selective-measurement)

<a id="complex-conjugate"></a>

### Complex conjugate

For real a and b, the conjugate of a+bi is a−bi. The squared modulus is (a+bi)(a−bi) = a²+b².

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Inner product](#inner-product) · [Scalar](#scalar)

<a id="adjoint"></a>

### Adjoint matrix

For a complex matrix in orthonormal bases, the adjoint A* is its conjugate transpose. In real orthonormal bases this is the ordinary transpose.

**Also called:** Conjugate transpose, Hermitian transpose.

**Quick example:** The adjoint of [[1,i],[0,2]] is [[1,0],[−i,2]]. Both transposition and conjugation are required.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Complex conjugate](#complex-conjugate) · [Inner product](#inner-product) · [Metric adjoint](#metric-adjoint)

<a id="unitary"></a>

### Unitary matrix

A complex square matrix U with U*U = UU* = I. It preserves the complex inner product and therefore vector norms.

**Quick example:** diag(1,i) is unitary because its adjoint diag(1,−i) is its inverse.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Norm](#norm) · [Orthogonal matrix](#orthogonal-matrix)

<a id="amplitude"></a>

### Quantum amplitude

A complex coordinate of a normalized state vector in a chosen orthonormal basis. Its squared modulus gives that basis outcome’s probability. Relative phases can affect measurements in other bases.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Complex conjugate](#complex-conjugate) · [Born probability](#born-probability) · [Coordinates](#coordinates) · [Qubit](#qubit) · [Relative phase](#relative-phase)

<a id="density-matrix"></a>

### Density matrix

A positive semidefinite Hermitian matrix with trace one. A normalized vector ψ gives the pure-state matrix ρ = ψψ*. Different vectors that differ only by an overall complex phase give the same density matrix.

**Also called:** Density operator.

**In the worked example:** The normalized vector ψ = (3/5,4i/5)ᵀ gives ρ = ψψ*. Its diagonal entries are 9/25 and 16/25, its upper-right entry is −12i/25, and its lower-left entry is 12i/25. Its trace is one.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Matrix trace](#trace) · [Purity of a density matrix](#purity)

<a id="trace"></a>

### Matrix trace

The sum of diagonal entries of a square matrix. It is unchanged by an invertible change of basis. Field trace is a related arithmetic construction with its own definition.

**Quick example:** The trace of [[1,2],[3,4]] is 1+4 = 5.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Matrix](#matrix) · [Field trace](#field-trace)

<a id="born-probability"></a>

### Born probability

For a density matrix ρ and an orthogonal measurement projector P, the outcome probability is tr(Pρ). A complete orthogonal projector family gives probabilities summing to one.

**In the worked example:** For ψ = (3/5,4i/5)ᵀ and ρ = ψψ*, the coordinate projectors P₀ = diag(1,0) and P₁ = diag(0,1) give tr(P₀ρ) = 9/25 and tr(P₁ρ) = 16/25. These probabilities sum to one.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Matrix trace](#trace) · [Orthogonal projector](#orthogonal-projector)

<a id="purity"></a>

### Purity of a density matrix

The number tr(ρ²). For a finite density matrix it equals one exactly for a pure state and is smaller for a mixed state.

**In the worked example:** For ρ = ψψ* with ψ = (3/5,4i/5)ᵀ, tr(ρ²) = 1. After coordinate dephasing, the purity is (9/25)² + (16/25)² = 337/625, which is less than one.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Matrix trace](#trace) · [Pure quantum state](#pure-state) · [Mixed quantum state](#mixed-state)

<a id="dephasing"></a>

### Dephasing

For a specified complete orthogonal family Pᵢ, the channel ρ ↦ sum PᵢρPᵢ removes coherence between different selected subspaces. Its effect depends on the chosen decomposition.

**In the worked example:** The coordinate measurement with its outcome forgotten sends the example’s ρ to P₀ρP₀ + P₁ρP₁ = diag(9/25,16/25). The off-diagonal terms disappear while the two coordinate probabilities remain unchanged.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Projector](#projector) · [Kraus operators](#kraus-operator) · [Quantum channel](#quantum-channel) · [Selective projective measurement](#selective-measurement)

<a id="kraus-operator"></a>

### Kraus operators

Matrices Kᵢ describing a finite quantum channel by Φ(ρ) = sum KᵢρKᵢ*. The condition sum Kᵢ*Kᵢ = I makes this map trace preserving.

**Also called:** Kraus representation.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Density matrix](#density-matrix) · [Matrix trace](#trace)

<a id="hermitian"></a>

### Hermitian matrix

A complex square matrix A with A* = A. Its diagonal entries are real and opposite off-diagonal entries are complex conjugates. This condition alone does not imply positivity.

**Also called:** Self-adjoint matrix.

**Quick example:** The matrix [[1,i],[−i,2]] is Hermitian because conjugating and transposing returns it.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Positive semidefinite matrix](#positive-semidefinite)

<a id="positive-semidefinite"></a>

### Positive semidefinite matrix

A Hermitian matrix A for which v*Av is nonnegative for every vector v. Zero eigenvalues are allowed.

**Also called:** PSD, PSD matrix.

**Quick example:** [[1,1],[1,1]] is positive semidefinite because its quadratic form is |x+y|², and it has a nonzero kernel.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Hermitian matrix](#hermitian) · [Eigenvalue](#eigenvalue) · [Density matrix](#density-matrix) · [Positive definite matrix](#positive-definite) · [Gram operator](#gram-operator) · [Pick matrix](#pick-matrix) · [Quadratic form](#quadratic-form)

<a id="coherence"></a>

### Coherence in a chosen basis

Off-diagonal density-matrix entries that encode relations between different basis components. They can contribute to probabilities after a change of measurement basis.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Dephasing](#dephasing) · [Quantum amplitude](#amplitude)

<a id="qubit"></a>

### Qubit

A quantum system with a two-dimensional complex state space. A pure state has a unit-vector representative α|0⟩+β|1⟩ with |α|²+|β|² = 1; multiplying both amplitudes by one global phase leaves the same density matrix. Mixed states use density matrices.

**Quick example:** The vector (3/5,4/5) is normalized because 9/25+16/25 = 1.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Quantum amplitude](#amplitude) · [Density matrix](#density-matrix) · [Global phase](#global-phase)

<a id="global-phase"></a>

### Global phase

A common unit-modulus factor multiplying every amplitude of a state vector. It cancels in |ψ⟩⟨ψ| and leaves the represented pure-state density matrix unchanged. This statement assumes the factor applies to the whole state being compared.

**Quick example:** The vectors (3/5,4/5) and (3i/5,4i/5) give the same density matrix.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Relative phase](#relative-phase) · [Density matrix](#density-matrix) · [Quantum amplitude](#amplitude)

<a id="relative-phase"></a>

### Relative phase

The phase difference between nonzero amplitudes in a chosen basis. It appears in off-diagonal density-matrix entries and can change interference probabilities even when the basis populations stay fixed.

**Quick example:** The states (3/5,4/5) and (3/5,−4/5) have the same Z probabilities but X-plus probabilities 49/50 and 1/50.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Global phase](#global-phase) · [Coherence in a chosen basis](#coherence) · [Born probability](#born-probability)

<a id="pure-state"></a>

### Pure quantum state

A density matrix of the form ρ = |ψ⟩⟨ψ| for a unit vector ψ. In finite dimensions it has rank one, satisfies ρ² = ρ and has purity tr(ρ²) = 1. The vector representative is determined only up to global phase.

**Also called:** Pure state.

**Quick example:** For ψ = (3/5,4/5), ρ = [[9,12],[12,16]]/25 is pure.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Density matrix](#density-matrix) · [Purity of a density matrix](#purity) · [Projector](#projector) · [Mixed quantum state](#mixed-state)

<a id="mixed-state"></a>

### Mixed quantum state

A density matrix that is not pure. In finite dimensions its purity is less than one, and it can be written as a convex mixture of pure-state density matrices. Such a decomposition is generally not unique.

**Also called:** Mixed state.

**Quick example:** The dephased state diag(9/25,16/25) has purity 337/625, so it is mixed.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Pure quantum state](#pure-state) · [Density matrix](#density-matrix) · [Dephasing](#dephasing) · [Purity of a density matrix](#purity)

<a id="quantum-effect"></a>

### Quantum measurement effect

A Hermitian operator E satisfying 0 ≤ E ≤ I. For density matrix ρ, tr(Eρ) is the probability of its associated outcome. Effects in a complete measurement sum to I. They need not individually be projectors.

**Also called:** Measurement effect.

**Quick example:** E = I/2 gives probability 1/2 for every state, although E² = I/4 differs from E.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Born probability](#born-probability) · [Positive semidefinite matrix](#positive-semidefinite) · [Projector](#projector)

<a id="observable"></a>

### Quantum observable

In the finite setting, a Hermitian operator whose real eigenvalues label possible outcomes of its projective measurement. Its expectation in state ρ is tr(Aρ). The operator and its measurement effects have related but different roles.

**Quick example:** The Pauli matrix Z = diag(1,−1) has mean 9/25−16/25 = −7/25 in the demonstration state.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Hermitian matrix](#hermitian) · [Quantum measurement effect](#quantum-effect) · [Eigenvalue](#eigenvalue) · [Matrix trace](#trace)

<a id="quantum-channel"></a>

### Quantum channel

A linear completely positive, trace-preserving map on density matrices. A finite Kraus representation is Φ(ρ) = ΣⱼKⱼρKⱼ* with ΣⱼKⱼ*Kⱼ = I. Complete positivity requires positivity to survive extension by an arbitrary auxiliary quantum system.

**Also called:** CPTP map, Completely positive trace-preserving map.

**Quick example:** Coordinate dephasing uses K₀ = diag(1,0) and K₁ = diag(0,1), keeping the diagonal entries and deleting the off-diagonal entries.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Kraus operators](#kraus-operator) · [Dephasing](#dephasing) · [Matrix trace](#trace) · [Density matrix](#density-matrix)

<a id="quantum-tomography"></a>

### Quantum state tomography

Reconstructing a state from probabilities for a sufficiently informative collection of measurement settings. For a qubit, exact X, Y and Z outcome probabilities determine its density matrix. Experimental estimates introduce sampling error and must still describe a positive state.

**Also called:** State tomography.

**Quick example:** For the phase-one demonstration state, X-plus = 49/50, Y-plus = 1/2 and Z-plus = 9/25 recover the upper-right entry 12/25.

**Keep in mind:** One outcome from a single copy does not supply the three ensemble probabilities.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Density matrix](#density-matrix) · [Quantum observable](#observable) · [Born probability](#born-probability) · [Identifiability relative to a model class](#identifiability)

<a id="selective-measurement"></a>

### Selective projective measurement

A projective measurement with its outcome retained. Outcome j has probability pⱼ = tr(Pⱼρ); if pⱼ > 0, the conditional output state is PⱼρPⱼ/pⱼ. Discarding the outcome instead gives the sum ΣⱼPⱼρPⱼ.

**Quick example:** In the demonstration, retaining coordinate outcome zero gives the state |0⟩⟨0| with probability 9/25.

**Keep in mind:** The conditional state formula is undefined for a zero-probability outcome.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Dephasing](#dephasing) · [Born probability](#born-probability) · [Projector](#projector)

<a id="arithmetic-and-modules"></a>

## Arithmetic and modules

Finite fields, lift branches, and the module data behind support.

[Prime power](#prime-power) · [Modular reduction](#modular-reduction) · [Lift branch](#lift-branch) · [Compatible tower](#compatible-tower) · [p-adic integer](#padic-integer) · [Survival to a finite level](#surviving-branch) · [Prime field](#prime-field) · [Extension field](#extension-field) · [Finite-field Frobenius](#frobenius) · [Field trace](#field-trace) · [Field norm](#field-norm) · [Irreducible polynomial](#irreducible-polynomial) · [Commutative ring with identity](#ring) · [Module](#module) · [Module presentation](#module-presentation) · [Cokernel](#cokernel) · [Module annihilator](#annihilator) · [Module support](#module-support) · [Zeroth Fitting ideal](#fitting-ideal) · [Multiplicity in the module example](#multiplicity) · [Ideal](#ideal) · [Prime ideal](#prime-ideal) · [Localization at a prime](#localization) · [p-adic valuation](#p-adic-valuation) · [p-adic unit](#p-adic-unit) · [Characteristic of a field](#characteristic-of-field)

<a id="prime-power"></a>

### Prime power

An integer pⁿ with p prime and n a nonnegative integer. Successive positive powers give the moduli in the lift-branch example.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Integer congruence](#congruence) · [Prime field](#prime-field)

<a id="modular-reduction"></a>

### Modular reduction

Passing from a residue class modulo pⁿ⁺¹ to its class modulo pⁿ. This map forgets the highest retained base-p digit.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Prime power](#prime-power) · [Residue class](#residue-class) · [Coarsening](#coarsening)

<a id="lift-branch"></a>

### Lift branch

A sequence of solutions at successive levels whose reductions agree. A node at one finite level can have several children or no child.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Lift](#lift) · [Modular reduction](#modular-reduction) · [Compatible tower](#compatible-tower)

<a id="compatible-tower"></a>

### Compatible tower

A collection of objects with specified maps between levels and stated compatibility identities. For modular solutions, the next residue must reduce to the preceding one.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Compatibility](#compatibility) · [Modular reduction](#modular-reduction) · [Completion](#completion)

<a id="padic-integer"></a>

### p-adic integer

For a prime p, an element of the inverse limit of the residue rings modulo pⁿ. It specifies a compatible residue at every positive level. A finite list of residues is only a truncation of that data.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Compatible tower](#compatible-tower) · [Prime power](#prime-power) · [Truncation](#truncation) · [p-adic valuation](#p-adic-valuation) · [p-adic unit](#p-adic-unit)

<a id="surviving-branch"></a>

### Survival to a finite level

A branch reaches the chosen last level without losing compatibility or the required equations. Survival to that level alone says nothing about the next one.

**In the worked example:** The residue 9 solves x² ≡ 1 modulo 16. Its only candidate lifts modulo 32 are 9 and 25, and both squares equal 17 modulo 32. This branch reaches level four but has no child at level five.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Lift branch](#lift-branch) · [Finite check](#finite-check)

<a id="prime-field"></a>

### Prime field

The smallest subfield of a field. In characteristic p it consists of the p scalar classes and is isomorphic to Fₚ. In characteristic zero it is isomorphic to the rational numbers.

**Quick example:** The field F₅ has five elements. Its nonzero element 2 has inverse 3.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Field](#field) · [Integer congruence](#congruence)

<a id="extension-field"></a>

### Extension field

A field containing a specified smaller field. The extension degree is its vector-space dimension over that smaller field.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Field](#field) · [Dimension](#dimension) · [Prime field](#prime-field)

<a id="frobenius"></a>

### Finite-field Frobenius

In a finite field of characteristic p, the map x ↦ xᵖ is an automorphism. Over F_q, the relative Frobenius is x ↦ x^q. The example uses q = p = 5.

**Also called:** Frobenius automorphism.

**Quick example:** In characteristic p, (a+b)ᵖ = aᵖ+bᵖ. On Fₚ itself the Frobenius fixes every element.

**In the worked example:** In F₂₅ = F₅[α] with α² = 3, one has α⁵ = −α. Thus Frobenius sends 1+α to 1−α, and applying it twice returns 1+α.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Extension field](#extension-field) · [Linear isomorphism](#isomorphism)

<a id="field-trace"></a>

### Field trace

For a finite field extension L/K, the trace of the K-linear map that multiplies L by an element a. In F₂₅/F₅ it is a+a⁵.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Matrix trace](#trace) · [Extension field](#extension-field) · [Finite-field Frobenius](#frobenius)

<a id="field-norm"></a>

### Field norm

For a finite field extension L/K, the determinant of multiplication by an element a as a K-linear map. In F₂₅/F₅ it is a·a⁵. This norm is algebraic and is not a vector length.

**In the worked example:** For β = 1+α in F₂₅ = F₅[α] with α² = 3, the norm to F₅ is ββ⁵ = (1+α)(1−α) = 1−3 = 3 in F₅.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Determinant](#determinant) · [Extension field](#extension-field) · [Norm](#norm)

<a id="irreducible-polynomial"></a>

### Irreducible polynomial

A nonconstant polynomial over a field that cannot be factored into two polynomials of positive degree over that field. For degree two, irreducibility is equivalent to having no root in the field.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Field](#field) · [Extension field](#extension-field)

<a id="ring"></a>

### Commutative ring with identity

A system with addition, subtraction and commutative multiplication satisfying the ring laws and having a multiplicative identity. A nonzero element need not have a multiplicative inverse.

**Quick example:** The integers form a commutative ring with identity, but 2 has no multiplicative inverse within the integers.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Field](#field) · [Module](#module)

<a id="module"></a>

### Module

An abelian additive group with a scalar action by a ring satisfying the usual distributive, associative, and identity laws. For a module over Q[t], multiplication by t can be specified by a Q-linear operator.

**Quick example:** An abelian group is a module over Z, where multiplying by an integer means repeated addition and its inverse.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Commutative ring with identity](#ring) · [Operator algebra](#operator-algebra)

<a id="module-presentation"></a>

### Module presentation

A description of a module by generators and relations. A finite matrix A: Rᵐ → Rⁿ presents the quotient Rⁿ/im A.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Module](#module) · [Cokernel](#cokernel) · [Image](#image)

<a id="cokernel"></a>

### Cokernel

For a linear map or module map A: U → V, the quotient V/im A. It records target classes modulo those already reached by A.

**Quick example:** The cokernel of multiplication by 2 on Z is Z/2Z, which records the two parity classes.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Quotient space](#quotient-space) · [Image](#image) · [Module](#module)

<a id="annihilator"></a>

### Module annihilator

The ideal of ring elements that act as zero on every element of a module. For Q[t]/(tᵏ), the annihilator is the ideal (tᵏ).

**Quick example:** In the Z-module Z/6Z, every multiple of 6 acts as zero, so its annihilator is the ideal (6).

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Module](#module) · [Nilpotent operator](#nilpotent) · [Commutative ring with identity](#ring)

<a id="module-support"></a>

### Module support

The prime ideals at which a module’s localization is nonzero. In the example Q[t]/(tᵏ), the support is the single prime ideal (t). The underlying support set does not determine k or the module.

**In the worked example:** Over R = Q[t], the modules R/(t) and R/(t²) both have support {(t)}. Their rational dimensions are one and two, so equal support does not identify the modules.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Module](#module) · [Module annihilator](#annihilator) · [Multiplicity in the module example](#multiplicity)

<a id="fitting-ideal"></a>

### Zeroth Fitting ideal

For a finite presentation Rᵐ → Rⁿ → M → 0 over a commutative ring, the ideal generated by the n by n minors of the presentation matrix. In the one-generator example with relation tᵏ, it is (tᵏ).

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Module presentation](#module-presentation) · [Determinant](#determinant) · [Module support](#module-support)

<a id="multiplicity"></a>

### Multiplicity in the module example

For Q[t]/(tᵏ) supported at t=0, the integer k records the module’s length and its Q-vector-space dimension. This is additional data beyond the one-point support set. Other works use multiplicity with their own specified objects.

**In the worked example:** The module Q[t]/(t²) has basis (1,t) over Q and multiplicity two in this example. Its fiber at t = 0 still has dimension one. That special-fiber dimension does not recover the full module’s rational dimension.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Dimension](#dimension) · [Module support](#module-support) · [Nilpotent operator](#nilpotent)

<a id="ideal"></a>

### Ideal

An additive subgroup of a commutative ring closed under multiplication by every element of the ring. The principal ideal (f) consists of all multiples of f.

**Quick example:** The even integers form the ideal (2) in Z: multiplying an even integer by any integer stays even.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Commutative ring with identity](#ring) · [Module annihilator](#annihilator)

<a id="prime-ideal"></a>

### Prime ideal

A proper ideal P such that ab in P implies a in P or b in P. The ideal (t) in Q[t] is prime because the quotient is the field Q.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Ideal](#ideal) · [Commutative ring with identity](#ring) · [Field](#field)

<a id="localization"></a>

### Localization at a prime

A construction that makes ring elements outside a chosen prime ideal invertible, and carries a module along with that scalar change. The prime lies in the module’s support exactly when the localized module is nonzero.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Prime ideal](#prime-ideal) · [Module support](#module-support) · [Module](#module)

<a id="p-adic-valuation"></a>

### p-adic valuation

For a prime p and a nonzero rational x, vₚ(x) is the exponent of p in its reduced numerator minus the exponent in its reduced denominator. Set vₚ(0) = ∞. A rational is p-adically integral when its valuation is nonnegative.

**Also called:** Prime-adic valuation, v_p.

**Quick example:** v₂(12/5) = 2, while v₂(3/8) = −3.

**In the worked example:** The factorial-lane recurrence gives C₂ = 178205/966966. Its numerator contains one factor of 5 and its denominator contains none, so v₅(C₂) = 1.

[Hand-worked example](demonstrations/FACTORIAL_LANES.md) · [p-adic unit](#p-adic-unit) · [Prime power](#prime-power) · [Modular reduction](#modular-reduction)

<a id="p-adic-unit"></a>

### p-adic unit

An invertible element of the p-adic integers. For a rational number, being a p-adic unit means vₚ(x) = 0: its reduced numerator and denominator are both coprime to p.

**Also called:** Unit at p.

**Quick example:** The rational 3/5 is a 2-adic unit because both numerator and denominator are odd.

**In the worked example:** g₁ = 1/1001 is a 5-adic unit and can be reduced modulo powers of 5. C₂ = 178205/966966 is 5-adically integral but is not a unit.

**Keep in mind:** A p-adically integral rational number need not be an ordinary integer, and a p-adically integral number of positive valuation is not a unit.

[Hand-worked example](demonstrations/FACTORIAL_LANES.md) · [p-adic valuation](#p-adic-valuation) · [Modular inverse](#modular-inverse) · [p-adic integer](#padic-integer)

<a id="characteristic-of-field"></a>

### Characteristic of a field

The least positive integer p for which adding the multiplicative identity to itself p times gives zero, if such an integer exists; otherwise the characteristic is zero. Positive field characteristic is always prime. Division by integers in formulas must respect this value.

**Quick example:** In the field with three elements, 1+1+1 = 0. A formula dividing by 3 cannot be used there.

**Keep in mind:** Falling-factorial coordinate maps remain monic triangular in positive characteristic, but derivative and roots-of-unity arguments can require additional hypotheses.

[Further reading](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md) · [Field](#field) · [Prime field](#prime-field) · [Roots-of-unity filter](#roots-of-unity-filter) · [Exponential generating function](#exponential-generating-function)

<a id="dynamics-and-calibration"></a>

## Dynamics, memory, and calibration

What a retained state predicts and what exact observations determine.

[Visible state](#visible-state) · [Hidden state](#hidden-state) · [Prepared hidden initialization](#prepared-state) · [Discrete memory maps](#memory-kernel) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [State augmentation](#state-augmentation) · [Semigroup law for evolution maps](#semigroup-law) · [Exact operator calibration](#calibration) · [Calibration span](#calibration-span) · [Compatible model](#compatible-model) · [Linear extension](#linear-extension) · [Reusable calibrated core](#reusable-core) · [Identifiability relative to a model class](#identifiability) · [Finite linear state-space realization](#state-space-realization) · [State sufficient for a deterministic update](#markov-state) · [Fixed point](#fixed-point)

<a id="visible-state"></a>

### Visible state

The state coordinates or summary retained for a specified prediction task. A visible value need not contain enough information to determine its own next value.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Hidden state](#hidden-state) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [Coarsening](#coarsening)

<a id="hidden-state"></a>

### Hidden state

The part of the declared full state omitted by the current observation or summary. It can influence later visible outputs even when it does not affect the current output.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Visible state](#visible-state) · [Discrete memory maps](#memory-kernel)

<a id="prepared-state"></a>

### Prepared hidden initialization

An initialization that fixes the hidden coordinates by a specified rule. The example uses R(y)=(y,0). Results for this preparation need not hold for arbitrary hidden starting values.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Hidden state](#hidden-state) · [Reconstruction](#reconstruction) · [Autonomous dynamics of a summary](#autonomous-dynamics)

<a id="memory-kernel"></a>

### Discrete memory maps

For the block update (y,z) ↦ (Ay+Bz,Gy+Dz), the maps Mₖ=BDᵏG describe a visible-to-hidden entry, k hidden transitions, and a return. The first effect of Mₖ on prepared visible evolution occurs after k+2 full steps.

**In the worked example:** For A = B = G = 1 and D = 0 in the visible and hidden block update, M₀ = BD⁰G = 1 while Mₖ = 0 for k ≥ 1. Information entering the hidden coordinate returns after two full steps.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Block matrix](#block-matrix) · [Hidden state](#hidden-state) · [Prepared hidden initialization](#prepared-state) · [State sufficient for a deterministic update](#markov-state) · [Finite linear state-space realization](#state-space-realization)

<a id="autonomous-dynamics"></a>

### Autonomous dynamics of a summary

A transition rule determined by the retained current state, under the declared controls and initialization contract. For deterministic maps, full states with the same summary must have the same next summary.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Visible state](#visible-state) · [Fiber](#fiber) · [Factorization through a map](#factorization)

<a id="state-augmentation"></a>

### State augmentation

Enlarging a retained state with additional coordinates or history needed for future prediction. The hidden-memory example retains the previous visible value along with the current one.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Visible state](#visible-state) · [Hidden state](#hidden-state) · [Autonomous dynamics of a summary](#autonomous-dynamics)

<a id="semigroup-law"></a>

### Semigroup law for evolution maps

The identity Eₘ₊ₙ=EₘEₙ for nonnegative step counts, with E₀ the identity. It expresses agreement between uninterrupted evolution and successive uses of the same state-level evolution maps.

**In the worked example:** With the hidden coordinate initialized to zero, the prepared visible maps Eₙ = CTⁿR are scalar multipliers with E₁ = 1 and E₂ = 2. Thus E₂ ≠ E₁E₁. Restarting from the visible value resets hidden information.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Composition](#composition) · [Identity operator](#identity) · [Prepared hidden initialization](#prepared-state)

<a id="calibration"></a>

### Exact operator calibration

Supplied input-output pairs for an unknown operation. For a linear operation, every linear relation among calibrated inputs must be respected by the supplied outputs.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Linear map](#linear-map) · [Calibration span](#calibration-span) · [Compatible model](#compatible-model)

<a id="calibration-span"></a>

### Calibration span

The span of the calibrated input vectors. Consistent exact linear calibration determines the operation on this span. Its outputs can leave that span.

**In the worked example:** The measurements Te₁ = e₁ and Te₂ = e₃ determine T(ae₁+be₂) = ae₁+be₃ throughout U = span(e₁,e₂). In particular, T(2e₁−e₂) = 2e₁−e₃, while Te₃ remains unspecified.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Exact operator calibration](#calibration) · [Span](#span) · [Reusable calibrated core](#reusable-core)

<a id="compatible-model"></a>

### Compatible model

A model satisfying all supplied data and every declared structural assumption. In the calibration example, all linear extensions of the known restriction are allowed, and each model stays fixed through a trajectory.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Exact operator calibration](#calibration) · [Linear extension](#linear-extension) · [Identifiability relative to a model class](#identifiability)

<a id="linear-extension"></a>

### Linear extension

A linear map on a larger vector space that agrees with a given map on its original subspace. Values on an added basis can vary unless further conditions are imposed.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Linear map](#linear-map) · [Subspace](#subspace) · [Basis](#basis)

<a id="reusable-core"></a>

### Reusable calibrated core

For the tutorial’s unrestricted linear extension class and full-state output, the largest subspace inside the calibration span preserved by every calibrated operation. All finite operation sequences from this subspace are determined by the calibration.

**In the worked example:** With Te₁ = e₁ and Te₂ = e₃, the known image of ae₁+be₂ stays in U = span(e₁,e₂) exactly when b = 0. The retained domain stabilizes at span(e₁), where every compatible extension satisfies Tⁿ(ae₁) = ae₁ for all n ≥ 0.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Calibration span](#calibration-span) · [Invariant subspace](#invariant-subspace) · [Compatible model](#compatible-model)

<a id="identifiability"></a>

### Identifiability relative to a model class

A requested quantity is identifiable from the supplied data when every compatible model gives the same value. Identifying a particular output can require less information than identifying the whole model.

**Quick example:** Observing only x+y cannot distinguish parameter pairs (1,2) and (2,1) if both are allowed.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Compatible model](#compatible-model) · [Exact operator calibration](#calibration) · [Obstruction](#obstruction)

<a id="state-space-realization"></a>

### Finite linear state-space realization

A description of a discrete linear system by xₙ₊₁ = Axₙ+Buₙ and yₙ = Cxₙ+Duₙ. It declares the retained state x, input u and observation y. Different coordinate systems can describe the same input-output behavior.

**Quick example:** The hidden-memory example has full state (y,z) and autonomous update matrix [[1,1],[1,0]]. Its visible observation selects y.

[Further reading](examples/22_HIDDEN_MEMORY.md) · [Visible state](#visible-state) · [Hidden state](#hidden-state) · [Realization](#realization) · [Scalar McMillan degree](#mcmillan-degree)

<a id="markov-state"></a>

### State sufficient for a deterministic update

A retained value that determines its own next value for every admissible full state, under a specified deterministic evolution. If R is the summary and T the full update, this requires a map T̄ with T̄R = RT on the admissible states.

**Quick example:** In the Fibonacci update, y alone is insufficient, while (yₙ,yₙ₋₁) has the autonomous rule (u,v) ↦ (u+v,u).

**Keep in mind:** Stochastic Markov properties concern conditional distributions and require their own probability model.

[Further reading](examples/22_HIDDEN_MEMORY.md) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [Sufficient summary for a requested output](#sufficient-summary) · [State augmentation](#state-augmentation)

<a id="fixed-point"></a>

### Fixed point

An input x satisfying T(x) = x for a declared map T. For a linear projector P, the fixed points are precisely its image. Being fixed is an algebraic property; stability under nearby perturbations is a further question.

**Quick example:** The projector P(x,y) = (x,0) fixes every point on the horizontal axis.

[Further reading](operators/PACKETS.md) · [Projector](#projector) · [Image](#image) · [Invariant subspace](#invariant-subspace)

<a id="inference-and-probability"></a>

## Inference and probability

The model, observation and Gaussian calculations used in the inference example.

[Finite-dimensional Gaussian model](#gaussian-model) · [Prior distribution](#prior) · [Likelihood](#likelihood) · [Posterior distribution](#posterior) · [Covariance matrix](#covariance) · [Precision matrix](#precision-matrix) · [Observation innovation](#innovation) · [Exact Gaussian gain](#gaussian-gain) · [Joseph covariance](#joseph-covariance)

<a id="gaussian-model"></a>

### Finite-dimensional Gaussian model

A model with a Gaussian state and specified linear observations with Gaussian noise. The tutorial supplies an independent noise variable, a prior mean and covariance, an observation matrix and a positive noise variance.

**Also called:** Multivariate Gaussian model, Multivariate normal model.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Prior distribution](#prior) · [Likelihood](#likelihood) · [Covariance matrix](#covariance)

<a id="prior"></a>

### Prior distribution

The state distribution specified before conditioning on the observation under the declared model. A Gaussian prior is described by its mean and covariance.

**Also called:** Prior.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Finite-dimensional Gaussian model](#gaussian-model) · [Posterior distribution](#posterior) · [Covariance matrix](#covariance)

<a id="likelihood"></a>

### Likelihood

For a fixed observed value, the observation density viewed as a function of the proposed state or parameter. It is combined with the prior and normalized to obtain a posterior density when that density formula applies.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Prior distribution](#prior) · [Posterior distribution](#posterior) · [Finite-dimensional Gaussian model](#gaussian-model)

<a id="posterior"></a>

### Posterior distribution

The state distribution conditional on the observed data under the supplied prior and observation model. The tutorial computes the usual explicit Gaussian conditional density by completing the square.

**Also called:** Posterior.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Prior distribution](#prior) · [Likelihood](#likelihood) · [Exact Gaussian gain](#gaussian-gain)

<a id="covariance"></a>

### Covariance matrix

For a random vector X with mean m and finite second moments, the matrix E[(X−m)(X−m)ᵀ]. Its diagonal entries are variances. For a unit direction u, uᵀCu is the variance in that direction.

**Quick example:** Independent coordinates with variances 1 and 4 have covariance matrix diag(1,4).

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Positive semidefinite matrix](#positive-semidefinite) · [Finite-dimensional Gaussian model](#gaussian-model) · [Precision matrix](#precision-matrix) · [Gaussian quadratic form](#gaussian-quadratic-form)

<a id="precision-matrix"></a>

### Precision matrix

The inverse covariance when the covariance is invertible. In a nonsingular Gaussian density it appears in the quadratic exponent. This use of precision is distinct from the number of bits in stored arithmetic.

**Also called:** Inverse covariance matrix, Concentration matrix.

**Quick example:** For covariance diag(1,4), the precision matrix is diag(1,1/4).

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Covariance matrix](#covariance) · [Inverse](#inverse) · [Precision](#precision)

<a id="innovation"></a>

### Observation innovation

The difference d=y−Hm between an observation and its predicted mean in the linear model. Its covariance is S=HPHᵀ+R when the state covariance is P and the independent noise covariance is R.

**Also called:** Observation residual.

**Quick example:** If an observation is 7 and the predicted observation is 5, the innovation is 2 under the observation-minus-prediction convention.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Finite-dimensional Gaussian model](#gaussian-model) · [Covariance matrix](#covariance) · [Exact Gaussian gain](#gaussian-gain)

<a id="gaussian-gain"></a>

### Exact Gaussian gain

For the declared linear Gaussian model, K=PHᵀ(HPHᵀ+R)⁻¹. Multiplying the innovation by K gives the posterior mean correction. Positive noise covariance makes the displayed observation-space inverse exist.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Observation innovation](#innovation) · [Posterior distribution](#posterior) · [Joseph covariance](#joseph-covariance)

<a id="joseph-covariance"></a>

### Joseph covariance

For a gain B, the matrix (I−BH)P(I−BH)ᵀ+BRBᵀ. It is positive semidefinite for valid prior and noise covariances. At the exact gain it equals the posterior covariance. A general gain still needs its own accuracy check.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Covariance matrix](#covariance) · [Exact Gaussian gain](#gaussian-gain) · [Positive semidefinite matrix](#positive-semidefinite)

## Symbols in the introductory example

The examples use the following notation. The reading column spells out symbols for readers who are unfamiliar with them.

| Symbol | Read as | Meaning here |
|---|---|---|
| x, y, v | Vector names | Objects or their coordinate columns, as declared in the example. |
| R², R³ | R two, R three | Real coordinate spaces of dimensions two and three. |
| xᵀ | x transpose | A row or column with its orientation exchanged. |
| Iₙ | I sub n | The identity matrix on n coordinates. |
| Pᵢ | P sub i | A projector in the declared family. |
| Σᵢ Pᵢx | Sum over i of P sub i applied to x | Add the selected components. The examples use finite sums. |
| A, S | A, S | Analysis and synthesis maps where that convention is declared. |
| C⁻¹ | C inverse | The inverse of an invertible coordinate change C. |
| QⱼTPᵢ | Q sub j, T, P sub i | Select source i, apply T, then select target j. |
| ker R, im R | Kernel of R, image of R | Inputs sent to zero and outputs attained by a linear map. |
| G ∘ R | G composed with R | Apply R first and G second. |
| span{v, Nv} | Span of v and N v | All scalar linear combinations of the displayed vectors. |
| ⟨u, v⟩w | Inner product of u and v with weights w | The weighted pairing defined in Example 8. |
| ‖x‖₂² | Squared Euclidean norm of x | Sum of squares of real coordinates. |
| x̂ | x hat | An approximation or reconstruction, as defined locally. |
| xₖₘ₊ᵣ | x sub k m plus r | A sequence entry whose index has remainder r modulo m. |
| 1.101₂ | One point one zero one in base two | The binary fraction 1 + 1/2 + 1/8. |

Symbols are local to their definitions. In another paper, the same letter can denote a different object.

## Alphabetical index

[A](#index-a) · [B](#index-b) · [C](#index-c) · [D](#index-d) · [E](#index-e) · [F](#index-f) · [G](#index-g) · [H](#index-h) · [I](#index-i) · [J](#index-j) · [K](#index-k) · [L](#index-l) · [M](#index-m) · [N](#index-n) · [O](#index-o) · [P](#index-p) · [Q](#index-q) · [R](#index-r) · [S](#index-s) · [T](#index-t) · [U](#index-u) · [V](#index-v) · [W](#index-w) · [Z](#index-z)

<a id="index-a"></a>

### A

[Absolute error](#absolute-error) · [Address](#address) · [Adjoint matrix](#adjoint) · [Admissible input set](#admissible-input) · [Admissible leaf](#admissible-leaf) · [Admittance](#admittance) · [Affine map](#affine-map) · [Algebra homomorphism](#algebra-homomorphism) · [Aliasing](#aliasing) · [Analysis and synthesis](#analysis-synthesis) · [Analysis filter bank](#filter-bank) · [Analytic error budget](#analytic-error-budget) · [Autonomous dynamics of a summary](#autonomous-dynamics)

<a id="index-b"></a>

### B

[Backward difference](#backward-difference) · [Backward error](#backward-error) · [Basis](#basis) · [Bell numbers](#bell-numbers) · [Bilinear form](#bilinear-form) · [Binomial coefficient convolution](#binomial-convolution) · [Block matrix](#block-matrix) · [Born probability](#born-probability) · [Bounded linear operator](#bounded-operator)

<a id="index-c"></a>

### C

[Calibration span](#calibration-span) · [Canonical dual synthesis](#canonical-dual) · [Cauchy product](#cauchy-product) · [Centered spectral packet](#centered-spectral-packet) · [Certificate](#certificate) · [Characteristic function](#characteristic-function) · [Characteristic of a field](#characteristic-of-field) · [Chinese remainder theorem](#chinese-remainder) · [Circuit realization](#circuit-realization) · [Circular shift](#circular-shift) · [Classical frame operator](#classical-frame-operator) · [Coarsening](#coarsening) · [Coefficient](#coefficient) · [Coefficient convolution](#convolution) · [Coefficient gauge](#coefficient-gauge) · [Coefficient metric](#coefficient-metric) · [Coefficient projection](#coefficient-projection) · [Coefficient recurrence](#coefficient-recurrence) · [Coherence in a chosen basis](#coherence) · [Cokernel](#cokernel) · [Collision witness](#collision-witness) · [Commutative ring with identity](#ring) · [Commutator](#commutator) · [Commuting diagram](#commuting-diagram) · [Compatibility](#compatibility) · [Compatible model](#compatible-model) · [Compatible tower](#compatible-tower) · [Complete packet family](#complete-packet-family) · [Completion](#completion) · [Complex conjugate](#complex-conjugate) · [Composition](#composition) · [Compositional inverse of a formal series](#compositional-inverse) · [Condition number of a coordinate map](#condition-number) · [Conditional](#conditional) · [Contracted argument](#contracted-argument) · [Coordinate change](#coordinate-change) · [Coordinates](#coordinates) · [Coprime integers](#coprime) · [COS method](#cos-method) · [Counterexample](#counterexample) · [Covariance matrix](#covariance) · [Covector](#covector) · [Covector pullback](#covector-pullback) · [Cyclic reachability](#cyclic-reachability) · [Cyclic vector](#cyclic)

<a id="index-d"></a>

### D

[Density matrix](#density-matrix) · [Dephasing](#dephasing) · [Derivation trace](#derivation-trace) · [Derivative in the series example](#derivative) · [Detail coefficient](#detail-coefficient) · [Determinant](#determinant) · [Diagonalizable operator](#diagonalizable) · [Differential equation](#differential-equation) · [Dimension](#dimension) · [Direct sum](#direct-sum) · [Directed enclosure](#directed-enclosure) · [Discrete cosine transform](#discrete-cosine-transform) · [Discrete Fourier transform](#discrete-fourier-transform) · [Discrete memory maps](#memory-kernel) · [Domain and codomain](#domain-codomain) · [Downsampling](#downsampling) · [Dual space](#dual-space) · [Dyadic rational](#dyadic-rational)

<a id="index-e"></a>

### E

[Eigenspace](#eigenspace) · [Eigenvalue](#eigenvalue) · [Eigenvector](#eigenvector) · [Elimination](#elimination) · [Exact](#exact) · [Exact Gaussian gain](#gaussian-gain) · [Exact operator calibration](#calibration) · [Exact recovery from a summary](#exact-recovery) · [Exponential generating function](#exponential-generating-function) · [Extension field](#extension-field)

<a id="index-f"></a>

### F

[Factorial lane](#factorial-lane) · [Factorization through a map](#factorization) · [Falling factorial](#falling-factorial) · [Falling-degree operator](#degree-operator) · [Falling-factorial raising operator](#raising-operator) · [Feasibility](#feasibility) · [Fiber](#fiber) · [Field](#field) · [Field norm](#field-norm) · [Field trace](#field-trace) · [Finite check](#finite-check) · [Finite conditional expectation](#conditional-expectation) · [Finite frame](#finite-frame) · [Finite impulse response filter](#finite-impulse-response-filter) · [Finite linear state-space realization](#state-space-realization) · [Finite proof field](#proof-field) · [Finite repair menu](#repair-menu) · [Finite-dimensional Gaussian model](#gaussian-model) · [Finite-field Frobenius](#frobenius) · [Fixed point](#fixed-point) · [Formal power series](#formal-power-series) · [Formal reciprocal](#formal-reciprocal) · [Formal series composition](#formal-composition) · [Formal statement](#formal-statement) · [Forward difference](#forward-difference) · [Forward error](#forward-error) · [Frame bounds](#frame-bounds) · [Free linear repair](#free-repair) · [Fubini numbers](#fubini-numbers)

<a id="index-g"></a>

### G

[Gaussian quadratic form](#gaussian-quadratic-form) · [Generalized hypergeometric series](#hypergeometric-series) · [Global phase](#global-phase) · [Gram operator](#gram-operator)

<a id="index-h"></a>

### H

[Haar pair](#haar-pair) · [Hermitian matrix](#hermitian) · [Heuristic](#heuristic) · [Hidden state](#hidden-state) · [Hilbert–Schmidt norm](#hilbert-schmidt-norm) · [Hypothesis](#hypothesis)

<a id="index-i"></a>

### I

[Ideal](#ideal) · [Identifiability relative to a model class](#identifiability) · [Identity operator](#identity) · [Image](#image) · [Impedance](#impedance) · [Impedance Cayley transform](#cayley-transform) · [Inclusion-minimal certificate](#inclusion-minimal) · [Inconclusive search](#search-inconclusive) · [Induced operator norm](#operator-norm) · [Initial condition](#initial-condition) · [Injective map](#injective) · [Inner product](#inner-product) · [Integer congruence](#congruence) · [Interpolation](#interpolation) · [Intertwiner](#intertwiner) · [Interval arithmetic](#interval-arithmetic) · [Invariant subspace](#invariant-subspace) · [Inverse](#inverse) · [Involution](#involution) · [Irreducible polynomial](#irreducible-polynomial)

<a id="index-j"></a>

### J

[Joseph covariance](#joseph-covariance)

<a id="index-k"></a>

### K

[Kernel](#kernel) · [Kraus operators](#kraus-operator)

<a id="index-l"></a>

### L

[Leakage from a retained packet](#packet-leakage) · [Lean correspondence](#lean-correspondence) · [Least certificate](#least-certificate) · [Left inverse](#left-inverse) · [Lift](#lift) · [Lift branch](#lift-branch) · [Likelihood](#likelihood) · [Linear extension](#linear-extension) · [Linear independence](#linear-independence) · [Linear isometry](#isometry) · [Linear isomorphism](#isomorphism) · [Linear map](#linear-map) · [Linear obstruction witness](#dual-witness) · [Linear quotient map](#quotient-map) · [Localization at a prime](#localization) · [Lossless transmission line](#lossless-line)

<a id="index-m"></a>

### M

[Matched load](#matched-load) · [Matrix](#matrix) · [Matrix trace](#trace) · [Metric adjoint](#metric-adjoint) · [Minimal polynomial](#minimal-polynomial) · [Minimum-cost certificate](#minimum-cost-certificate) · [Mixed quantum state](#mixed-state) · [Modular inverse](#modular-inverse) · [Modular reduction](#modular-reduction) · [Module](#module) · [Module annihilator](#annihilator) · [Module presentation](#module-presentation) · [Module support](#module-support) · [Monic polynomial](#monic-polynomial) · [Moore–Penrose inverse](#pseudoinverse) · [Multiplicity in the module example](#multiplicity) · [Mutual annihilation](#mutual-annihilation)

<a id="index-n"></a>

### N

[Necessary condition](#necessary-condition) · [Newton coefficient formula](#newton-coefficients) · [Nilpotent operator](#nilpotent) · [Nonlinear map](#nonlinear-map) · [Norm](#norm) · [Normal matrix](#normal-matrix) · [Normalization](#normalization) · [Normalized impedance](#normalized-impedance) · [Nullity](#nullity) · [Numerical](#numerical) · [Numerical ternary](#ternary)

<a id="index-o"></a>

### O

[Oblique projector](#oblique-projector) · [Observation innovation](#innovation) · [Obstruction](#obstruction) · [Operator](#operator) · [Operator algebra](#operator-algebra) · [Operator compression](#compression) · [Operator conjugation](#conjugation) · [Operator norm convergence](#operator-norm-convergence) · [Operator orbit](#operator-orbit) · [Operator relation](#relation) · [Ordinary generating function](#ordinary-generating-function) · [Orthogonal complement](#orthogonal-complement) · [Orthogonal matrix](#orthogonal-matrix) · [Orthogonal projector](#orthogonal-projector) · [Orthonormal basis](#orthonormal-basis)

<a id="index-p"></a>

### P

[p-adic integer](#padic-integer) · [p-adic unit](#p-adic-unit) · [p-adic valuation](#p-adic-valuation) · [Packet](#packet) · [Parseval identity in chosen coordinates](#parseval-identity) · [Partition of a set](#partition) · [Pick matrix](#pick-matrix) · [Pointwise transfer defect](#transfer-defect) · [Pole of a rational function](#pole) · [Polynomial degree](#polynomial-degree) · [Polynomial in an operator](#polynomial-in-operator) · [Polynomial translation operator](#translation-operator) · [Polyphase carry](#polyphase-carry) · [Polyphase decomposition](#polyphase) · [Positive definite matrix](#positive-definite) · [Positive semidefinite matrix](#positive-semidefinite) · [Positive-real impedance function](#positive-real-function) · [Posterior distribution](#posterior) · [Power series](#power-series) · [Precision](#precision) · [Precision matrix](#precision-matrix) · [Prepared hidden initialization](#prepared-state) · [Prime field](#prime-field) · [Prime ideal](#prime-ideal) · [Prime power](#prime-power) · [Prior distribution](#prior) · [Projector](#projector) · [Proof](#proof) · [Pure quantum state](#pure-state) · [Purity of a density matrix](#purity)

<a id="index-q"></a>

### Q

[Quadratic form](#quadratic-form) · [Quantum amplitude](#amplitude) · [Quantum channel](#quantum-channel) · [Quantum measurement effect](#quantum-effect) · [Quantum observable](#observable) · [Quantum state tomography](#quantum-tomography) · [Qubit](#qubit) · [Quotient space](#quotient-space)

<a id="index-r"></a>

### R

[Radius of convergence](#radius-of-convergence) · [Range core](#range-core) · [Rank](#rank) · [Rank–nullity identity](#rank-nullity) · [Rational function](#rational-function) · [Realization](#realization) · [Reconstruction](#reconstruction) · [Reconstruction component](#reconstruction-component) · [Recorded inference rule](#inference-rule) · [Redundant coordinates](#redundancy) · [Refinement](#refinement) · [Reflection coefficient](#reflection-coefficient) · [Relative error](#relative-error) · [Relative phase](#relative-phase) · [Repair direction](#repair-direction) · [Repair selection cost](#repair-cost) · [Reproducible computation](#reproducibility) · [Residual](#residual) · [Residue class](#residue-class) · [Residue coefficient selector](#coefficient-selector) · [Return loss](#return-loss) · [Reusable calibrated core](#reusable-core) · [Right inverse](#right-inverse) · [Rising factorial](#rising-factorial) · [Root of unity](#root-of-unity) · [Roots-of-unity filter](#roots-of-unity-filter) · [Rounding](#rounding) · [Row space](#row-space)

<a id="index-s"></a>

### S

[Scalar](#scalar) · [Scalar McMillan degree](#mcmillan-degree) · [Scalar Schur function](#schur-function) · [Schur complement](#schur-complement) · [Secant numbers](#secant-numbers) · [Seed](#seed) · [Seed rank](#seed-rank) · [Selective projective measurement](#selective-measurement) · [Semigroup law for evolution maps](#semigroup-law) · [Seminorm](#seminorm) · [Shared premise](#shared-premise) · [Signal boundary convention](#boundary-condition) · [Signed Euler numbers](#signed-euler-numbers) · [Signed Stirling numbers of the first kind](#stirling-first-kind) · [Singular block range condition](#singular-range-condition) · [Singular value](#singular-value) · [Singular value decomposition](#singular-value-decomposition) · [Span](#span) · [Spectral projector](#spectral-projector) · [Spectral radius](#spectral-radius) · [State augmentation](#state-augmentation) · [State sufficient for a deterministic update](#markov-state) · [Stirling numbers of the second kind](#stirling-second-kind) · [Stirling transform](#stirling-transform) · [Strong operator convergence](#strong-convergence) · [Subspace](#subspace) · [Sufficient condition](#sufficient-condition) · [Sufficient summary for a requested output](#sufficient-summary) · [Surjective map](#surjective) · [Survival to a finite level](#surviving-branch)

<a id="index-t"></a>

### T

[Taylor coefficient](#taylor-coefficient) · [Tensor product of operators](#tensor-product) · [Theorem](#theorem) · [Tolerance](#tolerance) · [Touchard polynomial](#touchard-polynomial) · [Transfer block](#transfer-block) · [Transported product](#transported-product) · [Triangular matrix](#triangular-matrix) · [Truncation](#truncation) · [Typed path](#typed-path) · [Typed system](#typed-system)

<a id="index-u"></a>

### U

[ULP](#ulp) · [Unitary matrix](#unitary)

<a id="index-v"></a>

### V

[Vector](#vector) · [Vector space](#vector-space) · [Verification closure](#verification-closure) · [Visible state](#visible-state) · [Voltage standing-wave ratio](#vswr)

<a id="index-w"></a>

### W

[Wavelet lifting step](#lifting-step)

<a id="index-z"></a>

### Z

[Zeroth Fitting ideal](#fitting-ideal)

[Reading routes](READING_ROUTES.md) · [Hand-worked examples](HAND_WORKED_EXAMPLES.md) · [First runs](FIRST_RUN.md) · [Browse works](BROWSE.md)
