import KomorebiSpace.OverlapViewBridge
import Mathlib.Combinatorics.SimpleGraph.Walk.Operations
import Mathlib.Tactic.FinCases

set_option autoImplicit false

/-!
# Uniform star control, sharp chain growth, and a nontrivial chart example

All graph families are defined for arbitrary finite sizes. No finite numerical
check supplies the universal statements or their asymptotic failure boundary.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace OverlapTransport
namespace Examples
variable {V : Type u} {H : Type v}
variable [NormedAddCommGroup H] [NormedSpace ℝ H]

def star (o : V) : SimpleGraph V := SimpleGraph.fromRel (fun i _ => i = o)

def starPath (o i : V) : (star o).Walk o i := by
  classical
  by_cases h : o = i
  · subst i; exact .nil
  · exact (show (star o).Adj o i from ⟨h, Or.inl rfl⟩).toWalk

@[simp] theorem starPath_anchor (o : V) : starPath o o = .nil := by
  classical
  simp [starPath]

theorem starPath_length_le_one (o i : V) : (starPath o i).length ≤ 1 := by
  classical
  by_cases h : o = i
  · subst i; simp
  · simp [starPath, h]

def starRouting (o : V) : Routing (star o) o where
  path := starPath o
  at_anchor := starPath_anchor o

variable [Fintype V]

theorem star_radius_le_one (o : V) : (starRouting o).radius ≤ 1 := by
  apply Finset.sup_le
  intro i _
  exact starPath_length_le_one o i

/-- The constant is independent of how many vertices the star has. -/
theorem star_error (e : Frames (V := V) (H := H)) (o : V) (x : V → H) :
    ‖x - repair e o x‖ ≤ ‖edgeDifferential e (star o) x‖ := by
  calc
    _ ≤ ((starRouting o).radius : ℝ) * ‖edgeDifferential e (star o) x‖ :=
      (starRouting o).repair_error e x
    _ ≤ 1 * ‖edgeDifferential e (star o) x‖ :=
      mul_le_mul_of_nonneg_right (by exact_mod_cast star_radius_le_one o) (norm_nonneg _)
    _ = _ := one_mul _

/-- Actual finite paths with n edges and n+1 views. -/
def chain (n : ℕ) : SimpleGraph (Fin (n+1)) where
  Adj i j := i.val + 1 = j.val ∨ j.val + 1 = i.val
  symm := ⟨by intro i j h; exact h.symm⟩
  loopless := ⟨by intro i h; omega⟩

def chainWalk (n : ℕ) : (k : ℕ) → (hk : k ≤ n) →
    (chain n).Walk (⟨0, by omega⟩ : Fin (n+1)) ⟨k, by omega⟩
  | 0, _ => .nil
  | k+1, hk => (chainWalk n k (by omega)).append
      (show (chain n).Adj (⟨k, by omega⟩ : Fin (n+1)) ⟨k+1, by omega⟩ from
        Or.inl rfl).toWalk

theorem chainWalk_length (n : ℕ) : ∀ (k : ℕ) (hk : k ≤ n),
    (chainWalk n k hk).length = k
  | 0, _ => rfl
  | k+1, hk => by
    simp only [chainWalk, SimpleGraph.Walk.length_append, SimpleGraph.Adj.length_toWalk]
    rw [chainWalk_length n k]

def chainRouting (n : ℕ) : Routing (chain n) (0 : Fin (n+1)) where
  path i := chainWalk n i.val (by omega)
  at_anchor := rfl

theorem chain_radius (n : ℕ) : (chainRouting n).radius = n := by
  apply le_antisymm
  · apply Finset.sup_le
    intro i _
    change (chainWalk n i.val _).length ≤ n
    rw [chainWalk_length]
    omega
  · have h := (chainRouting n).length_le_radius (Fin.last n)
    change (chainWalk n n _).length ≤ (chainRouting n).radius at h
    rw [chainWalk_length] at h
    exact h

def identityFrames (n : ℕ) : Frames (V := Fin (n+1)) (H := ℝ) :=
  fun _ => LinearIsometryEquiv.refl ℝ ℝ

def ramp (n : ℕ) (i : Fin (n+1)) : ℝ := i.val

theorem ramp_repair_zero (n : ℕ) : repair (identityFrames n) 0 (ramp n) = 0 := by
  funext i
  simp [repair, transport_apply, identityFrames, ramp]

theorem ramp_norm (n : ℕ) : ‖ramp n‖ = (n : ℝ) := by
  apply le_antisymm
  · apply (pi_norm_le_iff_of_nonneg (Nat.cast_nonneg n)).mpr
    intro i
    change ‖(i.val : ℝ)‖ ≤ (n : ℝ)
    rw [Real.norm_natCast]
    exact_mod_cast Nat.le_of_lt_succ i.isLt
  · have h := norm_le_pi_norm (ramp n) (Fin.last n)
    simpa [ramp] using h

theorem chain_residual_le_one (n : ℕ) :
    ‖edgeDifferential (identityFrames n) (chain n) (ramp n)‖ ≤ 1 := by
  apply (pi_norm_le_iff_of_nonneg zero_le_one).mpr
  intro a
  change ‖(a.val.2.val : ℝ) - (a.val.1.val : ℝ)‖ ≤ 1
  rcases a.property with h | h
  · rw [← h, Nat.cast_add, Nat.cast_one]
    norm_num
  · rw [← h, Nat.cast_add, Nat.cast_one]
    norm_num

theorem chain_residual_norm (n : ℕ) (hn : 0 < n) :
    ‖edgeDifferential (identityFrames n) (chain n) (ramp n)‖ = 1 := by
  apply le_antisymm (chain_residual_le_one n)
  let a : Edges (chain n) := ⟨(⟨0, by omega⟩,⟨1,by omega⟩),Or.inl rfl⟩
  have h := norm_le_pi_norm (edgeDifferential (identityFrames n) (chain n) (ramp n)) a
  simpa [edgeDifferential_apply, defect, transport_apply, identityFrames, ramp, a] using h

theorem chain_error (n : ℕ) :
    ‖ramp n - repair (identityFrames n) 0 (ramp n)‖ = (n : ℝ) := by
  rw [ramp_repair_zero, sub_zero, ramp_norm]

/-- A derived upper estimate and an input attaining it at every positive chain length. -/
theorem chain_bound_sharp (n : ℕ) (hn : 0 < n) :
    (∀ x : Fin (n+1) → ℝ,
      ‖x - repair (identityFrames n) 0 x‖ ≤ (n : ℝ) *
        ‖edgeDifferential (identityFrames n) (chain n) x‖) ∧
    ‖ramp n - repair (identityFrames n) 0 (ramp n)‖ =
      (n : ℝ) * ‖edgeDifferential (identityFrames n) (chain n) (ramp n)‖ := by
  constructor
  · intro x
    simpa only [chain_radius] using (chainRouting n).repair_error (identityFrames n) x
  · rw [chain_error, chain_residual_norm n hn, mul_one]

/-- No one finite constant works for every length of this explicit overlap family. -/
theorem no_uniform_chain_constant :
    ¬ ∃ C : ℝ, 0 ≤ C ∧ ∀ n (x : Fin (n+1) → ℝ),
      ‖x - repair (identityFrames n) 0 x‖ ≤ C *
        ‖edgeDifferential (identityFrames n) (chain n) x‖ := by
  rintro ⟨C,hC,hbound⟩
  obtain ⟨n,hn⟩ := exists_nat_gt C
  have hb := hbound n (ramp n)
  rw [chain_error] at hb
  have he := mul_le_mul_of_nonneg_left (chain_residual_le_one n) hC
  rw [mul_one] at he
  exact (not_le_of_gt hn) (hb.trans he)

/-- A nonidentity local chart on the real line. -/
def reflection : ℝ ≃ₗᵢ[ℝ] ℝ where
  toFun x := -x
  invFun x := -x
  left_inv := neg_neg
  right_inv := neg_neg
  map_add' := neg_add
  map_smul' := by intro c x; simp
  norm_map' := norm_neg

def signedFrames : Frames (V := Bool) (H := ℝ) :=
  fun b => if b then reflection else LinearIsometryEquiv.refl ℝ ℝ

def signedData : Bool → ℝ := fun b => if b then -9 else 7

theorem signed_repair_formula :
    repair signedFrames false signedData false = 7 ∧
    repair signedFrames false signedData true = -7 := by
  constructor <;> rfl

theorem signed_residual_nonzero :
    edgeDifferential signedFrames (star false) signedData ≠ 0 := by
  intro h
  let a : Edges (star false) := ⟨(false,true), ⟨by decide, Or.inl rfl⟩⟩
  have he := congrFun h a
  change -(-9 : ℝ) - 7 = 0 at he
  norm_num at he

end Examples
end OverlapTransport
end KomorebiSpace
end
