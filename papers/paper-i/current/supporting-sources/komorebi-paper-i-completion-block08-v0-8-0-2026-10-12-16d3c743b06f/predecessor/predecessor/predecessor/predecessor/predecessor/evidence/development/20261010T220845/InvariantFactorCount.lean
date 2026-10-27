import PaperICompletion3.OperatorPrimaryAPI

/-!
# Exact invariant-factor count

The publication's corollary starts with an actual rational canonical
presentation. From that presentation and the divisibility chain, the seed
count is proved, not accepted as a certificate. Existence of an ordered
invariant-factor presentation is not asserted by this module.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperICompletion3.InvariantFactorCount

open Polynomial
open Komorebi.SeedRankBasics
open Komorebi.PaperICompletion3.PrimarySeedFormula

universe u v
variable {k : Type u} [Field k]

/-- A chain of nonconstant invariant factors requires exactly one seed per factor.
The empty chain has minimum zero. -/
theorem invariantFactorProduct_seedNumber_isLeast {r : ℕ}
    (f : Fin r → k[X]) (hf : ∀ i, 0 < (f i).natDegree)
    (hchain : ∀ i j, i ≤ j → f i ∣ f j) :
    IsLeast {n : ℕ | ∃ s : Fin n → ((i : Fin r) → k[X] ⧸ Ideal.span {f i}),
      FamilyGenerates k[X] ((i : Fin r) → k[X] ⧸ Ideal.span {f i}) s} r := by
  classical
  constructor
  · refine ⟨coloredSeeds (fun i ↦ Ideal.span {f i}) (fun i ↦ i), ?_⟩
    apply coloredSeeds_generate
    intro i j hne heq
    exact (hne heq).elim
  · rintro n ⟨s, hs⟩
    by_cases hr : r = 0
    · subst r
      exact Nat.zero_le _
    · let first : Fin r := ⟨0, Nat.pos_of_ne_zero hr⟩
      obtain ⟨p, hp, hpf⟩ := Polynomial.exists_irreducible_of_natDegree_pos (hf first)
      let P : Ideal k[X] := Ideal.span {p}
      let : P.IsMaximal := PrincipalIdealRing.isMaximal_of_irreducible hp
      have hIP : ∀ i : Fin r, Ideal.span {f i} ≤ P := by
        intro i
        exact Ideal.span_singleton_le_span_singleton.mpr
          (hpf.trans (hchain first i (Fin.mk_le_mk.mpr (Nat.zero_le _))))
      have h := fiberMultiplicity_le_of_generates (fun i ↦ Ideal.span {f i})
        (fun _ : Fin r ↦ P) hIP P s hs
      simpa [fiberMultiplicity, ← Nat.card_eq_fintype_card] using h

/-- The printed invariant-factor corollary, for the actual polynomial module.
Only the displayed decomposition and nonconstant divisibility chain are inputs. -/
theorem invariantFactor_operator_seedRanks {V : Type v} [AddCommGroup V] [Module k V]
    (T : Module.End k V) {r : ℕ}
    (f : Fin r → k[X]) (hf : ∀ i, 0 < (f i).natDegree)
    (hchain : ∀ i j, i ≤ j → f i ∣ f j)
    (E : Module.AEval' T ≃ₗ[k[X]] ((i : Fin r) → k[X] ⧸ Ideal.span {f i})) :
    IsLeast {n : ℕ | Komorebi.SingleOperatorGraph.SeedNumberLE T n} r ∧
      seedFinrank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V = r ∧
      seedRank (Komorebi.SingleOperatorGraph.operatorAlgebra T) V = (r : Cardinal) := by
  have h := operator_seedNumber_isLeast_of_polynomialModule T r
    (seedNumber_isLeast_linearEquiv E r (invariantFactorProduct_seedNumber_isLeast f hf hchain))
  exact ⟨h,
    Komorebi.SingleOperatorGraph.operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast T r h,
    Komorebi.SingleOperatorGraph.operatorAlgebra_seedRank_eq_of_seedNumber_isLeast T r h⟩

end Komorebi.PaperICompletion3.InvariantFactorCount
