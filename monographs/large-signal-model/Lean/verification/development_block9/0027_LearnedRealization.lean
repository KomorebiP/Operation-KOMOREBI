import KomorebiLSM.DelayClosure
import KomorebiLSM.IdentificationBound
import KomorebiLSM.Realization
import KomorebiLSM.DefectPropagation

/-! P25: learning from a covering observation table, and explicit rollout bounds. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM.Identification
variable {E V : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable [FiniteDimensional ℝ E]

/-- Depends only on the paired observed columns. -/
noncomputable def learned (Zminus Zplus : E →ₗ[ℝ] V) : V →ₗ[ℝ] V :=
  Zplus.comp (pinv Zminus)

theorem learned_eq_true (Zminus Zplus : E →ₗ[ℝ] V) (D : V →ₗ[ℝ] V)
    (coverage : Function.Surjective Zminus) (successors : Zplus = D.comp Zminus) :
    learned Zminus Zplus = D := by
  apply LinearMap.ext
  intro v
  obtain ⟨x,rfl⟩ := coverage v
  change Zplus (pinv Zminus (Zminus x)) = D (Zminus x)
  rw [successors]
  change D (Zminus (pinv Zminus (Zminus x))) = _
  rw [pinv_apply_image, apply_retained]

theorem learned_all_horizons (Zminus Zplus : E →ₗ[ℝ] V) (D : V →ₗ[ℝ] V)
    (coverage : Function.Surjective Zminus) (successors : Zplus = D.comp Zminus)
    (v : V) (t : ℕ) : (learned Zminus Zplus ^ t) v = (D^t) v := by
  rw [learned_eq_true Zminus Zplus D coverage successors]

/-- Complete packet synthesis preserves every learned state, hence every decoded output. -/
theorem learned_packet_output {I O : Type*} [Fintype I] (P : I → V →ₗ[ℝ] V)
    (complete : ∑ i, P i = LinearMap.id) (H : V → O)
    (Zminus Zplus : E →ₗ[ℝ] V) (D : V →ₗ[ℝ] V)
    (coverage : Function.Surjective Zminus) (successors : Zplus = D.comp Zminus)
    (v : V) (t : ℕ) : H (∑ i, P i ((learned Zminus Zplus ^ t) v)) = H ((D^t) v) := by
  rw [learned_all_horizons Zminus Zplus D coverage successors]
  have he := congrArg (fun F : V →ₗ[ℝ] V => F ((D^t) v)) complete
  simpa only [LinearMap.sum_apply, LinearMap.id_apply] using congrArg H he

/-- The same learned transition in a lossless chart has exactly the same iterates. -/
theorem learned_atlas_iterates {C : Type*} (a : Realization V C)
    (Zminus Zplus : E →ₗ[ℝ] V) (D : V →ₗ[ℝ] V)
    (coverage : Function.Surjective Zminus) (successors : Zplus = D.comp Zminus)
    (v : V) (t : ℕ) :
    (Realization.realize a (learned Zminus Zplus) )^[t] (a.encode v) = a.encode ((D^t) v) := by
  rw [learned_eq_true Zminus Zplus D coverage successors]
  induction t with
  | zero => rfl
  | succ t ih =>
    rw [Function.iterate_succ_apply', ih]
    simp only [Realization.realize, Realization.decode_encode, pow_succ', Module.End.mul_apply]

/-- Combining P14 with a surjective table on its actual range identifies the delay transition. -/
theorem delay_table_identifies {X Y S : Type*} [AddCommGroup X] [Module ℝ X]
    [AddCommGroup Y] [Module ℝ Y] [AddCommGroup S] [Module ℝ S]
    (C : X →ₗ[ℝ] Y) (L : X →ₗ[ℝ] X) (h : ℕ)
    (hc : LinearMap.ker (Delay.observation C L h) ≤
      LinearMap.ker ((Delay.observation C L h).comp L))
    (Zm Zp : S →ₗ[ℝ] LinearMap.range (Delay.observation C L h))
    (coverage : Function.Surjective Zm)
    (successors : Zp = (Delay.transition C L h hc).comp Zm)
    (B : LinearMap.range (Delay.observation C L h) →ₗ[ℝ] LinearMap.range (Delay.observation C L h))
    (fit : B.comp Zm = Zp) : B = Delay.transition C L h hc := by
  apply LinearMap.ext
  intro v
  obtain ⟨x,rfl⟩ := coverage v
  have he := congrArg (fun F : S →ₗ[ℝ] LinearMap.range (Delay.observation C L h) => F x) fit
  simpa [successors] using he

variable [FiniteDimensional ℝ V]

/-- Noisy operator identification is connected to the actual recursively generated trajectory. -/
theorem fitted_rollout (A R E' F' : E →L[ℝ] V) (B : V →L[ℝ] V)
    (hE : ‖E'‖ < rowGain A) (x z : ℕ → V) (M : ℕ → ℝ)
    (true_step : ∀ t, x (t+1) = B (x t))
    (pred_step : ∀ t, z (t+1) = ((B.comp A + R + F').comp (pinvL (A+E'))) (z t))
    (bounded : ∀ t, ‖x t‖ ≤ M t) (T : ℕ) :
    ‖x T - z T‖ ≤ Stability.errorEnvelope
      (fun _ => ‖(B.comp A + R + F').comp (pinvL (A+E'))‖)
      (fun t => ((‖R‖+‖F'‖+‖B‖*‖E'‖)/(rowGain A-‖E'‖))*M t)
      ‖x 0-z 0‖ T := by
  let Bh := (B.comp A + R + F').comp (pinvL (A+E'))
  let q := (‖R‖+‖F'‖+‖B‖*‖E'‖)/(rowGain A-‖E'‖)
  have hq : 0 ≤ q := by dsimp [q]; positivity
  have hb : ‖Bh-B‖ ≤ q := noisy_identification_bound A R E' F' B hE
  apply Stability.recurrence_product_sum (fun t => ‖x t-z t‖)
    (fun _ => ‖Bh‖) (fun t => q*M t) (fun _ => norm_nonneg _)
  intro t
  rw [true_step, pred_step]
  apply Stability.local_error_step Bh
  · have hn := (Bh-B).le_opNorm (x t)
    have hn' : ‖B (x t)-Bh (x t)‖ ≤ ‖Bh-B‖*‖x t‖ := by
      simpa only [sub_apply, norm_sub_rev] using hn
    exact hn'.trans (mul_le_mul hb (bounded t) (norm_nonneg _) hq)
  · simpa only [map_sub] using Bh.le_opNorm (x t-z t)


/-- A strict common contraction gives an all-time invariant error radius. -/
theorem rollout_uniform_bound (B Bh : V →L[ℝ] V) (x z : ℕ → V)
    (delta radius : ℝ) (hrad : 0 ≤ radius) (gain : ‖Bh‖ < 1)
    (budget : delta ≤ (1-‖Bh‖)*radius)
    (initial : ‖x 0-z 0‖ ≤ radius)
    (true_step : ∀ t, x (t+1) = B (x t)) (pred_step : ∀ t, z (t+1) = Bh (z t))
    (defect : ∀ t, ‖B (x t)-Bh (x t)‖ ≤ delta) :
    ∀ t, ‖x t-z t‖ ≤ radius := by
  intro t
  induction t with
  | zero => exact initial
  | succ t ih =>
    rw [true_step, pred_step]
    have he := Stability.local_error_step Bh (x t) (z t) (B (x t)) (defect t)
      (by simpa only [map_sub] using Bh.le_opNorm (x t-z t))
    have hm := mul_le_mul_of_nonneg_left ih (norm_nonneg Bh)
    nlinarith
end Komorebi.LSM.Identification
