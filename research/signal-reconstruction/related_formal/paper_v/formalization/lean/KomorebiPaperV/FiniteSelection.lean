import Mathlib.Basic.Real.Basic
import Mathlib.Tactic

/-!
Author: Komorebi P.
Checked source. Finite objective selection with an explicit
singleton case. PruningSums connects these statements to arbitrary complete
covering antichains, including the attained positive gap.
-/

namespace KomorebiPaperV
section Selection
variable {A : Type*}

theorem finite_minimum (f : A → ℝ) :
    ∀ s : Finset A, s.Nonempty → ∃ m ∈ s, ∀ a ∈ s, f m ≤ f a := by
  classical
  intro s
  induction s using Finset.induction_on with
  | empty =>
    intro hs
    simp at hs
  | @insert a s ha ih =>
    intro _
    by_cases hs : s.Nonempty
    · obtain ⟨m, hm, hmin⟩ := ih hs
      by_cases h : f a ≤ f m
      · refine ⟨a, Finset.mem_insert_self _ _, ?_⟩
        intro b hb
        rcases Finset.mem_insert.mp hb with hba | hbs
        · subst b
          exact le_rfl
        · exact h.trans (hmin b hbs)
      · refine ⟨m, Finset.mem_insert_of_mem hm, ?_⟩
        intro b hb
        rcases Finset.mem_insert.mp hb with hba | hbs
        · subst b
          linarith
        · exact hmin b hbs
    · have hempty : s = ∅ := Finset.not_nonempty_iff_eq_empty.mp hs
      subst s
      refine ⟨a, by simp, ?_⟩
      intro b hb
      have hba : b = a := by simpa using hb
      subst b
      exact le_rfl

theorem positive_gap [DecidableEq A] (s : Finset A) (f : A → ℝ) (m : A)
    (hcompetitors : (s.erase m).Nonempty)
    (hstrict : ∀ a ∈ s, a ≠ m → f m < f a) :
    ∃ γ : ℝ, 0 < γ ∧ ∀ a ∈ s, a ≠ m → γ ≤ f a - f m := by
  obtain ⟨r, hr, hmin⟩ := finite_minimum (fun a => f a - f m) (s.erase m) hcompetitors
  have hr' := Finset.mem_erase.mp hr
  refine ⟨f r - f m, sub_pos.mpr (hstrict r hr'.2 hr'.1), ?_⟩
  intro a ha hne
  exact hmin a (Finset.mem_erase.mpr ⟨hne, ha⟩)

theorem gap_stability (s : Finset A) (f g : A → ℝ) (m : A)
    (hm : m ∈ s) (γ ε : ℝ)
    (hgap : ∀ a ∈ s, a ≠ m → γ ≤ f a - f m)
    (hpert : ∀ a ∈ s, |g a - f a| ≤ ε) (hmargin : 2 * ε < γ) :
    ∀ a ∈ s, a ≠ m → g m < g a := by
  intro a ha hne
  have hmerr := abs_le.mp (hpert m hm)
  have haerr := abs_le.mp (hpert a ha)
  have hsep := hgap a ha hne
  linarith

theorem singleton_minimum [DecidableEq A] (f : A → ℝ) (m : A) :
    ∀ a ∈ ({m} : Finset A), f m ≤ f a := by
  intro a ha
  have h : a = m := by simpa using ha
  subst a
  exact le_rfl

theorem singleton_selection_unchanged [DecidableEq A] (m a : A)
    (ha : a ∈ ({m} : Finset A)) : a = m := by
  simpa using ha
end Selection
end KomorebiPaperV
