import PaperXI.LineCharacter
import Mathlib.RepresentationTheory.Induced

/-! Actual induction from the stabilizer of a nonzero monomial basis line. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonomialInduction
open Representation Module
variable {G V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]

/-- The one dimensional representation belonging to a scalar character. -/
def scalarRepresentation {H : Type*} [Group H] (χ : H →* ℂˣ) : Representation ℂ H ℂ where
  toFun h := (χ h : ℂ) • LinearMap.id
  map_one' := by ext; simp
  map_mul' h k := by ext; simp [smul_smul, mul_comm]

@[simp] theorem scalarRepresentation_apply {H : Type*} [Group H] (χ : H →* ℂˣ)
    (h : H) (a : ℂ) : scalarRepresentation χ h a = (χ h : ℂ) * a := rfl

variable (ρ : Representation ℂ G V) (v : V) (hv : v ≠ 0)

abbrev stabilizer := LineCharacter.lineStabilizer ρ v
abbrev character := LineCharacter.character ρ v hv
abbrev lineRepresentation := scalarRepresentation (character ρ v hv)
abbrev induced := Representation.ind (stabilizer ρ v).subtype (lineRepresentation ρ v hv)
abbrev InducedSpace := Representation.IndV (stabilizer ρ v).subtype (lineRepresentation ρ v hv)

/-- Inclusion of the character line into the restricted representation. -/
def lineMap : Representation.IntertwiningMap (lineRepresentation ρ v hv)
    (ρ.comp (stabilizer ρ v).subtype) :=
  ⟨LinearMap.toSpanSingleton ℂ V v, by
    intro h
    apply LinearMap.ext
    intro a
    change ((character ρ v hv h : ℂ) * a) • v = ρ (h : G) (a • v)
    rw [map_smul, LineCharacter.character_action ρ v hv h]
    simp [smul_smul, mul_comm]⟩

/-- The universal induced map is evaluated in the original representation. -/
def evaluation : Representation.IntertwiningMap (induced ρ v hv) ρ :=
  ⟨Representation.Coinvariants.lift _
    (TensorProduct.lift <| (Finsupp.lift _ _ _ fun h : G =>
      ρ h⁻¹ ∘ₗ (lineMap ρ v hv).toLinearMap) ∘ₗ
      (MonoidAlgebra.coeffLinearEquiv ℂ).toLinearMap)
    (fun g => by
      ext h
      simp only [LinearMap.coe_comp, Function.comp_apply, MonoidAlgebra.lsingle_apply]
      simp [Representation.ofMulAction_single, mul_inv_rev,
        -scalarRepresentation_apply, (lineMap ρ v hv).isIntertwining]),
    fun g => by ext; simp⟩

@[simp] theorem evaluation_mk (g : G) (a : ℂ) :
    evaluation ρ v hv (IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv) g a) =
      a • ρ g⁻¹ v := by
  simp [evaluation, lineMap, map_smul]

/-- The actual quotient relation for a stabilizer scalar. -/
theorem mk_stabilizer (h : stabilizer ρ v) (g : G) (a : ℂ) :
    IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv)
      ((h : G)⁻¹ * g) a =
    IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv)
      g ((character ρ v hv h : ℂ) * a) := by
  have hh := Coinvariants.mk_inv_tmul
    ((Representation.leftRegular ℂ G).comp (stabilizer ρ v).subtype)
    (lineRepresentation ρ v hv) (MonoidAlgebra.single g 1) a h
  simpa using hh

variable {X : Type*} (b : Basis X ℂ V) (r : X → G) (a : X → ℂˣ)

/-- An explicit inverse, using the given basis and actual orbit representatives. -/
def reconstruction : V →ₗ[ℂ] InducedSpace ρ v hv :=
  b.constr ℂ fun i => (a i : ℂ)⁻¹ •
    IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv) (r i)⁻¹ 1

@[simp] theorem reconstruction_basis (i : X) :
    reconstruction ρ v hv b r a (b i) = (a i : ℂ)⁻¹ •
      IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv) (r i)⁻¹ 1 :=
  b.constr_basis ℂ _ i

variable (hr : ∀ i, ρ (r i) v = (a i : ℂ) • b i)

include hr in
theorem evaluation_reconstruction :
    (evaluation ρ v hv).toLinearMap ∘ₗ reconstruction ρ v hv b r a = LinearMap.id := by
  apply b.ext
  intro i
  change evaluation ρ v hv (reconstruction ρ v hv b r a (b i)) = b i
  rw [reconstruction_basis, map_smul, evaluation_mk]
  simp [hr, smul_smul]

include hr in
theorem representative_inverse (i : X) : ρ (r i)⁻¹ (b i) = (a i : ℂ)⁻¹ • v := by
  apply (ρ.apply_bijective (r i)).injective
  simp [hr, smul_smul]

/- Any group translate of the distinguished vector remains in one basis line. -/
variable (hmono : ∀ g : G, ∃ i : X, ∃ d : ℂˣ, ρ g v = (d : ℂ) • b i)

include hr hmono in
theorem reconstruction_evaluation :
    reconstruction ρ v hv b r a ∘ₗ (evaluation ρ v hv).toLinearMap = LinearMap.id := by
  apply IndV.hom_ext
  intro g
  apply LinearMap.ext_ring
  obtain ⟨i, d, hd⟩ := hmono g⁻¹
  have hk : (r i)⁻¹ * g⁻¹ ∈ stabilizer ρ v := by
    refine ⟨(d : ℂ) * (a i : ℂ)⁻¹, ?_⟩
    simp [map_mul, Module.End.mul_apply, hd,
      representative_inverse ρ v b r a hr i, smul_smul]
  let k : stabilizer ρ v := ⟨(r i)⁻¹ * g⁻¹, hk⟩
  have hc : (character ρ v hv k : ℂ) = (d : ℂ) * (a i : ℂ)⁻¹ := by
    apply LineCharacter.scalar_unique hv
    rw [← LineCharacter.character_action]
    change ρ ((r i)⁻¹ * g⁻¹) v = _
    simp [map_mul, Module.End.mul_apply, hd,
      representative_inverse ρ v b r a hr i, smul_smul]
  have hm := mk_stabilizer ρ v hv k (r i)⁻¹ 1
  have hm' : IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv) g 1 =
      ((d : ℂ) * (a i : ℂ)⁻¹) •
        IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv) (r i)⁻¹ 1 := by
    have hh : ((k : G)⁻¹ * (r i)⁻¹) = g := by simp [k, mul_assoc]
    rw [hh, hc, mul_one] at hm
    calc
      _ = IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv)
        (r i)⁻¹ ((d : ℂ) * (a i : ℂ)⁻¹) := hm
      _ = _ := by rw [← map_smul]; simp only [smul_eq_mul, mul_one]
  change reconstruction ρ v hv b r a
      (evaluation ρ v hv (IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv) g 1)) = _
  rw [evaluation_mk, one_smul, hd, map_smul, reconstruction_basis, smul_smul]
  exact hm'.symm

include hr hmono in
theorem evaluation_bijective : Function.Bijective (evaluation ρ v hv) := by
  constructor
  · exact Function.HasLeftInverse.injective
      ⟨reconstruction ρ v hv b r a, fun x =>
        LinearMap.congr_fun (reconstruction_evaluation ρ v hv b r a hr hmono) x⟩
  · exact Function.HasRightInverse.surjective
      ⟨reconstruction ρ v hv b r a, fun x =>
        LinearMap.congr_fun (evaluation_reconstruction ρ v hv b r a hr) x⟩

/-- A transitive monomial basis identifies the original representation with the
actual Mathlib induction of the scalar character on its line stabilizer. -/
def equivalence : Representation.Equiv (induced ρ v hv) ρ :=
  (evaluation ρ v hv).ofBijective (evaluation_bijective ρ v hv b r a hr hmono)

@[simp] theorem equivalence_mk (g : G) (z : ℂ) :
    equivalence ρ v hv b r a hr hmono
      (IndV.mk (stabilizer ρ v).subtype (lineRepresentation ρ v hv) g z) =
      z • ρ g⁻¹ v := evaluation_mk ρ v hv g z

end PaperXI.MonomialInduction
