module
public import StandardTranslation

@[expose] public section
namespace Komorebi.LogicalResolution.RelationalWitness
open Komorebi.Representation
open FirstOrder

/-- Three states, identity dynamics, and no observable value distinction. -/
def system : System (Fin 3) Unit Unit Unit where
  step := fun _ x => x
  observe := fun _ _ => ()

/-- The only directed edge is from vertex zero to vertex two. -/
def edge (_ : Unit) (x y : Fin 3) : Prop := x = 0 ∧ y = 2

theorem edge_irreflexive (x : Fin 3) : ¬ edge () x x := by
  intro h
  have bad : (0 : Fin 3) = 2 := h.1.symm.trans h.2
  exact (by decide : (0 : Fin 3) ≠ 2) bad

theorem old_behavior_equal (x y : Fin 3) : ObsEq system x y := by
  intro w j
  rfl

def successorQuery : RelFormula Unit Unit Unit Unit 1 :=
  .existsState (.related () ⟨1, []⟩ ⟨0, []⟩)

theorem successorQuery_holds (x : Fin 3) :
    successorQuery.Holds system edge (fun _ => x) ↔ x = 0 := by
  change (∃ y : Fin 3, x = 0 ∧ y = 2) ↔ x = 0
  constructor
  · rintro ⟨_, hx, _⟩; exact hx
  · intro hx; exact ⟨2, hx, rfl⟩

theorem successorQuery_rank : successorQuery.qrank = 1 := rfl

theorem relational_quotient_impossible :
    ¬ ∃ L : BehaviorQuotient system → BehaviorQuotient system → Prop,
      ∀ x y, edge () x y ↔ L (Quotient.mk _ x) (Quotient.mk _ y) := by
  intro h
  have hc := (relation_descends_behavior_iff system (edge ())).mp h
  have bad := (hc 0 1 2 2 (old_behavior_equal _ _) (old_behavior_equal _ _)).mp
    (show edge () 0 2 from ⟨rfl,rfl⟩)
  exact (by decide : (1 : Fin 3) ≠ 0) bad.1

abbrev L := Standard.language Unit Unit Unit Unit

/-- Identity operations ensure every standard first-order term under a constant
    variable assignment evaluates to that one element. No state constants exist. -/
theorem standard_term_constant {α : Type} (t : L.Term α) (x : Fin 3)
    (ρ : α → Fin 3) (hρ : ∀ i, ρ i = x) :
    let _inst : L.Structure (Fin 3) := Standard.model system edge
    t.realize ρ = x := by
  let _inst : L.Structure (Fin 3) := Standard.model system edge
  induction t with
  | var i => exact hρ i
  | func f ts ih =>
    cases f with
    | step a => exact ih 0

/-- All parameter-free one-variable standard QF formulas agree at vertices zero
    and one. This includes built-in state equality, not just the translated image. -/
theorem standard_qf_constant {α : Type} {n : Nat} (f : L.BoundedFormula α n)
    (hf : f.IsQF) (x y : Fin 3) :
    let _inst : L.Structure (Fin 3) := Standard.model system edge
    f.Realize (fun _ => x) (fun _ => x) ↔ f.Realize (fun _ => y) (fun _ => y) := by
  let _inst : L.Structure (Fin 3) := Standard.model system edge
  have hx : ∀ (i : α ⊕ Fin n), Sum.elim (fun _ => x) (fun _ => x) i = x := by
    intro i; cases i <;> rfl
  have hy : ∀ (i : α ⊕ Fin n), Sum.elim (fun _ => y) (fun _ => y) i = y := by
    intro i; cases i <;> rfl
  induction hf with
  | falsum => rfl
  | of_isAtomic ha =>
    cases ha with
    | equal t s =>
      change t.realize _ = s.realize _ ↔ t.realize _ = s.realize _
      rw [standard_term_constant t x _ hx, standard_term_constant s x _ hx,
        standard_term_constant t y _ hy, standard_term_constant s y _ hy]
      exact iff_of_true rfl rfl
    | rel r ts =>
      cases r with
      | literals a b => rfl
      | valueIs j v => rfl
      | agree j k => rfl
      | link k =>
        change edge k ((ts 0).realize _) ((ts 1).realize _) ↔
          edge k ((ts 0).realize _) ((ts 1).realize _)
        rw [standard_term_constant (ts 0) x _ hx, standard_term_constant (ts 1) x _ hx,
          standard_term_constant (ts 0) y _ hy, standard_term_constant (ts 1) y _ hy]
        cases k
        exact iff_of_false (edge_irreflexive x) (edge_irreflexive y)
  | imp h₁ h₂ ih₁ ih₂ => exact imp_congr ih₁ ih₂

def standardQuery : L.Formula (Fin 1) := Standard.translate successorQuery

theorem standard_query_holds (x : Fin 3) :
    let _inst : L.Structure (Fin 3) := Standard.model system edge
    standardQuery.Realize (fun _ => x) ↔ x = 0 :=
  (Standard.translate_realize system edge successorQuery (fun _ => x)).trans
    (successorQuery_holds x)

theorem standard_query_rank : Standard.rank standardQuery = 1 :=
  Standard.translate_rank successorQuery

theorem quantified_distinction :
    let _inst : L.Structure (Fin 3) := Standard.model system edge
    standardQuery.Realize (fun _ => (0 : Fin 3)) ∧ ¬standardQuery.Realize (fun _ => (1 : Fin 3)) := by
  constructor
  · exact (standard_query_holds 0).mpr rfl
  · intro h
    exact (by decide : (1 : Fin 3) ≠ 0) ((standard_query_holds 1).mp h)

/-- A within-one-model non-elimination result, not just a two-model comparison. -/
theorem no_qf_replacement_in_this_model (f : L.Formula (Fin 1)) (hf : f.IsQF) :
    let _inst : L.Structure (Fin 3) := Standard.model system edge
    ¬ ∀ x : Fin 3, f.Realize (fun _ => x) ↔ standardQuery.Realize (fun _ => x) := by
  let _inst : L.Structure (Fin 3) := Standard.model system edge
  change ¬ ∀ x : Fin 3, f.Realize (fun _ => x) ↔ standardQuery.Realize (fun _ => x)
  intro h
  have h0 : f.Realize (fun _ => (0 : Fin 3)) := (h 0).mpr quantified_distinction.1
  have hc := standard_qf_constant f hf 0 1
  have hz : (fun _ : Fin 0 => (0 : Fin 3)) = Fin.elim0 := by funext i; exact Fin.elim0 i
  have ho : (fun _ : Fin 0 => (1 : Fin 3)) = Fin.elim0 := by funext i; exact Fin.elim0 i
  dsimp only at hc
  rw [hz, ho] at hc
  have h1 : f.Realize (fun _ => (1 : Fin 3)) := hc.mp h0
  exact quantified_distinction.2 ((h 1).mp h1)

end Komorebi.LogicalResolution.RelationalWitness
