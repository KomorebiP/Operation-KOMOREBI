import Std
namespace H12UnitCoinvariants

structure V where
  x : Int
  y : Int
  z : Int
  deriving DecidableEq, Repr

def delta (v : V) : V := ⟨-v.x+v.y, -4*v.x+v.y+15*v.z, -v.x+3*v.z⟩
def original (v : V) : V := ⟨v.y, -4*v.x+2*v.y+15*v.z, -v.x+4*v.z⟩
def ell (v : V) : Int := v.x-v.y+3*v.z
def sub (v w : V) : V := ⟨v.x-w.x,v.y-w.y,v.z-w.z⟩
def e0 : V := ⟨1,0,0⟩
def e2 : V := ⟨0,0,1⟩
def carry : V := ⟨0,5,1⟩
def reconstruction (v : V) : V := ⟨-v.z,v.y-4*v.z,0⟩
def preimage (v : V) (k : Int) : V := ⟨-v.z-3*k,v.y-4*v.z+3*k,-k⟩

theorem ell_delta (v : V) : ell (delta v) = -6*v.z := by
  cases v; simp only [ell,delta]; omega

theorem ell_original (v : V) : ell (original v) = ell v - 6*v.z := by
  cases v; simp only [ell,original]; omega

theorem ell_add (v w : V) :
    ell ⟨v.x+w.x,v.y+w.y,v.z+w.z⟩=ell v+ell w := by
  simp only [ell]; omega

theorem ell_sub (v w : V) : ell (sub v w)=ell v-ell w := by
  simp only [ell,sub]; omega

theorem unit_delta (v : V) : delta v=sub (original v) v := by
  cases v; simp only [delta,sub,original]; congr 1 <;> omega

theorem residual_reconstruction (v : V) :
    delta (reconstruction v)=⟨v.x-ell v,v.y,v.z⟩ := by
  cases v; simp only [delta,reconstruction,ell]; congr 1 <;> omega

theorem six_generator : delta ⟨-3,3,-1⟩=⟨6,0,0⟩ := by decide

theorem exact_preimage (v : V) (k : Int) (h : ell v=6*k) :
    delta (preimage v k)=v := by
  cases v; simp only [ell] at h
  simp only [delta,preimage]; congr 1 <;> omega

theorem image_iff_multiple_six (v : V) :
    (∃ w, delta w=v) ↔ ∃ k : Int, ell v=6*k := by
  constructor
  · rintro ⟨w,rfl⟩
    exact ⟨-w.z, by rw [ell_delta]; omega⟩
  · rintro ⟨k,h⟩
    exact ⟨preimage v k, exact_preimage v k h⟩

theorem quotient_difference (v w : V) :
    (∃ q, delta q=sub v w) ↔ ∃ k : Int, ell v-ell w=6*k := by
  rw [image_iff_multiple_six,ell_sub]

theorem quotient_surjective (k : Int) : ell ⟨k,0,0⟩=k := by simp [ell]

theorem period_class : ell e2=3 := by decide

theorem carry_class : ell carry = -2 := by decide

theorem tripled_carry : delta e2=⟨3*carry.x,3*carry.y,3*carry.z⟩ := by decide

theorem carry_nonzero : ¬ (∃ v, delta v=carry) := by
  rw [image_iff_multiple_six]
  simp only [ell,carry]; omega

theorem doubled_carry_nonzero : ¬ (∃ v, delta v=⟨0,10,2⟩) := by
  rw [image_iff_multiple_six]
  simp only [ell]; omega

-- If r*p is an integral vector q, the carry of r*p is r times the carry of p.
-- This coefficient identity is the finite core of the based-holonomy theorem.
theorem delta_scaling (r : Int) (v : V) :
    delta ⟨r*v.x,r*v.y,r*v.z⟩ =
      ⟨r*(delta v).x,r*(delta v).y,r*(delta v).z⟩ := by
  cases v; simp only [delta]; congr 1 <;> grind

theorem period_restricted_indices : ∀ k : Fin 6,
    (3*k.val)%6=0 ↔ k.val=0 ∨ k.val=2 ∨ k.val=4 := by decide

theorem based_character_cubed (k : Int) : (3*(2*k))%6=0 := by omega

theorem based_character_image : ∀ k : Fin 6,
    (2*k.val)%6=0 ∨ (2*k.val)%6=2 ∨ (2*k.val)%6=4 := by decide

-- All characters on the lattice are determined by the three generator phases.
def compatible (a b c : Nat) : Prop :=
  (a+4*b+c)%6=0 ∧ (a+b)%6=0 ∧ (15*b+3*c)%6=0
instance (a b c : Nat) : Decidable (compatible a b c) :=
  inferInstanceAs (Decidable (_ ∧ _ ∧ _))

theorem all_invariant_sixth_characters : ∀ a b c : Fin 6,
    compatible a.val b.val c.val ↔
      b.val=(5*a.val)%6 ∧ c.val=(3*a.val)%6 := by decide

end H12UnitCoinvariants
