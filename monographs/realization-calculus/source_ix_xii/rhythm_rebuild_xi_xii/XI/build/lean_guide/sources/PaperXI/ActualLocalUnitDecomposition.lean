import PaperXI.ActualLocalUnitTopology
import Mathlib.RingTheory.DiscreteValuationRing.Basic
import Mathlib.Topology.Algebra.Group.Neighborhood
import Mathlib.Topology.Instances.Int

/-!
# Actual local-field unit and uniformizer coordinates

The uniformizer is chosen from the proved DVR structure of the actual ring of
integers. Existence of coordinates comes from fraction-field factorization;
uniqueness comes from the actual valuation. No split group is supplied.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualLocalUnitDecomposition
open ValuativeRel ActualLocalUnitTopology

variable (K : Type*) [Field K] [ValuativeRel K] [TopologicalSpace K]
  [IsNonarchimedeanLocalField K]

/-- A uniformizer chosen inside the actual local-field integer ring. -/
def uniformizer : 𝒪[K] := Classical.choose (IsDiscreteValuationRing.exists_irreducible 𝒪[K])

theorem uniformizer_irreducible : Irreducible (uniformizer K) :=
  Classical.choose_spec (IsDiscreteValuationRing.exists_irreducible 𝒪[K])

theorem uniformizer_ne_zero : (uniformizer K : K) ≠ 0 := by
  exact_mod_cast (uniformizer_irreducible K).ne_zero

/-- The chosen uniformizer as an actual element of `Kˣ`. -/
def uniformizerUnit : Kˣ := Units.mk0 (uniformizer K : K) (uniformizer_ne_zero K)

@[simp] theorem uniformizerUnit_coe : (uniformizerUnit K : K) = (uniformizer K : K) := rfl

theorem uniformizer_value_pos : 0 < valuation K (uniformizer K : K) :=
  Valuation.integer.v_irreducible_pos (uniformizer_irreducible K)

theorem uniformizer_value_lt_one : valuation K (uniformizer K : K) < 1 :=
  Valuation.integer.v_irreducible_lt_one (uniformizer_irreducible K)

/-- Multiplication of an actual integer-ring unit by an integral uniformizer power. -/
def normalFormHom : 𝒪[K]ˣ × Multiplicative ℤ →* Kˣ where
  toFun p := unitEmbedding K p.1 * uniformizerUnit K ^ p.2.toAdd
  map_one' := by simp
  map_mul' := by
    rintro ⟨u, m⟩ ⟨v, n⟩
    change unitEmbedding K (u * v) * uniformizerUnit K ^ (m.toAdd + n.toAdd) = _
    simp [map_mul, zpow_add, mul_mul_mul_comm]

@[simp] theorem normalFormHom_apply (u : 𝒪[K]ˣ) (n : Multiplicative ℤ) :
    normalFormHom K (u, n) = unitEmbedding K u * uniformizerUnit K ^ n.toAdd := rfl

/-- Existence is a theorem about the actual fraction field of the actual DVR. -/
theorem normalForm_surjective : Function.Surjective (normalFormHom K) := by
  intro x
  obtain ⟨n, u, hu⟩ := IsDiscreteValuationRing.exists_units_eq_smul_zpow_of_irreducible
    (K := K) (uniformizer_irreducible K) x.ne_zero
  refine ⟨(u, Multiplicative.ofAdd n), ?_⟩
  apply Units.ext
  have hmap (a : 𝒪[K]) : algebraMap 𝒪[K] K a = (a : K) := rfl
  simpa [normalFormHom, unitEmbedding, uniformizerUnit, Units.smul_def, Algebra.smul_def, hmap]
    using hu.symm

/-- The integer exponent and the residual actual unit are both unique. -/
theorem normalForm_injective : Function.Injective (normalFormHom K) := by
  apply (injective_iff_map_eq_one _).mpr
  rintro ⟨u, n⟩ h
  have huval : valuation K (algebraMap 𝒪[K] K (u : 𝒪[K])) = 1 :=
    (Valuation.integer.integers (valuation K)).valuation_unit u
  have hv := congrArg (fun x : Kˣ => valuation K (x : K)) h
  have hnval : valuation K (uniformizer K : K) ^ n.toAdd = 1 := by
    simpa [normalFormHom, unitEmbedding, uniformizerUnit, map_mul, huval] using hv
  have hn : n.toAdd = 0 :=
    (zpow_right_injective₀ (uniformizer_value_pos K) (uniformizer_value_lt_one K).ne)
      (by simpa using hnval)
  have hn' : n = 1 := congrArg Multiplicative.ofAdd hn
  subst n
  have hu : u = 1 := unitEmbedding_injective K (by simpa using h)
  simp [hu]

/-- Multiplicative coordinates on the actual multiplicative group of the local field. -/
def normalFormEquiv : (𝒪[K]ˣ × Multiplicative ℤ) ≃* Kˣ :=
  MulEquiv.ofBijective (normalFormHom K) ⟨normalForm_injective K, normalForm_surjective K⟩

@[simp] theorem normalFormEquiv_apply (u : 𝒪[K]ˣ) (n : Multiplicative ℤ) :
    normalFormEquiv K (u, n) = unitEmbedding K u * uniformizerUnit K ^ n.toAdd := rfl

/-- The actual normalized integer valuation, positive on the chosen uniformizer. -/
def degree : Kˣ →* Multiplicative ℤ :=
  (MonoidHom.snd 𝒪[K]ˣ (Multiplicative ℤ)).comp (normalFormEquiv K).symm.toMonoidHom

@[simp] theorem degree_normalForm (u : 𝒪[K]ˣ) (n : Multiplicative ℤ) :
    degree K (unitEmbedding K u * uniformizerUnit K ^ n.toAdd) = n := by
  change ((normalFormEquiv K).symm (normalFormEquiv K (u, n))).2 = n
  rw [MulEquiv.symm_apply_apply]

@[simp] theorem degree_unit (u : 𝒪[K]ˣ) : degree K (unitEmbedding K u) = 1 := by
  simpa using degree_normalForm K u 1

theorem degree_unitEmbedding (u : 𝒪[K]ˣ) : degree K (unitEmbedding K u) = 1 :=
  degree_unit K u

@[simp] theorem degree_uniformizer : degree K (uniformizerUnit K) = Multiplicative.ofAdd (1 : ℤ) := by
  simpa using degree_normalForm K 1 (Multiplicative.ofAdd 1)

/-- The degree-zero subgroup is literally the compact open unit subgroup. -/
theorem ker_degree : (degree K).ker = compactUnitSubgroup K := by
  ext x
  constructor
  · intro hx
    obtain ⟨⟨u, n⟩, rfl⟩ := (normalFormEquiv K).surjective x
    have hn : n = 1 := by simpa using hx
    subst n
    exact ⟨u, by simp⟩
  · rintro ⟨u, rfl⟩
    exact degree_unit K u

/-- Continuity follows from the proved openness of the actual unit subgroup. -/
theorem degree_continuous : Continuous (degree K) := by
  apply continuous_of_tendsto_nhds_one (degree K)
  have hker : IsOpen ((degree K).ker : Set Kˣ) := by
    rw [ker_degree]
    exact isOpen_compactUnitSubgroup K
  have he : ∀ᶠ x in nhds (1 : Kˣ), (1 : Multiplicative ℤ) = degree K x :=
    Filter.mem_of_superset (hker.mem_nhds (Subgroup.one_mem _)) fun x hx => hx.symm
  exact (Filter.tendsto_congr' he).mp tendsto_const_nhds

end PaperXI.ActualLocalUnitDecomposition
