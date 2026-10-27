import PaperXII.StableCores

/-! Paper XII, 8.11–8.12. The inverse limit is the actual compatible-sequence submodule. -/
namespace PaperXII.VectorInverseLimit

open StableCores

variable {K : Type*} [Field K] {V : ℕ → Type*}
    [∀ n, AddCommGroup (V n)] [∀ n, Module K (V n)]

/-- The vector space of sequences compatible with every transition map. -/
def limit (D : LinearSystem K V) : Submodule K (∀ n, V n) where
  carrier := {v | ∀ n m (h : m ≤ n), D.map n m h (v n) = v m}
  zero_mem' := by intro n m h; exact (D.map n m h).map_zero
  add_mem' := by
    intro u v hu hv n m h
    simp only [Pi.add_apply, map_add]
    rw [hu n m h, hv n m h]
  smul_mem' := by
    intro c v hv n m h
    simp only [Pi.smul_apply, map_smul]
    rw [hv n m h]

/-- Adjacent compatibility implies compatibility with every composite transition. -/
theorem compatible_of_adjacent (D : LinearSystem K V) (v : ∀ n, V n)
    (hv : ∀ n, D.map (n + 1) n (Nat.le_succ n) (v (n + 1)) = v n) :
    v ∈ limit D := by
  intro n m hmn
  induction n, hmn using Nat.le_induction with
  | base => rw [D.map_self]; rfl
  | succ n hmn ih =>
    rw [← D.map_comp (n + 1) n m hmn (Nat.le_succ n), LinearMap.comp_apply, hv, ih]

/-- Every coordinate of a compatible sequence lies in the actual stable core. -/
theorem coordinate_mem_stableCore (D : LinearSystem K V) (v : limit D) (m : ℕ) :
    v.val m ∈ stableCore D m := by
  rw [mem_stableCore_iff]
  intro n h
  exact ⟨v.val n, v.property n m h⟩

variable [∀ n, FiniteDimensional K (V n)]

/-- Choose a preimage under the proved surjective stable-core transition. -/
noncomputable def liftCore (D : LinearSystem K V) (m : ℕ)
    (y : stableCore D m) : stableCore D (m + 1) :=
  (coreMap_surjective D m y).choose

/-- The chosen preimage really maps to the prescribed vector. -/
theorem liftCore_spec (D : LinearSystem K V) (m : ℕ) (y : stableCore D m) :
    coreMap D m (liftCore D m y) = y :=
  (coreMap_surjective D m y).choose_spec

/-- Recursively lift a prescribed first stable-core vector. -/
noncomputable def coreSequence (D : LinearSystem K V) (y : stableCore D 0) :
    ∀ n, stableCore D n
  | 0 => y
  | n + 1 => liftCore D n (coreSequence D y n)

/-- The recursion produces an actual inverse-limit element. -/
noncomputable def fromInitialCore (D : LinearSystem K V) (y : stableCore D 0) : limit D :=
  ⟨fun n ↦ (coreSequence D y n).val, compatible_of_adjacent D _ (by
    intro n
    exact congrArg Subtype.val (liftCore_spec D n (coreSequence D y n)))⟩

/-- The initial coordinate of the constructed sequence is exactly prescribed. -/
theorem fromInitialCore_zero (D : LinearSystem K V) (y : stableCore D 0) :
    (fromInitialCore D y).val 0 = y.val := rfl

/-- Precise clause of 8.11, stronger because only the first vector need be nonzero. -/
theorem prescribed_nonzero_branch (D : LinearSystem K V) (y : V 0)
    (hy : y ∈ stableCore D 0) (hne : y ≠ 0) :
    ∃ v : limit D, v.val 0 = y ∧ ∀ n, v.val n ≠ 0 := by
  let v := fromInitialCore D ⟨y, hy⟩
  refine ⟨v, rfl, ?_⟩
  intro n hn
  have hc := v.property n 0 (Nat.zero_le n)
  rw [hn, map_zero] at hc
  exact hne hc.symm

/-- A nonzero first stable core forces the actual inverse-limit vector space to be nonzero. -/
theorem nontrivial_limit_of_first_core (D : LinearSystem K V)
    (hcore : stableCore D 0 ≠ ⊥) : Nontrivial (limit D) := by
  obtain ⟨y, hy, hne⟩ := Submodule.exists_mem_ne_zero_of_ne_bot hcore
  obtain ⟨v, _, hv⟩ := prescribed_nonzero_branch D y hy hne
  exact ⟨v, 0, fun heq ↦ hv 0 (congrArg (fun w : limit D ↦ w.val 0) heq)⟩

/-- Theorem 8.11 under the manuscript's all-level nonzero-core hypothesis. -/
theorem nontrivial_limit_of_nonzero_cores (D : LinearSystem K V)
    (hcore : ∀ m, stableCore D m ≠ ⊥) : Nontrivial (limit D) :=
  nontrivial_limit_of_first_core D (hcore 0)

omit [∀ n, FiniteDimensional K (V n)] in
/-- Surjective adjacent transitions make every composite transition surjective. -/
theorem maps_surjective (D : LinearSystem K V)
    (hs : ∀ m, Function.Surjective (D.map (m + 1) m (Nat.le_succ m)))
    (n m : ℕ) (h : m ≤ n) : Function.Surjective (D.map n m h) := by
  induction n, h using Nat.le_induction with
  | base => rw [D.map_self]; exact Function.surjective_id
  | succ n h ih =>
    rw [← D.map_comp (n + 1) n m h (Nat.le_succ n)]
    exact ih.comp (hs n)

omit [∀ n, FiniteDimensional K (V n)] in
/-- Surjective systems have the whole space as their stable core at every level. -/
theorem stableCore_eq_top_of_surjective (D : LinearSystem K V)
    (hs : ∀ m, Function.Surjective (D.map (m + 1) m (Nat.le_succ m))) (m : ℕ) :
    stableCore D m = ⊤ := by
  apply top_unique
  intro y _
  rw [mem_stableCore_iff]
  intro n h
  exact maps_surjective D hs n m h y

/-- Corollary 8.12, with nonzero first space sufficient. -/
theorem nontrivial_limit_of_surjective (D : LinearSystem K V) [Nontrivial (V 0)]
    (hs : ∀ m, Function.Surjective (D.map (m + 1) m (Nat.le_succ m))) :
    Nontrivial (limit D) := by
  apply nontrivial_limit_of_first_core
  rw [stableCore_eq_top_of_surjective D hs]
  exact top_ne_bot

end PaperXII.VectorInverseLimit
