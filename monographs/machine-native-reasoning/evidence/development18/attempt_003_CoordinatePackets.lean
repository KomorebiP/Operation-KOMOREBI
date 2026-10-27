import MachineTheory.PositivePackets
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic.Linarith

/-!
# Complete positive idempotents on the coordinate cone

Core 2.5, coordinate sector. Positivity and completeness force diagonal form.
Idempotence then forces a partition of the coordinates. Orthogonality and
unique ownership of each coordinate are conclusions, not hypotheses.
-/
namespace Komorebi.MachineTheory.PositivePackets.Coordinate

noncomputable section

open scoped BigOperators

universe uN uI
variable {N : Type uN} {I : Type uI}

/-- The actual nonnegative coordinate cone. -/
def cone (N : Type uN) : ConvexCone ℝ (N → ℝ) where
  carrier := {v | ∀ j, 0 ≤ v j}
  smul_mem' := by
    intro c hc v hv j
    exact mul_nonneg (le_of_lt hc) (hv j)
  add_mem' := by
    intro v hv w hw j
    exact add_nonneg (hv j) (hw j)

@[simp] theorem mem_cone (v : N → ℝ) : v ∈ cone N ↔ ∀ j, 0 ≤ v j := Iff.rfl

/-- Coefficients of the given linear map, obtained on standard basis vectors. -/
def coefficient (P : (N → ℝ) →ₗ[ℝ] (N → ℝ)) (r c : N) : ℝ := by
  classical
  exact P (Pi.single c 1) r

variable [Fintype N]

/-- The coordinate basis expands every input vector exactly. -/
theorem basis_expansion (v : N → ℝ) :
    (∑ j, v j • Pi.single j (1 : ℝ)) = v := by
  classical
  ext r
  simp [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.single_apply]

/-- The coefficients represent the actual linear operation on every vector. -/
theorem coordinate_action (P : (N → ℝ) →ₗ[ℝ] (N → ℝ)) (v : N → ℝ) (r : N) :
    P v r = ∑ c, coefficient P r c * v c := by
  classical
  calc
    P v r = P (∑ c, v c • Pi.single c (1 : ℝ)) r := by rw [basis_expansion]
    _ = ∑ c, coefficient P r c * v c := by
      simp [coefficient, map_sum, map_smul, Finset.sum_apply, mul_comm]

/-- Cone preservation is equivalent to nonnegative entries of the actual matrix. -/
theorem preserves_iff_coefficients (P : (N → ℝ) →ₗ[ℝ] (N → ℝ)) :
    Preserves (cone N) P ↔ ∀ r c, 0 ≤ coefficient P r c := by
  classical
  constructor
  · intro hp r c
    apply hp (Pi.single c 1)
    intro j
    simp [Pi.single_apply]
  · intro hc v hv r
    rw [coordinate_action]
    exact Finset.sum_nonneg (fun c _ => mul_nonneg (hc r c) (hv c))

variable [Fintype I]

/-- Completeness sums every matrix entry to the corresponding identity entry. -/
theorem complete_coefficient_sum (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ))
    (hc : Complete P) (r c : N) :
    (∑ i, coefficient (P i) r c) = if r = c then 1 else 0 := by
  classical
  have h := congrArg (fun F : (N → ℝ) →ₗ[ℝ] (N → ℝ) => F (Pi.single c 1) r) hc
  simpa [coefficient, LinearMap.sum_apply, Finset.sum_apply, Pi.single_apply, eq_comm] using h

/-- Positivity prevents off-diagonal cancellation in a complete family. -/
theorem off_diagonal_zero (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ))
    (hp : ∀ i, Preserves (cone N) (P i)) (hc : Complete P)
    (i : I) {r c : N} (hrc : r ≠ c) : coefficient (P i) r c = 0 := by
  classical
  have hnon : ∀ k, 0 ≤ coefficient (P k) r c :=
    fun k => (preserves_iff_coefficients (P k)).mp (hp k) r c
  have hle := Finset.single_le_sum (fun k (_ : k ∈ (Finset.univ : Finset I)) => hnon k)
    (Finset.mem_univ i)
  rw [complete_coefficient_sum P hc r c, if_neg hrc] at hle
  exact le_antisymm hle (hnon i)

/-- Complete positive maps act diagonally even before idempotence is assumed. -/
theorem diagonal_action (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ))
    (hp : ∀ i, Preserves (cone N) (P i)) (hc : Complete P)
    (i : I) (v : N → ℝ) (r : N) :
    P i v r = coefficient (P i) r r * v r := by
  classical
  rw [coordinate_action]
  apply Finset.sum_eq_single r
  · intro c _ hcr
    rw [off_diagonal_zero P hp hc i hcr.symm, zero_mul]
  · simp

/-- Idempotence makes each diagonal entry multiplicatively idempotent. -/
theorem diagonal_idempotent (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ))
    (hp : ∀ i, Preserves (cone N) (P i)) (hc : Complete P)
    (hi : ∀ i, (P i).comp (P i) = P i) (i : I) (r : N) :
    coefficient (P i) r r * coefficient (P i) r r = coefficient (P i) r r := by
  classical
  have h := congrArg (fun F : (N → ℝ) →ₗ[ℝ] (N → ℝ) => F (Pi.single r 1) r) (hi i)
  change P i (P i (Pi.single r 1)) r = P i (Pi.single r 1) r at h
  rw [diagonal_action P hp hc] at h
  exact h

/-- Every diagonal entry of a complete positive idempotent is zero or one. -/
theorem diagonal_zero_or_one (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ))
    (hp : ∀ i, Preserves (cone N) (P i)) (hc : Complete P)
    (hi : ∀ i, (P i).comp (P i) = P i) (i : I) (r : N) :
    coefficient (P i) r r = 0 ∨ coefficient (P i) r r = 1 := by
  have h := diagonal_idempotent P hp hc hi i r
  have hz : coefficient (P i) r r * (coefficient (P i) r r - 1) = 0 := by nlinarith
  rcases mul_eq_zero.mp hz with h0 | h1
  · exact Or.inl h0
  · exact Or.inr (sub_eq_zero.mp h1)

/-- Every coordinate is selected by exactly one operator. -/
theorem unique_owner (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ))
    (hp : ∀ i, Preserves (cone N) (P i)) (hc : Complete P)
    (hi : ∀ i, (P i).comp (P i) = P i) (r : N) :
    ∃! i, coefficient (P i) r r = 1 := by
  classical
  have hsum : (∑ i, coefficient (P i) r r) = 1 := by
    simpa using complete_coefficient_sum P hc r r
  have hnon : ∀ i, 0 ≤ coefficient (P i) r r :=
    fun i => (preserves_iff_coefficients (P i)).mp (hp i) r r
  have hex : ∃ i, coefficient (P i) r r = 1 := by
    by_contra hn
    have hall : ∀ i, coefficient (P i) r r = 0 := by
      intro i
      exact (diagonal_zero_or_one P hp hc hi i r).resolve_right (fun h => hn ⟨i, h⟩)
    simp [hall] at hsum
  obtain ⟨i, hival⟩ := hex
  refine ⟨i, hival, ?_⟩
  intro k hk
  by_contra hki
  have hsplit := Finset.sum_erase_add Finset.univ
    (fun j => coefficient (P j) r r) (Finset.mem_univ i)
  have hzero : (∑ j ∈ Finset.univ.erase i, coefficient (P j) r r) = 0 := by
    rw [hsum, hival] at hsplit
    linarith
  have hle := Finset.single_le_sum (fun j (_ : j ∈ Finset.univ.erase i) => hnon j)
    (Finset.mem_erase.mpr ⟨hki, Finset.mem_univ k⟩)
  rw [hzero, hk] at hle
  exact (not_le_of_gt zero_lt_one) hle

/-- A partition of coordinates determines its actual linear selector maps. -/
def selector (owner : N → I) (i : I) : (N → ℝ) →ₗ[ℝ] (N → ℝ) := by
  classical
  exact {
    toFun := fun v r => if owner r = i then v r else 0
    map_add' := by intro v w; ext r; split_ifs <;> simp
    map_smul' := by intro c v; ext r; split_ifs <;> simp }

@[simp] theorem selector_apply (owner : N → I) (i : I) (v : N → ℝ) (r : N) :
    selector owner i v r = if owner r = i then v r else 0 := by classical; rfl

/-- Every selector preserves the coordinate cone. -/
theorem selector_preserves (owner : N → I) (i : I) :
    Preserves (cone N) (selector owner i) := by
  classical
  intro v hv r
  simp only [selector_apply]
  split_ifs
  · exact hv r
  · exact le_rfl

/-- A selector family is complete, including the zero-dimensional case. -/
theorem selector_complete (owner : N → I) : Complete (selector owner) := by
  classical
  ext v r
  simp [LinearMap.sum_apply, Finset.sum_apply, selector_apply]

/-- Every selector is idempotent. -/
theorem selector_idempotent (owner : N → I) (i : I) :
    (selector owner i).comp (selector owner i) = selector owner i := by
  classical
  ext v r
  simp only [LinearMap.comp_apply, selector_apply]
  split_ifs <;> rfl

/-- Distinct selectors have zero composition. -/
theorem selector_disjoint (owner : N → I) {i k : I} (hik : i ≠ k) :
    (selector owner i).comp (selector owner k) = 0 := by
  classical
  ext v r
  simp only [LinearMap.comp_apply, selector_apply, LinearMap.zero_apply, Pi.zero_apply]
  split_ifs with hri hrk
  · exact False.elim (hik (hri.symm.trans hrk))
  · rfl
  · rfl

/-- Construction of the unique coordinate assignment from the original maps. -/
theorem exists_selectors (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ))
    (hp : ∀ i, Preserves (cone N) (P i)) (hc : Complete P)
    (hi : ∀ i, (P i).comp (P i) = P i) :
    ∃ owner : N → I, ∀ i, P i = selector owner i := by
  classical
  choose owner howner hunique using unique_owner P hp hc hi
  refine ⟨owner, ?_⟩
  intro i
  ext v r
  rw [diagonal_action P hp hc, selector_apply]
  by_cases hri : owner r = i
  · rw [if_pos hri, ← hri, howner r, one_mul]
  · rw [if_neg hri]
    have hzero : coefficient (P i) r r = 0 :=
      (diagonal_zero_or_one P hp hc hi i r).resolve_right
        (fun h => hri (hunique r i h).symm)
    rw [hzero, zero_mul]

/-- The selector representation also implies all the original hypotheses. -/
theorem classification_iff (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ)) :
    ((∀ i, Preserves (cone N) (P i)) ∧ Complete P ∧ ∀ i, (P i).comp (P i) = P i) ↔
      ∃ owner : N → I, ∀ i, P i = selector owner i := by
  constructor
  · rintro ⟨hp, hc, hi⟩
    exact exists_selectors P hp hc hi
  · rintro ⟨owner, h⟩
    have heq : P = selector owner := funext h
    subst P
    exact ⟨selector_preserves owner, selector_complete owner, selector_idempotent owner⟩

/-- Source-facing classification, with disjointness derived rather than assumed. -/
theorem source_core25_coordinate (P : I → (N → ℝ) →ₗ[ℝ] (N → ℝ))
    (hp : ∀ i, Preserves (cone N) (P i)) (hc : Complete P)
    (hi : ∀ i, (P i).comp (P i) = P i) :
    (∃ owner : N → I, ∀ i, P i = selector owner i) ∧
    (∀ r, ∃! i, coefficient (P i) r r = 1) ∧
    (∀ i k, i ≠ k → (P i).comp (P k) = 0) := by
  obtain ⟨owner, ho⟩ := exists_selectors P hp hc hi
  refine ⟨⟨owner, ho⟩, unique_owner P hp hc hi, ?_⟩
  intro i k hik
  rw [ho i, ho k]
  exact selector_disjoint owner hik

end
end Komorebi.MachineTheory.PositivePackets.Coordinate
