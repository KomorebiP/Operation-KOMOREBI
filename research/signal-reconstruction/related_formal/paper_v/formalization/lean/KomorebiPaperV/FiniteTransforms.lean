import Mathlib.Analysis.Real.Sqrt
import KomorebiPaperV.Lifting
import KomorebiPaperV.Packets

/-!
Author: Komorebi P.
Checked source; see the bundled build and axiom audit.
Flat even-length indexing, finite lifting, and exactly normalized real Haar pairs.
The infinite l2 energy/completeness arguments are not supplied by finite identities.
-/

open scoped BigOperators
namespace KomorebiPaperV.FiniteTransforms

variable {K : Type*}

/-- Valid even for n=0. This is literal flat-signal indexing, not an assumed address map. -/
def flatAddressEquiv (n : ℕ) : Fin (2 * n) ≃ Fin n × Fin 2 where
  toFun j := (⟨j.val / 2, by have := j.isLt; omega⟩,
    ⟨j.val % 2, by omega⟩)
  invFun p := ⟨2 * p.1.val + p.2.val, by
    have hi := p.1.isLt
    have hb := p.2.isLt
    omega⟩
  left_inv j := by apply Fin.ext; dsimp; omega
  right_inv p := by
    apply Prod.ext
    · apply Fin.ext
      dsimp
      have hb := p.2.isLt
      omega
    · apply Fin.ext
      dsimp
      have hb := p.2.isLt
      omega

def pairChannels {I : Type*} (c : I → Fin 2 → K) : I → K × K :=
  fun i => (c i 0, c i 1)

def unpairChannels {I : Type*} (p : I → K × K) : I → Fin 2 → K :=
  fun i b => if b = 0 then (p i).1 else (p i).2

theorem unpair_pair {I : Type*} (c : I → Fin 2 → K) :
    unpairChannels (pairChannels c) = c := by
  funext i b
  fin_cases b <;> simp [unpairChannels, pairChannels]

theorem pair_unpair {I : Type*} (p : I → K × K) :
    pairChannels (unpairChannels p) = p := by
  funext i
  apply Prod.ext <;> simp [unpairChannels, pairChannels]

def flatAnalysis (n : ℕ) (x : Fin (2 * n) → K) : Fin n → K × K :=
  pairChannels (KomorebiPaperV.analyzeAddress (flatAddressEquiv n) x)

def flatSynthesis (n : ℕ) (p : Fin n → K × K) : Fin (2 * n) → K :=
  KomorebiPaperV.synthesizeAddress (flatAddressEquiv n) (unpairChannels p)

theorem flat_synthesis_analysis (n : ℕ) (x : Fin (2 * n) → K) :
    flatSynthesis n (flatAnalysis n x) = x := by
  rw [flatSynthesis, flatAnalysis, unpair_pair]
  exact KomorebiPaperV.address_synthesize_analyze (flatAddressEquiv n) x

theorem flat_analysis_synthesis (n : ℕ) (p : Fin n → K × K) :
    flatAnalysis n (flatSynthesis n p) = p := by
  rw [flatAnalysis, flatSynthesis, KomorebiPaperV.address_analyze_synthesize]
  exact pair_unpair p

section Lifting
variable [Field K] [CharZero K]

def liftFlat (n : ℕ) (x : Fin (2 * n) → K) : Fin (2 * n) → K :=
  flatSynthesis n (fun i => KomorebiPaperV.liftingAnalysis (flatAnalysis n x i))

def unliftFlat (n : ℕ) (x : Fin (2 * n) → K) : Fin (2 * n) → K :=
  flatSynthesis n (fun i => KomorebiPaperV.liftingSynthesis (flatAnalysis n x i))

theorem unlift_lift_flat (n : ℕ) (x : Fin (2 * n) → K) :
    unliftFlat n (liftFlat n x) = x := by
  simp only [unliftFlat, liftFlat, flat_analysis_synthesis,
    KomorebiPaperV.lifting_synthesis_analysis, flat_synthesis_analysis]

theorem lift_unlift_flat (n : ℕ) (x : Fin (2 * n) → K) :
    liftFlat n (unliftFlat n x) = x := by
  simp only [liftFlat, unliftFlat, flat_analysis_synthesis,
    KomorebiPaperV.lifting_analysis_synthesis, flat_synthesis_analysis]
end Lifting

noncomputable def haar (x : ℝ × ℝ) : ℝ × ℝ :=
  ((x.1 + x.2) / Real.sqrt 2, (x.1 - x.2) / Real.sqrt 2)

theorem haar_involution (x : ℝ × ℝ) : haar (haar x) = x := by
  have hs : Real.sqrt 2 * Real.sqrt 2 = 2 := by
    simpa only [pow_two] using (Real.sq_sqrt (show (0 : ℝ) ≤ 2 by norm_num))
  apply Prod.ext
  · dsimp [haar]
    rw [← add_div, div_div, hs]
    ring
  · dsimp [haar]
    rw [← sub_div, div_div, hs]
    ring

theorem haar_pair_energy (x : ℝ × ℝ) :
    (haar x).1 ^ 2 + (haar x).2 ^ 2 = x.1 ^ 2 + x.2 ^ 2 := by
  have hs : Real.sqrt 2 ^ 2 = 2 := Real.sq_sqrt (by norm_num)
  dsimp [haar]
  rw [div_pow, div_pow, hs]
  ring

theorem haar_finite_energy {I : Type*} [Fintype I] (x : I → ℝ × ℝ) :
    (∑ i, ((haar (x i)).1 ^ 2 + (haar (x i)).2 ^ 2)) =
      ∑ i, ((x i).1 ^ 2 + (x i).2 ^ 2) := by
  exact Finset.sum_congr rfl (fun i _ => haar_pair_energy (x i))

noncomputable def haarFlat (n : ℕ) (x : Fin (2 * n) → ℝ) : Fin (2 * n) → ℝ :=
  flatSynthesis n (fun i => haar (flatAnalysis n x i))

theorem haar_flat_involution (n : ℕ) (x : Fin (2 * n) → ℝ) :
    haarFlat n (haarFlat n x) = x := by
  simp only [haarFlat, flat_analysis_synthesis, haar_involution, flat_synthesis_analysis]

section MatrixCriterion
variable {I : Type*} [Fintype I] [DecidableEq I] [Semiring K]

theorem matrix_eq_of_all_vectors (M D : Matrix I I K)
    (h : ∀ v : I → K, M.mulVec v = D.mulVec v) : M = D := by
  classical
  ext i j
  have hj := congrFun (h (fun k => if k = j then 1 else 0)) i
  simpa [Matrix.mulVec, dotProduct, mul_ite] using hj

/-- Algebraic matrix criterion. D may be a gain-delay or phase-permutation matrix.
The representation of filter-bank operators by those matrices is a separate bridge. -/
theorem perfect_reconstruction_matrix_iff (R E D : Matrix I I K) :
    (∀ v : I → K, (R * E).mulVec v = D.mulVec v) ↔ R * E = D := by
  constructor
  · exact matrix_eq_of_all_vectors (R * E) D
  · intro h v
    rw [h]
end MatrixCriterion

end KomorebiPaperV.FiniteTransforms
