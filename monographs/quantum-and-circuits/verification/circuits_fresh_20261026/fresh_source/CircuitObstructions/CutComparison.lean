import CircuitObstructions.Gates

/-!
# Complete discrepancy covers (maintained claim C01)

The endpoint condition is the definition of a restored implementation. It is not
an axiom. Reversibility is derived from the legal gates in `Gates.lean`.
-/
namespace CircuitObstructions

/-- An encoding whose designated target really stores the supplied Boolean bit. -/
structure Boundary (X W : Type) where
  encode : X → Bool → State W
  target : W
  target_eq : ∀ x b, encode x b target = b

theorem Boundary.target_separated {X W : Type} (e : Boundary X W) (x : X) :
    e.encode x false ≠ e.encode x true := by
  intro h
  have hh := congrArg (fun s : State W => s e.target) h
  simp only [e.target_eq, Bool.false_eq_true] at hh

/-- Correctness includes every logical input and both initial target values. -/
def Restores {X W : Type} [DecidableEq W] (e : Boundary X W)
    (c : Circuit W) (f : X → Bool) : Prop :=
  ∀ x b, run c (e.encode x b) = e.encode x (Bool.xor b (f x))

/-- Explicit logical inputs, zero ancillas, and one target. -/
abbrev CanonicalWire (n a : Nat) := Sum (Fin n) (Sum (Fin a) Unit)

def canonicalBoundary (n a : Nat) : Boundary (Fin n → Bool) (CanonicalWire n a) where
  encode x b
    | .inl i => x i
    | .inr (.inl _) => false
    | .inr (.inr _) => b
  target := .inr (.inr ())
  target_eq := by intros; rfl

@[simp] theorem canonical_input (n a : Nat) (x : Fin n → Bool) (b : Bool) (i : Fin n) :
    (canonicalBoundary n a).encode x b (.inl i) = x i := rfl

@[simp] theorem canonical_ancilla (n a : Nat) (x : Fin n → Bool) (b : Bool) (i : Fin a) :
    (canonicalBoundary n a).encode x b (.inr (.inl i)) = false := rfl

@[simp] theorem canonical_target (n a : Nat) (x : Fin n → Bool) (b : Bool) :
    (canonicalBoundary n a).encode x b (.inr (.inr ())) = b := rfl

/-- The inverse suffix meets the forward prefix on the appropriate target branch. -/
theorem inverse_suffix_boundary {X W : Type} [DecidableEq W]
    (e : Boundary X W) (p q : Circuit W) (f : X → Bool)
    (hR : Restores e (p ++ q) f) (x : X) (b : Bool) :
    run q.reverse (e.encode x b) = run p (e.encode x (Bool.xor b (f x))) := by
  have h := hR x (Bool.xor b (f x))
  rw [run_append, xor_cancel_right] at h
  have hh := congrArg (run q.reverse) h
  simpa only [run_reverse_run] using hh.symm

def direction {X W : Type} [DecidableEq W] (e : Boundary X W)
    (p : Circuit W) (x : X) (i : W) : Bool :=
  Bool.xor (run p (e.encode x true) i) (run p (e.encode x false) i)

def packet {X W : Type} [DecidableEq W] (e : Boundary X W)
    (p q : Circuit W) (x : X) (i : W) : Bool :=
  Bool.xor (run p (e.encode x false) i) (run q.reverse (e.encode x false) i)

/-- Distinct initial target bits remain distinguishable after every prefix. -/
theorem direction_nonzero {X W : Type} [DecidableEq W]
    (e : Boundary X W) (p : Circuit W) (x : X) :
    ∃ i, direction e p x i = true := by
  classical
  apply Classical.byContradiction
  intro h
  have heq : run p (e.encode x false) = run p (e.encode x true) := by
    funext i
    have hn : ¬ direction e p x i = true := fun hi => h ⟨i, hi⟩
    unfold direction at hn
    cases ha : run p (e.encode x true) i <;>
      cases hb : run p (e.encode x false) i <;> simp_all
  exact e.target_separated x (run_injective p heq)

/-- Exact pointwise transport identity H_i = f AND D_i. -/
theorem cut_transport_identity {X W : Type} [DecidableEq W]
    (e : Boundary X W) (p q : Circuit W) (f : X → Bool)
    (hR : Restores e (p ++ q) f) (x : X) (i : W) :
    packet e p q x i = (f x && direction e p x i) := by
  unfold packet
  rw [inverse_suffix_boundary e p q f hR x false]
  cases hf : f x <;> simp [direction, xor_commute]

/-- Every discrepancy vanishes on every rejected input. -/
theorem cut_packet_safe {X W : Type} [DecidableEq W]
    (e : Boundary X W) (p q : Circuit W) (f : X → Bool)
    (hR : Restores e (p ++ q) f) (x : X) (i : W) :
    packet e p q x i = true → f x = true := by
  rw [cut_transport_identity e p q f hR]
  cases f x <;> simp

/-- Every accepted input is detected by at least one discrepancy coordinate. -/
theorem cut_cover_complete {X W : Type} [DecidableEq W]
    (e : Boundary X W) (p q : Circuit W) (f : X → Bool)
    (hR : Restores e (p ++ q) f) (x : X) :
    f x = true ↔ ∃ i, packet e p q x i = true := by
  constructor
  · intro hf
    obtain ⟨i, hi⟩ := direction_nonzero e p x
    exact ⟨i, by rw [cut_transport_identity e p q f hR, hf, hi]; rfl⟩
  · rintro ⟨i, hi⟩
    exact cut_packet_safe e p q f hR x i hi

/-- C01, packaged as simultaneous safety and completeness at an arbitrary cut. -/
theorem complete_safe_cover {X W : Type} [DecidableEq W]
    (e : Boundary X W) (p q : Circuit W) (f : X → Bool)
    (hR : Restores e (p ++ q) f) :
    (∀ x i, packet e p q x i = true → f x = true) ∧
    (∀ x, f x = true ↔ ∃ i, packet e p q x i = true) := by
  exact ⟨cut_packet_safe e p q f hR, cut_cover_complete e p q f hR⟩

/-- An equivalent register-equality characterization, with no chosen decoder. -/
theorem cut_states_equal_iff_reject {X W : Type} [DecidableEq W]
    (e : Boundary X W) (p q : Circuit W) (f : X → Bool)
    (hR : Restores e (p ++ q) f) (x : X) :
    run p (e.encode x false) = run q.reverse (e.encode x false) ↔ f x = false := by
  rw [inverse_suffix_boundary e p q f hR x false]
  cases hf : f x
  · simp
  · simp only [Bool.false_xor, Bool.true_eq_false, iff_false]
    intro h
    exact e.target_separated x (run_injective p h)

/-- The theorem applies to every index, not only a cut supplied as a decomposition. -/
theorem every_index_cut {X W : Type} [DecidableEq W]
    (e : Boundary X W) (c : Circuit W) (f : X → Bool)
    (hR : Restores e c f) (k : Nat) (x : X) :
    f x = true ↔ ∃ i, packet e (c.take k) (c.drop k) x i = true := by
  apply cut_cover_complete e (c.take k) (c.drop k) f
  simpa only [List.take_append_drop] using hR

/-- Specialization to arbitrary finite logical registers and zero-initialized workspace. -/
theorem canonical_complete_safe_cover (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : (Fin n → Bool) → Bool)
    (hR : Restores (canonicalBoundary n a) c f) (k : Nat) :
    (∀ x i, packet (canonicalBoundary n a) (c.take k) (c.drop k) x i = true →
      f x = true) ∧
    (∀ x, f x = true ↔
      ∃ i, packet (canonicalBoundary n a) (c.take k) (c.drop k) x i = true) := by
  apply complete_safe_cover (canonicalBoundary n a) (c.take k) (c.drop k) f
  simpa only [List.take_append_drop] using hR

end CircuitObstructions
