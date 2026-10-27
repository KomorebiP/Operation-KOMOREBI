import PaperXI.DegreeIndex110
import Mathlib.Algebra.Group.AddChar
import Mathlib.Tactic.Group

/-! The original type-side quotient/form datum derives trace support through
actual commutators. Character intertwining of the original one-dimensional
theta is equivalent to its covariance on the literal intersection. Neither
result assumes the desired eta intertwiner or eta intersection dimension. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergCharacterProfile111
open Representation

section QuotientForm
variable {K k X W : Type*} [Group K] [Field k] [AddCommGroup X] [Module k X]
  [AddCommGroup W] [Module ℂ W]
  (H : Subgroup K) [H.Normal]

/-- Literal coordinates on the original K/H quotient, not on a substitute
finite group. Their multiplicative target is the additive vector-space group. -/
def coordinate (τ : (K ⧸ H) ≃* Multiplicative X) (x : K) : X :=
  Multiplicative.toAdd (τ (QuotientGroup.mk' H x))

theorem coordinate_surjective (τ : (K ⧸ H) ≃* Multiplicative X) :
    Function.Surjective (coordinate H τ) := by
  intro v
  obtain ⟨a, ha⟩ := τ.surjective (Multiplicative.ofAdd v)
  obtain ⟨x, rfl⟩ := QuotientGroup.mk_surjective a
  exact ⟨x, congrArg Multiplicative.toAdd ha⟩

theorem coordinate_eq_zero_iff (τ : (K ⧸ H) ≃* Multiplicative X) (x : K) :
    coordinate H τ x = 0 ↔ x ∈ H := by
  change τ (QuotientGroup.mk' H x) = 1 ↔ x ∈ H
  constructor
  · intro h
    apply (QuotientGroup.eq_one_iff (N := H) x).mp
    exact τ.injective (h.trans (map_one τ).symm)
  · intro h
    have hh : QuotientGroup.mk' H x = 1 := (QuotientGroup.eq_one_iff (N := H) x).mpr h
    exact hh ▸ map_one τ

/-- A vector-space coordinate isomorphism makes every original commutator
belong to H. No commutator-membership premise is supplied separately. -/
theorem commutator_mem (τ : (K ⧸ H) ≃* Multiplicative X) (x y : K) :
    x * y * x⁻¹ * y⁻¹ ∈ H := by
  apply (QuotientGroup.eq_one_iff (N := H) _).mp
  apply τ.injective
  simp [map_mul, map_inv, mul_assoc]

/-- Theta evaluated on the actual group commutator, with source convention
`[x,y] = x*y*x⁻¹*y⁻¹`. -/
def characterCommutator (τ : (K ⧸ H) ≃* Multiplicative X)
    (θ : H →* ℂˣ) (x y : K) : ℂˣ :=
  θ ⟨x * y * x⁻¹ * y⁻¹, commutator_mem H τ x y⟩

/-- Nondegeneracy of the declared field-valued commutator form produces an
actual trace detector. A nontrivial additive character need not be faithful:
scaling the detecting vector reaches a value on which that character is nontrivial. -/
theorem commutator_detection_of_nondegenerate_form
    (τ : (K ⧸ H) ≃* Multiplicative X) (θ : H →* ℂˣ)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ x y : K,
      ψ (B (coordinate H τ x) (coordinate H τ y)) = characterCommutator H τ θ x y)
    (x : K) (hx : x ∉ H) :
    ∃ y : K, ∃ z : H, y * x * y⁻¹ = (z : K) * x ∧ θ z ≠ 1 := by
  have hxv : coordinate H τ x ≠ 0 := fun h => hx ((coordinate_eq_zero_iff H τ x).mp h)
  obtain ⟨u, hu⟩ : ∃ u : X, B u (coordinate H τ x) ≠ 0 := by
    by_contra hn
    push Not at hn
    exact hxv (hnd (coordinate H τ x) hn)
  obtain ⟨t, ht⟩ : ∃ t : k, ψ t ≠ 1 := by
    by_contra hn
    apply hψ
    apply AddChar.ext
    intro t
    exact not_not.mp (not_exists.mp hn t)
  let a := t / B u (coordinate H τ x)
  obtain ⟨y, hy⟩ := coordinate_surjective H τ (a • u)
  let z : H := ⟨y * x * y⁻¹ * x⁻¹, commutator_mem H τ y x⟩
  refine ⟨y, z, ?_, ?_⟩
  · change y * x * y⁻¹ = (y * x * y⁻¹ * x⁻¹) * x
    group
  · have hf := hform y x
    rw [hy] at hf
    have hb : B (a • u) (coordinate H τ x) = t := by
      simp only [map_smul, LinearMap.smul_apply, smul_eq_mul]
      exact div_mul_cancel₀ t hu
    rw [hb] at hf
    exact fun hz => ht (hf.trans hz)

/-- The literal quotient/form datum of original §10 derives trace support for
the prescribed action, once its theta scalar restriction is attached. -/
theorem trace_support_of_nondegenerate_form
    (τ : (K ⧸ H) ≃* Multiplicative X) (θ : H →* ℂˣ)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ x y : K,
      ψ (B (coordinate H τ x) (coordinate H τ y)) = characterCommutator H τ θ x y)
    (η : Representation ℂ K W)
    (hscalar : ∀ h : H, η h = (θ h : ℂ) • LinearMap.id)
    (x : K) (hx : x ∉ H) : η.character x = 0 :=
  HeisenbergTrace108.character_off_subgroup H θ η hscalar
    (commutator_detection_of_nondegenerate_form H τ θ B ψ hψ hnd hform) x hx

end QuotientForm

section FormTransport
variable {K L k X : Type*} [Group K] [Group L] [Field k]
  [AddCommGroup X] [Module k X]
  (H : Subgroup K) (N : Subgroup L) [H.Normal] [N.Normal]
  (ε : K ≃* L) (hmap : H.map ε.toMonoidHom = N)

/-- Transport the declared canonical quotient through a literal group
dictionary that sends the original scalar subgroup to its original domain. -/
def transportedQuotient (τ : (L ⧸ N) ≃* Multiplicative X) :
    (K ⧸ H) ≃* Multiplicative X :=
  (QuotientGroup.congr H N ε hmap).trans τ

theorem coordinate_transport (τ : (L ⧸ N) ≃* Multiplicative X) (x : K) :
    coordinate H (transportedQuotient H N ε hmap τ) x = coordinate N τ (ε x) := rfl

/-- The same canonical theta, pulled through the literal subgroup dictionary. -/
def pulledBackCharacter (φ : N →* ℂˣ) : H →* ℂˣ :=
  φ.comp ((ε.toMonoidHom.comp H.subtype).codRestrict N
    (fun h => hmap ▸ Subgroup.mem_map_of_mem ε.toMonoidHom h.property))

theorem characterCommutator_transport (τ : (L ⧸ N) ≃* Multiplicative X)
    (φ : N →* ℂˣ) (x y : K) :
    characterCommutator H (transportedQuotient H N ε hmap τ)
      (pulledBackCharacter H N ε hmap φ) x y =
    characterCommutator N τ φ (ε x) (ε y) := by
  apply congrArg φ
  apply Subtype.ext
  change ε (x * y * x⁻¹ * y⁻¹) = ε x * ε y * (ε x)⁻¹ * (ε y)⁻¹
  simp only [map_mul, map_inv]

/-- Original form coherence transfers through the quotient/subgroup
dictionary; it need not be independently assumed again on the actual group. -/
theorem form_transport (τ : (L ⧸ N) ≃* Multiplicative X) (φ : N →* ℂˣ)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ)
    (hform : ∀ x y : L,
      ψ (B (coordinate N τ x) (coordinate N τ y)) = characterCommutator N τ φ x y)
    (x y : K) :
    ψ (B (coordinate H (transportedQuotient H N ε hmap τ) x)
      (coordinate H (transportedQuotient H N ε hmap τ) y)) =
    characterCommutator H (transportedQuotient H N ε hmap τ)
      (pulledBackCharacter H N ε hmap φ) x y := by
  rw [coordinate_transport, coordinate_transport, hform,
    characterCommutator_transport]

end FormTransport

section CharacterIntertwining
variable {G : Type*} [Group G]
open InductionIrreducibility NormalizerIntertwining60

/-- A nonzero intertwiner of the original one-dimensional theta is exactly
theta covariance on its literal conjugate intersection. Eta is absent. -/
theorem character_intertwinedAt_iff_covariance (D : Subgroup G) (θ : D →* ℂˣ) (g : G) :
    IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g ↔
      ∀ h : intersectionSubgroup D g,
        θ (h : D) = θ (intersectionConjugation D g h) := by
  constructor
  · rintro ⟨T, hT⟩
    have ht : ∀ z : ℂ, T z = z * T 1 := by
      intro z
      change T.toLinearMap z = z * T.toLinearMap 1
      simpa only [smul_eq_mul, mul_one] using T.map_smul z (1 : ℂ)
    have hn : T 1 ≠ 0 := by
      intro h
      apply hT
      apply IntertwiningMap.ext
      apply LinearMap.ext
      intro z
      change T z = 0
      rw [ht, h, mul_zero]
    intro h
    have he := IntertwiningMap.isIntertwining _ _ T h (1 : ℂ)
    change T ((θ (h : D) : ℂ) * 1) =
      (θ (intersectionConjugation D g h) : ℂ) * T 1 at he
    rw [mul_one, ht] at he
    apply Units.ext
    exact mul_right_cancel₀ hn he
  · exact character_intertwinedAt g D θ

theorem character_values_of_intertwinedAt
    (D : Subgroup G) (θ : D →* ℂˣ) (g : G)
    (hg : IntertwinedAt D (MonomialInduction.scalarRepresentation θ) g)
    (a b : G) (ha : a ∈ D) (hb : b ∈ D) (he : b = g * a * g⁻¹) :
    θ ⟨a, ha⟩ = θ ⟨b, hb⟩ := by
  let h : intersectionSubgroup D g := ⟨⟨a, ha⟩, by
    change g * a * g⁻¹ ∈ D
    rw [← he]
    exact hb⟩
  have hc := (character_intertwinedAt_iff_covariance D θ g).mp hg h
  have hi : intersectionConjugation D g h = ⟨b, hb⟩ := Subtype.ext he.symm
  rw [hi] at hc
  exact hc

end CharacterIntertwining

section Actual
open Matrix ValuativeRel IntersectionModel108
open ActualCharacterType61 ActualCuspidalCandidate105 DegreeIndex110 ActualELatticeTopology60

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
  [Nonempty n] (e : (m → E) ≃L[F] (n → F))
  (D : Subgroup (GL n F)) (θ : D →* ℂˣ)

/-- The actual scalar subgroup is normal in the actual first subgroup, since
the latter is contained in the literal domain-character pair normalizer. -/
instance actualScalarSubgroup_normal :
    (actualScalarSubgroup F E m n e D θ).Normal where
  conj_mem := by
    intro a ha b
    change ActualIntersection108.embedding F E m n e D θ (b * a * b⁻¹) ∈ D
    rw [map_mul, map_mul, map_inv]
    have hb : ActualIntersection108.embedding F E m n e D θ b ∈
        CharacterNormalizer61.normalizer D θ := b.val.property.1
    exact CharacterNormalizer61.conjugation_mem D θ hb
      ⟨ActualIntersection108.embedding F E m n e D θ a, ha⟩

variable {k X W : Type*} [Field k] [AddCommGroup X] [Module k X]
  [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]
  (hDc : D ≤ matrixCongruence F E m n e)
  (κ : Representation ℂ (compact F E m n e D θ) W)

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m]
  [Nonempty n] [FiniteDimensional ℂ W] in
/-- Attach the original canonical quotient and commutator form to the literal
actual first subgroup. Theta occurrence and irreducibility derive scalar action;
trace support is then a conclusion, rather than an independent profile premise. -/
theorem actual_trace_support_of_quotient_form
    [IsIrreducible (ActualIntersection108.restriction F E m n e D θ κ)]
    (hcontains : ActualCharacterData108.Contains F E m n e D θ hDc κ)
    (τ : ((firstSubgroup F E m n e D θ) ⧸
      actualScalarSubgroup F E m n e D θ) ≃* Multiplicative X)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ x y : firstSubgroup F E m n e D θ,
      ψ (B (coordinate (actualScalarSubgroup F E m n e D θ) τ x)
        (coordinate (actualScalarSubgroup F E m n e D θ) τ y)) =
      characterCommutator (actualScalarSubgroup F E m n e D θ) τ
        (actualScalarCharacter F E m n e D θ) x y)
    (x : firstSubgroup F E m n e D θ)
    (hx : x ∉ actualScalarSubgroup F E m n e D θ) :
    Representation.character (ActualIntersection108.restriction F E m n e D θ κ) x = 0 := by
  exact trace_support_of_nondegenerate_form
    (actualScalarSubgroup F E m n e D θ) τ (actualScalarCharacter F E m n e D θ)
    B ψ hψ hnd hform (ActualIntersection108.restriction F E m n e D θ κ)
    (actual_scalar F E m n e D θ hDc κ hcontains) x hx

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m] [DecidableEq m]
  [Nonempty n] in
/-- An intertwiner of the original scalar theta representation gives covariance
on the actual pair support. This hypothesis concerns theta, never eta. -/
theorem actual_covariance_of_character_intertwining (g : GL n F)
    (hg : NormalizerIntertwining60.IntertwinedAt D
      (MonomialInduction.scalarRepresentation θ) g)
    (p : pairs (ActualIntersection108.embedding F E m n e D θ) g)
    (h₁ : left (ActualIntersection108.embedding F E m n e D θ) g p ∈
      actualScalarSubgroup F E m n e D θ)
    (h₂ : right (ActualIntersection108.embedding F E m n e D θ) g p ∈
      actualScalarSubgroup F E m n e D θ) :
    actualScalarCharacter F E m n e D θ
      ⟨left (ActualIntersection108.embedding F E m n e D θ) g p, h₁⟩ =
    actualScalarCharacter F E m n e D θ
      ⟨right (ActualIntersection108.embedding F E m n e D θ) g p, h₂⟩ := by
  exact character_values_of_intertwinedAt D θ g hg
    (ActualIntersection108.embedding F E m n e D θ
      (left (ActualIntersection108.embedding F E m n e D θ) g p))
    (ActualIntersection108.embedding F E m n e D θ
      (right (ActualIntersection108.embedding F E m n e D θ) g p))
    h₁ h₂ p.property

/-- The candidate's actual eta Hom-line condition follows from the original
Heisenberg quotient/form, theta intertwining in the full field centralizer,
and the oriented ambient index identity. Trace and covariance are derived. -/
theorem actual_eta_dimension_from_quotient_form
    [IsIrreducible (ActualIntersection108.restriction F E m n e D θ κ)]
    (hF : Continuous (algebraMap F E)) (hDo : IsOpen (D : Set (GL n F)))
    (hκ : SmoothDegreeQuotient.IsSmooth κ)
    (hcontains : ActualCharacterData108.Contains F E m n e D θ hDc κ)
    (τ : ((firstSubgroup F E m n e D θ) ⧸
      actualScalarSubgroup F E m n e D θ) ≃* Multiplicative X)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hnd : ∀ v : X, (∀ u : X, B u v = 0) → v = 0)
    (hform : ∀ x y : firstSubgroup F E m n e D θ,
      ψ (B (coordinate (actualScalarSubgroup F E m n e D θ) τ x)
        (coordinate (actualScalarSubgroup F E m n e D θ) τ y)) =
      characterCommutator (actualScalarSubgroup F E m n e D θ) τ
        (actualScalarCharacter F E m n e D θ) x y)
    (hθcentralizer : ∀ y : GL m E, NormalizerIntertwining60.IntertwinedAt D
      (MonomialInduction.scalarRepresentation θ) (centralizerMap F E m n e y))
    (hindex : ∀ y : GL m E,
      ((ActualIntersection108.embedding F E m n e D θ).range ⊓
        (ActualIntersection108.embedding F E m n e D θ).range.comap
          (MulAut.conj (centralizerMap F E m n e y)).toMonoidHom).relIndex
            (ActualIntersection108.embedding F E m n e D θ).range =
      (D ⊓ D.comap (MulAut.conj (centralizerMap F E m n e y)).toMonoidHom).relIndex D) :
    ∀ y : GL m E, Module.finrank ℂ (IntertwiningSpace107.space
      (ActualIntersection108.embedding F E m n e D θ)
      (ActualIntersection108.restriction F E m n e D θ κ)
      (centralizerMap F E m n e y)) = 1 := by
  exact actual_eta_dimension_ambient F E m n e D θ hDc κ hF hDo hκ hcontains
    (actual_trace_support_of_quotient_form F E m n e D θ hDc κ hcontains
      τ B ψ hψ hnd hform)
    (fun y => actual_covariance_of_character_intertwining F E m n e D θ
      (centralizerMap F E m n e y) (hθcentralizer y)) hindex

end Actual

end PaperXI.HeisenbergCharacterProfile111
