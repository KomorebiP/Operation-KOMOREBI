import Mathlib.Data.Fintype.Powerset
import AVOC.ParallelSchedule
import AVOC.SchedulingCertificates

namespace Komorebi.AVOC.Scheduling.Examples

abbrev Diamond := Fin 2 × Fin 2

def root : Diamond := (0,0)
def left : Diamond := (0,1)
def right : Diamond := (1,0)
def tip : Diamond := (1,1)

theorem root_ideal : IsIdeal ({root} : Finset Diamond) := by
  unfold IsIdeal root
  decide

theorem diamond_frontier : frontier ({root} : Finset Diamond) = {left,right} := by
  ext x
  rw [mem_frontier]
  revert x
  simp only [Ready, root, left, right, lt_iff_le_not_ge]
  decide

theorem diamond_forward : Legal (∅ : Finset Diamond) [root,left,right,tip] := by
  simp only [Legal, Ready, root, left, right, tip, lt_iff_le_not_ge]
  decide

theorem diamond_swapped : Legal (∅ : Finset Diamond) [root,right,left,tip] := by
  simp only [Legal, Ready, root, left, right, tip, lt_iff_le_not_ge]
  decide

theorem diamond_bad_order : ¬ Legal (∅ : Finset Diamond) [tip,root,left,right] := by
  simp only [Legal, Ready, root, left, right, tip, lt_iff_le_not_ge]
  decide

theorem antichain_not_enough :
    Antichain ({tip} : Finset Diamond) ∧ ¬ Ready (∅ : Finset Diamond) tip := by
  simp only [Antichain, Ready, tip, lt_iff_le_not_ge]
  decide

theorem diamond_width : width (P := Diamond) = 2 := by
  classical
  have hlo : 2 ≤ width (P := Diamond) := by
    have ha : Antichain ({left,right} : Finset Diamond) := by
      unfold Antichain left right
      decide
    have h := antichain_card_le_width ha
    simpa [left,right] using h
  have hhi : width (P := Diamond) ≤ 2 := by
    have ha : ∀ B : Finset Diamond, Antichain B → B.card ≤ 2 := by
      unfold Antichain
      decide
    unfold width
    apply Finset.sup_le
    intro B hB
    exact ha B (Finset.mem_filter.mp hB).2
  omega

theorem three_chain_requires_three_rounds (slot : Fin 3 → Nat)
    (hs : RespectsDependencies slot) (rounds : Nat)
    (hb : ∀ x, slot x < rounds) : 3 ≤ rounds := by
  have hc : Chain (Finset.univ : Finset (Fin 3)) := by
    intro x _ y _
    exact le_total x y
  have h := chain_card_le_rounds hs rounds hb hc
  simpa using h

theorem diamond_frontier_has_two_tasks :
    (frontier ({root} : Finset Diamond)).card = 2 := by
  rw [diamond_frontier]
  simp [left,right]

end Komorebi.AVOC.Scheduling.Examples
