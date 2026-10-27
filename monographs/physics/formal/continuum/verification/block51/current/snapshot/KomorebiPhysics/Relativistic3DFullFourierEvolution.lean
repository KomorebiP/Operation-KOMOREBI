import KomorebiPhysics.Relativistic3DFourierCompactTime
import Mathlib.Analysis.InnerProductSpace.l2Space
import Mathlib.Analysis.Normed.Lp.lpSpace

/-!
# Full Fourier-coefficient Dirac evolution

This module removes the fixed Fourier cutoff on the canonical coefficient Hilbert
space `ℓ²(Mode, ℂ⁴)`.  The continuum and central-difference mode propagators act
coordinatewise, define exact linear isometries on the complete coefficient space,
and converge uniformly on every compact time interval for every square-summable
coefficient field.

The final transport from coefficient `ℓ²` to physical torus `L²` is deliberately
kept separate from this block.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

open Filter Asymptotics
open scoped ENNReal BigOperators Topology lp

namespace KomorebiPhysics
namespace Relativistic3DFullFourierEvolution

open Relativistic3DFourierHilbertStability
open Relativistic3DFourierCompactTime

abbrev Mode := Relativistic3DFourierHilbertStability.Mode
abbrev CoeffL2 := ℓ²(Mode, HilbertSpinor)

local instance : NormedAlgebra ℚ HilbertSpinorEnd :=
  NormedAlgebra.restrictScalars ℚ ℂ HilbertSpinorEnd

/-- Coordinatewise application of a norm-preserving family to Fourier coefficients. -/
def modewiseMap
    (U : Mode → HilbertSpinor →L[ℂ] HilbertSpinor)
    (hU : ∀ n ψ, ‖U n ψ‖ = ‖ψ‖) (f : CoeffL2) : CoeffL2 :=
  ⟨fun n => U n (f n), by
    change Memℓp (fun n => U n (f n)) 2
    exact Memℓp.mono f.prop.norm (fun n => by rw [hU])⟩

@[simp] theorem modewiseMap_apply
    (U : Mode → HilbertSpinor →L[ℂ] HilbertSpinor)
    (hU : ∀ n ψ, ‖U n ψ‖ = ‖ψ‖) (f : CoeffL2) (n : Mode) :
    modewiseMap U hU f n = U n (f n) := rfl

/-- Coordinatewise action of a norm-preserving family on Fourier coefficients. -/
def modewiseIsometry
    (U : Mode → HilbertSpinor →L[ℂ] HilbertSpinor)
    (hU : ∀ n ψ, ‖U n ψ‖ = ‖ψ‖) : CoeffL2 →ₗᵢ[ℂ] CoeffL2 where
  toFun := modewiseMap U hU
  map_add' f g := by
    apply lp.ext
    funext n
    change U n (f n + g n) = U n (f n) + U n (g n)
    exact (U n).map_add _ _
  map_smul' c f := by
    apply lp.ext
    funext n
    change U n (c • f n) = c • U n (f n)
    exact (U n).map_smul _ _
  norm_map' f := by
    let g : CoeffL2 := modewiseMap U hU f
    change ‖g‖ = ‖f‖
    apply (sq_eq_sq₀ (norm_nonneg _) (norm_nonneg _)).mp
    have hg := lp.norm_rpow_eq_tsum
      (p := (2 : ℝ≥0∞)) (E := fun _ : Mode => HilbertSpinor)
      (by norm_num : 0 < (2 : ℝ≥0∞).toReal) g
    have hf := lp.norm_rpow_eq_tsum
      (p := (2 : ℝ≥0∞)) (E := fun _ : Mode => HilbertSpinor)
      (by norm_num : 0 < (2 : ℝ≥0∞).toReal) f
    norm_num at hg hf
    rw [hg, hf]
    apply tsum_congr
    intro n
    change ‖U n (f n)‖ ^ 2 = ‖f n‖ ^ 2
    rw [hU]

@[simp] theorem modewiseIsometry_apply
    (U : Mode → HilbertSpinor →L[ℂ] HilbertSpinor)
    (hU : ∀ n ψ, ‖U n ψ‖ = ‖ψ‖) (f : CoeffL2) (n : Mode) :
    modewiseIsometry U hU f n = U n (f n) := rfl

/-- Full continuum Fourier-coefficient propagator. -/
def continuumCoeffPropagator (m t : ℝ) : CoeffL2 →ₗᵢ[ℂ] CoeffL2 :=
  modewiseIsometry
    (fun n => continuumHilbertModePropagator m n t)
    (fun n ψ => norm_continuumHilbertModePropagator m n t ψ)

/-- Full central-difference Fourier-coefficient propagator. -/
def centralCoeffPropagator (m h t : ℝ) : CoeffL2 →ₗᵢ[ℂ] CoeffL2 :=
  modewiseIsometry
    (fun n => centralHilbertModePropagator m h n t)
    (fun n ψ => norm_centralHilbertModePropagator m h n t ψ)

@[simp] theorem continuumCoeffPropagator_apply (m t : ℝ) (f : CoeffL2) (n : Mode) :
    continuumCoeffPropagator m t f n = continuumHilbertModePropagator m n t (f n) := rfl

@[simp] theorem centralCoeffPropagator_apply (m h t : ℝ) (f : CoeffL2) (n : Mode) :
    centralCoeffPropagator m h t f n = centralHilbertModePropagator m h n t (f n) := rfl

/-- Exact norm preservation of the full continuum coefficient evolution. -/
theorem norm_continuumCoeffPropagator (m t : ℝ) (f : CoeffL2) :
    ‖continuumCoeffPropagator m t f‖ = ‖f‖ :=
  (continuumCoeffPropagator m t).norm_map f

/-- Exact norm preservation of the full lattice coefficient evolution. -/
theorem norm_centralCoeffPropagator (m h t : ℝ) (f : CoeffL2) :
    ‖centralCoeffPropagator m h t f‖ = ‖f‖ :=
  (centralCoeffPropagator m h t).norm_map f




/-- Hilbert-space time scaling is additive for a fixed mode Hamiltonian. -/
theorem hilbertTimeScaledOperator_add (s t : ℝ) (A : HilbertSpinorEnd) :
    hilbertTimeScaledOperator (s + t) A =
      hilbertTimeScaledOperator s A + hilbertTimeScaledOperator t A := by
  simp only [hilbertTimeScaledOperator, Complex.ofReal_add]
  module

/-- Hilbert-space scalar time multiples of one Hamiltonian commute. -/
theorem hilbertTimeScaledOperator_commute (s t : ℝ) (A : HilbertSpinorEnd) :
    Commute (hilbertTimeScaledOperator s A) (hilbertTimeScaledOperator t A) := by
  rw [commute_iff_eq]
  ext ψ
  simp [hilbertTimeScaledOperator, mul_left_comm, mul_assoc]

/-- Continuum Hilbert-mode propagators form a one-parameter group. -/
theorem continuumHilbertModePropagator_add_time (m s t : ℝ) (n : Mode) :
    continuumHilbertModePropagator m n (s + t) =
      continuumHilbertModePropagator m n s *
        continuumHilbertModePropagator m n t := by
  rw [continuumHilbertModePropagator, hilbertTimeScaledOperator_add]
  exact NormedSpace.exp_add_of_commute
    (hilbertTimeScaledOperator_commute s t (continuumHilbertModeOperator m n))

/-- Lattice Hilbert-mode propagators form a one-parameter group. -/
theorem centralHilbertModePropagator_add_time (m h s t : ℝ) (n : Mode) :
    centralHilbertModePropagator m h n (s + t) =
      centralHilbertModePropagator m h n s *
        centralHilbertModePropagator m h n t := by
  rw [centralHilbertModePropagator, hilbertTimeScaledOperator_add]
  exact NormedSpace.exp_add_of_commute
    (hilbertTimeScaledOperator_commute s t (centralHilbertModeOperator m h n))

/-- Opposite continuum Hilbert-mode times compose to the identity. -/
theorem continuumHilbertModePropagator_neg_mul (m t : ℝ) (n : Mode) :
    continuumHilbertModePropagator m n (-t) *
      continuumHilbertModePropagator m n t = 1 := by
  rw [← continuumHilbertModePropagator_add_time]
  rw [show -t + t = 0 by ring]
  unfold continuumHilbertModePropagator
  rw [show hilbertTimeScaledOperator 0 (continuumHilbertModeOperator m n) = 0 by
    ext ψ
    simp [hilbertTimeScaledOperator], NormedSpace.exp_zero]

/-- Opposite lattice Hilbert-mode times compose to the identity. -/
theorem centralHilbertModePropagator_neg_mul (m h t : ℝ) (n : Mode) :
    centralHilbertModePropagator m h n (-t) *
      centralHilbertModePropagator m h n t = 1 := by
  rw [← centralHilbertModePropagator_add_time]
  rw [show -t + t = 0 by ring]
  unfold centralHilbertModePropagator
  rw [show hilbertTimeScaledOperator 0 (centralHilbertModeOperator m h n) = 0 by
    ext ψ
    simp [hilbertTimeScaledOperator], NormedSpace.exp_zero]

/-- The full continuum coefficient propagator is surjective. -/
theorem continuumCoeffPropagator_surjective (m t : ℝ) :
    Function.Surjective (continuumCoeffPropagator m t) := by
  intro f
  refine ⟨continuumCoeffPropagator m (-t) f, ?_⟩
  apply lp.ext
  funext n
  change continuumHilbertModePropagator m n t
      (continuumHilbertModePropagator m n (-t) (f n)) = f n
  have hmul := continuumHilbertModePropagator_neg_mul m (-t) n
  have happ := congrArg (fun A : HilbertSpinorEnd => A (f n)) hmul
  simpa using happ

/-- The full lattice coefficient propagator is surjective. -/
theorem centralCoeffPropagator_surjective (m h t : ℝ) :
    Function.Surjective (centralCoeffPropagator m h t) := by
  intro f
  refine ⟨centralCoeffPropagator m h (-t) f, ?_⟩
  apply lp.ext
  funext n
  change centralHilbertModePropagator m h n t
      (centralHilbertModePropagator m h n (-t) (f n)) = f n
  have hmul := centralHilbertModePropagator_neg_mul m h (-t) n
  have happ := congrArg (fun A : HilbertSpinorEnd => A (f n)) hmul
  simpa using happ

/-- Full continuum Fourier-coefficient evolution as a unitary linear isometric equivalence. -/
def continuumCoeffUnitary (m t : ℝ) : CoeffL2 ≃ₗᵢ[ℂ] CoeffL2 :=
  LinearIsometryEquiv.ofSurjective
    (continuumCoeffPropagator m t) (continuumCoeffPropagator_surjective m t)

/-- Full lattice Fourier-coefficient evolution as a unitary linear isometric equivalence. -/
def centralCoeffUnitary (m h t : ℝ) : CoeffL2 ≃ₗᵢ[ℂ] CoeffL2 :=
  LinearIsometryEquiv.ofSurjective
    (centralCoeffPropagator m h t) (centralCoeffPropagator_surjective m h t)

@[simp] theorem continuumCoeffUnitary_apply (m t : ℝ) (f : CoeffL2) :
    continuumCoeffUnitary m t f = continuumCoeffPropagator m t f := rfl

@[simp] theorem centralCoeffUnitary_apply (m h t : ℝ) (f : CoeffL2) :
    centralCoeffUnitary m h t f = centralCoeffPropagator m h t f := rfl


/-- Full continuum coefficient evolution satisfies the group law. -/
theorem continuumCoeffPropagator_add_time (m s t : ℝ) (f : CoeffL2) :
    continuumCoeffPropagator m (s + t) f =
      continuumCoeffPropagator m s (continuumCoeffPropagator m t f) := by
  apply lp.ext
  funext n
  change continuumHilbertModePropagator m n (s + t) (f n) =
    continuumHilbertModePropagator m n s
      (continuumHilbertModePropagator m n t (f n))
  have h := congrArg (fun A : HilbertSpinorEnd => A (f n))
    (continuumHilbertModePropagator_add_time m s t n)
  simpa using h

/-- Full lattice coefficient evolution satisfies the group law. -/
theorem centralCoeffPropagator_add_time (m h s t : ℝ) (f : CoeffL2) :
    centralCoeffPropagator m h (s + t) f =
      centralCoeffPropagator m h s (centralCoeffPropagator m h t f) := by
  apply lp.ext
  funext n
  change centralHilbertModePropagator m h n (s + t) (f n) =
    centralHilbertModePropagator m h n s
      (centralHilbertModePropagator m h n t (f n))
  have hmode := congrArg (fun A : HilbertSpinorEnd => A (f n))
    (centralHilbertModePropagator_add_time m h s t n)
  simpa using hmode

/-- Finite Fourier truncation of a square-summable coefficient field. -/
def coeffTruncation (S : Finset Mode) (f : CoeffL2) : CoeffL2 :=
  ∑ n ∈ S, lp.single 2 n (f n)

@[simp] theorem coeffTruncation_apply (S : Finset Mode) (f : CoeffL2) (n : Mode) :
    coeffTruncation S f n = if n ∈ S then f n else 0 := by
  classical
  simp only [coeffTruncation, lp.coeFn_sum, lp.coeFn_single,
    Finset.sum_apply, Finset.sum_pi_single]

/-- Canonical finite Fourier truncations converge to every coefficient field. -/
theorem hasSum_single_coeff (f : CoeffL2) :
    HasSum (fun n : Mode => lp.single 2 n (f n)) f :=
  lp.hasSum_single (p := (2 : ℝ≥0∞)) (by norm_num) f

/-- Every square-summable coefficient field admits a finite Fourier truncation
with arbitrarily small tail. -/
theorem exists_coeffTruncation_approx (f : CoeffL2) {ε : ℝ} (hε : 0 < ε) :
    ∃ S : Finset Mode, ‖f - coeffTruncation S f‖ < ε := by
  have ht := hasSum_single_coeff f
  rw [HasSum, Metric.tendsto_nhds] at ht
  obtain ⟨S, hS⟩ := (eventually_atTop.1 (ht ε hε))
  refine ⟨S, ?_⟩
  have hh := hS S (le_refl S)
  simpa [coeffTruncation, dist_eq_norm, norm_sub_rev] using hh

/-- Coefficient-space residual for one finite Fourier truncation. -/
def coeffPacketResidual (m h t : ℝ) (S : Finset Mode) (f : CoeffL2) : CoeffL2 :=
  centralCoeffPropagator m h t (coeffTruncation S f) -
    continuumCoeffPropagator m t (coeffTruncation S f)

@[simp] theorem coeffPacketResidual_apply (m h t : ℝ) (S : Finset Mode)
    (f : CoeffL2) (n : Mode) :
    coeffPacketResidual m h t S f n =
      if n ∈ S then
        (centralHilbertModePropagator m h n t -
          continuumHilbertModePropagator m n t) (f n)
      else 0 := by
  classical
  by_cases hn : n ∈ S
  · simp [coeffPacketResidual, hn]
  · simp [coeffPacketResidual, hn]

/-- Exact coefficient-space Parseval identity for a finite propagator residual. -/
theorem coeffPacketResidual_norm_sq (m h t : ℝ) (S : Finset Mode) (f : CoeffL2) :
    ‖coeffPacketResidual m h t S f‖ ^ 2 =
      ∑ n ∈ S,
        ‖(centralHilbertModePropagator m h n t -
          continuumHilbertModePropagator m n t) (f n)‖ ^ 2 := by
  classical
  have hr := lp.norm_rpow_eq_tsum
    (p := (2 : ℝ≥0∞)) (E := fun _ : Mode => HilbertSpinor)
    (by norm_num : 0 < (2 : ℝ≥0∞).toReal)
    (coeffPacketResidual m h t S f)
  norm_num at hr
  calc
    ‖coeffPacketResidual m h t S f‖ ^ 2 =
        ∑' n : Mode,
          ‖if n ∈ S then
              centralHilbertModePropagator m h n t (f n) -
                continuumHilbertModePropagator m n t (f n)
            else 0‖ ^ 2 := hr
    _ = ∑ n ∈ S,
        ‖centralHilbertModePropagator m h n t (f n) -
          continuumHilbertModePropagator m n t (f n)‖ ^ 2 := by
      rw [tsum_eq_sum (s := S)]
      · apply Finset.sum_congr rfl
        intro n hn
        simp [hn]
      · intro n hn
        simp [hn]
    _ = ∑ n ∈ S,
        ‖(centralHilbertModePropagator m h n t -
          continuumHilbertModePropagator m n t) (f n)‖ ^ 2 := by
      apply Finset.sum_congr rfl
      intro n hn
      rfl

/-- Exact torus Parseval identity for the Hilbert finite-packet compact-time residual. -/
theorem compactTimePacketResidualL2_norm_sq (m h t : ℝ) (S : Finset Mode)
    (a : Mode → HilbertSpinor) :
    ‖compactTimePacketResidualL2 m h t S a‖ ^ 2 =
      ∑ n ∈ S,
        ‖(centralHilbertModePropagator m h n t -
          continuumHilbertModePropagator m n t) (a n)‖ ^ 2 := by
  rw [compactTimePacketResidualL2_eq_sum]
  exact Relativistic3DFourierL2Generator.modeEmbed_orthogonalFamily.norm_sum
    (fun n => (centralHilbertModePropagator m h n t -
      continuumHilbertModePropagator m n t) (a n)) S

/-- The finite truncation residual has the same norm in coefficient and torus representations. -/
theorem norm_coeffPacketResidual_eq_torus (m h t : ℝ) (S : Finset Mode)
    (f : CoeffL2) :
    ‖coeffPacketResidual m h t S f‖ =
      ‖compactTimePacketResidualL2 m h t S (fun n => f n)‖ := by
  apply (sq_eq_sq₀ (norm_nonneg _) (norm_nonneg _)).mp
  rw [coeffPacketResidual_norm_sq, compactTimePacketResidualL2_norm_sq]



/-- Every finite coefficient truncation inherits the checked compact-time
quadratic propagator bound. -/
theorem exists_compactTime_coeffTruncation_bound (m T : ℝ)
    (S : Finset Mode) (f : CoeffL2) (hT : 0 ≤ T) :
    ∃ K : ℝ, 0 ≤ K ∧
      ∀ᶠ h in 𝓝[>] (0 : ℝ), ∀ t : ℝ, |t| ≤ T →
        ‖coeffPacketResidual m h t S f‖ ≤ K * ‖h ^ 2‖ := by
  obtain ⟨K, hK0, hK⟩ := exists_compactTime_packet_propagator_bound
    m T S (fun n => f n) hT
  refine ⟨K, hK0, ?_⟩
  filter_upwards [hK] with h hh
  intro t ht
  rw [norm_coeffPacketResidual_eq_torus]
  exact hh t ht

/-- Full coefficient-space propagator residual. -/
def fullCoeffResidual (m h t : ℝ) (f : CoeffL2) : CoeffL2 :=
  centralCoeffPropagator m h t f - continuumCoeffPropagator m t f

/-- Compact-time strong convergence on the complete square-summable Fourier
coefficient space.  No rate is asserted for arbitrary data. -/
theorem eventually_fullCoeffResidual_lt (m T : ℝ) (hT : 0 ≤ T)
    (f : CoeffL2) {ε : ℝ} (hε : 0 < ε) :
    ∀ᶠ h in 𝓝[>] (0 : ℝ), ∀ t : ℝ, |t| ≤ T →
      ‖fullCoeffResidual m h t f‖ < ε := by
  obtain ⟨S, htail⟩ := exists_coeffTruncation_approx f (by positivity : 0 < ε / 4)
  let g : CoeffL2 := coeffTruncation S f
  obtain ⟨K, hK0, hcore⟩ := exists_compactTime_coeffTruncation_bound m T S f hT
  have hzero : Tendsto (fun h : ℝ => K * ‖h ^ 2‖)
      (𝓝[>] (0 : ℝ)) (𝓝 0) := by
    have hid : Tendsto (fun h : ℝ => h) (𝓝[>] (0 : ℝ)) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    have hp : Tendsto (fun h : ℝ => h ^ 2) (𝓝[>] (0 : ℝ)) (𝓝 0) := by
      simpa using hid.pow 2
    have hn : Tendsto (fun h : ℝ => ‖h ^ 2‖) (𝓝[>] (0 : ℝ)) (𝓝 0) := by
      simpa using hp.norm
    simpa using (tendsto_const_nhds.mul hn)
  have hsmall : ∀ᶠ h in 𝓝[>] (0 : ℝ), K * ‖h ^ 2‖ < ε / 2 :=
    (tendsto_order.1 hzero).2 (ε / 2) (by positivity)
  filter_upwards [hcore, hsmall] with h hhcore hhsmall
  intro t ht
  have htwo := norm_sub_le_two_tail
    (centralCoeffPropagator m h t).toContinuousLinearMap
    (continuumCoeffPropagator m t).toContinuousLinearMap
    f g
    (fun x => norm_centralCoeffPropagator m h t x)
    (fun x => norm_continuumCoeffPropagator m t x)
  have hmiddle :
      ‖centralCoeffPropagator m h t g - continuumCoeffPropagator m t g‖ < ε / 2 := by
    have hle : ‖coeffPacketResidual m h t S f‖ ≤ K * ‖h ^ 2‖ := hhcore t ht
    have hlt : ‖coeffPacketResidual m h t S f‖ < ε / 2 := hle.trans_lt hhsmall
    simpa [g, coeffPacketResidual] using hlt
  have htail' : ‖f - g‖ < ε / 4 := by
    simpa [g] using htail
  have htwo' :
      ‖fullCoeffResidual m h t f‖ ≤
        2 * ‖f - g‖ +
          ‖centralCoeffPropagator m h t g - continuumCoeffPropagator m t g‖ := by
    simpa [fullCoeffResidual] using htwo
  calc
    ‖fullCoeffResidual m h t f‖
        ≤ 2 * ‖f - g‖ +
          ‖centralCoeffPropagator m h t g - continuumCoeffPropagator m t g‖ := htwo'
    _ < 2 * (ε / 4) + ε / 2 :=
      add_lt_add (mul_lt_mul_of_pos_left htail' (by norm_num)) hmiddle
    _ = ε := by ring

/-- Strong compact-time convergence stated as a vanishing uniform error envelope. -/
theorem fullCoeffPropagator_compactTime_converges (m T : ℝ) (hT : 0 ≤ T)
    (f : CoeffL2) :
    ∀ ε > 0, ∀ᶠ h in 𝓝[>] (0 : ℝ), ∀ t : ℝ, |t| ≤ T →
      ‖centralCoeffPropagator m h t f - continuumCoeffPropagator m t f‖ < ε := by
  intro ε hε
  simpa [fullCoeffResidual] using eventually_fullCoeffResidual_lt m T hT f hε



/-- Pointwise strong convergence on the complete Fourier coefficient space. -/
theorem tendsto_centralCoeffPropagator (m t : ℝ) (f : CoeffL2) :
    Tendsto (fun h : ℝ => centralCoeffPropagator m h t f)
      (𝓝[>] (0 : ℝ)) (𝓝 (continuumCoeffPropagator m t f)) := by
  rw [Metric.tendsto_nhds]
  intro ε hε
  filter_upwards [eventually_fullCoeffResidual_lt m |t| (abs_nonneg t) f hε] with h hh
  have ht : |t| ≤ |t| := le_rfl
  have hres := hh t ht
  simpa [fullCoeffResidual, dist_eq_norm, norm_sub_rev] using hres

end Relativistic3DFullFourierEvolution
end KomorebiPhysics
