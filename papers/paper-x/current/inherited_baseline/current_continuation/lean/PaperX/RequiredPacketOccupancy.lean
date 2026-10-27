import PaperX.JointOccupancy

/-! The positive trace of a spectral packet means its natural-number rank.
The field-valued trace is its cast, so this interpretation requires no order
on the coefficient field. Every required packet has its own witness. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.RequiredPacketOccupancy

open PaperX.JointOccupancy PaperX.SpectralProjectors

universe u v w x

section OnePacket

variable {K : Type u} [Field K] {V : Type v} [AddCommGroup V] [Module K V]
  [FiniteDimensional K V] {J : Type w}

/-- The nonnegative integer measured by the actual spectral projector trace. -/
def naturalTrace (T : J → Module.End K V) (a : J → K) (indices : List J) : ℕ :=
  Module.finrank K (jointSpace T a indices)

/-- Positivity is the existence of a positive natural-number preimage of the
field trace. It is meaningful over characteristic-zero fields without an order. -/
def PositiveTrace (T : J → Module.End K V) (a : J → K) (indices : List J) : Prop :=
  ∃ n : ℕ, 0 < n ∧ LinearMap.trace K V (joint T a indices) = (n : K)

theorem naturalTrace_cast (T : J → Module.End K V) (a : J → K)
    (hs : ∀ j, Split (T j)) (hc : ∀ i j, Commute (T i) (T j)) (indices : List J) :
    (naturalTrace T a indices : K) = LinearMap.trace K V (joint T a indices) :=
  (trace_eq_dimension T a hs hc indices).symm

theorem naturalTrace_eq_of_cast [CharZero K] (T : J → Module.End K V) (a : J → K)
    (hs : ∀ j, Split (T j)) (hc : ∀ i j, Commute (T i) (T j)) (indices : List J)
    (n : ℕ) (hn : (n : K) = LinearMap.trace K V (joint T a indices)) :
    n = naturalTrace T a indices :=
  Nat.cast_injective (hn.trans (naturalTrace_cast T a hs hc indices).symm)

theorem exists_unique_trace_integer [CharZero K] (T : J → Module.End K V)
    (a : J → K) (hs : ∀ j, Split (T j)) (hc : ∀ i j, Commute (T i) (T j))
    (indices : List J) :
    ∃! n : ℕ, (n : K) = LinearMap.trace K V (joint T a indices) := by
  exact ⟨naturalTrace T a indices, naturalTrace_cast T a hs hc indices,
    fun n hn => naturalTrace_eq_of_cast T a hs hc indices n hn⟩

theorem naturalTrace_pos_iff_occupied (T : J → Module.End K V) (a : J → K)
    (indices : List J) :
    0 < naturalTrace T a indices ↔ Occupied T a indices :=
  (occupied_iff_dimension_pos T a indices).symm

theorem naturalTrace_eq_zero_iff_not_occupied (T : J → Module.End K V) (a : J → K)
    (indices : List J) :
    naturalTrace T a indices = 0 ↔ ¬ Occupied T a indices := by
  rw [← naturalTrace_pos_iff_occupied, Nat.not_lt, Nat.le_zero]

theorem naturalTrace_pos_iff_fieldTrace_ne_zero [CharZero K]
    (T : J → Module.End K V) (a : J → K) (hs : ∀ j, Split (T j))
    (hc : ∀ i j, Commute (T i) (T j)) (indices : List J) :
    0 < naturalTrace T a indices ↔ LinearMap.trace K V (joint T a indices) ≠ 0 :=
  (naturalTrace_pos_iff_occupied T a indices).trans
    (occupied_iff_trace_ne_zero T a hs hc indices)

theorem naturalTrace_eq_zero_iff_fieldTrace_eq_zero [CharZero K]
    (T : J → Module.End K V) (a : J → K) (hs : ∀ j, Split (T j))
    (hc : ∀ i j, Commute (T i) (T j)) (indices : List J) :
    naturalTrace T a indices = 0 ↔ LinearMap.trace K V (joint T a indices) = 0 := by
  rw [← naturalTrace_cast T a hs hc indices, Nat.cast_eq_zero]

theorem positiveTrace_iff_rank_pos [CharZero K]
    (T : J → Module.End K V) (a : J → K) (hs : ∀ j, Split (T j))
    (hc : ∀ i j, Commute (T i) (T j)) (indices : List J) :
    PositiveTrace T a indices ↔ 0 < Module.finrank K (jointSpace T a indices) := by
  constructor
  · rintro ⟨n, hn, ht⟩
    have heq := naturalTrace_eq_of_cast T a hs hc indices n ht.symm
    change 0 < naturalTrace T a indices
    rw [← heq]
    exact hn
  · intro h
    exact ⟨naturalTrace T a indices, h, (naturalTrace_cast T a hs hc indices).symm⟩

theorem occupied_iff_positiveTrace [CharZero K]
    (T : J → Module.End K V) (a : J → K) (hs : ∀ j, Split (T j))
    (hc : ∀ i j, Commute (T i) (T j)) (indices : List J) :
    Occupied T a indices ↔ PositiveTrace T a indices :=
  (occupied_iff_dimension_pos T a indices).trans
    (positiveTrace_iff_rank_pos T a hs hc indices).symm

theorem positiveTrace_iff_fieldTrace_ne_zero [CharZero K]
    (T : J → Module.End K V) (a : J → K) (hs : ∀ j, Split (T j))
    (hc : ∀ i j, Commute (T i) (T j)) (indices : List J) :
    PositiveTrace T a indices ↔ LinearMap.trace K V (joint T a indices) ≠ 0 :=
  (occupied_iff_positiveTrace T a hs hc indices).symm.trans
    (occupied_iff_trace_ne_zero T a hs hc indices)

end OnePacket

section RequiredPackets

variable {P : Type x} (K : P → Type u) (V : P → Type v) (J : P → Type w)
  [∀ p, Field (K p)] [∀ p, AddCommGroup (V p)] [∀ p, Module (K p) (V p)]
  [∀ p, FiniteDimensional (K p) (V p)]
  (T : (p : P) → J p → Module.End (K p) (V p))
  (a : (p : P) → J p → K p) (indices : (p : P) → List (J p))

omit [∀ p, FiniteDimensional (K p) (V p)] in
/-- The index type need not be finite. Choice selects one witness in each of
the supplied carriers, without asserting that any two witnesses coincide. -/
theorem all_packets_iff_witnesses :
    (∀ p, Occupied (T p) (a p) (indices p)) ↔
    ∃ x : (p : P) → V p, ∀ p,
      x p ≠ 0 ∧ ∀ i ∈ indices p, T p i (x p) = a p i • x p := by
  constructor
  · intro h
    exact ⟨fun p => (h p).choose, fun p => (h p).choose_spec⟩
  · rintro ⟨x, hx⟩ p
    exact ⟨x p, hx p⟩

theorem all_positive_iff_occupied :
    (∀ p, 0 < naturalTrace (T p) (a p) (indices p)) ↔
    ∀ p, Occupied (T p) (a p) (indices p) := by
  exact forall_congr' fun p => naturalTrace_pos_iff_occupied (T p) (a p) (indices p)

theorem all_positive_iff_witnesses :
    (∀ p, 0 < naturalTrace (T p) (a p) (indices p)) ↔
    ∃ x : (p : P) → V p, ∀ p,
      x p ≠ 0 ∧ ∀ i ∈ indices p, T p i (x p) = a p i • x p :=
  (all_positive_iff_occupied K V J T a indices).trans
    (all_packets_iff_witnesses K V J T a indices)

variable [∀ p, CharZero (K p)]
  (hs : ∀ p j, Split (T p j)) (hc : ∀ p i j, Commute (T p i) (T p j))

include hs hc

theorem all_positive_iff_fieldTrace_ne_zero :
    (∀ p, 0 < naturalTrace (T p) (a p) (indices p)) ↔
    ∀ p, LinearMap.trace (K p) (V p) (joint (T p) (a p) (indices p)) ≠ 0 := by
  exact forall_congr' fun p =>
    naturalTrace_pos_iff_fieldTrace_ne_zero (T p) (a p) (hs p) (hc p) (indices p)

theorem all_fieldTrace_ne_zero_iff_witnesses :
    (∀ p, LinearMap.trace (K p) (V p) (joint (T p) (a p) (indices p)) ≠ 0) ↔
    ∃ x : (p : P) → V p, ∀ p,
      x p ≠ 0 ∧ ∀ i ∈ indices p, T p i (x p) = a p i • x p :=
  (all_positive_iff_fieldTrace_ne_zero K V J T a indices hs hc).symm.trans
    (all_positive_iff_witnesses K V J T a indices)

theorem all_positiveTrace_iff_occupied :
    (∀ p, PositiveTrace (T p) (a p) (indices p)) ↔
    ∀ p, Occupied (T p) (a p) (indices p) := by
  exact forall_congr' fun p => (occupied_iff_positiveTrace
    (T p) (a p) (hs p) (hc p) (indices p)).symm

theorem all_positiveTrace_iff_witnesses :
    (∀ p, PositiveTrace (T p) (a p) (indices p)) ↔
    ∃ x : (p : P) → V p, ∀ p,
      x p ≠ 0 ∧ ∀ i ∈ indices p, T p i (x p) = a p i • x p :=
  (all_positiveTrace_iff_occupied K V J T a indices hs hc).trans
    (all_packets_iff_witnesses K V J T a indices)

end RequiredPackets

end PaperX.RequiredPacketOccupancy
