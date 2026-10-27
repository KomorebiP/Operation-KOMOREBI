import Std
namespace H12DualFourier
structure V where
  x : Int
  y : Int
  z : Int
  deriving DecidableEq, Repr

def original (v : V) : V := ⟨v.y,-4*v.x+2*v.y+15*v.z,-v.x+4*v.z⟩
def dual (k : V) : V := ⟨-4*k.y-k.z,k.x+2*k.y,15*k.y+4*k.z⟩
def dualInv (k : V) : V := ⟨8*k.x+k.y+2*k.z,-4*k.x-k.z,15*k.x+4*k.z⟩
def dot (k v : V) : Int := k.x*v.x+k.y*v.y+k.z*v.z

theorem dual_pairing (k v : V) : dot (dual k) v = dot k (original v) := by
  cases k; cases v; simp only [dot,dual,original]; grind

theorem inverse_left (k : V) : dualInv (dual k) = k := by
  cases k; simp only [dualInv,dual]; congr 1 <;> omega

theorem inverse_right (k : V) : dual (dualInv k) = k := by
  cases k; simp only [dualInv,dual]; congr 1 <;> omega

theorem dual_injective (a b : V) (h : dual a = dual b) : a = b := by
  have h' := congrArg dualInv h
  simpa only [inverse_left] using h'

theorem conductor_residue (k : V) : (dual k).z % 3 = k.z % 3 := by
  simp only [dual]; omega

def iterate : Nat → V → V
  | 0,k => k
  | n+1,k => dual (iterate n k)

theorem all_iterates_conductor (n : Nat) (k : V) :
    (iterate n k).z % 3 = k.z % 3 := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [iterate]; rw [conductor_residue,ih]

theorem dual_cubic (k : V) :
    let k1 := dual k
    let k2 := dual k1
    let k3 := dual k2
    (⟨k3.x-6*k2.x+12*k1.x-k.x,
       k3.y-6*k2.y+12*k1.y-k.y,
       k3.z-6*k2.z+12*k1.z-k.z⟩ : V) = ⟨0,0,0⟩ := by
  cases k; simp only [dual]; congr 1 <;> omega

theorem gauge_winding_preserves_conductor (m n : V) :
    (m.z+n.z-(dual n).z)%3=m.z%3 := by
  simp only [dual]; omega

theorem actual_frequency_chain :
    dual ⟨0,0,1⟩=⟨-1,0,4⟩ ∧
    dual ⟨-1,0,4⟩=⟨-4,-1,16⟩ ∧
    dual ⟨-4,-1,16⟩=⟨-12,-6,49⟩ := by decide

end H12DualFourier
