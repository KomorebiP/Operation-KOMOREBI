import Komorebi.Foundation.LogicalCompactness
import Mathlib.Order.Filter.CardinalInter
import Mathlib.Order.Filter.Ultrafilter.Basic

/-!
# A conditional compactness bridge for fixed small domains

A fine kappa-complete ultrafilter is an explicit hypothesis, never an added axiom.
From it we prove compactness for constraints with fewer than kappa variables per
constraint and fewer than kappa possible values per variable. This bypasses infinitary
syntax without hiding the set-theoretic existence assumption.
-/

universe u

namespace Komorebi.FineUltrafilterCompactness

open Filter

/-- A kappa-complete ultrafilter picks one fiber of any map to a set of size < kappa. -/
theorem exists_eventually_constant {I A : Type u} (κ : Cardinal.{u})
    (U : Ultrafilter I) [CardinalInterFilter (U : Filter I) κ]
    (hA : Cardinal.mk A < κ) (f : I → A) :
    ∃ a : A, ∀ᶠ i in (U : Filter I), f i = a := by
  by_contra h
  have hn : ∀ a : A, ¬ (∀ᶠ i in (U : Filter I), f i = a) := by
    intro a ha
    exact h ⟨a, ha⟩
  have hc : ∀ a : A, ∀ᶠ i in (U : Filter I), f i ≠ a := by
    intro a
    exact Ultrafilter.eventually_not.mpr (hn a)
  have hall : ∀ᶠ i in (U : Filter I), ∀ a : A, f i ≠ a :=
    (Filter.eventually_cardinal_forall hA).mpr hc
  obtain ⟨i, hi⟩ := hall.exists
  exact hi (f i) rfl

/-- The genuine support set consists of the subsets of constraints of size < kappa. -/
def SmallPieces (κ : Cardinal.{u}) (I : Type u) :=
  {J : Set I // Cardinal.mk J < κ}

/-- Fineness says every individual constraint is present on a filter-large set of pieces. -/
def Fine {I : Type u} {κ : Cardinal.{u}}
    (U : Ultrafilter (SmallPieces κ I)) : Prop :=
  ∀ i : I, ∀ᶠ J in (U : Filter (SmallPieces κ I)), i ∈ J.val

/-- The new existence input that would require foundational justification. It is only
named as a proposition here; no witness or global principle is postulated. -/
def HasFineCompleteUltrafilter (κ : Cardinal.{u}) (I : Type u) : Prop :=
  ∃ U : Ultrafilter (SmallPieces κ I),
    CardinalInterFilter (U : Filter (SmallPieces κ I)) κ ∧ Fine U

/-- Fixed-domain compactness under a fine kappa-complete ultrafilter. Neither the
value set nor the variable set is replaced by a larger elementary extension. -/
theorem compactness_of_fine_complete
    {I V A : Type u} (κ : Cardinal.{u})
    (U : Ultrafilter (SmallPieces κ I))
    [CardinalInterFilter (U : Filter (SmallPieces κ I)) κ]
    (hfine : Fine U) (hA : Cardinal.mk A < κ)
    (scope : I → Set V) (hscope : ∀ i, Cardinal.mk (scope i) < κ)
    (satisfies : I → (V → A) → Prop)
    (locality : ∀ i a b, (∀ v ∈ scope i, a v = b v) → satisfies i a → satisfies i b)
    (hlocal : ∀ J : SmallPieces κ I, ∃ a : V → A, ∀ i ∈ J.val, satisfies i a) :
    ∃ a : V → A, ∀ i, satisfies i a := by
  classical
  choose localAssignment hlocalAssignment using hlocal
  have hchoice : ∀ v : V, ∃ a : A,
      ∀ᶠ J in (U : Filter (SmallPieces κ I)), localAssignment J v = a := by
    intro v
    exact exists_eventually_constant κ U hA (fun J => localAssignment J v)
  choose globalAssignment hglobal using hchoice
  refine ⟨globalAssignment, ?_⟩
  intro i
  have hagree : ∀ᶠ J in (U : Filter (SmallPieces κ I)),
      ∀ v ∈ scope i, localAssignment J v = globalAssignment v := by
    apply (Filter.eventually_cardinal_ball (hscope i)).mpr
    intro v _
    exact hglobal v
  obtain ⟨J, hJagree, hJi⟩ := (hagree.and (hfine i)).exists
  exact locality i (localAssignment J) globalAssignment hJagree (hlocalAssignment J i hJi)

/-- Contrapositive: with the same explicit input, global failure has a < kappa
subsystem already failing in the fixed value domain. -/
theorem small_obstruction_of_no_global
    {I V A : Type u} (κ : Cardinal.{u})
    (hexists : HasFineCompleteUltrafilter κ I) (hA : Cardinal.mk A < κ)
    (scope : I → Set V) (hscope : ∀ i, Cardinal.mk (scope i) < κ)
    (satisfies : I → (V → A) → Prop)
    (locality : ∀ i a b, (∀ v ∈ scope i, a v = b v) → satisfies i a → satisfies i b)
    (hbad : ¬ ∃ a : V → A, ∀ i, satisfies i a) :
    ∃ J : SmallPieces κ I, ¬ ∃ a : V → A, ∀ i ∈ J.val, satisfies i a := by
  by_contra h
  have hlocal : ∀ J : SmallPieces κ I, ∃ a : V → A, ∀ i ∈ J.val, satisfies i a := by
    intro J
    by_contra hj
    exact h ⟨J, hj⟩
  obtain ⟨U, hcomplete, hfine⟩ := hexists
  let : CardinalInterFilter (U : Filter (SmallPieces κ I)) κ := hcomplete
  exact hbad (compactness_of_fine_complete κ U hfine hA scope hscope satisfies locality hlocal)

/-- Concrete depth-zero residual encoding of a fixed-domain constraint problem. -/
def residualSystem {I V A : Type u} (κ : Cardinal.{u})
    (satisfies : I → (V → A) → Prop) : SizedResidualSystem where
  Piece := SmallPieces κ I
  size J := Cardinal.mk J.val
  Exact := ∃ a : V → A, ∀ i, satisfies i a
  Obstruct q J := q = 0 ∧ ¬ ∃ a : V → A, ∀ i ∈ J.val, satisfies i a

/-- The explicit ultrafilter hypothesis proves KRR0 for this concrete class. -/
theorem residualSystem_krr0
    {I V A : Type u} (κ : Cardinal.{u})
    (hexists : HasFineCompleteUltrafilter κ I) (hA : Cardinal.mk A < κ)
    (scope : I → Set V) (hscope : ∀ i, Cardinal.mk (scope i) < κ)
    (satisfies : I → (V → A) → Prop)
    (locality : ∀ i a b, (∀ v ∈ scope i, a v = b v) → satisfies i a → satisfies i b) :
    (residualSystem κ satisfies).KRR0At κ := by
  intro hbad
  obtain ⟨J, hJ⟩ := small_obstruction_of_no_global κ hexists hA scope hscope
    satisfies locality hbad
  exact ⟨J, J.property, rfl, hJ⟩

end Komorebi.FineUltrafilterCompactness
