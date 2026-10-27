import PaperXI.CocycleCommutator
import PaperXI.SchurScalar

/-! Scalar cocycles extracted from the multiplication of actual nonzero operators.
Associativity and normalization are conclusions of operator identities. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ProjectiveCocycle

open CocycleCommutator
variable {A V : Type*} [CommGroup A] [AddCommGroup V] [Module ℂ V]

/-- Nonzero operators make their scalar multipliers identifiable. -/
theorem scalar_injective (F : Module.End ℂ V) (hF : F ≠ 0) :
    Function.Injective (fun c : ℂˣ => (c : ℂ) • F) := by
  intro c d h
  apply Units.ext
  exact (smul_left_injective ℂ hF) h

/-- The scalar multiplication law of actual operators forces the cocycle identity. -/
def cocycle (T : A → Module.End ℂ V) (hT : ∀ a, T a ≠ 0)
    (c : A → A → ℂˣ)
    (hmul : ∀ a b, T a * T b = (c a b : ℂ) • T (a * b)) : Cocycle A ℂˣ where
  coeff := c
  assoc a b d := by
    apply scalar_injective (T (a * (b * d))) (hT _)
    have h := mul_assoc (T a) (T b) (T d)
    simpa only [hmul, smul_mul_assoc, mul_smul_comm, hmul, smul_smul,
      Units.val_mul, mul_assoc a b d] using h

/-- Identity operators force both scalar normalizations. -/
theorem normalized (T : A → Module.End ℂ V) (hT : ∀ a, T a ≠ 0)
    (c : A → A → ℂˣ)
    (hmul : ∀ a b, T a * T b = (c a b : ℂ) • T (a * b))
    (hone : T 1 = 1) : Normalized (cocycle T hT c hmul) := by
  constructor
  · intro a
    apply scalar_injective (T a) (hT a)
    simpa [hone, cocycle] using (hmul 1 a).symm
  · intro a
    apply scalar_injective (T a) (hT a)
    simpa [hone, cocycle] using (hmul a 1).symm

/-- Equality of all multiplication coefficients follows from equality of the operators. -/
theorem coefficient_unique (T : A → Module.End ℂ V) (hT : ∀ a, T a ≠ 0)
    (c d : A → A → ℂˣ)
    (hc : ∀ a b, T a * T b = (c a b : ℂ) • T (a * b))
    (hd : ∀ a b, T a * T b = (d a b : ℂ) • T (a * b)) : c = d := by
  funext a b
  exact scalar_injective (T (a * b)) (hT _) ((hc a b).symm.trans (hd a b))

/-- Rescaling the actual operators changes their scalar cocycle by the stated coboundary. -/
theorem rescale_coefficients (T U : A → Module.End ℂ V) (hT : ∀ a, T a ≠ 0)
    (c d : A → A → ℂˣ)
    (hc : ∀ a b, T a * T b = (c a b : ℂ) • T (a * b))
    (hd : ∀ a b, U a * U b = (d a b : ℂ) • U (a * b))
    (s : A → ℂˣ) (hs : ∀ a, U a = (s a : ℂ) • T a) (a b : A) :
    d a b = s a * s b / s (a * b) * c a b := by
  have h : ((d a b * s (a * b) : ℂˣ) : ℂ) • T (a * b) =
      ((s a * s b * c a b : ℂˣ) : ℂ) • T (a * b) := by
    simpa only [hs, smul_mul_assoc, mul_smul_comm, hc, smul_smul,
      Units.val_mul, mul_assoc, mul_left_comm] using (hd a b).symm
  have he := scalar_injective (T (a * b)) (hT _) h
  calc
    d a b = (s a * s b * c a b) / s (a * b) :=
      by
        have hh := congrArg (fun x : ℂˣ => x / s (a * b)) he
        simpa using hh
    _ = _ := by simp [div_eq_mul_inv, mul_assoc, mul_comm]

/-- Two actual projective families related by a cochain have equal commutators. -/
theorem commutator_rescale_operators
    (T U : A → Module.End ℂ V) (hT : ∀ a, T a ≠ 0) (hU : ∀ a, U a ≠ 0)
    (c d : A → A → ℂˣ)
    (hc : ∀ a b, T a * T b = (c a b : ℂ) • T (a * b))
    (hd : ∀ a b, U a * U b = (d a b : ℂ) • U (a * b))
    (s : A → ℂˣ) (hs : ∀ a, U a = (s a : ℂ) • T a) (a b : A) :
    commutator (cocycle U hU d hd) a b = commutator (cocycle T hT c hc) a b := by
  calc
    _ = commutator (rescale (cocycle T hT c hc) s) a b := by
      change d a b / d b a = _
      rw [rescale_coefficients T U hT c d hc hd s hs a b,
        rescale_coefficients T U hT c d hc hd s hs b a]
      rfl
    _ = _ := commutator_rescale _ s a b


/-- The operator cochain comparison gives equality of the actual cocycle structures. -/
theorem cocycle_rescale_operators
    (T U : A → Module.End ℂ V) (hT : ∀ a, T a ≠ 0) (hU : ∀ a, U a ≠ 0)
    (c d : A → A → ℂˣ)
    (hc : ∀ a b, T a * T b = (c a b : ℂ) • T (a * b))
    (hd : ∀ a b, U a * U b = (d a b : ℂ) • U (a * b))
    (s : A → ℂˣ) (hs : ∀ a, U a = (s a : ℂ) • T a) :
    cocycle U hU d hd = rescale (cocycle T hT c hc) s := by
  have h := funext (fun a => funext (rescale_coefficients T U hT c d hc hd s hs a))
  unfold cocycle rescale
  congr 1

/-- Normalized actual families force the comparing cochain to be normalized. -/
theorem cochain_one (T U : A → Module.End ℂ V) (hT : T 1 ≠ 0)
    (hT1 : T 1 = 1) (hU1 : U 1 = 1)
    (s : A → ℂˣ) (hs : ∀ a, U a = (s a : ℂ) • T a) : s 1 = 1 := by
  apply scalar_injective (T 1) hT
  simpa [hT1, hU1] using (hs 1).symm


/-- A cochain change of actual operators realizes the rescaled scalar cocycle. -/
theorem rescaledFamily_mul (T U : A → Module.End ℂ V) (c : Cocycle A ℂˣ)
    (hc : ∀ a b, T a * T b = (c.coeff a b : ℂ) • T (a * b))
    (s : A → ℂˣ) (hs : ∀ a, U a = (s a : ℂ) • T a) (a b : A) :
    U a * U b = ((rescale c s).coeff a b : ℂ) • U (a * b) := by
  have he : s b * (s a * c.coeff a b) =
      (s a * s b / s (a * b) * c.coeff a b) * s (a * b) := by
    simp [div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]
  simp only [hs, smul_mul_assoc, mul_smul_comm, hc, smul_smul, rescale]
  exact congrArg (fun z : ℂˣ => (z : ℂ) • T (a * b)) he

section Conjugation
variable {W : Type*} [AddCommGroup W] [Module ℂ W]

/-- Simultaneous change of coordinates preserves actual scalar multiplication. -/
theorem conjugate_mul (T : A → Module.End ℂ V) (c : A → A → ℂˣ)
    (hc : ∀ a b, T a * T b = (c a b : ℂ) • T (a * b))
    (e : V ≃ₗ[ℂ] W) (a b : A) :
    e.conj (T a) * e.conj (T b) = (c a b : ℂ) • e.conj (T (a * b)) := by
  have h := congrArg e.conj (hc a b)
  change e.conj ((T a).comp (T b)) = _ at h
  rw [LinearEquiv.conj_comp, map_smul] at h
  exact h

/-- A conjugation followed by a scalar change has the same explicit coboundary. -/
theorem conjugate_rescale_coefficients
    (T : A → Module.End ℂ V) (U : A → Module.End ℂ W) (hT : ∀ a, T a ≠ 0)
    (c d : A → A → ℂˣ)
    (hc : ∀ a b, T a * T b = (c a b : ℂ) • T (a * b))
    (hd : ∀ a b, U a * U b = (d a b : ℂ) • U (a * b))
    (e : V ≃ₗ[ℂ] W) (s : A → ℂˣ)
    (hs : ∀ a, U a = (s a : ℂ) • e.conj (T a)) (a b : A) :
    d a b = s a * s b / s (a * b) * c a b := by
  apply rescale_coefficients (fun a => e.conj (T a)) U _ c d
    (conjugate_mul T c hc e) hd s hs a b
  intro a h
  exact hT a (e.conj.injective (h.trans e.conj.map_zero.symm))


/-- Actual simultaneous conjugation, reindexing and a scalar cochain preserve
commutators on the corresponding elements of the two index groups. -/
theorem conjugate_rescale_commutator {B : Type*} [CommGroup B]
    (T : A → Module.End ℂ V) (U : B → Module.End ℂ W) (hT : ∀ a, T a ≠ 0)
    (c : Cocycle A ℂˣ) (d : Cocycle B ℂˣ)
    (hc : ∀ a b, T a * T b = (c.coeff a b : ℂ) • T (a * b))
    (hd : ∀ a b, U a * U b = (d.coeff a b : ℂ) • U (a * b))
    (e : V ≃ₗ[ℂ] W) (r : A ≃* B) (s : A → ℂˣ)
    (hs : ∀ a, U (r a) = (s a : ℂ) • e.conj (T a)) (a b : A) :
    commutator d (r a) (r b) = commutator c a b := by
  have hp (x y : A) : U (r x) * U (r y) =
      (d.coeff (r x) (r y) : ℂ) • U (r (x * y)) := by
    simpa only [map_mul] using hd (r x) (r y)
  have hh := conjugate_rescale_coefficients T (fun x => U (r x)) hT c.coeff
    (fun x y => d.coeff (r x) (r y)) hc hp e s hs
  calc
    _ = commutator (rescale c s) a b := by
      change d.coeff (r a) (r b) / d.coeff (r b) (r a) = _
      rw [hh a b, hh b a]
      rfl
    _ = _ := commutator_rescale c s a b

end Conjugation
end PaperXI.ProjectiveCocycle

