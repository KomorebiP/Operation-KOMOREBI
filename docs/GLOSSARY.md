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

A scalar supplies the coefficients in a linear combination. In a₁v₁+a₂v₂, the a-values say how much of each vector to take, while the v-values are the objects being combined. Scalars can themselves be complex numbers or elements of a finite field; they need not be ordinary real measurements.

Always identify the coefficient field before dividing or solving a linear system. For example, division by 2 is available over the rationals but unavailable in characteristic two. Changing the field can therefore change which coordinate formulas are legal, even when the displayed matrix entries look identical.

**Quick example:** In 3(2,−1) = (6,−3), the number 3 is the scalar.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Field](#field) · [Vector](#vector)

<a id="field"></a>

### Field

A number system with addition, subtraction, multiplication, and division by every nonzero element. The rational, real, and complex numbers are examples. A result over one field does not automatically hold over another.

The division requirement is what makes ordinary linear algebra over a field especially flexible: every nonzero pivot can be normalized. A field has a zero element and a multiplicative identity, and those elements must differ. The integers fail the field condition because, for example, 2 has no inverse within the integers.

The chosen field affects more than arithmetic notation. A real rotation can acquire eigenvectors after extending the scalars to the complex numbers. Conversely, a construction that divides by an integer may fail in a finite field when that integer becomes zero. A theorem’s field hypothesis is part of its mathematical content.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Scalar](#scalar)

<a id="vector"></a>

### Vector

An element of a vector space. In the finite examples it is a column of numbers. Its coordinates depend on a chosen representation.

The abstract object and its coordinate list are different things. A polynomial, a sampled signal and a column of numbers can each be vectors in an appropriate space. Once a basis is fixed, a coordinate list describes the object; choosing another basis changes that list without necessarily changing the object.

This distinction matters when comparing calculations in two representations. Before subtracting their coordinate columns, first put both columns in the same coordinate system. Otherwise an apparent discrepancy can come from comparing different descriptions rather than different vectors. The collection’s transfer and coordinate-change examples repeatedly use this separation.

**Quick example:** The pair (2,3) and the polynomial 2+3x are vectors in different declared vector spaces.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Vector space](#vector-space) · [Coordinates](#coordinates)

<a id="vector-space"></a>

### Vector space

A collection of vectors closed under addition and scalar multiplication, with the usual distributive and associative laws. The space of pairs of real numbers is denoted R².

The closure requirements mean that taking sums, differences and scalar multiples never leaves the space. A useful way to check a proposed example is to ask whether it contains zero and whether a general linear combination stays inside it. A plane through the origin can satisfy these conditions; a translated parallel plane generally does not.

Specifying the underlying set alone is insufficient: the scalar field and the addition and scaling operations also belong to the definition. In the finite examples, these choices let us speak consistently about kernels, bases and dimension. Other works may use spaces of functions or infinite sequences with additional analytic structure.

**Quick example:** Pairs (x,y) with x+y = 0 form a vector space; pairs with x+y = 1 do not contain zero.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Field](#field) · [Span](#span) · [Basis](#basis)

<a id="linear-map"></a>

### Linear map

A map T satisfying T(au + bv) = aT(u) + bT(v) for all vectors u, v and allowed scalars a, b. A linear map preserves linear combinations.

Linearity says that one can combine inputs before applying the map or combine their outputs afterward, with the same result. It implies T(0)=0 and makes the values on a basis sufficient to determine the entire map. This is why a finite matrix can encode an operation on infinitely many possible input vectors.

The identity must hold for every allowed linear combination, not just for a few test inputs. A map such as x↦x² can agree with a linear rule at selected points and still fail linearity elsewhere. Packet-by-packet reconstruction of an operation relies on this universal additivity, so nonlinear operations need a separate defect calculation.

**Also called:** Linear transformation.

**Quick example:** T(x,y) = (x+2y,3x) is linear. Adding a fixed nonzero offset would make it affine.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Matrix](#matrix) · [Kernel](#kernel) · [Image](#image)

<a id="matrix"></a>

### Matrix

A rectangular array representing a linear map after bases have been chosen. An m by n matrix takes n coordinates to m coordinates. Each output coordinate is a row multiplied by the input column.

The columns of a matrix are the outputs of the input basis vectors, expressed in the output basis. Thus a matrix stores both an operation and the coordinate choices used to describe it. Multiplying by a column forms the corresponding linear combination of those stored output columns.

Dimensions keep the calculation meaningful: an m-by-n matrix accepts n coordinates and returns m. Changing the input or output basis changes the matrix through the appropriate coordinate maps. Properties such as injectivity belong to the represented map, whereas individual entries and many numerical norm values depend on its description.

**Quick example:** The matrix \[\[1,2\],\[3,4\]\] sends (2,3) to (8,18).

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Linear map](#linear-map) · [Basis](#basis) · [Composition](#composition)

<a id="identity"></a>

### Identity operator

The map I that leaves every input unchanged, so Ix = x. The subscript in I₂ or I₃ specifies the dimension when needed.

The identity is the neutral operation for composition: TI=T and IT=T whenever the types match. Its matrix has ones on the diagonal and zeros elsewhere in any basis of the same space. The relevant space matters, because identities on different spaces are different typed maps.

Reconstruction formulas use the identity to say exactly what has been recovered. SA=I on the original object space means that every original input returns unchanged after analysis and synthesis. It does not also assert AS=I on a larger coefficient space. Keeping the identity’s domain visible prevents these two claims from being confused.

**Also called:** Identity map.

**Quick example:** I₂(2,3) = (2,3). The identity is different from a matrix with every entry equal to one.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Inverse](#inverse) · [Complete packet family](#complete-packet-family)

<a id="span"></a>

### Span

All finite linear combinations of a specified set of vectors. The span of the empty set consists only of the zero vector. With an operator action, one may first apply allowed operators and then take the span.

A span is the collection of everything obtainable by the stated linear combinations, rather than merely the original list of vectors. Adding a vector already in that span does not enlarge it. Adding a vector outside it creates at least one new independent direction in the finite-dimensional setting.

In a seed calculation there are two stages: apply allowed operators to the seeds, then take linear combinations of the generated vectors. The initial seeds may be few even when their generated span is large. A span computation therefore answers a different question depending on whether operator action is allowed before combination.

**Also called:** Linear span.

**Quick example:** The span of (1,1) is the line {(a,a) : a is a scalar}.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Seed](#seed) · [Basis](#basis) · [Linear independence](#linear-independence)

<a id="linear-independence"></a>

### Linear independence

A family is linearly independent when the only linear combination giving zero has every coefficient zero. No member of a finite independent family can be formed from the others.

Independence is the uniqueness condition behind coordinates. If a nontrivial combination of the listed vectors is zero, the same vector can have two different coefficient lists: add that zero combination to any representation. Independence rules out precisely this ambiguity within the chosen family.

For finitely many columns, solving the homogeneous matrix equation tests independence: only the zero coefficient column should map to zero. A family can be independent without spanning the whole target space. To be a basis it must satisfy both requirements, so neither independence alone nor a large number of stored vectors is enough.

**Quick example:** (1,0) and (0,1) are independent, while (1,0) and (2,0) are dependent.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Span](#span) · [Basis](#basis)

<a id="basis"></a>

### Basis

A linearly independent spanning family. Every vector has a unique finite linear combination in that basis. Redundant measurements can describe a vector without forming a basis.

A basis provides a complete coordinate system with no redundancy. Spanning guarantees that each vector can be represented, while independence guarantees that the coefficients are unique. These are separate requirements; a generating list can span successfully while still storing more measurements than a basis needs.

Choosing a basis also determines the matrices of operators and the coefficient rules for products or derivatives. A different basis can make one operation simpler and another more complicated. In the falling-factorial examples, the basis is chosen to simplify finite differences, so its usefulness comes from the operations being studied rather than from a universally preferred coordinate system.

**Quick example:** In the basis {(1,1),(1,−1)}, the vector (4,2) has coefficients (3,1).

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Span](#span) · [Linear independence](#linear-independence) · [Redundant coordinates](#redundancy) · [Finite frame](#finite-frame) · [Falling factorial](#falling-factorial) · [Orthonormal basis](#orthonormal-basis) · [Monic polynomial](#monic-polynomial)

<a id="dimension"></a>

### Dimension

The number of vectors in a basis of a finite-dimensional vector space. In these examples, R² has dimension two even when three redundant measurements are stored.

Dimension measures the number of independent scalar coordinates needed to specify a vector. It does not count the number of entries in every possible representation. An injective map can store a two-dimensional vector as three measurements, but those three measurements then satisfy a relation.

In finite-dimensional linear problems, dimension helps separate information retained from information lost: rank counts independent output directions, and nullity counts independent erased input directions. It also differs from seed rank, because one seed can generate many independent vectors when nontrivial operators are allowed to act on it.

**Quick example:** The subspace spanned by (1,0,0) and (0,1,0) has dimension two inside R³.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Basis](#basis) · [Rank](#rank) · [Seed rank](#seed-rank)

<a id="kernel"></a>

### Kernel

For a linear map T, the vectors sent to zero: ker T = {x : Tx = 0}. A nonzero kernel describes directions that this map cannot distinguish from zero.

The kernel describes invisible changes to an input. If k lies in ker T, then T(x+k)=Tx for every x, so the map cannot distinguish x from x+k. For a linear map, every nonempty fiber is a translate of this same subspace; one kernel therefore describes all of its ambiguities at once.

This makes kernels central to recovery. A requested linear observation F can be reconstructed from a summary R only when every change erased by R is also erased by F. The condition ker R⊆ker F states that requirement directly. A kernel vector violating it supplies a concrete witness that the summary lost needed information.

**Also called:** Nullspace, Null space.

**Quick example:** For R(x,y) = x+y, the kernel is span{(1,−1)}.

**In the worked example:** For the sum map R(a,b) = a+b over R, the vector (1,−1)ᵀ lies in the kernel: R(1,−1) = 0. Adding this vector does not change the observed sum.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Image](#image) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Sufficient summary for a requested output](#sufficient-summary) · [Orthogonal complement](#orthogonal-complement)

<a id="image"></a>

### Image

The outputs actually attained by a map. For a linear map T, im T = {Tx : x is an allowed input} is a subspace of the target. The declared target can be larger than the image.

The image is the set of valid outputs of an operation. In a redundant coordinate system, not every numerical list is valid analyzed data: some lists fail the relations imposed by the analysis map. The image records those consistency requirements as a subspace of the coefficient space.

For example, if A(x,y)=(x,y,x+y), then a triple is in the image exactly when its third entry equals the sum of the first two. A synthesis map may still accept an arbitrary triple, but synthesizing and reanalyzing it can change it into a valid one. That change is a coefficient-space projection, not an identity on all triples.

**Also called:** Range, Range of a linear map.

**Quick example:** The map x ↦ (x,0) has image the horizontal axis, even if its codomain is all of R².

**In the worked example:** For A(a,b) = (a,b,a+b), the image consists of triples whose third coordinate is the sum of the first two. The coordinate vector (0,0,1)ᵀ lies outside it.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Kernel](#kernel) · [Rank](#rank) · [Left inverse](#left-inverse)

<a id="rank"></a>

### Rank

For a finite linear map, the dimension of its image. A matrix has full column rank when its columns are linearly independent, so it has no nonzero input in its kernel.

Rank counts independent output directions, so it measures how many independent linear measurements a map can actually supply. Repeated or linearly dependent rows add storage without increasing rank. Column rank and row rank agree over a field, linking this output-space interpretation to independent measurement rows.

Rank is especially useful when a matrix is rectangular. A map can have full column rank and recover every input while failing to reach its entire codomain. Numerical rank also needs a scale and threshold: a very small computed singular value is not automatically an exact algebraic zero.

**Quick example:** The matrix \[\[1,1\],\[2,2\]\] has rank one because its second row and column add no independent direction.

**Keep in mind:** Matrix rank and seed rank answer different questions.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Dimension](#dimension) · [Image](#image) · [Seed rank](#seed-rank)

<a id="inner-product"></a>

### Inner product

For real vector spaces, a symmetric bilinear pairing with ⟨v,v⟩ &gt; 0 for every nonzero v. It defines lengths and angles. Positive weights give the pairing sum\_i w\_i u\_i v\_i. Complex inner products use conjugate symmetry and conjugate linearity in one argument.

An inner product supplies the geometry missing from bare linear algebra. It tells us which directions are perpendicular and gives a norm through ‖v‖²=⟨v,v⟩. Different positive weights change that geometry, so an averaging map can be orthogonal for one weighted pairing and oblique for another.

Over complex scalars, conjugation is essential: without it, the expression for a vector’s squared length need not be positive. Authors choose which argument is conjugate-linear, and adjoint formulas must follow that convention. When a coordinate transformation changes the metric matrix, transpose symmetry in the new coordinates need not describe orthogonality correctly by itself.

**Quick example:** For u = (1,2), the weighted inner product with weights (1,3) gives ⟨u,u⟩ = 1+12 = 13.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#averages) · [Norm](#norm) · [Orthogonal projector](#orthogonal-projector)

<a id="norm"></a>

### Norm

A nonnegative measure of size that is zero only at the zero vector, scales by the absolute value of a scalar and satisfies the triangle inequality. The Euclidean norm is the square root of the sum of squared coordinates.

A norm measures size but does not necessarily specify angles. The triangle inequality makes error bounds possible: the size of a sum of discrepancies is at most the sum of their sizes. Different norms can emphasize different features, such as the largest coordinate, total absolute magnitude or Euclidean energy.

Every reported residual norm should therefore name its convention. The same vector can have several correct numerical sizes under different norms, and an induced operator norm depends on the chosen norms on both input and output. In infinite-dimensional settings, changing the norm can also change which convergence statements are true.

**Quick example:** The Euclidean norm of (3,4) is 5, while its 1-norm is 7.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Inner product](#inner-product) · [Residual](#residual) · [Tolerance](#tolerance) · [Induced operator norm](#operator-norm) · [Seminorm](#seminorm) · [Hilbert–Schmidt norm](#hilbert-schmidt-norm) · [Linear isometry](#isometry)

<a id="subspace"></a>

### Subspace

A subset of a vector space that contains zero and is closed under addition and scalar multiplication. Kernels and images of linear maps are subspaces.

A subspace is a smaller linear world inside a larger one: the inherited addition and scaling operations still work without leaving it. Homogeneous linear equations define subspaces because combining two solutions produces another solution. Equations with a nonzero offset generally define affine sets instead.

Subspaces can play different roles in a calculation. A kernel describes erased directions, an image describes attainable outputs, and an invariant subspace describes directions preserved by an evolution. Those roles should be checked separately; being a subspace alone says nothing about whether an operator preserves or projects onto it.

**Quick example:** The plane z = 0 in R³ is a subspace; the parallel plane z = 1 is not.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Kernel](#kernel) · [Image](#image)

<a id="nullity"></a>

### Nullity

The dimension of the kernel of a finite-dimensional linear map. It counts independent input directions erased by the map.

Nullity measures how many independent degrees of freedom the map completely erases. If two inputs differ by a kernel vector, they give the same output, so a nullity greater than zero means that unrestricted input recovery is impossible. It does not say that every requested observation is unrecoverable.

For a matrix with n columns, nullity is n minus its rank. This formula refers to the input dimension, not to the number of output rows. Adding dependent output measurements can enlarge the stored result while leaving both rank and nullity unchanged, which is why extra coordinates need not supply extra information.

**Quick example:** The map R(x,y,z) = x+y has kernel {(a,−a,b)}, so its nullity is two.

**In the worked example:** For T(x₁,x₂,x₃) = (x₁+x₂,x₂+x₃), the kernel is span{(−1,1,−1)ᵀ}. It has one free direction, so nullity T = 1.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Kernel](#kernel) · [Dimension](#dimension)

<a id="rank-nullity"></a>

### Rank–nullity identity

For a linear map with finite-dimensional domain V, dim V = rank T + nullity T. The rank concerns the image, not the dimension of the entire declared target.

The identity divides the finite input dimension into two parts: directions visible in the image and directions invisible in the kernel. One way to understand it is to begin with a basis of the kernel and extend that to a basis of the domain; the added basis vectors supply independent output directions.

This count is a bookkeeping identity for a specified linear map. It does not identify the kernel directions, construct a recovery map or establish good numerical conditioning. Those require additional information. In particular, a full-rank matrix can still amplify small input errors severely when it is close to losing rank.

**Also called:** Rank-nullity theorem.

**Quick example:** For R(x,y,z) = x+y, domain dimension 3 equals rank 1 plus nullity 2.

**In the worked example:** The map T(x₁,x₂,x₃) = (x₁+x₂,x₂+x₃) has rank two and a one-dimensional kernel. Its three-dimensional domain therefore satisfies 3 = 2 + 1 = rank T + nullity T.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Rank](#rank) · [Nullity](#nullity)

<a id="injective"></a>

### Injective map

A map that sends distinct inputs to distinct outputs. A linear map is injective exactly when its kernel contains only zero.

Injectivity means that an output identifies at most one input. For a linear map, any collision Tx=Ty is equivalent to T(x−y)=0, which explains the kernel criterion. An injective analysis map therefore retains enough information for a left inverse on its image.

This says nothing about whether every vector in the declared codomain is attained. Redundant measurements often use an injective map into a larger coefficient space, with only a proper subspace consisting of valid measurements. Nor does injectivity guarantee a numerically stable inverse; conditioning controls how accurately that retained information can be recovered.

**Also called:** Injection, One-to-one map.

**Quick example:** The map x ↦ (x,2x) is injective, although it does not reach every pair.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Kernel](#kernel) · [Left inverse](#left-inverse)

<a id="surjective"></a>

### Surjective map

A map whose image is its entire declared target. Surjectivity depends on which target is specified.

Surjectivity means that every requested target value is attainable by some input. It is therefore a statement about both the rule and its declared codomain. The same rule may be surjective when its target is its image and nonsurjective when a larger target is declared.

An output can have many preimages even when the map is surjective. Choosing one preimage for each output gives a right inverse when such a choice is available, but generally does not recover an arbitrary original input. In linear recovery problems, the kernel describes the freedom among those possible preimages.

**Also called:** Surjection, Onto map.

**Quick example:** The map (x,y) ↦ x reaches every real number, although many pairs have the same output.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#kernels) · [Image](#image) · [Rank](#rank)

<a id="isomorphism"></a>

### Linear isomorphism

A bijective linear map between vector spaces over the same field. Its inverse is linear. It preserves the vector-space structure, although lengths need not be preserved.

A linear isomorphism lets us regard two vector spaces as equivalent descriptions of the same linear structure. Both the forward map and its inverse preserve linear combinations. In finite dimensions, an invertible square coordinate matrix provides such an equivalence between coordinate descriptions.

Additional structure needs additional preservation requirements. A linear isomorphism can stretch lengths, fail to preserve a chosen multiplication or change the appearance of an inner product. Accordingly, a vector-space isomorphism is not automatically an isometry or an algebra isomorphism. The collection’s transported-product examples make this distinction concrete.

**Also called:** Invertible linear map.

[Hand-worked example](examples/03_COORDINATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Inverse](#inverse) · [Coordinate change](#coordinate-change)

<a id="direct-sum"></a>

### Direct sum

A decomposition into subspaces in which each vector has a unique sum of components. For two subspaces, uniqueness is equivalent to their intersection containing only zero.

The uniqueness of the component decomposition is the important extra condition. Merely saying that two subspaces span a space allows overlaps and ambiguous components. For an internal direct sum of two subspaces, every vector splits into one vector from each, and their intersection contains only zero.

Orthogonality is a stronger geometric requirement, not part of the algebraic direct-sum definition. Complementary subspaces can meet at an oblique angle. Their associated projectors still reconstruct each vector, but squared lengths of the components need not add to the original squared length without cross terms.

**Quick example:** Every pair (x,y) is uniquely (x,0)+(0,y), the sum of one vector from each coordinate axis.

[Hand-worked example](examples/01_PACKETS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Subspace](#subspace) · [Complete packet family](#complete-packet-family)

<a id="quotient-space"></a>

### Quotient space

The vector space V/W obtained by identifying vectors whose difference lies in a subspace W. A coset x+W records the equivalence class of x.

A quotient keeps an equivalence class rather than a particular representative. Writing x+W means that adding any vector of W makes no difference to the retained description. Addition and scaling of classes are well defined because W is a subspace, so different representatives produce the same resulting class.

For a linear summary R, quotienting its domain by ker R removes exactly the distinctions R forgets. The resulting quotient is naturally isomorphic to im R. Recovering another linear observation from that summary therefore asks whether the observation also ignores those discarded directions, rather than whether a preferred representative can be guessed.

**Quick example:** Modulo span{(1,−1)}, the pairs (2,3) and (4,1) represent the same class because their difference is (2,−2).

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Subspace](#subspace) · [Fiber](#fiber)

<a id="determinant"></a>

### Determinant

A scalar attached to a square matrix. For \[\[a,b\],\[c,d\]\] it is ad − bc. Over a field, a square matrix is invertible exactly when its determinant is nonzero.

The determinant detects invertibility of a square linear coordinate map over a field. Geometrically over the reals, its absolute value is the volume-scaling factor, while its sign records orientation. A zero determinant means that some independent input directions have collapsed into dependence.

Its numerical magnitude is not a general conditioning measure: it mixes the scales of all directions through a product. A diagonal matrix can have determinant one while stretching one direction enormously and shrinking another. Rectangular matrices also need rank or singular-value information rather than a determinant test.

**Quick example:** The matrix \[\[1,2\],\[3,4\]\] has determinant 4−6 = −2 and is invertible over the real numbers.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#elimination) · [Inverse](#inverse) · [Field](#field)

<a id="domain-codomain"></a>

### Domain and codomain

The declared input and target spaces of a map. The codomain includes all permitted outputs, while the image consists of outputs actually attained.

The domain tells us which inputs a formula is required to handle; the codomain tells us where its outputs are declared to live. This information determines whether compositions are legal and what claims such as surjectivity mean. The actual image is obtained only after examining the rule.

Restrictions can materially change a problem. A summary that loses information on all of R² might become injective on a specified line. Conversely, a formula that works on valid analyzed coordinates may fail on arbitrary coefficient lists. Recovery and transfer claims should therefore state their admissible input set as well as their map formulas.

**Quick example:** For T: R² → R³ with T(x,y) = (x,y,0), the domain is R², codomain is R³ and image is a plane.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#typed-paths) · [Image](#image) · [Surjective map](#surjective) · [Typed system](#typed-system)

<a id="affine-map"></a>

### Affine map

A map between vector spaces of the form x↦Lx+c, where L is linear and c is a fixed output vector. The translation c may move zero, so the map is linear exactly when c=0.

An affine map preserves affine combinations, whose coefficients sum to one, but generally fails to preserve the chosen origin. The linear part describes how differences transform: f(x)−f(y)=L(x−y). The offset cancels from this difference, which separates translation from the response to a perturbation.

This makes affine models common when a linear relation is expressed around a nonzero reference state. One can sometimes encode the offset using an additional constant coordinate, but that changes the representation and its constraints. Calling the original map linear without recording the offset would give incorrect zero and superposition tests.

**Also called:** Affine transformation.

**Quick example:** f(x) = 2x+1 is affine; f(0) = 1 shows it is not linear.

**In the worked example:** The rule A(x₁,x₂)=2x₁−x₂+3 is affine. Its linear part is L(x₁,x₂)=2x₁−x₂, and A(0,0)=3.

[Hand-worked example](operators/BASICS.md#2-linear-affine-and-nonlinear-rules) · [Linear map](#linear-map) · [Nonlinear map](#nonlinear-map) · [Operator](#operator)

<a id="row-space"></a>

### Row space

The span of a matrix’s row vectors over its declared coefficient field. When rows represent scalar measurements, their row space is the set of all linear combinations of those measurements.

A row vector acts as a scalar measurement of an input. Taking its row space means allowing all linear combinations of the available measurements. If a desired measurement row lies in that space, its value can be computed from the existing measured values by the same coefficients.

This gives a constructive version of the linear recovery criterion. For example, measuring x+y permits every scalar multiple of that sum, but cannot recover x alone on unrestricted pairs. The row-space condition identifies what can be recovered, while a kernel or collision witness explains why a measurement outside that space cannot be reconstructed.

**Also called:** Row span.

**Quick example:** The rows (1,1) and (2,2) span the one-dimensional row space of \[\[1,1\],\[2,2\]\].

**In the worked example:** The rows (1,1,0) and (0,1,1) span the target row (1,2,1), obtained by adding them. Thus adding the corresponding two measurements recovers that target exactly.

[Hand-worked example](operators/RECOVERY.md#3-linear-recovery-row-spaces-and-kernels) · [Span](#span) · [Rank](#rank) · [Kernel](#kernel) · [Exact recovery from a summary](#exact-recovery)

<a id="covector"></a>

### Covector

A linear functional from a vector space to its coefficient field. With column-vector coordinates, it is stored as a row ℓ and acts by ℓx. Covectors form the dual space. A chosen inner product can identify vectors with covectors, but that identification depends on the metric.

A covector asks a scalar question about a vector. Its row entries are the values of that question on the chosen basis vectors. Under a coordinate change, the row must transform in the opposite direction to the coordinate column so that their scalar pairing remains the same.

For y=Cx, the same question ℓx is represented by ℓC⁻¹ acting on y. Reusing the old row on the new coordinates can change the question unintentionally. An inner product can turn a vector into a covector, but the metric used in that identification must travel with a change of representation.

**Also called:** Linear functional, Dual vector.

**In the worked example:** The sum observation R(a,b) = a+b is the covector (1,1). The requested first-coordinate observation F(a,b) = a is the covector (1,0).

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](operators/catalog/C_COORDINATES.md#op-172) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Linear map](#linear-map) · [Covector pullback](#covector-pullback) · [Inner product](#inner-product) · [Coordinates](#coordinates)

<a id="positive-definite"></a>

### Positive definite matrix

A real symmetric or complex Hermitian matrix Q for which x\*Qx &gt; 0 for every nonzero vector x. It defines an inner product and is invertible. Positive semidefiniteness only requires x\*Qx ≥ 0 and can allow nonzero vectors of zero length.

Positive definiteness says that every nonzero direction has strictly positive quadratic energy. For a finite Hermitian matrix, it is equivalent to all eigenvalues being positive. It ensures invertibility and permits the quadratic form to define a genuine inner product rather than only a seminorm.

The symmetry or Hermitian hypothesis belongs with the positivity statement. In numerical work, small positive eigenvalues can make inversion sensitive even though it remains algebraically valid. Positive semidefiniteness is a different condition: it allows zero directions, so formulas requiring an ordinary inverse may need a range restriction or pseudoinverse instead.

**Also called:** Positive-definite matrix, SPD matrix, HPD matrix.

**Quick example:** diag(1,3) is positive definite because x²+3y² &gt; 0 for every nonzero pair.

**In the worked example:** For the example's analysis matrix, Q = A\*A = \[\[2,1\],\[1,2\]\]. Its quadratic form is a²+b²+(a+b)², which is positive whenever (a,b) ≠ (0,0).

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/K_METRICS.md#op-185) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Positive semidefinite matrix](#positive-semidefinite) · [Inner product](#inner-product) · [Classical frame operator](#classical-frame-operator) · [Metric adjoint](#metric-adjoint)

<a id="seminorm"></a>

### Seminorm

A nonnegative function satisfying absolute homogeneity and the triangle inequality, while allowing a nonzero vector to have value zero. For linear synthesis S from a redundant coefficient space, p(c) = ‖Sc‖ is a seminorm whose zero directions are exactly ker S. Passing to the quotient by those directions gives a norm.

A seminorm measures size while intentionally ignoring some distinctions. If p(c)=‖Sc‖, two coefficient lists differing by an element of ker S have the same synthesized object and the same seminorm. Thus a nonzero stored list can have size zero in the physical quantity being measured.

Passing to equivalence classes modulo the zero directions removes this ambiguity and produces a norm. This is useful for redundant representations, where coordinate differences can be pure gauge. It also explains why a zero seminorm residual may certify agreement of synthesized objects without certifying equality of their original coefficient lists.

**Also called:** Semi-norm.

**Quick example:** p(x,y) = |x| is a seminorm on R² that vanishes on every vertical vector.

**In the worked example:** The coefficient vector g = (−1,−1,1) is nonzero but satisfies ‖Sg‖ = 0 for the example's synthesis map. Its ordinary Euclidean norm is √3.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Norm](#norm) · [Coefficient gauge](#coefficient-gauge) · [Coefficient metric](#coefficient-metric) · [Quotient space](#quotient-space)

<a id="dual-space"></a>

### Dual space

For a vector space V over a field, the vector space V\* of linear scalar-valued functions on V. Its elements are covectors or linear functionals. In finite coordinates a row vector acts on a column vector, but identifying covectors with vectors requires additional choices.

The dual space collects all linear scalar observations on the original space. In finite dimensions its dimension equals the original dimension, but this equal count does not supply a preferred identification of vectors with covectors. A basis determines a corresponding dual basis of questions that extract the individual coordinates.

When an operator changes an object, its pullback changes the questions asked of that object. This is why integration rows, measurement functionals and coordinate covectors often transform contravariantly. Keeping object space and dual space separate helps prevent a transpose or inverse from being placed on the wrong side of a formula.

**Quick example:** On pairs, ℓ(x,y) = 2x−y is a covector. It sends (3,4) to 2.

[Further reading](operators/BASICS.md) · [Covector](#covector) · [Covector pullback](#covector-pullback) · [Inner product](#inner-product)

<a id="orthogonal-complement"></a>

### Orthogonal complement

For a subspace W of an inner-product space, W⊥ consists of all vectors perpendicular to every vector in W. In finite dimensions the space decomposes as the orthogonal direct sum W ⊕ W⊥.

The complement contains the directions invisible to inner-product tests against W. For an orthogonal projection onto W, every vector decomposes into its projected part in W and its residual in W⊥. Their perpendicularity gives a Pythagorean identity for squared norms.

In finite dimensions this decomposition works for every subspace. Infinite-dimensional inner-product spaces require additional care; in a Hilbert space the standard projection theorem uses a closed subspace. An arbitrary algebraic complement can still support a projector, but need not equal the orthogonal complement selected by the chosen geometry.

**Also called:** Perpendicular complement.

**Quick example:** In Euclidean R², the perpendicular complement of span{(1,1)} is span{(1,−1)}.

**Keep in mind:** Perpendicularity depends on the inner product. A weighted inner product can change the complement.

[Further reading](operators/PACKETS.md) · [Subspace](#subspace) · [Inner product](#inner-product) · [Orthogonal projector](#orthogonal-projector) · [Direct sum](#direct-sum)

<a id="orthonormal-basis"></a>

### Orthonormal basis

A basis whose vectors have norm one and are pairwise perpendicular in the chosen inner product. In finite real or complex coordinates, the matrix Q with these basis columns satisfies Q\*Q = I.

Orthonormal coordinates make coefficient extraction especially simple: each coefficient is the inner product with the corresponding basis vector, using the declared complex convention. The squared norm is the sum of squared coefficient magnitudes, so no additional Gram matrix is needed in that coordinate system.

Normalization is essential to these convenient formulas. The unscaled Haar average-and-detail coordinates are perfectly invertible but require weights in their energy identity. A general independent basis also reconstructs vectors exactly, yet can be poorly conditioned or geometrically oblique. Orthonormality adds metric information to the algebraic basis property.

**Quick example:** The Haar vectors (1,1)/√2 and (1,−1)/√2 form an orthonormal basis of Euclidean R².

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Basis](#basis) · [Inner product](#inner-product) · [Orthogonal matrix](#orthogonal-matrix) · [Unitary matrix](#unitary)

<a id="singular-value"></a>

### Singular value

A nonnegative square root of an eigenvalue of A\*A for a real or complex matrix A, with zero-padding conventions stated when needed. The largest singular value is the induced Euclidean operator norm. Singular values describe gain and rank without requiring A to be square.

Singular values describe how strongly a matrix stretches orthogonal input directions after suitable unitary coordinate choices. A zero singular value corresponds to an erased direction; positive ones describe retained gains. This viewpoint applies to rectangular maps, including analysis maps with more measurements than input coordinates.

They differ from eigenvalues because the input and output directions need not be the same. A nonzero nilpotent matrix has only zero eigenvalues but still has positive gain on some inputs. Very small singular values identify sensitive recovery directions, although deciding that one is exactly zero requires more than a floating-point threshold.

**Quick example:** For A = \[\[0,2\],\[3,0\]\], A\*A = diag(9,4), so its singular values are 3 and 2.

**Keep in mind:** A small computed singular value needs a tolerance or enclosure before it is treated as exactly zero.

[Further reading](operators/STABILITY.md) · [Adjoint matrix](#adjoint) · [Gram operator](#gram-operator) · [Induced operator norm](#operator-norm) · [Rank](#rank)

<a id="singular-value-decomposition"></a>

### Singular value decomposition

A factorization A = UΣV\* of a finite real or complex matrix, where U and V are orthogonal or unitary and Σ is rectangular diagonal with nonnegative entries. These entries are the singular values. It separates input directions, gains and output directions.

Read the factorization from right to left: V\* changes to orthonormal input coordinates, Σ scales or erases those coordinates, and U places the results in orthonormal output coordinates. This separates geometry from gain and reveals the map’s rank through its positive singular values.

The same factorization constructs the Moore–Penrose inverse by reciprocating positive singular values and leaving zero ones at zero. Truncating small positive values is an approximation choice, not exact inversion. Such truncation can improve numerical robustness, but its threshold and resulting residual must be reported with the calculation.

**Also called:** SVD.

**Quick example:** The diagonal matrix diag(3,1) already has an SVD with U = V = I and Σ = diag(3,1).

**Keep in mind:** Truncating an SVD changes the operator unless all omitted singular values are zero.

[Further reading](operators/STABILITY.md) · [Singular value](#singular-value) · [Unitary matrix](#unitary) · [Moore–Penrose inverse](#pseudoinverse) · [Rank](#rank)

<a id="bilinear-form"></a>

### Bilinear form

A scalar-valued function B(u,v) linear separately in u and v. Over the real numbers a matrix M gives B(u,v) = uᵀMv. Symmetry, positivity and nondegeneracy are additional properties rather than part of bilinearity.

Bilinearity means that fixing either argument leaves a linear scalar question in the other. A matrix encodes those pairings between basis vectors, so the form can describe interactions or energies without being a positive notion of length. Symmetry and positivity should therefore be checked explicitly.

When coordinates change by y=Cx, a real bilinear-form matrix transforms by inverse factors on both sides, rather than by operator conjugation. For a quadratic expression xᵀMx, the corresponding matrix is C⁻ᵀMC⁻¹. This difference reflects the fact that the form consumes two vector arguments and returns a scalar.

**Quick example:** B(u,v) = u₁v₁−u₂v₂ is symmetric and bilinear, but B((0,1),(0,1)) = −1, so it is not an inner product.

**Keep in mind:** For complex inner products one argument is conjugate-linear. That pairing is sesquilinear.

[Further reading](operators/BASICS.md) · [Inner product](#inner-product) · [Quadratic form](#quadratic-form) · [Positive definite matrix](#positive-definite)

<a id="quadratic-form"></a>

### Quadratic form

In the real finite-dimensional setting, a scalar expression q(x) = xᵀMx, usually written with M symmetric. In complex Hermitian geometry the corresponding real-valued expression is x\*Mx with M Hermitian. Positivity asks whether this value is nonnegative for every input.

A quadratic form combines coordinates in pairs, including cross terms that record interaction between directions. With a symmetric real matrix, an off-diagonal entry appears twice in the expanded expression. For instance, the all-ones two-by-two matrix gives x²+2xy+y² rather than x²+xy+y².

Testing the sign on all vectors distinguishes positive definite, positive semidefinite and indefinite forms. A single negative value disproves positive semidefiniteness and can serve as an exact feasibility witness. In probability, evaluating such a form on a random vector gives a random variable; its distribution needs the vector’s law as additional data.

**Quick example:** With M = \[\[1,1\],\[1,1\]\], q(x,y) = (x+y)². It is nonnegative and vanishes on the nonzero direction (1,−1).

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Bilinear form](#bilinear-form) · [Positive semidefinite matrix](#positive-semidefinite) · [Gaussian quadratic form](#gaussian-quadratic-form)

<a id="triangular-matrix"></a>

### Triangular matrix

A square matrix with every entry on one side of its diagonal zero. A unitriangular matrix also has all diagonal entries equal to one, so it is invertible over any field. Triangular coordinate maps let successive coefficients be recovered in order.

A triangular matrix organizes dependencies in one direction. In a lower-triangular system, the first equation determines the first unknown, then each following equation can use the earlier answers. Nonzero diagonal entries make this successive recovery possible over a field.

Triangular changes of polynomial basis arise because a degree-k basis polynomial uses only powers of degree at most k. Monic basis polynomials give diagonal entries one, so every finite degree truncation is invertible. An infinite triangular array still needs its intended coefficientwise or analytic interpretation stated separately.

**Quick example:** The lower-triangular matrix \[\[1,0\],\[3,1\]\] sends (a,b) to (a,3a+b); recover b by subtracting 3a.

[Further reading](operators/POLYNOMIAL.md) · [Matrix](#matrix) · [Inverse](#inverse) · [Stirling transform](#stirling-transform)

<a id="operators-and-packets"></a>

## Operators, seeds, and packets

How an allowed action generates, selects, and decomposes objects.

[Realization](#realization) · [Seed](#seed) · [Address](#address) · [Projector](#projector) · [Packet](#packet) · [Typed system](#typed-system) · [Operator algebra](#operator-algebra) · [Seed rank](#seed-rank) · [Cyclic vector](#cyclic) · [Orthogonal projector](#orthogonal-projector) · [Complete packet family](#complete-packet-family) · [Mutual annihilation](#mutual-annihilation) · [Invariant subspace](#invariant-subspace) · [Eigenvector](#eigenvector) · [Eigenvalue](#eigenvalue) · [Eigenspace](#eigenspace) · [Diagonalizable operator](#diagonalizable) · [Polynomial in an operator](#polynomial-in-operator) · [Minimal polynomial](#minimal-polynomial) · [Spectral projector](#spectral-projector) · [Commutator](#commutator) · [Typed path](#typed-path) · [Operator relation](#relation) · [Nilpotent operator](#nilpotent) · [Operator](#operator) · [Nonlinear map](#nonlinear-map) · [Tensor product of operators](#tensor-product) · [Oblique projector](#oblique-projector) · [Spectral radius](#spectral-radius) · [Falling-factorial raising operator](#raising-operator) · [Falling-degree operator](#degree-operator) · [Normal matrix](#normal-matrix) · [Involution](#involution) · [Operator orbit](#operator-orbit)

<a id="realization"></a>

### Realization

A way to represent a declared system using concrete spaces and operations while respecting its required relations. A finite matrix realization assigns a space to each type and a matrix to each permitted arrow.

A realization gives an abstract specification something concrete to act on. The specification names objects, permitted operations and relations among compositions; the realization chooses spaces and actual maps that obey those relations. Merely drawing arrows or assigning matrices is insufficient if a required relation fails after the assignment.

For example, a specification with one arrow n and relation n²=0 can be realized by a nonzero square matrix N with N²=0. The relation constrains every input, not just one demonstrated vector. Different realizations can satisfy the same specification while having different dimensions, generating seeds, numerical conditioning or computational costs.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Typed system](#typed-system) · [Operator algebra](#operator-algebra) · [Compatibility](#compatibility)

<a id="seed"></a>

### Seed

Initial generating data from which the allowed operator action produces further elements. Whether a seed is sufficient depends on both the object and the declared action.

A seed is useful because allowed operations can extract more information from it than scalar multiplication alone. Start with the seed, apply the declared legal operator words, and then form linear combinations of the resulting vectors. The size of that generated space depends on both the seed and the action.

With the identity as the only available operator, one seed spans at most one direction. If an operator swaps the two coordinates, the seed (1,0) also generates (0,1), so its operator-generated span is all of R². A claim about sufficient seeds must therefore specify the operator algebra rather than counting initial vectors in isolation.

**In the worked example:** On R², let N(a,b) = (b,0) and v = (0,1). Then Nv = (1,0), so v and its image generate every vector by linear combinations.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Span](#span) · [Seed rank](#seed-rank) · [Cyclic vector](#cyclic)

<a id="address"></a>

### Address

A label for a legal operator path or a packet coordinate. Examples include signal phases, residue classes, and positions in a packet tree. An address identifies a location in a representation, not necessarily a physical location.

An address tells a reader or algorithm where a component belongs in a declared representation. It can encode which operator path was followed, which residue phase was selected or which branch of a refinement tree was retained. The object stored at that address is separate from the label itself.

An address change can be a reversible reorganization without changing the represented data. Deleting an address, identifying several addresses or changing the permitted paths can instead lose distinctions. In a typed system, not every sequence of labels is a legal path: consecutive operations must also have compatible input and output types.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Typed system](#typed-system) · [Packet](#packet) · [Residue class](#residue-class)

<a id="projector"></a>

### Projector

A linear operator P satisfying P² = P. Applying it twice has the same effect as applying it once. This algebraic definition does not require orthogonality.

Idempotence means that every output of P is already settled: if y=Px, then Py=P²x=Px=y. Thus P acts as the identity on its image. Every vector splits algebraically as x=Px+(I−P)x, with the first part in im P and the second in ker P.

The kernel specifies the directions along which the projection is taken. Choosing a different complementary kernel can produce a different projector onto the same image. Orthogonal projection makes a particular choice using an inner product, whereas a general projector may amplify lengths and need not give an additive decomposition of squared energy.

**Also called:** Projection, Idempotent linear operator.

**In the worked example:** On R², P₁(a,b) = (a,0). Applying P₁ again still gives (a,0), so P₁² = P₁.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Orthogonal projector](#orthogonal-projector) · [Packet](#packet) · [Redundant coordinates](#redundancy) · [Oblique projector](#oblique-projector) · [Reconstruction component](#reconstruction-component) · [Fixed point](#fixed-point) · [Involution](#involution)

<a id="packet"></a>

### Packet

In the finite projector example, a selected component Pᵢx or the subspace in which it lies, according to context. Signal, algebraic and arithmetic works may assign the word more specific meanings.

The packet language keeps track of a selected part of an object together with the rule selecting it. In a projector decomposition, Pᵢx is the actual packet value and im Pᵢ is its possible packet space. These are related objects, but a vector in a packet space is not the projector that selected it.

Completeness asks whether all retained packets reconstruct the original object. Transfer blocks then describe how an operation sends one packet into another. A packet decomposition need not be an eigenvector decomposition or an orthogonal split, so diagonal action and energy additivity require additional hypotheses stated in the relevant work.

**In the worked example:** For x = (2,3)ᵀ, the coordinate projectors give packets P₁x = (2,0)ᵀ and P₂x = (0,3)ᵀ. Their sum recovers x.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Complete packet family](#complete-packet-family) · [Address](#address)

<a id="typed-system"></a>

### Typed system

A system that records which objects an operation accepts and returns. A path of operations is legal only when consecutive input and output types agree. Types are part of the mathematical specification.

Types prevent formally written operations from being combined when their meanings do not match. A measurement row accepts a state vector and returns a scalar; it cannot generally be followed by a map expecting the original state. The dimensions of finite matrices provide a concrete version of these input and output restrictions.

Typing alone does not establish a system’s equations. Two paths can both be legal yet give different maps. A realization must satisfy the declared relations between legal paths as well as respect their types. This separates a malformed expression from a well-formed expression that fails a proposed mathematical identity.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#typed-finite-expressions) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Linear map](#linear-map) · [Composition](#composition) · [Realization](#realization)

<a id="operator-algebra"></a>

### Operator algebra

In the finite linear setting, a collection of linear operators closed under sums, scalar multiples, and composition. When a unital algebra is intended, the identity operator is included.

The algebra specifies the allowed linear ways to act: one may compose available operators, add them and scale them. Enlarging this collection can increase what a seed generates without changing the underlying vector space. Thus the action is part of the data in any generator-counting problem.

Composition is generally noncommutative, so reversing two allowed operators can change their result. A unital algebra also includes the empty action through the identity. Infinite-dimensional uses of the phrase may impose topology, norm closure or adjoint closure; the finite algebraic definition here does not automatically include those extra requirements.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Composition](#composition) · [Seed](#seed) · [Invariant subspace](#invariant-subspace)

<a id="seed-rank"></a>

### Seed rank

In the finite linear example, the least number of seeds whose operator-generated span is the whole space. More general definitions can involve modules, dense generation, and cardinalities. Read the definition in the chosen work.

Seed rank measures how many independent starting sources are needed when the operator action does part of the generating work. For a chosen family of seeds, take the span of all their allowed operator images. The family is sufficient when that span equals the required space or satisfies the work’s stated generation condition.

This can be much smaller than vector-space dimension. A cyclic vector gives seed rank one even in a space with many basis directions. Changing the action can change seed rank, and restricting to scalar multiples of the identity returns the usual need for a basis-sized generating family in finite dimensions.

**In the worked example:** For N(a,b) = (b,0) on R², one seed v = (0,1) suffices. With only the zero operator and the identity, two seeds are needed on the same space.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Seed](#seed) · [Span](#span) · [Rank](#rank)

<a id="cyclic"></a>

### Cyclic vector

For a single linear operator T, a vector v is cyclic when v, Tv, T²v and further iterates span the space under consideration. One cyclic vector is enough to generate that operator module.

A cyclic vector packages enough starting information for repeated application of one operator to generate the whole space by linear combination. In a d-dimensional space, this can be checked by the rank of the d-column matrix \[v,Tv,…,Tᵈ⁻¹v\]. Later iterates supply no new directions once the generated span becomes invariant.

The vector itself need not visit every vector as an orbit point: linear combinations of orbit points are allowed. Cyclicity also depends on T. A nonzero vector is cyclic for a scalar identity action only in dimension one, whereas suitable nontrivial operators can have cyclic vectors in much larger spaces.

**Also called:** Cyclic seed.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Seed](#seed) · [Span](#span)

<a id="orthogonal-projector"></a>

### Orthogonal projector

A projector onto a subspace whose residual x − Px is perpendicular to that subspace in the specified inner product. In ordinary real Euclidean coordinates its matrix is symmetric as well as idempotent.

Orthogonal projection keeps the component in the target subspace and leaves a perpendicular residual. This makes the projected point a nearest point in the induced norm in the finite-dimensional setting. It also gives ‖x‖²=‖Px‖²+‖x−Px‖² because the cross term vanishes.

The familiar test P\*=P assumes orthonormal coordinates for the stated inner product. With metric matrix G, self-adjointness instead reads P\*G=GP. Changing coordinates while retaining an inappropriate Euclidean metric can therefore make a mathematically orthogonal projection appear nonsymmetric or lead to an incorrect energy calculation.

**Also called:** Orthogonal projection.

**In the worked example:** With weights (1,3,2), the averaging map sends (2,6,9)ᵀ to (5,5,9)ᵀ. Its residual (−3,1,0)ᵀ has weighted inner product −3a + 3a = 0 with every retained vector (a,a,b)ᵀ. The averaging matrix is not symmetric in ordinary coordinates.

**Keep in mind:** Orthogonality depends on the inner product. Weighted averaging need not have a symmetric matrix in ordinary coordinates.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Inner product](#inner-product)

<a id="complete-packet-family"></a>

### Complete packet family

In these finite examples, projectors Pᵢ with PᵢPⱼ = 0 for distinct indices and sum\_i Pᵢ = I. These identities decompose every vector as x = sum\_i Pᵢx.

The sum-to-identity condition guarantees that no component is missing. Mutual annihilation guarantees that the algebraic selections do not overlap in a way that survives applying one projector after another. Together they give a direct-sum decomposition into the packet ranges and recover every input by summing its packet values.

Each condition has its own role. A partial family can remain idempotent and mutually annihilating while failing to reconstruct the whole space. Conversely, arbitrary reconstruction components can sum to the identity without being projectors individually. Completeness of an algebraic packet family also does not establish orthogonality in a chosen metric.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Mutual annihilation](#mutual-annihilation) · [Reconstruction](#reconstruction)

<a id="mutual-annihilation"></a>

### Mutual annihilation

The relation PᵢPⱼ = 0 whenever i and j differ. Applying one selection after a different selection gives zero. For a pair of projectors, both orders must be checked.

The relation says that a vector already selected by one projector has zero component under the other selection. It is an algebraic statement about ordered products, rather than a statement about the lengths or angles of the selected vectors. Both products PᵢPⱼ and PⱼPᵢ matter for an unordered pair.

For complete projector families, these zero products make component bookkeeping unambiguous and support reconstruction and block-composition formulas. Orthogonal projectors onto perpendicular subspaces satisfy the relation, but nonorthogonal direct-sum projectors can satisfy it too. The word annihilation here concerns operator composition, not physical destruction of a state.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Complete packet family](#complete-packet-family)

<a id="invariant-subspace"></a>

### Invariant subspace

A subspace W preserved by an operator T, meaning T(W) is contained in W. Preservation does not require T to act as the identity on W.

Invariance means that an input starting in W stays in W after the operation, although its value can change substantially there. The restriction of T to W is then an operator on W in its own right. This permits an exact smaller state description for trajectories known to remain in that subspace.

With a projector P onto W, invariance is equivalent to (I−P)TP=0: there is no leakage from retained inputs into discarded outputs. The reverse cross-block can still be nonzero. Invariance of a subspace should therefore be distinguished from a reducing decomposition in which both complementary pieces are preserved.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#seeds) · [Span](#span) · [Operator algebra](#operator-algebra)

<a id="eigenvector"></a>

### Eigenvector

A nonzero vector v for which Tv = λv. The scalar λ is the associated eigenvalue. Zero is excluded from the definition of eigenvector.

An eigenvector identifies a direction on which the operator acts by one scalar. The vector may grow, shrink, reverse sign or rotate in complex phase according to its eigenvalue, but no new direction appears in that one-dimensional subspace. Every nonzero scalar multiple of the eigenvector has the same property.

An eigenvector is always nonzero; allowing zero would make every scalar appear to be an eigenvalue. A single eigenvector also need not describe the operator’s behavior on other inputs. Building an entire basis of eigenvectors is the stronger diagonalizability condition, and some operators do not have such a basis.

**Also called:** Characteristic vector.

**Quick example:** For T = diag(2,3), the nonzero vector (1,0) is an eigenvector with eigenvalue 2.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Eigenvalue](#eigenvalue) · [Invariant subspace](#invariant-subspace)

<a id="eigenvalue"></a>

### Eigenvalue

A scalar λ such that Tv = λv for some nonzero v over the specified field. A real matrix may have no real eigenvalue even though it has eigenvalues over the complex numbers.

Eigenvalues reveal scalar behavior on invariant directions. Repeated powers multiply an eigenvector by λⁿ, which makes them useful for studying iteration. They depend on the coefficient field: a quarter-turn matrix has complex eigenvalues i and −i but no real eigenvector direction.

Eigenvalues alone can miss large one-step or transient amplification in a nonnormal matrix. They also do not describe the gain of a rectangular map, for which singular values are more appropriate. A spectral claim should state the field, multiplicities and structural assumptions under which eigenvalue information is being used.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Eigenvector](#eigenvector) · [Field](#field) · [Singular value](#singular-value) · [Normal matrix](#normal-matrix)

<a id="eigenspace"></a>

### Eigenspace

For an operator T and scalar λ, the kernel of T − λI. It includes zero and all eigenvectors with eigenvalue λ.

The eigenspace gathers all vectors on which T acts as multiplication by the same λ, including zero so that the collection forms a subspace. It is obtained by solving the homogeneous equation (T−λI)v=0. Its dimension counts independent eigenvector directions for that eigenvalue.

That dimension need not equal the multiplicity of λ as a root of the characteristic polynomial. A defective operator can have too few eigenvectors even when its eigenvalues are known exactly. Spectral projectors onto ordinary eigenspaces therefore need the diagonalizable setting used in the introductory example or a more general spectral construction.

**Quick example:** For T = diag(2,2,3), the eigenvalue-2 eigenspace is the plane {(x,y,0)}.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Kernel](#kernel) · [Eigenvector](#eigenvector)

<a id="diagonalizable"></a>

### Diagonalizable operator

An operator that has a basis of eigenvectors over the stated field. Equivalently, its matrix becomes diagonal after an invertible change of basis.

An eigenbasis changes a coupled operation into independent scalar actions: in those coordinates T becomes a diagonal matrix. Applying a polynomial or a repeated power then amounts to applying the corresponding scalar function to each diagonal entry. This is an exact algebraic simplification of the operator.

The eigenbasis need not be orthonormal or well conditioned. A diagonalizable matrix can still have large coordinate amplification when the basis change is poorly conditioned. Normal complex matrices provide the stronger orthonormal-eigenbasis situation; a nonzero nilpotent matrix provides a simple example that is not diagonalizable at all.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Basis](#basis) · [Eigenvector](#eigenvector) · [Coordinate change](#coordinate-change)

<a id="polynomial-in-operator"></a>

### Polynomial in an operator

Substitute T into p(t) = a₀ + a₁t + ⋯ + aₙtⁿ to obtain p(T) = a₀I + a₁T + ⋯ + aₙTⁿ. The constant term acts through the identity operator.

Operator powers mean repeated composition, so p(T) combines several iteration lengths of the same operation. The constant coefficient multiplies I rather than every matrix entry. This convention makes polynomial identities transferable from scalar polynomials to their evaluations at one fixed operator.

For a nilpotent N with N²=0, all terms involving N² or higher vanish, so every polynomial in N reduces to a₀I+a₁N. In spectral examples, interpolation polynomials can select eigenspaces. These calculations concern one operator; substituting several noncommuting operators into a multivariable expression requires an ordering convention.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Operator algebra](#operator-algebra) · [Identity operator](#identity)

<a id="minimal-polynomial"></a>

### Minimal polynomial

For a linear operator on a nonzero finite-dimensional space over a field, the monic polynomial of least degree with m(T) = 0. It records an exact operator relation.

The minimal polynomial is the shortest monic polynomial relation satisfied by the entire operator. If m has degree d, its equation expresses Tᵈ as a linear combination of lower powers. Higher powers can consequently be reduced using the same relation, which is useful in exact operator calculations.

It must annihilate every input, unlike a relation satisfied only by the orbit of one particular vector. It also differs from the characteristic polynomial, although the latter is an annihilating polynomial by Cayley–Hamilton. Repeated factors in the minimal polynomial record structure that an eigenvalue list alone can miss.

**Quick example:** For T = diag(2,3), the minimal polynomial is (t−2)(t−3).

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Polynomial in an operator](#polynomial-in-operator) · [Operator relation](#relation)

<a id="spectral-projector"></a>

### Spectral projector

In the diagonalizable finite example, the projector onto one eigenspace along the sum of the others. Distinct eigenvalues allow a polynomial interpolation formula for these projectors.

In the finite diagonalizable setting, a polynomial can be chosen to equal one at a selected eigenvalue and zero at all the others. Evaluating it at T gives the corresponding eigenspace projector. For distinct eigenvalues λⱼ, its factors divide by differences λᵢ−λⱼ, so distinctness is essential to this formula.

These projectors sum to the identity and reconstruct both vectors and the operator through its spectral components. They need not be orthogonal when the eigenbasis is oblique. Nondiagonalizable operators require additional generalized-eigenspace structure; simply reusing the elementary interpolation formula can omit part of the operator.

**Also called:** Eigenprojector.

**In the worked example:** For T(a,b) = (2a+b,3b), the projectors P₂ = 3I−T and P₃ = T−2I split (2,3)ᵀ into (−1,0)ᵀ and (3,3)ᵀ. The identity T = 2P₂+3P₃ then gives T(2,3)ᵀ = (7,9)ᵀ.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#spectral) · [Projector](#projector) · [Eigenspace](#eigenspace) · [Diagonalizable operator](#diagonalizable)

<a id="commutator"></a>

### Commutator

For operators on the same space, \[A,B\] = AB − BA. A zero commutator means the two orders of composition agree.

The commutator isolates the failure of two operations to be interchangeable. Applied to x, it compares the actual outputs ABx and BAx in the same space. A nonzero result for even one input disproves commutation, while proving the operator commutator zero establishes agreement on every input.

This is useful for filtering versus coarsening, changing coordinates versus applying an operation, and raising versus lowering degree. A commutator identity can itself encode structure, such as ΔA−AΔ=I on polynomials. Finite truncations may introduce boundary terms, so an identity on the full space need not survive dropping the highest coordinate.

**Quick example:** For P = diag(1,0) and T swapping coordinates, PT−TP = \[\[0,1\],\[−1,0\]\].

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#typed-paths) · [Composition](#composition) · [Operator algebra](#operator-algebra)

<a id="typed-path"></a>

### Typed path

A sequence of arrows in which each output type matches the next input type. Its realization is the corresponding ordered composition. An empty path at a type acts as its identity.

A typed path records a legal chain of operations, including its starting and ending types. Its realized matrix product is read from right to left when column-vector conventions are used. The intermediate types explain which matrices are being multiplied rather than merely supplying a dimensional coincidence.

Different paths can have the same endpoints without being equivalent. A declared relation may identify their composites, and a realization must respect that relation. The empty path supplies the identity at its own type, allowing paths of length zero to participate consistently in composition and algebraic equations.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#typed-paths) · [Typed system](#typed-system) · [Composition](#composition) · [Identity operator](#identity)

<a id="relation"></a>

### Operator relation

A required equality between legal operator expressions, such as T² = 0. In a typed system, both sides must have the same input and output types.

A relation is an equation that the allowed operations are required to satisfy. It can describe nilpotence, commutation, reconstruction or a more complicated equality of paths. Its significance is universal within the stated model: both sides act identically on every admissible input of their common type.

Testing a few vectors can suggest a relation but does not generally prove it. In a finite linear space, checking a spanning family can suffice because linearity extends the equality to every vector. A proposed realization is valid only when all required relations hold, not just when its maps have the correct sizes.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#typed-paths) · [Typed path](#typed-path) · [Realization](#realization) · [Minimal polynomial](#minimal-polynomial)

<a id="nilpotent"></a>

### Nilpotent operator

An operator N for which Nᵏ = 0 for some positive integer k. It can be nonzero. The smallest such k on a nonzero space is its nilpotency index.

Nilpotence means that sufficiently many repeated applications erase every input, even if earlier applications do something nontrivial. A coordinate shift that eventually moves every entry beyond the retained finite range is a basic model. For N²=0, applying N twice always gives zero, but applying it once can have a large effect.

Finite geometric identities then become exact: if Nᵏ=0, the inverse of I−N is I+N+⋯+Nᵏ⁻¹. No convergence argument is required. All eigenvalues of a nilpotent matrix are zero, which also illustrates why zero spectral radius does not imply that the operator itself or its one-step norm is zero.

**Also called:** Nilpotent linear map, Nilpotent endomorphism.

**Quick example:** N = \[\[0,1\],\[0,0\]\] is nonzero, but N² = 0.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Operator algebra](#operator-algebra) · [Minimal polynomial](#minimal-polynomial)

<a id="operator"></a>

### Operator

A specified rule T:X→Y taking each allowed input to an output of the declared type. The word alone does not imply linearity, invertibility, or continuity. Those are additional properties of the rule.

An operator is first a rule with a specified domain and output type. Its extra properties must then be established: linearity concerns combinations, continuity concerns limits, invertibility concerns recovery and boundedness concerns norm growth. The same written formula can have different properties on different declared domains.

This broad usage lets the collection discuss matrices, coefficient selectors, nonlinear summaries and differential operations in one language. It does not justify applying a linear identity to every operator. Before decomposing an output into packet contributions or moving an operation between coordinates, check the hypotheses needed by that particular transfer formula.

**In the worked example:** R(x₁,x₂)=x₁+x₂ maps a pair to a scalar, while B(s)=(s,0) maps a scalar to a pair. Thus RB and BR act on different spaces.

[Hand-worked example](operators/BASICS.md#1-typed-operators-domains-and-codomains) · [Linear map](#linear-map) · [Domain and codomain](#domain-codomain) · [Composition](#composition)

<a id="nonlinear-map"></a>

### Nonlinear map

A map between vector spaces that does not satisfy the linear-combination identity for all allowed vectors and scalars. Splitting its input into packets need not split its output into the sum of the separate packet outputs.

Nonlinearity allows interactions that disappear when inputs are examined separately. For f(x,y)=xy, both coordinate-axis restrictions vanish, yet f(2,3)=6. Adding the two isolated packet outputs therefore fails to reproduce the output of the combined input, even though the input itself splits exactly.

Such behavior motivates pointwise transfer defects and explicitly retained interaction terms. A nonlinear map can still be invertible, smooth or well conditioned on a specified domain; nonlinearity does not itself mean information loss. Likewise, a local linear approximation may be useful without making the original operation globally linear.

**Also called:** Nonlinear operator.

**In the worked example:** For f(x₁,x₂)=x₁x₂, f(1,0)+f(0,1)=0 but f((1,0)+(0,1))=1. The two input directions interact.

[Hand-worked example](operators/BASICS.md#2-linear-affine-and-nonlinear-rules) · [Linear map](#linear-map) · [Affine map](#affine-map) · [Pointwise transfer defect](#transfer-defect)

<a id="tensor-product"></a>

### Tensor product of operators

For linear maps A:X→X′ and B:Y→Y′, the linear map A⊗B determined by (A⊗B)(x⊗y)=Ax⊗By. Choosing bases represents it by a Kronecker matrix on the tensor-product coordinates.

The tensor product builds a joint linear action from separate actions on two factors. On a decomposable input x⊗y, each operator acts on its own factor, and linearity extends this prescription to sums of such inputs. In chosen bases, the Kronecker matrix records the resulting combined coordinates.

The joint space has product dimension in the finite setting, not the sum of the two dimensions. Moreover, a general joint vector need not be one decomposable tensor. This distinction is particularly important for quantum systems, where product operations are well defined even on states that cannot be written as a single product state.

**Also called:** Tensor product, Kronecker product of matrices.

**In the worked example:** With A=diag(2,3) and B the two-coordinate swap, A⊗B sends (1,2,0,0)ᵀ to (4,2,0,0)ᵀ. It acts on four coordinates, while AB acts on two.

[Hand-worked example](operators/ALGEBRA.md#7-tensor-products-and-kronecker-matrices) · [Linear map](#linear-map) · [Composition](#composition) · [Matrix](#matrix)

<a id="oblique-projector"></a>

### Oblique projector

A linear projector whose range and kernel are complementary but not perpendicular in the chosen inner product. It reconstructs by x=Px+(I−P)x, while the two pieces need not give an orthogonal energy decomposition.

An oblique projection keeps a vector in its range while removing a component along a chosen complementary direction. The algebraic identities P²=P and x=Px+(I−P)x remain exact. What changes from orthogonal projection is the angle between the two pieces.

The pieces can be large and nearly cancel, so an oblique projector can have norm much larger than one. Squared component norms then do not simply add to the squared norm of x. This is why exact reconstruction and good numerical behavior are separate questions, and why an energy calculation must carry its metric assumptions.

**Also called:** Oblique projection.

**In the worked example:** P(x₁,x₂)=(x₁+x₂,0) splits (2,3)ᵀ as (5,0)ᵀ+(−3,3)ᵀ. Their squared Euclidean lengths sum to 43, although the original squared length is 13.

[Hand-worked example](operators/PACKETS.md#3-orthogonal-and-oblique-projectors) · [Projector](#projector) · [Orthogonal projector](#orthogonal-projector) · [Inner product](#inner-product) · [Induced operator norm](#operator-norm)

<a id="spectral-radius"></a>

### Spectral radius

For an n by n complex matrix with n ≥ 1, the largest absolute value of its eigenvalues. For a real matrix, use its complex eigenvalues. This scalar need not equal the largest one-step amplification measured by an induced norm.

Spectral radius records the largest eigenvalue magnitude and helps describe repeated application, especially asymptotically. For an eigenvector, powers scale by λⁿ. For a general matrix, however, interactions and nonnormality can produce behavior that is not visible from this largest magnitude alone.

A nonzero nilpotent matrix has spectral radius zero and can still strongly amplify some inputs on its first application. An induced operator norm measures that worst-case one-step gain instead. Bounds based on spectral radius should therefore retain whatever hypotheses justify passing from eigenvalue information to finite-step or stability conclusions.

**In the worked example:** N=\[\[0,M\],\[0,0\]\] with M&gt;0 has spectral radius zero and Euclidean operator norm M. Since N²=0, this large one-step gain disappears at the second power.

[Hand-worked example](operators/STABILITY.md#6-spectrum-and-nonnormal-growth) · [Eigenvalue](#eigenvalue) · [Induced operator norm](#operator-norm) · [Nilpotent operator](#nilpotent)

<a id="raising-operator"></a>

### Falling-factorial raising operator

On rational polynomials, the operator Af(x)=x f(x−1), which sends bₖ to bₖ₊₁. It is multiplication by the source variable transported through Φ(zᵏ)=bₖ, so A=Φ(z·)Φ⁻¹.

The shift in the argument is what makes A raise falling-factorial degree. Ordinary multiplication by x would give x bₖ(x), whereas A gives x bₖ(x−1)=bₖ₊₁(x). The two operations agree on some simple inputs but are different operators on the polynomial space.

Together with forward difference, A forms a raising-and-lowering pair: Δbₖ=k bₖ₋₁ and ΔA−AΔ=I. A degree-d input may be raised to degree d+1. Keeping only a square degree-d truncation can therefore discard a necessary intermediate term and change the commutator at the upper boundary.

**Also called:** Raising operator in the polynomial example.

**In the worked example:** A b₂=x(x−1)(x−2)=b₃. Together with Δbₖ=k bₖ₋₁, this gives (ΔA−AΔ)bₖ=bₖ.

**Keep in mind:** The identity ΔA−AΔ=I is on the full polynomial space. A finite square truncation that drops the highest raised degree changes the boundary calculation.

[Hand-worked example](operators/POLYNOMIAL.md#3-raising-and-degree-operators) · [Falling factorial](#falling-factorial) · [Forward difference](#forward-difference) · [Falling-degree operator](#degree-operator) · [Commutator](#commutator)

<a id="degree-operator"></a>

### Falling-degree operator

On rational polynomials, N=AΔ with A the falling-factorial raising operator. Explicitly, Nf(x)=x(f(x)−f(x−1)), and Nbₖ=k bₖ. Its eigenvalue records falling degree in this basis.

The falling-factorial basis turns N into a diagonal degree counter: each bₖ is multiplied by k. Its explicit backward-difference expression follows by first lowering with Δ and then raising with A. This operator is transported from ordinary degree counting in the source polynomial coordinates.

The word degree refers to the chosen eigenbasis, not to blindly inspecting coefficients in any other representation. Over characteristic zero, distinct nonnegative integer degrees give distinct eigenvalues. In positive characteristic those eigenvalues can coincide, so polynomial functions of N can lose the ability to distinguish degrees that remain different as polynomials.

**Also called:** Degree operator in the falling-factorial basis.

**In the worked example:** For b₃=x(x−1)(x−2), Nb₃=3b₃.

**Keep in mind:** In positive characteristic, different degrees can give the same eigenvalue. Over F₃, b₀ and b₃ both have eigenvalue zero, so a polynomial in N cannot separate them.

[Hand-worked example](operators/POLYNOMIAL.md#3-raising-and-degree-operators) · [Falling-factorial raising operator](#raising-operator) · [Forward difference](#forward-difference) · [Eigenvalue](#eigenvalue) · [Residue coefficient selector](#coefficient-selector)

<a id="normal-matrix"></a>

### Normal matrix

A complex square matrix T satisfying T\*T = TT\*. In finite complex dimensions, normal matrices admit an orthonormal eigenbasis. Hermitian and unitary matrices are normal; an arbitrary diagonalizable matrix need not be normal.

Normality is the compatibility condition between an operator and its adjoint that permits a unitary eigenbasis over the complex numbers. In those coordinates, the operation consists of independent scalar actions without an oblique basis change. This makes spectral and Euclidean norm information fit together particularly well.

Hermitian and unitary matrices satisfy this condition for different reasons: one equals its adjoint, while the other has its adjoint as its inverse. A diagonalizable matrix with a poorly conditioned eigenbasis need not be normal. The property depends on the inner product through the adjoint, so it is not preserved by every arbitrary similarity change.

**Quick example:** The nonzero nilpotent matrix \[\[0,1\],\[0,0\]\] is not normal: T\*T = diag(0,1), while TT\* = diag(1,0).

[Further reading](operators/STABILITY.md) · [Adjoint matrix](#adjoint) · [Hermitian matrix](#hermitian) · [Unitary matrix](#unitary) · [Diagonalizable operator](#diagonalizable)

<a id="involution"></a>

### Involution

An operation U whose square is the identity: U² = I. Applying it twice restores the input. A linear involution over a field where 2 is invertible splits the space into its +1 and −1 eigenspaces via (I+U)/2 and (I−U)/2.

An involution is a reversible operation whose inverse is itself. The first application may change an object, but the second restores it exactly. When 2 is invertible, averaging x with Ux selects the fixed part, while taking half their difference selects the sign-reversing part.

This explains the even–odd polynomial split under reflection f(x)↦f(−x). It also distinguishes involutions from projectors: a projector satisfies P²=P, whereas an involution satisfies U²=I. An involution can be oblique with respect to a chosen metric, so self-inversion alone does not guarantee length preservation.

**Quick example:** Reflection of a polynomial, Uf(x) = f(−x), is an involution. Its +1 and −1 parts are the even and odd polynomials.

**Keep in mind:** The identity U² = I does not by itself make U orthogonal or unitary.

[Further reading](operators/POLYNOMIAL.md) · [Projector](#projector) · [Eigenvalue](#eigenvalue) · [Unitary matrix](#unitary)

<a id="operator-orbit"></a>

### Operator orbit

The set of outputs obtained from one input by the declared allowed operations. For a single operator T, its forward orbit is {v,Tv,T²v,…}. Taking the linear span of an orbit is a further step in the definition of a cyclic vector.

An orbit follows what the permitted action can actually reach from a starting object. With one forward operator, it records successive iterates. With a group action, inverses may also be allowed; with a typed system, only paths whose operations match the current type can be followed.

The orbit and its linear span answer different questions. A two-point orbit can span a two-dimensional space, and a finite cyclic orbit can impose a strict phase restriction even when every point has the same norm. Reachability arguments must specify the permitted action rather than replace it with all imaginable linear combinations or continuous motions.

**Quick example:** If T swaps two coordinates, the orbit of (1,0) is {(1,0),(0,1)}; its span is all of R².

[Further reading](examples/02_SEEDS.md) · [Seed](#seed) · [Cyclic vector](#cyclic) · [Span](#span) · [Address](#address)

<a id="coordinates-and-transfer"></a>

## Coordinates and transfer

How descriptions change and operations move between components.

[Coordinates](#coordinates) · [Analysis and synthesis](#analysis-synthesis) · [Transfer block](#transfer-block) · [Coordinate change](#coordinate-change) · [Inverse](#inverse) · [Left inverse](#left-inverse) · [Redundant coordinates](#redundancy) · [Composition](#composition) · [Operator conjugation](#conjugation) · [Intertwiner](#intertwiner) · [Block matrix](#block-matrix) · [Schur complement](#schur-complement) · [Elimination](#elimination) · [Orthogonal matrix](#orthogonal-matrix) · [Normalization](#normalization) · [Right inverse](#right-inverse) · [Transported product](#transported-product) · [Leakage from a retained packet](#packet-leakage) · [Pointwise transfer defect](#transfer-defect) · [Finite frame](#finite-frame) · [Frame bounds](#frame-bounds) · [Classical frame operator](#classical-frame-operator) · [Canonical dual synthesis](#canonical-dual) · [Moore–Penrose inverse](#pseudoinverse) · [Coefficient projection](#coefficient-projection) · [Reconstruction component](#reconstruction-component) · [Coefficient gauge](#coefficient-gauge) · [Coefficient metric](#coefficient-metric) · [Metric adjoint](#metric-adjoint) · [Covector pullback](#covector-pullback) · [Operator compression](#compression) · [Linear isometry](#isometry) · [Algebra homomorphism](#algebra-homomorphism)

<a id="coordinates"></a>

### Coordinates

Values describing an object relative to a chosen representation. Coordinates can be unique basis coefficients or redundant measurements, depending on the setup.

A coordinate list is meaningful only with its decoding convention. In basis coordinates, every list represents one vector and every vector has one list. In redundant analysis coordinates, valid lists satisfy relations, and several arbitrary lists can synthesize to the same vector.

When a calculation moves between representations, carry the maps and their directions with the numbers. Matching list lengths is insufficient to show that two lists describe the same object. This is particularly important when one stage stores ordinary polynomial coefficients and another stores falling-factorial coefficients or packet measurements.

**In the worked example:** The coordinate change C(a,b) = (a + b/2,b) sends x = (2,3)ᵀ to y = (7/2,3)ᵀ. These describe the same object in two coordinate systems.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Basis](#basis) · [Coordinate change](#coordinate-change) · [Redundant coordinates](#redundancy)

<a id="analysis-synthesis"></a>

### Analysis and synthesis

Analysis sends an object to coordinates. Synthesis returns an object from coordinates. In the finite linear model, A and S are linear maps and exact reconstruction is the identity SA = I.

Analysis describes what is measured or stored, while synthesis describes how those stored values are combined into an object. The order SA begins with an original vector, analyzes it and then reconstructs it. Exact reconstruction requires this composite to fix every vector in the stated input space.

The reverse order AS begins with a coefficient list. In a redundant representation it generally removes coefficient inconsistencies or gauge components instead of acting as the identity. Keeping these two spaces visible explains how exact object reconstruction can coexist with nonunique coefficient descriptions.

**In the worked example:** The analysis A(a,b) = (a,b,a+b) sends (2,3)ᵀ to (2,3,5)ᵀ. The example’s synthesis S returns (2,3)ᵀ, with SA = I₂.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Left inverse](#left-inverse) · [Coordinates](#coordinates) · [Reconstruction](#reconstruction) · [Finite frame](#finite-frame) · [Canonical dual synthesis](#canonical-dual) · [Reconstruction component](#reconstruction-component)

<a id="transfer-block"></a>

### Transfer block

The part of an operation connecting a source component to a target component. With source projector Pᵢ, target projector Qⱼ and operator T, the block is QⱼTPᵢ. Complete source and target families allow the blocks to reconstruct T.

Read QⱼTPᵢ from right to left: select input packet i, apply T, then retain output packet j. The two indices therefore name different roles, even when input and output spaces happen to coincide. A block may represent movement between scales, coordinates, phases or other declared components.

Summing every block reconstructs T when both projector families sum to their respective identities. Dropping cross-blocks asserts that some interactions are negligible or absent; the resulting residual must be checked. Diagonal packet blocks alone need not reproduce an operator that mixes the selected components.

**In the worked example:** For T = \[\[1,2\],\[3,4\]\], the coordinate block P₁TP₂ sends (2,3)ᵀ to (6,0)ᵀ. It carries source coordinate 2 into target coordinate 1.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Projector](#projector) · [Composition](#composition) · [Reconstruction](#reconstruction)

<a id="coordinate-change"></a>

### Coordinate change

A transformation between descriptions of the same object. In the invertible linear example the convention is y = Cx, so x = C⁻¹y. Keeping track of the direction prevents inverse formulas from being swapped.

The equation y=Cx fixes which direction the coordinate matrix acts. To apply an original operator T to a vector stored as y, first recover x=C⁻¹y, apply T, then convert the output as appropriate. This sequence derives the transported operator rather than relying on a memorized inverse placement.

A coordinate change preserves the represented object but need not preserve ordinary Euclidean lengths of its stored columns. A metric must transform too if geometric quantities are to agree. Rectangular maps between different spaces require separate input and output coordinate changes rather than one common conjugation.

**Also called:** Change of coordinates.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Coordinates](#coordinates) · [Inverse](#inverse) · [Operator conjugation](#conjugation) · [Algebra homomorphism](#algebra-homomorphism) · [Linear isometry](#isometry)

<a id="inverse"></a>

### Inverse

A map that undoes another map in both directions. For a square invertible matrix C, the inverse satisfies C⁻¹C = CC⁻¹ = I.

A two-sided inverse establishes a reversible correspondence: neither direction loses information or leaves unreachable target values. For a finite square matrix, checking both products equal I confirms this directly. Over a field, invertibility is equivalent to full rank and a nonzero determinant.

Exact invertibility is separate from stable numerical inversion. A matrix can be invertible while having a very large condition number, so small stored errors can produce large recovered errors. Rectangular analysis maps instead often use a one-sided inverse, whose identity applies only in the relevant composition order.

**Also called:** Two-sided inverse.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Identity operator](#identity) · [Left inverse](#left-inverse)

<a id="left-inverse"></a>

### Left inverse

For A mapping an input space to a coordinate space, S is a left inverse when SA = I on the input space. This gives exact reconstruction of analyzed inputs. It does not imply AS = I on the entire coordinate space.

The left inverse reconstructs every original input after analysis. It therefore forces A to be injective: if Ax=Ay, applying S gives x=y. Extra coefficient coordinates are allowed, so A can have more rows than columns and still admit exact reconstruction.

There can be many left inverses, differing in how they treat coefficient lists outside im A. Canonical dual synthesis chooses one using the declared inner products. A reconstruction test on valid analyzed data does not determine how a synthesis map should behave on arbitrary inconsistent or noisy coefficient lists.

**In the worked example:** The redundant-coordinate example has SA = I₂ but AS ≠ I₃. S recovers every original vector even though it does not invert every three-coordinate input.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Inverse](#inverse) · [Analysis and synthesis](#analysis-synthesis) · [Image](#image)

<a id="redundancy"></a>

### Redundant coordinates

A representation containing more coordinate entries than are needed for a basis description. Valid coordinate lists can satisfy relations, such as a third measurement being the sum of the first two.

Redundancy adds descriptions without adding independent object dimensions. For A(x,y)=(x,y,x+y), the third measurement provides a consistency relation, not a third freely variable object coordinate. Such extra measurements can be useful for checking consistency or distributing reconstruction across several components.

The cost is that coefficient-space identities require care. An arbitrary triple need not be valid analyzed data, and synthesis can have a nonzero kernel of gauge directions. Individual coordinate contributions can sum to the correct object even though none of them is an idempotent packet projector.

**Also called:** Redundant representation.

**Keep in mind:** The reconstruction components SEᵢA can sum to the identity without being projectors.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Basis](#basis) · [Analysis and synthesis](#analysis-synthesis) · [Projector](#projector)

<a id="composition"></a>

### Composition

Applying one map after another. In a matrix product UT, T acts first and U acts second. The intermediate dimensions or types must agree.

Composition connects operations through the actual intermediate object. Its order matters: UT means that T acts first, so its output must be a legal input for U. Associativity permits regrouping compatible operations, but does not permit swapping their order.

If the two stages store the intermediate object in different coordinates, a bridge between those descriptions is required. Omitting it can produce a dimensionally valid matrix product with the wrong meaning. Complete packet decompositions similarly require summing over every relevant intermediate component when composing transfer blocks.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#typed-finite-expressions) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Typed system](#typed-system) · [Matrix](#matrix) · [Transfer block](#transfer-block)

<a id="conjugation"></a>

### Operator conjugation

The change in an operator matrix under an invertible coordinate change. With y = Cx and original operator T, the new matrix is CTC⁻¹. This usage is distinct from complex conjugation.

Conjugation describes the same endomorphism in a different coordinate system. The rightmost inverse converts the new input coordinates back to the old ones, T performs the original action, and the leftmost C returns the result to the new coordinates.

It preserves algebraic relations: if T²=0, then (CTC⁻¹)²=0, because the intermediate inverse factors cancel. Eigenvalues and minimal polynomial are also preserved. Ordinary transpose symmetry and Euclidean norm values need not be preserved by an arbitrary C, since those depend on metric information as well as linear structure.

**Also called:** Similarity transformation.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Coordinate change](#coordinate-change) · [Intertwiner](#intertwiner)

<a id="intertwiner"></a>

### Intertwiner

A linear map C connecting operators T and U by CT = UC. Applying T and then C agrees with applying C and then U. An intertwiner need not be invertible.

The equation CT=UC says that two routes to the target agree: evolve under T and then encode with C, or encode first and evolve under U. Unlike conjugation, this permits C to lose information or embed into a larger space.

If C is a summary map, its kernel must be preserved by T for such an exact reduced evolution to exist on its image. When C is invertible, the equation solves to U=CTC⁻¹. Thus intertwining includes reversible coordinate transport and some irreversible but dynamically compatible summaries.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Operator conjugation](#conjugation) · [Commuting diagram](#commuting-diagram)

<a id="block-matrix"></a>

### Block matrix

A matrix grouped into rectangular submatrices according to decompositions of its input and output coordinates. Block products require the inner dimensions to agree.

Blocks group related coordinates so that a large linear map can be read as interactions between spaces. A block row collects contributions to one output group, while a block column follows the outputs caused by one input group. The blocks can be rectangular and have different sizes.

Block multiplication sums over the shared intermediate groups, exactly as ordinary matrix multiplication sums over coordinates. Writing a matrix in blocks is initially just bookkeeping; treating some blocks as zero, diagonal or invertible is an additional mathematical assumption that must be justified.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#transfer) · [Matrix](#matrix) · [Transfer block](#transfer-block)

<a id="schur-complement"></a>

### Schur complement

For the block matrix \[\[A,B\],\[C,D\]\] with invertible A, the Schur complement of A is D − CA⁻¹B. It is the remaining operator after eliminating the first block of unknowns.

In the system Au+Bv=f and Cu+Dv=g, solving the first equation gives u=A⁻¹(f−Bv). Substitution into the second leaves (D−CA⁻¹B)v=g−CA⁻¹f. The Schur complement is therefore the effective remaining operator after accounting for the eliminated variables.

The inverse of A is essential to this elementary formula. A singular positive-semidefinite block requires a separate range condition before a pseudoinverse formula can replace it. Ignoring that condition can make an infeasible augmented matrix appear acceptable from the scalar inequality alone.

**Quick example:** In \[\[2,1\],\[1,3\]\], eliminating the invertible upper-left entry gives the scalar complement 3−1/2 = 5/2.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#elimination) · [Block matrix](#block-matrix) · [Elimination](#elimination) · [Inverse](#inverse)

<a id="elimination"></a>

### Elimination

Removing selected unknowns by solving part of a system and substituting into the remaining equations. The substitution requires its stated invertibility or solvability assumptions.

Elimination moves the influence of removed unknowns into a remaining equation; it does not simply delete their rows and columns. Solving a block and substituting it back preserves the original system only under the required solvability conditions and with the substituted right-hand side retained.

The resulting reduced operator often contains new interactions, such as a Schur-complement correction. Singular blocks can leave compatibility constraints or free variables. Any reduction that silently assumes a unique solution for such a block can change the set of admissible original solutions.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#elimination) · [Schur complement](#schur-complement) · [Reconstruction](#reconstruction)

<a id="orthogonal-matrix"></a>

### Orthogonal matrix

A real square matrix Q with QᵀQ = QQᵀ = I. It preserves the Euclidean inner product and norm. A transform with orthogonal rows can still need normalization to satisfy this identity.

The transpose undoes an orthogonal coordinate transformation because the columns form an orthonormal basis. Consequently dot products and Euclidean norms are unchanged. Rotations and reflections provide familiar examples; a determinant of either +1 or −1 is possible.

Mutually perpendicular rows are insufficient unless their lengths are normalized appropriately. The sum-and-difference Haar matrix, for example, needs a scaling choice before it becomes orthogonal. For complex matrices the corresponding condition uses conjugate transpose and is called unitarity.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#haar) · [Inner product](#inner-product) · [Norm](#norm) · [Normalization](#normalization)

<a id="normalization"></a>

### Normalization

A declared scaling convention. For a Haar pair, dividing sums and differences by two gives averages, while dividing by √2 gives a Euclidean norm-preserving transform.

Normalization fixes the scale at which coordinates, transforms or probabilities are reported. Two formulas can describe equivalent information while using different numerical coefficients. The inverse map, coefficient metric and error thresholds must follow the same convention for their results to agree.

In a Haar pair, average/detail scaling gives u²+v²=2(a²+d²), whereas orthonormal scaling removes that factor. In a Fourier transform, the factor 1/N may be placed in the inverse or split between directions. A comparison made before matching these conventions can mistake a predictable scale factor for an error.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#haar) · [Haar pair](#haar-pair) · [Orthogonal matrix](#orthogonal-matrix)

<a id="right-inverse"></a>

### Right inverse

For R:X→S, a map B:S→X satisfying RB=I on S. It chooses an input that produces each summary value. This identity does not require BR=I on X.

A right inverse chooses one representative input for each target value. The identity RB=I guarantees that the representative has the requested summary, but says nothing about whether it is the input that originally produced that summary.

For a linear summary with a nonzero kernel, other representatives differ by invisible kernel directions. Substituting one chosen representative into a future operation gives a candidate prediction. It is exact for every original input only if that future observation is constant across each summary fiber.

**Quick example:** For R(x,y) = x, the map S(x) = (x,0) satisfies RS = I. The reverse product SR deletes the second coordinate.

**In the worked example:** For R(x₁,x₂)=x₁+x₂ and B(s)=(s,0), RB(s)=s. But BR(0,1)=(1,0), so this choice does not recover every original pair.

[Hand-worked example](operators/BASICS.md#6-left-and-right-inverses) · [Left inverse](#left-inverse) · [Inverse](#inverse) · [Projector](#projector)

<a id="transported-product"></a>

### Transported product

Given an invertible linear map Φ between two representations, the target product f⋆g=Φ(Φ⁻¹f·Φ⁻¹g), where · is the declared source product. This carries the source multiplication law into the target coordinates.

The transported product makes a linear change of representation compatible with a chosen multiplication law. Decode both factors, multiply in the original algebra, and encode the result. Associativity and the identity element then travel through the same invertible map.

The resulting multiplication need not coincide with the ordinary product of the target expressions. In falling-factorial coordinates, x⋆x=x(x−1), because both represent the source product z². Using ordinary x² instead changes the algebra and can break a transported derivative’s expected product rule.

**Also called:** Transported multiplication, Star product in the polynomial example.

**In the worked example:** For Φ(zᵏ)=bₖ, one has bₐ⋆bᵦ=bₐ₊ᵦ and x⋆x=x(x−1). The forward difference satisfies Δ(f⋆g)=(Δf)⋆g+f⋆(Δg).

**Keep in mind:** Ordinary target multiplication is a different product: Δ(x²)=2x+1, whereas Δ(x⋆x)=2x.

[Hand-worked example](operators/POLYNOMIAL.md#6-transported-multiplication-and-its-product-rule) · [Coordinate change](#coordinate-change) · [Composition](#composition) · [Falling factorial](#falling-factorial) · [Forward difference](#forward-difference)

<a id="packet-leakage"></a>

### Leakage from a retained packet

For a projector P and a linear operator T, the map (I−P)TP records output leaving the retained range after the input starts in that range. It vanishes exactly when that range is invariant under T.

Leakage answers a specific question: start entirely in the retained packet, apply the full operation, and measure the output outside that packet. The final factor P enforces this input restriction, while I−P selects the part that leaves the retained range.

Zero leakage means that range is invariant, so its internal dynamics can be represented exactly by restriction. It does not imply that discarded inputs cannot flow back into the retained range. For arbitrary inputs, the complete compression residual includes those other transfer blocks as well.

**Also called:** Packet leakage, Off-packet leakage.

**In the worked example:** With P=diag(1,0), T=\[\[1,2\],\[3,4\]\], and x=(2,0)ᵀ, the full output is (2,6)ᵀ and the retained output is (2,0)ᵀ. The leakage is (0,6)ᵀ.

**Keep in mind:** For an arbitrary input, T−PTP also includes transfers starting in the discarded input range. The single leakage term is not the whole residual in that setting.

[Hand-worked example](operators/TRANSFER.md#6-leakage-from-a-retained-packet) · [Transfer block](#transfer-block) · [Invariant subspace](#invariant-subspace) · [Projector](#projector) · [Residual](#residual)

<a id="transfer-defect"></a>

### Pointwise transfer defect

Given representation maps R\_X,R\_Y, an operation f, and a proposed transferred rule f̄, the discrepancy Δ\_f(x)=R\_Y(f(x))−f̄(R\_X(x)). The subtraction requires a common vector-space output. The defect depends on the proposed rule and the input.

A defect compares the true represented output with the output predicted by a proposed transferred rule. Writing both in the same target space makes their subtraction meaningful. It can reveal errors from coordinate mismatch, an inadequate summary, omitted interactions or an unsuitable candidate rule.

A zero defect at one input confirms agreement there only. To obtain an exact commuting relation, it must vanish on the declared input set. Conversely, a nonzero defect rejects that candidate but does not rule out every possible transferred rule; a collision witness or another argument is needed for a general obstruction.

**Also called:** Transfer defect, Nonlinear transfer defect.

**In the worked example:** For f(x₁,x₂)=x₁x₂, R\_X(x)=x₁+x₂, R\_Y=I, and f̄(s)=s²/4, the defect at (2,3) is 6−25/4=−1/4. The candidate is exact on inputs (t,t).

**Keep in mind:** A pointwise defect can be nonlinear. Failure of one proposed rule is not by itself an obstruction to every possible rule.

[Hand-worked example](operators/TRANSFER.md#7-nonlinear-transfer-defects) · [Nonlinear map](#nonlinear-map) · [Commuting diagram](#commuting-diagram) · [Residual](#residual) · [Exact recovery from a summary](#exact-recovery)

<a id="finite-frame"></a>

### Finite frame

A spanning family in a finite-dimensional real or complex inner-product space, used to analyze a vector through its inner products with the family. A frame may contain redundant vectors. In orthonormal coordinates, its analysis matrix A has full column rank and admits a left inverse.

A frame provides enough measurements to distinguish every vector while allowing more measurements than a basis would require. The analysis map collects inner products with the frame vectors. Its full column rank is the finite-dimensional statement that no nonzero vector is invisible to all those measurements.

Redundancy can provide alternative synthesis rules and useful consistency relations among the coefficients. It also means that arbitrary coefficient lists may not be valid analysis outputs. Frame bounds describe the geometry of analysis, while a specified dual synthesis map determines how coefficient data are turned back into objects.

**Also called:** Frame, Finite analysis frame.

**In the worked example:** The vectors (1,0), (0,1) and (1,1) give A(a,b) = (a,b,a+b). Three measurements recover a vector in R², although the three frame vectors are not a basis.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/A_STRUCTURAL.md#op-202) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Basis](#basis) · [Analysis and synthesis](#analysis-synthesis) · [Frame bounds](#frame-bounds) · [Canonical dual synthesis](#canonical-dual)

<a id="frame-bounds"></a>

### Frame bounds

Positive constants α and β such that α‖x‖² ≤ ‖Ax‖² ≤ β‖x‖² for every input x of a frame analysis map A. The lower bound ensures that analysis loses no vector direction. Both bounds depend on the declared inner products and normalization.

The lower bound prevents analyzed vectors from becoming arbitrarily small relative to their original size, and the upper bound prevents excessive amplification. In finite Euclidean coordinates, the sharp bounds are the smallest and largest eigenvalues of A\*A for a full-column-rank analysis matrix.

Their ratio describes how unevenly different input directions are measured. Tight frames have equal bounds, giving a particularly simple scaled energy identity. Changing coefficient normalization changes the bounds, so numerical values should be compared only after the underlying inner products and scaling conventions agree.

**Also called:** Lower frame bound, Upper frame bound.

**In the worked example:** For A(a,b) = (a,b,a+b), ‖Ax‖² = a²+b²+(a+b)² lies between ‖x‖² and 3‖x‖² in Euclidean norm. The optimal bounds are α = 1 and β = 3.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md#5-scope-boundary) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Finite frame](#finite-frame) · [Norm](#norm) · [Classical frame operator](#classical-frame-operator)

<a id="classical-frame-operator"></a>

### Classical frame operator

For a finite frame analysis map A with fixed inner products, the operator G = A\* A on the original vector space. In orthonormal stored coordinates, \* is conjugate transpose. G is positive definite and invertible when A has full column rank. Its inverse gives canonical dual synthesis G⁻¹A\*.

Applying A first measures the vector; applying A\* then combines those measurements using the same frame geometry. The composite A\*A therefore acts on the original object space. Its quadratic form is ‖Ax‖², which explains its positivity and its connection to frame bounds.

Inverting this operator compensates for the unequal weighting or overlap of the measurements and produces canonical dual synthesis. It should not be confused with AS, which acts on coefficient space, or SA, which is the object reconstruction identity when S is a left inverse.

**Also called:** Frame operator, Analysis Gram operator.

**In the worked example:** The example's analysis matrix gives G = \[\[2,1\],\[1,2\]\], with eigenvalues 1 and 3. This is different from the reconstruction SA = I₂ and the coefficient projection AS.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/A_STRUCTURAL.md#op-202) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Finite frame](#finite-frame) · [Positive definite matrix](#positive-definite) · [Canonical dual synthesis](#canonical-dual) · [Coefficient projection](#coefficient-projection)

<a id="canonical-dual"></a>

### Canonical dual synthesis

For a finite full-column-rank analysis matrix A in orthonormal coordinates, the synthesis S = (A\* A)⁻¹A\*. It satisfies SA = I, while AS is the orthogonal projector onto the image of A. For fixed A, applying S is linear. Constructing S as A varies requires the rank condition.

Canonical dual synthesis corrects the frame operator’s weighting before reconstructing. For an exact analysis output Ax, the formula gives (A\*A)⁻¹A\*Ax=x. On an arbitrary coefficient list, it selects the vector whose analyzed coefficients are the orthogonal projection of that list onto im A.

This choice depends on the declared Euclidean or Hermitian geometry. It is not the only possible left inverse of A, and a different coefficient metric can change which reconstruction is called canonical. Small singular values of A can also make this exact formula numerically sensitive.

**Also called:** Canonical dual frame synthesis, Canonical left inverse.

**In the worked example:** For A(a,b) = (a,b,a+b), canonical dual synthesis is S = (1/3)\[\[2,−1,1\],\[−1,2,1\]\]. It sends (2,3,5) back to (2,3).

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/A_STRUCTURAL.md#op-202) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Finite frame](#finite-frame) · [Classical frame operator](#classical-frame-operator) · [Moore–Penrose inverse](#pseudoinverse) · [Left inverse](#left-inverse)

<a id="pseudoinverse"></a>

### Moore–Penrose inverse

For a real or complex matrix A in Euclidean coordinates, the unique matrix A⁺ satisfying AA⁺A = A, A⁺AA⁺ = A⁺, (AA⁺)\* = AA⁺ and (A⁺A)\* = A⁺A. It is defined even for rectangular or rank-deficient matrices. AA⁺ and A⁺A are orthogonal projectors on the respective coordinate spaces.

The pseudoinverse reverses the nonzero singular-value directions and assigns zero to the missing ones. In Euclidean least squares, A⁺b is the minimum-norm input among the inputs minimizing ‖Ax−b‖. The two orthogonal projectors in its defining identities live on different spaces.

Thus it handles inconsistent outputs and nonunique inputs without pretending that A is bijective. A⁺Ax recovers only the component perpendicular to ker A, not an arbitrary original x. The minimum-norm characterization also depends on the metric, so raw conjugate-transpose formulas cannot be transferred unchanged to nonorthonormal coordinates.

**Also called:** Pseudoinverse, Moore-Penrose pseudoinverse, Moore Penrose inverse.

**Quick example:** For the column A = (1,1)ᵀ, A† = (1/2,1/2). Thus A†A = 1, while AA† projects onto equal-coordinate pairs.

**In the worked example:** For the full-column-rank matrix A in Example 6, A⁺ is the displayed synthesis S. Thus A⁺A = I₂ but AA⁺ ≠ I₃.

**Keep in mind:** A pseudoinverse does not recover directions in the kernel of A. With nonorthonormal coordinates, metric choices must be carried explicitly.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/F_NONLINEAR.md#op-109) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Canonical dual synthesis](#canonical-dual) · [Orthogonal projector](#orthogonal-projector) · [Kernel](#kernel) · [Metric adjoint](#metric-adjoint) · [Singular block range condition](#singular-range-condition) · [Singular value decomposition](#singular-value-decomposition)

<a id="coefficient-projection"></a>

### Coefficient projection

For linear analysis A and linear synthesis S satisfying SA = I, the map P = AS on coefficient space. It satisfies P² = P, has image im A and kernel ker S, and sends any coefficient vector to analyzed coordinates representing the same underlying vector. It need not be orthogonal for an arbitrary left inverse S.

The map AS first synthesizes a coefficient list into an object and then analyzes that object again. Its output is a valid analyzed list representing the same synthesized object. Applying this correction twice changes nothing further, which explains its idempotence.

Its complementary component (I−AS)c lies in ker S and therefore contributes nothing to the represented object. Canonical dual synthesis makes AS orthogonal in the standard coefficient geometry, but a different left inverse can give an oblique coefficient projection. Exact reconstruction alone does not choose that geometry.

**Also called:** Analysis-synthesis coefficient projector.

**In the worked example:** The triple c = (0,0,1) is not in im A. Its projection is AS c = (1/3,1/3,2/3), whose third coordinate is the sum of the first two.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Analysis and synthesis](#analysis-synthesis) · [Coefficient gauge](#coefficient-gauge) · [Canonical dual synthesis](#canonical-dual) · [Projector](#projector)

<a id="reconstruction-component"></a>

### Reconstruction component

For linear maps A and S with SA = I and a coefficient selector Eᵢ, the map Cᵢ = SEᵢA on the original space. When the selectors partition all coordinates, the Cᵢ sum to the identity. In a redundant system, an individual Cᵢ need not be idempotent, so additive reconstruction alone does not make it a projector.

Each component follows one route through coefficient space: analyze, keep a selected coefficient group, then synthesize its contribution. Adding all these routes reconstructs the original vector when the selectors partition the coefficients and SA=I.

The intermediate redundant representation can prevent an individual route from being idempotent. Reanalyzing its contribution may spread it across several coefficient groups. Consequently, the words component and projector cannot be interchanged merely because all contributions sum to the identity; the extra equation Cᵢ²=Cᵢ must be checked.

**Also called:** Physical frame component, Analysis-synthesis component.

**In the worked example:** The first component is C₁ = (1/3)\[\[2,0\],\[−1,0\]\]. It satisfies C₁² = (2/3)C₁ ≠ C₁, even though C₁+C₂+C₃ = I₂.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/A_STRUCTURAL.md#op-021) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Projector](#projector) · [Finite frame](#finite-frame) · [Coefficient projection](#coefficient-projection) · [Reconstruction](#reconstruction)

<a id="coefficient-gauge"></a>

### Coefficient gauge

The kernel of a linear synthesis map S in a redundant linear presentation. Adding g ∈ ker S to a coefficient vector c leaves the represented vector unchanged because S(c+g) = Sc. The quotient of coefficient space by ker S records the represented vectors. For SA = I, (I−AS)c is the gauge part of c.

A gauge direction changes the stored coefficient list without changing the synthesized object. This identifies which apparent coefficient differences are representation freedom rather than physical differences. In a presentation with SA=I, every list decomposes into its analyzed representative ASc and its gauge part (I−AS)c.

The quotient by ker S records only the represented object. A norm or residual on raw coefficient lists can still detect gauge differences, whereas the seminorm ‖Sc‖ ignores them. Neither choice is universally correct: the intended question determines whether coefficient identity or synthesized-object identity matters.

**Also called:** Synthesis kernel, Coefficient gauge subspace.

**In the worked example:** For the displayed synthesis S, the nonzero vector g = (−1,−1,1) satisfies Sg = 0. Coefficients c and c+g therefore synthesize to the same vector.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/REDUNDANT_FRAME_ALGEBRA.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Kernel](#kernel) · [Quotient space](#quotient-space) · [Coefficient projection](#coefficient-projection) · [Coefficient metric](#coefficient-metric)

<a id="coefficient-metric"></a>

### Coefficient metric

In a finite linear presentation with Euclidean inner products on the stored spaces, H = S\* S pulls the underlying vector geometry back to coefficient space: c\*Hd = (Sc)\*(Sd). H is positive semidefinite and its kernel is ker S. It gives a genuine inner product after quotienting out those gauge directions.

The pulled-back metric measures coefficients by what they synthesize. Its quadratic value c\*Hc equals the squared norm of Sc, so two coefficient lists representing the same vector have the same physical size under this convention.

Because synthesis can erase gauge directions, H is generally singular in a redundant system. It defines a seminorm on raw coefficients and a genuine norm on the quotient by ker S. Treating it as an invertible coordinate metric without removing those directions would invalidate ordinary metric-adjoint or inverse formulas.

**Also called:** Synthesis pullback metric, Coefficient seminorm metric.

**In the worked example:** With the example's synthesis S and g = (−1,−1,1), g\*Hg = ‖Sg‖² = 0 although g is nonzero. This coefficient metric is singular.

**Keep in mind:** For an underlying metric Q rather than the identity, the pulled-back coefficient metric is S\*QS.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/a3aa04ac18a523f30c50c7f5dba709f88e904eff/docs/METRIC_PACKETS.md#1-redundant-analysis--synthesis-presentations) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Coefficient gauge](#coefficient-gauge) · [Seminorm](#seminorm) · [Positive semidefinite matrix](#positive-semidefinite) · [Metric adjoint](#metric-adjoint)

<a id="metric-adjoint"></a>

### Metric adjoint

The adjoint of a linear map T:X→Y for declared positive-definite Hermitian metric matrices Q\_X and Q\_Y. In stored coordinates it is T♯ = Q\_X⁻¹T\*Q\_Y, where \* is raw conjugate transpose. It satisfies ⟨Tx,y⟩\_Y = ⟨x,T♯y⟩\_X. The formula requires Q\_X to be invertible.

The adjoint moves an operator from one side of an inner-product pairing to the other. Its coordinate formula must therefore account for both the input and output metrics. Raw conjugate transpose is the special case in which those metric matrices are identities.

This distinction matters after a nonorthonormal coordinate change: the same underlying adjoint can have a different stored matrix. The inverse of the input metric requires positive definiteness. A singular coefficient metric arising from redundancy needs a quotient construction or an explicitly justified alternative rather than a formal inverse.

**Also called:** Weighted adjoint, Adjoint relative to a metric.

**In the worked example:** Using the example's analysis A with source metric Q\_X = A\*A and target metric Q\_Y = I₃ makes A♯ = (A\*A)⁻¹A\*, the displayed canonical synthesis S.

**Keep in mind:** A singular coefficient metric cannot be inverted by this formula. Its gauge directions require a quotient or a separately justified generalized inverse.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](operators/catalog/K_METRICS.md#op-185) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#redundancy) · [Adjoint matrix](#adjoint) · [Positive definite matrix](#positive-definite) · [Coefficient metric](#coefficient-metric) · [Canonical dual synthesis](#canonical-dual)

<a id="covector-pullback"></a>

### Covector pullback

For a linear map A:X→Y and a covector ℓ on Y, the covector ℓA on X, defined by (ℓA)(x) = ℓ(Ax). Pullback composes an observation with the map and does not require A to be invertible. Under a coordinate change y = Cx, storing the same observation in y coordinates instead gives the row ℓC⁻¹.

Pullback asks the same output question earlier in the computation. If A takes x to an output and ℓ measures that output, the composed row ℓA measures it directly from x. No reconstruction or inverse of A is needed.

This direction differs from rewriting a fixed question in new coordinates. For y=Cx, the row in y coordinates is ℓC⁻¹ because x=C⁻¹y. Distinguishing composition of a question with a map from conversion of its coordinate row prevents a common inverse-direction error.

**Also called:** Pullback of a linear functional.

**In the worked example:** Pulling the scalar observation ℓ(s) = 2s back along R(a,b) = a+b gives ℓR(a,b) = 2a+2b. Its row is (2,2).

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](operators/catalog/C_COORDINATES.md#op-172) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Covector](#covector) · [Composition](#composition) · [Coordinate change](#coordinate-change) · [Factorization through a map](#factorization)

<a id="compression"></a>

### Operator compression

A retained description of an operation. For a projector P and operator T, PTP acts on the retained range. For a summary R and a chosen lift S, RTS is a candidate reduced operation. Exact agreement with all original inputs requires an additional compatibility condition.

Compression replaces a full operation by one acting through a retained description. It can reduce storage or calculation, but its interpretation depends on the chosen summary and lift. Selecting a representative input is a modeling choice unless all inputs with the same summary give the same required output.

For PTP, inputs and outputs are restricted to the retained range. The omitted blocks describe what was lost. A useful approximation can tolerate a controlled residual; exact reduced dynamics instead require a compatibility or invariance argument that eliminates the relevant ambiguity for every admissible input.

**Quick example:** For T = \[\[1,2\],\[3,4\]\] and P = diag(1,0), PTP retains only the upper-left entry 1.

**Keep in mind:** A compression can be useful even when the retained state does not determine its own exact future.

[Further reading](operators/TRANSFER.md) · [Coarsening](#coarsening) · [Leakage from a retained packet](#packet-leakage) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [Transfer block](#transfer-block)

<a id="isometry"></a>

### Linear isometry

A linear map preserving the specified norm of every input. Between finite inner-product spaces, preserving inner products is equivalent. In orthonormal coordinates an isometric embedding Q satisfies Q\*Q = I; it need not be onto its codomain.

An isometry retains the geometry measured by its stated norm. In inner-product coordinates, Q\*Q=I says that its columns form an orthonormal family, so inner products of all input pairs are preserved. The map can embed a smaller space into a larger one without losing information.

The reverse product QQ\* is then a projector onto the embedded image, not generally the identity on the whole codomain. This is the rectangular counterpart of an orthogonal or unitary coordinate change. Preserving one chosen norm also does not imply preserving every differently weighted coordinate norm.

**Quick example:** The map x ↦ (x,0) preserves Euclidean length. Its matrix is rectangular, so it is not a unitary automorphism of R².

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Norm](#norm) · [Inner product](#inner-product) · [Unitary matrix](#unitary) · [Left inverse](#left-inverse)

<a id="algebra-homomorphism"></a>

### Algebra homomorphism

A linear map between algebras that also preserves their specified multiplication; in the unital convention it preserves the identity element. A linear coordinate isomorphism alone need not satisfy the multiplication condition.

Preserving multiplication means that encoding a product agrees with multiplying the encoded factors: Φ(fg)=Φ(f)Φ(g), for the products actually declared. Linearity alone only guarantees compatibility with addition and scalar scaling, so it cannot supply this extra identity.

The falling-factorial coordinate map illustrates the difference: Φ(z²)=x(x−1), while Φ(z)Φ(z)=x² under ordinary multiplication. Defining a transported product on the target restores multiplicative compatibility. This permits the original algebraic laws to travel through the representation without silently changing which product is being used.

**Quick example:** The falling-factorial map sends z² to x(x−1), while the square of its value on z is x². It therefore fails to preserve ordinary multiplication.

[Further reading](operators/POLYNOMIAL.md) · [Transported product](#transported-product) · [Coordinate change](#coordinate-change) · [Commutative ring with identity](#ring)

<a id="refinement-and-constraints"></a>

## Refinement and constraints

How descriptions become finer, discard information or meet a compatibility condition.

[Refinement](#refinement) · [Obstruction](#obstruction) · [Coarsening](#coarsening) · [Polyphase decomposition](#polyphase) · [Residue class](#residue-class) · [Compatibility](#compatibility) · [Commuting diagram](#commuting-diagram) · [Reconstruction](#reconstruction) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Lift](#lift) · [Finite conditional expectation](#conditional-expectation) · [Completion](#completion) · [Haar pair](#haar-pair) · [Detail coefficient](#detail-coefficient) · [Repair direction](#repair-direction) · [Free linear repair](#free-repair) · [Finite repair menu](#repair-menu) · [Repair selection cost](#repair-cost) · [Feasibility](#feasibility) · [Linear obstruction witness](#dual-witness) · [Admissible input set](#admissible-input) · [Exact recovery from a summary](#exact-recovery) · [Collision witness](#collision-witness) · [Partition of a set](#partition) · [Sufficient summary for a requested output](#sufficient-summary) · [Linear quotient map](#quotient-map)

<a id="refinement"></a>

### Refinement

A compatible move from a coarser description to a finer one. In finite packet refinement, each fine packet has a coarse parent and each coarse projector is the sum of its children.

Refinement records more detailed distinctions while retaining a rule for recovering the coarser description. In a packet tree, children belong to specified parents, and summing the children’s projectors recovers the parent projector. The extra detail is organized information rather than an unrelated second representation.

Compatibility must hold between levels, not merely within each separate level. Two individually valid decompositions may fail to form the claimed tower if their parent-child sums do not agree. Refining a description also does not guarantee convergence to an infinite limiting object; that requires separate analytic or structural conditions.

**In the worked example:** The zero-based even indices split into residue classes 0 and 2 modulo 4. Their selectors satisfy P₀ = F₀ + F₂.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Coarsening](#coarsening) · [Compatibility](#compatibility) · [Residue class](#residue-class)

<a id="obstruction"></a>

### Obstruction

An identified reason a requested construction cannot meet its stated conditions. In the recovery example, two inputs have the same coarse value but require different answers, so no recovery function from that value alone exists.

An obstruction excludes a requested construction throughout the stated class of possibilities. It therefore needs both a precise request and a reason that applies to every allowed candidate. A failed attempt, a large residual or a timeout identifies a problem with one method or run, but need not establish such a universal exclusion.

The recovery collision gives a particularly transparent obstruction. If two admissible inputs have the same summary and require different answers, a single function receiving that summary cannot return both. This proves impossibility for that summary and input class while leaving richer summaries or narrower input classes open.

**In the worked example:** The inputs (1,0) and (0,1) have the same sum but different first coordinates. No function of their sum alone can return the first coordinate for every real input.

**Keep in mind:** A nonzero numerical residual is not automatically a proof that every possible construction fails.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Residual](#residual)

<a id="coarsening"></a>

### Coarsening

Passing to a description that groups or forgets distinctions. Combining fine packets can recover a coarse packet, while discarding the fine values can prevent later reconstruction.

A coarsening groups fine descriptions into larger classes or discards distinctions between them. Its fibers make the forgotten information explicit: all inputs in one fiber receive the same coarse value. Some requested questions can remain constant on those fibers even when full reconstruction becomes impossible.

For a pair of samples, retaining their average loses the signed difference but still determines their sum. Whether coarsening is acceptable is therefore relative to the task. Applying an operation after coarsening also needs care, because the discarded detail may influence later coarse observations.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Refinement](#refinement) · [Obstruction](#obstruction) · [Fiber](#fiber) · [Sufficient summary for a requested output](#sufficient-summary) · [Operator compression](#compression)

<a id="polyphase"></a>

### Polyphase decomposition

For a sequence x and a positive integer m, the phase r collects samples x\_(mk+r), with 0 ≤ r &lt; m. Interleaving all phases reconstructs the indexed sequence. Filtering requires additional boundary and convention choices.

Polyphase decomposition reorganizes a sequence by its index modulo m. For m=2, one stream contains even-indexed samples and another odd-indexed samples. Keeping all phases with their within-phase positions is reversible; discarding a phase is an additional information-losing operation.

A shift can move a sample to a different phase and also change its within-phase index. That extra carry is why a filter’s polyphase representation is more than a permutation of its scalar taps. Finite signals additionally need a boundary rule before the resulting shifts and filter matrices are determined.

**Also called:** Polyphase splitting.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Address](#address) · [Residue class](#residue-class) · [Reconstruction](#reconstruction) · [Polyphase carry](#polyphase-carry) · [Finite impulse response filter](#finite-impulse-response-filter) · [Downsampling](#downsampling) · [Analysis filter bank](#filter-bank) · [Circular shift](#circular-shift)

<a id="residue-class"></a>

### Residue class

Integers with the same remainder modulo a positive integer m. Two integers belong to the same class when their difference is a multiple of m. Even and odd indices are the two classes modulo two.

A residue class is an equivalence class of integer indices, not just the chosen remainder used to label it. The label r usually represents every integer mk+r. Different representatives describe the same class whenever they differ by a multiple of the modulus.

This supplies the address system for polyphase streams and degree selectors. Refining from modulus m to a multiple of m splits each coarse class into finer classes with compatible parent labels. Operations on the actual indices may also change the quotient index k, so the residue label alone does not record the whole shift.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Polyphase decomposition](#polyphase) · [Address](#address) · [Residue coefficient selector](#coefficient-selector) · [Factorial lane](#factorial-lane)

<a id="compatibility"></a>

### Compatibility

Agreement between specified maps, operations or levels of a construction. The relevant equality must be stated, such as a coarse projector equaling the sum of its fine children.

Compatibility says that independently described pieces fit together according to a specified equality. For example, refining and then summing children should agree with selecting the original parent packet. The equality identifies exactly which outputs are meant to coincide and on which inputs.

It is not a general assurance that two constructions are similar or intuitively consistent. A coordinate system, a refinement tower and a dynamics summary each require their own compatibility equations. Checking those equations exposes whether an apparent discrepancy comes from a convention mismatch, omitted data or an actual failure of the proposed construction.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Commuting diagram](#commuting-diagram) · [Refinement](#refinement) · [Completion](#completion)

<a id="commuting-diagram"></a>

### Commuting diagram

A diagram in which the declared routes between the same starting and ending objects give the same map. In Example 3 the equality is D\_y C = C D.

A commuting diagram expresses route independence: following either declared path gives the same result at the common endpoint. To read one, identify its starting space, ending space and the composition order along each route, then translate those routes into an equation of maps.

Drawing the diagram does not prove the equation. In a finite linear setting, equality on a spanning family can establish it; for a nonlinear map, sampled agreement generally has narrower scope. A transfer defect quantifies how much the routes disagree when exact commutation is unavailable.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Composition](#composition) · [Compatibility](#compatibility) · [Intertwiner](#intertwiner)

<a id="reconstruction"></a>

### Reconstruction

Recovering an object from its representation under the stated identities. Exact reconstruction may use all packet components or a synthesis map. Dropping components generally introduces a residual.

Reconstruction asks whether the stored representation determines the object or requested quantity and whether the chosen synthesis rule returns it. An exact identity such as SA=I establishes this for every admissible input in its stated space. A successful single input is only an instance of that identity.

Dropping coordinates changes the reconstruction map and usually introduces a residual. That residual can be computed exactly even when the approximation is poor. Reconstruction accuracy also differs from numerical stability: exact algebraic recovery may amplify small perturbations if the representation is badly conditioned.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Analysis and synthesis](#analysis-synthesis) · [Residual](#residual) · [Complete packet family](#complete-packet-family)

<a id="fiber"></a>

### Fiber

For a map R and an output s, the set of all inputs with R(x) = s. A proposed observation can be recovered from R(x) alone only if it is constant on each fiber.

A fiber gathers all inputs that a map regards as indistinguishable at one output value. For a linear summary, each nonempty fiber is a translate of the kernel. For a nonlinear summary, fibers can have very different shapes, sizes or numbers of connected pieces.

Fibers turn a recovery question into a test of constancy. If the requested answer varies within one fiber, the summary cannot determine it. If it is constant on every fiber, an answer rule exists on the attained summary values, although continuity, stable evaluation and efficient computation remain additional questions.

**Also called:** Fibre, Preimage of a point.

**In the worked example:** For R(a,b) = a+b on R², the fiber over 1 consists of all (t,1−t) with real t. It contains both (1,0) and (0,1).

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Kernel](#kernel) · [Factorization through a map](#factorization)

<a id="factorization"></a>

### Factorization through a map

Writing one map F as G composed with another map R, so F(x) = G(R(x)). This means the intermediate value R(x) contains enough information for the requested output F(x).

Factoring F through R means that R is an adequate intermediate description for the particular output F. The intermediate rule G uses only R(x), so it cannot consult distinctions already erased by R. The factorization equation must hold throughout the declared input set.

For unrestricted linear maps, ker R⊆ker F supplies the corresponding existence criterion. In the finite matrix setting, one can also seek coefficients expressing the desired measurement rows through the available ones. For nonlinear settings the fiber criterion remains useful even when no kernel or row-space description is available.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Fiber](#fiber) · [Obstruction](#obstruction) · [Composition](#composition)

<a id="lift"></a>

### Lift

An object at a finer or richer level that maps to a specified object at a coarser level. Existence, uniqueness and compatibility of lifts are separate questions.

A lift supplies a finer object whose coarse image is the required one. There may be no lift, exactly one lift or many lifts. When many exist, selecting one representative is a further choice and may affect later computations that depend on the hidden finer information.

Across several levels, individually choosing lifts is not enough: their reductions must agree to form a compatible tower. Likewise, finding a lift at every tested finite level does not by itself exhibit one infinite compatible branch. The relevant existence and limit arguments must accompany that stronger claim.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#7-constrain) · [Refinement](#refinement) · [Compatibility](#compatibility) · [Obstruction](#obstruction)

<a id="conditional-expectation"></a>

### Finite conditional expectation

For positive weights and a finite partition, replace each value by its group’s weighted mean. The resulting map fixes group-constant vectors and is an orthogonal projector in the corresponding weighted inner product.

In the finite partition model, the operation replaces variation inside each group by a weighted constant. Positive weights determine both the group mean and the inner product in which the residual is perpendicular to group-constant vectors. Applying the averaging again changes nothing, so the map is a projector.

This explains how averaging can preserve all group-constant observations while losing within-group detail. The weights belong to the construction; replacing them can change the means and orthogonality. General measure-theoretic conditional expectation extends the idea but requires its own probability space and integrability hypotheses.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#averages) · [Orthogonal projector](#orthogonal-projector) · [Inner product](#inner-product) · [Coarsening](#coarsening)

<a id="completion"></a>

### Completion

A construction that adds or realizes limits or missing structure under a specified mathematical definition. There is no single universal completion operation across the collection. A finite compatible tower does not by itself construct an infinite limit.

The meaning of completion depends on what is missing and what equivalence or limiting notion is being used. A metric completion adds limits of suitable Cauchy sequences; an algebraic or realization construction can address a different kind of missing structure. The word alone does not identify one shared operation.

When a work builds compatible finite stages, distinguish the existence of those stages from the existence and properties of a completed object. Additional arguments may be needed for compatibility, convergence, uniqueness or preservation of operations. Editorial labels saying a manuscript is complete concern a separate assessment of its declared scope.

**Keep in mind:** Mathematical completion and the editorial completion stage of a paper are different uses of the word.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#8-complete) · [Compatibility](#compatibility) · [Lift](#lift)

<a id="haar-pair"></a>

### Haar pair

A two-sample transform that separates an average and a difference. The tutorial uses a = (u+v)/2 and d = (u−v)/2, with inverse (u,v) = (a+d,a−d). Other Haar normalizations use square roots.

The average records the common level of two samples, while the detail records how they differ. Together they contain exactly the original two numbers because adding and subtracting the stored values recovers u and v. Retaining only the average merges many distinct input pairs.

The tutorial’s half-sum and half-difference convention is convenient for averaging, but its energy identity has a factor of two. Orthonormal Haar coordinates use a different scaling. Both are legitimate transforms; the inverse and coefficient weights must match whichever normalization is chosen.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#haar) · [Detail coefficient](#detail-coefficient) · [Normalization](#normalization) · [Refinement](#refinement)

<a id="detail-coefficient"></a>

### Detail coefficient

In the Haar pair example, the signed half-difference d = (u−v)/2. It records the information lost when the pair is replaced by its repeated average.

The sign of the detail tells which sample is larger, and its magnitude measures their contrast under the chosen scaling. Adding it to the average restores one sample; subtracting it restores the other. It therefore carries exactly the information the repeated average omits in a two-sample Haar split.

At multiple scales, details describe differences at their own resolutions. Their numerical magnitudes cannot automatically be compared as equal energy contributions, because normalization and scale weights matter. Dropping selected details produces an explicit reconstruction residual rather than merely changing an index label.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#haar) · [Haar pair](#haar-pair) · [Residual](#residual)

<a id="repair-direction"></a>

### Repair direction

An allowed vector added to the span of the original image so that a required target can become reachable. Both the target equation and the permitted coefficient system must remain specified.

A repair direction adds a permitted way to move beyond the outputs already attainable. If a target is outside the original image, its class in the cokernel records the missing part. A useful added direction must address that missing class rather than merely duplicate an existing image direction.

The allowed coefficient system and admissibility rules matter. Rational linear combinations, nonnegative combinations and discrete component selections define different repair problems. A direction that repairs the unrestricted linear span may therefore fail to be an allowable physical or menu-constrained repair.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Image](#image) · [Span](#span) · [Finite repair menu](#repair-menu)

<a id="free-repair"></a>

### Free linear repair

A repair problem allowing freely chosen added directions over the declared field. In the rational finite-dimensional setting, the minimum added dimension is the dimension of the span of the target residual classes in the original cokernel.

Free linear repair asks how much new span is needed when added directions can be chosen without a finite menu restriction. Passing to the original cokernel removes directions already available. The span of the target residual classes then measures the independent missing directions in the stated finite-dimensional linear model.

This dimension count concerns added linear freedom, not necessarily the number or cost of physical components. Restricting candidates to a supplied menu can require more selected choices or make repair impossible. Claims about minimum repair should therefore retain whether the choices are free or constrained.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Repair direction](#repair-direction) · [Cokernel](#cokernel) · [Dimension](#dimension)

<a id="repair-menu"></a>

### Finite repair menu

A supplied finite list of candidate directions, with costs and any selection restrictions. Feasibility and optimality are judged using this list and the original target equation.

A repair menu turns a free existence question into a constrained selection problem. Each candidate has specified mathematical effects, and costs or compatibility rules determine which subsets may be used together. Solving the resulting problem requires both reachability of the target and compliance with those selection rules.

A cheap candidate may add no new direction, while a more expensive candidate may resolve several target residuals at once. Counting only the dimension of the missing span can therefore miss the actual menu optimum. Exhaustive search establishes an optimum only over the declared finite candidate population and cost model.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Repair direction](#repair-direction) · [Repair selection cost](#repair-cost) · [Feasibility](#feasibility)

<a id="repair-cost"></a>

### Repair selection cost

The declared cost of the selected repair choices. In the tutorial it is the sum of their selection costs, paid once per choice, independently of the rational coefficients used to combine them.

A cost model says what is charged: selected directions, repeated uses, coefficient magnitudes, hardware resources or something else. In the tutorial, paying once for a selected candidate differs from charging each algebraic use or each nonzero coefficient.

Optimality is meaningful only after this convention is fixed. Changing a candidate’s price or allowing a new repair can change the cheapest solution while leaving feasibility unchanged. A minimum-cost repair need not be unique, and it need not be the smallest repair under a different inclusion or dimension ordering.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Finite repair menu](#repair-menu) · [Free linear repair](#free-repair)

<a id="feasibility"></a>

### Feasibility

Existence of a solution satisfying the stated equations and admissibility conditions. Failure of one candidate or exhaustion of a search budget does not by itself show infeasibility.

Feasibility asks whether at least one allowed solution exists, before asking which is best. The allowed set includes the equations, input restrictions, coefficient field and any positivity or topology constraints. Removing or weakening a restriction changes the problem whose feasibility is being assessed.

A valid witness proves feasibility by satisfying those requirements. Infeasibility needs a reason excluding every allowed witness, such as a separating linear functional or an exhaustive argument over a finite domain. A rejected candidate or timed-out solver leaves a more limited conclusion.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Hypothesis](#hypothesis) · [Obstruction](#obstruction) · [Certificate](#certificate)

<a id="dual-witness"></a>

### Linear obstruction witness

A linear functional that annihilates every allowed direction but has a nonzero value on the required target. It proves that this target lies outside their span under the stated linear problem.

The witness turns an impossible vector equation into an impossible scalar equation. If ℓ annihilates every allowed direction, it also annihilates every linear combination of them. A target with ℓ(t)≠0 therefore cannot lie in that span.

This is a checkable certificate for the specified unrestricted linear problem. Its hypotheses must still match the allowed directions and field. More restrictive problems, such as nonnegative combinations or fixed circuit topologies, can have additional obstructions that are not captured merely by exclusion from a linear span.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#repair-menus) · [Linear map](#linear-map) · [Kernel](#kernel) · [Obstruction](#obstruction) · [Feasibility](#feasibility)

<a id="admissible-input"></a>

### Admissible input set

The declared set of inputs on which a construction or claim is required to work. Restricting this set can change fibers, recovery, and feasibility, so the input restriction belongs to the mathematical statement.

Admissibility specifies which cases a claim must handle, rather than which cases happen to appear in a demonstration. It can encode an input subspace, positivity condition, physical state constraint or a finite test domain. Removing inputs can eliminate collisions and make a previously impossible recovery possible.

For example, the sum x+y cannot determine x on all pairs, but does determine it when y is required to be zero. An argument using an input outside the allowed set is not a counterexample to the restricted claim. Conversely, a construction tested only on a convenient subset has not covered a larger declared domain.

**Also called:** Admissible inputs.

**In the worked example:** The sum s=x₁+x₂ does not determine x₁ on all of R². On the restricted inputs (t,t), it does: x₁=s/2.

[Hand-worked example](operators/RECOVERY.md#2-exact-recovery-and-factorization) · [Domain and codomain](#domain-codomain) · [Hypothesis](#hypothesis) · [Fiber](#fiber) · [Exact recovery from a summary](#exact-recovery)

<a id="exact-recovery"></a>

### Exact recovery from a summary

Recovery of a requested answer F(x) by a rule G using only a summary R(x), with F=G∘R on the declared input set. Such a rule on the attained summaries exists exactly when F has the same value on every fiber of R.

Exact recovery concerns the requested answer, which may be much smaller than the whole original input. A summary can fail to reconstruct the input while still determining its sum, energy or another specified observation. The equation F=G∘R identifies which information is being recovered.

Constancy on fibers supplies existence of G on attained summaries. To use G in practice, one must also consider how it is evaluated and how perturbations affect it. In linear finite-dimensional problems, kernel inclusion or row-space calculations can make this recovery rule explicit rather than merely existential.

**Also called:** Task-relative recovery, Summary sufficiency.

**In the worked example:** From R(x₁,x₂)=x₁+x₂, the answer H(x₁,x₂)=2x₁+2x₂ is recovered by G(s)=2s. The first coordinate alone is not recoverable on all real pairs.

**Keep in mind:** The fiber criterion establishes existence. Continuity, stability, and efficient evaluation require their own hypotheses.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](operators/RECOVERY.md#2-exact-recovery-and-factorization) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Factorization through a map](#factorization) · [Fiber](#fiber) · [Admissible input set](#admissible-input) · [Collision witness](#collision-witness)

<a id="collision-witness"></a>

### Collision witness

Two admissible inputs u,v with R(u)=R(v) but F(u)≠F(v). They prove that no function of the summary R alone recovers the requested answer F on the whole declared input set.

A collision witness demonstrates the precise ambiguity that defeats a proposed summary. Both inputs satisfy the same admissibility conditions, and their identical summaries give any summary-only rule exactly the same input. If their required answers differ, one of those answers must be wrong under any single-valued recovery rule.

The witness establishes an obstruction independently of how the recovery algorithm is implemented. It is stronger than showing one algorithm fails on one example. Its scope still belongs to the chosen summary and domain; retaining another measurement or restricting the inputs can remove the collision.

**Also called:** Recovery collision.

**In the worked example:** The inputs (1,0) and (0,1) have the same sum 1 but different first coordinates. For linear R and F, their difference w=(1,−1) gives Rw=0 and Fw=1.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](operators/RECOVERY.md#4-collision-and-kernel-witnesses) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Exact recovery from a summary](#exact-recovery) · [Fiber](#fiber) · [Kernel](#kernel) · [Obstruction](#obstruction)

<a id="partition"></a>

### Partition of a set

A family of nonempty, pairwise disjoint subsets whose union is the whole set. Each element lies in exactly one block. A finer partition divides coarse blocks into smaller blocks; this set-theoretic use of block is distinct from an operator matrix block.

A partition specifies which elements are grouped together without overlaps or omissions. It can represent coarse observations, packet addresses or events whose internal distinctions are being ignored. A refinement splits existing blocks but does not mix elements from different coarse blocks.

In finite averaging, values are replaced by one weighted mean per block. The partition determines which observations remain visible, while the weights determine the averaging geometry. A partition of a set should not be confused with a decomposition of an operator into matrix blocks, although the two can be related by coordinate selectors.

**Quick example:** The partition {{0,2},{1,3}} groups four indices by parity. The singleton partition refines it.

[Further reading](demonstrations/REFINEMENT.md) · [Refinement](#refinement) · [Coarsening](#coarsening) · [Finite conditional expectation](#conditional-expectation) · [Bell numbers](#bell-numbers)

<a id="sufficient-summary"></a>

### Sufficient summary for a requested output

A map R that retains enough information to determine a specified output F: there is a map G on the attained summary values such that F = G∘R. Equivalently, F is constant on each fiber of R. Sufficiency is relative to the requested output and admissible inputs.

Sufficiency is always relative to a question. Two inputs may differ in many ways but still be interchangeable if the requested output takes the same value on both. A summary is sufficient when it never merges inputs whose requested answers differ.

This viewpoint supports deliberate compression: retain exactly the distinctions needed by the task rather than require full input reconstruction. For a family of requested outputs, every member of that family must be constant on summary fibers. A summary sufficient for one present observation may still be insufficient for predicting future observations under an operation.

**Quick example:** R(x,y) = x+y is sufficient for F(x,y) = 2(x+y), but is insufficient for recovering x on all of R².

**Keep in mind:** This deterministic recovery definition is separate from statistical sufficiency for a family of probability laws.

[Further reading](operators/RECOVERY.md) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Exact recovery from a summary](#exact-recovery) · [Admissible input set](#admissible-input)

<a id="quotient-map"></a>

### Linear quotient map

For a vector space V and subspace K, the canonical linear map V → V/K sending x to its equivalence class x+K. Its kernel is K and it is surjective. It retains exactly the distinction between inputs differing by an element of K.

The quotient map formalizes forgetting an entire subspace of directions at once. It sends every x+k with k∈K to the same class as x. Its output is therefore an equivalence class, not a chosen representative or a numerical average.

Any linear map that annihilates K descends to a well-defined linear map on the quotient. This is the algebraic reason kernel inclusion appears in recovery. Choosing coordinates or representatives for the quotient is an additional construction, and choosing representatives alone does not restore the discarded distinctions.

**Quick example:** Quotienting R² by span{(1,−1)} identifies all pairs with the same sum.

[Further reading](operators/RECOVERY.md) · [Quotient space](#quotient-space) · [Kernel](#kernel) · [Surjective map](#surjective) · [Factorization through a map](#factorization)

<a id="arithmetic-and-error"></a>

## Arithmetic and error

How exact values, stored approximations, and error measures differ.

[Residual](#residual) · [Exact](#exact) · [Numerical](#numerical) · [Precision](#precision) · [Dyadic rational](#dyadic-rational) · [Rounding](#rounding) · [ULP](#ulp) · [Numerical ternary](#ternary) · [Tolerance](#tolerance) · [Integer congruence](#congruence) · [Coprime integers](#coprime) · [Modular inverse](#modular-inverse) · [Chinese remainder theorem](#chinese-remainder) · [Induced operator norm](#operator-norm) · [Condition number of a coordinate map](#condition-number) · [Strong operator convergence](#strong-convergence) · [Operator norm convergence](#operator-norm-convergence) · [Hilbert–Schmidt norm](#hilbert-schmidt-norm) · [Absolute error](#absolute-error) · [Relative error](#relative-error) · [Forward error](#forward-error) · [Backward error](#backward-error) · [Interval arithmetic](#interval-arithmetic) · [Bounded linear operator](#bounded-operator)

<a id="residual"></a>

### Residual

A discrepancy computed for a specified identity or reconstruction. In Example 5 it is r = x − x̂. Other operations may use a different sign or norm, so the definition belongs with the reported number.

A residual measures failure of a particular equation or reconstruction, so its interpretation begins with that equation. The reconstruction residual x−x̂ differs from the equation residual b−Ax̂, even when both concern the same computed answer. Their signs, units and norms can also differ.

A small residual shows that the tested relation is nearly satisfied under its chosen measure. It does not automatically show that the computed answer is close to the desired answer: an ill-conditioned problem can turn a small equation residual into a large forward error. Recovering such a bound requires a stability estimate.

**In the worked example:** Dropping residue class 2 modulo 4 from (1,2,3,4,5,6,7,8) gives r = (0,0,3,0,0,0,7,0). Its squared Euclidean norm is 58.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Norm](#norm) · [Tolerance](#tolerance) · [Obstruction](#obstruction) · [Absolute error](#absolute-error) · [Forward error](#forward-error) · [Backward error](#backward-error)

<a id="exact"></a>

### Exact

Computed or stated in exact algebra or arithmetic under the declared hypotheses. Exact rational arithmetic avoids rounding of those rational values. It does not establish an unchecked modeling assumption.

Exactness describes the arithmetic or equality being claimed, not the completeness of the entire investigation. Rational operations can retain fractions without rounding, and symbolic algebra can establish identities under explicit assumptions. These methods remove a particular source of numerical uncertainty.

The encoded problem can still differ from the intended model, omit cases or rely on an unproved premise. An exact calculation on sampled inputs also remains a finite calculation unless a general argument extends it. Read exact together with the domain, hypotheses and quantity actually computed.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#coordinates) · [Numerical](#numerical) · [Hypothesis](#hypothesis) · [Dyadic rational](#dyadic-rational)

<a id="numerical"></a>

### Numerical

Computed with finite-precision arithmetic and interpreted using a stated error or residual rule. A zero observed floating-point residual does not turn the whole computation into an exact-arithmetic proof.

Numerical work approximates quantities using finite representations and algorithms. Its reliability depends on input interpretation, rounding, conditioning and approximation error, not merely on the number of printed digits. A reproducible numerical result should identify the relevant precision and acceptance rule.

Some numerical methods provide rigorous enclosures when their arithmetic and analytic remainders are controlled. Others provide estimates supported by residuals or convergence studies. These are different evidence classes. Repeated agreement or a displayed zero residual alone does not establish exact equality of the underlying mathematical objects.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Exact](#exact) · [Residual](#residual) · [Tolerance](#tolerance)

<a id="precision"></a>

### Precision

The capacity of a numerical representation. For the binary model here it is the number of significant binary digits, including the leading bit. More precision does not alone prove that an algorithm or its input is accurate.

Precision governs how finely a representation can distinguish nearby values at its current scale. For a binary significand with a fixed number of bits, the absolute spacing changes with the exponent. It therefore differs from a fixed decimal error tolerance or the number of trustworthy digits in an answer.

Increasing precision can reduce rounding effects, but cannot repair incorrect formulas, inaccurate input data or omitted approximation terms. It can also expose cancellation or instability that a shorter display concealed. Precision comparisons should distinguish the stored format from the actual error established for the computed quantity.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Rounding](#rounding) · [ULP](#ulp) · [Numerical](#numerical)

<a id="dyadic-rational"></a>

### Dyadic rational

A rational number expressible as an integer divided by a power of two. These are precisely the rational numbers with a finite binary expansion, apart from representation range limits.

A terminating binary fraction is a finite sum of integer multiples of powers of two, which is why its reduced denominator is a power of two. Numbers such as 3/8 fit this pattern, whereas 1/3 does not, despite being an exact rational number.

A dyadic value may still exceed the range or precision of a particular floating-point format. Conversely, a stored binary floating-point number has an exact dyadic interpretation even when it approximates a non-dyadic intended input. Input conversion error and later arithmetic error should therefore be tracked separately.

**Also called:** Binary rational.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Exact](#exact) · [Rounding](#rounding)

<a id="rounding"></a>

### Rounding

Choosing a representable stored value for an exact value according to a specified rule. Nearest, ties to even chooses the closer value and resolves an exact midpoint by the parity of the last retained significand bit.

Rounding maps an exact value onto the available representable grid. The chosen rule determines which stored neighbor is selected and how midpoint cases are resolved. A rounding error is consequently a property of the exact value, format, scale and rule together.

Repeated rounded operations need not equal one final rounding of the exact combined expression. This matters for cancellation, summation and reproducibility. Directed rounding deliberately selects enclosing neighbors, while nearest rounding aims at closeness; one convention cannot be silently substituted for the other in a numerical certificate.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Precision](#precision) · [ULP](#ulp) · [Numerical ternary](#ternary)

<a id="ulp"></a>

### ULP

A unit in the last retained place at a specified precision and exponent. In the three-bit example the spacing in \[1, 2) is 1/4, while the spacing in \[2, 4) is 1/2. It is not one fixed absolute distance.

An ULP expresses spacing in the local representation rather than a universal physical unit. With fixed significand precision, moving to the next exponent interval changes that spacing. Near boundaries, adjacent gaps can differ, so a statement about ULP error must retain the convention being used.

An error measured in a few ULPs can be small relative to a nonzero value’s scale while having very different absolute sizes at different exponents. It should not be confused with a global tolerance. Exceptional values and underflow regions also need the numerical format’s own rules.

**Also called:** Unit in the last place.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Precision](#precision) · [Rounding](#rounding)

<a id="ternary"></a>

### Numerical ternary

A numerical return whose sign compares the stored result with the exact value under the operation’s contract. Zero means exact, negative means below and positive means above. An error sentinel is not a numerical direction.

The ternary return records the direction of rounding relative to the exact mathematical result of the specified operation. It is additional information beyond the stored approximation itself. In the stated contract, a negative sign means the stored value is below that exact result, not that the result is negative.

Check the API contract before interpreting a return code. Error indicators, unordered comparisons and numerical direction values can have different roles. The direction also concerns that individual operation and its encoded inputs; it is not a bound on all accumulated error in a longer computation.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#rounding) · [Rounding](#rounding) · [Exact](#exact)

<a id="tolerance"></a>

### Tolerance

A declared threshold used by a numerical acceptance rule. Its units, scaling and comparison must match the residual being checked. A residual below tolerance is evidence within that rule, not exact equality in general.

A tolerance defines what a particular acceptance test regards as small enough. Its meaning comes from the tested quantity: an absolute residual, a relative discrepancy, a matrix norm or a probability enclosure can each need a different threshold.

Passing a tolerance test is therefore a scoped numerical statement. A threshold chosen after observing a result can have a different evidential meaning from a justified bound fixed beforehand. Tolerance zero also does not generally convert floating-point calculations into exact proofs; the arithmetic and equality test remain finite representations.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#refinement) · [Residual](#residual) · [Norm](#norm) · [Numerical](#numerical)

<a id="congruence"></a>

### Integer congruence

The relation a ≡ b modulo m means m divides a − b, with m a positive integer. It compares residue classes, not the ordinary sizes of a and b.

Congruence retains divisibility information while forgetting which integer representative was chosen. If a≡b modulo m, adding the same integer or multiplying by the same integer preserves the relation. This makes residue classes a consistent arithmetic system.

Division is more restrictive. Cancelling a factor modulo m requires appropriate invertibility, so ordinary-looking algebraic manipulations can fail when that factor shares a divisor with m. The modulus belongs with every modular statement, especially when comparing lift branches or combining several residue conditions.

**Also called:** Congruence modulo m.

**Quick example:** 17 and 2 are congruent modulo 5 because their difference 15 is divisible by 5.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#modular) · [Residue class](#residue-class) · [Modular inverse](#modular-inverse)

<a id="coprime"></a>

### Coprime integers

Integers with greatest common divisor one. Pairwise coprime moduli give independent residue coordinates in the ordinary Chinese remainder theorem.

Coprimality means that two integers share no prime factor. Bézout’s identity expresses this as an integer combination au+bv=1, which explains both modular inverses and the independence of residue coordinates in the elementary Chinese remainder theorem.

For several moduli, pairwise coprime means every distinct pair has gcd one; this is stronger than saying that the gcd of the whole list is one. If moduli share factors, compatible residues can still sometimes be combined, but the ordinary product-modulus uniqueness statement needs modification.

**Also called:** Relatively prime integers.

**Quick example:** The integers 4 and 9 are coprime; 4 and 6 have common divisor 2.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#modular) · [Chinese remainder theorem](#chinese-remainder) · [Integer congruence](#congruence)

<a id="modular-inverse"></a>

### Modular inverse

An integer b with ab ≡ 1 modulo m. For m greater than one, it exists exactly when a and m are coprime. The inverse is a residue class modulo m.

A modular inverse undoes multiplication within residue classes. If ab≡1 modulo m, multiplying by b reverses the effect of multiplying by a modulo m. Different integer representatives of b describe the same inverse class.

Existence is controlled by gcd(a,m)=1. A nonzero residue need not be invertible when the modulus is composite: 2 modulo 6 is an example. This is why prime fields behave differently from general modular rings and why divisions in roots-of-unity or interpolation formulas require explicit denominator checks.

**Also called:** Multiplicative inverse modulo m.

**Quick example:** The inverse of 3 modulo 7 is 5 because 3·5 = 15 is congruent to 1.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#modular) · [Integer congruence](#congruence) · [Coprime integers](#coprime)

<a id="chinese-remainder"></a>

### Chinese remainder theorem

For pairwise coprime positive moduli, a tuple of residues specifies exactly one residue class modulo their product. Selecting an integer representative requires an additional convention.

The theorem combines several compatible pieces of modular information into one class when the moduli are pairwise coprime. The product modulus is the combined period: adding that product changes none of the individual residues.

It determines a class, not a unique ordinary integer, until a representative interval or another convention is fixed. Shared factors between moduli introduce compatibility requirements and change the combined modulus. In reconstruction problems, keep the modular solution separate from any later claim about bounded integer recovery or an infinite lift.

**Also called:** CRT.

**Quick example:** The requirements x ≡ 1 modulo 2 and x ≡ 2 modulo 3 give x ≡ 5 modulo 6.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#modular) · [Residue class](#residue-class) · [Coprime integers](#coprime) · [Reconstruction](#reconstruction)

<a id="operator-norm"></a>

### Induced operator norm

For a linear map between specified normed spaces with a nonzero domain, the supremum of ‖Tx‖/‖x‖ over nonzero inputs. It is the smallest uniform amplification bound when finite. The input and output norms are part of its meaning.

The induced norm asks for the largest amplification over all input directions, after the input and output norms have been fixed. It therefore gives the uniform inequality ‖Tx‖≤‖T‖‖x‖, which converts an operator residual into a bound valid for every input of controlled size.

This differs from evaluating the operation on one test vector or taking the largest matrix entry. In Euclidean coordinates it is the largest singular value, whereas other vector norms give different formulas. Infinite-dimensional linear maps can have no finite amplification bound at all.

**Also called:** Operator norm, Induced matrix norm.

**In the worked example:** For E=\[\[0,2\],\[3,0\]\], the Euclidean induced norm is 3 because EᵀE=diag(9,4). Thus ‖Ex‖₂≤3‖x‖₂ for every input.

**Keep in mind:** For the zero input space, the operator norm is defined to be zero.

[Hand-worked example](operators/STABILITY.md#1-vector-norms-and-induced-operator-norms) · [Norm](#norm) · [Condition number of a coordinate map](#condition-number) · [Spectral radius](#spectral-radius)

<a id="condition-number"></a>

### Condition number of a coordinate map

For an invertible linear coordinate map C on a nonzero finite-dimensional normed space, κ(C)=‖C‖‖C⁻¹‖. It bounds how the chosen coordinate representation can amplify errors, and depends on the norms being used.

The product ‖C‖‖C⁻¹‖ measures how unevenly a reversible coordinate map can stretch and then recover directions. It is at least one for a nonzero space under compatible induced norms. A large value signals that small stored perturbations can be magnified during recovery.

This is a property of the chosen map and norms, not a proof that a particular computation has incurred that worst-case error. Orthogonal or unitary changes have Euclidean condition number one. Exact rational inversion avoids rounding during inversion but does not remove sensitivity to uncertain input data.

**Also called:** Condition number, Coordinate conditioning.

**Quick example:** For C = diag(1,100), κ₂(C) = 100. The map stretches one coordinate one hundred times more than the other.

**In the worked example:** C=\[\[1,10\],\[0,1\]\] and C⁻¹ both have infinity norm 11, so κ∞(C)=121. Conjugating diag(1,2) by C keeps its eigenvalues but changes its infinity norm from 2 to 11.

[Hand-worked example](operators/STABILITY.md#4-coordinate-conditioning) · [Coordinate change](#coordinate-change) · [Induced operator norm](#operator-norm) · [Operator conjugation](#conjugation)

<a id="strong-convergence"></a>

### Strong operator convergence

For bounded linear maps Tₘ and T between fixed normed spaces, convergence Tₘx→Tx in the output norm for every fixed input x. It does not require one error bound to tend to zero uniformly over all unit inputs.

Strong convergence follows one fixed input at a time. For each x, the output error must tend to zero, but the stage at which it becomes small may depend on x. This permits progressively better treatment of every fixed vector without one bound controlling all unit vectors simultaneously.

The coordinate projections onto the first m positions in ℓ² illustrate the distinction. Every fixed square-summable sequence has a vanishing omitted tail, so the projections converge strongly to I. At each finite m, however, a unit vector supported in the next position still has error one.

**Also called:** Strong convergence of operators.

**In the worked example:** On ℓ², let Pₘ keep the first m coordinates. Then ‖x−Pₘx‖₂² is the tail sum of |xₖ|² and tends to zero for each fixed square-summable x.

**Keep in mind:** The square-summable sequence space ℓ² consists of sequences x for which Σₖ|xₖ|² is finite.

[Hand-worked example](operators/STABILITY.md#7-finite-truncation-and-infinite-convergence) · [Operator norm convergence](#operator-norm-convergence) · [Truncation](#truncation) · [Norm](#norm)

<a id="operator-norm-convergence"></a>

### Operator norm convergence

Convergence ‖Tₘ−T‖→0 for bounded linear maps between fixed normed spaces. It controls the error uniformly over all inputs of norm at most one, and implies strong operator convergence.

Operator norm convergence makes one shrinking error bound work for all inputs of norm at most one. For any fixed x, multiplying that bound by ‖x‖ gives strong convergence. The uniformity is the additional requirement, not simply a different way to print pointwise errors.

It is especially useful when the input will be chosen after the approximation level has been fixed. Strong convergence alone cannot provide that uniform guarantee. In a finite-dimensional domain, convergence on a basis can control the operator norm, but the infinite-dimensional projection example shows why that reasoning does not extend automatically.

**Also called:** Norm convergence of operators.

**In the worked example:** The first-m-coordinate projectors Pₘ on ℓ² converge strongly to I, but ‖I−Pₘ‖=1 for every finite m: a unit vector beyond the retained coordinates is still completely omitted.

[Hand-worked example](operators/STABILITY.md#7-finite-truncation-and-infinite-convergence) · [Strong operator convergence](#strong-convergence) · [Induced operator norm](#operator-norm) · [Truncation](#truncation)

<a id="hilbert-schmidt-norm"></a>

### Hilbert–Schmidt norm

For a finite real or complex matrix A, the norm defined by ‖A‖HS² = tr(A\*A), equal to the sum of the squared absolute values of its entries. It measures matrix size in the specified orthonormal coordinates and differs from the largest-singular-value operator norm.

This norm treats the matrix entries as one Euclidean vector of coefficients. Equivalently, it sums the squared gains over an orthonormal input basis, which makes it useful for total matrix discrepancy or density-matrix coherence calculations.

It differs from the induced Euclidean norm, which asks only for the largest gain in one direction. For a rank-r matrix, the squared Hilbert–Schmidt norm is the sum of the r positive squared singular values. The finite matrix convention here should not be transferred unchanged to every infinite-dimensional operator.

**Also called:** Frobenius norm, HS norm.

**Quick example:** For diag(3,4), the Hilbert–Schmidt norm is 5, while the induced Euclidean norm is 4.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Matrix trace](#trace) · [Adjoint matrix](#adjoint) · [Induced operator norm](#operator-norm) · [Residual](#residual)

<a id="absolute-error"></a>

### Absolute error

The size of an approximation error measured in a stated norm, such as |x−x̂| for scalars or ‖x−x̂‖ for vectors. It retains the units and scale of the quantity. An acceptance threshold must use the same units and norm.

Absolute error answers how large the discrepancy is in the quantity’s own units. An error of one volt, one coordinate unit or a stated vector norm can be interpreted without dividing by the target’s magnitude. This also makes the measure meaningful at a zero target.

Whether it is acceptably small still depends on the application’s scale. The same absolute discrepancy can be negligible for a large quantity and dominant for a small one. Report the norm and units before comparing absolute errors from different calculations or using them with a tolerance.

**Quick example:** Approximating 100 by 99 gives absolute error 1, while approximating 0.001 by 0 gives absolute error 0.001.

[Further reading](operators/STABILITY.md) · [Residual](#residual) · [Relative error](#relative-error) · [Tolerance](#tolerance)

<a id="relative-error"></a>

### Relative error

An absolute error divided by a specified nonzero reference size. With exact target x, a common rule is ‖x−x̂‖/‖x‖ when x ≠ 0. The reference and zero-target rule must be stated.

Relative error compares the discrepancy with a declared reference size, producing a scale-free ratio when the units agree. It is useful when outputs span very different magnitudes and a fixed absolute threshold would treat them unevenly.

The denominator matters. Dividing by the exact target, the computed answer or an input scale produces different tests. At or near a zero target, a relative measure can be undefined or misleadingly large, so numerical contracts often combine a relative rule with a separately stated absolute rule.

**Quick example:** Approximating 100 by 99 gives relative error 1/100. Approximating 0.001 by 0 gives relative error 1.

**Keep in mind:** A small absolute error can have a large relative error near zero.

[Further reading](operators/STABILITY.md) · [Absolute error](#absolute-error) · [Tolerance](#tolerance) · [Condition number of a coordinate map](#condition-number)

<a id="forward-error"></a>

### Forward error

The difference between a computed output and the exact output of the declared problem on the declared input. A forward bound controls the answer directly. It can include effects from input uncertainty, operator approximation and finite arithmetic.

Forward error concerns the answer the user wanted: how far the computed output lies from the exact output for the same declared input. It is the most direct accuracy question, but the exact reference answer is often unavailable, so a bound must be derived indirectly.

An equation residual can support such a bound only when the problem’s stability is controlled. For a nonsingular linear system, applying A⁻¹ to the residual relates it to the solution error. The inverse’s norm explains why a small residual can coexist with a large forward error in an ill-conditioned problem.

**Quick example:** For the equation 2x = 6, a computed answer x̂ = 2.9 has absolute forward error 0.1.

[Further reading](operators/STABILITY.md) · [Backward error](#backward-error) · [Residual](#residual) · [Condition number of a coordinate map](#condition-number)

<a id="backward-error"></a>

### Backward error

The size of an allowed perturbation to the input data that makes the computed answer an exact solution. The data components allowed to change and their norm determine the backward-error problem. Small backward error gives a useful forward guarantee only with suitable conditioning.

Backward error changes the question from the output to the input data. It asks whether the computed answer is exactly right for a nearby permitted problem. The word permitted is essential: changing only a right-hand side differs from changing both a matrix and a right-hand side.

A backward-stable algorithm can return answers corresponding to small data perturbations, yet an ill-conditioned problem can still have large forward error. Separating algorithmic stability from problem conditioning helps identify whether the remedy is better arithmetic, a different algorithm or a better-posed model.

**Quick example:** For 2x = 6, x̂ = 2.9 exactly solves 2x = 5.8. If only the right side may change, that perturbation has absolute size 0.2.

[Further reading](operators/STABILITY.md) · [Forward error](#forward-error) · [Condition number of a coordinate map](#condition-number) · [Residual](#residual)

<a id="interval-arithmetic"></a>

### Interval arithmetic

Arithmetic on sets represented by intervals, with operations producing intervals that contain all allowed exact outputs. Finite implementations need outward rounding. Repeated occurrences of an uncertain quantity can widen an enclosure because interval endpoints do not record all dependencies.

Intervals represent sets of possible exact values. Each operation returns a set guaranteed to include all corresponding outputs, provided the implementation encloses rounding as well. This supports validated bounds rather than a single estimate with an unexplained number of digits.

The enclosure can be conservative because ordinary intervals do not remember dependencies between repeated occurrences of a variable. Dividing by an interval containing zero also requires special treatment. A narrow final interval is useful only when all necessary input uncertainty and analytic approximation terms have been included.

**Also called:** Interval enclosure arithmetic.

**Quick example:** For x in \[1,2\], direct interval subtraction gives x−x in \[−1,1\], although the expression is identically zero when both occurrences denote the same x.

[Further reading](KCOS_NUMERICAL_CERTIFICATION_AUDIT.md) · [Directed enclosure](#directed-enclosure) · [Rounding](#rounding) · [Certificate](#certificate)

<a id="bounded-operator"></a>

### Bounded linear operator

A linear map T between normed spaces for which a finite constant C satisfies ‖Tx‖ ≤ C‖x‖ for every input. Its induced norm is the least such bound. All linear maps between finite-dimensional normed spaces are bounded; infinite-dimensional cases need this hypothesis.

Boundedness is the existence of one finite amplification constant that works for every input. For linear maps on normed spaces it is equivalent to continuity, connecting an algebraic operation with control of limiting processes and small perturbations.

Finite-dimensional matrices have this property for the usual norms, but familiar infinite-dimensional operations can depend strongly on their chosen domain and norm. Differentiation, for example, cannot be assumed bounded merely because it is linear. The operator’s function space and norm must accompany an analytic stability argument.

**Quick example:** Multiplication of every coordinate by 2 on Euclidean space is bounded with induced norm 2.

[Further reading](operators/STABILITY.md) · [Induced operator norm](#operator-norm) · [Strong operator convergence](#strong-convergence) · [Operator norm convergence](#operator-norm-convergence)

<a id="claims-and-evidence"></a>

## Claims and evidence

How to read assumptions, proofs, formal links, and computation records.

[Certificate](#certificate) · [Conditional](#conditional) · [Lean correspondence](#lean-correspondence) · [Hypothesis](#hypothesis) · [Theorem](#theorem) · [Proof](#proof) · [Heuristic](#heuristic) · [Finite check](#finite-check) · [Finite proof field](#proof-field) · [Admissible leaf](#admissible-leaf) · [Recorded inference rule](#inference-rule) · [Verification closure](#verification-closure) · [Inclusion-minimal certificate](#inclusion-minimal) · [Least certificate](#least-certificate) · [Minimum-cost certificate](#minimum-cost-certificate) · [Derivation trace](#derivation-trace) · [Shared premise](#shared-premise) · [Counterexample](#counterexample) · [Necessary condition](#necessary-condition) · [Sufficient condition](#sufficient-condition) · [Inconclusive search](#search-inconclusive) · [Formal statement](#formal-statement) · [Reproducible computation](#reproducibility)

<a id="certificate"></a>

### Certificate

A structured report describing a particular check, with its evidence class, residuals, and assumptions. The producer determines what was checked. A saved certificate describes a past calculation and needs revalidation for a new one.

A certificate makes a check inspectable by recording what was tested, the assumptions used and the evidence returned. Its force comes from the checker’s contract and the validity of the recorded data, not from the file’s name or a success flag alone.

A numerical enclosure, a linear obstruction witness and a proof-path certificate therefore have different contents and implications. Check the input identity, source revision and evidence class before reusing one. Replaying a certificate can confirm its stated check without establishing additional modeling assumptions or broader mathematical claims.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Exact](#exact) · [Numerical](#numerical) · [Conditional](#conditional) · [Derivation trace](#derivation-trace) · [Inconclusive search](#search-inconclusive)

<a id="conditional"></a>

### Conditional

A result that retains explicitly listed assumptions. In a computation record, some of those assumptions may not have been established by the computation. Passing its checks does not discharge them.

A conditional theorem proves an implication: under the listed assumptions, the conclusion follows. The proof can be complete even when applying it to a particular example requires establishing assumptions that remain open or externally supplied.

Computation records need the same separation. A run may verify an algebraic step under a supplied bound without proving that bound. Reporting the final outcome should retain such dependencies explicitly. Calling a statement conditional does not itself say whether its assumptions are plausible, proved elsewhere or merely conjectured.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Hypothesis](#hypothesis) · [Certificate](#certificate) · [Completion](#completion)

<a id="lean-correspondence"></a>

### Lean correspondence

A recorded connection between a written claim and a formal Lean statement. Compare hypotheses, the full formal type, source edition, and execution record. A similar declaration name or a working link alone does not establish the correspondence.

Correspondence concerns meaning between two statements, while Lean execution concerns checking the formal statement that was actually supplied. A successful kernel check does not by itself show that the formal types encode the intended objects, hypotheses and conclusion of the written theorem.

Compare the full declaration, imported assumptions and source edition with the relevant written passage. Also distinguish selected formal results from coverage of an entire work. A functioning source link or a similarly named declaration can help locate evidence, but cannot replace that comparison or an accepted execution record.

[Further reading](COMPLETION_STATUS.md#lean-coverage) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Proof](#proof) · [Theorem](#theorem) · [Certificate](#certificate)

<a id="hypothesis"></a>

### Hypothesis

An assumption required by a statement or construction. It may describe the space, arithmetic, domain, regularity or supplied data. A conclusion applies only where its hypotheses hold.

Hypotheses delimit the cases in which a statement is asserted. Invertibility, positive weights, a finite domain or a specified coefficient field can each make an otherwise invalid formula correct. Removing one changes the claim rather than merely shortening its presentation.

When applying a theorem, match its hypotheses to the actual problem before using its conclusion. When proposing a counterexample, check that the example satisfies them. A computation can establish some hypotheses for its encoded inputs while leaving others as external mathematical obligations.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](VERIFICATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#averages) · [Conditional](#conditional) · [Theorem](#theorem) · [Certificate](#certificate) · [Necessary condition](#necessary-condition) · [Sufficient condition](#sufficient-condition)

<a id="theorem"></a>

### Theorem

A mathematical statement established by a proof from its specified assumptions. A theorem may be conditional on explicit hypotheses, even when the implication itself is fully proved.

A theorem is a proved statement with a particular logical scope. It can assert an implication, an existence result, an equivalence or a bound, and these forms have different uses. For example, an existence theorem need not provide an efficient construction of the object whose existence it proves.

The theorem’s assumptions, definitions and dependencies travel with its conclusion. A finite example can illustrate it, and a formal companion can cover a precisely encoded version, but neither automatically enlarges the written result. Distinguishing mathematical validity from implementation efficiency is especially important in computational applications.

[Further reading](VERIFICATION.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Hypothesis](#hypothesis) · [Proof](#proof) · [Conditional](#conditional)

<a id="proof"></a>

### Proof

An argument establishing a statement from its hypotheses and accepted prior results. A worked input illustrates a statement. A general identity or argument is needed to establish a claim about every allowed input.

A proof explains why the conclusion follows throughout the stated domain. Its steps can use definitions, logical inference, algebraic identities and established results. A chain of correct calculations still needs to address the actual hypotheses and quantifiers of the claim being proved.

Examples are valuable for understanding and detecting errors, but sampled agreement does not generally settle a universal statement. Exhaustive checking of a finite domain can form a proof when coverage and checking correctness are established. Formal verification likewise proves the encoded proposition, whose correspondence with the intended written claim needs separate care.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](VERIFICATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#obstructions) · [Theorem](#theorem) · [Finite check](#finite-check) · [Lean correspondence](#lean-correspondence)

<a id="heuristic"></a>

### Heuristic

A method for discovery, search or estimation without a complete guarantee for the claimed outcome. Its suggestions can lead to later proofs or checks, but the suggestions alone do not establish them.

A heuristic can guide which seed, candidate, parameter or proof route to investigate next. Its value may come from producing useful suggestions quickly, even when it cannot guarantee success or optimality. The suggestion and its later verification are different stages.

A failed heuristic search does not establish that no solution exists. A successful heuristic proposal can become rigorous evidence after an appropriate exact or validated check. Claims about reliability or performance should describe the tested population and resource limits rather than turn favorable examples into an unrestricted guarantee.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Proof](#proof) · [Finite check](#finite-check)

<a id="finite-check"></a>

### Finite check

A check over specified, finitely many inputs or cases. Exhaustive checking can prove a claim about that finite domain. Sampling a larger domain does not establish the universal claim without an additional argument.

A finite check has a declared population of cases. It can be exhaustive over that population or sample only some of it. These alternatives must be distinguished because checking every member of a finite domain can settle a finite claim, while testing a subset leaves untested cases.

Coverage is part of the evidence: bounds, skipped cases, early exits and resource caps matter. An exact computation removes rounding concerns for the arithmetic performed, but does not automatically prove that the enumerator covered the promised population or that a finite pattern continues indefinitely.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](VERIFICATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#packets) · [Proof](#proof) · [Certificate](#certificate) · [Hypothesis](#hypothesis)

<a id="proof-field"></a>

### Finite proof field

A declared finite collection of claim nodes, admissible leaves, and recorded inference rules. Certificate validity is relative to this supplied system.

A proof field supplies the ambient vocabulary and certified rules within which a certificate is judged. Its claim nodes identify obligations, its admissible leaves specify allowed starting points, and its rules say which conclusions can follow from available premises.

Validity is relative to that supplied system. A checker can establish that a target is reached using the recorded rules without proving the soundness of arbitrary replacement rules or the adequacy of the field for every mathematical question. Changing the ambient field can change which certificates exist and what their optimal costs are.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Recorded inference rule](#inference-rule) · [Admissible leaf](#admissible-leaf) · [Certificate](#certificate)

<a id="admissible-leaf"></a>

### Admissible leaf

A node allowed as a starting point under the declared proof-field contract. Selecting such a leaf does not require deriving it again inside that certificate.

An admissible leaf is a permitted foundation for the current certificate, such as an accepted premise or an already certified result. It does not need a derivation inside that certificate because the proof-field contract has assigned it that starting role.

This is a scoped permission, not a declaration that any arbitrary claim is true. Its justification can reside in an external proof or evidence record. When a certificate is moved to another proof field or source edition, the leaf’s admissibility must be checked again against that new contract.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Finite proof field](#proof-field) · [Hypothesis](#hypothesis)

<a id="inference-rule"></a>

### Recorded inference rule

A specified set of premise nodes together with a conclusion node. The certificate can use the rule only when the required premises have been derived and its recorded certification permits it.

A rule connects a specified collection of premises to a conclusion. A rule requiring {a,b,c,d} cannot fire merely because three premises are available. All required premises and the rule’s recorded certification must be present under the current checking contract.

Using a rule several times can share already established premises, depending on the system’s representation. This affects certificate cost and graph structure. A valid derivation uses permitted rules correctly; it does not establish that an unverified implication inserted into the rule list is mathematically sound.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Finite proof field](#proof-field) · [Verification closure](#verification-closure)

<a id="verification-closure"></a>

### Verification closure

The nodes obtainable by admitting selected admissible leaves and repeatedly applying the retained certified rules whose premises are available.

Closure is obtained by repeatedly adding conclusions whose retained rules have all their premises available. In a finite supplied field, this process reaches a stage at which no new nodes can be added. A target in that closure is reachable from the selected starting evidence.

The result depends on both selected leaves and selected rules. Omitting a needed rule can make one proposed certificate fail even when another valid certificate exists in the ambient field. Closure checks validity for the proposal; searching for a least or cheapest valid proposal is a separate problem.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Admissible leaf](#admissible-leaf) · [Recorded inference rule](#inference-rule) · [Certificate](#certificate)

<a id="inclusion-minimal"></a>

### Inclusion-minimal certificate

A valid node-and-rule certificate with no valid strictly smaller subcertificate under componentwise inclusion. Several incomparable minimal certificates can exist.

Inclusion-minimality asks whether any selected node or rule can be removed while retaining a valid smaller certificate. It is a local statement in the inclusion order: no strictly smaller valid subcertificate exists inside that selected certificate.

It does not say that another incomparable certificate uses fewer items or costs less. Several minimal certificates can reach the same target through different leaves and rules. To compare all valid certificates by cost, cardinality or a least-element property, one must solve the corresponding stronger and differently ordered problem.

**In the worked example:** The certificate built from leaves s₁ and s₃ derives a, b, c and d, then the target t. Removing either selected leaf or any of its five retained rules breaks that derivation, so this certificate is inclusion-minimal.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Certificate](#certificate) · [Least certificate](#least-certificate) · [Minimum-cost certificate](#minimum-cost-certificate)

<a id="least-certificate"></a>

### Least certificate

A certificate contained componentwise in every certificate for the same request and rule system. This is stronger than being inclusion-minimal or having minimum numerical cost.

A least certificate would be a common valid core contained in every valid certificate for the same request. This is stronger than being impossible to shrink: it compares the candidate with all alternatives, including incomparable ones.

In the shared-premise example, two different pairs of leaves each reach the target, but their common selected evidence cannot start a derivation. Consequently no certificate can lie validly inside both, and no least certificate exists. Minimum cost can still exist despite this failure of a least element.

**In the worked example:** The two optimal certificates start from {s₁,s₃} and {s₂,s₄}. Their intersection contains no admissible leaf. With no mandatory starting leaves, it cannot derive t, so there is no least certificate in this rule system.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Inclusion-minimal certificate](#inclusion-minimal) · [Minimum-cost certificate](#minimum-cost-certificate)

<a id="minimum-cost-certificate"></a>

### Minimum-cost certificate

A valid certificate attaining the lowest declared total cost among the permitted certificates. Costs count selected items according to the supplied rule, so a shared premise need not be charged each time it is used.

Minimum cost compares valid certificates using a declared numerical objective. The objective may charge selected leaves once even when several later rules reuse them. Shared premises can therefore make the cheapest derivation different from one obtained by independently minimizing each branch.

Proving optimality requires both a valid certificate of the stated cost and a lower-bound argument excluding cheaper allowed certificates. The result belongs to the supplied field and cost model. It need not identify a unique certificate, a least certificate under inclusion or the shortest proof in every possible proof system.

**In the worked example:** Each selected leaf costs one and supplies two of four required obligations. Either pair {s₁,s₃} or {s₂,s₄} reaches the target at cost two, while zero or one leaf cannot. Reusing a selected leaf for two consequences does not double its cost.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#proof-certificates) · [Certificate](#certificate) · [Least certificate](#least-certificate) · [Finite proof field](#proof-field)

<a id="derivation-trace"></a>

### Derivation trace

A recorded sequence of inference steps showing how admitted leaves and previously established conclusions reach a target. Each step must cite an allowed rule with all its premises available. Checking a trace establishes its validity within the declared rule system.

A trace exposes the order in which evidence becomes available. At each step, the checker verifies that the cited rule is permitted and that its premises have already been established or admitted. This makes the difference between a reachable target and a merely listed target inspectable.

The trace’s final validity depends on the ambient rule and leaf contract. A correct trace checker and a correct search implementation are separate obligations: the first can reject a bad proposal without proving that the search procedure will find every valid one or identify the cheapest one.

**Also called:** Proof trace.

**Quick example:** Admit s₁ and s₃, derive a,b,c,d using their recorded rules, then apply {a,b,c,d} ⇒ t.

**Keep in mind:** A valid trace in a supplied proof field does not establish the soundness of arbitrary externally supplied rules.

[Further reading](examples/21_PROOF_CERTIFICATES.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Recorded inference rule](#inference-rule) · [Admissible leaf](#admissible-leaf) · [Certificate](#certificate) · [Verification closure](#verification-closure)

<a id="shared-premise"></a>

### Shared premise

An established node used by more than one later inference. Sharing allows a derivation to be represented as a directed acyclic graph instead of copying the whole premise derivation into each branch. Costs depend on whether reused nodes are charged once or once per use.

Sharing records one established fact as support for several later conclusions. It avoids copying the entire supporting derivation into each branch. A graph representation can therefore use fewer selected proof objects than a tree representation that duplicates every use.

The cost convention must say whether that shared object is charged once, once per use or in another way. In the tutorial, one selected leaf can discharge two obligations for one unit of cost. Optimizing branches separately can miss this benefit and overestimate the minimum cost of the whole certificate.

**Also called:** Proof sharing.

**Quick example:** In the certificate example, s₁ supplies both a and b but its selected-leaf cost is charged only once.

[Further reading](examples/21_PROOF_CERTIFICATES.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Derivation trace](#derivation-trace) · [Minimum-cost certificate](#minimum-cost-certificate) · [Recorded inference rule](#inference-rule)

<a id="counterexample"></a>

### Counterexample

An admissible instance on which a claimed universal conclusion fails. A counterexample must satisfy the claim’s hypotheses. For a recovery claim, two admissible inputs with the same summary and different requested outputs provide a collision counterexample.

A counterexample refutes the precise universal statement it satisfies the hypotheses of. Its strength is logical, not statistical: one genuine violating instance is enough to disprove a claim about every admissible input.

It should identify both the satisfied assumptions and the failed conclusion. A numerical discrepancy near a tolerance boundary may require exact arithmetic or an enclosure before it becomes a rigorous witness. Failure of a stronger statement also does not refute a weaker or more restricted statement that was actually claimed.

**Quick example:** The pairs (1,0) and (0,1) have the same sum and different first coordinates, disproving recovery of the first coordinate from the sum alone.

[Further reading](demonstrations/RECOVERY.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Hypothesis](#hypothesis) · [Collision witness](#collision-witness) · [Proof](#proof) · [Obstruction](#obstruction)

<a id="necessary-condition"></a>

### Necessary condition

A condition that must hold whenever a requested property holds. If A implies B, then B is necessary for A. Failing B rules out A, but passing B alone need not establish A.

A necessary condition supplies a test every solution must pass. It is especially useful for ruling out candidates: violating the condition immediately excludes them from the requested class. Passing the test, however, may leave other independent requirements unresolved.

On a Smith-chart cyclic orbit, equal reflection magnitude is necessary because rotations preserve radius. A fixed finite rotation order also restricts phase, so matching radius alone is insufficient. This illustrates why a list of necessary conditions should not be described as a complete feasibility criterion without proving the converse.

**Quick example:** Equal reflection magnitude is necessary for cyclic reachability on the Smith chart. A prescribed finite rotation order also restricts the phase.

[Further reading](demonstrations/SMITH_CHART.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Sufficient condition](#sufficient-condition) · [Obstruction](#obstruction) · [Feasibility](#feasibility)

<a id="sufficient-condition"></a>

### Sufficient condition

A condition that guarantees the requested property. If A implies B, then A is sufficient for B. The same implication makes B necessary for A. An equivalence provides both directions.

A sufficient condition gives a route to establishing the desired property. Once its hypotheses are verified, the implication guarantees the conclusion. It can be stronger than necessary, meaning that other valid cases may exist outside its scope.

For example, an invertible coordinate change is sufficient to transfer an operator by conjugation, but some noninvertible intertwiners also connect compatible operations. An equivalence or an if-and-only-if theorem proves both necessity and sufficiency; a one-direction argument establishes only the direction it actually proves.

**Quick example:** For linear F and R on a common vector space, ker R contained in ker F is sufficient for recovering F from R on the whole space.

[Further reading](operators/RECOVERY.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Necessary condition](#necessary-condition) · [Exact recovery from a summary](#exact-recovery) · [Kernel](#kernel)

<a id="search-inconclusive"></a>

### Inconclusive search

A search that has established neither a valid witness nor a proof that none exists within the specified problem. A timeout, an exhausted budget or rejection of one proposed certificate can leave the existence question unresolved.

An inconclusive search leaves the existence question unresolved. The procedure may have explored only part of the candidate space, exhausted a resource budget or failed to validate the candidate it happened to find. None of those outcomes by itself excludes valid candidates elsewhere.

A useful record distinguishes this status from infeasibility and from a checked witness. It should preserve the search bounds, stopping reason and any valid intermediate evidence. Later work can then continue from a known limitation instead of treating a timeout or a rejected proposal as an impossibility theorem.

**Also called:** UNKNOWN, Search timeout, Unresolved search.

**Quick example:** Rejecting the one-leaf proposal {s₁} leaves the valid two-leaf certificate {s₁,s₃} available.

[Further reading](examples/21_PROOF_CERTIFICATES.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Certificate](#certificate) · [Feasibility](#feasibility) · [Finite check](#finite-check) · [Counterexample](#counterexample)

<a id="formal-statement"></a>

### Formal statement

A proposition expressed in a proof assistant’s language with explicit types, hypotheses and conclusion. Its relationship to a written theorem depends on the interpretation of every object and assumption. A declaration name alone does not specify that relationship.

A formal statement makes types, assumptions and quantifiers part of an expression that a proof assistant can check. Small differences in those details can change its meaning substantially, even when its declaration name resembles a familiar written theorem.

To establish correspondence, compare the full formal type with the written claim and explain how its objects are interpreted. An encoded finite model can prove useful selected facts without covering an unrestricted infinite-dimensional claim. Successful compilation confirms the accepted formal development, not every informal interpretation attached to it.

**Quick example:** A declaration proving a finite matrix identity covers that identity under its encoded hypotheses; it does not automatically cover an infinite-dimensional analogue.

[Further reading](routes/PROOF_REVIEW.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Lean correspondence](#lean-correspondence) · [Hypothesis](#hypothesis) · [Proof](#proof)

<a id="reproducibility"></a>

### Reproducible computation

A computation with enough recorded inputs, source identity, environment information and instructions to repeat the stated check. Reproduction should compare the promised outputs or invariants. Repeating a calculation preserves the scope of the calculation rather than extending it.

Reproducibility makes a claimed run repeatable on identified inputs with identified code and conventions. Source hashes, commands, versions and expected invariants help another reader distinguish a genuine replay from a similar calculation performed on changed data.

A reproduced result retains its original scope. Repeating finite tests does not establish untested asymptotic behavior, and reproducing an implementation’s output does not independently establish the implementation’s correctness. The strongest records keep execution success, mathematical interpretation and source-to-claim correspondence separate.

**Quick example:** A source archive, its hash, the arithmetic convention and the expected rational output let another reader replay one exact example.

[Further reading](routes/PROOF_REVIEW.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Certificate](#certificate) · [Finite check](#finite-check) · [Exact](#exact) · [Numerical](#numerical)

<a id="series-and-functions"></a>

## Series and cyclic functions

Coefficient operations and the distinction between a finite truncation and an infinite series.

[Coefficient](#coefficient) · [Power series](#power-series) · [Truncation](#truncation) · [Formal reciprocal](#formal-reciprocal) · [Coefficient convolution](#convolution) · [Root of unity](#root-of-unity) · [Derivative in the series example](#derivative) · [Differential equation](#differential-equation) · [Initial condition](#initial-condition) · [Contracted argument](#contracted-argument) · [Coefficient recurrence](#coefficient-recurrence) · [Falling factorial](#falling-factorial) · [Forward difference](#forward-difference) · [Residue coefficient selector](#coefficient-selector) · [Polynomial translation operator](#translation-operator) · [Newton coefficient formula](#newton-coefficients) · [Ordinary generating function](#ordinary-generating-function) · [Exponential generating function](#exponential-generating-function) · [Binomial coefficient convolution](#binomial-convolution) · [Stirling numbers of the second kind](#stirling-second-kind) · [Signed Stirling numbers of the first kind](#stirling-first-kind) · [Stirling transform](#stirling-transform) · [Bell numbers](#bell-numbers) · [Fubini numbers](#fubini-numbers) · [Touchard polynomial](#touchard-polynomial) · [Roots-of-unity filter](#roots-of-unity-filter) · [Factorial lane](#factorial-lane) · [Generalized hypergeometric series](#hypergeometric-series) · [Signed Euler numbers](#signed-euler-numbers) · [Secant numbers](#secant-numbers) · [Formal series composition](#formal-composition) · [Compositional inverse of a formal series](#compositional-inverse) · [Polynomial degree](#polynomial-degree) · [Monic polynomial](#monic-polynomial) · [Rising factorial](#rising-factorial) · [Cauchy product](#cauchy-product) · [Formal power series](#formal-power-series) · [Radius of convergence](#radius-of-convergence) · [Taylor coefficient](#taylor-coefficient) · [Backward difference](#backward-difference)

<a id="coefficient"></a>

### Coefficient

The scalar multiplying a specified basis term. In f(z) = sum aₙzⁿ, aₙ is the coefficient of zⁿ.

A coefficient is attached to a particular basis element, not just to the represented object. The same polynomial can have different coefficient lists in ordinary powers and falling factorials. Specifying the basis is therefore part of specifying which scalar is being read.

Normalization matters too. In an exponential generating function, the stored sequence entry multiplies tⁿ/n!, so the ordinary coefficient of tⁿ is smaller by n!. Changing basis or normalization without changing coefficient formulas can create incorrect products, derivatives and comparisons.

**Quick example:** In 2+5x+3x², the coefficient of x is 5; in a different basis the coefficient list changes.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Scalar](#scalar) · [Basis](#basis) · [Newton coefficient formula](#newton-coefficients) · [Ordinary generating function](#ordinary-generating-function)

<a id="power-series"></a>

### Power series

An expression sum aₙzⁿ with infinitely many coefficient positions. A formal power series is manipulated through its coefficients. Evaluating it at a number additionally requires convergence.

A power series stores one coefficient at each nonnegative degree. Its formal interpretation supports algebraic manipulation degree by degree: only finitely many terms contribute to a fixed product coefficient. No numerical value of the variable needs to be chosen for those identities.

To interpret the same expression as a function, establish where the series converges and which operations are justified there. A finite list of coefficients does not determine the size of the omitted tail without further information. This is why truncation identities and analytic error bounds are recorded separately.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Coefficient](#coefficient) · [Truncation](#truncation) · [Ordinary generating function](#ordinary-generating-function) · [Exponential generating function](#exponential-generating-function) · [Formal series composition](#formal-composition) · [Formal power series](#formal-power-series) · [Radius of convergence](#radius-of-convergence)

<a id="truncation"></a>

### Truncation

Keeping only specified degrees or levels. Equality modulo zᴺ means the coefficients of degrees below N agree. It need not be equality of the full functions or series.

Truncation produces a finite description by discarding selected positions. Equality modulo zᴺ checks all coefficients of degrees 0 through N−1 while deliberately leaving higher degrees unspecified. Two very different full series can agree to that finite order.

The discarded part must be controlled separately when evaluating a function or applying an operation that moves information across the truncation boundary. Raising polynomial degree, for example, can require an extra intermediate coordinate. Simply dropping that coordinate can change an otherwise exact operator identity.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Power series](#power-series) · [Residual](#residual)

<a id="formal-reciprocal"></a>

### Formal reciprocal

For a power series over a field with nonzero constant coefficient, the unique series whose product with it is one. Its coefficients are determined recursively. A finite truncation only verifies the corresponding finite set of coefficient identities.

Multiplying A(z) by its reciprocal B(z) and equating coefficients determines B successively. The constant equation fixes b₀=1/a₀; each later equation contains the new bₙ multiplied by a₀ and terms already known. This explains the nonzero-constant-term requirement over a field.

The inverse concerns multiplication, so it differs from a substitution inverse. Computing the first N coefficients establishes A(z)B(z)=1 modulo zᴺ, not a complete analytic statement about values at every z. Convergence and evaluation errors need their own arguments.

**Also called:** Multiplicative inverse of a formal series.

**Quick example:** The formal reciprocal of 1−z is 1+z+z²+⋯ because their Cauchy product is 1.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Power series](#power-series) · [Coefficient convolution](#convolution) · [Field](#field) · [Compositional inverse of a formal series](#compositional-inverse)

<a id="convolution"></a>

### Coefficient convolution

The multiplication rule cₙ = sum from k=0 to n of aₖbₙ₋ₖ for ordinary power series. Each output coefficient is a finite sum, even when the series are infinite.

Convolution collects all degree pairs that contribute to one output degree. To form degree n, combine the degree-k term of one factor with the degree-(n−k) term of the other and sum over k. This is why each coefficient uses finitely many terms even for infinite formal series.

The coefficient convention determines the weights. Ordinary powers give this unweighted sum, while factorially normalized exponential series produce binomial coefficients. Signal convolution is related but also requires an index direction and boundary convention when the stored signal is finite.

**Also called:** Cauchy product.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Coefficient](#coefficient) · [Power series](#power-series) · [Binomial coefficient convolution](#binomial-convolution)

<a id="root-of-unity"></a>

### Root of unity

A complex number ω with ωᴺ = 1 for a positive integer N. It is primitive when N is its least positive such exponent. A weighted average over the powers of a primitive Nth root selects coefficients in one residue class modulo N.

Powers of a root of unity describe a finite cyclic phase action. Primitive order means that the complete cycle has the claimed length; a root whose true order divides N visits fewer distinct phases. This distinction is essential for exact averaging and cyclic reachability arguments.

The weighted phase sum cancels monomials in unwanted residue classes and retains those in the selected class. Over other fields, the required root and division by the cycle length may be unavailable. The coefficient selector can still exist algebraically even when this particular averaging realization does not.

**Quick example:** The number i has exact order 4: i⁴ = 1, and no smaller positive power equals 1.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Residue class](#residue-class) · [Packet](#packet) · [Roots-of-unity filter](#roots-of-unity-filter) · [Residue coefficient selector](#coefficient-selector) · [Cyclic reachability](#cyclic-reachability)

<a id="derivative"></a>

### Derivative in the series example

For n≥1, differentiating a power-series term aₙzⁿ gives n aₙzⁿ⁻¹. Constant terms differentiate to zero. Formal differentiation acts on coefficients. An analytic interpretation uses the function’s convergence and differentiability conditions.

Formal differentiation changes the coefficient list according to the monomial rule, without asking where a function converges. It lowers degree and weights the contribution by the original exponent. In an exponential normalization, the factorials reorganize this operation into a simpler shift of stored sequence entries.

Transporting differentiation through a basis change can produce a different-looking target operator. The falling-factorial map sends the source derivative to forward difference, not to ordinary differentiation in the target variable. Analytic differentiation and infinite termwise operations additionally require their stated convergence setting.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Coefficient](#coefficient) · [Power series](#power-series) · [Taylor coefficient](#taylor-coefficient)

<a id="differential-equation"></a>

### Differential equation

An equation relating an unknown function to one or more of its derivatives. The example also evaluates the same function at contracted arguments qz and rz.

A differential equation constrains an unknown function through its rates of change, rather than merely listing its values. A power-series approach substitutes an unknown coefficient sequence and compares like degrees, converting the equation into algebraic relationships among those coefficients.

The feedback example also uses values at scaled arguments, so the recurrence must include the corresponding powers of the contraction factors. Solving the formal coefficient equations does not alone establish an analytic solution or its convergence interval. Existence, uniqueness and evaluation error require the hypotheses of the particular equation.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Derivative in the series example](#derivative) · [Initial condition](#initial-condition) · [Contracted argument](#contracted-argument)

<a id="initial-condition"></a>

### Initial condition

A specified value, or collection of derivative values, used with a differential equation. The feedback example fixes T(0)=0, and the equation then forces T′(0)=1.

Initial data select among functions that satisfy a differential equation. The number and type of conditions needed depend on the equation, its order and its domain. A value at zero can also enter the coefficient recurrence as its starting coefficient.

Some derivative values are consequences of the equation rather than independent choices. In the stated feedback example, imposing T(0)=0 makes the equation force T′(0)=1. Assigning an incompatible derivative value as extra data would therefore change the problem into an inconsistent one.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Differential equation](#differential-equation) · [Derivative in the series example](#derivative)

<a id="contracted-argument"></a>

### Contracted argument

Evaluation at qz with 0&lt;q&lt;1 in the feedback example. A term cₙzⁿ becomes cₙqⁿzⁿ after this substitution. The scaling is inside the defining equation.

Replacing z by qz scales each degree-n coefficient contribution by qⁿ. For 0&lt;q&lt;1, higher degrees receive progressively stronger scaling at the same argument. This operation changes the input to the function; it is different from multiplying the whole output by q.

When the scaled function appears inside an equation, these degree-dependent factors belong in its coefficient recurrence. Their presence can influence convergence or bounds, but the contraction factor by itself does not settle those questions for an arbitrary nonlinear feedback equation.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Coefficient](#coefficient) · [Differential equation](#differential-equation)

<a id="coefficient-recurrence"></a>

### Coefficient recurrence

A rule determining successive series coefficients from earlier ones. It gives exact finite calculations at each degree. Analytic convergence and bounds for a discarded tail require additional arguments.

A recurrence turns a series construction into successive finite tasks: compute a new coefficient from coefficients already determined. It makes the calculation reproducible and can expose indexing, sign or normalization errors through low-degree checks.

The recurrence may establish a unique formal solution without proving that its series converges at a chosen argument. To use a finite prefix for numerical evaluation, one still needs a bound for the remaining coefficients or another remainder argument. Exact prefix arithmetic and analytic tail control answer different questions.

**Also called:** Recurrence for coefficients.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#contracted-feedback) · [Coefficient](#coefficient) · [Truncation](#truncation) · [Coefficient convolution](#convolution)

<a id="falling-factorial"></a>

### Falling factorial

The polynomial b₀(x)=1 and bₖ(x)=x(x−1)⋯(x−k+1) for k≥1. These monic polynomials form a basis of the polynomial space. Falling degree records the basis index k, which need not match an ordinary-power packet after expansion.

The basis element bₖ has ordinary degree k and leading coefficient one, but its lower powers are mixed. This makes the basis change triangular and invertible on each finite degree range. A packet defined by the index k therefore selects falling degree, not necessarily the same ordinary-power residues after expansion.

The basis is especially adapted to finite differences: Δbₖ=k bₖ₋₁ mirrors differentiation of ordinary powers. Products require more care, because a linear basis change does not generally preserve ordinary multiplication. The transported product carries the source multiplication law consistently.

**Also called:** Falling-factorial polynomial.

**In the worked example:** b₃(x)=x³−3x²+2x, while x³=b₁(x)+3b₂(x)+b₃(x). The map Φ(zᵏ)=bₖ therefore has Φ⁻¹(x³)=z+3z²+z³.

[Hand-worked example](operators/POLYNOMIAL.md#1-falling-factorial-coordinates) · [Basis](#basis) · [Forward difference](#forward-difference) · [Residue coefficient selector](#coefficient-selector) · [Newton coefficient formula](#newton-coefficients) · [Rising factorial](#rising-factorial) · [Monic polynomial](#monic-polynomial)

<a id="forward-difference"></a>

### Forward difference

The operator Δf(x)=f(x+1)−f(x). On rational polynomials, Δbₖ=k bₖ₋₁ for the falling-factorial basis and Δb₀=0. Under Φ(zᵏ)=bₖ, this is the transported source derivative: Δ=ΦD\_zΦ⁻¹.

Forward difference measures the change in a function after a unit shift of its input. On polynomials it lowers degree, and on falling factorials it has the simple coefficient k, matching the source monomial derivative under the stated coordinate map.

It should not be confused with ordinary differentiation or backward difference. For x², these give 2x+1, 2x and 2x−1 respectively. The direction and step size are mathematical data, so changing either can alter transport identities and the placement of phase carries.

**Also called:** Unit forward difference, Delta operator in the polynomial example.

**In the worked example:** For f(x)=x³, Δf(x)=3x²+3x+1. Ordinary differentiation in x instead gives 3x², so the coordinate transport matters.

[Hand-worked example](operators/POLYNOMIAL.md#2-forward-difference-as-a-transported-derivative) · [Falling factorial](#falling-factorial) · [Derivative in the series example](#derivative) · [Polynomial translation operator](#translation-operator) · [Transported product](#transported-product)

<a id="coefficient-selector"></a>

### Residue coefficient selector

For an integer m≥2 and 0≤r&lt;m, the projector Pᵣ retaining exactly the coefficients whose basis degree k satisfies k≡r modulo m. The basis is part of the definition. In falling-factorial coordinates the corresponding projector is Qᵣ=ΦPᵣΦ⁻¹.

A coefficient selector keeps named basis positions and sets the rest to zero. Applying it again changes nothing, which makes it a projector. The residue selectors are mutually annihilating and sum to the identity when all residue classes are included.

The basis determines what is selected. Selecting ordinary-power degrees after a polynomial has been converted to falling-factorial coordinates generally gives the wrong transported packet. The correct selector is obtained by decoding, selecting in the source basis and encoding again.

**Also called:** Coefficient selector, Residue projector.

**In the worked example:** For x³=b₁+3b₂+b₃, the even falling-degree packet is 3b₂ and the odd packet is b₁+b₃. At x=4 their values are 36 and 28, summing to 64.

**Keep in mind:** Coefficient selection is defined over any commutative ring. Over a field, its roots-of-unity averaging formula requires a primitive mth root and invertible m.

[Hand-worked example](operators/POLYNOMIAL.md#5-transported-projectors-and-a-complete-packet-calculation) · [Further reading](operators/POLYNOMIAL.md#4-coefficient-selectors-and-roots-of-unity-averaging) · [Projector](#projector) · [Residue class](#residue-class) · [Falling factorial](#falling-factorial) · [Root of unity](#root-of-unity) · [Roots-of-unity filter](#roots-of-unity-filter)

<a id="translation-operator"></a>

### Polynomial translation operator

For a specified scalar shift h, the operator T\_h f(x)=f(x+h). Over rational polynomials it is linear, with T₀=I and T\_hT\_k=T\_{h+k}. In falling-factorial coordinates, a unit shift satisfies T₁=I+Δ.

Translation changes the input location at which a polynomial is evaluated. The composition rule T\_hT\_k=T\_{h+k} follows because the argument receives both shifts. Its inverse is the opposite shift, so translation preserves all polynomial information on the full space.

In falling-factorial coordinates, a shift mixes degrees according to finite-difference identities. For the unit forward step, T₁=I+Δ. A shift of sequence indices in a finite signal needs an additional boundary convention, so the polynomial translation law should not be transplanted without checking the domain.

**Also called:** Translation operator, Polynomial shift operator.

**In the worked example:** For f=x³ and the even falling-degree projector Q₀, Q₀T₁f(4)=73 while T₁Q₀f(4)=60. Both orders translate the total correctly after all packets are added, but the individual packets differ.

[Hand-worked example](operators/POLYNOMIAL.md#7-translation-carries-information-between-packets) · [Forward difference](#forward-difference) · [Falling factorial](#falling-factorial) · [Transfer block](#transfer-block) · [Commutator](#commutator)

<a id="newton-coefficients"></a>

### Newton coefficient formula

For f=Σₖaₖbₖ in the falling-factorial basis over Q, the coefficient is aₖ=Δᵏf(0)/k!. Repeated forward differences lower the basis index, and evaluation at zero isolates the matching coefficient.

Repeated differences successively remove lower-degree ambiguity. Evaluating Δᵏf at zero isolates the coefficient of bₖ, up to the factor k!, because higher falling-factorial terms still vanish at that evaluation after k differences.

The division by k! is legitimate over Q but can fail in positive characteristic. This failure concerns the sampling formula, not the underlying monic triangular basis change. Distinguishing the two prevents a denominator obstruction from being misreported as failure of the entire falling-factorial coordinate system.

**Also called:** Newton coefficients, Finite-difference coefficient recovery.

**In the worked example:** The samples of x³ at 0,1,2,3 are 0,1,8,27. The first entries of successive difference rows are 0,1,6,6. Dividing by 0!,1!,2!,3! yields the coefficients 0,1,3,1.

**Keep in mind:** This division formula requires the factorial denominators to be invertible. The integral Stirling basis change remains invertible over any commutative ring, even where this sampling formula fails.

[Hand-worked example](operators/POLYNOMIAL.md#8-recover-coordinates-and-check-the-coefficient-ring) · [Coefficient](#coefficient) · [Falling factorial](#falling-factorial) · [Forward difference](#forward-difference) · [Field](#field)

<a id="ordinary-generating-function"></a>

### Ordinary generating function

The formal series A(z) = Σₙ≥₀ aₙzⁿ used to store a sequence (aₙ). The coefficient of zⁿ is aₙ itself. This convention determines the multiplication rule and differs from factorial normalization.

An ordinary generating function packages a sequence into algebra whose degree tracks the sequence index directly. Multiplication combines two sequences by ordinary coefficient convolution, while shifting or multiplying by z changes the index pattern in a predictable way.

The package is initially formal unless an analytic interpretation has been established. Evaluating at a number can forget coefficient information or fail to converge. Comparing it with an exponential generating function requires accounting for factorial normalization rather than identifying the two stored coefficient lists.

**Also called:** OGF.

**In the worked example:** The reciprocal of 1+z+z² is (1−z)/(1−z³), with ordinary coefficient pattern 1, −1, 0, 1, −1, 0, ….

**Keep in mind:** Formal coefficient identities do not by themselves justify evaluating the series outside its convergence region.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#cyclic-reciprocals) · [Power series](#power-series) · [Coefficient](#coefficient) · [Exponential generating function](#exponential-generating-function) · [Coefficient convolution](#convolution)

<a id="exponential-generating-function"></a>

### Exponential generating function

The formal series A(t) = Σₙ≥₀ aₙtⁿ/n! over a coefficient field of characteristic zero. The sequence entry aₙ is the coefficient in the basis tⁿ/n!, while the ordinary coefficient of tⁿ is aₙ/n!.

Factorial normalization is useful when labelled combinatorial objects or derivatives are involved. The sequence entry aₙ equals the nth derivative at zero in an analytic interpretation, while the ordinary power coefficient is aₙ/n!. This explains why multiplication introduces binomial weights.

The factorial denominators require the stated characteristic-zero field setting. Index compression introduces another independent convention: a sequence indexed by n may be stored at even degree 2n, as in the secant example. Both the basis normalization and degree map must match before coefficients are compared.

**Also called:** EGF.

**In the worked example:** The Bell numbers have EGF exp(eᵗ−1). Its degree-five term is 52t⁵/5!, because B₅ = 52.

**Keep in mind:** The Euler demonstration uses the compressed index n for degree 2n. Its secant denominator is (2n)!, not n!.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Ordinary generating function](#ordinary-generating-function) · [Binomial coefficient convolution](#binomial-convolution) · [Normalization](#normalization) · [Coefficient](#coefficient)

<a id="binomial-convolution"></a>

### Binomial coefficient convolution

The product rule for exponentially normalized series: if A(t) = Σ aₙtⁿ/n! and B(t) = Σ bₙtⁿ/n!, their product has coefficient cₙ = Σₖ₌₀ⁿ binom(n,k)aₖbₙ₋ₖ in that same basis.

The binomial factor accounts for moving between ordinary multiplication and factorially normalized coefficients. Multiplying tᵏ/k! by tⁿ⁻ᵏ/(n−k)! and rewriting in the basis tⁿ/n! produces n!/(k!(n−k)!), which is binom(n,k).

Thus the extra weights are forced by the coordinate convention rather than being an optional correction. Using ordinary unweighted convolution on the same stored sequence entries computes a different product. A product identity should state whether its arrays contain ordinary coefficients or exponentially normalized sequence values.

**Also called:** Binomial convolution, Exponential coefficient convolution.

**In the worked example:** In the secant recurrence, the degree-four row is s₂ = 6s₁ − s₀ = 5. The factor 6 is binom(4,2).

[Hand-worked example](demonstrations/EULER_PACKETS.md) · [Coefficient convolution](#convolution) · [Exponential generating function](#exponential-generating-function) · [Normalization](#normalization)

<a id="stirling-second-kind"></a>

### Stirling numbers of the second kind

The integers S(n,k) counting partitions of an n-element labelled set into k nonempty, unlabelled blocks. For n ≥ 1 they satisfy S(n,k) = S(n−1,k−1) + kS(n−1,k), with S(0,0) = 1 and zero outside 0 ≤ k ≤ n.

The recurrence separates partitions according to what happens to the newest label. It either forms a new singleton block, contributing S(n−1,k−1), or joins one of k existing blocks, contributing kS(n−1,k). The blocks themselves are unlabelled despite the elements being labelled.

The same numbers give the basis change xⁿ=ΣₖS(n,k)bₖ(x). This connects a counting interpretation with polynomial coordinates. Summing a row gives a Bell number, while weighting its entries by k! gives a Fubini number; those summaries retain different amounts of the row’s information.

**Also called:** Stirling partition numbers.

**Quick example:** S(3,2) = 3: the singleton can be any of the three labels, with the other two in the second block.

**In the worked example:** The row at n = 5 is (0,1,15,25,10,1). In particular, S(5,3) = 7+3·6 = 25.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling transform](#stirling-transform) · [Bell numbers](#bell-numbers) · [Fubini numbers](#fubini-numbers) · [Falling factorial](#falling-factorial)

<a id="stirling-first-kind"></a>

### Signed Stirling numbers of the first kind

The coefficients s(n,k) in x(x−1)⋯(x−n+1) = Σₖ₌₀ⁿ s(n,k)xᵏ. Their lower-triangular matrix is the inverse of the second-kind Stirling matrix. The sign is part of this convention.

The signed numbers record how a falling-factorial polynomial expands into ordinary powers. Their signs arise from the factors x−j, so removing the signs changes the coefficient transformation. The lower-triangular inverse relationship supplies exact conversion in the opposite direction from second-kind Stirling numbers.

Conventions differ across counting and special-function sources. Unsigned first-kind numbers count permutations by cycles, whereas the signed convention is the one used for this inverse basis matrix. Checking a low-degree expansion, such as b₂=x²−x, quickly identifies which convention a formula uses.

**Also called:** Signed first-kind Stirling numbers.

**In the worked example:** The n = 5 coefficient row is (0,24,−50,35,−10,1). Applied to (F₀,…,F₅), it gives 24−150+455−750+541 = 120 = 5!.

**Keep in mind:** Unsigned first-kind Stirling numbers count permutations by cycles and remove these alternating signs. They are not the inverse matrix used here.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Stirling transform](#stirling-transform) · [Inverse](#inverse) · [Falling factorial](#falling-factorial)

<a id="stirling-transform"></a>

### Stirling transform

The triangular sequence map cₙ = Σₖ₌₀ⁿ S(n,k)aₖ. Each output uses finitely many input entries. Signed first-kind Stirling numbers invert the full triangular map, and the EGF form is C(t) = A(eᵗ−1).

Each transformed entry combines a finite prefix of the input sequence using one Stirling row. Because the matrix is triangular with diagonal entries one, the full output prefix can be inverted successively using signed first-kind Stirling numbers.

This reversibility concerns the whole triangular sequence map. A single row sum, such as a Bell number, generally cannot recover an arbitrary row of coefficients. The generating-function identity expresses the same transform through substitution and therefore also depends on the exponential normalization convention.

**In the worked example:** Weights aₖ = 1 produce Bell numbers. Weights aₖ = k! produce Fubini numbers through the same matrix.

**Keep in mind:** Recovering an input sequence from all preceding output values is different from recovering an arbitrary partition row from a single row sum.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Signed Stirling numbers of the first kind](#stirling-first-kind) · [Formal series composition](#formal-composition) · [Inverse](#inverse)

<a id="bell-numbers"></a>

### Bell numbers

The integers Bₙ counting all partitions of an n-element labelled set into nonempty, unlabelled blocks. Equivalently Bₙ = Σₖ₌₀ⁿ S(n,k), with B₀ = 1.

Bell numbers forget how many blocks a partition has and retain only the total count. The Stirling row separates that count by block number, so summing the row gives Bₙ. The empty set has one empty partition, which explains B₀=1.

This is a scalar summary of richer data. Keeping a Touchard polynomial retains the block-count distribution as coefficients, while evaluating it at one gives the Bell number. Recovering arbitrary coefficient information from that one value would require additional restrictions or measurements.

**Quick example:** B₃ = 1+3+1 = 5, summing S(3,1), S(3,2) and S(3,3).

**In the worked example:** Adding the n = 5 Stirling row gives B₅ = 1+15+25+10+1 = 52.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Fubini numbers](#fubini-numbers) · [Touchard polynomial](#touchard-polynomial)

<a id="fubini-numbers"></a>

### Fubini numbers

The integers Fₙ counting partitions of an n-element labelled set whose blocks are linearly ordered. A partition with k blocks has k! possible block orders, so Fₙ = Σₖ₌₀ⁿ k!S(n,k), with F₀ = 1.

Ordering the blocks distinguishes partitions that the Bell count treats as the same. A partition with k blocks admits k! linear orders of those blocks, which explains the weighted Stirling sum. The ordering applies to the blocks, not to the elements inside each block.

This difference is visible even at small n: for three labels, Bell and Fubini counts are 5 and 13. Their relationship illustrates how a changed observation or weighting can produce another sequence from common underlying combinatorial data without making the two counting problems identical.

**Also called:** Ordered Bell numbers.

**Quick example:** F₃ = 1!·1+2!·3+3!·1 = 13.

**In the worked example:** F₅ = 1·1!+15·2!+25·3!+10·4!+1·5! = 541. The EGF is 1/(2−eᵗ).

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Bell numbers](#bell-numbers) · [Formal reciprocal](#formal-reciprocal)

<a id="touchard-polynomial"></a>

### Touchard polynomial

The polynomial Tₙ(z) = Σₖ₌₀ⁿ S(n,k)zᵏ retaining the complete partition row as coefficients. Evaluation at z = 1 gives Bₙ. Applying the functional zᵏ ↦ k! gives Fₙ.

The variable z marks the number of blocks, so the polynomial retains every entry of one second-kind Stirling row. Different evaluations or linear functionals then extract different summaries from the same coefficient data.

Setting z=1 yields the Bell count. Replacing each monomial zᵏ by k! yields the Fubini count through a different functional, not a fixed ordinary evaluation at one universal z. This makes the family a useful example of representation, observation and information loss within a finite coefficient space.

**Also called:** Bell polynomial of one variable.

**Quick example:** T₃(z) = z+3z²+z³. Its value at 1 is B₃ = 5.

**In the worked example:** T₅(z) = z+15z²+25z³+10z⁴+z⁵. Its value at 1 is 52, while ∫₀∞ e⁻ᵘT₅(u) du = 541.

**Keep in mind:** The one-variable Touchard family is distinct from the multivariable partial Bell polynomials, which encode a different set of inputs.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Stirling numbers of the second kind](#stirling-second-kind) · [Bell numbers](#bell-numbers) · [Fubini numbers](#fubini-numbers)

<a id="roots-of-unity-filter"></a>

### Roots-of-unity filter

For m ≥ 2 and 0 ≤ r &lt; m, work over a field containing a primitive mth root ζ and in which m is invertible. The operator Pᵣf(z) = (1/m)Σₗ₌₀ᵐ⁻¹ ζ⁻ʳˡf(ζˡz) selects precisely the monomials whose degrees are congruent to r modulo m. The polynomial identity also applies coefficientwise to formal series.

On a monomial zᵏ, every phase rotation contributes a scalar power of ζ. The weighted sum equals one when k has the selected residue and zero otherwise. Linearity then proves the formula for every polynomial, and coefficientwise reasoning extends it to formal series.

The average needs both a primitive root and an invertible m. Coefficient selection itself needs neither analytic convergence nor this averaging implementation. A change of polynomial basis must also transport the selector; averaging raw target-variable rotations can select a different decomposition.

**Also called:** Character filter, Residue-degree projector.

**In the worked example:** On a monomial zᵏ, the multiplier (1/m)Σₗ ζˡ⁽ᵏ⁻ʳ⁾ equals one when k ≡ r modulo m and zero otherwise.

**Keep in mind:** The coefficient selector itself does not require roots of unity. This averaging formula needs both the stated root and division by m. A different polynomial basis requires transporting the projector through its basis change.

[Hand-worked example](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md) · [Root of unity](#root-of-unity) · [Residue class](#residue-class) · [Projector](#projector) · [Refinement](#refinement) · [Residue coefficient selector](#coefficient-selector)

<a id="factorial-lane"></a>

### Factorial lane

For integers N ≥ 1 and n ≥ 0, a product of n factors in one arithmetic progression: (a)ₙ;N = ∏ₖ₌₀ⁿ⁻¹(a+Nk), with empty product one. Splitting the factors of a factorial into disjoint residue lanes gives an exact product decomposition.

A lane groups factors of a product according to their residue positions, such as alternating factors in a factorial. Multiplying the disjoint lanes restores the full product because each original factor occurs exactly once. The empty-product convention makes the definition work at n=0.

This multiplicative split differs from separating a series into an additive sum of degree classes. The factorial demonstration relates them through coefficient formulas, with the step size and indexing stated explicitly. Rising-factorial notation can express the same products after rescaling, but its parameters and powers of N must be tracked.

**Also called:** Step factorial, Arithmetic-progression product.

**In the worked example:** The lane starting at 5 with step 10 and three factors is 5·15·25 = 1875. Taking three factors in each of the ten lanes starting at 5 through 14, multiplying the lanes, then multiplying by 4!, reconstructs 34!.

**Keep in mind:** A multiplicative lane of factors and an additive residue section of a series are different objects. The factorial demonstration explicitly relates them.

[Hand-worked example](demonstrations/FACTORIAL_LANES.md) · [Residue class](#residue-class) · [Generalized hypergeometric series](#hypergeometric-series) · [Normalization](#normalization)

<a id="hypergeometric-series"></a>

### Generalized hypergeometric series

The coefficient-defined series ₚF\_q(a₁,…,aₚ; b₁,…,b\_q; z) = Σₙ≥₀ \[(a₁)ₙ⋯(aₚ)ₙ/((b₁)ₙ⋯(b\_q)ₙ)\]zⁿ/n!, where (a)ₙ = a(a+1)⋯(a+n−1). The denominator factors must be defined and nonzero for the terms being used.

The rising factorials encode a systematic ratio between consecutive coefficients, which makes many special-function expansions recognizable in this form. The parameter lists determine both that ratio and whether a numerator can terminate the sequence.

Denominator factors must remain valid for every term being used. A terminating numerator does not license an undefined denominator without a separately specified interpretation. Formal coefficient identities also do not settle convergence at a numerical argument; parameter counts, exceptional parameters and the argument’s location require their own analytic treatment.

**Also called:** Hypergeometric series.

**In the worked example:** The identity (r)ₙ;10 = 10ⁿ(r/10)ₙ converts the selected exponential section into a ₀F₉ series. The parameter r/10 = 1 supplies the separate n! factor.

**Keep in mind:** The displayed identity is coefficientwise. Analytic convergence depends on the parameters and the argument. Terminating cases also require the appropriate denominator conditions.

[Hand-worked example](demonstrations/FACTORIAL_LANES.md) · [Factorial lane](#factorial-lane) · [Power series](#power-series) · [Coefficient recurrence](#coefficient-recurrence)

<a id="signed-euler-numbers"></a>

### Signed Euler numbers

In the Euler demonstration, the sequence Eⱼ is defined by sech(t) = Σⱼ≥₀ Eⱼtʲ/j!. Odd entries vanish and even entries alternate in sign. The sign and index convention must be fixed before comparing Euler tables.

The chosen generating function fixes both the signs and the indexing. Since sech is even, odd-degree entries vanish. Replacing t by it connects the even coefficients to the positive secant convention and introduces the alternating factor (−1)ⁿ.

Published Euler tables use several conventions, including compressed even indices and different signs. A matching name is therefore insufficient for comparing values. State the generating function and the relationship between the sequence index and polynomial degree before transferring a coefficient formula or a recurrence.

**Also called:** Euler numbers in the sech convention.

**In the worked example:** E₀ = 1, E₂ = −1, E₄ = 5 and E₆ = −61. The sequence a(n) = E₂ₙ has a(1) = −1, although E₁ = 0.

[Hand-worked example](demonstrations/EULER_PACKETS.md) · [Secant numbers](#secant-numbers) · [Exponential generating function](#exponential-generating-function) · [Formal reciprocal](#formal-reciprocal)

<a id="secant-numbers"></a>

### Secant numbers

The positive coefficients sₙ defined by sec(t) = Σₙ≥₀ sₙt²ⁿ/(2n)!. Their compressed index n refers to ordinary degree 2n. In the signed sech convention, E₂ₙ = (−1)ⁿsₙ.

The index n counts the nonzero even positions, while the actual power is t²ⁿ. The factorial in the denominator must therefore be (2n)!, which is independent of the choice to store the sequence in a compressed array.

The positive secant values and signed sech Euler values encode related data with different phase signs. This is a useful example of a convention change that should be made explicitly rather than corrected by inspection after a calculation. Truncating a list of secant entries also corresponds to a particular even-degree cutoff.

**Also called:** Positive Euler secant numbers.

**In the worked example:** The first values are 1, 1, 5, 61, 1385, 50521 and 2702765. Thus s₆ = 2702765 is the coefficient of t¹²/12!, not t⁶/6!.

[Hand-worked example](demonstrations/EULER_PACKETS.md) · [Signed Euler numbers](#signed-euler-numbers) · [Binomial coefficient convolution](#binomial-convolution) · [Formal reciprocal](#formal-reciprocal)

<a id="formal-composition"></a>

### Formal series composition

Substitution A(u(t)) of one formal series into another. If u has zero constant term, each output coefficient receives only finitely many contributions, so an arbitrary formal A can be composed without an analytic convergence assumption.

Substitution replaces each power of the outer variable by a power of the inner series. When the inner constant term is zero, its kth power starts at degree at least k, so only finitely many outer terms contribute to any fixed output degree.

That degree argument makes arbitrary formal outer series composable in the stated setting. If the inner constant term is nonzero, infinitely many outer terms may contribute to one coefficient, so an additional valid interpretation is needed. A polynomial outer expression avoids that problem because it has only finitely many terms.

**Also called:** Formal substitution.

**In the worked example:** Substituting u(t) = eᵗ−1 into the weight EGF A(u) gives the transformed EGF C(t) = A(eᵗ−1).

**Keep in mind:** If A is a polynomial, substitution is also a finite operation without the zero-constant-term condition. General infinite outer series need a valid formal or analytic setting.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Power series](#power-series) · [Compositional inverse of a formal series](#compositional-inverse) · [Stirling transform](#stirling-transform)

<a id="compositional-inverse"></a>

### Compositional inverse of a formal series

For a formal series u(t) over a field with u(0) = 0 and nonzero linear coefficient, the unique series v(t) with v(0) = 0 satisfying u(v(t)) = t and v(u(t)) = t. The inverse concerns substitution.

The nonzero linear coefficient allows successive coefficient equations to solve for a reverse substitution. The zero constant term ensures that the inverse remains centered at zero and that formal composition is defined in the stated way.

This inverse reverses a change of argument, not multiplication of values. For u(t)=2t, its substitution inverse is t/2, whereas a multiplicative reciprocal would involve 1/(2t) and lie outside ordinary power series at zero. Keeping the operation being inverted explicit prevents these distinct constructions from being mixed.

**Also called:** Series reversion, Formal inverse under substitution.

**Quick example:** The substitution inverse of u(t) = 2t is v(t) = t/2. Their product is not the identity being tested.

**In the worked example:** The compositional inverse of eᵗ−1 is log(1+t). Consequently C(t) = A(eᵗ−1) is inverted by A(u) = C(log(1+u)).

**Keep in mind:** A formal reciprocal solves u(t)v(t) = 1 and requires a nonzero constant coefficient. These are different inverse operations with different hypotheses.

[Hand-worked example](demonstrations/STIRLING_BELL_FUBINI.md) · [Formal series composition](#formal-composition) · [Formal reciprocal](#formal-reciprocal) · [Inverse](#inverse)

<a id="polynomial-degree"></a>

### Polynomial degree

For a nonzero polynomial, the largest exponent having a nonzero coefficient. Over a field, degrees add under multiplication of nonzero polynomials. The zero polynomial needs a separate convention, often degree −∞, when degree formulas include it.

Degree records the highest occupied ordinary-power position after zero coefficients are removed. It controls how finite polynomial operations change the size of a coefficient description: differentiation lowers it in characteristic zero, multiplication adds degrees for nonzero factors over a field, and translation does not raise it.

It is not the same as every packet address or eigenvalue label. A polynomial expressed in falling-factorial coordinates can mix ordinary-power residues after expansion. Positive characteristic can also make a derivative lose its expected leading term, so familiar degree arguments need their field assumptions.

**Also called:** Degree of a polynomial.

**Quick example:** The polynomial 4−2x+3x³ has degree 3. A falling-factorial basis element b₃ also has ordinary degree 3.

[Further reading](operators/POLYNOMIAL.md) · [Coefficient](#coefficient) · [Falling factorial](#falling-factorial) · [Truncation](#truncation)

<a id="monic-polynomial"></a>

### Monic polynomial

A nonzero polynomial whose highest-degree coefficient is one. A sequence with one monic polynomial of each degree gives an invertible triangular change from ordinary powers on every finite degree range.

Monicity fixes the leading scale of a polynomial while leaving its lower coefficients free. A degree-k monic polynomial differs from xᵏ only by lower-degree terms, which explains the triangular relationship with ordinary powers.

Having one such polynomial at each degree gives unique finite polynomial coordinates. The falling factorials use this fact even in coefficient rings where factorial division is unavailable. Monicity supplies an algebraic basis-change argument; it does not imply orthogonality, numerical conditioning or a particular multiplication rule in the new coordinates.

**Quick example:** x(x−1)(x−2) = x³−3x²+2x is monic. The constant polynomial 1 is monic of degree zero.

[Further reading](operators/POLYNOMIAL.md) · [Polynomial degree](#polynomial-degree) · [Basis](#basis) · [Falling factorial](#falling-factorial)

<a id="rising-factorial"></a>

### Rising factorial

The finite product (a)ₙ = a(a+1)⋯(a+n−1), with (a)₀ = 1. This is the Pochhammer convention used in the hypergeometric series entry. The notation must be distinguished from falling factorials and from the step-N factorial lanes.

The rising factorial advances its factors upward by one, and the zero-length product is one. It provides compact coefficient formulas for hypergeometric series and for rescaled arithmetic-progression products.

Notation is a common source of confusion because some sources use similar parentheses for falling products. Check the displayed factors or the stated Pochhammer convention. Reversing the direction changes roots, signs and recurrence relations, so a familiar-looking symbol alone does not justify importing another source’s formula.

**Also called:** Pochhammer symbol.

**Quick example:** (2)₃ = 2·3·4 = 24, while the falling factorial 2(2−1)(2−2) is zero.

[Further reading](demonstrations/FACTORIAL_LANES.md) · [Falling factorial](#falling-factorial) · [Factorial lane](#factorial-lane) · [Generalized hypergeometric series](#hypergeometric-series)

<a id="cauchy-product"></a>

### Cauchy product

The coefficient rule for multiplying ordinary formal power series: the coefficient of zⁿ in A(z)B(z) is Σₖ₌₀ⁿ aₖbₙ₋ₖ. Each coefficient uses finitely many terms, so this formal rule needs no analytic convergence assumption.

The Cauchy product is ordinary series multiplication organized by output degree. Each pair of terms contributes to the degree obtained by adding its two exponents. Collecting those contributions gives the convolution formula for the new coefficient sequence.

This finite-per-coefficient interpretation is automatically meaningful formally. Analytic statements about multiplying convergent numerical sums require their relevant convergence hypotheses. The term also differs from binomial convolution, which appears when the stored coefficients use an exponential rather than ordinary power basis.

**Quick example:** The coefficient of z² in (1+2z+3z²)(1+4z+5z²) is 5+8+3 = 16.

[Further reading](demonstrations/EULER_PACKETS.md) · [Coefficient convolution](#convolution) · [Binomial coefficient convolution](#binomial-convolution) · [Ordinary generating function](#ordinary-generating-function)

<a id="formal-power-series"></a>

### Formal power series

An infinite coefficient list written as Σₙ≥₀ aₙzⁿ and manipulated coefficientwise over a declared ring. Addition and multiplication are algebraic operations on these lists. Evaluating the series at a numerical z is a separate analytic question.

A formal series is treated as its entire coefficient sequence, with equality meaning agreement at every position. The variable is a bookkeeping symbol rather than a numerical input. Infinite notation is harmless for operations whose individual output coefficients have well-defined finite formulas.

This makes formal inversion, residue selection and suitable composition useful independently of analytic convergence. A finite prefix verifies only a finite set of coefficient statements. To evaluate the series or bound a discarded tail at a chosen number, one must supply analytic information beyond the formal algebra.

**Also called:** Formal series.

**Quick example:** The identity (1−z)(1+z+z²+⋯) = 1 is valid formally even when no numerical value for z is chosen.

[Further reading](demonstrations/EULER_PACKETS.md) · [Power series](#power-series) · [Formal reciprocal](#formal-reciprocal) · [Formal series composition](#formal-composition) · [Truncation](#truncation)

<a id="radius-of-convergence"></a>

### Radius of convergence

For a complex power series centered at zero, the radius R such that the series converges absolutely for |z| &lt; R and diverges for |z| &gt; R. The endpoints R = 0 and R = ∞ are allowed. Boundary convergence must be checked separately.

The radius describes where one complex power series represents a convergent sum around its center. Inside the open disk it converges absolutely; beyond the radius it cannot converge. Boundary points can behave differently from one another and need separate analysis.

The radius does not by itself provide a useful finite-truncation error at every interior point. Evaluation near the boundary may need many terms or stronger coefficient estimates. A formal identity remains valid coefficientwise even when the corresponding numerical substitution lies outside this convergence region.

**Quick example:** The geometric series Σₙ≥₀ zⁿ has radius 1. At z = 1 its terms do not tend to zero.

[Further reading](demonstrations/EULER_PACKETS.md) · [Power series](#power-series) · [Formal power series](#formal-power-series) · [Truncation](#truncation)

<a id="taylor-coefficient"></a>

### Taylor coefficient

For a function analytic near zero, the ordinary coefficient of zⁿ in its Taylor series is f⁽ⁿ⁾(0)/n!. Its exponentially normalized coefficient is f⁽ⁿ⁾(0). The basis convention determines which number is called the stored coefficient.

Taylor coefficients connect local derivative data with a power-series representation. The factorial compensates for differentiating zⁿ exactly n times. Forgetting it confuses an ordinary coefficient list with an exponentially normalized sequence.

Knowing derivatives formally or to finite order does not automatically provide a convergent Taylor representation of a general smooth function. The analytic setting in this definition supplies that interpretation. For a finite approximation, the range of validity and a remainder estimate still need to accompany the retained coefficients.

**Quick example:** For exp(z), every derivative at zero is 1, while its ordinary coefficients are 1, 1, 1/2, 1/6, ….

[Further reading](demonstrations/EULER_PACKETS.md) · [Coefficient](#coefficient) · [Derivative in the series example](#derivative) · [Exponential generating function](#exponential-generating-function)

<a id="backward-difference"></a>

### Backward difference

The polynomial operator ∇f(x) = f(x)−f(x−1), with unit step. It differs from the forward difference Δf(x) = f(x+1)−f(x). The falling-degree operator is x∇, while the falling-factorial lowering operator is Δ.

Backward difference compares the current value with its value one step earlier. It is related to forward difference by translation, but they act differently at the same argument. Their explicit formulas should therefore be preserved when transporting operators or comparing coefficient recurrences.

In the falling-factorial calculus, multiplying the backward difference by x gives the degree operator. The plain backward difference alone is not that degree counter. On finite sampled signals, both directions also require a boundary rule for the sample requested outside the stored range.

**Quick example:** For f(x) = x², ∇f = 2x−1 and Δf = 2x+1.

[Further reading](operators/POLYNOMIAL.md) · [Forward difference](#forward-difference) · [Falling-degree operator](#degree-operator) · [Polynomial translation operator](#translation-operator)

<a id="signal-and-spectral-evaluation"></a>

## Signals and spectral evaluation

Finite transforms, phase carries, Gaussian quadratic forms and the distinct error controls used in K-COS.

[Finite impulse response filter](#finite-impulse-response-filter) · [Polyphase carry](#polyphase-carry) · [Discrete Fourier transform](#discrete-fourier-transform) · [Discrete cosine transform](#discrete-cosine-transform) · [Gram operator](#gram-operator) · [Range core](#range-core) · [Characteristic function](#characteristic-function) · [Gaussian quadratic form](#gaussian-quadratic-form) · [COS method](#cos-method) · [Centered spectral packet](#centered-spectral-packet) · [Directed enclosure](#directed-enclosure) · [Analytic error budget](#analytic-error-budget) · [Circular shift](#circular-shift) · [Downsampling](#downsampling) · [Aliasing](#aliasing) · [Analysis filter bank](#filter-bank) · [Wavelet lifting step](#lifting-step) · [Parseval identity in chosen coordinates](#parseval-identity) · [Signal boundary convention](#boundary-condition)

<a id="finite-impulse-response-filter"></a>

### Finite impulse response filter

A linear filter given by finitely many taps, or coefficients, applied to specified shifts of a signal. In a causal convention yₙ = Σₗ₌₀ᴸ⁻¹ hₗxₙ₋ₗ. A finite signal also needs a boundary rule, such as zero extension or circular indexing.

Each tap weights one shifted copy of the input, and summing those copies forms the output. The filter is linear because its coefficients are fixed and each shift is linear. A short tap list therefore defines an operation on an entire sequence, not just on one sample.

For a finite stored signal, taps alone do not determine the matrix. Circular indexing, zero extension and other boundary rules produce different endpoint outputs. Moving the filter into polyphase or wavelet coordinates must carry the actual shifts, their phase carries and the selected boundary convention.

**Also called:** FIR, FIR filter, Finite convolution filter.

**In the worked example:** On the sixteen-sample circular signal, H = I+2T−T² gives (Hx)₁₀ = 12+2(−4)−(−4) = 8.

**Keep in mind:** The worked wavelet example uses circular indexing. The catalog’s causal FIR entry uses zero extension. The transfer formula must retain the chosen boundary convention.

[Hand-worked example](demonstrations/WAVELET_POLYPHASE.md) · [Further reading](operators/catalog/E_SIGNAL.md#op-081) · [Polyphase decomposition](#polyphase) · [Polyphase carry](#polyphase-carry) · [Linear map](#linear-map) · [Composition](#composition)

<a id="polyphase-carry"></a>

### Polyphase carry

The extra shift in a phase coordinate required when an index crosses a residue boundary. Splitting a signal into residue phases changes both the phase label and, when necessary, the position within that phase.

The carry appears because a global index contains both a residue and a position within that residue stream. Crossing the residue boundary changes the quotient position as well as the phase label. Ignoring that second change generally shifts the wrong sample into a filter calculation.

For a one-sample delay and even–odd phases, the new odd phase comes from the old even phase at the same within-phase index, while the new even phase comes from the previous odd position. Reversing the shift direction moves the carry to the other block.

**Also called:** Lane-boundary carry, Phase carry.

**In the worked example:** For even and odd rows E and O, one backward circular shift sends the even output to ZO and the odd output to E. Its two-phase matrix is \[\[0,Z\],\[I,0\]\], with Z the half-rate delay.

**Keep in mind:** Forward shifts place the carry in a different block from backward shifts. Its position follows from the index convention.

[Hand-worked example](demonstrations/WAVELET_POLYPHASE.md) · [Polyphase decomposition](#polyphase) · [Finite impulse response filter](#finite-impulse-response-filter) · [Transfer block](#transfer-block) · [Residue class](#residue-class)

<a id="discrete-fourier-transform"></a>

### Discrete Fourier transform

For a complex vector x of length N ≥ 1, the convention used here is x̂ₖ = Σₙ₌₀ᴺ⁻¹ xₙ exp(−2πikn/N). The inverse uses the positive exponential sign and divides by N.

Each Fourier coordinate measures the input against one periodic complex oscillation. The complete set of N coordinates retains the original N samples, because the finite Fourier matrix is invertible with the stated inverse normalization.

Circular shifts and circular convolution have especially simple representations in these coordinates. Zero-extended filtering is a different finite operation unless embedded or otherwise handled consistently. Fourier magnitude alone also loses phase information, so retaining a full transform and retaining only its magnitudes are different summaries.

**Also called:** DFT, Finite Fourier transform.

**Keep in mind:** A different normalization may distribute the factor 1/N between the two maps. Changing conventions changes their matrix entries.

[Further reading](operators/catalog/E_SIGNAL.md#op-090) · [Root of unity](#root-of-unity) · [Coordinates](#coordinates) · [Normalization](#normalization) · [Discrete cosine transform](#discrete-cosine-transform)

<a id="discrete-cosine-transform"></a>

### Discrete cosine transform

A coordinate transform of a real vector of length N ≥ 1 using cosine samples. The catalog fixes orthonormal DCT-II: yₖ = αₖΣₙ₌₀ᴺ⁻¹xₙ cos(π(n+1/2)k/N), where α₀ = 1/√N and αₖ = √(2/N) for k &gt; 0.

The DCT expresses a real finite vector using sampled cosine patterns. Its type specifies where those samples are taken and how endpoint behavior is encoded. In the orthonormal DCT-II convention, the differing zero-mode factor makes the complete transform preserve Euclidean energy.

Changing type or normalization changes the transform matrix and its inverse formula. The COS probability method also uses cosine modes but approximates distributional quantities from characteristic-function values. Sharing the word cosine does not make that analytic expansion identical to this finite data-coordinate transformation.

**Also called:** DCT, DCT-II.

**Keep in mind:** DCT type and normalization are part of the definition. The COS probability method uses a Fourier-cosine expansion but is not simply this finite data transform.

[Further reading](operators/catalog/E_SIGNAL.md#op-091) · [Discrete Fourier transform](#discrete-fourier-transform) · [Orthogonal matrix](#orthogonal-matrix) · [Normalization](#normalization) · [COS method](#cos-method)

<a id="gram-operator"></a>

### Gram operator

For a real matrix A, either K = AAᵀ on its output space or H = AᵀA on its input space. Both are positive semidefinite. Their positive eigenvalues agree with multiplicity, although their dimensions and zero-eigenvalue multiplicities can differ.

The two Gram operators view the same factor from opposite sides. A\*A measures interactions between input-coordinate columns, while AA\* measures the resulting output-space covariance or energy structure. Their positive singular-value information agrees even when one space has many more coordinates than the other.

Their zero directions can differ because their dimensions differ. A block sum for AA\* is exact when every column block is retained; deleting a block changes the operator. This makes Gram structure useful for compression, provided exact range capture and omitted contributions are distinguished.

**Also called:** Gram matrix, Sample Gram, Feature Gram.

**Keep in mind:** For a column partition A = \[A₁ … A\_B\], the exact identity AAᵀ = Σ\_b A\_bA\_bᵀ retains every column. Dropping a block changes the operator.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/01_gaussian.tex#L39) · [Positive semidefinite matrix](#positive-semidefinite) · [Eigenvalue](#eigenvalue) · [Range core](#range-core) · [Gaussian quadratic form](#gaussian-quadratic-form) · [Classical frame operator](#classical-frame-operator)

<a id="range-core"></a>

### Range core

A representation of a real factor A in coordinates on a chosen subspace. If Q has orthonormal columns and the range of A is contained in the range of Q, then B = QᵀA gives A = QB. The matrices BBᵀ and AAᵀ have the same nonzero spectrum, including multiplicity. The core is smaller when Q has fewer columns than A has rows.

The matrix Q supplies orthonormal coordinates for a subspace containing every column of A. Encoding those columns as B=Q\*A then loses no information, because synthesis gives QB=A. The potentially smaller matrix BB\* retains the nonzero spectral information relevant to the full Gram operator.

The containment hypothesis is the key exactness condition. If Q captures only an approximate range, A−QQ\*A is a residual that needs a bound. A numerical threshold declaring some directions negligible cannot by itself turn that approximation into exact rank reduction.

**Also called:** Exact range core, Range compression.

**Keep in mind:** If the chosen subspace misses part of the range, the omitted residual requires a separate bound. A floating-point rank threshold does not establish exact range capture.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/04_range.tex#L127) · [Gram operator](#gram-operator) · [Image](#image) · [Orthogonal projector](#orthogonal-projector) · [Residual](#residual)

<a id="characteristic-function"></a>

### Characteristic function

For a real random variable Q, φ(t) = E\[exp(itQ)\] at real frequency t. It encodes the probability law in Fourier coordinates. Unlike a real moment-generating function, it is defined for every real t because the integrand has modulus one.

The expectation averages complex phases generated by the random variable at a chosen frequency. At t=0 every phase is one, so φ(0)=1. Its real and imaginary parts capture cosine and sine averages, making it a natural input for Fourier-based distribution calculations.

Unlike a moment-generating function at arbitrary real arguments, it always exists for a real random variable. That existence does not automatically give a stable finite inversion formula. Tail evaluation still needs truncation windows, mode bounds and arithmetic control in the method using the transform.

**Also called:** Probability characteristic function, CF.

**Keep in mind:** For an admissible exponential tilt with cumulant generator κ, the monograph uses φθ(t) = exp(κ(θ+it)−κ(θ)). The domain and logarithm branch are stated with that transform.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/06_packets.tex#L73) · [COS method](#cos-method) · [Gaussian quadratic form](#gaussian-quadratic-form) · [Complex conjugate](#complex-conjugate)

<a id="gaussian-quadratic-form"></a>

### Gaussian quadratic form

A random variable Q = XᵀMX with real Gaussian vector X and symmetric matrix M. In the central positive case X has mean zero and covariance Σ, M is positive semidefinite, and Q has the same law as ΣⱼλⱼZⱼ² for independent standard normal Zⱼ and eigenvalues λⱼ of Σ¹ᐟ²MΣ¹ᐟ².

The quadratic form measures a weighted squared size of a Gaussian vector, including correlations through its covariance. In the central positive case, a spectral coordinate change reduces its law to a weighted sum of independent squared standard normals.

The relevant eigenvalues belong to the covariance-weighted symmetric matrix, not generally to M alone. Zero mean and positive semidefiniteness determine the stated central nonnegative setting. Indefinite or noncentral forms require their corresponding extensions, so a positive-tail formula should not be applied merely because an expression looks quadratic.

**Also called:** Quadratic form of a Gaussian vector.

**Keep in mind:** The zero-mean assumption gives the central reduction. Positive semidefiniteness makes the eigenvalues nonnegative and the law supported on \[0,∞), as required by the positive-tail formula. A central indefinite form has the same reduction with signed eigenvalues. Noncentral forms require their additional parameters. With no nonzero eigenvalues, Q is identically zero.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/01_gaussian.tex#L9) · [Finite-dimensional Gaussian model](#gaussian-model) · [Covariance matrix](#covariance) · [Eigenvalue](#eigenvalue) · [Characteristic function](#characteristic-function)

<a id="cos-method"></a>

### COS method

A Fourier-cosine method for evaluating distributional quantities from characteristic-function values. K-COS applies this representation to Gaussian quadratic-form tails, with a stated window, retained mode count, spectral approximation and error bounds.

The method represents the desired distributional quantity through a cosine expansion derived from transform information. A finite implementation chooses a window and retains finitely many modes, so its output combines several distinct approximation decisions rather than just one numerical integration rule.

K-COS additionally approximates spectral transform data using packets. A justified final error statement must therefore account for packet, window or folding, and omitted-mode effects, as well as finite arithmetic when a numerical enclosure is claimed. A finite cosine sum alone is an approximation, however accurately its terms were evaluated.

**Also called:** Fourier-cosine method.

**Keep in mind:** The positive-tail formula uses frequencies kπ/b on \[0,b\] and half weight on the zero mode. A finite sum is an approximation until the applicable remainders and numerical arithmetic have been controlled.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/07_inversion.tex#L1) · [Characteristic function](#characteristic-function) · [Gaussian quadratic form](#gaussian-quadratic-form) · [Centered spectral packet](#centered-spectral-packet) · [Analytic error budget](#analytic-error-budget)

<a id="centered-spectral-packet"></a>

### Centered spectral packet

In K-COS, a nonempty group P of eigenvalues represented by its count n, mean μ and centered power sums Mₘ = Σⱼ∈P(λⱼ−μ)ᵐ. Thus M₀ = n and M₁ = 0. Truncated transform expansions also carry a remainder bound.

Centering separates a packet’s location from its internal spread. The mean supplies the reference eigenvalue, while centered power sums describe deviations around it. The first centered sum vanishes by construction, simplifying the expansion used to approximate transform contributions.

Retaining only a finite number of those summaries generally loses information about individual eigenvalues. The approximation needs a remainder bound under the frequency-dependent condition stated in the entry. Grouping nearby values is therefore a computational design choice, not an automatic exact replacement of their full spectral data.

**Also called:** Spectral packet, Centered packet.

**Keep in mind:** The expansion needs |2s/(1−2sμ)|·maxⱼ|λⱼ−μ| &lt; 1 on the frequencies and tilt being used. Nearby eigenvalues alone do not establish that condition for every query.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/06_packets.tex#L94) · [Packet](#packet) · [Eigenvalue](#eigenvalue) · [COS method](#cos-method) · [Analytic error budget](#analytic-error-budget)

<a id="directed-enclosure"></a>

### Directed enclosure

An interval guaranteed to contain the specified exact quantity. Its finite arithmetic rounds outward, and its final endpoints include every required analytic remainder. The claim concerns the encoded inputs and stated mathematical model.

An enclosure returns a set containing the specified exact answer, rather than only a plausible central estimate. Outward rounding protects the containment against finite arithmetic, while analytic remainder bounds protect it against the deliberate approximations in the method.

Both protections are needed. Rigorously rounding an incomplete formula does not enclose errors from omitted modes or uncertain inputs. Likewise, a proven real-arithmetic error budget does not automatically certify floating-point endpoints. Relative probability acceptance also needs a positive lower endpoint before division is meaningful.

**Also called:** Outward-rounded enclosure, Probability enclosure.

**Keep in mind:** For a probability interval \[p₋,p₊\], the stated relative acceptance test requires p₋ &gt; 0 and p₊/p₋−1 ≤ ε. A narrow interval is insufficient if a required source of error was omitted.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/09_intervals.tex#L1) · [Certificate](#certificate) · [Rounding](#rounding) · [Analytic error budget](#analytic-error-budget) · [Tolerance](#tolerance)

<a id="analytic-error-budget"></a>

### Analytic error budget

A sum of justified bounds for the approximation steps in a mathematical model. The K-COS budget separates spectral-packet approximation, support and cosine-folding error, and omitted Fourier modes.

An error budget separates approximation mechanisms so that each has an explicit bound and the combined effect can be controlled, often through a triangle inequality. This makes it possible to identify whether more spectral detail, a larger window or more modes addresses the dominant contribution.

The bounds must apply simultaneously to the stated parameters and query. They also need to measure compatible quantities before being added. Finite-arithmetic rounding and input-encoding uncertainty belong in the final numerical guarantee even when they are tracked outside the analytic portion of the budget.

**Also called:** Packet-support-mode budget.

**Keep in mind:** These real or complex arithmetic bounds do not automatically enclose floating-point rounding. A numerical certificate must also account for its finite arithmetic and exact-input interpretation.

[Further reading](https://github.com/KomorebiP/Operation-KOMOREBI/blob/da8e6d29558688c3580a5258bf11773449428452/monographs/cos-method/book/chapters/07_inversion.tex#L1) · [Centered spectral packet](#centered-spectral-packet) · [Truncation](#truncation) · [Directed enclosure](#directed-enclosure) · [Residual](#residual)

<a id="circular-shift"></a>

### Circular shift

A shift of a finite length-N signal with indices reduced modulo N. Under the convention (Sx)ₙ = xₙ₋₁ mod N, the last sample moves to the first position. This boundary rule differs from zero extension.

A circular shift treats the finite signal as one period of a repeating sequence. Samples crossing an endpoint reappear at the opposite endpoint, so the operation is a reversible permutation of the stored coordinates and preserves their Euclidean energy.

This boundary behavior distinguishes it from a zero-extended delay, which can discard the final sample and insert zero. Fourier diagonalization and polyphase carry formulas must use the intended convention. Matching the shift’s name or tap pattern is insufficient if the endpoint model changes.

**Also called:** Cyclic shift, Periodic delay.

**Quick example:** The circular delay sends (1,2,3,4) to (4,1,2,3).

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Finite impulse response filter](#finite-impulse-response-filter) · [Polyphase carry](#polyphase-carry) · [Discrete Fourier transform](#discrete-fourier-transform)

<a id="downsampling"></a>

### Downsampling

Retaining samples on a specified residue class: with factor m and phase r, yₖ = xₘₖ₊ᵣ. The phase and boundary convention are part of the operation. Retaining only one phase generally loses information about the others.

Downsampling keeps one phase of an indexed sequence. It reduces the number of stored samples but generally merges inputs that differ on the discarded phases. The starting residue r matters because changing it selects a different subset.

Keeping all phases as separate streams is instead a reversible polyphase reorganization. Exact recovery from fewer samples can become possible with a restricted signal class or a suitable complete filter bank. Such an input restriction or complementary channel is an additional hypothesis, not a consequence of downsampling alone.

**Also called:** Decimation.

**Quick example:** Taking the even phase of (1,2,3,4) gives (1,3). Retaining the odd phase (2,4) as well permits interleaving back to the original signal.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Polyphase decomposition](#polyphase) · [Aliasing](#aliasing) · [Reconstruction](#reconstruction)

<a id="aliasing"></a>

### Aliasing

Failure of a sampling operation to distinguish different inputs. In frequency language, distinct oscillations can produce the same retained samples. Additional input restrictions or complementary filter-bank outputs are needed for exact recovery.

Aliasing is a collision in the sampling map. Oscillations that differ before sampling can become indistinguishable afterward, so no algorithm receiving only those samples can recover which unrestricted input was present.

Anti-alias filtering changes the permitted or retained frequency content before downsampling, while multi-channel reconstruction can retain complementary information. These remedies have their own assumptions. Relabeling the sampled frequencies does not restore distinctions that the acquisition process has already removed.

**Quick example:** On integer indices, the signals 1 and (−1)ⁿ both give the constant sequence 1 after retaining only even-indexed samples.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Downsampling](#downsampling) · [Collision witness](#collision-witness) · [Exact recovery from a summary](#exact-recovery)

<a id="filter-bank"></a>

### Analysis filter bank

A collection of filters and sampling maps sending one signal to several component streams. A synthesis bank combines those streams into an output signal. Perfect reconstruction is a property of the combined analysis and synthesis maps with their declared delays and boundary conventions.

An analysis bank distributes information across several filtered streams, often followed by phase selection or downsampling. A synthesis bank reconstructs by filtering and combining those streams. Individual streams may be insufficient even when their complete collection retains the original signal.

Perfect reconstruction is an identity of the combined maps, with any allowed delay or scale stated explicitly. It depends on the filters, boundary rules and sampling phases together. Checking each channel separately or retaining only its energy does not establish that joint identity.

**Quick example:** For a pair (u,v), the Haar analysis stores average (u+v)/2 and detail (u−v)/2; synthesis returns their sum and difference.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Analysis and synthesis](#analysis-synthesis) · [Downsampling](#downsampling) · [Polyphase decomposition](#polyphase) · [Finite impulse response filter](#finite-impulse-response-filter)

<a id="lifting-step"></a>

### Wavelet lifting step

An invertible update of one component using another, such as predicting odd samples from even samples and then updating the even stream with the prediction residual. The inverse undoes the updates in reverse order. This signal-processing meaning of lifting differs from lifting an object through a quotient.

Lifting builds an invertible transform from simple updates whose inverses are explicit. A predict step stores a discrepancy using another stream; an update step then changes that other stream using the stored discrepancy. Reversing the sequence and subtracting the same updates recovers the inputs.

Normalization can be applied separately from these updates. The prediction residual therefore need not equal the tutorial’s half-difference coefficient without an additional scale and sign conversion. This constructive factorization explains reversibility, but does not by itself imply orthonormality or a particular boundary extension.

**Quick example:** Set d = v−u, then a = u+d/2. Recover u = a−d/2 and v = u+d.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Analysis filter bank](#filter-bank) · [Haar pair](#haar-pair) · [Inverse](#inverse) · [Lift](#lift)

<a id="parseval-identity"></a>

### Parseval identity in chosen coordinates

An equality between the squared norm of an object and the correctly weighted squared magnitudes of its complete transform coefficients. Orthonormal coordinates use unit weights. Other normalizations change the weights, so energy formulas must follow the analysis convention.

The identity connects coefficient bookkeeping with the geometry of the original object. For a complete orthonormal transform, every squared coefficient magnitude contributes directly to the total energy. Nonorthonormal but invertible coordinates instead need weights or a metric, potentially including cross terms.

This distinction matters when ranking coefficients for truncation. A large raw coefficient does not necessarily represent a large physical energy contribution under an arbitrary normalization. Exact reconstruction and an additive sum-of-squares identity are separate properties and should each be established for the representation used.

**Quick example:** With a = (u+v)/2 and d = (u−v)/2, u²+v² = 2(a²+d²). The factor 2 belongs to this normalization.

[Further reading](demonstrations/WAVELET_POLYPHASE.md) · [Orthonormal basis](#orthonormal-basis) · [Coefficient metric](#coefficient-metric) · [Normalization](#normalization)

<a id="boundary-condition"></a>

### Signal boundary convention

A rule supplying samples outside the stored finite signal, such as periodic continuation, zero extension or reflection. A filter’s taps do not determine its finite matrix until this rule and the indexing convention have been fixed.

A boundary convention completes a finite signal into the values needed by a shift or filter near its endpoints. Zero extension inserts zeros, periodic continuation wraps around, and reflection mirrors samples according to its specified endpoint rule.

These choices can agree on interior outputs while disagreeing at the edges. Consequently a test using only interior samples can miss an incorrect finite operator. The convention must travel with any polyphase, wavelet or matrix representation of the filter rather than be supplied silently by an implementation default.

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

Impedance describes the joint magnitude and phase relation between voltage and current in the stated linear frequency-domain model. Resistance contributes its real part, while reactance contributes its imaginary part. Both generally depend on the frequency at which the load is examined.

The Smith chart changes coordinates from impedance to reflection; it does not change the physical load. A single-frequency impedance value also differs from an entire rational impedance function Z(s). Matching a value at one frequency is therefore a weaker request than realizing a prescribed function across its domain.

**Quick example:** The load Z = 25+i25 ohms with Z₀ = 50 ohms has normalized impedance z = (1+i)/2.

[Further reading](demonstrations/SMITH_CHART.md) · [Normalized impedance](#normalized-impedance) · [Admittance](#admittance) · [Reflection coefficient](#reflection-coefficient)

<a id="normalized-impedance"></a>

### Normalized impedance

The dimensionless ratio z = Z/Z₀ relative to a declared reference impedance. In the Smith-chart guide Z₀ is positive and real, so the real and imaginary parts are normalized resistance and reactance.

Normalization measures the load relative to the chosen reference, removing its physical units from the chart coordinates. The same physical impedance can occupy different normalized positions when Z₀ changes. A normalized value of one means equality with that reference.

The guide assumes a positive real reference resistance, which supports its familiar passive-disk and return-loss formulas. More general complex-reference conventions require their own definitions. Physical component values must also be converted consistently when moving between normalized circuit formulas and a dimensional implementation.

**Quick example:** Changing Z₀ from 50 to 25 ohms changes the coordinates of a 50-ohm resistor from z = 1 to z = 2, while the physical resistor stays the same.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance](#impedance) · [Normalization](#normalization) · [Reflection coefficient](#reflection-coefficient)

<a id="admittance"></a>

### Admittance

The reciprocal Y = 1/Z where Z is nonzero, measured in siemens. With normalized impedance z, normalized admittance is y = 1/z. Switching to the admittance grid changes the description of the same load.

Admittance describes the same one-port using current per voltage instead of voltage per current. Parallel combinations are often simpler in this description, just as series combinations are simpler in impedance coordinates. The reciprocal relation must still respect zeros and poles.

On the normalized chart, the admittance reflection coordinate is the negative of the impedance reflection coordinate under the stated convention. Switching grids therefore changes the coordinate description, not the load. An ideal short or open needs limiting treatment rather than a finite reciprocal value in both descriptions.

**Quick example:** If z = (1+i)/2, then y = 1−i.

**Keep in mind:** A short has zero impedance and no finite reciprocal admittance.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance](#impedance) · [Normalized impedance](#normalized-impedance) · [Impedance Cayley transform](#cayley-transform)

<a id="reflection-coefficient"></a>

### Reflection coefficient

For normalized impedance z with z ≠ −1, the Smith coordinate Γ = (z−1)/(z+1). For finite passive loads with nonnegative resistance, |Γ| ≤ 1. Its magnitude measures mismatch relative to the declared positive real reference resistance.

The reflection coordinate converts the positive-real load half-plane into a disk. Its center represents a match, and its boundary represents the ideal passive zero-resistance limit together with the open-load limiting point. Both magnitude and phase are needed to specify a general chart position.

The magnitude is especially useful because a lossless line preserves it. Equal magnitudes therefore place loads on the same continuous line-rotation circle, but a prescribed finite cyclic action can impose further phase restrictions. Reflection data at one frequency do not alone identify a unique broadband circuit.

**Also called:** Gamma, Load reflection coefficient.

**Quick example:** For z = (1+i)/2, Γ = (−1+2i)/5 and |Γ|² = 1/5.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance Cayley transform](#cayley-transform) · [Impedance](#impedance) · [Matched load](#matched-load) · [Voltage standing-wave ratio](#vswr)

<a id="cayley-transform"></a>

### Impedance Cayley transform

The fractional-linear coordinate map Γ = (z−1)/(z+1) and its inverse z = (1+Γ)/(1−Γ), on their stated domains. It takes the open positive-real half-plane to the open unit disk and finite purely reactive impedances to its boundary.

The Cayley map is reversible away from its excluded denominator zeros. It allows a geometric statement in the reflection disk to be translated into an impedance-coordinate statement in a half-plane. For example, rotating Γ becomes a fractional-linear action on z after conjugating by the coordinate map.

Boundary behavior requires care because finite disk coordinates can correspond to an infinite impedance limit. The point Γ=1 is a pole of the inverse formula. Treating it as an ordinary finite load can invalidate arithmetic or a claimed packet decomposition at that point.

**Quick example:** The matched point z = 1 maps to Γ = 0. The point Γ = 1 has no finite impedance under the inverse formula.

**Keep in mind:** Other literature uses different Cayley-transform conventions. Keep this direction and reference normalization explicit.

[Further reading](demonstrations/SMITH_CHART.md) · [Reflection coefficient](#reflection-coefficient) · [Normalized impedance](#normalized-impedance) · [Pole of a rational function](#pole)

<a id="matched-load"></a>

### Matched load

A load with impedance equal to the chosen reference resistance in this real-reference model. Its normalized impedance is z = 1 and its reflection coefficient is zero. Matching is relative to the reference and frequency being used.

A match eliminates reflection at the chosen reference plane in this model. It fixes both the resistance and reactance requirements: the load equals the positive real Z₀, rather than merely having a convenient resistance magnitude.

Matching depends on frequency and reference conventions. A lossless line can rotate a nonzero reflection coefficient but cannot change its magnitude to zero, so line rotation alone cannot match an arbitrary mismatched load. Adding a matching network poses a different realization problem with additional permitted operations and components.

**Quick example:** A 50-ohm resistor is matched to a 50-ohm real reference and gives VSWR 1.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance](#impedance) · [Reflection coefficient](#reflection-coefficient) · [Return loss](#return-loss)

<a id="vswr"></a>

### Voltage standing-wave ratio

For reflection magnitude r with 0 ≤ r &lt; 1, VSWR = (1+r)/(1−r). The matched case gives one; as r approaches one the ratio diverges. The ideal passive boundary is assigned infinite VSWR.

VSWR converts reflection magnitude into the ratio between standing-wave voltage maxima and minima in the ideal line model. Its value loses the reflection phase, so many different loads have the same VSWR. The ratio grows sharply as the reflection magnitude approaches the passive boundary.

A finite VSWR greater than one signals mismatch relative to the reference, but does not identify which impedance or matching operation is needed. The matched value one and the infinite boundary limit should be handled separately rather than substituted blindly into formulas involving division by 1−r.

**Also called:** VSWR, Standing-wave ratio, SWR.

**Quick example:** Reflection magnitude 1/3 gives VSWR 2.

[Further reading](demonstrations/SMITH_CHART.md) · [Reflection coefficient](#reflection-coefficient) · [Matched load](#matched-load) · [Return loss](#return-loss)

<a id="return-loss"></a>

### Return loss

For 0 &lt; |Γ| ≤ 1, the quantity −20 log₁₀|Γ| in decibels. Smaller reflected magnitude gives larger return loss. The matched limit |Γ| = 0 has ideal infinite return loss; the passive boundary |Γ| = 1 gives zero decibels.

Return loss expresses reflected amplitude on a logarithmic decibel scale under the stated convention. The minus sign makes a smaller reflection magnitude correspond to a larger positive return-loss value. It therefore moves in the opposite numerical direction from mismatch measures that increase with reflection.

Like VSWR, it omits reflection phase and does not identify the load uniquely. The infinite matched limit is an ideal mathematical value, not a finite measured number. Comparing return-loss values requires the same reference and a compatible measurement or model convention.

**Also called:** RL.

**Quick example:** For |Γ| = 1/√5, return loss is 10 log₁₀5, approximately 6.99 decibels.

[Further reading](demonstrations/SMITH_CHART.md) · [Reflection coefficient](#reflection-coefficient) · [Voltage standing-wave ratio](#vswr) · [Matched load](#matched-load)

<a id="lossless-line"></a>

### Lossless transmission line

In the guide’s propagation convention, a line of length ℓ gives Γin = ΓL exp(−4πiℓ/λ) at wavelength λ. It rotates the reflection point while preserving its magnitude. This is a physical line model with its own length and reference assumptions.

Propagation changes the phase accumulated by the reflected wave on a round trip. This explains the factor 4πℓ/λ in the guide’s reflection formula. A quarter-wavelength changes the reflection sign and, where finite, reciprocates normalized impedance.

Because the magnitude is unchanged, line propagation has an exact reachability limitation: it moves along a reflection circle rather than throughout the disk. This physical model is also distinct from choosing one of N algebraic cyclic rotations. Their phases can coincide at selected lengths without making their allowed action sets identical.

**Quick example:** A quarter wavelength multiplies Γ by −1 and sends a finite nonzero normalized load z to 1/z.

**Keep in mind:** Line rotation alone cannot turn a nonzero reflection magnitude into a matched load.

[Further reading](demonstrations/SMITH_CHART.md) · [Reflection coefficient](#reflection-coefficient) · [Cyclic reachability](#cyclic-reachability) · [Matched load](#matched-load)

<a id="cyclic-reachability"></a>

### Cyclic reachability

Reachability by a fixed finite set of phase rotations Γ ↦ ωᴷΓ, where ω = exp(2πi/N), N &gt; 0 and K is an integer. For Γ₀ ≠ 0, a target Γ\* is reachable exactly when (Γ\*/Γ₀)ᴺ = 1. The zero start reaches only zero.

The allowed orbit contains only the N equally spaced phase multiples of the starting point, with repetitions removed in degenerate cases. For a nonzero start, dividing by Γ₀ isolates the required phase factor. Raising it to N tests whether that factor is one of the allowed roots of unity.

Matching radius is therefore necessary but generally insufficient for fixed finite N. The zero start is a separate case because division by Γ₀ is unavailable and every rotation fixes zero. Increasing the allowed order changes the reachability problem rather than proving reachability under the original order.

**Quick example:** For N = 4, the orbit of Γ₀ = 1/2 is {1/2,i/2,−1/2,−i/2}. A point at angle π/4 with radius 1/2 is outside this orbit.

[Further reading](demonstrations/SMITH_CHART.md) · [Root of unity](#root-of-unity) · [Necessary condition](#necessary-condition) · [Lossless transmission line](#lossless-line) · [Feasibility](#feasibility)

<a id="pole"></a>

### Pole of a rational function

A point where a rational function has a nonremovable singularity after common factors are cancelled. A zero in a displayed denominator is only a candidate until cancellation is considered. Individual terms in a decomposition can have poles that cancel in their sum.

A pole is a genuine blow-up of the reduced rational function near a point, not merely a denominator zero in one unreduced formula. Cancelling common factors can reveal that an apparent singularity was removable.

Decomposed expressions need additional care: individual packet terms can have poles whose singular parts cancel when summed. Evaluating those terms separately at the singular point can therefore fail even when the total extends regularly. State whether a formula concerns each component, their sum or a limiting continuation.

**Quick example:** The function 1/(1−t) has a pole at t = 1. By contrast, (1−t)/(1−t) extends to the constant 1 after cancellation.

[Further reading](demonstrations/SMITH_CHART.md) · [Impedance Cayley transform](#cayley-transform) · [Rational function](#rational-function) · [Packet](#packet)

<a id="rational-function"></a>

### Rational function

A quotient of polynomials over a declared field, understood with common factors cancelled when studying its poles or degree. In circuit work the variable is often complex frequency s. Frequency samples alone do not determine an arbitrary rational function without further constraints.

A rational function is an exact global algebraic description, subject to its domain exclusions. Its values are determined by numerator and denominator polynomials up to common rescaling and cancellation. Degree and pole questions should use a reduced representation.

Finitely many samples generally permit many rational interpolants when degree and other restrictions are unspecified. Additional conditions such as passivity, analyticity, properness or bounded degree change the admissible class. Finding one fitting formula does not establish uniqueness or a realization within every circuit topology.

**Quick example:** The one-inductor example has normalized impedance z(s) = (7s+5)/(2s+4).

[Further reading](demonstrations/SMITH_FIRST_ORDER_RL.md) · [Pole of a rational function](#pole) · [Scalar McMillan degree](#mcmillan-degree) · [Interpolation](#interpolation)

<a id="positive-real-function"></a>

### Positive-real impedance function

In the real-rational scalar circuit setting, a rational function Z(s) analytic for Re s &gt; 0 and satisfying Re Z(s) ≥ 0 there. Real coefficients give the usual conjugation symmetry. Boundary poles and realization restrictions require their stated additional conditions.

Positive-realness encodes a half-plane positivity condition on an entire function, not only on selected boundary samples. In passive network theory it connects analytic impedance behavior with realizability under appropriate classical assumptions.

A restricted synthesis question can impose more requirements, such as positive element values, a particular topology or no transformers. Those restrictions should remain separate from the analytic positive-real test. A finite sample check can detect a violation at a sampled point but cannot generally certify the whole half-plane condition.

**Also called:** Positive-real function, PR function.

**Quick example:** For positive R and L, the series RL function Z(s) = R+sL has positive real part throughout Re s &gt; 0.

**Keep in mind:** Checking finitely many frequency samples is insufficient to establish positivity on the whole half-plane.

[Further reading](demonstrations/SMITH_FIRST_ORDER_RL.md) · [Rational function](#rational-function) · [Scalar Schur function](#schur-function) · [Circuit realization](#circuit-realization)

<a id="schur-function"></a>

### Scalar Schur function

A complex analytic function F on the open unit disk satisfying |F(t)| ≤ 1 throughout that disk. The Smith-chart research uses such reflection functions for interpolation. A rational Schur function has a finite rational description, with its degree and boundary behavior still to be specified.

A Schur function remains inside the closed unit disk in value while its argument ranges over the open disk. This global analytic constraint makes interpolation much more restrictive than passing a polynomial through finitely many prescribed points.

The Cayley-coordinate viewpoint relates such bounded reflection functions to half-plane positivity under the relevant transformations. Rationality and degree are extra properties. A Schur interpolation witness therefore need not supply a circuit with a requested component count or a specific transformer-free realization.

**Quick example:** F(t) = t is a Schur function. It realizes the sample values 1/2 at t = 1/2 and −1/2 at t = −1/2.

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Positive-real impedance function](#positive-real-function) · [Pick matrix](#pick-matrix) · [Impedance Cayley transform](#cayley-transform)

<a id="interpolation"></a>

### Interpolation

Finding a function in a declared class that takes prescribed values at prescribed nodes. Feasibility, uniqueness and the range of possible unmeasured values are separate questions. A fit in an unrestricted polynomial class need not satisfy the analytic or passive constraints of a circuit model.

Interpolation first asks whether the requested values can be attained within a specified function class. Once feasible, one can ask whether the interpolant is unique, what other values it can take or how small its degree can be.

These are separate questions because finite data may leave substantial freedom. The Schur class adds a global analytic bound, and a restricted circuit class adds still further structure. A fit in a larger class cannot automatically answer feasibility or uniqueness in the smaller one.

**Quick example:** The data F(1/2) = 1/2 and F(−1/2) = −1/2 admit F(t) = t in the Schur class.

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Scalar Schur function](#schur-function) · [Pick matrix](#pick-matrix) · [Identifiability relative to a model class](#identifiability)

<a id="pick-matrix"></a>

### Pick matrix

For distinct disk nodes tₖ and proposed scalar values vₖ, the Hermitian matrix Pₖₗ = (1−vₖ conjugate(vₗ))/(1−tₖ conjugate(tₗ)). Its positive semidefiniteness is the classical scalar Schur interpolation criterion used in the linked reading.

The matrix combines the proposed values with the geometry of their disk nodes. Its positive-semidefinite condition tests whether those finite observations can come from a scalar Schur function under the theorem’s hypotheses. It is more informative than checking only that each individual value lies in the disk.

Singularity is a meaningful boundary case, not merely a numerical inconvenience. Null vectors can force additional constraints on an unmeasured value. A tolerance-based eigenvalue decision needs care near that boundary, and the interpolation criterion still does not settle restricted physical component-count questions.

**Quick example:** The nodes 1/2 and −1/2 with equal respective values give P = \[\[1,1\],\[1,1\]\], a rank-one singular matrix.

**Keep in mind:** The nodes are distinct and strictly inside the disk. This criterion is not a component-count theorem for a restricted circuit topology.

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Interpolation](#interpolation) · [Scalar Schur function](#schur-function) · [Positive semidefinite matrix](#positive-semidefinite) · [Singular block range condition](#singular-range-condition)

<a id="singular-range-condition"></a>

### Singular block range condition

For Hermitian P ≥ 0, the block matrix \[\[P,b\],\[b\*,d\]\] is positive semidefinite exactly when b is perpendicular to ker P and d ≥ b\*P†b. Here P† is the Moore–Penrose inverse. The range condition remains essential when P is singular.

At a singular positive-semidefinite block, the new column must avoid directions in the old kernel. Otherwise the augmented quadratic form can become negative regardless of the lower-right scalar. This explains why the range condition is logically independent of the remaining pseudoinverse inequality.

After the range condition holds, completing the square reduces positivity to d−b\*P†b≥0. If P=0, the condition forces b=0 outright. When P itself depends on unknown data, its pseudoinverse cannot be treated as a fixed known matrix while varying those data.

**Quick example:** If P = 0, its range is {0}. Positivity of the augmented block forces b = 0 as well as d ≥ 0.

**Keep in mind:** Substituting a pseudoinverse into the scalar inequality while omitting the range condition is insufficient.

[Further reading](demonstrations/SMITH_SINGULAR_COMPLETION.md) · [Pick matrix](#pick-matrix) · [Moore–Penrose inverse](#pseudoinverse) · [Schur complement](#schur-complement) · [Kernel](#kernel)

<a id="mcmillan-degree"></a>

### Scalar McMillan degree

For a proper scalar rational transfer function p(s)/q(s) in lowest terms, the degree of q. It counts the minimal state dimension of an unrestricted finite linear realization. Improper functions and restricted passive circuit component counts need their own conventions.

In the stated proper scalar setting, cancelling common factors identifies the genuinely retained denominator dynamics. Its degree corresponds to the smallest state dimension among unrestricted finite linear realizations of that transfer function.

This is an input-output complexity measure, not a universal count of circuit elements. A passive network with restricted components or forbidden transformers can need a different analysis. An approximation with smaller McMillan degree also realizes a different function unless an exact equality with the target is established.

**Quick example:** The proper function (7s+5)/(2s+4) has no common numerator-denominator factor and has McMillan degree one.

**Keep in mind:** A minimal state dimension does not alone give the minimum number of reactive elements in a transformer-free network.

[Further reading](demonstrations/SMITH_FIRST_ORDER_RL.md) · [Rational function](#rational-function) · [Circuit realization](#circuit-realization) · [Finite linear state-space realization](#state-space-realization)

<a id="circuit-realization"></a>

### Circuit realization

A network built from the allowed components whose driving-point impedance or transfer function equals the specified function on its stated domain. The component alphabet, positivity rules and permitted transformers determine the realization problem.

A circuit realization must reproduce the specified impedance or transfer behavior using the permitted component laws. Topology, element values and admissibility restrictions all belong to the construction. Two algebraically equivalent rational expressions need not display the same circuit directly.

Existence of an unrestricted state-space model or a Schur interpolant is therefore only part of a restricted synthesis argument. Exact realization, approximation quality and minimum component count are distinct claims. The one-inductor supplement explicitly realizes its degree-one approximation without settling the harder exact higher-degree target question.

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

Conjugation reverses the imaginary part while leaving the real part unchanged. Multiplying a complex number by its conjugate produces its nonnegative squared modulus, which explains why conjugation appears in complex lengths and quantum probabilities.

Conjugating a product conjugates each factor without reversing their scalar order. For matrices, the adjoint additionally transposes the entries and reverses the order of a matrix product. Operator conjugation CTC⁻¹ is a different construction despite sharing the word conjugation.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Inner product](#inner-product) · [Scalar](#scalar)

<a id="adjoint"></a>

### Adjoint matrix

For a complex matrix in orthonormal bases, the adjoint A\* is its conjugate transpose. In real orthonormal bases this is the ordinary transpose.

The adjoint is characterized by moving an operator across an inner-product pairing. In orthonormal complex coordinates this produces conjugate transpose, so both the entry positions and their imaginary signs change. For products, (AB)\*=B\*A\*, with reversed order.

The coordinate formula depends on the inner products. With nonidentity metric matrices, raw conjugate transpose no longer represents the same adjoint operation without metric factors. This matters when comparing unitary or self-adjoint operators across nonorthonormal coordinate systems.

**Also called:** Conjugate transpose, Hermitian transpose.

**Quick example:** The adjoint of \[\[1,i\],\[0,2\]\] is \[\[1,0\],\[−i,2\]\]. Both transposition and conjugation are required.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Complex conjugate](#complex-conjugate) · [Inner product](#inner-product) · [Metric adjoint](#metric-adjoint)

<a id="unitary"></a>

### Unitary matrix

A complex square matrix U with U\*U = UU\* = I. It preserves the complex inner product and therefore vector norms.

A unitary map is a reversible complex linear change preserving the inner product. Its adjoint supplies its inverse, so it preserves normalization and all pairwise geometric relations between state vectors.

In density-matrix form it acts by ρ↦UρU\*, preserving eigenvalues and purity. This differs from a general quantum channel, which can discard information or turn a pure state into a mixed one. Unitarity also does not mean that probabilities in a fixed measurement basis remain unchanged; the state’s coordinates can rotate.

**Quick example:** diag(1,i) is unitary because its adjoint diag(1,−i) is its inverse.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Norm](#norm) · [Orthogonal matrix](#orthogonal-matrix)

<a id="amplitude"></a>

### Quantum amplitude

A complex coordinate of a normalized state vector in a chosen orthonormal basis. Its squared modulus gives that basis outcome’s probability. Relative phases can affect measurements in other bases.

An amplitude has both magnitude and phase. Squaring its modulus gives a probability only after a normalized state and an orthonormal measurement basis have been specified. Individual amplitudes can interfere when the measurement basis changes.

Consequently, keeping only their squared magnitudes loses information about relative phase. The demonstration’s states with phases 1 and −1 have identical coordinate probabilities but different X-measurement probabilities. This distinguishes a state vector’s full information from the probability list of one particular measurement.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Complex conjugate](#complex-conjugate) · [Born probability](#born-probability) · [Coordinates](#coordinates) · [Qubit](#qubit) · [Relative phase](#relative-phase)

<a id="density-matrix"></a>

### Density matrix

A positive semidefinite Hermitian matrix with trace one. A normalized vector ψ gives the pure-state matrix ρ = ψψ\*. Different vectors that differ only by an overall complex phase give the same density matrix.

A density matrix describes a state in a way that supports both pure states and mixtures. Its trace-one condition normalizes total probability, while positive semidefiniteness ensures that every valid measurement effect has a nonnegative probability.

For a pure state, the outer product removes the unobservable common phase while retaining relative phases in off-diagonal entries. A mixed density matrix can have several different ensemble decompositions, so it does not identify a unique hidden list of prepared pure states. Measurements determine the matrix’s observable consequences.

**Also called:** Density operator.

**In the worked example:** The normalized vector ψ = (3/5,4i/5)ᵀ gives ρ = ψψ\*. Its diagonal entries are 9/25 and 16/25, its upper-right entry is −12i/25, and its lower-left entry is 12i/25. Its trace is one.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Matrix trace](#trace) · [Purity of a density matrix](#purity)

<a id="trace"></a>

### Matrix trace

The sum of diagonal entries of a square matrix. It is unchanged by an invertible change of basis. Field trace is a related arithmetic construction with its own definition.

Trace adds the diagonal contributions of an endomorphism and is independent of the basis used to represent that endomorphism. Compatible finite matrix products satisfy tr(AB)=tr(BA), which often simplifies probability and channel-normalization calculations.

It is a scalar summary and does not determine the matrix. Many different density matrices share trace one. Positivity must therefore be checked separately; a Hermitian trace-one matrix with a negative eigenvalue is not a valid quantum state.

**Quick example:** The trace of \[\[1,2\],\[3,4\]\] is 1+4 = 5.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Matrix](#matrix) · [Field trace](#field-trace)

<a id="born-probability"></a>

### Born probability

For a density matrix ρ and an orthogonal measurement projector P, the outcome probability is tr(Pρ). A complete orthogonal projector family gives probabilities summing to one.

The Born rule pairs a state with a specified measurement outcome. For projective measurements, the trace formula agrees with the squared norm of the projected pure-state vector. Completeness of the measurement projectors makes the total probability one.

Changing the measurement changes the question being asked of the same state. Coordinate probabilities may ignore coherences that another basis can detect. General measurements use positive effects summing to I, while the projective form in this entry is the important special case used in the introductory example.

**In the worked example:** For ψ = (3/5,4i/5)ᵀ and ρ = ψψ\*, the coordinate projectors P₀ = diag(1,0) and P₁ = diag(0,1) give tr(P₀ρ) = 9/25 and tr(P₁ρ) = 16/25. These probabilities sum to one.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Matrix trace](#trace) · [Orthogonal projector](#orthogonal-projector)

<a id="purity"></a>

### Purity of a density matrix

The number tr(ρ²). For a finite density matrix it equals one exactly for a pure state and is smaller for a mixed state.

Purity depends on the eigenvalues of the density matrix: it is their squared sum. A pure state concentrates the whole trace in one eigenvalue equal to one. For a d-dimensional state, the completely mixed matrix I/d has purity 1/d.

Unitary coordinate changes preserve purity, whereas dephasing can reduce it by removing off-diagonal coherence. Purity is still only one scalar and does not determine the state or its measurement probabilities. Compare it together with the density matrix and the operation that produced it.

**In the worked example:** For ρ = ψψ\* with ψ = (3/5,4i/5)ᵀ, tr(ρ²) = 1. After coordinate dephasing, the purity is (9/25)² + (16/25)² = 337/625, which is less than one.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Matrix trace](#trace) · [Pure quantum state](#pure-state) · [Mixed quantum state](#mixed-state)

<a id="dephasing"></a>

### Dephasing

For a specified complete orthogonal family Pᵢ, the channel ρ ↦ sum PᵢρPᵢ removes coherence between different selected subspaces. Its effect depends on the chosen decomposition.

Dephasing keeps the diagonal packet blocks PᵢρPᵢ and deletes the cross-blocks PᵢρPⱼ for different indices. It models a projective measurement whose outcome has been discarded. Applying the same complete dephasing again makes no further change.

The retained information depends on the chosen decomposition. Coherences inside a multidimensional retained block can remain, while coherences between blocks vanish. Diagonal observations can stay exactly recoverable even when other measurement probabilities cannot be recovered from the dephased output alone.

**In the worked example:** The coordinate measurement with its outcome forgotten sends the example’s ρ to P₀ρP₀ + P₁ρP₁ = diag(9/25,16/25). The off-diagonal terms disappear while the two coordinate probabilities remain unchanged.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Projector](#projector) · [Kraus operators](#kraus-operator) · [Quantum channel](#quantum-channel) · [Selective projective measurement](#selective-measurement)

<a id="kraus-operator"></a>

### Kraus operators

Matrices Kᵢ describing a finite quantum channel by Φ(ρ) = sum KᵢρKᵢ\*. The condition sum Kᵢ\*Kᵢ = I makes this map trace preserving.

Each Kraus term contributes one possible branch to a channel’s unconditioned output. Summing the terms gives a completely positive map, and the completeness equation makes the trace of every input state remain one.

The Kraus representation is generally not unique, so its individual matrices are not automatically unique physical events. If a branch is interpreted as a measured outcome, its probability and conditional normalization must be specified. A complete channel and one selected branch therefore have different trace and information interpretations.

**Also called:** Kraus representation.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Density matrix](#density-matrix) · [Matrix trace](#trace)

<a id="hermitian"></a>

### Hermitian matrix

A complex square matrix A with A\* = A. Its diagonal entries are real and opposite off-diagonal entries are complex conjugates. This condition alone does not imply positivity.

Hermitian matrices are the complex analogue of real symmetric matrices. In finite dimensions they have real eigenvalues and an orthonormal eigenbasis, making their quadratic forms real-valued and supporting their use as observables.

Real eigenvalues can still be negative. Positivity is an additional condition checked by the signs of the quadratic form or eigenvalues. Thus an observable can be Hermitian without being a density matrix, and a trace-one Hermitian matrix need not represent a state.

**Also called:** Self-adjoint matrix.

**Quick example:** The matrix \[\[1,i\],\[−i,2\]\] is Hermitian because conjugating and transposing returns it.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Positive semidefinite matrix](#positive-semidefinite)

<a id="positive-semidefinite"></a>

### Positive semidefinite matrix

A Hermitian matrix A for which v\*Av is nonnegative for every vector v. Zero eigenvalues are allowed.

Positive semidefiniteness rules out negative quadratic energy in every direction while allowing invisible zero directions. For finite Hermitian matrices it is equivalent to all eigenvalues being nonnegative. One exact negative quadratic-form value is enough to disprove it.

This condition appears in density matrices, covariance matrices, Gram operators and Pick feasibility matrices, but their other constraints differ. Singular cases also need care in block elimination: replacing an inverse by a pseudoinverse without a range condition can miss an actual positivity obstruction.

**Also called:** PSD, PSD matrix.

**Quick example:** \[\[1,1\],\[1,1\]\] is positive semidefinite because its quadratic form is |x+y|², and it has a nonzero kernel.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Hermitian matrix](#hermitian) · [Eigenvalue](#eigenvalue) · [Density matrix](#density-matrix) · [Positive definite matrix](#positive-definite) · [Gram operator](#gram-operator) · [Pick matrix](#pick-matrix) · [Quadratic form](#quadratic-form)

<a id="coherence"></a>

### Coherence in a chosen basis

Off-diagonal density-matrix entries that encode relations between different basis components. They can contribute to probabilities after a change of measurement basis.

Coherence records relationships between components, not additional classical populations. Off-diagonal entries contribute cross terms when a measurement mixes the chosen basis vectors. Their complex phases can therefore affect interference while leaving coordinate probabilities fixed.

The description is basis-dependent. A matrix diagonal in one basis can have off-diagonal entries in another. Dephasing specifies which basis or subspace family defines the discarded coherence, so saying that coherence was removed without naming that decomposition leaves the operation ambiguous.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Dephasing](#dephasing) · [Quantum amplitude](#amplitude)

<a id="qubit"></a>

### Qubit

A quantum system with a two-dimensional complex state space. A pure state has a unit-vector representative α|0⟩+β|1⟩ with |α|²+|β|² = 1; multiplying both amplitudes by one global phase leaves the same density matrix. Mixed states use density matrices.

A qubit is a two-dimensional state system, not merely a stored bit with an unknown value. Its pure-state amplitudes can have a relative phase that influences measurements beyond the coordinate basis. Density matrices also allow statistical mixtures of preparations.

The two coordinate probabilities alone do not specify a general qubit state. Measurements in additional settings can detect its off-diagonal entries, which is why tomography uses several settings. A single observed outcome likewise does not reveal the full amplitude or probability list.

**Quick example:** The vector (3/5,4/5) is normalized because 9/25+16/25 = 1.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Quantum amplitude](#amplitude) · [Density matrix](#density-matrix) · [Global phase](#global-phase)

<a id="global-phase"></a>

### Global phase

A common unit-modulus factor multiplying every amplitude of a state vector. It cancels in |ψ⟩⟨ψ| and leaves the represented pure-state density matrix unchanged. This statement assumes the factor applies to the whole state being compared.

Multiplying a whole state vector by eⁱθ changes its representative but leaves ψψ\* unchanged, because the factor and its conjugate cancel. All measurement probabilities derived from that density matrix therefore stay the same.

The word whole is essential. Applying a phase only to one component or one coherent branch changes a relative phase and can alter interference. A factor that is global for an isolated subexpression may become relative when that expression is compared coherently with another branch of a larger state.

**Quick example:** The vectors (3/5,4/5) and (3i/5,4i/5) give the same density matrix.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Relative phase](#relative-phase) · [Density matrix](#density-matrix) · [Quantum amplitude](#amplitude)

<a id="relative-phase"></a>

### Relative phase

The phase difference between nonzero amplitudes in a chosen basis. It appears in off-diagonal density-matrix entries and can change interference probabilities even when the basis populations stay fixed.

Relative phase compares components rather than multiplying the entire state by one common factor. It enters the products of amplitudes appearing off the density matrix’s diagonal. A measurement combining those components can turn that phase information into different outcome probabilities.

The selected basis and nonzero amplitudes matter to the comparison. In the demonstration, changing the phase of the second amplitude leaves Z probabilities fixed but changes X or Y probabilities. Retaining only Z populations therefore cannot recover every phase-sensitive observation.

**Quick example:** The states (3/5,4/5) and (3/5,−4/5) have the same Z probabilities but X-plus probabilities 49/50 and 1/50.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Global phase](#global-phase) · [Coherence in a chosen basis](#coherence) · [Born probability](#born-probability)

<a id="pure-state"></a>

### Pure quantum state

A density matrix of the form ρ = |ψ⟩⟨ψ| for a unit vector ψ. In finite dimensions it has rank one, satisfies ρ² = ρ and has purity tr(ρ²) = 1. The vector representative is determined only up to global phase.

A pure-state density matrix is the orthogonal projector onto one normalized state direction. The unit-vector representative carries no additional information through its overall phase, which is why different phase representatives give the same projector.

Purity can be recognized from ρ²=ρ or tr(ρ²)=1 in the finite trace-one positive setting. A deterministic unitary evolution preserves this property. A channel that discards information about branches can instead produce a mixed output, even when its input was pure.

**Also called:** Pure state.

**Quick example:** For ψ = (3/5,4/5), ρ = \[\[9,12\],\[12,16\]\]/25 is pure.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Density matrix](#density-matrix) · [Purity of a density matrix](#purity) · [Projector](#projector) · [Mixed quantum state](#mixed-state)

<a id="mixed-state"></a>

### Mixed quantum state

A density matrix that is not pure. In finite dimensions its purity is less than one, and it can be written as a convex mixture of pure-state density matrices. Such a decomposition is generally not unique.

A mixed state is represented by a convex combination of pure-state density matrices, with nonnegative weights summing to one. It can arise from uncertain preparation or from forgetting part of a larger system or measurement record.

Different preparation ensembles can yield the same density matrix and therefore the same state-level measurement probabilities. The mixture should not be confused with adding state amplitudes coherently: probabilities average across an ensemble, whereas amplitude addition can introduce interference cross terms.

**Also called:** Mixed state.

**Quick example:** The dephased state diag(9/25,16/25) has purity 337/625, so it is mixed.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Pure quantum state](#pure-state) · [Density matrix](#density-matrix) · [Dephasing](#dephasing) · [Purity of a density matrix](#purity)

<a id="quantum-effect"></a>

### Quantum measurement effect

A Hermitian operator E satisfying 0 ≤ E ≤ I. For density matrix ρ, tr(Eρ) is the probability of its associated outcome. Effects in a complete measurement sum to I. They need not individually be projectors.

An effect describes the probability question associated with one outcome. The inequalities 0≤E≤I ensure that its probability lies between zero and one for every state. A complete measurement consists of effects whose sum is I.

A projector is a special effect with the additional idempotence property. General effects can describe less sharp measurements and need not identify a post-measurement state by themselves. The probability rule and the state-update rule are separate pieces of a measurement model.

**Also called:** Measurement effect.

**Quick example:** E = I/2 gives probability 1/2 for every state, although E² = I/4 differs from E.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Born probability](#born-probability) · [Positive semidefinite matrix](#positive-semidefinite) · [Projector](#projector)

<a id="observable"></a>

### Quantum observable

In the finite setting, a Hermitian operator whose real eigenvalues label possible outcomes of its projective measurement. Its expectation in state ρ is tr(Aρ). The operator and its measurement effects have related but different roles.

An observable packages numerical outcome labels together with their spectral projectors. The Born probabilities determine how likely those outcomes are, and their weighted average equals tr(Aρ). Its expectation is therefore a summary of a measurement distribution, not necessarily an individual outcome.

Different observables ask different questions about the same state. The Pauli X, Y and Z settings in the example reveal different combinations of its entries. Noncommuting observables need not share a measurement basis, so their probability descriptions cannot be identified simply by reusing coordinate populations.

**Quick example:** The Pauli matrix Z = diag(1,−1) has mean 9/25−16/25 = −7/25 in the demonstration state.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Hermitian matrix](#hermitian) · [Quantum measurement effect](#quantum-effect) · [Eigenvalue](#eigenvalue) · [Matrix trace](#trace)

<a id="quantum-channel"></a>

### Quantum channel

A linear completely positive, trace-preserving map on density matrices. A finite Kraus representation is Φ(ρ) = ΣⱼKⱼρKⱼ\* with ΣⱼKⱼ\*Kⱼ = I. Complete positivity requires positivity to survive extension by an arbitrary auxiliary quantum system.

A channel describes an unconditioned physical state transformation in the finite model. Complete positivity ensures that the operation remains valid when applied to one part of a larger quantum system, while trace preservation retains total probability.

Unitary evolution is one channel, but dephasing and damping can lose information. A channel need not have a physically valid inverse even when one can write a formal linear inverse on some subset of matrices. Selected measurement branches also require conditioning and are not individually trace-preserving channels in general.

**Also called:** CPTP map, Completely positive trace-preserving map.

**Quick example:** Coordinate dephasing uses K₀ = diag(1,0) and K₁ = diag(0,1), keeping the diagonal entries and deleting the off-diagonal entries.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Kraus operators](#kraus-operator) · [Dephasing](#dephasing) · [Matrix trace](#trace) · [Density matrix](#density-matrix)

<a id="quantum-tomography"></a>

### Quantum state tomography

Reconstructing a state from probabilities for a sufficiently informative collection of measurement settings. For a qubit, exact X, Y and Z outcome probabilities determine its density matrix. Experimental estimates introduce sampling error and must still describe a positive state.

Tomography treats measurement probabilities as a representation of the unknown state. Informationally sufficient settings permit reconstruction of all its independent matrix parameters. For a qubit, X, Y and Z settings provide the three real parameters left after Hermitian symmetry and trace normalization.

The demonstration uses exact ensemble probabilities, so inversion is an exact algebraic calculation. Experimental frequencies are estimates and can yield an unconstrained reconstructed matrix that is not positive. Statistical uncertainty and state-validity constraints must therefore be handled in an actual estimation procedure.

**Also called:** State tomography.

**Quick example:** For the phase-one demonstration state, X-plus = 49/50, Y-plus = 1/2 and Z-plus = 9/25 recover the upper-right entry 12/25.

**Keep in mind:** One outcome from a single copy does not supply the three ensemble probabilities.

[Further reading](demonstrations/QUANTUM_PHASE_MEASUREMENT.md) · [Density matrix](#density-matrix) · [Quantum observable](#observable) · [Born probability](#born-probability) · [Identifiability relative to a model class](#identifiability)

<a id="selective-measurement"></a>

### Selective projective measurement

A projective measurement with its outcome retained. Outcome j has probability pⱼ = tr(Pⱼρ); if pⱼ &gt; 0, the conditional output state is PⱼρPⱼ/pⱼ. Discarding the outcome instead gives the sum ΣⱼPⱼρPⱼ.

Retaining an outcome tells us which branch occurred. Dividing PⱼρPⱼ by its nonzero probability renormalizes that branch into a trace-one conditional state. This conditional state can differ from the unconditioned state obtained by averaging over all outcomes.

If the outcome is discarded, the branch probabilities are already included in the unnormalized terms, so those terms are summed directly. Confusing the normalized selected branches with their weighted unconditioned sum gives an incorrect channel or incorrect probabilities. Zero-probability branches cannot be normalized by this formula.

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

Powers of one prime provide nested modular resolutions. Moving from pⁿ to pⁿ⁺¹ retains the old residue information while allowing one additional base-p digit. The primality assumption gives the arithmetic structure used in p-adic lifting arguments.

Level zero corresponds to p⁰=1, whose residue information is trivial. A solution modulo one prime power need not extend to every higher power. The lifting equations and compatibility maps determine which next digits are allowed.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Integer congruence](#congruence) · [Prime field](#prime-field)

<a id="modular-reduction"></a>

### Modular reduction

Passing from a residue class modulo pⁿ⁺¹ to its class modulo pⁿ. This map forgets the highest retained base-p digit.

Reduction preserves the lower-level residue while forgetting finer digits. Several residues modulo pⁿ⁺¹ therefore share one image modulo pⁿ. The map respects addition and multiplication, making equations at successive levels comparable.

Reduction is straightforward, but reversing it is a constrained lifting problem. A coarse solution can have several fine solutions above it or none satisfying the required equation. Choosing an arbitrary finer representative does not establish that it remains a solution.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Prime power](#prime-power) · [Residue class](#residue-class) · [Coarsening](#coarsening)

<a id="lift-branch"></a>

### Lift branch

A sequence of solutions at successive levels whose reductions agree. A node at one finite level can have several children or no child.

A branch records consecutive choices of finer solutions above a common coarse starting point. Each new node must satisfy both its own equation and the reduction condition linking it to the previous node. This distinguishes a coherent path from unrelated solutions found at separate moduli.

Branching describes genuine ambiguity among possible next digits, while a dead end records a local obstruction to continuation. Reaching a fixed finite depth provides finite evidence. An infinite compatible solution requires an additional existence argument or an explicit compatible construction at all levels.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Lift](#lift) · [Modular reduction](#modular-reduction) · [Compatible tower](#compatible-tower)

<a id="compatible-tower"></a>

### Compatible tower

A collection of objects with specified maps between levels and stated compatibility identities. For modular solutions, the next residue must reduce to the preceding one.

A tower includes the maps between its levels, so its meaning is more than a list of objects of increasing size. Compatibility ensures that moving between levels in the prescribed ways gives consistent results. Modular reduction is a concrete example of these connecting maps.

To pass to a limiting object, the tower must satisfy whatever hypotheses justify that passage in the chosen setting. Finite prefixes can demonstrate the intended structure and detect failures, but do not automatically supply a complete infinite branch, convergence or uniqueness theorem.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Compatibility](#compatibility) · [Modular reduction](#modular-reduction) · [Completion](#completion)

<a id="padic-integer"></a>

### p-adic integer

For a prime p, an element of the inverse limit of the residue rings modulo pⁿ. It specifies a compatible residue at every positive level. A finite list of residues is only a truncation of that data.

A p-adic integer gives one consistent residue at every modulus pⁿ. These residues can be viewed as successive finite prefixes of an infinite base-p expansion. Agreement at more low-order digits means greater p-adic closeness, rather than closeness in the ordinary real absolute value.

A computer stores only a finite prefix or another finite description, so its output usually represents a congruence class or enclosure at a chosen precision. Extending that data to a specific infinite object requires more information. P-adic integers also include values that are not ordinary nonnegative integers.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Compatible tower](#compatible-tower) · [Prime power](#prime-power) · [Truncation](#truncation) · [p-adic valuation](#p-adic-valuation) · [p-adic unit](#p-adic-unit)

<a id="surviving-branch"></a>

### Survival to a finite level

A branch reaches the chosen last level without losing compatibility or the required equations. Survival to that level alone says nothing about the next one.

Survival means that the branch has met every tested requirement through the declared final level. The depth and equations checked belong with the reported result, because extending the modulus can introduce new constraints.

An absence of dead ends in a finite search does not by itself prove indefinite continuation. Conversely, the failure of one branch need not eliminate its siblings. A useful record preserves the actual parent-child links and stopping depth so that later work can distinguish a local branch failure from a global impossibility claim.

**In the worked example:** The residue 9 solves x² ≡ 1 modulo 16. Its only candidate lifts modulo 32 are 9 and 25, and both squares equal 17 modulo 32. This branch reaches level four but has no child at level five.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#lift-branches) · [Lift branch](#lift-branch) · [Finite check](#finite-check)

<a id="prime-field"></a>

### Prime field

The smallest subfield of a field. In characteristic p it consists of the p scalar classes and is isomorphic to Fₚ. In characteristic zero it is isomorphic to the rational numbers.

Every field contains a canonical copy of the arithmetic generated by its multiplicative identity and the required inverses. Positive characteristic gives the finite prime field Fₚ; characteristic zero gives a copy of Q. Other field elements can then be regarded as extending this starting scalar system.

The prime field should not be confused with every finite field of the same characteristic. F₂₅ contains F₅ but has additional elements and extension degree two over it. That distinction affects Frobenius, trace and norm formulas.

**Quick example:** The field F₅ has five elements. Its nonzero element 2 has inverse 3.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Field](#field) · [Integer congruence](#congruence)

<a id="extension-field"></a>

### Extension field

A field containing a specified smaller field. The extension degree is its vector-space dimension over that smaller field.

An extension treats elements of a larger field as vectors over the smaller field. Its degree counts how many smaller-field coordinates are needed when that dimension is finite. A basis lets multiplication by a larger-field element be represented as a matrix over the smaller field.

This viewpoint defines the field trace and norm through ordinary matrix trace and determinant. The smaller field must be stated: the same larger field can have different dimensions over different subfields. Extending scalars can also make a polynomial split or introduce roots unavailable in the original field.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Field](#field) · [Dimension](#dimension) · [Prime field](#prime-field)

<a id="frobenius"></a>

### Finite-field Frobenius

In a finite field of characteristic p, the map x ↦ xᵖ is an automorphism. Over F\_q, the relative Frobenius is x ↦ x^q. The example uses q = p = 5.

In characteristic p, the binomial coefficients between the endpoints vanish modulo p, giving (a+b)ᵖ=aᵖ+bᵖ. This makes the power map compatible with field addition as well as multiplication. Finiteness ensures that the injective field map is also surjective.

Relative Frobenius fixes the chosen base field F\_q and organizes the conjugates in a finite extension. Its iterates enter trace and norm formulas. The exponent q and the extension degree therefore belong to the construction; the map is not ordinary numerical exponentiation used as an approximation.

**Also called:** Frobenius automorphism.

**Quick example:** In characteristic p, (a+b)ᵖ = aᵖ+bᵖ. On Fₚ itself the Frobenius fixes every element.

**In the worked example:** In F₂₅ = F₅\[α\] with α² = 3, one has α⁵ = −α. Thus Frobenius sends 1+α to 1−α, and applying it twice returns 1+α.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Extension field](#extension-field) · [Linear isomorphism](#isomorphism)

<a id="field-trace"></a>

### Field trace

For a finite field extension L/K, the trace of the K-linear map that multiplies L by an element a. In F₂₅/F₅ it is a+a⁵.

Multiplication by a fixed extension-field element is a linear operation over the base field. Taking that operation’s matrix trace produces a scalar in the base field, independently of the basis used to represent multiplication.

For finite fields, the same trace is a sum of Frobenius conjugates. It is additive and base-field linear, unlike the multiplicative field norm. Although it is computed using a matrix trace, its input is an extension-field element rather than an arbitrary matrix or a vector length.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Matrix trace](#trace) · [Extension field](#extension-field) · [Finite-field Frobenius](#frobenius)

<a id="field-norm"></a>

### Field norm

For a finite field extension L/K, the determinant of multiplication by an element a as a K-linear map. In F₂₅/F₅ it is a·a⁵. This norm is algebraic and is not a vector length.

The determinant of multiplication measures an algebraic multiplicative effect of one extension-field element on the whole extension space. Changing its basis does not change that determinant. In a finite-field extension it equals the product of the relevant Frobenius conjugates.

This norm is multiplicative, but it is not a nonnegative length satisfying a triangle inequality. Its values lie in the base field and can have finite-field arithmetic. Confusing it with a vector-space norm would give incorrect geometric or error interpretations.

**In the worked example:** For β = 1+α in F₂₅ = F₅\[α\] with α² = 3, the norm to F₅ is ββ⁵ = (1+α)(1−α) = 1−3 = 3 in F₅.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Determinant](#determinant) · [Extension field](#extension-field) · [Norm](#norm)

<a id="irreducible-polynomial"></a>

### Irreducible polynomial

A nonconstant polynomial over a field that cannot be factored into two polynomials of positive degree over that field. For degree two, irreducibility is equivalent to having no root in the field.

Irreducibility depends on the coefficient field. A polynomial can resist factorization over one field and split over a larger extension. Over a field, quotienting the polynomial ring by an irreducible polynomial produces a field, which is a standard way to construct finite extensions.

The no-root test is sufficient for irreducibility only in degrees two and three. In higher degrees a polynomial can factor into nonconstant pieces without having a linear factor. Low-degree checks should therefore not be used as unrestricted irreducibility criteria.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#finite-frobenius) · [Field](#field) · [Extension field](#extension-field)

<a id="ring"></a>

### Commutative ring with identity

A system with addition, subtraction and commutative multiplication satisfying the ring laws and having a multiplicative identity. A nonzero element need not have a multiplicative inverse.

A ring retains addition and multiplication while allowing more varied division behavior than a field. It may contain nonzero nonunits or zero divisors. The glossary’s convention is commutative and includes an identity, so those assumptions should be checked when another work uses the same word differently.

Linear algebra over rings becomes module theory: generators need not form a basis, and familiar rank arguments can require extra hypotheses. An equation solved by dividing by a nonzero element over a field may fail over a ring unless that element is actually invertible.

**Quick example:** The integers form a commutative ring with identity, but 2 has no multiplicative inverse within the integers.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Field](#field) · [Module](#module)

<a id="module"></a>

### Module

An abelian additive group with a scalar action by a ring satisfying the usual distributive, associative, and identity laws. For a module over Q\[t\], multiplication by t can be specified by a Q-linear operator.

A module generalizes a vector space by permitting scalars from a ring. The distributive rules still allow linear combinations, but the absence of division can produce torsion and prevent a module from having a basis.

For a Q\[t\]-module, the variable t acts as a chosen Q-linear operator. Polynomial relations in t then express operator relations on vectors. This connects generator questions and minimal-polynomial behavior to algebraic presentations, while keeping the scalar ring part of the model.

**Quick example:** An abelian group is a module over Z, where multiplying by an integer means repeated addition and its inverse.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Commutative ring with identity](#ring) · [Operator algebra](#operator-algebra)

<a id="module-presentation"></a>

### Module presentation

A description of a module by generators and relations. A finite matrix A: Rᵐ → Rⁿ presents the quotient Rⁿ/im A.

Generators describe possible formal coordinates, while relations identify combinations that represent zero. A presentation matrix maps relation coordinates into generator coordinates, and taking its cokernel imposes those relations on the free generator module.

Different presentation matrices can describe isomorphic modules, so presentation-dependent entries should be distinguished from module invariants. The matrix’s sizes, coefficient ring and direction are essential. Over a general ring, treating it as an ordinary real matrix can discard the arithmetic structure the presentation was meant to retain.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Module](#module) · [Cokernel](#cokernel) · [Image](#image)

<a id="cokernel"></a>

### Cokernel

For a linear map or module map A: U → V, the quotient V/im A. It records target classes modulo those already reached by A.

The cokernel records what remains of the target after identifying outputs that differ by something already reachable. A target has zero cokernel class exactly when it lies in the original image. This makes the cokernel a natural place to describe missing directions in a repair problem.

It differs from the kernel, which describes erased input directions. In finite vector spaces, its dimension is codomain dimension minus rank. Over modules, its structure can contain torsion and multiplicity information that a dimension count alone would miss.

**Quick example:** The cokernel of multiplication by 2 on Z is Z/2Z, which records the two parity classes.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Quotient space](#quotient-space) · [Image](#image) · [Module](#module)

<a id="annihilator"></a>

### Module annihilator

The ideal of ring elements that act as zero on every element of a module. For Q\[t\]/(tᵏ), the annihilator is the ideal (tᵏ).

The annihilator records scalar operations that kill the entire module. For a Q\[t\]-module, it therefore describes polynomial operator relations holding on every vector, not merely on one selected input.

For Q\[t\]/(tᵏ), multiplication by tᵏ vanishes while lower powers can remain nonzero. The annihilator retains that exponent, unlike the underlying one-point support set. One can also define annihilators of individual elements; that is a related construction with a potentially larger set of killing scalars.

**Quick example:** In the Z-module Z/6Z, every multiple of 6 acts as zero, so its annihilator is the ideal (6).

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Module](#module) · [Nilpotent operator](#nilpotent) · [Commutative ring with identity](#ring)

<a id="module-support"></a>

### Module support

The prime ideals at which a module’s localization is nonzero. In the example Q\[t\]/(tᵏ), the support is the single prime ideal (t). The underlying support set does not determine k or the module.

Support asks where the module remains present after localizing at prime ideals. It is a set of locations in the algebraic sense, not a list of the module’s generators or a numerical support interval.

Modules can share this set while differing substantially in their internal structure. The family Q\[t\]/(tᵏ) always lives at the same prime (t), yet its length and rational dimension grow with k. Support therefore identifies where information remains, while invariants such as multiplicity describe how much structure remains there.

**In the worked example:** Over R = Q\[t\], the modules R/(t) and R/(t²) both have support {(t)}. Their rational dimensions are one and two, so equal support does not identify the modules.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Module](#module) · [Module annihilator](#annihilator) · [Multiplicity in the module example](#multiplicity)

<a id="fitting-ideal"></a>

### Zeroth Fitting ideal

For a finite presentation Rᵐ → Rⁿ → M → 0 over a commutative ring, the ideal generated by the n by n minors of the presentation matrix. In the one-generator example with relation tᵏ, it is (tᵏ).

The zeroth Fitting ideal extracts a presentation-independent ideal from maximal minors of a finite presentation matrix. In the one-generator case it simply retains the relation element, making the tutorial’s ideal (tᵏ) directly visible.

Its ideal structure can distinguish modules whose support sets agree. Passing to only the set of primes containing that ideal can discard exponents and other information. The zeroth convention and finite-presentation assumptions matter, especially when there are too few columns to form the displayed minors.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Module presentation](#module-presentation) · [Determinant](#determinant) · [Module support](#module-support)

<a id="multiplicity"></a>

### Multiplicity in the module example

For Q\[t\]/(tᵏ) supported at t=0, the integer k records the module’s length and its Q-vector-space dimension. This is additional data beyond the one-point support set. Other works use multiplicity with their own specified objects.

Multiplicity measures additional structure at an already identified location. In the tutorial, 1,t,…,tᵏ⁻¹ remain as independent rational classes in Q\[t\]/(tᵏ), so k counts the module’s rational dimension and its length at that support point.

Knowing that the support is {(t)} does not reveal this count. The example separates location from retained algebraic thickness. Other uses of multiplicity, such as root or eigenvalue multiplicity, require their own definitions rather than inheriting the module example’s interpretation automatically.

**In the worked example:** The module Q\[t\]/(t²) has basis (1,t) over Q and multiplicity two in this example. Its fiber at t = 0 still has dimension one. That special-fiber dimension does not recover the full module’s rational dimension.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Dimension](#dimension) · [Module support](#module-support) · [Nilpotent operator](#nilpotent)

<a id="ideal"></a>

### Ideal

An additive subgroup of a commutative ring closed under multiplication by every element of the ring. The principal ideal (f) consists of all multiples of f.

An ideal contains scalar combinations that remain within it even after multiplication by arbitrary ring elements. This absorption property allows a quotient ring to have well-defined multiplication, because changing a representative by an ideal element does not change its product class.

A principal ideal (f) records all multiples of one element. Different generators can give the same ideal when they differ by a unit. Ideals are therefore more structural than the choice of one displayed equation, and they underlie annihilators, Fitting invariants and prime-local support.

**Quick example:** The even integers form the ideal (2) in Z: multiplying an even integer by any integer stays even.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Commutative ring with identity](#ring) · [Module annihilator](#annihilator)

<a id="prime-ideal"></a>

### Prime ideal

A proper ideal P such that ab in P implies a in P or b in P. The ideal (t) in Q\[t\] is prime because the quotient is the field Q.

Primality says that a product can vanish in the quotient only if one of its factors vanishes there. Equivalently, quotienting a commutative ring by a prime ideal gives an integral domain. Requiring the ideal to be proper excludes the whole ring.

A prime ideal need not always give a field quotient; that stronger condition corresponds to maximality. The example (t) in Q\[t\] has a field quotient and hence satisfies both. Prime ideals provide the locations used in localization and module support.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Ideal](#ideal) · [Commutative ring with identity](#ring) · [Field](#field)

<a id="localization"></a>

### Localization at a prime

A construction that makes ring elements outside a chosen prime ideal invertible, and carries a module along with that scalar change. The prime lies in the module’s support exactly when the localized module is nonzero.

Localization permits division by a specified collection of elements, here those outside a chosen prime ideal. It changes which scalar operations are invertible while retaining the algebraic information relevant near that prime.

Some module elements or whole modules can disappear after this scalar change. The support records exactly the primes where the localized module does not vanish. This is an algebraic construction; interpreting it as ordinary numerical zooming or limiting requires additional explanation rather than following from the name alone.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#support-multiplicity) · [Prime ideal](#prime-ideal) · [Module support](#module-support) · [Module](#module)

<a id="p-adic-valuation"></a>

### p-adic valuation

For a prime p and a nonzero rational x, vₚ(x) is the exponent of p in its reduced numerator minus the exponent in its reduced denominator. Set vₚ(0) = ∞. A rational is p-adically integral when its valuation is nonnegative.

The valuation counts the net power of p in a rational number, treating numerator powers positively and denominator powers negatively. It converts multiplication into addition of valuations and distinguishes p-divisibility from ordinary real magnitude.

A large positive valuation means strong divisibility by p and smallness in the associated p-adic absolute value. It need not mean a small real number. Setting vₚ(0)=∞ makes divisibility conventions consistent, but calculations involving that symbol must retain its extended-value interpretation.

**Also called:** Prime-adic valuation, v_p.

**Quick example:** v₂(12/5) = 2, while v₂(3/8) = −3.

**In the worked example:** The factorial-lane recurrence gives C₂ = 178205/966966. Its numerator contains one factor of 5 and its denominator contains none, so v₅(C₂) = 1.

[Hand-worked example](demonstrations/FACTORIAL_LANES.md) · [p-adic unit](#p-adic-unit) · [Prime power](#prime-power) · [Modular reduction](#modular-reduction)

<a id="p-adic-unit"></a>

### p-adic unit

An invertible element of the p-adic integers. For a rational number, being a p-adic unit means vₚ(x) = 0: its reduced numerator and denominator are both coprime to p.

A p-adic unit has no net factor of p, so it has a multiplicative inverse inside the p-adic integers. For a reduced rational, this requires both numerator and denominator to be indivisible by p.

P-adic integrality is weaker: nonnegative valuation permits positive powers of p, which are not units. Ordinary integer status is another separate question; a rational such as 3/5 is 2-adically integral and invertible without being an ordinary integer. These distinctions determine which divisions are legal in a lifting formula.

**Also called:** Unit at p.

**Quick example:** The rational 3/5 is a 2-adic unit because both numerator and denominator are odd.

**In the worked example:** g₁ = 1/1001 is a 5-adic unit and can be reduced modulo powers of 5. C₂ = 178205/966966 is 5-adically integral but is not a unit.

**Keep in mind:** A p-adically integral rational number need not be an ordinary integer, and a p-adically integral number of positive valuation is not a unit.

[Hand-worked example](demonstrations/FACTORIAL_LANES.md) · [p-adic valuation](#p-adic-valuation) · [Modular inverse](#modular-inverse) · [p-adic integer](#padic-integer)

<a id="characteristic-of-field"></a>

### Characteristic of a field

The least positive integer p for which adding the multiplicative identity to itself p times gives zero, if such an integer exists; otherwise the characteristic is zero. Positive field characteristic is always prime. Division by integers in formulas must respect this value.

Characteristic describes how ordinary integer coefficients are interpreted inside a field. In characteristic p, the integer p becomes zero, so factorials and denominators containing p cannot be inverted there. In characteristic zero, no positive integer becomes zero.

This affects derivative coefficients, eigenvalue degree labels and roots-of-unity averages. A monic triangular polynomial basis change can remain invertible even when a factorial-based sampling formula fails. Checking characteristic therefore separates a failure of one formula from a failure of the underlying representation itself.

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

Visible state is the information retained by the chosen observation, not necessarily the complete physical or mathematical state. Two full states can have the same current visible value while containing different hidden data.

Whether that visible value is enough depends on the prediction task. It may determine the present observation exactly yet fail to determine the next one. Testing for autonomous visible dynamics therefore requires comparing future visible outputs of all admissible full states sharing the same current summary.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Hidden state](#hidden-state) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [Coarsening](#coarsening)

<a id="hidden-state"></a>

### Hidden state

The part of the declared full state omitted by the current observation or summary. It can influence later visible outputs even when it does not affect the current output.

Hidden state includes whatever the current representation omits. Its significance comes from how the full dynamics couples it to the visible coordinates, not from whether it is directly measured now. An initially invisible difference can return to the visible part later.

The block update makes those pathways explicit through visible-to-hidden, hidden-to-hidden and hidden-to-visible maps. Ignoring the hidden state can introduce memory into the visible equation. A preparation fixing hidden coordinates reduces one kind of ambiguity, but need not make every later visible state sufficient on its own.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Visible state](#visible-state) · [Discrete memory maps](#memory-kernel)

<a id="prepared-state"></a>

### Prepared hidden initialization

An initialization that fixes the hidden coordinates by a specified rule. The example uses R(y)=(y,0). Results for this preparation need not hold for arbitrary hidden starting values.

A preparation specifies which full state is associated with a retained initial value. The map R(y)=(y,0) chooses zero hidden coordinates, so predictions from that preparation do not need to consider arbitrary initial hidden values.

After evolution, the hidden coordinates may no longer satisfy the preparation rule. Restarting the same preparation from a later visible value can therefore reset information that uninterrupted evolution retained. This explains why prepared visible evolution maps can fail the semigroup law even when the full state evolves autonomously.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Hidden state](#hidden-state) · [Reconstruction](#reconstruction) · [Autonomous dynamics of a summary](#autonomous-dynamics)

<a id="memory-kernel"></a>

### Discrete memory maps

For the block update (y,z) ↦ (Ay+Bz,Gy+Dz), the maps Mₖ=BDᵏG describe a visible-to-hidden entry, k hidden transitions, and a return. The first effect of Mₖ on prepared visible evolution occurs after k+2 full steps.

The product BDᵏG follows a specific information path: enter hidden coordinates through G, spend k additional transitions there through D, then return through B. Its contribution is delayed because entry and return each consume a full step.

Eliminating hidden variables from the visible equation produces such delayed contributions from past visible states. Vanishing later memory maps can simplify the recurrence without making the current visible value alone sufficient. The permitted hidden initialization and the complete block model must remain attached to any claimed memory-free reduction.

**In the worked example:** For A = B = G = 1 and D = 0 in the visible and hidden block update, M₀ = BD⁰G = 1 while Mₖ = 0 for k ≥ 1. Information entering the hidden coordinate returns after two full steps.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Block matrix](#block-matrix) · [Hidden state](#hidden-state) · [Prepared hidden initialization](#prepared-state) · [State sufficient for a deterministic update](#markov-state) · [Finite linear state-space realization](#state-space-realization)

<a id="autonomous-dynamics"></a>

### Autonomous dynamics of a summary

A transition rule determined by the retained current state, under the declared controls and initialization contract. For deterministic maps, full states with the same summary must have the same next summary.

An autonomous retained description has enough present information to determine its own next state under the stated contract. It does not need to inspect an unrecorded hidden coordinate or reconstruct an unspecified past history at each update.

For a deterministic summary, the decisive test is whether equal present summaries always yield equal next summaries. In the unrestricted linear setting, this becomes invariance of the summary kernel under the full update. A rule valid only for chosen representatives or prepared states has a narrower scope.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Visible state](#visible-state) · [Fiber](#fiber) · [Factorization through a map](#factorization)

<a id="state-augmentation"></a>

### State augmentation

Enlarging a retained state with additional coordinates or history needed for future prediction. The hidden-memory example retains the previous visible value along with the current one.

Augmentation retains information that a smaller state discarded, such as an extra coordinate, a delayed sample or a sufficient history statistic. The aim is to make future prediction depend only on the augmented present value.

In the Fibonacci example, retaining the preceding visible value supplies the missing hidden contribution and gives a two-coordinate autonomous update. More storage alone does not guarantee sufficiency: the added data must actually distinguish full states whose future requested outputs differ. Minimal augmentation is a separate optimization question.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Visible state](#visible-state) · [Hidden state](#hidden-state) · [Autonomous dynamics of a summary](#autonomous-dynamics)

<a id="semigroup-law"></a>

### Semigroup law for evolution maps

The identity Eₘ₊ₙ=EₘEₙ for nonnegative step counts, with E₀ the identity. It expresses agreement between uninterrupted evolution and successive uses of the same state-level evolution maps.

The law says that evolving for n steps and then m more steps agrees with evolving for m+n steps in one uninterrupted run. The maps must act on the same sufficient state description, with compatible controls and initialization conventions.

Prepared visible maps can violate this law because composing them silently reapplies the preparation and resets hidden state. Such a failure does not contradict the semigroup behavior of the full autonomous dynamics. It identifies information omitted by the retained description or changed by the restart contract.

**In the worked example:** With the hidden coordinate initialized to zero, the prepared visible maps Eₙ = CTⁿR are scalar multipliers with E₁ = 1 and E₂ = 2. Thus E₂ ≠ E₁E₁. Restarting from the visible value resets hidden information.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#hidden-memory) · [Composition](#composition) · [Identity operator](#identity) · [Prepared hidden initialization](#prepared-state)

<a id="calibration"></a>

### Exact operator calibration

Supplied input-output pairs for an unknown operation. For a linear operation, every linear relation among calibrated inputs must be respected by the supplied outputs.

Calibration constrains an unknown operation by supplying its values on selected inputs. If the operation is assumed linear, a relation among those inputs must give the corresponding relation among outputs. Inconsistent assignments cannot be repaired merely by choosing another linear extension.

Consistent data determine the operation on the calibrated span, but generally leave its behavior outside that span open. A one-step prediction can consequently be determined while a later prediction becomes ambiguous after the trajectory leaves the known region. Structural assumptions can reduce that ambiguity and must be stated explicitly.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Linear map](#linear-map) · [Calibration span](#calibration-span) · [Compatible model](#compatible-model)

<a id="calibration-span"></a>

### Calibration span

The span of the calibrated input vectors. Consistent exact linear calibration determines the operation on this span. Its outputs can leave that span.

Linearity extends calibrated values to all linear combinations of the calibrated inputs. This gives a complete known restriction on their span when the supplied input-output relations are consistent. It does not determine values on independent directions outside that span.

The known outputs can themselves leave the calibrated span. In that case, applying the operation again may require uncalibrated information. Identifying a subspace that stays inside the known region under all allowed operations is what supports reusable multi-step predictions in the tutorial.

**In the worked example:** The measurements Te₁ = e₁ and Te₂ = e₃ determine T(ae₁+be₂) = ae₁+be₃ throughout U = span(e₁,e₂). In particular, T(2e₁−e₂) = 2e₁−e₃, while Te₃ remains unspecified.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Exact operator calibration](#calibration) · [Span](#span) · [Reusable calibrated core](#reusable-core)

<a id="compatible-model"></a>

### Compatible model

A model satisfying all supplied data and every declared structural assumption. In the calibration example, all linear extensions of the known restriction are allowed, and each model stays fixed through a trajectory.

A compatible model is one complete interpretation of the unknown operation that satisfies all supplied constraints. Comparing these models reveals which conclusions follow from the data and which depend on an extra choice.

In the calibration example, choosing a model fixes its linear extension throughout a trajectory. One cannot change that extension independently at each step and still claim to be analyzing one fixed model. Additional positivity, symmetry or physical assumptions would restrict the model class and can change identifiability conclusions.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Exact operator calibration](#calibration) · [Linear extension](#linear-extension) · [Identifiability relative to a model class](#identifiability)

<a id="linear-extension"></a>

### Linear extension

A linear map on a larger vector space that agrees with a given map on its original subspace. Values on an added basis can vary unless further conditions are imposed.

To extend a linear map, choose a basis of the known subspace and complete it to a basis of the larger space. Values on the added basis vectors specify the previously unconstrained part, while the original basis values retain the known restriction.

This construction explains why exact calibration can leave many compatible models. It establishes algebraic extensions under the stated vector-space setting, not necessarily extensions satisfying extra norm, positivity or circuit constraints. Those additional structures need their own existence and uniqueness analysis.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Linear map](#linear-map) · [Subspace](#subspace) · [Basis](#basis)

<a id="reusable-core"></a>

### Reusable calibrated core

For the tutorial’s unrestricted linear extension class and full-state output, the largest subspace inside the calibration span preserved by every calibrated operation. All finite operation sequences from this subspace are determined by the calibration.

The reusable core identifies starting vectors whose allowed operation sequences stay within the region controlled by calibration. One-step knowledge is insufficient if the resulting vector can leave that known region before the next operation is applied.

Within the tutorial’s unrestricted linear-extension and full-state-output contract, preserving a subspace inside the calibration span ensures that all finite continuations remain determined there. Changing the model class or asking only for a partial output can change the appropriate core, so this definition should not be generalized without restating the task.

**In the worked example:** With Te₁ = e₁ and Te₂ = e₃, the known image of ae₁+be₂ stays in U = span(e₁,e₂) exactly when b = 0. The retained domain stabilizes at span(e₁), where every compatible extension satisfies Tⁿ(ae₁) = ae₁ for all n ≥ 0.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Calibration span](#calibration-span) · [Invariant subspace](#invariant-subspace) · [Compatible model](#compatible-model)

<a id="identifiability"></a>

### Identifiability relative to a model class

A requested quantity is identifiable from the supplied data when every compatible model gives the same value. Identifying a particular output can require less information than identifying the whole model.

Identifiability asks whether the available evidence forces one answer across all models still allowed by the assumptions. It is a uniqueness-of-consequence question, not necessarily uniqueness of the whole underlying model.

Several different models can agree on a requested prediction even when their unobserved parameters differ. Conversely, selecting one convenient fitted model does not establish that its prediction is identifiable. To disprove identifiability, exhibit compatible models with different requested values; to establish it, show that every compatible model agrees.

**Quick example:** Observing only x+y cannot distinguish parameter pairs (1,2) and (2,1) if both are allowed.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#calibrated-continuation) · [Compatible model](#compatible-model) · [Exact operator calibration](#calibration) · [Obstruction](#obstruction)

<a id="state-space-realization"></a>

### Finite linear state-space realization

A description of a discrete linear system by xₙ₊₁ = Axₙ+Buₙ and yₙ = Cxₙ+Duₙ. It declares the retained state x, input u and observation y. Different coordinate systems can describe the same input-output behavior.

The state stores the information used to continue the system, while the observation extracts the quantity reported externally. Inputs affect the next state through B and can contribute immediately to the output through D. The matrices therefore have different typed roles despite appearing in one model.

An invertible state-coordinate change can preserve input-output behavior while changing these stored matrices. Minimal state dimension and restricted physical realization are additional questions. Observing y alone also need not provide a sufficient state, because distinct hidden states can share the same current output.

**Quick example:** The hidden-memory example has full state (y,z) and autonomous update matrix \[\[1,1\],\[1,0\]\]. Its visible observation selects y.

[Further reading](examples/22_HIDDEN_MEMORY.md) · [Visible state](#visible-state) · [Hidden state](#hidden-state) · [Realization](#realization) · [Scalar McMillan degree](#mcmillan-degree)

<a id="markov-state"></a>

### State sufficient for a deterministic update

A retained value that determines its own next value for every admissible full state, under a specified deterministic evolution. If R is the summary and T the full update, this requires a map T̄ with T̄R = RT on the admissible states.

In this deterministic use, the retained value contains everything needed for the next update. The factorization T̄R=RT says that updating the full state and then summarizing agrees with updating the summary directly.

The condition must hold for every admissible state, not merely one observed trajectory. Adding an appropriate delayed value can make an insufficient summary sufficient, as in the hidden-memory example. Stochastic Markov properties instead concern conditional probability laws and require a probability model beyond this deterministic criterion.

**Quick example:** In the Fibonacci update, y alone is insufficient, while (yₙ,yₙ₋₁) has the autonomous rule (u,v) ↦ (u+v,u).

**Keep in mind:** Stochastic Markov properties concern conditional distributions and require their own probability model.

[Further reading](examples/22_HIDDEN_MEMORY.md) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [Sufficient summary for a requested output](#sufficient-summary) · [State augmentation](#state-augmentation)

<a id="fixed-point"></a>

### Fixed point

An input x satisfying T(x) = x for a declared map T. For a linear projector P, the fixed points are precisely its image. Being fixed is an algebraic property; stability under nearby perturbations is a further question.

A fixed point is unchanged by one application, so it remains unchanged under every repeated application of the same map. For a projector, every output is fixed, which is why its fixed-point set equals its image.

Existence of a fixed point does not establish uniqueness or attraction. Nearby states can move away even when the fixed state itself stays put. Stability and convergence toward a fixed point depend on additional properties of the dynamics and on the neighborhood and metric being considered.

**Quick example:** The projector P(x,y) = (x,0) fixes every point on the horizontal axis.

[Further reading](operators/PACKETS.md) · [Projector](#projector) · [Image](#image) · [Invariant subspace](#invariant-subspace)

<a id="inference-and-probability"></a>

## Inference and probability

The model, observation and Gaussian calculations used in the inference example.

[Finite-dimensional Gaussian model](#gaussian-model) · [Prior distribution](#prior) · [Likelihood](#likelihood) · [Posterior distribution](#posterior) · [Covariance matrix](#covariance) · [Precision matrix](#precision-matrix) · [Observation innovation](#innovation) · [Exact Gaussian gain](#gaussian-gain) · [Joseph covariance](#joseph-covariance)

<a id="gaussian-model"></a>

### Finite-dimensional Gaussian model

A model with a Gaussian state and specified linear observations with Gaussian noise. The tutorial supplies an independent noise variable, a prior mean and covariance, an observation matrix and a positive noise variance.

The model specifies a prior state distribution and an observation mechanism, including the noise distribution and its independence assumptions. Linearity and Gaussian structure make the conditional mean and covariance computable through explicit finite matrix formulas.

Those formulas are exact consequences of the declared probabilistic model, not universal guarantees that the model matches observed reality. Changing noise dependence, covariance assumptions or observation nonlinearity can change the posterior calculation. Exact rational matrix arithmetic can verify an example’s algebra without validating its statistical assumptions.

**Also called:** Multivariate Gaussian model, Multivariate normal model.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Prior distribution](#prior) · [Likelihood](#likelihood) · [Covariance matrix](#covariance)

<a id="prior"></a>

### Prior distribution

The state distribution specified before conditioning on the observation under the declared model. A Gaussian prior is described by its mean and covariance.

The prior records the distribution used before incorporating the particular observation under discussion. It can encode earlier evidence or modeling assumptions; the word does not mean that it must precede every observation in the entire history of a problem.

Its mean and covariance influence how strongly a Gaussian update responds to new data. Two different priors can produce different posteriors from the same likelihood. Once the posterior is reused as a later prior, the new observation and independence contract must be stated consistently.

**Also called:** Prior.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Finite-dimensional Gaussian model](#gaussian-model) · [Posterior distribution](#posterior) · [Covariance matrix](#covariance)

<a id="likelihood"></a>

### Likelihood

For a fixed observed value, the observation density viewed as a function of the proposed state or parameter. It is combined with the prior and normalized to obtain a posterior density when that density formula applies.

The likelihood holds the observed data fixed and varies the candidate state or parameter. It expresses how compatible those data are with different candidates under the observation model. As a function of the candidate, it need not integrate to one.

Bayesian updating multiplies this function by the prior and normalizes over the candidate state when the density formula applies. Confusing likelihood with the posterior omits that prior information and normalization. The chosen observation density and reference measure also belong to the model.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Prior distribution](#prior) · [Posterior distribution](#posterior) · [Finite-dimensional Gaussian model](#gaussian-model)

<a id="posterior"></a>

### Posterior distribution

The state distribution conditional on the observed data under the supplied prior and observation model. The tutorial computes the usual explicit Gaussian conditional density by completing the square.

The posterior incorporates the observed data through the specified prior and observation law. In the tutorial’s linear Gaussian setting, completing the quadratic exponent gives another Gaussian distribution with an updated mean and covariance.

It describes conditional uncertainty under that model, rather than certainty about the true state or proof of model adequacy. A narrow posterior can still be misleading if the observation or noise assumptions are wrong. Singular Gaussian models require care because an ordinary full-dimensional density or inverse covariance may be unavailable.

**Also called:** Posterior.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Prior distribution](#prior) · [Likelihood](#likelihood) · [Exact Gaussian gain](#gaussian-gain)

<a id="covariance"></a>

### Covariance matrix

For a random vector X with mean m and finite second moments, the matrix E\[(X−m)(X−m)ᵀ\]. Its diagonal entries are variances. For a unit direction u, uᵀCu is the variance in that direction.

Covariance measures fluctuations around the mean and their pairwise relationships. Its diagonal gives individual variances, while off-diagonal entries describe how coordinates vary together. Every real covariance matrix is symmetric positive semidefinite because every scalar projection has nonnegative variance.

The matrix changes with the coordinate system and its units. Zero covariance implies independence for jointly Gaussian coordinates, but not for arbitrary distributions. Singular covariance means that some linear direction has zero variance, so an ordinary precision-matrix inverse is unavailable there.

**Quick example:** Independent coordinates with variances 1 and 4 have covariance matrix diag(1,4).

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Positive semidefinite matrix](#positive-semidefinite) · [Finite-dimensional Gaussian model](#gaussian-model) · [Precision matrix](#precision-matrix) · [Gaussian quadratic form](#gaussian-quadratic-form)

<a id="precision-matrix"></a>

### Precision matrix

The inverse covariance when the covariance is invertible. In a nonsingular Gaussian density it appears in the quadratic exponent. This use of precision is distinct from the number of bits in stored arithmetic.

The precision matrix weights deviations in the exponent of a nonsingular Gaussian density. Directions with smaller covariance receive stronger quadratic penalties after inversion. Off-diagonal precision structure has its own interpretation and should not be read as simply the reciprocal of each covariance entry.

The inverse exists only when covariance is nonsingular. A singular Gaussian distribution can still be valid, but needs a suitable lower-dimensional or generalized formulation. Arithmetic precision, measured in stored bits, is an unrelated use of the same word.

**Also called:** Inverse covariance matrix, Concentration matrix.

**Quick example:** For covariance diag(1,4), the precision matrix is diag(1,1/4).

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Covariance matrix](#covariance) · [Inverse](#inverse) · [Precision](#precision)

<a id="innovation"></a>

### Observation innovation

The difference d=y−Hm between an observation and its predicted mean in the linear model. Its covariance is S=HPHᵀ+R when the state covariance is P and the independent noise covariance is R.

The innovation measures how surprising the observation is relative to its predicted mean before updating. Its covariance includes both projected state uncertainty and observation noise, so a given discrepancy can have different significance at different uncertainty scales.

The gain maps this observation-space discrepancy back into a state-space correction. The subtraction convention matters for its sign. An innovation is also not by itself a diagnosis of model error: it combines random state variation, noise and any mismatch present in the assumed model.

**Also called:** Observation residual.

**Quick example:** If an observation is 7 and the predicted observation is 5, the innovation is 2 under the observation-minus-prediction convention.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Finite-dimensional Gaussian model](#gaussian-model) · [Covariance matrix](#covariance) · [Exact Gaussian gain](#gaussian-gain)

<a id="gaussian-gain"></a>

### Exact Gaussian gain

For the declared linear Gaussian model, K=PHᵀ(HPHᵀ+R)⁻¹. Multiplying the innovation by K gives the posterior mean correction. Positive noise covariance makes the displayed observation-space inverse exist.

The gain determines how the observation discrepancy changes the prior mean. Its factors combine state-observation covariance with inverse innovation covariance, balancing how informative the observation is against the uncertainty in its noise and predicted value.

In the declared Gaussian model, m+K(y−Hm) is the exact conditional mean formula. A different chosen gain can define an estimator but need not give that posterior mean. The inverse belongs to observation space and requires its stated positivity or nonsingularity condition.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean, and code](LEARNING_MAP.md#gaussian-update) · [Observation innovation](#innovation) · [Posterior distribution](#posterior) · [Joseph covariance](#joseph-covariance)

<a id="joseph-covariance"></a>

### Joseph covariance

For a gain B, the matrix (I−BH)P(I−BH)ᵀ+BRBᵀ. It is positive semidefinite for valid prior and noise covariances. At the exact gain it equals the posterior covariance. A general gain still needs its own accuracy check.

The two terms propagate prior uncertainty and noise uncertainty through a specified linear gain. Their positive-semidefinite sum makes the sources of estimator error visible, rather than relying on a cancellation-prone shortened expression.

At the exact Gaussian gain, this agrees with the posterior covariance under the tutorial’s independence assumptions. For an arbitrary gain, it instead describes the corresponding linear update’s error covariance in that model. Positive semidefiniteness alone does not prove that the gain is optimal or that the estimator is accurate.

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
