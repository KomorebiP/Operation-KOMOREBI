import Komorebi.SufficientResolution.ContinuousFlow

/-!
# Exponential transfer is equivalent to transfer of all generator powers

The forward implication differentiates actual Banach-algebra exponential jets.
The reverse implication transports the convergent exponential series through
bounded linear maps. No finite-time sampling hypothesis replaces these identities.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousFlow

variable {X Z W : Type*}
variable [NormedAddCommGroup X] [NormedSpace ℝ X] [CompleteSpace X]
variable [NormedAddCommGroup Z] [NormedSpace ℝ Z] [CompleteSpace Z]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]

 theorem hasDerivAt_mapped_jet (L : X →L[ℝ] X) (K : (X →L[ℝ] X) →L[ℝ] W)
    (n : ℕ) (t : ℝ) :
    HasDerivAt (fun s => K (jet L n s)) (K (jet L (n+1) t)) t := by
  simpa using (hasDerivAt_const t K).clm_apply (hasDerivAt_jet L n t)

/-- An all-time equality of observed exponentials determines every observed jet. -/
 theorem mapped_jets_eq_of_flow_eq (L : X →L[ℝ] X) (D : Z →L[ℝ] Z)
    (K : (X →L[ℝ] X) →L[ℝ] W) (J : (Z →L[ℝ] Z) →L[ℝ] W)
    (h : ∀ t, K (flow L t) = J (flow D t)) :
    ∀ n t, K (jet L n t) = J (jet D n t) := by
  intro n
  induction n with
  | zero => simpa using h
  | succ n ih =>
    intro t
    have hl := hasDerivAt_mapped_jet L K n t
    have hr := hasDerivAt_mapped_jet D J n t
    have heq : (fun s => K (jet L n s)) = (fun s => J (jet D n s)) := funext ih
    rw [heq] at hl
    exact hl.unique hr

 theorem mapped_powers_eq_of_flow_eq (L : X →L[ℝ] X) (D : Z →L[ℝ] Z)
    (K : (X →L[ℝ] X) →L[ℝ] W) (J : (Z →L[ℝ] Z) →L[ℝ] W)
    (h : ∀ t, K (flow L t) = J (flow D t)) (n : ℕ) :
    K (L^n) = J (D^n) := by
  simpa using mapped_jets_eq_of_flow_eq L D K J h n 0

/-- The observed exponential is the convergent series of observed powers. -/
 theorem mapped_flow_hasSum (L : X →L[ℝ] X) (K : (X →L[ℝ] X) →L[ℝ] W) (t : ℝ) :
    HasSum (fun n : ℕ => ((n.factorial : ℝ)⁻¹ * t^n) • K (L^n)) (K (flow L t)) := by
  have h := K.hasSum (NormedSpace.exp_series_hasSum_exp' (𝕂 := ℝ) (t • L))
  simpa [flow, smul_pow, map_smul, smul_smul] using! h

 theorem mapped_flow_eq_of_powers_eq (L : X →L[ℝ] X) (D : Z →L[ℝ] Z)
    (K : (X →L[ℝ] X) →L[ℝ] W) (J : (Z →L[ℝ] Z) →L[ℝ] W)
    (h : ∀ n, K (L^n) = J (D^n)) (t : ℝ) :
    K (flow L t) = J (flow D t) := by
  have hl := mapped_flow_hasSum L K t
  have hr := mapped_flow_hasSum D J t
  simp_rw [h] at hl
  exact hl.unique hr

 theorem mapped_flow_eq_iff_powers_eq (L : X →L[ℝ] X) (D : Z →L[ℝ] Z)
    (K : (X →L[ℝ] X) →L[ℝ] W) (J : (Z →L[ℝ] Z) →L[ℝ] W) :
    (∀ t, K (flow L t) = J (flow D t)) ↔ (∀ n, K (L^n) = J (D^n)) :=
  ⟨mapped_powers_eq_of_flow_eq L D K J, mapped_flow_eq_of_powers_eq L D K J⟩

/-- Equality to zero is detected by all powers, not finitely sampled times. -/
 theorem mapped_flow_zero_iff (L : X →L[ℝ] X) (K : (X →L[ℝ] X) →L[ℝ] W) :
    (∀ t, K (flow L t) = 0) ↔ (∀ n, K (L^n) = 0) := by
  simpa using mapped_flow_eq_iff_powers_eq L L K (0 : (X →L[ℝ] X) →L[ℝ] W)

variable {Y : Type*} [NormedAddCommGroup Y] [NormedSpace ℝ Y]

/-- A bounded observation of an operator through input and output channels. -/
def sandwich (B : X →L[ℝ] W) (G : Y →L[ℝ] X) :
    (X →L[ℝ] X) →L[ℝ] (Y →L[ℝ] W) :=
  (ContinuousLinearMap.compL ℝ Y X W B).comp
    ((ContinuousLinearMap.compL ℝ Y X X).flip G)

omit [CompleteSpace X] in
@[simp] theorem sandwich_apply (B : X →L[ℝ] W) (G : Y →L[ℝ] X) (T : X →L[ℝ] X) :
    sandwich B G T = B.comp (T.comp G) := rfl

 theorem sandwich_flow_zero_iff (B : X →L[ℝ] W) (D : X →L[ℝ] X) (G : Y →L[ℝ] X) :
    (∀ t, B.comp ((flow D t).comp G) = 0) ↔
      (∀ n : ℕ, B.comp ((D^n).comp G) = 0) :=
  mapped_flow_zero_iff D (sandwich B G)

/-- Continuous prepared compression is equivalent to compression of all powers. -/
 theorem compressed_flow_iff_powers (C : X →L[ℝ] Z) (R : Z →L[ℝ] X)
    (L : X →L[ℝ] X) (A : Z →L[ℝ] Z) :
    (∀ t, C.comp ((flow L t).comp R) = flow A t) ↔
      (∀ n : ℕ, C.comp ((L^n).comp R) = A^n) := by
  simpa using mapped_flow_eq_iff_powers_eq L A (sandwich C R)
    (ContinuousLinearMap.id ℝ (Z →L[ℝ] Z))

omit [CompleteSpace Z] in
/-- Continuous-time nonmultiplicativity is exactly a hidden excursion and return. -/
 theorem compressed_flow_defect (C : X →L[ℝ] Z) (R : Z →L[ℝ] X)
    (L : X →L[ℝ] X) (s t : ℝ) :
    C.comp ((flow L (s+t)).comp R) -
      (C.comp ((flow L s).comp R)).comp (C.comp ((flow L t).comp R)) =
    C.comp ((flow L s).comp ((1 - R.comp C).comp ((flow L t).comp R))) := by
  ext x
  simp only [flow_add, sub_apply, ContinuousLinearMap.comp_apply,
    mul_apply_eq_comp, one_apply_eq_self, map_sub]

end Komorebi.SufficientResolution.ContinuousFlow
