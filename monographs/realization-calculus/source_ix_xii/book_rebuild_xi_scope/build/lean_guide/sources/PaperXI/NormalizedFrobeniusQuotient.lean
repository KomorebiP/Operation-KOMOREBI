import PaperXI.SpectralGeometricFrobenius
import PaperXI.RamifiedUnramifiedQuotient

/-!
# The field-normalized Frobenius pullback and its inertia quotient

All valuation data below come from the same finite Galois spectral extension.
The degree-one element and surjectivity of degree are derived, not certificate
fields. The quotient remains a bounded pullback model, not an absolute Weil group.
-/
set_option autoImplicit false
noncomputable section

namespace PaperXI.NormalizedFrobeniusQuotient
open IsLocalRing
open PaperXI.SpectralGeometricFrobenius

variable (E L : Type*) [NontriviallyNormedField E] [IsUltrametricDist E]
  [CompleteSpace E] [ProperSpace E] [Field L] [Algebra E L]
  [FiniteDimensional E L]

abbrev Decomposition := (integers E L).decompositionSubgroup E
abbrev residueHom : Decomposition E L →* RingAut (ExtensionResidue E L) :=
  PaperXI.ResidueWeil.residueAction E (integers E L)
abbrev Weil := PaperXI.ResidueWeil.Pullback (residueHom E L) (geometricFrobenius E L)
abbrev degree : Weil E L →* Multiplicative ℤ :=
  PaperXI.ResidueWeil.degree (residueHom E L) (geometricFrobenius E L)
abbrev Inertia := (degree E L).ker

/-- Pullback inertia is the actual valuation inertia, without a cyclicity assumption. -/
def inertiaEquiv : Inertia E L ≃* (integers E L).inertiaSubgroup E :=
  PaperXI.ResidueWeil.valuationInertiaEquiv E (integers E L) (geometricFrobenius E L)

variable [IsGalois E L]

/-- The derived geometric lift as an element of the actual decomposition group. -/
def decompositionLift : Decomposition E L :=
  ⟨geometricLift E L, automorphism_stable E L (geometricLift E L)⟩

theorem residue_decompositionLift :
    residueHom E L (decompositionLift E L) = geometricFrobenius E L :=
  residue_geometricLift E L

/-- The former lifting premise is now a conclusion about this actual field extension. -/
theorem frobenius_mem_range : geometricFrobenius E L ∈ (residueHom E L).range :=
  ⟨decompositionLift E L, residue_decompositionLift E L⟩

/-- A geometric degree-one lift in the field-normalized pullback. -/
def weilGeometricLift : Weil E L :=
  ⟨(decompositionLift E L, Multiplicative.ofAdd (1 : ℤ)), by
    change residueHom E L (decompositionLift E L) = geometricFrobenius E L ^ (1 : ℤ)
    rw [zpow_one, residue_decompositionLift]⟩

@[simp]
theorem degree_geometricLift :
    degree E L (weilGeometricLift E L) = Multiplicative.ofAdd (1 : ℤ) := rfl

/-- The chosen geometric lift is normalized by the full residue size of E. -/
theorem lift_inverse_power (x : ExtensionResidue E L) :
    (residueHom E L (decompositionLift E L) x) ^ Nat.card (BaseResidue E L) = x := by
  rw [residue_decompositionLift]
  exact geometric_inverse_power E L x

/-- Arithmetic Frobenius is the inverse of this geometric lift. -/
def weilArithmeticLift : Weil E L := (weilGeometricLift E L)⁻¹

@[simp]
theorem degree_arithmeticLift :
    degree E L (weilArithmeticLift E L) = Multiplicative.ofAdd (-1 : ℤ) := by
  rw [weilArithmeticLift, map_inv, degree_geometricLift]
  rfl

/-- All integer degrees occur: no degree-surjectivity hypothesis remains. -/
theorem degree_surjective : Function.Surjective (degree E L) :=
  PaperXI.RamifiedUnramifiedQuotient.degree_surjective_of_frobenius_mem_range
    (residueHom E L) (geometricFrobenius E L) (frobenius_mem_range E L)

/-- The v0.44 quotient theorem instantiated with a proved field-side lift. -/
def quotientEquivIntegerDegree : Weil E L ⧸ Inertia E L ≃* Multiplicative ℤ :=
  PaperXI.RamifiedUnramifiedQuotient.quotientEquivIntegerDegree
    (residueHom E L) (geometricFrobenius E L) (frobenius_mem_range E L)

@[simp]
theorem quotientEquivIntegerDegree_mk (w : Weil E L) :
    quotientEquivIntegerDegree E L (QuotientGroup.mk w) = degree E L w :=
  PaperXI.RamifiedUnramifiedQuotient.quotientEquivIntegerDegree_mk
    (residueHom E L) (geometricFrobenius E L) (frobenius_mem_range E L) w

@[simp]
theorem quotient_geometricLift :
    quotientEquivIntegerDegree E L (QuotientGroup.mk (weilGeometricLift E L)) =
      Multiplicative.ofAdd (1 : ℤ) := by
  rw [quotientEquivIntegerDegree_mk, degree_geometricLift]

section FixedVectors
omit [IsGalois E L]
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable (ρ : Representation ℂ (Weil E L) V)

/-- The coarse inertia-fixed channel cannot distinguish degree-one lifts.
No such assertion is made on ramified detail channels. -/
theorem degree_one_action_eq_on_invariants
    (a b : Weil E L)
    (ha : degree E L a = Multiplicative.ofAdd (1 : ℤ))
    (hb : degree E L b = Multiplicative.ofAdd (1 : ℤ))
    (v : Representation.invariants (ρ.comp (Inertia E L).subtype)) :
    ρ a (v : V) = ρ b (v : V) := by
  have hd : b⁻¹ * a ∈ Inertia E L := by
    change degree E L (b⁻¹ * a) = 1
    rw [map_mul, map_inv, ha, hb]
    simp
  have hv : ρ (b⁻¹ * a) (v : V) = (v : V) := v.property ⟨b⁻¹ * a, hd⟩
  calc
    ρ a (v : V) = ρ b (ρ (b⁻¹ * a) (v : V)) := by
      rw [← Module.End.mul_apply, ← map_mul]
      simp
    _ = ρ b (v : V) := congrArg (fun x => ρ b x) hv

end FixedVectors
end PaperXI.NormalizedFrobeniusQuotient
