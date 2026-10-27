import KomorebiSpace.Realization

set_option autoImplicit false

/-! All-pairs restriction maps, derived from actual adjacent bonding functions. -/

universe u v
namespace KomorebiSpace
namespace Resolution
namespace Adjacent

variable (V : ℕ → Type u) (down : ∀ n, V (n+1) → V n)

def restrict {i j : ℕ} (h : i ≤ j) : V j → V i :=
  Nat.leRecOn (C := fun n => V n → V i) h (fun {n} f => f ∘ down n) _root_.id

@[simp] theorem restrict_refl (n : ℕ) (x : V n) :
    restrict V down (Nat.le_refl n) x = x := by
  simp [restrict, Nat.leRecOn_self]

theorem restrict_succ {i j : ℕ} (h : i ≤ j) (h' : i ≤ j+1) (x : V (j+1)) :
    restrict V down h' x = restrict V down h (down j x) := by
  simp only [restrict, Nat.leRecOn_succ h, Function.comp_apply]

theorem restrict_trans {i j k : ℕ} (hij : i ≤ j) (hjk : j ≤ k) :
    ∀ x : V k,
      restrict V down hij (restrict V down hjk x) =
      restrict V down (Nat.le_trans hij hjk) x := by
  induction k, hjk using Nat.le_induction with
  | base => intro x; rw [restrict_refl]
  | succ k hk ih =>
    intro x
    rw [restrict_succ V down hk, restrict_succ V down (Nat.le_trans hij hk)]
    exact ih (down k x)

def resolution : Resolution.{u} where
  Obj := V
  restrict := restrict V down
  restrict_refl := restrict_refl V down
  restrict_trans := fun hij hjk => restrict_trans V down hij hjk

/-- Adjacent coherence implies coherence at every ordered pair of levels. -/
theorem coherent_all (x : ∀ n, V n) (hx : ∀ n, down n (x (n+1)) = x n)
    {i j : ℕ} (h : i ≤ j) : restrict V down h (x j) = x i := by
  induction j, h using Nat.le_induction with
  | base => exact restrict_refl V down i (x i)
  | succ j hj ih => rw [restrict_succ V down hj, hx j, ih]

/-- No original space is identified with its limit without a separate equivalence. -/
def pointEquiv : {x : ∀ n, V n // ∀ n, down n (x (n+1)) = x n} ≃
    (resolution V down).Point where
  toFun x := ⟨x.val, fun _ _ h => coherent_all V down x.val x.property h⟩
  invFun x := ⟨x.val, by
    intro n
    have h := x.property n (n+1) (Nat.le_succ n)
    change restrict V down (Nat.le_succ n) (x.val (n+1)) = x.val n at h
    have hs := restrict_succ V down (Nat.le_refl n) (Nat.le_succ n) (x.val (n+1))
    have hr := restrict_refl V down n (down n (x.val (n+1)))
    exact (hs.trans hr).symm.trans h⟩
  left_inv _ := rfl
  right_inv _ := rfl

variable {V down} {W : ℕ → Type v} {downW : ∀ n, W (n+1) → W n}

theorem map_all (f : ∀ n, V n → W n)
    (hf : ∀ n x, downW n (f (n+1) x) = f n (down n x))
    {i j : ℕ} (h : i ≤ j) : ∀ x : V j,
    restrict W downW h (f j x) = f i (restrict V down h x) := by
  induction j, h using Nat.le_induction with
  | base => intro x; simp
  | succ j hj ih =>
    intro x
    rw [restrict_succ W downW hj, hf j, ih, restrict_succ V down hj]

def map (f : ∀ n, V n → W n)
    (hf : ∀ n x, downW n (f (n+1) x) = f n (down n x)) :
    Map (resolution V down) (resolution W downW) where
  app := f
  exact := fun _ _ h => map_all f hf h

@[simp] theorem map_onLimit (f : ∀ n, V n → W n)
    (hf : ∀ n x, downW n (f (n+1) x) = f n (down n x))
    (x : (resolution V down).Point) (n : ℕ) :
    ((map f hf).onLimit x).val n = f n (x.val n) := rfl

end Adjacent
end Resolution
end KomorebiSpace
