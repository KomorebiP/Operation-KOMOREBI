module
public import CompactRangeFactors
import all SmallCoreNorms
import all CompactRangeFactors
public import Mathlib.Tactic
/-! Author: Komorebi P. Optimality transfer for every ambient competitor.
The abstract transfer lemmas deliberately expose core optimality as a hypothesis;
the final SVD instantiation is a separate proof obligation. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII.SmallCore
open scoped BigOperators Matrix Classical
variable {m n r s t : Type*} [Fintype m] [Fintype n] [Fintype r] [Fintype s] [Fintype t]
  [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] [DecidableEq t]

def BestRank (N : Matrix m n ℂ → ℝ) (A B : Matrix m n ℂ) (k : ℕ) : Prop :=
  B.rank ≤ k ∧ ∀ C, C.rank ≤ k → N (A-B) ≤ N (A-C)

omit [DecidableEq m] [DecidableEq n] in
theorem compressed_error (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) (G : Matrix r s ℂ) (B : Matrix m n ℂ) :
    G-compress Q V B = compress Q V (lift Q V G - B) := by
  rw [compress_sub,compress_lift Q V hQ hV]

theorem spectral_best_lift (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) (G H : Matrix r s ℂ) (k : ℕ)
    (hbest : BestRank spectralNorm G H k) :
    BestRank spectralNorm (lift Q V G) (lift Q V H) k := by
  refine ⟨(rank_lift_le Q V H).trans hbest.1,fun B hB => ?_⟩
  calc
    spectralNorm (lift Q V G-lift Q V H) = spectralNorm (G-H) := by
      rw [←lift_sub,spectral_lift Q V hQ hV]
    _ ≤ spectralNorm (G-compress Q V B) := hbest.2 _ ((rank_compress_le Q V B).trans hB)
    _ = spectralNorm (compress Q V (lift Q V G-B)) := by rw [compressed_error Q V hQ hV]
    _ ≤ spectralNorm (lift Q V G-B) := spectral_compress_le Q V hQ hV _

omit [DecidableEq m] [DecidableEq n] in
theorem frobenius_best_lift (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (hQ : Qᴴ*Q=1) (hV : Vᴴ*V=1) (G H : Matrix r s ℂ) (k : ℕ)
    (hbest : BestRank frobeniusNorm G H k) :
    BestRank frobeniusNorm (lift Q V G) (lift Q V H) k := by
  refine ⟨(rank_lift_le Q V H).trans hbest.1,fun B hB => ?_⟩
  calc
    frobeniusNorm (lift Q V G-lift Q V H) = frobeniusNorm (G-H) := by
      rw [←lift_sub,frobenius_lift Q V hQ hV]
    _ ≤ frobeniusNorm (G-compress Q V B) := hbest.2 _ ((rank_compress_le Q V B).trans hB)
    _ = frobeniusNorm (compress Q V (lift Q V G-B)) := by rw [compressed_error Q V hQ hV]
    _ ≤ frobeniusNorm (lift Q V G-B) := frobenius_compress_le Q V hQ hV _

omit [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] [DecidableEq t] in
theorem exact_factor_core (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (RL : Matrix r t ℂ) (RR : Matrix s t ℂ) :
    (Q*RL)*(V*RR)ᴴ = lift Q V (RL*RRᴴ) := by
  simp only [lift,Matrix.conjTranspose_mul,Matrix.mul_assoc]

omit [DecidableEq m] [DecidableEq n] in
noncomputable def factorCore (L : Matrix m t ℂ) (R : Matrix n t ℂ) :
    Matrix (Fin (compactDim L)) (Fin (compactDim R)) ℂ := compactR L * (compactR R)ᴴ

omit [DecidableEq m] [DecidableEq n] in
theorem compact_product_reconstruction (L : Matrix m t ℂ) (R : Matrix n t ℂ) :
    L*Rᴴ = lift (compactQ L) (compactQ R) (factorCore L R) := by
  calc
    L*Rᴴ = (compactQ L*compactR L)*(compactQ R*compactR R)ᴴ := by
      rw [compact_factorization,compact_factorization]
    _ = _ := exact_factor_core _ _ _ _

omit [DecidableEq m] [DecidableEq n] in
theorem compact_core_rank (L : Matrix m t ℂ) (R : Matrix n t ℂ) :
    (factorCore L R).rank = (L*Rᴴ).rank := by
  calc
    (factorCore L R).rank = (lift (compactQ L) (compactQ R) (factorCore L R)).rank :=
      (rank_lift _ _ (compactQ_isometry L) (compactQ_isometry R) _).symm
    _ = _ := congrArg Matrix.rank (compact_product_reconstruction L R).symm

omit [Fintype m] [Fintype n] [DecidableEq m] [DecidableEq n] [DecidableEq r] [DecidableEq s] [DecidableEq t] in
theorem factorized_truncation (Q : Matrix m r ℂ) (V : Matrix n s ℂ)
    (U : Matrix r t ℂ) (Z : Matrix s t ℂ) (D : Matrix t t ℂ)
    (hD : Dᴴ=D) (S : Matrix t t ℂ) (hS : D*D=S) :
    (Q*U*D)*(V*Z*D)ᴴ = lift Q V (U*S*Zᴴ) := by
  simp only [Matrix.conjTranspose_mul,hD,Matrix.mul_assoc,lift]
  rw [←Matrix.mul_assoc D D (Zᴴ*Vᴴ),hS]
end KomorebiPaperVIII.SmallCore

-- SIXTH AXIOM AUDITS
#print axioms KomorebiPaperVIII.SmallCore.compressed_error
#print axioms KomorebiPaperVIII.SmallCore.spectral_best_lift
#print axioms KomorebiPaperVIII.SmallCore.frobenius_best_lift
#print axioms KomorebiPaperVIII.SmallCore.exact_factor_core
#print axioms KomorebiPaperVIII.SmallCore.compact_product_reconstruction
#print axioms KomorebiPaperVIII.SmallCore.compact_core_rank
#print axioms KomorebiPaperVIII.SmallCore.factorized_truncation
#print axioms KomorebiPaperVIII.SmallCore.BestRank
#print axioms KomorebiPaperVIII.SmallCore.factorCore
