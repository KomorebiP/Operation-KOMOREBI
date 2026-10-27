import Komorebi.RationalBall

set_option autoImplicit false
namespace Komorebi.RoundedPosterior

/-- Fixed fractional precision, with unbounded signed integer parts. -/
def scale (p : ℕ) : ℚ := 2^p
def down (p : ℕ) (x : ℚ) : ℚ := (⌊x * scale p⌋ : ℚ) / scale p
def up (p : ℕ) (x : ℚ) : ℚ := (⌈x * scale p⌉ : ℚ) / scale p

theorem scale_pos (p : ℕ) : 0 < scale p := by unfold scale; positivity

theorem down_le (p : ℕ) (x : ℚ) : down p x ≤ x := by
  unfold down
  exact (div_le_iff₀ (scale_pos p)).mpr (Int.floor_le _)

theorem le_up (p : ℕ) (x : ℚ) : x ≤ up p x := by
  unfold up
  exact (le_div_iff₀ (scale_pos p)).mpr (Int.le_ceil _)

/-- Round the center downward and the inflated radius upward to the dyadic grid. -/
def round (p : ℕ) (b : Ball) : Ball :=
  let c := down p b.center
  ⟨c, up p (b.radius + |b.center-c|)⟩

theorem round_encloses (p : ℕ) {b : Ball} {x : ℚ} (h : Encloses b x) :
    Encloses (round p b) x := by
  change |x-down p b.center| ≤ up p (b.radius+|b.center-down p b.center|)
  calc
    _ = |(x-b.center)+(b.center-down p b.center)| := by congr 1; ring
    _ ≤ |x-b.center|+|b.center-down p b.center| := abs_add_le _ _
    _ ≤ b.radius+|b.center-down p b.center| := add_le_add h le_rfl
    _ ≤ _ := le_up _ _

def rExact (p : ℕ) (x : ℚ) : Ball := round p (exact x)
def rAdd (p : ℕ) (a b : Ball) : Ball := round p (add a b)
def rSub (p : ℕ) (a b : Ball) : Ball := round p (sub a b)
def rMul (p : ℕ) (a b : Ball) : Ball := round p (mul a b)
def rSum {ι : Type*} (p : ℕ) (s : Finset ι) (b : ι → Ball) : Ball := round p (sum s b)

theorem rExact_encloses (p : ℕ) (x : ℚ) : Encloses (rExact p x) x :=
  round_encloses p (exact_encloses x)
theorem rAdd_encloses (p : ℕ) {a b : Ball} {x y : ℚ}
    (ha : Encloses a x) (hb : Encloses b y) : Encloses (rAdd p a b) (x+y) :=
  round_encloses p (add_encloses ha hb)
theorem rSub_encloses (p : ℕ) {a b : Ball} {x y : ℚ}
    (ha : Encloses a x) (hb : Encloses b y) : Encloses (rSub p a b) (x-y) :=
  round_encloses p (sub_encloses ha hb)
theorem rMul_encloses (p : ℕ) {a b : Ball} {x y : ℚ}
    (ha : Encloses a x) (hb : Encloses b y) : Encloses (rMul p a b) (x*y) :=
  round_encloses p (mul_encloses ha hb)
theorem rSum_encloses {ι : Type*} (p : ℕ) (s : Finset ι) (b : ι → Ball)
    (x : ι → ℚ) (h : ∀ i ∈ s, Encloses (b i) (x i)) :
    Encloses (rSum p s b) (∑ i ∈ s, x i) :=
  round_encloses p (sum_encloses s b x h)

/-- Every reported center and radius lies on the declared dyadic grid. -/
theorem round_grid (p : ℕ) (b : Ball) :
    (∃ z : ℤ, (round p b).center = (z : ℚ) / scale p) ∧
    (∃ z : ℤ, (round p b).radius = (z : ℚ) / scale p) := by
  exact ⟨⟨_, rfl⟩, ⟨_, rfl⟩⟩

end Komorebi.RoundedPosterior
