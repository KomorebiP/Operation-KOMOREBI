import Komorebi.SufficientResolution.InexactResidual

/-!
# Forward-operator uncertainty budgets

The true operator A and the available operator C act between the SAME spaces.
The operator norm allowance, true-data noise allowance, and source norm bound
are explicit premises, not inferred from a fitting residual.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.OperatorUncertainty

open Filter Topology

/-- Inflated discrepancy noise for an uncertain operator and a bounded source. -/
def effectiveNoise (eta delta M : ℝ) : ℝ := eta + delta * M

 theorem effective_nonneg (eta delta M : ℝ) (he : 0 ≤ eta)
    (hd : 0 ≤ delta) (hM : 0 ≤ M) : 0 ≤ effectiveNoise eta delta M :=
  add_nonneg he (mul_nonneg hd hM)

 theorem effective_pos (eta delta M : ℝ) (he : 0 < eta)
    (hd : 0 ≤ delta) (hM : 0 ≤ M) : 0 < effectiveNoise eta delta M :=
  add_pos_of_pos_of_nonneg he (mul_nonneg hd hM)

 theorem effective_zero_operator_error (eta M : ℝ) :
    effectiveNoise eta 0 M = eta := by simp [effectiveNoise]

 theorem effective_tendsto {ι : Type*} (f : Filter ι) (eta delta : ι → ℝ) (M : ℝ)
    (he : Tendsto eta f (𝓝 0)) (hd : Tendsto delta f (𝓝 0)) :
    Tendsto (fun i => effectiveNoise (eta i) (delta i) M) f (𝓝 0) := by
  simpa only [effectiveNoise, zero_mul, zero_add] using
    he.add (hd.mul (tendsto_const_nhds (x := M)))

section Normed
variable {G V : Type*}
variable [NormedAddCommGroup G] [NormedSpace ℝ G]
variable [NormedAddCommGroup V] [NormedSpace ℝ V]

 theorem action_error (A C : G →L[ℝ] V) (delta : ℝ)
    (hd : ‖C-A‖ ≤ delta) (x : G) : ‖C x-A x‖ ≤ delta*‖x‖ := by
  change ‖(C-A) x‖ ≤ delta*‖x‖
  exact ((C-A).le_opNorm x).trans (mul_le_mul_of_nonneg_right hd (norm_nonneg x))

 theorem reverse_action_error (A C : G →L[ℝ] V) (delta : ℝ)
    (hd : ‖C-A‖ ≤ delta) (x : G) : ‖A x-C x‖ ≤ delta*‖x‖ := by
  rw [norm_sub_rev]
  exact action_error A C delta hd x

 theorem operator_allowance_nonneg (A C : G →L[ℝ] V) (delta : ℝ)
    (hd : ‖C-A‖ ≤ delta) : 0 ≤ delta := (norm_nonneg _).trans hd

 theorem true_operator_norm_le (A C : G →L[ℝ] V) (delta : ℝ)
    (hd : ‖C-A‖ ≤ delta) : ‖A‖ ≤ ‖C‖+delta := by
  calc
    _ ≤ ‖A-C‖+‖C‖ := norm_le_norm_sub_add A C
    _ = ‖C-A‖+‖C‖ := by rw [norm_sub_rev A C]
    _ ≤ delta+‖C‖ := add_le_add hd le_rfl
    _ = _ := add_comm _ _

 theorem effective_data_noise (A C : G →L[ℝ] V) (g : G) (v : V)
    (eta delta M : ℝ) (hd : ‖C-A‖ ≤ delta) (hM : ‖g‖ ≤ M)
    (he : ‖A g-v‖ ≤ eta) : ‖C g-v‖ ≤ effectiveNoise eta delta M := by
  have hdn := operator_allowance_nonneg A C delta hd
  calc
    _ ≤ ‖C g-A g‖+‖A g-v‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ delta*‖g‖+eta := add_le_add (action_error A C delta hd g) he
    _ ≤ delta*M+eta := add_le_add (mul_le_mul_of_nonneg_left hM hdn) le_rfl
    _ = _ := by simp only [effectiveNoise]; ring

 theorem fitting_norm_difference (A C : G →L[ℝ] V) (x : G) (v : V)
    (delta : ℝ) (hd : ‖C-A‖ ≤ delta) :
    |‖A x-v‖-‖C x-v‖| ≤ delta*‖x‖ := by
  calc
    _ ≤ ‖(A x-v)-(C x-v)‖ := abs_norm_sub_norm_le _ _
    _ = ‖A x-C x‖ := by congr 1; abel
    _ ≤ _ := reverse_action_error A C delta hd x

 theorem true_residual_bound (A C : G →L[ℝ] V) (x g : G) (v : V)
    (eta delta fit : ℝ) (hd : ‖C-A‖ ≤ delta)
    (he : ‖A g-v‖ ≤ eta) (hf : ‖C x-v‖ ≤ fit) :
    ‖A x-A g‖ ≤ delta*‖x‖+fit+eta := by
  calc
    _ ≤ ‖A x-C x‖+‖C x-A g‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ ‖A x-C x‖+(‖C x-v‖+‖v-A g‖) :=
      add_le_add le_rfl (norm_sub_le_norm_sub_add_norm_sub _ _ _)
    _ ≤ delta*‖x‖+(fit+eta) := add_le_add (reverse_action_error A C delta hd x)
      (add_le_add hf (by simpa only [norm_sub_rev] using he))
    _ = _ := by ring

 theorem measured_true_fitting_envelope (A C : G →L[ℝ] V) (x : G) (v : V)
    (delta measured omega : ℝ) (hd : ‖C-A‖ ≤ delta)
    (hm : |measured-‖C x-v‖| ≤ omega) :
    |measured-‖A x-v‖| ≤ omega+delta*‖x‖ := by
  calc
    _ ≤ |measured-‖C x-v‖|+|‖C x-v‖-‖A x-v‖| :=
      abs_sub_le _ _ _
    _ ≤ omega+delta*‖x‖ := add_le_add hm
      (by simpa only [abs_sub_comm] using fitting_norm_difference A C x v delta hd)

end Normed

end Komorebi.SufficientResolution.OperatorUncertainty
