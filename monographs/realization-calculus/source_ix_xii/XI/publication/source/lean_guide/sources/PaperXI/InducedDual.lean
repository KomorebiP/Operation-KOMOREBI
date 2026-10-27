import PaperXI.MonomialDual
import PaperXI.CyclicInducedCoordinates
import PaperXI.MonomialInductionSubgroup

/-! Duality and the full-character classification for induction from a finite normal quotient. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InducedDual
open PaperXI.CyclicInduced
open scoped Classical
variable {G Q : Type*} [Group G] [Group Q] [Fintype Q]
variable (d : G →* Q) (r : Q → G) (hr : ∀ q, d (r q) = q⁻¹)

/-- The index permutation is genuine left multiplication in the quotient. -/
def indexAction : G →* Equiv.Perm Q where
  toFun g := Equiv.mulLeft (d g)
  map_one' := by ext q; simp
  map_mul' g h := by ext q; simp

omit [Fintype Q] in
@[simp] theorem indexAction_apply (g : G) (q : Q) : indexAction d g q = d g * q := rfl

variable (χ : d.ker →* ℂˣ)

/-- Induction of the inverse character identifies with the actual dual representation. -/
def inverseCharacterEquiv : Representation.Equiv (induced d (χ⁻¹)) (induced d χ).dual :=
  Representation.Equiv.mk
    ((basis d r hr (χ⁻¹)).equiv (basis d r hr χ).dualBasis (Equiv.refl Q))
    (fun g => by
      apply (basis d r hr (χ⁻¹)).ext
      intro j
      change (basis d r hr (χ⁻¹)).equiv (basis d r hr χ).dualBasis (Equiv.refl Q)
        (induced d (χ⁻¹) g (basis d r hr (χ⁻¹) j)) =
        (induced d χ).dual g
          ((basis d r hr (χ⁻¹)).equiv (basis d r hr χ).dualBasis (Equiv.refl Q)
            (basis d r hr (χ⁻¹) j))
      rw [basis_action, map_smul, Module.Basis.equiv_apply, Module.Basis.equiv_apply]
      rw [MonomialDual.dual_basis_action (induced d χ) (basis d r hr χ)
        (indexAction d) (weight d r hr χ) (fun g j => basis_action d r hr χ g j)]
      rfl)

end PaperXI.InducedDual
