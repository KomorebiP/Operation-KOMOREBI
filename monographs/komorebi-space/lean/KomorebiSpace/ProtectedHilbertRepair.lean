import KomorebiSpace.HilbertKernelProjection
import Mathlib.Tactic.Linarith

set_option autoImplicit false

/-!
# KS56: nearest feasible repair preserving a declared continuous observable

All corrections lie in the actual kernel of p. The closed-range condition is
on D restricted to that kernel, not on D alone. Feasibility is never assumed
for every raw vector. No closed-range hypothesis is used for nearest-point
existence or the Pythagorean identity.
-/
universe u v w
noncomputable section
namespace KomorebiSpace.ProtectedHilbertRepair
open scoped RealInnerProductSpace
variable {E : Type u} {R : Type v} {S : Type w}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup R] [NormedSpace ℝ R]
variable [NormedAddCommGroup S] [NormedSpace ℝ S]
variable (D : E →L[ℝ] R) (p : E →L[ℝ] S)

/-- The actual admissible-correction operator on the protected kernel. -/
def restricted : p.ker →L[ℝ] R := D.comp p.ker.subtypeL

omit [CompleteSpace E] in
@[simp] theorem restricted_apply (h : p.ker) : restricted D p h = D h.val := rfl

def Feasible (x : E) : Prop := ∃ h : p.ker, restricted D p h = D x

omit [CompleteSpace E] in
theorem feasible_iff_answer (x : E) :
    Feasible D p x ↔ ∃ y : E, D y = 0 ∧ p y = p x := by
  constructor
  · rintro ⟨h, hh⟩
    refine ⟨x-h.val, ?_, ?_⟩
    · rw [map_sub]; exact sub_eq_zero.mpr hh.symm
    · have hz : p h.val = 0 := h.property
      rw [map_sub, hz, sub_zero]
  · rintro ⟨y, hd, hp⟩
    refine ⟨⟨x-y, ?_⟩, ?_⟩
    · change p (x-y) = 0
      rw [map_sub, hp, sub_self]
    · change D (x-y) = D x
      rw [map_sub, hd, sub_zero]

def rawCorrection (x : E) (hx : Feasible D p x) : p.ker := Classical.choose hx

omit [CompleteSpace E] in
theorem rawCorrection_image (x : E) (hx : Feasible D p x) :
    restricted D p (rawCorrection D p x hx) = D x := Classical.choose_spec hx

/-- Orthogonal displacement inside the protected kernel, not in the whole raw space. -/
def leastCorrection (x : E) (hx : Feasible D p x) : p.ker :=
  rawCorrection D p x hx - HilbertKernelProjection.projection (restricted D p)
    (rawCorrection D p x hx)

theorem leastCorrection_image (x : E) (hx : Feasible D p x) :
    restricted D p (leastCorrection D p x hx) = D x := by
  rw [leastCorrection, HilbertKernelProjection.defect_error, rawCorrection_image]

theorem leastCorrection_orthogonal (x : E) (hx : Feasible D p x) :
    leastCorrection D p x hx ∈ (restricted D p).kerᗮ :=
  HilbertKernelProjection.error_orthogonal _ _

theorem leastCorrection_unique (x : E) (hx : Feasible D p x) (h : p.ker)
    (hh : restricted D p h = D x) (ho : h ∈ (restricted D p).kerᗮ) :
    h = leastCorrection D p x hx := by
  have he : (⟨h, ho⟩ : (restricted D p).kerᗮ) =
      ⟨leastCorrection D p x hx, leastCorrection_orthogonal D p x hx⟩ := by
    apply HilbertKernelProjection.reduced_injective
    change restricted D p h = restricted D p (leastCorrection D p x hx)
    rw [hh, leastCorrection_image]
  exact congrArg Subtype.val he

def repair (x : E) (hx : Feasible D p x) : E := x - (leastCorrection D p x hx).val

theorem repair_exact (x : E) (hx : Feasible D p x) : D (repair D p x hx) = 0 := by
  rw [repair, map_sub]
  exact sub_eq_zero.mpr (leastCorrection_image D p x hx).symm

theorem repair_preserves (x : E) (hx : Feasible D p x) : p (repair D p x hx) = p x := by
  have hz : p (leastCorrection D p x hx).val = 0 := (leastCorrection D p x hx).property
  rw [repair, map_sub, hz, sub_zero]

theorem displacement_norm (x : E) (hx : Feasible D p x) :
    ‖x - repair D p x hx‖ = ‖leastCorrection D p x hx‖ := by
  rw [repair, sub_sub_cancel]
  rfl

/-- The difference of any two permitted corrections is in the actual ambiguity kernel. -/
theorem correction_difference (x : E) (hx : Feasible D p x) (h : p.ker)
    (hh : restricted D p h = D x) :
    h - leastCorrection D p x hx ∈ (restricted D p).ker := by
  change restricted D p (h - leastCorrection D p x hx) = 0
  rw [map_sub, hh, leastCorrection_image, sub_self]

theorem correction_pythagoras (x : E) (hx : Feasible D p x) (h : p.ker)
    (hh : restricted D p h = D x) :
    ‖h‖^2 = ‖leastCorrection D p x hx‖^2 + ‖h-leastCorrection D p x hx‖^2 := by
  have ho : ⟪h-leastCorrection D p x hx, leastCorrection D p x hx⟫ = 0 :=
    leastCorrection_orthogonal D p x hx _ (correction_difference D p x hx h hh)
  have he := norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero
    (h-leastCorrection D p x hx) (leastCorrection D p x hx) ho
  rw [sub_add_cancel] at he
  simpa only [pow_two, add_comm] using he

theorem repair_pythagoras (x : E) (hx : Feasible D p x) (y : E)
    (hy : D y = 0) (hp : p y = p x) :
    ‖x-y‖^2 = ‖x-repair D p x hx‖^2 + ‖repair D p x hx-y‖^2 := by
  let h : p.ker := ⟨x-y, by change p (x-y)=0; rw [map_sub, hp, sub_self]⟩
  have hh : restricted D p h = D x := by
    change D (x-y) = D x
    rw [map_sub, hy, sub_zero]
  have he := correction_pythagoras D p x hx h hh
  rw [displacement_norm]
  have hn : ‖h-leastCorrection D p x hx‖ = ‖repair D p x hx-y‖ := by
    change ‖(x-y)-(leastCorrection D p x hx).val‖ = ‖(x-(leastCorrection D p x hx).val)-y‖
    congr 1
    abel
  rw [hn] at he
  exact he

theorem repair_best (x : E) (hx : Feasible D p x) (y : E)
    (hy : D y = 0) (hp : p y = p x) :
    ‖x-repair D p x hx‖ ≤ ‖x-y‖ := by
  have he := repair_pythagoras D p x hx y hy hp
  have h1 := norm_nonneg (x-repair D p x hx)
  have h2 := norm_nonneg (x-y)
  nlinarith [sq_nonneg ‖repair D p x hx-y‖]

theorem repair_unique_nearest (x : E) (hx : Feasible D p x) (y : E)
    (hy : D y = 0) (hp : p y = p x)
    (hb : ‖x-y‖ ≤ ‖x-repair D p x hx‖) : y = repair D p x hx := by
  have he := repair_pythagoras D p x hx y hy hp
  have h1 := norm_nonneg (x-repair D p x hx)
  have h2 := norm_nonneg (x-y)
  have h3 := norm_nonneg (repair D p x hx-y)
  have hz : ‖repair D p x hx-y‖ = 0 := by nlinarith
  exact (sub_eq_zero.mp (norm_eq_zero.mp hz)).symm

theorem exists_unique_nearest (x : E) (hx : Feasible D p x) :
    ∃! y : E, D y = 0 ∧ p y = p x ∧
      ∀ z : E, D z = 0 → p z = p x → ‖x-y‖ ≤ ‖x-z‖ := by
  refine ⟨repair D p x hx,
    ⟨repair_exact D p x hx, repair_preserves D p x hx, repair_best D p x hx⟩, ?_⟩
  intro y hy
  exact repair_unique_nearest D p x hx y hy.1 hy.2.1
    (hy.2.2 _ (repair_exact D p x hx) (repair_preserves D p x hx))

/-- On an admissible raw vector, protected displacement is the usual kernel displacement in M. -/
theorem leastCorrection_subtype (a : p.ker) (hx : Feasible D p a.val) :
    leastCorrection D p a.val hx =
      a - HilbertKernelProjection.projection (restricted D p) a := by
  symm
  apply leastCorrection_unique
  · exact HilbertKernelProjection.defect_error _ a
  · exact HilbertKernelProjection.error_orthogonal _ a

variable [CompleteSpace R]

/-- The transverse inverse norm for the restricted, rather than unconstrained, operator. -/
def gain (hc : IsClosed (Set.range (restricted D p))) : ℝ :=
  HilbertKernelProjection.gain (restricted D p) hc

theorem gain_nonneg (hc : IsClosed (Set.range (restricted D p))) : 0 ≤ gain D p hc :=
  HilbertKernelProjection.gain_nonneg _ _

theorem repair_bound (hc : IsClosed (Set.range (restricted D p)))
    (x : E) (hx : Feasible D p x) :
    ‖x-repair D p x hx‖ ≤ gain D p hc * ‖D x‖ := by
  rw [displacement_norm]
  have he := HilbertKernelProjection.complement_bound (restricted D p) hc
    ⟨leastCorrection D p x hx, leastCorrection_orthogonal D p x hx⟩
  simpa only [gain, leastCorrection_image] using he

theorem closed_range_iff_protected_bound :
    IsClosed (Set.range (restricted D p)) ↔
      ∃ C : ℝ, 0 ≤ C ∧ ∀ (x : E) (hx : Feasible D p x),
        ‖x-repair D p x hx‖ ≤ C * ‖D x‖ := by
  constructor
  · intro hc
    exact ⟨gain D p hc, gain_nonneg D p hc, repair_bound D p hc⟩
  · rintro ⟨C, hC, hb⟩
    apply HilbertKernelProjection.closed_range_of_bound (restricted D p) C hC
    intro a
    have hx : Feasible D p a.val := ⟨a, rfl⟩
    have he := hb a.val hx
    rw [displacement_norm, leastCorrection_subtype] at he
    exact he

theorem gain_le_of_protected_bound (hc : IsClosed (Set.range (restricted D p)))
    (C : ℝ) (hC : 0 ≤ C)
    (hb : ∀ (x : E) (hx : Feasible D p x), ‖x-repair D p x hx‖ ≤ C*‖D x‖) :
    gain D p hc ≤ C := by
  apply HilbertKernelProjection.gain_le_of_bound (restricted D p) hc C hC
  intro a
  have hx : Feasible D p a.val := ⟨a, rfl⟩
  have he := hb a.val hx
  rw [displacement_norm, leastCorrection_subtype] at he
  exact he

theorem gain_characterization (hc : IsClosed (Set.range (restricted D p)))
    (C : ℝ) (hC : 0 ≤ C) :
    (∀ (x : E) (hx : Feasible D p x), ‖x-repair D p x hx‖ ≤ C*‖D x‖) ↔
      gain D p hc ≤ C := by
  constructor
  · exact gain_le_of_protected_bound D p hc C hC
  · intro h x hx
    exact (repair_bound D p hc x hx).trans (mul_le_mul_of_nonneg_right h (norm_nonneg _))

theorem gain_zero_iff (hc : IsClosed (Set.range (restricted D p))) :
    gain D p hc = 0 ↔ restricted D p = 0 :=
  HilbertKernelProjection.gain_eq_zero_iff _ _

end KomorebiSpace.ProtectedHilbertRepair
end
