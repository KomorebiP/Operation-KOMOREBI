import Mathlib.LinearAlgebra.Quotient.Basic
import Mathlib.Algebra.Module.Submodule.Lattice
import Mathlib.Data.Fintype.BigOperators

/-!
# Actual lattice gluing quotients

The constructions use O-submodules and their actual quotients.  The algebraic
core holds over any commutative ring.  Rational projectors on a K-vector space
are used here by restricting scalars along O → K.  No quotient, injectivity,
annihilator, or splitting conclusion is supplied as a certificate.
-/

set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseGluing

universe u v w
variable {O : Type u} {V : Type v} {I : Type w}
variable [CommRing O] [AddCommGroup V] [Module O V] [Fintype I]

/-- A finite complete orthogonal family; zero packets are harmless to the quotient construction. -/
structure Projectors (O : Type u) (V : Type v) (I : Type w)
    [CommRing O] [AddCommGroup V] [Module O V] [Fintype I] where
  proj : I → Module.End O V
  idem : ∀ i, proj i * proj i = proj i
  orthogonal : ∀ i j, i ≠ j → proj i * proj j = 0
  complete : ∑ i, proj i = 1

variable (P : Projectors O V I) (Λ : Submodule O V)

theorem reconstruct (x : V) : ∑ i, P.proj i x = x := by
  simpa only [LinearMap.sum_apply, Module.End.one_apply] using
    LinearMap.congr_fun P.complete x

theorem proj_idem (i : I) (x : V) : P.proj i (P.proj i x) = P.proj i x :=
  LinearMap.congr_fun (P.idem i) x

theorem proj_other (i j : I) (hij : i ≠ j) (x : V) :
    P.proj i (P.proj j x) = 0 :=
  LinearMap.congr_fun (P.orthogonal i j hij) x

/-- Λ_i = Λ ∩ im(E_i), as an O-submodule of the ambient space. -/
def packetLattice (i : I) : Submodule O V := Λ ⊓ LinearMap.range (P.proj i)

/-- The actual split sublattice, the finite sum of packet intersections. -/
def splitLattice : Submodule O V := ⨆ i, packetLattice P Λ i

theorem splitLattice_le : splitLattice P Λ ≤ Λ :=
  iSup_le fun _ => inf_le_left

theorem proj_mem_of_mem_packetLattice (i j : I) {x : V}
    (hx : x ∈ packetLattice P Λ j) : P.proj i x ∈ Λ := by
  classical
  obtain ⟨hxΛ, y, hy⟩ := hx
  by_cases hij : i = j
  · subst j
    rw [← hy, proj_idem]
    exact hy ▸ hxΛ
  · rw [← hy, proj_other P i j hij]
    exact Λ.zero_mem

theorem proj_mem_of_mem_split (i : I) {x : V}
    (hx : x ∈ splitLattice P Λ) : P.proj i x ∈ Λ := by
  have hle : splitLattice P Λ ≤ Λ.comap (P.proj i) :=
    iSup_le fun j => fun y hy => proj_mem_of_mem_packetLattice P Λ i j hy
  exact hle hx

/-- Membership in the split sublattice is exactly integrality of every packet component. -/
theorem mem_splitLattice_iff (x : V) :
    x ∈ splitLattice P Λ ↔ ∀ i, P.proj i x ∈ Λ := by
  constructor
  · intro hx i
    exact proj_mem_of_mem_split P Λ i hx
  · intro hx
    rw [← reconstruct P x]
    exact Submodule.sum_mem_iSup fun i => ⟨hx i, x, rfl⟩

/-- The split lattice as a submodule of Λ itself. -/
def splitInside : Submodule O Λ := (splitLattice P Λ).comap Λ.subtype

/-- The manuscript's gluing module Λ / ⊕_i(Λ ∩ im(E_i)). -/
abbrev GluingModule := Λ ⧸ splitInside P Λ

/-- The projected lattice E_i Λ. -/
def projectedLattice (i : I) : Submodule O V := Λ.map (P.proj i)

/-- Its integral part, as a submodule of E_i Λ.  Its ambient image is Λ_i. -/
def projectedIntegral (i : I) : Submodule O (projectedLattice P Λ i) :=
  Λ.comap (projectedLattice P Λ i).subtype

theorem projectedIntegral_ambient (i : I) (x : projectedLattice P Λ i) :
    x ∈ projectedIntegral P Λ i ↔ (x : V) ∈ packetLattice P Λ i := by
  constructor
  · intro hx
    refine ⟨hx, ?_⟩
    obtain ⟨y, _hy, hyeq⟩ := x.property
    exact ⟨y, hyeq⟩
  · exact fun hx => hx.1

abbrev CoordinateQuotient (i : I) :=
  projectedLattice P Λ i ⧸ projectedIntegral P Λ i

/-- The genuine projection of an element of Λ into its projected lattice. -/
def projectionToLattice (i : I) : Λ →ₗ[O] projectedLattice P Λ i :=
  ((P.proj i).comp Λ.subtype).codRestrict _ fun x => ⟨x, x.property, rfl⟩

theorem projectionToLattice_surjective (i : I) :
    Function.Surjective (projectionToLattice P Λ i) := by
  intro y
  obtain ⟨x, hx, heq⟩ := y.property
  refine ⟨⟨x, hx⟩, ?_⟩
  exact Subtype.ext heq

def rawCoordinate (i : I) : Λ →ₗ[O] CoordinateQuotient P Λ i :=
  (projectedIntegral P Λ i).mkQ.comp (projectionToLattice P Λ i)

theorem rawCoordinate_eq_zero_iff (i : I) (x : Λ) :
    rawCoordinate P Λ i x = 0 ↔ P.proj i x ∈ Λ := by
  change ((projectedIntegral P Λ i).mkQ (projectionToLattice P Λ i x) = 0) ↔ _
  rw [Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero]
  rfl

theorem splitInside_le_ker_rawCoordinate (i : I) :
    splitInside P Λ ≤ LinearMap.ker (rawCoordinate P Λ i) := by
  intro x hx
  exact (rawCoordinate_eq_zero_iff P Λ i x).mpr (proj_mem_of_mem_split P Λ i hx)

/-- One coordinate of the actual gluing homomorphism. -/
def gluingCoordinate (i : I) : GluingModule P Λ →ₗ[O] CoordinateQuotient P Λ i :=
  (splitInside P Λ).liftQ (rawCoordinate P Λ i) (splitInside_le_ker_rawCoordinate P Λ i)

/-- The canonical map [x] ↦ ([E_i x])_i into the finite product of packet quotients. -/
def gluingMap : GluingModule P Λ →ₗ[O] (∀ i, CoordinateQuotient P Λ i) :=
  LinearMap.pi (gluingCoordinate P Λ)

theorem gluingCoordinate_mk (i : I) (x : Λ) :
    gluingCoordinate P Λ i ((splitInside P Λ).mkQ x) = rawCoordinate P Λ i x := rfl

theorem gluingMap_injective : Function.Injective (gluingMap P Λ) := by
  apply (LinearMap.ker_eq_bot).mp
  apply le_antisymm
  · intro z hz
    obtain ⟨x, rfl⟩ := (splitInside P Λ).mkQ_surjective z
    have hx : x ∈ splitInside P Λ := by
      apply (mem_splitLattice_iff P Λ x).mpr
      intro i
      apply (rawCoordinate_eq_zero_iff P Λ i x).mp
      exact congrFun hz i
    simpa only [Submodule.mem_bot, Submodule.mkQ_apply,
      Submodule.Quotient.mk_eq_zero] using hx
  · exact bot_le

theorem gluingCoordinate_surjective (i : I) :
    Function.Surjective (gluingCoordinate P Λ i) := by
  intro y
  obtain ⟨v, rfl⟩ := (projectedIntegral P Λ i).mkQ_surjective y
  obtain ⟨x, rfl⟩ := projectionToLattice_surjective P Λ i v
  exact ⟨(splitInside P Λ).mkQ x, rfl⟩

/-- An actual scalar annihilates the gluing quotient precisely when it sends Λ into the split lattice. -/
theorem annihilates_gluing_iff (a : O) :
    (∀ z : GluingModule P Λ, a • z = 0) ↔
      ∀ x : V, x ∈ Λ → a • x ∈ splitLattice P Λ := by
  constructor
  · intro h x hx
    have heq := h ((splitInside P Λ).mkQ ⟨x, hx⟩)
    rw [← map_smul, Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero] at heq
    exact heq
  · intro h z
    obtain ⟨x, rfl⟩ := (splitInside P Λ).mkQ_surjective z
    rw [← map_smul, Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero]
    exact h x x.property

/-- The exact exponent-level gluing theorem, before taking least exponents. -/
theorem annihilates_gluing_iff_clears (pi : O) (s : ℕ) :
    (∀ z : GluingModule P Λ, (pi ^ s) • z = 0) ↔
      ∀ i x, x ∈ Λ → (pi ^ s) • P.proj i x ∈ Λ := by
  rw [annihilates_gluing_iff]
  constructor
  · intro h i x hx
    simpa only [map_smul] using (mem_splitLattice_iff P Λ _).mp (h x hx) i
  · intro h x hx
    apply (mem_splitLattice_iff P Λ _).mpr
    intro i
    simpa only [map_smul] using h i x hx

/-- Integral splitting is equivalent to integral action of every packet projector. -/
theorem splitLattice_eq_iff : splitLattice P Λ = Λ ↔
    ∀ i x, x ∈ Λ → P.proj i x ∈ Λ := by
  constructor
  · intro h i x hx
    exact proj_mem_of_mem_split P Λ i (h.symm ▸ hx)
  · intro h
    apply le_antisymm (splitLattice_le P Λ)
    intro x hx
    exact (mem_splitLattice_iff P Λ x).mpr fun i => h i x hx

/-- A packet's clearing predicate; this is integrality of the scaled actual operator. -/
def ClearsPacket (pi : O) (i : I) (s : ℕ) : Prop :=
  ∀ x : V, x ∈ Λ → (pi ^ s) • P.proj i x ∈ Λ

theorem clearsPacket_mono (pi : O) (i : I) {s t : ℕ}
    (hs : ClearsPacket P Λ pi i s) (hst : s ≤ t) :
    ClearsPacket P Λ pi i t := by
  intro x hx
  have ht : t = (t - s) + s := (Nat.sub_add_cancel hst).symm
  rw [ht, pow_add, mul_smul]
  exact Λ.smul_mem _ (hs x hx)

/-- Least packet weight, with the existence proof explicitly attached. -/
noncomputable def packetWeight (pi : O) (i : I)
    (finite : ∃ s, ClearsPacket P Λ pi i s) : ℕ := Nat.find finite

theorem clearsPacket_iff_weight_le (pi : O) (i : I)
    (finite : ∃ s, ClearsPacket P Λ pi i s) (s : ℕ) :
    ClearsPacket P Λ pi i s ↔ packetWeight P Λ pi i finite ≤ s := by
  constructor
  · exact Nat.find_min' finite
  · exact clearsPacket_mono P Λ pi i (Nat.find_spec finite)

/-- The maximum of the genuine least packet weights; the empty maximum is zero. -/
noncomputable def globalWeight (pi : O)
    (finite : ∀ i, ∃ s, ClearsPacket P Λ pi i s) : ℕ :=
  Finset.univ.sup fun i => packetWeight P Λ pi i (finite i)

theorem gluing_annihilated_iff_globalWeight_le (pi : O)
    (finite : ∀ i, ∃ s, ClearsPacket P Λ pi i s) (s : ℕ) :
    (∀ z : GluingModule P Λ, (pi ^ s) • z = 0) ↔ globalWeight P Λ pi finite ≤ s := by
  rw [annihilates_gluing_iff_clears]
  change (∀ i, ClearsPacket P Λ pi i s) ↔ _
  simp only [globalWeight, Finset.sup_le_iff, Finset.mem_univ, true_implies]
  exact forall_congr' fun i => clearsPacket_iff_weight_le P Λ pi i (finite i) s

theorem gluing_finite_exponent (pi : O)
    (finite : ∀ i, ∃ s, ClearsPacket P Λ pi i s) :
    ∃ s : ℕ, ∀ z : GluingModule P Λ, (pi ^ s) • z = 0 :=
  ⟨globalWeight P Λ pi finite,
    (gluing_annihilated_iff_globalWeight_le P Λ pi finite _).mpr le_rfl⟩

/-- The exponent of the actual gluing quotient equals the maximum of the least packet weights. -/
theorem gluing_exponent_eq_globalWeight (pi : O)
    (finite : ∀ i, ∃ s, ClearsPacket P Λ pi i s) :
    Nat.find (gluing_finite_exponent P Λ pi finite) = globalWeight P Λ pi finite := by
  apply le_antisymm
  · exact Nat.find_min' _
      ((gluing_annihilated_iff_globalWeight_le P Λ pi finite _).mpr le_rfl)
  · exact (gluing_annihilated_iff_globalWeight_le P Λ pi finite _).mp
      (Nat.find_spec (gluing_finite_exponent P Λ pi finite))

section Refinement
variable {J : Type*} [Fintype J] (Q : Projectors O V J)

/-- Range containment is the exact part of refinement needed by lattice gluing. -/
theorem splitLattice_le_of_refines
    (parent : J → I)
    (hrange : ∀ j, LinearMap.range (Q.proj j) ≤ LinearMap.range (P.proj (parent j))) :
    splitLattice Q Λ ≤ splitLattice P Λ := by
  apply iSup_le
  intro j
  exact le_iSup_of_le (parent j) (inf_le_inf_left Λ (hrange j))

theorem splitInside_le_of_refines
    (parent : J → I)
    (hrange : ∀ j, LinearMap.range (Q.proj j) ≤ LinearMap.range (P.proj (parent j))) :
    splitInside Q Λ ≤ splitInside P Λ :=
  Submodule.comap_mono (splitLattice_le_of_refines P Λ Q parent hrange)

theorem globalWeight_mono_of_refines (pi : O)
    (finiteP : ∀ i, ∃ s, ClearsPacket P Λ pi i s)
    (finiteQ : ∀ j, ∃ s, ClearsPacket Q Λ pi j s)
    (parent : J → I)
    (hrange : ∀ j, LinearMap.range (Q.proj j) ≤ LinearMap.range (P.proj (parent j))) :
    globalWeight P Λ pi finiteP ≤ globalWeight Q Λ pi finiteQ := by
  apply (gluing_annihilated_iff_globalWeight_le P Λ pi finiteP _).mp
  apply (annihilates_gluing_iff P Λ _).mpr
  intro x hx
  apply splitLattice_le_of_refines P Λ Q parent hrange
  apply (annihilates_gluing_iff Q Λ _).mp
    ((gluing_annihilated_iff_globalWeight_le Q Λ pi finiteQ _).mpr le_rfl) x hx

end Refinement

section NestedQuotients
variable {W : Type*} [AddCommGroup W] [Module O W]
variable (S T : Submodule O W) (hST : S ≤ T)

/-- The inclusion T/S → W/S for genuinely nested submodules. -/
def quotientInclusion : (T ⧸ S.comap T.subtype) →ₗ[O] W ⧸ S :=
  (S.comap T.subtype).mapQ S T.subtype le_rfl

theorem quotientInclusion_injective :
    Function.Injective (quotientInclusion S T) := by
  apply LinearMap.ker_eq_bot.mp
  rw [quotientInclusion, Submodule.ker_mapQ]
  exact Submodule.mkQ_map_self _

theorem quotientFactor_surjective : Function.Surjective (Submodule.factor hST) := by
  intro z
  obtain ⟨x, rfl⟩ := T.mkQ_surjective z
  exact ⟨S.mkQ x, rfl⟩

theorem quotientInclusion_range_eq_factor_ker :
    LinearMap.range (quotientInclusion S T) = LinearMap.ker (Submodule.factor hST) := by
  rw [quotientInclusion, Submodule.range_mapQ, Submodule.range_subtype]
  rw [Submodule.factor, Submodule.ker_mapQ, Submodule.comap_id]

/-- All three exactness obligations of 0 → T/S → W/S → W/T → 0. -/
theorem nested_quotient_short_exact :
    Function.Injective (quotientInclusion S T) ∧
    LinearMap.range (quotientInclusion S T) = LinearMap.ker (Submodule.factor hST) ∧
    Function.Surjective (Submodule.factor hST) :=
  ⟨quotientInclusion_injective S T,
    quotientInclusion_range_eq_factor_ker S T hST,
    quotientFactor_surjective S T hST⟩

end NestedQuotients

/-- The actual gluing short exact sequence for a refinement. -/
theorem gluing_refinement_short_exact
    {J : Type*} [Fintype J] (Q : Projectors O V J) (parent : J → I)
    (hrange : ∀ j, LinearMap.range (Q.proj j) ≤ LinearMap.range (P.proj (parent j))) :
    let h := splitInside_le_of_refines P Λ Q parent hrange
    Function.Injective (quotientInclusion (splitInside Q Λ) (splitInside P Λ)) ∧
    LinearMap.range (quotientInclusion (splitInside Q Λ) (splitInside P Λ)) =
      LinearMap.ker (Submodule.factor h) ∧
    Function.Surjective (Submodule.factor h) := by
  exact nested_quotient_short_exact _ _ (splitInside_le_of_refines P Λ Q parent hrange)

end Komorebi.PaperII.ReleaseGluing
