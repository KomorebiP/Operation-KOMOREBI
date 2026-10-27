module
public import CertifiedOracle

@[expose] public section
namespace Komorebi.Discovery.CertifiedExamples
open Komorebi.Discovery Komorebi.Discovery.Certified
open Komorebi.Representation Komorebi.Representation.Matrix

abbrev R := ZMod 4
def A : Fin 1 → Mat R 1 1 := ![![![1]]]
def O : Mat R 2 1 := ![![2], ![1]]
def AA := fun a => rowRight (A a)
def valid : List (Evidence R 1) :=
  [.separation ![1], .separation ![2], .combination [1,0], .combination [0,1]]
def answer : List (Test 1 2) := [([],0),([],1)]

theorem good_data_accepts : replaySource A O valid = some answer := by decide +kernel
theorem missing_event_rejects : replaySource A O (valid.take 3) = none := by decide +kernel
theorem trailing_event_rejects :
    replaySource A O (valid ++ [.combination [0,0]]) = none := by decide +kernel

theorem zero_separator_rejects :
    checkMembership AA O [] (![2] : Fin 1 → R) (.separation ![0]) = none := by decide +kernel

theorem wrong_length_rejects :
    checkMembership AA O [] (0 : Fin 1 → R) (.combination [0]) = none := by decide +kernel

theorem nonunit_false_member_rejects :
    checkMembership AA O [([],0)] (![1] : Fin 1 → R) (.combination [2]) = none := by decide +kernel

theorem genuine_nonmembership_accepts :
    checkMembership AA O [([],0)] (![1] : Fin 1 → R) (.separation ![2]) = some false := by decide +kernel

def badProposer : List (Test 1 2) → (Fin 1 → R) → Option (Evidence R 1) :=
  fun _ _ => some (.separation ![0])

theorem always_bad_proposer_still_correct :
    guardedPrimeDiscover 2 2 1 AA O badProposer = some answer := by
  rw [guardedPrimeDiscover_eq_reference]
  exact replaySource_reference 2 2 1 (by decide) A O valid answer good_data_accepts

theorem always_bad_proposer_computed :
    guardedPrimeDiscover 2 2 1 AA O badProposer = some answer := by decide +kernel

def emptyA : Fin 0 → Mat R 0 0 := Fin.elim0
def emptyO : Mat R 0 0 := Fin.elim0

theorem empty_source_accepts :
    replaySource emptyA emptyO [] = some [] := by decide +kernel

theorem empty_source_trailing_rejects :
    replaySource emptyA emptyO [.combination []] = none := by decide +kernel

end Komorebi.Discovery.CertifiedExamples
