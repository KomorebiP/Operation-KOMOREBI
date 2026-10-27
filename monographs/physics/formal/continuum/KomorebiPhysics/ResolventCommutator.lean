module
public import KomorebiPhysics.ResolventDomain

/-! Section 6.7 (6.53)-(6.55). The domain-correct commutator identity
and operator-norm certificate. The bounded packet need not be a projector. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace ResolventDomain

variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]

/-- Receiving-first operator commutator: [A,P]=AP-PA. -/
def commutator (A P : H →L[ℂ] H) : H →L[ℂ] H := A * P - P * A

theorem commutator_apply (A P : H →L[ℂ] H) (x : H) :
    commutator A P x = A (P x) - P (A x) := rfl

theorem commutator_swap (A P : H →L[ℂ] H) :
    commutator P A = -commutator A P := by
  simp only [commutator, neg_sub]

namespace Certificate
variable {T : H →ₗ.[ℂ] H} {z : ℂ} (R : Certificate T z)
variable {P : H →L[ℂ] H} (B : BoundedCommutator T P)

/-- The domain computation before taking the bounded-operator difference. -/
theorem packet_resolvent (x : H) :
    P (R.op x) = R.op (P x) + R.op (B.bound (R.op x)) := by
  have h := congrArg R.op (B.shifted_intertwining z (R.lift x))
  simpa only [R.left_inverse, restrict_coe, R.shifted_lift, R.lift_coe, map_add] using h

/-- Literal negative sign, with no illicit application of T off its domain. -/
theorem commutator_vector (x : H) :
    commutator R.op P x = -R.op (B.bound (R.op x)) := by
  rw [commutator_apply, R.packet_resolvent B x]
  abel

theorem commutator_identity :
    commutator R.op P = -(R.op * B.bound * R.op) := by
  ext x
  exact R.commutator_vector B x

/-- The product estimate is proved for the actual bounded extension. -/
theorem commutator_norm_bound :
    ‖commutator R.op P‖ ≤ ‖R.op‖ ^ 2 * ‖B.bound‖ := by
  rw [R.commutator_identity B, norm_neg]
  calc
    _ ≤ (‖R.op‖ * ‖B.bound‖) * ‖R.op‖ :=
      (norm_mul_le _ _).trans (mul_le_mul_of_nonneg_right (norm_mul_le _ _) (norm_nonneg _))
    _ = _ := by ring

theorem commutator_state_bound (x : H) :
    ‖commutator R.op P x‖ ≤ ‖R.op‖ ^ 2 * ‖B.bound‖ * ‖x‖ :=
  ((commutator R.op P).le_opNorm x).trans
    (mul_le_mul_of_nonneg_right (R.commutator_norm_bound B) (norm_nonneg x))

/-- Quantitative certificate for any supplied upper resolvent norm bound. -/
theorem commutator_norm_bound_of_le {r : ℝ} (hr : ‖R.op‖ ≤ r) :
    ‖commutator R.op P‖ ≤ r ^ 2 * ‖B.bound‖ := by
  apply (R.commutator_norm_bound B).trans
  apply mul_le_mul_of_nonneg_right _ (norm_nonneg _)
  exact pow_le_pow_left₀ (norm_nonneg _) hr 2

theorem commutator_zero_of_bound_zero (h : B.bound = 0) :
    commutator R.op P = 0 := by
  rw [R.commutator_identity B, h, mul_zero, zero_mul, neg_zero]

/-- If the resolvent commutes, its range identifies the preserved T-domain. -/
theorem preserves_of_commutator_zero (h : commutator R.op P = 0)
    (x : T.domain) : P x ∈ T.domain := by
  have hh := congrArg (fun A : H →L[ℂ] H => A (shifted T z x)) h
  simp only [commutator_apply, R.left_inverse, zero_apply] at hh
  have he : R.op (P (shifted T z x)) = P x := sub_eq_zero.mp hh
  rw [← he]
  exact R.range_mem _

/-- Commutation of one genuine resolvent implies commutation on D(T). -/
theorem action_commutes_of_commutator_zero (h : commutator R.op P = 0)
    (x : T.domain) :
    T (restrict T P (R.preserves_of_commutator_zero h) x) = P (T x) := by
  have hh := congrArg (fun A : H →L[ℂ] H => A (shifted T z x)) h
  simp only [commutator_apply, R.left_inverse, zero_apply] at hh
  have he : R.lift (P (shifted T z x)) =
      restrict T P (R.preserves_of_commutator_zero h) x :=
    Subtype.ext (sub_eq_zero.mp hh)
  have hs := R.shifted_lift (P (shifted T z x))
  rw [he] at hs
  simp only [shifted_apply, restrict_coe, map_sub, map_smul] at hs
  exact sub_left_inj.mp hs

/-- The converse needs only invariance and actual zero commutator on the domain. -/
theorem commutator_zero_of_action_commutes
    (hP : ∀ x : T.domain, P x ∈ T.domain)
    (hc : ∀ x : T.domain, T (restrict T P hP x) = P (T x)) :
    commutator R.op P = 0 := by
  let B0 : BoundedCommutator T P := {
    preserves := hP
    bound := 0
    agrees := fun x => by simp only [hc x, sub_self, zero_apply] }
  exact R.commutator_zero_of_bound_zero B0 rfl

/-- Zero-resolvent leakage is equivalent to domain invariance plus reduction. -/
theorem commutator_zero_iff :
    commutator R.op P = 0 ↔
      ∃ hP : ∀ x : T.domain, P x ∈ T.domain,
        ∀ x : T.domain, T (restrict T P hP x) = P (T x) := by
  constructor
  · intro h
    exact ⟨R.preserves_of_commutator_zero h, R.action_commutes_of_commutator_zero h⟩
  · rintro ⟨hP, hc⟩
    exact R.commutator_zero_of_action_commutes hP hc

/-- A nonzero domain commutator cannot be hidden by the resolvent. -/
theorem commutator_ne_zero_of_action_ne (x : T.domain)
    (hx : T (restrict T P B.preserves x) ≠ P (T x)) :
    commutator R.op P ≠ 0 := by
  intro h
  exact hx (R.action_commutes_of_commutator_zero h x)

end Certificate
end ResolventDomain
end KomorebiPhysics
