module

public import KomorebiPhysics.Relativistic3DCombinedDefect
public import Mathlib.Analysis.InnerProductSpace.PiL2

@[expose] public section
noncomputable section
set_option autoImplicit false

open scoped BigOperators ComplexConjugate Topology
open WithLp Filter

namespace KomorebiPhysics
namespace Relativistic3DHilbertScalarDefect

open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement
open Relativistic3DGeometricEdgeRefinement
open Relativistic3DEdgeCompatibility
open Relativistic3DCombinedDefect

universe u v

abbrev HilbertState (Site : Type u) := EuclideanSpace ℂ (Site × Fin 4)

def stateToHilbert {Site : Type u} (ψ : State (Site := Site)) : HilbertState Site :=
  toLp 2 (fun p => ψ p.1 p.2)

def hilbertToState {Site : Type u} (ψ : HilbertState Site) : State (Site := Site) :=
  fun x j => ψ (x, j)

@[simp] theorem stateToHilbert_apply {Site : Type u}
    (ψ : State (Site := Site)) (p : Site × Fin 4) :
    stateToHilbert ψ p = ψ p.1 p.2 := rfl

@[simp] theorem hilbertToState_apply {Site : Type u}
    (ψ : HilbertState Site) (x : Site) (j : Fin 4) :
    hilbertToState ψ x j = ψ (x, j) := rfl

@[simp] theorem hilbertToState_stateToHilbert {Site : Type u}
    (ψ : State (Site := Site)) :
    hilbertToState (stateToHilbert ψ) = ψ := by
  rfl

@[simp] theorem stateToHilbert_hilbertToState {Site : Type u}
    (ψ : HilbertState Site) :
    stateToHilbert (hilbertToState ψ) = ψ := by
  apply PiLp.ext
  intro p
  rfl

@[simp] theorem stateToHilbert_add {Site : Type u}
    (ψ φ : State (Site := Site)) :
    stateToHilbert (ψ + φ) = stateToHilbert ψ + stateToHilbert φ := by
  apply PiLp.ext
  intro p
  rfl

@[simp] theorem stateToHilbert_smul {Site : Type u}
    (c : ℂ) (ψ : State (Site := Site)) :
    stateToHilbert (c • ψ) = c • stateToHilbert ψ := by
  apply PiLp.ext
  intro p
  rfl

@[simp] theorem hilbertToState_add {Site : Type u}
    (ψ φ : HilbertState Site) :
    hilbertToState (ψ + φ) = hilbertToState ψ + hilbertToState φ := by
  rfl

@[simp] theorem hilbertToState_smul {Site : Type u}
    (c : ℂ) (ψ : HilbertState Site) :
    hilbertToState (c • ψ) = c • hilbertToState ψ := by
  rfl

/-- Algebraic identification of ordinary finite spinor fields with their
Euclidean `ℓ²` realization. -/
def stateHilbertEquiv {Site : Type u} :
    State (Site := Site) ≃ₗ[ℂ] HilbertState Site where
  toFun := stateToHilbert
  invFun := hilbertToState
  left_inv := hilbertToState_stateToHilbert
  right_inv := stateToHilbert_hilbertToState
  map_add' := stateToHilbert_add
  map_smul' := stateToHilbert_smul

/-- The Euclidean norm is exactly the real self-inner-product already used by
Blocks 25--30. -/
theorem stateToHilbert_norm_sq {Site : Type u} [Fintype Site]
    (ψ : State (Site := Site)) :
    ‖stateToHilbert ψ‖ ^ 2 = (stateIP ψ ψ).re := by
  rw [EuclideanSpace.norm_sq_eq]
  rw [show (stateIP ψ ψ).re = ∑ x, (ip (ψ x) (ψ x)).re by
    simp [stateIP]]
  rw [show (stateToHilbert ψ).ofLp =
      (fun p : Site × Fin 4 => ψ p.1 p.2) by
    exact WithLp.ofLp_toLp 2 _]
  rw [Fintype.sum_prod_type]
  apply Finset.sum_congr rfl
  intro x hx
  rw [ip_self_eq_normSq_sum]
  simp only [Complex.normSq_eq_norm_sq, Complex.ofReal_re]

theorem phaseErrorWeight_eq_realCast (z w : Circle) :
    phaseErrorWeight z w = ((‖(z : ℂ) - (w : ℂ)‖ ^ 2 : ℝ) : ℂ) := by
  unfold phaseErrorWeight
  rw [← Complex.normSq_eq_conj_mul_self]
  simp only [Complex.normSq_eq_norm_sq]

theorem directionalShift_sub_stateIP_re_formula {Site : Type u} [Fintype Site]
    (H : HermitianClifford) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) (ψ : State (Site := Site)) :
    (stateIP
      (directionalShift H.toClifford τ v ψ -
        directionalShift H.toClifford τ u ψ)
      (directionalShift H.toClifford τ v ψ -
        directionalShift H.toClifford τ u ψ)).re =
    ∑ x,
      (‖(v (τ.symm x) : ℂ) - (u (τ.symm x) : ℂ)‖ ^ 2 *
        (ip (H.toClifford.plus (ψ (τ.symm x)))
          (H.toClifford.plus (ψ (τ.symm x)))).re +
      ‖(((v x)⁻¹ : Circle) : ℂ) - (((u x)⁻¹ : Circle) : ℂ)‖ ^ 2 *
        (ip (H.toClifford.minus (ψ (τ x)))
          (H.toClifford.minus (ψ (τ x)))).re) := by
  rw [directionalShift_sub_stateIP]
  rw [Complex.re_sum]
  simp only [phaseErrorWeight_eq_realCast, Complex.add_re, Complex.mul_re,
    Complex.ofReal_re, Complex.ofReal_im, zero_mul, sub_zero]


theorem circle_inv_sub_inv_norm (z w : Circle) :
    ‖(((z⁻¹ : Circle) : ℂ) - ((w⁻¹ : Circle) : ℂ))‖ =
      ‖(z : ℂ) - (w : ℂ)‖ := by
  rw [Circle.coe_inv_eq_conj, Circle.coe_inv_eq_conj, ← map_sub,
    Complex.norm_conj]

theorem stateIP_re_eq_sum {Site : Type u} [Fintype Site]
    (ψ : State (Site := Site)) :
    (stateIP ψ ψ).re = ∑ x, (ip (ψ x) (ψ x)).re := by
  unfold stateIP
  rw [Complex.re_sum]

theorem directionalShift_sub_stateIP_re_le {Site : Type u} [Fintype Site]
    (H : HermitianClifford) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) (δ : ℝ) (hδ : 0 ≤ δ)
    (hdiff : ∀ x, ‖(v x : ℂ) - (u x : ℂ)‖ ≤ δ)
    (ψ : State (Site := Site)) :
    (stateIP
      (directionalShift H.toClifford τ v ψ -
        directionalShift H.toClifford τ u ψ)
      (directionalShift H.toClifford τ v ψ -
        directionalShift H.toClifford τ u ψ)).re ≤
      δ ^ 2 * (stateIP ψ ψ).re := by
  rw [directionalShift_sub_stateIP_re_formula]
  calc
    ∑ x,
        (‖(v (τ.symm x) : ℂ) - (u (τ.symm x) : ℂ)‖ ^ 2 *
          (ip (H.toClifford.plus (ψ (τ.symm x)))
            (H.toClifford.plus (ψ (τ.symm x)))).re +
        ‖(((v x)⁻¹ : Circle) : ℂ) - (((u x)⁻¹ : Circle) : ℂ)‖ ^ 2 *
          (ip (H.toClifford.minus (ψ (τ x)))
            (H.toClifford.minus (ψ (τ x)))).re) ≤
      ∑ x,
        (δ ^ 2 *
          (ip (H.toClifford.plus (ψ (τ.symm x)))
            (H.toClifford.plus (ψ (τ.symm x)))).re +
        δ ^ 2 *
          (ip (H.toClifford.minus (ψ (τ x)))
            (H.toClifford.minus (ψ (τ x)))).re) := by
          apply Finset.sum_le_sum
          intro x hx
          have hp : 0 ≤ (ip (H.toClifford.plus (ψ (τ.symm x)))
              (H.toClifford.plus (ψ (τ.symm x)))).re :=
            ip_self_re_nonneg _
          have hm : 0 ≤ (ip (H.toClifford.minus (ψ (τ x)))
              (H.toClifford.minus (ψ (τ x)))).re :=
            ip_self_re_nonneg _
          have hvp : ‖(v (τ.symm x) : ℂ) - (u (τ.symm x) : ℂ)‖ ^ 2 ≤ δ ^ 2 :=
            (sq_le_sq₀ (norm_nonneg _) hδ).2 (hdiff _)
          have hvm : ‖(((v x)⁻¹ : Circle) : ℂ) - (((u x)⁻¹ : Circle) : ℂ)‖ ^ 2 ≤
              δ ^ 2 := by
            rw [circle_inv_sub_inv_norm]
            exact (sq_le_sq₀ (norm_nonneg _) hδ).2 (hdiff _)
          exact add_le_add
            (mul_le_mul_of_nonneg_right hvp hp)
            (mul_le_mul_of_nonneg_right hvm hm)
    _ = δ ^ 2 * (stateIP ψ ψ).re := by
      rw [Finset.sum_add_distrib]
      rw [← Finset.mul_sum, ← Finset.mul_sum]
      have hplus := τ.symm.sum_comp (fun i =>
        (ip (H.toClifford.plus (ψ i)) (H.toClifford.plus (ψ i))).re)
      have hminus := τ.sum_comp (fun i =>
        (ip (H.toClifford.minus (ψ i)) (H.toClifford.minus (ψ i))).re)
      rw [hplus, hminus]
      rw [← mul_add]
      rw [← Finset.sum_add_distrib]
      rw [stateIP_re_eq_sum]
      congr 1
      apply Finset.sum_congr rfl
      intro x hx
      exact congrArg Complex.re (H.ip_split (ψ x) (ψ x))


@[simp] theorem hilbertToState_stateIP_re {Site : Type u} [Fintype Site]
    (ψ : HilbertState Site) :
    (stateIP (hilbertToState ψ) (hilbertToState ψ)).re = ‖ψ‖ ^ 2 := by
  rw [← stateToHilbert_norm_sq]
  simp


/-- Hilbert-space linear operator associated with the difference of two
link-coupled Clifford shifts. -/
def directionalShiftDefectHilbertLinear {Site : Type u} [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) :
    HilbertState Site →ₗ[ℂ] HilbertState Site :=
  stateHilbertEquiv.toLinearMap.comp
    (((directionalShiftCLM A τ v - directionalShiftCLM A τ u).toLinearMap).comp
      stateHilbertEquiv.symm.toLinearMap)

/-- The same operator, continuously realized in the finite Euclidean Hilbert space. -/
def directionalShiftDefectHilbertCLM {Site : Type u} [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) :
    HilbertState Site →L[ℂ] HilbertState Site :=
  LinearMap.toContinuousLinearMap (directionalShiftDefectHilbertLinear A τ v u)

@[simp] theorem directionalShiftDefectHilbertCLM_apply
    {Site : Type u} [Fintype Site]
    (A : CliffordInvolution) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) (ψ : HilbertState Site) :
    directionalShiftDefectHilbertCLM A τ v u ψ =
      stateToHilbert
        (directionalShift A τ v (hilbertToState ψ) -
          directionalShift A τ u (hilbertToState ψ)) := by
  rfl

theorem directionalShiftDefectHilbertCLM_norm_le
    {Site : Type u} [Fintype Site]
    (H : HermitianClifford) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) (δ : ℝ) (hδ : 0 ≤ δ)
    (hdiff : ∀ x, ‖(v x : ℂ) - (u x : ℂ)‖ ≤ δ)
    (ψ : HilbertState Site) :
    ‖directionalShiftDefectHilbertCLM H.toClifford τ v u ψ‖ ≤
      δ * ‖ψ‖ := by
  have hsq := directionalShift_sub_stateIP_re_le H τ v u δ hδ hdiff
    (hilbertToState ψ)
  rw [← stateToHilbert_norm_sq] at hsq
  rw [← directionalShiftDefectHilbertCLM_apply] at hsq
  rw [hilbertToState_stateIP_re] at hsq
  apply (sq_le_sq₀ (norm_nonneg _)
    (mul_nonneg hδ (norm_nonneg _))).mp
  simpa only [mul_pow] using hsq

theorem directionalShiftDefectHilbertCLM_opNorm_le
    {Site : Type u} [Fintype Site]
    (H : HermitianClifford) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) (δ : ℝ) (hδ : 0 ≤ δ)
    (hdiff : ∀ x, ‖(v x : ℂ) - (u x : ℂ)‖ ≤ δ) :
    ‖directionalShiftDefectHilbertCLM H.toClifford τ v u‖ ≤ δ := by
  exact ContinuousLinearMap.opNorm_le_bound _ hδ
    (directionalShiftDefectHilbertCLM_norm_le H τ v u δ hδ hdiff)


/-- Largest pointwise phase mismatch on a finite link set. -/
def edgeMismatchSup {Site : Type u} [Fintype Site] [Nonempty Site]
    (v u : Link (Site := Site)) : ℝ :=
  Finset.univ.sup' Finset.univ_nonempty
    (fun x => ‖(v x : ℂ) - (u x : ℂ)‖)

theorem edgeMismatch_le_sup {Site : Type u} [Fintype Site] [Nonempty Site]
    (v u : Link (Site := Site)) (x : Site) :
    ‖(v x : ℂ) - (u x : ℂ)‖ ≤ edgeMismatchSup v u := by
  exact Finset.le_sup' (fun y : Site => ‖(v y : ℂ) - (u y : ℂ)‖)
    (Finset.mem_univ x)

theorem edgeMismatchSup_nonneg {Site : Type u} [Fintype Site] [Nonempty Site]
    (v u : Link (Site := Site)) : 0 ≤ edgeMismatchSup v u := by
  let x : Site := Classical.choice inferInstance
  exact (norm_nonneg ((v x : ℂ) - (u x : ℂ))).trans
    (edgeMismatch_le_sup v u x)

/-- Sharp constant-one Hilbert operator-norm bound by the maximal local phase mismatch. -/
theorem directionalShiftDefectHilbertCLM_opNorm_le_sup
    {Site : Type u} [Fintype Site] [Nonempty Site]
    (H : HermitianClifford) (τ : Site ≃ Site)
    (v u : Link (Site := Site)) :
    ‖directionalShiftDefectHilbertCLM H.toClifford τ v u‖ ≤
      edgeMismatchSup v u := by
  exact directionalShiftDefectHilbertCLM_opNorm_le H τ v u
    (edgeMismatchSup v u) (edgeMismatchSup_nonneg v u)
    (edgeMismatch_le_sup v u)


abbrev HalfHilbertState (Site : Type u) := HilbertState (HalfSite Site)

def halfStateToHilbert {Site : Type u}
    (Ψ : State (Site := HalfSite Site)) : HalfHilbertState Site :=
  (((Real.sqrt 2)⁻¹ : ℝ) : ℂ) • stateToHilbert Ψ

@[simp] theorem halfStateToHilbert_add {Site : Type u}
    (Ψ Φ : State (Site := HalfSite Site)) :
    halfStateToHilbert (Ψ + Φ) = halfStateToHilbert Ψ + halfStateToHilbert Φ := by
  simp [halfStateToHilbert, smul_add]

@[simp] theorem halfStateToHilbert_smul {Site : Type u}
    (c : ℂ) (Ψ : State (Site := HalfSite Site)) :
    halfStateToHilbert (c • Ψ) = c • halfStateToHilbert Ψ := by
  simp [halfStateToHilbert, smul_smul, mul_comm]

theorem halfScale_norm_sq :
    ‖((((Real.sqrt 2)⁻¹ : ℝ) : ℂ))‖ ^ 2 = (2 : ℝ)⁻¹ := by
  have htwo : 0 < Real.sqrt 2 := Real.sqrt_pos.2 (by norm_num)
  rw [Complex.norm_real, Real.norm_eq_abs, abs_of_pos (inv_pos.2 htwo)]
  rw [inv_pow]
  rw [Real.sq_sqrt (by norm_num)]

/-- The scaled Euclidean norm is the half-cell Hilbert energy. -/
theorem halfStateToHilbert_norm_sq {Site : Type u} [Fintype Site]
    (Ψ : State (Site := HalfSite Site)) :
    ‖halfStateToHilbert Ψ‖ ^ 2 = (halfCellIP Ψ Ψ).re := by
  rw [halfStateToHilbert, norm_smul, mul_pow, halfScale_norm_sq]
  rw [stateToHilbert_norm_sq]
  unfold halfCellIP
  rw [Complex.mul_re]
  have him : (stateIP Ψ Ψ).im = 0 := by
    unfold stateIP
    rw [Complex.im_sum]
    apply Finset.sum_eq_zero
    intro x hx
    rw [ip_self_eq_normSq_sum]
    simp
  simp [him]

/-- The actual fine adjacent-scale defect, realized in the half-cell normalized
Euclidean Hilbert space. -/
def fineEdgeDefectHilbertLinear {Site : Type u} [Fintype Site]
    (P : FineEdgePair Site) (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    HilbertState Site →ₗ[ℂ] HalfHilbertState Site where
  toFun := fun ψ =>
    halfStateToHilbert (P.fineIntertwiningDefect A τ u (hilbertToState ψ))
  map_add' := by
    intro ψ φ
    rw [hilbertToState_add, fineEdgeIntertwiningDefect_add,
      halfStateToHilbert_add]
  map_smul' := by
    intro c ψ
    rw [hilbertToState_smul, fineEdgeIntertwiningDefect_smul,
      halfStateToHilbert_smul]
    rfl

def fineEdgeDefectHilbertCLM {Site : Type u} [Fintype Site]
    (P : FineEdgePair Site) (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    HilbertState Site →L[ℂ] HalfHilbertState Site :=
  LinearMap.toContinuousLinearMap (fineEdgeDefectHilbertLinear P A τ u)

@[simp] theorem fineEdgeDefectHilbertCLM_apply {Site : Type u} [Fintype Site]
    (P : FineEdgePair Site) (A : CliffordInvolution) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : HilbertState Site) :
    fineEdgeDefectHilbertCLM P A τ u ψ =
      halfStateToHilbert
        (P.fineIntertwiningDefect A τ u (hilbertToState ψ)) := rfl

/-- The weighted fine defect has exactly the same Hilbert norm as its coarse
reconstructed-link mismatch. -/
theorem fineEdgeDefectHilbertCLM_norm_eq_coarse
    {Site : Type u} [Fintype Site]
    (P : FineEdgePair Site) (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (ψ : HilbertState Site) :
    ‖fineEdgeDefectHilbertCLM P H.toClifford τ u ψ‖ =
      ‖directionalShiftDefectHilbertCLM H.toClifford τ P.productLink u ψ‖ := by
  apply (sq_eq_sq₀ (norm_nonneg _) (norm_nonneg _)).mp
  rw [fineEdgeDefectHilbertCLM_apply, halfStateToHilbert_norm_sq]
  rw [directionalShiftDefectHilbertCLM_apply, stateToHilbert_norm_sq]
  exact congrArg Complex.re
    (P.fineIntertwiningDefect_halfCellIP H τ u (hilbertToState ψ))

/-- Constant-one norm estimate for the genuine normalized fine refinement defect. -/
theorem fineEdgeDefectHilbertCLM_norm_le
    {Site : Type u} [Fintype Site]
    (P : FineEdgePair Site) (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (δ : ℝ) (hδ : 0 ≤ δ)
    (hdiff : ∀ x, ‖(P.productLink x : ℂ) - (u x : ℂ)‖ ≤ δ)
    (ψ : HilbertState Site) :
    ‖fineEdgeDefectHilbertCLM P H.toClifford τ u ψ‖ ≤ δ * ‖ψ‖ := by
  rw [fineEdgeDefectHilbertCLM_norm_eq_coarse]
  exact directionalShiftDefectHilbertCLM_norm_le H τ P.productLink u δ hδ hdiff ψ

/-- Sharp constant-one operator-norm bound for the normalized fine defect. -/
theorem fineEdgeDefectHilbertCLM_opNorm_le
    {Site : Type u} [Fintype Site]
    (P : FineEdgePair Site) (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) (δ : ℝ) (hδ : 0 ≤ δ)
    (hdiff : ∀ x, ‖(P.productLink x : ℂ) - (u x : ℂ)‖ ≤ δ) :
    ‖fineEdgeDefectHilbertCLM P H.toClifford τ u‖ ≤ δ := by
  exact ContinuousLinearMap.opNorm_le_bound _ hδ
    (fineEdgeDefectHilbertCLM_norm_le P H τ u δ hδ hdiff)

/-- Supremum specialization of the sharp normalized fine-defect estimate. -/
theorem fineEdgeDefectHilbertCLM_opNorm_le_sup
    {Site : Type u} [Fintype Site] [Nonempty Site]
    (P : FineEdgePair Site) (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    ‖fineEdgeDefectHilbertCLM P H.toClifford τ u‖ ≤
      edgeMismatchSup P.productLink u := by
  exact fineEdgeDefectHilbertCLM_opNorm_le P H τ u
    (edgeMismatchSup P.productLink u)
    (edgeMismatchSup_nonneg P.productLink u)
    (edgeMismatch_le_sup P.productLink u)


/-- Multiplicative edge reconstruction error. -/
def edgeRatio {Site : Type u} (v u : Link (Site := Site)) (x : Site) : Circle :=
  v x * (u x)⁻¹

@[simp] theorem edgeRatio_eq_one_iff {Site : Type u}
    (v u : Link (Site := Site)) (x : Site) :
    edgeRatio v u x = 1 ↔ v x = u x := by
  unfold edgeRatio
  exact mul_inv_eq_one

theorem edgeMismatch_eq_ratioError {Site : Type u}
    (v u : Link (Site := Site)) (x : Site) :
    ‖(v x : ℂ) - (u x : ℂ)‖ =
      ‖(edgeRatio v u x : ℂ) - 1‖ := by
  have hu : ‖(((u x)⁻¹ : Circle) : ℂ)‖ = 1 := by simp
  calc
    ‖(v x : ℂ) - (u x : ℂ)‖ =
        ‖((v x : ℂ) - (u x : ℂ)) * (((u x)⁻¹ : Circle) : ℂ)‖ := by
          rw [norm_mul, hu, mul_one]
    _ = ‖(edgeRatio v u x : ℂ) - 1‖ := by
      congr 1
      unfold edgeRatio
      push_cast
      have hu0 : (u x : ℂ) ≠ 0 := by simp
      field_simp

/-- Largest multiplicative reconstruction-ratio error. -/
def edgeRatioSup {Site : Type u} [Fintype Site] [Nonempty Site]
    (v u : Link (Site := Site)) : ℝ :=
  Finset.univ.sup' Finset.univ_nonempty
    (fun x => ‖(edgeRatio v u x : ℂ) - 1‖)

theorem edgeRatioError_le_sup {Site : Type u} [Fintype Site] [Nonempty Site]
    (v u : Link (Site := Site)) (x : Site) :
    ‖(edgeRatio v u x : ℂ) - 1‖ ≤ edgeRatioSup v u := by
  exact Finset.le_sup'
    (fun y : Site => ‖(edgeRatio v u y : ℂ) - 1‖) (Finset.mem_univ x)

theorem edgeMismatchSup_eq_edgeRatioSup
    {Site : Type u} [Fintype Site] [Nonempty Site]
    (v u : Link (Site := Site)) :
    edgeMismatchSup v u = edgeRatioSup v u := by
  apply le_antisymm
  · apply Finset.sup'_le Finset.univ_nonempty
    intro x hx
    rw [edgeMismatch_eq_ratioError]
    exact edgeRatioError_le_sup v u x
  · apply Finset.sup'_le Finset.univ_nonempty
    intro x hx
    rw [← edgeMismatch_eq_ratioError]
    exact edgeMismatch_le_sup v u x

/-- Ratio form of the sharp fine-edge operator bound. -/
theorem fineEdgeDefectHilbertCLM_opNorm_le_ratioSup
    {Site : Type u} [Fintype Site] [Nonempty Site]
    (P : FineEdgePair Site) (H : HermitianClifford) (τ : Site ≃ Site)
    (u : Link (Site := Site)) :
    ‖fineEdgeDefectHilbertCLM P H.toClifford τ u‖ ≤
      edgeRatioSup P.productLink u := by
  rw [← edgeMismatchSup_eq_edgeRatioSup]
  exact fineEdgeDefectHilbertCLM_opNorm_le_sup P H τ u

/-- The flat quarter-turn half-link witness has maximal edge-ratio error two. -/
@[simp] theorem quarterPair_edgeRatioSup :
    edgeRatioSup (quarterPair PUnit).productLink (fun _ => 1) = 2 := by
  simp [edgeRatioSup, edgeRatio]
  norm_num [Complex.norm_def]

/-- The additive phase-mismatch formulation gives the same concrete value. -/
@[simp] theorem quarterPair_edgeMismatchSup :
    edgeMismatchSup (quarterPair PUnit).productLink (fun _ => 1) = 2 := by
  rw [edgeMismatchSup_eq_edgeRatioSup]
  exact quarterPair_edgeRatioSup

/-- Concrete normalized Hilbert bound for the flat-but-edge-incompatible witness. -/
theorem quarterPair_fineEdgeDefectHilbertCLM_opNorm_le_two :
    ‖fineEdgeDefectHilbertCLM (quarterPair PUnit) hermitianX.toClifford
      (Equiv.refl PUnit) (fun _ => 1)‖ ≤ 2 := by
  simpa using fineEdgeDefectHilbertCLM_opNorm_le_ratioSup
    (quarterPair PUnit) hermitianX (Equiv.refl PUnit) (fun _ => 1)


/-- Geometric mesh law with ratio one half. -/
def dyadicMesh (a₀ : ℝ) (n : ℕ) : ℝ := a₀ * ((2 : ℝ)⁻¹) ^ n

/-- Every fixed initial mesh shrinks to zero under dyadic refinement. -/
theorem tendsto_dyadicMesh_zero (a₀ : ℝ) :
    Tendsto (dyadicMesh a₀) atTop (𝓝 0) := by
  have hpow : Tendsto (fun n : ℕ => ((2 : ℝ)⁻¹) ^ n) atTop (𝓝 0) :=
    tendsto_pow_atTop_nhds_zero_of_norm_lt_one (by norm_num)
  rw [show dyadicMesh a₀ = (fun n : ℕ => a₀ * ((2 : ℝ)⁻¹) ^ n) by rfl]
  simpa only [mul_zero] using hpow.const_mul a₀

/-- A defect channel whose amplitude is proportional to the dyadic mesh. -/
def dyadicScaleBudget (C : ℝ) (n : ℕ) : ℝ := C * ((2 : ℝ)⁻¹) ^ n

/-- A geometrically decaying defect channel is summable. -/
theorem summable_dyadicScaleBudget (C : ℝ) :
    Summable (dyadicScaleBudget C) := by
  have hgeom : Summable (fun n : ℕ => ((2 : ℝ)⁻¹) ^ n) :=
    summable_geometric_of_norm_lt_one (by norm_num)
  rw [show dyadicScaleBudget C = (fun n : ℕ => C * ((2 : ℝ)⁻¹) ^ n) by rfl]
  exact hgeom.mul_left C

/-- The dyadic defect amplitude itself tends to zero. -/
theorem tendsto_dyadicScaleBudget_zero (C : ℝ) :
    Tendsto (dyadicScaleBudget C) atTop (𝓝 0) :=
  tendsto_dyadicMesh_zero C

/-- Explicit summability of the independent edge and curvature channels. -/
theorem summable_dyadicTwoBudget (Cedge Ccurvature : ℝ) :
    Summable (combinedScaleBudget
      (dyadicScaleBudget Cedge) (dyadicScaleBudget Ccurvature)) := by
  exact summable_combinedScaleBudget
    (summable_dyadicScaleBudget Cedge)
    (summable_dyadicScaleBudget Ccurvature)

variable {Y : Type v} [MetricSpace Y] [CompleteSpace Y]

/-- Concrete global-limit theorem for a hierarchy whose edge and curvature
budgets both decay geometrically with the physical dyadic mesh. -/
theorem tendsto_dyadicTwoBudgetLimit (f : ℕ → Y)
    (Cedge Ccurvature : ℝ)
    (hstep : ∀ n, dist (f n) (f n.succ) ≤
      combinedScaleBudget (dyadicScaleBudget Cedge)
        (dyadicScaleBudget Ccurvature) n) :
    Tendsto f atTop
      (𝓝 ((twoBudgetSummableDefect f
        (dyadicScaleBudget Cedge) (dyadicScaleBudget Ccurvature)
        (summable_dyadicScaleBudget Cedge)
        (summable_dyadicScaleBudget Ccurvature) hstep).limit)) := by
  exact tendsto_twoBudgetLimit f
    (dyadicScaleBudget Cedge) (dyadicScaleBudget Ccurvature)
    (summable_dyadicScaleBudget Cedge)
    (summable_dyadicScaleBudget Ccurvature) hstep

/-- Quantitative tail estimate in the explicit dyadic two-budget regime. -/
theorem dist_dyadicTwoBudgetLimit_le_tail (f : ℕ → Y)
    (Cedge Ccurvature : ℝ)
    (hstep : ∀ n, dist (f n) (f n.succ) ≤
      combinedScaleBudget (dyadicScaleBudget Cedge)
        (dyadicScaleBudget Ccurvature) n) (n : ℕ) :
    dist (f n)
      ((twoBudgetSummableDefect f
        (dyadicScaleBudget Cedge) (dyadicScaleBudget Ccurvature)
        (summable_dyadicScaleBudget Cedge)
        (summable_dyadicScaleBudget Ccurvature) hstep).limit) ≤
      ∑' m : ℕ, combinedScaleBudget
        (dyadicScaleBudget Cedge) (dyadicScaleBudget Ccurvature) (n + m) := by
  exact dist_twoBudgetLimit_le_tail f
    (dyadicScaleBudget Cedge) (dyadicScaleBudget Ccurvature)
    (summable_dyadicScaleBudget Cedge)
    (summable_dyadicScaleBudget Ccurvature) hstep n

end Relativistic3DHilbertScalarDefect
end KomorebiPhysics
