import PaperX.SeedCertificates
import PaperX.SeedBoundary

/-!
A new explicit seven-root transport model matching the manuscript's component
pattern. This is not presented as a rerun of the unretrieved companion script.
-/
set_option autoImplicit false
set_option maxRecDepth 4096
set_option maxHeartbeats 2000000
namespace PaperX.SeedExamples

open PaperX.DirectedSeeds PaperX.SeedCertificates

def edges : Finset (Fin 7 × Fin 7) :=
  {(0,1),(1,0),(1,2),(2,5),(3,4),(4,3),(4,5),(6,5)}

def edge (a b : Fin 7) : Prop := (a,b) ∈ edges

instance edgeDecidable : DecidableRel edge := fun _ _ => inferInstanceAs (Decidable (_ ∈ edges))

theorem closure_closed : ClosedAt edge 3 := by decide +kernel

theorem reach_iff (a b : Fin 7) : Reach edge a b ↔ b ∈ reachableWithin edge 3 a :=
  reach_iff_certificate edge 3 closure_closed a b

def label : Fin 7 → Fin 5 := ![0,0,1,2,2,3,4]

def rep : Fin 5 → Fin 7 := ![0,2,3,5,6]

theorem label_rep : ∀ k, label (rep k) = k := by decide

theorem label_law : ∀ a b, label a = label b ↔ Reach edge a b ∧ Reach edge b a := by
  simp only [reach_iff]
  decide +kernel

noncomputable def componentEquiv : Component edge ≃ Fin 5 :=
  componentEquivOfLabels edge label rep label_rep label_law

theorem component_count : Nat.card (Component edge) = 5 := by
  rw [Nat.card_congr componentEquiv]
  simp

def sourceLabel (k : Fin 5) : Prop := k = 0 ∨ k = 2 ∨ k = 4

instance sourceLabelDecidable : DecidablePred sourceLabel :=
  fun _ => inferInstanceAs (Decidable (_ = 0 ∨ _ = 2 ∨ _ = 4))

theorem source_label_iff (k : Fin 5) :
    IsSource edge (component edge (rep k)) ↔ sourceLabel k := by
  rw [source_iff]
  simp only [reach_iff]
  revert k
  decide +kernel

noncomputable def sourceEquiv : Source edge ≃ {k : Fin 5 // sourceLabel k} :=
  componentEquiv.subtypeEquiv (fun c => by
    have h := source_label_iff (componentEquiv c)
    have heq : component edge (rep (componentEquiv c)) = c := componentEquiv.left_inv c
    rw [heq] at h
    exact h)

theorem source_count : Nat.card (Source edge) = 3 := by
  rw [Nat.card_congr sourceEquiv, Nat.card_eq_fintype_card]
  decide

theorem rank_three : seedRank edge = 3 := by
  rw [directed_minimum_seed, source_count]

def chosenSeeds : Finset (Fin 7) := {0,3,6}

theorem chosenSeeds_cover : Covers edge chosenSeeds := by
  apply (certifiedCover_iff edge 3 closure_closed _).1
  decide +kernel

theorem chosenSeeds_optimal (S : Finset (Fin 7)) (hS : Covers edge S) :
    chosenSeeds.card ≤ S.card := by
  have h := seedRank_le edge S hS
  rw [rank_three] at h
  exact h

/-- All minima in the explicit example, computed from a certified path closure. -/
def minimumSeedSets : Finset (Finset (Fin 7)) :=
  Finset.univ.powerset.filter (fun S => S.card = 3 ∧ certifiedCover edge 3 S)

theorem minimumSeedSets_iff (S : Finset (Fin 7)) :
    S ∈ minimumSeedSets ↔ Covers edge S ∧ S.card = seedRank edge := by
  simp only [minimumSeedSets, Finset.mem_filter, Finset.mem_powerset,
    Finset.subset_univ, true_and, certifiedCover_iff edge 3 closure_closed,
    rank_three, and_comm]

theorem minimumSeedSets_exact : minimumSeedSets =
    {{0,3,6},{0,4,6},{1,3,6},{1,4,6}} := by decide +kernel

theorem four_minimum_sets : minimumSeedSets.card = 4 := by
  rw [minimumSeedSets_exact]
  decide

/-- Removing the seed for G fails, despite the downstream meeting at F. -/
theorem two_seeds_do_not_cover : ¬ Covers edge {0,3} := by
  rw [← certifiedCover_iff edge 3 closure_closed]
  decide +kernel

/-- The empty graph is included, with rank zero rather than a forced seed. -/
theorem empty_graph_rank : seedRank (fun _ _ : Fin 0 => False) = 0 :=
  (PaperX.SeedConsequences.rank_zero_iff _).2 inferInstance

end PaperX.SeedExamples
