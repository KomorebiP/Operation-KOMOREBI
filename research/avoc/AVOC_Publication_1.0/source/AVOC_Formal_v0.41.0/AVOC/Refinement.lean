import AVOC.Core
import Mathlib.Data.Finset.Card
import Mathlib.Data.Fintype.Prod
import Lean.Elab.Tactic.Omega

namespace Komorebi.AVOC

universe u v w

/-- The finite set of task-relevant collisions made by an encoding: pairs that
are merged by the encoding but distinguished by the target. -/
noncomputable def collisionPairs
    {X : Type u} [Fintype X]
    {Z : Type v} {Y : Type w}
    (φ : X → Z) (T : X → Y) : Finset (X × X) := by
  classical
  exact Finset.univ.filter (fun p => φ p.1 = φ p.2 ∧ T p.1 ≠ T p.2)

/-- Membership in `collisionPairs` is exactly the collision predicate. -/
theorem mem_collisionPairs_iff
    {X : Type u} [Fintype X]
    {Z : Type v} {Y : Type w}
    (φ : X → Z) (T : X → Y) (x y : X) :
    (x, y) ∈ collisionPairs φ T ↔ φ x = φ y ∧ T x ≠ T y := by
  classical
  simp [collisionPairs]

/-- An exact sufficient encoding has no task-relevant collisions. -/
theorem sufficient_collisionPairs_empty
    {X : Type u} [Fintype X]
    {Z : Type v} {Y : Type w}
    {φ : X → Z} {T : X → Y}
    (h : TaskSufficient φ T) : collisionPairs φ T = ∅ := by
  classical
  apply Finset.eq_empty_iff_forall_notMem.mpr
  rintro ⟨x, y⟩ hp
  rw [mem_collisionPairs_iff] at hp
  exact hp.2 (sufficient_preserves_target_distinctions h hp.1)

/-- On a finite input type, absence of task-relevant collisions is also
sufficient for exact recovery (assuming an inhabited target codomain). -/
theorem collisionPairs_empty_implies_sufficient
    {X : Type u} [Fintype X]
    {Z : Type v} {Y : Type w} [Nonempty Y]
    {φ : X → Z} {T : X → Y}
    (h : collisionPairs φ T = ∅) : TaskSufficient φ T := by
  apply fiber_refinement_implies_sufficient
  intro x y hxy
  by_contra hT
  have hmem : (x, y) ∈ collisionPairs φ T :=
    (mem_collisionPairs_iff φ T x y).2 ⟨hxy, hT⟩
  rw [h] at hmem
  simp at hmem

/-- Finite collision criterion: exact sufficiency is equivalent to an empty
collision set. -/
theorem sufficient_iff_collisionPairs_empty
    {X : Type u} [Fintype X]
    {Z : Type v} {Y : Type w} [Nonempty Y]
    {φ : X → Z} {T : X → Y} :
    TaskSufficient φ T ↔ collisionPairs φ T = ∅ := by
  exact ⟨sufficient_collisionPairs_empty, collisionPairs_empty_implies_sufficient⟩

/-- Refining a representation cannot create a new task-relevant collision. -/
theorem collisionPairs_subset_of_refines
    {X : Type u} [Fintype X]
    {A : Type v} {B : Type w} {Y : Type*}
    {fine : X → A} {coarse : X → B} {T : X → Y}
    (h : Refines fine coarse) :
    collisionPairs fine T ⊆ collisionPairs coarse T := by
  classical
  rcases h with ⟨decode, hdecode⟩
  intro p hp
  rcases p with ⟨x, y⟩
  rw [mem_collisionPairs_iff] at hp ⊢
  refine ⟨?_, hp.2⟩
  calc
    coarse x = decode (fine x) := (hdecode x).symm
    _ = decode (fine y) := congrArg decode hp.1
    _ = coarse y := hdecode y

/-- If a refinement separates one collision of the coarser representation,
then the finite collision set strictly shrinks. -/
theorem collisionPairs_ssubset_of_refines_and_separates
    {X : Type u} [Fintype X]
    {A : Type v} {B : Type w} {Y : Type*}
    {fine : X → A} {coarse : X → B} {T : X → Y}
    (href : Refines fine coarse)
    {x y : X}
    (hcoarse : coarse x = coarse y)
    (hT : T x ≠ T y)
    (hfine : fine x ≠ fine y) :
    collisionPairs fine T ⊂ collisionPairs coarse T := by
  classical
  refine Finset.ssubset_iff_subset_ne.mpr ⟨collisionPairs_subset_of_refines href, ?_⟩
  intro heq
  have hmemCoarse : (x, y) ∈ collisionPairs coarse T :=
    (mem_collisionPairs_iff coarse T x y).2 ⟨hcoarse, hT⟩
  have hmemFine : (x, y) ∈ collisionPairs fine T := by
    rw [heq]
    exact hmemCoarse
  exact hfine ((mem_collisionPairs_iff fine T x y).1 hmemFine).1

/-- Strictly separating a live collision strictly decreases collision count. -/
theorem collisionCard_strictly_decreases
    {X : Type u} [Fintype X]
    {A : Type v} {B : Type w} {Y : Type*}
    {fine : X → A} {coarse : X → B} {T : X → Y}
    (href : Refines fine coarse)
    {x y : X}
    (hcoarse : coarse x = coarse y)
    (hT : T x ≠ T y)
    (hfine : fine x ≠ fine y) :
    (collisionPairs fine T).card < (collisionPairs coarse T).card := by
  exact Finset.card_lt_card
    (collisionPairs_ssubset_of_refines_and_separates href hcoarse hT hfine)

/-- A natural-number measure cannot strictly decrease for more steps than its
initial value. This is the termination engine for finite refinement. -/
theorem strict_nat_descent_length_bound
    (m : ℕ) (measure : ℕ → ℕ)
    (hstep : ∀ i < m, measure (i + 1) < measure i) :
    m ≤ measure 0 := by
  induction m generalizing measure with
  | zero => omega
  | succ m ih =>
      have h0 : measure 1 < measure 0 := by
        simpa using hstep 0 (Nat.zero_lt_succ m)
      let tail : ℕ → ℕ := fun i => measure (i + 1)
      have htail : ∀ i < m, tail (i + 1) < tail i := by
        intro i hi
        dsimp [tail]
        have hs := hstep (i + 1) (Nat.succ_lt_succ hi)
        simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using hs
      have hih : m ≤ tail 0 := ih tail htail
      dsimp [tail] at hih
      omega

/-- Finite counterexample-guided refinement terminates quantitatively: if each
of `m` successive refinements decodes to its predecessor and separates a live
task collision, then `m` is bounded by the initial collision count. -/
theorem collision_guided_refinement_length_bound
    {X : Type u} [Fintype X]
    {Z : Type v} {Y : Type w}
    (T : X → Y) (rep : ℕ → X → Z) (m : ℕ)
    (hstep : ∀ i < m,
      Refines (rep (i + 1)) (rep i) ∧
      ∃ x y,
        rep i x = rep i y ∧
        T x ≠ T y ∧
        rep (i + 1) x ≠ rep (i + 1) y) :
    m ≤ (collisionPairs (rep 0) T).card := by
  apply strict_nat_descent_length_bound m (fun i => (collisionPairs (rep i) T).card)
  intro i hi
  rcases hstep i hi with ⟨href, x, y, hcoarse, hT, hfine⟩
  exact collisionCard_strictly_decreases href hcoarse hT hfine

end Komorebi.AVOC
