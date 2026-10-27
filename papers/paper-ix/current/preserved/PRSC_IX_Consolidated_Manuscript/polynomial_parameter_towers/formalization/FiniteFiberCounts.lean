module
public import Mathlib.Algebra.Torsor.Basic
public import Mathlib.FieldTheory.Finiteness
public import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
public import Mathlib.Algebra.Field.ZMod

/-!
# Linear correction fibers, torsors, and exact finite-field cardinalities

A fiber is the set of actual correction digits satisfying `b + A t = 0`.
No nonsingularity hypothesis is imposed. Choosing a point identifies the fiber
with the kernel. The action itself is independent of this choice.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false
open scoped Classical

namespace Komorebi.FiniteFiberCounts

section General
variable {K U V : Type*} [Ring K] [AddCommGroup U] [AddCommGroup V]
  [Module K U] [Module K V]

/-- The correction equation has the sign used by the Taylor obstruction. -/
def Fiber (A : U →ₗ[K] V) (b : V) := {t : U // b + A t = 0}

/-- Kernel vectors act by translation on correction digits. -/
def translate (A : U →ₗ[K] V) (b : V) (v : A.ker) (t : Fiber A b) : Fiber A b :=
  ⟨v.1 + t.1, by
    have hv : A v.1 = 0 := v.2
    simpa only [map_add, hv, zero_add] using t.2⟩

/-- The difference of two correction digits is a kernel vector. -/
def difference (A : U →ₗ[K] V) (b : V) (t u : Fiber A b) : A.ker :=
  ⟨t.1 - u.1, by
    change A (t.1 - u.1) = 0
    rw [map_sub, sub_eq_zero]
    exact add_left_cancel (t.2.trans u.2.symm)⟩

theorem translate_zero (A : U →ₗ[K] V) (b : V) (t : Fiber A b) :
    translate A b 0 t = t := by
  apply Subtype.ext
  exact zero_add _

theorem translate_add (A : U →ₗ[K] V) (b : V) (v w : A.ker) (t : Fiber A b) :
    translate A b (v + w) t = translate A b v (translate A b w t) := by
  apply Subtype.ext
  exact add_assoc _ _ _

theorem translate_difference (A : U →ₗ[K] V) (b : V) (t u : Fiber A b) :
    translate A b (difference A b t u) u = t := by
  apply Subtype.ext
  exact sub_add_cancel _ _

theorem difference_translate (A : U →ₗ[K] V) (b : V) (v : A.ker) (t : Fiber A b) :
    difference A b (translate A b v t) t = v := by
  apply Subtype.ext
  exact add_sub_cancel_right _ _

/-- Actual free and transitive kernel action on every nonempty correction fiber.
This is an explicit structure rather than a global typeclass instance. -/
@[instance_reducible] def fiberAddTorsor (A : U →ₗ[K] V) (b : V) (h : Nonempty (Fiber A b)) :
    AddTorsor A.ker (Fiber A b) where
  vadd := translate A b
  zero_vadd := translate_zero A b
  add_vadd := translate_add A b
  vsub := difference A b
  nonempty := h
  vsub_vadd' := translate_difference A b
  vadd_vsub' := difference_translate A b

/-- A chosen solution identifies all correction digits with the kernel. -/
def fiberEquivKernel (A : U →ₗ[K] V) (b : V) (u : Fiber A b) : Fiber A b ≃ A.ker where
  toFun t := difference A b t u
  invFun v := translate A b v u
  left_inv t := translate_difference A b t u
  right_inv v := difference_translate A b v u

theorem translate_exists_unique (A : U →ₗ[K] V) (b : V) (u t : Fiber A b) :
    ∃! v : A.ker, translate A b v u = t := by
  refine ⟨difference A b t u, translate_difference A b t u, ?_⟩
  intro v hv
  rw [← hv, difference_translate]

/-- Vanishing of the actual quotient class is exactly correction existence. -/
theorem fiber_nonempty_iff_class_zero (A : U →ₗ[K] V) (b : V) :
    Nonempty (Fiber A b) ↔ (Submodule.Quotient.mk b : V ⧸ A.range) = 0 := by
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨t⟩
    refine ⟨-t.1, ?_⟩
    rw [map_neg]
    exact (eq_neg_of_add_eq_zero_left t.2).symm
  · rintro ⟨t, ht⟩
    refine ⟨⟨-t, ?_⟩⟩
    rw [map_neg, ht, add_neg_cancel]

theorem fiber_card_eq_kernel (A : U →ₗ[K] V) (b : V) (h : Nonempty (Fiber A b)) :
    Nat.card (Fiber A b) = Nat.card A.ker := by
  obtain ⟨u⟩ := h
  exact Nat.card_congr (fiberEquivKernel A b u)

theorem fiber_card_of_empty (A : U →ₗ[K] V) (b : V) (h : ¬ Nonempty (Fiber A b)) :
    Nat.card (Fiber A b) = 0 := by
  have : IsEmpty (Fiber A b) := not_nonempty_iff.mp h
  exact Nat.card_eq_zero.mpr (Or.inl inferInstance)

end General

section PrimeField
variable (p : ℕ) [Fact (Nat.Prime p)] {d e : ℕ}

/-- Rank of the actual correction map over the prime field. -/
def rank (A : (Fin d → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p)) : ℕ :=
  Module.finrank (ZMod p) A.range

theorem kernel_finrank (A : (Fin d → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p)) :
    Module.finrank (ZMod p) A.ker = d - rank p A := by
  have hr := A.finrank_range_add_finrank_ker
  rw [Module.finrank_fin_fun] at hr
  unfold rank
  omega

theorem kernel_card (A : (Fin d → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p)) :
    Nat.card A.ker = p ^ (d - rank p A) := by
  rw [Module.natCard_eq_pow_finrank (K := ZMod p), kernel_finrank p]
  simp only [Nat.card_eq_fintype_card, ZMod.card]

/-- Every nonempty correction fiber has precisely the kernel cardinality. -/
theorem fiber_card_of_nonempty
    (A : (Fin d → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p)) (b : Fin e → ZMod p)
    (h : Nonempty (Fiber A b)) : Nat.card (Fiber A b) = p ^ (d - rank p A) := by
  rw [fiber_card_eq_kernel A b h, kernel_card p A]

/-- Empty fibers have zero points; nonempty fibers obey rank-nullity. -/
theorem fiber_card (A : (Fin d → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p))
    (b : Fin e → ZMod p) :
    Nat.card (Fiber A b) = if Nonempty (Fiber A b) then p ^ (d - rank p A) else 0 := by
  classical
  split_ifs with h
  · exact fiber_card_of_nonempty p A b h
  · exact fiber_card_of_empty A b h

/-- The finite obstruction space has the codomain dimension minus the rank. -/
theorem cokernel_finrank (A : (Fin d → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p)) :
    Module.finrank (ZMod p) ((Fin e → ZMod p) ⧸ A.range) = e - rank p A := by
  rw [Submodule.finrank_quotient, Module.finrank_fin_fun]
  rfl

theorem cokernel_card (A : (Fin d → ZMod p) →ₗ[ZMod p] (Fin e → ZMod p)) :
    Nat.card ((Fin e → ZMod p) ⧸ A.range) = p ^ (e - rank p A) := by
  rw [Module.natCard_eq_pow_finrank (K := ZMod p), cokernel_finrank p]
  simp only [Nat.card_eq_fintype_card, ZMod.card]

end PrimeField
end Komorebi.FiniteFiberCounts
