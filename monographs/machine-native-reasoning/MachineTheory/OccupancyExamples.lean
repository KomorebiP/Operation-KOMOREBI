import MachineTheory.OccupancyBinary

/-!
# Partition memory examples and boundaries

These examples preserve empty candidates, unused target values, target values
shared by distinct cells, and cells containing several target values. The
four-cell/eight-world example uses exactly the source variables (b,s,nuisance).
-/
namespace Komorebi.MachineTheory.PartitionCorrection.Examples

noncomputable section

abbrev SensorWorld := Bool × Bool × Bool

def sensorCell (w : SensorWorld) : Bool × Bool := (w.1, w.2.1)
def sensorTarget (w : SensorWorld) : Bool := w.1

theorem sensorCell_surjective : Function.Surjective sensorCell := by
  intro p
  exact ⟨(p.1, p.2, false), rfl⟩

def sensorPairEquiv : Pair sensorCell sensorTarget ≃ (Bool × Bool) where
  toFun d := d.val.1
  invFun p := pair sensorCell sensorTarget (p.1, p.2, false)
  left_inv d := by
    apply Subtype.ext
    change ((d.val.1.1, d.val.1.2), d.val.1.1) = d.val
    obtain ⟨w, hw⟩ := d.property
    rw [← hw]
    rfl
  right_inv _ := rfl

theorem sensor_pair_count : Fintype.card (Pair sensorCell sensorTarget) = 4 := by
  rw [Fintype.card_congr sensorPairEquiv]
  decide

theorem sensor_world_count : Fintype.card SensorWorld = 8 := by decide

theorem sensor_signature_count :
    Fintype.card ((algebra sensorCell).Memory sensorTarget) = 16 := by
  rw [card_memory, sensor_pair_count]
  decide

theorem sensor_no_three_bit_memory :
    ¬ ∃ (r : Set SensorWorld → (Fin 3 → Bool))
      (q : (Fin 3 → Bool) → Set Bool)
      (step : (algebra sensorCell).Event → (Fin 3 → Bool) → (Fin 3 → Bool)),
      (∀ V, q (r V) = sensorTarget '' V) ∧
      (∀ e V, step e (r V) = r ((algebra sensorCell).filter e V)) := by
  rintro ⟨r, q, step, hq, hs⟩
  have h := fixed_bits_necessary sensorCell sensorTarget 3 r q step hq hs
  rw [sensor_pair_count] at h
  exact (by decide : ¬ 4 ≤ 3) h

def sensorV : Set SensorWorld := {(false, false, false), (true, true, false)}
def sensorW : Set SensorWorld := {(false, true, false), (true, false, false)}
def calibrationCells : Set (Bool × Bool) := {p | p.2 = false}

theorem sensor_present_targets_equal : sensorTarget '' sensorV = sensorTarget '' sensorW := by
  simp [sensorV, sensorW, sensorTarget]

theorem sensor_filter_V : sensorV ∩ sensorCell ⁻¹' calibrationCells =
    {(false, false, false)} := by
  ext w
  rcases w with ⟨b, s, n⟩
  cases b <;> cases s <;> cases n <;> simp [sensorV, sensorCell, calibrationCells]

theorem sensor_filter_W : sensorW ∩ sensorCell ⁻¹' calibrationCells =
    {(true, false, false)} := by
  ext w
  rcases w with ⟨b, s, n⟩
  cases b <;> cases s <;> cases n <;> simp [sensorW, sensorCell, calibrationCells]

theorem sensor_signatures_ne :
    (algebra sensorCell).signature sensorTarget sensorV ≠
      (algebra sensorCell).signature sensorTarget sensorW := by
  intro h
  have he := congrFun h (event sensorCell calibrationCells)
  change sensorTarget '' (sensorV ∩ sensorCell ⁻¹' calibrationCells) =
    sensorTarget '' (sensorW ∩ sensorCell ⁻¹' calibrationCells) at he
  rw [sensor_filter_V, sensor_filter_W] at he
  have ht := congrArg (fun S : Set Bool => false ∈ S) he
  simp [sensorTarget] at ht

theorem current_target_set_does_not_determine_correction :
    ¬ ∀ V W : Set SensorWorld, sensorTarget '' V = sensorTarget '' W →
      (algebra sensorCell).signature sensorTarget V =
        (algebra sensorCell).signature sensorTarget W := by
  intro h
  exact sensor_signatures_ne (h sensorV sensorW sensor_present_targets_equal)

@[simp] theorem empty_occupancy {Ω I Y : Type*} (c : Ω → I) (t : Ω → Y) :
    occupancy c t ∅ = ∅ := by simp [occupancy]

/-- An impossible admitted event produces the contradictory candidate state. -/
theorem contradictory_filter {Ω I : Type*} (c : Ω → I) (V : Set Ω) :
    (algebra c).filter (event c ∅) V = ∅ := by
  simp [EvidenceAlgebra.filter, event]

/-- The binary readout retains contradiction, rather than choosing a target. -/
theorem contradictory_binary_readout {Ω I Y : Type*} [Fintype Ω]
    (c : Ω → I) (t : Ω → Y) (V : Set Ω) :
    readBits c t (updateBits c t (event c ∅) (encode c t V)) = ∅ := by
  rw [encode_update, encode_read, contradictory_filter]
  exact Set.image_empty t

def emptyCell : Empty → Empty := Empty.elim
def emptyTarget : Empty → Nat := Empty.elim

theorem empty_pair_count : Fintype.card (Pair emptyCell emptyTarget) = 0 := by
  let : IsEmpty (Pair emptyCell emptyTarget) := ⟨fun d => by
    obtain ⟨w, _⟩ := d.property
    exact Empty.elim w⟩
  simp

theorem empty_signature_count :
    Fintype.card ((algebra emptyCell).Memory emptyTarget) = 1 := by
  rw [card_memory, empty_pair_count]
  decide

def oneCell (_ : Bool) : Unit := ()
def constantTarget (_ : Bool) : Bool := false

def constantPairEquiv : Pair oneCell constantTarget ≃ Unit where
  toFun _ := ()
  invFun _ := pair oneCell constantTarget false
  left_inv d := by
    apply Subtype.ext
    obtain ⟨w, hw⟩ := d.property
    rw [← hw]
    rfl
  right_inv p := by cases p; rfl

theorem one_cell_pair_count : Fintype.card (Pair oneCell constantTarget) = 1 := by
  rw [Fintype.card_congr constantPairEquiv]
  decide

theorem one_cell_signature_count :
    Fintype.card ((algebra oneCell).Memory constantTarget) = 2 := by
  rw [card_memory, one_cell_pair_count]
  decide

theorem constant_singletons_same_occupancy :
    occupancy oneCell constantTarget {false} = occupancy oneCell constantTarget {true} := by
  simp [occupancy, pair, record, oneCell, constantTarget]

def splitAlgebra : EvidenceAlgebra Bool where
  events := Set.univ
  univ_mem := Set.mem_univ _
  inter_mem := by intros; trivial

def splitEvent : splitAlgebra.Event := ⟨{false}, Set.mem_univ _⟩

theorem splitting_cell_changes_signature :
    splitAlgebra.signature constantTarget {false} ≠
      splitAlgebra.signature constantTarget {true} := by
  intro h
  have ht := congrArg (fun S : Set Bool => false ∈ S) (congrFun h splitEvent)
  simp [EvidenceAlgebra.signature, splitEvent, constantTarget] at ht

theorem singleton_event_not_old_admitted : ({false} : Set Bool) ∉ (algebra oneCell).events := by
  rintro ⟨J, hJ⟩
  change oneCell ⁻¹' J = {false} at hJ
  have hf : oneCell false ∈ J := by
    change false ∈ oneCell ⁻¹' J
    rw [hJ]
    exact Set.mem_singleton false
  have ht : true ∈ oneCell ⁻¹' J := hf
  rw [hJ] at ht
  simp at ht

def separateCells : Bool → Bool := id

theorem separate_singletons_different_occupancy :
    occupancy separateCells constantTarget {false} ≠
      occupancy separateCells constantTarget {true} := by
  intro h
  have hm : pair separateCells constantTarget false ∈
      occupancy separateCells constantTarget {false} := ⟨false, Set.mem_singleton _, rfl⟩
  rw [h] at hm
  obtain ⟨w, hw, hp⟩ := hm
  have hw' : w = true := hw
  subst w
  have hb := congrArg (fun d : Pair separateCells constantTarget => d.val.1) hp
  change true = false at hb
  cases hb

theorem missing_cells_merges_signatures :
    (algebra oneCell).signature constantTarget {false} =
      (algebra oneCell).signature constantTarget {true} :=
  (signature_eq_iff_occupancy_eq oneCell constantTarget _ _).mpr
    constant_singletons_same_occupancy

def multiCell (w : Bool × Bool) : Bool := w.1
def multiTarget (w : Bool × Bool) : Bool := w.2

def multiPairEquiv : Pair multiCell multiTarget ≃ (Bool × Bool) where
  toFun d := d.val
  invFun p := pair multiCell multiTarget p
  left_inv _ := Subtype.ext rfl
  right_inv _ := rfl

theorem multi_target_pair_count : Fintype.card (Pair multiCell multiTarget) = 4 := by
  rw [Fintype.card_congr multiPairEquiv]
  decide

theorem multi_target_signature_count :
    Fintype.card ((algebra multiCell).Memory multiTarget) = 16 := by
  rw [card_memory, multi_target_pair_count]
  decide

def natTarget (b : Bool) : Nat := if b then 1 else 0

theorem target_two_unattained : 2 ∉ Set.range natTarget := by
  rintro ⟨b, hb⟩
  cases b <;> simp [natTarget] at hb

theorem no_unattained_pair (d : Pair oneCell natTarget) : d.val.2 ≠ 2 := by
  have ht : d.val.2 ∈ Set.range natTarget := by
    obtain ⟨b, hb⟩ := d.property
    exact ⟨b, congrArg Prod.snd hb⟩
  intro h
  rw [h] at ht
  exact target_two_unattained ht

end
end Komorebi.MachineTheory.PartitionCorrection.Examples
