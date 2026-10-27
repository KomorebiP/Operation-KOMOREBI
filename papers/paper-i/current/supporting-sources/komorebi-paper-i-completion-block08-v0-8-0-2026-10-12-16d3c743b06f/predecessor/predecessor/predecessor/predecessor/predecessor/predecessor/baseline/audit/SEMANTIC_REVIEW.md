# Paper I: semantic and assumption audit

Date: 10 October 2026  
Scope: the preserved formal component v1.0.2 and its normative 35-row contract.

This review compares the actual elaborated types of all 84 mapped declarations with the contract and inspects the defining objects and load-bearing proof routes. It is separate from compiler acceptance and same-kernel replay. It is not an independently formalized second development, an independent novelty review, or certification of every statement in the expanded 108-record monograph.

The complete declaration-by-declaration source and compiler-log locators are in `DECLARATION_CROSSWALK.md` and `DECLARATION_CROSSWALK.json`. The untouched normative wording is in `../source/main/LEAN_THEOREM_MAP_v1.0.2.md`. The fresh signature log is `../evidence/fresh_main_retry/mapped_declarations.log`.

## 1. Generation and seed rank: rows 1–9

`Generates A M S` means that the actual submodule span of S is the top submodule. `seedRank A M` is Mathlib's cardinal span rank of that top submodule. It is not a user-provided integer, a metadata field, or a renamed assertion that the desired number is correct. `seedFinrank` is the natural-valued companion. The least finite free-surjection result explicitly requires `Module.Finite`.

The one-seed map is the literal action map a ↦ a • s. Its kernel quotient is identified with its actual range by a linear equivalence. The glue theorem identifies the image of the quotient class. The multiseed map uses finitely supported coefficients and their actual linear combination. The ring and additive-group assumptions needed for the quotient constructions remain visible in the source and elaborated signatures. The more general singleton-generation equivalence is over a semiring and an additive commutative monoid.

The zero-module endpoint is not folded into the nontrivial cyclic-rank-one theorem. Surjective semilinear quotient transport gives an inequality, not an automatic equality. Image-algebra invariance restricts to the actual range algebra of the algebra homomorphism. It does not silently replace that range by the full codomain algebra.

Rows 6 and 7 use different actions. A shared diagonal action gives a sum upper bound. Independent actions of a product algebra give the maximum formula. Row 8 uses the algebraic tensor product with explicit module, scalar-tower, and commuting-action hypotheses. No completed tensor product is substituted. Row 9 requires a quotient whose action factors through a specified scalar character. A general quotient is not assigned the same dimension obstruction.

Finding: the foundational objects and action types match the stated contract. No source repair was required.

## 2. Multiplicity and cyclicity: rows 10–14

The full-matrix and multiplicity results concern genuine matrix actions. The rank estimate is grounded in row spans and dimension bounds. Positive block size is essential for the ceiling-division formula. The full natural matrix module has rank one when its dimension is positive; the proof that every nonzero vector generates uses the actual matrix action.

The abstract split-semisimple transport theorem accepts an algebra equivalence to a product of full matrix algebras and a compatible semilinear module equivalence. It then transports the proved concrete rank formula. It does not construct a Wedderburn decomposition or prove the nonsplit division-algebra formula. See `SemisimpleCompletion.lean`, especially the supplied-equivalence theorem at lines 343–361.

The primary single-operator theorem has substantive upper and lower hypotheses. Joint generation and polynomial extraction from padded seeds supply the upper construction. Surjective scalar quotient maps with polynomial-evaluation intertwining supply the lower bound. The bridge to `seedRank` and `seedFinrank` uses the genuine operator algebra `Algebra.adjoin k {T}`. It is not a free algebra substituted without accounting for its action kernel.

The cyclic-matrix equivalence has a particularly important boundary. Its `hLeast` input supplies the exact positive seed-number certificate. Its `hgeometric_eq_blocks` input supplies the identification of geometric and block multiplicities. Its `hpoly` input already supplies the minpoly/charpoly canonical-form equivalence. The final component of the proof is `hpoly.symm`. Thus this declaration is a checked assembly of the displayed implications, not an independent Lean derivation of the canonical-form bridge for an arbitrary matrix. This is consistent with the current contract, which explicitly records the bridges as supplied inputs. See `SingleOperatorGraph.lean`, lines 600–631.

Finding: rows 10, 13, and 14 are valid at their certificate-explicit scopes. A bare “Lean proved the general classification theorem” description would be inaccurate.

## 3. Packets and transfer blocks: rows 15–25

The packet carrier is the independently defined dependent product of the actual ranges of the supplied projectors. Analysis applies the projectors. Synthesis forms a finite sum. Completeness proves synthesis-after-analysis. Idempotence and pairwise annihilation prove analysis-after-synthesis on range elements. The carrier is not defined as the image of analysis merely to make the inverse laws tautological.

The packetwise equality result retains completeness and a finite family. The topological constructions use continuous linear maps. The range-closure theorem is stronger than an invariance-only formulation: for a bounded idempotent and a dense submodule, closure of the image equals the full range without requiring that dense submodule to be invariant. It does not cover unbounded projectors.

Transfer blocks are literal composites, with output index first. The reconstruction theorem sums all blocks. The multiplication law inserts the intermediate completeness relation and gives a sum of composed blocks. The source supports distinct source, intermediate, and target modules. The power formula includes exponent zero and a recursively defined finite path sum.

Adjoint reversal requires self-adjoint outer maps and the completeness and boundedness assumptions of the adjoint API. It does not require idempotence of those outer maps. The full block algebra is the genuine family of packet-to-packet linear maps; restriction and synthesis are inverse, and the transported multiplication is proved to be the block product. The dimension formula is finite-dimensional.

The reflexivity and transitivity converses require every packet range to be nontrivial and allow all algebraic packet-Hom blocks. These hypotheses are needed to construct nonzero witnesses. They are not silently extended to zero packets or arbitrary restricted categories of bounded maps.

Finding: packet coordinates and block operations are actual algebraic constructions with the necessary hypotheses retained. Reachability must not be read as absence of cancellation in path sums.

## 4. Obstruction and transport: rows 26–30

The algebraic reachability result proves containment in reachable support. A nontrivial unreachable packet certifies that the generated hull is proper. It does not assert that graph reachability is sufficient for cyclic generation or that an arbitrary source-count rule applies to mixed-packet seeds.

The topological obstruction consumes a kernel-containment hypothesis and uses the closed kernel of a bounded map to retain that obstruction after closure. It does not derive the graph-to-kernel inclusion by itself.

Coordinate conjugation uses an invertible linear equivalence, so it preserves every zero/nonzero block and the induced reachability relation. Strict naturality tracks the actual image algebra. It retains injectivity of the label map. Equality over the full target algebra and complete target edge coverage require their stated bijectivity conditions. This strict result does not require the manuscript's finite-dimensional restriction.

The dense-realization theorem uses a continuous surjection and an intertwining operator assignment. The exact equality of transported ranges uses surjectivity, not merely density. The concrete quiver theorem concerns its displayed two- and three-dimensional spaces, arrows, missing kernel direction, and two generating seeds. It is not a universal quiver classification.

Finding: the proof directions are not reversed, and obstruction results are not promoted to sufficiency results.

## 5. Infinite-dimensional example, paths, and cycles: rows 31–32

The bilateral-shift example is a literal reindexing action on ℓ²(ℤ). The proof establishes dense orbit generation by the delta vector and minimum finite seed cardinality one. It does not identify this with an unrestricted algebraic cardinal rank or prove an infinite residue-packet decomposition.

The general graph formula accepts an eigenbasis and multiplicity data. One variant accepts explicit polynomial projectors; another constructs the separation from distinct eigenvalue labels. Neither constructs the eigenbasis from an unqualified symmetry claim. Separately, the path endpoint and complex simple-cycle results have their own constructions. Their endpoint regimes are n+1 path vertices and n+3 cycle vertices.

Finding: the general spectral statement remains certificate-explicit, while the concrete path and cycle theorems have the stated direct formal coverage.

## 6. Mathematical algorithms: rows 33–35

The orbit-hull algorithm is an ascending iteration of subspaces. In finite dimension the proof supplies a stopping index, proves stability, and identifies the stable subspace with the least invariant hull. This is a mathematical termination and correctness theorem, not extracted basis-maintenance code or a complexity theorem.

The transfer-table construction is the actual family of blocks and its sum. Its support predicate is exact nonvanishing. It does not contain a verified numerical tolerance rule or an executable zero-test for arbitrary linear maps.

`exactGraphSeedRank` is a noncomputable natural-valued definition based on exact spectral data. The least-seed theorem requires an eigenbasis, polynomial-projector certificates, spectrum coverage, multiplicity identifications, and an attained maximum. It is not a certified eigensolver, factorization routine, or symmetry-to-diagonalization algorithm.

Finding: all three mathematical specifications are covered at the stated scope. Executable extraction and numerical conditioning remain outside this audit's formal denominator.

## 7. Audit coverage improvement

The inherited namespace-based audit inspects 1,126 entries. The additional audit selects declarations by their actual source module, not by the spelling of their names. It inspects 1,152 entries: the same 1,126 plus 25 private declarations and one generated declaration in the `ContinuousLinearMap` namespace. Every entry passes the same axiom and safety policy.

This does not mean that 26 missing mathematical theorems were proved in this audit. Their sources already compiled. The improvement closes a gap in the *axiom inventory's selection rule*. The source-owned inventory records 720 theorem-kind entries, 382 definitions, 32 constructors, 9 inductives, and 9 recursors, including generated helpers. These are not counts of independent novel mathematical results. The contract's mapped surface is 73 theorem declarations plus 11 definitions or equivalences.

## 8. Final claim boundary

The proper assertion is that all 35 rows of the current Paper I formal contract have freshly compiled declarations, matched types, clean dependency audits, and source-preserving module replay under the pinned environment. The expanded 108-record monograph is a different inventory. The historical attached v0.2.0 tranche remains a provenance artifact and is not added to the denominator as a second current formalization.

No proof body, theorem statement, definition, toolchain pin, or dependency revision in the 20-file production source was changed. No formal claim is made here about independent novelty, all classical existence inputs, performance, Python correctness, later papers, or a fresh reconstruction of Mathlib itself.
