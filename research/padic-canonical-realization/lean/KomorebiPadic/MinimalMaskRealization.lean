import KomorebiPadic.CanonicalLinearRealization
import KomorebiPadic.ObservableMaskAutomaton

/-! # Canonical minimum-cardinality linear realizations of rational-mask coefficients
The category is fixed: R-linear state modules, the alphabet Fin p, distinguished
initial state, and R-linear output. Equivalence means equality on ALL words.
Existence of a noncomputable formal machine is not an efficient executable compiler.
-/
namespace KomorebiPadic
open Polynomial
noncomputable section

/-- The all-word function includes noncanonical digit encodings and the empty word. -/
def canonicalMaskWordBehavior (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) : ResidualRealization.Behavior (ZMod (p^r)) (Fin p) :=
  fun ds => PowerSeries.coeff (cartierWordValue p (ds.map Fin.val)) (canonicalMaskSeries p r A B hp hr hB)

/-- The already constructed reachable-observable quotient, with no changed executable rule. -/
def minimalMaskSystem (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) :
    LinearObservability.System (ZMod (p^r)) (ObservableMaskState p r A B hp hr hB) (Fin p) :=
  LinearObservability.quotientSystem (observableMaskSystem p r A B hp hr hB)

theorem minimalMaskSystem_reachable (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) : ResidualRealization.IsReachable (minimalMaskSystem p r A B hp hr hB) :=
  observableMask_reachable p r A B hp hr hB

theorem minimalMaskSystem_observable (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) : ResidualRealization.IsObservable (minimalMaskSystem p r A B hp hr hB) :=
  LinearObservability.quotient_observable _

theorem minimalMaskSystem_behavior (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    ResidualRealization.behavior (minimalMaskSystem p r A B hp hr hB) =
      canonicalMaskWordBehavior p r A B hp hr hB := by
  funext ds
  simp only [ResidualRealization.behavior, LinearObservability.observation,
    LinearMap.comp_apply, LinearObservability.wordMap_apply]
  exact observableMask_output_canonical_word p r A B hp hr hB hAB ds

/-- Intrinsic residual coordinates, depending on the word function rather than a mask presentation. -/
def minimalMaskEquivResidual (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    ObservableMaskState p r A B hp hr hB ≃ₗ[ZMod (p^r)]
      ResidualRealization.ResidualState (canonicalMaskWordBehavior p r A B hp hr hB) :=
  ResidualRealization.equivResidual _ _ (minimalMaskSystem_reachable p r A B hp hr hB)
    (minimalMaskSystem_observable p r A B hp hr hB) (minimalMaskSystem_behavior p r A B hp hr hB hAB)

theorem minimalMaskEquivResidual_simulation (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    ResidualRealization.Simulation (minimalMaskSystem p r A B hp hr hB)
      (ResidualRealization.residualSystem (canonicalMaskWordBehavior p r A B hp hr hB))
      (minimalMaskEquivResidual p r A B hp hr hB hAB).toLinearMap :=
  ResidualRealization.equivResidual_simulation _ _ (minimalMaskSystem_reachable p r A B hp hr hB)
    (minimalMaskSystem_observable p r A B hp hr hB) (minimalMaskSystem_behavior p r A B hp hr hB hAB)

/-- An arbitrary linear competitor need not be reachable; its reachable part still surjects. -/
theorem minimalMask_comparison {V : Type*} [AddCommGroup V] {p r : ℕ} [Module (ZMod (p^r)) V]
    (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0)
    (hAB : MaskConstantsAgree p r A B)
    (N : LinearObservability.System (ZMod (p^r)) V (Fin p))
    (hf : ResidualRealization.behavior N = canonicalMaskWordBehavior p r A B hp hr hB) :
    ∃ g : LinearReachability.State N.dynamics →ₗ[ZMod (p^r)] ObservableMaskState p r A B hp hr hB,
      ResidualRealization.Simulation (ResidualRealization.reachableSystem N)
        (minimalMaskSystem p r A B hp hr hB) g ∧ Function.Surjective g :=
  ResidualRealization.exists_surjective_comparison_from_reachable _ N
    (minimalMaskSystem_reachable p r A B hp hr hB) (minimalMaskSystem_observable p r A B hp hr hB)
    (hf.trans (minimalMaskSystem_behavior p r A B hp hr hB hAB).symm)

/-- Global cardinality minimality, not merely a comparison with predecessor quotients. -/
theorem minimalMask_cardinality {V : Type*} [AddCommGroup V] [Finite V] {p r : ℕ}
    [Module (ZMod (p^r)) V] (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B)
    (N : LinearObservability.System (ZMod (p^r)) V (Fin p))
    (hf : ResidualRealization.behavior N = canonicalMaskWordBehavior p r A B hp hr hB) :
    Nat.card (ObservableMaskState p r A B hp hr hB) ≤ Nat.card V :=
  ResidualRealization.minimal_cardinality _ N
    (minimalMaskSystem_reachable p r A B hp hr hB) (minimalMaskSystem_observable p r A B hp hr hB)
    (hf.trans (minimalMaskSystem_behavior p r A B hp hr hB hAB).symm)

/-- Reachable-observable competitors have a unique isomorphism preserving the full machine. -/
theorem minimalMask_unique_equiv {V : Type*} [AddCommGroup V] {p r : ℕ}
    [Module (ZMod (p^r)) V] (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B)
    (N : LinearObservability.System (ZMod (p^r)) V (Fin p))
    (hR : ResidualRealization.IsReachable N) (hO : ResidualRealization.IsObservable N)
    (hf : ResidualRealization.behavior N = canonicalMaskWordBehavior p r A B hp hr hB) :
    ∃! e : ObservableMaskState p r A B hp hr hB ≃ₗ[ZMod (p^r)] V,
      ResidualRealization.Simulation (minimalMaskSystem p r A B hp hr hB) N e.toLinearMap := by
  let M := minimalMaskSystem p r A B hp hr hB
  let f := canonicalMaskWordBehavior p r A B hp hr hB
  let hMR := minimalMaskSystem_reachable p r A B hp hr hB
  let hMO := minimalMaskSystem_observable p r A B hp hr hB
  let hMf := minimalMaskSystem_behavior p r A B hp hr hB hAB
  refine ⟨ResidualRealization.canonicalEquiv M N f hMR hMO hR hO hMf hf,
    ResidualRealization.canonicalEquiv_simulation M N f hMR hMO hR hO hMf hf, ?_⟩
  intro e he
  exact ResidualRealization.canonicalEquiv_unique M N f hMR hMO hR hO hMf hf e he

/-- Equality of actual series gives all-word behavior equality, not just canonical-digit equality. -/
theorem canonicalMaskWordBehavior_eq_of_series_eq (p r : ℕ) (A B C D : ℤ[X])
    (hp : p.Prime) (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hD : ¬ (p : ℤ) ∣ D.coeff 0)
    (hF : canonicalMaskSeries p r A B hp hr hB = canonicalMaskSeries p r C D hp hr hD) :
    canonicalMaskWordBehavior p r A B hp hr hB = canonicalMaskWordBehavior p r C D hp hr hD := by
  funext ds
  exact congrArg (PowerSeries.coeff (cartierWordValue p (ds.map Fin.val))) hF

/-- A finite intrinsic residual module follows from the already finite quotient. -/
theorem canonicalMaskResidual_finite (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    Finite (ResidualRealization.ResidualState (canonicalMaskWordBehavior p r A B hp hr hB)) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  let : Fintype (ReachableMaskState p r A B hp) := Fintype.ofFinite _
  exact Finite.of_surjective (minimalMaskEquivResidual p r A B hp hr hB hAB)
    (minimalMaskEquivResidual p r A B hp hr hB hAB).surjective

/-- Mathematical compiler certificate; no runtime refinement is asserted by this record. -/
structure MinimalCanonicalMaskCertificate (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime)
    (hr : 0 < r) (hB : ¬ (p : ℤ) ∣ B.coeff 0) where
  predecessor : ObservableCanonicalMaskCertificate p r A B hp hr hB
  residualEquiv : ObservableMaskState p r A B hp hr hB ≃ₗ[ZMod (p^r)]
    ResidualRealization.ResidualState (canonicalMaskWordBehavior p r A B hp hr hB)
  residual_simulation : ResidualRealization.Simulation (minimalMaskSystem p r A B hp hr hB)
    (ResidualRealization.residualSystem (canonicalMaskWordBehavior p r A B hp hr hB)) residualEquiv.toLinearMap
  behavior_exact : ResidualRealization.behavior (minimalMaskSystem p r A B hp hr hB) =
    canonicalMaskWordBehavior p r A B hp hr hB
  minimum_cardinality : ∀ (V : Type) [AddCommGroup V] [Module (ZMod (p^r)) V] [Finite V]
    (N : LinearObservability.System (ZMod (p^r)) V (Fin p)),
    ResidualRealization.behavior N = canonicalMaskWordBehavior p r A B hp hr hB →
      Nat.card (ObservableMaskState p r A B hp hr hB) ≤ Nat.card V

def compileCanonicalMask (p r : ℕ) (A B : ℤ[X]) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    MinimalCanonicalMaskCertificate p r A B hp hr hB where
  predecessor := observableCanonicalMaskCertificate p r A B hp hr hB hAB
  residualEquiv := minimalMaskEquivResidual p r A B hp hr hB hAB
  residual_simulation := minimalMaskEquivResidual_simulation p r A B hp hr hB hAB
  behavior_exact := minimalMaskSystem_behavior p r A B hp hr hB hAB
  minimum_cardinality := fun _ _ _ _ N hf => minimalMask_cardinality A B hp hr hB hAB N hf

end
end KomorebiPadic
