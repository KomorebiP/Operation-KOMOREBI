import Komorebi.Foundation.LogicalCompactness

/-!
# Boundaries of the residual interface

These results separate witness completeness from witness soundness, make the direction
of depth monotonicity explicit, and show that unrestricted syntactic reindexing can
hide a depth index inside a local-piece label. None is a consistency-strength theorem.
-/

namespace Komorebi.ResidualSystem

/-- A detected admissible obstruction must actually imply global failure. -/
def Sound (S : ResidualSystem) : Prop :=
  ∀ q J, S.Small J → S.Obstruct q J → ¬ S.Exact

/-- The earlier KRR definition supplies completeness only; soundness is separate. -/
theorem exact_iff_no_witness {S : ResidualSystem} (hs : S.Sound) (hc : S.KRR) :
    S.Exact ↔ ¬ S.HasResidualWitness := by
  constructor
  · intro he ⟨q, J, hj, ho⟩
    exact hs q J hj ho he
  · intro hn
    by_contra he
    exact hn (hc he)

/-- An explicit depth bound, with the same exactness and admissibility predicates. -/
def KRRUpTo (S : ResidualSystem) (d : ℕ) : Prop :=
  ¬ S.Exact → ∃ q J, q ≤ d ∧ S.Small J ∧ S.Obstruct q J

/-- Permitting more depths makes the assertion weaker, not stronger, for fixed data. -/
theorem krrUpTo_mono {S : ResidualSystem} {d e : ℕ} (hde : d ≤ e)
    (h : S.KRRUpTo d) : S.KRRUpTo e := by
  intro hf
  obtain ⟨q, J, hq, hj, ho⟩ := h hf
  exact ⟨q, J, le_trans hq hde, hj, ho⟩

theorem krrUpTo_zero_iff {S : ResidualSystem} : S.KRRUpTo 0 ↔ S.KRR0 := by
  constructor
  · intro h hf
    obtain ⟨q, J, hq, hj, ho⟩ := h hf
    have heq : q = 0 := Nat.eq_zero_of_le_zero hq
    exact ⟨J, hj, heq ▸ ho⟩
  · intro h hf
    obtain ⟨J, hj, ho⟩ := h hf
    exact ⟨0, J, le_refl 0, hj, ho⟩

theorem krr_of_krrUpTo {S : ResidualSystem} {d : ℕ} (h : S.KRRUpTo d) : S.KRR := by
  intro hf
  obtain ⟨q, J, _, hj, ho⟩ := h hf
  exact ⟨q, J, hj, ho⟩

/-- Reindexing only: it records the original depth inside a pair, rather than removing
its mathematical content. No semantic support, definability, or cost preservation is
claimed by this construction. -/
def degreePacked (S : ResidualSystem) : ResidualSystem where
  Piece := ℕ × S.Piece
  Small p := S.Small p.2
  Exact := S.Exact
  Obstruct q p := q = 0 ∧ S.Obstruct p.1 p.2

/-- Arbitrary predicate systems permit a tautological depth-zero re-presentation. This
is not the predecessor's fixed-system `Flattenable` property. -/
theorem packed_krr0_iff {S : ResidualSystem} : S.degreePacked.KRR0 ↔ S.KRR := by
  constructor
  · intro h hf
    obtain ⟨⟨q, J⟩, hj, _, ho⟩ := h hf
    exact ⟨q, J, hj, ho⟩
  · intro h hf
    obtain ⟨q, J, hj, ho⟩ := h hf
    exact ⟨(q, J), hj, rfl, ho⟩

theorem packed_sound_iff {S : ResidualSystem} : S.degreePacked.Sound ↔ S.Sound := by
  constructor
  · intro h q J hj ho
    exact h 0 (q, J) hj ⟨rfl, ho⟩
  · intro h q p hj ho
    exact h p.1 p.2 hj ho.2

/-- Even soundness alone is not a completeness or reflection principle. -/
theorem sound_does_not_imply_krr :
    ∃ S : ResidualSystem.{0}, S.Sound ∧ ¬ S.KRR := by
  let S : ResidualSystem := {
    Piece := Unit
    Small := fun _ => True
    Exact := False
    Obstruct := fun _ _ => False }
  refine ⟨S, ?_, ?_⟩
  · intro _ _ _ h
    exact h.elim
  · intro h
    obtain ⟨_, _, _, ho⟩ := h (fun hf => hf)
    exact ho

end Komorebi.ResidualSystem
