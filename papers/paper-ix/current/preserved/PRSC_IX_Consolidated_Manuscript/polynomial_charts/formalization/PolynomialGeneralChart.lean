module
public import PolynomialParameterChart
public import PolynomialCoordinateReorder

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialGeneralChart
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialPadicLift Komorebi.PolynomialLocalSurjective
open Komorebi.PolynomialParameterSystem Komorebi.PolynomialParameterChart
open Komorebi.PolynomialCoordinateReorder
variable {d e q : ℕ}

/-- Coordinate renaming identifies the entire original and reordered root loci. -/
def reorderRootHomeomorph (p L : ℕ) [Fact (Nat.Prime p)]
    (σ : Equiv.Perm (Fin d)) (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :
    {a : residueBall p L x // padicEval p F a.val = 0} ≃ₜ
      {a : residueBall p L (reorderPoint σ x) // padicEval p (reorderSystem σ F) a.val = 0} where
  toFun a := ⟨⟨reorderPoint σ a.val.val, fun i => a.val.property (σ i)⟩, by
    rw [padicEval_reorder_at]
    exact a.property⟩
  invFun a := ⟨⟨reorderPoint σ.symm a.val.val, by
    intro i
    simpa only [reorderPoint, Equiv.apply_symm_apply] using a.val.property (σ.symm i)⟩, by
    rw [← padicEval_reorder]
    exact a.property⟩
  left_inv a := by
    apply Subtype.ext
    apply Subtype.ext
    exact reorderPoint_inverse σ a.val.val
  right_inv a := by
    apply Subtype.ext
    apply Subtype.ext
    exact reorderPoint_inverse' σ a.val.val
  continuous_toFun := by
    apply Continuous.subtype_mk
    apply Continuous.subtype_mk
    exact (continuous_reorderPoint σ).comp
      (continuous_subtype_val.comp continuous_subtype_val)
  continuous_invFun := by
    apply Continuous.subtype_mk
    apply Continuous.subtype_mk
    exact (continuous_reorderPoint σ.symm).comp
      (continuous_subtype_val.comp continuous_subtype_val)

/-- A full surjective rectangular Jacobian supplies its own solved coordinates.
The original root locus is homeomorphic to the remaining-coordinate ball,
with its actual coordinate projection as inverse and exact congruence reflection. -/
theorem exists_parameter_homeomorph (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin (e + q)) ℤ) (x : Fin (e + q) → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    ∃ σ : Equiv.Perm (Fin (e + q)),
    ∃ h : residueBall p L (freePart (reorderPoint σ x)) ≃ₜ
        {z : residueBall p L x // padicEval p F z.val = 0},
      (∀ z, (h.symm z).val = freePart (reorderPoint σ z.val.val)) ∧
      (∀ N t u,
        (∀ j, (p : ℤ_[p])^N ∣ t.val j - u.val j) ↔
        (∀ i, (p : ℤ_[p])^N ∣ (h t).val.val i - (h u).val.val i)) := by
  obtain ⟨σ, hσ⟩ := exists_reorder_solvedJacobian_surjective p F x hJ
  have hxσ : ∀ i, (p : ℤ)^L ∣ evalSystem (reorderSystem σ F) (reorderPoint σ x) i := by
    simpa only [evalSystem_reorder_at] using hx
  let h₁ := parameterHomeomorph p L hL (reorderSystem σ F) (reorderPoint σ x) hxσ hσ
  let h₂ := reorderRootHomeomorph p L σ F x
  let h := h₁.trans h₂.symm
  refine ⟨σ, h, ?_, ?_⟩
  · intro z
    rfl
  · intro N t u
    constructor
    · intro htu i
      exact chartPoint_congruent p L N hL (reorderSystem σ F) (reorderPoint σ x)
        hxσ hσ t u htu (σ.symm i)
    · intro htu j
      have hh := htu (σ (Fin.natAdd e j))
      change (p : ℤ_[p])^N ∣
        (chartPoint p L hL (reorderSystem σ F) (reorderPoint σ x) hxσ hσ t).val
          (σ.symm (σ (Fin.natAdd e j))) -
        (chartPoint p L hL (reorderSystem σ F) (reorderPoint σ x) hxσ hσ u).val
          (σ.symm (σ (Fin.natAdd e j))) at hh
      simp only [Equiv.symm_apply_apply] at hh
      have ht := congrFun (chartPoint_free p L hL (reorderSystem σ F)
        (reorderPoint σ x) hxσ hσ t) j
      have hu := congrFun (chartPoint_free p L hL (reorderSystem σ F)
        (reorderPoint σ x) hxσ hσ u) j
      change (chartPoint p L hL (reorderSystem σ F) (reorderPoint σ x) hxσ hσ t).val
        (Fin.natAdd e j) = t.val j at ht
      change (chartPoint p L hL (reorderSystem σ F) (reorderPoint σ x) hxσ hσ u).val
        (Fin.natAdd e j) = u.val j at hu
      rwa [ht, hu] at hh

#print axioms reorderRootHomeomorph
#print axioms exists_parameter_homeomorph

end Komorebi.PolynomialGeneralChart
