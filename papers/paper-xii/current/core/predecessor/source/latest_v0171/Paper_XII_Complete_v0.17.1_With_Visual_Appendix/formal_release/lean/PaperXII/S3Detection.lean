import PaperXII.S3Standard
import Mathlib.RepresentationTheory.Irreducible
import Mathlib.LinearAlgebra.Matrix.Trace

/-!
# Canonical spectral projectors detect the standard representation

The projectors are the two-root Lagrange spectral projectors, with their
actual eigenspace action proved below. Four such projectors separate every
endomorphism. This is stronger than detection on the irreducible adjoint
subrepresentations required by adequacy.
-/

namespace PaperXII.S3Detection

open PaperXII.S3Standard
open scoped Matrix

abbrev Mat (k : Type*) := Matrix (Fin 2) (Fin 2) k

/-- The canonical projector onto the `α` eigenspace for an operator with
annihilating polynomial `(X-α)(X-β)` and distinct roots. -/
def CanonicalProjector {k : Type*} [Field k] (A : Mat k) (α β : k) (P : Mat k) : Prop :=
  α ≠ β ∧ (A - α • 1) * (A - β • 1) = 0 ∧ P = (α - β)⁻¹ • (A - β • 1)

variable {k : Type*} [Field k]

theorem projector_fixed_iff {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) :
    P *ᵥ v = v ↔ A *ᵥ v = α • v := by
  have hab : α - β ≠ 0 := sub_ne_zero.mpr h.1
  rw [h.2.2, Matrix.smul_mulVec, Matrix.sub_mulVec, Matrix.smul_mulVec,
    Matrix.one_mulVec]
  constructor
  · intro hv
    have hh := congrArg (fun w : Space k => (α - β) • w) hv
    simp only [smul_smul, mul_inv_cancel₀ hab, one_smul] at hh
    rw [sub_smul] at hh
    exact sub_left_inj.mp hh
  · intro hv
    rw [hv, ← sub_smul, smul_smul, inv_mul_cancel₀ hab, one_smul]

theorem projector_kills_other {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) {v : Space k}
    (hv : A *ᵥ v = β • v) : P *ᵥ v = 0 := by
  rw [h.2.2, Matrix.smul_mulVec, Matrix.sub_mulVec, Matrix.smul_mulVec,
    Matrix.one_mulVec, hv, sub_self, smul_zero]

theorem projector_image_eigen {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) :
    A *ᵥ (P *ᵥ v) = α • (P *ᵥ v) := by
  have hz : (A - α • 1) *ᵥ ((A - β • 1) *ᵥ v) = 0 := by
    rw [Matrix.mulVec_mulVec, h.2.1, Matrix.zero_mulVec]
  rw [Matrix.sub_mulVec, Matrix.smul_mulVec, Matrix.one_mulVec] at hz
  have he := sub_eq_zero.mp hz
  rw [h.2.2, Matrix.smul_mulVec, Matrix.mulVec_smul, he, smul_comm]

theorem projector_idempotent {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) : P * P = P := by
  apply Matrix.mulVec_injective
  funext v
  rw [← Matrix.mulVec_mulVec]
  exact (projector_fixed_iff h _).2 (projector_image_eigen h v)

/-- The image is exactly the `α` eigenspace, rather than merely an invariant summand. -/
theorem projector_image_iff {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) :
    (∃ w, P *ᵥ w = v) ↔ A *ᵥ v = α • v := by
  constructor
  · rintro ⟨w, rfl⟩
    exact projector_image_eigen h w
  · intro hv
    exact ⟨v, (projector_fixed_iff h v).2 hv⟩

/-- The complementary component is an actual `β` eigenvector. -/
theorem projector_complement_eigen {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) :
    A *ᵥ (v - P *ᵥ v) = β • (v - P *ᵥ v) := by
  have hab : α - β ≠ 0 := sub_ne_zero.mpr h.1
  have hh : (α - β) • (P *ᵥ v) = A *ᵥ v - β • v := by
    rw [h.2.2, Matrix.smul_mulVec, smul_smul, mul_inv_cancel₀ hab,
      one_smul, Matrix.sub_mulVec, Matrix.smul_mulVec, Matrix.one_mulVec]
  rw [sub_smul] at hh
  rw [Matrix.mulVec_sub, projector_image_eigen h v, smul_sub]
  linear_combination -hh

theorem projector_eigen_decomposition {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) :
    ∃ vα vβ : Space k, v = vα + vβ ∧
      A *ᵥ vα = α • vα ∧ A *ᵥ vβ = β • vβ := by
  exact ⟨P *ᵥ v, v - P *ᵥ v, by abel,
    projector_image_eigen h v, projector_complement_eigen h v⟩

theorem power_mulVec_of_eigen {A : Mat k} {α : k} {v : Space k}
    (hv : A *ᵥ v = α • v) (n : ℕ) : A ^ n *ᵥ v = α ^ n • v := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ, ← Matrix.mulVec_mulVec, hv, Matrix.mulVec_smul, ih,
      smul_smul, pow_succ]
    congr 1
    exact mul_comm _ _

theorem shifted_power_mulVec_of_eigen {A : Mat k} {α : k} {v : Space k}
    (hv : A *ᵥ v = α • v) (β : k) (n : ℕ) :
    (A - β • 1) ^ n *ᵥ v = (α - β) ^ n • v := by
  apply power_mulVec_of_eigen
  rw [Matrix.sub_mulVec, Matrix.smul_mulVec, Matrix.one_mulVec, hv, sub_smul]

theorem generalized_eigen_iff_projector_fixed {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) {n : ℕ} (hn : 0 < n) :
    (A - α • 1) ^ n *ᵥ v = 0 ↔ P *ᵥ v = v := by
  have hp := shifted_power_mulVec_of_eigen (projector_image_eigen h v) α n
  have hq := shifted_power_mulVec_of_eigen (projector_complement_eigen h v) α n
  have hz : (A - α • 1) ^ n *ᵥ (P *ᵥ v) = 0 := by
    simpa [zero_pow (Nat.ne_of_gt hn)] using hp
  have he : (A - α • 1) ^ n *ᵥ v = (β - α) ^ n • (v - P *ᵥ v) := by
    rw [Matrix.mulVec_sub, hz, sub_zero] at hq
    exact hq
  rw [he]
  constructor
  · intro hv
    have ha : (β - α) ^ n ≠ 0 := pow_ne_zero _ (sub_ne_zero.mpr h.1.symm)
    have hv' : v - P *ᵥ v = 0 := (smul_eq_zero.mp hv).resolve_left ha
    exact (sub_eq_zero.mp hv').symm
  · intro hv
    rw [hv, sub_self, smul_zero]

theorem projector_kills_generalized_other {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) {n : ℕ} (hn : 0 < n)
    (hv : (A - β • 1) ^ n *ᵥ v = 0) : P *ᵥ v = 0 := by
  have hp := shifted_power_mulVec_of_eigen (projector_image_eigen h v) β n
  have hq := shifted_power_mulVec_of_eigen (projector_complement_eigen h v) β n
  have hz : (A - β • 1) ^ n *ᵥ (v - P *ᵥ v) = 0 := by
    simpa [zero_pow (Nat.ne_of_gt hn)] using hq
  rw [Matrix.mulVec_sub, hv, zero_sub, neg_eq_zero] at hz
  rw [hz] at hp
  exact (smul_eq_zero.mp hp.symm).resolve_left (pow_ne_zero _ (sub_ne_zero.mpr h.1))

/-- The complementary projection has exactly the other eigenspace as image. -/
theorem projector_complement_image_iff {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) :
    (∃ w, (1 - P) *ᵥ w = v) ↔ A *ᵥ v = β • v := by
  constructor
  · rintro ⟨w, rfl⟩
    simpa only [Matrix.sub_mulVec, Matrix.one_mulVec] using projector_complement_eigen h w
  · intro hv
    refine ⟨v, ?_⟩
    rw [Matrix.sub_mulVec, Matrix.one_mulVec, projector_kills_other h hv, sub_zero]

/-- For every positive exponent, the generalized eigenspace is the actual
ordinary eigenspace, because the two roots are distinct. -/
theorem generalized_eigen_iff_eigen {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) {n : ℕ} (hn : 0 < n) :
    (A - α • 1) ^ n *ᵥ v = 0 ↔ A *ᵥ v = α • v :=
  (generalized_eigen_iff_projector_fixed h v hn).trans (projector_fixed_iff h v)

/-- The explicitly constructed matrix is the projection onto every positive
order generalized eigenspace, not only the ordinary eigenspace. -/
theorem projector_generalized_image_iff {A P : Mat k} {α β : k}
    (h : CanonicalProjector A α β P) (v : Space k) {n : ℕ} (hn : 0 < n) :
    (∃ w, P *ᵥ w = v) ↔ (A - α • 1) ^ n *ᵥ v = 0 :=
  (projector_image_iff h v).trans (generalized_eigen_iff_eigen h v hn).symm


abbrev F := ZMod 7


def Ps1 : Mat F := !![0, 4; 0, 1]
def Psminus : Mat F := !![1, 3; 0, 0]
def Pt2 : Mat F := !![2, 4; 3, 6]
def Pconj : Mat F := !![1, 0; 4, 0]

theorem ps1_canonical :
    CanonicalProjector (matrixRep F transposition) 1 (-1) Ps1 := by
  rw [matrixRep_transposition]
  unfold CanonicalProjector
  decide +kernel

theorem psminus_canonical :
    CanonicalProjector (matrixRep F transposition) (-1) 1 Psminus := by
  rw [matrixRep_transposition]
  unfold CanonicalProjector
  decide +kernel

theorem pt2_canonical :
    CanonicalProjector (matrixRep F cycle) 2 4 Pt2 := by
  rw [matrixRep_cycle]
  unfold CanonicalProjector
  decide +kernel

theorem pconj_canonical :
    CanonicalProjector (matrixRep F (cycle * transposition * cycle⁻¹)) 1 (-1) Pconj := by
  have hi : cycle⁻¹ = cycle * cycle := by decide +kernel
  rw [hi]
  simp only [map_mul]
  rw [matrixRep_cycle, matrixRep_transposition]
  unfold CanonicalProjector
  decide +kernel



/-- These four genuine eigenprojectors have a nondegenerate trace pairing
with the entire endomorphism algebra. -/
theorem trace_pairings_separate (W : Mat F)
    (h1 : Matrix.trace (Ps1 * W) = 0)
    (h2 : Matrix.trace (Psminus * W) = 0)
    (h3 : Matrix.trace (Pt2 * W) = 0)
    (h4 : Matrix.trace (Pconj * W) = 0) : W = 0 := by
  simp [Matrix.trace, Matrix.vecMul, dotProduct, Fin.sum_univ_succ,
    Ps1, Psminus, Pt2, Pconj] at h1 h2 h3 h4
  ext i j
  fin_cases i <;> fin_cases j <;> change _ = (0 : F)
  · linear_combination (norm := ring_nf) 3 * h1 + 6 * h2 + 3 * h3 + 3 * h4
    simp only [show (42 : F) = 0 from rfl, show (21 : F) = 0 from rfl,
      show (15 : F) = 1 from rfl, mul_zero, mul_one, sub_zero]
    exact sub_self _
  · linear_combination (norm := ring_nf) h1 + 2 * h2 + h3 + 3 * h4
    simp only [show (14 : F) = 0 from rfl, show (7 : F) = 0 from rfl,
      show (15 : F) = 1 from rfl, mul_zero, mul_one, sub_zero]
    exact sub_self _
  · linear_combination (norm := ring_nf) 6 * h1 + 3 * h2 + 6 * h3 + 6 * h4
    simp only [show (57 : F) = 1 from rfl, show (42 : F) = 0 from rfl,
      show (21 : F) = 0 from rfl, mul_zero, mul_one, sub_zero]
    exact sub_self _
  · linear_combination (norm := ring_nf) 5 * h1 + 2 * h2 + 4 * h3 + 4 * h4
    simp only [show (42 : F) = 0 from rfl, show (29 : F) = 1 from rfl,
      show (14 : F) = 0 from rfl, show (28 : F) = 0 from rfl,
      mul_zero, mul_one, sub_zero]
    exact sub_self _

/-- Every nonzero endomorphism is detected by an actual canonical
projector for an element of the represented group. -/
theorem detects_every_nonzero (W : Mat F) (hW : W ≠ 0) :
    ∃ (g : Group) (α β : F) (P : Mat F),
      CanonicalProjector (matrixRep F g) α β P ∧ Matrix.trace (P * W) ≠ 0 := by
  by_cases h1 : Matrix.trace (Ps1 * W) = 0
  · by_cases h2 : Matrix.trace (Psminus * W) = 0
    · by_cases h3 : Matrix.trace (Pt2 * W) = 0
      · refine ⟨cycle * transposition * cycle⁻¹, 1, -1, Pconj, pconj_canonical, ?_⟩
        intro h4
        exact hW (trace_pairings_separate W h1 h2 h3 h4)
      · exact ⟨cycle, 2, 4, Pt2, pt2_canonical, h3⟩
    · exact ⟨transposition, -1, 1, Psminus, psminus_canonical, h2⟩
  · exact ⟨transposition, 1, -1, Ps1, ps1_canonical, h1⟩

/-- The two displayed witnesses from the manuscript have their claimed traces. -/
theorem trace_sign_witness : Matrix.trace (Pt2 * !![2, 3; 4, 5]) = (3 : F) := by
  decide +kernel

theorem trace_standard_witness : Matrix.trace (Ps1 * !![6, 4; 3, 1]) = (6 : F) := by
  decide +kernel

/-- The group matrices linearly span the complete endomorphism algebra.
The sole characteristic restriction for this identity is `3 ≠ 0`. -/
theorem matrix_expansion (h3 : (3 : k) ≠ 0) (W : Mat k) :
    W = ((W 0 0 - W 0 1 + W 1 0 + 2 * W 1 1) / 3) • matrixRep k 1 +
      ((-W 0 0 + W 0 1 + 2 * W 1 0 + W 1 1) / 3) • matrixRep k transposition +
      ((-W 0 0 - 2 * W 0 1 + 2 * W 1 0 + W 1 1) / 3) • matrixRep k cycle +
      ((W 0 0 + 2 * W 0 1 + W 1 0 - W 1 1) / 3) •
        matrixRep k (transposition * cycle) := by
  simp only [map_one, map_mul, matrixRep_transposition, matrixRep_cycle]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp <;>
    field_simp <;> ring

theorem all_matrices_preserve (h3 : (3 : k) ≠ 0)
    (N : Subrepresentation (rep k)) {v : Space k} (hv : v ∈ N) (W : Mat k) :
    W *ᵥ v ∈ N := by
  rw [matrix_expansion h3 W]
  simp only [Matrix.add_mulVec, Matrix.smul_mulVec, matrixRep_mulVec]
  exact N.toSubmodule.add_mem
    (N.toSubmodule.add_mem
      (N.toSubmodule.add_mem (N.toSubmodule.smul_mem _ (N.apply_mem_toSubmodule 1 hv))
        (N.toSubmodule.smul_mem _ (N.apply_mem_toSubmodule transposition hv)))
      (N.toSubmodule.smul_mem _ (N.apply_mem_toSubmodule cycle hv)))
    (N.toSubmodule.smul_mem _ (N.apply_mem_toSubmodule (transposition * cycle) hv))

/-- Irreducibility over every field whose characteristic is not three. -/
theorem irreducible_of_three_ne_zero (h3 : (3 : k) ≠ 0) :
    Representation.IsIrreducible (rep k) := by
  have : Nontrivial (Subrepresentation (rep k)) :=
    ⟨⟨⊥, ⊤, fun h => by
      have hh : (fun _ : Fin 2 => (1 : k)) ∈ (⊥ : Subrepresentation (rep k)) := by
        rw [h]
        trivial
      have hz : (fun _ : Fin 2 => (1 : k)) = 0 := hh
      have hh' := congrFun hz 0
      exact one_ne_zero hh'⟩⟩
  apply IsSimpleOrder.of_forall_eq_top
  intro N hN
  have hN' : N.toSubmodule ≠ ⊥ := fun h =>
    hN (Subrepresentation.toSubmodule_injective h)
  obtain ⟨v, hv, hv0⟩ := Submodule.exists_mem_ne_zero_of_ne_bot hN'
  obtain ⟨j, hj⟩ : ∃ j, v j ≠ 0 := by
    by_contra! hn
    exact hv0 (funext hn)
  apply Subrepresentation.toSubmodule_injective
  apply top_unique
  intro w _
  let W : Mat k := fun i l => if l = j then w i / v j else 0
  have heq : W *ᵥ v = w := by
    ext i
    simp [W, Matrix.mulVec, dotProduct, hj]
  rw [← heq]
  exact all_matrices_preserve h3 N hv W

/-- In particular the same representation is irreducible over every
characteristic-seven extension field, including an algebraic closure. -/
theorem irreducible_char_seven [CharP k 7] :
    Representation.IsIrreducible (rep k) := by
  apply irreducible_of_three_ne_zero
  exact fun h => (by decide : ¬7 ∣ 3) ((CharP.cast_eq_zero_iff k 7 3).mp h)

end PaperXII.S3Detection
