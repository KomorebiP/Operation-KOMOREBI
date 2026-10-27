module

public import KomorebiPhysics.Dispersion3D
public import KomorebiPhysics.Relativistic1DShellAsymptotics

/-!
Three-dimensional small-spacing structure of the exact product-cosine shell.

The exact four-factor shell is factored into two already-checked one-dimensional
shells.  This keeps all branch questions outside the present module: the target
here is the genuine sixth-order Taylor control underlying equations (8.31)--(8.36).
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DShellAsymptotics

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.DiracWalk3D
open KomorebiPhysics.Relativistic1DShellAsymptotics

/-- Continuum three-dimensional energy. -/
def energy3 (m kx ky kz : ℝ) : ℝ :=
  Real.sqrt (m^2 + kx^2 + ky^2 + kz^2)

/-- The quartic anisotropy polynomial in equations (8.32)--(8.36). -/
def anisotropyQ (m kx ky kz : ℝ) : ℝ :=
  m^2 * (kx^2 + ky^2 + kz^2) +
    kx^2 * ky^2 + kx^2 * kz^2 + ky^2 * kz^2

/-- The fourth derivative moment of the exact shell at zero. -/
def shellQuarticMoment3 (m kx ky kz : ℝ) : ℝ :=
  m^4 + kx^4 + ky^4 + kz^4 + 6 * anisotropyQ m kx ky kz

/-- Expanded quartic coefficient of the exact shell. -/
def shellQuarticCoeff3 (m kx ky kz : ℝ) : ℝ :=
  shellQuarticMoment3 m kx ky kz / 24

/-- Source form of the quartic coefficient. -/
def shellQuarticCoeffSource3 (m kx ky kz : ℝ) : ℝ :=
  energy3 m kx ky kz ^ 4 / 24 + anisotropyQ m kx ky kz / 6

/-- Fourth-order approximant to the exact three-dimensional shell. -/
def shellPoly4_3 (m kx ky kz ε : ℝ) : ℝ :=
  1 - energy3 m kx ky kz ^ 2 * ε^2 / 2 +
    shellQuarticCoeffSource3 m kx ky kz * ε^4

/-- A compact pairwise expression for the sixth derivative moment. -/
def shellSexticMoment3 (m kx ky kz : ℝ) : ℝ :=
  (m^6 + 15*m^4*kx^2 + 15*m^2*kx^4 + kx^6) +
  (ky^6 + 15*ky^4*kz^2 + 15*ky^2*kz^4 + kz^6) +
  15 * (m^2 + kx^2) * (ky^4 + 6*ky^2*kz^2 + kz^4) +
  15 * (m^4 + 6*m^2*kx^2 + kx^4) * (ky^2 + kz^2)

/-- The continuum energy square is the Euclidean mass-momentum quadratic form. -/
theorem energy3_sq (m kx ky kz : ℝ) :
    energy3 m kx ky kz ^ 2 = m^2 + kx^2 + ky^2 + kz^2 := by
  rw [energy3, Real.sq_sqrt]
  positivity

/-- The continuum energy is nonnegative. -/
theorem energy3_nonneg (m kx ky kz : ℝ) :
    0 ≤ energy3 m kx ky kz := by
  exact Real.sqrt_nonneg _

/-- The expanded and invariant quartic coefficients coincide. -/
theorem shellQuarticCoeff3_eq_source (m kx ky kz : ℝ) :
    shellQuarticCoeff3 m kx ky kz =
      shellQuarticCoeffSource3 m kx ky kz := by
  rw [shellQuarticCoeff3, shellQuarticCoeffSource3, shellQuarticMoment3]
  rw [show energy3 m kx ky kz ^ 4 = (energy3 m kx ky kz ^ 2)^2 by ring]
  rw [energy3_sq]
  simp only [anisotropyQ]
  ring

/-- The exact 3D shell is a product of two exact 1D shells. -/
theorem shell_eq_pair_product (m kx ky kz ε : ℝ) :
    shell m kx ky kz ε =
      KomorebiPhysics.Dispersion1D.shell m kx ε *
        KomorebiPhysics.Dispersion1D.shell ky kz ε := by
  simp [shell, KomorebiPhysics.Dispersion1D.shell, mul_assoc]

/-- Smoothness of the exact 3D shell to arbitrary finite order. -/
theorem contDiff_shell3 (m kx ky kz : ℝ) (n : ℕ) :
    ContDiff ℝ n (fun ε => shell m kx ky kz ε) := by
  rw [show (fun ε => shell m kx ky kz ε) =
      (fun ε => KomorebiPhysics.Dispersion1D.shell m kx ε) *
        (fun ε => KomorebiPhysics.Dispersion1D.shell ky kz ε) by
      funext ε
      exact shell_eq_pair_product m kx ky kz ε]
  exact (contDiff_shell m kx n).mul (contDiff_shell ky kz n)

/-- Exact shell value at zero. -/
theorem shell3_zero (m kx ky kz : ℝ) :
    shell m kx ky kz 0 = 1 := by
  simp [shell]

/-- First shell derivative at zero vanishes. -/
theorem shell3_deriv1_zero (m kx ky kz : ℝ) :
    iteratedDeriv 1 (fun ε => shell m kx ky kz ε) 0 = 0 := by
  rw [show (fun ε => shell m kx ky kz ε) =
      (fun ε => KomorebiPhysics.Dispersion1D.shell m kx ε) *
        (fun ε => KomorebiPhysics.Dispersion1D.shell ky kz ε) by
      funext ε
      exact shell_eq_pair_product m kx ky kz ε]
  rw [iteratedDeriv_mul
      (contDiff_shell m kx 1).contDiffAt (contDiff_shell ky kz 1).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose, shell_zero,
    shell_deriv1_zero]

/-- Second shell derivative at zero. -/
theorem shell3_deriv2_zero (m kx ky kz : ℝ) :
    iteratedDeriv 2 (fun ε => shell m kx ky kz ε) 0 =
      -(m^2 + kx^2 + ky^2 + kz^2) := by
  rw [show (fun ε => shell m kx ky kz ε) =
      (fun ε => KomorebiPhysics.Dispersion1D.shell m kx ε) *
        (fun ε => KomorebiPhysics.Dispersion1D.shell ky kz ε) by
      funext ε
      exact shell_eq_pair_product m kx ky kz ε]
  rw [iteratedDeriv_mul
      (contDiff_shell m kx 2).contDiffAt (contDiff_shell ky kz 2).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose, shell_zero,
    shell_deriv1_zero, shell_deriv2_zero]
  ring

/-- Third shell derivative at zero vanishes. -/
theorem shell3_deriv3_zero (m kx ky kz : ℝ) :
    iteratedDeriv 3 (fun ε => shell m kx ky kz ε) 0 = 0 := by
  rw [show (fun ε => shell m kx ky kz ε) =
      (fun ε => KomorebiPhysics.Dispersion1D.shell m kx ε) *
        (fun ε => KomorebiPhysics.Dispersion1D.shell ky kz ε) by
      funext ε
      exact shell_eq_pair_product m kx ky kz ε]
  rw [iteratedDeriv_mul
      (contDiff_shell m kx 3).contDiffAt (contDiff_shell ky kz 3).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose, shell_zero,
    shell_deriv1_zero, shell_deriv2_zero, shell_deriv3_zero]

/-- Fourth shell derivative at zero. -/
theorem shell3_deriv4_zero (m kx ky kz : ℝ) :
    iteratedDeriv 4 (fun ε => shell m kx ky kz ε) 0 =
      shellQuarticMoment3 m kx ky kz := by
  rw [show (fun ε => shell m kx ky kz ε) =
      (fun ε => KomorebiPhysics.Dispersion1D.shell m kx ε) *
        (fun ε => KomorebiPhysics.Dispersion1D.shell ky kz ε) by
      funext ε
      exact shell_eq_pair_product m kx ky kz ε]
  rw [iteratedDeriv_mul
      (contDiff_shell m kx 4).contDiffAt (contDiff_shell ky kz 4).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose, shell_zero,
    shell_deriv1_zero, shell_deriv2_zero, shell_deriv3_zero,
    shell_deriv4_zero, shellQuarticMoment3, anisotropyQ]
  ring

/-- Fifth shell derivative at zero vanishes. -/
theorem shell3_deriv5_zero (m kx ky kz : ℝ) :
    iteratedDeriv 5 (fun ε => shell m kx ky kz ε) 0 = 0 := by
  rw [show (fun ε => shell m kx ky kz ε) =
      (fun ε => KomorebiPhysics.Dispersion1D.shell m kx ε) *
        (fun ε => KomorebiPhysics.Dispersion1D.shell ky kz ε) by
      funext ε
      exact shell_eq_pair_product m kx ky kz ε]
  rw [iteratedDeriv_mul
      (contDiff_shell m kx 5).contDiffAt (contDiff_shell ky kz 5).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose, shell_zero,
    shell_deriv1_zero, shell_deriv2_zero, shell_deriv3_zero,
    shell_deriv4_zero, shell_deriv5_zero]

/-- Sixth shell derivative at zero, retained to certify the remainder order. -/
theorem shell3_deriv6_zero (m kx ky kz : ℝ) :
    iteratedDeriv 6 (fun ε => shell m kx ky kz ε) 0 =
      -shellSexticMoment3 m kx ky kz := by
  rw [show (fun ε => shell m kx ky kz ε) =
      (fun ε => KomorebiPhysics.Dispersion1D.shell m kx ε) *
        (fun ε => KomorebiPhysics.Dispersion1D.shell ky kz ε) by
      funext ε
      exact shell_eq_pair_product m kx ky kz ε]
  rw [iteratedDeriv_mul
      (contDiff_shell m kx 6).contDiffAt (contDiff_shell ky kz 6).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose, shell_zero,
    shell_deriv1_zero, shell_deriv2_zero, shell_deriv3_zero,
    shell_deriv4_zero, shell_deriv5_zero, shell_deriv6_zero,
    shellSexticMoment3]
  ring

/-- Taylor polynomial of order six, evaluated at zero, in closed form. -/
theorem taylor6_shell3_closed (m kx ky kz ε : ℝ) :
    taylorWithinEval (fun x => shell m kx ky kz x) 6 Set.univ 0 ε =
      shellPoly4_3 m kx ky kz ε -
        shellSexticMoment3 m kx ky kz * ε^6 / 720 := by
  rw [shellPoly4_3, ← shellQuarticCoeff3_eq_source]
  simp only [taylorWithinEval_succ, taylor_within_zero_eval,
    iteratedDerivWithin_univ]
  norm_num [shell3_zero, shell3_deriv1_zero, shell3_deriv2_zero,
    shell3_deriv3_zero, shell3_deriv4_zero, shell3_deriv5_zero,
    shell3_deriv6_zero, shellQuarticCoeff3, energy3_sq]
  ring

/-- Genuine sixth-order Taylor control for the exact 3D shell. -/
theorem shell3_sub_taylor6_isLittleO (m kx ky kz : ℝ) :
    (fun ε => shell m kx ky kz ε -
      taylorWithinEval (fun x => shell m kx ky kz x) 6 Set.univ 0 ε) =o[𝓝 0]
      (fun ε : ℝ => ε^6) := by
  simpa using
    (taylor_isLittleO_univ (x₀ := (0 : ℝ)) (contDiff_shell3 m kx ky kz 6))

/-- Equation (8.36): exact 3D shell through quartic order with an `O(ε^6)` remainder. -/
theorem shell3_expansion_isBigO (m kx ky kz : ℝ) :
    (fun ε => shell m kx ky kz ε - shellPoly4_3 m kx ky kz ε) =O[𝓝 0]
      (fun ε : ℝ => ε^6) := by
  have hsmall := (shell3_sub_taylor6_isLittleO m kx ky kz).isBigO
  have hpoly :
      (fun ε : ℝ =>
        taylorWithinEval (fun x => shell m kx ky kz x) 6 Set.univ 0 ε -
          shellPoly4_3 m kx ky kz ε) =O[𝓝 0] (fun ε : ℝ => ε^6) := by
    have hc : (fun ε : ℝ =>
        -(shellSexticMoment3 m kx ky kz) / 720 * ε^6) =O[𝓝 0]
        (fun ε : ℝ => ε^6) :=
      (isBigO_refl (fun ε : ℝ => ε^6) (𝓝 0)).const_mul_left _
    convert hc using 1
    funext ε
    rw [taylor6_shell3_closed]
    ring
  exact (hsmall.add hpoly).congr_left (by
    intro ε
    ring)

end KomorebiPhysics.Relativistic3DShellAsymptotics
