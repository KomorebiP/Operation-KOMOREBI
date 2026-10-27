import PadicFiniteBranch
import PersistentFinitePrefix

/-! Exact p-adic root existence above any fixed finite prefix, including resonance.
No chosen sequence of roots and no nonresonance assumption are needed. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
open ResonantBranch
variable (p : ℕ) [Fact (Nat.Prime p)]
variable (n : Type) [Fintype n] [DecidableEq n]

def matrixUnitTower : FiniteTower (MatrixUnits p n) where
  project h a := project p n h a
  project_refl a := project_refl p n _ a
  project_trans hij hjk a := project_trans p n hij hjk a

def RootNode (d : ℕ) (U : (Matrix n n ℤ_[p])ˣ) (r : ℕ)
    (F : MatrixUnits p n r) : Prop := F^d = padicUnitReduction p n r U

theorem rootNode_downward (d : ℕ) (U : (Matrix n n ℤ_[p])ˣ) :
    DownwardClosed (matrixUnitTower p n) (RootNode p n d U) := by
  intro i j h F hF
  change (project p n h F)^d = padicUnitReduction p n i U
  rw [← map_pow, hF, project_padicReduction]

/-- An actual p-adic root above a fixed prefix exists iff that prefix has roots
above it at every deeper finite coefficient level. -/
theorem padic_root_iff_all_deeper_roots (d k : ℕ) (U : (Matrix n n ℤ_[p])ˣ)
    (a : MatrixUnits p n k) :
    (∃ F : (Matrix n n ℤ_[p])ˣ, padicUnitReduction p n k F = a ∧ F^d = U) ↔
    ∀ r, ∀ h : k ≤ r, ∃ b : MatrixUnits p n r,
      b^d = padicUnitReduction p n r U ∧ project p n h b = a := by
  constructor
  · rintro ⟨F, hFa, hFU⟩ r h
    refine ⟨padicUnitReduction p n r F, ?_, ?_⟩
    · rw [← map_pow, hFU]
    · rw [project_padicReduction, hFa]
  · intro ha
    obtain ⟨f, hf, hc, hk⟩ := (persistent_iff_branch (matrixUnitTower p n)
      (RootNode p n d U) (rootNode_downward p n d U) k a).mp ha
    have hfc : Compatible p n f := by
      intro r
      exact (project_succ p n r _).symm.trans (hc (Nat.le_succ r))
    refine ⟨unitLimit p n f hfc, (unitLimit_spec p n f hfc k).trans hk, ?_⟩
    apply padicUnit_ext p n
    intro r
    rw [map_pow, unitLimit_spec]
    exact hf r

/-- Any failure above a chosen prefix has a finite, deeper no-extension certificate. -/
theorem no_padic_root_iff_finite_prefix_obstruction (d k : ℕ)
    (U : (Matrix n n ℤ_[p])ˣ) (a : MatrixUnits p n k) :
    (¬ ∃ F : (Matrix n n ℤ_[p])ˣ, padicUnitReduction p n k F = a ∧ F^d = U) ↔
    ∃ r, ∃ h : k ≤ r, ∀ b : MatrixUnits p n r,
      b^d = padicUnitReduction p n r U → project p n h b ≠ a := by
  rw [padic_root_iff_all_deeper_roots p n d k U a]
  simp only [not_forall, not_exists, not_and]

/-- At fixed prefix depth, a finite horizon distinguishes exactly the prefixes
of genuine p-adic roots. No computable bound for the horizon is supplied. -/
theorem padic_root_finite_survivor_horizon (d k : ℕ) (U : (Matrix n n ℤ_[p])ˣ) :
    ∃ m, ∃ hkm : k ≤ m, ∀ a : MatrixUnits p n k,
      (∃ F : (Matrix n n ℤ_[p])ˣ, padicUnitReduction p n k F = a ∧ F^d = U) ↔
      ∃ b : MatrixUnits p n m, b^d = padicUnitReduction p n m U ∧ project p n hkm b = a := by
  obtain ⟨m, hkm, hm⟩ := finite_survivor_horizon (matrixUnitTower p n)
    (RootNode p n d U) (rootNode_downward p n d U) k
  refine ⟨m, hkm, fun a => ?_⟩
  rw [padic_root_iff_all_deeper_roots p n d k U a]
  exact hm a

/-- Every prefix of a genuine root has a child that is itself a prefix of a genuine root. -/
theorem surviving_root_has_surviving_child (d k : ℕ) (U : (Matrix n n ℤ_[p])ˣ)
    (a : MatrixUnits p n k)
    (ha : ∃ F : (Matrix n n ℤ_[p])ˣ, padicUnitReduction p n k F = a ∧ F^d = U) :
    ∃ b : MatrixUnits p n (k+1), down p n k b = a ∧
      ∃ F : (Matrix n n ℤ_[p])ˣ, padicUnitReduction p n (k+1) F = b ∧ F^d = U := by
  obtain ⟨F, hFa, hFU⟩ := ha
  refine ⟨padicUnitReduction p n (k+1) F, ?_, F, rfl, hFU⟩
  exact (padicUnitReduction_compatible p n F k).trans hFa

/-- An unbounded collection of successful deeper levels is enough. -/
theorem padic_root_iff_arbitrarily_deep_roots (d k : ℕ)
    (U : (Matrix n n ℤ_[p])ˣ) (a : MatrixUnits p n k) :
    (∃ F : (Matrix n n ℤ_[p])ˣ, padicUnitReduction p n k F = a ∧ F^d = U) ↔
    ∀ N, ∃ r, N ≤ r ∧ ∃ h : k ≤ r, ∃ b : MatrixUnits p n r,
      b^d = padicUnitReduction p n r U ∧ project p n h b = a := by
  rw [padic_root_iff_all_deeper_roots p n d k U a]
  constructor
  · intro h N
    exact ⟨max N k, le_max_left _ _, le_max_right _ _, h _ (le_max_right _ _)⟩
  · intro h s hks
    obtain ⟨r, hsr, hkr, b, hb, hba⟩ := h s
    refine ⟨project p n hsr b, ?_, ?_⟩
    · rw [← map_pow, hb, project_padicReduction]
    · rw [project_trans]
      exact hba

/-- A dead prefix has a first dead level, while every preceding visible level has a root. -/
theorem first_obstructed_level (d k : ℕ) (U : (Matrix n n ℤ_[p])ˣ)
    (a : MatrixUnits p n k)
    (hno : ¬ ∃ F : (Matrix n n ℤ_[p])ˣ, padicUnitReduction p n k F = a ∧ F^d = U) :
    ∃ r, ∃ hkr : k ≤ r,
      (∀ b : MatrixUnits p n r,
        b^d = padicUnitReduction p n r U → project p n hkr b ≠ a) ∧
      ∀ s, ∀ hks : k ≤ s, s < r → ∃ b : MatrixUnits p n s,
        b^d = padicUnitReduction p n s U ∧ project p n hks b = a := by
  classical
  have hex := (no_padic_root_iff_finite_prefix_obstruction p n d k U a).mp hno
  obtain ⟨hk, hbad⟩ := Nat.find_spec hex
  refine ⟨Nat.find hex, hk, hbad, ?_⟩
  intro s hks hlt
  by_contra hs
  have hnone : ∀ b : MatrixUnits p n s,
      b^d = padicUnitReduction p n s U → project p n hks b ≠ a := by
    simpa only [not_exists, not_and] using hs
  exact (Nat.find_min hex hlt) ⟨hks, hnone⟩

end Komorebi.StrongArtin.FrobeniusTower
