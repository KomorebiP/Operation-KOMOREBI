import PaperIRelease.AlgebraSupport
import KomorebiVerification.TopologicalCompletion
import Mathlib.Algebra.Star.Subalgebra

/-!
# Bounded Hilbert support patterns

The necessary conditions use actual bounded rank-one operators between the
nonzero projector ranges. No bounded realization of arbitrary algebraic
blocks is assumed.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 2000000

open scoped InnerProduct
open InnerProductSpace
open KomorebiVerification.TopologicalCompletion

namespace Komorebi.PaperIRelease.BoundedSupport

universe u v w
variable {K : Type u} [RCLike K]
variable {X : Type v} [NormedAddCommGroup X] [InnerProductSpace K X] [CompleteSpace X]
variable {I : Type w} [Fintype I]

abbrev Block (P : BoundedProjectorFamily K X I) (T : X →L[K] X) (b a : I) :=
  BoundedProjectorFamily.transferBlock (P.proj b) T (P.proj a)

/-- Source-first relation convention, with literal vanishing ambient blocks. -/
def Supported (P : BoundedProjectorFamily K X I) (rel : I → I → Prop)
    (T : X →L[K] X) : Prop := ∀ b a, ¬ rel a b → Block P T b a = 0

def underlying (P : BoundedProjectorFamily K X I) :
    Komorebi.Foundation.LinearProjectorFamily K X I where
  proj i := (P.proj i).toLinearMap
  idempotent := P.idempotent
  orthogonal := P.annihilate
  complete := P.complete

omit [CompleteSpace X] in
theorem supported_iff_underlying (P : BoundedProjectorFamily K X I)
    (rel : I → I → Prop) (T : X →L[K] X) :
    Supported P rel T ↔ OperatorSupported (underlying P) rel T.toLinearMap := by
  rw [operatorSupported_iff_ambient]
  constructor
  · intro h b a hab
    exact congrArg ContinuousLinearMap.toLinearMap (h b a hab)
  · intro h b a hab
    ext x
    exact LinearMap.congr_fun (h b a hab) x

omit [CompleteSpace X] in
theorem proj_mem (P : BoundedProjectorFamily K X I) (a : I) {x : X}
    (hx : x ∈ P.packet a) : P.proj a x = x := by
  obtain ⟨y, rfl⟩ := hx
  exact P.idempotent a y

omit [CompleteSpace X] in
theorem proj_other (P : BoundedProjectorFamily K X I) {a b : I} (h : b ≠ a)
    {x : X} (hx : x ∈ P.packet a) : P.proj b x = 0 := by
  obtain ⟨y, rfl⟩ := hx
  exact P.annihilate h y

theorem block_rankOne (P : BoundedProjectorFamily K X I)
    (hself : ∀ i, (P.proj i).adjoint = P.proj i) (x y : X) (b a : I) :
    Block P (rankOne K x y) b a = rankOne K (P.proj b x) (P.proj a y) := by
  simp only [Block, BoundedProjectorFamily.transferBlock, rankOne_comp,
    comp_rankOne, hself]

/-- A bounded rank-one map with both vectors in their actual packet ranges
has precisely the prescribed single possible transfer block. -/
theorem supported_rankOne (P : BoundedProjectorFamily K X I)
    (hself : ∀ i, (P.proj i).adjoint = P.proj i) (rel : I → I → Prop)
    {a b : I} (hab : rel a b) {x y : X}
    (hx : x ∈ P.packet b) (hy : y ∈ P.packet a) :
    Supported P rel (rankOne K x y) := by
  intro d c hcd
  rw [block_rankOne P hself]
  by_cases hd : d = b
  · subst d
    have hc : c ≠ a := by intro heq; subst c; exact hcd hab
    rw [proj_other P hc hy]
    simp
  · rw [proj_other P hd hx]
    simp

omit [CompleteSpace X] in
theorem exists_nonzero_packet (P : BoundedProjectorFamily K X I)
    [∀ i, Nontrivial (P.packet i)] (a : I) : ∃ x : X, x ∈ P.packet a ∧ x ≠ 0 := by
  obtain ⟨x, hx⟩ := exists_ne (0 : P.packet a)
  exact ⟨x, x.property, fun h => hx (Subtype.ext h)⟩

/-- Adjoint closure is exactly symmetry, including its rank-one converse. -/
theorem adjoint_closed_iff_symmetric (P : BoundedProjectorFamily K X I)
    (hself : ∀ i, (P.proj i).adjoint = P.proj i)
    [∀ i, Nontrivial (P.packet i)] (rel : I → I → Prop) :
    (∀ T : X →L[K] X, Supported P rel T → Supported P rel T.adjoint) ↔
      (∀ ⦃a b⦄, rel a b → rel b a) := by
  constructor
  · intro h a b hab
    by_contra hba
    obtain ⟨x, hx, hx0⟩ := exists_nonzero_packet P b
    obtain ⟨y, hy, hy0⟩ := exists_nonzero_packet P a
    have hz := h (rankOne K x y) (supported_rankOne P hself rel hab hx hy) a b hba
    rw [adjoint_rankOne, block_rankOne P hself, proj_mem P a hy, proj_mem P b hx] at hz
    exact rankOne_ne_zero hy0 hx0 hz
  · intro hsym T hT b a hab
    have hz := hT a b (fun hba => hab (hsym hba))
    have hadj := congrArg ContinuousLinearMap.adjoint hz
    rw [BoundedProjectorFamily.adjoint_transferBlock _ _ _ (hself b) (hself a)] at hadj
    simpa using hadj

omit [CompleteSpace X] in
theorem identity_supported_iff_reflexive (P : BoundedProjectorFamily K X I)
    [∀ i, Nontrivial (P.packet i)] (rel : I → I → Prop) :
    Supported P rel (1 : X →L[K] X) ↔ (∀ a, rel a a) := by
  constructor
  · intro h a
    by_contra haa
    obtain ⟨x, hx, hx0⟩ := exists_nonzero_packet P a
    have heq := congrArg (fun T : X →L[K] X => T x) (h a a haa)
    apply hx0
    simpa [Block, BoundedProjectorFamily.transferBlock, proj_mem P a hx] using heq
  · intro hrefl b a hab
    have hba : b ≠ a := by intro h; subst b; exact hab (hrefl a)
    ext x
    exact P.annihilate hba x

/-- Composition closure forces transitivity through bounded rank-one maps. -/
theorem transitive_of_mul_closed (P : BoundedProjectorFamily K X I)
    (hself : ∀ i, (P.proj i).adjoint = P.proj i)
    [∀ i, Nontrivial (P.packet i)] (rel : I → I → Prop)
    (hclosed : ∀ S T : X →L[K] X, Supported P rel S → Supported P rel T →
      Supported P rel (S * T)) : ∀ ⦃a b c⦄, rel a b → rel b c → rel a c := by
  intro a b c hab hbc
  by_contra hac
  obtain ⟨x, hx, hx0⟩ := exists_nonzero_packet P a
  obtain ⟨y, hy, hy0⟩ := exists_nonzero_packet P b
  obtain ⟨z, hz, hz0⟩ := exists_nonzero_packet P c
  have heq := hclosed (rankOne K z y) (rankOne K y x)
    (supported_rankOne P hself rel hbc hz hy)
    (supported_rankOne P hself rel hab hy hx) c a hac
  have hblock : Block P (rankOne K z y * rankOne K y x) c a =
      inner K y y • rankOne K z x := by
    change Block P ((rankOne K z y).comp (rankOne K y x)) c a = _
    rw [rankOne_comp_rankOne]
    have hs : Block P (inner K y y • rankOne K z x) c a =
        inner K y y • Block P (rankOne K z x) c a := by
      ext v
      simp only [Block, BoundedProjectorFamily.transferBlock,
        ContinuousLinearMap.comp_apply, smul_apply, map_smul]
    rw [hs, block_rankOne P hself, proj_mem P c hz, proj_mem P a hx]
  rw [hblock] at heq
  exact smul_ne_zero (inner_self_ne_zero.mpr hy0) (rankOne_ne_zero hz0 hx0) heq

variable [DecidableEq I]

/-- Bounded operators with a reflexive transitive support pattern form an
actual subalgebra of the bounded operator algebra. -/
def supportSubalgebra (P : BoundedProjectorFamily K X I) (rel : I → I → Prop)
    (hrefl : ∀ a, rel a a) (htrans : ∀ ⦃a b c⦄, rel a b → rel b c → rel a c) : Subalgebra K (X →L[K] X) where
  carrier := {T | Supported P rel T}
  zero_mem' := by intro b a _; ext x; simp [Block, BoundedProjectorFamily.transferBlock]
  add_mem' := by
    intro S T hS hT
    apply (supported_iff_underlying P rel (S + T)).mpr
    exact (Komorebi.PaperIRelease.supportSubalgebra (underlying P) rel hrefl
      (fun _ _ _ h1 h2 => htrans h1 h2)).add_mem
        ((supported_iff_underlying P rel S).mp hS)
        ((supported_iff_underlying P rel T).mp hT)
  mul_mem' := by
    intro S T hS hT
    apply (supported_iff_underlying P rel (S * T)).mpr
    exact (Komorebi.PaperIRelease.supportSubalgebra (underlying P) rel hrefl
      (fun _ _ _ h1 h2 => htrans h1 h2)).mul_mem
        ((supported_iff_underlying P rel S).mp hS)
        ((supported_iff_underlying P rel T).mp hT)
  algebraMap_mem' k := by
    apply (supported_iff_underlying P rel (algebraMap K (X →L[K] X) k)).mpr
    exact (Komorebi.PaperIRelease.supportSubalgebra (underlying P) rel hrefl
      (fun _ _ _ h1 h2 => htrans h1 h2)).algebraMap_mem k

/-- Actual unital star-subalgebra, obtained from an equivalence relation. -/
def supportStarSubalgebra (P : BoundedProjectorFamily K X I)
    (hself : ∀ i, (P.proj i).adjoint = P.proj i)
    [∀ i, Nontrivial (P.packet i)] (rel : I → I → Prop) (heq : Equivalence rel) :
    StarSubalgebra K (X →L[K] X) where
  toSubalgebra := supportSubalgebra P rel heq.refl (fun {_ _ _} h1 h2 => heq.trans h1 h2)
  star_mem' := by
    intro T hT
    exact (adjoint_closed_iff_symmetric P hself rel).mpr (fun {_ _} h => heq.symm h) T hT

/-- Literal Paper I corollary: equality with the bounded support space is
equivalent to an equivalence relation, with no supplied closure certificates. -/
theorem star_subalgebra_iff_equivalence (P : BoundedProjectorFamily K X I)
    (hself : ∀ i, (P.proj i).adjoint = P.proj i)
    [∀ i, Nontrivial (P.packet i)] (rel : I → I → Prop) :
    (∃ A : StarSubalgebra K (X →L[K] X), ∀ T, T ∈ A ↔ Supported P rel T) ↔
      Equivalence rel := by
  constructor
  · rintro ⟨A, hA⟩
    refine ⟨(identity_supported_iff_reflexive P rel).mp ((hA 1).mp A.one_mem), ?_, ?_⟩
    · apply (adjoint_closed_iff_symmetric P hself rel).mp
      intro T hT
      exact (hA T.adjoint).mp (star_mem ((hA T).mpr hT))
    · apply transitive_of_mul_closed P hself rel
      intro S T hS hT
      exact (hA (S*T)).mp (A.mul_mem ((hA S).mpr hS) ((hA T).mpr hT))
  · intro heq
    exact ⟨supportStarSubalgebra P hself rel heq, fun _ => Iff.rfl⟩

/-- Equality support (block diagonal operators) is a genuine star-subalgebra. -/
theorem equality_pattern_boundary (P : BoundedProjectorFamily K X I)
    (hself : ∀ i, (P.proj i).adjoint = P.proj i)
    [∀ i, Nontrivial (P.packet i)] :
    ∃ A : StarSubalgebra K (X →L[K] X), ∀ T, T ∈ A ↔ Supported P Eq T := by
  apply (star_subalgebra_iff_equivalence P hself Eq).mpr
  exact ⟨fun _ => rfl, fun h => h.symm, fun h1 h2 => h1.trans h2⟩

/-- The full support pattern recovers a star-subalgebra containing every
bounded operator, including in the empty-index/zero-space case. -/
theorem universal_pattern_boundary (P : BoundedProjectorFamily K X I)
    (hself : ∀ i, (P.proj i).adjoint = P.proj i)
    [∀ i, Nontrivial (P.packet i)] :
    ∃ A : StarSubalgebra K (X →L[K] X), ∀ T, T ∈ A := by
  let rel : I → I → Prop := fun _ _ => True
  have heq : Equivalence rel := ⟨fun _ => trivial, fun _ => trivial, fun _ _ => trivial⟩
  refine ⟨supportStarSubalgebra P hself rel heq, ?_⟩
  intro T b a h
  exact (h trivial).elim

/-- On two nonzero packets a single allowed arrow fails adjoint closure. -/
theorem directed_two_packet_boundary (P : BoundedProjectorFamily K X Bool)
    (hself : ∀ i, (P.proj i).adjoint = P.proj i)
    [∀ i, Nontrivial (P.packet i)] :
    ¬ (∀ T : X →L[K] X,
      Supported P (fun a b => a = false ∧ b = true) T →
      Supported P (fun a b => a = false ∧ b = true) T.adjoint) := by
  intro h
  have hs := (adjoint_closed_iff_symmetric P hself _).mp h
  have hbad := hs (a := false) (b := true) ⟨rfl, rfl⟩
  cases hbad.1

omit [CompleteSpace X] [DecidableEq I] in
/-- An empty relation cannot contain the identity when a nonzero packet exists. -/
theorem empty_pattern_boundary [Nonempty I] (P : BoundedProjectorFamily K X I)
    [∀ i, Nontrivial (P.packet i)] :
    ¬ Supported P (fun _ _ => False) (1 : X →L[K] X) := by
  intro h
  obtain ⟨i⟩ := ‹Nonempty I›
  exact (identity_supported_iff_reflexive P _).mp h i

end Komorebi.PaperIRelease.BoundedSupport
