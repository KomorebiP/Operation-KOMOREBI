import PaperXI.FiniteProfileBridge109
import PaperXI.CompactIntersection108
import PaperXI.ActualIntersection108
import PaperXI.PairIndex110

/-! The degree-square identity from the original irreducible character profile,
and the positive-index cancellation that supplies the intersection Hom line.
Arithmetic trace support, character covariance, and the oriented lattice-index
identity remain explicit hypotheses. Schur is used only on the entire action. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DegreeIndex110
open Representation FiniteProfileBridge109 IntersectionModel108

variable {K Q G W : Type*} [Group K] [Group Q] [Group G]
  [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]

/-- A finite model of the entire irreducible representation, with its original
scalar/trace profile, derives the degree-square index identity. -/
theorem degree_square_of_finite_model [Finite Q]
    (q : K →* Q) (hq : Function.Surjective q)
    (ρ : Representation ℂ Q W) [IsIrreducible ρ]
    (H : Subgroup K) (θ : H →* ℂˣ)
    (hd : 0 < Module.finrank ℂ W)
    (hscalar : ∀ h : H, (ρ.comp q) h = (θ h : ℂ) • LinearMap.id)
    (hz : ∀ x : K, x ∉ H → Representation.character (ρ.comp q) x = 0) :
    Module.finrank ℂ W * Module.finrank ℂ W = H.index := by
  classical
  let : Fintype Q := Fintype.ofFinite Q
  have he := (dimension_one_iff_of_original_profiles q hq ρ ρ H H θ θ hd
    hscalar hscalar hz hz (fun _ _ _ => rfl)).mp
      (Representation.IsIrreducible.finrank_intertwiningMap_self (ρ := ρ))
  simp only [inf_idem] at he
  have hk : q.ker ≤ H := (quotient_kernel_le_action_kernel q ρ).trans
    (kernel_le_of_trace_support (ρ.comp q) H hd hz)
  have hc := (H.map q).index_mul_card
  have hp : 0 < Nat.card (H.map q) := Nat.card_pos
  have hi : Module.finrank ℂ W * Module.finrank ℂ W = (H.map q).index :=
    Nat.eq_of_mul_eq_mul_right hp (he.trans hc.symm)
  exact hi.trans (image_index q hq H hk)

/-- Irreducibility supplies positive degree, and survives the surjective
quotient of the entire action. No degree-square premise is supplied. -/
theorem degree_square_of_finite_kernel_quotient
    (η : Representation ℂ K W) [IsIrreducible η] [Finite (K ⧸ η.ker)]
    (H : Subgroup K) (θ : H →* ℂˣ)
    (hscalar : ∀ h : H, η h = (θ h : ℂ) • LinearMap.id)
    (hz : ∀ x : K, x ∉ H → η.character x = 0) :
    Module.finrank ℂ W * Module.finrank ℂ W = H.index := by
  let : Nontrivial W := GeneratedIrreducibility.nontrivial_space η
  let ρ := QuotientRepresentation.descend η.ker η le_rfl
  let : IsIrreducible ρ := QuotientRepresentation.descend_irreducible η.ker η le_rfl
  exact degree_square_of_finite_model (QuotientGroup.mk' η.ker)
    QuotientGroup.mk_surjective ρ H θ Module.finrank_pos hscalar hz

/-- Compactness and smoothness construct the finite whole-action model needed
to derive the original Heisenberg degree identity. -/
theorem degree_square [TopologicalSpace K] [IsTopologicalGroup K] [CompactSpace K]
    (η : Representation ℂ K W) [IsIrreducible η]
    (hη : SmoothDegreeQuotient.IsSmooth η)
    (H : Subgroup K) (θ : H →* ℂˣ)
    (hscalar : ∀ h : H, η h = (θ h : ℂ) • LinearMap.id)
    (hz : ∀ x : K, x ∉ H → η.character x = 0) :
    Module.finrank ℂ W * Module.finrank ℂ W = H.index := by
  let : Finite (K ⧸ η.ker) := η.ker.quotient_finite_of_isOpen
    (SmoothDegreeQuotient.isOpen_kernel_of_smooth η hη)
  exact degree_square_of_finite_kernel_quotient η H θ hscalar hz

/-- The oriented BK index identity, with a positive (therefore finite) outer
index, cancels the two subgroup towers. No orders of infinite groups occur. -/
theorem intersection_index_of_oriented_identity
    (H I C : Subgroup K) (hCH : C ≤ H) (hCI : C ≤ I)
    (hI : 0 < I.index) (horiented : I.index = C.relIndex H) :
    C.relIndex I = H.index := by
  have he : I.index * C.relIndex I = I.index * H.index := by
    calc
      I.index * C.relIndex I = C.index := by
        simpa only [Nat.mul_comm] using (Subgroup.relIndex_mul_index hCI)
      _ = C.relIndex H * H.index := (Subgroup.relIndex_mul_index hCH).symm
      _ = I.index * H.index := by rw [← horiented]
  exact Nat.eq_of_mul_eq_mul_left hI he

/-- The original-profile finite character criterion is exactly the index
condition on the original support intersection. -/
theorem dimension_one_iff_original_index [Finite Q]
    (q : K →* Q) (hq : Function.Surjective q)
    (ρ σ : Representation ℂ Q W)
    (H₁ H₂ : Subgroup K) (θ₁ : H₁ →* ℂˣ) (θ₂ : H₂ →* ℂˣ)
    (hd : 0 < Module.finrank ℂ W)
    (h₁ : ∀ h : H₁, (ρ.comp q) h = (θ₁ h : ℂ) • LinearMap.id)
    (h₂ : ∀ h : H₂, (σ.comp q) h = (θ₂ h : ℂ) • LinearMap.id)
    (hz₁ : ∀ p : K, p ∉ H₁ → Representation.character (ρ.comp q) p = 0)
    (hz₂ : ∀ p : K, p ∉ H₂ → Representation.character (σ.comp q) p = 0)
    (hc : ∀ p : K, ∀ h₁ : p ∈ H₁, ∀ h₂ : p ∈ H₂,
      θ₁ ⟨p, h₁⟩ = θ₂ ⟨p, h₂⟩) :
    Module.finrank ℂ (IntertwiningMap ρ σ) = 1 ↔
      (H₁ ⊓ H₂).index = Module.finrank ℂ W * Module.finrank ℂ W := by
  classical
  let : Fintype Q := Fintype.ofFinite Q
  have hk₁ : q.ker ≤ H₁ := (quotient_kernel_le_action_kernel q ρ).trans
    (kernel_le_of_trace_support (ρ.comp q) H₁ hd hz₁)
  have hk₂ : q.ker ≤ H₂ := (quotient_kernel_le_action_kernel q σ).trans
    (kernel_le_of_trace_support (σ.comp q) H₂ hd hz₂)
  have hi := image_index q hq (H₁ ⊓ H₂) (le_inf hk₁ hk₂)
  have hcard := ((H₁ ⊓ H₂).map q).index_mul_card
  have hp : 0 < Nat.card ((H₁ ⊓ H₂).map q) := Nat.card_pos
  rw [dimension_one_iff_of_original_profiles q hq ρ σ H₁ H₂ θ₁ θ₂
    hd h₁ h₂ hz₁ hz₂ hc]
  constructor
  · intro he
    have heq := Nat.eq_of_mul_eq_mul_right hp (hcard.trans he.symm)
    exact hi.symm.trans heq
  · intro he
    rw [hi, he] at hcard
    exact hcard

/-- The actual conjugate-intersection Hom line follows from profiles on the
original eta and compatibility of its pulled-back scalar characters, once the
original paired-support intersection has the correct index. -/
theorem intersection_dimension_one_of_index
    (ι : K →* G) (η : Representation ℂ K W) (g : G)
    (H : Subgroup K) (θ : H →* ℂˣ)
    (hd : 0 < Module.finrank ℂ W)
    (hscalar : ∀ h : H, η h = (θ h : ℂ) • LinearMap.id)
    (hz : ∀ x : K, x ∉ H → η.character x = 0)
    (hc : ∀ p : pairs ι g,
      ∀ h₁ : left ι g p ∈ H, ∀ h₂ : right ι g p ∈ H,
      θ ⟨left ι g p, h₁⟩ = θ ⟨right ι g p, h₂⟩)
    [Finite (FiniteJointQuotient108.quotient
      (η.comp (left ι g)) (η.comp (right ι g)))]
    (hindex : (H.comap (left ι g) ⊓ H.comap (right ι g)).index =
      Module.finrank ℂ W * Module.finrank ℂ W) :
    Module.finrank ℂ (IntertwiningSpace107.space ι η g) = 1 := by
  let A := H.comap (left ι g)
  let B := H.comap (right ι g)
  let θ₁ : A →* ℂˣ := θ.comp (((left ι g).comp A.subtype).codRestrict H (fun p => p.property))
  let θ₂ : B →* ℂˣ := θ.comp (((right ι g).comp B.subtype).codRestrict H (fun p => p.property))
  rw [CompactIntersection108.finrank_quotient ι η g]
  apply (dimension_one_iff_original_index
    (QuotientGroup.mk' (FiniteJointQuotient108.kernel
      (η.comp (left ι g)) (η.comp (right ι g)))) QuotientGroup.mk_surjective
    (FiniteJointQuotient108.first (η.comp (left ι g)) (η.comp (right ι g)))
    (FiniteJointQuotient108.second (η.comp (left ι g)) (η.comp (right ι g)))
    A B θ₁ θ₂ hd
    (fun p => hscalar ⟨left ι g p, p.property⟩)
    (fun p => hscalar ⟨right ι g p, p.property⟩)
    (fun p hp => hz (left ι g p) hp)
    (fun p hp => hz (right ι g p) hp) hc).mpr
  exact hindex

/-- Profiles on the original irreducible eta and the oriented arithmetic
index equality give the line on the literal conjugate-intersection space.
The degree and all finite quotient/profile transport premises are derived. -/
theorem intersection_dimension_one
    [TopologicalSpace K] [IsTopologicalGroup K] [CompactSpace K]
    [TopologicalSpace G] [IsTopologicalGroup G] [T2Space G]
    (ι : K →* G) (hι : Function.Injective ι) (hi : Continuous ι)
    (η : Representation ℂ K W) [IsIrreducible η]
    (hη : SmoothDegreeQuotient.IsSmooth η) (g : G)
    (H : Subgroup K) (θ : H →* ℂˣ)
    (hscalar : ∀ h : H, η h = (θ h : ℂ) • LinearMap.id)
    (hz : ∀ x : K, x ∉ H → η.character x = 0)
    (hc : ∀ p : pairs ι g,
      ∀ h₁ : left ι g p ∈ H, ∀ h₂ : right ι g p ∈ H,
      θ ⟨left ι g p, h₁⟩ = θ ⟨right ι g p, h₂⟩)
    (hI : 0 < (PairIndex110.intersection ι g).index)
    (horiented : (PairIndex110.intersection ι g).index =
      (PairIndex110.scalarIntersection ι H g).relIndex H) :
    Module.finrank ℂ (IntertwiningSpace107.space ι η g) = 1 := by
  let : Nontrivial W := GeneratedIrreducibility.nontrivial_space η
  let : Finite (FiniteJointQuotient108.quotient
      (η.comp (left ι g)) (η.comp (right ι g))) :=
    CompactIntersection108.finite_quotient ι hi η hη g
  have hd := degree_square η hη H θ hscalar hz
  have hcindex := intersection_index_of_oriented_identity H
    (PairIndex110.intersection ι g) (PairIndex110.scalarIntersection ι H g)
    (PairIndex110.scalarIntersection_le ι H g)
    (PairIndex110.scalarIntersection_le_intersection ι H g) hI horiented
  apply intersection_dimension_one_of_index ι η g H θ Module.finrank_pos hscalar hz hc
  exact (PairIndex110.pairSupport_index ι H g hι).trans (hcindex.trans hd.symm)

omit [FiniteDimensional ℂ W] in
/-- An open embedded compact subgroup has a finite positive intersection
index at every ambient element. This discharges the cancellation positivity
premise in the actual open-subgroup application. -/
theorem intersection_index_pos
    [TopologicalSpace K] [IsTopologicalGroup K] [CompactSpace K]
    [TopologicalSpace G] [IsTopologicalGroup G]
    (ι : K →* G) (hi : Continuous ι) (ho : IsOpen (ι.range : Set G)) (g : G) :
    0 < (PairIndex110.intersection ι g).index := by
  have hI : IsOpen (PairIndex110.intersection ι g : Set K) :=
    ho.preimage ((continuous_const.mul hi).mul continuous_const)
  let : Finite (K ⧸ PairIndex110.intersection ι g) :=
    (PairIndex110.intersection ι g).quotient_finite_of_isOpen hI
  exact Nat.pos_of_ne_zero (Subgroup.index_ne_zero_of_finite)

/-- The outer index in the original compact group is the corresponding
relative index of the literal first-coordinate ambient intersection. -/
theorem intersection_index_ambient (ι : K →* G) (hι : Function.Injective ι) (g : G) :
    (PairIndex110.intersection ι g).index =
      (ι.range ⊓ ι.range.comap (MulAut.conj g).toMonoidHom).relIndex ι.range := by
  rw [← PairIndex110.intersection_image, MonoidHom.range_eq_map,
    Subgroup.relIndex_map_map_of_injective _ _ hι, Subgroup.relIndex_top_right]

theorem scalarIntersection_index_ambient
    (ι : K →* G) (hι : Function.Injective ι) (H : Subgroup K) (g : G) :
    (PairIndex110.scalarIntersection ι H g).relIndex H =
      (H.map ι ⊓ (H.map ι).comap (MulAut.conj g).toMonoidHom).relIndex (H.map ι) := by
  rw [← PairIndex110.scalarIntersection_image,
    Subgroup.relIndex_map_map_of_injective _ _ hι]

/-- An arithmetic identity stated on the original ambient subgroup images
supplies exactly the oriented identity used by the cancellation theorem. -/
theorem oriented_identity_of_ambient
    (ι : K →* G) (hι : Function.Injective ι) (H : Subgroup K) (g : G)
    (h : (ι.range ⊓ ι.range.comap (MulAut.conj g).toMonoidHom).relIndex ι.range =
      (H.map ι ⊓ (H.map ι).comap (MulAut.conj g).toMonoidHom).relIndex (H.map ι)) :
    (PairIndex110.intersection ι g).index =
      (PairIndex110.scalarIntersection ι H g).relIndex H :=
  (intersection_index_ambient ι hι g).trans
    (h.trans (scalarIntersection_index_ambient ι hι H g).symm)

section Actual
open Matrix ValuativeRel
open ActualCharacterType61 ActualCuspidalCandidate105 LatticeCongruenceTopology60
open ActualELatticeTopology60

variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]
variable (m n : Type*) [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
  [Nonempty n] (e : (m → E) ≃L[F] (n → F))
  (D : Subgroup (GL n F)) (θ : D →* ℂˣ)

/-- The original character domain inside the actual first subgroup. -/
def actualScalarSubgroup : Subgroup (firstSubgroup F E m n e D θ) :=
  D.comap (ActualIntersection108.embedding F E m n e D θ)

/-- The same original theta, carried through the actual nested subgroup map. -/
def actualScalarCharacter : actualScalarSubgroup F E m n e D θ →* ℂˣ :=
  θ.comp (((ActualIntersection108.embedding F E m n e D θ).comp
    (actualScalarSubgroup F E m n e D θ).subtype).codRestrict D (fun p => p.property))

variable (hDc : D ≤ matrixCongruence F E m n e)
  (κ : Representation ℂ (compact F E m n e D θ) W)

omit [FiniteDimensional ℂ W] [ValuativeRel F] [IsNonarchimedeanLocalField F]
  [Fintype m] [DecidableEq m] [Nonempty n] in
/-- Existing occurrence and restricted irreducibility supply scalar action
on the actual scalar subgroup; no new scalar action premise is introduced. -/
theorem actual_scalar
    [IsIrreducible (ActualIntersection108.restriction F E m n e D θ κ)]
    (hc : ActualCharacterData108.Contains F E m n e D θ hDc κ)
    (h : actualScalarSubgroup F E m n e D θ) :
    ActualIntersection108.restriction F E m n e D θ κ h =
      (actualScalarCharacter F E m n e D θ h : ℂ) • LinearMap.id := by
  exact ActualCharacterData108.scalar_restriction F E m n e D θ hDc κ hc
    ⟨ActualIntersection108.embedding F E m n e D θ h, h.property⟩

omit [ValuativeRel F] [IsNonarchimedeanLocalField F] [Fintype m]
  [DecidableEq m] [Nonempty n] in
include hDc in
/-- The scalar subgroup image is exactly the original character domain D. -/
theorem actualScalarSubgroup_image :
    (actualScalarSubgroup F E m n e D θ).map
      (ActualIntersection108.embedding F E m n e D θ) = D := by
  apply Subgroup.map_comap_eq_self
  intro d hd
  let dc := ActualCharacterData108.intoCompact F E m n e D θ hDc ⟨d, hd⟩
  have hf : dc ∈ firstSubgroup F E m n e D θ :=
    ActualCharacterData108.intoCompact_mem_first F E m n e D θ hDc ⟨d, hd⟩
  exact ⟨⟨dc, hf⟩, rfl⟩

/-- The literal first-subgroup embedding has open range in the ambient group. -/
theorem actual_embedding_range_open
    (hF : Continuous (algebraMap F E)) (hDo : IsOpen (D : Set (GL n F))) :
    IsOpen ((ActualIntersection108.embedding F E m n e D θ).range : Set (GL n F)) := by
  have hrange : ((ActualIntersection108.embedding F E m n e D θ).range : Set (GL n F)) =
      (compact F E m n e D θ).subtype ''
        (firstSubgroup F E m n e D θ : Set (compact F E m n e D θ)) := by
    ext x
    constructor
    · rintro ⟨a, rfl⟩
      exact ⟨(a : compact F E m n e D θ), a.property, rfl⟩
    · rintro ⟨a, ha, rfl⟩
      exact ⟨⟨a, ha⟩, rfl⟩
  rw [hrange]
  exact (compactGroup_compact_open F E m n e D θ hF hDo).2.isOpenMap_subtype_val _
    (firstSubgroup_open F E m n e D θ hF)

/-- Conditional discharge of the candidate's literal eta-dimension premise
at one ambient element, for the same prescribed kappa and original theta.
Only trace support, character covariance, and the positive oriented arithmetic
index identity remain to be instantiated by the simple-character model. -/
theorem actual_eta_dimension_one
    [IsIrreducible (ActualIntersection108.restriction F E m n e D θ κ)]
    (hF : Continuous (algebraMap F E)) (hDo : IsOpen (D : Set (GL n F)))
    (hκ : SmoothDegreeQuotient.IsSmooth κ)
    (hcontains : ActualCharacterData108.Contains F E m n e D θ hDc κ)
    (hz : ∀ x : firstSubgroup F E m n e D θ,
      x ∉ actualScalarSubgroup F E m n e D θ →
      Representation.character (ActualIntersection108.restriction F E m n e D θ κ) x = 0)
    (g : GL n F)
    (hc : ∀ p : pairs (ActualIntersection108.embedding F E m n e D θ) g,
      ∀ h₁ : ActualIntersection108.embedding F E m n e D θ
        (left (ActualIntersection108.embedding F E m n e D θ) g p) ∈ D,
      ∀ h₂ : ActualIntersection108.embedding F E m n e D θ
        (right (ActualIntersection108.embedding F E m n e D θ) g p) ∈ D,
      θ ⟨ActualIntersection108.embedding F E m n e D θ
        (left (ActualIntersection108.embedding F E m n e D θ) g p), h₁⟩ =
      θ ⟨ActualIntersection108.embedding F E m n e D θ
        (right (ActualIntersection108.embedding F E m n e D θ) g p), h₂⟩)
    (hI : 0 < (PairIndex110.intersection
      (ActualIntersection108.embedding F E m n e D θ) g).index)
    (horiented : (PairIndex110.intersection
      (ActualIntersection108.embedding F E m n e D θ) g).index =
      (PairIndex110.scalarIntersection (ActualIntersection108.embedding F E m n e D θ)
        (actualScalarSubgroup F E m n e D θ) g).relIndex
          (actualScalarSubgroup F E m n e D θ)) :
    Module.finrank ℂ (IntertwiningSpace107.space
      (ActualIntersection108.embedding F E m n e D θ)
      (ActualIntersection108.restriction F E m n e D θ κ) g) = 1 := by
  let : CompactSpace (compact F E m n e D θ) := isCompact_iff_compactSpace.mp
    (compactGroup_compact_open F E m n e D θ hF hDo).1
  let : CompactSpace (firstSubgroup F E m n e D θ) := isCompact_iff_compactSpace.mp
    ((firstSubgroup F E m n e D θ).isClosed_of_isOpen
      (firstSubgroup_open F E m n e D θ hF)).isCompact
  have hι : Function.Injective (ActualIntersection108.embedding F E m n e D θ) := by
    intro a b h
    exact Subtype.ext (Subtype.ext h)
  exact intersection_dimension_one (ActualIntersection108.embedding F E m n e D θ)
    hι (continuous_subtype_val.comp continuous_subtype_val)
    (ActualIntersection108.restriction F E m n e D θ κ)
    (CompactIntersection108.smooth_comp κ hκ
      (firstSubgroup F E m n e D θ).subtype continuous_subtype_val) g
    (actualScalarSubgroup F E m n e D θ) (actualScalarCharacter F E m n e D θ)
    (actual_scalar F E m n e D θ hDc κ hcontains) hz hc hI horiented

/-- The exact universally quantified eta-dimension input of the prescribed
candidate, from its original theta profile, covariance at every centralizer
element, and the oriented lattice-index identity. Positive finite indices,
the degree-square identity, and the common finite model are all derived. -/
theorem actual_eta_dimension
    [IsIrreducible (ActualIntersection108.restriction F E m n e D θ κ)]
    (hF : Continuous (algebraMap F E)) (hDo : IsOpen (D : Set (GL n F)))
    (hκ : SmoothDegreeQuotient.IsSmooth κ)
    (hcontains : ActualCharacterData108.Contains F E m n e D θ hDc κ)
    (hz : ∀ x : firstSubgroup F E m n e D θ,
      x ∉ actualScalarSubgroup F E m n e D θ →
      Representation.character (ActualIntersection108.restriction F E m n e D θ κ) x = 0)
    (hc : ∀ y : GL m E,
      ∀ p : pairs (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y),
      ∀ h₁ : left (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y) p ∈ actualScalarSubgroup F E m n e D θ,
      ∀ h₂ : right (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y) p ∈ actualScalarSubgroup F E m n e D θ,
      actualScalarCharacter F E m n e D θ
        ⟨left (ActualIntersection108.embedding F E m n e D θ)
          (centralizerMap F E m n e y) p, h₁⟩ =
      actualScalarCharacter F E m n e D θ
        ⟨right (ActualIntersection108.embedding F E m n e D θ)
          (centralizerMap F E m n e y) p, h₂⟩)
    (horiented : ∀ y : GL m E,
      (PairIndex110.intersection (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y)).index =
      (PairIndex110.scalarIntersection (ActualIntersection108.embedding F E m n e D θ)
        (actualScalarSubgroup F E m n e D θ)
          (centralizerMap F E m n e y)).relIndex (actualScalarSubgroup F E m n e D θ)) :
    ∀ y : GL m E, Module.finrank ℂ (IntertwiningSpace107.space
      (ActualIntersection108.embedding F E m n e D θ)
      (ActualIntersection108.restriction F E m n e D θ κ)
      (centralizerMap F E m n e y)) = 1 := by
  let : CompactSpace (compact F E m n e D θ) := isCompact_iff_compactSpace.mp
    (compactGroup_compact_open F E m n e D θ hF hDo).1
  let : CompactSpace (firstSubgroup F E m n e D θ) := isCompact_iff_compactSpace.mp
    ((firstSubgroup F E m n e D θ).isClosed_of_isOpen
      (firstSubgroup_open F E m n e D θ hF)).isCompact
  intro y
  exact actual_eta_dimension_one F E m n e D θ hDc κ hF hDo hκ hcontains hz
    (centralizerMap F E m n e y) (hc y)
    (intersection_index_pos (ActualIntersection108.embedding F E m n e D θ)
      (continuous_subtype_val.comp continuous_subtype_val)
      (actual_embedding_range_open F E m n e D θ hF hDo)
      (centralizerMap F E m n e y)) (horiented y)

/-- The candidate's exact eta-dimension input from an arithmetic index identity
on the original ambient D and actual first-subgroup image. All other generic
degree, quotient, index, and scalar-attachment premises are derived. -/
theorem actual_eta_dimension_ambient
    [IsIrreducible (ActualIntersection108.restriction F E m n e D θ κ)]
    (hF : Continuous (algebraMap F E)) (hDo : IsOpen (D : Set (GL n F)))
    (hκ : SmoothDegreeQuotient.IsSmooth κ)
    (hcontains : ActualCharacterData108.Contains F E m n e D θ hDc κ)
    (hz : ∀ x : firstSubgroup F E m n e D θ,
      x ∉ actualScalarSubgroup F E m n e D θ →
      Representation.character (ActualIntersection108.restriction F E m n e D θ κ) x = 0)
    (hc : ∀ y : GL m E,
      ∀ p : pairs (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y),
      ∀ h₁ : left (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y) p ∈ actualScalarSubgroup F E m n e D θ,
      ∀ h₂ : right (ActualIntersection108.embedding F E m n e D θ)
        (centralizerMap F E m n e y) p ∈ actualScalarSubgroup F E m n e D θ,
      actualScalarCharacter F E m n e D θ
        ⟨left (ActualIntersection108.embedding F E m n e D θ)
          (centralizerMap F E m n e y) p, h₁⟩ =
      actualScalarCharacter F E m n e D θ
        ⟨right (ActualIntersection108.embedding F E m n e D θ)
          (centralizerMap F E m n e y) p, h₂⟩)
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
  apply actual_eta_dimension F E m n e D θ hDc κ hF hDo hκ hcontains hz hc
  intro y
  have hι : Function.Injective (ActualIntersection108.embedding F E m n e D θ) := by
    intro a b h
    exact Subtype.ext (Subtype.ext h)
  apply oriented_identity_of_ambient (ActualIntersection108.embedding F E m n e D θ)
    hι (actualScalarSubgroup F E m n e D θ) (centralizerMap F E m n e y)
  simpa only [actualScalarSubgroup_image F E m n e D θ hDc] using hindex y

end Actual

end PaperXI.DegreeIndex110
