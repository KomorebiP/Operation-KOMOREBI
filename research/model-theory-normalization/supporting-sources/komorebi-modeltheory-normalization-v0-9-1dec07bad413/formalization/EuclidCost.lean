module
public import BoundedBezout

@[expose] public section
namespace Komorebi.Echelon.Cost

/-- Number of nonterminal divisions in the recursion defining euclidCoeff. -/
def euclidSteps (a b : Nat) : Nat :=
  if _h : b=0 then 0 else 1+euclidSteps b (a%b)
termination_by b
decreasing_by exact Nat.mod_lt _ (Nat.pos_of_ne_zero _h)

@[simp] theorem euclidSteps_zero (a : Nat) : euclidSteps a 0=0 := by
  rw [euclidSteps]; simp

theorem euclidSteps_step (a b : Nat) (hb : b≠0) :
    euclidSteps a b=1+euclidSteps b (a%b) := by rw [euclidSteps]; simp [hb]

/-- Every two Euclidean divisions consume at least one bit of remainder budget. -/
theorem euclidSteps_binary_bound (bits a b : Nat) (hb : b<2^bits) :
    euclidSteps a b≤2*bits := by
  induction bits generalizing a b with
  | zero =>
    have hz : b=0 := by simpa using hb
    subst b; simp
  | succ bits ih =>
    by_cases hz : b=0
    · subst b; simp
    · let r := a%b
      have hrb : r<b := Nat.mod_lt a (Nat.pos_of_ne_zero hz)
      have hp : 0<2^bits := by positivity
      rw [euclidSteps_step a b hz]
      by_cases hr : r<2^bits
      · have h := ih b r hr
        change 1+euclidSteps b r≤_
        omega
      · have hrpos : 0<r := by omega
        have hbr : r≤b := by omega
        have hsmall : b-r<r := by rw [pow_succ] at hb; omega
        have hmod : b%r=b-r := by rw [Nat.mod_eq_sub_mod hbr, Nat.mod_eq_of_lt hsmall]
        have hnext : b%r<2^bits := by rw [hmod]; rw [pow_succ] at hb; omega
        have h := ih r (b%r) hnext
        change 1+euclidSteps b r≤_
        rw [euclidSteps_step b r (Nat.ne_of_gt hrpos)]
        omega

end Komorebi.Echelon.Cost
