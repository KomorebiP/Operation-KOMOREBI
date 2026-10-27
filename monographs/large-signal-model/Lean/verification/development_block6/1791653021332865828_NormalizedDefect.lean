import KomorebiLSM.PositivePriors

/-! P36: likelihood error and normalized state error are distinct.
The all-interior-prior converse is derived using explicit spanning priors. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteInstruments
open scoped BigOperators
open FiniteBayes
universe u v

section Algebra
variable {E : Type*} [AddCommGroup E] [Module ℝ E]

/-- The rank-one mass component is removed after normalization. -/
def oblique (l : E →ₗ[ℝ] ℝ) (q : E) : E →ₗ[ℝ] E :=
  LinearMap.id - l.smulRight q

@[simp] theorem oblique_apply (l : E →ₗ[ℝ] ℝ) (q x : E) :
    oblique l q x = x - l x • q := rfl

theorem oblique_null (l : E →ₗ[ℝ] ℝ) (q : E) (hq : l q = 1) :
    oblique l q q = 0 := by
  simp [hq]

theorem oblique_mass_zero (l : E →ₗ[ℝ] ℝ) (q : E) (hq : l q = 1) (x : E) :
    l (oblique l q x) = 0 := by
  simp [map_sub, hq]

theorem oblique_idempotent (l : E →ₗ[ℝ] ℝ) (q : E) (hq : l q = 1) :
    (oblique l q).comp (oblique l q) = oblique l q := by
  ext x
  change oblique l q (oblique l q x) = oblique l q x
  rw [oblique_apply, oblique_mass_zero l q hq, zero_smul, sub_zero]

variable {X : Type*} [AddCommGroup X] [Module ℝ X]

def closureDefect (R : X →ₗ[ℝ] E) (M : X →ₗ[ℝ] X) (B : E →ₗ[ℝ] E) :
    X →ₗ[ℝ] E := R.comp M - B.comp R

@[simp] theorem closureDefect_apply (R : X →ₗ[ℝ] E) (M : X →ₗ[ℝ] X)
    (B : E →ₗ[ℝ] E) (p : X) : closureDefect R M B p = R (M p) - B (R p) := rfl

theorem closureDefect_zero_iff (R : X →ₗ[ℝ] E) (M : X →ₗ[ℝ] X)
    (B : E →ₗ[ℝ] E) : closureDefect R M B = 0 ↔ R.comp M = B.comp R := sub_eq_zero

theorem normalize_transport (R : X →ₗ[ℝ] E) (mu : X →ₗ[ℝ] ℝ)
    (l : E →ₗ[ℝ] ℝ) (h : l.comp R = mu) (x : X) :
    R (normalize mu x) = normalize l (R x) := by
  have hx : l (R x) = mu x := congrArg (fun f : X →ₗ[ℝ] ℝ => f x) h
  simp only [normalize, map_smul, hx]

theorem likelihood_defect (R : X →ₗ[ℝ] E) (M : X →ₗ[ℝ] X) (B : E →ₗ[ℝ] E)
    (mu : X →ₗ[ℝ] ℝ) (l : E →ₗ[ℝ] ℝ) (h : l.comp R = mu) (p : X) :
    mu (M p) - l (B (R p)) = l (closureDefect R M B p) := by
  have hx : l (R (M p)) = mu (M p) := congrArg (fun f : X →ₗ[ℝ] ℝ => f (M p)) h
  simp [hx]

end Algebra

section CoordinateIdentity
variable {J : Type v}

/-- A vector identity with both denominators declared nonzero. -/
theorem normalized_difference (l : (J → ℝ) →ₗ[ℝ] ℝ) (u v : J → ℝ)
    (hu : l u ≠ 0) (hv : l v ≠ 0) :
    normalize l u - normalize l v =
      (l u)⁻¹ • oblique l (normalize l v) (u-v) := by
  funext j
  simp only [normalize, oblique_apply, map_sub, Pi.sub_apply, Pi.smul_apply, smul_eq_mul]
  field_simp
  ring

/-- P36's vector defect, including transport from the fine normalized state. -/
theorem normalized_closure_defect {I : Type u} [Fintype I]
    (R : (I → ℝ) →ₗ[ℝ] (J → ℝ)) (M : (I → ℝ) →ₗ[ℝ] (I → ℝ))
    (B : (J → ℝ) →ₗ[ℝ] (J → ℝ)) (l : (J → ℝ) →ₗ[ℝ] ℝ)
    (hmass : l.comp R = mass) (p : I → ℝ)
    (ha : 0 < mass (M p)) (hb : 0 < l (B (R p))) :
    R (normalize mass (M p)) - normalize l (B (R p)) =
      (mass (M p))⁻¹ • oblique l (normalize l (B (R p))) (closureDefect R M B p) := by
  have hx : l (R (M p)) = mass (M p) :=
    congrArg (fun f : (I → ℝ) →ₗ[ℝ] ℝ => f (M p)) hmass
  rw [normalize_transport R mass l hmass]
  have hd := normalized_difference l (R (M p)) (B (R p))
    (by rw [hx]; exact ne_of_gt ha) (ne_of_gt hb)
  simpa only [hx, closureDefect_apply] using hd

end CoordinateIdentity

section Converse
variable {I : Type u} [Fintype I] [Nonempty I]
variable {E : Type*} [AddCommGroup E] [Module ℝ E]

/-- Matching likelihood and posterior on every interior belief forces actual closure. -/
theorem closure_of_likelihood_and_posterior
    (M : Matrix I I ℝ) (hM : ∀ j i, 0 ≤ M j i) (h0 : M ≠ 0)
    (R : (I → ℝ) →ₗ[ℝ] E) (B : E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
    (hlik : ∀ p, IsStrictPrior p → mass (M.mulVecLin p) = l (B (R p)))
    (hpost : ∀ p, IsStrictPrior p →
      R (normalize mass (M.mulVecLin p)) = normalize l (B (R p))) :
    R.comp M.mulVecLin = B.comp R := by
  apply linearMap_eq_of_strict_priors
  intro p hp
  have ha := nonnegative_branch_mass_pos M hM h0 p hp.2
  have hb : l (B (R p)) ≠ 0 := by rw [← hlik p hp]; exact ne_of_gt ha
  change R (M.mulVecLin p) = B (R p)
  calc
    R (M.mulVecLin p) = R (mass (M.mulVecLin p) • normalize mass (M.mulVecLin p)) :=
      congrArg R (recover_from_normalize mass _ (ne_of_gt ha)).symm
    _ = mass (M.mulVecLin p) • R (normalize mass (M.mulVecLin p)) := map_smul R _ _
    _ = l (B (R p)) • normalize l (B (R p)) := by rw [hlik p hp, hpost p hp]
    _ = B (R p) := recover_from_normalize l _ hb

end Converse

section Packet
variable {X : Type*} [AddCommGroup X] [Module ℝ X]

/-- The probability defect reduces to the omitted-to-retained transfer block. -/
theorem closureDefect_projected (P M : X →ₗ[ℝ] X) (hP : P.comp P = P) :
    closureDefect P M (P.comp (M.comp P)) = P.comp (M.comp (LinearMap.id-P)) := by
  ext x
  have hx : P (P x) = P x := congrArg (fun F : X →ₗ[ℝ] X => F x) hP
  simp [closureDefect, LinearMap.comp_apply, hx, map_sub]

end Packet
end Komorebi.LSM.FiniteInstruments
