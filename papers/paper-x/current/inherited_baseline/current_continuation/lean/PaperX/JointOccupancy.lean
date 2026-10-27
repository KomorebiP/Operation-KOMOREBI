import PaperX.SpectralProjectors

/-! Finite products of actual commuting spectral projectors; exact image,
idempotence and trace-rank. Empty lists give the identity. Characteristic zero
is needed only to recover integer occupancy from the field-valued trace. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.JointOccupancy

open scoped BigOperators
open LinearMap Module.End PaperX.SpectralProjectors
universe u v w
variable {K : Type u} [Field K] {V : Type v} [AddCommGroup V] [Module K V]
  [FiniteDimensional K V] {I : Type w}

/-- An actual intersection, not a range stipulated to be the desired one. -/
def jointSpace (T : I → Module.End K V) (a : I → K) : List I → Submodule K V
  | [] => ⊤
  | i :: l => (T i).eigenspace (a i) ⊓ jointSpace T a l

omit [FiniteDimensional K V] in
theorem mem_jointSpace (T : I → Module.End K V) (a : I → K) (l : List I) (x : V) :
    x ∈ jointSpace T a l ↔ ∀ i ∈ l, T i x = a i • x := by
  induction l with
  | nil => simp [jointSpace]
  | cons i l ih => simp [jointSpace, ih]

/-- Ordered product of polynomially constructed individual projectors. -/
def joint (T : I → Module.End K V) (a : I → K) (l : List I) : Module.End K V :=
  (l.map fun i => spectral (T i) (a i)).prod

theorem joint_nil (T : I → Module.End K V) (a : I → K) : joint T a [] = 1 := rfl

theorem joint_cons (T : I → Module.End K V) (a : I → K) (i : I) (l : List I) :
    joint T a (i :: l) = spectral (T i) (a i) * joint T a l := rfl

omit [FiniteDimensional K V] in
/-- The product projects onto the intersection, provided the projections commute. -/
theorem product_isProj {p q : Submodule K V} {P Q : Module.End K V}
    (hp : IsProj p P) (hq : IsProj q Q) (h : Commute P Q) :
    IsProj (p ⊓ q) (P * Q) := by
  constructor
  · intro x
    refine ⟨hp.map_mem _, hq.mem_iff_map_id.mpr ?_⟩
    change Q (P (Q x)) = P (Q x)
    rw [← Module.End.mul_apply, ← h.eq, Module.End.mul_apply]
    rw [hq.map_id _ (hq.map_mem x)]
  · intro x hx
    change P (Q x) = x
    rw [hq.map_id x hx.2, hp.map_id x hx.1]

theorem spectral_commute_joint (T : I → Module.End K V) (a : I → K)
    (hc : ∀ i j, Commute (T i) (T j)) (i : I) (l : List I) :
    Commute (spectral (T i) (a i)) (joint T a l) := by
  apply Commute.list_prod_right
  intro P hP
  obtain ⟨j, _, rfl⟩ := List.mem_map.mp hP
  exact spectral_commute _ _ (hc i j) _ _

/-- The ordered implementation is independent of ordering for commuting inputs. -/
theorem joint_perm (T : I → Module.End K V) (a : I → K)
    (hc : ∀ i j, Commute (T i) (T j)) {l m : List I} (h : l.Perm m) :
    joint T a l = joint T a m := by
  induction h with
  | nil => rfl
  | cons i _ ih => simp only [joint_cons, ih]
  | swap i j l =>
      simp only [joint_cons, ← mul_assoc]
      rw [(spectral_commute (T j) (T i) (hc j i) (a j) (a i)).eq]
  | trans _ _ ih1 ih2 => exact ih1.trans ih2

theorem joint_isProj (T : I → Module.End K V) (a : I → K)
    (hs : ∀ i, Split (T i)) (hc : ∀ i j, Commute (T i) (T j)) (l : List I) :
    IsProj (jointSpace T a l) (joint T a l) := by
  induction l with
  | nil => exact ⟨fun _ => Submodule.mem_top, fun _ _ => rfl⟩
  | cons i l ih =>
    exact product_isProj (spectral_isProj (T i) (hs i) (a i)) ih
      (spectral_commute_joint T a hc i l)

theorem joint_idempotent (T : I → Module.End K V) (a : I → K)
    (hs : ∀ i, Split (T i)) (hc : ∀ i j, Commute (T i) (T j)) (l : List I) :
    IsIdempotentElem (joint T a l) := (joint_isProj T a hs hc l).isIdempotentElem

theorem joint_range (T : I → Module.End K V) (a : I → K)
    (hs : ∀ i, Split (T i)) (hc : ∀ i j, Commute (T i) (T j)) (l : List I) :
    LinearMap.range (joint T a l) = jointSpace T a l := (joint_isProj T a hs hc l).range

theorem joint_fixed_iff (T : I → Module.End K V) (a : I → K)
    (hs : ∀ i, Split (T i)) (hc : ∀ i j, Commute (T i) (T j)) (l : List I) (x : V) :
    joint T a l x = x ↔ ∀ i ∈ l, T i x = a i • x := by
  rw [← (joint_isProj T a hs hc l).mem_iff_map_id, mem_jointSpace]

/-- Trace equality is valid in every characteristic as an equality in K. -/
theorem trace_eq_dimension (T : I → Module.End K V) (a : I → K)
    (hs : ∀ i, Split (T i)) (hc : ∀ i j, Commute (T i) (T j)) (l : List I) :
    LinearMap.trace K V (joint T a l) = (Module.finrank K (jointSpace T a l) : K) :=
  (joint_isProj T a hs hc l).trace

/-- Occupancy means an actual nonzero joint eigenvector. -/
def Occupied (T : I → Module.End K V) (a : I → K) (l : List I) : Prop :=
  ∃ x : V, x ≠ 0 ∧ ∀ i ∈ l, T i x = a i • x

theorem occupied_iff_dimension_pos (T : I → Module.End K V) (a : I → K) (l : List I) :
    Occupied T a l ↔ 0 < Module.finrank K (jointSpace T a l) := by
  rw [Module.finrank_pos_iff_exists_ne_zero]
  constructor
  · rintro ⟨x, hx, h⟩
    exact ⟨⟨x, (mem_jointSpace T a l x).2 h⟩, fun hz => hx (congrArg Subtype.val hz)⟩
  · rintro ⟨x, hx⟩
    exact ⟨x, fun hz => hx (Subtype.ext hz), (mem_jointSpace T a l x).1 x.property⟩

theorem occupied_iff_trace_ne_zero [CharZero K] (T : I → Module.End K V) (a : I → K)
    (hs : ∀ i, Split (T i)) (hc : ∀ i j, Commute (T i) (T j)) (l : List I) :
    Occupied T a l ↔ LinearMap.trace K V (joint T a l) ≠ 0 := by
  rw [trace_eq_dimension T a hs hc l, Nat.cast_ne_zero, occupied_iff_dimension_pos]
  exact Nat.pos_iff_ne_zero

/-- The natural integer encoded by trace is unique in characteristic zero. -/
theorem trace_integer_unique [CharZero K] (T : I → Module.End K V) (a : I → K)
    (hs : ∀ i, Split (T i)) (hc : ∀ i j, Commute (T i) (T j)) (l : List I) :
    ∃! n : ℕ, LinearMap.trace K V (joint T a l) = (n : K) := by
  refine ⟨Module.finrank K (jointSpace T a l), trace_eq_dimension T a hs hc l, ?_⟩
  intro n hn
  exact Nat.cast_injective (hn.symm.trans (trace_eq_dimension T a hs hc l))

omit [FiniteDimensional K V] in
/-- Adding conditions cannot increase the actual joint eigenspace. -/
theorem space_antitone (T : I → Module.End K V) (a : I → K)
    {l m : List I} (h : ∀ i ∈ l, i ∈ m) : jointSpace T a m ≤ jointSpace T a l := by
  intro x hx
  exact (mem_jointSpace T a l x).2 fun i hi => (mem_jointSpace T a m x).1 hx i (h i hi)

theorem dimension_antitone (T : I → Module.End K V) (a : I → K)
    {l m : List I} (h : ∀ i ∈ l, i ∈ m) :
    Module.finrank K (jointSpace T a m) ≤ Module.finrank K (jointSpace T a l) :=
  Submodule.finrank_mono (space_antitone T a h)

/-- This is the literal finite-index version, with every condition imposed. -/
theorem finite_occupancy [Fintype I] [CharZero K] (T : I → Module.End K V) (a : I → K)
    (hs : ∀ i, Split (T i)) (hc : ∀ i j, Commute (T i) (T j)) :
    ∃ E : Module.End K V,
      E = joint T a (Finset.univ.toList) ∧ IsIdempotentElem E ∧
      (∀ x, x ∈ LinearMap.range E ↔ ∀ i, T i x = a i • x) ∧
      LinearMap.trace K V E = (Module.finrank K (jointSpace T a Finset.univ.toList) : K) ∧
      ((∃ x : V, x ≠ 0 ∧ ∀ i, T i x = a i • x) ↔ LinearMap.trace K V E ≠ 0) := by
  classical
  refine ⟨joint T a Finset.univ.toList, rfl, joint_idempotent T a hs hc _, ?_,
    trace_eq_dimension T a hs hc _, ?_⟩
  · intro x
    rw [joint_range T a hs hc, mem_jointSpace]
    simp
  · simpa [Occupied] using occupied_iff_trace_ne_zero T a hs hc Finset.univ.toList

end PaperX.JointOccupancy
