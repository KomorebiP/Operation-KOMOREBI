import KomorebiVerification.PaperII.ReleaseGluing

/-! The precision rule is an actual O-linear map between the stated quotients. -/

set_option autoImplicit false

namespace Komorebi.PaperII.ReleaseGluing

universe u v
variable {O : Type u} {V : Type v}
variable [CommRing O] [AddCommGroup V] [Module O V]

/-- The ambient scalar sublattice pi^n Λ. -/
def scaledLattice (Λ : Submodule O V) (pi : O) (n : ℕ) : Submodule O V :=
  Λ.map ((pi ^ n) • LinearMap.id)

/-- The same scalar sublattice, as a submodule of Λ. -/
def scaledInside (Λ : Submodule O V) (pi : O) (n : ℕ) : Submodule O Λ :=
  (⊤ : Submodule O Λ).map ((pi ^ n) • LinearMap.id)

def projectedReduction (Λ : Submodule O V) (pi : O) (m : ℕ)
    (E : Module.End O V) : Λ →ₗ[O] V ⧸ scaledLattice Λ pi m :=
  (scaledLattice Λ pi m).mkQ.comp (E.comp Λ.subtype)

theorem precision_kernel_contains_input_lattice
    (Λ : Submodule O V) (pi : O) (m s : ℕ) (E : Module.End O V)
    (hclear : ∀ x : V, x ∈ Λ → (pi ^ s) • E x ∈ Λ) :
    scaledInside Λ pi (m + s) ≤ LinearMap.ker (projectedReduction Λ pi m E) := by
  intro x hx
  obtain ⟨z, _hz, hzx⟩ := hx
  change (pi ^ (m + s)) • z = x at hzx
  change (scaledLattice Λ pi m).mkQ (E x) = 0
  rw [Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero]
  refine ⟨(pi ^ s) • E z, hclear z z.property, ?_⟩
  change (pi ^ m) • ((pi ^ s) • E z) = E x
  rw [← hzx]
  simp only [Submodule.coe_smul, map_smul, pow_add, mul_smul]

/-- The printed map [x]_(m+s) ↦ [Ex]_m with target V/pi^mΛ, not Λ/pi^mΛ. -/
def precisionQuotientMap
    (Λ : Submodule O V) (pi : O) (m s : ℕ) (E : Module.End O V)
    (hclear : ∀ x : V, x ∈ Λ → (pi ^ s) • E x ∈ Λ) :
    (Λ ⧸ scaledInside Λ pi (m + s)) →ₗ[O] V ⧸ scaledLattice Λ pi m :=
  (scaledInside Λ pi (m + s)).liftQ (projectedReduction Λ pi m E)
    (precision_kernel_contains_input_lattice Λ pi m s E hclear)

theorem precisionQuotientMap_mk
    (Λ : Submodule O V) (pi : O) (m s : ℕ) (E : Module.End O V)
    (hclear : ∀ x : V, x ∈ Λ → (pi ^ s) • E x ∈ Λ) (x : Λ) :
    precisionQuotientMap Λ pi m s E hclear ((scaledInside Λ pi (m + s)).mkQ x) =
      (scaledLattice Λ pi m).mkQ (E x) := rfl

end Komorebi.PaperII.ReleaseGluing
