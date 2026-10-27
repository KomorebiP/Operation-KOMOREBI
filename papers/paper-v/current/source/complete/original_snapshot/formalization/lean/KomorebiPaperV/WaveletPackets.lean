import KomorebiPaperV.HaarChannels
import Mathlib.Analysis.InnerProductSpace.Adjoint

/-! Author: Komorebi P. Finite-depth literal Haar packet operators and adjoint synthesis. -/
namespace KomorebiPaperV.WaveletPackets
open KomorebiPaperV.HilbertPackets KomorebiPaperV.HaarChannels
abbrev H := Signal ℤ

noncomputable def lowLinear : H →ₗ[ℂ] H where
  toFun := analysisLow
  map_add' x y := by
    apply lp.ext
    funext n
    simp only [haar_low_samples, lp.coeFn_add, Pi.add_apply]
    ring
  map_smul' c x := by
    apply lp.ext
    funext n
    simp only [haar_low_samples, lp.coeFn_smul, Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    ring

noncomputable def highLinear : H →ₗ[ℂ] H where
  toFun := analysisHigh
  map_add' x y := by
    apply lp.ext
    funext n
    simp only [haar_high_samples, lp.coeFn_add, Pi.add_apply]
    ring
  map_smul' c x := by
    apply lp.ext
    funext n
    simp only [haar_high_samples, lp.coeFn_smul, Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    ring

theorem low_norm_bound (x : H) : ‖analysisLow x‖ ≤ ‖x‖ := by
  have h := haar_energy x
  nlinarith [sq_nonneg ‖analysisHigh x‖, norm_nonneg x, norm_nonneg (analysisLow x)]

theorem high_norm_bound (x : H) : ‖analysisHigh x‖ ≤ ‖x‖ := by
  have h := haar_energy x
  nlinarith [sq_nonneg ‖analysisLow x‖, norm_nonneg x, norm_nonneg (analysisHigh x)]

noncomputable def lowOp : H →L[ℂ] H := lowLinear.mkContinuous 1 (by
  intro x
  simpa [lowLinear] using low_norm_bound x)

noncomputable def highOp : H →L[ℂ] H := highLinear.mkContinuous 1 (by
  intro x
  simpa [highLinear] using high_norm_bound x)

noncomputable def childOp (i : Fin 2) : H →L[ℂ] H := if i = 0 then lowOp else highOp

theorem child_energy (x : H) : ∑ i : Fin 2, ‖childOp i x‖ ^ 2 = ‖x‖ ^ 2 := by
  simpa [Fin.sum_univ_two, childOp, lowOp, lowLinear, highOp, highLinear] using (haar_energy x).symm

def Word : ℕ → Type
  | 0 => Unit
  | n+1 => Fin 2 × Word n

instance wordFintype : (n : ℕ) → Fintype (Word n)
  | 0 => inferInstanceAs (Fintype Unit)
  | n+1 => letI := wordFintype n; inferInstanceAs (Fintype (Fin 2 × Word n))

noncomputable def packet : (n : ℕ) → Word n → H →L[ℂ] H
  | 0, _ => ContinuousLinearMap.id ℂ H
  | n+1, (b,w) => (packet n w).comp (childOp b)

theorem packet_energy (n : ℕ) (x : H) : ∑ w : Word n, ‖packet n w x‖ ^ 2 = ‖x‖ ^ 2 := by
  induction n generalizing x with
  | zero =>
    change (∑ w : Unit, ‖x‖ ^ 2) = _
    simp
  | succ n ih =>
    change (∑ w : Fin 2 × Word n, ‖(packet n w.2) (childOp w.1 x)‖ ^ 2) = _
    rw [Fintype.sum_prod_type]
    simp_rw [ih]
    exact child_energy x

/-- Complex polarization turns the energy identity into literal adjoint synthesis. -/
theorem energy_implies_adjoint_identity {I : Type*} [Fintype I]
    (W : I → H →L[ℂ] H) (h : ∀ x, ∑ i, ‖W i x‖ ^ 2 = ‖x‖ ^ 2) :
    (∑ i, (W i).adjoint.comp (W i)) = ContinuousLinearMap.id ℂ H := by
  have he : (∑ i, (W i).adjoint.comp (W i)).toLinearMap = LinearMap.id := by
    apply (ext_inner_map _ _).mp
    intro x
    change inner ℂ ((∑ i, (W i).adjoint.comp (W i)) x) x = inner ℂ x x
    simp only [sum_apply, ContinuousLinearMap.comp_apply, sum_inner,
      ContinuousLinearMap.adjoint_inner_left, inner_self_eq_norm_sq_to_K]
    exact_mod_cast h x
  apply ContinuousLinearMap.ext
  intro x
  exact LinearMap.congr_fun he x

theorem packet_operator_reconstruction (n : ℕ) :
    (∑ w : Word n, (packet n w).adjoint.comp (packet n w)) = ContinuousLinearMap.id ℂ H :=
  energy_implies_adjoint_identity (packet n) (packet_energy n)

theorem packet_reconstruction (n : ℕ) (x : H) :
    (∑ w : Word n, (packet n w).adjoint (packet n w x)) = x := by
  have h := congrArg (fun T : H →L[ℂ] H => T x) (packet_operator_reconstruction n)
  simpa using h

end KomorebiPaperV.WaveletPackets
