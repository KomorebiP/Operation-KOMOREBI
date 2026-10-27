import KomorebiVerification.PaperII.FiniteCommonRefinement

/-! Exact manuscript consumers and closed mathematical controls. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.CommonRefinement
open Komorebi.Foundation Komorebi.PaperII.NestedRefinement
universe u v w x y z
variable {R : Type u} {M : Type v} [Semiring R] [AddCommMonoid M] [Module R M]
variable {ι : Type w} {κ : Type x} {τ : Type y}
variable [Fintype ι] [Fintype κ] [Fintype τ]

/-- The exact binary supported-product conclusion, with onto parent maps. -/
theorem manuscript_common_refinement
    (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (h : CrossCommutes P Q) (hp : Nonzero P) (hq : Nonzero Q) :
    Nonzero (common P Q h) ∧
    Refines P (common P Q h) (fun k => k.val.1) ∧
    Refines Q (common P Q h) (fun k => k.val.2) :=
  ⟨supported_nonzero _, common_refines_left P Q h hp, common_refines_right P Q h hq⟩

/-- The coarsest theorem supplies an actual, unique parent map. -/
theorem manuscript_coarsest_unique
    (P : LinearProjectorFamily R M ι) (Q : LinearProjectorFamily R M κ)
    (h : CrossCommutes P Q) (S : LinearProjectorFamily R M τ) (hs : Nonzero S)
    (p : τ → ι) (q : τ → κ) (hp : Refines P S p) (hq : Refines Q S q) :
    ∃! parent : τ → Support (product P Q h), Refines (common P Q h) S parent := by
  refine ⟨jointParent P Q h S hs p q hp hq, common_coarsest P Q h S hs p q hp hq, ?_⟩
  intro parent hparent
  exact parent_unique _ S hs _ _ hparent (common_coarsest P Q h S hs p q hp hq)

/-- A finite collection, including an empty collection, under only pairwise commutation. -/
theorem manuscript_finite_common {T : Type z} [Fintype T]
    (F : T → Packet.{u,v,w} R M)
    (hc : ∀ s t, s ≠ t → CrossCommutes (F s).family (F t).family) :
    ∃ S : Packet.{u,v,w} R M,
      (∀ t, HasRefinement (F t) S) ∧
      (∀ U : Packet.{u,v,w} R M,
        (∀ t, HasRefinement (F t) U) → HasRefinement S U) :=
  finite_common_coarsest F hc

/-- The zero-module edge case does not introduce an illegal zero member. -/
theorem supported_index_empty_on_zero_module [Subsingleton M]
    (P : LinearProjectorFamily R M ι) : IsEmpty (Support P) := by
  refine ⟨?_⟩
  intro i
  exact i.property (by ext a; exact Subsingleton.elim _ _)

section ConcreteControl

def p0 : Matrix (Fin 2) (Fin 2) Int := !![1,0;0,0]
def p1 : Matrix (Fin 2) (Fin 2) Int := !![0,0;0,1]
def q0 : Matrix (Fin 2) (Fin 2) Int := !![1,1;0,0]
def q1 : Matrix (Fin 2) (Fin 2) Int := !![0,-1;0,1]

theorem first_matrix_packet :
    p0 * p0 = p0 ∧ p1 * p1 = p1 ∧ p0 * p1 = 0 ∧ p1 * p0 = 0 ∧ p0 + p1 = 1 := by
  decide

theorem second_matrix_packet :
    q0 * q0 = q0 ∧ q1 * q1 = q1 ∧ q0 * q1 = 0 ∧ q1 * q0 = 0 ∧ q0 + q1 = 1 := by
  decide

theorem noncommuting_product_nonzero : p0 * q1 ≠ 0 := by decide

theorem noncommuting_product_square_zero : (p0 * q1) * (p0 * q1) = 0 := by decide

theorem noncommuting_product_not_idempotent : (p0 * q1) * (p0 * q1) ≠ p0 * q1 := by decide

end ConcreteControl
end Komorebi.PaperII.CommonRefinement
