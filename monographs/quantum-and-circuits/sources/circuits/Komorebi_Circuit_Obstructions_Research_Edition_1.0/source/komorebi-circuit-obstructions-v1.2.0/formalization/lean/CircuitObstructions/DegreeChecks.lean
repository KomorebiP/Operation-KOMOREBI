import CircuitObstructions.AffineOutput

/-!
# Semantic controls for the new degree representation

The lower-degree exclusions below are proved inside Lean. They are separate
from the independent finite truth-table checker shipped with this block.
-/
namespace CircuitObstructions

def twoInput (a b : Bool) : Fin 2 → Bool := fun i => if i = 0 then a else b

def squareParity (f : BFun 2) : Bool :=
  Bool.xor (Bool.xor (f (twoInput false false)) (f (twoInput false true)))
    (Bool.xor (f (twoInput true false)) (f (twoInput true true)))

theorem squareParity_add (f g : BFun 2) :
    squareParity (fun x => Bool.xor (f x) (g x)) =
      Bool.xor (squareParity f) (squareParity g) := by
  simp only [squareParity, Bool.xor_assoc, Bool.xor_left_comm, Bool.xor_comm]

theorem affine_squareParity_zero (f : BFun 2) (h : DegreeLE 1 f) :
    squareParity f = false := by
  induction h with
  | zero => rfl
  | monomial l hl =>
      cases l with
      | nil => rfl
      | cons i is =>
          have his : is = [] := by cases is <;> simp_all
          subst is
          rcases i with ⟨i, hi⟩
          have hx : i = 0 ∨ i = 1 := by omega
          rcases hx with rfl | rfl <;> rfl
  | add _ _ ihf ihg => rw [squareParity_add, ihf, ihg]; rfl

def andTwo : BFun 2 := fun x => x 0 && x 1

theorem andTwo_degree_two : DegreeLE 2 andTwo := by
  change DegreeLE 2 (fun x => x 0 && x 1)
  simpa [bprod] using DegreeLE.monomial (d := 2) [0,1] (by simp)

theorem andTwo_not_affine : ¬ DegreeLE 1 andTwo := by
  intro h
  have hp := affine_squareParity_zero andTwo h
  change true = false at hp
  cases hp

theorem andTwo_no_degree_one_safe_cover : ¬ CompleteSafeDegreeLE andTwo 1 := by
  intro h
  obtain ⟨g, hg, hs, hv⟩ := h (twoInput true true) (by decide)
  have h00 : g (twoInput false false) = false := by
    have hh := hs (twoInput false false)
    cases he : g (twoInput false false) <;> simp_all [andTwo, twoInput]
  have h01 : g (twoInput false true) = false := by
    have hh := hs (twoInput false true)
    cases he : g (twoInput false true) <;> simp_all [andTwo, twoInput]
  have h10 : g (twoInput true false) = false := by
    have hh := hs (twoInput true false)
    cases he : g (twoInput true false) <;> simp_all [andTwo, twoInput]
  have hp := affine_squareParity_zero g hg
  simp [squareParity, h00, h01, h10, hv] at hp

theorem beta_andTwo : beta andTwo = 2 := by
  have hu := beta_le_inputs andTwo
  have hn := andTwo_no_degree_one_safe_cover
  have hl : ¬ beta andTwo ≤ 1 := by
    intro h
    exact hn ((beta_le_iff andTwo).mp h)
  omega

theorem betaStar_andTwo : betaStar andTwo = 2 := by
  have hu := betaStar_le_inputs andTwo
  have hl := beta_le_betaStar andTwo
  rw [beta_andTwo] at hl
  omega

theorem restored_andTwo_needs_toffoli (a : Nat)
    (c : Circuit (CanonicalWire 2 a))
    (hR : Restores (canonicalBoundary 2 a) c andTwo) : 1 ≤ toffoliCount c := by
  have h := betaStar_restoration_bound 2 a c andTwo hR
  rw [betaStar_andTwo] at h
  omega

end CircuitObstructions
