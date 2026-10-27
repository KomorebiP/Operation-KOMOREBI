import Std
namespace H12SevenClassDetector

-- The two reductions of Z[omega]/7 send omega to 2 and 4.
theorem root_two : ((2*2+2+1:Nat)%7)=0 := by decide
theorem root_four : ((4*4+4+1:Nat)%7)=0 := by decide

theorem eval_twist_two (a b : Int) :
    (-b)+2*(a-b)-2*(a+2*b) = -7*b := by omega

theorem eval_twist_four (a b : Int) :
    (-b)+4*(a-b)-4*(a+4*b) = -21*b := by omega

-- R = M^-1, reduced modulo seven, is [[1,3,1],[1,0,0],[2,6,4]].
def fixedAt (r x y z : Nat) : Prop :=
  (r*(x+3*y+z))%7=x ∧ (r*x)%7=y ∧ (r*(2*x+6*y+4*z))%7=z
instance (r x y z : Nat) : Decidable (fixedAt r x y z) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _))

theorem fixed_at_two : ∀ x y z : Fin 7,
    fixedAt 2 x.val y.val z.val ↔
      y.val=(2*x.val)%7 ∧ z.val=(4*x.val)%7 := by decide

theorem fixed_at_four : ∀ x y z : Fin 7,
    fixedAt 4 x.val y.val z.val ↔
      x.val=0 ∧ y.val=0 ∧ z.val=0 := by decide

theorem coefficient_recovery : ∀ a b k : Fin 7,
    ((a.val+2*b.val)%7=k.val ∧ (a.val+4*b.val)%7=0) ↔
      (a.val=(2*k.val)%7 ∧ b.val=(3*k.val)%7) := by decide

-- For an integral alternating form with coefficients A_12, B_12,
-- B_21, C_12, the first projected coordinate evaluated at omega=2.
theorem selector_formula (a b12 b21 c : Int) :
    (c-a)+2*(-a-b12+b21)=c-3*a-2*b12+2*b21 := by omega

theorem model_selector : ((-5+2*3:Int)%7)=1 ∧ ((-5+4*3:Int)%7)=0 := by decide

end H12SevenClassDetector
