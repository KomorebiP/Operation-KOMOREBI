module

public import KomorebiPhysics.RefinementTower
public import Mathlib.LinearAlgebra.Matrix.PosDef
public import Mathlib.Analysis.Calculus.Deriv.Mul
public import Mathlib.Analysis.Complex.Order
import all TensorRefinement

/-!
Chapter 4.2 (4.6)--(4.15), finite complex matrices.
Actual matrix-valued real-time derivatives imply the trace-probability law.
Hermiticity, positivity and trace-one normalization have separate roles.
The conjugation bar in (4.14) is essential. No trace-class or unbounded
infinite-dimensional assertion is hidden in these finite statements.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace MixedTransfer
open scoped BigOperators Matrix

variable {n I J K : Type*} [Fintype n] [DecidableEq n]
  [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]
  [Fintype K] [DecidableEq K]

/-- Finite complete orthogonal matrix atlas. Its probabilities and currents
are defined below and are not axiom fields. -/
structure MatrixAtlas (n I : Type*) [Fintype n] [DecidableEq n]
    [Fintype I] [DecidableEq I]
    extends KomorebiPaperVII.PacketFamily (Matrix n n ℂ) I where
  hermitian : ∀ i, (proj i).conjTranspose = proj i

/-- The von Neumann right-hand side, with hbar normalized to one. -/
def generator (H ρ : Matrix n n ℂ) : Matrix n n ℂ :=
  (-Complex.I) • (H * ρ - ρ * H)

/-- The trace of every finite commutator vanishes. No Hermiticity is needed. -/
theorem trace_generator (H ρ : Matrix n n ℂ) : Matrix.trace (generator H ρ) = 0 := by
  simp only [generator, Matrix.trace_smul, Matrix.trace_sub]
  rw [Matrix.trace_mul_comm H ρ, sub_self, smul_zero]

/-- The commutator generator is Hermitian at a Hermitian pair. -/
theorem generator_hermitian (H ρ : Matrix n n ℂ)
    (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) :
    (generator H ρ).conjTranspose = generator H ρ := by
  simp only [generator, Matrix.conjTranspose_smul, Matrix.conjTranspose_sub,
    Matrix.conjTranspose_mul, hH, hρ, star_neg, Complex.star_def, map_neg,
    Complex.conj_I]
  rw [show ρ * H - H * ρ = -(H * ρ - ρ * H) by abel]
  simp

/-- Derivative of an actual matrix coordinate follows from the derivative
in the finite matrix norm. -/
theorem hasDerivAt_entry {ρ : ℝ → Matrix n n ℂ} {dρ : Matrix n n ℂ} {t : ℝ}
    (hρ : HasDerivAt ρ dρ t) (i j : n) :
    HasDerivAt (fun s => ρ s i j) (dρ i j) t := by
  let ev : Matrix n n ℂ →L[ℝ] ℂ :=
    (ContinuousLinearMap.proj j).comp (ContinuousLinearMap.proj i)
  exact ev.hasFDerivAt.comp_hasDerivAt t hρ

/-- Actual derivative of the trace of a constant matrix times a matrix curve. -/
theorem hasDerivAt_trace_mul (B : Matrix n n ℂ) {ρ : ℝ → Matrix n n ℂ}
    {dρ : Matrix n n ℂ} {t : ℝ} (hρ : HasDerivAt ρ dρ t) :
    HasDerivAt (fun s => Matrix.trace (B * ρ s)) (Matrix.trace (B * dρ)) t := by
  simpa only [Matrix.trace, Matrix.diag_apply, Matrix.mul_apply] using
    HasDerivAt.fun_sum (u := Finset.univ) (fun i _ =>
      HasDerivAt.fun_sum (u := Finset.univ) (fun j _ =>
        (hasDerivAt_entry hρ j i).const_mul (B i j)))

/-- Trace preservation is an actual derivative theorem. H may be time-dependent. -/
theorem hasDerivAt_trace {H : Matrix n n ℂ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hρ : HasDerivAt ρ (generator H (ρ t)) t) :
    HasDerivAt (fun s => Matrix.trace (ρ s)) 0 t := by
  simpa only [one_mul, trace_generator] using hasDerivAt_trace_mul 1 hρ

/-- All-time trace conservation, even for state- and time-dependent H,
provided an actual trajectory satisfies the matrix equation. -/
theorem trace_constant (H : Matrix n n ℂ → ℝ → Matrix n n ℂ)
    (ρ : ℝ → Matrix n n ℂ)
    (hρ : ∀ t, HasDerivAt ρ (generator (H (ρ t) t) (ρ t)) t) (s t : ℝ) :
    Matrix.trace (ρ s) = Matrix.trace (ρ t) := by
  exact is_const_of_deriv_eq_zero
    (fun u => (hasDerivAt_trace (hρ u)).differentiableAt)
    (fun u => (hasDerivAt_trace (hρ u)).deriv) s t

/-- Actual rank-one operator, without a normalization assumption. -/
def pureState (ψ : n → ℂ) : Matrix n n ℂ := Matrix.vecMulVec ψ (star ψ)

/-- A rank-one state is positive semidefinite, not merely Hermitian. -/
theorem pureState_posSemidef (ψ : n → ℂ) : (pureState ψ).PosSemidef :=
  Matrix.posSemidef_vecMulVec_self_star ψ

/-- Tr(M |psi><psi|) is the Hermitian quadratic pairing. -/
theorem trace_mul_pureState (M : Matrix n n ℂ) (ψ : n → ℂ) :
    Matrix.trace (M * pureState ψ) = star ψ ⬝ᵥ (M *ᵥ ψ) := by
  rw [pureState, Matrix.mul_vecMulVec, Matrix.trace_vecMulVec, dotProduct_comm]

namespace MatrixAtlas
variable (P : MatrixAtlas n I)

/-- Complex trace amplitude before taking its imaginary part. -/
def amplitude (H ρ : Matrix n n ℂ) (i j : I) : ℂ :=
  Matrix.trace (P.proj i * H * P.proj j * ρ)

/-- Equation (4.8). Receiving index precedes source index. -/
def current (H ρ : Matrix n n ℂ) (i j : I) : ℝ :=
  2 * (P.amplitude H ρ i j).im

/-- Real-valued packet probability. Equality with the complex trace is proved
under Hermiticity, rather than silently assuming the trace is real. -/
def probability (ρ : Matrix n n ℂ) (i : I) : ℝ :=
  (Matrix.trace (P.proj i * ρ)).re

/-- The trace defining a packet probability is real for Hermitian rho. -/
theorem trace_probability_real (ρ : Matrix n n ℂ) (hρ : ρ.conjTranspose = ρ) (i : I) :
    (Matrix.trace (P.proj i * ρ)).im = 0 := by
  have h : star (Matrix.trace (P.proj i * ρ)) = Matrix.trace (P.proj i * ρ) := by
    rw [← Matrix.trace_conjTranspose, Matrix.conjTranspose_mul, hρ, P.hermitian,
      Matrix.trace_mul_comm]
  have hi := congrArg Complex.im h
  simp only [Complex.star_def, Complex.conj_im] at hi
  linarith

/-- Literal complex-trace form of equation (4.7). -/
theorem probability_cast (ρ : Matrix n n ℂ) (hρ : ρ.conjTranspose = ρ) (i : I) :
    (P.probability ρ i : ℂ) = Matrix.trace (P.proj i * ρ) := by
  apply Complex.ext
  · rfl
  · simpa only [Complex.ofReal_im] using (P.trace_probability_real ρ hρ i).symm

/-- Equation (4.14), with the indispensable complex conjugation. -/
theorem amplitude_reverse (H ρ : Matrix n n ℂ)
    (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) (i j : I) :
    P.amplitude H ρ j i = star (P.amplitude H ρ i j) := by
  unfold amplitude
  rw [← Matrix.trace_conjTranspose]
  simp only [Matrix.conjTranspose_mul, hH, hρ, P.hermitian]
  rw [Matrix.trace_mul_comm ρ]
  simp only [Matrix.mul_assoc]

/-- Equation (4.10), proved from trace cyclicity and Hermiticity. -/
theorem current_antisymm (H ρ : Matrix n n ℂ)
    (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) (i j : I) :
    P.current H ρ i j = -P.current H ρ j i := by
  rw [current, current, P.amplitude_reverse H ρ hH hρ i j]
  simp

/-- Diagonal unitary transfer is zero. -/
theorem current_diagonal (H ρ : Matrix n n ℂ)
    (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) (i : I) :
    P.current H ρ i i = 0 := by
  have h := P.current_antisymm H ρ hH hρ i i
  linarith

/-- Reconstruction on the source side of a transfer amplitude. -/
theorem amplitude_row_sum (H ρ : Matrix n n ℂ) (i : I) :
    (∑ j, P.amplitude H ρ i j) = Matrix.trace (P.proj i * H * ρ) := by
  simp only [amplitude, ← Matrix.trace_sum, ← Finset.sum_mul, ← Finset.mul_sum,
    P.sum_proj, mul_one]

/-- Reconstruction on the receiving side, retaining cyclic operator order. -/
theorem amplitude_column_sum (H ρ : Matrix n n ℂ) (i : I) :
    (∑ j, P.amplitude H ρ j i) = Matrix.trace (P.proj i * ρ * H) := by
  simp only [amplitude, ← Matrix.trace_sum, ← Finset.sum_mul, P.sum_proj, one_mul]
  rw [Matrix.trace_mul_cycle]

/-- The resolved commutator expansion (4.12)--(4.13). -/
theorem trace_generator_resolved (H ρ : Matrix n n ℂ) (i : I) :
    Matrix.trace (P.proj i * generator H ρ) =
      (-Complex.I) * ∑ j, (P.amplitude H ρ i j - P.amplitude H ρ j i) := by
  rw [Finset.sum_sub_distrib, P.amplitude_row_sum, P.amplitude_column_sum]
  simp only [generator, Matrix.mul_smul, Matrix.mul_sub, Matrix.trace_smul,
    Matrix.trace_sub, smul_eq_mul, Matrix.mul_assoc]

/-- Trace of the actual matrix generator gives exactly the current row sum. -/
theorem probability_rate (H ρ : Matrix n n ℂ)
    (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) (i : I) :
    (Matrix.trace (P.proj i * generator H ρ)).re = ∑ j, P.current H ρ i j := by
  rw [P.trace_generator_resolved, Finset.mul_sum, Complex.re_sum]
  apply Finset.sum_congr rfl
  intro j _
  rw [P.amplitude_reverse H ρ hH hρ i j]
  simp [current, Complex.mul_re, Complex.sub_im, two_mul]

/-- Equation (4.9), actual derivative of the real packet probability. -/
theorem hasDerivAt_probability {H : Matrix n n ℂ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (generator H (ρ t)) t) (i : I) :
    HasDerivAt (fun s => P.probability (ρ s) i) (∑ j, P.current H (ρ t) i j) t := by
  have h := Complex.reCLM.hasFDerivAt.comp_hasDerivAt t
    (hasDerivAt_trace_mul (P.proj i) hρ)
  simpa only [Function.comp_def, Complex.reCLM_apply, ← probability,
    P.probability_rate H (ρ t) hH hρt] using h

/-- Cancellation holds on every finite subatlas. -/
theorem internal_current_zero (H ρ : Matrix n n ℂ)
    (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) (s : Finset I) :
    (∑ i ∈ s, ∑ j ∈ s, P.current H ρ i j) = 0 :=
  antisymmetric_sum_zero _ s (fun i _ j _ => P.current_antisymm H ρ hH hρ i j)

/-- The boundary identity also holds for mixed states. -/
theorem boundary_balance (H ρ : Matrix n n ℂ)
    (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) (s : Finset I) :
    (∑ i ∈ s, ∑ j, P.current H ρ i j) =
      ∑ i ∈ s, ∑ j ∈ sᶜ, P.current H ρ i j := by
  calc
    _ = ∑ i ∈ s, ((∑ j ∈ s, P.current H ρ i j) +
        ∑ j ∈ sᶜ, P.current H ρ i j) := by
      apply Finset.sum_congr rfl
      intro i _
      exact (Finset.sum_add_sum_compl s _).symm
    _ = _ := by
      rw [Finset.sum_add_distrib, P.internal_current_zero H ρ hH hρ, zero_add]

/-- Derivative of an actual subsystem probability equals only external flux. -/
theorem hasDerivAt_subset_probability {H : Matrix n n ℂ}
    {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (generator H (ρ t)) t) (s : Finset I) :
    HasDerivAt (fun u => ∑ i ∈ s, P.probability (ρ u) i)
      (∑ i ∈ s, ∑ j ∈ sᶜ, P.current H (ρ t) i j) t := by
  have h := HasDerivAt.fun_sum (u := s)
    (fun i _ => P.hasDerivAt_probability hH hρt hρ i)
  rwa [P.boundary_balance H (ρ t) hH hρt] at h

/-- Equation (4.11), zero derivative of the total actual probability. -/
theorem hasDerivAt_total_probability {H : Matrix n n ℂ}
    {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (generator H (ρ t)) t) :
    HasDerivAt (fun s => ∑ i, P.probability (ρ s) i) 0 t := by
  have h := HasDerivAt.fun_sum (u := Finset.univ)
    (fun i _ => P.hasDerivAt_probability hH hρt hρ i)
  rwa [P.internal_current_zero H (ρ t) hH hρt Finset.univ] at h

/-- Total packet probability is the real trace, independently of positivity. -/
theorem sum_probability (ρ : Matrix n n ℂ) :
    (∑ i, P.probability ρ i) = (Matrix.trace ρ).re := by
  simp only [probability, ← Complex.re_sum, ← Matrix.trace_sum,
    ← Finset.sum_mul, P.sum_proj, one_mul]

/-- A positive semidefinite rho has nonnegative projector probabilities.
The trace is rewritten as a positive sandwich using projector idempotence. -/
theorem probability_nonneg (ρ : Matrix n n ℂ) (hρ : ρ.PosSemidef) (i : I) :
    0 ≤ P.probability ρ i := by
  have h := (hρ.conjTranspose_mul_mul_same (P.proj i)).trace_nonneg
  have ht : Matrix.trace ((P.proj i).conjTranspose * ρ * P.proj i) =
      Matrix.trace (P.proj i * ρ) := by
    rw [P.hermitian, Matrix.trace_mul_cycle', P.toPacketFamily.idempotent]
  rw [ht] at h
  exact (Complex.nonneg_iff.mp h).1

/-- Positivity plus trace one gives a genuine finite probability vector. -/
theorem probability_normalized (ρ : Matrix n n ℂ) (hρ : ρ.PosSemidef)
    (htrace : Matrix.trace ρ = 1) :
    (∑ i, P.probability ρ i) = 1 ∧ ∀ i, 0 ≤ P.probability ρ i ∧ P.probability ρ i ≤ 1 := by
  have hs : (∑ i, P.probability ρ i) = 1 := by rw [P.sum_probability, htrace]; rfl
  refine ⟨hs, fun i => ⟨P.probability_nonneg ρ hρ i, ?_⟩⟩
  have hle := Finset.single_le_sum (fun j (_ : j ∈ Finset.univ) =>
    P.probability_nonneg ρ hρ j) (Finset.mem_univ i)
  exact hs ▸ hle

/-- Equation (4.15) is the pure-state specialization of the trace current. -/
theorem pureState_current (H : Matrix n n ℂ) (ψ : n → ℂ) (i j : I) :
    P.current H (pureState ψ) i j =
      2 * (star (P.proj i *ᵥ ψ) ⬝ᵥ (H *ᵥ (P.proj j *ᵥ ψ))).im := by
  unfold current amplitude
  rw [trace_mul_pureState, ← Matrix.mulVec_mulVec, ← Matrix.mulVec_mulVec,
    Matrix.dotProduct_mulVec, Matrix.star_mulVec, P.hermitian]

/-- Coarsen a genuine finite matrix atlas by an address map. -/
def coarsen (f : I → J) : MatrixAtlas n J where
  proj := KomorebiPaperVII.TensorRefinement.coarse P.proj f
  mul_proj := KomorebiPaperVII.TensorRefinement.coarse_mul P.proj f P.mul_proj
  sum_proj := KomorebiPaperVII.TensorRefinement.coarse_complete P.proj f P.sum_proj
  hermitian := KomorebiPaperVII.TensorRefinement.coarse_selfAdjoint P.proj f P.hermitian

/-- The matrix projector is the exact sum on its address fiber. -/
theorem coarsen_proj (f : I → J) (a : J) :
    (P.coarsen f).proj a = ∑ i ∈ Atlas.fiber f a, P.proj i := by
  simp only [coarsen, KomorebiPaperVII.TensorRefinement.coarse,
    Atlas.fiber, Finset.sum_filter]

/-- Coarse mixed-state probabilities are exact sums of fine ones. -/
theorem coarsen_probability (f : I → J) (ρ : Matrix n n ℂ) (a : J) :
    (P.coarsen f).probability ρ a = ∑ i ∈ Atlas.fiber f a, P.probability ρ i := by
  simp only [probability, P.coarsen_proj, Finset.sum_mul, Matrix.trace_sum, Complex.re_sum]

/-- Coarse trace currents are exact double sums, for arbitrary H and rho. -/
theorem coarsen_current (f : I → J) (H ρ : Matrix n n ℂ) (a b : J) :
    (P.coarsen f).current H ρ a b =
      ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, P.current H ρ i j := by
  simp only [current, amplitude, P.coarsen_proj, Finset.sum_mul, Finset.mul_sum,
    Matrix.trace_sum, Complex.im_sum]
  rw [Finset.sum_comm]
  simp only [Finset.mul_sum]

/-- Matrix atlas projectors also satisfy the associative tower exactly. -/
theorem coarsen_coarsen_proj (f : I → J) (g : J → K) (c : K) :
    ((P.coarsen f).coarsen g).proj c = (P.coarsen (g ∘ f)).proj c :=
  congrFun (RefinementTower.push_comp f g P.proj) c

/-- Coarse probability continuity with its slope expanded to fine currents. -/
theorem hasDerivAt_coarse_probability (f : I → J) {H : Matrix n n ℂ}
    {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (generator H (ρ t)) t) (a : J) :
    HasDerivAt (fun u => (P.coarsen f).probability (ρ u) a)
      (∑ b, ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, P.current H (ρ t) i j) t := by
  simpa only [P.coarsen_current] using
    (P.coarsen f).hasDerivAt_probability hH hρt hρ a

end MatrixAtlas
end MixedTransfer
end KomorebiPhysics
