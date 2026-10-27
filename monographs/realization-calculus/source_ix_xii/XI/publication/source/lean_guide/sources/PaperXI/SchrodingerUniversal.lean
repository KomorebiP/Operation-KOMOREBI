import PaperXI.HeisenbergNormalForm
import PaperXI.HeisenbergFrequency
import PaperXI.HeisenbergDimension
import PaperXI.HeisenbergRepresentation
import PaperXI.SchurScalar
import Mathlib.LinearAlgebra.StdBasis

/-! The actual map from the Schrödinger model, built from a nonzero vector
fixed by all modulations, and its representation equivalence. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SchrodingerUniversal
open PaperXI.Heisenberg
variable {K X W : Type*} [Field K] [AddCommGroup X] [Module K X] [Fintype X]
variable [AddCommGroup W] [Module ℂ W]

/-- The coordinate basis vector at `a` maps to `σ(T_(-a)) w₀`. -/
def basis_map (σ : Representation ℂ (Element K X) W) (w₀ : W) :
    (X → ℂ) →ₗ[ℂ] W :=
  (Pi.basisFun ℂ X).constr ℂ (fun a => σ (translationElement (-a)) w₀)

@[simp] theorem basis_map_basis (σ : Representation ℂ (Element K X) W)
    (w₀ : W) (a : X) :
    basis_map σ w₀ (Pi.basisFun ℂ X a) = σ (translationElement (-a)) w₀ := by
  exact (Pi.basisFun ℂ X).constr_basis ℂ _ a

/-- With the manuscript convention, translation moves `δ_a` to `δ_(a-x)`. -/
theorem translation_basis (x a : X) :
    Schrodinger.translation x (Pi.basisFun ℂ X a) = Pi.basisFun ℂ X (a - x) := by
  classical
  ext u
  simp [Pi.single_apply, ← eq_sub_iff_add_eq]

theorem modulation_basis (ψ : AddChar K ℂ) (ξ : Module.Dual K X) (a : X) :
    Schrodinger.modulation ψ ξ (Pi.basisFun ℂ X a) = ψ (ξ a) • Pi.basisFun ℂ X a := by
  classical
  ext u
  by_cases h : u = a
  · subst u
    simp
  · simp [h]

theorem basis_map_translation (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) (w₀ : W) (x : X) :
    (basis_map σ w₀).comp (representation ψ h2 (translationElement x)) =
      (σ (translationElement x)).comp (basis_map σ w₀) := by
  apply (Pi.basisFun ℂ X).ext
  intro a
  simp only [LinearMap.comp_apply, translation_action, translation_basis, basis_map_basis]
  change σ (translationElement (-(a - x))) w₀ =
    (σ (translationElement x) * σ (translationElement (-a))) w₀
  rw [← map_mul, translationElement_mul]
  congr 2
  abel_nf

theorem basis_map_modulation (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W)
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id)
    (w₀ : W) (hfixed : ∀ ξ, σ (modulationElement ξ) w₀ = w₀)
    (ξ : Module.Dual K X) :
    (basis_map σ w₀).comp (representation ψ h2 (modulationElement ξ)) =
      (σ (modulationElement ξ)).comp (basis_map σ w₀) := by
  apply (Pi.basisFun ℂ X).ext
  intro a
  simp only [LinearMap.comp_apply, modulation_action, modulation_basis, map_smul,
    basis_map_basis]
  change ψ (ξ a) • σ (translationElement (-a)) w₀ =
    (σ (modulationElement ξ) * σ (translationElement (-a))) w₀
  rw [← map_mul, modulation_translation h2, map_mul, map_mul, hcentral]
  simp [hfixed]

theorem basis_map_central (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W)
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id)
    (w₀ : W) (z : K) :
    (basis_map σ w₀).comp (representation ψ h2 (centralElement z)) =
      (σ (centralElement z)).comp (basis_map σ w₀) := by
  rw [central_action, hcentral]
  ext f
  simp

/-- Generator intertwinement extends to every actual group element by its normal form. -/
theorem intertwines (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W)
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id)
    (w₀ : W) (hfixed : ∀ ξ, σ (modulationElement ξ) w₀ = w₀)
    (g : Element K X) :
    (basis_map σ w₀).comp (representation ψ h2 g) =
      (σ g).comp (basis_map σ w₀) := by
  have hc := basis_map_central ψ h2 σ hcentral w₀
  have ht := basis_map_translation ψ h2 σ w₀
  have hm := basis_map_modulation ψ h2 σ hcentral w₀ hfixed
  rw [normal_form g]
  ext f
  simp only [map_mul, LinearMap.comp_apply, Module.End.mul_apply]
  have hc' (z : K) (v : X → ℂ) := LinearMap.congr_fun (hc z) v
  have ht' (x : X) (v : X → ℂ) := LinearMap.congr_fun (ht x) v
  have hm' (ξ : Module.Dual K X) (v : X → ℂ) := LinearMap.congr_fun (hm ξ) v
  simp only [LinearMap.comp_apply] at hc' ht' hm'
  rw [hc', ht', hm']

/-- The constructed map bundled with the actual representation actions. -/
def intertwiningMap (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W)
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id)
    (w₀ : W) (hfixed : ∀ ξ, σ (modulationElement ξ) w₀ = w₀) :
    Representation.IntertwiningMap (representation ψ h2) σ :=
  ⟨basis_map σ w₀, intertwines ψ h2 σ hcentral w₀ hfixed⟩

/-- The map is nonzero because its value at the origin basis vector is `w₀`. -/
theorem intertwiningMap_ne_zero (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W)
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id)
    (w₀ : W) (hw₀ : w₀ ≠ 0) (hfixed : ∀ ξ, σ (modulationElement ξ) w₀ = w₀) :
    intertwiningMap ψ h2 σ hcentral w₀ hfixed ≠ 0 := by
  intro h
  have hh := congrArg (fun F : Representation.IntertwiningMap (representation ψ h2) σ =>
    F (Pi.basisFun ℂ X 0)) h
  exact hw₀ (by simpa [intertwiningMap] using hh)

/-- Irreducibility of both actual actions proves bijectivity; it is not assumed. -/
def equiv_of_fixed (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id)
    (w₀ : W) (hw₀ : w₀ ≠ 0) (hfixed : ∀ ξ, σ (modulationElement ξ) w₀ = w₀) :
    Representation.Equiv (representation ψ h2) σ := by
  letI : Representation.IsIrreducible (representation (X := X) ψ h2) :=
    irreducible ψ hψ h2
  exact (intertwiningMap ψ h2 σ hcentral w₀ hfixed).ofBijective
    ((Representation.IsIrreducible.bijective_or_eq_zero _).resolve_right
      (intertwiningMap_ne_zero ψ h2 σ hcentral w₀ hw₀ hfixed))

variable [Fintype (Module.Dual K X)] [FiniteDimensional K X]

/-- Finite Stone–von Neumann for the actual odd-characteristic coordinate group:
every irreducible representation with central character `ψ ≠ 1` is the model.
The fixed vector, bijectivity, and target dimension are conclusions of the proof. -/
theorem exists_equiv (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id) :
    Nonempty (Representation.Equiv (representation ψ h2) σ) := by
  let : Nontrivial W := GeneratedIrreducibility.nontrivial_space σ
  obtain ⟨w₀, hw₀, hfixed⟩ :=
    HeisenbergFrequency.nonzero_zero_fiber ψ hψ h2 σ hcentral
  exact ⟨equiv_of_fixed ψ hψ h2 σ hcentral w₀ hw₀ hfixed⟩

/-- A chosen actual equivalence supplied by finite Stone–von Neumann. -/
def equiv (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id) :
    Representation.Equiv (representation ψ h2) σ :=
  Classical.choice (exists_equiv ψ hψ h2 σ hcentral)

/-- The chosen linear equivalence intertwines every actual group element. -/
theorem equiv_intertwines (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id)
    (g : Element K X) (f : X → ℂ) :
    equiv ψ hψ h2 σ hcentral ((representation ψ h2 g) f) =
      σ g (equiv ψ hψ h2 σ hcentral f) :=
  Representation.IntertwiningMap.isIntertwining (representation ψ h2) σ
    (equiv ψ hψ h2 σ hcentral).toIntertwiningMap g f

/-- Finite dimensionality of the arbitrary irreducible target is transported
from the constructed model equivalence. -/
theorem finiteDimensional (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id) :
    FiniteDimensional ℂ W := by
  let U := (equiv ψ hψ h2 σ hcentral).toLinearEquiv
  exact FiniteDimensional.of_injective U.symm.toLinearMap U.symm.injective

/-- The actual target dimension is the number of position coordinates. -/
theorem finrank_eq (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id) :
    Module.finrank ℂ W = Fintype.card X := by
  rw [← (equiv ψ hψ h2 σ hcentral).toLinearEquiv.finrank_eq]
  exact Module.finrank_fintype_fun_eq_card ℂ

/-- The target dimension equals the square root of the symplectic quotient order. -/
theorem finrank_eq_sqrt (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id) :
    Module.finrank ℂ W = Nat.sqrt (Nat.card (X × Module.Dual K X)) := by
  rw [finrank_eq ψ hψ h2 σ hcentral, HeisenbergDimension.sqrt_natCard_symplectic,
    Nat.card_eq_fintype_card]

/-- Every invertible intertwiner differs from the constructed equivalence
by a unique nonzero complex scalar. -/
theorem unique_scalar (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id)
    (T : (X → ℂ) ≃ₗ[ℂ] W)
    (hT : ∀ g f, T ((representation ψ h2 g) f) = σ g (T f)) :
    ∃! c : ℂˣ, ∀ f, T f = (c : ℂ) • equiv ψ hψ h2 σ hcentral f := by
  let : Representation.IsIrreducible (representation (X := X) ψ h2) :=
    irreducible ψ hψ h2
  exact SchurScalar.bridge_unique (representation ψ h2) σ
    (equiv ψ hψ h2 σ hcentral).toLinearEquiv T
    (equiv_intertwines ψ hψ h2 σ hcentral) hT

omit [Fintype X] [Fintype (Module.Dual K X)] in
/-- The finite-field formulation needs no separately supplied enumeration
of the position or dual space. -/
theorem exists_equiv_finiteField [Finite K]
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W) [Representation.IsIrreducible σ]
    (hcentral : ∀ z, σ (centralElement z) = ψ z • LinearMap.id) :
    Nonempty (Representation.Equiv (representation ψ h2) σ) := by
  let : Finite X := Module.finite_of_finite K
  let : Finite (Module.Dual K X) := Module.finite_of_finite K
  let : Fintype X := Fintype.ofFinite X
  let : Fintype (Module.Dual K X) := Fintype.ofFinite (Module.Dual K X)
  exact exists_equiv ψ hψ h2 σ hcentral

end PaperXI.SchrodingerUniversal
