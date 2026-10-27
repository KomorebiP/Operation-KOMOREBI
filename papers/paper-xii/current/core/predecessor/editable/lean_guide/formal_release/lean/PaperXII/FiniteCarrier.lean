import Mathlib.RingTheory.Artinian.Module
import Mathlib.LinearAlgebra.FiniteDimensional.Basic

/-! Paper XII, 8.7–8.8. Index zero is the manuscript's first level. -/
namespace PaperXII.FiniteCarrier

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]

/-- The entire descending submodule chain eventually stabilizes. -/
theorem descending_stabilizes (W : ℕ → Submodule K V) (hW : Antitone W) :
    ∃ N, ∀ n, N ≤ n → W n = W N := by
  obtain ⟨N, hN⟩ := IsArtinian.monotone_stabilizes (R := K) (M := V) ⟨W, hW⟩
  exact ⟨N, fun n hn ↦ (hN n hn).symm⟩

/-- The stable value equals the intersection of all levels. -/
theorem exists_iInf_eq (W : ℕ → Submodule K V) (hW : Antitone W) :
    ∃ N, (⨅ n, W n) = W N ∧ ∀ n, N ≤ n → W n = W N := by
  obtain ⟨N, hN⟩ := descending_stabilizes W hW
  refine ⟨N, le_antisymm (iInf_le W N) ?_, hN⟩
  apply le_iInf
  intro n
  rcases le_total n N with hn | hn
  · exact hW hn
  · exact (hN n hn).symm.le

/-- Nonzero levels in a descending finite-dimensional chain have nonzero intersection. -/
theorem iInf_ne_bot (W : ℕ → Submodule K V) (hW : Antitone W)
    (hne : ∀ n, W n ≠ ⊥) : (⨅ n, W n) ≠ ⊥ := by
  obtain ⟨N, hN, _⟩ := exists_iInf_eq W hW
  rw [hN]
  exact hne N

/-- A zero intersection is witnessed at a finite level. -/
theorem exists_eq_bot_of_iInf_eq_bot (W : ℕ → Submodule K V) (hW : Antitone W)
    (hzero : (⨅ n, W n) = ⊥) : ∃ n, W n = ⊥ := by
  obtain ⟨N, hN, _⟩ := exists_iInf_eq W hW
  exact ⟨N, hN.symm.trans hzero⟩

omit [FiniteDimensional K V] in
/-- The absorption relation forces the packet ranges to descend.
Idempotence and the reverse absorption relation are not needed for this implication. -/
theorem ranges_antitone (e : ℕ → Module.End K V)
    (habs : ∀ n, (e n).comp (e (n + 1)) = e (n + 1)) :
    Antitone (fun n ↦ LinearMap.range (e n)) := by
  apply antitone_nat_of_succ_le
  intro n y hy
  obtain ⟨v, rfl⟩ := hy
  refine ⟨e (n + 1) v, ?_⟩
  exact LinearMap.congr_fun (habs n) v

/-- Manuscript 8.7, with stabilization and nonzero intersection in one statement. -/
theorem nested_packets (e : ℕ → Module.End K V)
    (habs : ∀ n, (e n).comp (e (n + 1)) = e (n + 1))
    (hne : ∀ n, LinearMap.range (e n) ≠ ⊥) :
    (∃ N, ∀ n, N ≤ n → LinearMap.range (e n) = LinearMap.range (e N)) ∧
      (⨅ n, LinearMap.range (e n)) ≠ ⊥ :=
  ⟨descending_stabilizes _ (ranges_antitone e habs),
    iInf_ne_bot _ (ranges_antitone e habs) hne⟩

/-- Manuscript 8.8. This holds without assuming the individual ranges are nonzero. -/
theorem finite_incompatibility_witness (e : ℕ → Module.End K V)
    (habs : ∀ n, (e n).comp (e (n + 1)) = e (n + 1))
    (hzero : (⨅ n, LinearMap.range (e n)) = ⊥) :
    ∃ n, LinearMap.range (e n) = ⊥ :=
  exists_eq_bot_of_iInf_eq_bot _ (ranges_antitone e habs) hzero

end PaperXII.FiniteCarrier
