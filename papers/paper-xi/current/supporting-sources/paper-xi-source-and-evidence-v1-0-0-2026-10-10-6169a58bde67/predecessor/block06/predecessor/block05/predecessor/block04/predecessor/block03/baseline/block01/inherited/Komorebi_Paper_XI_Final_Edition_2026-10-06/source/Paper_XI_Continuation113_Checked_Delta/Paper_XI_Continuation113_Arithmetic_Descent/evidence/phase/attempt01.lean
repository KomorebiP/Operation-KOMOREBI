import PaperXI.GlobalHeisenbergBridge112
import Mathlib.Data.Int.GCD

/-! Same-carrier existence and uniqueness of determinant-one cyclic
implementers. The full automorphism and prescribed central character are
retained. No arithmetic realization or identification of the original kappa
is asserted. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicNormalization113
open Representation GlobalHeisenbergBridge112

section ScalarCorrection
variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- Scalar correction of an actual implementer on its original carrier. -/
def scale (c : ℂˣ) (A : V ≃ₗ[ℂ] V) : V ≃ₗ[ℂ] V :=
  A.trans (LinearEquiv.smulOfUnit c)

@[simp] theorem scale_apply (c : ℂˣ) (A : V ≃ₗ[ℂ] V) (v : V) :
    scale c A v = (c : ℂ) • A v := rfl

@[simp] theorem scale_pow_apply (c : ℂˣ) (A : V ≃ₗ[ℂ] V) (m : ℕ) (v : V) :
    (scale c A ^ m) v = ((c ^ m : ℂˣ) : ℂ) • (A ^ m) v := by
  induction m generalizing v with
  | zero => simp
  | succ m ih =>
    rw [pow_succ, LinearEquiv.mul_apply, ih, scale_apply, map_smul]
    simp only [pow_succ, Units.val_mul, smul_smul, LinearEquiv.mul_apply]

/-- Bézout gives the unique d-th root among n-torsion scalars. -/
theorem scalar_correction_exists (u : ℂˣ) (n d : ℕ)
    (hcop : Nat.Coprime n d) (hu : u ^ n = 1) :
    ∃ c : ℂˣ, c ^ n = 1 ∧ c ^ d = u := by
  refine ⟨u ^ Nat.gcdB n d, ?_, ?_⟩
  · rw [← zpow_natCast, ← zpow_mul, mul_comm, zpow_mul, zpow_natCast, hu, one_zpow]
  · have he : (1 : ℤ) = (n : ℤ) * Nat.gcdA n d + (d : ℤ) * Nat.gcdB n d := by
      simpa only [hcop, Nat.cast_one] using Nat.gcd_eq_gcd_ab n d
    have hu' : u ^ (n : ℤ) = 1 := by simpa using hu
    have h := congrArg (fun a : ℤ => u ^ a) he
    simpa only [zpow_one, zpow_add, zpow_mul, hu', one_zpow, one_mul,
      mul_comm, zpow_natCast] using h.symm

variable [FiniteDimensional ℂ V]

@[simp] theorem det_scale (c : ℂˣ) (A : V ≃ₗ[ℂ] V) :
    LinearEquiv.det (scale c A) = c ^ Module.finrank ℂ V * LinearEquiv.det A := by
  apply Units.ext
  change LinearMap.det (scale c A).toLinearMap = _
  have he : (scale c A).toLinearMap = (c : ℂ) • A.toLinearMap := by ext v; rfl
  rw [he, LinearMap.det_smul]
  rfl

/-- Every honest cyclic operator has a determinant-one scalar correction
when its order is coprime to the dimension. Both operators act on V. -/
theorem normalize_honest (A : V ≃ₗ[ℂ] V) (n : ℕ) (hAn : A ^ n = 1)
    (hcop : Nat.Coprime n (Module.finrank ℂ V)) :
    ∃ c : ℂˣ, c ^ n = 1 ∧ (scale c A) ^ n = 1 ∧
      LinearEquiv.det (scale c A) = 1 := by
  have hd : (LinearEquiv.det A) ^ n = 1 := by
    rw [← map_pow, hAn, map_one]
  obtain ⟨c, hcn, hcd⟩ := scalar_correction_exists (LinearEquiv.det A)⁻¹ n
    (Module.finrank ℂ V) hcop (by rw [inv_pow, hd, inv_one])
  refine ⟨c, hcn, ?_, ?_⟩
  · ext v
    simp only [scale_pow_apply, hcn, Units.val_one, one_smul, hAn]
  · rw [det_scale, hcd, inv_mul_cancel]

end ScalarCorrection

end PaperXI.CyclicNormalization113
