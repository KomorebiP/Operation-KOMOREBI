import KernelGaugeCorrection

/-! Exact (not asymptotic) Frobenius restriction across a square-zero kernel.
The norm map is the linear effect of changing the lifted Frobenius. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum
variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable (D : Datum G A B)

@[simp] theorem kernelUnit_zero : D.kernelUnit 0 = 1 := by
  apply Units.ext
  change 1 + (0 : A) = 1
  exact add_zero _

theorem kernelUnit_injective : Function.Injective D.kernelUnit := by
  intro x y h
  apply Subtype.ext
  have he := congrArg (fun u : Aˣ => (u : A)) h
  change 1 + (x : A) = 1 + (y : A) at he
  exact add_left_cancel he

theorem unit_commute_kernelUnit (F : Aˣ) (x : D.Kernel) :
    F * D.kernelUnit x = D.kernelUnit (D.conjugate F x) * F := by
  apply Units.ext
  change (F : A)*(1+(x : A))=(1+((F : A)*(x : A)*↑F⁻¹))*(F : A)
  simp only [mul_add, mul_one, add_mul, one_mul, mul_assoc, Units.inv_mul]

/-- Sum of the conjugates by F^i, i=0,...,d-1, recursively as an integer-linear map. -/
def frobeniusNorm (F : Aˣ) : ℕ → (D.Kernel →ₗ[ℤ] D.Kernel) :=
  Nat.rec 0 (fun n acc => acc + D.conjugate (F^n))

@[simp] theorem frobeniusNorm_zero (F : Aˣ) (x : D.Kernel) :
    D.frobeniusNorm F 0 x = 0 := rfl

@[simp] theorem frobeniusNorm_succ (F : Aˣ) (n : ℕ) (x : D.Kernel) :
    D.frobeniusNorm F (n+1) x = D.frobeniusNorm F n x + D.conjugate (F^n) x := rfl

/-- The derivative of the power map is exact in a square-zero kernel. -/
theorem kernel_perturbed_power (F : Aˣ) (x : D.Kernel) (d : ℕ) :
    (D.kernelUnit x * F)^d = D.kernelUnit (D.frobeniusNorm F d x) * F^d := by
  induction d with
  | zero => simp
  | succ n ih =>
    rw [pow_succ,ih]
    calc
      (D.kernelUnit (D.frobeniusNorm F n x) * F^n) * (D.kernelUnit x * F) =
        D.kernelUnit (D.frobeniusNorm F n x) * (F^n * D.kernelUnit x) * F := by group
      _ = D.kernelUnit (D.frobeniusNorm F n x) *
          (D.kernelUnit (D.conjugate (F^n) x) * F^n) * F := by
            rw [D.unit_commute_kernelUnit]
      _ = D.kernelUnit (D.frobeniusNorm F (n+1) x) * F^(n+1) := by
        rw [← mul_assoc, D.kernelUnit_add]
        simp only [frobeniusNorm_succ, pow_succ, mul_assoc]

/-- Independent local kernel conjugation contributes the degree-zero coboundary. -/
theorem conjugate_kernel_perturbed_power (F : Aˣ) (x z : D.Kernel) (d : ℕ) :
    D.kernelUnit z * (D.kernelUnit x * F)^d * (D.kernelUnit z)⁻¹ =
      D.kernelUnit (D.frobeniusNorm F d x + z - D.conjugate (F^d) z) * F^d := by
  rw [D.kernel_perturbed_power]
  have he := D.kernelUnit_conjugation
    (D.kernelUnit (D.frobeniusNorm F d x) * F^d) (-z)
  rw [neg_neg, map_neg, sub_neg_eq_add] at he
  have hc : D.conjugate (D.kernelUnit (D.frobeniusNorm F d x) * F^d) =
      D.conjugate (F^d) := by
    apply D.conjugate_same_residue
    change D.q ((D.kernelUnit (D.frobeniusNorm F d x) : A) * (F^d : A)) = _
    rw [map_mul, D.kernelUnit_residue, one_mul]
    simp
  rw [hc] at he
  rw [he, ← mul_assoc, D.kernelUnit_add]
  congr 2
  abel

/-- The actual mismatch between prescribed and base lifted Frobenius powers. -/
def unitMismatch (V F : Aˣ) (h : D.q V = D.q F) : D.Kernel :=
  ⟨((V : A)-(F : A))*↑F⁻¹, by simp [h]⟩

theorem unitMismatch_spec (V F : Aˣ) (h : D.q V = D.q F) :
    D.kernelUnit (D.unitMismatch V F h) * F = V := by
  apply Units.ext
  change (1+(((V : A)-(F : A))*↑F⁻¹))*(F : A)=(V : A)
  simp [add_mul,mul_assoc]

/-- Compute the precise local matching obstruction, with no prime-to-order assumption. -/
theorem local_power_lifting_iff_norm_image (F V : Aˣ) (d : ℕ)
    (hV : D.q V = D.q (F^d)) :
    (∃ F' u : Aˣ, D.q F' = D.q F ∧ D.q u = 1 ∧ u * F'^d * u⁻¹ = V) ↔
    ∃ x z : D.Kernel,
      D.unitMismatch V (F^d) hV = D.frobeniusNorm F d x + z - D.conjugate (F^d) z := by
  constructor
  · rintro ⟨F',u,hF',hu,hmatch⟩
    let x := D.unitMismatch F' F hF'
    obtain ⟨z,hz⟩ := D.every_residual_one_unit_is_kernelUnit u hu
    refine ⟨x,z,?_⟩
    have hx : D.kernelUnit x * F = F' := D.unitMismatch_spec F' F hF'
    rw [← hx, ← hz, D.conjugate_kernel_perturbed_power] at hmatch
    apply D.kernelUnit_injective
    apply mul_right_cancel (b := F^d)
    rw [D.unitMismatch_spec]
    exact hmatch.symm
  · rintro ⟨x,z,hxz⟩
    refine ⟨D.kernelUnit x * F,D.kernelUnit z,?_,D.kernelUnit_residue z,?_⟩
    · change D.q ((D.kernelUnit x : A)*(F : A)) = D.q F
      rw [map_mul,D.kernelUnit_residue,one_mul]
    · rw [D.conjugate_kernel_perturbed_power,← hxz,D.unitMismatch_spec]

end Komorebi.StrongArtin.SquareZeroH2.Datum
