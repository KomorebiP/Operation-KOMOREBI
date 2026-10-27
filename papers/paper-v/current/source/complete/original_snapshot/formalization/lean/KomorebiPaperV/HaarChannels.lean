import KomorebiPaperV.HaarHilbert

/-! Author: Komorebi P. Literal interleaved l2 channels and the Haar energy theorem. -/
namespace KomorebiPaperV.HaarChannels
open KomorebiPaperV.HilbertPackets KomorebiPaperV.HaarHilbert

noncomputable def channel {I J : Type*} (x : Signal (I × J)) (i : I) : Signal J :=
  ⟨fun j => x (i,j), memℓp_gen (by
    exact ((lp.memℓp x).summable (by norm_num)).comp_injective
      (fun _ _ h => Prod.mk.inj h |>.2))⟩

theorem norm_sq_tsum {I : Type*} (x : Signal I) : ‖x‖ ^ 2 = ∑' i, ‖x i‖ ^ 2 := by
  simpa using lp.norm_rpow_eq_tsum (by norm_num : 0 < (2 : ENNReal).toReal) x

theorem channel_energy {I J : Type*} [Fintype I] (x : Signal (I × J)) :
    ∑ i, ‖channel x i‖ ^ 2 = ‖x‖ ^ 2 := by
  simp_rw [norm_sq_tsum]
  have hs : Summable (fun p : I × J => ‖x p‖ ^ 2) := by
    simpa using (lp.memℓp x).summable (by norm_num)
  rw [hs.tsum_prod]
  exact (tsum_fintype _).symm

noncomputable def even (x : Signal ℤ) : Signal ℤ := channel (polyphase 2 (by norm_num) x) 0
noncomputable def odd (x : Signal ℤ) : Signal ℤ := channel (polyphase 2 (by norm_num) x) 1

theorem even_apply (x : Signal ℤ) (n : ℤ) : even x n = x (2*n) := by
  change x ((2:ℤ)*n + 0) = _
  rw [add_zero]

theorem odd_apply (x : Signal ℤ) (n : ℤ) : odd x n = x (2*n+1) := rfl

theorem interleaved_energy (x : Signal ℤ) : ‖even x‖ ^ 2 + ‖odd x‖ ^ 2 = ‖x‖ ^ 2 := by
  have h := channel_energy (polyphase 2 (by norm_num) x)
  rw [Fin.sum_univ_two, polyphase_energy] at h
  exact h

noncomputable def analysisLow (x : Signal ℤ) : Signal ℤ := low (even x) (odd x)
noncomputable def analysisHigh (x : Signal ℤ) : Signal ℤ := high (even x) (odd x)

theorem haar_energy (x : Signal ℤ) :
    ‖x‖ ^ 2 = ‖analysisLow x‖ ^ 2 + ‖analysisHigh x‖ ^ 2 := by
  rw [analysisLow, analysisHigh, energy, interleaved_energy]

theorem haar_low_samples (x : Signal ℤ) (n : ℤ) :
    analysisLow x n = ((Real.sqrt 2 : ℝ) : ℂ)⁻¹ * (x (2*n) + x (2*n+1)) := by
  rw [analysisLow, low_apply, even_apply, odd_apply]

theorem haar_high_samples (x : Signal ℤ) (n : ℤ) :
    analysisHigh x n = ((Real.sqrt 2 : ℝ) : ℂ)⁻¹ * (x (2*n) - x (2*n+1)) := by
  rw [analysisHigh, high_apply, even_apply, odd_apply]

end KomorebiPaperV.HaarChannels
