import Std
namespace H12WeilCharacter

abbrev E := Int × Int
def emul (x y : E) : E := (x.1*y.1-x.2*y.2, x.1*y.2+x.2*y.1-x.2*y.2)
def eadd (x y : E) : E := (x.1+y.1,x.2+y.2)
def scale (n : Int) (x : E) : E := (n*x.1,n*x.2)
def one : E := (1,0)
def om : E := (0,1)
def J : E := (2,3)
def Jbar : E := (-1,-3)
def wedge (x y : E) : Int := x.1*y.2-x.2*y.1
def phase (x y : E) : Int := wedge x y % 7

theorem jacobi_norm : emul J Jbar = (7,0) := by decide
theorem base_pairing_exponent : wedge Jbar J = 3 := by decide
theorem base_pairing_nonzero : phase Jbar J ≠ 0 := by decide
theorem conjugation_reverses_phase : phase J Jbar = 4 := by decide

theorem pairing_all_residue_multiples : ∀ a b : Fin 7,
    phase (scale a.val Jbar) (scale b.val J) = ((3*a.val*b.val : Int) % 7) := by decide

theorem pairing_nondegenerate : ∀ a : Fin 7,
    (∀ b : Fin 7, phase (scale a.val Jbar) (scale b.val J) = 0) ↔ a.val=0 := by decide

def productPairingExponent : Int :=
    wedge Jbar J + wedge (scale 2 Jbar) (scale 2 J)
      + wedge (scale 4 Jbar) (scale 4 J)
theorem product_pairing_exact_exponent : productPairingExponent = 63 := by decide
theorem product_polarization_trivial : productPairingExponent % 7 = 0 := by decide

def chi : Nat → E
  | 0 => (0,0)
  | 1 => (1,0)
  | 2 => (0,1)
  | 3 => (-1,-1)
  | 4 => (-1,-1)
  | 5 => (0,1)
  | 6 => (1,0)
  | _ => (0,0)

theorem character_doubling : ∀ k : Fin 7, chi ((2*k.val)%7) = emul om (chi k.val) := by decide

def jacobiSum : E := (List.range 7).foldl
  (fun s k => eadd s (emul (chi k) (chi ((8-k)%7)))) (0,0)
theorem exact_jacobi_sum : jacobiSum = J := by decide

-- The formal variable is exp(2*pi*i/7); the pairing contributes its third power.
def gauss (k : Nat) : E := chi ((5*k)%7)
def gaussCubeCoeff (k : Nat) : E := (List.range 7).foldl
  (fun s i => (List.range 7).foldl
    (fun t j => eadd t (emul (emul (gauss i) (gauss j)) (gauss ((k+14-i-j)%7)))) s) (0,0)
set_option maxRecDepth 10000 in
set_option maxHeartbeats 2000000 in
theorem gauss_cube_group_algebra : ∀ k : Fin 7,
    gaussCubeCoeff k.val = scale ((if k.val=0 then 7 else 0)-1) J := by decide

-- Map z -> 5z to the coarse triptic basis (5tau,5s,1).
def smoothingMatrix : List (List Int) := [[1,0,0],[0,1,0],[0,0,5]]
def e (i j : Nat) : Int := (smoothingMatrix.getD i []).getD j 0
def smoothingDet : Int :=
  e 0 0*(e 1 1*e 2 2-e 1 2*e 2 1)
  -e 0 1*(e 1 0*e 2 2-e 1 2*e 2 0)
  +e 0 2*(e 1 0*e 2 1-e 1 1*e 2 0)
theorem smoothing_determinant : smoothingDet = 5 := by decide
theorem topological_fifth_cancellation : 5-smoothingDet=0 := by decide
end H12WeilCharacter
