import PaperXI.ActualDepthZeroExtension
import PaperXI.CompactDegreeSeparation
import Mathlib.Topology.Algebra.Module.FiniteDimension

/-!
# Uniformizers of actual matrix-embedded local fields

For a continuous algebra embedding of a local field `E` into matrices over
`F`, its actual uniformizer has nonzero determinant degree over `F`.
The proof uses actual compact integral units and actual uniformizer coordinates;
it does not assume a determinant-norm formula or a ramification index.
Consequently no nonzero power belongs to any compact matrix subgroup.
The embedding may be noncentral. No simple-type realization is asserted here.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualEmbeddedUniformizer58

open Matrix ValuativeRel
open ActualLocalUnitTopology ActualLocalUnitDecomposition ActualDepthZeroExtension

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F]
  [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (n : Type*) [Fintype n] [DecidableEq n]
variable (ι : E →ₐ[F] Matrix n n F)

/-- The literal map on invertible matrices induced by the field embedding. -/
def unitsEmbedding : Eˣ →* GeneralLinearGroup n F :=
  Units.map ι.toMonoidHom

/-- The actual `E`-uniformizer, as a matrix over `F`. -/
def embeddedUniformizer : GeneralLinearGroup n F :=
  unitsEmbedding F E n ι (uniformizerUnit E)

omit [ValuativeRel F] [IsNonarchimedeanLocalField F]
  [ValuativeRel E] [IsNonarchimedeanLocalField E] in
theorem unitsEmbedding_continuous (hι : Continuous ι) :
    Continuous (unitsEmbedding F E n ι) := hι.units_map _

theorem determinantDegree_continuous : Continuous (determinantDegree F n) :=
  (degree_continuous F).comp GeneralLinearGroup.continuous_det

omit [ValuativeRel F] [TopologicalSpace F] [IsNonarchimedeanLocalField F]
  [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
/-- The algebra embedding carries scalars from `F` to literal scalar matrices. -/
@[simp] theorem unitsEmbedding_baseScalar (a : Fˣ) :
    unitsEmbedding F E n ι (Units.map (algebraMap F E).toMonoidHom a) =
      GeneralLinearGroup.scalar n a := by
  apply Units.ext
  change ι (algebraMap F E (a : F)) = Matrix.scalar n (a : F)
  rw [ι.commutes]
  rfl

/-- Compact integral units have zero matrix determinant degree. -/
@[simp] theorem determinantDegree_integral_unit (hι : Continuous ι) (u : 𝒪[E]ˣ) :
    determinantDegree F n (unitsEmbedding F E n ι (unitEmbedding E u)) = 1 := by
  let δ : Eˣ →* Multiplicative ℤ :=
    (determinantDegree F n).comp (unitsEmbedding F E n ι)
  have hδ : Continuous δ :=
    (determinantDegree_continuous F n).comp (unitsEmbedding_continuous F E n ι hι)
  exact CompactDegreeSeparation.compact_le_degree_ker (compactUnitSubgroup E) δ hδ
    (isCompact_compactUnitSubgroup E) (show unitEmbedding E u ∈ compactUnitSubgroup E from
      ⟨u, rfl⟩)

variable [Nonempty n]

/-- Continuity of the matrix embedding follows from the compatible local-field
algebra topology. Finite dimensionality is derived from the embedding itself. -/
theorem algebraEmbedding_continuous (hF : Continuous (algebraMap F E)) :
    Continuous ι := by
  let := IsTopologicalAddGroup.rightUniformSpace F
  have := isUniformAddGroup_of_addCommGroup (G := F)
  let : (Valued.v (R := F)).RankOne :=
    { hom' := ValuativeRel.IsRankLeOne.nonempty.some.emb (R := F).comp
        MonoidWithZeroHom.ValueGroup₀.embedding
      strictMono' := ValuativeRel.IsRankLeOne.nonempty.some.strictMono.comp
        MonoidWithZeroHom.ValueGroup₀.embedding_strictMono }
  let : ContinuousSMul F E := continuousSMul_of_algebraMap F E hF
  let : T2Space E := localFieldT2Space E
  let : FiniteDimensional F E := FiniteDimensional.of_injective ι.toLinearMap ι.injective
  open scoped Valued in
    exact ι.toLinearMap.continuous_of_finiteDimensional

/-- An embedded local-field uniformizer has nonzero ambient determinant degree.
If its degree vanished, unit/uniformizer decomposition would kill every element
of `Eˣ`, contradicting the known positive degree of the scalar `F`-uniformizer. -/
theorem embeddedUniformizer_degree_ne_one (hι : Continuous ι) :
    determinantDegree F n (embeddedUniformizer F E n ι) ≠ 1 := by
  intro ht
  have hzero (a : Eˣ) : determinantDegree F n (unitsEmbedding F E n ι a) = 1 := by
    obtain ⟨⟨u, r⟩, rfl⟩ := (normalFormEquiv E).surjective a
    rw [normalFormEquiv_apply, map_mul, map_zpow, map_mul, map_zpow,
      determinantDegree_integral_unit F E n ι hι u]
    change 1 * determinantDegree F n (embeddedUniformizer F E n ι) ^ r.toAdd = 1
    rw [ht, one_zpow, mul_one]
  have hscalar := hzero (Units.map (algebraMap F E).toMonoidHom (uniformizerUnit F))
  rw [unitsEmbedding_baseScalar] at hscalar
  change determinantDegree F n (scalarUniformizer F n) = 1 at hscalar
  rw [determinantDegree_scalarUniformizer] at hscalar
  have hcard : (Fintype.card n : ℤ) = 0 := congrArg Multiplicative.toAdd hscalar
  exact (Nat.ne_of_gt (Fintype.card_pos)).elim (Int.ofNat_eq_zero.mp hcard)

/-- No nonzero power of the genuine matrix uniformizer belongs to a compact
matrix subgroup, without any centrality hypothesis. -/
theorem embeddedUniformizer_free (hι : Continuous ι)
    (J : Subgroup (GeneralLinearGroup n F))
    (hJ : IsCompact (J : Set (GeneralLinearGroup n F))) :
    ∀ r : ℤ, embeddedUniformizer F E n ι ^ r ∈ J → r = 0 :=
  CompactDegreeSeparation.hfree_from_compact_degree J (determinantDegree F n)
    (determinantDegree_continuous F n) hJ (embeddedUniformizer F E n ι)
    (embeddedUniformizer_degree_ne_one F E n ι hι)

/-- The freeness theorem under the actual compatible extension topology,
with matrix-embedding continuity proved rather than supplied. -/
theorem embeddedUniformizer_free_of_algebraMap
    (hF : Continuous (algebraMap F E))
    (J : Subgroup (GeneralLinearGroup n F))
    (hJ : IsCompact (J : Set (GeneralLinearGroup n F))) :
    ∀ r : ℤ, embeddedUniformizer F E n ι ^ r ∈ J → r = 0 :=
  embeddedUniformizer_free F E n ι (algebraEmbedding_continuous F E n ι hF) J hJ

/-- The coordinates `t^r j` in actual matrices are unique for every compact
subgroup `J`; no normalization hypothesis is needed for uniqueness. -/
theorem normalForm_injective (hF : Continuous (algebraMap F E))
    (J : Subgroup (GeneralLinearGroup n F))
    (hJ : IsCompact (J : Set (GeneralLinearGroup n F))) :
    Function.Injective (fun p : ℤ × J =>
      embeddedUniformizer F E n ι ^ p.1 * (p.2 : GeneralLinearGroup n F)) := by
  rintro ⟨r, j⟩ ⟨s, k⟩ h
  let t := embeddedUniformizer F E n ι
  change t ^ r * (j : GeneralLinearGroup n F) = t ^ s * k at h
  have hpow : t ^ (r - s) = (k : GeneralLinearGroup n F) * (j : GeneralLinearGroup n F)⁻¹ := by
    calc
      t ^ (r - s) = t ^ (-s) * t ^ r := by rw [← zpow_add]; congr 1; omega
      _ = t ^ (-s) * (t ^ r * j) * (j : GeneralLinearGroup n F)⁻¹ := by group
      _ = t ^ (-s) * (t ^ s * k) * (j : GeneralLinearGroup n F)⁻¹ := by rw [h]
      _ = (k : GeneralLinearGroup n F) * (j : GeneralLinearGroup n F)⁻¹ := by
        rw [zpow_neg]; group
  have hrs : r - s = 0 := embeddedUniformizer_free_of_algebraMap F E n ι hF J hJ
    (r - s) (hpow ▸ J.mul_mem k.property (J.inv_mem j.property))
  have hsr : r = s := sub_eq_zero.mp hrs
  subst s
  have hjk : j = k := Subtype.ext (mul_left_cancel h)
  subst k
  rfl

omit [ValuativeRel F] [TopologicalSpace F] [IsNonarchimedeanLocalField F] [Nonempty n] in
/-- Every literal element of `Eˣ J` has uniformizer coordinates once the actual
integral units of `E` map into `J`. -/
theorem field_product_normalForm
    (J : Subgroup (GeneralLinearGroup n F))
    (hunits : ∀ u : 𝒪[E]ˣ, unitsEmbedding F E n ι (unitEmbedding E u) ∈ J)
    (a : Eˣ) (j : J) :
    ∃ r : ℤ, ∃ k : J, unitsEmbedding F E n ι a * (j : GeneralLinearGroup n F) =
      embeddedUniformizer F E n ι ^ r * (k : GeneralLinearGroup n F) := by
  obtain ⟨⟨u, r⟩, rfl⟩ := (normalFormEquiv E).surjective a
  refine ⟨r.toAdd, ⟨unitsEmbedding F E n ι (unitEmbedding E u) * j,
    J.mul_mem (hunits u) j.property⟩, ?_⟩
  rw [normalFormEquiv_apply, mul_comm (unitEmbedding E u), map_mul, map_zpow, mul_assoc]
  rfl

/-- The actual product `Eˣ J` has unique integral-exponent/compact coordinates.
This is the coordinate input for a noncentral type-normalizer extension. -/
theorem field_product_unique_normalForm
    (hF : Continuous (algebraMap F E))
    (J : Subgroup (GeneralLinearGroup n F))
    (hJ : IsCompact (J : Set (GeneralLinearGroup n F)))
    (hunits : ∀ u : 𝒪[E]ˣ, unitsEmbedding F E n ι (unitEmbedding E u) ∈ J)
    (a : Eˣ) (j : J) :
    ∃! p : ℤ × J, unitsEmbedding F E n ι a * (j : GeneralLinearGroup n F) =
      embeddedUniformizer F E n ι ^ p.1 * (p.2 : GeneralLinearGroup n F) := by
  obtain ⟨r, k, h⟩ := field_product_normalForm F E n ι J hunits a j
  exact ⟨(r, k), h, fun q hq => normalForm_injective F E n ι hF J hJ (hq.symm.trans h)⟩

end PaperXI.ActualEmbeddedUniformizer58
