import PaperXII.ReuseCompactness
import Mathlib.Data.Fintype.EquivFin

/-! Paper XII 10.3–10.4 and the branch portion of 10.5.
The two finite-set compactness primitives are reused from Paper X unchanged.
Index 0 is the first residual level. No transition surjectivity is assumed. -/
namespace PaperXII.CompanionForests

open PaperX.Compactness

/-- Ordinary finiteness supplies the exhaustive lists required by the reused proof. -/
theorem finiteLevels (T : Tower) [∀ n, Finite (T.Level n)] : FiniteLevels T := by
  classical
  intro n
  let _ := Fintype.ofFinite (T.Level n)
  exact ⟨Finset.univ.toList, fun x ↦ by simp⟩

/-- Claim 10.3 without the unnecessary fixed-root restriction. -/
theorem branch_exists (T : Tower) [∀ n, Finite (T.Level n)]
    (hne : ∀ n, Nonempty (T.Level n)) : Nonempty (Branch T) :=
  finite_branch_compactness T (finiteLevels T) hne

/-- A branch is determined by its values. -/
theorem branch_ext {T : Tower} (b c : Branch T)
    (h : ∀ n, b.value n = c.value n) : b = c := by
  cases b with
  | mk bv bh =>
    cases c with
    | mk cv ch =>
      have hv : bv = cv := funext h
      cases hv
      rfl

/-- Composite reduction from level n to the first residual level. -/
def reduceToFirst (T : Tower) : (n : ℕ) → T.Level n → T.Level 0
  | 0 => id
  | n + 1 => fun x ↦ reduceToFirst T n (T.parent n x)

/-- Every coordinate of a branch reduces to its first value. -/
theorem branch_reduces_to_first (T : Tower) (b : Branch T) (n : ℕ) :
    reduceToFirst T n (b.value n) = b.value 0 := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change reduceToFirst T n (T.parent n (b.value (n + 1))) = _
    rw [b.compatible n, ih]

/-- Claim 10.3 with the source's fixed residual root retained explicitly. -/
theorem rooted_branch_exists (T : Tower) [∀ n, Finite (T.Level n)]
    (hne : ∀ n, Nonempty (T.Level n)) (root : T.Level 0)
    (hroot : ∀ n (x : T.Level n), reduceToFirst T n x = root) :
    ∃ b : Branch T, b.value 0 = root ∧
      ∀ n, reduceToFirst T n (b.value n) = root := by
  obtain ⟨b⟩ := branch_exists T hne
  exact ⟨b, hroot 0 (b.value 0), fun n ↦ hroot n (b.value n)⟩

/-- The complete finite-level criterion, in both directions. -/
theorem branch_iff_nonempty_levels (T : Tower) [∀ n, Finite (T.Level n)] :
    Nonempty (Branch T) ↔ ∀ n, Nonempty (T.Level n) :=
  branch_iff_levels_nonempty T (finiteLevels T)

/-- A missing finite level rules out every branch, even without finiteness. -/
theorem empty_level_no_branch (T : Tower) (n : ℕ) (h : ¬ Nonempty (T.Level n)) :
    ¬ Nonempty (Branch T) := empty_level_obstruction T n h

/-- Claim 10.4 applies to any complete realization carrying its actual finite reductions. -/
theorem empty_level_no_realization (T : Tower) {R : Type*}
    (reduce : ∀ n, R → T.Level n) (n : ℕ) (h : ¬ Nonempty (T.Level n)) :
    ¬ Nonempty R := by
  rintro ⟨r⟩
  exact h ⟨reduce n r⟩

/-- For finite towers, failure of completion has a finite-level witness. -/
theorem no_branch_has_empty_level (T : Tower) [∀ n, Finite (T.Level n)]
    (h : ¬ Nonempty (Branch T)) : ∃ n, ¬ Nonempty (T.Level n) := by
  exact Classical.not_forall.mp (fun hne ↦ h ((branch_iff_nonempty_levels T).mpr hne))

/-- The branch-selection portion of 10.5, with no effectivity conclusion hidden in it. -/
theorem simultaneous_branches {I : Type} (T : I → Tower)
    [∀ i n, Finite ((T i).Level n)]
    (hne : ∀ i n, Nonempty ((T i).Level n)) : Nonempty (∀ i, Branch (T i)) :=
  indexed_finite_completion T (fun i ↦ finiteLevels (T i)) hne

end PaperXII.CompanionForests
