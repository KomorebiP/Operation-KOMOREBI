import H12ConjugationOrder

/-! Eisenstein-linear identities for a CM-threefold model.
The passage to complex tori and the analytic gamma comparison are ordinary
mathematics in PROOF.md, not hidden as formal axioms here. -/
namespace H12.CMThreefold
open H12.ConjugationOrder

def esub (x y : Eis) : Eis := ⟨x.a-y.a,x.b-y.b⟩
def sub (x y : R6) : R6 := ⟨esub x.c0 y.c0,esub x.c1 y.c1,esub x.c2 y.c2⟩
def scale (k : Eis) (x : R6) : R6 := ⟨emul k x.c0,emul k x.c1,emul k x.c2⟩
def original (x : R6) : R6 :=
  ⟨x.c1, eadd (eadd (escale (-4) x.c0) (escale 2 x.c1)) (escale 15 x.c2),
    eadd (escale (-1) x.c0) (escale 4 x.c2)⟩
def change (x : R6) : R6 :=
  ⟨eadd (escale (-2) x.c1) (escale 15 x.c2),
    eadd (escale 2 x.c0) (escale (-1) x.c1),x.c0⟩
def ordinary (z : Eis) : R6 := ⟨z,z,z⟩
def embed7 (z : Eis) : R6 := ⟨z,escale 2 z,escale 4 z⟩
def c : Eis := ⟨3,1⟩
def j : Eis := ⟨2,3⟩
def twisted (z : Eis) : R6 := ⟨emul (emul c c) z,emul c z,z⟩
def companion (x : R6) : R6 := mul epsilon1 x

theorem intertwining (x : R6) : change (original x) = companion (change x) := by
  rcases x with ⟨⟨a,b⟩,⟨c0,d⟩,⟨e,f⟩⟩
  simp [change,original,companion,mul,epsilon1,ez,eadd,escale,emul]
  congr 2 <;> omega

/-- Companion untwisted fixed points are controlled by six-torsion. -/
theorem ordinary_fixed_identity (z : Eis) :
    sub (ordinary z) (companion (ordinary z)) = ⟨escale 6 z,ez,ez⟩ := by
  rcases z with ⟨a,b⟩
  simp [ordinary,sub,esub,companion,mul,epsilon1,ez,eadd,escale,emul]
  congr 2 <;> omega

/-- Companion twisted fixed points are controlled by 6J-torsion. -/
theorem twisted_fixed_identity (z : Eis) :
    sub (scale ew (companion (twisted z))) (twisted z) =
      ⟨emul (emul ew j) (escale 6 z),ez,ez⟩ := by
  rcases z with ⟨a,b⟩
  simp [sub,scale,esub,companion,twisted,c,j,mul,epsilon1,ez,ew,eadd,escale,emul]
  congr 2 <;> omega

/-- The seventh-torsion orbit is the (1,2,4) line for the original unit. -/
theorem seven_doubling_carry (z : Eis) :
    original (embed7 z) = add (embed7 (escale 2 z)) ⟨ez,escale 56 z,escale 7 z⟩ := by
  rcases z with ⟨a,b⟩
  simp [original,embed7,add,ez,eadd,escale]
  congr 2 <;> omega

/-- This factorization proves the whole J-torsion line is twisted fixed,
not merely one sampled point. -/
theorem seven_twisted_factor (z : Eis) :
    sub (scale ew (original (embed7 z))) (embed7 z) =
      scale (emul j z) ⟨⟨1,1⟩,⟨26,18⟩,⟨7,6⟩⟩ := by
  rcases z with ⟨a,b⟩
  simp [sub,scale,esub,original,embed7,ew,j,eadd,escale,emul]
  congr 2 <;> omega

/-- The degree-225 change of threefold coordinates is an isomorphism on
this seventh-torsion subgroup: its extra coordinate is divisible by seven. -/
theorem seven_change_coordinates (z : Eis) :
    change (embed7 z) = ⟨escale 56 z,ez,z⟩ := by
  rcases z with ⟨a,b⟩
  simp [change,embed7,escale,eadd,ez]
  congr 2 <;> omega

theorem c_associate_j : c = escale (-1) (emul ew j) := by decide

theorem c_cube_identity :
    esub (emul (emul c c) c) ⟨7,0⟩ = escale 6 j := by decide

/-- The CRT splitting uses 7 and -6, which add to one. -/
theorem splitting_identity (z : Eis) :
    eadd (escale 7 z) (escale (-6) z) = z := by
  rcases z with ⟨a,b⟩
  simp [eadd,escale]
  constructor <;> omega

def ordinaryOriginal (z : Eis) : R6 := ⟨escale 3 z,escale 3 z,z⟩
def twistedOriginal (z : Eis) : R6 :=
  ⟨emul ⟨5,1⟩ z,emul ⟨-4,-5⟩ z,z⟩

/-- Complete original-matrix fixed-point parameterization, before quotienting. -/
theorem original_ordinary_identity (z : Eis) :
    sub (ordinaryOriginal z) (original (ordinaryOriginal z)) =
      ⟨ez,escale (-6) z,ez⟩ := by
  rcases z with ⟨a,b⟩
  simp [sub,esub,ordinaryOriginal,original,ez,eadd,escale]
  congr 2 <;> omega

/-- Complete original-matrix twisted fixed-point parameterization. -/
theorem original_twisted_identity (z : Eis) :
    sub (scale ew (original (twistedOriginal z))) (twistedOriginal z) =
      ⟨ez,escale 6 (emul c z),ez⟩ := by
  rcases z with ⟨a,b⟩
  simp [sub,esub,scale,ew,twistedOriginal,original,c,ez,eadd,escale,emul]
  congr 2 <;> omega

end H12.CMThreefold
