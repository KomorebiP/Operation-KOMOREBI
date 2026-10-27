import PaperXI.ScalarRepresentation112
import PaperXI.CyclicDefect113

/-! Honest actions on an actual group induce honest scalar-pushout actions.
The section phase and its multiplication law are conclusions. The original
theta, its literal kernel subgroup, and the quotient labels are retained. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualScalarLift113
open ScalarRepresentation112 ScalarCocycle112 CyclicDefect113

variable {G A : Type*} [Group G] [CommGroup A]
  (D : Subgroup G) [D.Normal] (θ : D →* ℂˣ)
  (hinv : TypeSideDescent.Invariant D θ)
  (q : G →* A) (hker : q.ker = D)
  (t : A → G) (ht : ∀ a, q (t a) = a) (ht1 : t 1 = 1)

/-- The scalar pushout map is derived from the actual normalized section. -/
def actualPushout : G →* Extension (actualScalarCocycle D θ hinv q hker t ht ht1) where
  toFun g := ⟨sectionScalar D θ q hker t ht g, q g⟩
  map_one' := by
    apply Extension.ext
    · exact sectionScalar_one D θ q hker t ht ht1
    · exact q.map_one
  map_mul' g h := by
    apply Extension.ext
    · exact sectionScalar_mul D θ hinv q hker t ht g h
    · exact q.map_mul g h

@[simp] theorem actualPushout_section (a : A) :
    actualPushout D θ hinv q hker t ht ht1 (t a) =
      Extension.sectionOf (actualScalarCocycle D θ hinv q hker t ht ht1) a := by
  apply Extension.ext
  · exact sectionScalar_section D θ q hker t ht a
  · exact ht a

@[simp] theorem actualPushout_subgroup (d : D) :
    actualPushout D θ hinv q hker t ht ht1 (d : G) =
      Extension.scalarInclusion (actualScalarCocycle D θ hinv q hker t ht ht1) (θ d) := by
  apply Extension.ext
  · exact sectionScalar_on_subgroup D θ q hker t ht ht1 d
  · change (d : G) ∈ q.ker
    rw [hker]
    exact d.property

variable (α : G ≃* G) (β : A ≃* A) (hq : ∀ g, q (α g) = β (q g))

/-- The subgroup map is induced by the actual automorphism and exact kernel. -/
def subgroupMap : D →* D where
  toFun d := ⟨α (d : G), by
    have hd : q (d : G) = 1 := by
      change (d : G) ∈ q.ker
      rw [hker]
      exact d.property
    have hm : α (d : G) ∈ q.ker := by
      change q (α (d : G)) = 1
      rw [hq, hd, map_one]
    simpa only [hker] using hm⟩
  map_one' := by apply Subtype.ext; exact α.map_one
  map_mul' d e := by apply Subtype.ext; exact α.map_mul (d : G) (e : G)

variable (hθ : ∀ d : D, θ (subgroupMap D q hker α β hq d) = θ d)

/-- The phase is the original theta of the actual section discrepancy. -/
def actualPhase (a : A) : ℂˣ := sectionScalar D θ q hker t ht (α (t a))

omit [D.Normal] in
include ht1 in
@[simp] theorem actualPhase_one : actualPhase D θ q hker t ht α 1 = 1 := by
  simp only [actualPhase, ht1, map_one, sectionScalar_one D θ q hker t ht ht1]

include hθ hinv ht1 in
/-- Scalar covariance follows from actual theta preservation, not from a
premise about a projective section or an already corrected cochain. -/
theorem sectionScalar_action (g : G) :
    sectionScalar D θ q hker t ht (α g) =
      sectionScalar D θ q hker t ht g * actualPhase D θ q hker t ht α (q g) := by
  let d := sectionResidue D q hker t ht g
  have hg : g = (d : G) * t (q g) := by
    simp only [d, sectionResidue]
    group
  have hdq : q (α (d : G)) = 1 := by
    rw [hq]
    have hd : q (d : G) = 1 := by
      change (d : G) ∈ q.ker
      rw [hker]
      exact d.property
    rw [hd, map_one]
  have hdθ : sectionScalar D θ q hker t ht (α (d : G)) = θ d := by
    change sectionScalar D θ q hker t ht
      (subgroupMap D q hker α β hq d : G) = θ d
    rw [sectionScalar_on_subgroup D θ q hker t ht ht1, hθ]
  calc
    sectionScalar D θ q hker t ht (α g) =
        sectionScalar D θ q hker t ht (α (d : G) * α (t (q g))) := by
      rw [← map_mul, ← hg]
    _ = θ d * actualPhase D θ q hker t ht α (q g) := by
      rw [sectionScalar_mul D θ hinv, hdθ, hdq,
        sectionCocycle_one_left D θ q hker t ht ht1, mul_one]
      rfl
    _ = _ := rfl

include hθ hinv ht1 in
theorem actualPhase_mul (a b : A) :
    sectionCocycle D θ q hker t ht a b * actualPhase D θ q hker t ht α (a*b) =
      actualPhase D θ q hker t ht α a * actualPhase D θ q hker t ht α b *
        sectionCocycle D θ q hker t ht (β a) (β b) := by
  have h := sectionScalar_action D θ hinv q hker t ht ht1 α β hq hθ (t a * t b)
  rw [map_mul α, sectionScalar_mul D θ hinv, hq, hq, ht, ht,
    map_mul q, ht, ht] at h
  exact h.symm

/-- An actual automorphism induces an automorphism of the scalar pushout. -/
def actualLift : ScalarLift (actualScalarCocycle D θ hinv q hker t ht ht1) β where
  action := {
    toFun x := ⟨x.scalar * actualPhase D θ q hker t ht α x.base, β x.base⟩
    invFun y := ⟨y.scalar / actualPhase D θ q hker t ht α (β.symm y.base), β.symm y.base⟩
    left_inv x := by apply Extension.ext <;> simp
    right_inv y := by apply Extension.ext <;> simp
    map_mul' x y := by
      apply Extension.ext
      · change (x.scalar * y.scalar * sectionCocycle D θ q hker t ht x.base y.base) *
          actualPhase D θ q hker t ht α (x.base*y.base) =
          (x.scalar * actualPhase D θ q hker t ht α x.base) *
          (y.scalar * actualPhase D θ q hker t ht α y.base) *
          sectionCocycle D θ q hker t ht (β x.base) (β y.base)
        rw [mul_assoc, actualPhase_mul D θ hinv q hker t ht ht1 α β hq hθ]
        ac_rfl
      · exact β.map_mul x.base y.base
  }
  on_base _ := rfl
  fixes_scalar z := by
    apply Extension.ext
    · change z * actualPhase D θ q hker t ht α 1 = z
      rw [actualPhase_one D θ q hker t ht ht1 α, mul_one]
    · exact β.map_one

theorem actualLift_phase (a : A) :
    (actualLift D θ hinv q hker t ht ht1 α β hq hθ).phase a =
      actualPhase D θ q hker t ht α a := by
  change 1 * actualPhase D θ q hker t ht α a = _
  exact one_mul _

theorem actualLift_intertwines (g : G) :
    (actualLift D θ hinv q hker t ht ht1 α β hq hθ).action
      (actualPushout D θ hinv q hker t ht ht1 g) =
        actualPushout D θ hinv q hker t ht ht1 (α g) := by
  apply Extension.ext
  · exact (sectionScalar_action D θ hinv q hker t ht ht1 α β hq hθ g).symm
  · exact (hq g).symm

theorem actualLift_power_intertwines (n : ℕ) (g : G) :
    ((actualLift D θ hinv q hker t ht ht1 α β hq hθ).action ^ n)
      (actualPushout D θ hinv q hker t ht ht1 g) =
        actualPushout D θ hinv q hker t ht ht1 ((α ^ n) g) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [pow_succ', pow_succ']
    change (actualLift D θ hinv q hker t ht ht1 α β hq hθ).action
      (((actualLift D θ hinv q hker t ht ht1 α β hq hθ).action ^ n)
        (actualPushout D θ hinv q hker t ht ht1 g)) =
      actualPushout D θ hinv q hker t ht ht1 (α ((α ^ n) g))
    rw [ih, actualLift_intertwines]

/-- An honest cyclic action on the actual group gives an honest cyclic
action on the scalar pushout, with no separate phase-period hypothesis. -/
theorem actualLift_power_eq_one (n : ℕ) (hn : α ^ n = 1) :
    (actualLift D θ hinv q hker t ht ht1 α β hq hθ).action ^ n = 1 := by
  let c := actualScalarCocycle D θ hinv q hker t ht ht1
  let L := actualLift D θ hinv q hker t ht ht1 α β hq hθ
  have hfix (z : ℂˣ) : (L.action ^ n) (Extension.scalarInclusion c z) =
      Extension.scalarInclusion c z := by
    induction n with
    | zero => rfl
    | succ k ih =>
      rw [pow_succ']
      change L.action ((L.action ^ k) (Extension.scalarInclusion c z)) = _
      rw [ih, L.fixes_scalar]
  have hsec (a : A) : (L.action ^ n) (Extension.sectionOf c a) =
      Extension.sectionOf c a := by
    have h := actualLift_power_intertwines D θ hinv q hker t ht ht1 α β hq hθ n (t a)
    rw [hn] at h
    simpa only [actualPushout_section, MulEquiv.one_apply] using h
  apply MulEquiv.ext
  intro x
  have hx : x = Extension.scalarInclusion c x.scalar * Extension.sectionOf c x.base := by
    apply Extension.ext <;> simp [Extension.sectionOf, c.one_left]
  change (L.action ^ n) x = x
  rw [hx, map_mul, hfix, hsec]

end PaperXI.ActualScalarLift113
