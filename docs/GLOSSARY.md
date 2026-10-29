# Glossary and notation

This guide explains 183 terms used in the collection and its finite examples. Start with a subject below, use the [alphabetical index](#alphabetical-index), or look up [symbols](#symbols-in-the-introductory-example).

A word can have a more specific meaning in another paper. The paper’s definitions and hypotheses take precedence. Examples and source links provide context without changing any recorded evidence status.

[Look up notation across the collection](NOTATION_INDEX.md) · [Work through the calculations by hand](HAND_WORKED_EXAMPLES.md) · [Papers, proofs, Lean and code by topic](LEARNING_MAP.md) · [First software runs](FIRST_RUN.md)

- [Linear foundations](#linear-foundations)
- [Operators, seeds and packets](#operators-and-packets)
- [Coordinates and transfer](#coordinates-and-transfer)
- [Refinement and constraints](#refinement-and-constraints)
- [Arithmetic and error](#arithmetic-and-error)
- [Claims and evidence](#claims-and-evidence)
- [Series and cyclic functions](#series-and-functions)
- [Finite quantum systems](#finite-quantum)
- [Arithmetic and modules](#arithmetic-and-modules)
- [Dynamics, memory and calibration](#dynamics-and-calibration)
- [Inference and probability](#inference-and-probability)

<a id="linear-foundations"></a>

## Linear foundations

The objects and notation used in the finite examples.

[Scalar](#scalar) · [Field](#field) · [Vector](#vector) · [Vector space](#vector-space) · [Linear map](#linear-map) · [Matrix](#matrix) · [Identity operator](#identity) · [Span](#span) · [Linear independence](#linear-independence) · [Basis](#basis) · [Dimension](#dimension) · [Kernel](#kernel) · [Image](#image) · [Rank](#rank) · [Inner product](#inner-product) · [Norm](#norm) · [Subspace](#subspace) · [Nullity](#nullity) · [Rank–nullity identity](#rank-nullity) · [Injective map](#injective) · [Surjective map](#surjective) · [Linear isomorphism](#isomorphism) · [Direct sum](#direct-sum) · [Quotient space](#quotient-space) · [Determinant](#determinant) · [Domain and codomain](#domain-codomain)

<a id="scalar"></a>

### Scalar

A number from the declared coefficient field, used to multiply vectors. The hand-worked matrix examples use real scalars and exact rational entries.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Field](#field) · [Vector](#vector)

<a id="field"></a>

### Field

A number system with addition, subtraction, multiplication and division by every nonzero element. The rational, real and complex numbers are examples. A result over one field does not automatically hold over another.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Scalar](#scalar)

<a id="vector"></a>

### Vector

An element of a vector space. In the finite examples it is a column of numbers. Its coordinates depend on a chosen representation.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#packets) · [Vector space](#vector-space) · [Coordinates](#coordinates)

<a id="vector-space"></a>

### Vector space

A collection of vectors closed under addition and scalar multiplication, with the usual distributive and associative laws. The space of pairs of real numbers is denoted R².

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#seeds) · [Field](#field) · [Span](#span) · [Basis](#basis)

<a id="linear-map"></a>

### Linear map

A map T satisfying T(au + bv) = aT(u) + bT(v) for all vectors u, v and allowed scalars a, b. A linear map preserves linear combinations.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#transfer) · [Matrix](#matrix) · [Kernel](#kernel) · [Image](#image)

<a id="matrix"></a>

### Matrix

A rectangular array representing a linear map after bases have been chosen. An m by n matrix takes n coordinates to m coordinates. Each output coordinate is a row multiplied by the input column.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Linear map](#linear-map) · [Basis](#basis) · [Composition](#composition)

<a id="identity"></a>

### Identity operator

The map I that leaves every input unchanged, so Ix = x. The subscript in I₂ or I₃ specifies the dimension when needed.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean and code](LEARNING_MAP.md#packets) · [Inverse](#inverse) · [Complete packet family](#complete-packet-family)

<a id="span"></a>

### Span

All finite linear combinations of a specified set of vectors. The span of the empty set consists only of the zero vector. With an operator action, one may first apply allowed operators and then take the span.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean and code](LEARNING_MAP.md#seeds) · [Seed](#seed) · [Basis](#basis) · [Linear independence](#linear-independence)

<a id="linear-independence"></a>

### Linear independence

A family is linearly independent when the only linear combination giving zero has every coefficient zero. No member of a finite independent family can be formed from the others.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#seeds) · [Span](#span) · [Basis](#basis)

<a id="basis"></a>

### Basis

A linearly independent spanning family. Every vector has a unique finite linear combination in that basis. Redundant measurements can describe a vector without forming a basis.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Span](#span) · [Linear independence](#linear-independence) · [Redundant coordinates](#redundancy)

<a id="dimension"></a>

### Dimension

The number of vectors in a basis of a finite-dimensional vector space. In these examples, R² has dimension two even when three redundant measurements are stored.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#redundancy) · [Basis](#basis) · [Rank](#rank) · [Seed rank](#seed-rank)

<a id="kernel"></a>

### Kernel

For a linear map T, the vectors sent to zero: ker T = {x : Tx = 0}. A nonzero kernel describes directions that this map cannot distinguish from zero.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean and code](LEARNING_MAP.md#obstructions) · [Image](#image) · [Fiber](#fiber) · [Factorization through a map](#factorization)

<a id="image"></a>

### Image

The outputs actually attained by a map. For a linear map T, im T = {Tx : x is an allowed input} is a subspace of the target. The declared target can be larger than the image.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean and code](LEARNING_MAP.md#redundancy) · [Kernel](#kernel) · [Rank](#rank) · [Left inverse](#left-inverse)

<a id="rank"></a>

### Rank

For a finite linear map, the dimension of its image. A matrix has full column rank when its columns are linearly independent, so it has no nonzero input in its kernel.

**Keep in mind:** Matrix rank and seed rank answer different questions.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean and code](LEARNING_MAP.md#redundancy) · [Dimension](#dimension) · [Image](#image) · [Seed rank](#seed-rank)

<a id="inner-product"></a>

### Inner product

For real vector spaces, a symmetric bilinear pairing with ⟨v,v⟩ > 0 for every nonzero v. It defines lengths and angles. Positive weights give the pairing sum_i w_i u_i v_i. Complex inner products use conjugate symmetry and conjugate linearity in one argument.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean and code](LEARNING_MAP.md#averages) · [Norm](#norm) · [Orthogonal projector](#orthogonal-projector)

<a id="norm"></a>

### Norm

A nonnegative measure of size that is zero only at the zero vector, scales by the absolute value of a scalar and satisfies the triangle inequality. The Euclidean norm is the square root of the sum of squared coordinates.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Inner product](#inner-product) · [Residual](#residual) · [Tolerance](#tolerance)

<a id="subspace"></a>

### Subspace

A subset of a vector space that contains zero and is closed under addition and scalar multiplication. Kernels and images of linear maps are subspaces.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#kernels) · [Kernel](#kernel) · [Image](#image)

<a id="nullity"></a>

### Nullity

The dimension of the kernel of a finite-dimensional linear map. It counts independent input directions erased by the map.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#kernels) · [Kernel](#kernel) · [Dimension](#dimension)

<a id="rank-nullity"></a>

### Rank–nullity identity

For a linear map with finite-dimensional domain V, dim V = rank T + nullity T. The rank concerns the image, not the dimension of the entire declared target.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#kernels) · [Rank](#rank) · [Nullity](#nullity)

<a id="injective"></a>

### Injective map

A map that sends distinct inputs to distinct outputs. A linear map is injective exactly when its kernel contains only zero.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#kernels) · [Kernel](#kernel) · [Left inverse](#left-inverse)

<a id="surjective"></a>

### Surjective map

A map whose image is its entire declared target. Surjectivity depends on which target is specified.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#kernels) · [Image](#image) · [Rank](#rank)

<a id="isomorphism"></a>

### Linear isomorphism

A bijective linear map between vector spaces over the same field. Its inverse is linear. It preserves the vector-space structure, although lengths need not be preserved.

[Hand-worked example](examples/03_COORDINATES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Inverse](#inverse) · [Coordinate change](#coordinate-change)

<a id="direct-sum"></a>

### Direct sum

A decomposition into subspaces in which each vector has a unique sum of components. For two subspaces, uniqueness is equivalent to their intersection containing only zero.

[Hand-worked example](examples/01_PACKETS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#packets) · [Subspace](#subspace) · [Complete packet family](#complete-packet-family)

<a id="quotient-space"></a>

### Quotient space

The vector space V/W obtained by identifying vectors whose difference lies in a subspace W. A coset x+W records the equivalence class of x.

[Hand-worked example](examples/10_KERNELS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#obstructions) · [Subspace](#subspace) · [Fiber](#fiber)

<a id="determinant"></a>

### Determinant

A scalar attached to a square matrix. For [[a,b],[c,d]] it is ad − bc. Over a field, a square matrix is invertible exactly when its determinant is nonzero.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#elimination) · [Inverse](#inverse) · [Field](#field)

<a id="domain-codomain"></a>

### Domain and codomain

The declared input and target spaces of a map. The codomain includes all permitted outputs, while the image consists of outputs actually attained.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#typed-paths) · [Image](#image) · [Surjective map](#surjective) · [Typed system](#typed-system)

<a id="operators-and-packets"></a>

## Operators, seeds and packets

How an allowed action generates, selects and decomposes objects.

[Realization](#realization) · [Seed](#seed) · [Address](#address) · [Projector](#projector) · [Packet](#packet) · [Typed system](#typed-system) · [Operator algebra](#operator-algebra) · [Seed rank](#seed-rank) · [Cyclic vector](#cyclic) · [Orthogonal projector](#orthogonal-projector) · [Complete packet family](#complete-packet-family) · [Mutual annihilation](#mutual-annihilation) · [Invariant subspace](#invariant-subspace) · [Eigenvector](#eigenvector) · [Eigenvalue](#eigenvalue) · [Eigenspace](#eigenspace) · [Diagonalizable operator](#diagonalizable) · [Polynomial in an operator](#polynomial-in-operator) · [Minimal polynomial](#minimal-polynomial) · [Spectral projector](#spectral-projector) · [Commutator](#commutator) · [Typed path](#typed-path) · [Operator relation](#relation) · [Nilpotent operator](#nilpotent)

<a id="realization"></a>

### Realization

A way to represent a declared system using concrete spaces and operations while respecting its required relations. A finite matrix realization assigns a space to each type and a matrix to each permitted arrow.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate) · [Papers, proofs, Lean and code](LEARNING_MAP.md#seeds) · [Typed system](#typed-system) · [Operator algebra](#operator-algebra) · [Compatibility](#compatibility)

<a id="seed"></a>

### Seed

Initial generating data from which the allowed operator action produces further elements. Whether a seed is sufficient depends on both the object and the declared action.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean and code](LEARNING_MAP.md#seeds) · [Span](#span) · [Seed rank](#seed-rank) · [Cyclic vector](#cyclic)

<a id="address"></a>

### Address

A label for a legal operator path or a packet coordinate. Examples include signal phases, residue classes and positions in a packet tree. An address identifies a location in a representation, not necessarily a physical location.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Typed system](#typed-system) · [Packet](#packet) · [Residue class](#residue-class)

<a id="projector"></a>

### Projector

A linear operator P satisfying P² = P. Applying it twice has the same effect as applying it once. This algebraic definition does not require orthogonality.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors) · [Papers, proofs, Lean and code](LEARNING_MAP.md#packets) · [Orthogonal projector](#orthogonal-projector) · [Packet](#packet) · [Redundant coordinates](#redundancy)

<a id="packet"></a>

### Packet

In the finite projector example, a selected component Pᵢx or the subspace in which it lies, according to context. Signal, algebraic and arithmetic works may assign the word more specific meanings.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Papers, proofs, Lean and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Complete packet family](#complete-packet-family) · [Address](#address)

<a id="typed-system"></a>

### Typed system

A system that records which objects an operation accepts and returns. A path of operations is legal only when consecutive input and output types agree. Types are part of the mathematical specification.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#typed-finite-expressions) · [Papers, proofs, Lean and code](LEARNING_MAP.md#transfer) · [Linear map](#linear-map) · [Composition](#composition) · [Realization](#realization)

<a id="operator-algebra"></a>

### Operator algebra

In the finite linear setting, a collection of linear operators closed under sums, scalar multiples and composition. When a unital algebra is intended, the identity operator is included.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate) · [Papers, proofs, Lean and code](LEARNING_MAP.md#seeds) · [Composition](#composition) · [Seed](#seed) · [Invariant subspace](#invariant-subspace)

<a id="seed-rank"></a>

### Seed rank

In the finite linear example, the least number of seeds whose operator-generated span is the whole space. More general definitions can involve modules, dense generation and cardinalities. Read the definition in the chosen work.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean and code](LEARNING_MAP.md#seeds) · [Seed](#seed) · [Span](#span) · [Rank](#rank)

<a id="cyclic"></a>

### Cyclic vector

For a single linear operator T, a vector v is cyclic when v, Tv, T²v and further iterates span the space under consideration. One cyclic vector is enough to generate that operator module.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean and code](LEARNING_MAP.md#seeds) · [Seed](#seed) · [Span](#span)

<a id="orthogonal-projector"></a>

### Orthogonal projector

A projector onto a subspace whose residual x − Px is perpendicular to that subspace in the specified inner product. In ordinary real Euclidean coordinates its matrix is symmetric as well as idempotent.

**Keep in mind:** Orthogonality depends on the inner product. Weighted averaging need not have a symmetric matrix in ordinary coordinates.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Inner product](#inner-product)

<a id="complete-packet-family"></a>

### Complete packet family

In these finite examples, projectors Pᵢ with PᵢPⱼ = 0 for distinct indices and sum_i Pᵢ = I. These identities decompose every vector as x = sum_i Pᵢx.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Papers, proofs, Lean and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Mutual annihilation](#mutual-annihilation) · [Reconstruction](#reconstruction)

<a id="mutual-annihilation"></a>

### Mutual annihilation

The relation PᵢPⱼ = 0 whenever i and j differ. Applying one selection after a different selection gives zero. For a pair of projectors, both orders must be checked.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Papers, proofs, Lean and code](LEARNING_MAP.md#packets) · [Projector](#projector) · [Complete packet family](#complete-packet-family)

<a id="invariant-subspace"></a>

### Invariant subspace

A subspace W preserved by an operator T, meaning T(W) is contained in W. Preservation does not require T to act as the identity on W.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Papers, proofs, Lean and code](LEARNING_MAP.md#seeds) · [Span](#span) · [Operator algebra](#operator-algebra)

<a id="eigenvector"></a>

### Eigenvector

A nonzero vector v for which Tv = λv. The scalar λ is the associated eigenvalue. Zero is excluded from the definition of eigenvector.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#spectral) · [Eigenvalue](#eigenvalue) · [Invariant subspace](#invariant-subspace)

<a id="eigenvalue"></a>

### Eigenvalue

A scalar λ such that Tv = λv for some nonzero v over the specified field. A real matrix may have no real eigenvalue even though it has eigenvalues over the complex numbers.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#spectral) · [Eigenvector](#eigenvector) · [Field](#field)

<a id="eigenspace"></a>

### Eigenspace

For an operator T and scalar λ, the kernel of T − λI. It includes zero and all eigenvectors with eigenvalue λ.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#spectral) · [Kernel](#kernel) · [Eigenvector](#eigenvector)

<a id="diagonalizable"></a>

### Diagonalizable operator

An operator that has a basis of eigenvectors over the stated field. Equivalently, its matrix becomes diagonal after an invertible change of basis.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#spectral) · [Basis](#basis) · [Eigenvector](#eigenvector) · [Coordinate change](#coordinate-change)

<a id="polynomial-in-operator"></a>

### Polynomial in an operator

Substitute T into p(t) = a₀ + a₁t + ⋯ + aₙtⁿ to obtain p(T) = a₀I + a₁T + ⋯ + aₙTⁿ. The constant term acts through the identity operator.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#spectral) · [Operator algebra](#operator-algebra) · [Identity operator](#identity)

<a id="minimal-polynomial"></a>

### Minimal polynomial

For a linear operator on a nonzero finite-dimensional space over a field, the monic polynomial of least degree with m(T) = 0. It records an exact operator relation.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#spectral) · [Polynomial in an operator](#polynomial-in-operator) · [Operator relation](#relation)

<a id="spectral-projector"></a>

### Spectral projector

In the diagonalizable finite example, the projector onto one eigenspace along the sum of the others. Distinct eigenvalues allow a polynomial interpolation formula for these projectors.

[Hand-worked example](examples/11_SPECTRAL_PROJECTORS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#spectral) · [Projector](#projector) · [Eigenspace](#eigenspace) · [Diagonalizable operator](#diagonalizable)

<a id="commutator"></a>

### Commutator

For operators on the same space, [A,B] = AB − BA. A zero commutator means the two orders of composition agree.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#typed-paths) · [Composition](#composition) · [Operator algebra](#operator-algebra)

<a id="typed-path"></a>

### Typed path

A sequence of arrows in which each output type matches the next input type. Its realization is the corresponding ordered composition. An empty path at a type acts as its identity.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#typed-paths) · [Typed system](#typed-system) · [Composition](#composition) · [Identity operator](#identity)

<a id="relation"></a>

### Operator relation

A required equality between legal operator expressions, such as T² = 0. In a typed system, both sides must have the same input and output types.

[Hand-worked example](examples/15_TYPED_PATHS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#typed-paths) · [Typed path](#typed-path) · [Realization](#realization) · [Minimal polynomial](#minimal-polynomial)

<a id="nilpotent"></a>

### Nilpotent operator

An operator N for which Nᵏ = 0 for some positive integer k. It can be nonzero. The smallest such k on a nonzero space is its nilpotency index.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Operator algebra](#operator-algebra) · [Minimal polynomial](#minimal-polynomial)

<a id="coordinates-and-transfer"></a>

## Coordinates and transfer

How descriptions change and operations move between components.

[Coordinates](#coordinates) · [Analysis and synthesis](#analysis-synthesis) · [Transfer block](#transfer-block) · [Coordinate change](#coordinate-change) · [Inverse](#inverse) · [Left inverse](#left-inverse) · [Redundant coordinates](#redundancy) · [Composition](#composition) · [Operator conjugation](#conjugation) · [Intertwiner](#intertwiner) · [Block matrix](#block-matrix) · [Schur complement](#schur-complement) · [Elimination](#elimination) · [Orthogonal matrix](#orthogonal-matrix) · [Normalization](#normalization)

<a id="coordinates"></a>

### Coordinates

Values describing an object relative to a chosen representation. Coordinates can be unique basis coefficients or redundant measurements, depending on the setup.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Basis](#basis) · [Coordinate change](#coordinate-change) · [Redundant coordinates](#redundancy)

<a id="analysis-synthesis"></a>

### Analysis and synthesis

Analysis sends an object to coordinates. Synthesis returns an object from coordinates. In the finite model, A analyzes and S synthesizes, and exact reconstruction is the identity SA = I.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean and code](LEARNING_MAP.md#redundancy) · [Left inverse](#left-inverse) · [Coordinates](#coordinates) · [Reconstruction](#reconstruction)

<a id="transfer-block"></a>

### Transfer block

The part of an operation connecting a source component to a target component. With source projector Pᵢ, target projector Qⱼ and operator T, the block is QⱼTPᵢ. Complete source and target families allow the blocks to reconstruct T.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean and code](LEARNING_MAP.md#transfer) · [Projector](#projector) · [Composition](#composition) · [Reconstruction](#reconstruction)

<a id="coordinate-change"></a>

### Coordinate change

A transformation between descriptions of the same object. In the invertible linear example the convention is y = Cx, so x = C⁻¹y. Keeping track of the direction prevents inverse formulas from being swapped.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Coordinates](#coordinates) · [Inverse](#inverse) · [Operator conjugation](#conjugation)

<a id="inverse"></a>

### Inverse

A map that undoes another map in both directions. For a square invertible matrix C, the inverse satisfies C⁻¹C = CC⁻¹ = I.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Identity operator](#identity) · [Left inverse](#left-inverse)

<a id="left-inverse"></a>

### Left inverse

For A mapping an input space to a coordinate space, S is a left inverse when SA = I on the input space. This gives exact reconstruction of analyzed inputs. It does not imply AS = I on the entire coordinate space.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean and code](LEARNING_MAP.md#redundancy) · [Inverse](#inverse) · [Analysis and synthesis](#analysis-synthesis) · [Image](#image)

<a id="redundancy"></a>

### Redundant coordinates

A representation containing more coordinate entries than are needed for a basis description. Valid coordinate lists can satisfy relations, such as a third measurement being the sum of the first two.

**Keep in mind:** The reconstruction components SEᵢA can sum to the identity without being projectors.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors) · [Papers, proofs, Lean and code](LEARNING_MAP.md#redundancy) · [Basis](#basis) · [Analysis and synthesis](#analysis-synthesis) · [Projector](#projector)

<a id="composition"></a>

### Composition

Applying one map after another. In a matrix product UT, T acts first and U acts second. The intermediate dimensions or types must agree.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#typed-finite-expressions) · [Papers, proofs, Lean and code](LEARNING_MAP.md#transfer) · [Typed system](#typed-system) · [Matrix](#matrix) · [Transfer block](#transfer-block)

<a id="conjugation"></a>

### Operator conjugation

The change in an operator matrix under an invertible coordinate change. With y = Cx and original operator T, the new matrix is CTC⁻¹. This usage is distinct from complex conjugation.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Coordinate change](#coordinate-change) · [Intertwiner](#intertwiner)

<a id="intertwiner"></a>

### Intertwiner

A linear map C connecting operators T and U by CT = UC. Applying T and then C agrees with applying C and then U. An intertwiner need not be invertible.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Operator conjugation](#conjugation) · [Commuting diagram](#commuting-diagram)

<a id="block-matrix"></a>

### Block matrix

A matrix grouped into rectangular submatrices according to decompositions of its input and output coordinates. Block products require the inner dimensions to agree.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#transfer) · [Matrix](#matrix) · [Transfer block](#transfer-block)

<a id="schur-complement"></a>

### Schur complement

For the block matrix [[A,B],[C,D]] with invertible A, the Schur complement of A is D − CA⁻¹B. It is the remaining operator after eliminating the first block of unknowns.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#elimination) · [Block matrix](#block-matrix) · [Elimination](#elimination) · [Inverse](#inverse)

<a id="elimination"></a>

### Elimination

Removing selected unknowns by solving part of a system and substituting into the remaining equations. The substitution requires its stated invertibility or solvability assumptions.

[Hand-worked example](examples/12_BLOCK_ELIMINATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#elimination) · [Schur complement](#schur-complement) · [Reconstruction](#reconstruction)

<a id="orthogonal-matrix"></a>

### Orthogonal matrix

A real square matrix Q with QᵀQ = QQᵀ = I. It preserves the Euclidean inner product and norm. A transform with orthogonal rows can still need normalization to satisfy this identity.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#haar) · [Inner product](#inner-product) · [Norm](#norm) · [Normalization](#normalization)

<a id="normalization"></a>

### Normalization

A declared scaling convention. For a Haar pair, dividing sums and differences by two gives averages, while dividing by √2 gives a Euclidean norm-preserving transform.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#haar) · [Haar pair](#haar-pair) · [Orthogonal matrix](#orthogonal-matrix)

<a id="refinement-and-constraints"></a>

## Refinement and constraints

How descriptions become finer, discard information or meet a compatibility condition.

[Refinement](#refinement) · [Obstruction](#obstruction) · [Coarsening](#coarsening) · [Polyphase decomposition](#polyphase) · [Residue class](#residue-class) · [Compatibility](#compatibility) · [Commuting diagram](#commuting-diagram) · [Reconstruction](#reconstruction) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Lift](#lift) · [Finite conditional expectation](#conditional-expectation) · [Completion](#completion) · [Haar pair](#haar-pair) · [Detail coefficient](#detail-coefficient) · [Repair direction](#repair-direction) · [Free linear repair](#free-repair) · [Finite repair menu](#repair-menu) · [Repair selection cost](#repair-cost) · [Feasibility](#feasibility) · [Linear obstruction witness](#dual-witness)

<a id="refinement"></a>

### Refinement

A compatible move from a coarser description to a finer one. In finite packet refinement, each fine packet has a coarse parent and each coarse projector is the sum of its children.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Coarsening](#coarsening) · [Compatibility](#compatibility) · [Residue class](#residue-class)

<a id="obstruction"></a>

### Obstruction

An identified reason a requested construction cannot meet its stated conditions. In the recovery example, two inputs have the same coarse value but require different answers, so no recovery function from that value alone exists.

**Keep in mind:** A nonzero numerical residual is not automatically a proof that every possible construction fails.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean and code](LEARNING_MAP.md#obstructions) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Residual](#residual)

<a id="coarsening"></a>

### Coarsening

Passing to a description that groups or forgets distinctions. Combining fine packets can recover a coarse packet, while discarding the fine values can prevent later reconstruction.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Refinement](#refinement) · [Obstruction](#obstruction) · [Fiber](#fiber)

<a id="polyphase"></a>

### Polyphase decomposition

For a sequence x and a positive integer m, the phase r collects samples x_(mk+r), with 0 ≤ r < m. Interleaving all phases reconstructs the indexed sequence. Filtering requires additional boundary and convention choices.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Address](#address) · [Residue class](#residue-class) · [Reconstruction](#reconstruction)

<a id="residue-class"></a>

### Residue class

Integers with the same remainder modulo a positive integer m. Two integers belong to the same class when their difference is a multiple of m. Even and odd indices are the two classes modulo two.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Polyphase decomposition](#polyphase) · [Address](#address)

<a id="compatibility"></a>

### Compatibility

Agreement between specified maps, operations or levels of a construction. The relevant equality must be stated, such as a coarse projector equaling the sum of its fine children.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Commuting diagram](#commuting-diagram) · [Refinement](#refinement) · [Completion](#completion)

<a id="commuting-diagram"></a>

### Commuting diagram

A diagram in which the declared routes between the same starting and ending objects give the same map. In Example 3 the equality is D_y C = C D.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Composition](#composition) · [Compatibility](#compatibility) · [Intertwiner](#intertwiner)

<a id="reconstruction"></a>

### Reconstruction

Recovering an object from its representation under the stated identities. Exact reconstruction may use all packet components or a synthesis map. Dropping components generally introduces a residual.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Analysis and synthesis](#analysis-synthesis) · [Residual](#residual) · [Complete packet family](#complete-packet-family)

<a id="fiber"></a>

### Fiber

For a map R and an output s, the set of all inputs with R(x) = s. A proposed observation can be recovered from R(x) alone only if it is constant on each fiber.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean and code](LEARNING_MAP.md#obstructions) · [Kernel](#kernel) · [Factorization through a map](#factorization)

<a id="factorization"></a>

### Factorization through a map

Writing one map F as G composed with another map R, so F(x) = G(R(x)). This means the intermediate value R(x) contains enough information for the requested output F(x).

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Papers, proofs, Lean and code](LEARNING_MAP.md#obstructions) · [Fiber](#fiber) · [Obstruction](#obstruction) · [Composition](#composition)

<a id="lift"></a>

### Lift

An object at a finer or richer level that maps to a specified object at a coarser level. Existence, uniqueness and compatibility of lifts are separate questions.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#7-constrain) · [Refinement](#refinement) · [Compatibility](#compatibility) · [Obstruction](#obstruction)

<a id="conditional-expectation"></a>

### Finite conditional expectation

For positive weights and a finite partition, replace each value by its group’s weighted mean. The resulting map fixes group-constant vectors and is an orthogonal projector in the corresponding weighted inner product.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Papers, proofs, Lean and code](LEARNING_MAP.md#averages) · [Orthogonal projector](#orthogonal-projector) · [Inner product](#inner-product) · [Coarsening](#coarsening)

<a id="completion"></a>

### Completion

A construction that adds or realizes limits or missing structure under a specified mathematical definition. There is no single universal completion operation across the collection. A finite compatible tower does not by itself construct an infinite limit.

**Keep in mind:** Mathematical completion and the editorial completion stage of a paper are different uses of the word.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#8-complete) · [Compatibility](#compatibility) · [Lift](#lift)

<a id="haar-pair"></a>

### Haar pair

A two-sample transform that separates an average and a difference. The tutorial uses a = (u+v)/2 and d = (u−v)/2, with inverse (u,v) = (a+d,a−d). Other Haar normalizations use square roots.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#haar) · [Detail coefficient](#detail-coefficient) · [Normalization](#normalization) · [Refinement](#refinement)

<a id="detail-coefficient"></a>

### Detail coefficient

In the Haar pair example, the signed half-difference d = (u−v)/2. It records the information lost when the pair is replaced by its repeated average.

[Hand-worked example](examples/14_HAAR_PAIRS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#haar) · [Haar pair](#haar-pair) · [Residual](#residual)

<a id="repair-direction"></a>

### Repair direction

An allowed vector added to the span of the original image so that a required target can become reachable. Both the target equation and the permitted coefficient system must remain specified.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#repair-menus) · [Image](#image) · [Span](#span) · [Finite repair menu](#repair-menu)

<a id="free-repair"></a>

### Free linear repair

A repair problem allowing freely chosen added directions over the declared field. In the rational finite-dimensional setting, the minimum added dimension is the dimension of the span of the target residual classes in the original cokernel.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#repair-menus) · [Repair direction](#repair-direction) · [Cokernel](#cokernel) · [Dimension](#dimension)

<a id="repair-menu"></a>

### Finite repair menu

A supplied finite list of candidate directions, with costs and any selection restrictions. Feasibility and optimality are judged using this list and the original target equation.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#repair-menus) · [Repair direction](#repair-direction) · [Repair selection cost](#repair-cost) · [Feasibility](#feasibility)

<a id="repair-cost"></a>

### Repair selection cost

The declared cost of the selected repair choices. In the tutorial it is the sum of their selection costs, paid once per choice, independently of the rational coefficients used to combine them.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#repair-menus) · [Finite repair menu](#repair-menu) · [Free linear repair](#free-repair)

<a id="feasibility"></a>

### Feasibility

Existence of a solution satisfying the stated equations and admissibility conditions. Failure of one candidate or exhaustion of a search budget does not by itself show infeasibility.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#repair-menus) · [Hypothesis](#hypothesis) · [Obstruction](#obstruction) · [Certificate](#certificate)

<a id="dual-witness"></a>

### Linear obstruction witness

A linear functional that annihilates every allowed direction but has a nonzero value on the required target. It proves that this target lies outside their span under the stated linear problem.

[Hand-worked example](examples/25_REPAIR_MENUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#repair-menus) · [Linear map](#linear-map) · [Kernel](#kernel) · [Obstruction](#obstruction) · [Feasibility](#feasibility)

<a id="arithmetic-and-error"></a>

## Arithmetic and error

How exact values, stored approximations and error measures differ.

[Residual](#residual) · [Exact](#exact) · [Numerical](#numerical) · [Precision](#precision) · [Dyadic rational](#dyadic-rational) · [Rounding](#rounding) · [ULP](#ulp) · [Numerical ternary](#ternary) · [Tolerance](#tolerance) · [Integer congruence](#congruence) · [Coprime integers](#coprime) · [Modular inverse](#modular-inverse) · [Chinese remainder theorem](#chinese-remainder)

<a id="residual"></a>

### Residual

A discrepancy computed for a specified identity or reconstruction. In Example 5 it is r = x − x̂. Other operations may use a different sign or norm, so the definition belongs with the reported number.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Norm](#norm) · [Tolerance](#tolerance) · [Obstruction](#obstruction)

<a id="exact"></a>

### Exact

Computed or stated in exact algebra or arithmetic under the declared hypotheses. Exact rational arithmetic avoids rounding of those rational values. It does not establish an unchecked modeling assumption.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [Papers, proofs, Lean and code](LEARNING_MAP.md#coordinates) · [Numerical](#numerical) · [Hypothesis](#hypothesis) · [Dyadic rational](#dyadic-rational)

<a id="numerical"></a>

### Numerical

Computed with finite-precision arithmetic and interpreted using a stated error or residual rule. A zero observed floating-point residual does not turn the whole computation into an exact-arithmetic proof.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [Papers, proofs, Lean and code](LEARNING_MAP.md#rounding) · [Exact](#exact) · [Residual](#residual) · [Tolerance](#tolerance)

<a id="precision"></a>

### Precision

The capacity of a numerical representation. For the binary model here it is the number of significant binary digits, including the leading bit. More precision does not alone prove that an algorithm or its input is accurate.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#rounding) · [Rounding](#rounding) · [ULP](#ulp) · [Numerical](#numerical)

<a id="dyadic-rational"></a>

### Dyadic rational

A rational number expressible as an integer divided by a power of two. These are precisely the rational numbers with a finite binary expansion, apart from representation range limits.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#rounding) · [Exact](#exact) · [Rounding](#rounding)

<a id="rounding"></a>

### Rounding

Choosing a representable stored value for an exact value according to a specified rule. Nearest, ties to even chooses the closer value and resolves an exact midpoint by the parity of the last retained significand bit.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#rounding) · [Precision](#precision) · [ULP](#ulp) · [Numerical ternary](#ternary)

<a id="ulp"></a>

### ULP

A unit in the last retained place at a specified precision and exponent. In the three-bit example the spacing in [1, 2) is 1/4, while the spacing in [2, 4) is 1/2. It is not one fixed absolute distance.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#rounding) · [Precision](#precision) · [Rounding](#rounding)

<a id="ternary"></a>

### Numerical ternary

A numerical return whose sign compares the stored result with the exact value under the operation’s contract. Zero means exact, negative means below and positive means above. An error sentinel is not a numerical direction.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#rounding) · [Rounding](#rounding) · [Exact](#exact)

<a id="tolerance"></a>

### Tolerance

A declared threshold used by a numerical acceptance rule. Its units, scaling and comparison must match the residual being checked. A residual below tolerance is evidence within that rule, not exact equality in general.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Papers, proofs, Lean and code](LEARNING_MAP.md#refinement) · [Residual](#residual) · [Norm](#norm) · [Numerical](#numerical)

<a id="congruence"></a>

### Integer congruence

The relation a ≡ b modulo m means m divides a − b, with m a positive integer. It compares residue classes, not the ordinary sizes of a and b.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#modular) · [Residue class](#residue-class) · [Modular inverse](#modular-inverse)

<a id="coprime"></a>

### Coprime integers

Integers with greatest common divisor one. Pairwise coprime moduli give independent residue coordinates in the ordinary Chinese remainder theorem.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#modular) · [Chinese remainder theorem](#chinese-remainder) · [Integer congruence](#congruence)

<a id="modular-inverse"></a>

### Modular inverse

An integer b with ab ≡ 1 modulo m. For m greater than one, it exists exactly when a and m are coprime. The inverse is a residue class modulo m.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#modular) · [Integer congruence](#congruence) · [Coprime integers](#coprime)

<a id="chinese-remainder"></a>

### Chinese remainder theorem

For pairwise coprime positive moduli, a tuple of residues specifies exactly one residue class modulo their product. Selecting an integer representative requires an additional convention.

[Hand-worked example](examples/13_MODULAR_RECONSTRUCTION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#modular) · [Residue class](#residue-class) · [Coprime integers](#coprime) · [Reconstruction](#reconstruction)

<a id="claims-and-evidence"></a>

## Claims and evidence

How to read assumptions, proofs, formal links and computation records.

[Certificate](#certificate) · [Conditional](#conditional) · [Lean correspondence](#lean-correspondence) · [Hypothesis](#hypothesis) · [Theorem](#theorem) · [Proof](#proof) · [Heuristic](#heuristic) · [Finite check](#finite-check) · [Finite proof field](#proof-field) · [Admissible leaf](#admissible-leaf) · [Recorded inference rule](#inference-rule) · [Verification closure](#verification-closure) · [Inclusion-minimal certificate](#inclusion-minimal) · [Least certificate](#least-certificate) · [Minimum-cost certificate](#minimum-cost-certificate)

<a id="certificate"></a>

### Certificate

A structured report describing a particular check, with its evidence class, residuals and assumptions. The producer determines what was checked. A saved certificate describes a past calculation and needs revalidation for a new one.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Exact](#exact) · [Numerical](#numerical) · [Conditional](#conditional)

<a id="conditional"></a>

### Conditional

A result that retains explicitly listed assumptions. In a computation record, some of those assumptions may not have been established by the computation. Passing its checks does not discharge them.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Hypothesis](#hypothesis) · [Certificate](#certificate) · [Completion](#completion)

<a id="lean-correspondence"></a>

### Lean correspondence

A recorded connection between a written claim and a formal Lean statement. Compare hypotheses, the full formal type, source edition and execution record. A similar declaration name or a working link alone does not establish the correspondence.

[Further reading](COMPLETION_STATUS.md#lean-coverage) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Proof](#proof) · [Theorem](#theorem) · [Certificate](#certificate)

<a id="hypothesis"></a>

### Hypothesis

An assumption required by a statement or construction. It may describe the space, arithmetic, domain, regularity or supplied data. A conclusion applies only where its hypotheses hold.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](VERIFICATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#averages) · [Conditional](#conditional) · [Theorem](#theorem) · [Certificate](#certificate)

<a id="theorem"></a>

### Theorem

A mathematical statement established by a proof from its specified assumptions. A theorem may be conditional on explicit hypotheses, even when the implication itself is fully proved.

[Further reading](VERIFICATION.md) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Hypothesis](#hypothesis) · [Proof](#proof) · [Conditional](#conditional)

<a id="proof"></a>

### Proof

An argument establishing a statement from its hypotheses and accepted prior results. A worked input illustrates a statement. A general identity or argument is needed to establish a claim about every allowed input.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](VERIFICATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#obstructions) · [Theorem](#theorem) · [Finite check](#finite-check) · [Lean correspondence](#lean-correspondence)

<a id="heuristic"></a>

### Heuristic

A method for discovery, search or estimation without a complete guarantee for the claimed outcome. Its suggestions can lead to later proofs or checks, but the suggestions alone do not establish them.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [How to inspect a proof](routes/PROOF_REVIEW.md) · [Proof](#proof) · [Finite check](#finite-check)

<a id="finite-check"></a>

### Finite check

A check over specified, finitely many inputs or cases. Exhaustive checking can prove a claim about that finite domain. Sampling a larger domain does not establish the universal claim without an additional argument.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](VERIFICATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#packets) · [Proof](#proof) · [Certificate](#certificate) · [Hypothesis](#hypothesis)

<a id="proof-field"></a>

### Finite proof field

A declared finite collection of claim nodes, admissible leaves and recorded inference rules. Certificate validity is relative to this supplied system.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#proof-certificates) · [Recorded inference rule](#inference-rule) · [Admissible leaf](#admissible-leaf) · [Certificate](#certificate)

<a id="admissible-leaf"></a>

### Admissible leaf

A node allowed as a starting point under the declared proof-field contract. Selecting such a leaf does not require deriving it again inside that certificate.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#proof-certificates) · [Finite proof field](#proof-field) · [Hypothesis](#hypothesis)

<a id="inference-rule"></a>

### Recorded inference rule

A specified set of premise nodes together with a conclusion node. The certificate can use the rule only when the required premises have been derived and its recorded certification permits it.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#proof-certificates) · [Finite proof field](#proof-field) · [Verification closure](#verification-closure)

<a id="verification-closure"></a>

### Verification closure

The nodes obtainable by admitting selected admissible leaves and repeatedly applying the retained certified rules whose premises are available.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#proof-certificates) · [Admissible leaf](#admissible-leaf) · [Recorded inference rule](#inference-rule) · [Certificate](#certificate)

<a id="inclusion-minimal"></a>

### Inclusion-minimal certificate

A valid node-and-rule certificate with no valid strictly smaller subcertificate under componentwise inclusion. Several incomparable minimal certificates can exist.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#proof-certificates) · [Certificate](#certificate) · [Least certificate](#least-certificate) · [Minimum-cost certificate](#minimum-cost-certificate)

<a id="least-certificate"></a>

### Least certificate

A certificate contained componentwise in every certificate for the same request and rule system. This is stronger than being inclusion-minimal or having minimum numerical cost.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#proof-certificates) · [Inclusion-minimal certificate](#inclusion-minimal) · [Minimum-cost certificate](#minimum-cost-certificate)

<a id="minimum-cost-certificate"></a>

### Minimum-cost certificate

A valid certificate attaining the lowest declared total cost among the permitted certificates. Costs count selected items according to the supplied rule, so a shared premise need not be charged each time it is used.

[Hand-worked example](examples/21_PROOF_CERTIFICATES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#proof-certificates) · [Certificate](#certificate) · [Least certificate](#least-certificate) · [Finite proof field](#proof-field)

<a id="series-and-functions"></a>

## Series and cyclic functions

Coefficient operations and the distinction between a finite truncation and an infinite series.

[Coefficient](#coefficient) · [Power series](#power-series) · [Truncation](#truncation) · [Formal reciprocal](#formal-reciprocal) · [Coefficient convolution](#convolution) · [Root of unity](#root-of-unity) · [Derivative in the series example](#derivative) · [Differential equation](#differential-equation) · [Initial condition](#initial-condition) · [Contracted argument](#contracted-argument) · [Coefficient recurrence](#coefficient-recurrence)

<a id="coefficient"></a>

### Coefficient

The scalar multiplying a specified basis term. In f(z) = sum aₙzⁿ, aₙ is the coefficient of zⁿ.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#cyclic-reciprocals) · [Scalar](#scalar) · [Basis](#basis)

<a id="power-series"></a>

### Power series

An expression sum aₙzⁿ with infinitely many coefficient positions. A formal power series is manipulated through its coefficients. Evaluating it at a number additionally requires convergence.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#cyclic-reciprocals) · [Coefficient](#coefficient) · [Truncation](#truncation)

<a id="truncation"></a>

### Truncation

Keeping only specified degrees or levels. Equality modulo zᴺ means the coefficients of degrees below N agree. It need not be equality of the full functions or series.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#cyclic-reciprocals) · [Power series](#power-series) · [Residual](#residual)

<a id="formal-reciprocal"></a>

### Formal reciprocal

For a power series over a field with nonzero constant coefficient, the unique series whose product with it is one. Its coefficients are determined recursively. A finite truncation only verifies the corresponding finite set of coefficient identities.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#cyclic-reciprocals) · [Power series](#power-series) · [Coefficient convolution](#convolution) · [Field](#field)

<a id="convolution"></a>

### Coefficient convolution

The multiplication rule cₙ = sum from k=0 to n of aₖbₙ₋ₖ for ordinary power series. Each output coefficient is a finite sum, even when the series are infinite.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#cyclic-reciprocals) · [Coefficient](#coefficient) · [Power series](#power-series)

<a id="root-of-unity"></a>

### Root of unity

A complex number ω with ωᴺ = 1 for a positive integer N. It is primitive when N is its least positive such exponent. A weighted average over the powers of a primitive Nth root selects coefficients in one residue class modulo N.

[Hand-worked example](examples/16_CYCLIC_RECIPROCALS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#cyclic-reciprocals) · [Residue class](#residue-class) · [Packet](#packet)

<a id="derivative"></a>

### Derivative in the series example

For n≥1, differentiating a power-series term aₙzⁿ gives n aₙzⁿ⁻¹. Constant terms differentiate to zero. Formal differentiation acts on coefficients. An analytic interpretation uses the function’s convergence and differentiability conditions.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#contracted-feedback) · [Coefficient](#coefficient) · [Power series](#power-series)

<a id="differential-equation"></a>

### Differential equation

An equation relating an unknown function to one or more of its derivatives. The example also evaluates the same function at contracted arguments qz and rz.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#contracted-feedback) · [Derivative in the series example](#derivative) · [Initial condition](#initial-condition) · [Contracted argument](#contracted-argument)

<a id="initial-condition"></a>

### Initial condition

A specified value, or collection of derivative values, used with a differential equation. The feedback example fixes T(0)=0, and the equation then forces T′(0)=1.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#contracted-feedback) · [Differential equation](#differential-equation) · [Derivative in the series example](#derivative)

<a id="contracted-argument"></a>

### Contracted argument

Evaluation at qz with 0<q<1 in the feedback example. A term cₙzⁿ becomes cₙqⁿzⁿ after this substitution. The scaling is inside the defining equation.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#contracted-feedback) · [Coefficient](#coefficient) · [Differential equation](#differential-equation)

<a id="coefficient-recurrence"></a>

### Coefficient recurrence

A rule determining successive series coefficients from earlier ones. It gives exact finite calculations at each degree. Analytic convergence and bounds for a discarded tail require additional arguments.

[Hand-worked example](examples/24_CONTRACTED_FEEDBACK.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#contracted-feedback) · [Coefficient](#coefficient) · [Truncation](#truncation) · [Coefficient convolution](#convolution)

<a id="finite-quantum"></a>

## Finite quantum systems

States, measurement and channels on finite complex vector spaces.

[Complex conjugate](#complex-conjugate) · [Adjoint matrix](#adjoint) · [Unitary matrix](#unitary) · [Quantum amplitude](#amplitude) · [Density matrix](#density-matrix) · [Matrix trace](#trace) · [Born probability](#born-probability) · [Purity of a density matrix](#purity) · [Dephasing](#dephasing) · [Kraus operators](#kraus-operator) · [Hermitian matrix](#hermitian) · [Positive semidefinite matrix](#positive-semidefinite) · [Coherence in a chosen basis](#coherence)

<a id="complex-conjugate"></a>

### Complex conjugate

For real a and b, the conjugate of a+bi is a−bi. The squared modulus is (a+bi)(a−bi) = a²+b².

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Inner product](#inner-product) · [Scalar](#scalar)

<a id="adjoint"></a>

### Adjoint matrix

For a complex matrix in orthonormal bases, the adjoint A* is its conjugate transpose. In real orthonormal bases this is the ordinary transpose.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Complex conjugate](#complex-conjugate) · [Inner product](#inner-product)

<a id="unitary"></a>

### Unitary matrix

A complex square matrix U with U*U = UU* = I. It preserves the complex inner product and therefore vector norms.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Norm](#norm) · [Orthogonal matrix](#orthogonal-matrix)

<a id="amplitude"></a>

### Quantum amplitude

A complex coordinate of a normalized state vector in a chosen orthonormal basis. Its squared modulus gives that basis outcome’s probability. Relative phases can affect measurements in other bases.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Complex conjugate](#complex-conjugate) · [Born probability](#born-probability) · [Coordinates](#coordinates)

<a id="density-matrix"></a>

### Density matrix

A positive semidefinite Hermitian matrix with trace one. A normalized vector ψ gives the pure-state matrix ρ = ψψ*. Different vectors that differ only by an overall complex phase give the same density matrix.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Matrix trace](#trace) · [Purity of a density matrix](#purity)

<a id="trace"></a>

### Matrix trace

The sum of diagonal entries of a square matrix. It is unchanged by an invertible change of basis. Field trace is a related arithmetic construction with its own definition.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Matrix](#matrix) · [Field trace](#field-trace)

<a id="born-probability"></a>

### Born probability

For a density matrix ρ and an orthogonal measurement projector P, the outcome probability is tr(Pρ). A complete orthogonal projector family gives probabilities summing to one.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Matrix trace](#trace) · [Orthogonal projector](#orthogonal-projector)

<a id="purity"></a>

### Purity of a density matrix

The number tr(ρ²). For a finite density matrix it equals one exactly for a pure state and is smaller for a mixed state.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Matrix trace](#trace)

<a id="dephasing"></a>

### Dephasing

For a specified complete orthogonal family Pᵢ, the channel ρ ↦ sum PᵢρPᵢ removes coherence between different selected subspaces. Its effect depends on the chosen decomposition.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Projector](#projector) · [Kraus operators](#kraus-operator)

<a id="kraus-operator"></a>

### Kraus operators

Matrices Kᵢ describing a finite quantum channel by Φ(ρ) = sum KᵢρKᵢ*. The condition sum Kᵢ*Kᵢ = I makes this map trace preserving.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Density matrix](#density-matrix) · [Matrix trace](#trace)

<a id="hermitian"></a>

### Hermitian matrix

A complex square matrix A with A* = A. Its diagonal entries are real and opposite off-diagonal entries are complex conjugates. This condition alone does not imply positivity.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Adjoint matrix](#adjoint) · [Positive semidefinite matrix](#positive-semidefinite)

<a id="positive-semidefinite"></a>

### Positive semidefinite matrix

A Hermitian matrix A for which v*Av is nonnegative for every vector v. Zero eigenvalues are allowed.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Hermitian matrix](#hermitian) · [Eigenvalue](#eigenvalue) · [Density matrix](#density-matrix)

<a id="coherence"></a>

### Coherence in a chosen basis

Off-diagonal density-matrix entries that encode relations between different basis components. They can contribute to probabilities after a change of measurement basis.

[Hand-worked example](examples/17_QUANTUM_MEASUREMENT.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#quantum-measurement) · [Density matrix](#density-matrix) · [Dephasing](#dephasing) · [Quantum amplitude](#amplitude)

<a id="arithmetic-and-modules"></a>

## Arithmetic and modules

Finite fields, lift branches and the module data behind support.

[Prime power](#prime-power) · [Modular reduction](#modular-reduction) · [Lift branch](#lift-branch) · [Compatible tower](#compatible-tower) · [p-adic integer](#padic-integer) · [Survival to a finite level](#surviving-branch) · [Prime field](#prime-field) · [Extension field](#extension-field) · [Finite-field Frobenius](#frobenius) · [Field trace](#field-trace) · [Field norm](#field-norm) · [Irreducible polynomial](#irreducible-polynomial) · [Commutative ring with identity](#ring) · [Module](#module) · [Module presentation](#module-presentation) · [Cokernel](#cokernel) · [Module annihilator](#annihilator) · [Module support](#module-support) · [Zeroth Fitting ideal](#fitting-ideal) · [Multiplicity in the module example](#multiplicity) · [Ideal](#ideal) · [Prime ideal](#prime-ideal) · [Localization at a prime](#localization)

<a id="prime-power"></a>

### Prime power

An integer pⁿ with p prime and n a nonnegative integer. Successive positive powers give the moduli in the lift-branch example.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#lift-branches) · [Integer congruence](#congruence) · [Prime field](#prime-field)

<a id="modular-reduction"></a>

### Modular reduction

Passing from a residue class modulo pⁿ⁺¹ to its class modulo pⁿ. This map forgets the highest retained base-p digit.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#lift-branches) · [Prime power](#prime-power) · [Residue class](#residue-class) · [Coarsening](#coarsening)

<a id="lift-branch"></a>

### Lift branch

A sequence of solutions at successive levels whose reductions agree. A node at one finite level can have several children or no child.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#lift-branches) · [Lift](#lift) · [Modular reduction](#modular-reduction) · [Compatible tower](#compatible-tower)

<a id="compatible-tower"></a>

### Compatible tower

A collection of objects with specified maps between levels and stated compatibility identities. For modular solutions, the next residue must reduce to the preceding one.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#lift-branches) · [Compatibility](#compatibility) · [Modular reduction](#modular-reduction) · [Completion](#completion)

<a id="padic-integer"></a>

### p-adic integer

For a prime p, an element of the inverse limit of the residue rings modulo pⁿ. It specifies a compatible residue at every positive level. A finite list of residues is only a truncation of that data.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#lift-branches) · [Compatible tower](#compatible-tower) · [Prime power](#prime-power) · [Truncation](#truncation)

<a id="surviving-branch"></a>

### Survival to a finite level

A branch reaches the chosen last level without losing compatibility or the required equations. Survival to that level alone says nothing about the next one.

[Hand-worked example](examples/18_LIFT_BRANCHES.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#lift-branches) · [Lift branch](#lift-branch) · [Finite check](#finite-check)

<a id="prime-field"></a>

### Prime field

The smallest subfield of a field. In characteristic p it consists of the p scalar classes and is isomorphic to Fₚ. In characteristic zero it is isomorphic to the rational numbers.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#finite-frobenius) · [Field](#field) · [Integer congruence](#congruence)

<a id="extension-field"></a>

### Extension field

A field containing a specified smaller field. The extension degree is its vector-space dimension over that smaller field.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#finite-frobenius) · [Field](#field) · [Dimension](#dimension) · [Prime field](#prime-field)

<a id="frobenius"></a>

### Finite-field Frobenius

In a finite field of characteristic p, the map x ↦ xᵖ is an automorphism. Over F_q, the relative Frobenius is x ↦ x^q. The example uses q = p = 5.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#finite-frobenius) · [Extension field](#extension-field) · [Linear isomorphism](#isomorphism)

<a id="field-trace"></a>

### Field trace

For a finite field extension L/K, the trace of the K-linear map that multiplies L by an element a. In F₂₅/F₅ it is a+a⁵.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#finite-frobenius) · [Matrix trace](#trace) · [Extension field](#extension-field) · [Finite-field Frobenius](#frobenius)

<a id="field-norm"></a>

### Field norm

For a finite field extension L/K, the determinant of multiplication by an element a as a K-linear map. In F₂₅/F₅ it is a·a⁵. This norm is algebraic and is not a vector length.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#finite-frobenius) · [Determinant](#determinant) · [Extension field](#extension-field) · [Norm](#norm)

<a id="irreducible-polynomial"></a>

### Irreducible polynomial

A nonconstant polynomial over a field that cannot be factored into two polynomials of positive degree over that field. For degree two, irreducibility is equivalent to having no root in the field.

[Hand-worked example](examples/19_FINITE_FROBENIUS.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#finite-frobenius) · [Field](#field) · [Extension field](#extension-field)

<a id="ring"></a>

### Commutative ring with identity

A system with addition, subtraction and commutative multiplication satisfying the ring laws and having a multiplicative identity. A nonzero element need not have a multiplicative inverse.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Field](#field) · [Module](#module)

<a id="module"></a>

### Module

An abelian additive group with a scalar action by a ring satisfying the usual distributive, associative and identity laws. For a module over Q[t], multiplication by t can be specified by a Q-linear operator.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Commutative ring with identity](#ring) · [Operator algebra](#operator-algebra)

<a id="module-presentation"></a>

### Module presentation

A description of a module by generators and relations. A finite matrix A: Rᵐ → Rⁿ presents the quotient Rⁿ/im A.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Module](#module) · [Cokernel](#cokernel) · [Image](#image)

<a id="cokernel"></a>

### Cokernel

For a linear map or module map A: U → V, the quotient V/im A. It records target classes modulo those already reached by A.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Quotient space](#quotient-space) · [Image](#image) · [Module](#module)

<a id="annihilator"></a>

### Module annihilator

The ideal of ring elements that act as zero on every element of a module. For Q[t]/(tᵏ), the annihilator is the ideal (tᵏ).

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Module](#module) · [Nilpotent operator](#nilpotent) · [Commutative ring with identity](#ring)

<a id="module-support"></a>

### Module support

The prime ideals at which a module’s localization is nonzero. In the example Q[t]/(tᵏ), the support is the single prime ideal (t). The underlying support set does not determine k or the module.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Module](#module) · [Module annihilator](#annihilator) · [Multiplicity in the module example](#multiplicity)

<a id="fitting-ideal"></a>

### Zeroth Fitting ideal

For a finite presentation Rᵐ → Rⁿ → M → 0 over a commutative ring, the ideal generated by the n by n minors of the presentation matrix. In the one-generator example with relation tᵏ, it is (tᵏ).

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Module presentation](#module-presentation) · [Determinant](#determinant) · [Module support](#module-support)

<a id="multiplicity"></a>

### Multiplicity in the module example

For Q[t]/(tᵏ) supported at t=0, the integer k records the module’s length and its Q-vector-space dimension. This is additional data beyond the one-point support set. Other works use multiplicity with their own specified objects.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Dimension](#dimension) · [Module support](#module-support) · [Nilpotent operator](#nilpotent)

<a id="ideal"></a>

### Ideal

An additive subgroup of a commutative ring closed under multiplication by every element of the ring. The principal ideal (f) consists of all multiples of f.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Commutative ring with identity](#ring) · [Module annihilator](#annihilator)

<a id="prime-ideal"></a>

### Prime ideal

A proper ideal P such that ab in P implies a in P or b in P. The ideal (t) in Q[t] is prime because the quotient is the field Q.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Ideal](#ideal) · [Commutative ring with identity](#ring) · [Field](#field)

<a id="localization"></a>

### Localization at a prime

A construction that makes ring elements outside a chosen prime ideal invertible, and carries a module along with that scalar change. The prime lies in the module’s support exactly when the localized module is nonzero.

[Hand-worked example](examples/20_SUPPORT_AND_MULTIPLICITY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#support-multiplicity) · [Prime ideal](#prime-ideal) · [Module support](#module-support) · [Module](#module)

<a id="dynamics-and-calibration"></a>

## Dynamics, memory and calibration

What a retained state predicts and what exact observations determine.

[Visible state](#visible-state) · [Hidden state](#hidden-state) · [Prepared hidden initialization](#prepared-state) · [Discrete memory maps](#memory-kernel) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [State augmentation](#state-augmentation) · [Semigroup law for evolution maps](#semigroup-law) · [Exact operator calibration](#calibration) · [Calibration span](#calibration-span) · [Compatible model](#compatible-model) · [Linear extension](#linear-extension) · [Reusable calibrated core](#reusable-core) · [Identifiability relative to a model class](#identifiability)

<a id="visible-state"></a>

### Visible state

The state coordinates or summary retained for a specified prediction task. A visible value need not contain enough information to determine its own next value.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#hidden-memory) · [Hidden state](#hidden-state) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [Coarsening](#coarsening)

<a id="hidden-state"></a>

### Hidden state

The part of the declared full state omitted by the current observation or summary. It can influence later visible outputs even when it does not affect the current output.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#hidden-memory) · [Visible state](#visible-state) · [Discrete memory maps](#memory-kernel)

<a id="prepared-state"></a>

### Prepared hidden initialization

An initialization that fixes the hidden coordinates by a specified rule. The example uses R(y)=(y,0). Results for this preparation need not hold for arbitrary hidden starting values.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#hidden-memory) · [Hidden state](#hidden-state) · [Reconstruction](#reconstruction) · [Autonomous dynamics of a summary](#autonomous-dynamics)

<a id="memory-kernel"></a>

### Discrete memory maps

For the block update (y,z) ↦ (Ay+Bz,Gy+Dz), the maps Mₖ=BDᵏG describe a visible-to-hidden entry, k hidden transitions and a return. The first effect of Mₖ on prepared visible evolution occurs after k+2 full steps.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#hidden-memory) · [Block matrix](#block-matrix) · [Hidden state](#hidden-state) · [Prepared hidden initialization](#prepared-state)

<a id="autonomous-dynamics"></a>

### Autonomous dynamics of a summary

A transition rule determined by the retained current state, under the declared controls and initialization contract. For deterministic maps, full states with the same summary must have the same next summary.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#hidden-memory) · [Visible state](#visible-state) · [Fiber](#fiber) · [Factorization through a map](#factorization)

<a id="state-augmentation"></a>

### State augmentation

Enlarging a retained state with additional coordinates or history needed for future prediction. The hidden-memory example retains the previous visible value along with the current one.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#hidden-memory) · [Visible state](#visible-state) · [Hidden state](#hidden-state) · [Autonomous dynamics of a summary](#autonomous-dynamics)

<a id="semigroup-law"></a>

### Semigroup law for evolution maps

The identity Eₘ₊ₙ=EₘEₙ for nonnegative step counts, with E₀ the identity. It expresses agreement between uninterrupted evolution and successive uses of the same state-level evolution maps.

[Hand-worked example](examples/22_HIDDEN_MEMORY.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#hidden-memory) · [Composition](#composition) · [Identity operator](#identity) · [Prepared hidden initialization](#prepared-state)

<a id="calibration"></a>

### Exact operator calibration

Supplied input-output pairs for an unknown operation. For a linear operation, every linear relation among calibrated inputs must be respected by the supplied outputs.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#calibrated-continuation) · [Linear map](#linear-map) · [Calibration span](#calibration-span) · [Compatible model](#compatible-model)

<a id="calibration-span"></a>

### Calibration span

The span of the calibrated input vectors. Consistent exact linear calibration determines the operation on this span. Its outputs can leave that span.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#calibrated-continuation) · [Exact operator calibration](#calibration) · [Span](#span) · [Reusable calibrated core](#reusable-core)

<a id="compatible-model"></a>

### Compatible model

A model satisfying all supplied data and every declared structural assumption. In the calibration example, all linear extensions of the known restriction are allowed, and each model stays fixed through a trajectory.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#calibrated-continuation) · [Exact operator calibration](#calibration) · [Linear extension](#linear-extension) · [Identifiability relative to a model class](#identifiability)

<a id="linear-extension"></a>

### Linear extension

A linear map on a larger vector space that agrees with a given map on its original subspace. Values on an added basis can vary unless further conditions are imposed.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#calibrated-continuation) · [Linear map](#linear-map) · [Subspace](#subspace) · [Basis](#basis)

<a id="reusable-core"></a>

### Reusable calibrated core

For the tutorial’s unrestricted linear extension class and full-state output, the largest subspace inside the calibration span preserved by every calibrated operation. All finite operation sequences from this subspace are determined by the calibration.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#calibrated-continuation) · [Calibration span](#calibration-span) · [Invariant subspace](#invariant-subspace) · [Compatible model](#compatible-model)

<a id="identifiability"></a>

### Identifiability relative to a model class

A requested quantity is identifiable from the supplied data when every compatible model gives the same value. Identifying a particular output can require less information than identifying the whole model.

[Hand-worked example](examples/23_CALIBRATED_CONTINUATION.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#calibrated-continuation) · [Compatible model](#compatible-model) · [Exact operator calibration](#calibration) · [Obstruction](#obstruction)

<a id="inference-and-probability"></a>

## Inference and probability

The model, observation and Gaussian calculations used in the inference example.

[Finite-dimensional Gaussian model](#gaussian-model) · [Prior distribution](#prior) · [Likelihood](#likelihood) · [Posterior distribution](#posterior) · [Covariance matrix](#covariance) · [Precision matrix](#precision-matrix) · [Observation innovation](#innovation) · [Exact Gaussian gain](#gaussian-gain) · [Joseph covariance](#joseph-covariance)

<a id="gaussian-model"></a>

### Finite-dimensional Gaussian model

A model with a Gaussian state and specified linear observations with Gaussian noise. The tutorial supplies an independent noise variable, a prior mean and covariance, an observation matrix and a positive noise variance.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#gaussian-update) · [Prior distribution](#prior) · [Likelihood](#likelihood) · [Covariance matrix](#covariance)

<a id="prior"></a>

### Prior distribution

The state distribution specified before conditioning on the observation under the declared model. A Gaussian prior is described by its mean and covariance.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#gaussian-update) · [Finite-dimensional Gaussian model](#gaussian-model) · [Posterior distribution](#posterior) · [Covariance matrix](#covariance)

<a id="likelihood"></a>

### Likelihood

For a fixed observed value, the observation density viewed as a function of the proposed state or parameter. It is combined with the prior and normalized to obtain a posterior density when that density formula applies.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#gaussian-update) · [Prior distribution](#prior) · [Posterior distribution](#posterior) · [Finite-dimensional Gaussian model](#gaussian-model)

<a id="posterior"></a>

### Posterior distribution

The state distribution conditional on the observed data under the supplied prior and observation model. The tutorial computes the usual explicit Gaussian conditional density by completing the square.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#gaussian-update) · [Prior distribution](#prior) · [Likelihood](#likelihood) · [Exact Gaussian gain](#gaussian-gain)

<a id="covariance"></a>

### Covariance matrix

For a random vector X with mean m and finite second moments, the matrix E[(X−m)(X−m)ᵀ]. Its diagonal entries are variances. For a unit direction u, uᵀCu is the variance in that direction.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#gaussian-update) · [Positive semidefinite matrix](#positive-semidefinite) · [Finite-dimensional Gaussian model](#gaussian-model) · [Precision matrix](#precision-matrix)

<a id="precision-matrix"></a>

### Precision matrix

The inverse covariance when the covariance is invertible. In a nonsingular Gaussian density it appears in the quadratic exponent. This use of precision is distinct from the number of bits in stored arithmetic.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#gaussian-update) · [Covariance matrix](#covariance) · [Inverse](#inverse) · [Precision](#precision)

<a id="innovation"></a>

### Observation innovation

The difference d=y−Hm between an observation and its predicted mean in the linear model. Its covariance is S=HPHᵀ+R when the state covariance is P and the independent noise covariance is R.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#gaussian-update) · [Finite-dimensional Gaussian model](#gaussian-model) · [Covariance matrix](#covariance) · [Exact Gaussian gain](#gaussian-gain)

<a id="gaussian-gain"></a>

### Exact Gaussian gain

For the declared linear Gaussian model, K=PHᵀ(HPHᵀ+R)⁻¹. Multiplying the innovation by K gives the posterior mean correction. Positive noise covariance makes the displayed observation-space inverse exist.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#gaussian-update) · [Observation innovation](#innovation) · [Posterior distribution](#posterior) · [Joseph covariance](#joseph-covariance)

<a id="joseph-covariance"></a>

### Joseph covariance

For a gain B, the matrix (I−BH)P(I−BH)ᵀ+BRBᵀ. It is positive semidefinite for valid prior and noise covariances. At the exact gain it equals the posterior covariance. A general gain still needs its own accuracy check.

[Hand-worked example](examples/26_GAUSSIAN_UPDATE.md) · [Papers, proofs, Lean and code](LEARNING_MAP.md#gaussian-update) · [Covariance matrix](#covariance) · [Exact Gaussian gain](#gaussian-gain) · [Positive semidefinite matrix](#positive-semidefinite)

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

[Address](#address) · [Adjoint matrix](#adjoint) · [Admissible leaf](#admissible-leaf) · [Analysis and synthesis](#analysis-synthesis) · [Autonomous dynamics of a summary](#autonomous-dynamics) · [Basis](#basis) · [Block matrix](#block-matrix) · [Born probability](#born-probability) · [Calibration span](#calibration-span) · [Certificate](#certificate) · [Chinese remainder theorem](#chinese-remainder) · [Coarsening](#coarsening) · [Coefficient](#coefficient) · [Coefficient convolution](#convolution) · [Coefficient recurrence](#coefficient-recurrence) · [Coherence in a chosen basis](#coherence) · [Cokernel](#cokernel) · [Commutative ring with identity](#ring) · [Commutator](#commutator) · [Commuting diagram](#commuting-diagram) · [Compatibility](#compatibility) · [Compatible model](#compatible-model) · [Compatible tower](#compatible-tower) · [Complete packet family](#complete-packet-family) · [Completion](#completion) · [Complex conjugate](#complex-conjugate) · [Composition](#composition) · [Conditional](#conditional) · [Contracted argument](#contracted-argument) · [Coordinate change](#coordinate-change) · [Coordinates](#coordinates) · [Coprime integers](#coprime) · [Covariance matrix](#covariance) · [Cyclic vector](#cyclic) · [Density matrix](#density-matrix) · [Dephasing](#dephasing) · [Derivative in the series example](#derivative) · [Detail coefficient](#detail-coefficient) · [Determinant](#determinant) · [Diagonalizable operator](#diagonalizable) · [Differential equation](#differential-equation) · [Dimension](#dimension) · [Direct sum](#direct-sum) · [Discrete memory maps](#memory-kernel) · [Domain and codomain](#domain-codomain) · [Dyadic rational](#dyadic-rational) · [Eigenspace](#eigenspace) · [Eigenvalue](#eigenvalue) · [Eigenvector](#eigenvector) · [Elimination](#elimination) · [Exact](#exact) · [Exact Gaussian gain](#gaussian-gain) · [Exact operator calibration](#calibration) · [Extension field](#extension-field) · [Factorization through a map](#factorization) · [Feasibility](#feasibility) · [Fiber](#fiber) · [Field](#field) · [Field norm](#field-norm) · [Field trace](#field-trace) · [Finite check](#finite-check) · [Finite conditional expectation](#conditional-expectation) · [Finite proof field](#proof-field) · [Finite repair menu](#repair-menu) · [Finite-dimensional Gaussian model](#gaussian-model) · [Finite-field Frobenius](#frobenius) · [Formal reciprocal](#formal-reciprocal) · [Free linear repair](#free-repair) · [Haar pair](#haar-pair) · [Hermitian matrix](#hermitian) · [Heuristic](#heuristic) · [Hidden state](#hidden-state) · [Hypothesis](#hypothesis) · [Ideal](#ideal) · [Identifiability relative to a model class](#identifiability) · [Identity operator](#identity) · [Image](#image) · [Inclusion-minimal certificate](#inclusion-minimal) · [Initial condition](#initial-condition) · [Injective map](#injective) · [Inner product](#inner-product) · [Integer congruence](#congruence) · [Intertwiner](#intertwiner) · [Invariant subspace](#invariant-subspace) · [Inverse](#inverse) · [Irreducible polynomial](#irreducible-polynomial) · [Joseph covariance](#joseph-covariance) · [Kernel](#kernel) · [Kraus operators](#kraus-operator) · [Lean correspondence](#lean-correspondence) · [Least certificate](#least-certificate) · [Left inverse](#left-inverse) · [Lift](#lift) · [Lift branch](#lift-branch) · [Likelihood](#likelihood) · [Linear extension](#linear-extension) · [Linear independence](#linear-independence) · [Linear isomorphism](#isomorphism) · [Linear map](#linear-map) · [Linear obstruction witness](#dual-witness) · [Localization at a prime](#localization) · [Matrix](#matrix) · [Matrix trace](#trace) · [Minimal polynomial](#minimal-polynomial) · [Minimum-cost certificate](#minimum-cost-certificate) · [Modular inverse](#modular-inverse) · [Modular reduction](#modular-reduction) · [Module](#module) · [Module annihilator](#annihilator) · [Module presentation](#module-presentation) · [Module support](#module-support) · [Multiplicity in the module example](#multiplicity) · [Mutual annihilation](#mutual-annihilation) · [Nilpotent operator](#nilpotent) · [Norm](#norm) · [Normalization](#normalization) · [Nullity](#nullity) · [Numerical](#numerical) · [Numerical ternary](#ternary) · [Observation innovation](#innovation) · [Obstruction](#obstruction) · [Operator algebra](#operator-algebra) · [Operator conjugation](#conjugation) · [Operator relation](#relation) · [Orthogonal matrix](#orthogonal-matrix) · [Orthogonal projector](#orthogonal-projector) · [p-adic integer](#padic-integer) · [Packet](#packet) · [Polynomial in an operator](#polynomial-in-operator) · [Polyphase decomposition](#polyphase) · [Positive semidefinite matrix](#positive-semidefinite) · [Posterior distribution](#posterior) · [Power series](#power-series) · [Precision](#precision) · [Precision matrix](#precision-matrix) · [Prepared hidden initialization](#prepared-state) · [Prime field](#prime-field) · [Prime ideal](#prime-ideal) · [Prime power](#prime-power) · [Prior distribution](#prior) · [Projector](#projector) · [Proof](#proof) · [Purity of a density matrix](#purity) · [Quantum amplitude](#amplitude) · [Quotient space](#quotient-space) · [Rank](#rank) · [Rank–nullity identity](#rank-nullity) · [Realization](#realization) · [Reconstruction](#reconstruction) · [Recorded inference rule](#inference-rule) · [Redundant coordinates](#redundancy) · [Refinement](#refinement) · [Repair direction](#repair-direction) · [Repair selection cost](#repair-cost) · [Residual](#residual) · [Residue class](#residue-class) · [Reusable calibrated core](#reusable-core) · [Root of unity](#root-of-unity) · [Rounding](#rounding) · [Scalar](#scalar) · [Schur complement](#schur-complement) · [Seed](#seed) · [Seed rank](#seed-rank) · [Semigroup law for evolution maps](#semigroup-law) · [Span](#span) · [Spectral projector](#spectral-projector) · [State augmentation](#state-augmentation) · [Subspace](#subspace) · [Surjective map](#surjective) · [Survival to a finite level](#surviving-branch) · [Theorem](#theorem) · [Tolerance](#tolerance) · [Transfer block](#transfer-block) · [Truncation](#truncation) · [Typed path](#typed-path) · [Typed system](#typed-system) · [ULP](#ulp) · [Unitary matrix](#unitary) · [Vector](#vector) · [Vector space](#vector-space) · [Verification closure](#verification-closure) · [Visible state](#visible-state) · [Zeroth Fitting ideal](#fitting-ideal)

[Reading routes](READING_ROUTES.md) · [Hand-worked examples](HAND_WORKED_EXAMPLES.md) · [First runs](FIRST_RUN.md) · [Browse works](BROWSE.md)
