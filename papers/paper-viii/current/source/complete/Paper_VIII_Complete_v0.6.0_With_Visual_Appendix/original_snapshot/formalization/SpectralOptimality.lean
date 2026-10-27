module
public import DiagonalTruncation
public import KernelFrame
import all SmallCoreNorms
import all DiagonalTruncation
import all SmallCoreTransfer
public import Mathlib.Tactic
/-! Author: Komorebi P. Spectral low-rank lower bound by a prefix-kernel witness.
No Eckart--Young theorem or low-rank lower bound is assumed. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {d : ℕ}

noncomputable def prefixEmbedding (k : ℕ) (hk : k+1≤d) :
    Matrix (Fin d) (Fin (k+1)) ℂ :=
  fun i j => if i=Fin.castLE hk j then 1 else 0

theorem prefix_isometry (k : ℕ) (hk : k+1≤d) :
    (prefixEmbedding k hk)ᴴ * prefixEmbedding k hk = 1 := by
  ext i j
  simp [prefixEmbedding,Matrix.mul_apply,Matrix.conjTranspose_apply,Matrix.one_apply,eq_comm]

theorem prefix_support (k : ℕ) (hk : k+1≤d) (z : Fin (k+1) → ℂ)
    (i : Fin d) (hi : k+1 ≤ i.val) : (prefixEmbedding k hk *ᵥ z) i = 0 := by
  simp only [Matrix.mulVec,dotProduct]
  apply Finset.sum_eq_zero
  intro j _
  have hne : i ≠ Fin.castLE hk j := by
    intro he
    have hv : i.val=j.val := by simpa using congrArg Fin.val he
    have := j.isLt
    omega
  simp [prefixEmbedding,hne]

set_option backward.isDefEq.respectTransparency false in
theorem rank_lt_kernel_witness {m n : Type*} [Fintype m] [Fintype n]
    [DecidableEq m] [DecidableEq n] (B : Matrix m n ℂ) (hB : B.rank < Fintype.card n) :
    ∃ z : EuclideanSpace ℂ n, z≠0 ∧ B*ᵥ z=0 := by
  let f := Matrix.toEuclideanLin B
  have hr := Matrix.rank_eq_finrank_range_toLin B
    (EuclideanSpace.basisFun m ℂ).toBasis (EuclideanSpace.basisFun n ℂ).toBasis
  rw [←Matrix.toEuclideanLin_eq_toLin_orthonormal] at hr
  have hn := f.finrank_range_add_finrank_ker
  have hp : 0 < Module.finrank ℂ f.ker := by
    rw [←hr,finrank_euclideanSpace] at hn
    omega
  have hker : f.ker ≠ ⊥ := Submodule.one_le_finrank_iff.mp hp
  obtain ⟨z,hz,hne⟩ := f.ker.ne_bot_iff.mp hker
  refine ⟨z,hne,?_⟩
  exact congrArg WithLp.ofLp hz

/-- A rank-k matrix has a nonzero kernel vector supported in the first k+1 coordinates. -/
theorem prefix_kernel_witness (k : ℕ) (hk : k<d)
    (B : Matrix (Fin d) (Fin d) ℂ) (hB : B.rank≤k) :
    ∃ y : EuclideanSpace ℂ (Fin d), y≠0 ∧ B*ᵥ y=0 ∧
      ∀ i : Fin d, k+1 ≤ i.val → y i=0 := by
  let J := prefixEmbedding k (by omega : k+1≤d)
  have hj : Jᴴ*J=1 := prefix_isometry k _
  have hr : (B*J).rank < Fintype.card (Fin (k+1)) := by
    have := Matrix.rank_mul_le_left B J
    simp only [Fintype.card_fin]
    omega
  obtain ⟨z,hz,hbz⟩ := rank_lt_kernel_witness (B*J) hr
  let y : EuclideanSpace ℂ (Fin d) := WithLp.toLp 2 (J*ᵥ z)
  have hy : y≠0 := by
    intro he
    have he' : J*ᵥ z=0 := congrArg WithLp.ofLp he
    have hz' : (z : Fin (k+1) → ℂ)=0 := by
      calc
        (z : Fin (k+1) → ℂ) = (Jᴴ*J)*ᵥ z := by rw [hj,Matrix.one_mulVec]
        _ = Jᴴ*ᵥ(J*ᵥ z) := (Matrix.mulVec_mulVec _ _ _).symm
        _ = 0 := by rw [he',Matrix.mulVec_zero]
    apply hz
    exact (EuclideanSpace.equiv (Fin (k+1)) ℂ).injective hz'
  refine ⟨y,hy,?_,?_⟩
  · change B*ᵥ(J*ᵥ z)=0
    rw [Matrix.mulVec_mulVec]
    exact hbz
  · intro i hi
    exact prefix_support k _ z i hi

section Operator
open scoped Matrix.Norms.L2Operator

theorem prefix_diagonal_lower (σ : Fin d → ℝ) (hσ : ∀ i, 0≤σ i)
    (hsort : Antitone σ) (k : ℕ) (hk : k<d) (y : EuclideanSpace ℂ (Fin d))
    (hy : ∀ i : Fin d, k+1 ≤ i.val → y i=0) :
    σ ⟨k,hk⟩ * ‖y‖ ≤ ‖WithLp.toLp 2 (diag σ*ᵥ y)‖ := by
  apply (sq_le_sq₀ (mul_nonneg (hσ _) (norm_nonneg y)) (norm_nonneg _)).mp
  rw [mul_pow,EuclideanSpace.norm_sq_eq,EuclideanSpace.norm_sq_eq,Finset.mul_sum]
  apply Finset.sum_le_sum
  intro i _
  by_cases hi : i.val<k+1
  · have hle : σ ⟨k,hk⟩ ≤ σ i := hsort (by show i.val ≤ k; omega)
    have hs : σ ⟨k,hk⟩^2 ≤ σ i^2 := by nlinarith [hσ i,hσ ⟨k,hk⟩]
    simpa [diag,Matrix.mulVec_diagonal,norm_mul,mul_pow,Complex.norm_real,
      Real.norm_eq_abs,sq_abs] using mul_le_mul_of_nonneg_right hs (sq_nonneg ‖y i‖)
  · have hz := hy i (by omega)
    simp [diag,Matrix.mulVec_diagonal,hz]

theorem diagonal_spectral_lower (σ : Fin d → ℝ) (hσ : ∀ i, 0≤σ i)
    (hsort : Antitone σ) (k : ℕ) (B : Matrix (Fin d) (Fin d) ℂ) (hB : B.rank≤k) :
    nextSingular σ k ≤ spectralNorm (diag σ-B) := by
  by_cases hk : k<d
  · obtain ⟨y,hy,hby,hys⟩ := prefix_kernel_witness k hk B hB
    have hl := prefix_diagonal_lower σ hσ hsort k hk y hys
    have hu := Matrix.l2_opNorm_mulVec (diag σ-B) y
    have he : (diag σ-B)*ᵥ y=diag σ*ᵥ y := by rw [Matrix.sub_mulVec,hby,sub_zero]
    rw [he] at hu
    have hle : σ ⟨k,hk⟩ * ‖y‖ ≤ ‖diag σ-B‖ * ‖y‖ := hl.trans hu
    have hp : 0<‖y‖ := norm_pos_iff.mpr hy
    have hb : σ ⟨k,hk⟩ ≤ ‖diag σ-B‖ := by nlinarith
    simpa [nextSingular,hk,spectralNorm] using hb
  · simp only [nextSingular,hk]
    unfold spectralNorm
    positivity

theorem diagonal_spectral_best (σ : Fin d → ℝ) (hσ : ∀ i, 0≤σ i)
    (hsort : Antitone σ) (k : ℕ) :
    BestRank spectralNorm (diag σ) (diag (kept σ k)) k := by
  refine ⟨rank_kept_le σ k,fun B hB => ?_⟩
  rw [diagonal_residual,spectral_diagonal_tail σ hσ hsort]
  exact diagonal_spectral_lower σ hσ hsort k B hB
end Operator
end KomorebiPaperVIII.SmallCore

-- SIXTH AXIOM AUDITS
#print axioms KomorebiPaperVIII.SmallCore.prefix_isometry
#print axioms KomorebiPaperVIII.SmallCore.prefix_support
#print axioms KomorebiPaperVIII.SmallCore.rank_lt_kernel_witness
#print axioms KomorebiPaperVIII.SmallCore.prefix_kernel_witness
#print axioms KomorebiPaperVIII.SmallCore.prefix_diagonal_lower
#print axioms KomorebiPaperVIII.SmallCore.diagonal_spectral_lower
#print axioms KomorebiPaperVIII.SmallCore.diagonal_spectral_best
#print axioms KomorebiPaperVIII.SmallCore.prefixEmbedding
