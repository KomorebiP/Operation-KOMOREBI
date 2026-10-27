import Mathlib.RingTheory.Jacobson.Radical
import Mathlib.Algebra.Module.Torsion.Basic

/-!
Noncommutative Nakayama lifting, with the actual ideal-times-module submodule.
Only finite generation of the ambient module is used. No commutativity,
Noetherian, semisimplicity or finite length assumption is imposed.
-/
set_option autoImplicit false

namespace Komorebi.PaperICompletion7.Nakayama

universe u v
variable {R : Type u} {M : Type v} [Ring R] [AddCommGroup M] [Module R M]

/-- The radical of a finitely generated module is superfluous. -/
theorem eq_top_of_sup_module_jacobson [Module.Finite R M]
    (N : Submodule R M) (h : N ⊔ Module.jacobson R M = ⊤) : N = ⊤ := by
  by_contra hn
  obtain ⟨P, hP, hNP⟩ := (eq_top_or_exists_le_coatom N).resolve_left hn
  have hrad : Module.jacobson R M ≤ P := sInf_le hP
  exact hP.1 (top_unique (h ▸ sup_le hNP hrad))

/-- Nakayama with an arbitrary left ideal contained in the ring radical. -/
theorem eq_top_of_sup_ideal_smul [Module.Finite R M]
    (I : Ideal R) (hI : I ≤ Ring.jacobson R) (N : Submodule R M)
    (h : N ⊔ I • (⊤ : Submodule R M) = ⊤) : N = ⊤ := by
  apply eq_top_of_sup_module_jacobson N
  apply top_unique
  rw [← h]
  exact sup_le_sup_left
    ((Submodule.smul_mono_left hI).trans (Ring.jacobson_smul_top_le R M)) N

/-- The usual Jacobson-radical specialization of noncommutative Nakayama. -/
theorem eq_top_of_sup_jacobson_smul [Module.Finite R M]
    (N : Submodule R M)
    (h : N ⊔ Ring.jacobson R • (⊤ : Submodule R M) = ⊤) : N = ⊤ :=
  eq_top_of_sup_ideal_smul (Ring.jacobson R) le_rfl N h

/-- The quotient by the literal ideal image. -/
abbrev IdealTop (I : Ideal R) (M : Type v) [AddCommGroup M] [Module R M] :=
  M ⧸ I • (⊤ : Submodule R M)

/-- The actual quotient map, semilinear over the scalar quotient homomorphism. -/
def idealTopMap (I : Ideal R) [I.IsTwoSided] :
    M →ₛₗ[Ideal.Quotient.mk I] IdealTop I M where
  toFun := (I • (⊤ : Submodule R M)).mkQ
  map_add' := map_add _
  map_smul' := fun _ _ ↦ rfl

@[simp] theorem idealTopMap_apply (I : Ideal R) [I.IsTwoSided] (x : M) :
    idealTopMap (M := M) I x = Submodule.Quotient.mk x := rfl

@[simp] theorem idealTopMap_smul (I : Ideal R) [I.IsTwoSided] (a : R) (x : M) :
    idealTopMap (M := M) I (a • x) =
      Ideal.Quotient.mk I a • idealTopMap (M := M) I x := rfl

/-- The quotient map is surjective, on the actual quotient representatives. -/
theorem idealTopMap_surjective (I : Ideal R) [I.IsTwoSided] :
    Function.Surjective (idealTopMap (M := M) I) :=
  (I • (⊤ : Submodule R M)).mkQ_surjective

/-- The semilinear quotient map has exactly the ideal image as its kernel. -/
theorem idealTopMap_ker (I : Ideal R) [I.IsTwoSided] :
    LinearMap.ker (idealTopMap (M := M) I) = I • (⊤ : Submodule R M) := by
  ext x
  exact Submodule.Quotient.mk_eq_zero _

/-- Passing to the quotient detects whether a submodule is the whole module. -/
theorem map_eq_top_iff [Module.Finite R M]
    (I : Ideal R) [I.IsTwoSided] (hI : I ≤ Ring.jacobson R) (N : Submodule R M) :
    N.map (idealTopMap (M := M) I) = ⊤ ↔ N = ⊤ := by
  constructor
  · intro h
    have hc := congrArg (Submodule.comap (idealTopMap (M := M) I)) h
    rw [Submodule.comap_map_eq, Submodule.comap_top, idealTopMap_ker] at hc
    exact eq_top_of_sup_ideal_smul I hI N hc
  · intro h
    rw [h, Submodule.map_top, LinearMap.range_eq_top.mpr (idealTopMap_surjective I)]

end Komorebi.PaperICompletion7.Nakayama
