import PaperX.SpineExistenceCriterion
import PaperX.RequiredPacketBoundary

set_option autoImplicit false
noncomputable section
open PaperX.SpectralProjectors PaperX.JointOccupancy
open PaperX.RequiredPacketOccupancy PaperX.OccupancyExamples

-- Empty conditions occupy exactly a nonzero carrier, not the zero space.
example : ¬ PositiveTrace (fun _ : Unit => diagOp (fun _ : Fin 0 => (1 : ℚ)))
    (fun _ => (1 : ℚ)) [] := by
  rw [← occupied_iff_positiveTrace _ _ (fun _ => diag_split _)
    (fun _ _ => diag_commute _ _) []]
  rintro ⟨x, hx, _⟩
  exact hx (Subsingleton.elim _ _)

example : PositiveTrace (fun _ : Unit => diagOp (fun _ : Fin 1 => (1 : ℚ)))
    (fun _ => (1 : ℚ)) [] := by
  apply (occupied_iff_positiveTrace _ _ (fun _ => diag_split _)
    (fun _ _ => diag_commute _ _) []).mp
  refine ⟨fun _ => 1, ?_, ?_⟩
  · intro h
    have hh := congrFun h 0
    norm_num at hh
  · simp

-- Characteristic zero is essential for the positive-natural-preimage convention.
-- Even the zero projector has positive natural preimage 2 in F_2.
example : PositiveTrace (fun _ : Unit => diagOp (fun _ : Fin 0 => (1 : ZMod 2)))
    (fun _ => (1 : ZMod 2)) [] := by
  refine ⟨2, by decide, ?_⟩
  norm_num [joint_nil, LinearMap.trace_one]

-- An empty required index has a valid empty family, without nonzero vectors.
example : ∃ x : (p : Empty) → (Fin 0 → ℚ), ∀ p,
    x p ≠ 0 ∧ ∀ i ∈ ([] : List Unit),
      diagOp (fun _ : Fin 0 => (1 : ℚ)) (x p) = (1 : ℚ) • x p := by
  exact (all_packets_iff_witnesses (fun _ : Empty => ℚ)
    (fun _ : Empty => Fin 0 → ℚ) (fun _ : Empty => Unit)
    (fun _ _ => diagOp (fun _ : Fin 0 => (1 : ℚ)))
    (fun _ _ => (1 : ℚ)) (fun _ => [])).mp (by intro p; exact Empty.elim p)

-- Required packets may have different actual carriers and unbounded dimension.
example : ∀ p : ℕ, PositiveTrace
    (fun _ : Unit => diagOp (fun _ : Fin (p+1) => (1 : ℚ)))
    (fun _ => (1 : ℚ)) [()] := by
  intro p
  apply (occupied_iff_positiveTrace _ _ (fun _ => diag_split _)
    (fun _ _ => diag_commute _ _) [()]).mp
  refine ⟨fun _ => 1, ?_, ?_⟩
  · intro h
    have hh := congrFun h ⟨0, Nat.zero_lt_succ p⟩
    norm_num at hh
  · intro i hi
    ext j
    simp [diag_apply]

-- The omitted packet may be the first one, including the empty-prefix case.
example : ¬ Occupied PaperX.RequiredPacketBoundary.operator
    (PaperX.RequiredPacketBoundary.target 0 0) [()] :=
  PaperX.RequiredPacketBoundary.omitted_packet_empty 0

-- In contrast, all finite prefixes of one fixed family do imply pointwise occupancy.
example (h : ∀ N, ∀ n < N, Occupied PaperX.RequiredPacketBoundary.operator
    (PaperX.RequiredPacketBoundary.target 1 n) [()]) :
    ∀ n, Occupied PaperX.RequiredPacketBoundary.operator
      (PaperX.RequiredPacketBoundary.target 1 n) [()] := by
  intro n
  exact h (n+1) n (Nat.lt_succ_self n)

#check PaperX.SpineExistenceCriterion.full_existence_boundary
