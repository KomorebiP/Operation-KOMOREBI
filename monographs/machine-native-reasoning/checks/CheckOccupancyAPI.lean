import MachineTheory.OccupancyExamples

open Komorebi.MachineTheory
open Komorebi.MachineTheory.PartitionCorrection
open Komorebi.MachineTheory.PartitionCorrection.Examples

noncomputable section

-- The target and cell ambient types are arbitrary. Only the world type is finite.
variable {Ω I Y : Type*} [Fintype Ω]

example (c : Ω → I) (t : Ω → Y) (hc : Function.Surjective c) :
    Fintype.card ((algebra c).Memory t) = 2 ^ Fintype.card (Pair c t) :=
  (partition_correction_memory c t hc).1

-- Actual correction signatures for exactly the preimages of cell subsets.
example (c : Ω → I) (t : Ω → Y) (hc : Function.Surjective c) :
    ∀ V W, (algebra c).signature t V = (algebra c).signature t W ↔
      occupancy c t V = occupancy c t W :=
  (partition_correction_memory c t hc).2.1

example (c : Ω → I) (t : Ω → Y) :
    (algebra c).Memory t ≃ Set (Pair c t) := memoryEquiv c t

example (c : Ω → I) (t : Ω → Y) (S : Set (Pair c t)) :
    occupancy c t (pair c t ⁻¹' S) = S := occupancy_realize c t S

example (c : Ω → I) (t : Ω → Y) (events : List (algebra c).Event) (V : Set Ω) :
    readBits c t (run (updateBits c t) events (encode c t V)) =
      t '' (run (algebra c).filter events V) :=
  bits_readout_continuation c t events V

-- A user supplies raw readout and update laws; no minimality certificate is assumed.
example (c : Ω → I) (t : Ω → Y) (b : Nat)
    (remember : Set Ω → (Fin b → Bool)) (readout : (Fin b → Bool) → Set Y)
    (step : (algebra c).Event → (Fin b → Bool) → (Fin b → Bool))
    (hq : ∀ V, readout (remember V) = t '' V)
    (hs : ∀ e V, step e (remember V) = remember ((algebra c).filter e V)) :
    Fintype.card (Pair c t) ≤ b :=
  fixed_bits_necessary c t b remember readout step hq hs

example : Fintype.card SensorWorld = 8 := sensor_world_count
example : Fintype.card ((algebra sensorCell).Memory sensorTarget) = 16 :=
  sensor_signature_count
example : Fintype.card ((algebra emptyCell).Memory emptyTarget) = 1 :=
  empty_signature_count

#check sensor_no_three_bit_memory
#check contradictory_filter
#check contradictory_binary_readout
#check current_target_set_does_not_determine_correction
#check constant_singletons_same_occupancy
#check splitting_cell_changes_signature
#check singleton_event_not_old_admitted
#check separate_singletons_different_occupancy
#check missing_cells_merges_signatures
#check multi_target_signature_count
#check no_unattained_pair

end
