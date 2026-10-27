import Std

/-!
Paper X, first checked block: residual partition and no crossing.
The reduction map is data. Positive-depth operations must preserve that map.
An infinite stream has a limit only under the explicit convergence hypothesis.
No arithmetic companion, occupancy, or Collatz assumption is imported.
-/
set_option autoImplicit false
namespace PaperX.Residual

variable {X R : Type}

def Fiber (red : X → R) (r : R) := {x : X // red x = r}

def pack (red : X → R) (x : X) : (r : R) × Fiber red r :=
  ⟨red x, ⟨x, rfl⟩⟩

def unpack (red : X → R) (p : (r : R) × Fiber red r) : X := p.2.1

theorem unpack_pack (red : X → R) (x : X) : unpack red (pack red x) = x := rfl

theorem pack_unpack (red : X → R) (p : (r : R) × Fiber red r) :
    pack red (unpack red p) = p := by
  rcases p with ⟨r, x, hx⟩
  cases hx
  rfl

theorem residual_exhaustive (red : X → R) (x : X) : ∃ r, red x = r :=
  ⟨red x, rfl⟩

theorem residual_unique (red : X → R) (x : X) (r s : R)
    (hr : red x = r) (hs : red x = s) : r = s := hr.symm.trans hs

theorem fibers_disjoint (red : X → R) (r s : R) (hne : r ≠ s) :
    ¬ ∃ x, red x = r ∧ red x = s := by
  rintro ⟨x, hr, hs⟩
  exact hne (residual_unique red x r s hr hs)

/-- A finite sequence of allowed operations, including the empty sequence. -/
inductive Reach (step : X → X → Prop) : X → X → Prop
  | refl (x : X) : Reach step x x
  | next {x y z : X} : Reach step x y → step y z → Reach step x z

theorem no_crossing_finite (red : X → R) (step : X → X → Prop)
    (preserves : ∀ {x y}, step x y → red y = red x)
    {x y : X} (h : Reach step x y) : red y = red x := by
  induction h with
  | refl => rfl
  | next _ hs ih => exact (preserves hs).trans ih

theorem zeroth_order_obstruction (red : X → R) (step : X → X → Prop)
    (preserves : ∀ {x y}, step x y → red y = red x)
    {x y : X} (different : red x ≠ red y) : ¬ Reach step x y := by
  intro h
  exact different (no_crossing_finite red step preserves h).symm

theorem stream_invariant (red : X → R) (step : X → X → Prop)
    (preserves : ∀ {x y}, step x y → red y = red x)
    (stream : Nat → X) (follows : ∀ n, step (stream n) (stream (n+1))) :
    ∀ n, red (stream n) = red (stream 0) := by
  intro n
  induction n with
  | zero => rfl
  | succ n ih => exact (preserves (follows n)).trans ih

/-- Finite-precision convergence; the type of observations may depend on depth. -/
def PrecisionConverges {Y : Type} {Level : Nat → Type}
    (observe : (d : Nat) → Y → Level d) (stream : Nat → Y) (limit : Y) : Prop :=
  ∀ d, ∃ N, ∀ n, N ≤ n → observe d (stream n) = observe d limit

theorem no_crossing_limit {Y : Type} {Level : Nat → Type}
    (observe : (d : Nat) → Y → Level d) (stream : Nat → Y) (limit : Y)
    (sameRoot : ∀ n, observe 0 (stream n) = observe 0 (stream 0))
    (converges : PrecisionConverges observe stream limit) :
    observe 0 limit = observe 0 (stream 0) := by
  obtain ⟨N, hN⟩ := converges 0
  exact (hN N (Nat.le_refl N)).symm.trans (sameRoot N)

theorem positive_depth_mod (p x h : Nat) : (x + p*h) % p = x % p := by
  simp [Nat.add_mod]

/-- Root preservation alone does not imply convergence: alternating 0 and 3. -/
def oscillation (n : Nat) : Nat := if n % 2 = 0 then 0 else 3

theorem oscillation_same_root (n : Nat) : oscillation n % 3 = 0 := by
  unfold oscillation
  split <;> decide

/-- At precision 9, the root-preserving stream is not even eventually constant. -/
theorem oscillation_not_eventually_constant_mod9 :
    ¬ ∃ r N : Nat, ∀ n, N ≤ n → oscillation n % 9 = r := by
  rintro ⟨r, N, h⟩
  have he := h (2*N) (by omega)
  have ho := h (2*N+1) (by omega)
  have even : (2*N) % 2 = 0 := by omega
  simp [oscillation, even] at he
  simp [oscillation] at ho
  omega

end PaperX.Residual
