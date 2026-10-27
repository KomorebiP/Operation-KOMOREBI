/- Integer argument taps and their conductor-three gain obstruction. -/
module
public import Mathlib.Tactic.Ring.Basic
public import Mathlib.Tactic.FieldSimp
public section
namespace H12.Taps

def phase3 (n : ℤ) : ℤ := if n%3=0 then 0 else if n%3=1 then 1 else -1

theorem phase3_lift (n : ℤ) : ∃ d : ℤ, phase3 n=n+3*d := by
  unfold phase3
  split_ifs with h0 h1
  · refine ⟨-(n/3), ?_⟩; omega
  · refine ⟨-(n/3), ?_⟩; omega
  · refine ⟨-(n/3)-1, ?_⟩; omega

def gain : List (ℤ × ℤ) → ℤ
  | [] => 0
  | (k,h)::xs => h*phase3 k+gain xs

def firstMoment : List (ℤ × ℤ) → ℤ
  | [] => 0
  | (k,h)::xs => h*k+firstMoment xs

def secondMoment : List (ℤ × ℤ) → ℤ
  | [] => 0
  | (k,h)::xs => h*k^2+secondMoment xs

theorem gain_lift (xs : List (ℤ × ℤ)) : ∃ d : ℤ, gain xs=firstMoment xs+3*d := by
  induction xs with
  | nil => exact ⟨0,rfl⟩
  | cons kh xs ih =>
    rcases kh with ⟨k,h⟩
    rcases ih with ⟨d,hd⟩
    rcases phase3_lift k with ⟨e,he⟩
    refine ⟨h*e+d, ?_⟩
    simp only [gain,firstMoment,he,hd]
    ring1

theorem gain_divisible_by_three (xs : List (ℤ × ℤ)) (h : firstMoment xs=0) :
    (3 : ℤ) ∣ gain xs := by
  rcases gain_lift xs with ⟨d,hd⟩
  rw [h,zero_add] at hd
  exact ⟨d,hd⟩

def cubicStencil : List (ℤ × ℤ) := [(-1,1),(1,3),(2,-1)]
theorem stencil_first_moment : firstMoment cubicStencil=0 := by decide
theorem stencil_second_moment : secondMoment cubicStencil=0 := by decide
theorem stencil_target_gain : gain cubicStencil=3 := by decide

theorem triple_zero_identity {K : Type*} [Field K] (z : K) (hz : z≠0) :
    z*(z⁻¹+3*z-z^2-3)=-(z-1)^3 := by
  field_simp
  ring1

theorem cubic_unit_identity {K : Type*} [CommRing K] (b : K) (h : b^3=7) :
    (2-b)*(b^2+2*b+4)=1 := by
  calc
    _ = 8-b^3 := by ring1
    _ = 1 := by rw [h]; ring1

end H12.Taps
