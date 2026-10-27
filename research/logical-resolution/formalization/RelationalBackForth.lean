module
public import RelationalSyntax

@[expose] public section
namespace Komorebi.LogicalResolution
open Komorebi.Representation
universe u v w z b
variable {X Y : Type u} {A : Type v} {O : Type w} {V : Type z} {B : Type b}

/-- Agreement of all permitted atomic tests on a tuple. Operational word depth is
    unrestricted here. This is not the equality-inclusive full FO atomic diagram. -/
def AtomicAgreement (S : System X A O V) (T : System Y A O V)
    (K : B → X → X → Prop) (L : B → Y → Y → Prop)
    {n : Nat} (ρ : Fin n → X) (τ : Fin n → Y) : Prop :=
  (∀ t s : ValueTerm A O V n, t.eval S ρ = s.eval S ρ ↔ t.eval T τ = s.eval T τ) ∧
  (∀ k (t s : StateTerm A n), K k (t.eval S ρ) (s.eval S ρ) ↔
    L k (t.eval T τ) (s.eval T τ))

/-- Finite-rank back-and-forth obligations with both witness directions explicit. -/
def BackForth (S : System X A O V) (T : System Y A O V)
    (K : B → X → X → Prop) (L : B → Y → Y → Prop) :
    Nat → {n : Nat} → (Fin n → X) → (Fin n → Y) → Prop
  | 0, _, ρ, τ => AtomicAgreement S T K L ρ τ
  | q+1, _, ρ, τ => AtomicAgreement S T K L ρ τ ∧
      (∀ x, ∃ y, BackForth S T K L q (extend x ρ) (extend y τ)) ∧
      (∀ y, ∃ x, BackForth S T K L q (extend x ρ) (extend y τ))

theorem backForth_atomic {S : System X A O V} {T : System Y A O V}
    {K : B → X → X → Prop} {L : B → Y → Y → Prop} {q n : Nat}
    {ρ : Fin n → X} {τ : Fin n → Y} (h : BackForth S T K L q ρ τ) :
    AtomicAgreement S T K L ρ τ := by
  cases q with
  | zero => exact h
  | succ q => exact h.1

theorem backForth_reflexive (S : System X A O V) (K : B → X → X → Prop)
    (q : Nat) {n : Nat} (ρ : Fin n → X) : BackForth S S K K q ρ ρ := by
  induction q generalizing n with
  | zero => exact ⟨fun _ _ => Iff.rfl, fun _ _ _ => Iff.rfl⟩
  | succ q ih =>
    exact ⟨⟨fun _ _ => Iff.rfl, fun _ _ _ => Iff.rfl⟩,
      (fun x => ⟨x, ih (extend x ρ)⟩), (fun x => ⟨x, ih (extend x ρ)⟩)⟩

theorem backForth_symmetric {S : System X A O V} {T : System Y A O V}
    {K : B → X → X → Prop} {L : B → Y → Y → Prop} (q : Nat) {n : Nat}
    {ρ : Fin n → X} {τ : Fin n → Y} (h : BackForth S T K L q ρ τ) :
    BackForth T S L K q τ ρ := by
  induction q generalizing n with
  | zero => exact ⟨fun t s => (h.1 t s).symm, fun k t s => (h.2 k t s).symm⟩
  | succ q ih =>
    refine ⟨⟨fun t s => (h.1.1 t s).symm, fun k t s => (h.1.2 k t s).symm⟩, ?_, ?_⟩
    · intro y; obtain ⟨x, hx⟩ := h.2.2 y; exact ⟨x, ih hx⟩
    · intro x; obtain ⟨y, hy⟩ := h.2.1 x; exact ⟨y, ih hy⟩

/-- Quantifier rank is now governed by witness matching, not by observations alone. -/
theorem backForth_preserves_formula (S : System X A O V) (T : System Y A O V)
    (K : B → X → X → Prop) (L : B → Y → Y → Prop) {n : Nat}
    (f : RelFormula A O V B n) (q : Nat) (hq : f.qrank ≤ q)
    (ρ : Fin n → X) (τ : Fin n → Y) (h : BackForth S T K L q ρ τ) :
    f.Holds S K ρ ↔ f.Holds T L τ := by
  induction f generalizing q with
  | falsum => rfl
  | equal t s => exact (backForth_atomic h).1 t s
  | related k t s => exact (backForth_atomic h).2 k t s
  | neg f ih => exact not_congr (ih q hq ρ τ h)
  | conj f g ihf ihg =>
    have hf : f.qrank ≤ q := Nat.le_trans (Nat.le_max_left _ _) hq
    have hg : g.qrank ≤ q := Nat.le_trans (Nat.le_max_right _ _) hq
    exact and_congr (ihf q hf ρ τ h) (ihg q hg ρ τ h)
  | existsState f ih =>
    cases q with
    | zero => simp [RelFormula.qrank] at hq
    | succ q =>
      have hq' : f.qrank ≤ q := Nat.le_of_succ_le_succ hq
      constructor
      · rintro ⟨x,hx⟩
        obtain ⟨y,hxy⟩ := h.2.1 x
        exact ⟨y,(ih q hq' (extend x ρ) (extend y τ) hxy).mp hx⟩
      · rintro ⟨y,hy⟩
        obtain ⟨x,hxy⟩ := h.2.2 y
        exact ⟨x,(ih q hq' (extend x ρ) (extend y τ) hxy).mpr hy⟩

theorem backForth_all_formulas (S : System X A O V) (T : System Y A O V)
    (K : B → X → X → Prop) (L : B → Y → Y → Prop) {n : Nat}
    (ρ : Fin n → X) (τ : Fin n → Y)
    (h : ∀ q, BackForth S T K L q ρ τ) (f : RelFormula A O V B n) :
    f.Holds S K ρ ↔ f.Holds T L τ :=
  backForth_preserves_formula S T K L f f.qrank (Nat.le_refl _) ρ τ (h f.qrank)

end Komorebi.LogicalResolution
