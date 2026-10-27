import MachineTheory.Correction
import Mathlib.Data.Fintype.Pi

/-!
# Partition correction memory

Reviewed Core v0.2, Corollary 3.2. The evidence events are exactly preimages
of cell subsets. Target values need not all be attained, and the target type
need not be finite. Empty candidate sets are retained. The counting and bit
claims concern all candidate subsets and fixed-width binary states only.
-/

namespace Komorebi.MachineTheory.PartitionCorrection

variable {Ω I Y : Type*}

/-- Exactly the unions of cells of the cell map. -/
def algebra (c : Ω → I) : EvidenceAlgebra Ω where
  events := Set.range (fun J : Set I => c ⁻¹' J)
  univ_mem := ⟨Set.univ, Set.preimage_univ⟩
  inter_mem := by
    rintro E ⟨J, rfl⟩ F ⟨K, rfl⟩
    exact ⟨J ∩ K, rfl⟩

/-- A specified union of cells is an admitted evidence event. -/
def event (c : Ω → I) (J : Set I) : (algebra c).Event :=
  ⟨c ⁻¹' J, ⟨J, rfl⟩⟩

theorem event_membership_iff (c : Ω → I) (E : Set Ω) :
    E ∈ (algebra c).events ↔ ∃ J : Set I, c ⁻¹' J = E := Iff.rfl

/-- The attained cell-target pairs, excluding unoccupied ambient pairs. -/
abbrev Pair (c : Ω → I) (t : Ω → Y) := Attained (fun ω => (c ω, t ω))

def pair (c : Ω → I) (t : Ω → Y) (ω : Ω) : Pair c t :=
  record (fun x => (c x, t x)) ω

theorem pair_surjective (c : Ω → I) (t : Ω → Y) :
    Function.Surjective (pair c t) := by
  intro d
  obtain ⟨ω, hω⟩ := d.property
  exact ⟨ω, Subtype.ext hω⟩

/-- Occupancy records the attained pairs met by the candidate set. -/
def occupancy (c : Ω → I) (t : Ω → Y) (V : Set Ω) : Set (Pair c t) :=
  pair c t '' V

theorem mem_occupancy_iff (c : Ω → I) (t : Ω → Y)
    (V : Set Ω) (d : Pair c t) :
    d ∈ occupancy c t V ↔
      ∃ ω ∈ V, c ω = d.val.1 ∧ t ω = d.val.2 := by
  constructor
  · rintro ⟨ω, hω, he⟩
    have hpair : (c ω, t ω) = d.val := congrArg Subtype.val he
    exact ⟨ω, hω, congrArg Prod.fst hpair, congrArg Prod.snd hpair⟩
  · rintro ⟨ω, hω, hc, ht⟩
    exact ⟨ω, hω, Subtype.ext (Prod.ext hc ht)⟩

/-- The single-cell signature coordinate recovers each occupancy bit. -/
theorem mem_occupancy_iff_single_cell (c : Ω → I) (t : Ω → Y)
    (V : Set Ω) (d : Pair c t) :
    d ∈ occupancy c t V ↔
      d.val.2 ∈ (algebra c).signature t V (event c {d.val.1}) := by
  rw [mem_occupancy_iff]
  constructor
  · rintro ⟨ω, hω, hc, ht⟩
    exact ⟨ω, ⟨hω, hc⟩, ht⟩
  · rintro ⟨ω, ⟨hω, hc⟩, ht⟩
    exact ⟨ω, hω, hc, ht⟩

/-- All correction signatures and occupancy records identify the same subsets. -/
theorem signature_eq_iff_occupancy_eq (c : Ω → I) (t : Ω → Y)
    (V W : Set Ω) :
    (algebra c).signature t V = (algebra c).signature t W ↔
      occupancy c t V = occupancy c t W := by
  constructor
  · intro h
    ext d
    rw [mem_occupancy_iff_single_cell, mem_occupancy_iff_single_cell, h]
  · intro h
    funext e
    obtain ⟨J, hJ⟩ := e.property
    apply Set.ext
    intro y
    change y ∈ t '' (V ∩ e.val) ↔ y ∈ t '' (W ∩ e.val)
    rw [← hJ]
    constructor
    · rintro ⟨ω, ⟨hω, hcell⟩, ht⟩
      have ho : pair c t ω ∈ occupancy c t W := by
        rw [← h]
        exact ⟨ω, hω, rfl⟩
      obtain ⟨ω', hω', hc', ht'⟩ := (mem_occupancy_iff c t W _).mp ho
      refine ⟨ω', ⟨hω', ?_⟩, ht'.trans ht⟩
      change c ω' ∈ J
      change c ω' = c ω at hc'
      rw [hc']
      exact hcell
    · rintro ⟨ω, ⟨hω, hcell⟩, ht⟩
      have ho : pair c t ω ∈ occupancy c t V := by
        rw [h]
        exact ⟨ω, hω, rfl⟩
      obtain ⟨ω', hω', hc', ht'⟩ := (mem_occupancy_iff c t V _).mp ho
      refine ⟨ω', ⟨hω', ?_⟩, ht'.trans ht⟩
      change c ω' ∈ J
      change c ω' = c ω at hc'
      rw [hc']
      exact hcell

/-- A realization uses the full pair-fibre preimage, with no choices of worlds. -/
def realize (c : Ω → I) (t : Ω → Y) (S : Set (Pair c t)) : Set Ω :=
  pair c t ⁻¹' S

@[simp] theorem occupancy_realize (c : Ω → I) (t : Ω → Y)
    (S : Set (Pair c t)) : occupancy c t (realize c t S) = S := by
  exact Set.image_preimage_eq S (pair_surjective c t)

theorem occupancy_surjective (c : Ω → I) (t : Ω → Y) :
    Function.Surjective (occupancy c t) :=
  fun S => ⟨realize c t S, occupancy_realize c t S⟩

def fromOccupancy (c : Ω → I) (t : Ω → Y) (S : Set (Pair c t)) :
    (algebra c).Memory t := (algebra c).remember t (realize c t S)

theorem fromOccupancy_bijective (c : Ω → I) (t : Ω → Y) :
    Function.Bijective (fromOccupancy c t) := by
  constructor
  · intro S T h
    have hs : (algebra c).signature t (realize c t S) =
        (algebra c).signature t (realize c t T) := congrArg Subtype.val h
    have ho := (signature_eq_iff_occupancy_eq c t _ _).mp hs
    simpa only [occupancy_realize] using ho
  · intro m
    obtain ⟨V, hV⟩ := m.property
    refine ⟨occupancy c t V, ?_⟩
    apply Subtype.ext
    change (algebra c).signature t (realize c t (occupancy c t V)) = m.val
    rw [← hV]
    apply (signature_eq_iff_occupancy_eq c t _ _).mpr
    exact occupancy_realize c t _

/-- Actual equivalence, not only matching cardinal inequalities. -/
noncomputable def memoryEquiv (c : Ω → I) (t : Ω → Y) :
    (algebra c).Memory t ≃ Set (Pair c t) :=
  (Equiv.ofBijective (fromOccupancy c t) (fromOccupancy_bijective c t)).symm

@[simp] theorem memoryEquiv_fromOccupancy (c : Ω → I) (t : Ω → Y)
    (S : Set (Pair c t)) : memoryEquiv c t (fromOccupancy c t S) = S :=
  (Equiv.ofBijective (fromOccupancy c t) (fromOccupancy_bijective c t)).left_inv S

@[simp] theorem fromOccupancy_occupancy (c : Ω → I) (t : Ω → Y)
    (V : Set Ω) : fromOccupancy c t (occupancy c t V) = (algebra c).remember t V := by
  apply Subtype.ext
  exact (signature_eq_iff_occupancy_eq c t _ _).mpr (occupancy_realize c t _)

@[simp] theorem memoryEquiv_remember (c : Ω → I) (t : Ω → Y) (V : Set Ω) :
    memoryEquiv c t ((algebra c).remember t V) = occupancy c t V := by
  rw [← fromOccupancy_occupancy, memoryEquiv_fromOccupancy]

theorem card_memory [Fintype Ω] (c : Ω → I) (t : Ω → Y) :
    Fintype.card ((algebra c).Memory t) = 2 ^ Fintype.card (Pair c t) := by
  classical
  rw [Fintype.card_congr (memoryEquiv c t), Fintype.card_set]

/-- Read the occupied target values, without forgetting cell associations in state. -/
def readOccupancy (c : Ω → I) (t : Ω → Y) (S : Set (Pair c t)) : Set Y :=
  (fun d => d.val.2) '' S

@[simp] theorem readOccupancy_occupancy (c : Ω → I) (t : Ω → Y) (V : Set Ω) :
    readOccupancy c t (occupancy c t V) = t '' V := by
  unfold readOccupancy occupancy
  rw [Set.image_image]
  rfl

/-- Evidence restricts the existing occupancy vector by its cell coordinate. -/
def restrictOccupancy (c : Ω → I) (t : Ω → Y) (J : Set I)
    (S : Set (Pair c t)) : Set (Pair c t) := S ∩ {d | d.val.1 ∈ J}

theorem occupancy_inter_cells (c : Ω → I) (t : Ω → Y) (V : Set Ω) (J : Set I) :
    occupancy c t (V ∩ c ⁻¹' J) = restrictOccupancy c t J (occupancy c t V) := by
  ext d
  constructor
  · intro h
    obtain ⟨ω, ⟨hV, hJ⟩, hc, ht⟩ := (mem_occupancy_iff c t _ d).mp h
    refine ⟨(mem_occupancy_iff c t V d).mpr ⟨ω, hV, hc, ht⟩, ?_⟩
    change d.val.1 ∈ J
    rw [← hc]
    exact hJ
  · rintro ⟨h, hJ⟩
    obtain ⟨ω, hV, hc, ht⟩ := (mem_occupancy_iff c t V d).mp h
    apply (mem_occupancy_iff c t _ d).mpr
    refine ⟨ω, ⟨hV, ?_⟩, hc, ht⟩
    change c ω ∈ J
    rw [hc]
    exact hJ

/-- Every admitted event comes with an actual cell-subset representation. -/
noncomputable def eventCells (c : Ω → I) (e : (algebra c).Event) : Set I :=
  Classical.choose e.property

theorem eventCells_preimage (c : Ω → I) (e : (algebra c).Event) :
    c ⁻¹' eventCells c e = e.val := Classical.choose_spec e.property

theorem occupancy_filter (c : Ω → I) (t : Ω → Y)
    (e : (algebra c).Event) (V : Set Ω) :
    occupancy c t ((algebra c).filter e V) =
      restrictOccupancy c t (eventCells c e) (occupancy c t V) := by
  change occupancy c t (V ∩ e.val) = _
  rw [← eventCells_preimage c e]
  exact occupancy_inter_cells c t V _

/-- Source-facing partition condition. Surjectivity makes each named cell nonempty. -/
theorem nonempty_cells_iff_surjective (c : Ω → I) :
    (∀ i, (c ⁻¹' ({i} : Set I)).Nonempty) ↔ Function.Surjective c := by
  constructor
  · intro h i
    obtain ⟨ω, hω⟩ := h i
    exact ⟨ω, hω⟩
  · intro h i
    obtain ⟨ω, hω⟩ := h i
    exact ⟨ω, hω⟩

end Komorebi.MachineTheory.PartitionCorrection
