import Mathlib.RingTheory.Localization.FractionRing
import Mathlib.RingTheory.Localization.Integer
import Mathlib.RingTheory.Finiteness.Basic
import Mathlib.RingTheory.DiscreteValuationRing.Basic
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.RepresentationTheory.Irreducible

/-! Clearing denominators in a full field-valued action span. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.IntegralActionSpan
open scoped BigOperators

variable {R K M V : Type*} [CommRing R] [IsDomain R] [Field K]
  [Algebra R K] [IsFractionRing R K]
  [AddCommGroup M] [Module R M]
  [AddCommGroup V] [Module R V] [Module K V] [IsScalarTower R K V]

/-- Every vector in a field span has a nonzero integral multiple in the integral span. -/
theorem exists_integral_multiple_of_mem_span (f : M →ₗ[R] V) (s : Set M)
    {x : V} (hx : x ∈ Submodule.span K (f '' s)) :
    ∃ d : R, d ≠ 0 ∧ ∃ y ∈ Submodule.span R s, f y = d • x := by
  induction hx using Submodule.span_induction with
  | mem x hx =>
      obtain ⟨y, hy, rfl⟩ := hx
      exact ⟨1, one_ne_zero, y, Submodule.subset_span hy, by simp⟩
  | zero => exact ⟨1, one_ne_zero, 0, Submodule.zero_mem _, by simp⟩
  | add x z _ _ hx hz =>
      obtain ⟨d, hd, y, hy, hfy⟩ := hx
      obtain ⟨e, he, w, hw, hfw⟩ := hz
      refine ⟨d * e, mul_ne_zero hd he, e • y + d • w,
        Submodule.add_mem _ (Submodule.smul_mem _ e hy) (Submodule.smul_mem _ d hw), ?_⟩
      simp only [map_add, map_smul, hfy, hfw, smul_add, smul_smul, mul_comm e d]
  | smul c x _ hx =>
      obtain ⟨d, hd, y, hy, hfy⟩ := hx
      obtain ⟨e, r, hr⟩ := IsLocalization.exists_integer_multiple (nonZeroDivisors R) c
      refine ⟨(e : R) * d, mul_ne_zero (nonZeroDivisors.ne_zero e.property) hd,
        r • y, Submodule.smul_mem _ r hy, ?_⟩
      rw [map_smul, hfy]
      calc
        r • (d • x) = d • ((algebraMap R K r) • x) := by
          rw [algebraMap_smul, smul_comm]
        _ = d • (((e : R) • c) • x) := by rw [hr]
        _ = ((e : R) * d) • (c • x) := by rw [smul_assoc, smul_smul, mul_comm d]

/-- Finite generation permits one nonzero denominator for the entire integral module. -/
theorem exists_nonzero_smul_subset_of_span_eq_top [Module.Finite R M]
    (f : M →ₗ[R] V) (hf : Function.Injective f) (s : Set M)
    (hspan : Submodule.span K (f '' s) = ⊤) :
    ∃ d : R, d ≠ 0 ∧ ∀ x : M, d • x ∈ Submodule.span R s := by
  classical
  obtain ⟨t, ht⟩ := Module.Finite.fg_top (R := R) (M := M)
  have hlocal (x : M) : ∃ d : R, d ≠ 0 ∧ d • x ∈ Submodule.span R s := by
    obtain ⟨d, hd, y, hy, he⟩ := exists_integral_multiple_of_mem_span f s
      (x := f x) (by rw [hspan]; exact Submodule.mem_top)
    have he' : y = d • x := hf (by simpa only [map_smul] using he)
    exact ⟨d, hd, he' ▸ hy⟩
  choose d hd hmem using hlocal
  refine ⟨∏ x ∈ t, d x, Finset.prod_ne_zero_iff.mpr (fun x _ => hd x), ?_⟩
  intro x
  have hx : x ∈ Submodule.span R (t : Set M) := by rw [ht]; exact Submodule.mem_top
  induction hx using Submodule.span_induction with
  | mem y hy =>
      have hm := (Submodule.span R s).smul_mem (∏ z ∈ t.erase y, d z) (hmem y)
      simpa only [smul_smul, Finset.prod_erase_mul _ _ hy] using hm
  | zero => simp
  | add y z _ _ hy hz => simpa only [smul_add] using Submodule.add_mem _ hy hz
  | smul a y _ hy => simpa only [smul_comm (∏ x ∈ t, d x) a] using
      Submodule.smul_mem (Submodule.span R s) a hy

/-- The entrywise coefficient embedding, as an integral linear map. -/
def matrixCoefficientMap {n : Type*} : Matrix n n R →ₗ[R] Matrix n n K where
  toFun A := A.map (algebraMap R K)
  map_add' A B := by ext i j; simp
  map_smul' a A := by ext i j; simp [Algebra.smul_def]

variable {n G : Type*} [Fintype n]

/-- A full rational action span contains a fixed nonzero multiple of every integral matrix. -/
theorem exists_nonzero_smul_matrix_subset_span (τ : G → Matrix n n R)
    (hspan : Submodule.span K
      (Set.range (fun g => (τ g).map (algebraMap R K))) = ⊤) :
    ∃ d : R, d ≠ 0 ∧ ∀ A : Matrix n n R, d • A ∈ Submodule.span R (Set.range τ) := by
  apply exists_nonzero_smul_subset_of_span_eq_top (K := K) (matrixCoefficientMap (K := K))
  · intro A B h
    ext i j
    exact IsFractionRing.injective R K (congrFun (congrFun h i) j)
  · rw [← Set.range_comp]
    exact hspan

/-- Over a DVR, the denominator can be chosen to be a power of a uniformizer. -/
theorem exists_uniformizer_power_matrix_subset_span [IsDiscreteValuationRing R]
    (π : R) (hπ : Irreducible π) (τ : G → Matrix n n R)
    (hspan : Submodule.span K
      (Set.range (fun g => (τ g).map (algebraMap R K))) = ⊤) :
    ∃ c : ℕ, ∀ A : Matrix n n R, π ^ c • A ∈ Submodule.span R (Set.range τ) := by
  obtain ⟨d, hd, hmem⟩ := exists_nonzero_smul_matrix_subset_span τ hspan
  obtain ⟨c, u, hu⟩ := IsDiscreteValuationRing.eq_unit_mul_pow_irreducible hd hπ
  refine ⟨c, fun A => ?_⟩
  have hm := (Submodule.span R (Set.range τ)).smul_mem (↑(u⁻¹) : R) (hmem A)
  simpa only [hu, smul_smul, ← mul_assoc, Units.inv_mul, one_mul] using hm

section Density

variable {F A W : Type*} [Field F] [Ring A] [Algebra F A]
  [AddCommGroup W] [Module F W] [Module A W] [IsScalarTower F A W]
  [IsSimpleModule A W] [FiniteDimensional F W]

/-- Jacobson density becomes surjectivity when the commutant consists of scalars. -/
theorem surjective_module_action_of_scalar_commutant
    (hscalar : Function.Surjective (algebraMap F (Module.End A W))) :
    Function.Surjective (Module.toModuleEnd F (S := A) W) := by
  classical
  intro T
  let T' : Module.End (Module.End A W) W :=
    { T.toAddMonoidHom with
      map_smul' := fun e x => by
        obtain ⟨a, rfl⟩ := hscalar e
        exact T.map_smul a x }
  let b := Module.finBasis F W
  obtain ⟨a, ha⟩ := jacobson_density T' (Finset.univ.image b)
  refine ⟨a, b.ext fun i => ?_⟩
  exact (ha (b i) (Finset.mem_image.mpr ⟨i, Finset.mem_univ i, rfl⟩)).symm

end Density

section Representations
open scoped MonoidAlgebra
variable {F H W : Type*} [Field F] [Monoid H]
  [AddCommGroup W] [Module F W] [FiniteDimensional F W]

/-- Split irreducibility is recorded by irreducibility and an explicitly scalar commutant.
No algebraic-closure assumption is placed on a DVR fraction field. -/
theorem span_range_eq_top_of_split_irreducible (ρ : Representation F H W)
    [Representation.IsIrreducible ρ]
    (hscalar : Function.Surjective (algebraMap F (Module.End F[H] ρ.asModule))) :
    Submodule.span F (Set.range ρ) = ⊤ := by
  classical
  apply top_unique
  intro T _
  let e := ρ.asModuleEquiv
  let T' : Module.End F ρ.asModule := e.symm.toLinearMap.comp (T.comp e.toLinearMap)
  obtain ⟨a, ha⟩ := surjective_module_action_of_scalar_commutant hscalar T'
  have he : ρ.asAlgebraHom a = T := by
    apply LinearMap.ext
    intro x
    have hx := LinearMap.congr_fun ha (e.symm x)
    apply e.symm.injective
    exact hx
  rw [← he, Representation.asAlgebraHom_def, MonoidAlgebra.lift_apply, Finsupp.sum]
  exact Submodule.sum_mem _ (fun g _ => Submodule.smul_mem _ _
    (Submodule.subset_span (Set.mem_range_self g)))

end Representations

section MatrixRepresentations
open scoped MonoidAlgebra
variable {F H m : Type*} [Field F] [Monoid H] [Fintype m] [DecidableEq m]

/-- The ordinary representation associated to actual action matrices. -/
def matrixRepresentation (τ : H →* Matrix m m F) : Representation F H (m → F) :=
  Matrix.toLinAlgEquiv'.toMonoidHom.comp τ

/-- Split irreducibility supplies the full matrix span required by denominator clearing. -/
theorem matrix_span_eq_top_of_split_irreducible (τ : H →* Matrix m m F)
    [Representation.IsIrreducible (matrixRepresentation τ)]
    (hscalar : Function.Surjective
      (algebraMap F (Module.End F[H] (matrixRepresentation τ).asModule))) :
    Submodule.span F (Set.range τ) = ⊤ := by
  have hs := span_range_eq_top_of_split_irreducible (matrixRepresentation τ) hscalar
  apply top_unique
  intro A _
  apply (Submodule.apply_mem_span_image_iff_mem_span
    (f := Matrix.toLinAlgEquiv'.toLinearMap) Matrix.toLinAlgEquiv'.injective).mp
  rw [← Set.range_comp]
  change Matrix.toLinAlgEquiv' A ∈ Submodule.span F (Set.range (matrixRepresentation τ))
  rw [hs]
  exact Submodule.mem_top

end MatrixRepresentations

end PaperX.IntegralActionSpan
