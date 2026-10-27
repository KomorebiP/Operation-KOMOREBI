import PaperXI.OddSymplectic
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.Algebra.Module.Submodule.LinearMap
import Mathlib.Algebra.BigOperators.Module

/-! Actual restricted forms and automorphisms on an internal orthogonal
family. Nondegeneracy is derived from orthogonality and spanning. Inverse
invariance is derived from finite-dimensionality and forward invariance. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OrthogonalSummands
open scoped BigOperators

variable {K V ι : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- The restriction of the actual alternating form remains alternating. -/
theorem restricted_isAlt (b : LinearMap.BilinForm K V) (ha : b.IsAlt)
    (S : Submodule K V) : (b.restrict S).IsAlt := fun x => ha x

/-- Every summand in an orthogonal spanning family inherits nondegeneracy.
Neither finite-dimensionality nor an assumed restricted form is used. -/
theorem restricted_form_nondegenerate (b : LinearMap.BilinForm K V) (hn : b.Nondegenerate)
    (S : ι → Submodule K V) (hspan : (⨆ i, S i) = ⊤)
    (horth : ∀ i j, i ≠ j → ∀ x ∈ S i, ∀ y ∈ S j, b x y = 0) (i : ι) :
    (b.restrict (S i)).Nondegenerate := by
  constructor
  · intro x hx
    apply Subtype.ext
    apply hn.1 (x : V)
    have hk : (⨆ j, S j) ≤ (b x).ker := by
      apply iSup_le
      intro j y hy
      change b x y = 0
      by_cases hji : j = i
      · subst j
        exact hx ⟨y, hy⟩
      · exact horth i j (Ne.symm hji) x x.property y hy
    rw [hspan] at hk
    intro y
    exact hk (Submodule.mem_top : y ∈ (⊤ : Submodule K V))
  · intro x hx
    apply Subtype.ext
    apply hn.2 (x : V)
    have hk : (⨆ j, S j) ≤ (b.flip x).ker := by
      apply iSup_le
      intro j y hy
      change b y x = 0
      by_cases hji : j = i
      · subst j
        exact hx ⟨y, hy⟩
      · exact horth j i hji y hy x x.property
    rw [hspan] at hk
    intro y
    exact hk (Submodule.mem_top : y ∈ (⊤ : Submodule K V))

/-- A finite internal sum equivalence with the literal summation equation
supplies the spanning hypothesis used above. -/
theorem iSup_eq_top_of_equiv_sum [Fintype ι] (S : ι → Submodule K V)
    (E : (∀ i, S i) ≃ₗ[K] V) (hE : ∀ x, E x = ∑ i, (x i : V)) :
    (⨆ i, S i) = ⊤ := by
  apply top_unique
  intro v _
  obtain ⟨x, rfl⟩ := E.surjective v
  rw [hE]
  exact Submodule.sum_mem _ (fun i _ => (le_iSup S i) (x i).property)

variable [FiniteDimensional K V]

/-- Actual restriction of an invertible ambient map to a forward-invariant
subspace. Surjectivity of the restriction is proved from its injectivity. -/
def restrictionEquiv (g : V ≃ₗ[K] V) (S : Submodule K V)
    (hg : ∀ x ∈ S, g x ∈ S) : S ≃ₗ[K] S :=
  LinearEquiv.ofInjectiveEndo (g.toLinearMap.restrict hg) (by
    intro x y h
    apply Subtype.ext
    exact g.injective (congrArg Subtype.val h))

@[simp] theorem restrictionEquiv_coe (g : V ≃ₗ[K] V) (S : Submodule K V)
    (hg : ∀ x ∈ S, g x ∈ S) (x : S) : (restrictionEquiv g S hg x : V) = g x := rfl

/-- The inverse of the restricted equivalence is the actual ambient inverse. -/
theorem restrictionEquiv_symm_coe (g : V ≃ₗ[K] V) (S : Submodule K V)
    (hg : ∀ x ∈ S, g x ∈ S) (x : S) :
    ((restrictionEquiv g S hg).symm x : V) = g.symm x := by
  apply g.injective
  rw [g.apply_symm_apply]
  exact congrArg Subtype.val ((restrictionEquiv g S hg).apply_symm_apply x)

/-- Forward invariance under an invertible finite-dimensional map also gives
inverse invariance; it is not an extra source hypothesis. -/
theorem inverse_mem (g : V ≃ₗ[K] V) (S : Submodule K V)
    (hg : ∀ x ∈ S, g x ∈ S) (x : V) (hx : x ∈ S) : g.symm x ∈ S := by
  rw [← restrictionEquiv_symm_coe g S hg ⟨x, hx⟩]
  exact ((restrictionEquiv g S hg).symm ⟨x, hx⟩).property

/-- Preservation of the ambient form gives preservation of its actual restriction. -/
theorem restrictionEquiv_form (b : LinearMap.BilinForm K V) (g : V ≃ₗ[K] V)
    (hform : ∀ x y, b (g x) (g y) = b x y)
    (S : Submodule K V) (hg : ∀ x ∈ S, g x ∈ S) (x y : S) :
    b.restrict S (restrictionEquiv g S hg x) (restrictionEquiv g S hg y) =
      b.restrict S x y := hform x y

/-- A fixed-point-free ambient automorphism remains so on each invariant summand. -/
theorem restrictionEquiv_fixed_eq_zero (g : V ≃ₗ[K] V)
    (hfix : ∀ x, g x = x → x = 0) (S : Submodule K V)
    (hg : ∀ x ∈ S, g x ∈ S) (x : S) (hx : restrictionEquiv g S hg x = x) : x = 0 := by
  apply Subtype.ext
  exact hfix x (congrArg Subtype.val hx)

/-- Each actual orthogonal summand has even dimension under the odd-characteristic
symplectic hypotheses. -/
theorem restricted_even_finrank (b : LinearMap.BilinForm K V) (ha : b.IsAlt)
    (hn : b.Nondegenerate) (h2 : (2 : K) ≠ 0) (S : ι → Submodule K V)
    (hspan : (⨆ i, S i) = ⊤)
    (horth : ∀ i j, i ≠ j → ∀ x ∈ S i, ∀ y ∈ S j, b x y = 0) (i : ι) :
    Even (Module.finrank K (S i)) :=
  OddSymplectic.even_finrank (b.restrict (S i)) (restricted_isAlt b ha (S i))
    (restricted_form_nondegenerate b hn S hspan horth i) h2

end PaperXI.OrthogonalSummands
