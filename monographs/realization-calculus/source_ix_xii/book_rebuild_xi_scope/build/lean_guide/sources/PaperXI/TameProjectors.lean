import PaperXI.FourierPackets
import Mathlib.Analysis.SpecialFunctions.Complex.CircleAddChar

/-! Proposition 3.1 over C, with primitivity and the nonzero denominator proved.
Both Frobenius conventions are stated explicitly, without changing the operators. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameProjectors
open scoped BigOperators
open PaperXI.CyclicAction
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

def projector (ρ : Action (K := ℂ) (V := V) (M := M)) (j : ZMod M) : Module.End ℂ V :=
  PaperXI.FourierProjectors.projector ρ ZMod.stdAddChar j

theorem idempotent (ρ : Action (K := ℂ) (V := V) (M := M)) (j : ZMod M) :
    projector ρ j ^ 2 = projector ρ j :=
  PaperXI.FourierProjectors.projector_idempotent ρ _ (ZMod.isPrimitive_stdAddChar M)
    (NeZero.ne (M : ℂ)) j

theorem orthogonal (ρ : Action (K := ℂ) (V := V) (M := M))
    {i j : ZMod M} (h : i ≠ j) : projector ρ i * projector ρ j = 0 :=
  PaperXI.FourierProjectors.projector_orthogonal ρ _ (ZMod.isPrimitive_stdAddChar M)
    (NeZero.ne (M : ℂ)) h

theorem complete (ρ : Action (K := ℂ) (V := V) (M := M)) :
    (∑ j : ZMod M, projector ρ j) = 1 :=
  PaperXI.FourierProjectors.projector_complete ρ _ (ZMod.isPrimitive_stdAddChar M)
    (NeZero.ne (M : ℂ))

theorem range_eq_character_space (ρ : Action (K := ℂ) (V := V) (M := M)) (j : ZMod M) :
    LinearMap.range (projector ρ j) = PaperXI.FourierPackets.packet ρ ZMod.stdAddChar j :=
  PaperXI.FourierPackets.projector_range ρ _ (NeZero.ne (M : ℂ)) j

/-- Under F t F^-1 = t^q the projector label changes by q^-1. -/
theorem forward_generator_covariance (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.conj (operator ρ 1) = operator ρ (q : ZMod M)) (j : ZMod M) :
    F.conj (projector ρ j) = projector ρ (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * j) :=
  PaperXI.FourierCovariance.inverse_exponent_covariance q F (operator ρ) ZMod.stdAddChar j
    (conjugation_from_generator ρ F q h)

/-- Under F^-1 t F = t^q the projector label changes by q. -/
theorem geometric_covariance (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) (j : ZMod M) :
    F.conj (projector ρ j) = projector ρ ((q : ZMod M) * j) := by
  have hs := forward_generator_covariance ρ F.symm q h ((q : ZMod M) * j)
  simp only [← mul_assoc, Units.inv_mul, one_mul] at hs
  have hh := congrArg F.conj hs
  simpa only [LinearEquiv.conj_conj_symm] using hh.symm

theorem character_weight (j a : ZMod M) :
    (ZMod.stdAddChar (N := M)) (-j * a) =
      (ZMod.stdAddChar (N := M) 1) ^ (-((j.val : ℤ) * (a.val : ℤ))) := by
  have h : (-((j.val : ℤ) * (a.val : ℤ))) • (1 : ZMod M) = -j * a := by
    simp [zsmul_eq_mul]
  rw [← h, AddChar.map_zsmul_eq_zpow]

theorem standard_root : (ZMod.stdAddChar (N := M)) 1 =
    Complex.exp (2 * Real.pi * Complex.I / M) := by
  simpa using (ZMod.stdAddChar_coe (N := M) (1 : ℤ))

/-- The computed operator is exactly the manuscript's root-of-unity sum. -/
theorem manuscript_formula (ρ : Action (K := ℂ) (V := V) (M := M)) (j : ZMod M) :
    projector ρ j = (M : ℂ)⁻¹ • ∑ a : ZMod M,
      (Complex.exp (2 * Real.pi * Complex.I / M)) ^ (-((j.val : ℤ) * (a.val : ℤ))) •
        (operator ρ 1 ^ a.val) := by
  rw [projector, PaperXI.FourierProjectors.projector_formula]
  congr 1
  apply Finset.sum_congr rfl
  intro a _
  rw [character_weight, standard_root, operator_eq_generator_pow ρ a]

/-- The complete finite statement in Proposition 3.1 with the geometric relation. -/
theorem tame_projector_theorem (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M)) :
    (∀ j, projector ρ j ^ 2 = projector ρ j) ∧
    (∀ i j, i ≠ j → projector ρ i * projector ρ j = 0) ∧
    (∑ j : ZMod M, projector ρ j) = 1 ∧
    (∀ j, F.conj (projector ρ j) = projector ρ ((q : ZMod M) * j)) :=
  ⟨idempotent ρ, fun _ _ hij => orthogonal ρ hij, complete ρ, geometric_covariance ρ F q h⟩

end PaperXI.TameProjectors
