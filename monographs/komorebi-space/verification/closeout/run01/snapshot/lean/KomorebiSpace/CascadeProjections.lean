import KomorebiSpace.CoarseningCascade

set_option autoImplicit false

/-!
# Nested remainder projections and persistent information

All statements concern the actual coarsening/section cascade. The remainder
is restored to the original normed space before any limiting assertion.
The persistent subspace is not assumed trivial.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace CoarseningCascade
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (T : CoarseningCascade.{u,v} 𝕜)

/-- Coarse observation, as a continuous linear operator. -/
def levelMap : ∀ n, T.Obj 0 →L[𝕜] T.Obj n
  | 0 => ContinuousLinearMap.id 𝕜 (T.Obj 0)
  | n+1 => (T.down n).comp (levelMap n)

@[simp] theorem levelMap_apply (x : T.Obj 0) (n : ℕ) :
    T.levelMap n x = T.level x n := by
  induction n with
  | zero => rfl
  | succ n ih => change T.down n (T.levelMap n x) = _; rw [ih]; rfl

/-- Lifted coarse remainder, expressed in the original candidate space. -/
def remainder (n : ℕ) : T.Obj 0 →L[𝕜] T.Obj 0 :=
  (T.restore n).comp (T.levelMap n)

@[simp] theorem remainder_apply (x : T.Obj 0) (n : ℕ) :
    T.remainder n x = T.restore n (T.level x n) := by
  simp only [remainder, ContinuousLinearMap.comp_apply, levelMap_apply]

@[simp] theorem remainder_zero (x : T.Obj 0) : T.remainder 0 x = x := rfl

/-- Every repeated section remains a right inverse at its own coarse level. -/
@[simp] theorem level_restore (n : ℕ) (y : T.Obj n) :
    T.level (T.restore n y) n = y := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [restore_succ, level_succ, ih]
    exact (T.splitting n).right_inv y

theorem restore_injective (n : ℕ) : Function.Injective (T.restore n) := by
  intro x y h
  have hh := congrArg (fun z => T.level z n) h
  simpa only [level_restore] using hh

@[simp] theorem remainder_restore (n : ℕ) (y : T.Obj n) :
    T.remainder n (T.restore n y) = T.restore n y := by
  rw [remainder_apply, level_restore]

@[simp] theorem remainder_idempotent (n : ℕ) (x : T.Obj 0) :
    T.remainder n (T.remainder n x) = T.remainder n x := by
  simp only [remainder_apply, level_restore]

/-- Restoring at level m leaves every coarser observation unchanged. -/
theorem level_remainder_of_le (m n : ℕ) (h : m ≤ n) (x : T.Obj 0) :
    T.level (T.remainder m x) n = T.level x n := by
  induction n, h using Nat.le_induction with
  | base => rw [remainder_apply, level_restore]
  | succ n h ih => rw [level_succ, ih, level_succ]

/-- A finer remainder fixes every datum restored from a coarser level. -/
theorem remainder_restore_of_le (m n : ℕ) (h : m ≤ n) (y : T.Obj n) :
    T.remainder m (T.restore n y) = T.restore n y := by
  induction n, h using Nat.le_induction with
  | base => exact T.remainder_restore m y
  | succ n h ih =>
    rw [restore_succ]
    exact ih ((T.splitting n).lift y)

/-- The projections are nested. -/
theorem remainder_nested_left (m n : ℕ) (h : m ≤ n) (x : T.Obj 0) :
    T.remainder m (T.remainder n x) = T.remainder n x := by
  rw [T.remainder_apply x n]
  exact T.remainder_restore_of_le m n h _

theorem remainder_nested_right (m n : ℕ) (h : m ≤ n) (x : T.Obj 0) :
    T.remainder n (T.remainder m x) = T.remainder n x := by
  rw [remainder_apply, T.level_remainder_of_le m n h, remainder_apply]

/-- Unlike arbitrary repair projectors, these nested remainder projections commute. -/
theorem remainder_commute (m n : ℕ) (x : T.Obj 0) :
    T.remainder m (T.remainder n x) = T.remainder n (T.remainder m x) := by
  rcases le_total m n with h | h
  · rw [T.remainder_nested_left m n h, T.remainder_nested_right m n h]
  · rw [T.remainder_nested_right n m h, T.remainder_nested_left n m h]

/-- A detail is the difference of two consecutive original-space remainders. -/
theorem detailTerm_eq_remainder_sub (x : T.Obj 0) (n : ℕ) :
    T.detailTerm x n = T.remainder n x - T.remainder (n+1) x := by
  have h := T.one_layer x n
  rw [← remainder_apply, ← remainder_apply] at h
  rw [h]
  abel

/-- The first N layers reconstructed in their natural order. -/
def reconstructed (N : ℕ) : T.Obj 0 →L[𝕜] T.Obj 0 :=
  ContinuousLinearMap.id 𝕜 (T.Obj 0) - T.remainder N

@[simp] theorem partial_apply (x : T.Obj 0) (N : ℕ) :
    T.reconstructed N x = x - T.remainder N x := rfl

theorem partial_eq_sum (x : T.Obj 0) (N : ℕ) :
    T.reconstructed N x = ∑ n ∈ Finset.range N, T.detailTerm x n := by
  have h := T.reconstruction x N
  rw [← remainder_apply] at h
  rw [partial_apply]
  exact sub_eq_iff_eq_add.mpr h

@[simp] theorem remainder_partial (x : T.Obj 0) (N : ℕ) :
    T.remainder N (T.reconstructed N x) = 0 := by
  rw [partial_apply, map_sub, remainder_idempotent, sub_self]

@[simp] theorem partial_idempotent (x : T.Obj 0) (N : ℕ) :
    T.reconstructed N (T.reconstructed N x) = T.reconstructed N x := by
  rw [partial_apply, remainder_partial, sub_zero]

/-- Persistent coarse information, invisible to every retained detail. -/
def persistent : Submodule 𝕜 (T.Obj 0) where
  carrier := {x | ∀ n, T.remainder n x = x}
  zero_mem' := by intro n; exact map_zero _
  add_mem' := by intro x y hx hy n; rw [map_add, hx n, hy n]
  smul_mem' := by intro c x hx n; rw [map_smul, hx n]

@[simp] theorem mem_persistent (x : T.Obj 0) :
    x ∈ T.persistent ↔ ∀ n, T.remainder n x = x := Iff.rfl

/-- Vanishing all details alone is exactly membership in the persistent subspace. -/
theorem persistent_iff_details_zero (x : T.Obj 0) :
    x ∈ T.persistent ↔ ∀ n, T.detail x n = 0 := by
  constructor
  · intro hx n
    apply T.restore_injective n
    change T.detailTerm x n = T.restore n 0
    rw [map_zero, detailTerm_eq_remainder_sub, hx n, hx (n+1), sub_self]
  · intro hx n
    induction n with
    | zero => rfl
    | succ n ih =>
      have hl := T.one_layer x n
      have hd : T.detailTerm x n = 0 := by simp only [detailTerm, hx n, map_zero]
      rw [← remainder_apply, ← remainder_apply, hd, zero_add] at hl
      exact hl.symm.trans ih

/-- Equal detail coordinates determine only a class modulo persistent information. -/
theorem equal_details_iff_persistent_difference (x y : T.Obj 0) :
    (∀ n, T.detail x n = T.detail y n) ↔ x-y ∈ T.persistent := by
  rw [persistent_iff_details_zero]
  have hd (n : ℕ) : T.detail (x-y) n = T.detail x n - T.detail y n := by
    unfold detail
    rw [← levelMap_apply, map_sub, levelMap_apply, levelMap_apply, map_sub]
  simp only [hd, sub_eq_zero]

/-- The N-th coarse remainder has no retained detail below level N. -/
theorem remainder_details_below (x : T.Obj 0) (N j : ℕ) (hj : j < N) :
    T.detail (T.remainder N x) j = 0 := by
  apply T.restore_injective j
  change T.detailTerm (T.remainder N x) j = T.restore j 0
  rw [map_zero, detailTerm_eq_remainder_sub,
    T.remainder_nested_left j N hj.le,
    T.remainder_nested_left (j+1) N (by omega), sub_self]


end CoarseningCascade
end KomorebiSpace
end
