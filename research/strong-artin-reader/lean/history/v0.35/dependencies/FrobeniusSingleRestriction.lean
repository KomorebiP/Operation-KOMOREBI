import FrobeniusRestrictionNorm

/-! Single-restriction gauge can be absorbed into the global Frobenius.
This does not assert the same for several prescriptions sharing one Frobenius. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum
variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable (D : Datum G A B)

/-- Recover the actual kernel coordinate of a prescribed perturbation. -/
theorem unitMismatch_kernel_perturbed (F : Aˣ) (e : D.Kernel)
    (h : D.q (D.kernelUnit e * F) = D.q F) :
    D.unitMismatch (D.kernelUnit e * F) F h = e := by
  apply D.kernelUnit_injective
  apply mul_right_cancel (b := F)
  rw [D.unitMismatch_spec]

/-- For one restriction, a kernel conjugator changes the choice of global root. -/
theorem one_power_gauge_iff_strict (F V : Aˣ) (d : ℕ) :
    (∃ F' u : Aˣ, D.q F' = D.q F ∧ D.q u = 1 ∧ u * F'^d * u⁻¹ = V) ↔
    ∃ F' : Aˣ, D.q F' = D.q F ∧ F'^d = V := by
  constructor
  · rintro ⟨F', u, hF, hu, hv⟩
    refine ⟨(MulAut.conj u) F', ?_, ?_⟩
    · change D.q ((u : A) * (F' : A) * (↑u⁻¹ : A)) = D.q F
      have hi : D.q (↑u⁻¹ : A) = 1 := by
        have h := D.inverse_same_residue (u := u) (v := 1) (by simpa using hu)
        simpa using h
      simp [map_mul, hu, hi, hF]
    · rw [← map_pow]
      exact hv
  · rintro ⟨F', hF, hv⟩
    exact ⟨F', 1, hF, by simp, by simpa using hv⟩

/-- Strict roots are controlled by the actual norm image, with no extra gauge image. -/
theorem power_lifting_iff_norm_image (F V : Aˣ) (d : ℕ)
    (hV : D.q V = D.q (F^d)) :
    (∃ F' : Aˣ, D.q F' = D.q F ∧ F'^d = V) ↔
    ∃ x : D.Kernel, D.frobeniusNorm F d x = D.unitMismatch V (F^d) hV := by
  constructor
  · rintro ⟨F', hF, hv⟩
    let x := D.unitMismatch F' F hF
    refine ⟨x, ?_⟩
    have hx : D.kernelUnit x * F = F' := D.unitMismatch_spec F' F hF
    apply D.kernelUnit_injective
    apply mul_right_cancel (b := F^d)
    rw [D.unitMismatch_spec, ← D.kernel_perturbed_power, hx, hv]
  · rintro ⟨x, hx⟩
    refine ⟨D.kernelUnit x * F, ?_, ?_⟩
    · change D.q ((D.kernelUnit x : A) * (F : A)) = D.q F
      rw [map_mul, D.kernelUnit_residue, one_mul]
    · rw [D.kernel_perturbed_power, hx, D.unitMismatch_spec]

/-- A single local gauge prescription is no easier than the strict power problem. -/
theorem one_power_matching_iff_norm_image (F V : Aˣ) (d : ℕ)
    (hV : D.q V = D.q (F^d)) :
    (∃ F' u : Aˣ, D.q F' = D.q F ∧ D.q u = 1 ∧ u * F'^d * u⁻¹ = V) ↔
    ∃ x : D.Kernel, D.frobeniusNorm F d x = D.unitMismatch V (F^d) hV := by
  rw [D.one_power_gauge_iff_strict, D.power_lifting_iff_norm_image]

end Komorebi.StrongArtin.SquareZeroH2.Datum
