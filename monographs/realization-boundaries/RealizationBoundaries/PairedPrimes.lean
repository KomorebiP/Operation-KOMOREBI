import RealizationBoundaries.Cocycle
import Mathlib.Data.Nat.Prime.Nth

/-! # The actual paired-prime selector groups and their marked root tests -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

def primeAt (n : ℕ) : Prime :=
  ⟨Nat.nth Nat.Prime n, Nat.nth_mem_of_infinite Nat.infinite_setOfPred_prime n⟩

theorem primeAt_injective : Function.Injective primeAt := by
  intro i j h
  exact Nat.nth_injective Nat.infinite_setOfPred_prime (congrArg Subtype.val h)

def chosenIndex (a : ℕ → Bool) (n : ℕ) : ℕ := 2*n + if a n then 1 else 0

def omittedIndex (a : ℕ → Bool) (n : ℕ) : ℕ := 2*n + if a n then 0 else 1

theorem chosenIndex_bounds (a : ℕ → Bool) (n : ℕ) :
    2*n ≤ chosenIndex a n ∧ chosenIndex a n < 2*n+2 := by
  simp only [chosenIndex]
  split <;> omega

theorem omittedIndex_bounds (a : ℕ → Bool) (n : ℕ) :
    2*n ≤ omittedIndex a n ∧ omittedIndex a n < 2*n+2 := by
  simp only [omittedIndex]
  split <;> omega

theorem chosenIndex_injective (a : ℕ → Bool) : Function.Injective (chosenIndex a) := by
  intro i j h
  have hi := chosenIndex_bounds a i
  have hj := chosenIndex_bounds a j
  omega

def pairedSelector (a : ℕ → Bool) : Set Prime := Set.range (fun n => primeAt (chosenIndex a n))

theorem pairedSelector_infinite (a : ℕ → Bool) : (pairedSelector a).Infinite :=
  Set.infinite_range_of_injective (primeAt_injective.comp (chosenIndex_injective a))

theorem chosen_mem (a : ℕ → Bool) (n : ℕ) :
    primeAt (chosenIndex a n) ∈ pairedSelector a := ⟨n, rfl⟩

theorem omitted_not_mem (a : ℕ → Bool) (n : ℕ) :
    primeAt (omittedIndex a n) ∉ pairedSelector a := by
  rintro ⟨j, hj⟩
  have h := primeAt_injective hj
  have h1 := chosenIndex_bounds a j
  have h2 := omittedIndex_bounds a n
  have hjn : j = n := by omega
  subst j
  cases ha : a n <;> simp [chosenIndex, omittedIndex, ha] at h

/-- The group is the preimage of its actual rational line in P/D. -/
def pairedGroup (a : ℕ → Bool) : AddSubgroup Ambient := selectorGroup (pairedSelector a)

def markedElement (S : Set Prime) : selectorGroup S :=
  ⟨indicator S, by simpa using rationalSection_mem S 1⟩

/-- Exact marked divisibility holds at every prime, not just outside finitely many exceptions. -/
theorem marked_prime_root_iff (S : Set Prime) (p : Prime) :
    (∃ y : selectorGroup S, p.val • y = markedElement S) ↔ p ∉ S := by
  classical
  refine (preimage_root_iff (selectorLine S) p.property.pos (markedElement S)).trans ?_
  constructor
  · intro h hs
    have h0 := h p (dvd_refl _)
    change indicator S p = 0 at h0
    simp [hs] at h0
  · intro hp q hq
    have hqp : q = p := Subtype.ext ((p.property.dvd_iff_eq q.property.ne_one).mp hq).symm
    subst q
    exact indicator_apply_not_mem hp

theorem chosen_prime_obstructs (a : ℕ → Bool) (n : ℕ) :
    ¬ ∃ y : pairedGroup a,
      (primeAt (chosenIndex a n)).val • y = markedElement (pairedSelector a) := by
  intro h
  exact ((marked_prime_root_iff _ _).mp h) (chosen_mem a n)

theorem omitted_prime_has_root (a : ℕ → Bool) (n : ℕ) :
    ∃ y : pairedGroup a,
      (primeAt (omittedIndex a n)).val • y = markedElement (pairedSelector a) :=
  (marked_prime_root_iff _ _).mpr (omitted_not_mem a n)

/-- The formal normal-form bijection applies to every binary selector, without an extra
infinite-support assumption on the caller. -/
def pairedNormalFormEquiv (a : ℕ → Bool) :
    (ℚ × finiteSupport) ≃ pairedGroup a := normalFormEquiv (pairedSelector_infinite a)

end RealizationBoundaries
