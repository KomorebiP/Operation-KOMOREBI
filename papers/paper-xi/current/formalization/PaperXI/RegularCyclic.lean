import PaperXI.TameProjectors

/-! A concrete regular cyclic model. Every character packet is nonzero, and
the erroneous forward-label rule has an actual complex representation counterexample. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.RegularCyclic
open PaperXI.CyclicAction
variable {K : Type*} [Field K]
variable {M : ℕ}

def translation (a : ZMod M) : Module.End K (ZMod M → K) where
  toFun f x := f (x + a)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

def regular : Action (K := K) (V := ZMod M → K) (M := M) where
  toFun a := translation a.toAdd
  map_one' := by
    apply LinearMap.ext
    intro f
    funext x
    simp [translation]
  map_mul' a b := by
    apply LinearMap.ext
    intro f
    funext x
    simp [translation, Module.End.mul_apply, add_assoc]

@[simp] theorem operator_apply (a x : ZMod M) (f : ZMod M → K) :
    operator (regular (K := K)) a f x = f (x + a) := rfl

def frobenius (q : (ZMod M)ˣ) : (ZMod M → K) ≃ₗ[K] (ZMod M → K) where
  toFun f x := f (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * x)
  invFun f x := f ((q : ZMod M) * x)
  left_inv f := by funext x; simp [← mul_assoc]
  right_inv f := by funext x; simp [← mul_assoc]
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem generator_relation (q : (ZMod M)ˣ) :
    (frobenius (K := K) q).conj (operator regular 1) = operator regular (q : ZMod M) := by
  apply LinearMap.ext
  intro f
  funext x
  change f ((q : ZMod M) * (((q⁻¹ : (ZMod M)ˣ) : ZMod M) * x + 1)) =
    f (x + (q : ZMod M))
  simp [mul_add, ← mul_assoc]

theorem character_vector_mem (ψ : AddChar (ZMod M) K) (j : ZMod M) :
    (fun x => ψ (j * x)) ∈ PaperXI.FourierPackets.packet regular ψ j := by
  intro a
  funext x
  change ψ (j * (x + a)) = ψ (j * a) * ψ (j * x)
  rw [mul_add, AddChar.map_add_eq_mul, mul_comm]

variable [NeZero M]

theorem projector_nonzero (ψ : AddChar (ZMod M) K) (hM : (M : K) ≠ 0) (j : ZMod M) :
    PaperXI.FourierProjectors.projector regular ψ j ≠ 0 := by
  intro h
  have hp := PaperXI.FourierPackets.projector_on_packet regular ψ hM j
    (character_vector_mem ψ j)
  have hh := congrArg (fun f : ZMod M → K => f 0) hp
  simp [h] at hh

theorem projectors_distinct (ψ : AddChar (ZMod M) K) (hψ : ψ.IsPrimitive)
    (hM : (M : K) ≠ 0) {i j : ZMod M} (hij : i ≠ j) :
    PaperXI.FourierProjectors.projector regular ψ i ≠
      PaperXI.FourierProjectors.projector regular ψ j := by
  intro h
  have hp := PaperXI.FourierProjectors.projector_orthogonal regular ψ hψ hM hij
  rw [h, ← pow_two, PaperXI.FourierProjectors.projector_idempotent regular ψ hψ hM] at hp
  exact projector_nonzero ψ hM j hp

def twoModFive : (ZMod 5)ˣ := ⟨2, 3, by decide, by decide⟩

/-- Actual counterexample over C: F t F^-1 = t^2 but F P_1 F^-1 is not P_2. -/
theorem wrong_forward_label :
    (frobenius (K := ℂ) twoModFive).conj
      (PaperXI.TameProjectors.projector (regular (K := ℂ) (M := 5)) 1) ≠
        PaperXI.TameProjectors.projector (regular (K := ℂ) (M := 5)) 2 := by
  rw [PaperXI.TameProjectors.forward_generator_covariance regular (frobenius twoModFive)
    twoModFive (generator_relation twoModFive)]
  apply projectors_distinct ZMod.stdAddChar (ZMod.isPrimitive_stdAddChar 5)
    (by norm_num : (5 : ℂ) ≠ 0)
  change (3 : ZMod 5) * 1 ≠ 2
  decide

end PaperXI.RegularCyclic
