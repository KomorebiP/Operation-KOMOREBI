import PaperX.OccupancyExamples

/-! The required-packet quantifier cannot be replaced by occupancy of one
packet or by a fixed finite sample. These are actual one-dimensional packets
over ℚ, with a split identity operator and its polynomial spectral projector.
For each omitted index N a different family is constructed. This does not
claim that one family can satisfy every finite prefix and fail globally. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.RequiredPacketBoundary

open PaperX.SpectralProjectors PaperX.JointOccupancy PaperX.OccupancyExamples

/-- Every packet has the same actual one-dimensional carrier and operator. -/
def operator (_ : Unit) : Module.End ℚ (Fin 1 → ℚ) :=
  diagOp (fun _ => 1)

/-- Exactly the N-th packet asks for the absent zero eigenvalue. -/
def target (N n : ℕ) (_ : Unit) : ℚ := if n = N then 0 else 1

theorem operator_split (i : Unit) : Split (operator i) :=
  diag_split _

theorem operators_commute (i j : Unit) : Commute (operator i) (operator j) :=
  diag_commute _ _

/-- The projector is computed from the spectral polynomial, not assigned. -/
theorem projector (N n : ℕ) :
    joint operator (target N n) [()] =
      diagOp (fun _ : Fin 1 => if n = N then (0 : ℚ) else 1) := by
  simp only [joint_cons, joint_nil, mul_one, operator, spectral_diag]
  congr 1
  funext j
  by_cases h : n = N <;> simp [target, h]

theorem projector_trace (N n : ℕ) :
    LinearMap.trace ℚ (Fin 1 → ℚ) (joint operator (target N n) [()]) =
      if n = N then 0 else 1 := by
  rw [projector, trace_diag]
  simp

theorem occupied_iff (N n : ℕ) :
    Occupied operator (target N n) [()] ↔ n ≠ N := by
  rw [occupied_iff_trace_ne_zero operator (target N n) operator_split
    operators_commute, projector_trace]
  by_cases h : n = N <;> simp [h]

theorem omitted_packet_empty (N : ℕ) :
    ¬ Occupied operator (target N N) [()] := by
  simp [occupied_iff]

theorem prefix_occupied (N n : ℕ) (hn : n < N) :
    Occupied operator (target N n) [()] :=
  (occupied_iff N n).mpr (Nat.ne_of_lt hn)

theorem no_family_fully_occupied (N : ℕ) :
    ¬ ∀ n, Occupied operator (target N n) [()] := by
  intro h
  exact omitted_packet_empty N (h N)

/-- One occupied required packet does not imply occupancy of every packet. -/
theorem some_but_not_all :
    (∃ n, Occupied operator (target 1 n) [()]) ∧
      ¬ ∀ n, Occupied operator (target 1 n) [()] := by
  exact ⟨⟨0, prefix_occupied 1 0 (by decide)⟩, no_family_fully_occupied 1⟩

/-- For every prefix length there is a family passing it and failing next. -/
theorem finite_prefix_misses_failure (N : ℕ) :
    (∀ n < N, Occupied operator (target N n) [()]) ∧
      ¬ Occupied operator (target N N) [()] :=
  ⟨prefix_occupied N, omitted_packet_empty N⟩

/-- An arbitrary predetermined finite sample can miss an empty packet. -/
theorem finite_sample_misses_failure (s : Finset ℕ) :
    ∃ N, (∀ n ∈ s, Occupied operator (target N n) [()]) ∧
      ¬ Occupied operator (target N N) [()] := by
  refine ⟨s.sup id + 1, ?_, omitted_packet_empty _⟩
  intro n hn
  apply prefix_occupied
  exact Nat.lt_succ_of_le (Finset.le_sup (f := id) hn)

end PaperX.RequiredPacketBoundary
