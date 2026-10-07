import KomorebiPadic.FiniteCartierMachine
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Algebra.Order.BigOperators.Group.Finset

/-! # Finite least propagation profiles
A row capacity is a coefficient count. Capacity zero represents only the zero
polynomial; capacity one permits constants. No `natDegree 0 = 0` conflation.
The generic transfer system is monotone and bounded by U, and iteration from zero
stabilizes after L*U rounds. Leastness holds against all closed natural profiles,
not just those chosen below U.
-/
namespace KomorebiPadic

structure DegreePropagationSystem (L J U : ℕ) where
  target : Fin L → Fin J → Fin L
  seed : Fin L → ℕ
  seed_bound : ∀ i, seed i ≤ U
  transfer : Fin L → Fin J → ℕ → ℕ
  transfer_mono : ∀ i k, Monotone (transfer i k)
  transfer_bound : ∀ i k, transfer i k U ≤ U

variable {L J U : ℕ}

def degreeProfileStep (S : DegreePropagationSystem L J U) (w : Fin L → ℕ) : Fin L → ℕ :=
  fun j => max (w j) (max (S.seed j)
    (Finset.univ.sup fun ik : Fin L × Fin J =>
      if S.target ik.1 ik.2 = j then S.transfer ik.1 ik.2 (w ik.1) else 0))

def DegreeProfileClosed (S : DegreePropagationSystem L J U) (w : Fin L → ℕ) : Prop :=
  (∀ i, S.seed i ≤ w i) ∧ ∀ i k, S.transfer i k (w i) ≤ w (S.target i k)

theorem degreeProfileStep_inflationary (S : DegreePropagationSystem L J U) (w : Fin L → ℕ) :
    w ≤ degreeProfileStep S w := fun _ => Nat.le_max_left _ _

theorem degreeProfileStep_mono (S : DegreePropagationSystem L J U) :
    Monotone (degreeProfileStep S) := by
  intro v w hv j
  apply max_le_max (hv j)
  apply max_le_max le_rfl
  apply Finset.sup_le
  intro ik hik
  apply Finset.le_sup_of_le hik
  split_ifs
  · exact S.transfer_mono _ _ (hv _)
  · exact le_rfl

theorem degreeProfileStep_bound (S : DegreePropagationSystem L J U) (w : Fin L → ℕ)
    (hw : ∀ i, w i ≤ U) : ∀ i, degreeProfileStep S w i ≤ U := by
  intro j
  apply max_le (hw j)
  apply max_le (S.seed_bound j)
  apply Finset.sup_le
  intro ik _
  split_ifs
  · exact (S.transfer_mono _ _ (hw _)).trans (S.transfer_bound _ _)
  · exact Nat.zero_le _

theorem degreeProfileStep_le_iff (S : DegreePropagationSystem L J U) (w : Fin L → ℕ) :
    degreeProfileStep S w ≤ w ↔ DegreeProfileClosed S w := by
  constructor
  · intro h
    constructor
    · intro i
      exact (Nat.le_max_left _ _).trans ((Nat.le_max_right _ _).trans (h i))
    · intro i k
      have he : S.transfer i k (w i) ≤
          Finset.univ.sup (fun ik : Fin L × Fin J =>
            if S.target ik.1 ik.2 = S.target i k then S.transfer ik.1 ik.2 (w ik.1) else 0) := by
        simpa using (Finset.le_sup (f := fun ik : Fin L × Fin J =>
          if S.target ik.1 ik.2 = S.target i k then S.transfer ik.1 ik.2 (w ik.1) else 0)
          (Finset.mem_univ (i,k)))
      exact he.trans ((Nat.le_max_right _ _).trans ((Nat.le_max_right _ _).trans (h _)))
  · rintro ⟨hs, ht⟩ j
    apply max_le le_rfl
    apply max_le (hs j)
    apply Finset.sup_le
    intro ik _
    split_ifs with hh
    · simpa only [← hh] using ht ik.1 ik.2
    · exact Nat.zero_le _

theorem degreeProfileStep_eq_iff (S : DegreePropagationSystem L J U) (w : Fin L → ℕ) :
    degreeProfileStep S w = w ↔ DegreeProfileClosed S w := by
  rw [← degreeProfileStep_le_iff]
  exact ⟨fun h => h.le, fun h => le_antisymm h (degreeProfileStep_inflationary S w)⟩

def degreeProfileIterate (S : DegreePropagationSystem L J U) : ℕ → (Fin L → ℕ)
  | 0 => fun _ => 0
  | n+1 => degreeProfileStep S (degreeProfileIterate S n)

theorem degreeProfileIterate_bound (S : DegreePropagationSystem L J U) (n : ℕ) :
    ∀ i, degreeProfileIterate S n i ≤ U := by
  induction n with
  | zero => exact fun _ => Nat.zero_le _
  | succ n ih => exact degreeProfileStep_bound S _ ih

theorem degreeProfileIterate_le_closed (S : DegreePropagationSystem L J U)
    (w : Fin L → ℕ) (hw : DegreeProfileClosed S w) (n : ℕ) :
    degreeProfileIterate S n ≤ w := by
  induction n with
  | zero => exact fun _ => Nat.zero_le _
  | succ n ih =>
    exact (degreeProfileStep_mono S ih).trans ((degreeProfileStep_le_iff S w).mpr hw)

def degreeProfileMass (w : Fin L → ℕ) : ℕ := ∑ i, w i

theorem degreeProfileMass_le (w : Fin L → ℕ) (hw : ∀ i, w i ≤ U) :
    degreeProfileMass w ≤ L*U := by
  calc
    degreeProfileMass w ≤ ∑ _ : Fin L, U := Finset.sum_le_sum fun i _ => hw i
    _ = L*U := by simp

theorem degreeProfileMass_strict {v w : Fin L → ℕ} (hle : v ≤ w) (hne : v ≠ w) :
    degreeProfileMass v < degreeProfileMass w := by
  classical
  have hx : ∃ i, v i < w i := by
    by_contra hn
    apply hne
    funext i
    have := not_exists.mp hn i
    exact le_antisymm (hle i) (Nat.le_of_not_gt this)
  obtain ⟨i, hi⟩ := hx
  exact Finset.sum_lt_sum (fun j _ => hle j) ⟨i, Finset.mem_univ _, hi⟩

theorem degreeProfileIterate_progress (S : DegreePropagationSystem L J U) (n : ℕ)
    (hn : degreeProfileIterate S (n+1) ≠ degreeProfileIterate S n) :
    n+1 ≤ degreeProfileMass (degreeProfileIterate S (n+1)) := by
  induction n with
  | zero =>
    have hs := degreeProfileMass_strict (degreeProfileStep_inflationary S (degreeProfileIterate S 0))
      (Ne.symm hn)
    have hz : degreeProfileMass (degreeProfileIterate S 0) = 0 := by simp [degreeProfileMass, degreeProfileIterate]
    change degreeProfileMass (degreeProfileIterate S 0) < degreeProfileMass (degreeProfileIterate S 1) at hs
    exact Nat.succ_le_of_lt (by simpa only [hz] using hs)
  | succ n ih =>
    have hprev : degreeProfileIterate S (n+1) ≠ degreeProfileIterate S n := by
      intro he
      apply hn
      exact congrArg (degreeProfileStep S) he
    have hl := ih hprev
    have hs := degreeProfileMass_strict (degreeProfileStep_inflationary S (degreeProfileIterate S (n+1)))
      (Ne.symm hn)
    change degreeProfileMass (degreeProfileIterate S (n+1)) <
      degreeProfileMass (degreeProfileIterate S (n+1+1)) at hs
    omega

/-- A bounded mass can strictly increase at most L*U times. -/
theorem degreeProfileIterate_stabilizes (S : DegreePropagationSystem L J U) :
    degreeProfileStep S (degreeProfileIterate S (L*U)) = degreeProfileIterate S (L*U) := by
  by_contra hn
  have hl := degreeProfileIterate_progress S (L*U) hn
  have hu := degreeProfileMass_le _ (degreeProfileIterate_bound S (L*U+1))
  omega

def leastDegreeProfile (S : DegreePropagationSystem L J U) : Fin L → ℕ :=
  degreeProfileIterate S (L*U)

theorem leastDegreeProfile_closed (S : DegreePropagationSystem L J U) :
    DegreeProfileClosed S (leastDegreeProfile S) :=
  (degreeProfileStep_eq_iff S _).mp (degreeProfileIterate_stabilizes S)

theorem leastDegreeProfile_le (S : DegreePropagationSystem L J U) (w : Fin L → ℕ)
    (hw : DegreeProfileClosed S w) : leastDegreeProfile S ≤ w :=
  degreeProfileIterate_le_closed S w hw _

theorem leastDegreeProfile_bound (S : DegreePropagationSystem L J U) :
    ∀ i, leastDegreeProfile S i ≤ U := degreeProfileIterate_bound S _

/-- The result is characterized uniquely by closure and leastness. -/
theorem leastDegreeProfile_unique (S : DegreePropagationSystem L J U) (w : Fin L → ℕ)
    (hc : DegreeProfileClosed S w)
    (hl : ∀ v, DegreeProfileClosed S v → w ≤ v) : w = leastDegreeProfile S :=
  le_antisymm (hl _ (leastDegreeProfile_closed S)) (leastDegreeProfile_le S w hc)

end KomorebiPadic
