module
public import StandardTranslation
public import RelationalBackForth

@[expose] public section
namespace Komorebi.LogicalResolution.Standard
open Komorebi.Representation
universe u v w z b
variable {X Y : Type u} {A : Type v} {O : Type w} {V : Type z} {B : Type b}

theorem standard_quotient_preservation (S : System X A O V) (K : B → X → X → Prop)
    (hc : ∀ k x x' y y', ObsEq S x x' → ObsEq S y y' → (K k x y ↔ K k x' y'))
    {n : Nat} (f : RelFormula A O V B n) (ρ : Fin n → X) :
    (let _inst := model S K; (translate f).Realize ρ) ↔
    (let _inst := model (quotientSystem S) (quotientRelation S K)
     (translate f).Realize (fun i => Quotient.mk (behaviorSetoid S) (ρ i))) :=
  (translate_realize S K f ρ).trans
    ((relational_quotient_formula S K hc f ρ).trans
      (translate_realize (quotientSystem S) (quotientRelation S K) f _).symm)

/-- A finite back-and-forth certificate suffices for a standard translated query
    up to its exact quantifier rank. No global map is assumed. -/
theorem standard_backForth_preservation (S : System X A O V) (T : System Y A O V)
    (K : B → X → X → Prop) (L : B → Y → Y → Prop) {n : Nat}
    (f : RelFormula A O V B n) (q : Nat) (hq : f.qrank ≤ q)
    (ρ : Fin n → X) (τ : Fin n → Y) (h : BackForth S T K L q ρ τ) :
    (let _inst := model S K; (translate f).Realize ρ) ↔
    (let _inst := model T L; (translate f).Realize τ) :=
  (translate_realize S K f ρ).trans
    ((backForth_preserves_formula S T K L f q hq ρ τ h).trans
      (translate_realize T L f τ).symm)

end Komorebi.LogicalResolution.Standard
