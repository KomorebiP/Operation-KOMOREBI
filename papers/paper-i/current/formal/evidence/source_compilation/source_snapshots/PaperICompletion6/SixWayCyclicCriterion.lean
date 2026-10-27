import PaperICompletion6.ScalarExtension
import PaperICompletion6.PrimaryCyclicCriterion
import PaperICompletion6.OneInvariantFactor
import Mathlib.FieldTheory.IsAlgClosed.AlgebraicClosure
import Mathlib.Tactic.TFAE

/-! # The six-way cyclic-matrix criterion
Every clause refers to the actual operator, its intrinsic primary components,
an actual one-factor presentation, or its literal tensor-product extension.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperICompletion6.SixWayCyclicCriterion
open Polynomial
open Komorebi.SingleOperatorGraph
open Komorebi.SeedRankBasics
open Komorebi.PaperICompletion.CyclicClassification
open Komorebi.PaperICompletion4.IntrinsicPrimary
open Komorebi.PaperICompletion6.ScalarExtension
open Komorebi.PaperICompletion6.PrimaryCyclicCriterion
open Komorebi.PaperICompletion6.OneInvariantFactor
universe u v w
variable {k : Type u} [Field k] {V : Type v} [AddCommGroup V] [Module k V]
variable [FiniteDimensional k V] [Nontrivial V]

/-- All six printed clauses over an arbitrary algebraically closed extension. -/
theorem cyclic_six_way (K : Type w) [Field K] [Algebra k K] [IsAlgClosed K]
    (T : Module.End k V) :
    List.TFAE [
      HasCyclicVector T,
      seedRank (operatorAlgebra T) V = 1,
      ∀ p : k[X], Irreducible p →
        Nontrivial (primarySubmodule (Module.AEval' T) p) →
        Cyclic k[X] (primarySubmodule (Module.AEval' T) p),
      HasOneInvariantFactor T,
      minpoly k T = T.charpoly,
      ∀ a : K, a ∈ spectrum K (T.baseChange K) →
        Module.finrank K (Module.End.eigenspace (T.baseChange K) a) = 1] := by
  tfae_have 1 ↔ 5 := hasCyclicVector_iff_minpoly_eq_charpoly T
  tfae_have 2 ↔ 5 := operatorAlgebra_seedRank_eq_one_iff_minpoly_eq_charpoly T
  tfae_have 1 ↔ 3 := hasCyclicVector_iff_nonzero_primary_cyclic T
  tfae_have 1 ↔ 4 := hasCyclicVector_iff_oneInvariantFactor T
  tfae_have 1 ↔ 6 := hasCyclicVector_iff_extended_spectral_multiplicities_one K T
  tfae_finish

/-- The precise algebraic-closure instance in the manuscript. -/
theorem cyclic_six_way_algebraicClosure (T : Module.End k V) :
    List.TFAE [
      HasCyclicVector T,
      seedRank (operatorAlgebra T) V = 1,
      ∀ p : k[X], Irreducible p →
        Nontrivial (primarySubmodule (Module.AEval' T) p) →
        Cyclic k[X] (primarySubmodule (Module.AEval' T) p),
      HasOneInvariantFactor T,
      minpoly k T = T.charpoly,
      ∀ a : AlgebraicClosure k, a ∈ spectrum (AlgebraicClosure k)
          (T.baseChange (AlgebraicClosure k)) →
        Module.finrank (AlgebraicClosure k)
          (Module.End.eigenspace (T.baseChange (AlgebraicClosure k)) a) = 1] :=
  cyclic_six_way (AlgebraicClosure k) T

/-- In any supplied invariant-factor chain, cyclicity forces exactly one factor. -/
theorem cyclic_iff_invariantFactor_count_one (T : Module.End k V) {r : ℕ}
    (p : Fin r → k[X]) (hp : ∀ i, 0 < (p i).natDegree)
    (hchain : ∀ i j, i ≤ j → p i ∣ p j)
    (E : Module.AEval' T ≃ₗ[k[X]] ((i : Fin r) → k[X] ⧸ Ideal.span {p i})) :
    HasCyclicVector T ↔ r = 1 := by
  have hr := (Komorebi.PaperICompletion3.InvariantFactorCount.invariantFactor_operator_seedRanks T p hp hchain E).2.2
  have h := (hasCyclicVector_iff_minpoly_eq_charpoly T).trans
    (operatorAlgebra_seedRank_eq_one_iff_minpoly_eq_charpoly T).symm
  rw [hr] at h
  exact h.trans (by norm_cast)

end Komorebi.PaperICompletion6.SixWayCyclicCriterion
