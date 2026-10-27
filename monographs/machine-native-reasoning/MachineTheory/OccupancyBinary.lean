import MachineTheory.PartitionOccupancy
import Mathlib.Data.Fintype.BigOperators

/-!
# Exact fixed-width binary occupancy memory

The state is a Boolean vector indexed by exactly the attained cell-target pairs.
Readout projects occupied pairs to targets. Evidence update masks cell coordinates.
The lower bound is for exact deterministic memory on all candidate subsets, with
fixed-width binary states. No variable-length, average-bit or runtime bound is claimed.
-/

namespace Komorebi.MachineTheory.PartitionCorrection

variable {Ω I Y : Type*} [Fintype Ω]

/-- Characteristic vectors of occupancy subsets, using one bit per attained pair. -/
noncomputable def bitsEquiv (c : Ω → I) (t : Ω → Y) :
    Set (Pair c t) ≃ (Fin (Fintype.card (Pair c t)) → Bool) := by
  classical
  let e := Fintype.equivFin (Pair c t)
  refine
    { toFun := fun S i => decide (e.symm i ∈ S)
      invFun := fun b => {d | b (e d) = true}
      left_inv := ?_
      right_inv := ?_ }
  · intro S
    ext d
    simp only [Set.mem_ofPred_eq, Equiv.symm_apply_apply, decide_eq_true_eq]
  · intro b
    funext i
    simp only [Set.mem_ofPred_eq, Equiv.apply_symm_apply]
    cases b i <;> rfl

/-- The attained signature state is equivalent to the complete r-bit state space. -/
noncomputable def binaryMemoryEquiv (c : Ω → I) (t : Ω → Y) :
    (algebra c).Memory t ≃ (Fin (Fintype.card (Pair c t)) → Bool) :=
  (memoryEquiv c t).trans (bitsEquiv c t)

noncomputable def encode (c : Ω → I) (t : Ω → Y) (V : Set Ω) :
    Fin (Fintype.card (Pair c t)) → Bool := bitsEquiv c t (occupancy c t V)

noncomputable def readBits (c : Ω → I) (t : Ω → Y)
    (b : Fin (Fintype.card (Pair c t)) → Bool) : Set Y :=
  readOccupancy c t ((bitsEquiv c t).symm b)

noncomputable def updateBits (c : Ω → I) (t : Ω → Y)
    (e : (algebra c).Event) (b : Fin (Fintype.card (Pair c t)) → Bool) :
    Fin (Fintype.card (Pair c t)) → Bool :=
  bitsEquiv c t (restrictOccupancy c t (eventCells c e) ((bitsEquiv c t).symm b))

@[simp] theorem encode_read (c : Ω → I) (t : Ω → Y) (V : Set Ω) :
    readBits c t (encode c t V) = t '' V := by
  unfold readBits encode
  rw [Equiv.symm_apply_apply, readOccupancy_occupancy]

@[simp] theorem encode_update (c : Ω → I) (t : Ω → Y)
    (e : (algebra c).Event) (V : Set Ω) :
    updateBits c t e (encode c t V) = encode c t ((algebra c).filter e V) := by
  unfold updateBits encode
  rw [Equiv.symm_apply_apply, occupancy_filter]

theorem encode_surjective (c : Ω → I) (t : Ω → Y) :
    Function.Surjective (encode c t) := by
  intro b
  refine ⟨realize c t ((bitsEquiv c t).symm b), ?_⟩
  unfold encode
  rw [occupancy_realize, Equiv.apply_symm_apply]

theorem bits_finite_continuation (c : Ω → I) (t : Ω → Y)
    (events : List (algebra c).Event) (V : Set Ω) :
    run (updateBits c t) events (encode c t V) =
      encode c t (run (algebra c).filter events V) := by
  induction events generalizing V with
  | nil => rfl
  | cons e es ih =>
    simp only [run_cons, encode_update]
    exact ih _

theorem bits_readout_continuation (c : Ω → I) (t : Ω → Y)
    (events : List (algebra c).Event) (V : Set Ω) :
    readBits c t (run (updateBits c t) events (encode c t V)) =
      t '' (run (algebra c).filter events V) := by
  rw [bits_finite_continuation, encode_read]

omit [Fintype Ω] in
/-- An exact b-bit memory cannot merge distinct occupancy subsets. -/
theorem exact_bits_occupancy_injective (c : Ω → I) (t : Ω → Y) (b : ℕ)
    (r : Set Ω → (Fin b → Bool)) (readout : (Fin b → Bool) → Set Y)
    (step : (algebra c).Event → (Fin b → Bool) → (Fin b → Bool))
    (hq : ∀ V, readout (r V) = t '' V)
    (hs : ∀ e V, step e (r V) = r ((algebra c).filter e V)) :
    Function.Injective (fun S : Set (Pair c t) => r (realize c t S)) := by
  intro S T h
  have hsig := (algebra c).any_exact_memory_separates t r readout step hq hs _ _ h
  have hocc := (signature_eq_iff_occupancy_eq c t _ _).mp hsig
  simpa only [occupancy_realize] using hocc

/-- Counting all initialized occupancies gives the exact fixed-width bit bound. -/
theorem fixed_bits_necessary (c : Ω → I) (t : Ω → Y) (b : ℕ)
    (r : Set Ω → (Fin b → Bool)) (readout : (Fin b → Bool) → Set Y)
    (step : (algebra c).Event → (Fin b → Bool) → (Fin b → Bool))
    (hq : ∀ V, readout (r V) = t '' V)
    (hs : ∀ e V, step e (r V) = r ((algebra c).filter e V)) :
    Fintype.card (Pair c t) ≤ b := by
  classical
  have hcard := Fintype.card_le_of_injective _
    (exact_bits_occupancy_injective c t b r readout step hq hs)
  have hpow : 2 ^ Fintype.card (Pair c t) ≤ 2 ^ b := by
    simpa only [Fintype.card_set, Fintype.card_fun, Fintype.card_bool,
      Fintype.card_fin] using hcard
  by_contra h
  have hb : b < Fintype.card (Pair c t) := Nat.lt_of_not_ge h
  exact (not_lt_of_ge hpow) (Nat.pow_lt_pow_right (by decide : 1 < 2) hb)

/-- The raw source partition contract: nonempty cells, exact union evidence,
arbitrary target, all candidate subsets, exact count and an optimal binary memory. -/
theorem partition_correction_memory (c : Ω → I) (t : Ω → Y)
    (_hc : Function.Surjective c) :
    (Fintype.card ((algebra c).Memory t) = 2 ^ Fintype.card (Pair c t)) ∧
    (∀ V W, (algebra c).signature t V = (algebra c).signature t W ↔
      occupancy c t V = occupancy c t W) ∧
    (∀ V, readBits c t (encode c t V) = t '' V) ∧
    (∀ e V, updateBits c t e (encode c t V) = encode c t ((algebra c).filter e V)) ∧
    (∀ b (r : Set Ω → (Fin b → Bool)) (readout : (Fin b → Bool) → Set Y)
      (step : (algebra c).Event → (Fin b → Bool) → (Fin b → Bool)),
      (∀ V, readout (r V) = t '' V) →
      (∀ e V, step e (r V) = r ((algebra c).filter e V)) →
      Fintype.card (Pair c t) ≤ b) := by
  exact ⟨card_memory c t, signature_eq_iff_occupancy_eq c t,
    encode_read c t, encode_update c t, fixed_bits_necessary c t⟩

end Komorebi.MachineTheory.PartitionCorrection
