import PaperXI.CentralExtensionCocycle
import PaperXI.TwistedRescaling
import PaperXI.CentralCharacterAction

/-! Independence of normalized quotient section for the actual cocycle and
twisted algebra of a central extension. The alternate defect is computed
in the middle group, then identified with the derived coboundary. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralExtension

open CocycleCommutator
variable {Z H A : Type*} [CommGroup Z] [Group H] [CommGroup A]
variable (D : Datum Z H A)

omit [CommGroup Z] [Group H] in
/-- Cocycles with the same actual coefficients are equal. -/
theorem cocycle_eq_of_coeff_eq {C : Type*} [CommGroup C]
    (c d : Cocycle A C) (h : ∀ a b, c.coeff a b = d.coeff a b) : c = d := by
  cases c
  cases d
  congr
  funext a b
  exact h a b

/-- The central factor relating an arbitrary section to the chosen section. -/
def sectionFactor (t : A → H) (a : A) : Z := coordinate D (t a)

theorem section_factor (t : A → H) (ht : ∀ a, D.q (t a) = a) (a : A) :
    t a = D.i (sectionFactor D t a) * sectionMap D a := by
  simpa only [sectionFactor, ht] using normal_form D (t a)

@[simp] theorem sectionFactor_one (t : A → H) (htOne : t 1 = 1) :
    sectionFactor D t 1 = 1 := by
  simp [sectionFactor, htOne]

/-- The actual central coordinate of the alternate section's defect. -/
def sectionDefect (t : A → H) (a b : A) : Z :=
  coordinate D (t a * t b * (t (a * b))⁻¹)

theorem i_sectionDefect (t : A → H) (ht : ∀ a, D.q (t a) = a) (a b : A) :
    D.i (sectionDefect D t a b) = t a * t b * (t (a * b))⁻¹ := by
  simp only [sectionDefect, coordinate_spec, map_mul, map_inv, ht,
    mul_inv_cancel, section_one, inv_one, mul_one]

theorem sectionDefect_mul (t : A → H) (ht : ∀ a, D.q (t a) = a) (a b : A) :
    t a * t b = D.i (sectionDefect D t a b) * t (a * b) := by
  rw [i_sectionDefect D t ht, inv_mul_cancel_right]

/-- The coboundary formula follows from the two actual section products. -/
theorem sectionDefect_eq_rescale (t : A → H) (ht : ∀ a, D.q (t a) = a)
    (a b : A) :
    sectionDefect D t a b =
      (rescale (centralCocycle D) (sectionFactor D t)).coeff a b := by
  apply D.i_injective
  apply mul_right_cancel (b := t (a * b))
  rw [← sectionDefect_mul D t ht]
  calc
    t a * t b = D.i (sectionFactor D t a * sectionFactor D t b * defect D a b) *
        sectionMap D (a * b) := by
      rw [section_factor D t ht a, section_factor D t ht b, normal_form_mul]
    _ = D.i (((rescale (centralCocycle D) (sectionFactor D t)).coeff a b) *
        sectionFactor D t (a * b)) * sectionMap D (a * b) := by
      congr 2
      simp [rescale, centralCocycle, div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]
    _ = _ := by
      rw [map_mul, mul_assoc, ← section_factor D t ht (a * b)]

/-- The alternate cocycle is built from its actual middle-group defect. -/
def sectionCocycle (t : A → H) (ht : ∀ a, D.q (t a) = a) : Cocycle A Z where
  coeff := sectionDefect D t
  assoc a b d := by
    simp only [sectionDefect_eq_rescale D t ht]
    exact (rescale (centralCocycle D) (sectionFactor D t)).assoc a b d

theorem sectionCocycle_eq_rescale (t : A → H) (ht : ∀ a, D.q (t a) = a) :
    sectionCocycle D t ht = rescale (centralCocycle D) (sectionFactor D t) := by
  apply cocycle_eq_of_coeff_eq
  exact sectionDefect_eq_rescale D t ht

theorem normalized_sectionCocycle (t : A → H) (ht : ∀ a, D.q (t a) = a)
    (htOne : t 1 = 1) : Normalized (sectionCocycle D t ht) := by
  rw [sectionCocycle_eq_rescale]
  exact normalized_rescale _ (normalized_centralCocycle D) _ (sectionFactor_one D t htOne)

/-- The scalar cocycle of an arbitrary section applies the fixed central
character to that section's actual defect. -/
def sectionScalarCocycle (ζ : Z →* ℂˣ) (t : A → H) (ht : ∀ a, D.q (t a) = a) :
    Cocycle A ℂˣ where
  coeff a b := ζ (sectionDefect D t a b)
  assoc a b d := by
    simpa only [sectionCocycle, map_mul] using congrArg ζ ((sectionCocycle D t ht).assoc a b d)

theorem sectionScalarCocycle_eq_rescale (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) :
    sectionScalarCocycle D ζ t ht =
      rescale (scalarCocycle D ζ) (fun a => ζ (sectionFactor D t a)) := by
  have hcoeff : ∀ a b, ζ (sectionDefect D t a b) =
      (rescale (scalarCocycle D ζ) (fun a => ζ (sectionFactor D t a))).coeff a b := by
    intro a b
    rw [sectionDefect_eq_rescale D t ht]
    simp only [rescale, centralCocycle, scalarCocycle_coeff, map_mul, map_div]
  apply cocycle_eq_of_coeff_eq
  exact hcoeff

theorem normalized_sectionScalarCocycle (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (htOne : t 1 = 1) :
    Normalized (sectionScalarCocycle D ζ t ht) := by
  rw [sectionScalarCocycle_eq_rescale]
  apply normalized_rescale _ (normalized_scalarCocycle D ζ)
  simp [htOne]

/-- Every normalized section has the same scalar commutator pairing. -/
theorem sectionScalarCocycle_commutator (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (a b : A) :
    commutator (sectionScalarCocycle D ζ t ht) a b =
      commutator (scalarCocycle D ζ) a b := by
  rw [sectionScalarCocycle_eq_rescale, commutator_rescale]

/-- In particular, the nondegeneracy condition does not depend on section. -/
theorem sectionScalarCocycle_radical (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) :
    radical (sectionScalarCocycle D ζ t ht) = radical (scalarCocycle D ζ) := by
  rw [sectionScalarCocycle_eq_rescale, radical_rescale]

variable [Fintype A]

/-- The actual algebra equivalence from an arbitrary normalized section to
the chosen section, constructed through the proved coboundary identity. -/
def sectionAlgebraEquiv (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (htOne : t 1 = 1) :
    TwistedAlgebra.Algebra (sectionScalarCocycle D ζ t ht)
      (normalized_sectionScalarCocycle D ζ t ht htOne) ≃ₐ[ℂ]
        TwistedAlgebra.Algebra (scalarCocycle D ζ) (normalized_scalarCocycle D ζ) :=
  (TwistedRescaling.congrEquiv _ _ (normalized_sectionScalarCocycle D ζ t ht htOne)
    (normalized_rescale _ (normalized_scalarCocycle D ζ)
      (fun a => ζ (sectionFactor D t a)) (by simp [htOne]))
    (sectionScalarCocycle_eq_rescale D ζ t ht)).trans
      (TwistedRescaling.rescaleEquiv (scalarCocycle D ζ) (normalized_scalarCocycle D ζ)
        (fun a => ζ (sectionFactor D t a)) (by simp [htOne]))

@[simp] theorem sectionAlgebraEquiv_basis (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (htOne : t 1 = 1) (a : A) :
    sectionAlgebraEquiv D ζ t ht htOne
      (TwistedAlgebra.basis (sectionScalarCocycle D ζ t ht)
        (normalized_sectionScalarCocycle D ζ t ht htOne) a) =
      (ζ (sectionFactor D t a) : ℂ) •
        TwistedAlgebra.basis (scalarCocycle D ζ) (normalized_scalarCocycle D ζ) a := by
  simp only [sectionAlgebraEquiv, AlgEquiv.trans_apply,
    TwistedRescaling.congrEquiv_basis, TwistedRescaling.rescaleEquiv_basis]

@[simp] theorem sectionAlgebraEquiv_symm_basis (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (htOne : t 1 = 1) (a : A) :
    (sectionAlgebraEquiv D ζ t ht htOne).symm
      (TwistedAlgebra.basis (scalarCocycle D ζ) (normalized_scalarCocycle D ζ) a) =
      ((ζ (sectionFactor D t a))⁻¹ : ℂˣ) •
        TwistedAlgebra.basis (sectionScalarCocycle D ζ t ht)
          (normalized_sectionScalarCocycle D ζ t ht htOne) a := by
  apply (sectionAlgebraEquiv D ζ t ht htOne).injective
  simp only [AlgEquiv.apply_symm_apply, Units.smul_def, map_smul,
    sectionAlgebraEquiv_basis, smul_smul]
  simp

/-- Any two normalized sections give explicitly equivalent actual algebras. -/
def betweenSectionsEquiv (ζ : Z →* ℂˣ) (t u : A → H)
    (ht : ∀ a, D.q (t a) = a) (hu : ∀ a, D.q (u a) = a)
    (htOne : t 1 = 1) (huOne : u 1 = 1) :
    TwistedAlgebra.Algebra (sectionScalarCocycle D ζ u hu)
      (normalized_sectionScalarCocycle D ζ u hu huOne) ≃ₐ[ℂ]
        TwistedAlgebra.Algebra (sectionScalarCocycle D ζ t ht)
          (normalized_sectionScalarCocycle D ζ t ht htOne) :=
  (sectionAlgebraEquiv D ζ u hu huOne).trans (sectionAlgebraEquiv D ζ t ht htOne).symm

@[simp] theorem betweenSectionsEquiv_basis (ζ : Z →* ℂˣ) (t u : A → H)
    (ht : ∀ a, D.q (t a) = a) (hu : ∀ a, D.q (u a) = a)
    (htOne : t 1 = 1) (huOne : u 1 = 1) (a : A) :
    betweenSectionsEquiv D ζ t u ht hu htOne huOne
      (TwistedAlgebra.basis (sectionScalarCocycle D ζ u hu)
        (normalized_sectionScalarCocycle D ζ u hu huOne) a) =
      ((ζ (sectionFactor D u a) / ζ (sectionFactor D t a) : ℂˣ) : ℂ) •
        TwistedAlgebra.basis (sectionScalarCocycle D ζ t ht)
          (normalized_sectionScalarCocycle D ζ t ht htOne) a := by
  simp only [betweenSectionsEquiv, AlgEquiv.trans_apply, sectionAlgebraEquiv_basis,
    map_smul, sectionAlgebraEquiv_symm_basis, Units.smul_def, smul_smul,
    div_eq_mul_inv, Units.val_mul]

variable {V : Type*} [AddCommGroup V] [Module ℂ V]

omit [Fintype A] in
/-- The section change rescales the actual representation operators. -/
theorem sectionOperators_factor (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (σ : Representation ℂ H V)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) (a : A) :
    σ (t a) = (ζ (sectionFactor D t a) : ℂ) • σ (sectionMap D a) := by
  rw [section_factor D t ht a, map_mul, hcentral]
  change ((ζ (sectionFactor D t a) : ℂ) • (1 : Module.End ℂ V)) *
    σ (sectionMap D a) = _
  rw [smul_mul_assoc, one_mul]

omit [Fintype A] in
/-- The alternate section operators have their actual alternate cocycle. -/
theorem sectionOperators_mul (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (σ : Representation ℂ H V)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) (a b : A) :
    σ (t a) * σ (t b) = ((sectionScalarCocycle D ζ t ht).coeff a b : ℂ) •
      σ (t (a * b)) := by
  rw [← map_mul, sectionDefect_mul D t ht, map_mul, hcentral]
  change ((ζ (sectionDefect D t a b) : ℂ) • (1 : Module.End ℂ V)) *
    σ (t (a * b)) = (ζ (sectionDefect D t a b) : ℂ) • σ (t (a * b))
  rw [smul_mul_assoc, one_mul]

/-- Extend the representation along the actual basis for any normalized
section, without assuming an algebra action for that section. -/
def sectionAction (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (htOne : t 1 = 1)
    (σ : Representation ℂ H V)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    TwistedAlgebra.Algebra (sectionScalarCocycle D ζ t ht)
      (normalized_sectionScalarCocycle D ζ t ht htOne) →ₐ[ℂ] Module.End ℂ V :=
  TwistedAction.action (sectionScalarCocycle D ζ t ht)
    (normalized_sectionScalarCocycle D ζ t ht htOne) (fun a => σ (t a))
    (by rw [htOne, map_one]) (sectionOperators_mul D ζ t ht σ hcentral)

@[simp] theorem sectionAction_basis (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (htOne : t 1 = 1)
    (σ : Representation ℂ H V)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) (a : A) :
    sectionAction D ζ t ht htOne σ hcentral
      (TwistedAlgebra.basis (sectionScalarCocycle D ζ t ht)
        (normalized_sectionScalarCocycle D ζ t ht htOne) a) = σ (t a) :=
  TwistedAction.action_basis _ _ _ _ _ a

/-- The algebra action from any normalized section is exactly the canonical
action transported through the constructed section-change equivalence. -/
theorem sectionAction_eq_transport (ζ : Z →* ℂˣ) (t : A → H)
    (ht : ∀ a, D.q (t a) = a) (htOne : t 1 = 1)
    (σ : Representation ℂ H V)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    sectionAction D ζ t ht htOne σ hcentral =
      (CentralCharacter.toAlgebraAction D ζ σ hcentral).comp
        (sectionAlgebraEquiv D ζ t ht htOne).toAlgHom := by
  apply AlgHom.toLinearMap_injective
  apply (TwistedAlgebra.basis (sectionScalarCocycle D ζ t ht)
    (normalized_sectionScalarCocycle D ζ t ht htOne)).ext
  intro a
  change sectionAction D ζ t ht htOne σ hcentral _ =
    CentralCharacter.toAlgebraAction D ζ σ hcentral (sectionAlgebraEquiv D ζ t ht htOne _)
  rw [sectionAction_basis, sectionAlgebraEquiv_basis, map_smul]
  rw [CentralCharacter.toAlgebraAction_basis]
  exact sectionOperators_factor D ζ t ht σ hcentral a

/-- Two arbitrary section constructions give the same representation action
after the explicit section-change equivalence. -/
theorem sectionAction_betweenSections (ζ : Z →* ℂˣ) (t u : A → H)
    (ht : ∀ a, D.q (t a) = a) (hu : ∀ a, D.q (u a) = a)
    (htOne : t 1 = 1) (huOne : u 1 = 1) (σ : Representation ℂ H V)
    (hcentral : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id) :
    sectionAction D ζ u hu huOne σ hcentral =
      (sectionAction D ζ t ht htOne σ hcentral).comp
        (betweenSectionsEquiv D ζ t u ht hu htOne huOne).toAlgHom := by
  rw [sectionAction_eq_transport D ζ u hu huOne,
    sectionAction_eq_transport D ζ t ht htOne]
  ext x
  simp only [AlgHom.comp_apply, AlgEquiv.coe_toAlgHom, betweenSectionsEquiv,
    AlgEquiv.trans_apply, AlgEquiv.apply_symm_apply]

end PaperXI.CentralExtension
