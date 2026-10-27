/-!
Komorebi Resolution Semantics 0.1.0

STATUS: UNCOMPILED SOURCE SCAFFOLD.
This file was not checked by a Lean compiler in the release environment.
It is not proof evidence for the PDF. The scope is only the two-valued core.
No model of ZFC, forcing theorem, graph classification, or general Boolean-ring
instance is constructed here.

Reproduction target with a local Lean 4 installation:
  lean formal/KRS_Core.lean
-/
import Std

namespace KRS

def defect (a b : Bool) : Bool := Bool.xor a b

theorem defect_self (a : Bool) : defect a a = false := by
  cases a <;> rfl

theorem defect_comm (a b : Bool) : defect a b = defect b a := by
  cases a <;> cases b <;> rfl

theorem defect_zero (a : Bool) : defect a false = a := by
  cases a <;> rfl

theorem defect_eq_false_iff (a b : Bool) : defect a b = false ↔ a = b := by
  cases a <;> cases b <;> simp [defect]

theorem defect_composition (a b c : Bool) :
    defect a c = Bool.xor (defect a b) (defect b c) := by
  cases a <;> cases b <;> cases c <;> rfl

theorem defect_reconstruction (a b : Bool) :
    Bool.xor a (defect a b) = b := by
  cases a <;> cases b <;> rfl

theorem defect_additive (a b c d : Bool) :
    defect (Bool.xor a b) (Bool.xor c d) =
      Bool.xor (defect a c) (defect b d) := by
  cases a <;> cases b <;> cases c <;> cases d <;> rfl

theorem defect_twisted_product (a b c d : Bool) :
    defect (a && b) (c && d) =
      Bool.xor ((defect a c) && b) (c && (defect b d)) := by
  cases a <;> cases b <;> cases c <;> cases d <;> rfl

theorem defect_complement (a b : Bool) :
    defect (!a) (!b) = defect a b := by
  cases a <;> cases b <;> rfl

theorem triangle_telescope (a b c : Bool) :
    Bool.xor (Bool.xor (defect a b) (defect b c)) (defect c a) = false := by
  cases a <;> cases b <;> cases c <;> rfl

universe u
variable {W : Type u}

def Invariant (E : W → W → Prop) (a : W → Bool) : Prop :=
  ∀ w z, E w z → a w = a z

theorem invariant_constant (E : W → W → Prop) (b : Bool) :
    Invariant E (fun _ => b) := by
  intro w z _
  rfl

theorem invariant_complement (E : W → W → Prop) (a : W → Bool)
    (ha : Invariant E a) : Invariant E (fun w => !(a w)) := by
  intro w z h
  rw [ha w z h]

theorem invariant_xor (E : W → W → Prop) (a b : W → Bool)
    (ha : Invariant E a) (hb : Invariant E b) :
    Invariant E (fun w => Bool.xor (a w) (b w)) := by
  intro w z h
  rw [ha w z h, hb w z h]

theorem invariant_and (E : W → W → Prop) (a b : W → Bool)
    (ha : Invariant E a) (hb : Invariant E b) :
    Invariant E (fun w => (a w) && (b w)) := by
  intro w z h
  rw [ha w z h, hb w z h]

theorem invariant_of_more_edges (E F : W → W → Prop)
    (hEF : ∀ w z, E w z → F w z) (a : W → Bool)
    (ha : Invariant F a) : Invariant E a := by
  intro w z h
  exact ha w z (hEF w z h)

end KRS
