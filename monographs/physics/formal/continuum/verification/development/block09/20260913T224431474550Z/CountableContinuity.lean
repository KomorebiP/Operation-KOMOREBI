module

public import KomorebiPhysics.CountableAtlas

/-!
Chapter 6.4: actual unbounded-domain Schrödinger derivatives, current limits,
finite-region flux, and global Parseval conservation. The generator is not
assumed bounded, a differentiable solution is supplied, and no infinite
sum of derivatives or double sum of currents is interchanged.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace DomainAtlas
open Filter
open scoped BigOperators Topology

variable {H I : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable {T : H →ₗ.[ℂ] H} (P : DomainAtlas T I)

def amplitude (x : T.domain) (i j : I) : ℂ :=
  inner ℂ (P.atlas.proj i x) (T (P.project j x))

def current (x : T.domain) (i j : I) : ℝ := 2 * (P.amplitude x i j).im

def rate (x : T.domain) (i : I) : ℝ := 2 * (inner ℂ (P.atlas.proj i x) (T x)).im

/-- The complex conjugation in source (6.34) is essential. -/
theorem amplitude_reverse (hT : GraphDomain.IsSymmetric T) (x : T.domain) (i j : I) :
    P.amplitude x j i = star (P.amplitude x i j) := by
  change inner ℂ ((P.project j x : T.domain) : H) (T (P.project i x)) = _
  rw [← hT (P.project j x) (P.project i x)]
  exact (inner_conj_symm (𝕜 := ℂ) _ _).symm

theorem current_antisymm (hT : GraphDomain.IsSymmetric T) (x : T.domain) (i j : I) :
    P.current x i j = -P.current x j i := by
  unfold current
  rw [P.amplitude_reverse hT x j i]
  simp

theorem current_self (hT : GraphDomain.IsSymmetric T) (x : T.domain) (i : I) :
    P.current x i i = 0 := by
  have h := P.current_antisymm hT x i i
  linarith

theorem internal_current_zero (hT : GraphDomain.IsSymmetric T) (x : T.domain) (s : Finset I) :
    (∑ i ∈ s, ∑ j ∈ s, P.current x i j) = 0 :=
  antisymmetric_sum_zero _ s (fun i _ j _ => P.current_antisymm hT x i j)

/-- Finite linearity is legitimate on the actual invariant domain. -/
theorem partial_current (x : T.domain) (i : I) (s : Finset I) :
    (∑ j ∈ s, P.current x i j) =
      2 * (inner ℂ (P.atlas.proj i x) (T (P.partialSum s x))).im := by
  simp only [P.action_partial, inner_sum, Complex.im_sum, Finset.mul_sum, current, amplitude]

/-- Literal graph-compatible route to the complex pairing limit. -/
theorem amplitude_hasSum_graph (hG : P.GraphCompatible) (x : T.domain) (i : I) :
    HasSum (P.amplitude x i) (inner ℂ (P.atlas.proj i x) (T x)) :=
  (P.action_hasSum hG x).mapL (innerSL ℂ (P.atlas.proj i x))

/-- Literal graph-compatible current limit (6.33). -/
theorem current_hasSum_graph (hG : P.GraphCompatible) (x : T.domain) (i : I) :
    HasSum (P.current x i) (P.rate x i) :=
  ((P.amplitude_hasSum_graph hG x i).mapL Complex.imCLM).mul_left 2

/-- Added strengthening: for one fixed packet, symmetry moves the unbounded
operator onto that packet. Strong completeness alone then gives the scalar
pairing limit, without asserting convergence of T S_F x in Hilbert norm. -/
theorem amplitude_hasSum_strong (hT : GraphDomain.IsSymmetric T) (x : T.domain) (i : I) :
    HasSum (P.amplitude x i) (inner ℂ (P.atlas.proj i x) (T x)) := by
  have h := (P.atlas.strong (x : H)).mapL (innerSL ℂ (T (P.project i x)))
  change HasSum (fun j => inner ℂ (T (P.project i x)) (P.atlas.proj j x))
    (inner ℂ (T (P.project i x)) (x : H)) at h
  have heq : ∀ j, P.amplitude x i j =
      inner ℂ (T (P.project i x)) (P.atlas.proj j x) := by
    intro j
    exact (hT (P.project i x) (P.project j x)).symm
  have h' := h.congr_fun heq
  rwa [hT (P.project i x) x] at h'

theorem current_hasSum (hT : GraphDomain.IsSymmetric T) (x : T.domain) (i : I) :
    HasSum (P.current x i) (P.rate x i) :=
  ((P.amplitude_hasSum_strong hT x i).mapL Complex.imCLM).mul_left 2

/-- Absolute summability is proved for each scalar row, not for the entire
double array. It follows from the unconditional finite-subset limit in ℝ. -/
theorem current_row_abs_summable (hT : GraphDomain.IsSymmetric T) (x : T.domain) (i : I) :
    Summable (fun j => |P.current x i j|) := (P.current_hasSum hT x i).summable.abs

theorem current_row_tsum (hT : GraphDomain.IsSymmetric T) (x : T.domain) (i : I) :
    (∑' j, P.current x i j) = P.rate x i := (P.current_hasSum hT x i).tsum_eq

/-- Quantified graph-action error; no symmetry is needed for this estimate. -/
theorem current_tail_graph_bound (x : T.domain) (i : I) (s : Finset I) :
    |(∑ j ∈ s, P.current x i j) - P.rate x i| ≤
      2 * ‖P.atlas.proj i x‖ * ‖T (P.partialSum s x) - T x‖ := by
  rw [P.partial_current, rate, ← mul_sub, ← Complex.sub_im, ← inner_sub_right, abs_mul]
  rw [abs_of_nonneg (by norm_num : (0 : ℝ) ≤ 2)]
  calc
    _ ≤ 2 * ‖inner ℂ (P.atlas.proj i x) (T (P.partialSum s x) - T x)‖ :=
      mul_le_mul_of_nonneg_left (Complex.abs_im_le_norm _) (by norm_num)
    _ ≤ _ := by
      have h := norm_inner_le_norm (𝕜 := ℂ) (P.atlas.proj i x) (T (P.partialSum s x) - T x)
      nlinarith

/-- A stronger fixed-row error estimate from symmetry and Hilbert tail alone. -/
theorem current_tail_strong_bound (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (i : I) (s : Finset I) :
    |(∑ j ∈ s, P.current x i j) - P.rate x i| ≤
      2 * ‖T (P.project i x)‖ * ‖P.atlas.partialSum s x - (x : H)‖ := by
  rw [P.partial_current, rate]
  change |2 * (inner ℂ ((P.project i x : T.domain) : H) (T (P.partialSum s x))).im -
    2 * (inner ℂ ((P.project i x : T.domain) : H) (T x)).im| ≤ _
  rw [← hT (P.project i x) (P.partialSum s x), ← hT (P.project i x) x,
    P.partial_coe, ← mul_sub, ← Complex.sub_im, ← inner_sub_right, abs_mul]
  rw [abs_of_nonneg (by norm_num : (0 : ℝ) ≤ 2)]
  have h := (Complex.abs_im_le_norm
    (inner ℂ (T (P.project i x)) (P.atlas.partialSum s x - (x : H)))).trans
      (norm_inner_le_norm (𝕜 := ℂ) _ _)
  nlinarith

/-- Differentiate the ambient state curve using its bounded projector. The
trajectory takes values in the true domain, but no graph derivative is assumed. -/
theorem hasDerivAt_energy {ψ : ℝ → T.domain} {t : ℝ}
    (hψ : HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t) (i : I) :
    HasDerivAt (fun s => P.atlas.energy (ψ s : H) i) (P.rate (ψ t) i) t := by
  have hp := ((P.atlas.proj i).restrictScalars ℝ).hasFDerivAt.comp_hasDerivAt t hψ
  have hn := hasDerivAt_norm_sq hp
  change HasDerivAt (fun s => P.atlas.energy (ψ s : H) i)
    (2 * (inner ℂ (P.atlas.proj i (ψ t))
      (P.atlas.proj i ((-Complex.I) • T (ψ t)))).re) t at hn
  simpa only [map_smul, inner_smul_right, P.atlas.projected_inner,
    Complex.mul_re, Complex.neg_re, Complex.I_re, neg_zero, zero_mul,
    Complex.neg_im, Complex.I_im, neg_mul, one_mul, sub_neg_eq_add,
    zero_add, zero_sub, neg_neg, rate] using hn

/-- Source (6.33): derivative of the actual packet equals the actual finite
current limit, with graph compatibility explicitly supplying that limit. -/
theorem energy_derivative_graph_limit (hG : P.GraphCompatible)
    {ψ : ℝ → T.domain} {t : ℝ}
    (hψ : HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t) (i : I) :
    HasSum (P.current (ψ t) i) (deriv (fun s => P.atlas.energy (ψ s : H) i) t) := by
  rw [(P.hasDerivAt_energy hψ i).deriv]
  exact P.current_hasSum_graph hG (ψ t) i

/-- Symmetric-domain strengthening, without the extra graph assumption. -/
theorem hasDerivAt_energy_tsum (hT : GraphDomain.IsSymmetric T)
    {ψ : ℝ → T.domain} {t : ℝ}
    (hψ : HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t) (i : I) :
    HasDerivAt (fun s => P.atlas.energy (ψ s : H) i) (∑' j, P.current (ψ t) i j) t := by
  rw [P.current_row_tsum hT]
  exact P.hasDerivAt_energy hψ i

/-- Algebraic finite-subset boundary identity before passing to a limit. -/
theorem boundary_identity [DecidableEq I] (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (B s : Finset I) (hBs : B ⊆ s) :
    (∑ i ∈ B, ∑ j ∈ s \ B, P.current x i j) =
      ∑ i ∈ B, ∑ j ∈ s, P.current x i j := by
  have hsplit : ∀ i, (∑ j ∈ s, P.current x i j) =
      (∑ j ∈ s \ B, P.current x i j) + ∑ j ∈ B, P.current x i j := by
    intro i
    exact (Finset.sum_sdiff hBs).symm
  simp_rw [hsplit, Finset.sum_add_distrib]
  rw [P.internal_current_zero hT, add_zero]

/-- Source finite-region boundary limit. Only the inner label limit is
infinite; the receiving region remains a finite sum. -/
theorem boundary_tendsto [DecidableEq I] (hT : GraphDomain.IsSymmetric T)
    (x : T.domain) (B : Finset I) :
    Tendsto (fun s : Finset I => ∑ i ∈ B, ∑ j ∈ s \ B, P.current x i j)
      atTop (𝓝 (∑ i ∈ B, P.rate x i)) := by
  have h : Tendsto (fun s : Finset I => ∑ i ∈ B, ∑ j ∈ s, P.current x i j)
      atTop (𝓝 (∑ i ∈ B, P.rate x i)) :=
    tendsto_finsetSum B (fun i _ => P.current_hasSum hT x i)
  apply h.congr'
  filter_upwards [eventually_ge_atTop B] with s hs
  exact (P.boundary_identity hT x B s hs).symm

theorem hasDerivAt_region {ψ : ℝ → T.domain} {t : ℝ}
    (hψ : HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t) (B : Finset I) :
    HasDerivAt (fun s => ∑ i ∈ B, P.atlas.energy (ψ s : H) i)
      (∑ i ∈ B, P.rate (ψ t) i) t :=
  HasDerivAt.fun_sum (u := B) (fun i _ => P.hasDerivAt_energy hψ i)

/-- Literal (6.37) with the true derivative as the limiting value. -/
theorem region_derivative_boundary_limit [DecidableEq I]
    (hT : GraphDomain.IsSymmetric T) {ψ : ℝ → T.domain} {t : ℝ}
    (hψ : HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t) (B : Finset I) :
    Tendsto (fun s : Finset I => ∑ i ∈ B, ∑ j ∈ s \ B, P.current (ψ t) i j)
      atTop (𝓝 (deriv (fun s => ∑ i ∈ B, P.atlas.energy (ψ s : H) i) t)) := by
  rw [(P.hasDerivAt_region hψ B).deriv]
  exact P.boundary_tendsto hT (ψ t) B

end DomainAtlas

namespace GraphDomain
open Filter
open scoped BigOperators Topology
variable {H I : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable {T : H →ₗ.[ℂ] H}

/-- Symmetry on the actual domain gives conservation without using a false
bounded extension of T, and without exchanging infinite derivatives. -/
theorem hasDerivAt_norm_sq_zero (hT : IsSymmetric T) {ψ : ℝ → T.domain} {t : ℝ}
    (hψ : HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t) :
    HasDerivAt (fun s => ‖(ψ s : H)‖ ^ 2) 0 t := by
  have h := KomorebiPhysics.hasDerivAt_norm_sq hψ
  simpa [inner_smul_right, Complex.mul_re, symmetric_self_im_zero T hT] using h

theorem norm_sq_constant (hT : IsSymmetric T) (ψ : ℝ → T.domain)
    (hψ : ∀ t, HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t) (s t : ℝ) :
    ‖(ψ s : H)‖ ^ 2 = ‖(ψ t : H)‖ ^ 2 :=
  is_const_of_deriv_eq_zero
    (fun u => (hasDerivAt_norm_sq_zero hT (hψ u)).differentiableAt)
    (fun u => (hasDerivAt_norm_sq_zero hT (hψ u)).deriv) s t

/-- Source global countable law (6.41), conditional on an actual all-time
solution. This does not construct exp(-itT) or invoke its unproved properties. -/
theorem packet_energy_constant (P : StrongAtlas H I) (hT : IsSymmetric T)
    (ψ : ℝ → T.domain)
    (hψ : ∀ t, HasDerivAt (fun s => (ψ s : H)) ((-Complex.I) • T (ψ t)) t) (s t : ℝ) :
    (∑' i, P.energy (ψ s : H) i) = ∑' i, P.energy (ψ t : H) i := by
  rw [P.energy_tsum, P.energy_tsum]
  exact norm_sq_constant hT ψ hψ s t

end GraphDomain
end KomorebiPhysics
