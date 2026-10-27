import PaperX.GeneralReconstructionRecovery
import PaperX.SpecialMonodromy
import PaperX.LogarithmTruncation

set_option autoImplicit false
noncomputable section
namespace PaperX.LogarithmAudit

open PaperX.FiniteLogarithm PaperX.NilpotentLogarithm
open PaperX.LogarithmicRecovery PaperX.NilpotentExponential
open PaperX.SpecialMonodromy

/-- No commutativity hypothesis is inferred or supplied for the ambient algebra. -/
theorem arbitrary_ring {A : Type*} [Ring A] [Algebra ℚ A]
    (a : A) (ha : IsNilpotent a) : log (IsNilpotent.exp a) = a := log_exp ha

/-- The zero-dimensional matrix algebra is allowed, including exponent zero. -/
theorem zero_ring_exponent_zero :
    log (1 : Matrix (Fin 0) (Fin 0) ℚ) =
      ∑ j ∈ Finset.range 0, ((-1 : ℚ) ^ (j + 1) / (j : ℚ)) •
        ((1 : Matrix (Fin 0) (Fin 0) ℚ) - 1) ^ j := by
  exact log_eq_sum (Subsingleton.elim _ _)

theorem zero_ring_exponential_cutoff :
    (IsNilpotent.exp (0 : Matrix (Fin 0) (Fin 0) ℚ) - 1) ^ 0 = 0 := by
  exact PaperX.LogarithmTruncation.exp_sub_one_pow_eq_zero (Subsingleton.elim _ _)

/-- The endomorphism algebra need not have finite dimension. -/
theorem infinite_module (N : Module.End ℚ (ℕ → ℚ)) (hN : IsNilpotent N) :
    recoverN (2 : ℚ) (expN N 2) = N :=
  recoverN_expN hN (by norm_num)

/-- Nor need it be a nonzero module. -/
theorem zero_module :
    recoverN (1 : ℚ) (expN (0 : Module.End ℚ (Fin 0 → ℚ)) 1) = 0 := by
  exact recoverN_expN ⟨1, by simp⟩ (by norm_num)

def inclusion23 : (Fin 2 → ℚ) →ₗ[ℚ] (Fin 3 → ℚ) where
  toFun x i := if h : i.val < 2 then x ⟨i.val, h⟩ else 0
  map_add' x y := by funext i; dsimp; split <;> simp
  map_smul' c x := by funext i; dsimp; split <;> simp

theorem inclusion23_intertwines :
    shift (K := ℚ) 3 ∘ₗ inclusion23 = inclusion23 ∘ₗ shift 2 := by
  ext x i
  fin_cases i <;> simp [inclusion23, shift]

/-- A nonzero map between unequal dimensions and unequal nilpotence orders. -/
theorem unequal_orders_sample :
    expN (shift (K := ℚ) 3) 2 ∘ₗ inclusion23 =
      inclusion23 ∘ₗ expN (shift 2) 2 := by
  exact (expN_intertwines_iff ⟨2, shift_nilpotent 2⟩ ⟨3, shift_nilpotent 3⟩
    inclusion23 (by norm_num : (2 : ℚ) ≠ 0)).mpr inclusion23_intertwines

theorem unequal_orders_recovered :
    shift (K := ℚ) 3 ∘ₗ inclusion23 = inclusion23 ∘ₗ shift 2 := by
  exact (expN_intertwines_iff ⟨2, shift_nilpotent 2⟩ ⟨3, shift_nilpotent 3⟩
    inclusion23 (by norm_num : (2 : ℚ) ≠ 0)).mp unequal_orders_sample

theorem inclusion23_nonzero : inclusion23 ≠ 0 := by
  intro h
  have he := congrFun (LinearMap.congr_fun h (fun _ => 1)) (0 : Fin 3)
  norm_num [inclusion23] at he

#print axioms arbitrary_ring
#print axioms zero_ring_exponent_zero
#print axioms zero_ring_exponential_cutoff
#print axioms infinite_module
#print axioms zero_module
#print axioms unequal_orders_recovered
#print axioms inclusion23_nonzero

end PaperX.LogarithmAudit
