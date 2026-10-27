import Std

/-! Explicit integer coefficients in Z[r,w], r^3=7, w^2+w+1=0.
The field embedding and analytic gamma comparison are not assumed here.
This module uses only Lean's bundled Std; no Mathlib restoration is needed. -/
namespace H12.ConjugationOrder

structure Eis where
  a : Int
  b : Int
  deriving DecidableEq, Repr

def ez : Eis := ⟨0,0⟩
def eo : Eis := ⟨1,0⟩
def ew : Eis := ⟨0,1⟩
def eadd (x y : Eis) : Eis := ⟨x.a+y.a,x.b+y.b⟩
def escale (n : Int) (x : Eis) : Eis := ⟨n*x.a,n*x.b⟩
def emul (x y : Eis) : Eis :=
  ⟨x.a*y.a-x.b*y.b, x.a*y.b+x.b*y.a-x.b*y.b⟩
def ebar (x : Eis) : Eis := ⟨x.a-x.b,-x.b⟩

structure R6 where
  c0 : Eis
  c1 : Eis
  c2 : Eis
  deriving DecidableEq, Repr

def one : R6 := ⟨eo,ez,ez⟩
def omega : R6 := ⟨ew,ez,ez⟩
def rgen : R6 := ⟨ez,eo,ez⟩
def add (x y : R6) : R6 :=
  ⟨eadd x.c0 y.c0,eadd x.c1 y.c1,eadd x.c2 y.c2⟩
def mul (x y : R6) : R6 :=
  ⟨eadd (emul x.c0 y.c0) (escale 7 (eadd (emul x.c1 y.c2) (emul x.c2 y.c1))),
   eadd (eadd (emul x.c0 y.c1) (emul x.c1 y.c0)) (escale 7 (emul x.c2 y.c2)),
   eadd (eadd (emul x.c0 y.c2) (emul x.c1 y.c1)) (emul x.c2 y.c0)⟩
def bar (x : R6) : R6 := ⟨ebar x.c0,ebar x.c1,ebar x.c2⟩
def sigma (x : R6) : R6 :=
  ⟨x.c0, emul ew x.c1, emul (emul ew ew) x.c2⟩

def joined (x : R6) : Prop := x.c0.b % 7 = 0
def conductor (x : R6) : Prop := x.c0.a % 7 = 0 ∧ x.c0.b % 7 = 0
def ev2 (x : R6) : Int := (x.c0.a+2*x.c0.b)%7
def ev4 (x : R6) : Int := (x.c0.a+4*x.c0.b)%7
def defect (x : R6) : Int := x.c0.b%7

/-- Exact coefficient model for complex conjugation. -/
theorem bar_involution (x : R6) : bar (bar x) = x := by
  rcases x with ⟨⟨a,b⟩,⟨c,d⟩,⟨e,f⟩⟩
  simp [bar,ebar]

/-- Rotation of the real cubic generator has order three. -/
theorem sigma_order_three (x : R6) : sigma (sigma (sigma x)) = x := by
  rcases x with ⟨⟨a,b⟩,⟨c,d⟩,⟨e,f⟩⟩
  simp [sigma,emul,ew]
  congr 2 <;> omega

/-- Conjugation reverses the cubic rotation, not commutes with it. -/
theorem semilinear_relation (x : R6) : bar (sigma (bar x)) = sigma (sigma x) := by
  rcases x with ⟨⟨a,b⟩,⟨c,d⟩,⟨e,f⟩⟩
  simp [bar,ebar,sigma,emul,ew]
  congr 2 <;> omega

/-- The diagonal pullback criterion at the two residue factors. -/
theorem joined_iff_diagonal (x : R6) : joined x ↔ ev2 x = ev4 x := by
  simp only [joined,ev2,ev4]
  omega

/-- The residue map kernel is exactly the proposed conductor ideal. -/
theorem conductor_iff_residue_zero (x : R6) :
    conductor x ↔ ev2 x = 0 ∧ ev4 x = 0 := by
  simp only [conductor,ev2,ev4]
  omega

/-- The full norm-49 fiber has explicit lifts, with no counting assumption. -/
theorem residue_surjective (u v : Int) :
    ∃ x : R6, ev2 x = u%7 ∧ ev4 x = v%7 := by
  refine ⟨⟨⟨9*u-8*v, 4*(v-u)⟩,ez,ez⟩, ?_⟩
  simp only [ev2,ev4]
  constructor <;> omega

/-- Additive quotient R/A is Z/7 via the coefficient of w. -/
theorem defect_kernel (x : R6) : defect x = 0 ↔ joined x := by
  rfl

theorem defect_surjective (n : Int) :
    ∃ x : R6, defect x = n%7 := by
  exact ⟨⟨⟨0,n⟩,ez,ez⟩,rfl⟩

/-- Conjugation negates this additive defect. -/
theorem defect_conjugation (x : R6) : defect (bar x) = (-defect x)%7 := by
  simp only [defect,bar,ebar]
  omega

/-- The cubic field rotation acts trivially on the additive defect. -/
theorem defect_rotation (x : R6) : defect (sigma x) = defect x := by
  rfl

/-- Multiplication by w detects the extra conductor condition. -/
theorem conductor_two_tests (x : R6) :
    (joined x ∧ joined (mul x omega)) ↔ conductor x := by
  simp only [joined,mul,omega,eadd,emul,escale,ew,ez,conductor]
  omega

/-- A conductor element multiplies every element into the joined order. -/
theorem conductor_mul_into_joined (x y : R6) (hx : conductor x) :
    joined (mul x y) := by
  rcases hx with ⟨ha,hb⟩
  simp only [joined,mul,eadd,emul,escale]
  simp [Int.add_emod,Int.sub_emod,Int.mul_emod,ha,hb]

/-- Exact universal conductor, not merely tests on a finite list. -/
theorem conductor_universal (x : R6) :
    (∀ y : R6, joined (mul x y)) ↔ conductor x := by
  constructor
  · intro h
    have h1 := h one
    have hw := h omega
    have hx : joined x := by
      simpa [joined,mul,one,eadd,emul,escale,eo,ez] using h1
    exact (conductor_two_tests x).mp ⟨hx,hw⟩
  · intro hx y
    exact conductor_mul_into_joined x y hx

/-- Closure of the pulled-back order under multiplication. -/
theorem joined_mul (x y : R6) (hx : joined x) (hy : joined y) :
    joined (mul x y) := by
  simp only [joined] at hx hy ⊢
  simp only [mul,eadd,emul,escale]
  simp [Int.add_emod,Int.sub_emod,Int.mul_emod,hx,hy]

/-- Multiplication by r has image exactly the conductor. -/
theorem conductor_iff_r_multiple (x : R6) :
    conductor x ↔ ∃ y : R6, mul rgen y = x := by
  constructor
  · intro hx
    refine ⟨⟨x.c1,x.c2,⟨x.c0.a/7,x.c0.b/7⟩⟩, ?_⟩
    rcases x with ⟨⟨a,b⟩,⟨c,d⟩,⟨e,f⟩⟩
    simp only [conductor] at hx
    simp [mul,rgen,eadd,emul,escale,eo,ez]
    congr 2 <;> omega
  · rintro ⟨y,rfl⟩
    simp [conductor,mul,rgen,eadd,emul,escale,eo,ez]

/-- Concrete Jacobi idempotent lifts, their exact error retained. -/
def jacobi : R6 := ⟨⟨2,3⟩,ez,ez⟩
def jacobiBar : R6 := ⟨⟨-1,-3⟩,ez,ez⟩
def seven : R6 := ⟨⟨7,0⟩,ez,ez⟩

theorem jacobi_sum_one : add jacobi jacobiBar = one := by decide

theorem jacobi_product_seven : mul jacobi jacobiBar = seven := by decide

theorem jacobi_not_joined : ¬ joined jacobi := by
  unfold joined jacobi
  decide

theorem jacobi_residues :
    ev2 jacobi = 1 ∧ ev4 jacobi = 0 ∧
    ev2 jacobiBar = 0 ∧ ev4 jacobiBar = 1 := by decide

theorem jacobi_conjugation : bar jacobi = jacobiBar := by decide

def epsilon0 : R6 := ⟨⟨2,0⟩,⟨1,1⟩,ez⟩
def epsilon1 : R6 := ⟨⟨2,0⟩,⟨-1,0⟩,ez⟩
def epsilon2 : R6 := ⟨⟨2,0⟩,⟨0,-1⟩,ez⟩

theorem unit_product_one : mul (mul epsilon0 epsilon1) epsilon2 = one := by decide

theorem unit_rotation : sigma epsilon0 = epsilon1 ∧ sigma epsilon1 = epsilon2 ∧
    sigma epsilon2 = epsilon0 := by decide

theorem unit_conjugation : bar epsilon0 = epsilon2 ∧ bar epsilon1 = epsilon1 := by decide

/-- Every conjugate unit has the same order-three residual action. -/
theorem unit_defect_action (x : R6) :
    defect (mul epsilon0 x) = (2*defect x)%7 ∧
    defect (mul epsilon1 x) = (2*defect x)%7 ∧
    defect (mul epsilon2 x) = (2*defect x)%7 := by
  simp [defect,mul,epsilon0,epsilon1,epsilon2,ez,eadd,emul,escale,
    Int.add_emod,Int.mul_emod]

/-- The additive quotient map respects sums. -/
theorem defect_add (x y : R6) : defect (add x y) = (defect x+defect y)%7 := by
  simp [defect,add,eadd,Int.add_emod]

end H12.ConjugationOrder
