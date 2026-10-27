import PaperXI.CanonicalDVRValuation
import Mathlib.Analysis.Normed.Unbundled.SpectralNorm
import Mathlib.Analysis.Normed.Module.FiniteDimension
import Mathlib.NumberTheory.LocalField.Basic

/-!
# Spectral local-field structure on the constructed unramified fraction field

The upper field is finite over the given nonarchimedean local field. This file
installs its spectral norm, proves completeness and local compactness, and
packages the norm valuation as an actual nonarchimedean local-field structure.
The canonical DVR valuation remains a separate explicitly named valuation; the
comparison of the two valued structures is not hidden in an instance.
-/

set_option autoImplicit false
noncomputable section

namespace PaperXI.SpectralLocalField

open PaperXI.LocalFieldResidueExtension
open ValuativeRel
open scoped WithZero

variable (K : Type*) [Field K] [ValuativeRel K] [UniformSpace K]
  [IsUniformAddGroup K] [IsNonarchimedeanLocalField K]
variable (s : Type*) [Field s] [Algebra 𝓀[K] s]
  [FiniteDimensional 𝓀[K] s]

private local instance baseValued : Valued K (ValueGroupWithZero K) := inferInstance

private local instance baseRankOne :
    Valuation.RankOne (Valued.v (R := K) (Γ₀ := ValueGroupWithZero K)) :=
  { hom' := IsRankLeOne.nonempty.some.emb (R := K).comp
      MonoidWithZeroHom.ValueGroup₀.embedding
    strictMono' := IsRankLeOne.nonempty.some.strictMono.comp
      MonoidWithZeroHom.ValueGroup₀.embedding_strictMono }

private local instance baseNormedField : NormedField K :=
  Valued.toNormedField K (ValueGroupWithZero K)

private local instance baseNontriviallyNormedField : NontriviallyNormedField K :=
  Valued.toNontriviallyNormedField K (ValueGroupWithZero K)

abbrev UpperField := LocalFieldResidueExtension.field K s

/-- The spectral normed-field structure on the constructed finite extension. -/
noncomputable instance upperNormedField : NormedField (UpperField K s) :=
  spectralNorm.normedField K (UpperField K s)

/-- The spectral norm is nontrivial because it extends the base-field norm. -/
noncomputable instance upperNontriviallyNormedField :
    NontriviallyNormedField (UpperField K s) :=
  spectralNorm.nontriviallyNormedField K (UpperField K s)

/-- The upper field is a normed space over the base through the spectral norm. -/
noncomputable instance upperNormedSpace : NormedSpace K (UpperField K s) :=
  spectralNorm.normedSpace K (UpperField K s)

/-- The algebra map is norm-compatible for the spectral norm. -/
noncomputable instance upperNormedAlgebra : NormedAlgebra K (UpperField K s) :=
  spectralNorm.normedAlgebra K (UpperField K s)

/-- The spectral norm extends the original norm exactly. -/
theorem norm_algebraMap (x : K) :
    ‖algebraMap K (UpperField K s) x‖ = ‖x‖ := by
  exact_mod_cast spectralNorm_extends (K := K) (L := UpperField K s) x

/-- The installed norm is definitionally the finite-extension spectral norm. -/
theorem norm_eq_spectralNorm (x : UpperField K s) :
    ‖x‖ = (spectralNorm K (UpperField K s) x : ℝ) := rfl

/-- The base-field embedding is an isometry for the spectral extension norm. -/
theorem algebraMap_isometry :
    Isometry (algebraMap K (UpperField K s)) := by
  refine Isometry.of_dist_eq ?_
  intro x y
  rw [dist_eq_norm, dist_eq_norm, ← map_sub, norm_algebraMap]

/-- The spectral norm on the upper field is nonarchimedean. -/
instance upperUltrametric : IsUltrametricDist (UpperField K s) := by
  constructor
  intro x y z
  change (spectralNorm K (UpperField K s) (x - z) : ℝ) ≤
    max (spectralNorm K (UpperField K s) (x - y) : ℝ)
      (spectralNorm K (UpperField K s) (y - z) : ℝ)
  rw [← sub_add_sub_cancel x y z]
  exact_mod_cast
    (isNonarchimedean_spectralNorm (K := K) (L := UpperField K s)
      (x - y) (y - z))

/-- Finite extensions are complete for the spectral norm. -/
instance upperComplete : CompleteSpace (UpperField K s) :=
  spectralNorm.completeSpace K (UpperField K s)

/-- Finite extensions of a locally compact normed field are proper. -/
instance upperProper : ProperSpace (UpperField K s) :=
  FiniteDimensional.proper K (UpperField K s)

/-- In particular the spectral upper field is locally compact. -/
instance upperLocallyCompact : LocallyCompactSpace (UpperField K s) := by
  infer_instance

/-- The valued-field structure associated to the spectral norm. -/
private noncomputable instance upperNormValued : Valued (UpperField K s) NNReal :=
  NormedField.toValued

/-- The valuative relation induced by the spectral norm valuation. -/
noncomputable instance upperValuativeRel : ValuativeRel (UpperField K s) :=
  ValuativeRel.ofValuation (NormedField.valuation (K := UpperField K s))

private instance upperNormValuationCompatible :
    (NormedField.valuation (K := UpperField K s)).Compatible :=
  Valuation.Compatible.ofValuation _

/-- The spectral norm topology is the topology induced by its norm valuation. -/
instance upperIsValuativeTopology : IsValuativeTopology (UpperField K s) := by
  exact IsValuativeTopology.of_mem_nhds_zero_iff_vle
    (NormedField.valuation (K := UpperField K s)) (by
      intro U
      exact Valued.mem_nhds_zero)

/-- The norm valuation is nontrivial. -/
instance upperValuativeNontrivial :
    ValuativeRel.IsNontrivial (UpperField K s) := by
  exact (ValuativeRel.isNontrivial_iff_isNontrivial
    (NormedField.valuation (K := UpperField K s))).mpr inferInstance

/-- The canonical valuation attached to the valuative relation and the original
norm valuation have exactly the same integer subring. -/
theorem relation_integer_eq_norm_integer :
    (ValuativeRel.valuation (UpperField K s)).integer =
      (NormedField.valuation (K := UpperField K s)).integer := by
  ext x
  simp only [Valuation.mem_integer_iff]
  simpa using
    (ValuativeRel.isEquiv
      (NormedField.valuation (K := UpperField K s))
      (ValuativeRel.valuation (UpperField K s)) x 1).symm

/-- Membership in the local-field integer ring is equivalent to spectral norm
at most one. -/
theorem mem_integer_iff_norm_le_one (x : UpperField K s) :
    x ∈ (ValuativeRel.valuation (UpperField K s)).integer ↔ ‖x‖ ≤ 1 := by
  rw [relation_integer_eq_norm_integer K s, Valuation.mem_integer_iff]
  change ‖x‖₊ ≤ 1 ↔ ‖x‖ ≤ 1
  exact NNReal.coe_le_coe

/-- The finite spectral extension is an actual nonarchimedean local field. -/
instance upperIsNonarchimedeanLocalField :
    IsNonarchimedeanLocalField (UpperField K s) where
  toIsValuativeTopology := inferInstance
  toLocallyCompactSpace := inferInstance
  toIsNontrivial := inferInstance

/-- The residue field of the spectral upper local field is finite. -/
instance upperFiniteResidue : Finite 𝓀[UpperField K s] := by
  infer_instance

/-- The local-field integer ring is a discrete valuation ring. -/
instance upperIntegerIsDVR :
    IsDiscreteValuationRing 𝒪[UpperField K s] := by
  infer_instance

/-- The local-field value group is canonically order-isomorphic to `ℤᵐ⁰`. -/
def upperValueGroupIsoInt :
    ValueGroupWithZero (UpperField K s) ≃*o ℤᵐ⁰ :=
  IsNonarchimedeanLocalField.valueGroupWithZeroIsoInt (UpperField K s)

/-- The spectral normed field has the already constructed extension degree. -/
theorem finrank_eq_residue_finrank :
    Module.finrank K (UpperField K s) = Module.finrank 𝓀[K] s :=
  LocalFieldResidueExtension.degree K s

end PaperXI.SpectralLocalField
