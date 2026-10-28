# Glossary and notation

This guide explains 69 terms used in the collection and its finite examples. Start with a subject below, use the [alphabetical index](#alphabetical-index), or look up [symbols](#symbols-in-the-introductory-example).

A word can have a more specific meaning in another paper. The paper’s definitions and hypotheses take precedence. Examples and source links provide context without changing any recorded evidence status.

[Work through the calculations by hand](HAND_WORKED_EXAMPLES.md) · [First software runs](FIRST_RUN.md)

- [Linear foundations](#linear-foundations)
- [Operators, seeds and packets](#operators-and-packets)
- [Coordinates and transfer](#coordinates-and-transfer)
- [Refinement and constraints](#refinement-and-constraints)
- [Arithmetic and error](#arithmetic-and-error)
- [Claims and evidence](#claims-and-evidence)

<a id="linear-foundations"></a>

## Linear foundations

The objects and notation used in the finite examples.

[Scalar](#scalar) · [Field](#field) · [Vector](#vector) · [Vector space](#vector-space) · [Linear map](#linear-map) · [Matrix](#matrix) · [Identity operator](#identity) · [Span](#span) · [Linear independence](#linear-independence) · [Basis](#basis) · [Dimension](#dimension) · [Kernel](#kernel) · [Image](#image) · [Rank](#rank) · [Inner product](#inner-product) · [Norm](#norm)

<a id="scalar"></a>

### Scalar

A number from the declared coefficient field, used to multiply vectors. The hand-worked matrix examples use real scalars and exact rational entries.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Field](#field) · [Vector](#vector)

<a id="field"></a>

### Field

A number system with addition, subtraction, multiplication and division by every nonzero element. The rational, real and complex numbers are examples. A result over one field does not automatically hold over another.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Scalar](#scalar)

<a id="vector"></a>

### Vector

An element of a vector space. In the finite examples it is a column of numbers. Its coordinates depend on a chosen representation.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Vector space](#vector-space) · [Coordinates](#coordinates)

<a id="vector-space"></a>

### Vector space

A collection of vectors closed under addition and scalar multiplication, with the usual distributive and associative laws. The space of pairs of real numbers is denoted R².

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Field](#field) · [Span](#span) · [Basis](#basis)

<a id="linear-map"></a>

### Linear map

A map T satisfying T(au + bv) = aT(u) + bT(v) for all vectors u, v and allowed scalars a, b. A linear map preserves linear combinations.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Matrix](#matrix) · [Kernel](#kernel) · [Image](#image)

<a id="matrix"></a>

### Matrix

A rectangular array representing a linear map after bases have been chosen. An m by n matrix takes n coordinates to m coordinates. Each output coordinate is a row multiplied by the input column.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Linear map](#linear-map) · [Basis](#basis) · [Composition](#composition)

<a id="identity"></a>

### Identity operator

The map I that leaves every input unchanged, so Ix = x. The subscript in I₂ or I₃ specifies the dimension when needed.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Inverse](#inverse) · [Complete packet family](#complete-packet-family)

<a id="span"></a>

### Span

All finite linear combinations of a specified set of vectors. The span of the empty set consists only of the zero vector. With an operator action, one may first apply allowed operators and then take the span.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Seed](#seed) · [Basis](#basis) · [Linear independence](#linear-independence)

<a id="linear-independence"></a>

### Linear independence

A family is linearly independent when the only linear combination giving zero has every coefficient zero. No member of a finite independent family can be formed from the others.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Span](#span) · [Basis](#basis)

<a id="basis"></a>

### Basis

A linearly independent spanning family. Every vector has a unique finite linear combination in that basis. Redundant measurements can describe a vector without forming a basis.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Span](#span) · [Linear independence](#linear-independence) · [Redundant coordinates](#redundancy)

<a id="dimension"></a>

### Dimension

The number of vectors in a basis of a finite-dimensional vector space. In these examples, R² has dimension two even when three redundant measurements are stored.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Basis](#basis) · [Rank](#rank) · [Seed rank](#seed-rank)

<a id="kernel"></a>

### Kernel

For a linear map T, the vectors sent to zero: ker T = {x : Tx = 0}. A nonzero kernel describes directions that this map cannot distinguish from zero.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Image](#image) · [Fiber](#fiber) · [Factorization through a map](#factorization)

<a id="image"></a>

### Image

The outputs actually attained by a map. For a linear map T, im T = {Tx : x is an allowed input} is a subspace of the target. The declared target can be larger than the image.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Kernel](#kernel) · [Rank](#rank) · [Left inverse](#left-inverse)

<a id="rank"></a>

### Rank

For a finite linear map, the dimension of its image. A matrix has full column rank when its columns are linearly independent, so it has no nonzero input in its kernel.

**Keep in mind:** Matrix rank and seed rank answer different questions.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Dimension](#dimension) · [Image](#image) · [Seed rank](#seed-rank)

<a id="inner-product"></a>

### Inner product

For real vector spaces, a symmetric bilinear pairing with ⟨v,v⟩ > 0 for every nonzero v. It defines lengths and angles. Positive weights give the pairing sum_i w_i u_i v_i. Complex inner products use conjugate symmetry and conjugate linearity in one argument.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Norm](#norm) · [Orthogonal projector](#orthogonal-projector)

<a id="norm"></a>

### Norm

A nonnegative measure of size that is zero only at the zero vector, scales by the absolute value of a scalar and satisfies the triangle inequality. The Euclidean norm is the square root of the sum of squared coordinates.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Inner product](#inner-product) · [Residual](#residual) · [Tolerance](#tolerance)

<a id="operators-and-packets"></a>

## Operators, seeds and packets

How an allowed action generates, selects and decomposes objects.

[Realization](#realization) · [Seed](#seed) · [Address](#address) · [Projector](#projector) · [Packet](#packet) · [Typed system](#typed-system) · [Operator algebra](#operator-algebra) · [Seed rank](#seed-rank) · [Cyclic vector](#cyclic) · [Orthogonal projector](#orthogonal-projector) · [Complete packet family](#complete-packet-family) · [Mutual annihilation](#mutual-annihilation) · [Invariant subspace](#invariant-subspace)

<a id="realization"></a>

### Realization

A way to represent a declared system using concrete spaces and operations while respecting its required relations. A finite matrix realization assigns a space to each type and a matrix to each permitted arrow.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate) · [Typed system](#typed-system) · [Operator algebra](#operator-algebra) · [Compatibility](#compatibility)

<a id="seed"></a>

### Seed

Initial generating data from which the allowed operator action produces further elements. Whether a seed is sufficient depends on both the object and the declared action.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Span](#span) · [Seed rank](#seed-rank) · [Cyclic vector](#cyclic)

<a id="address"></a>

### Address

A label for a legal operator path or a packet coordinate. Examples include signal phases, residue classes and positions in a packet tree. An address identifies a location in a representation, not necessarily a physical location.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Typed system](#typed-system) · [Packet](#packet) · [Residue class](#residue-class)

<a id="projector"></a>

### Projector

A linear operator P satisfying P² = P. Applying it twice has the same effect as applying it once. This algebraic definition does not require orthogonality.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors) · [Orthogonal projector](#orthogonal-projector) · [Packet](#packet) · [Redundant coordinates](#redundancy)

<a id="packet"></a>

### Packet

In the finite projector example, a selected component Pᵢx or the subspace in which it lies, according to context. Signal, algebraic and arithmetic works may assign the word more specific meanings.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Projector](#projector) · [Complete packet family](#complete-packet-family) · [Address](#address)

<a id="typed-system"></a>

### Typed system

A system that records which objects an operation accepts and returns. A path of operations is legal only when consecutive input and output types agree. Types are part of the mathematical specification.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#typed-finite-expressions) · [Linear map](#linear-map) · [Composition](#composition) · [Realization](#realization)

<a id="operator-algebra"></a>

### Operator algebra

In the finite linear setting, a collection of linear operators closed under sums, scalar multiples and composition. When a unital algebra is intended, the identity operator is included.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate) · [Composition](#composition) · [Seed](#seed) · [Invariant subspace](#invariant-subspace)

<a id="seed-rank"></a>

### Seed rank

In the finite linear example, the least number of seeds whose operator-generated span is the whole space. More general definitions can involve modules, dense generation and cardinalities. Read the definition in the chosen work.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Seed](#seed) · [Span](#span) · [Rank](#rank)

<a id="cyclic"></a>

### Cyclic vector

For a single linear operator T, a vector v is cyclic when v, Tv, T²v and further iterates span the space under consideration. One cyclic vector is enough to generate that operator module.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Seed](#seed) · [Span](#span)

<a id="orthogonal-projector"></a>

### Orthogonal projector

A projector onto a subspace whose residual x − Px is perpendicular to that subspace in the specified inner product. In ordinary real Euclidean coordinates its matrix is symmetric as well as idempotent.

**Keep in mind:** Orthogonality depends on the inner product. Weighted averaging need not have a symmetric matrix in ordinary coordinates.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Projector](#projector) · [Inner product](#inner-product)

<a id="complete-packet-family"></a>

### Complete packet family

In these finite examples, projectors Pᵢ with PᵢPⱼ = 0 for distinct indices and sum_i Pᵢ = I. These identities decompose every vector as x = sum_i Pᵢx.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Projector](#projector) · [Mutual annihilation](#mutual-annihilation) · [Reconstruction](#reconstruction)

<a id="mutual-annihilation"></a>

### Mutual annihilation

The relation PᵢPⱼ = 0 whenever i and j differ. Applying one selection after a different selection gives zero. For a pair of projectors, both orders must be checked.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction) · [Projector](#projector) · [Complete packet family](#complete-packet-family)

<a id="invariant-subspace"></a>

### Invariant subspace

A subspace W preserved by an operator T, meaning T(W) is contained in W. Preservation does not require T to act as the identity on W.

[Hand-worked example](examples/02_SEEDS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed) · [Span](#span) · [Operator algebra](#operator-algebra)

<a id="coordinates-and-transfer"></a>

## Coordinates and transfer

How descriptions change and operations move between components.

[Coordinates](#coordinates) · [Analysis and synthesis](#analysis-synthesis) · [Transfer block](#transfer-block) · [Coordinate change](#coordinate-change) · [Inverse](#inverse) · [Left inverse](#left-inverse) · [Redundant coordinates](#redundancy) · [Composition](#composition) · [Operator conjugation](#conjugation) · [Intertwiner](#intertwiner)

<a id="coordinates"></a>

### Coordinates

Values describing an object relative to a chosen representation. Coordinates can be unique basis coefficients or redundant measurements, depending on the setup.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Basis](#basis) · [Coordinate change](#coordinate-change) · [Redundant coordinates](#redundancy)

<a id="analysis-synthesis"></a>

### Analysis and synthesis

Analysis sends an object to coordinates. Synthesis returns an object from coordinates. In the finite model, A analyzes and S synthesizes, and exact reconstruction is the identity SA = I.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Left inverse](#left-inverse) · [Coordinates](#coordinates) · [Reconstruction](#reconstruction)

<a id="transfer-block"></a>

### Transfer block

The part of an operation connecting a source component to a target component. With source projector Pᵢ, target projector Qⱼ and operator T, the block is QⱼTPᵢ. Complete source and target families allow the blocks to reconstruct T.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Projector](#projector) · [Composition](#composition) · [Reconstruction](#reconstruction)

<a id="coordinate-change"></a>

### Coordinate change

A transformation between descriptions of the same object. In the invertible linear example the convention is y = Cx, so x = C⁻¹y. Keeping track of the direction prevents inverse formulas from being swapped.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Coordinates](#coordinates) · [Inverse](#inverse) · [Operator conjugation](#conjugation)

<a id="inverse"></a>

### Inverse

A map that undoes another map in both directions. For a square invertible matrix C, the inverse satisfies C⁻¹C = CC⁻¹ = I.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases) · [Identity operator](#identity) · [Left inverse](#left-inverse)

<a id="left-inverse"></a>

### Left inverse

For A mapping an input space to a coordinate space, S is a left inverse when SA = I on the input space. This gives exact reconstruction of analyzed inputs. It does not imply AS = I on the entire coordinate space.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Inverse](#inverse) · [Analysis and synthesis](#analysis-synthesis) · [Image](#image)

<a id="redundancy"></a>

### Redundant coordinates

A representation containing more coordinate entries than are needed for a basis description. Valid coordinate lists can satisfy relations, such as a third measurement being the sum of the first two.

**Keep in mind:** The reconstruction components SEᵢA can sum to the identity without being projectors.

[Hand-worked example](examples/06_REDUNDANT_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors) · [Basis](#basis) · [Analysis and synthesis](#analysis-synthesis) · [Projector](#projector)

<a id="composition"></a>

### Composition

Applying one map after another. In a matrix product UT, T acts first and U acts second. The intermediate dimensions or types must agree.

[Hand-worked example](examples/04_TRANSFER.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#typed-finite-expressions) · [Typed system](#typed-system) · [Matrix](#matrix) · [Transfer block](#transfer-block)

<a id="conjugation"></a>

### Operator conjugation

The change in an operator matrix under an invertible coordinate change. With y = Cx and original operator T, the new matrix is CTC⁻¹. This usage is distinct from complex conjugation.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Coordinate change](#coordinate-change) · [Intertwiner](#intertwiner)

<a id="intertwiner"></a>

### Intertwiner

A linear map C connecting operators T and U by CT = UC. Applying T and then C agrees with applying C and then U. An intertwiner need not be invertible.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Operator conjugation](#conjugation) · [Commuting diagram](#commuting-diagram)

<a id="refinement-and-constraints"></a>

## Refinement and constraints

How descriptions become finer, discard information or meet a compatibility condition.

[Refinement](#refinement) · [Obstruction](#obstruction) · [Coarsening](#coarsening) · [Polyphase decomposition](#polyphase) · [Residue class](#residue-class) · [Compatibility](#compatibility) · [Commuting diagram](#commuting-diagram) · [Reconstruction](#reconstruction) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Lift](#lift) · [Finite conditional expectation](#conditional-expectation) · [Completion](#completion)

<a id="refinement"></a>

### Refinement

A compatible move from a coarser description to a finer one. In finite packet refinement, each fine packet has a coarse parent and each coarse projector is the sum of its children.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Coarsening](#coarsening) · [Compatibility](#compatibility) · [Residue class](#residue-class)

<a id="obstruction"></a>

### Obstruction

An identified reason a requested construction cannot meet its stated conditions. In the recovery example, two inputs have the same coarse value but require different answers, so no recovery function from that value alone exists.

**Keep in mind:** A nonzero numerical residual is not automatically a proof that every possible construction fails.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Fiber](#fiber) · [Factorization through a map](#factorization) · [Residual](#residual)

<a id="coarsening"></a>

### Coarsening

Passing to a description that groups or forgets distinctions. Combining fine packets can recover a coarse packet, while discarding the fine values can prevent later reconstruction.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Refinement](#refinement) · [Obstruction](#obstruction) · [Fiber](#fiber)

<a id="polyphase"></a>

### Polyphase decomposition

For a sequence x and a positive integer m, the phase r collects samples x_(mk+r), with 0 ≤ r < m. Interleaving all phases reconstructs the indexed sequence. Filtering requires additional boundary and convention choices.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Address](#address) · [Residue class](#residue-class) · [Reconstruction](#reconstruction)

<a id="residue-class"></a>

### Residue class

Integers with the same remainder modulo a positive integer m. Two integers belong to the same class when their difference is a multiple of m. Even and odd indices are the two classes modulo two.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization) · [Polyphase decomposition](#polyphase) · [Address](#address)

<a id="compatibility"></a>

### Compatibility

Agreement between specified maps, operations or levels of a construction. The relevant equality must be stated, such as a coarse projector equaling the sum of its fine children.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine) · [Commuting diagram](#commuting-diagram) · [Refinement](#refinement) · [Completion](#completion)

<a id="commuting-diagram"></a>

### Commuting diagram

A diagram in which the declared routes between the same starting and ending objects give the same map. In Example 3 the equality is D_y C = C D.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport) · [Composition](#composition) · [Compatibility](#compatibility) · [Intertwiner](#intertwiner)

<a id="reconstruction"></a>

### Reconstruction

Recovering an object from its representation under the stated identities. Exact reconstruction may use all packet components or a synthesis map. Dropping components generally introduces a residual.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition) · [Analysis and synthesis](#analysis-synthesis) · [Residual](#residual) · [Complete packet family](#complete-packet-family)

<a id="fiber"></a>

### Fiber

For a map R and an output s, the set of all inputs with R(x) = s. A proposed observation can be recovered from R(x) alone only if it is constant on each fiber.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Kernel](#kernel) · [Factorization through a map](#factorization)

<a id="factorization"></a>

### Factorization through a map

Writing one map F as G composed with another map R, so F(x) = G(R(x)). This means the intermediate value R(x) contains enough information for the requested output F(x).

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion) · [Fiber](#fiber) · [Obstruction](#obstruction) · [Composition](#composition)

<a id="lift"></a>

### Lift

An object at a finer or richer level that maps to a specified object at a coarser level. Existence, uniqueness and compatibility of lifts are separate questions.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#7-constrain) · [Refinement](#refinement) · [Compatibility](#compatibility) · [Obstruction](#obstruction)

<a id="conditional-expectation"></a>

### Finite conditional expectation

For positive weights and a finite partition, replace each value by its group’s weighted mean. The resulting map fixes group-constant vectors and is an orthogonal projector in the corresponding weighted inner product.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#4-project) · [Orthogonal projector](#orthogonal-projector) · [Inner product](#inner-product) · [Coarsening](#coarsening)

<a id="completion"></a>

### Completion

A construction that adds or realizes limits or missing structure under a specified mathematical definition. There is no single universal completion operation across the collection. A finite compatible tower does not by itself construct an infinite limit.

**Keep in mind:** Mathematical completion and the editorial completion stage of a paper are different uses of the word.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#8-complete) · [Compatibility](#compatibility) · [Lift](#lift)

<a id="arithmetic-and-error"></a>

## Arithmetic and error

How exact values, stored approximations and error measures differ.

[Residual](#residual) · [Exact](#exact) · [Numerical](#numerical) · [Precision](#precision) · [Dyadic rational](#dyadic-rational) · [Rounding](#rounding) · [ULP](#ulp) · [Numerical ternary](#ternary) · [Tolerance](#tolerance)

<a id="residual"></a>

### Residual

A discrepancy computed for a specified identity or reconstruction. In Example 5 it is r = x − x̂. Other operations may use a different sign or norm, so the definition belongs with the reported number.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Norm](#norm) · [Tolerance](#tolerance) · [Obstruction](#obstruction)

<a id="exact"></a>

### Exact

Computed or stated in exact algebra or arithmetic under the declared hypotheses. Exact rational arithmetic avoids rounding of those rational values. It does not establish an unchecked modeling assumption.

[Hand-worked example](examples/03_COORDINATES.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [Numerical](#numerical) · [Hypothesis](#hypothesis) · [Dyadic rational](#dyadic-rational)

<a id="numerical"></a>

### Numerical

Computed with finite-precision arithmetic and interpreted using a stated error or residual rule. A zero observed floating-point residual does not turn the whole computation into an exact-arithmetic proof.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [Exact](#exact) · [Residual](#residual) · [Tolerance](#tolerance)

<a id="precision"></a>

### Precision

The capacity of a numerical representation. For the binary model here it is the number of significant binary digits, including the leading bit. More precision does not alone prove that an algorithm or its input is accurate.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Rounding](#rounding) · [ULP](#ulp) · [Numerical](#numerical)

<a id="dyadic-rational"></a>

### Dyadic rational

A rational number expressible as an integer divided by a power of two. These are precisely the rational numbers with a finite binary expansion, apart from representation range limits.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Exact](#exact) · [Rounding](#rounding)

<a id="rounding"></a>

### Rounding

Choosing a representable stored value for an exact value according to a specified rule. Nearest, ties to even chooses the closer value and resolves an exact midpoint by the parity of the last retained significand bit.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Precision](#precision) · [ULP](#ulp) · [Numerical ternary](#ternary)

<a id="ulp"></a>

### ULP

A unit in the last retained place at a specified precision and exponent. In the three-bit example the spacing in [1, 2) is 1/4, while the spacing in [2, 4) is 1/2. It is not one fixed absolute distance.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Precision](#precision) · [Rounding](#rounding)

<a id="ternary"></a>

### Numerical ternary

A numerical return whose sign compares the stored result with the exact value under the operation’s contract. Zero means exact, negative means below and positive means above. An error sentinel is not a numerical direction.

[Hand-worked example](examples/09_BINARY_ROUNDING.md) · [Further reading](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/glossary.md) · [Rounding](#rounding) · [Exact](#exact)

<a id="tolerance"></a>

### Tolerance

A declared threshold used by a numerical acceptance rule. Its units, scaling and comparison must match the residual being checked. A residual below tolerance is evidence within that rule, not exact equality in general.

[Hand-worked example](examples/05_REFINEMENT.md) · [Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Residual](#residual) · [Norm](#norm) · [Numerical](#numerical)

<a id="claims-and-evidence"></a>

## Claims and evidence

How to read assumptions, proofs, formal links and computation records.

[Certificate](#certificate) · [Conditional](#conditional) · [Lean correspondence](#lean-correspondence) · [Hypothesis](#hypothesis) · [Theorem](#theorem) · [Proof](#proof) · [Heuristic](#heuristic) · [Finite check](#finite-check)

<a id="certificate"></a>

### Certificate

A structured report describing a particular check, with its evidence class, residuals and assumptions. The producer determines what was checked. A saved certificate describes a past calculation and needs revalidation for a new one.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Exact](#exact) · [Numerical](#numerical) · [Conditional](#conditional)

<a id="conditional"></a>

### Conditional

A result that retains explicitly listed assumptions. In a computation record, some of those assumptions may not have been established by the computation. Passing its checks does not discharge them.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence) · [Hypothesis](#hypothesis) · [Certificate](#certificate) · [Completion](#completion)

<a id="lean-correspondence"></a>

### Lean correspondence

A recorded connection between a written claim and a formal Lean statement. Compare hypotheses, the full formal type, source edition and execution record. A similar declaration name or a working link alone does not establish the correspondence.

[Further reading](COMPLETION_STATUS.md#lean-coverage) · [Proof](#proof) · [Theorem](#theorem) · [Certificate](#certificate)

<a id="hypothesis"></a>

### Hypothesis

An assumption required by a statement or construction. It may describe the space, arithmetic, domain, regularity or supplied data. A conclusion applies only where its hypotheses hold.

[Hand-worked example](examples/08_WEIGHTED_AVERAGES.md) · [Further reading](VERIFICATION.md) · [Conditional](#conditional) · [Theorem](#theorem) · [Certificate](#certificate)

<a id="theorem"></a>

### Theorem

A mathematical statement established by a proof from its specified assumptions. A theorem may be conditional on explicit hypotheses, even when the implication itself is fully proved.

[Further reading](VERIFICATION.md) · [Hypothesis](#hypothesis) · [Proof](#proof) · [Conditional](#conditional)

<a id="proof"></a>

### Proof

An argument establishing a statement from its hypotheses and accepted prior results. A worked input illustrates a statement. A general identity or argument is needed to establish a claim about every allowed input.

[Hand-worked example](examples/07_OBSTRUCTIONS.md) · [Further reading](VERIFICATION.md) · [Theorem](#theorem) · [Finite check](#finite-check) · [Lean correspondence](#lean-correspondence)

<a id="heuristic"></a>

### Heuristic

A method for discovery, search or estimation without a complete guarantee for the claimed outcome. Its suggestions can lead to later proofs or checks, but the suggestions alone do not establish them.

[Further reading](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes) · [Proof](#proof) · [Finite check](#finite-check)

<a id="finite-check"></a>

### Finite check

A check over specified, finitely many inputs or cases. Exhaustive checking can prove a claim about that finite domain. Sampling a larger domain does not establish the universal claim without an additional argument.

[Hand-worked example](examples/01_PACKETS.md) · [Further reading](VERIFICATION.md) · [Proof](#proof) · [Certificate](#certificate) · [Hypothesis](#hypothesis)

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

[Address](#address) · [Analysis and synthesis](#analysis-synthesis) · [Basis](#basis) · [Certificate](#certificate) · [Coarsening](#coarsening) · [Commuting diagram](#commuting-diagram) · [Compatibility](#compatibility) · [Complete packet family](#complete-packet-family) · [Completion](#completion) · [Composition](#composition) · [Conditional](#conditional) · [Coordinate change](#coordinate-change) · [Coordinates](#coordinates) · [Cyclic vector](#cyclic) · [Dimension](#dimension) · [Dyadic rational](#dyadic-rational) · [Exact](#exact) · [Factorization through a map](#factorization) · [Fiber](#fiber) · [Field](#field) · [Finite check](#finite-check) · [Finite conditional expectation](#conditional-expectation) · [Heuristic](#heuristic) · [Hypothesis](#hypothesis) · [Identity operator](#identity) · [Image](#image) · [Inner product](#inner-product) · [Intertwiner](#intertwiner) · [Invariant subspace](#invariant-subspace) · [Inverse](#inverse) · [Kernel](#kernel) · [Lean correspondence](#lean-correspondence) · [Left inverse](#left-inverse) · [Lift](#lift) · [Linear independence](#linear-independence) · [Linear map](#linear-map) · [Matrix](#matrix) · [Mutual annihilation](#mutual-annihilation) · [Norm](#norm) · [Numerical](#numerical) · [Numerical ternary](#ternary) · [Obstruction](#obstruction) · [Operator algebra](#operator-algebra) · [Operator conjugation](#conjugation) · [Orthogonal projector](#orthogonal-projector) · [Packet](#packet) · [Polyphase decomposition](#polyphase) · [Precision](#precision) · [Projector](#projector) · [Proof](#proof) · [Rank](#rank) · [Realization](#realization) · [Reconstruction](#reconstruction) · [Redundant coordinates](#redundancy) · [Refinement](#refinement) · [Residual](#residual) · [Residue class](#residue-class) · [Rounding](#rounding) · [Scalar](#scalar) · [Seed](#seed) · [Seed rank](#seed-rank) · [Span](#span) · [Theorem](#theorem) · [Tolerance](#tolerance) · [Transfer block](#transfer-block) · [Typed system](#typed-system) · [ULP](#ulp) · [Vector](#vector) · [Vector space](#vector-space)

[Reading routes](READING_ROUTES.md) · [Hand-worked examples](HAND_WORKED_EXAMPLES.md) · [First runs](FIRST_RUN.md) · [Browse works](BROWSE.md)
