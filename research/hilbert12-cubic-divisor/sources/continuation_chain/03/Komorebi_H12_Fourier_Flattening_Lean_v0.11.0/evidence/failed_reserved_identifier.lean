import Std
namespace H12OrbitAntidifference

/-- Prefix summation along one certified orbit of the dual unit. -/
def prefix (f : Nat → Int) : Nat → Int
  | 0 => 0
  | n+1 => prefix f n + f n

def boundary (b : Nat → Int) (n : Nat) : Int := b (n+1) - b n

theorem prefix_zero (f : Nat → Int) : prefix f 0 = 0 := rfl

theorem prefix_successor (f : Nat → Int) (n : Nat) :
    prefix f (n+1) = prefix f n + f n := rfl

theorem prefix_primitive (f : Nat → Int) (n : Nat) :
    boundary (prefix f) n = f n := by
  simp only [boundary, prefix]; omega

theorem telescope (b : Nat → Int) (n : Nat) :
    prefix (boundary b) n = b n - b 0 := by
  induction n with
  | zero => simp [prefix]
  | succ n ih => simp only [prefix, boundary] at *; omega

theorem prefix_congruence_below (f g : Nat → Int) (n : Nat)
    (h : ∀ j, j < n → f j = g j) : prefix f n = prefix g n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    have hs : f n = g n := h n (by omega)
    have hi : prefix f n = prefix g n := ih (by intro j hj; exact h j (by omega))
    simp only [prefix]; rw [hs, hi]

theorem endpoint_charge (f b : Nat → Int) (n : Nat)
    (h : ∀ j, j < n → boundary b j = f j) :
    prefix f n = b n - b 0 := by
  have hc : prefix f n = prefix (boundary b) n :=
    prefix_congruence_below f (boundary b) n (by intro j hj; exact (h j hj).symm)
  rw [hc, telescope]

/-- A finite orbit block is a compactly supported difference precisely when
its total charge vanishes. Analytic infinite-series convergence is not assumed. -/
theorem zero_charge_iff_closed_primitive (f : Nat → Int) (n : Nat) :
    prefix f n = 0 ↔
      ∃ b : Nat → Int, b 0 = 0 ∧ b n = 0 ∧
        ∀ j, j < n → boundary b j = f j := by
  constructor
  · intro h
    exact ⟨prefix f, rfl, h, by intro j _; exact prefix_primitive f j⟩
  · rintro ⟨b, h0, hn, hd⟩
    rw [endpoint_charge f b n hd, h0, hn]
    rfl

theorem prefix_add (f g : Nat → Int) (n : Nat) :
    prefix (fun j => f j + g j) n = prefix f n + prefix g n := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [prefix]; rw [ih]; omega

theorem charge_under_gauge (f b : Nat → Int) (n : Nat) :
    prefix (fun j => f j + boundary b j) n =
      prefix f n + b n - b 0 := by
  rw [prefix_add, telescope]; omega

theorem equal_boundary_preserves_charge (f b : Nat → Int) (n : Nat)
    (h : b n = b 0) :
    prefix (fun j => f j + boundary b j) n = prefix f n := by
  rw [charge_under_gauge, h]; omega

theorem anchored_primitive_unique (f b : Nat → Int) (h0 : b 0 = 0)
    (hd : ∀ j, boundary b j = f j) (n : Nat) : b n = prefix f n := by
  have h := endpoint_charge f b n (by intro j _; exact hd j)
  rw [h0] at h; omega

theorem prefix_zero_tail (f : Nat → Int) (n : Nat)
    (h0 : prefix f n = 0) (ht : ∀ j, n ≤ j → f j = 0) (k : Nat) :
    prefix f (n+k) = 0 := by
  induction k with
  | zero => simpa using h0
  | succ k ih =>
    have hz := ht (n+k) (by omega)
    simpa [prefix, hz] using ih

theorem weighted_charge (f : Nat → Int) (w : Int) (n : Nat) :
    prefix (fun j => w * f j) n = w * prefix f n := by
  induction n with
  | zero => simp [prefix]
  | succ n ih => simp only [prefix]; rw [ih]; grind

theorem nonzero_charge_no_closed_primitive (f : Nat → Int) (n : Nat)
    (h : prefix f n ≠ 0) :
    ¬ ∃ b : Nat → Int, b 0 = 0 ∧ b n = 0 ∧
      ∀ j, j < n → boundary b j = f j := by
  intro hb
  exact h ((zero_charge_iff_closed_primitive f n).mpr hb)

end H12OrbitAntidifference
