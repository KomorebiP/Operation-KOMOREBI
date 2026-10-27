import FiniteLocalFamilyUpToConjugacy
import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Algebra.Group.TypeTags.Basic

/-! Even in invertible image order, different local kernel conjugators need not
come from one strict global lift. The chosen local involutions over Z/9 have
the same mod-3 reduction, but they do not commute. -/
namespace Komorebi.StrongArtin.SquareZeroH2.TameGluingExample

abbrev C2 := Multiplicative (ZMod 2)
abbrev G := C2 × C2
abbrev M9 := Matrix (Fin 2) (Fin 2) (ZMod 9)
abbrev M3 := Matrix (Fin 2) (Fin 2) (ZMod 3)

def reduction : ZMod 9 →+* ZMod 3 := ZMod.castHom (by decide) (ZMod 3)
def matrixReduction : M9 →+* M3 := reduction.mapMatrix

def a : M9ˣ where
  val := !![-1,0;0,1]
  inv := !![-1,0;0,1]
  val_inv := by decide
  inv_val := by decide

def b : M9ˣ where
  val := !![-1,6;0,1]
  inv := !![-1,6;0,1]
  val_inv := by decide
  inv_val := by decide

def conjugator : M9ˣ where
  val := !![1,3;0,1]
  inv := !![1,6;0,1]
  val_inv := by decide
  inv_val := by decide

theorem conjugator_reduces_to_one : matrixReduction conjugator=1 := by decide

theorem local_involutions_same_residue : matrixReduction a=matrixReduction b := by decide

theorem local_involutions_kernel_conjugate : b=conjugator*a*conjugator⁻¹ := by decide

theorem local_involutions_do_not_commute : a*b≠b*a := by decide

theorem group_order_isUnit : IsUnit (Fintype.card G : ZMod 9) := by decide

def signA : C2 →* M9ˣ where
  toFun h := if h=1 then 1 else a
  map_one' := by simp
  map_mul' := by decide

def signB : C2 →* M9ˣ where
  toFun h := if h=1 then 1 else b
  map_one' := by simp
  map_mul' := by decide

def globalCandidate : G →* M9ˣ where
  toFun g := signA (g.1*g.2)
  map_one' := by simp
  map_mul' g h := by
    change signA ((g.1*h.1)*(g.2*h.2))=signA (g.1*g.2)*signA (h.1*h.2)
    rw [show (g.1*h.1)*(g.2*h.2)=(g.1*g.2)*(h.1*h.2) by
      simp [mul_comm,mul_left_comm],map_mul]

theorem explicit_simultaneous_local_conjugacy :
    (∀ h, globalCandidate (h,1)=signA h) ∧
    (∀ h, signB h=conjugator*globalCandidate (1,h)*conjugator⁻¹) := by decide

theorem explicit_local_residue_compatibility :
    ∀ h, matrixReduction (signB h)=matrixReduction (globalCandidate (1,h)) := by decide

def generator : C2 := Multiplicative.ofAdd 1

theorem no_literal_global_lift :
    ¬∃ lift : G →* M9ˣ,
      (∀ h, lift (h,1)=signA h) ∧ (∀ h, lift (1,h)=signB h) := by
  rintro ⟨lift,hA,hB⟩
  have hprod : (generator,1)*(1,generator)=(1,generator)*(generator,1) := by simp
  have he := congrArg lift hprod
  rw [map_mul,map_mul,hA,hB] at he
  exact local_involutions_do_not_commute he

end Komorebi.StrongArtin.SquareZeroH2.TameGluingExample
