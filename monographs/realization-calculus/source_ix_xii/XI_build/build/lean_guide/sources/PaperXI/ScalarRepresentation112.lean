import PaperXI.GlobalHeisenbergBridge112
import PaperXI.RepresentationStability
import PaperXI.ScalarCocycle112

/-! Construct an action of the actual group from labelled packet operators
and an explicit scalar cochain. The section multiplication and original theta
restriction are derived from the literal quotient kernel, not supplied as
representation or lambda hypotheses. Existence of a compatible quotient map
and preservation of any required dyadic lift remain separate obligations. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ScalarRepresentation112
open Representation

section ActualSection
variable {G A : Type*} [Group G] [Group A]
  (D : Subgroup G) [D.Normal] (θ : D →* ℂˣ)
  (hinv : TypeSideDescent.Invariant D θ)
  (q : G →* A) (hker : q.ker = D)
  (t : A → G) (ht : ∀ a, q (t a) = a) (ht1 : t 1 = 1)

/-- The literal normal-subgroup remainder of an actual group element. -/
def sectionResidue (g : G) : D :=
  ⟨g * (t (q g))⁻¹, by
    rw [← hker]
    change q (g * (t (q g))⁻¹) = 1
    simp only [map_mul, map_inv, ht, mul_inv_cancel]⟩

/-- The scalar retained from the original theta on the actual remainder. -/
def sectionScalar (g : G) : ℂˣ := θ (sectionResidue D q hker t ht g)

/-- The theta-valued factor set of the actual normalized quotient section. -/
def sectionCocycle (a b : A) : ℂˣ :=
  sectionScalar D θ q hker t ht (t a * t b)

theorem sectionResidue_mul (g h : G) :
    sectionResidue D q hker t ht (g * h) =
      sectionResidue D q hker t ht g *
        TypeSideDescent.conjugate D (t (q g)) (sectionResidue D q hker t ht h) *
          sectionResidue D q hker t ht (t (q g) * t (q h)) := by
  apply Subtype.ext
  simp only [sectionResidue, TypeSideDescent.conjugate, Subgroup.coe_mul,
    map_mul, ht]
  group

include hinv in
theorem sectionScalar_mul (g h : G) :
    sectionScalar D θ q hker t ht (g * h) =
      sectionScalar D θ q hker t ht g * sectionScalar D θ q hker t ht h *
        sectionCocycle D θ q hker t ht (q g) (q h) := by
  change θ (sectionResidue D q hker t ht (g * h)) = _
  rw [sectionResidue_mul, map_mul, map_mul, hinv]
  rfl

omit [D.Normal] in
theorem sectionResidue_section (a : A) : sectionResidue D q hker t ht (t a) = 1 := by
  apply Subtype.ext
  simp only [sectionResidue, ht, mul_inv_cancel, Subgroup.coe_one]

omit [D.Normal] in
theorem sectionScalar_section (a : A) : sectionScalar D θ q hker t ht (t a) = 1 := by
  rw [sectionScalar, sectionResidue_section, map_one]

omit [D.Normal] in
include ht1 in
theorem sectionScalar_one : sectionScalar D θ q hker t ht 1 = 1 := by
  simpa only [ht1] using sectionScalar_section D θ q hker t ht 1

omit [D.Normal] in
include ht1 in
theorem sectionCocycle_one_left (a : A) : sectionCocycle D θ q hker t ht 1 a = 1 := by
  simpa only [sectionCocycle, ht1, one_mul] using sectionScalar_section D θ q hker t ht a

omit [D.Normal] in
include ht1 in
theorem sectionCocycle_one_right (a : A) : sectionCocycle D θ q hker t ht a 1 = 1 := by
  simpa only [sectionCocycle, ht1, mul_one] using sectionScalar_section D θ q hker t ht a

include hinv in
/-- Associativity of the scalar factor set is derived from actual group
associativity and invariance of the same original theta. -/
theorem sectionCocycle_assoc (a b c : A) :
    sectionCocycle D θ q hker t ht a b * sectionCocycle D θ q hker t ht (a * b) c =
      sectionCocycle D θ q hker t ht b c * sectionCocycle D θ q hker t ht a (b * c) := by
  have h := congrArg (sectionScalar D θ q hker t ht) (mul_assoc (t a) (t b) (t c))
  simpa only [sectionScalar_mul D θ hinv, sectionScalar_section, ht, map_mul,
    one_mul, mul_one] using h

omit [D.Normal] in
include ht1 in
theorem sectionScalar_on_subgroup (d : D) :
    sectionScalar D θ q hker t ht (d : G) = θ d := by
  have hd : q (d : G) = 1 := by
    change (d : G) ∈ q.ker
    rw [hker]
    exact d.property
  apply congrArg θ
  apply Subtype.ext
  simp only [sectionResidue, hd, ht1, inv_one, mul_one]

end ActualSection

section PacketOperators
variable {P A V : Type*} [Group P] [Group A] [AddCommGroup V] [Module ℂ V]
  (H : Subgroup P) [H.Normal] (χ : H →* ℂˣ)
  (q : P →* A) (hker : q.ker = H) (t : A → P) (ht : ∀ a, q (t a) = a)
  (ρ : Representation ℂ P V)
  (hρ : ∀ h : H, ρ h = (χ h : ℂ) • LinearMap.id)

/-- The packet's operators retain their quotient labels. -/
def packetOperator (a : A) : Module.End ℂ V := ρ (t a)

omit [H.Normal] in
include hρ in
/-- The projective multiplication coefficient is the literal scalar
character of the actual section remainder. -/
theorem packetOperator_mul (a b : A) :
    packetOperator t ρ a * packetOperator t ρ b =
      (sectionCocycle H χ q hker t ht a b : ℂ) • packetOperator t ρ (a * b) := by
  have hg : t a * t b =
      (sectionResidue H q hker t ht (t a * t b) : P) * t (a * b) := by
    simp only [sectionResidue, map_mul, ht]
    group
  change ρ (t a) * ρ (t b) = _
  rw [← map_mul, hg, map_mul, hρ]
  ext v
  simp only [Module.End.mul_apply, LinearMap.smul_apply, LinearMap.id_apply,
    sectionCocycle, sectionScalar, packetOperator]

end PacketOperators

section ScalarTransport
variable {G P A V : Type*} [Group G] [Group P] [Group A]
  [AddCommGroup V] [Module ℂ V]
  (D : Subgroup G) [D.Normal] (θ : D →* ℂˣ)
  (hinv : TypeSideDescent.Invariant D θ)
  (q : G →* A) (hker : q.ker = D)
  (t : A → G) (ht : ∀ a, q (t a) = a) (ht1 : t 1 = 1)
  (H : Subgroup P) [H.Normal] (χ : H →* ℂˣ)
  (r : P →* A) (hkerP : r.ker = H)
  (u : A → P) (hu : ∀ a, r (u a) = a) (hu1 : u 1 = 1)
  (ρ : Representation ℂ P V)
  (hρ : ∀ h : H, ρ h = (χ h : ℂ) • LinearMap.id)
  (s : A → ℂˣ) (hs1 : s 1 = 1)
  (hc : ∀ a b, sectionCocycle D θ q hker t ht a b =
    (s a * s b / s (a * b)) * sectionCocycle H χ r hkerP u hu a b)

/-- A scalar cochain constructs an honest representation of the actual group,
even when the packet center and actual center have different orders. -/
def scalarTransport : Representation ℂ G V where
  toFun g := ((sectionScalar D θ q hker t ht g * s (q g) : ℂˣ) : ℂ) • ρ (u (q g))
  map_one' := by
    simp only [map_one, sectionScalar_one D θ q hker t ht ht1, hs1,
      hu1, mul_one, Units.val_one, one_smul]
  map_mul' g h := by
    have hcoeff :
        sectionScalar D θ q hker t ht (g * h) * s (q (g * h)) =
          (sectionScalar D θ q hker t ht g * s (q g)) *
          (sectionScalar D θ q hker t ht h * s (q h)) *
            sectionCocycle H χ r hkerP u hu (q g) (q h) := by
      rw [sectionScalar_mul D θ hinv, hc, map_mul]
      simp only [div_eq_mul_inv]
      simp [mul_assoc, mul_comm, mul_left_comm]
    ext v
    rw [hcoeff, map_mul]
    have hp := LinearMap.congr_fun (packetOperator_mul H χ r hkerP u hu ρ hρ (q g) (q h)) v
    change ρ (u (q g)) (ρ (u (q h)) v) = _ at hp
    simp only [LinearMap.smul_apply, Units.val_mul, Module.End.mul_apply,
      map_smul, smul_smul]
    rw [hp]
    simp only [LinearMap.smul_apply, packetOperator, smul_smul]
    congr 1
    ring

omit [H.Normal] in
/-- The constructed actual action contains precisely the original theta on
the original subgroup, rather than a replacement central character. -/
theorem scalarTransport_on_subgroup (d : D) :
    scalarTransport D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc (d : G) =
      (θ d : ℂ) • LinearMap.id := by
  have hd : q (d : G) = 1 := by
    change (d : G) ∈ q.ker
    rw [hker]
    exact d.property
  change ((sectionScalar D θ q hker t ht (d : G) * s (q (d : G)) : ℂˣ) : ℂ) •
    ρ (u (q (d : G))) = _
  rw [sectionScalar_on_subgroup D θ q hker t ht ht1, hd, hs1, hu1, map_one, mul_one]
  rfl

omit [H.Normal] in
/-- On each actual quotient-section element the representation is the packet
operator with exactly its derived scalar-cochain correction. -/
theorem scalarTransport_section (a : A) :
    scalarTransport D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc (t a) =
      (s a : ℂ) • ρ (u a) := by
  change ((sectionScalar D θ q hker t ht (t a) * s (q (t a)) : ℂˣ) : ℂ) •
    ρ (u (q (t a))) = _
  rw [sectionScalar_section, ht, one_mul]

omit [H.Normal] in
include hρ in
/-- Every packet operator is its section-labelled operator times its original
scalar remainder. This is an actual group identity, not a dimension argument. -/
theorem packet_normalForm (p : P) :
    ρ p = (sectionScalar H χ r hkerP u hu p : ℂ) • ρ (u (r p)) := by
  have hp : p = (sectionResidue H r hkerP u hu p : P) * u (r p) := by
    simp only [sectionResidue]
    group
  calc
    ρ p = ρ ((sectionResidue H r hkerP u hu p : P) * u (r p)) := congrArg ρ hp
    _ = _ := by
      rw [map_mul, hρ]
      ext v
      simp only [Module.End.mul_apply, LinearMap.smul_apply, LinearMap.id_apply, sectionScalar]

omit [H.Normal] in
/-- The rescaled actual action is irreducible because every original packet
operator preserves each of its stable subspaces. No target eta iso is used. -/
theorem scalarTransport_irreducible [IsIrreducible ρ] :
    IsIrreducible (scalarTransport D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc) := by
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space ρ
  apply RepresentationStability.irreducible_of_stable
  intro S hS
  apply RepresentationStability.eq_bot_or_top ρ S
  intro p v hv
  have hRv : ρ (u (r p)) v ∈ S := by
    have hx := hS (t (r p)) v hv
    have hs := S.smul_mem (((s (r p))⁻¹ : ℂˣ) : ℂ) hx
    rw [scalarTransport_section D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc] at hs
    simpa only [LinearMap.smul_apply, smul_smul, ← Units.val_mul,
      inv_mul_cancel, Units.val_one, one_smul] using hs
  rw [packet_normalForm H χ r hkerP u hu ρ hρ]
  exact S.smul_mem _ hRv

omit [H.Normal] in
/-- The actual theta occurrence is a conclusion of the transport on the
nonzero original packet carrier. -/
theorem scalarTransport_contains [Nontrivial V] :
    TypeSideDescent.Contains D θ
      (scalarTransport D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc) := by
  obtain ⟨v, hv⟩ := exists_ne (0 : V)
  refine ⟨v, hv, fun d => ?_⟩
  rw [scalarTransport_on_subgroup D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc]
  rfl

end ScalarTransport

section CochainExistence
variable {G P A V : Type*} [Group G] [Group P] [CommGroup A]
  [AddCommGroup V] [Module ℂ V]

/-- The scalar cocycle is constructed from the original character and actual
section, with all cocycle laws proved above. -/
def actualScalarCocycle
    (D : Subgroup G) [D.Normal] (θ : D →* ℂˣ)
    (hinv : TypeSideDescent.Invariant D θ)
    (q : G →* A) (hker : q.ker = D)
    (t : A → G) (ht : ∀ a, q (t a) = a) (ht1 : t 1 = 1) :
    ScalarCocycle112.Cocycle A ℂˣ where
  coeff := sectionCocycle D θ q hker t ht
  assoc := sectionCocycle_assoc D θ hinv q hker t ht
  one_left := sectionCocycle_one_left D θ q hker t ht ht1
  one_right := sectionCocycle_one_right D θ q hker t ht ht1

/-- The actual character commutator with the quotient label retained. -/
def sectionCommutator
    (D : Subgroup G) (q : G →* A) (hker : q.ker = D)
    (t : A → G) (ht : ∀ a, q (t a) = a) (a b : A) : D :=
  ⟨t a * t b * (t a)⁻¹ * (t b)⁻¹, by
    rw [← hker]
    change q (t a * t b * (t a)⁻¹ * (t b)⁻¹) = 1
    simp only [map_mul, map_inv, ht]
    simp [mul_assoc]⟩

/-- The scalar cocycle commutator is the original theta of the literal group
commutator. This translates quotient-form matching into the cochain theorem. -/
theorem sectionCocycle_commutator
    (D : Subgroup G) (θ : D →* ℂˣ)
    (q : G →* A) (hker : q.ker = D)
    (t : A → G) (ht : ∀ a, q (t a) = a) (a b : A) :
    sectionCocycle D θ q hker t ht a b / sectionCocycle D θ q hker t ht b a =
      θ (sectionCommutator D q hker t ht a b) := by
  have hz : sectionResidue D q hker t ht (t a * t b) /
      sectionResidue D q hker t ht (t b * t a) = sectionCommutator D q hker t ht a b := by
    apply Subtype.ext
    simp only [sectionResidue, sectionCommutator, Subgroup.coe_div, map_mul, ht]
    rw [mul_comm b a]
    simp only [div_eq_mul_inv]
    group
  change θ (sectionResidue D q hker t ht (t a * t b)) /
    θ (sectionResidue D q hker t ht (t b * t a)) = _
  rw [← map_div, hz]

/-- Equal labelled scalar commutators construct an honest irreducible actual
group action containing the literal original theta. The packet and actual
central subgroups need not be isomorphic. -/
theorem exists_actual_action_of_equal_scalar_commutators
    (D : Subgroup G) [D.Normal] (θ : D →* ℂˣ)
    (hinv : TypeSideDescent.Invariant D θ)
    (q : G →* A) (hker : q.ker = D)
    (t : A → G) (ht : ∀ a, q (t a) = a) (ht1 : t 1 = 1)
    (H : Subgroup P) [H.Normal] (χ : H →* ℂˣ)
    (hχ : TypeSideDescent.Invariant H χ)
    (r : P →* A) (hkerP : r.ker = H)
    (u : A → P) (hu : ∀ a, r (u a) = a) (hu1 : u 1 = 1)
    (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (hρ : ∀ h : H, ρ h = (χ h : ℂ) • LinearMap.id)
    (hcomm : ∀ a b,
      sectionCocycle D θ q hker t ht a b / sectionCocycle D θ q hker t ht b a =
        sectionCocycle H χ r hkerP u hu a b / sectionCocycle H χ r hkerP u hu b a) :
    ∃ Ξ : Representation ℂ G V,
      IsIrreducible Ξ ∧ TypeSideDescent.Contains D θ Ξ ∧
        (∀ d : D, Ξ d = (θ d : ℂ) • LinearMap.id) := by
  let cθ := actualScalarCocycle D θ hinv q hker t ht ht1
  let cP := actualScalarCocycle H χ hχ r hkerP u hu hu1
  obtain ⟨s, hs1, hc⟩ := ScalarCocycle112.same_commutator_exists_cochain cθ cP hcomm
  let Ξ := scalarTransport D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc
  let : Nontrivial V := GeneratedIrreducibility.nontrivial_space ρ
  exact ⟨Ξ, scalarTransport_irreducible D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc,
    scalarTransport_contains D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc,
    scalarTransport_on_subgroup D θ hinv q hker t ht ht1 H χ r hkerP u hu hu1 ρ hρ s hs1 hc⟩

end CochainExistence

section PrescribedEta
variable {G P A V W k X : Type*} [Group G] [Finite G] [Group P] [CommGroup A]
  [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]
  [Field k] [AddCommGroup X] [Module k X]

/-- The constructed packet realization is identified with the prescribed
actual eta using nondegenerate original quotient data. Equality of commutator
characters replaces a literal central-extension group isomorphism. For an
infinite J¹ this theorem is used on its actual finite J¹/ker(theta) quotient. -/
theorem bridge_to_prescribed_eta_of_equal_commutators
    (D : Subgroup G) [D.Normal] (θ : D →* ℂˣ)
    (hinv : TypeSideDescent.Invariant D θ)
    (q : G →* A) (hker : q.ker = D)
    (t : A → G) (ht : ∀ a, q (t a) = a) (ht1 : t 1 = 1)
    (H : Subgroup P) [H.Normal] (χ : H →* ℂˣ)
    (hχ : TypeSideDescent.Invariant H χ)
    (r : P →* A) (hkerP : r.ker = H)
    (u : A → P) (hu : ∀ a, r (u a) = a) (hu1 : u 1 = 1)
    (ρ : Representation ℂ P V) [IsIrreducible ρ]
    (hρ : ∀ h : H, ρ h = (χ h : ℂ) • LinearMap.id)
    (hcomm : ∀ a b, θ (sectionCommutator D q hker t ht a b) =
      χ (sectionCommutator H r hkerP u hu a b))
    (η : Representation ℂ G W) [IsIrreducible η]
    (hcontains : TypeSideDescent.Contains D θ η)
    (τ : (G ⧸ D) ≃* Multiplicative X)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ z : X, B z v = 0) → v = 0)
    (hform : ∀ g h : G, ψ (B (HeisenbergCharacterProfile111.coordinate D τ g)
      (HeisenbergCharacterProfile111.coordinate D τ h)) =
        HeisenbergCharacterProfile111.characterCommutator D τ θ g h) :
    ∃ Ξ : Representation ℂ G V,
      IsIrreducible Ξ ∧ TypeSideDescent.Contains D θ Ξ ∧
        Nonempty (Representation.Equiv Ξ η) := by
  have hc : ∀ a b,
      sectionCocycle D θ q hker t ht a b / sectionCocycle D θ q hker t ht b a =
        sectionCocycle H χ r hkerP u hu a b / sectionCocycle H χ r hkerP u hu b a := by
    intro a b
    rw [sectionCocycle_commutator, sectionCocycle_commutator, hcomm]
  obtain ⟨Ξ, hΞ, hcontainsΞ, hscalarΞ⟩ :=
    exists_actual_action_of_equal_scalar_commutators D θ hinv q hker t ht ht1
      H χ hχ r hkerP u hu hu1 ρ hρ hc
  let : IsIrreducible Ξ := hΞ
  exact ⟨Ξ, hΞ, hcontainsΞ,
    GlobalHeisenbergBridge112.equiv_of_common_quotient_form D θ τ B ψ hψ hnd hform
      Ξ η hscalarΞ (TypeSideDescent.scalar_restriction D θ hinv η hcontains)⟩

end PrescribedEta

end PaperXI.ScalarRepresentation112
