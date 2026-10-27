import PaperX.SeedConsequences

/-!
Finite reachability certificates. A bounded walk search is accepted as complete
only after its closure under the original edges is proved. There is no claim that
an arbitrary cutoff is sufficient, and no external solver output is trusted.
-/
set_option autoImplicit false
namespace PaperX.SeedCertificates

open PaperX.DirectedSeeds
universe u v
variable {V : Type u} [Fintype V] [DecidableEq V]
variable (E : V → V → Prop) [DecidableRel E]

def neighbors (a : V) : Finset V := Finset.univ.filter (E a)

def reachableWithin : ℕ → V → Finset V
  | 0, a => {a}
  | n+1, a => reachableWithin n a ∪ (reachableWithin n a).biUnion (neighbors E)

theorem reachableWithin_self (n : ℕ) (a : V) : a ∈ reachableWithin E n a := by
  induction n with
  | zero => simp [reachableWithin]
  | succ n ih => exact Finset.mem_union_left _ ih

theorem reachableWithin_sound {n : ℕ} {a b : V} (h : b ∈ reachableWithin E n a) :
    Reach E a b := by
  induction n generalizing b with
  | zero =>
    have heq : b = a := Finset.mem_singleton.mp h
    subst b
    exact .refl
  | succ n ih =>
    rcases Finset.mem_union.mp h with h | h
    · exact ih h
    · obtain ⟨c, hc, hcb⟩ := Finset.mem_biUnion.mp h
      exact (ih hc).tail (Finset.mem_filter.mp hcb).2

def ClosedAt (n : ℕ) : Prop :=
  ∀ a b, b ∈ reachableWithin E n a → ∀ c, E b c → c ∈ reachableWithin E n a

instance closedAtDecidable (n : ℕ) : Decidable (ClosedAt E n) :=
  inferInstanceAs (Decidable (∀ a b, b ∈ reachableWithin E n a →
    ∀ c, E b c → c ∈ reachableWithin E n a))

theorem reach_iff_certificate (n : ℕ) (hclosed : ClosedAt E n) (a b : V) :
    Reach E a b ↔ b ∈ reachableWithin E n a := by
  constructor
  · intro h
    induction h with
    | refl => exact reachableWithin_self E n a
    | @tail b c _ hbc ih => exact hclosed a b ih c hbc
  · exact reachableWithin_sound E

def certifiedCover (n : ℕ) (S : Finset V) : Prop :=
  ∀ v, ∃ s ∈ S, v ∈ reachableWithin E n s

instance certifiedCoverDecidable (n : ℕ) (S : Finset V) :
    Decidable (certifiedCover E n S) :=
  inferInstanceAs (Decidable (∀ v, ∃ s ∈ S, v ∈ reachableWithin E n s))

theorem certifiedCover_iff (n : ℕ) (hclosed : ClosedAt E n) (S : Finset V) :
    certifiedCover E n S ↔ Covers E S := by
  simp only [certifiedCover, Covers, reach_iff_certificate E n hclosed]

/-- A certified complete component labeling is equivalent to the actual SCC quotient. -/
noncomputable def componentEquivOfLabels {K : Type v}
    (label : V → K) (rep : K → V) (sectionLaw : ∀ k, label (rep k) = k)
    (labelLaw : ∀ a b, label a = label b ↔ Reach E a b ∧ Reach E b a) :
    Component E ≃ K where
  toFun := Quotient.lift label (fun a b hab => (labelLaw a b).2 hab)
  invFun := fun k => component E (rep k)
  left_inv := by
    intro c
    induction c using Quotient.inductionOn with
    | h a =>
      apply (component_eq_iff E _ _).2
      exact (labelLaw _ _).1 (sectionLaw (label a))
  right_inv := sectionLaw

end PaperX.SeedCertificates
