import SplitPrimeTransverseLocalization
import RelativeTaylorWilesFiniteSet

/-!
# Split-prime raw local functionals instantiate auxiliary selection

If every admissible localization kills the canonical cyclic class, then an
uncentered raw local detector canonically defines a functional on the global
transverse quotient.  A one-prime detection hypothesis for these raw
functionals therefore instantiates the v0.15 auxiliary-selection interface and
produces an exact finite detecting set.

This is an abstract arithmetic interface.  It does not construct the primes,
localization maps, or local Tate-duality functionals.
-/

namespace Komorebi.StrongArtin.SplitPrimeAuxiliarySelectionCapstone

open Komorebi.StrongArtin.SplitPrimeTransverseLocalization
open Komorebi.StrongArtin.AdaptiveAuxiliarySelection
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet

noncomputable section

variable {k H L Aux : Type*} [Field k]
  [AddCommGroup H] [Module k H]
  [AddCommGroup L] [Module k L]

/-- The v0.15 one-prime interface built from raw local functionals at labels
whose localization kills the cyclic defect. -/
def splitPrimeSelectionInterface
    (d : H)
    (loc : Aux → H →ₗ[k] L)
    (hkill : ∀ a : Aux, loc a d = 0)
    (probe : Aux → Module.Dual k L)
    (admissible : Aux → Prop)
    (hdetect : ∀ x : H ⧸ cyclicLine (k := k) d, x ≠ 0 →
      ∃ a : Aux, admissible a ∧
        transverseLocalFunctional (loc a) d (hkill a) (probe a) x ≠ 0) :
    OnePrimeSelectionInterface k (H ⧸ cyclicLine (k := k) d) Aux where
  admissible := admissible
  localFunctional a :=
    transverseLocalFunctional (loc a) d (hkill a) (probe a)
  detects := hdetect

/--
**Split-prime auxiliary-selection capstone.** If every nonzero transverse class
is detected by one admissible raw local functional and all admissible
localizations kill the cyclic class, then exactly the transverse dimension many
admissible labels can be selected; their simultaneous raw local evaluation is
injective on the quotient.
-/
theorem exists_exact_splitPrime_auxiliary_set
    (d : H)
    [DecidableEq Aux]
    [FiniteDimensional k (H ⧸ cyclicLine (k := k) d)]
    (loc : Aux → H →ₗ[k] L)
    (hkill : ∀ a : Aux, loc a d = 0)
    (probe : Aux → Module.Dual k L)
    (admissible : Aux → Prop)
    (hdetect : ∀ x : H ⧸ cyclicLine (k := k) d, x ≠ 0 →
      ∃ a : Aux, admissible a ∧
        transverseLocalFunctional (loc a) d (hkill a) (probe a) x ≠ 0) :
    ∃ Q : Finset Aux,
      (∀ a ∈ Q, admissible a) ∧
      Q.card = Module.finrank k (H ⧸ cyclicLine (k := k) d) ∧
      selectedKernel
        (fun a => transverseLocalFunctional (loc a) d (hkill a) (probe a)) Q = ⊥ ∧
      Function.Injective
        (evaluationMap
          (fun a => transverseLocalFunctional (loc a) d (hkill a) (probe a)) Q) := by
  exact exists_relative_TaylorWiles_set_exact
    (splitPrimeSelectionInterface d loc hkill probe admissible hdetect)

/-- The selected simultaneous evaluations agree exactly with the original raw
local evaluations on representatives of global classes. -/
theorem selected_evaluation_on_representative
    [DecidableEq Aux]
    (d : H)
    (loc : Aux → H →ₗ[k] L)
    (hkill : ∀ a : Aux, loc a d = 0)
    (probe : Aux → Module.Dual k L)
    (Q : Finset Aux) (h : H) (a : Q) :
    evaluationMap
      (fun i => transverseLocalFunctional (loc i) d (hkill i) (probe i)) Q
      ((cyclicLine (k := k) d).mkQ h) a =
        probe a.1 (loc a.1 h) := by
  rfl

end

end Komorebi.StrongArtin.SplitPrimeAuxiliarySelectionCapstone

#print axioms Komorebi.StrongArtin.SplitPrimeAuxiliarySelectionCapstone.splitPrimeSelectionInterface
#print axioms Komorebi.StrongArtin.SplitPrimeAuxiliarySelectionCapstone.exists_exact_splitPrime_auxiliary_set
#print axioms Komorebi.StrongArtin.SplitPrimeAuxiliarySelectionCapstone.selected_evaluation_on_representative
