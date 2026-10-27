# Independent audit: continuous dyadic packet isometries

Date: 8 September 2026. Release author: Komorebi P.

## Normalized claim and verdict

**Verdict: proved as written.**

For each natural address \(j<4\), let
\[
U_j(n)=E_{4n}^{(4,j)}=j!C_{4,j}(n),\qquad
(d_0,d_1,d_2,d_3)=(1,1,5,3).
\]
There exists a unique isometric bijection
\[
G_j:\mathbb Z_2\longrightarrow\mathbb Z_2,
\qquad
G_j(n)=\frac{U_j(n)-j!}{2^{d_j}}\quad(n\in\mathbb N),
\]
where the displayed rational value is embedded in \(\mathbb Q_2\). The proof establishes its integrality. The map fixes zero, preserves every dyadic distance, and is uniquely determined even among all continuous maps with these natural values.

The original extension
\[
\widetilde U_j(x)=j!+2^{d_j}G_j(x)
\]
is continuous and injective, agrees with the actual original coefficients at every natural packet index, has image exactly \(j!+2^{d_j}\mathbb Z_2\), and has one preimage for every point in that image. It satisfies
\[
|\widetilde U_j(x)-\widetilde U_j(y)|_2=2^{-d_j}|x-y|_2
\quad(x,y\in\mathbb Z_2).
\]
The variable being extended is the packet index \(n\), corresponding to Euler degree \(4n\). This does not assert a ring or additive isomorphism, or a surjection of the original coefficients onto all of \(\mathbb Z_2\).

The independent reviewer read the actual proof sources, the coefficient dependency, the pinned Mathlib source leaves, the statement contract and boundary controls. The verdict also incorporates the completed fresh continuation replay and independent hash/axiom-log checks below.

## Dependency graph

1. **Internal proved input:** `DyadicFourLeastPeriods.exact_displacement` gives both nonvanishing and
   \(v_2(U_j(n+T)-U_j(n))=v_2(T)+d_j\) for every \(n\ge0,T>0,j<4\). The reviewed source derives this from the actual coefficient function and recurrence-derived Mahler estimates; it is not a premise introduced by the new capstone.
2. **New internal proof:** `DyadicPacketRational` subtracts the actual constant \(j!\), divides by \(2^{d_j}\), removes exactly the extra valuation, and proves the rational norm identity for every ordered pair of natural rows. Equal and reversed rows are explicitly covered.
3. **New internal proof plus pinned norm bridge:** `RationalPadicEmbedding` includes these rational values in the integral unit ball and identifies their distances with distances of natural casts in \(\mathbb Z_p\).
4. **New internal proof plus pinned topology:** `DensePadicIsometry` treats the natural-cast range as a subtype of \(\mathbb Z_p\), proves an isometry on this induced metric space, and extends it using density and target completeness. Distance equality on the dense product extends to all pairs. Density also proves uniqueness among continuous maps.
5. **New internal proof plus pinned compactness:** `CompactSelfIsometry` proves every self-isometry of a compact metric space is onto. A convergent subsequence of the forward orbit supplies arbitrarily close iterates. Cancelling a common isometric iterate gives positive returns arbitrarily close to the original point, so the image is dense. Its compactness makes it closed. No surjectivity assumption is used.
6. **New capstone:** `DyadicFourIsometry` applies these generic facts to the actual four packets, packages the inverse in `IsometryEquiv`, and undoes the normalization to prove the exact affine image and distance scaling.

No circular dependency or unchecked interpolation, convergence or surjectivity premise was found.

## Obligation matrix

| Obligation | Status | Decisive evidence |
|---|---|---|
| Actual coefficient family and factorial normalization | Passed | `packet`, `samples_coe`, `isometry_nat`, and the expanded contract use `Congruential.unnormalized 4 j n`; the contract also checks `generalizedEuler` at degree `4*n`. |
| Exact address range | Passed | Actual-family results quantify `j : ℕ` with `j < 4`; no result for other addresses is inferred. |
| Correct exponent and sign | Passed | `originalBonus_values` gives 1,1,5,3. Division subtracts this valuation. `norm_p_pow` gives the factor \(2^{-d_j}\). |
| Zero differences and finite valuation conventions | Passed | Positive shifts carry explicit nonzero proofs before using the valuation-to-norm identity; the equal-row case is proved separately. |
| Correct natural-number metric | Passed | `onNaturalRange` has source `Set.range (Nat.cast : ℕ → ℤ_[p])`, with the subtype metric inherited from \(\mathbb Z_p\). The proof never uses the usual discrete metric on \(\mathbb N\). |
| Choice of representative on the natural range | Passed | `onNaturalRange_nat` uses injectivity of natural casts; the chosen representative has the required unique natural value. |
| Integrality of all rational samples | Passed | Zero is fixed and the all-pairs norm identity gives \(|G_j(n)|_2=|n|_2\le1\). |
| Completeness, density and extension agreement | Passed | Exact pinned `Dense` extension theorems apply to the induced subtype and complete target; natural casts are proved dense. |
| All-pairs isometry after completion | Passed | Continuous distance functions agree on the dense product of natural-cast ranges. |
| Surjectivity is proved rather than assumed | Passed | Compact orbit recurrence and closedness of the image establish generic self-isometry surjectivity. |
| Uniqueness has the claimed scope | Passed | The competing map in `unique_continuous` is only assumed continuous with matching values; it need not be an isometry. |
| Original image and preimages | Passed | Range equality is in both directions; `unique_original_preimage` combines the inverse of \(G_j\) with cancellation of the nonzero power of two. |
| Metric versus algebra structure | Passed | Only metric equivalences are constructed. A checked control proves \(G_0\) is not additive. |
| Universal proof versus finite evidence | Passed | Main results quantify all rows or all dyadic points. Concrete values are controls, not a replacement for the universal proof. |
| Native conjectures or other packet families resolved by this block | Out of scope | No such inference occurs in the audited theorem. The updated checklist retains their separate obligations. |

## Pinned primary-source checks

The source question was whether the exact metric, completeness, density, compactness and extension hypotheses required above are present in the pinned implementation. The authorized local Mathlib checkout was used directly; no web snippet or recalled theorem was substituted for source inspection.

- Source: Mathlib community, Mathlib4, revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, under Lean `4.34.0-rc2`.
- Revision was checked against the portable workspace's `lake-manifest.json`.
- Local source root: `/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2/workspace/.lake/packages/mathlib/`.
- Inspection date: 8 September 2026. Files were read as Lean source; no extraction or OCR was involved.

| Source/result | Exact implication checked | SHA-256 of source file |
|---|---|---|
| `Mathlib/NumberTheory/Padics/PadicIntegers.lean`: `completeSpace`, `norm_p_pow` | The integral unit ball is a closed complete metric subspace; \(\|p^n\|=p^{-n}\). | `5392888b7e9833f14ab600bd3a3944da1f341366da2f3de95cd9737a19b1ff3b` |
| `Mathlib/NumberTheory/Padics/RingHoms.lean`: `denseRange_natCast` | Naturals are dense in \(\mathbb Z_p\), using arbitrarily accurate finite approximants. | `93ba84a94f41b266b73aaaab58a34982d0cb61cfb5bea592d05cb01ab31113c6` |
| `Mathlib/NumberTheory/Padics/ProperSpace.lean`: `compactSpace` | Total boundedness plus completeness proves compactness of \(\mathbb Z_p\). | `a7f441053a4464cfe4269f58334a1379ac54dca23a094bf1006fb50e7e6800a0` |
| `Mathlib/Topology/UniformSpace/UniformEmbedding.lean`: `Dense.uniformContinuous_extend`, `Dense.extend_of_ind` | A uniformly continuous map from a dense induced subtype extends continuously into a complete target and agrees on the subtype; the metric target supplies the separation hypothesis. | `d654b7daf50aa5ec57538e3e957509ceb738bc764213858cd4a5aa98d60355f8` |
| `Mathlib/Topology/Sequences.lean`: `CompactSpace.tendsto_subseq` | A compact first-countable space admits convergent subsequences, with strictly increasing indices; a metric space supplies first countability. | `a6a3be606e290b87bfb3b6619adcfbb64287f2474b22e804232e7ce9e4586b4c` |

All these source implications match the usage. The generic compact-isometry argument is independently written in this block; the underlying topology is standard library input. This audit makes no historical priority or global novelty claim.

## Decisive controls and small cases

The contract expands the actual rational normalization instead of providing an isometry hypothesis for the desired packet. It checks the existence of an `IsometryEquiv`, uniqueness among continuous maps, interpolation at original degree \(4n\), unique original preimages, and the generic extension theorem with the induced p-adic distance.

Checked controls prove
\[
G_0(1)=-1,\qquad G_0(2)=34,\qquad G_0^{-1}(34)=2.
\]
Thus \(G_0\) is not additive. Reduction modulo two proves the original map \(\widetilde U_0\) never attains zero and is not surjective onto all of \(\mathbb Z_2\).

An independent exact rational check also computed the first two coefficient rows directly from the reciprocal EGF, using Python `Fraction` and integer factorials. With \(a=j!/(4+j)!\), \(b=j!/(8+j)!\), the computation used \(C_{4,j}(1)=-4!a\) and \(C_{4,j}(2)=8!(a^2-b)\). Its first normalized values are
\[
\bigl(G_0(1),G_1(1),G_2(1),G_3(1)\bigr)
=\left(-1,-\frac35,-\frac1{15},-\frac{27}{35}\right).
\]
All four are dyadic units, consistent with the claimed isometry. This finite sanity check is not used as universal proof. In particular, the original-\(U\) normalization for address three includes the odd unit factor three compared with normalizing \(C_{4,3}-1\) directly.

The two new invalid-proof controls were rejected for their intended type mismatches: changing \(G_0(1)=-1\) to \(G_0(1)=1\), and transferring normalized surjectivity to the unnormalized original map. Their logs contain those exact mismatches, rather than missing imports or infrastructure errors.

## Fresh verification and independent integrity checks

The completed gate record is `strengthening/verification/continuation_verification.json` in the release. The reviewed original is `/workspace/scratch/196a43c5b4f3/dyadic_isometry/combined_replay_01/continuation_verification.json`, SHA-256:

`0be320c488f6666c3c239d0b99ee47ab1d802017d2665fb5e150243c2f99d54d`.

It reports **PASS in 146.828 seconds**: 22 freshly compiled continuation modules, 246 explicit declaration audits, 11 correctly rejected invalid-proof controls, and three passing statement-contract files. All 38 recorded gates passed. The six new modules contribute 46 theorems/supporting lemmas and eight definitions, including six positive boundary controls. These are declaration counts, not counts of independent mathematical discoveries.

The independent reviewer checked:

- all 22 staged module hashes against the report's source inventory;
- all 14 staged control/contract hashes against that inventory;
- equality of the staged and recorded inventories;
- exact agreement between the 246 inventory names, recorded axiom closures, and independently parsed `#print axioms` output;
- every closure uses only `propext`, `Classical.choice`, and `Quot.sound`;
- all 38 log hashes and expected success/failure exit statuses;
- all 110 recorded new compiled-output hashes.

The new source hashes are:

| Module | SHA-256 |
|---|---|
| `CompactSelfIsometry` | `3a81b435e899be582f1bcec59c561de1c57b7d7a7c6150a3eeafbe2ca8723c44` |
| `DensePadicIsometry` | `5ff66895f2ef98dad15abe1af104aa00285c05466d87ba384f7f5af795fbc136` |
| `RationalPadicEmbedding` | `234880a6a053a143265ab9b474f489ff7f4107356135b7038518b757d617f6dc` |
| `DyadicPacketRational` | `7a29429898faaa4d9d0d8d9ee931be6ba38644b061e967d6c36a69a3d49dc9e1` |
| `DyadicFourIsometry` | `22ee30fdfe665602b491ef9ff43b3aa8fe2bacfc503724e19e6623b227ef4da8` |
| `DyadicIsometryControls` | `b4f813406c69b1d9c37766c388be658d82e900f2efdccc864a5d41458b6625b3` |

Compiler warnings were treated as errors. The gate revalidates and reuses the earlier checked baseline outputs and the pinned Mathlib cache; it does not rebuild either. The separate shared-correction work also retains its earlier replay. This independent review inspected the completed replay rather than running a duplicate full compilation.

The gate JSON records every exact command. Compilation used the preserved `scripts/check_low_memory.py` runner, the pinned kit, one thread, a 240-second per-module timeout and a fresh continuation import/output directory. The release's replay wrapper consumes the updated inventory. Source inspection used `rg` and direct reads; integrity checks used Python `hashlib`, `json` and an independent axiom-log parser.

Development logs include failed numeral-coercion and simplification attempts. Those failures were corrected in the frozen sources; they did not reveal a mathematical counterexample. The final combined replay is the evidence for the delivered version.

## Remaining gap and safe scope

There is no remaining proof gap in this continuous \(N=4\) isometry block. The strongest safe conclusion is the actual all-points isometric bijection theorem, its continuous uniqueness, and the exact original affine-image theorem stated above.

This audit does not settle the polynomial Taylor/lifting formalization, unrestricted native Conjectures 13.2/13.3, exact higher-difference valuations, other least-period families, or general Mahler-kernel valuations. The updated checklist correctly leaves these separate. No additional check is needed for this completed block; the next bounded task is the fixed-presentation multivariable polynomial lifting bridge.
